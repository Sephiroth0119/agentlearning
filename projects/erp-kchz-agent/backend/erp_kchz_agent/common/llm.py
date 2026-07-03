from __future__ import annotations

from dataclasses import dataclass
import os

from erp_kchz_agent.common.config import load_dotenv


@dataclass(frozen=True)
class LlmSettings:
    api_key: str
    base_url: str
    model: str


def get_llm_settings() -> LlmSettings:
    load_dotenv()
    return LlmSettings(
        api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "",
        base_url=os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "",
        model=os.getenv("LLM_MODEL") or "dp-v4-pro",
    )


def build_openai_client_kwargs(settings: LlmSettings) -> dict[str, str]:
    kwargs = {"api_key": settings.api_key}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    return kwargs


def create_openai_client(settings: LlmSettings | None = None):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai is not installed. Run: pip install -r backend/requirements.txt") from exc

    current = settings or get_llm_settings()
    if not current.api_key:
        raise RuntimeError("Missing LLM_API_KEY or OPENAI_API_KEY")
    return OpenAI(**build_openai_client_kwargs(current))
