"""
RAG (Retrieval-Augmented Generation) module for HealthLabelCheck
Answers questions from retrieved regulation chunks with citations.
"""

import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from app.vectorstore import semantic_search, get_collection, build_index
from app.chunking import load_records, chunk_all_records

# ── ensure the vector index exists ──────────────────────────────────────────

def _ensure_index() -> None:
    """Build Chroma index if it is empty."""
    try:
        col = get_collection()
        if col.count() == 0:
            build_index()
    except Exception:
        build_index()


_ensure_index()


# ── LLM call (optional) ──────────────────────────────────────────────────────

def _call_llm(system: str, user: str) -> str:
    """
    Call Groq LLM if GROQ_API_KEY is set, otherwise return a structured
    rule-based answer so the RAG pipeline works without an API key.
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key and api_key != "your_key_here_replace_this":
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=float(os.getenv("LLM_TEMPERATURE", 0.3)),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", 500)),
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[LLM error: {e}]"

    # ── fallback: rule-based answer from retrieved chunks ──
    return None   # signal to caller to use chunk text directly


# ── out-of-scope detector ────────────────────────────────────────────────────

OUT_OF_SCOPE_KEYWORDS = [
    "cheapest", "price", "cost", "shop", "vendor", "supplier",
    "where to buy", "how much", "weather", "news", "recipe",
    "health benefit", "cure", "medicine",
]

def _is_out_of_scope(question: str) -> bool:
    q = question.lower()
    return any(kw in q for kw in OUT_OF_SCOPE_KEYWORDS)


# ── main RAG function ────────────────────────────────────────────────────────

def ask(question: str, top_k: int = 3, chunk_size: str = "full") -> dict:
    """
    Answer a question using RAG.

    Args:
        question  : User question string
        top_k     : Number of chunks to retrieve
        chunk_size: "full" uses complete chunk text; "short" uses first 120 chars

    Returns dict with:
        answer      : str
        citations   : list of regulation numbers used
        chunks_used : int
        source      : "llm" | "rule_based" | "out_of_scope"
    """
    # Out-of-scope guard
    if _is_out_of_scope(question):
        return {
            "answer": (
                "I don't know. That question is outside the scope of FSSAI "
                "food labelling regulations. I can only help with what must be "
                "printed on food packets under FSSAI rules."
            ),
            "citations": [],
            "chunks_used": 0,
            "source": "out_of_scope",
        }

    # Retrieve
    hits = semantic_search(question, top_k=top_k)
    if not hits:
        return {
            "answer": "I don't know. No relevant regulation found for this question.",
            "citations": [],
            "chunks_used": 0,
            "source": "out_of_scope",
        }

    citations = [h["regulation_no"] for h in hits]

    # Build context string
    context_parts = []
    for h in hits:
        text = h["text"]
        if chunk_size == "short":
            text = text[:120] + ("…" if len(h["text"]) > 120 else "")
        context_parts.append(
            f"[Regulation {h['regulation_no']}] {h['title']}\n{text}"
        )
    context = "\n\n".join(context_parts)

    # System prompt
    system = (
        "You are HealthLabelCheck AI, an FSSAI food labelling expert. "
        "Answer the user's question using ONLY the regulation excerpts provided. "
        "Always cite regulation numbers. "
        "If the excerpts do not contain enough information, say 'I don't know'."
    )
    user_msg = (
        f"Regulation excerpts:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Reply in 3-5 sentences. Start with the direct answer, then cite the regulation number."
    )

    llm_answer = _call_llm(system, user_msg)

    if llm_answer:
        return {
            "answer": llm_answer,
            "citations": citations,
            "chunks_used": len(hits),
            "source": "llm",
        }

    # Rule-based fallback: compose answer from chunk texts
    answer_lines = [f"Based on FSSAI regulations:\n"]
    for h in hits:
        answer_lines.append(
            f"• Regulation {h['regulation_no']} ({h['title']}): "
            f"{h['text'][:200]}…"
        )
    answer_lines.append(
        "\nPlease set GROQ_API_KEY in .env for natural-language answers."
    )

    return {
        "answer": "\n".join(answer_lines),
        "citations": citations,
        "chunks_used": len(hits),
        "source": "rule_based",
    }


if __name__ == "__main__":
    test_questions = [
        "What must be printed on a food label?",
        "What is the vegetarian symbol rule?",
        "What is the cheapest printer in Kopargaon?",   # out-of-scope
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        result = ask(q)
        print(f"Source   : {result['source']}")
        print(f"Citations: {result['citations']}")
        print(f"Answer   : {result['answer'][:200]}…")
