from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Mission:
    id: str
    title: str
    description: str
    goals: dict[str, int]
    reward: str
    completed: bool = False
    progress: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "goals": dict(self.goals),
            "reward": self.reward,
            "completed": self.completed,
            "progress": dict(self.progress),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mission":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            goals=dict(data.get("goals", {})),
            reward=data.get("reward", ""),
            completed=bool(data.get("completed", False)),
            progress=dict(data.get("progress", {})),
        )


def default_campaign() -> list[Mission]:
    return [
        Mission(
            "1.1",
            "Первый шар",
            "Открыть бильярдную и не потерять всю еду.",
            {"ticks": 10, "rooms": 4},
            "Титул 'не совсем консоль'",
        ),
        Mission(
            "1.2",
            "Феромоновый бухгалтер",
            "Пережить голосование с суммой процентов не 100.",
            {"votes": 1},
            "Печать кворума",
        ),
        Mission(
            "1.3",
            "Матка сказала надо",
            "Построить или активировать 4 новые комнаты.",
            {"rooms": 10},
            "Чертеж казино",
        ),
        Mission(
            "2.1",
            "Соседи снизу",
            "Познакомиться с соседней колонией.",
            {"diplomacy": 1},
            "Пакет семечек дружбы",
        ),
        Mission(
            "2.2",
            "Грибной MVP",
            "Запустить грибной стартап и не получить конец света сразу.",
            {"mushroom_food": 10},
            "Сертификат стартапера",
        ),
        Mission(
            "2.3",
            "Крипто-матка",
            "Намайнить первые 100 ANT.",
            {"antcoin": 100},
            "Кошелек ANTCOIN V2",
        ),
        Mission(
            "3.1",
            "NFT, но без газа",
            "Отчеканить первого NFT-муравья.",
            {"nft": 1},
            "JPEG, который никто не видел",
        ),
        Mission(
            "3.2",
            "AI сказал норм",
            "Получить любой AI-off текст.",
            {"ai_lines": 1},
            "Шаблонная мудрость",
        ),
    ]
