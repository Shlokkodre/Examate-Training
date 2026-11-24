"""
Day 16 — Unit tests for app/feedback.py and GET /feedback-stats endpoint

Run from repo root:
    python -m pytest tests/test_feedback.py -v
"""

import os
import sys
import json
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def temp_feedback_file(monkeypatch, tmp_path):
    """Redirect feedback file to a temp path for each test."""
    import app.feedback as fb
    fake_path = str(tmp_path / "feedback.jsonl")
    monkeypatch.setattr(fb, "FEEDBACK_PATH", fake_path)
    yield fake_path


# ── save_feedback() tests ─────────────────────────────────────────────────────

class TestSaveFeedback:
    def test_creates_file(self, temp_feedback_file):
        from app.feedback import save_feedback
        save_feedback("Test question?", "Test answer.", "up")
        assert os.path.exists(temp_feedback_file)

    def test_appends_jsonl(self, temp_feedback_file):
        from app.feedback import save_feedback
        save_feedback("Q1", "A1", "up")
        save_feedback("Q2", "A2", "down")
        with open(temp_feedback_file) as f:
            lines = f.readlines()
        assert len(lines) == 2

    def test_record_has_required_fields(self, temp_feedback_file):
        from app.feedback import save_feedback
        save_feedback("What is veg symbol?", "Green circle.", "up")
        with open(temp_feedback_file) as f:
            rec = json.loads(f.readline())
        assert "ts" in rec
        assert rec["question"] == "What is veg symbol?"
        assert rec["answer"]   == "Green circle."
        assert rec["rating"]   == "up"

    def test_truncates_long_question(self, temp_feedback_file):
        from app.feedback import save_feedback
        long_q = "x" * 500
        save_feedback(long_q, "ans", "up")
        with open(temp_feedback_file) as f:
            rec = json.loads(f.readline())
        assert len(rec["question"]) <= 300

    def test_saves_down_rating(self, temp_feedback_file):
        from app.feedback import save_feedback
        save_feedback("Q", "A", "down")
        with open(temp_feedback_file) as f:
            rec = json.loads(f.readline())
        assert rec["rating"] == "down"


# ── load_feedback() tests ─────────────────────────────────────────────────────

class TestLoadFeedback:
    def test_returns_empty_list_when_no_file(self):
        from app.feedback import load_feedback
        result = load_feedback()
        assert result == []

    def test_loads_all_records(self, temp_feedback_file):
        from app.feedback import save_feedback, load_feedback
        save_feedback("Q1", "A1", "up")
        save_feedback("Q2", "A2", "down")
        save_feedback("Q3", "A3", "up")
        records = load_feedback()
        assert len(records) == 3

    def test_skips_malformed_lines(self, temp_feedback_file):
        from app.feedback import load_feedback
        with open(temp_feedback_file, "w") as f:
            f.write('{"question":"Q1","rating":"up","ts":"x","answer":"a"}\n')
            f.write("not valid json\n")
            f.write('{"question":"Q2","rating":"down","ts":"x","answer":"b"}\n')
        records = load_feedback()
        assert len(records) == 2


# ── get_feedback_stats() tests ────────────────────────────────────────────────

class TestGetFeedbackStats:
    def test_empty_stats_when_no_file(self):
        from app.feedback import get_feedback_stats
        stats = get_feedback_stats()
        assert stats["total"] == 0
        assert stats["thumbs_up"] == 0
        assert stats["satisfaction_pct"] == 0.0

    def test_counts_correctly(self, temp_feedback_file):
        from app.feedback import save_feedback, get_feedback_stats
        save_feedback("Q1", "A", "up")
        save_feedback("Q2", "A", "up")
        save_feedback("Q3", "A", "down")
        stats = get_feedback_stats()
        assert stats["total"] == 3
        assert stats["thumbs_up"] == 2
        assert stats["thumbs_down"] == 1

    def test_satisfaction_percentage(self, temp_feedback_file):
        from app.feedback import save_feedback, get_feedback_stats
        for _ in range(3):
            save_feedback("Q", "A", "up")
        save_feedback("Q", "A", "down")
        stats = get_feedback_stats()
        assert stats["satisfaction_pct"] == 75.0

    def test_top_questions(self, temp_feedback_file):
        from app.feedback import save_feedback, get_feedback_stats
        save_feedback("veg symbol?", "A", "up")
        save_feedback("veg symbol?", "A", "up")
        save_feedback("font size?",  "A", "up")
        stats = get_feedback_stats()
        assert stats["top_questions"][0]["question"] == "veg symbol?"
        assert stats["top_questions"][0]["count"] == 2

    def test_recent_limited_to_5(self, temp_feedback_file):
        from app.feedback import save_feedback, get_feedback_stats
        for i in range(8):
            save_feedback(f"Q{i}", "A", "up")
        stats = get_feedback_stats()
        assert len(stats["recent"]) == 5

    def test_has_all_required_keys(self, temp_feedback_file):
        from app.feedback import save_feedback, get_feedback_stats
        save_feedback("Q", "A", "up")
        stats = get_feedback_stats()
        for key in ["total", "thumbs_up", "thumbs_down",
                    "satisfaction_pct", "top_questions", "recent"]:
            assert key in stats


# ── API endpoint tests ────────────────────────────────────────────────────────

class TestFeedbackEndpoints:
    def test_feedback_stats_returns_200(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.get("/feedback-stats")
        assert r.status_code == 200

    def test_feedback_stats_has_total(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.get("/feedback-stats")
        assert "total" in r.json()

    def test_submit_feedback_up(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.post("/feedback", json={
            "question": "What is the veg symbol?",
            "answer": "Green circle.",
            "rating": "up"
        })
        assert r.status_code == 200
        assert r.json()["rating"] == "up"

    def test_submit_feedback_down(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.post("/feedback", json={
            "question": "Is nutrition required?",
            "answer": "Not always.",
            "rating": "down"
        })
        assert r.status_code == 200
        assert r.json()["rating"] == "down"

    def test_submit_feedback_invalid_rating(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.post("/feedback", json={
            "question": "Q", "answer": "A", "rating": "maybe"
        })
        assert r.status_code == 422

    def test_submit_feedback_missing_question(self):
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        r = client.post("/feedback", json={"answer": "A", "rating": "up"})
        assert r.status_code == 422
