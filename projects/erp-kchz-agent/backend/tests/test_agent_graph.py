from erp_kchz_agent.agent.graph import extract_material_id


def test_extract_material_id_next_to_chinese_text():
    assert extract_material_id("物料编码W1现在多少") == "W1"
