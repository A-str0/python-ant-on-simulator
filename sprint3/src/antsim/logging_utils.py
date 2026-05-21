from __future__ import annotations

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "antsim.log"


def get_log_path() -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    return LOG_FILE


def write_log(message: str, category: str = "runtime") -> None:
    path = get_log_path()
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} [{category}] {message}\n"
    with path.open("a", encoding="utf-8") as log_file:
        log_file.write(line)


def tail_log(limit: int = 40) -> list[str]:
    path = get_log_path()
    if not path.exists():
        return []
    limit = int(limit)
    if limit <= 0:
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]
