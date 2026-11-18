"""
Day 9 — LangGraph agent graph for HealthLabelCheck
Wires the LLM + tools into a ReAct-style graph with:
  - MemorySaver checkpointing (conversation memory across turns)
  - interrupt_before=["tools"] for human-in-the-loop approval
  - POST /agent FastAPI endpoint

Graph structure:
    START → llm_node → (should_continue) → tools_node → llm_node → …
                                         ↘ END

Usage (standalone):
    python -m app.graph

Usage (via FastAPI):
    POST /agent  {"question": "...", "thread_id": "user-1", "approve": true}
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

from app.tools import TOOLS
from app.agent_loop import should_continue, format_final_answer

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are HealthLabelCheck AI, an expert on FSSAI food labelling regulations "
    "for small food business owners in India. "
    "You have four tools:\n"
    "  • min_font_size_checker  — calculate minimum font size from panel dimensions\n"
    "  • search_regulations     — semantic search over 14 FSSAI regulations\n"
    "  • get_mandatory_checklist_tool — full list of mandatory label items\n"
    "  • get_regulation_by_id  — fetch a specific regulation by number\n\n"
    "Rules:\n"
    "1. Always cite regulation numbers in your final answer.\n"
    "2. Use tools to look up regulations; do not guess.\n"
    "3. For font-size questions with dimensions given, always call min_font_size_checker.\n"
    "4. If the question is outside FSSAI labelling scope, say 'I don't know' and explain why.\n"
    "5. Keep answers concise and practical for a small business owner."
)


# ── Build the LLM (with tools bound) ─────────────────────────────────────────

def _build_llm():
    """Return a Groq ChatModel with tools bound, or raise if key missing."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_key_here_replace_this":
        raise EnvironmentError(
            "GROQ_API_KEY not set. Add it to .env to run the LangGraph agent."
        )
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        temperature=float(os.getenv("LLM_TEMPERATURE", 0.3)),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", 500)),
        api_key=api_key,
    )
    return llm.bind_tools(TOOLS)


# ── Graph nodes ───────────────────────────────────────────────────────────────

def llm_node(state: MessagesState) -> dict:
    """Call the LLM with the current message history."""
    llm_with_tools = _build_llm()
    messages = state["messages"]
    # Prepend system prompt if first turn
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(TOOLS)


# ── Graph assembly ────────────────────────────────────────────────────────────

def build_graph(interrupt_before_tools: bool = True):
    """
    Build and compile the HealthLabelCheck agent graph.

    Args:
        interrupt_before_tools: When True the graph pauses before executing
            tools so the caller can inspect and approve the tool call.
            Set to False for fully automated use.

    Returns:
        A compiled LangGraph app with MemorySaver checkpointing.
    """
    builder = StateGraph(MessagesState)
    builder.add_node("llm",   llm_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", should_continue, {"tools": "tools", "__end__": END})
    builder.add_edge("tools", "llm")

    memory = MemorySaver()

    if interrupt_before_tools:
        return builder.compile(checkpointer=memory, interrupt_before=["tools"])
    return builder.compile(checkpointer=memory)


# ── Convenience runner ────────────────────────────────────────────────────────

def run_agent(
    question: str,
    thread_id: str = "default",
    approve: bool = True,
    interrupt_before_tools: bool = True,
) -> dict:
    """
    Run the agent for one user question.

    Args:
        question:               The user's question string.
        thread_id:              Conversation thread ID (enables memory).
        approve:                If interrupt_before_tools=True, set approve=True
                                to automatically continue past the tool call,
                                or False to return the pending state for review.
        interrupt_before_tools: Whether to pause before tool execution.

    Returns:
        dict with keys:
            answer       : str  — final answer text
            tool_calls   : list — tool calls made (names + args)
            interrupted  : bool — True if paused awaiting approval
            thread_id    : str
    """
    graph = build_graph(interrupt_before_tools=interrupt_before_tools)
    config = {"configurable": {"thread_id": thread_id}}

    input_messages = {"messages": [HumanMessage(content=question)]}

    # First invocation
    state = graph.invoke(input_messages, config=config)

    tool_calls_made = []
    interrupted = False

    # Check if interrupted at tool node
    if interrupt_before_tools:
        snapshot = graph.get_state(config)
        next_nodes = list(snapshot.next)
        if "tools" in next_nodes:
            # Collect pending tool calls for the response
            last_ai = state["messages"][-1]
            if hasattr(last_ai, "tool_calls"):
                tool_calls_made = [
                    {"name": tc["name"], "args": tc["args"]}
                    for tc in last_ai.tool_calls
                ]

            if approve:
                # Resume — pass None to continue from checkpoint
                state = graph.invoke(None, config=config)
            else:
                interrupted = True
                return {
                    "answer": "Paused — awaiting approval to call tools.",
                    "tool_calls": tool_calls_made,
                    "interrupted": True,
                    "thread_id": thread_id,
                }

    # Collect all tool calls from full history
    if not tool_calls_made:
        for msg in state.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls_made.append({"name": tc["name"], "args": tc["args"]})

    return {
        "answer":      format_final_answer(state),
        "tool_calls":  tool_calls_made,
        "interrupted": interrupted,
        "thread_id":   thread_id,
    }


# ── FastAPI endpoint (registered in main.py) ─────────────────────────────────

class AgentRequest:
    """Pydantic model imported by main.py for POST /agent."""
    pass  # defined inline in main.py to avoid circular import


# ── Standalone demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    test_questions = [
        "My chakli pouch is 12 cm by 8 cm. What is the minimum font size?",
        "What must I print on my laddoo packet?",
        "My laddoos contain groundnuts — what allergen declaration do I need?",
        "What is the cheapest printer in Kopargaon?",   # out-of-scope
    ]

    print("=" * 60)
    print("HealthLabelCheck — LangGraph Agent Demo")
    print("=" * 60)

    for q in test_questions:
        print(f"\nQ: {q}")
        try:
            result = run_agent(q, thread_id="demo", approve=True)
            print(f"Tools used : {[t['name'] for t in result['tool_calls']]}")
            print(f"Answer     : {result['answer'][:300]}")
        except EnvironmentError as e:
            print(f"[No API key] {e}")
            print("Skipping live LLM call — tools module still works without a key.")
            break
