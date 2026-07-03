# Existing ERP MCP Baseline

Source project: `E:\ERPCode\erp-mcp`

## Verified Query

Question:

```text
物料编码 W1 在 RSERPTR 里现在数量是多少？
```

Result from existing MCP scripts:

```text
KCHZ_WLID = W1
TOTAL_KCSL = 138
TOTAL_FKCSL = 0
TOTAL_FPSL = 0
ROW_COUNT = 3
```

Details:

```text
CKID  KCSL
0010  123
0017  0
YS    15
```

## ERP Field Naming Rule

DMG metadata stores logical field names such as `WLID` and `KCSL`.

RSERP physical table columns follow the fixed rule:

```text
physical column = table_name + "_" + logical_field_name
```

For `KCHZ`:

```text
WLID -> KCHZ_WLID
KCSL -> KCHZ_KCSL
FKCSL -> KCHZ_FKCSL
FPSL -> KCHZ_FPSL
```

This is normal RSERP behavior, not a schema mismatch.

Special temporary tables or views such as `V_BOM_WLID` may not be in DMG and should be handled outside the normal DMG-driven path.
