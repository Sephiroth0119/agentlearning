from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TableField:
    logical_name: str
    physical_name: str
    comment: str
    sql_type: str
    primary_key: bool = False
    nullable: bool = True


@dataclass(frozen=True)
class TableSchema:
    table_name: str
    title: str
    fields: list[TableField]
