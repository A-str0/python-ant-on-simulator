from typing import Any


class Room:
    def __init__(
        self, room_id: str, name: str, capacity: int, room_type: str
    ) -> None:
        self.id = room_id
        self.name = name
        self.capacity = capacity
        self.type = room_type
        self.ant_ids: list[str] = []
        self.extra: dict[str, Any] = {}

    @property
    def is_full(self) -> bool:
        return len(self.ant_ids) >= self.capacity

    def assign_ant(self, ant_id: str) -> bool:
        if self.is_full:
            return False
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
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Room":
        room = cls(data["id"], data["name"], data["capacity"], data["type"])
        room.ant_ids = list(data.get("ant_ids", []))
        room.extra = dict(data.get("extra", {}))
        return room


def create_default_rooms() -> dict[str, Room]:
    rooms: dict[str, Room] = {
        "food_storage": Room(
            room_id="food_storage",
            name="Склад пищи",
            capacity=50,
            room_type="food_storage",
        ),
        "cemetery": Room(
            room_id="cemetery",
            name="Кладбище живых и мертвых",
            capacity=30,
            room_type="cemetery",
        ),
        "royal_chamber": Room(
            room_id="royal_chamber",
            name="Королевская зал",
            capacity=10,
            room_type="royal_chamber",
        ),
        "billiard_room": Room(
            room_id="billiard_room",
            name="Бильярдная",
            capacity=20,
            room_type="billiard_room",
        ),
        "soft_sign_room": Room(
            room_id="soft_sign_room",
            name="Комната мягкого знака",
            capacity=15,
            room_type="soft_sign_room",
        ),
        "pheromone_circle": Room(
            room_id="pheromone_circle",
            name="Феромоновый кружок (о)",
            capacity=15,
            room_type="pheromone_circle",
        ),
        "mushroom_startup": Room(
            room_id="mushroom_startup",
            name="Грибной стартап",
            capacity=20,
            room_type="mushroom_startup",
        ),
        "voting_room": Room(
            room_id="voting_room",
            name="Комната голосования",
            capacity=40,
            room_type="voting_room",
        ),
        "surface": Room(
            room_id="surface",
            name="Поверхность",
            capacity=200,
            room_type="surface",
        ),
    }
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
}
