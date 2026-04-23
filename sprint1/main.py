from pathlib import Path
from ants import Ant, Harvester
from colony import Colony
from storage import (
    list_saves as _list_saves,
    load_colony as _load_colony,
    save_colony as _save_colony,
)


SAVE_DIR = Path("saves")
SAVE_DIR.mkdir(exist_ok=True)


def save_colony(colony: Colony):
    return _save_colony(colony, SAVE_DIR)


def list_saves():
    return _list_saves(SAVE_DIR)


def load_colony(filename: str):
    return _load_colony(filename, SAVE_DIR)


if __name__ == "__main__":
    colony = Colony("colony_1", 5, 100)

    colony.tick()
    colony.tick()

    save_colony(colony)

    loaded = load_colony("colony_1")
    print("id:", loaded.id)
    print("food:", loaded.food)
    print("time:", loaded.time)
    print("ants:", len(loaded.ants))
