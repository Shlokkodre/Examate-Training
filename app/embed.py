"""
Embedding module for HealthLabelCheck
Embeds chunks with sentence-transformers and runs semantic search.
Hits for the 10 questions are recorded in eval/search_results.md
"""

import json
import os
from typing import List, Dict, Tuple

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.chunking import load_records, chunk_all_records

MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingSearchEngine:
    """Semantic search engine backed by sentence-transformers embeddings."""

    def __init__(self, model_name: str = MODEL_NAME):
        print(f"Loading embedding model: {model_name} …")
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Dict] = []
        self.embeddings: np.ndarray = np.array([])

    def index(self, chunks: List[Dict]) -> None:
        """Embed and index a list of chunks."""
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Indexed {len(chunks)} chunks.")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """
        Return top_k (chunk, score) pairs for the query.
        Score is cosine similarity [0, 1].
        """
        if self.embeddings.size == 0:
            return []
        q_vec = self.model.encode([query])
        scores = cosine_similarity(q_vec, self.embeddings)[0]
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top_idx if scores[i] > 0]


# ── singleton ────────────────────────────────────────────────────────────────
_engine: EmbeddingSearchEngine | None = None


def get_engine() -> EmbeddingSearchEngine:
    global _engine
    if _engine is None:
        _engine = EmbeddingSearchEngine()
        records = load_records()
        chunks = chunk_all_records(records)
        _engine.index(chunks)
    return _engine


# ── run on 10 questions and record results ───────────────────────────────────
QUESTIONS = [
    "What things must be printed on a packed food label as per FSSAI?",
    "What is the rule for the vegetarian green dot symbol?",
    "Is nutrition information required on every packet?",
    "My chakli pouch front is 12 cm by 8 cm, what minimum font size do I need for net weight?",
    "Do I need to list all ingredients on my laddoo packet?",
    "What is the cheapest printing shop for food pouches in Kopargaon?",
    "What FSSAI license number do I need and how do I get it?",
    "Can I write the manufacturing date as MFD 12-11-2026 on my packet?",
    "My laddoos contain groundnuts. What must I declare about allergens?",
    "I add turmeric powder to my chakli for color. Do I need to declare it?",
]


def record_search_results(engine: EmbeddingSearchEngine, out_path: str = "eval/search_results.md") -> None:
    """Run all 10 questions and write results to markdown."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    lines = [
        "# Semantic Search Results\n",
        "Model: `all-MiniLM-L6-v2`  \n",
        f"Chunks indexed: {len(engine.chunks)}\n\n",
    ]

    for i, q in enumerate(QUESTIONS, 1):
        lines.append(f"## Q{i}: {q}\n\n")
        results = engine.search(q, top_k=3)
        if not results:
            lines.append("_No results returned._\n\n")
            continue
        for rank, (chunk, score) in enumerate(results, 1):
            lines.append(
                f"**Hit {rank}** (score {score:.4f})  \n"
                f"Regulation: {chunk['regulation_no']}  \n"
                f"Title: {chunk['title']}  \n"
                f"Source: {chunk['source']}  \n"
                f"Text: {chunk['text'][:200]}…\n\n"
            )

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Search results written to {out_path}")


if __name__ == "__main__":
    engine = get_engine()

    print("\n=== Quick semantic search demo ===")
    test_q = "What font size do I need for my chakli pouch?"
    for chunk, score in engine.search(test_q, top_k=3):
        print(f"  [{score:.3f}] {chunk['regulation_no']}: {chunk['title']}")

    record_search_results(engine)
