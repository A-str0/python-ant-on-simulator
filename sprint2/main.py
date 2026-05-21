from pathlib import Path

from ants import ANT_TYPES_REGISTRY
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


def _show_colony(colony: Colony) -> None:
    alive = colony.get_alive_ants()
    print(f"\n=== Колония: {colony.id} ===")
    print(f"Вид: {colony.ant_type}")
    print(f"Время: {colony.time} ев")
    print(f"Еда: {colony.food} еп")
    print(f"Муравьи: {len(alive)} живых / {len(colony.ants)} всего")
    print(f"Активных событий: {len(colony.active_events)}")
    if colony.last_voting:
        v = colony.last_voting
        print(f"Последнее голосование: {v.issue}")
        print(f"  За: {v.for_count}, Против: {v.against_count}, Воздержались: {v.abstain_count}, Потерялись: {v.lost_count}")
        if v.queen_overridden:
            print("  (матка уточнила результаты)")
    print()

    print("Комнаты:")
    for room_id, room in colony.rooms.items():
        assigned = len(room.ant_ids)
        print(f"  [{room_id}] {room.name} ({assigned}/{room.capacity})")

    if alive:
        print("\nМуравьи (первые 10):")
        for i, ant in enumerate(alive[:10]):
            status_str = ", ".join(ant.statuses) if ant.statuses else "ok"
            room_str = ant.current_room or "none"
            stats_str = " ".join(f"{k}={v}" for k, v in ant.stats.items())
            print(f"  #{i}: age={ant.age} room={room_str} [{status_str}] {stats_str}")


def _create_colony() -> None:
    print("\nДоступные виды муравьев:")
    types_list = list(ANT_TYPES_REGISTRY.keys())
    for i, t in enumerate(types_list):
        ant = ANT_TYPES_REGISTRY[t]()
        print(f"  {i + 1}. {ant.name} ({t})")

    try:
        type_choice = int(input("\nВыберите вид (номер): ")) - 1
        if type_choice < 0 or type_choice >= len(types_list):
            print("Неверный выбор")
            return
        ant_type = types_list[type_choice]

        ant_count = int(input("Начальная численность муравьев: "))
        if ant_count < 0:
            print("Численность не может быть отрицательной")
            return

        food = int(input("Начальный запас пищи: "))
        if food < 0:
            print("Запас пищи не может быть отрицательным")
            return

        colony_id = input("Название колонии: ") or f"colony_{hash(str([ant_type, ant_count, food])) & 0xFFFFFFFF}"
    except ValueError:
        print("Ошибка ввода")
        return

    colony = Colony(
        colony_id=colony_id,
        ant_count=ant_count,
        food=food,
        ant_type=ant_type,
    )
    save_colony(colony)
    print(f"\nКолония '{colony_id}' создана и сохранена!")
    _show_colony(colony)


def _load_and_run() -> None:
    saves = list_saves()
    if not saves:
        print("Нет сохранений")
        return

    print("\nСохранения:")
    for i, path in enumerate(saves):
        print(f"  {i + 1}. {path.stem}")

    try:
        choice = int(input("\nВыберите сохранение (номер): ")) - 1
        if choice < 0 or choice >= len(saves):
            print("Неверный выбор")
            return
        colony = load_colony(saves[choice].stem)
    except (ValueError, FileNotFoundError):
        print("Ошибка загрузки")
        return

    print(f"\nЗагружена колония: {colony.id}")
    while True:
        _show_colony(colony)
        print("\nКоманды:")
        print("  1. Шаг симуляции (1 ев)")
        print("  2. Шагов симуляции (N ев)")
        print("  3. Назначить муравья в комнату")
        print("  4. Сохранить и выйти")
        print("  5. Голосование")
        print("  6. Выйти без сохранения")

        cmd = input("\nКоманда: ").strip()

        if cmd == "1":
            colony.tick()
        elif cmd == "2":
            try:
                steps = int(input("Количество шагов: "))
                for _ in range(steps):
                    colony.tick()
            except ValueError:
                print("Неверное число")
        elif cmd == "3":
            _assign_ant(colony)
        elif cmd == "4":
            save_colony(colony)
            print("Сохранено!")
            break
        elif cmd == "5":
            issue = input("Вопрос для голосования: ") or "Общий вопрос"
            result = colony.hold_voting(issue)
            print(f"\nРезультат: За {result.for_count}, Против {result.against_count}, Воздержались {result.abstain_count}, Потерялись {result.lost_count}")
            if result.queen_overridden:
                print("Матка уточнила результаты!")
        elif cmd == "6":
            print("Выход без сохранения")
            break


def _assign_ant(colony: Colony) -> None:
    alive = colony.get_alive_ants()
    if not alive:
        print("Нет живых муравьев")
        return

    print("Доступные муравьи:")
    for i, ant in enumerate(alive[:20]):
        room = ant.current_room or "none"
        print(f"  {i}. age={ant.age} room={room}")

    try:
        ant_idx = int(input("Индекс муравья: "))
        if ant_idx < 0 or ant_idx >= len(alive):
            print("Неверный индекс")
            return
    except ValueError:
        print("Ошибка ввода")
        return

    print("Доступные комнаты:")
    room_list = list(colony.rooms.keys())
    for i, (rid, room) in enumerate(colony.rooms.items()):
        print(f"  {i}. [{rid}] {room.name} ({len(room.ant_ids)}/{room.capacity})")

    try:
        room_choice = int(input("Номер комнаты: "))
        if room_choice < 0 or room_choice >= len(room_list):
            print("Неверный выбор")
            return
        room_id = room_list[room_choice]
    except ValueError:
        print("Ошибка ввода")
        return

    real_idx = colony.ants.index(alive[ant_idx])
    if colony.assign_ant_to_room(real_idx, room_id):
        print(f"Муравей назначен в комнату '{colony.rooms[room_id].name}'")
    else:
        print("Не удалось назначить муравья")


def _list_saves_only() -> None:
    saves = list_saves()
    if not saves:
        print("Нет сохранений")
        return
    print("\nСохранения:")
    for path in saves:
        print(f"  {path.stem}")


def main() -> None:
    while True:
        print("\n=== СИМУЛЯТОР МУРАВЬИНОЙ ФЕРМЫ ===")
        print("1. Создать новую колонию")
        print("2. Загрузить колонию")
        print("3. Список сохранений")
        print("4. Выход")
        cmd = input("\nКоманда: ").strip()

        if cmd == "1":
            _create_colony()
        elif cmd == "2":
            _load_and_run()
        elif cmd == "3":
            _list_saves_only()
        elif cmd == "4":
            print("До свидания!")
            break


if __name__ == "__main__":
    main()
