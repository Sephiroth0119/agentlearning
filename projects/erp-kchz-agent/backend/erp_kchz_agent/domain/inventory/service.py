from __future__ import annotations

from erp_kchz_agent.domain.inventory.models import InventoryLine, InventoryResult
from erp_kchz_agent.metadata.field_naming import physical_column
from erp_kchz_agent.query.oracle_client import OracleReadonlyClient


class InventoryService:
    def __init__(self, oracle_client: OracleReadonlyClient):
        self.oracle_client = oracle_client

    def get_material_inventory(self, material_id: str) -> InventoryResult:
        table = "KCHZ"
        c_ckid = physical_column(table, "CKID")
        c_wlid = physical_column(table, "WLID")
        c_kwid = physical_column(table, "KWID")
        c_wlph = physical_column(table, "WLPH")
        c_kcsl = physical_column(table, "KCSL")
        c_fkcsl = physical_column(table, "FKCSL")
        c_fpsl = physical_column(table, "FPSL")

        sql = f"""
SELECT {c_ckid}, {c_kwid}, {c_wlph}, {c_kcsl}, {c_fkcsl}, {c_fpsl}
FROM {table}
WHERE {c_wlid} = :material_id
ORDER BY {c_ckid}, {c_kwid}, {c_wlph}
"""
        result = self.oracle_client.query(sql, {"material_id": material_id}, limit=500)

        lines: list[InventoryLine] = []
        total_quantity = 0.0
        total_assist_quantity = 0.0
        total_allocated_quantity = 0.0
        for row in result.rows:
            quantity = float(row.get(c_kcsl) or 0)
            assist_quantity = float(row.get(c_fkcsl) or 0)
            allocated_quantity = float(row.get(c_fpsl) or 0)
            total_quantity += quantity
            total_assist_quantity += assist_quantity
            total_allocated_quantity += allocated_quantity
            lines.append(
                InventoryLine(
                    warehouse_id=str(row.get(c_ckid) or ""),
                    location_id=str(row.get(c_kwid) or ""),
                    batch_no=str(row.get(c_wlph) or ""),
                    quantity=quantity,
                    assist_quantity=assist_quantity,
                    allocated_quantity=allocated_quantity,
                )
            )

        return InventoryResult(
            material_id=material_id,
            total_quantity=total_quantity,
            total_assist_quantity=total_assist_quantity,
            total_allocated_quantity=total_allocated_quantity,
            lines=lines,
        )
