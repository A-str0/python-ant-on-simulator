import abc
from typing import Any


ANT_TYPES_REGISTRY: dict[str, type["Ant"]] = {}


class AntStatus:
    ALIVE = "alive"
    DEAD = "dead"
    SMELLS_LIKE_DEAD = "smells_like_dead"
    FERMENTED = "fermented"
    BILLIARD_MAIN = "billiard_main"
    INFECTED = "infected"
    CHAMPION = "champion"


STAT_NAMES = ["Б", "И", "Л", "Ь", "Я", "Р", "Д"]


class Ant(abc.ABC):
    ant_type_name: str = ""

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
        self.statuses: set[str] = set()

        self.stats: dict[str, int] = {k: 5 for k in STAT_NAMES}
        self.stat_progress: dict[str, float] = {k: 0.0 for k in STAT_NAMES}
        self.current_room: str | None = None

    def tick(self) -> None:
        self.age += 1
        if self.age > self.life_period:
            self.alive = False
            self.statuses.add(AntStatus.DEAD)

    def train_stat(self, stat: str, amount: float = 0.1) -> None:
        if stat not in self.stats:
            return
        if not self.alive or AntStatus.SMELLS_LIKE_DEAD in self.statuses:
            return
        if AntStatus.BILLIARD_MAIN in self.statuses and stat != "И":
            return

        self.stat_progress[stat] += amount
        if self.stat_progress[stat] >= 1.0 and self.stats[stat] < 10:
            self.stats[stat] += 1
            self.stat_progress[stat] -= 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.ant_type_name,
            "name": self.name,
            "carry_capacity": self.carry_capacity,
            "life_period": self.life_period,
            "food_per_tick": self.food_per_tick,
            "birth_rate": self.birth_rate,
            "speed": self.speed,
            "role": self.role,
            "age": self.age,
            "alive": self.alive,
            "statuses": list(self.statuses),
            "stats": dict(self.stats),
            "stat_progress": dict(self.stat_progress),
            "current_room": self.current_room,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ant":
        ant = cls()
        ant.age = data["age"]
        ant.alive = data["alive"]
        ant.statuses = set(data.get("statuses", []))
        ant.stats = data.get("stats", ant.stats.copy())
        ant.stat_progress = data.get("stat_progress", ant.stat_progress.copy())
        ant.current_room = data.get("current_room")
        return ant

    def play_billiards(self) -> None:
        ...


def _register_ant_type(cls: type[Ant]) -> type[Ant]:
    if cls.ant_type_name:
        ANT_TYPES_REGISTRY[cls.ant_type_name] = cls
    return cls


@_register_ant_type
class Harvester(Ant):
    ant_type_name = "Harvester"

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


@_register_ant_type
class WeaverAnt(Ant):
    ant_type_name = "WeaverAnt"

    def __init__(self) -> None:
        super().__init__(
            name="Азиатские муравьи-портные",
            carry_capacity=4,
            life_period=35,
            food_per_tick=3,
            birth_rate=1.2,
            speed=1,
            role="builder",
        )
        self.stats = {"Б": 4, "И": 6, "Л": 4, "Ь": 7, "Я": 4, "Р": 6, "Д": 5}

    def build_leaf_room(self, larvae_count: int) -> bool:
        return larvae_count >= 1


@_register_ant_type
class RedReactiveAnt(Ant):
    ant_type_name = "RedReactiveAnt"

    def __init__(self) -> None:
        super().__init__(
            name="Рыжие реактивные муравьи",
            carry_capacity=3,
            life_period=25,
            food_per_tick=3,
            birth_rate=2.0,
            speed=2,
            role="worker",
        )
        self.stats = {"Б": 6, "И": 3, "Л": 5, "Ь": 4, "Я": 6, "Р": 5, "Д": 4}


@_register_ant_type
class ExplodingAnt(Ant):
    ant_type_name = "ExplodingAnt"

    def __init__(self) -> None:
        super().__init__(
            name="Взрывающиеся муравьи",
            carry_capacity=2,
            life_period=20,
            food_per_tick=4,
            birth_rate=1.0,
            speed=1,
            role="soldier",
        )
        self.stats = {"Б": 7, "И": 7, "Л": 3, "Ь": 3, "Я": 8, "Р": 4, "Д": 6}

    def explode(self, target_hp: int) -> int:
        self.alive = False
        self.statuses.add(AntStatus.DEAD)
        return min(10, target_hp + self.stats.get("Л", 3))


def create_ant(ant_type: str) -> Ant:
    if ant_type not in ANT_TYPES_REGISTRY:
        raise ValueError(f"Unknown ant type: {ant_type}")
    return ANT_TYPES_REGISTRY[ant_type]()


def ant_from_dict(data: dict[str, Any]) -> Ant:
    ant_type = data["type"]
    if ant_type not in ANT_TYPES_REGISTRY:
        raise ValueError(f"Unknown ant type: {ant_type}")
    return ANT_TYPES_REGISTRY[ant_type].from_dict(data)
