from __future__ import annotations

from typing import Any

from erp_kchz_agent.common.config import OracleSettings
from erp_kchz_agent.db_clients import connect_oracle
from erp_kchz_agent.query.result_models import QueryResult
from erp_kchz_agent.query.sql_guard import ensure_readonly_select


def _coerce(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ", timespec="seconds")
    if hasattr(value, "read") and callable(value.read):
        try:
            return value.read()
        except Exception:
            return str(value)
    return value


class OracleReadonlyClient:
    def __init__(self, settings: OracleSettings):
        self.settings = settings

    def query(self, sql: str, params: dict[str, Any] | None = None, limit: int = 200) -> QueryResult:
        clean_sql = ensure_readonly_select(sql)
        safe_limit = min(max(int(limit or 200), 1), 1000)

        with connect_oracle(self.settings) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(clean_sql, params or {})
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows: list[dict[str, Any]] = []
                truncated = False
                for index, row in enumerate(cursor):
                    if index >= safe_limit:
                        truncated = True
                        break
                    rows.append({column: _coerce(value) for column, value in zip(columns, row)})
                return QueryResult(columns=columns, rows=rows, row_count=len(rows), truncated=truncated)
            finally:
                cursor.close()
