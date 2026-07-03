from erp_kchz_agent.metadata.field_naming import physical_column


def test_physical_column_prefixes_table_name():
    assert physical_column("KCHZ", "WLID") == "KCHZ_WLID"
    assert physical_column("kchz", "kcsl") == "KCHZ_KCSL"


def test_physical_column_rejects_blank_values():
    try:
        physical_column("", "WLID")
    except ValueError as exc:
        assert "table_name" in str(exc)
    else:
        raise AssertionError("expected blank table_name to fail")
