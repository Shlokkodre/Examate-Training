"""
Day 9 — Agent loop for HealthLabelCheck
Decides at each step whether to call a tool (RAG search, font-size
calculator, checklist, regulation lookup) or return a final answer.

The logic mirrors the ReAct pattern:
  - If the last message is a ToolMessage → pass back to the LLM.
  - If the LLM returned tool_calls → route to the tool node.
  - Otherwise → END (final answer ready).

No LangGraph import is needed here; this module only contains the
routing function and a convenience run() wrapper used by graph.py.
"""

from typing import Literal
from langchain_core.messages import AIMessage


def should_continue(state: dict) -> Literal["tools", "__end__"]:
    """
    Routing function for LangGraph conditional edge.

    Inspect the last message produced by the LLM node.
    - If it carries tool_calls  →  route to the 'tools' node.
    - Otherwise                 →  END (final answer).
    """
    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    last = messages[-1]
    # LangChain AIMessage exposes tool_calls as a list (empty if none)
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "__end__"


def format_final_answer(state: dict) -> str:
    """
    Extract the final text answer from a completed graph state.
    Returns the content of the last AIMessage, or an error string.
    """
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                # Some providers return content as a list of blocks
                parts = [
                    b.get("text", "") if isinstance(b, dict) else str(b)
                    for b in content
                ]
                return " ".join(p for p in parts if p).strip()
            return str(content).strip()
    return "No answer produced."


if __name__ == "__main__":
    # Minimal smoke test without a live LLM
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    # Simulate: LLM decided to call a tool
    state_with_tool_call = {
        "messages": [
            HumanMessage(content="What is the font size for a 12x8 cm pouch?"),
            AIMessage(
                content="",
                tool_calls=[{
                    "id": "call_1",
                    "name": "min_font_size_checker",
                    "args": {"panel_length_cm": 12, "panel_width_cm": 8},
                }],
            ),
        ]
    }
    print("should_continue (tool call):", should_continue(state_with_tool_call))

    # Simulate: LLM returned a final answer
    state_final = {
        "messages": [
            HumanMessage(content="What is the font size for a 12x8 cm pouch?"),
            AIMessage(content="The minimum font size is 1.5 mm per Regulation 6.1."),
        ]
    }
    print("should_continue (final):", should_continue(state_final))
    print("format_final_answer:", format_final_answer(state_final))
