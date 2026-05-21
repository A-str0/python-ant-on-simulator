import random
from typing import Any
from uuid import uuid4

from ants import (
    Ant,
    AntStatus,
    STAT_NAMES,
    ant_from_dict,
    create_ant,
)
from rooms import ROOM_TRAIN_MAP, Room, create_default_rooms


class VotingResult:
    def __init__(self) -> None:
        self.for_count = 0
        self.against_count = 0
        self.abstain_count = 0
        self.lost_count = 0
        self.issue: str = ""
        self.queen_overridden = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "for_count": self.for_count,
            "against_count": self.against_count,
            "abstain_count": self.abstain_count,
            "lost_count": self.lost_count,
            "issue": self.issue,
            "queen_overridden": self.queen_overridden,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VotingResult":
        r = cls()
        r.for_count = data["for_count"]
        r.against_count = data["against_count"]
        r.abstain_count = data["abstain_count"]
        r.lost_count = data["lost_count"]
        r.issue = data["issue"]
        r.queen_overridden = data["queen_overridden"]
        return r


class RandomEvent:
    def __init__(
        self, event_id: str, name: str, event_type: str, duration: int
    ) -> None:
        self.id = event_id
        self.name = name
        self.type = event_type
        self.duration = duration
        self.ticks_left = duration

    def tick(self) -> bool:
        self.ticks_left -= 1
        return self.ticks_left <= 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "duration": self.duration,
            "ticks_left": self.ticks_left,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RandomEvent":
        e = cls(data["id"], data["name"], data["type"], data["duration"])
        e.ticks_left = data["ticks_left"]
        return e


class Colony:
    def __init__(
        self,
        colony_id: str,
        ant_count: int,
        food: int,
        ant_type: str = "Harvester",
    ) -> None:
        if not isinstance(colony_id, str):
            raise TypeError("colony_id must be a string")
        if not isinstance(ant_count, int) or isinstance(ant_count, bool):
            raise TypeError("ant_count must be an integer")
        if not isinstance(food, int) or isinstance(food, bool):
            raise TypeError("food must be an integer")
        if ant_count < 0:
            raise ValueError("ant_count cannot be negative")
        if food < 0:
            raise ValueError("food cannot be negative")

        self.id = colony_id
        self.food = food
        self.ant_type = ant_type
        self.ants: list[Ant] = [create_ant(ant_type) for _ in range(ant_count)]
        self.time = 0
        self.rooms: dict[str, Room] = create_default_rooms()
        self.active_events: list[RandomEvent] = []
        self.last_voting: VotingResult | None = None
        self.queen_morale = 50
        self.mushroom_fungus_level = 0

    def get_alive_ants(self) -> list[Ant]:
        return [a for a in self.ants if a.alive]

    def get_alive_ants_count(self) -> int:
        return sum(1 for a in self.ants if a.alive)

    def assign_ant_to_room(self, ant_index: int, room_id: str) -> bool:
        if ant_index < 0 or ant_index >= len(self.ants):
            return False
        ant = self.ants[ant_index]
        if not ant.alive:
            return False
        if room_id not in self.rooms:
            return False

        for r in self.rooms.values():
            r.remove_ant(str(ant_index))

        room = self.rooms[room_id]
        if room.assign_ant(str(ant_index)):
            ant.current_room = room_id
            return True
        return False

    def tick(self) -> None:
        self.time += 1

        for ant in self.ants:
            if ant.alive:
                ant.tick()
                self.food -= ant.food_per_tick

                if ant.current_room and ant.current_room in self.rooms:
                    room = self.rooms[ant.current_room]
                    for stat in ROOM_TRAIN_MAP.get(room.type, []):
                        ant.train_stat(stat, 0.05)

                if AntStatus.SMELLS_LIKE_DEAD in ant.statuses:
                    pass

        self._handle_death()
        self._handle_birth()
        self._handle_events()
        self._maybe_spawn_event()

        if self.food < 0:
            self.food = 0

    def _handle_death(self) -> None:
        for ant in self.ants:
            if ant.alive and AntStatus.DEAD in ant.statuses:
                for room in self.rooms.values():
                    room.remove_ant(str(self.ants.index(ant)))
                ant.current_room = "cemetery"
                self.rooms["cemetery"].assign_ant(str(self.ants.index(ant)))

    def _handle_birth(self) -> None:
        alive = self.get_alive_ants()
        if not alive:
            return
        avg_birth_rate = sum(a.birth_rate for a in alive) / len(alive)
        birth_chance = avg_birth_rate / 100.0
        if random.random() < birth_chance and self.food > len(alive):
            new_ant = create_ant(self.ant_type)
            self.ants.append(new_ant)
            self.food -= 1

    def _handle_events(self) -> None:
        expired = []
        for event in self.active_events:
            if event.tick():
                expired.append(event)
        for e in expired:
            self._resolve_event(e)
            self.active_events.remove(e)

    def _resolve_event(self, event: RandomEvent) -> None:
        if event.type == "pheromone_death_spiral":
            for ant in self.get_alive_ants():
                if ant.stats.get("Р", 5) < 4 and random.random() < 0.3:
                    ant.train_stat("Д", 0.1)
        elif event.type == "smells_like_dead":
            pass
        elif event.type == "fermented_syrup":
            for ant in self.get_alive_ants():
                if "fermented" in ant.statuses:
                    ant.statuses.discard("fermented")
        elif event.type == "zombie_fungus":
            self.mushroom_fungus_level = max(0, self.mushroom_fungus_level - 1)
            for ant in self.get_alive_ants():
                if AntStatus.INFECTED in ant.statuses:
                    if random.random() < 0.5:
                        ant.statuses.discard("infected")
        elif event.type == "billiard_addiction":
            for ant in self.get_alive_ants():
                if AntStatus.BILLIARD_MAIN in ant.statuses:
                    if random.random() < 0.3:
                        ant.statuses.discard("billiard_main")

    def _maybe_spawn_event(self) -> None:
        checks = [
            (0.02, self._spawn_pheromone_death_spiral),
            (0.03, self._spawn_smells_like_dead),
            (0.01, self._spawn_fermented_syrup),
            (0.005, self._spawn_zombie_fungus),
            (0.02, self._spawn_billiard_addiction),
            (0.01, self._spawn_voting),
        ]
        for chance, spawn_fn in checks:
            if random.random() < chance:
                spawn_fn()
                break

    def _spawn_pheromone_death_spiral(self) -> None:
        event = RandomEvent(
            event_id=str(uuid4()),
            name="Феромоновая смерть-спираль",
            event_type="pheromone_death_spiral",
            duration=5,
        )
        self.active_events.append(event)
        for ant in self.get_alive_ants():
            if ant.stats.get("Р", 5) < 4 and random.random() < 0.5:
                ant.current_room = None

    def _spawn_smells_like_dead(self) -> None:
        alive = self.get_alive_ants()
        if not alive:
            return
        target = random.choice(alive)
        target.statuses.add(AntStatus.SMELLS_LIKE_DEAD)
        event = RandomEvent(
            event_id=str(uuid4()),
            name="Он не умер, он просто пахнет",
            event_type="smells_like_dead",
            duration=3,
        )
        self.active_events.append(event)

        for ant in self.get_alive_ants():
            if ant is not target and random.random() < 0.3:
                ant.current_room = "cemetery"

    def _spawn_fermented_syrup(self) -> None:
        event = RandomEvent(
            event_id=str(uuid4()),
            name="Забродивший сироп",
            event_type="fermented_syrup",
            duration=4,
        )
        self.active_events.append(event)
        for ant in self.get_alive_ants():
            if ant.ant_type_name == "RedReactiveAnt" and random.random() < 0.4:
                ant.statuses.add(AntStatus.FERMENTED)
            elif random.random() < 0.1:
                ant.statuses.add(AntStatus.FERMENTED)

    def _spawn_zombie_fungus(self) -> None:
        if self.mushroom_fungus_level < 3:
            return
        event = RandomEvent(
            event_id=str(uuid4()),
            name="Зомби-гриб",
            event_type="zombie_fungus",
            duration=6,
        )
        self.active_events.append(event)
        alive = self.get_alive_ants()
        if alive:
            target = random.choice(alive)
            target.statuses.add(AntStatus.INFECTED)

    def _spawn_billiard_addiction(self) -> None:
        event = RandomEvent(
            event_id=str(uuid4()),
            name="Бильярдная зависимость",
            event_type="billiard_addiction",
            duration=5,
        )
        self.active_events.append(event)
        for ant in self.get_alive_ants():
            if (
                ant.current_room == "billiard_room"
                and ant.stats.get("И", 5) < 4
                and random.random() < 0.5
            ):
                ant.statuses.add(AntStatus.BILLIARD_MAIN)

    def _spawn_voting(self) -> None:
        self.hold_voting("Провести бильярдный турнир")

    def hold_voting(self, issue: str) -> VotingResult:
        alive = self.get_alive_ants()
        if not alive:
            return VotingResult()

        result = VotingResult()
        result.issue = issue

        for ant in alive:
            roll = random.random()
            queen_power = ant.stats.get("Я", 5) / 10.0
            if AntStatus.FERMENTED in ant.statuses:
                roll = random.random()

            if roll < 0.37 - queen_power * 0.1:
                result.for_count += 1
            elif roll < 0.85:
                result.against_count += 1
            elif roll < 0.97:
                result.abstain_count += 1
            else:
                result.lost_count += 1

        if random.random() < 0.2:
            result.queen_overridden = True

        self.last_voting = result
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "food": self.food,
            "time": self.time,
            "ant_type": self.ant_type,
            "ants": [ant.to_dict() for ant in self.ants],
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "active_events": [e.to_dict() for e in self.active_events],
            "last_voting": self.last_voting.to_dict() if self.last_voting else None,
            "queen_morale": self.queen_morale,
            "mushroom_fungus_level": self.mushroom_fungus_level,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Colony":
        ant_type = data.get("ant_type", "Harvester")
        colony = cls(data["id"], 0, data["food"], ant_type)
        colony.time = data["time"]
        colony.ants = []

        for ant_data in data["ants"]:
            colony.ants.append(ant_from_dict(ant_data))

        if "rooms" in data:
            colony.rooms = {
                k: Room.from_dict(v) for k, v in data["rooms"].items()
            }
        else:
            colony.rooms = create_default_rooms()

        if "active_events" in data:
            colony.active_events = [
                RandomEvent.from_dict(e) for e in data["active_events"]
            ]

        if "last_voting" in data and data["last_voting"]:
            colony.last_voting = VotingResult.from_dict(data["last_voting"])

        colony.queen_morale = data.get("queen_morale", 50)
        colony.mushroom_fungus_level = data.get("mushroom_fungus_level", 0)

        return colony
