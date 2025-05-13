import os, json, time
import numpy as np
import faiss
import vertexai
from transformers import AutoTokenizer
from vertexai.language_models import TextEmbeddingModel
from google.api_core.exceptions import ServiceUnavailable

# Silence HF parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1) Init Vertex AI
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-f29fe995937e"),
    location="us-east1"
)

# 2) Paths relative to this script
HERE = os.path.dirname(__file__)
CHUNKS_PATH = os.path.join(HERE, "chunks.json")
INDEX_PATH = os.path.join(HERE, "faiss_index.bin")

# 3) Load chunks
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    texts = json.load(f)
print(f"[embed] Loaded {len(texts)} chunks")

# 4) Load embedding model
model = TextEmbeddingModel.from_pretrained("text-embedding-005")

# 5) Initial static batching (≤250 chunks)
initial_batches = [
    texts[i : i + 250] for i in range(0, len(texts), 250)
]

# 6) Recursive split by actual Vertex token count (≤20 000)
def split_by_token_limit(batch):
    resp = model.count_tokens(batch)
    if resp.total_tokens <= 20_000:
        return [batch]
    mid = len(batch) // 2
    return split_by_token_limit(batch[:mid]) + split_by_token_limit(batch[mid:])

batches = []
for b in initial_batches:
    batches.extend(split_by_token_limit(b))

print(f"[embed] Final batches: {len(batches)}; sizes: {[len(b) for b in batches]}")

# 7) Embed with retries
def embed_with_retries(batch, max_retries=5):
    for i in range(1, max_retries + 1):
        try:
            return model.get_embeddings(batch)
        except ServiceUnavailable:
            wait = 2 ** i
            print(f"[WARN] Retry {i} in {wait}s due to UNAVAILABLE")
            time.sleep(wait)
    return model.get_embeddings(batch)

# 8) Generate embeddings and build FAISS index
all_vecs = []
for idx, b in enumerate(batches, 1):
    print(f"[embed] Embedding batch {idx}/{len(batches)} ({len(b)} chunks)…")
    embs = embed_with_retries(b)
    all_vecs.extend([e.values for e in embs])

vecs = np.array(all_vecs, dtype="float32")
index = faiss.IndexFlatL2(vecs.shape[1])
index.add(vecs)

# 9) Write index to backend/
faiss.write_index(index, INDEX_PATH)
print(f"[embed] Wrote FAISS index to {INDEX_PATH}")

# 10) (Optional) remove or comment out this GCS upload section
# from google.cloud import storage
# client = storage.Client()
# bucket = client.bucket("pm-sage-data-982")
# blob = bucket.blob("faiss_index.bin")
# blob.upload_from_filename(INDEX_PATH)
# print("[embed] Uploaded index to GCS")

