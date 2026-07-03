from erp_kchz_agent.domain.inventory.formatter import format_inventory_answer
from erp_kchz_agent.domain.inventory.models import InventoryLine, InventoryResult


def test_formats_inventory_total_and_details():
    result = InventoryResult(
        material_id="W1",
        total_quantity=138,
        total_assist_quantity=0,
        total_allocated_quantity=0,
        lines=[
            InventoryLine(warehouse_id="0010", location_id="", batch_no="", quantity=123),
            InventoryLine(warehouse_id="0017", location_id="", batch_no="", quantity=0),
            InventoryLine(warehouse_id="YS", location_id="", batch_no="", quantity=15),
        ],
    )

    answer = format_inventory_answer(result)

    assert "W1" in answer
    assert "138" in answer
    assert "0010" in answer
    assert "123" in answer
    assert "YS" in answer
