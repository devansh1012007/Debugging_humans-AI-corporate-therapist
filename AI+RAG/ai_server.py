from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import CrossEncoder
from fastapi.responses import StreamingResponse
import json
import time
import numpy as np
from config import *

app = FastAPI()
# loading
vectorstore = None
if os.path.exists(VECTOR_DB_PATH):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)

def mmr_with_min_similarity(
    query: str,
    vectorstore,
    embeddings,
    *,
    top_k: int = 6,
    fetch_k: int = 24,
    min_similarity: float = 0.45,
    lambda_mult: float = 0.7,
):


    q_vec = np.array(embeddings.embed_query(query))
    q_vec = q_vec / np.linalg.norm(q_vec)

    results = vectorstore.similarity_search_with_score_by_vector(
        q_vec.tolist(),
        k=fetch_k
    )

    if not results:
        return []

    candidates = []
    for doc, distance in results:
        sim = 1.0 - distance
        if sim < min_similarity:
            continue

        if "embedding" not in doc.metadata:
            doc_vec = np.array(embeddings.embed_query(doc.page_content))
            doc_vec = doc_vec / np.linalg.norm(doc_vec)
            doc.metadata["embedding"] = doc_vec

        candidates.append((doc, sim))

    if not candidates:
        return []

    selected_docs = []
    selected_vecs = []

    for _ in range(min(top_k, len(candidates))):
        best_doc = None
        best_vec = None
        best_score = -1e9

        for doc, sim in candidates:
            doc_vec = doc.metadata["embedding"]

            if not selected_vecs:
                score = sim
            else:
                diversity_penalty = max(
                    cosine_similarity(
                        doc_vec.reshape(1, -1),
                        np.vstack(selected_vecs)
                    )[0]
                )
                score = (
                    lambda_mult * sim
                    - (1.0 - lambda_mult) * diversity_penalty
                )

            if score > best_score:
                best_score = score
                best_doc = doc
                best_vec = doc_vec

        if best_doc is None:
            break

        selected_docs.append(best_doc)
        selected_vecs.append(best_vec)

        candidates = [(d, s) for d, s in candidates if d != best_doc]

    return selected_docs



class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: list, top_k: int = 6, min_score: float = 0.0):
        if not docs:
            return []

        pairs = [(query, d.page_content) for d in docs]
        scores = self.model.predict(pairs)

        reranked = []
        for doc, score in zip(docs, scores):
            if score >= min_score:
                doc.metadata["rerank_score"] = float(score)
                reranked.append(doc)

        reranked.sort(
            key=lambda d: d.metadata["rerank_score"],
            reverse=True
        )

        return reranked[:top_k]

reranker = CrossEncoderReranker()

# SCHEMA

class ChatRequest(BaseModel):
    message: str
    conversation: list[dict[str, str]]
    user_profile: str
    workspace_context: str
    model_override: str | None = None


def ollama_stream_generator(payload: dict, metadata: dict):
    
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=600
        ) as r:

            buffer = []
            last_flush = time.time()

            # Send metadata once at the beginning
            yield f"data: {json.dumps({'type': 'meta', 'data': metadata})}\n\n"

            for line in r.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode("utf-8"))

                if data.get("done", False):
                    if buffer:
                        yield f"data: {json.dumps({'type': 'token', 'data': ''.join(buffer)})}\n\n"
                        buffer.clear()

                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return

                token = data.get("response", "")
                if token:
                    buffer.append(token)

                #flush every 100 ms 
                if (
                    time.time() - last_flush > 0.12
                    or token.endswith((".", "?", "!", "\n"))
                ):
                    if buffer:
                        yield f"data: {json.dumps({'type': 'token', 'data': ''.join(buffer)})}\n\n"
                        buffer.clear()
                        last_flush = time.time()

    except GeneratorExit:
        return
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

def compute_context_confidence(docs: list) -> float:
    if not docs:
        return 0.0

    scores = []
    for d in docs:
        score = d.metadata.get("score")
        if score is not None:
            scores.append(score)

    if scores:
        avg_score = sum(scores) / len(scores)
        confidence = max(0.0, min(1.0, 1 - avg_score))
    else:
        confidence = min(1.0, len(docs) / TOP_K)

    return round(confidence, 2)

def preload_models():
    for model in [DEFAULT_MODEL]:
        try:
            requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": "simply say 'OK' and nothing else: ",
                    "temperature": 0,
                    "stream": False
                },
                timeout=100
            )
            print(f"Preloaded model: {model}")
        except Exception as e:
            print(f"Failed to preload {model}: {e}")

# auto temp
def base_temperature_from_confidence(confidence: float) -> float:
    return 0.7 - (0.4 * confidence)

def intent_adjustment(text: str) -> float:
    text = text.lower()

    analytical_triggers = ["why", "how", "explain", "calculate", "derive"]
    emotional_triggers = ["feel", "anxious", "sad", "overwhelmed", "stressed"]

    if any(t in text for t in analytical_triggers):
        return -0.1
    if any(t in text for t in emotional_triggers):
        return +0.1

    return 0.0

def model_adjustment(model_name: str) -> float:
    if "therapy" in model_name:
        return +0.05
    return 0.0

import re
from collections import Counter
def emotional_temperature_boost(text: str) -> float:
    
    if not text or len(text) < 5:
        return 0.0

    boost = 0.0
    text_lower = text.lower()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if sentences:
        avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_len < 6:
            boost += 0.05

    words = re.findall(r'\b\w+\b', text_lower)
    if len(words) > 0:
        counts = Counter(words)
        most_common_freq = counts.most_common(1)[0][1]
        repetition_ratio = most_common_freq / len(words)

        if repetition_ratio > 0.15:
            boost += 0.04

    first_person = {"i", "me", "my", "mine", "myself"}
    fp_count = sum(1 for w in words if w in first_person)
    if len(words) > 0 and (fp_count / len(words)) > 0.12:
        boost += 0.03

    unique_ratio = len(set(words)) / max(1, len(words))
    if unique_ratio < 0.45:
        boost += 0.02

    if "..." in text or "!!" in text or text.count("?") >= 3:
        boost += 0.03

    return round(max(boost, 0.15), 2)

EMOTIONAL_ANCHORS = {
    "neutral": "calm, emotionally balanced, neutral state",
    "analytical": "logical reasoning, problem solving, technical thinking",
    "distressed": "emotionally overwhelmed, anxious, hopeless, distressed",
    "ruminative": "repetitive negative thinking, stuck thoughts, mental fatigue",
    "positive": "hopeful, optimistic, forward looking, emotionally resilient, happy"
}
anchor_embeddings = {}
def preload_emotional_anchors(embedding_model):
    global anchor_embeddings
    texts = list(EMOTIONAL_ANCHORS.values())
    vectors = embedding_model.embed_documents(texts)

    for key, vec in zip(EMOTIONAL_ANCHORS.keys(), vectors):
        anchor_embeddings[key] = vec

import numpy as np
def cosine_similarity_1d(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def emotional_geometry_score(message: str, embedding_model) -> dict:
    if not message.strip():
        return {}

    msg_vec = embedding_model.embed_query(message)
    scores = {}

    for name, anchor_vec in anchor_embeddings.items():
        scores[name] = 2*np.arccos(cosine_similarity_1d(msg_vec, anchor_vec))/np.pi - 1

    return scores


def geometry_temperature_adjustment(geo_scores: dict) -> float:
    if not geo_scores:
        return 0.0

    distressed = geo_scores.get("distressed", 0)
    ruminative = geo_scores.get("ruminative", 0)
    analytical = geo_scores.get("analytical", 0)

    adjustment = 0.0

    adjustment += max(0, distressed - 0.4) * 0.15
    adjustment += max(0, ruminative - 0.4) * 0.1

    adjustment -= max(0, analytical - 0.4) * -0.5

    return round(adjustment, 2)

def compute_temperature(confidence, message, model, geo_scores):
    temp = base_temperature_from_confidence(confidence)
    temp += intent_adjustment(message)
    temp += model_adjustment(model)
    temp += emotional_temperature_boost(message)
    temp += geometry_temperature_adjustment(geo_scores)

    if "therapy" in model:
        upper_cap = 0.85
    else:
        upper_cap = 0.75

    return round(max(0.2, min(upper_cap, temp)), 2)


# chat 
@app.on_event("startup")
def startup_event():
    # preload_models()
    if vectorstore:
        preload_emotional_anchors(embeddings)


@app.post("/chat")
def chat(req: ChatRequest):

    model = req.model_override or DEFAULT_MODEL

    # retrie
    context = ""
    confidence = 0.0

    if vectorstore:
        docs = mmr_with_min_similarity(
            query=req.message,
            vectorstore=vectorstore,
            embeddings=embeddings,
            top_k=TOP_K,
            fetch_k=24,
            min_similarity=0.55,
            lambda_mult=0.7
        )
        docs = reranker.rerank(
            query=req.message,
            docs=docs,
            top_k=TOP_K,
            min_score=0.15
        )
        for d in docs:
            print(round(d.metadata["rerank_score"], 3), d.page_content[:80])

        confidence = compute_context_confidence(docs)
        context = "<document>" + "</document>\n\n<document>".join(d.page_content for d in docs) + "</document>"

    geo_score = emotional_geometry_score(req.message, embeddings)
    temperature = compute_temperature(confidence, req.message, model, geo_score)

    system_prompt = (
        SYSTEM_PROMPT_PROBLEM_SOLVER
        if model in [DEFAULT_MODEL, "granite", "mistral", "mixtral"]
        else SYSTEM_PROMPT_THERAPY_AI
    )

    prompt = f"""
System prompt:-{system_prompt}

User's information:-
User profile: {req.user_profile}
Workspace culture: {req.workspace_context}

Relevant documents:-
{context}

Past conversation:-
{req.conversation}

Prompt:-
{req.message}

Response:-
"""
    if context == "<document></docuemnt>":
        prompt.replace("\n\nRelevant documents:-\n<document></document>", "")
    
    if context == "<document></document>" and len(req.message.split()) <= 12:
        temperature -= 0.1
        temperature = min([0.6, temperature])

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
    )

    return {
    "response": response.json()["response"],
    "context_confidence": confidence,
    "model_used": model,
    "temperature_used": temperature,
    "prompt": prompt,
    "resp": response.json(),
    "geo_scores": geo_score
    }

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):

    model = req.model_override or DEFAULT_MODEL

    context = ""
    confidence = 0.0

    if vectorstore:
        docs = mmr_with_min_similarity(
            query=req.message,
            vectorstore=vectorstore,
            embeddings=embeddings,
            top_k=TOP_K,
            fetch_k=24,
            min_similarity=0.55,
            lambda_mult=0.7
        )
        docs = reranker.rerank(
            query=req.message,
            docs=docs,
            top_k=TOP_K,
            min_score=0.15
        )
        for d in docs:
            print(round(d.metadata["rerank_score"], 3), d.page_content[:80])

        confidence = compute_context_confidence(docs)
        context = "<document>" + "</document>\n\n<document>".join(d.page_content for d in docs) + "</document>"

    geo_score = emotional_geometry_score(req.message, embeddings)
    temperature = compute_temperature(confidence, req.message, model, geo_score)

    system_prompt = (
        SYSTEM_PROMPT_PROBLEM_SOLVER
        if model in [DEFAULT_MODEL, "granite", "mistral", "mixtral"]
        else SYSTEM_PROMPT_THERAPY_AI
    )

    prompt = f"""
System prompt:-{system_prompt}

User's information:-
User profile: {req.user_profile}
Workspace culture: {req.workspace_context}

Relevant documents:-
{context}

Past conversation:-
{req.conversation}

Prompt:-
{req.message}

Response:-
"""
    if context == "<document></docuemnt>":
        prompt.replace("\n\nRelevant documents:-\n<document></document>", "")
    
    if context == "<document></document>" and len(req.message.split()) <= 12:
        temperature -= 0.1
        temperature = min([0.6, temperature])

    ollama_payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": True
    }

    metadata = {
        "model_used": model,
        "temperature_used": temperature,
        "context_confidence": confidence,
        "geo_scores": geo_score,
        "documents": context
    }

    return StreamingResponse(
        ollama_stream_generator(ollama_payload, metadata),
        media_type="text/event-stream"
    )
# sumarizer
def clean_output(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip("\"'")

    if not text:
        return "EMPTY"

    words = text.split()
    if len(words) > 22:
        text = " ".join(words[:22])

    if not text.endswith("."):
        text += "."

    return text

def summarize_message(text: str, role: str) -> str:
    system_prompt = SYSTEM_USER if role == "user" else SYSTEM_ASSISTANT

    payload = {
        "model": SUMMARY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0,
        "stream": False
    }

    response = requests.post(OLLAMA_URL+"/api/chat", json=payload)
    response.raise_for_status()

    raw = response.json()["message"]["content"]
    return clean_output(raw)

class SummaryRequest(BaseModel):
    conversation: list[dict[str, str]]

@app.post("/summarizer")
def summarize_conversation(req: SummaryRequest):
    output = [
        {
            "role": msg["role"],
            "message": summarize_message(msg["message"], msg["role"])
        }
        for msg in req.conversation
    ]

    return {
        "output": output
    }

# personality extracter
class PersonalityExtracterRequest(BaseModel):
    conversations: list[list[dict[str, str]]]
    existing_personality_profile: dict

@app.post("/personality_extractor")
def personality_extracter(req: PersonalityExtracterRequest):
    prompt = json.dumps(
        {
            "existing_personality": req.existing_personality_profile,
            "new_conversation": req.conversations
        },
        ensure_ascii=False
    )

    payload = {
        "model": PERSONALITY_EXTRACTER_MODEL,
        "system": PERSONALITY_EXTRACTER_SYSTEM,
        "prompt": prompt,
        "temperature": 0,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL+"/api/generate",
        json=payload
    )

    response.raise_for_status()
    data = response.json()

    result = json.loads(data["response"])

    assert set(result.keys()) <= {"add", "remove", "change", "no_change"}

    if result["no_change"]:
        assert result["add"] == {}
        assert result["remove"] == []
        assert result["change"] == {}

    
    new_personality_profile = req.existing_personality_profile.copy()
    if new_personality_profile == None:
        new_personality_profile = {}
        
    for k, v in result["add"].items():
        new_personality_profile[k] = v

    for k, v in result["change"].items():
        new_personality_profile[k] = v

    for k in result["remove"]:
        new_personality_profile.pop(k)

    return {
        "output": new_personality_profile
    }


class ExtractionModel(BaseModel):
    convos: list
    prev_ass: dict

@app.post("/assessments")
def assesser(req:ExtractionModel):

    prompt = f"""
    Previous assessment values:
    {req.prev_ass}

    Conversation chunk:
    {req.convos}

    Update the assessment strictly according to system instructions.
    """

    payload = {
    "model": "problem-solver",
    "system": ASSESSMENT_SYSTEM_PROMPT,
    "prompt": prompt,
    "temperature": 0,
    "stream": False,
    "format": "json"
    }

    response = requests.post(
        OLLAMA_URL+"/api/generate",
        json=payload
    )

    response.raise_for_status()
    data = response.json()
    result = json.loads(data["response"])

    return {
        "result": result
    }