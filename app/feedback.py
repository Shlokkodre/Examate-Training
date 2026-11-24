"""
Day 16 — Feedback analysis module for HealthLabelCheck
Reads data/feedback.jsonl and computes thumbs-up/down stats,
top questions, and recent entries.

Usage:
    from app.feedback import get_feedback_stats
    stats = get_feedback_stats()
"""

import json
import os
from typing import List, Dict
from collections import Counter

FEEDBACK_PATH = os.path.join("data", "feedback.jsonl")


def load_feedback() -> List[Dict]:
    """Load all feedback records from data/feedback.jsonl."""
    if not os.path.exists(FEEDBACK_PATH):
        return []
    records = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def get_feedback_stats() -> Dict:
    """
    Compute feedback statistics.

    Returns dict with:
        total          : int
        thumbs_up      : int
        thumbs_down    : int
        satisfaction   : float  (0-100 %)
        top_questions  : list of {question, count, rating}
        recent         : last 5 feedback entries
    """
    records = load_feedback()

    if not records:
        return {
            "total": 0,
            "thumbs_up": 0,
            "thumbs_down": 0,
            "satisfaction_pct": 0.0,
            "top_questions": [],
            "recent": [],
            "message": "No feedback recorded yet.",
        }

    thumbs_up   = sum(1 for r in records if r.get("rating") == "up")
    thumbs_down = sum(1 for r in records if r.get("rating") == "down")
    total       = len(records)
    satisfaction = round(thumbs_up / total * 100, 1) if total else 0.0

    # Top questions by frequency
    question_counter = Counter(r.get("question", "")[:100] for r in records)
    top_questions = [
        {"question": q, "count": c}
        for q, c in question_counter.most_common(5)
        if q
    ]

    # Recent 5 entries (newest first)
    recent = list(reversed(records[-5:]))

    return {
        "total":            total,
        "thumbs_up":        thumbs_up,
        "thumbs_down":      thumbs_down,
        "satisfaction_pct": satisfaction,
        "top_questions":    top_questions,
        "recent":           recent,
    }


def save_feedback(question: str, answer: str, rating: str) -> None:
    """Append one feedback record to data/feedback.jsonl."""
    import datetime
    os.makedirs("data", exist_ok=True)
    record = {
        "ts":       datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "question": question[:300],
        "answer":   answer[:300],
        "rating":   rating,
    }
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # Seed some sample feedback for testing
    sample = [
        ("What is the veg symbol rule?", "Green circle in a square...", "up"),
        ("What font size for 12x8 cm?", "1.5 mm per Reg 6.1...", "up"),
        ("What must be on my label?", "Name, ingredients, net qty...", "up"),
        ("Is nutrition info required?", "Not for small packets...", "down"),
        ("What is the veg symbol rule?", "Green circle in a square...", "up"),
    ]
    for q, a, r in sample:
        save_feedback(q, a, r)

    stats = get_feedback_stats()
    print(f"Total feedback : {stats['total']}")
    print(f"Thumbs up      : {stats['thumbs_up']}")
    print(f"Thumbs down    : {stats['thumbs_down']}")
    print(f"Satisfaction   : {stats['satisfaction_pct']}%")
    print(f"\nTop questions:")
    for q in stats['top_questions']:
        print(f"  ({q['count']}x) {q['question'][:60]}")
    print(f"\nRecent:")
    for r in stats['recent']:
        print(f"  [{r['rating']}] {r['question'][:50]}")
