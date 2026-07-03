from __future__ import annotations

def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("fastapi is not installed. Run: pip install -r backend/requirements.txt") from exc

    from erp_kchz_agent.app.api import register_routes

    app = FastAPI(title="ERP KCHZ Agent", version="0.1.0")
    register_routes(app)
    return app


app = create_app()
