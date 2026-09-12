"""
Wires extract -> retrieve -> draft -> notify into a single LangGraph
state machine. This is optional plumbing — scripts/run_pipeline.py calls
the three functions directly for quick testing — but this is what you
point to in the write-up and interview when you talk about "the agent",
and it's the piece that's easy to extend later (e.g. add a
"needs_more_info" branch that loops back and asks a clarifying question
instead of drafting on thin data).
"""
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from app.extraction import extract_call_data
from app.retrieval import retrieve_best_proposal
from app.drafting import draft_proposal
from app.telegram_bot import send_approval_card


class PipelineState(TypedDict):
    call_id: str
    transcript: str
    extraction: Optional[dict]
    matched_proposal: Optional[dict]
    draft: Optional[dict]
    status: Optional[str]


def node_extract(state: PipelineState) -> dict:
    return {"extraction": extract_call_data(state["transcript"])}


def node_retrieve(state: PipelineState) -> dict:
    return {"matched_proposal": retrieve_best_proposal(state["extraction"])}


def node_draft(state: PipelineState) -> dict:
    return {"draft": draft_proposal(state["extraction"], state["matched_proposal"])}


def node_notify(state: PipelineState) -> dict:
    send_approval_card(state["call_id"], state["draft"])
    return {"status": "awaiting_approval"}


def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("extract", node_extract)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("generate_draft", node_draft)
    graph.add_node("notify", node_notify)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "retrieve")
    graph.add_edge("retrieve", "generate_draft")
    graph.add_edge("generate_draft", "notify")
    graph.add_edge("notify", END)

    return graph.compile()


pipeline = build_graph()