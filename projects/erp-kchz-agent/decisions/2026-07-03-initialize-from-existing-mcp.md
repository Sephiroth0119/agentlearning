# Initialize From Existing ERP MCP

## Decision

Start this project by wrapping the existing `E:\ERPCode\erp-mcp` behavior into a cleaner project shape before adding frontend or new agent orchestration.

## Why

The old MCP already proves the important path:

```text
natural language
  -> describe KCHZ through DMG metadata
  -> generate readonly Oracle SQL
  -> query KCHZ
  -> answer in Chinese
```

But it is still a small MCP proof, not a maintainable project boundary. The new project should first preserve this working path, then gradually split responsibilities.

## Initial Shape

```text
backend/
  config.py          Load local database config
  db_clients.py      Low-level SQL Server and Oracle clients
  metadata/          DMG table/procedure metadata lookup
  inventory/         KCHZ-specific query use cases
  agent/             Natural-language routing later

frontend/
  placeholder only
```

Do not depend on `erpservice?action=table_AI` for this project. That is a small feature from another context and is not an applicable foundation here.

For now, this project should use:

- direct readonly Oracle access for local/backend development
- the existing `E:\ERPCode\erp-mcp` MCP behavior as a proven reference path
- FastAPI only as this project's own service boundary, if/when an HTTP API is needed

## First Real Slice

Do not build a broad ERP agent first.

Build one vertical slice:

```text
问：物料编码 W1 现在数量是多少？
答：查 KCHZ，按仓库明细返回库存数量，并给总数。
```

This slice needs:

- `describe_table("KCHZ")`
- field mapping by RSERP convention: `KCHZ` + `WLID` -> `KCHZ_WLID`
- readonly Oracle query
- Chinese answer formatting
- a regression example using `W1`, expected total `138`
