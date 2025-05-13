# preprocess/extract_text.py
import os, subprocess
from io import BytesIO
from PyPDF2 import PdfReader

def repair_pdf_bytes(data: bytes) -> BytesIO:
    """Use pdftk to rewrite a malformed PDF in-memory."""
    p = subprocess.Popen(
        ["pdftk", "-", "output", "-", "uncompress"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, _ = p.communicate(data)
    return BytesIO(out)

def extract_all_pdfs(input_folder="data", output_folder="preprocess"):
    os.makedirs(output_folder, exist_ok=True)
    for fname in os.listdir(input_folder):
        if not fname.lower().endswith(".pdf"):
            continue

        path = os.path.join(input_folder, fname)
        raw = open(path, "rb").read()
        try:
            reader = PdfReader(BytesIO(raw), strict=False)
        except Exception:
            # fallback: repair then read
            repaired = repair_pdf_bytes(raw)
            reader = PdfReader(repaired, strict=False)

        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        out_path = os.path.join(output_folder, fname + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Extracted {out_path}")

if __name__ == "__main__":
    extract_all_pdfs()
