from erp_kchz_agent.query.sql_guard import QueryRejected, ensure_readonly_select


def test_accepts_select_and_removes_trailing_semicolon():
    sql = ensure_readonly_select(" SELECT * FROM KCHZ WHERE KCHZ_WLID = :wlid; ")
    assert sql == "SELECT * FROM KCHZ WHERE KCHZ_WLID = :wlid"


def test_rejects_update():
    try:
        ensure_readonly_select("UPDATE KCHZ SET KCHZ_KCSL = 0")
    except QueryRejected as exc:
        assert "SELECT" in str(exc) or "forbidden" in str(exc)
    else:
        raise AssertionError("expected UPDATE to fail")


def test_rejects_multiple_statements():
    try:
        ensure_readonly_select("SELECT * FROM KCHZ; SELECT * FROM WLXX")
    except QueryRejected as exc:
        assert "multiple" in str(exc)
    else:
        raise AssertionError("expected multiple statements to fail")
