from typing import Any

from ants import Ant, Harvester


class Colony:
    def __init__(self, colony_id: str, ant_count: int, food: int) -> None:
        self.id = colony_id
        self.food = food
        self.ants: list[Ant] = [Harvester() for _ in range(ant_count)]
        self.time = 0

    def tick(self) -> None:
        self.time += 1

        for ant in self.ants:
            if ant.alive:
                ant.tick()
                self.food -= ant.food_per_tick

        self.ants = [ant for ant in self.ants if ant.alive]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "food": self.food,
            "time": self.time,
            "ants": [ant.to_dict() for ant in self.ants],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Colony":
        colony = cls(data["id"], 0, data["food"])
        colony.time = data["time"]
        colony.ants = []

        for ant_data in data["ants"]:
            if ant_data["type"] == "Harvester":
                colony.ants.append(Harvester.from_dict(ant_data))

        return colony
