"""
generator.py
Step 4 of the RAG pipeline: take the retrieved chunks + the user's question,
build a prompt, and get an answer from an LLM.

Three backends are supported, auto-selected in this priority order so the
bot works out of the box even with zero API keys:

  1. ANTHROPIC_API_KEY set  -> Claude (claude-sonnet-4-6)
  2. OPENAI_API_KEY set     -> GPT (gpt-4o-mini)
  3. neither set            -> "context-only" fallback: no LLM call at all,
                               just prints the retrieved chunks. Lets you
                               verify retrieval works before wiring up a key.
"""
import os

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided context from a document. If the answer isn't in the context, "
    "say you don't know based on the document. Be concise."
)


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(f"[Excerpt {i+1}]\n{c}" for i, c in enumerate(context_chunks))
    return (
        f"Context from the document:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the context above."
    )


def _answer_with_anthropic(prompt: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def _answer_with_openai(prompt: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
    )
    return resp.choices[0].message.content


def _answer_context_only(question: str, context_chunks: list[str]) -> str:
    lines = [
        "[No LLM API key found — showing raw retrieval instead of a generated answer.]",
        "[Set ANTHROPIC_API_KEY or OPENAI_API_KEY to get a real generated answer.]",
        "",
        f"Question: {question}",
        "",
        "Most relevant excerpts found in the document:",
    ]
    for i, c in enumerate(context_chunks):
        lines.append(f"\n{i+1}. {c}")
    return "\n".join(lines)


def generate_answer(question: str, context_chunks: list[str]) -> str:
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    prompt = build_prompt(question, context_chunks)

    if anthropic_key:
        return _answer_with_anthropic(prompt, anthropic_key)
    elif openai_key:
        return _answer_with_openai(prompt, openai_key)
    else:
        return _answer_context_only(question, context_chunks)
