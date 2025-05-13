from transformers import AutoTokenizer
import os, json

# SciBERT tokenizer for technical text
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")

def chunk(text, size=100, overlap=20):
    """
    Split text into chunks of ≤100 tokens with 20-token overlap.
    """
    tokens = tokenizer(text)["input_ids"]
    step = size - overlap
    chunks = []
    for i in range(0, len(tokens), step):
        segment = tokens[i : i + size]
        chunks.append(tokenizer.decode(segment, skip_special_tokens=True))
    return chunks

def process_folder(
    input_folder="preprocess",
    output_file="backend/chunks.json" 
):
    all_chunks = []
    for fname in os.listdir(input_folder):
        if fname.endswith(".txt"):
            with open(os.path.join(input_folder, fname), encoding="utf-8") as f:
                text = f.read()
            all_chunks.extend(chunk(text))

    # ensure backend dir exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(all_chunks, out, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_chunks)} chunks to {output_file}")

if __name__ == "__main__":
    process_folder()
