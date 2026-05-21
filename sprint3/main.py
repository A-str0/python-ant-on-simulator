from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from antsim.colony import Colony
from antsim.main import SAVE_DIR, main
from antsim.storage import (
    list_saves as _list_saves,
    load_colony as _load_colony,
    save_colony as _save_colony,
)


def save_colony(colony: Colony):
    return _save_colony(colony, SAVE_DIR)


def list_saves():
    return _list_saves(SAVE_DIR)


def load_colony(filename: str):
    return _load_colony(filename, SAVE_DIR)


if __name__ == "__main__":
    main()
