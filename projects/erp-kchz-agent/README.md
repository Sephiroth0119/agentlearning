# ERP KCHZ Agent Development

This directory records notes, decisions, experiments, and progress for ERP KCHZ agent development.

## Layout

```text
backend/      Python backend skeleton and DB connection checks
frontend/     Placeholder only for now
notes/        Rough working notes
decisions/    Durable design and scope decisions
experiments/  Runnable probes and mock-data experiments
```

Backend package layout:

```text
backend/erp_kchz_agent/
  app/                 FastAPI boundary
  agent/               LangGraph workflow boundary
  common/              Config and LLM helpers
  metadata/            DMG schema models and RSERP field naming
  query/               Readonly SQL guard and Oracle query client
  domain/inventory/    KCHZ inventory business logic
```

## Local Config

Copy `.env.example` to `.env` and fill local database credentials. `.env` is ignored by git.

```powershell
cd projects/erp-kchz-agent
Copy-Item .env.example .env
```

Install backend dependencies when you are ready to verify database connections:

```powershell
cd backend
pip install -r requirements.txt
python scripts/check_connections.py
```

Oracle 11g needs `python-oracledb` thick mode, so set `ORACLE_INSTANT_CLIENT_DIR` if the Instant Client directory is not already on `PATH`.

LLM config is OpenAI-compatible. If your environment already has DP v4 pro configured, map it to:

```powershell
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=dp-v4-pro
```

Run local unit tests without extra test dependencies:

```powershell
cd backend
python scripts/run_unit_tests.py
```

Run the API after dependencies are installed:

```powershell
cd backend
uvicorn erp_kchz_agent.app.main:app --reload
```

## Log

- 2026-07-03: Verified existing `E:\ERPCode\erp-mcp` can answer W1 KCHZ inventory. Current total `KCSL` is `138`.
- 2026-07-03: Created this workspace.
