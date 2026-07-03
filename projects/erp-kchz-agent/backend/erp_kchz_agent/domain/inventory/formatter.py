from __future__ import annotations

from erp_kchz_agent.domain.inventory.models import InventoryResult


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def format_inventory_answer(result: InventoryResult) -> str:
    lines = [
        f"物料 {result.material_id} 当前库存总数是 {_format_number(result.total_quantity)}。",
        f"辅助库存总数 {_format_number(result.total_assist_quantity)}，分配数量 {_format_number(result.total_allocated_quantity)}。",
    ]

    if result.lines:
        lines.append("明细：")
        for line in result.lines:
            location = line.location_id.strip() or "-"
            batch = line.batch_no.strip() or "-"
            lines.append(
                f"- 仓库 {line.warehouse_id.strip() or '-'}，库位 {location}，批号 {batch}："
                f"{_format_number(line.quantity)}"
            )
    return "\n".join(lines)
