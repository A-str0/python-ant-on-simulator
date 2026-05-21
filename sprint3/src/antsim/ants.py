import abc
from typing import Any
from uuid import uuid4


ANT_TYPES_REGISTRY: dict[str, type["Ant"]] = {}
ANT_TYPE_ALIASES: dict[str, str] = {
    "Муравьи-жнецы": "Harvester",
    "Messor structor": "Harvester",
    "Азиатские муравьи-портные": "WeaverAnt",
    "Oecophylla smaragdina": "WeaverAnt",
    "Рыжие реактивные муравьи": "RedReactiveAnt",
    "Camponotus nicobarensis": "RedReactiveAnt",
    "Взрывающиеся муравьи": "ExplodingAnt",
    "Colobopsis explodens": "ExplodingAnt",
}


class AntStatus:
    ALIVE = "alive"
    DEAD = "dead"
    SMELLS_LIKE_DEAD = "smells_like_dead"
    FERMENTED = "fermented"
    BILLIARD_MAIN = "billiard_main"
    INFECTED = "infected"
    CHAMPION = "champion"
    INJURED = "injured"
    OUTRAGED = "outraged"
    CORRUPTED = "corrupted"
    RADIATED = "radiated"
    ABDUCTED = "abducted"
    ENLIGHTENED = "enlightened"
    STRIKING = "striking"
    ADDICTED = "addicted"
    SMELLY = "smelly"
    NFT = "nft"
    OFFICIAL = "official"
    BOUNTY = "bounty"
    ARTIST = "artist"
    HAMMOCKED = "hammocked"


STAT_NAMES = ["Б", "И", "Л", "Ь", "Я", "Р", "Д"]

PERSONAL_NAMES = [
    "Жора",
    "Илюха",
    "Борис-Бильярдный",
    "Матвей-Не-Дверь",
    "Семён-Семечка",
    "Рома-Рельса",
    "Антон-ANT",
    "Лёха-Лифтинг",
    "Ььь",
    "Кирилл-Кворум",
    "Пахом-Пахнет",
]


def _clamp_stat(value: int) -> int:
    return max(0, min(10, int(value)))


def _register_ant_type(cls: type["Ant"]) -> type["Ant"]:
    if cls.ant_type_name:
        ANT_TYPES_REGISTRY[cls.ant_type_name] = cls
    return cls


def normalize_ant_type(ant_type: str) -> str:
    return ANT_TYPE_ALIASES.get(ant_type, ant_type)


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
        self.id = str(uuid4())
        self.name = name
        self.personal_name = PERSONAL_NAMES[hash(self.id) % len(PERSONAL_NAMES)]
        self.carry_capacity = carry_capacity
        self.life_period = life_period
        self.food_per_tick = food_per_tick
        self.birth_rate = birth_rate
        self.speed = speed
        self.role = role
        self.age = 0
        self.alive = True
        self.statuses: set[str] = set()
        self.status_timers: dict[str, int] = {}
        self.stats: dict[str, int] = {k: 5 for k in STAT_NAMES}
        self.stat_progress: dict[str, float] = {k: 0.0 for k in STAT_NAMES}
        self.current_room: str | None = None
        self.happiness = 50
        self.health = 100
        self.starvation_ticks = 0
        self.biography: list[str] = ["родился и сразу попал в ТЗ"]
        self.achievements: list[str] = []
        self.nft_id: str | None = None

    @property
    def display_name(self) -> str:
        return f"{self.personal_name} ({self.name})"

    @property
    def resource_needs(self) -> dict[str, int]:
        return {"food": self.food_per_tick, "protein": 1, "water": 1}

    def add_status(self, status: str, duration: int | None = None) -> None:
        self.statuses.add(status)
        if duration is not None:
            self.status_timers[status] = duration
        self.remember(f"получил статус {status}")

    def remove_status(self, status: str) -> None:
        self.statuses.discard(status)
        self.status_timers.pop(status, None)

    def remember(self, text: str) -> None:
        self.biography.append(f"t{self.age}: {text}")
        self.biography = self.biography[-10:]

    def tick(self) -> None:
        self.age += 1
        expired: list[str] = []
        for status, ticks_left in self.status_timers.items():
            new_value = ticks_left - 1
            self.status_timers[status] = new_value
            if new_value <= 0:
                expired.append(status)
        for status in expired:
            self.remove_status(status)

        if self.age > self.life_period:
            self.die("старость решила, что хватит")

    def suffer_hunger(self) -> None:
        self.starvation_ticks += 1
        self.health -= 25
        self.happiness = max(0, self.happiness - 5)
        self.remember("понял трёхресурсную экономику через боль")
        if self.health <= 0:
            self.die("не хватило одного из ресурсов")

    def feed_successfully(self) -> None:
        self.starvation_ticks = 0
        self.health = min(100, self.health + 2)

    def die(self, reason: str) -> None:
        if not self.alive:
            return
        self.alive = False
        self.statuses.add(AntStatus.DEAD)
        self.remember(f"умер: {reason}")

    def train_stat(self, stat: str, amount: float = 0.1) -> bool:
        if stat not in self.stats:
            return False
        if not self.alive or AntStatus.SMELLS_LIKE_DEAD in self.statuses:
            return False
        if AntStatus.BILLIARD_MAIN in self.statuses and stat != "И":
            return False

        self.stat_progress[stat] += amount
        if self.stat_progress[stat] >= 1.0 and self.stats[stat] < 10:
            self.stats[stat] += 1
            self.stat_progress[stat] -= 1.0
            self.remember(f"прокачал {stat} до {self.stats[stat]}")
            return True
        return False

    @abc.abstractmethod
    def special_action(self) -> str:
        raise NotImplementedError

    def play_billiards(self) -> None:
        self.happiness = min(100, self.happiness + 5)
        self.train_stat("И", 0.2)
        if self.stats.get("И", 5) < 4 and self.happiness > 70:
            self.add_status(AntStatus.BILLIARD_MAIN, duration=20)
        self.remember("катал шары и делал вид, что это механика")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.ant_type_name,
            "name": self.name,
            "personal_name": self.personal_name,
            "carry_capacity": self.carry_capacity,
            "life_period": self.life_period,
            "food_per_tick": self.food_per_tick,
            "birth_rate": self.birth_rate,
            "speed": self.speed,
            "role": self.role,
            "age": self.age,
            "alive": self.alive,
            "statuses": sorted(self.statuses),
            "status_timers": dict(self.status_timers),
            "stats": dict(self.stats),
            "stat_progress": dict(self.stat_progress),
            "current_room": self.current_room,
            "happiness": self.happiness,
            "health": self.health,
            "starvation_ticks": self.starvation_ticks,
            "biography": list(self.biography),
            "achievements": list(self.achievements),
            "nft_id": self.nft_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ant":
        ant = cls()
        ant.id = data.get("id", str(uuid4()))
        ant.personal_name = data.get(
            "personal_name", PERSONAL_NAMES[hash(ant.id) % len(PERSONAL_NAMES)]
        )
        ant.age = data.get("age", 0)
        ant.alive = data.get("alive", True)
        ant.statuses = set(data.get("statuses", []))
        ant.status_timers = {
            str(k): int(v) for k, v in data.get("status_timers", {}).items()
        }
        ant.stats = {
            k: _clamp_stat(v) for k, v in data.get("stats", ant.stats.copy()).items()
        }
        for stat in STAT_NAMES:
            ant.stats.setdefault(stat, 5)
        ant.stat_progress = {
            k: float(v)
            for k, v in data.get("stat_progress", ant.stat_progress.copy()).items()
        }
        for stat in STAT_NAMES:
            ant.stat_progress.setdefault(stat, 0.0)
        ant.current_room = data.get("current_room")
        ant.happiness = int(data.get("happiness", 50))
        ant.health = int(data.get("health", 100))
        ant.starvation_ticks = int(data.get("starvation_ticks", 0))
        ant.biography = list(data.get("biography", ant.biography))[-10:]
        ant.achievements = list(data.get("achievements", []))
        ant.nft_id = data.get("nft_id")
        return ant


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
        self.stats = {"Б": 6, "И": 5, "Л": 6, "Ь": 5, "Я": 4, "Р": 5, "Д": 6}

    def special_action(self) -> str:
        return "перемолол семечки в муравьиный план Б"


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

    def special_action(self) -> str:
        return "посмотрел на личинку как на строительный степлер"


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

    def special_action(self) -> str:
        return "ускорился от забродившего сиропа, но забыл зачем"


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
        damage = min(25, 10 + self.stats.get("Д", 6) + self.stats.get("Л", 3))
        self.die("самопожертвование по ТЗ")
        self.achievements.append("официально взорвался")
        return min(target_hp, damage)

    def special_action(self) -> str:
        return "попросил всех отойти на два муравья назад"


def create_ant(ant_type: str) -> Ant:
    normalized = normalize_ant_type(ant_type)
    if normalized not in ANT_TYPES_REGISTRY:
        raise ValueError(f"Unknown ant type: {ant_type}")
    return ANT_TYPES_REGISTRY[normalized]()


def ant_from_dict(data: dict[str, Any]) -> Ant:
    ant_type = normalize_ant_type(data.get("type", "Harvester"))
    if ant_type not in ANT_TYPES_REGISTRY:
        raise ValueError(f"Unknown ant type: {ant_type}")
    return ANT_TYPES_REGISTRY[ant_type].from_dict(data)
