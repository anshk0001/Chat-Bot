<<<<<<< HEAD
# Chat-Bot
A Retrieval-Augmented Generation (RAG) chatbot that answers questions about a PDF using only its own content. Built from scratch with pypdf, sentence-transformers, and ChromaDB — no LangChain abstraction hiding the pipeline. Supports Claude, GPT, or a context-only fallback with zero API keys.
=======
# Personal PDF Q&A Bot (RAG from scratch)

A minimal, dependency-light RAG pipeline that answers questions about a PDF
using **only the content of that PDF**. Built to show the full pipeline
explicitly — no LangChain/LlamaIndex abstraction hiding the steps.

## Pipeline

```
PDF file
  -> loader.py       : extract text (pypdf), split into overlapping chunks
  -> vectorstore.py  : embed each chunk (sentence-transformers, local/free)
                        and store in ChromaDB
  -> app.py           : embed the user's question, retrieve top-3 chunks
  -> generator.py    : stuff those chunks into a prompt, ask an LLM
```

## Setup

```bash
pip install pypdf sentence-transformers chromadb anthropic
```

(`anthropic` is only needed if you use Claude for generation — see below.
Swap in `openai` instead if you prefer GPT.)

The first run downloads the embedding model (`all-MiniLM-L6-v2`, ~90MB) from
Hugging Face — this needs a normal internet connection once, then it's
cached locally and every future run is fully offline for the embedding step.

## Run

```bash
python app.py your_resume.pdf
```

Then just ask questions:

```
You: What projects has this person built?
Bot: ...
You: exit
```

## Generation backends (pick one, or none)

`generator.py` auto-detects which backend to use, in this order:

| Env var set            | Backend used                     |
|-------------------------|-----------------------------------|
| `ANTHROPIC_API_KEY`     | Claude (`claude-sonnet-4-6`)      |
| `OPENAI_API_KEY`        | GPT (`gpt-4o-mini`)               |
| *(neither)*             | "Context-only" mode — just prints the retrieved chunks, no LLM call |

The context-only fallback is deliberate: it lets you verify **retrieval**
is working (the hard, interesting part of RAG) before you ever touch an
API key. Set a key like this before running:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python app.py your_resume.pdf
```

## Files

- `loader.py` — PDF text extraction + chunking (Steps 1–2)
- `vectorstore.py` — embeddings + ChromaDB storage/retrieval (Step 3)
- `generator.py` — prompt construction + LLM call (Step 4)
- `app.py` — ties it all together into a chat loop
- `sample_resume.pdf` — a sample document to test with immediately

## Tuning knobs worth experimenting with

- **`chunk_size` / `overlap`** in `chunk_text()` — smaller chunks give more
  precise retrieval but less surrounding context per chunk; try 300/30 vs
  800/100 and see how answers change.
- **`top_k`** in `store.query()` — how many chunks get passed to the LLM.
  More isn't always better: too many irrelevant chunks can confuse the model.
- **Embedding model** — `all-MiniLM-L6-v2` is fast and small. For better
  accuracy at the cost of speed, try `all-mpnet-base-v2`.

## Known limitation

This only handles **text-based PDFs**. A scanned/image PDF (e.g. a photographed
resume) will extract empty text — you'd need an OCR step (e.g. `pytesseract`)
added to `loader.py` first.

## Natural next steps once this works

1. Swap the CLI loop for a small Streamlit UI.
2. Support multiple PDFs at once (add a `source` filter to queries).
3. Add conversation memory so follow-up questions ("what about the second one?")
   work.
4. Show *which* chunk each answer came from (citations) in the UI.
>>>>>>> bcc5b2c (chat bot created)
