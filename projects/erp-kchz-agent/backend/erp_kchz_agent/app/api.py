from __future__ import annotations

from typing import Any


def register_routes(app) -> None:
    try:
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("pydantic is not installed. Run: pip install -r backend/requirements.txt") from exc

    class ChatRequest(BaseModel):
        question: str

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/chat")
    def chat(request: ChatRequest) -> dict[str, Any]:
        return {
            "answer": "后端骨架已就绪，库存 LangGraph 查询链路下一步接入。",
            "question": request.question,
        }
