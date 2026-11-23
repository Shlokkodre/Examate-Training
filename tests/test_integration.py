"""
Day 15 — End-to-end integration tests for HealthLabelCheck
Spins up a real FastAPI TestClient and tests every endpoint end-to-end.
No mocking — real records, real RAG pipeline, real logic.

Run from repo root:
    python -m pytest tests/test_integration.py -v
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Health & Root ─────────────────────────────────────────────────────────────

class TestHealthAndRoot:
    def test_health_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_has_required_fields(self):
        r = client.get("/health")
        data = r.json()
        assert data["status"] == "healthy"
        assert data["records_loaded"] == 14
        assert "service" in data

    def test_root_returns_endpoint_map(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "health" in data["endpoints"]
        assert "records" in data["endpoints"]


# ── Records ───────────────────────────────────────────────────────────────────

class TestRecords:
    def test_get_records_default_limit(self):
        r = client.get("/records")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_get_records_custom_limit(self):
        r = client.get("/records?limit=3")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_get_records_all_14(self):
        r = client.get("/records?limit=14")
        assert r.status_code == 200
        assert len(r.json()) == 14

    def test_record_has_required_fields(self):
        r = client.get("/records?limit=1")
        rec = r.json()[0]
        for field in ["regulation_no", "requirement", "applies_to", "details", "exemption", "source_doc"]:
            assert field in rec

    def test_get_record_by_id_510(self):
        r = client.get("/records/5.10")
        assert r.status_code == 200
        data = r.json()
        assert data["regulation_no"] == "5.10"
        assert "veg" in data["requirement"].lower() or "symbol" in data["requirement"].lower()

    def test_get_record_by_id_61(self):
        r = client.get("/records/6.1")
        assert r.status_code == 200
        assert r.json()["regulation_no"] == "6.1"

    def test_get_record_not_found(self):
        r = client.get("/records/99.9")
        assert r.status_code == 404

    def test_get_record_not_found_message(self):
        r = client.get("/records/99.9")
        assert "not found" in r.json()["detail"].lower()


# ── Search ────────────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_vegetarian(self):
        r = client.get("/search?q=vegetarian")
        assert r.status_code == 200
        results = r.json()
        assert len(results) >= 1
        reg_nos = [rec["regulation_no"] for rec in results]
        assert "5.10" in reg_nos

    def test_search_fssai_license(self):
        r = client.get("/search?q=FSSAI+license")
        assert r.status_code == 200
        results = r.json()
        assert any(rec["regulation_no"] == "5.8" for rec in results)

    def test_search_no_results(self):
        r = client.get("/search?q=xyznonexistent999")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_semantic_search_font_size(self):
        r = client.get("/search/semantic?q=font+size&top_k=2")
        assert r.status_code == 200
        results = r.json()
        assert len(results) >= 1
        assert results[0]["regulation_no"] == "6.1"
        assert results[0]["score"] > 0.5

    def test_semantic_search_returns_scores(self):
        r = client.get("/search/semantic?q=allergen&top_k=3")
        assert r.status_code == 200
        for hit in r.json():
            assert "score" in hit
            assert "regulation_no" in hit
            assert "text" in hit


# ── Font Size Calculator ──────────────────────────────────────────────────────

class TestFontSize:
    def test_12x8_panel(self):
        r = client.post("/font-size", json={"panel_length_cm": 12, "panel_width_cm": 8})
        assert r.status_code == 200
        data = r.json()
        assert data["panel_area_cm2"] == 96.0
        assert data["min_letter_height_mm"] == 1.5
        assert data["regulation"] == "6.1"

    def test_small_panel_under_40(self):
        r = client.post("/font-size", json={"panel_length_cm": 5, "panel_width_cm": 7})
        assert r.status_code == 200
        assert r.json()["min_letter_height_mm"] == 1.0

    def test_large_panel_over_650(self):
        r = client.post("/font-size", json={"panel_length_cm": 30, "panel_width_cm": 25})
        assert r.status_code == 200
        assert r.json()["min_letter_height_mm"] == 3.0

    def test_medium_panel_170_to_650(self):
        r = client.post("/font-size", json={"panel_length_cm": 20, "panel_width_cm": 15})
        assert r.status_code == 200
        assert r.json()["min_letter_height_mm"] == 2.0

    def test_negative_dimension_rejected(self):
        r = client.post("/font-size", json={"panel_length_cm": -5, "panel_width_cm": 8})
        assert r.status_code == 422

    def test_zero_dimension_rejected(self):
        r = client.post("/font-size", json={"panel_length_cm": 0, "panel_width_cm": 8})
        assert r.status_code == 422


# ── Mandatory Checklist ───────────────────────────────────────────────────────

class TestMandatoryChecklist:
    def test_returns_10_items(self):
        r = client.get("/mandatory-checklist")
        assert r.status_code == 200
        assert len(r.json()) == 10

    def test_all_apply_to_packaged_foods(self):
        r = client.get("/mandatory-checklist")
        for item in r.json():
            assert "packaged" in item["applies_to"].lower()

    def test_contains_key_regulations(self):
        r = client.get("/mandatory-checklist")
        reg_nos = [item["regulation_no"] for item in r.json()]
        for expected in ["5.1", "5.6", "5.8", "5.10", "6.1"]:
            assert expected in reg_nos


# ── RAG /ask ──────────────────────────────────────────────────────────────────

class TestAsk:
    def test_ask_returns_200(self):
        r = client.post("/ask", json={"question": "What is the veg symbol rule?", "top_k": 3})
        assert r.status_code == 200

    def test_ask_has_required_fields(self):
        r = client.post("/ask", json={"question": "What is the veg symbol rule?", "top_k": 3})
        data = r.json()
        for field in ["answer", "citations", "chunks_used", "source"]:
            assert field in data

    def test_ask_veg_symbol_cites_510(self):
        r = client.post("/ask", json={"question": "What is the veg symbol rule?", "top_k": 3})
        assert "5.10" in r.json()["citations"]

    def test_ask_font_size_cites_61(self):
        r = client.post("/ask", json={"question": "What is the minimum font size?", "top_k": 3})
        assert "6.1" in r.json()["citations"]

    def test_ask_out_of_scope(self):
        r = client.post("/ask", json={"question": "What is the cheapest printer in Kopargaon?", "top_k": 3})
        assert r.status_code == 200
        assert r.json()["source"] == "out_of_scope"

    def test_ask_empty_question_rejected(self):
        r = client.post("/ask", json={"question": "", "top_k": 3})
        assert r.status_code == 422

    def test_ask_chunks_used_matches_top_k(self):
        r = client.post("/ask", json={"question": "What is the veg symbol?", "top_k": 3})
        data = r.json()
        if data["source"] != "out_of_scope":
            assert data["chunks_used"] <= 3


# ── Questions endpoint ────────────────────────────────────────────────────────

class TestQuestions:
    def test_veg_question(self):
        r = client.post("/questions", json={"question": "What is the vegetarian symbol?"})
        assert r.status_code == 200
        data = r.json()
        assert "5.10" in data["relevant_regulations"]

    def test_font_question(self):
        r = client.post("/questions", json={"question": "What font size do I need?"})
        assert r.status_code == 200
        assert "6.1" in r.json()["relevant_regulations"]

    def test_nutrition_question(self):
        r = client.post("/questions", json={"question": "Is nutrition information required?"})
        assert r.status_code == 200
        assert "5.3" in r.json()["relevant_regulations"]


# ── WhatsApp webhook ──────────────────────────────────────────────────────────

class TestWhatsAppWebhook:
    def test_health_endpoint(self):
        r = client.get("/whatsapp/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_webhook_hi_message(self):
        r = client.post("/whatsapp", data={"From": "whatsapp:+919876543210", "Body": "hi"})
        assert r.status_code == 200
        assert "xml" in r.headers["content-type"]
        assert "HealthLabelCheck" in r.text

    def test_webhook_checklist_message(self):
        r = client.post("/whatsapp", data={"From": "whatsapp:+919876543210", "Body": "checklist"})
        assert r.status_code == 200
        assert "5.1" in r.text

    def test_webhook_font_message(self):
        r = client.post("/whatsapp", data={"From": "whatsapp:+919876543210", "Body": "font 12 8"})
        assert r.status_code == 200
        assert "1.5" in r.text

    def test_webhook_twiml_format(self):
        r = client.post("/whatsapp", data={"From": "whatsapp:+919876543210", "Body": "help"})
        assert r.status_code == 200
        assert "<Response>" in r.text
        assert "<Message>" in r.text
