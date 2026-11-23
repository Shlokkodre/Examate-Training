"""
Evaluation runner for HealthLabelCheck RAG pipeline.
Tests two configurations and prints a comparison table.
Results summary is appended to README.md.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.rag import ask


EVAL_PATH = "eval/eval_set.json"


def load_eval_set():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def score_result(item: dict, result: dict) -> dict:
    """
    Score a single RAG result against the expected values.

    Metrics:
    - citation_hit   : at least one expected regulation appears in citations
    - keyword_hit    : at least one expected keyword appears in the answer
    - scope_correct  : out-of-scope questions get 'out_of_scope' source
    - answered       : answerable questions return a non-trivial answer
    """
    answer_lower = result["answer"].lower()
    citations    = result["citations"]

    # Citation hit
    if item["expected_regulations"]:
        citation_hit = any(
            r in citations for r in item["expected_regulations"]
        )
    else:
        citation_hit = True  # out-of-scope: no citations expected

    # Keyword hit
    keyword_hit = any(
        kw.lower() in answer_lower
        for kw in item["expected_answer_contains"]
    )

    # Scope handling
    if not item["is_answerable"]:
        scope_correct = result["source"] == "out_of_scope"
    else:
        scope_correct = result["source"] != "out_of_scope"

    # Overall pass
    passed = citation_hit and keyword_hit and scope_correct

    return {
        "id": item["id"],
        "citation_hit":  citation_hit,
        "keyword_hit":   keyword_hit,
        "scope_correct": scope_correct,
        "passed":        passed,
    }


def run_config(label: str, top_k: int, chunk_size: str, items: list) -> list:
    """Run eval for one config, return list of score dicts."""
    print(f"\n{'='*60}")
    print(f"Config: {label}  (top_k={top_k}, chunk_size={chunk_size})")
    print("="*60)

    scores = []
    for item in items:
        result = ask(item["question"], top_k=top_k, chunk_size=chunk_size)
        sc = score_result(item, result)
        status = "PASS" if sc["passed"] else "FAIL"
        print(
            f"  Q{item['id']:02d} {status}  "
            f"cite={sc['citation_hit']}  kw={sc['keyword_hit']}  "
            f"scope={sc['scope_correct']}"
        )
        scores.append(sc)

    passed = sum(1 for s in scores if s["passed"])
    print(f"\n  Passed: {passed}/{len(scores)}")
    return scores


def print_comparison_table(configs: list[tuple]) -> str:
    """
    configs: list of (label, scores)
    Returns the markdown table string.
    """
    header = f"{'Config':<30} {'Passed':>8} {'Citation':>10} {'Keyword':>10} {'Scope':>8}"
    sep    = "-" * len(header)
    rows   = [header, sep]

    for label, scores in configs:
        n        = len(scores)
        passed   = sum(1 for s in scores if s["passed"])
        cite_ok  = sum(1 for s in scores if s["citation_hit"])
        kw_ok    = sum(1 for s in scores if s["keyword_hit"])
        scope_ok = sum(1 for s in scores if s["scope_correct"])
        rows.append(
            f"{label:<30} {passed:>4}/{n:<3} {cite_ok:>5}/{n:<3} "
            f"{kw_ok:>5}/{n:<3} {scope_ok:>3}/{n}"
        )

    table = "\n".join(rows)
    print(f"\n{'='*60}")
    print("COMPARISON TABLE")
    print(table)

    # Determine winner
    winner_label, winner_scores = max(
        configs, key=lambda c: sum(1 for s in c[1] if s["passed"])
    )
    print(f"\nWinner: {winner_label}")
    return table, winner_label


def update_readme(table: str, winner: str) -> None:
    """Replace (not append) the eval results block in README.md."""
    readme_path = "README.md"
    section = f"""## RAG Evaluation Results

Two configurations tested on 15 questions (`eval/eval_set.json`):

```
{table}
```

**Winner**: {winner}

Metrics: citation_hit = at least one expected regulation cited;
keyword_hit = at least one expected keyword in answer;
scope_correct = out-of-scope questions answered with "I don't know".

Run: `python eval/run_eval.py`
"""
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove all existing RAG Evaluation Results sections
        import re
        content = re.sub(
            r"## RAG Evaluation Results.*?(?=\n## |\Z)",
            "",
            content,
            flags=re.DOTALL,
        ).rstrip()

        # Append the single updated section
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content + "\n\n" + section)

        print(f"\nREADME updated with eval results.")
    except Exception as e:
        print(f"\nCould not update README: {e}")


if __name__ == "__main__":
    items = load_eval_set()
    print(f"Eval set: {len(items)} questions")

    # Config A: top_k=3, full chunk text
    scores_a = run_config("Config A: top_k=3, full",  top_k=3, chunk_size="full",  items=items)

    # Config B: top_k=5, short chunk text
    scores_b = run_config("Config B: top_k=5, short", top_k=5, chunk_size="short", items=items)

    table, winner = print_comparison_table([
        ("Config A: top_k=3, full",  scores_a),
        ("Config B: top_k=5, short", scores_b),
    ])

    update_readme(table, winner)
