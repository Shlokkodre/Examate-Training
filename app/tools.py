"""
Day 9 — LangChain Tools for HealthLabelCheck agent
Exposes domain functions as @tool-decorated callables so LangGraph
can let the LLM decide when to call them.

Tools:
  min_font_size_checker  — Regulation 6.1 font size from panel dimensions
  search_regulations     — semantic vector search over 14 FSSAI regulations
  get_mandatory_checklist — returns all mandatory label items
  get_regulation_by_id   — fetch a specific regulation by number
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langchain_core.tools import tool

from app.models import get_min_font_size
from app.vectorstore import semantic_search
from app.records import load_records, get_mandatory_checklist, get_by_id


# ── Tool 1: Font size calculator ──────────────────────────────────────────────

@tool
def min_font_size_checker(panel_length_cm: float, panel_width_cm: float) -> str:
    """
    Calculate the minimum letter height required by FSSAI Regulation 6.1
    for a food packet label given the principal display panel dimensions.

    Args:
        panel_length_cm: Length of the principal display panel in centimetres.
        panel_width_cm:  Width of the principal display panel in centimetres.

    Returns:
        A plain-English string with the panel area and minimum font height.
    """
    area = panel_length_cm * panel_width_cm
    min_height = get_min_font_size(area)

    if area < 40:
        range_label = "< 40 cm²"
    elif area < 170:
        range_label = "40–170 cm²"
    elif area < 650:
        range_label = "170–650 cm²"
    else:
        range_label = "> 650 cm²"

    return (
        f"Panel area: {area:.1f} cm² (category: {range_label}). "
        f"Minimum letter height per FSSAI Regulation 6.1: {min_height} mm. "
        f"This applies to the name of food, net quantity, and all mandatory "
        f"declarations on the principal display panel."
    )


# ── Tool 2: Semantic search ───────────────────────────────────────────────────

@tool
def search_regulations(query: str, top_k: int = 3) -> str:
    """
    Search FSSAI food labelling regulations using semantic similarity.
    Use this to find which regulations are relevant to a user's question.

    Args:
        query: A natural-language question or keyword about food labelling.
        top_k: Number of top results to return (default 3, max 5).

    Returns:
        A formatted string listing the most relevant regulations with details.
    """
    top_k = min(int(top_k), 5)
    try:
        hits = semantic_search(query, top_k=top_k)
    except Exception as e:
        return f"Search error: {e}"

    if not hits:
        return "No relevant regulations found for that query."

    lines = [f"Top {len(hits)} regulations for '{query}':\n"]
    for i, h in enumerate(hits, 1):
        lines.append(
            f"{i}. Regulation {h['regulation_no']} — {h['title']} "
            f"(score: {h['score']:.3f})\n"
            f"   {h['text'][:200]}{'…' if len(h['text']) > 200 else ''}"
        )
    return "\n".join(lines)


# ── Tool 3: Mandatory checklist ───────────────────────────────────────────────

@tool
def get_mandatory_checklist_tool() -> str:
    """
    Return the complete list of mandatory FSSAI labelling requirements
    that apply to every packaged food sold in India.
    Use this when the user asks what must be on their label.

    Returns:
        A numbered checklist of mandatory label items with regulation numbers.
    """
    try:
        records = load_records()
        checklist = get_mandatory_checklist(records)
    except Exception as e:
        return f"Could not load checklist: {e}"

    if not checklist:
        return "No mandatory checklist items found."

    lines = [f"Mandatory FSSAI label requirements ({len(checklist)} items):\n"]
    for i, item in enumerate(checklist, 1):
        exemption = item.get("exemption", "None")
        ex_note = f" [Exemption: {exemption}]" if exemption and exemption != "None" else ""
        lines.append(f"{i}. Regulation {item['regulation_no']}: {item['requirement']}{ex_note}")
    return "\n".join(lines)


# ── Tool 4: Get regulation by ID ──────────────────────────────────────────────

@tool
def get_regulation_by_id(regulation_no: str) -> str:
    """
    Retrieve full details of a specific FSSAI regulation by its number,
    for example '5.10' for the Veg/Non-Veg Symbol rule.

    Args:
        regulation_no: The regulation number string, e.g. '5.3', '6.1'.

    Returns:
        Full details of the regulation including applies_to and exemption.
    """
    try:
        records = load_records()
        rec = get_by_id(records, regulation_no)
    except Exception as e:
        return f"Could not load records: {e}"

    if rec is None:
        return f"Regulation {regulation_no} not found. Valid numbers: 5.1–5.12, 6.1, 6.2."

    return (
        f"Regulation {rec['regulation_no']}: {rec['requirement']}\n"
        f"Applies to : {rec['applies_to']}\n"
        f"Details    : {rec['details']}\n"
        f"Exemption  : {rec['exemption']}\n"
        f"Source     : {rec['source_doc']}"
    )


# ── Tool registry (convenient list for the agent) ────────────────────────────

TOOLS = [
    min_font_size_checker,
    search_regulations,
    get_mandatory_checklist_tool,
    get_regulation_by_id,
]


if __name__ == "__main__":
    print("=== Testing tools.py ===\n")

    print("Tool 1 — min_font_size_checker(12, 8):")
    print(min_font_size_checker.invoke({"panel_length_cm": 12, "panel_width_cm": 8}))

    print("\nTool 2 — search_regulations('vegetarian symbol'):")
    print(search_regulations.invoke({"query": "vegetarian symbol", "top_k": 2}))

    print("\nTool 3 — get_mandatory_checklist_tool():")
    result = get_mandatory_checklist_tool.invoke({})
    print(result[:400], "…")

    print("\nTool 4 — get_regulation_by_id('5.10'):")
    print(get_regulation_by_id.invoke({"regulation_no": "5.10"}))
