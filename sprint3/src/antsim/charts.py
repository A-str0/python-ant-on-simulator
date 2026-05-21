from __future__ import annotations

from .ants import STAT_NAMES, Ant
from .rooms import Room


BLOCKS = "▁▂▃▄▅▆▇█"


def _spark(values: list[float], width: int = 40) -> str:
    if not values:
        return "нет данных".ljust(width)
    sample = values[-width:]
    low = min(sample)
    high = max(sample)
    if high == low:
        return BLOCKS[0] * len(sample)
    chars = []
    for value in sample:
        idx = int((value - low) / (high - low) * (len(BLOCKS) - 1))
        chars.append(BLOCKS[idx])
    return "".join(chars)


def line_chart(title: str, values: list[float], width: int = 40) -> str:
    if not values:
        return f"{title:<18} | нет данных"
    return f"{title:<18} | {_spark(values, width)} {values[-1]:.1f}"


def bar_chart(title: str, data: dict[str, int], width: int = 24) -> str:
    if not data:
        return f"{title}\n  нет данных"
    max_value = max(max(data.values()), 1)
    lines = [title]
    for key, value in sorted(data.items(), key=lambda item: item[0]):
        bar_len = int(value / max_value * width)
        lines.append(f"  {key[:16]:<16} {'█' * bar_len:<{width}} {value}")
    return "\n".join(lines)


def radar_stats(ants: list[Ant]) -> str:
    if not ants:
        return "B.I.L.Y.A.R.D. AVG | нет живых муравьев"
    averages: dict[str, float] = {}
    for stat in STAT_NAMES:
        averages[stat] = sum(ant.stats.get(stat, 0) for ant in ants) / len(ants)
    parts = []
    for stat in STAT_NAMES:
        value = averages[stat]
        parts.append(f"{stat}:{'█' * int(value)}{value:.1f}")
    return "B.I.L.Y.A.R.D. AVG | " + " ".join(parts)


def heatmap(rooms: dict[str, Room]) -> str:
    if not rooms:
        return "H E A T M A P\nнет комнат"
    max_x = max(room.x for room in rooms.values())
    max_y = max(room.y for room in rooms.values())
    grid = [[" ." for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    legend: list[str] = []
    for idx, room in enumerate(rooms.values(), start=1):
        symbol = f"{idx % 10}{_heat_symbol(room.occupancy)}"
        grid[room.y][room.x] = symbol
        legend.append(f"{idx % 10}: {room.name} ({len(room.ant_ids)}/{room.capacity})")
    lines = ["H E A T M A P"]
    lines.extend(" ".join(row) for row in grid)
    lines.append(" | ".join(legend[:8]))
    return "\n".join(lines)


def _heat_symbol(value: float) -> str:
    if value <= 0:
        return "."
    if value < 0.33:
        return "░"
    if value < 0.66:
        return "▒"
    if value < 1:
        return "▓"
    return "█"
