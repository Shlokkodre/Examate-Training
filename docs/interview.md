# HealthLabelCheck — Interview Prep

## 60-Second Pitch

"HealthLabelCheck is an AI tool that helps small food business owners in India — like a home-based chakli maker in Kopargaon — check whether their food packet labels comply with FSSAI regulations before they go to print.

The user uploads a photo of their label or asks a question in English, Marathi, or Hindi. The system uses OCR to extract text, runs it against 14 mandatory FSSAI regulations, and returns a green/red compliance table with exact regulation numbers and actionable fixes.

It's built on a FastAPI backend with RAG-powered answers using Gemini, a LangGraph agent for tool calling, a Streamlit UI, and a WhatsApp bot — all deployed on Render. 182 tests, CI on GitHub Actions, live at healthlabelcheck-api-latest.onrender.com."

---

## Hardest Problem Story

**Problem:** The RAG pipeline was returning rule-based answers even after I set the Gemini API key. The answer always ended with "Please set GROQ_API_KEY in .env for natural-language answers."

**Investigation:** I checked `app/rag.py` and found `_call_llm()` was checking `os.getenv("GROQ_API_KEY")` to decide whether to call an LLM — but I had already switched the actual LLM call to Gemini. The check condition was never updated.

**Root cause:** Render was also still holding `LLM_PROVIDER=groq` and `GROQ_MODEL=llama-3.1-70b-versatile` as environment variables, which overrode the code. When Groq deprecated `llama-3.1-70b-versatile`, the error surfaced.

**Fix:** Updated `_call_llm()` to check `GEMINI_API_KEY`, removed all Groq references from `render.yaml`, `requirements.txt`, and `app/llm.py` default, then rebuilt and pushed the Docker image to Docker Hub so Render pulled the new code.

**Lesson:** When migrating LLM providers, check every place that reads env vars — not just the call site. And when deploying via Docker image, pushing to GitHub does nothing; you must rebuild and push the image.

---

## 10 Likely Interview Questions

### 1. What problem does HealthLabelCheck solve?
Small food business owners in India (home-based snack makers) don't know what must be printed on their food packets under FSSAI regulations before they go to print. A wrong or incomplete label can get their products rejected from shops. HealthLabelCheck gives them an instant, plain-language compliance check with exact regulation citations.

### 2. Walk me through the architecture.
The system has four layers:
- **Data**: 14 FSSAI regulations in `records.json`, chunked and indexed in a Chroma vector store using sentence-transformers (all-MiniLM-L6-v2)
- **Backend**: FastAPI with 15+ endpoints — RAG `/ask`, OCR `/ocr-checklist`, font-size calculator, LangGraph `/agent`, WhatsApp `/whatsapp`
- **LLM**: Gemini 2.0 Flash via `google-genai` SDK, with rule-based fallback when no key is set
- **UI**: Streamlit (calls API via HTTP), WhatsApp bot (Twilio TwiML), deployed on Render via Docker

### 3. What is RAG and how did you implement it?
RAG (Retrieval-Augmented Generation) retrieves relevant documents before calling the LLM, so the answer is grounded in real data rather than hallucinated. I chunked each regulation into main + exemption chunks, embedded them with sentence-transformers, stored in Chroma, then at query time retrieved the top-5 most similar chunks and passed them as context to Gemini. The LLM is told to only answer from the provided excerpts.

### 4. Why did you choose Chroma over Pinecone or FAISS?
Chroma is persistent (data survives restarts), runs in-process (no separate server), and has a simple Python API. For 14 regulations (20 chunks), it's more than sufficient. FAISS is faster at scale but requires manual persistence. Pinecone is managed but adds cost and network latency for a small dataset.

### 5. How does the OCR pipeline work?
The user uploads a label photo → Pillow preprocesses it (upscale to 800px min width, sharpen, boost contrast) → EasyOCR extracts text → `label_checker.py` runs 14 regex rules against the extracted text → returns a present/missing table with hints. The same pipeline supports 3 languages via `multilang_checker.py`.

### 6. What is LangGraph and why did you use it?
LangGraph is a framework for building stateful, multi-step LLM workflows as a graph. I used it for the `/agent` endpoint: the LLM decides which tool to call (font-size calculator, semantic search, checklist, regulation lookup), executes it, and loops until it has enough information to answer. `MemorySaver` gives it conversation memory across turns. `interrupt_before=["tools"]` enables human-in-the-loop approval before tool execution.

### 7. How did you handle multi-language support?
`app/translations.py` contains EN/MR/HI translations for all 14 regulation names, hints, and 8 UI strings. `multilang_checker.py` wraps `label_checker.py` and adds `requirement_translated` and `hint_translated` fields. The WhatsApp bot stores per-user language preference in an in-memory dict keyed by phone number. The `/ocr-checklist-lang` endpoint accepts a `lang` query parameter.

### 8. How is the app deployed?
Two Docker containers on Render free tier:
- `healthlabelcheck-api` — FastAPI backend (`Dockerfile.api`, CPU-only torch to keep image size down)
- `healthlabelcheck-web` — Streamlit UI (`Dockerfile.web`, only installs streamlit + requests)
Both images are pushed to Docker Hub (`shlok0626/healthlabelcheck-*`). `render.yaml` defines both services, with `API_BASE` injected via Render's `fromService` property so the UI always knows the API's URL.

### 9. How did you ensure code quality?
182 unit and integration tests across 5 test files using pytest:
- `test_pdf_parser.py` — 27 tests (PDF extraction, section splitting, pipeline)
- `test_label_checker.py` — 32 tests (regex rules, compliance summary)
- `test_translations.py` — 32 tests (all languages, fallbacks, Devanagari)
- `test_whatsapp_bot.py` — 51 tests (intent parsing, session state, TwiML)
- `test_integration.py` — 40 tests (every FastAPI endpoint via TestClient)

GitHub Actions CI runs all 182 tests on every push to main.

### 10. What would you improve with more time?
- **Real PDF parsing**: Fetch the actual FSSAI PDF instead of a curated table — the FSSAI server currently returns 502 so the fallback table is used
- **Label photo OCR accuracy**: Fine-tune EasyOCR on Indian food label fonts; current accuracy is ~80% on printed labels
- **WhatsApp persistence**: Replace in-memory language sessions with Redis so sessions survive server restarts
- **LLM evaluation**: Add an automated eval that scores Gemini answers against the 15-question eval set and alerts if quality drops below 90%
- **User auth**: Add phone number verification for the WhatsApp bot to prevent abuse

---

## Key Numbers to Remember

| Metric | Value |
|--------|-------|
| FSSAI regulations covered | 14 (5.1–5.12, 6.1–6.2) |
| API endpoints | 15+ |
| Test count | 182 / 182 passing |
| Languages supported | 3 (EN, MR, HI) |
| RAG eval score | Config B: 15/15 (100%) |
| Days completed | 15 |
| Live URL | healthlabelcheck-api-latest.onrender.com |
