import json
from pathlib import Path

from .colony import Colony
from .logging_utils import write_log


def ensure_save_dir(save_dir: Path) -> Path:
    save_dir.mkdir(exist_ok=True)
    return save_dir


def save_colony(colony: Colony, save_dir: Path) -> Path:
    target_dir = ensure_save_dir(save_dir)
    path = target_dir / f"{colony.id}.json"
    path.write_text(
        json.dumps(colony.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_log(f"saved colony {colony.id} to {path}", category="storage")
    return path


def list_saves(save_dir: Path) -> list[Path]:
    target_dir = ensure_save_dir(save_dir)
    return sorted(target_dir.glob("*.json"))


def load_colony(filename: str, save_dir: Path) -> Colony:
    target_dir = ensure_save_dir(save_dir)
    path = target_dir / filename
    if not path.exists() and not filename.endswith(".json"):
        path = target_dir / f"{filename}.json"
    if not path.exists():
        raise FileNotFoundError(filename)

    data = json.loads(path.read_text(encoding="utf-8"))
    colony = Colony.from_dict(data)
    write_log(f"loaded colony {colony.id} from {path}", category="storage")
    return colony
