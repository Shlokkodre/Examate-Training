"""
Streamlit UI for HealthLabelCheck — Day 9
A web interface that lets small food business owners check their FSSAI
label requirements without touching any code.

Run:
    streamlit run app/streamlit_app.py
"""

import os
import sys

import streamlit as st

# Allow imports from project root when running as `streamlit run app/streamlit_app.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.rag import ask
from app.records import load_records, get_mandatory_checklist


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="HealthLabelCheck",
    page_icon="🥘",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/e/e6/FSSAI_logo.svg/200px-FSSAI_logo.svg.png",
        width=120,
    )
    st.title("HealthLabelCheck")
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

    llm_status = "✅ LLM enabled" if os.getenv("GROQ_API_KEY") else "⚠️ No API key — rule-based mode"
    st.caption(llm_status)


# ── Main header ───────────────────────────────────────────────────────────────

st.markdown("## 🥘 HealthLabelCheck")
st.markdown(
    "Ask anything about **FSSAI food labelling regulations** — "
    "what must go on your food packet, font sizes, symbols, dates, and more."
)
st.markdown("---")


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_ask, tab_font, tab_checklist, tab_browse = st.tabs(
    ["💬 Ask a Question", "📐 Font Size Calculator", "✅ Mandatory Checklist", "📋 Browse Regulations"]
)


# ─── Tab 1: Ask a Question ───────────────────────────────────────────────────

with tab_ask:
    st.subheader("Ask about FSSAI Labelling Regulations")

    # Sample questions as quick-pick buttons
    st.caption("Quick questions:")
    sample_questions = [
        "What must be printed on a food label?",
        "What is the vegetarian symbol rule?",
        "Is nutrition information required on small packets?",
        "My laddoos contain groundnuts — what allergen rules apply?",
        "What FSSAI license number must I show on my packet?",
    ]

    cols = st.columns(len(sample_questions))
    selected_sample = None
    for col, q in zip(cols, sample_questions):
        if col.button(q[:30] + "…", help=q, use_container_width=True):
            selected_sample = q

    # Text input — pre-fill if a sample was clicked
    default_text = selected_sample or st.session_state.get("last_question", "")
    user_question = st.text_area(
        "Your question",
        value=default_text,
        placeholder="e.g. What is the minimum font size for my chakli pouch (12cm × 8cm)?",
        height=90,
        key="question_input",
    )

    top_k = st.slider("How many regulation excerpts to use", min_value=1, max_value=5, value=3)

    ask_btn = st.button("🔍 Get Answer", type="primary", use_container_width=True)

    if ask_btn and user_question.strip():
        st.session_state["last_question"] = user_question
        with st.spinner("Searching regulations…"):
            result = ask(user_question.strip(), top_k=top_k)

        st.markdown("---")

        # Source badge
        source_map = {
            "llm": ("🤖 LLM answer", "green"),
            "rule_based": ("📚 Rule-based answer", "orange"),
            "out_of_scope": ("⛔ Out of scope", "red"),
        }
        label, color = source_map.get(result["source"], ("ℹ️ Answer", "blue"))
        st.markdown(f"**{label}**")

        # Answer
        st.markdown(result["answer"])

        # Citations
        if result["citations"]:
            st.markdown("---")
            st.caption(f"📌 Regulations cited: **{', '.join(result['citations'])}**")

        # Chunks used
        st.caption(f"Regulation excerpts used: {result['chunks_used']}")

    elif ask_btn:
        st.warning("Please enter a question first.")


# ─── Tab 2: Font Size Calculator ─────────────────────────────────────────────

with tab_font:
    st.subheader("📐 Minimum Font Size Calculator")
    st.markdown(
        "Enter your package's **principal display panel** dimensions to find "
        "the minimum letter height required by **FSSAI Regulation 6.1**."
    )

    col1, col2 = st.columns(2)
    with col1:
        length_cm = st.number_input("Panel length (cm)", min_value=0.1, value=12.0, step=0.5)
    with col2:
        width_cm = st.number_input("Panel width (cm)", min_value=0.1, value=8.0, step=0.5)

    area = length_cm * width_cm

    # Font size table from FSSAI Regulation 6.1 Table I
    if area < 40:
        min_font = 1.0
        range_label = "< 40 cm²"
    elif area < 170:
        min_font = 1.5
        range_label = "40 – 170 cm²"
    elif area < 650:
        min_font = 2.0
        range_label = "170 – 650 cm²"
    else:
        min_font = 3.0
        range_label = "> 650 cm²"

    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Panel Area", f"{area:.1f} cm²")
    col_b.metric("Size Category", range_label)
    col_c.metric("Minimum Font Height", f"{min_font} mm")

    st.info(
        f"For a **{length_cm} × {width_cm} cm** panel (area = {area:.1f} cm²), "
        f"FSSAI Regulation 6.1 requires a minimum letter height of **{min_font} mm** "
        f"for mandatory declarations (name of food, net quantity, etc.)."
    )

    st.markdown("**FSSAI Regulation 6.1 — Table I**")
    st.table(
        {
            "Panel Area": ["< 40 cm²", "40 – 170 cm²", "170 – 650 cm²", "> 650 cm²"],
            "Min. Letter Height": ["1.0 mm", "1.5 mm", "2.0 mm", "3.0 mm"],
        }
    )


# ─── Tab 3: Mandatory Checklist ──────────────────────────────────────────────

with tab_checklist:
    st.subheader("✅ Mandatory Label Requirements Checklist")
    st.markdown(
        "Every packaged food sold in India must carry these items on the label "
        "under **FSSAI Labelling and Display Regulations 2020**."
    )

    try:
        records = load_records()
        checklist = get_mandatory_checklist(records)
    except Exception as e:
        st.error(f"Could not load records: {e}")
        checklist = []

    if checklist:
        for item in checklist:
            with st.expander(f"☐  **{item['regulation_no']}** — {item['requirement']}"):
                st.markdown(f"**Regulation**: {item['regulation_no']}")
                # Find full record for details
                full = next(
                    (r for r in records if r["regulation_no"] == item["regulation_no"]),
                    None,
                )
                if full:
                    st.markdown(f"**Applies to**: {full['applies_to']}")
                    st.markdown(f"**Details**: {full['details']}")
                    if item.get("exemption") and item["exemption"] != "None":
                        st.markdown(f"**Exemption**: {item['exemption']}")
    else:
        st.warning("No records loaded. Make sure data/records.json exists.")


# ─── Tab 4: Browse Regulations ───────────────────────────────────────────────

with tab_browse:
    st.subheader("📋 Browse All 14 FSSAI Regulations")

    try:
        records = load_records()
    except Exception as e:
        st.error(f"Could not load records: {e}")
        records = []

    if records:
        keyword = st.text_input("🔎 Filter by keyword", placeholder="e.g. allergen, font, veg")

        filtered = records
        if keyword.strip():
            kw = keyword.lower()
            filtered = [
                r for r in records
                if kw in r.get("requirement", "").lower()
                or kw in r.get("details", "").lower()
                or kw in r.get("applies_to", "").lower()
                or kw in r.get("regulation_no", "").lower()
            ]
            st.caption(f"{len(filtered)} regulation(s) match '{keyword}'")

        for rec in filtered:
            with st.expander(f"**Regulation {rec['regulation_no']}** — {rec['requirement']}"):
                st.markdown(f"**Applies to**: {rec['applies_to']}")
                st.markdown(f"**Details**: {rec['details']}")
                if rec.get("exemption") and rec["exemption"] != "None":
                    st.markdown(f"**Exemption**: {rec['exemption']}")
                st.caption(f"Source: {rec.get('source_doc', 'FSSAI Labelling Regulation 2020')}")
    else:
        st.warning("No records loaded.")


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    "HealthLabelCheck — Day 9 Streamlit UI  |  "
    "Data: FSSAI Labelling and Display Regulations 2020  |  "
    "For educational purposes only. Always verify with official FSSAI documents."
)
