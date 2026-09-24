"""
loader.py
Step 1 & 2 of the RAG pipeline: load a PDF and split it into overlapping chunks.
"""
from pypdf import PdfReader


def load_pdf_text(pdf_path: str) -> str:
    """Extract all text from a PDF, page by page."""
    reader = PdfReader(pdf_path)
    full_text = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        full_text.append(text)
    return "\n".join(full_text)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks by CHARACTER count.

    Why overlap? If a sentence is cut in half at a chunk boundary, the
    overlap ensures the full sentence still appears intact in at least
    one chunk, so retrieval doesn't lose context at the edges.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    # Collapse excessive whitespace/newlines so chunks aren't mostly blank lines
    cleaned = " ".join(text.split())

    chunks = []
    start = 0
    text_len = len(cleaned)
    step = chunk_size - overlap

    while start < text_len:
        end = start + chunk_size
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_resume.pdf"
    raw_text = load_pdf_text(path)
    print(f"Extracted {len(raw_text)} characters from {path}\n")
    chunks = chunk_text(raw_text)
    print(f"Split into {len(chunks)} chunks\n")
    for i, c in enumerate(chunks[:3]):
        print(f"--- Chunk {i} ({len(c)} chars) ---")
        print(c)
        print()
