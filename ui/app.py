"""
Day 10 — HealthLabelCheck Streamlit UI
Calls the FastAPI backend via HTTP (POST /ask, POST /agent, POST /font-size)
instead of importing app modules directly.

Adds 👍 / 👎 feedback buttons that append to data/feedback.jsonl.

Run (with backend already running on :8000):
    streamlit run ui/app.py
"""

import json
import os
import datetime
import requests
import streamlit as st

# ── Backend base URL ──────────────────────────────────────────────────────────
# Render's `fromService ... property: host` supplies a bare hostname
# (healthlabelcheck-api.onrender.com), so normalize it to a full URL.
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
if API_BASE and not API_BASE.startswith(("http://", "https://")):
    API_BASE = f"https://{API_BASE}"
if API_BASE and not API_BASE.startswith(("http://", "https://")):
    API_BASE = f"https://{API_BASE}"

# ── Feedback file ─────────────────────────────────────────────────────────────
FEEDBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "feedback.jsonl"
)
os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)


def save_feedback(question: str, answer: str, rating: str) -> None:
    """Append one feedback record to data/feedback.jsonl."""
    record = {
        "ts":       datetime.datetime.utcnow().isoformat(),
        "question": question,
        "answer":   answer[:300],
        "rating":   rating,          # "up" or "down"
    }
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── API helpers ───────────────────────────────────────────────────────────────

def call_ask(question: str, top_k: int = 5) -> dict:
    """POST /ask — RAG answer with citations. Retries once on timeout (Render wake-up)."""
    for attempt in range(2):
        try:
            r = requests.post(
                f"{API_BASE}/ask",
                json={"question": question, "top_k": top_k},
                timeout=90,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            if attempt == 0:
                continue  # retry once
            return {"answer": "The server took too long to respond. It may be waking up — please try again in 30 seconds.",
                    "citations": [], "chunks_used": 0, "source": "error"}
        except requests.exceptions.ConnectionError:
            return {"answer": f"Cannot reach backend at {API_BASE}. Is the FastAPI server running?",
                    "citations": [], "chunks_used": 0, "source": "error"}
        except Exception as e:
            return {"answer": f"Error: {e}", "citations": [], "chunks_used": 0, "source": "error"}


def call_font_size(length: float, width: float) -> dict:
    """POST /font-size — Regulation 6.1 calculator."""
    try:
        r = requests.post(
            f"{API_BASE}/font-size",
            json={"panel_length_cm": length, "panel_width_cm": width},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def call_checklist() -> list:
    """GET /mandatory-checklist."""
    try:
        r = requests.get(f"{API_BASE}/mandatory-checklist", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return []


def call_browse(limit: int = 14) -> list:
    """GET /records."""
    try:
        r = requests.get(f"{API_BASE}/records", params={"limit": limit}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return []


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="HealthLabelCheck",
    page_icon="🥘",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🥘 HealthLabelCheck")
    st.caption("FSSAI Food Labelling Advisor")
    st.markdown("---")
    st.markdown(
        "**What can I help with?**\n"
        "- Mandatory label requirements\n"
        "- Font size calculator\n"
        "- Mandatory checklist\n"
        "- Allergen & additive rules\n"
        "- Veg / Non-veg symbol rules\n"
        "- Nutritional info requirements"
    )
    st.markdown("---")
    st.markdown(
        "**Target users**: Home-based snack makers (chakli, laddoo, farsan) "
        "who need to print compliant labels before selling in shops."
    )
    st.markdown("---")

    # Backend health + auto wake-up ping
    try:
        h = requests.get(f"{API_BASE}/health", timeout=10).json()
        st.success(f"API online — {h.get('records_loaded', '?')} regulations loaded")
    except requests.exceptions.Timeout:
        st.warning("⏳ API is waking up — first request may take 30s. Please wait.")
    except Exception:
        st.error(f"API offline ({API_BASE})")

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("## 🥘 HealthLabelCheck")
st.markdown(
    "Ask anything about **FSSAI food labelling regulations** — "
    "what must go on your food packet, font sizes, symbols, dates, and more."
)
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_ask, tab_font, tab_checklist, tab_browse, tab_ocr, tab_stats = st.tabs(
    ["💬 Ask a Question", "📐 Font Size Calculator", "✅ Mandatory Checklist",
     "📋 Browse Regulations", "📸 Label Photo Check", "📊 Feedback Stats"]
)

# ─── Tab 1: Ask a Question ────────────────────────────────────────────────────

with tab_ask:
    st.subheader("Ask about FSSAI Labelling Regulations")

    sample_questions = [
        "What must be printed on a food label?",
        "What is the vegetarian symbol rule?",
        "Is nutrition info required on small packets?",
        "My laddoos contain groundnuts — allergen rules?",
        "What FSSAI license number must I show?",
    ]

    st.caption("Quick questions:")
    cols = st.columns(len(sample_questions))
    selected_sample = None
    for col, q in zip(cols, sample_questions):
        if col.button(q[:28] + "…", help=q, use_container_width=True):
            selected_sample = q

    default_text = selected_sample or st.session_state.get("last_question", "")
    user_question = st.text_area(
        "Your question",
        value=default_text,
        placeholder="e.g. What is the minimum font size for my chakli pouch (12 cm × 8 cm)?",
        height=90,
        key="question_input",
    )

    top_k = st.slider("Regulation excerpts to use", min_value=1, max_value=5, value=5)
    ask_btn = st.button("🔍 Get Answer", type="primary", use_container_width=True)

    if ask_btn and user_question.strip():
        st.session_state["last_question"] = user_question
        with st.spinner("Searching regulations… (first request may take ~30s if server just woke up)"):
            result = call_ask(user_question.strip(), top_k=top_k)

        st.markdown("---")

        source_map = {
            "llm":        "🤖 LLM answer",
            "rule_based": "📚 Rule-based answer",
            "out_of_scope": "⛔ Out of scope",
            "error":      "❌ Error",
        }
        st.markdown(f"**{source_map.get(result.get('source',''), 'Answer')}**")
        st.markdown(result.get("answer", ""))

        citations = result.get("citations", [])
        if citations:
            st.caption(f"📌 Regulations cited: **{', '.join(citations)}**")
        st.caption(f"Excerpts used: {result.get('chunks_used', 0)}")

        # ── 👍 / 👎 feedback ──────────────────────────────────────────────────
        st.markdown("---")
        st.caption("Was this answer helpful?")
        fb_col1, fb_col2, _ = st.columns([1, 1, 6])
        if fb_col1.button("👍", key="up", use_container_width=True):
            save_feedback(user_question, result.get("answer", ""), "up")
            st.success("Thanks for the feedback!")
        if fb_col2.button("👎", key="down", use_container_width=True):
            save_feedback(user_question, result.get("answer", ""), "down")
            st.info("Sorry it wasn't helpful — feedback saved.")

    elif ask_btn:
        st.warning("Please enter a question first.")

# ─── Tab 2: Font Size Calculator ─────────────────────────────────────────────

with tab_font:
    st.subheader("📐 Minimum Font Size Calculator")
    st.markdown(
        "Enter your **principal display panel** dimensions to get the minimum "
        "letter height required by **FSSAI Regulation 6.1**."
    )

    c1, c2 = st.columns(2)
    with c1:
        length_cm = st.number_input("Panel length (cm)", min_value=0.1, value=12.0, step=0.5)
    with c2:
        width_cm = st.number_input("Panel width (cm)",  min_value=0.1, value=8.0,  step=0.5)

    result_fs = call_font_size(length_cm, width_cm)

    if "error" not in result_fs:
        area      = result_fs.get("panel_area_cm2", length_cm * width_cm)
        min_font  = result_fs.get("min_letter_height_mm", "—")
    else:
        area      = length_cm * width_cm
        # fallback local calc
        if area < 40:   min_font, range_label = 1.0, "< 40 cm²"
        elif area < 170: min_font, range_label = 1.5, "40–170 cm²"
        elif area < 650: min_font, range_label = 2.0, "170–650 cm²"
        else:            min_font, range_label = 3.0, "> 650 cm²"

    if area < 40:   range_label = "< 40 cm²"
    elif area < 170: range_label = "40–170 cm²"
    elif area < 650: range_label = "170–650 cm²"
    else:            range_label = "> 650 cm²"

    st.markdown("---")
    ca, cb, cc = st.columns(3)
    ca.metric("Panel Area",          f"{area:.1f} cm²")
    cb.metric("Size Category",       range_label)
    cc.metric("Min. Letter Height",  f"{min_font} mm")

    st.info(
        f"For a **{length_cm} × {width_cm} cm** panel, FSSAI Regulation 6.1 requires "
        f"**{min_font} mm** minimum letter height for mandatory declarations."
    )

    st.markdown("**FSSAI Regulation 6.1 — Table I**")
    st.table({
        "Panel Area":        ["< 40 cm²", "40–170 cm²", "170–650 cm²", "> 650 cm²"],
        "Min. Letter Height": ["1.0 mm",   "1.5 mm",     "2.0 mm",      "3.0 mm"],
    })

# ─── Tab 3: Mandatory Checklist ───────────────────────────────────────────────

with tab_checklist:
    st.subheader("✅ Mandatory Label Requirements Checklist")
    st.markdown(
        "Every packaged food sold in India must carry these items on the label "
        "under **FSSAI Labelling and Display Regulations 2020**."
    )

    checklist = call_checklist()
    if checklist:
        for item in checklist:
            with st.expander(f"☐  **{item['regulation_no']}** — {item['requirement']}"):
                st.markdown(f"**Applies to**: {item.get('applies_to', '')}")
                st.markdown(f"**Details**: {item.get('details', '')}")
                ex = item.get("exemption", "None")
                if ex and ex != "None":
                    st.markdown(f"**Exemption**: {ex}")
    else:
        st.warning("Could not load checklist — is the API running?")

# ─── Tab 4: Browse Regulations ────────────────────────────────────────────────

with tab_browse:
    st.subheader("📋 Browse All 14 FSSAI Regulations")
    records = call_browse()

    if records:
        keyword = st.text_input("🔎 Filter by keyword",
                                placeholder="e.g. allergen, font, veg")
        if keyword.strip():
            kw = keyword.lower()
            records = [
                r for r in records
                if kw in r.get("requirement",  "").lower()
                or kw in r.get("details",       "").lower()
                or kw in r.get("applies_to",    "").lower()
                or kw in r.get("regulation_no", "").lower()
            ]
            st.caption(f"{len(records)} regulation(s) match '{keyword}'")

        for rec in records:
            with st.expander(f"**Regulation {rec['regulation_no']}** — {rec['requirement']}"):
                st.markdown(f"**Applies to**: {rec.get('applies_to', '')}")
                st.markdown(f"**Details**: {rec.get('details', '')}")
                ex = rec.get("exemption", "None")
                if ex and ex != "None":
                    st.markdown(f"**Exemption**: {ex}")
                st.caption(f"Source: {rec.get('source_doc', 'FSSAI 2020')}")
    else:
        st.warning("Could not load regulations — is the API running?")

# ── Footer ────────────────────────────────────────────────────────────────────

# ─── Tab 5: Label Photo Check (OCR) ──────────────────────────────────────────

with tab_ocr:
    st.subheader("📸 Upload Label Photo → Compliance Check")
    st.markdown(
        "Upload a photo of your food packet label. The system uses OCR to extract "
        "the text and checks it against all 14 FSSAI regulations."
    )

    lang_ocr = st.selectbox(
        "Result language",
        options=["en", "mr", "hi"],
        format_func=lambda x: {"en": "English", "mr": "Marathi", "hi": "Hindi"}[x],
    )

    uploaded = st.file_uploader(
        "Upload label image", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded:
        st.image(uploaded, caption="Uploaded label", width=300)
        with st.spinner("Running OCR and checking regulations…"):
            try:
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                r = requests.post(
                    f"{API_BASE}/ocr-checklist-lang",
                    files=files,
                    params={"lang": lang_ocr},
                    timeout=60,
                )
                r.raise_for_status()
                data = r.json()

                st.markdown("---")
                summary = data.get("summary", {})
                pct = summary.get("compliance_pct", 0)
                col1, col2, col3 = st.columns(3)
                col1.metric("Mandatory Present", f"{summary.get('mandatory_present', 0)}/{summary.get('mandatory_total', 0)}")
                col2.metric("Compliance", f"{pct}%")
                col3.metric("Missing", summary.get("mandatory_missing", 0))

                st.markdown("### Regulation Results")
                for item in data.get("results", []):
                    icon = "✅" if item["status"] == "present" else "❌"
                    req = item.get("requirement_translated") or item["requirement"]
                    st.markdown(f"{icon} **{item['regulation_no']}** — {req}")
                    if item["status"] == "missing" and item.get("hint_translated"):
                        st.caption(f"   → {item['hint_translated']}")

                with st.expander("Raw OCR text"):
                    st.text(data.get("ocr_text", ""))

            except Exception as e:
                st.error(f"Error: {e}")


# ─── Tab 6: Feedback Stats ────────────────────────────────────────────────────

with tab_stats:
    st.subheader("📊 User Feedback Statistics")

    try:
        r = requests.get(f"{API_BASE}/feedback-stats", timeout=10)
        r.raise_for_status()
        stats = r.json()
    except Exception as e:
        st.error(f"Could not load stats: {e}")
        stats = {}

    if stats and stats.get("total", 0) > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Feedback",  stats["total"])
        c2.metric("👍 Thumbs Up",    stats["thumbs_up"])
        c3.metric("Satisfaction",    f"{stats['satisfaction_pct']}%")

        st.markdown("---")
        st.markdown("**Top Questions Asked**")
        for q in stats.get("top_questions", []):
            st.markdown(f"- ({q['count']}×) {q['question'][:80]}")

        st.markdown("---")
        st.markdown("**Recent Feedback**")
        for entry in stats.get("recent", []):
            icon = "👍" if entry.get("rating") == "up" else "👎"
            st.markdown(f"{icon} {entry.get('question', '')[:80]}")
    else:
        st.info("No feedback yet. Ask a question and rate the answer to see stats here.")

    if st.button("Refresh", use_container_width=True):
        st.rerun()


st.markdown("---")
st.caption(
    "HealthLabelCheck — Day 16 UI  |  "
    "Data: FSSAI Labelling and Display Regulations 2020  |  "
    "For educational purposes only. Always verify with official FSSAI documents."
)
