from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InventoryLine:
    warehouse_id: str
    location_id: str
    batch_no: str
    quantity: float
    assist_quantity: float = 0
    allocated_quantity: float = 0


@dataclass(frozen=True)
class InventoryResult:
    material_id: str
    total_quantity: float
    total_assist_quantity: float
    total_allocated_quantity: float
    lines: list[InventoryLine] = field(default_factory=list)
