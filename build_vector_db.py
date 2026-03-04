from pathlib import Path
import hashlib
import numpy as np

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
print("Imported")

RAW_DOCS = Path("docs")
DB_PATH = "vector_db"

# --- Dedup thresholds ---
DISCARD_THRESHOLD = 0.92
MERGE_THRESHOLD = 0.85


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- Load documents ---
documents = []

print("Loading documents")
for file in RAW_DOCS.glob("*"):
    if file.suffix == ".pdf":
        documents += PyPDFLoader(str(file)).load()
    elif file.suffix == ".txt":
        documents += TextLoader(str(file), encoding="utf-8").load()
    print(f"{len(documents)} loaded")

if not documents:
    print("No documents found. Vector DB not created.")
    exit()


# --- Chunking ---
print("Chunking")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

chunks = splitter.split_documents(documents)



# --- Embeddings ---
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# --- Merger Function ---
import re
def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

def intelligent_merge(text_a, text_b, embeddings, sim_threshold=0.9):
    sentences_a = split_sentences(text_a)
    sentences_b = split_sentences(text_b)

    merged = []
    merged_embs = []

    for sent in sentences_a + sentences_b:
        emb = embeddings.embed_query(sent)
        emb_np = np.array(emb).reshape(1, -1)

        if merged_embs:
            sims = cosine_similarity(emb_np, np.vstack(merged_embs))[0]
            if sims.max() >= sim_threshold:
                continue

        merged.append(sent)
        merged_embs.append(emb)

    return " ".join(merged)

# --- Deduplication pipeline ---
print("Deduplicating")
accepted_docs = []
accepted_embeddings = []
seen_hashes = set()

i = 0
for doc in chunks:
    print(100*i/len(chunks)+1, "% completion")
    i+=1
    normalized = normalize_text(doc.page_content)
    h = text_hash(normalized)

    # 1. Exact / near-exact dedup
    if h in seen_hashes:
        print("discarding", end = " ")
        continue

    emb = embeddings.embed_query(doc.page_content)
    emb_np = np.array(emb).reshape(1, -1)

    discard = False

    # 2. Semantic dedup
    if accepted_embeddings:
        sims = cosine_similarity(emb_np, np.vstack(accepted_embeddings))[0]
        max_sim = sims.max()
        print(f"max_sim = {max_sim:.3f}", end=" ")

        if max_sim >= DISCARD_THRESHOLD:
            discard = True

        elif MERGE_THRESHOLD <= max_sim < DISCARD_THRESHOLD:
            print("merging", end=" ")
            # merge chunks
            existing_idx = sims.argmax()
            existing_doc = accepted_docs[existing_idx]

            merged_text = intelligent_merge(
            existing_doc.page_content,
            doc.page_content,
            embeddings
            )

            accepted_docs[existing_idx].page_content = merged_text
            accepted_embeddings[existing_idx] = embeddings.embed_query(merged_text)
            seen_hashes.add(h)


            discard = True

    if discard:
        print("discarding", end=" ")
        continue

    # Accept chunk
    print("appending", end=" ")
    accepted_docs.append(doc)
    accepted_embeddings.append(emb)
    seen_hashes.add(h)


print(f"Chunks before dedup: {len(chunks)}")
print(f"Chunks after dedup:  {len(accepted_docs)}")


# --- Final vector DB ---
print("Storing Vector DB")
vectorstore = FAISS.from_documents(accepted_docs, embeddings)
vectorstore.save_local(DB_PATH)

print("Vector DB built successfully with deduplication.")