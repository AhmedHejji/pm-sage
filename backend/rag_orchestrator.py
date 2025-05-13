import os
import json
import faiss
import numpy as np
from google.cloud import firestore
from google import genai          # Google Gen AI SDK 

# Paths to embedded data files
HERE = os.path.dirname(__file__)
INDEX_PATH = os.path.join(HERE, "faiss_index.bin")
CHUNKS_PATH = os.path.join(HERE, "chunks.json")

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-f29fe995937e")
EMBED_MODEL = "text-embedding-005"       # GA embedding model 
GEN_MODEL = "gemini-2.0-flash-001"        # Gemini 2.0 flash generation model

# Lazy-loaded globals
_index = None
_chunks = None
client = None

def load_resources():
    global _index, _chunks, client
    if _index is None:
        # 1) Load FAISS index
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"Missing index file: {INDEX_PATH}")
        _index = faiss.read_index(INDEX_PATH)  # FAISS index load

        # 2) Load text chunks
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            _chunks = json.load(f)

        # 3) Initialize Gen AI client
        client = genai.Client(                 # SDK client init
            project=PROJECT_ID,
            location="us-east1",
            vertexai=True
        )

def retrieve_chunks(query: str, k: int = 5):
    load_resources()

    # 1) Embed the query
    embed_resp = client.models.embed_content(  # embed_content method
        model=EMBED_MODEL,
        contents=[query]
    )
    # Extract raw float embedding
    q_vec = np.array(embed_resp.embeddings[0].values, dtype="float32")

    # 2) FAISS search
    _, idxs = _index.search(np.array([q_vec]), k)
    return [_chunks[i] for i in idxs[0]]

def generate_response(query: str) -> str:
    load_resources()

    # Retrieve context chunks
    docs = retrieve_chunks(query)
    context = "\n---\n".join(docs)

    # Build RAG prompt
    prompt = (
        "You are a project-management expert. Base your answer ONLY on:\n\n"
        f"{context}\n\nQuestion: {query}"
    )

    # Call Gemini for generation
    gen_resp = client.models.generate_content(  # generate_content usage
        model=GEN_MODEL,
        contents=prompt
    )

    # Log session to Firestore
    db = firestore.Client(project=PROJECT_ID)
    db.collection("sessions").add({
        "query": query,
        "response": gen_resp.text,
        "chunks": docs
    })

    return gen_resp.text
