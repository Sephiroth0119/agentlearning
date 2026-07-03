from __future__ import annotations

from erp_kchz_agent.common.config import DmgSettings, OracleSettings

_oracle_client_inited = False


def connect_dmg(settings: DmgSettings):
    try:
        import pyodbc
    except ImportError:
        pyodbc = None

    if pyodbc:
        for driver in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server", "SQL Server"):
            try:
                connection_string = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={settings.server},{settings.port};"
                    f"DATABASE={settings.database};"
                    f"UID={settings.user};"
                    f"PWD={settings.password};"
                    "TrustServerCertificate=yes;"
                )
                return pyodbc.connect(connection_string, timeout=5)
            except Exception:
                continue

    try:
        import pymssql
    except ImportError as exc:
        raise RuntimeError("Install pyodbc or pymssql. Run: pip install -r backend/requirements.txt") from exc

    return pymssql.connect(
        server=settings.server,
        port=settings.port,
        database=settings.database,
        user=settings.user,
        password=settings.password,
        timeout=5,
        login_timeout=5,
    )


def init_oracle_client(settings: OracleSettings) -> None:
    global _oracle_client_inited
    if _oracle_client_inited:
        return

    try:
        import oracledb
    except ImportError as exc:
        raise RuntimeError("oracledb is not installed. Run: pip install -r backend/requirements.txt") from exc

    try:
        if settings.instant_client_dir:
            oracledb.init_oracle_client(lib_dir=settings.instant_client_dir)
        else:
            oracledb.init_oracle_client()
    except Exception as exc:
        message = str(exc)
        if "already" not in message.lower():
            raise

    _oracle_client_inited = True


def connect_oracle(settings: OracleSettings):
    try:
        import oracledb
    except ImportError as exc:
        raise RuntimeError("oracledb is not installed. Run: pip install -r backend/requirements.txt") from exc

    init_oracle_client(settings)
    return oracledb.connect(user=settings.user, password=settings.password, dsn=settings.dsn)
