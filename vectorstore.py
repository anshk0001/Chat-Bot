"""
vectorstore.py
Step 3 of the RAG pipeline: turn chunks into embeddings and store/retrieve
them with ChromaDB.

Embeddings are generated locally with sentence-transformers
(all-MiniLM-L6-v2) — free, no API key, runs on CPU.
"""
import chromadb
from chromadb.utils import embedding_functions

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


class PDFVectorStore:
    def __init__(self, collection_name: str = "pdf_docs", persist_dir: str = "./chroma_db"):
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL_NAME
        )
        self.client = chromadb.PersistentClient(path=persist_dir)
        # Fresh collection each time we ingest a new document, to avoid
        # mixing chunks from unrelated PDFs in one demo run.
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

    def add_chunks(self, chunks: list[str], source_name: str = "document"):
        """Embed each chunk and store it, with an id and simple metadata."""
        ids = [f"{source_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source_name, "chunk_index": i} for i in range(len(chunks))]
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    def query(self, question: str, top_k: int = 3) -> list[str]:
        """Return the top_k most relevant chunks for a question."""
        results = self.collection.query(query_texts=[question], n_results=top_k)
        return results["documents"][0] if results["documents"] else []


if __name__ == "__main__":
    store = PDFVectorStore()
    store.add_chunks(
        [
            "Ansh is a B.Tech Computer Science student.",
            "He is targeting a software engineering role by June 2027.",
            "His core focus areas are DSA, full-stack development, and system design.",
        ],
        source_name="test",
    )
    print(store.query("What is Ansh targeting?", top_k=2))
