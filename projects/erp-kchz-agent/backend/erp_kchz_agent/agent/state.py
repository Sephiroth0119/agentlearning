from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    material_id: str
    answer: str
    rows: list[dict[str, Any]]
