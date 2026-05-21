from typing import Any


class Room:
    def __init__(
        self,
        room_id: str,
        name: str,
        capacity: int,
        room_type: str,
        x: int = 0,
        y: int = 0,
        defense: int = 0,
    ) -> None:
        self.id = room_id
        self.name = name
        self.capacity = capacity
        self.type = room_type
        self.ant_ids: list[str] = []
        self.extra: dict[str, Any] = {}
        self.x = x
        self.y = y
        self.defense = defense
        self.enabled = True

    @property
    def is_full(self) -> bool:
        return len(self.ant_ids) >= self.capacity

    @property
    def occupancy(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return min(1.0, len(self.ant_ids) / self.capacity)

    def assign_ant(self, ant_id: str) -> bool:
        if not self.enabled or self.is_full:
            return False
        if ant_id in self.ant_ids:
            return True
        self.ant_ids.append(ant_id)
        return True

    def remove_ant(self, ant_id: str) -> bool:
        if ant_id in self.ant_ids:
            self.ant_ids.remove(ant_id)
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "type": self.type,
            "ant_ids": list(self.ant_ids),
            "extra": dict(self.extra),
            "x": self.x,
            "y": self.y,
            "defense": self.defense,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Room":
        room = cls(
            data["id"],
            data["name"],
            data["capacity"],
            data["type"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            defense=data.get("defense", 0),
        )
        room.ant_ids = list(data.get("ant_ids", []))
        room.extra = dict(data.get("extra", {}))
        room.enabled = bool(data.get("enabled", True))
        return room


def create_default_rooms() -> dict[str, Room]:
    specs = [
        ("food_storage", "Склад пищи", 80, "food_storage", 1, 1, 5),
        ("cemetery", "Кладбище живых и мертвых", 60, "cemetery", 0, 3, 1),
        ("royal_chamber", "Королевская зал", 15, "royal_chamber", 3, 2, 10),
        ("billiard_room", "Бильярдная", 35, "billiard_room", 5, 1, 2),
        ("soft_sign_room", "Комната мягкого знака", 25, "soft_sign_room", 6, 3, 1),
        ("pheromone_circle", "Феромоновый кружок (о)", 25, "pheromone_circle", 2, 4, 1),
        ("mushroom_startup", "Грибной стартап", 40, "mushroom_startup", 4, 4, 2),
        ("voting_room", "Комната голосования", 80, "voting_room", 3, 0, 4),
        ("surface", "Поверхность", 500, "surface", 3, 6, 0),
        ("server_room", "Серверная ANTCOIN", 30, "server_room", 7, 2, 3),
        ("gym_seed", "Качалка семечки", 30, "gym_seed", 1, 5, 2),
        ("water_room", "Комната с водой", 50, "water_room", 6, 5, 1),
        ("rehab_cell", "Одиночная реабилитация", 10, "rehab_cell", 0, 5, 0),
        ("hammock_room", "Гамачная профсоюза", 45, "hammock_room", 7, 5, 0),
        ("casino", "Казино имени кийка", 30, "casino", 5, 6, 2),
        ("cue_armory", "Арсенал бильярдных киёв", 20, "cue_armory", 1, 0, 8),
        ("nursery", "Личиночный коворкинг", 45, "nursery", 4, 0, 4),
        ("trade_floor", "Муравьиная биржа", 40, "trade_floor", 7, 0, 1),
        ("council_office", "Кабинет чиновника", 12, "council_office", 0, 1, 0),
    ]
    rooms = {
        room_id: Room(room_id, name, capacity, room_type, x, y, defense)
        for room_id, name, capacity, room_type, x, y, defense in specs
    }
    rooms["server_room"].enabled = False
    return rooms


ROOM_TRAIN_MAP: dict[str, list[str]] = {
    "food_storage": ["Б", "Л"],
    "billiard_room": ["И"],
    "soft_sign_room": ["Ь"],
    "pheromone_circle": ["Р"],
    "mushroom_startup": ["Д"],
    "royal_chamber": ["Я"],
    "cemetery": [],
    "voting_room": [],
    "surface": ["Б"],
    "server_room": ["Д"],
    "gym_seed": ["Л", "Д"],
    "water_room": ["Ь"],
    "rehab_cell": ["И", "Д"],
    "hammock_room": ["Ь"],
    "casino": ["И", "Я"],
    "cue_armory": ["Л", "Д"],
    "nursery": ["Я", "Ь"],
    "trade_floor": ["Б", "Д"],
    "council_office": ["Я"],
}
