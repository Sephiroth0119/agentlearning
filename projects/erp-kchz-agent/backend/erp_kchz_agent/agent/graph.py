from __future__ import annotations

import re

from erp_kchz_agent.agent.state import AgentState


def extract_material_id(question: str) -> str | None:
    match = re.search(r"物料(?:编码)?\s*([A-Za-z][A-Za-z0-9_]*)", question)
    if match:
        return match.group(1).upper()
    match = re.search(r"([A-Za-z][A-Za-z0-9_]*)", question)
    return match.group(1).upper() if match else None


def build_graph():
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise RuntimeError("langgraph is not installed. Run: pip install -r backend/requirements.txt") from exc

    def parse_question(state: AgentState) -> AgentState:
        material_id = extract_material_id(state.get("question", ""))
        return {**state, "material_id": material_id or ""}

    workflow = StateGraph(AgentState)
    workflow.add_node("parse_question", parse_question)
    workflow.set_entry_point("parse_question")
    workflow.add_edge("parse_question", END)
    return workflow.compile()
