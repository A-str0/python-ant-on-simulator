from __future__ import annotations

from pathlib import Path

from .ants import ANT_TYPES_REGISTRY
from .colony import Colony
from .storage import list_saves, load_colony, save_colony
from .tui import choose_ant_type, launch_tui, render_dashboard


SAVE_DIR = Path("saves")
SAVE_DIR.mkdir(exist_ok=True)


def create_colony_interactive() -> Colony | None:
    print("\nДоступные виды муравьев:")
    ant_type = choose_ant_type()
    try:
        ant_count = int(input("Начальная численность муравьев: "))
        food = int(input("Начальный запас еды: "))
    except ValueError:
        print("Ошибка ввода")
        return None
    colony_id = input("Название колонии: ") or f"colony_{ant_type}_{ant_count}"
    colony = Colony(colony_id, ant_count, food, ant_type)
    save_colony(colony, SAVE_DIR)
    return colony


def load_colony_interactive() -> Colony | None:
    saves = list_saves(SAVE_DIR)
    if not saves:
        print("Нет сохранений")
        return None
    for i, path in enumerate(saves, start=1):
        print(f"{i}. {path.stem}")
    try:
        index = int(input("Сохранение: ")) - 1
    except ValueError:
        return None
    if index < 0 or index >= len(saves):
        return None
    return load_colony(saves[index].stem, SAVE_DIR)


def quick_demo() -> None:
    colony = Colony("demo_sprint3", 30, 2000, "Harvester", seed=42)
    room_ids = ["surface", "food_storage", "billiard_room", "server_room", "gym_seed"]
    colony.rooms["server_room"].enabled = True
    for index, _ant in enumerate(colony.ants[:20]):
        colony.assign_ant_to_room(index, room_ids[index % len(room_ids)])
    for _ in range(12):
        colony.tick()
    print(render_dashboard(colony))


def main() -> None:
    while True:
        print("\n=== СИМУЛЯТОР МУРАВЬИНОЙ ФЕРМЫ / SPRINT 3 ===")
        print("1. Создать новую колонию и открыть TUI")
        print("2. Загрузить колонию и открыть TUI")
        print("3. Список сохранений")
        print("4. Quick demo без интерактива")
        print("5. Виды муравьев")
        print("6. Выход")
        command = input("> ").strip()
        if command == "1":
            colony = create_colony_interactive()
            if colony:
                launch_tui(colony, SAVE_DIR)
        elif command == "2":
            colony = load_colony_interactive()
            if colony:
                launch_tui(colony, SAVE_DIR)
        elif command == "3":
            for path in list_saves(SAVE_DIR):
                print(path.stem)
        elif command == "4":
            quick_demo()
        elif command == "5":
            for ant_type, cls in ANT_TYPES_REGISTRY.items():
                print(f"{ant_type}: {cls().name}")
        elif command == "6":
            break


if __name__ == "__main__":
    main()
