"""
app.py
Personal PDF Q&A Bot — full RAG pipeline in one CLI script.

Usage:
    python app.py path/to/document.pdf

Then ask questions in a loop. Type 'exit' to quit.
"""
import sys
from loader import load_pdf_text, chunk_text
from vectorstore import PDFVectorStore
from generator import generate_answer


def build_index(pdf_path: str) -> PDFVectorStore:
    print(f"Loading {pdf_path} ...")
    raw_text = load_pdf_text(pdf_path)
    if not raw_text.strip():
        raise ValueError(
            "No text extracted from PDF. If it's a scanned/image PDF, "
            "you'll need OCR first (this bot only handles text-based PDFs)."
        )

    print("Chunking text ...")
    chunks = chunk_text(raw_text, chunk_size=500, overlap=50)
    print(f"Created {len(chunks)} chunks.")

    print(f"Embedding chunks and building vector index (first run downloads the "
          f"embedding model, ~90MB, one-time) ...")
    store = PDFVectorStore()
    store.add_chunks(chunks, source_name=pdf_path.split("/")[-1])
    print("Index ready.\n")
    return store


def chat_loop(store: PDFVectorStore):
    print("Ask questions about the document. Type 'exit' to quit.\n")
    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break

        top_chunks = store.query(question, top_k=3)
        if not top_chunks:
            print("Bot: Couldn't find anything relevant in the document.\n")
            continue

        answer = generate_answer(question, top_chunks)
        print(f"\nBot: {answer}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py path/to/document.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    vector_store = build_index(pdf_path)
    chat_loop(vector_store)
