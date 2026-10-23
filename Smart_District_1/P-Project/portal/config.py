"""Configuration from .env (Day 10: venv, .env, python-dotenv)."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.environ.get("PORTAL_ENV_FILE", ROOT / ".env"))


def _load_env(path: Path) -> None:
    """Use python-dotenv if installed, otherwise a tiny fallback parser."""
    try:
        from dotenv import load_dotenv
        load_dotenv(path)
        return
    except ImportError:
        pass
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    report_dir: Path
    log_file: Path
    expected_files: tuple
    fine_per_day: float
    admin_token: str
    log_level: str


def load_settings() -> Settings:
    _load_env(ENV_FILE)
    get = os.environ.get
    return Settings(
        data_dir=ROOT / get("DATA_DIR", "data"),
        report_dir=ROOT / get("REPORT_DIR", "reports"),
        log_file=ROOT / get("LOG_FILE", "logs/portal.log"),
        expected_files=tuple(f.strip() for f in get("EXPECTED_FILES", "").split(",") if f.strip()),
        fine_per_day=float(get("FINE_PER_DAY", "50")),
        admin_token=get("ADMIN_TOKEN", ""),
        log_level=get("LOG_LEVEL", "INFO").upper(),
    )
