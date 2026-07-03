from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from erp_kchz_agent.config import get_settings
from erp_kchz_agent.db_clients import connect_dmg, connect_oracle


def check_dmg() -> None:
    settings = get_settings().dmg
    with connect_dmg(settings) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
    print("DMG SQL Server connection: OK")


def check_oracle() -> None:
    settings = get_settings().oracle
    with connect_oracle(settings) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM dual")
        cursor.fetchone()
    print("Oracle RSERP connection: OK")


def main() -> None:
    check_dmg()
    check_oracle()


if __name__ == "__main__":
    main()
