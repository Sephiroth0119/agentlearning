from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_ROOT / ".env"


def load_dotenv(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.lstrip("\ufeff").split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class DmgSettings:
    server: str
    port: int
    database: str
    user: str
    password: str


@dataclass(frozen=True)
class OracleSettings:
    dsn: str
    schema: str
    user: str
    password: str
    instant_client_dir: str | None = None


@dataclass(frozen=True)
class Settings:
    dmg: DmgSettings
    oracle: OracleSettings


def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        dmg=DmgSettings(
            server=require_env("DMG_SERVER"),
            port=int(require_env("DMG_PORT")),
            database=require_env("DMG_DATABASE"),
            user=require_env("DMG_USER"),
            password=require_env("DMG_PASSWORD"),
        ),
        oracle=OracleSettings(
            dsn=require_env("ORACLE_DSN"),
            schema=require_env("ORACLE_SCHEMA"),
            user=require_env("ORACLE_USER"),
            password=require_env("ORACLE_PASSWORD"),
            instant_client_dir=os.getenv("ORACLE_INSTANT_CLIENT_DIR") or None,
        ),
    )
