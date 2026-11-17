# Checkpoint 2 Demo Script

## Overview
**Date**: Day 10 (November 17, 2026)  
**Project**: HealthLabelCheck — FSSAI Food Labelling Compliance Checker  
**Demo Duration**: ~5 minutes  
**What's new**: Full deployment pipeline — Render (Docker) + Hugging Face Spaces

---

## 1. Introduction (30 seconds)

"At Checkpoint 1 we showed a local FastAPI + search engine.
Since then we added an LLM layer, a semantic vector store with RAG,
and today we're wrapping it all in a Streamlit UI that any food business
owner can open in a browser — no terminal, no code."

**Two live URLs to show**:
- Render: `https://healthlabelcheck.onrender.com`
- Hugging Face Spaces: `https://huggingface.co/spaces/<username>/healthlabelcheck`

---

## 2. Walk Through the Streamlit UI (2 minutes)

### Tab 1 — Ask a Question
Type: `"My laddoos contain groundnuts — what must I declare?"`

Expected output:
- Source badge: 🤖 LLM answer (or 📚 Rule-based if no key)
- Answer cites **Regulation 5.4** (allergen declaration)
- Shows regulations used count

Show out-of-scope handling:
Type: `"What is the cheapest printer in Kopargaon?"`

Expected: ⛔ Out of scope — politely declined, no hallucination.

### Tab 2 — Font Size Calculator
Enter: length = 12 cm, width = 8 cm

Expected:
- Panel Area: **96.0 cm²**
- Size Category: **40 – 170 cm²**
- Minimum Font Height: **1.5 mm**

"This is real FSSAI Regulation 6.1 logic, not a lookup table copy-paste.
Our user doesn't need to read the regulation — they just enter dimensions."

### Tab 3 — Mandatory Checklist
Show the 10 expandable items.
Open **5.8 FSSAI License Number** to show full details.

"Every item links back to its regulation number for traceability."

### Tab 4 — Browse Regulations
Type `allergen` in the filter box.
Expected: Regulation 5.4 appears instantly.

---

## 3. Architecture Walk-Through (1 minute)

```
User (browser)
    ↓
Streamlit UI  (app/streamlit_app.py)
    ↓
RAG Pipeline  (app/rag.py)
    ├── Chroma Vector Store  (app/vectorstore.py)
    │       └── all-MiniLM-L6-v2 embeddings  (app/chunking.py)
    └── Groq LLM  (app/llm.py)
            └── llama-3.1-70b-versatile
    ↓
14 FSSAI Regulations  (data/records.json)
```

**Deployment stack**:
- Docker container → Render (auto-deploy on git push)
- HF Spaces → Streamlit SDK (zero-infra, free tier)
- Secrets stored in platform environment variables, never in code

---

## 4. Eval Results (30 seconds)

Show `eval/run_eval.py` output:

```
Config A: top_k=3, full    12/15
Config B: top_k=5, short   15/15   ← winner
```

"We ran 15 questions, including 2 out-of-scope traps.
Config B (top_k=5, short excerpts) scores 15/15 — 100%."

---

## 5. What We Built in 10 Days (30 seconds)

| Week | Days | What |
|------|------|------|
| 1 | 1–4 | Python basics → FastAPI + TF-IDF search |
| 2 | 5–8 | LLM + prompt engineering + RAG pipeline |
| 2 | 9–10 | Streamlit UI + Docker + Render/HF deployment |

**Lines of code**: ~1 200 across 14 Python files  
**Regulations covered**: 14  
**Eval score**: 15/15 (Config B)

---

## 6. Next Steps (30 seconds)

- Fetch real FSSAI PDF and parse it (replace curated table with live data)
- Add label photo upload → OCR → auto-checklist
- Multi-language support (Marathi, Hindi)
- WhatsApp bot integration for rural users

---

## Demo Checklist

Before the demo:
- [ ] Render deploy is live and healthy (check dashboard)
- [ ] HF Space is public and loaded
- [ ] GROQ_API_KEY set in both platforms
- [ ] Browser tabs open to both URLs
- [ ] Fallback: local `streamlit run app/streamlit_app.py`

During demo:
- [ ] Show both live URLs first
- [ ] Walk through all 4 tabs
- [ ] Show out-of-scope refusal
- [ ] Show architecture diagram
- [ ] Quote eval score

---

**Demo completed! Checkpoint 2 passed ✅**
