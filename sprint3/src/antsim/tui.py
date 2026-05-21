from __future__ import annotations

import os
import time
from pathlib import Path

from .ants import ANT_TYPES_REGISTRY, AntStatus
from .charts import bar_chart, heatmap, line_chart, radar_stats
from .colony import Colony
from .storage import save_colony


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def render_dashboard(colony: Colony) -> str:
    snapshot = colony.snapshot()
    history = snapshot["history"]
    room_counts = {
        room.name[:12]: len(room.ant_ids) for room in colony.rooms.values() if room.enabled
    }
    status_counts: dict[str, int] = {}
    for ant in colony.ants:
        if not ant.statuses and ant.alive:
            status_counts["ok"] = status_counts.get("ok", 0) + 1
        for status in ant.statuses:
            status_counts[status] = status_counts.get(status, 0) + 1

    food_values = [point["food"] for point in history]
    pop_values = [point["population"] for point in history]
    ant_values = [point["antcoin"] for point in history]

    lines = [
        "╔══════════════════════════════════════════════════════════════════════╗",
        f"║ {colony.id:<30} TICK {colony.time:<6} MODE {'PAUSE' if colony.paused else 'LIVE':<5} ║",
        "╠══════════════════════════════════════════════════════════════════════╣",
        (
            "║ "
            f"Муравьи {snapshot['population']}/{snapshot['total_ants']} | "
            f"Еда {colony.resources['food']} | ПББ {colony.resources['protein']} | "
            f"Вода {colony.resources['water']} | ANT {colony.antcoin:.1f}"
        )[:71]
        + "║",
        (
            "║ "
            f"BTC ${colony.btc_price:,.0f} | ANT ${colony.ant_price:.6f} | "
            f"NFT {len(colony.nft_registry)} | счастье {colony.average_happiness():.1f}"
        )[:71]
        + "║",
        "╚══════════════════════════════════════════════════════════════════════╝",
        "",
        line_chart("Food stock", food_values),
        line_chart("Population", pop_values),
        line_chart("ANTCOIN", ant_values),
        radar_stats(colony.get_alive_ants()),
        "",
        bar_chart("Комнаты", room_counts, width=18),
        "",
        bar_chart("Статусы", status_counts, width=18),
        "",
        heatmap(colony.rooms),
        "",
        "Активные события:",
    ]
    if colony.active_events:
        for event in colony.active_events[:6]:
            lines.append(f"  - {event.name}: {event.ticks_left}/{event.duration}")
    else:
        lines.append("  - тихо, слишком тихо")

    lines.append("")
    lines.append("Лог:")
    lines.extend(f"  {item}" for item in colony.event_log[-8:])
    lines.append("")
    lines.append(
        "Hotkeys: Space pause | Enter tick | 1-9 speed | r room | R mass | v vote | "
        "g charts | G god | n NFT | a AI | s save | q quit"
    )
    return "\n".join(lines)


def render_room(colony: Colony, room_id: str) -> str:
    room = colony.rooms[room_id]
    ants = [ant for ant in colony.ants if ant.current_room == room_id]
    lines = [
        f"=== {room.name} [{room.id}] ===",
        f"type={room.type} capacity={len(room.ant_ids)}/{room.capacity} defense={room.defense}",
        f"extra={room.extra}",
        "",
    ]
    for ant in ants[:30]:
        statuses = ", ".join(sorted(ant.statuses)) or "ok"
        stats = " ".join(f"{k}{v}" for k, v in ant.stats.items())
        lines.append(f"- {ant.personal_name}: {statuses}; {stats}")
    if len(ants) > 30:
        lines.append(f"... и еще {len(ants) - 30}")
    return "\n".join(lines)


def launch_tui(colony: Colony, save_dir: Path) -> None:
    while True:
        clear_screen()
        print(render_dashboard(colony))
        command = input("\n> ").strip()

        if command == "q":
            break
        if command == " ":
            colony.paused = not colony.paused
        elif command == "":
            colony.tick()
        elif command.isdigit():
            colony.tui_speed = max(1, min(9, int(command)))
            for _ in range(colony.tui_speed):
                colony.tick()
        elif command == "r":
            _assign_one(colony)
        elif command == "R":
            _mass_assign(colony)
        elif command == "v":
            issue = input("Вопрос голосования: ") or "Матка сказала надо?"
            result = colony.hold_voting(issue)
            print(result.to_dict())
            input("Enter...")
        elif command == "g":
            _show_charts(colony)
        elif command == "G":
            _god_mode(colony)
        elif command == "n":
            _nft_menu(colony)
        elif command == "a":
            _ai_menu(colony)
        elif command == "s":
            save_colony(colony, save_dir)
            print("Сохранено.")
            time.sleep(0.5)
        elif command.startswith("room "):
            _, room_id = command.split(maxsplit=1)
            if room_id in colony.rooms:
                clear_screen()
                print(render_room(colony, room_id))
                input("Enter...")
        else:
            colony.log(f"неизвестная команда TUI: {command}")


def _assign_one(colony: Colony) -> None:
    alive = colony.get_alive_ants()
    for i, ant in enumerate(alive[:30]):
        print(f"{i}: {ant.personal_name} room={ant.current_room or '-'}")
    try:
        visible_index = int(input("Муравей: "))
    except ValueError:
        return
    if visible_index < 0 or visible_index >= len(alive):
        return
    room_ids = [room_id for room_id, room in colony.rooms.items() if room.enabled]
    for i, room_id in enumerate(room_ids):
        room = colony.rooms[room_id]
        print(f"{i}: {room.name} ({len(room.ant_ids)}/{room.capacity})")
    try:
        room_index = int(input("Комната: "))
    except ValueError:
        return
    if 0 <= room_index < len(room_ids):
        colony.assign_ant_to_room(colony.ants.index(alive[visible_index]), room_ids[room_index])


def _mass_assign(colony: Colony) -> None:
    status = input(f"Статус ({AntStatus.FERMENTED}/{AntStatus.BILLIARD_MAIN}/...): ")
    room_id = input("room_id: ")
    count = colony.mass_assign(status, room_id)
    colony.log(f"массово назначено {count} муравьев со статусом {status}")


def _show_charts(colony: Colony) -> None:
    clear_screen()
    history = colony.history
    print(line_chart("Food stock", [p["food"] for p in history], width=60))
    print(line_chart("Protein", [p["protein"] for p in history], width=60))
    print(line_chart("Water", [p["water"] for p in history], width=60))
    print(line_chart("Population", [p["population"] for p in history], width=60))
    print(line_chart("ANTCOIN", [p["antcoin"] for p in history], width=60))
    print(radar_stats(colony.get_alive_ants()))
    print(heatmap(colony.rooms))
    input("Enter...")


def _god_mode(colony: Colony) -> None:
    print("God Mode: 1 resource, 2 event, 3 balagan, 4 add ants, 5 pest")
    command = input("> ")
    if command == "1":
        resource = input("resource food/protein/water: ")
        amount = int(input("amount: "))
        print(colony.god_mode("set_resource", resource=resource, amount=amount))
    elif command == "2":
        event_type = input("event pheromone/smell/fermented/fungus/billiard/radiation/ufo: ")
        print(colony.god_mode("spawn_event", event_type=event_type))
    elif command == "3":
        print(colony.god_mode("balagan"))
    elif command == "4":
        amount = int(input("amount: "))
        print(colony.god_mode("add_ants", amount=amount))
    elif command == "5":
        print(colony.god_mode("pest"))
    input("Enter...")


def _nft_menu(colony: Colony) -> None:
    print(f"ANT balance: {colony.antcoin:.1f}")
    print("1 mint first alive | 2 list first NFT | 3 buy market")
    command = input("> ")
    if command == "1":
        alive = colony.get_alive_ants()
        if alive:
            colony.antcoin = max(colony.antcoin, 50.0)
            nft_id = colony.mint_nft(colony.ants.index(alive[0]))
            print(nft_id or "не вышло")
    elif command == "2":
        if colony.nft_registry:
            nft_id = next(iter(colony.nft_registry))
            print(colony.list_nft_for_sale(nft_id, 75.0))
    elif command == "3":
        print(colony.buy_first_nft())
    input("Enter...")


def _ai_menu(colony: Colony) -> None:
    print("AI modes: off/local/cloud/chaos. Сейчас:", colony.ai.mode)
    mode = input("new mode или пусто: ")
    if mode:
        colony.ai.set_mode(mode)
    question = input("Вопрос матке: ") or "что делать с бильярдом?"
    print(colony.ai_queen_dialog(question))
    input("Enter...")


def choose_ant_type() -> str:
    types = list(ANT_TYPES_REGISTRY.keys())
    for i, ant_type in enumerate(types, start=1):
        ant = ANT_TYPES_REGISTRY[ant_type]()
        print(f"{i}. {ant.name} ({ant_type})")
    try:
        index = int(input("Вид: ")) - 1
    except ValueError:
        return "Harvester"
    if 0 <= index < len(types):
        return types[index]
    return "Harvester"
