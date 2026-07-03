from __future__ import annotations


def normalize_identifier(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise ValueError(f"{name} cannot be blank")
    return normalized


def physical_column(table_name: str, logical_field_name: str) -> str:
    table = normalize_identifier(table_name, "table_name")
    field = normalize_identifier(logical_field_name, "logical_field_name")
    return f"{table}_{field}"
