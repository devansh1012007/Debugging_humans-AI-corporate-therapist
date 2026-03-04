from pathlib import Path
import hashlib
import re
import numpy as np
from typing import Dict, List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity

print("Imported")

# ================= CONFIG =================
RAW_DOCS = Path("docs")
DB_PATH = "vector_db_final"

DISCARD_THRESHOLD = 0.92
MERGE_THRESHOLD = 0.85
TOP_K = 1                      # <- locked to 1
SENTENCE_SIM_THRESHOLD = 0.90
# =========================================


# ---------------- UTILS ----------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def split_sentences(text: str) -> List[str]:
    return re.split(r"(?<=[.!?])\s+", text.strip())


# ---------------- LOAD DOCS ----------------
documents = []

print("Loading documents")
for file in RAW_DOCS.glob("*"):
    if file.suffix == ".pdf":
        documents += PyPDFLoader(str(file)).load()
    elif file.suffix == ".txt":
        documents += TextLoader(str(file), encoding="utf-8").load()
    print(f"{len(documents)} loaded")

if not documents:
    print("No documents found.")
    exit()


# ---------------- CHUNKING ----------------
print("Chunking")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunks = splitter.split_documents(documents)


# ---------------- EMBEDDINGS ----------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ---------------- SENTENCE CACHE ----------------
sentence_embedding_cache: Dict[str, np.ndarray] = {}

def embed_sentence(sent: str) -> np.ndarray:
    if sent not in sentence_embedding_cache:
        vec = np.array(embeddings.embed_query(sent))
        vec = vec / np.linalg.norm(vec)   # explicit normalize
        sentence_embedding_cache[sent] = vec
    return sentence_embedding_cache[sent]


# ---------------- CONFIDENCE-WEIGHTED MERGE ----------------
def confidence_weighted_merge(text_a: str, text_b: str) -> str:
    sentences = split_sentences(text_a) + split_sentences(text_b)

    vecs = np.vstack([embed_sentence(s) for s in sentences])
    centroid = vecs.mean(axis=0, keepdims=True)
    centroid /= np.linalg.norm(centroid)

    confidences = cosine_similarity(vecs, centroid).flatten()

    kept_sents = []
    kept_vecs = []

    for sent, vec, conf in sorted(
        zip(sentences, vecs, confidences),
        key=lambda x: -x[2]
    ):
        if not kept_vecs:
            kept_sents.append(sent)
            kept_vecs.append(vec)
            continue

        sims = cosine_similarity(
            vec.reshape(1, -1),
            np.vstack(kept_vecs)
        )[0]

        if sims.max() < SENTENCE_SIM_THRESHOLD:
            kept_sents.append(sent)
            kept_vecs.append(vec)

    return " ".join(kept_sents)


# ---------------- DEDUP PIPELINE ----------------
print("Deduplicating")

accepted_docs = []
seen_hashes = set()
faiss_index = None

for i, doc in enumerate(chunks):
    print(f"{100*i/len(chunks):.2f}% completion", end=" ")

    norm = normalize_text(doc.page_content)
    h = text_hash(norm)

    if h in seen_hashes:
        print("discard (hash)")
        continue

    emb = np.array(embeddings.embed_query(doc.page_content))
    emb = emb / np.linalg.norm(emb)   # critical
    emb_list = emb.tolist()

    discard = False

    if faiss_index is not None:
        # FAISS returns (Document, distance)
        best_doc, distance = faiss_index.similarity_search_with_score_by_vector(
            emb_list,
            k=TOP_K
        )[0]

        # FAISS distance = cosine distance = 1 - cosine similarity
        sim = 1.0 - distance

        print(f"sim={sim:.3f}", end=" ")

        if sim >= DISCARD_THRESHOLD:
            discard = True

        elif MERGE_THRESHOLD <= sim < DISCARD_THRESHOLD:
            print("merge", end=" ")

            merged_text = confidence_weighted_merge(
                best_doc.page_content,
                doc.page_content
            )

            best_doc.page_content = merged_text
            seen_hashes.add(h)
            discard = True

    if discard:
        print("discarded")
        continue

    print("append")
    accepted_docs.append(doc)
    seen_hashes.add(h)

    if faiss_index is None:
        faiss_index = FAISS.from_documents([doc], embeddings)
    else:
        faiss_index.add_documents([doc])


print(f"Chunks before dedup: {len(chunks)}")
print(f"Chunks after dedup:  {len(accepted_docs)}")


# ---------------- FINAL VECTOR DB ----------------
print("Storing Vector DB")
vectorstore = FAISS.from_documents(accepted_docs, embeddings)
vectorstore.save_local(DB_PATH)

print("Vector DB built successfully.")
