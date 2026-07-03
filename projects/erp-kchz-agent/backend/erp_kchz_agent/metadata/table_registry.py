from __future__ import annotations

from erp_kchz_agent.metadata.field_naming import physical_column
from erp_kchz_agent.metadata.schema_models import TableField, TableSchema


def kchz_schema() -> TableSchema:
    table = "KCHZ"
    return TableSchema(
        table_name=table,
        title="库存汇总",
        fields=[
            TableField("CKID", physical_column(table, "CKID"), "仓库编码", "VARCHAR2", primary_key=True, nullable=False),
            TableField("WLID", physical_column(table, "WLID"), "物料编码", "VARCHAR2", primary_key=True, nullable=False),
            TableField("KWID", physical_column(table, "KWID"), "库位编码", "VARCHAR2", primary_key=True, nullable=False),
            TableField("WLPH", physical_column(table, "WLPH"), "物料批号", "VARCHAR2", primary_key=True, nullable=False),
            TableField("KCSL", physical_column(table, "KCSL"), "库存数量", "FLOAT"),
            TableField("FKCSL", physical_column(table, "FKCSL"), "辅助库存数量", "FLOAT"),
            TableField("FPSL", physical_column(table, "FPSL"), "分配数量", "FLOAT"),
        ],
    )
