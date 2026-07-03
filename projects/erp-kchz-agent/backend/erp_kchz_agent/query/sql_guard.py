from __future__ import annotations

import re


class QueryRejected(ValueError):
    """Raised when SQL violates the readonly boundary."""


_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|TRUNCATE|DROP|ALTER|CREATE|GRANT|REVOKE|EXEC|EXECUTE|CALL|COMMIT|ROLLBACK|SAVEPOINT|LOCK)\b",
    re.IGNORECASE,
)
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"--[^\n]*")


def _strip_comments(sql: str) -> str:
    return _LINE_COMMENT.sub(" ", _BLOCK_COMMENT.sub(" ", sql))


def ensure_readonly_select(sql: str) -> str:
    if not sql or not sql.strip():
        raise QueryRejected("SQL cannot be blank")

    clean = _strip_comments(sql).strip().rstrip(";").strip()
    if not clean:
        raise QueryRejected("SQL cannot be blank after removing comments")
    if ";" in clean:
        raise QueryRejected("multiple SQL statements are not allowed")

    upper = clean.lstrip().upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise QueryRejected("only SELECT or WITH queries are allowed")

    match = _FORBIDDEN.search(clean)
    if match:
        raise QueryRejected(f"forbidden SQL keyword: {match.group(0).upper()}")

    return clean
