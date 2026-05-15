import abc
from typing import Any


class Ant(abc.ABC):
    def __init__(
        self,
        name: str,
        carry_capacity: int,
        life_period: int,
        food_per_tick: int,
        birth_rate: float,
        speed: int,
        role: str,
    ) -> None:
        self.name = name
        self.carry_capacity = carry_capacity
        self.life_period = life_period
        self.food_per_tick = food_per_tick
        self.birth_rate = birth_rate
        self.speed = speed
        self.role = role
        self.age = 0
        self.alive = True

    def tick(self) -> None:
        self.age += 1
        if self.age >= self.life_period:
            self.alive = False

    @abc.abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    def play_billiards(self) -> None:
        ...


class Harvester(Ant):
    def __init__(self) -> None:
        super().__init__(
            name="Муравьи-жнецы",
            carry_capacity=5,
            life_period=30,
            food_per_tick=2,
            birth_rate=1.5,
            speed=1,
            role="worker",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "Harvester",
            "name": self.name,
            "carry_capacity": self.carry_capacity,
            "life_period": self.life_period,
            "food_per_tick": self.food_per_tick,
            "birth_rate": self.birth_rate,
            "speed": self.speed,
            "role": self.role,
            "age": self.age,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Harvester":
        ant = cls()
        ant.age = data["age"]
        ant.alive = data["alive"]
        return ant
