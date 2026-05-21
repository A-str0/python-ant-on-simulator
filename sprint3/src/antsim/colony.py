from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .ai import TemplateAI
from .ants import (
    Ant,
    AntStatus,
    STAT_NAMES,
    ant_from_dict,
    create_ant,
    normalize_ant_type,
)
from .campaign import Mission, default_campaign
from .rooms import ROOM_TRAIN_MAP, Room, create_default_rooms


RESOURCE_NAMES = ("food", "protein", "water")


class VotingResult:
    def __init__(self) -> None:
        self.for_count = 0
        self.against_count = 0
        self.abstain_count = 0
        self.lost_count = 0
        self.issue: str = ""
        self.queen_overridden = False
        self.percentages: dict[str, int] = {}
        self.final_decision = "pending"

    def total_counted(self) -> int:
        return self.for_count + self.against_count + self.abstain_count + self.lost_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "for_count": self.for_count,
            "against_count": self.against_count,
            "abstain_count": self.abstain_count,
            "lost_count": self.lost_count,
            "issue": self.issue,
            "queen_overridden": self.queen_overridden,
            "percentages": dict(self.percentages),
            "final_decision": self.final_decision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VotingResult":
        result = cls()
        result.for_count = data.get("for_count", 0)
        result.against_count = data.get("against_count", 0)
        result.abstain_count = data.get("abstain_count", 0)
        result.lost_count = data.get("lost_count", 0)
        result.issue = data.get("issue", "")
        result.queen_overridden = data.get("queen_overridden", False)
        result.percentages = {
            str(k): int(v) for k, v in data.get("percentages", {}).items()
        }
        result.final_decision = data.get("final_decision", "pending")
        return result


class RandomEvent:
    def __init__(
        self,
        event_id: str,
        name: str,
        event_type: str,
        duration: int,
        description: str = "",
    ) -> None:
        self.id = event_id
        self.name = name
        self.type = event_type
        self.duration = duration
        self.ticks_left = duration
        self.description = description

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
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RandomEvent":
        event = cls(
            data["id"],
            data["name"],
            data["type"],
            data["duration"],
            data.get("description", ""),
        )
        event.ticks_left = data.get("ticks_left", event.duration)
        return event


@dataclass
class NeighborColony:
    name: str
    attitude: int = 0
    strength: int = 20
    resources: dict[str, int] | None = None
    last_action: str = "молчит и копает"

    def __post_init__(self) -> None:
        if self.resources is None:
            self.resources = {"food": 50, "protein": 20, "water": 40, "antcoin": 0}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "attitude": self.attitude,
            "strength": self.strength,
            "resources": dict(self.resources or {}),
            "last_action": self.last_action,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NeighborColony":
        return cls(
            name=data["name"],
            attitude=data.get("attitude", 0),
            strength=data.get("strength", 20),
            resources=dict(data.get("resources", {})),
            last_action=data.get("last_action", "молчит и копает"),
        )


class Colony:
    save_version = "3.0"

    def __init__(
        self,
        colony_id: str,
        ant_count: int,
        food: int,
        ant_type: str = "Harvester",
        seed: int | None = None,
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

        self.random = random.Random(seed)
        self.id = colony_id
        self.ant_type = normalize_ant_type(ant_type)
        self.ants: list[Ant] = [create_ant(self.ant_type) for _ in range(ant_count)]
        self.time = 0
        self.resources: dict[str, int] = {
            "food": food,
            "protein": max(ant_count * 30, food // 2, 10),
            "water": max(ant_count * 30, food // 2, 10),
        }
        self.rooms: dict[str, Room] = create_default_rooms()
        self.active_events: list[RandomEvent] = []
        self.event_log: list[str] = []
        self.last_voting: VotingResult | None = None
        self.queen_morale = 50
        self.mushroom_fungus_level = 0
        self.mushroom_food = 0
        self.market_rates: dict[str, float] = {
            "food/protein": 1.3,
            "food/water": 1.0,
            "protein/water": 1.1,
        }
        self.antcoin = 0.0
        self.antcoin_classic = 0.0
        self.btc_price = 69420.0
        self.ant_price = self.btc_price * 0.0000001
        self.nft_registry: dict[str, dict[str, Any]] = {}
        self.nft_market: list[dict[str, Any]] = []
        self.neighbors: list[NeighborColony] = [
            NeighborColony("Колония имени чужого дедлайна", attitude=-5, strength=25)
        ]
        self.campaign: list[Mission] = default_campaign()
        self.ai = TemplateAI(mode="off")
        self.ai_lines_generated = 0
        self.history: list[dict[str, float]] = []
        self.god_mode_enabled = False
        self.tui_speed = 1
        self.paused = False
        self.record_history()

    @property
    def food(self) -> int:
        return self.resources.get("food", 0)

    @food.setter
    def food(self, value: int) -> None:
        self.resources["food"] = max(0, int(value))

    def log(self, message: str) -> None:
        self.event_log.append(f"[TICK {self.time}] {message}")
        self.event_log = self.event_log[-80:]

    def get_alive_ants(self) -> list[Ant]:
        return [ant for ant in self.ants if ant.alive]

    def get_alive_ants_count(self) -> int:
        return len(self.get_alive_ants())

    def average_happiness(self) -> float:
        alive = self.get_alive_ants()
        if not alive:
            return 0.0
        return sum(ant.happiness for ant in alive) / len(alive)

    def average_stats(self) -> dict[str, float]:
        alive = self.get_alive_ants()
        if not alive:
            return {stat: 0.0 for stat in STAT_NAMES}
        return {
            stat: sum(ant.stats.get(stat, 0) for ant in alive) / len(alive)
            for stat in STAT_NAMES
        }

    def assign_ant_to_room(self, ant_index: int, room_id: str) -> bool:
        if ant_index < 0 or ant_index >= len(self.ants):
            return False
        ant = self.ants[ant_index]
        if not ant.alive or room_id not in self.rooms:
            return False

        room = self.rooms[room_id]
        if room.is_full or not room.enabled:
            return False

        for existing_room in self.rooms.values():
            existing_room.remove_ant(ant.id)
            existing_room.remove_ant(str(ant_index))

        if room.assign_ant(ant.id):
            ant.current_room = room_id
            ant.remember(f"назначен в комнату {room.name}")
            return True
        return False

    def mass_assign(self, status: str, room_id: str) -> int:
        assigned = 0
        for index, ant in enumerate(self.ants):
            if status in ant.statuses and self.assign_ant_to_room(index, room_id):
                assigned += 1
        return assigned

    def tick(self) -> None:
        self.time += 1
        if self.get_alive_ants_count() >= 100:
            self.rooms["server_room"].enabled = True

        for index, ant in enumerate(self.ants):
            if not ant.alive:
                continue
            ant.tick()
            if not ant.alive:
                self._move_to_cemetery(index, ant)
                continue
            if not self._consume_resources(ant):
                ant.suffer_hunger()
            else:
                ant.feed_successfully()
            self._apply_room_effect(index, ant)

        self._handle_dead_assignments()
        self._handle_birth()
        self._handle_events()
        self._maybe_spawn_event()
        self._market_session_if_needed()
        self._campaign_tick()
        self.record_history()

    def _consume_resources(self, ant: Ant) -> bool:
        needs = ant.resource_needs
        if AntStatus.FERMENTED in ant.statuses:
            needs = {k: max(1, v + (1 if k == "water" else 0)) for k, v in needs.items()}
        if any(self.resources.get(resource, 0) < amount for resource, amount in needs.items()):
            return False
        for resource, amount in needs.items():
            self.resources[resource] = max(0, self.resources.get(resource, 0) - amount)
        return True

    def _apply_room_effect(self, ant_index: int, ant: Ant) -> None:
        if not ant.current_room or ant.current_room not in self.rooms:
            return
        room = self.rooms[ant.current_room]
        for stat in ROOM_TRAIN_MAP.get(room.type, []):
            ant.train_stat(stat, 0.06)

        if room.type == "surface":
            gain = max(1, ant.stats.get("Б", 5) // 3)
            self.resources["food"] += gain
            if self.random.random() < 0.25:
                self.resources["protein"] += 1
        elif room.type == "food_storage":
            self.resources["food"] += 1 if ant.stats.get("Л", 5) >= 7 else 0
        elif room.type == "water_room":
            self.resources["water"] += 2
            ant.remove_status(AntStatus.SMELLY)
        elif room.type == "mushroom_startup":
            if self.resources.get("water", 0) > 0:
                self.resources["water"] -= 1
                self.mushroom_food += 2
                self.resources["food"] += 1
            else:
                self.mushroom_fungus_level += 1
        elif room.type == "server_room":
            self.antcoin += 0.2 + ant.stats.get("Д", 5) * 0.03
        elif room.type == "billiard_room":
            ant.play_billiards()
        elif room.type == "casino":
            self._casino_round(ant)
        elif room.type == "hammock_room":
            ant.happiness = min(100, ant.happiness + 3)
            ant.add_status(AntStatus.HAMMOCKED, duration=3)
        elif room.type == "rehab_cell":
            ant.remove_status(AntStatus.BILLIARD_MAIN)
            ant.remove_status(AntStatus.ADDICTED)
        elif room.type == "cue_armory":
            room.defense = min(50, room.defense + 1)
        elif room.type == "council_office":
            if AntStatus.OFFICIAL not in ant.statuses:
                ant.add_status(AntStatus.OFFICIAL)
            tax = max(0, int(sum(self.resources.values()) * 0.01))
            self.resources["food"] = max(0, self.resources["food"] - tax)
            if self.time > 100:
                ant.add_status(AntStatus.CORRUPTED)

    def _casino_round(self, ant: Ant) -> None:
        if self.random.random() < 0.45:
            self.resources["food"] += 3
            ant.happiness = min(100, ant.happiness + 4)
            ant.achievements.append("выиграл в казино имени кийка")
        else:
            self.resources["food"] = max(0, self.resources["food"] - 3)
            ant.happiness = max(0, ant.happiness - 2)
            if self.random.random() < 0.1:
                ant.add_status(AntStatus.BILLIARD_MAIN, duration=20)

    def _handle_dead_assignments(self) -> None:
        for index, ant in enumerate(self.ants):
            if not ant.alive or AntStatus.DEAD in ant.statuses:
                self._move_to_cemetery(index, ant)

    def _move_to_cemetery(self, index: int, ant: Ant) -> None:
        for room in self.rooms.values():
            room.remove_ant(ant.id)
            room.remove_ant(str(index))
        ant.current_room = "cemetery"
        self.rooms["cemetery"].assign_ant(ant.id)

    def _handle_birth(self) -> None:
        alive = self.get_alive_ants()
        if not alive or self.resources.get("food", 0) <= len(alive):
            return
        avg_birth_rate = sum(ant.birth_rate for ant in alive) / len(alive)
        nursery_bonus = len(self.rooms["nursery"].ant_ids) * 0.001
        birth_chance = avg_birth_rate / 120.0 + nursery_bonus
        if self.random.random() < birth_chance:
            new_ant = create_ant(self.ant_type)
            if self.random.random() < 0.5 and any(
                AntStatus.RADIATED in ant.statuses for ant in alive
            ):
                stat = self.random.choice(["Б", "И"])
                new_ant.stats[stat] = min(10, new_ant.stats[stat] + 2)
            self.ants.append(new_ant)
            self.resources["food"] = max(0, self.resources["food"] - 1)
            self.log(f"родился {new_ant.display_name}")

    def _handle_events(self) -> None:
        expired = []
        for event in self.active_events:
            self._apply_active_event(event)
            if event.tick():
                expired.append(event)
        for event in expired:
            self._resolve_event(event)
            self.active_events.remove(event)

    def _apply_active_event(self, event: RandomEvent) -> None:
        if event.type == "radiation":
            radiated = [
                ant for ant in self.get_alive_ants() if AntStatus.RADIATED in ant.statuses
            ]
            for ant in radiated[:2]:
                for target in self.random.sample(
                    self.get_alive_ants(), min(2, len(self.get_alive_ants()))
                ):
                    target.add_status(AntStatus.RADIATED, duration=15)
        elif event.type == "billiard_epidemic":
            for ant in self.get_alive_ants():
                if self.random.random() < 0.05:
                    ant.add_status(AntStatus.BILLIARD_MAIN, duration=20)

    def _resolve_event(self, event: RandomEvent) -> None:
        if event.type == "pheromone_death_spiral":
            for ant in self.get_alive_ants():
                if ant.stats.get("Д", 5) >= 7:
                    ant.train_stat("Д", 0.2)
        elif event.type == "smells_like_dead":
            for ant in self.get_alive_ants():
                if AntStatus.SMELLS_LIKE_DEAD in ant.statuses:
                    if self.random.random() < 0.6:
                        ant.remove_status(AntStatus.SMELLS_LIKE_DEAD)
                        ant.train_stat("Д", 1.0)
                    else:
                        self._move_to_cemetery(self.ants.index(ant), ant)
        elif event.type == "fermented_syrup":
            for ant in self.get_alive_ants():
                ant.remove_status(AntStatus.FERMENTED)
        elif event.type == "zombie_fungus":
            self.mushroom_fungus_level = max(0, self.mushroom_fungus_level - 1)
            for ant in self.get_alive_ants():
                if AntStatus.INFECTED in ant.statuses and self.random.random() < 0.5:
                    ant.remove_status(AntStatus.INFECTED)
        elif event.type == "billiard_addiction":
            for ant in self.get_alive_ants():
                if AntStatus.BILLIARD_MAIN in ant.statuses and self.random.random() < 0.3:
                    ant.remove_status(AntStatus.BILLIARD_MAIN)
        elif event.type == "ufo_abduction":
            self._return_enlightened_ants()

    def _maybe_spawn_event(self) -> None:
        checks = [
            (0.020, self.spawn_pheromone_death_spiral),
            (0.025, self.spawn_smells_like_dead),
            (0.018, self.spawn_fermented_syrup),
            (0.010, self.spawn_zombie_fungus),
            (0.015, self.spawn_billiard_addiction),
            (0.006, self.spawn_radiation),
            (0.004, self.spawn_ufo_abduction),
            (0.010, lambda: self.hold_voting("Провести бильярдный турнир")),
        ]
        for chance, spawn_fn in checks:
            if self.random.random() < chance:
                spawn_fn()
                break

    def _new_event(
        self, name: str, event_type: str, duration: int, description: str = ""
    ) -> RandomEvent:
        event = RandomEvent(str(uuid4()), name, event_type, duration, description)
        self.active_events.append(event)
        self.log(f"событие: {name}")
        return event

    def spawn_pheromone_death_spiral(self) -> RandomEvent:
        event = self._new_event(
            "Феромоновая смерть-спираль",
            "pheromone_death_spiral",
            5,
            "часть муравьев ходит по кругу как планерка без конца",
        )
        for ant in self.get_alive_ants():
            if ant.stats.get("Р", 5) < 5 and self.random.random() < 0.45:
                ant.current_room = None
                ant.remember("ходил по кругу и называл это маршрутизацией")
        return event

    def spawn_smells_like_dead(self) -> RandomEvent | None:
        alive = self.get_alive_ants()
        if not alive:
            return None
        target = self.random.choice(alive)
        target.add_status(AntStatus.SMELLS_LIKE_DEAD, duration=3)
        self._move_to_cemetery(self.ants.index(target), target)
        return self._new_event(
            "Он не умер, он просто пахнет",
            "smells_like_dead",
            3,
            f"{target.personal_name} унесен на кладбище авансом",
        )

    def spawn_fermented_syrup(self) -> RandomEvent:
        event = self._new_event("Забродивший сироп", "fermented_syrup", 4)
        for ant in self.get_alive_ants():
            chance = 0.45 if ant.ant_type_name == "RedReactiveAnt" else 0.1
            if self.random.random() < chance:
                ant.add_status(AntStatus.FERMENTED, duration=4)
        return event

    def spawn_zombie_fungus(self) -> RandomEvent | None:
        if self.mushroom_fungus_level < 3 and self.random.random() > 0.2:
            return None
        event = self._new_event("Зомби-гриб", "zombie_fungus", 6)
        alive = self.get_alive_ants()
        if alive:
            self.random.choice(alive).add_status(AntStatus.INFECTED, duration=6)
        return event

    def spawn_billiard_addiction(self) -> RandomEvent:
        event = self._new_event("Бильярдная зависимость", "billiard_addiction", 5)
        billiard_ids = set(self.rooms["billiard_room"].ant_ids + self.rooms["casino"].ant_ids)
        for ant in self.get_alive_ants():
            if ant.id in billiard_ids or ant.stats.get("И", 5) < 4:
                if self.random.random() < 0.35:
                    ant.add_status(AntStatus.BILLIARD_MAIN, duration=20)
        return event

    def spawn_radiation(self) -> RandomEvent | None:
        alive = self.get_alive_ants()
        if not alive:
            return None
        target = self.random.choice(alive)
        target.add_status(AntStatus.RADIATED, duration=15)
        stat = self.random.choice(STAT_NAMES)
        target.stats[stat] = min(10, target.stats[stat] + 3)
        return self._new_event("Радиационная семечка", "radiation", 10)

    def spawn_ufo_abduction(self) -> RandomEvent | None:
        alive = self.get_alive_ants()
        if len(alive) < 5:
            return None
        for ant in self.random.sample(alive, 5):
            ant.add_status(AntStatus.ABDUCTED, duration=50)
            ant.alive = False
        return self._new_event("НЛО над муравейником", "ufo_abduction", 50)

    def _return_enlightened_ants(self) -> None:
        abducted = [
            ant for ant in self.ants if AntStatus.ABDUCTED in ant.statuses
        ][:3]
        for ant in abducted:
            ant.alive = True
            ant.remove_status(AntStatus.ABDUCTED)
            ant.add_status(AntStatus.ENLIGHTENED)
            for stat in STAT_NAMES:
                ant.stats[stat] = min(10, ant.stats.get(stat, 5) + 2)
            ant.remember("вернулся из НЛО и теперь всё понимает хуже")

    def hold_voting(self, issue: str) -> VotingResult:
        alive = self.get_alive_ants()
        result = VotingResult()
        result.issue = issue
        if not alive:
            self.last_voting = result
            return result

        queen_factor = self.average_stats().get("Я", 5) / 10.0
        for ant in alive:
            roll = self.random.random()
            if AntStatus.FERMENTED in ant.statuses:
                roll = self.random.random()
            if roll < 0.35 - queen_factor * 0.08:
                result.for_count += 1
            elif roll < 0.82:
                result.against_count += 1
            elif roll < 0.95:
                result.abstain_count += 1
            else:
                result.lost_count += 1

        result.percentages = {
            "за": self.random.randint(12, 67),
            "против": self.random.randint(20, 78),
            "воздержались": self.random.randint(0, 31),
            "потерялись": self.random.randint(1, 17),
        }
        result.queen_overridden = self.random.random() < 0.35 or queen_factor > 0.7
        if result.queen_overridden:
            result.final_decision = "матка уточнила: принято"
        elif result.for_count > result.against_count:
            result.final_decision = "принято"
        else:
            result.final_decision = "отклонено, но не факт"
        self.last_voting = result
        self.log(f"голосование: {issue} -> {result.final_decision}")
        self._mission_progress("votes", 1)
        return result

    def _market_session_if_needed(self) -> None:
        if self.time % 10 != 0:
            return
        self.market_rates = {
            name: max(0.2, value + self.random.uniform(-0.15, 0.15))
            for name, value in self.market_rates.items()
        }
        self.btc_price = max(1000.0, self.btc_price + self.random.uniform(-900, 900))
        self.ant_price = self.btc_price * 0.0000001 * self.random.uniform(0.7, 1.5)
        if self.random.random() < 0.08:
            self.log(self.ai.event_text(self.summary(), self.time))
            self.ai_lines_generated += 1
            self._mission_progress("ai_lines", 1)

    def trade_with_neighbor(self, neighbor_index: int, resource: str, amount: int) -> bool:
        if neighbor_index < 0 or neighbor_index >= len(self.neighbors):
            return False
        if resource not in self.resources or self.resources[resource] < amount:
            return False
        neighbor = self.neighbors[neighbor_index]
        self.resources[resource] -= amount
        self.resources["food"] += max(1, amount // 2)
        neighbor.attitude += 2
        neighbor.last_action = f"торговля ресурсом {resource}"
        self.log(f"торговля с {neighbor.name}: {resource} x{amount}")
        self._mission_progress("diplomacy", 1)
        return True

    def attack_neighbor(self, neighbor_index: int) -> str:
        if neighbor_index < 0 or neighbor_index >= len(self.neighbors):
            return "нет такой соседней колонии"
        neighbor = self.neighbors[neighbor_index]
        our_strength = sum(
            ant.stats.get("Л", 0) + ant.stats.get("Д", 0)
            for ant in self.get_alive_ants()
            if ant.role in {"soldier", "worker"}
        )
        if our_strength >= neighbor.strength:
            loot = min(50, neighbor.resources.get("food", 0) if neighbor.resources else 0)
            self.resources["food"] += loot
            if neighbor.resources:
                neighbor.resources["food"] = max(0, neighbor.resources.get("food", 0) - loot)
            neighbor.attitude -= 20
            neighbor.last_action = "получила по феромонам"
            result = f"победа, добыто {loot} еды"
        else:
            for ant in self.random.sample(
                self.get_alive_ants(), min(3, len(self.get_alive_ants()))
            ):
                ant.add_status(AntStatus.INJURED, duration=5)
            neighbor.attitude -= 10
            result = "поражение, трое сделали вид что это разведка"
        self.log(f"война с {neighbor.name}: {result}")
        self._mission_progress("diplomacy", 1)
        return result

    def mine_antcoin(self, amount: float | None = None) -> float:
        if amount is None:
            amount = max(0.1, len(self.rooms["server_room"].ant_ids) * 0.25)
        self.antcoin += amount
        self._mission_progress("antcoin", int(self.antcoin))
        return self.antcoin

    def mint_nft(self, ant_index: int, price: float = 50.0) -> str | None:
        if ant_index < 0 or ant_index >= len(self.ants):
            return None
        if self.antcoin < price:
            return None
        ant = self.ants[ant_index]
        nft_id = f"ANTNFT-{len(self.nft_registry) + 1:04d}"
        self.antcoin -= price
        ant.nft_id = nft_id
        ant.add_status(AntStatus.NFT)
        for stat in STAT_NAMES:
            ant.stats[stat] = min(10, ant.stats.get(stat, 5) + 1)
        metadata = {
            "id": nft_id,
            "ant_id": ant.id,
            "name": ant.display_name,
            "price": price,
            "story": self.ai.epitaph(ant.display_name, "инвестиция", self.time),
            "listed": False,
        }
        self.nft_registry[nft_id] = metadata
        self.log(f"отчеканен {nft_id} для {ant.personal_name}")
        self._mission_progress("nft", 1)
        return nft_id

    def list_nft_for_sale(self, nft_id: str, price: float) -> bool:
        if nft_id not in self.nft_registry:
            return False
        item = dict(self.nft_registry[nft_id])
        item["price"] = price
        item["listed"] = True
        self.nft_registry[nft_id]["listed"] = True
        self.nft_market.append(item)
        return True

    def buy_first_nft(self) -> bool:
        if not self.nft_market:
            return False
        item = self.nft_market[0]
        price = float(item["price"])
        if self.antcoin < price:
            return False
        self.antcoin -= price
        self.nft_market.pop(0)
        self.log(f"куплен чужой JPEG {item['id']}")
        return True

    def god_mode(self, action: str, **kwargs: Any) -> str:
        self.god_mode_enabled = True
        if action == "set_resource":
            resource = str(kwargs.get("resource", "food"))
            amount = int(kwargs.get("amount", 0))
            if resource in self.resources:
                self.resources[resource] = max(0, amount)
                return f"{resource} = {amount}"
            return "неизвестный ресурс"
        if action == "balagan":
            for ant in self.get_alive_ants():
                ant.add_status(AntStatus.FERMENTED, duration=20)
                ant.add_status(AntStatus.BILLIARD_MAIN, duration=20)
            return "режим балагана включен"
        if action == "spawn_event":
            event_type = str(kwargs.get("event_type", "pheromone"))
            return self.force_event(event_type)
        if action == "add_ants":
            amount = int(kwargs.get("amount", 1))
            for _ in range(max(0, amount)):
                self.ants.append(create_ant(self.ant_type))
            return f"добавлено {amount} муравьев"
        if action == "pest":
            for ant in self.random.sample(
                self.get_alive_ants(), min(2, len(self.get_alive_ants()))
            ):
                ant.add_status(AntStatus.INJURED, duration=5)
            return "вредитель пришел, сказал что он ревьюер"
        return "бог нажал не ту кнопку"

    def force_event(self, event_type: str) -> str:
        mapping = {
            "pheromone": self.spawn_pheromone_death_spiral,
            "smell": self.spawn_smells_like_dead,
            "fermented": self.spawn_fermented_syrup,
            "fungus": self.spawn_zombie_fungus,
            "billiard": self.spawn_billiard_addiction,
            "radiation": self.spawn_radiation,
            "ufo": self.spawn_ufo_abduction,
        }
        fn = mapping.get(event_type)
        if not fn:
            return "нет такого события"
        event = fn()
        return event.name if event else "событие отказалось приходить"

    def ai_queen_dialog(self, question: str) -> str:
        self.ai_lines_generated += 1
        self._mission_progress("ai_lines", 1)
        return self.ai.queen_dialog(question, self.time)

    def _campaign_tick(self) -> None:
        self._mission_progress("ticks", self.time)
        self._mission_progress("rooms", sum(1 for room in self.rooms.values() if room.enabled))
        self._mission_progress("antcoin", int(self.antcoin))
        self._mission_progress("mushroom_food", self.mushroom_food)
        self._mission_progress("nft", len(self.nft_registry))
        self._mission_progress("ai_lines", self.ai_lines_generated)

    def _mission_progress(self, key: str, value: int) -> None:
        for mission in self.campaign:
            if mission.completed or key not in mission.goals:
                continue
            mission.progress[key] = max(int(mission.progress.get(key, 0)), value)
            if all(
                int(mission.progress.get(goal, 0)) >= required
                for goal, required in mission.goals.items()
            ):
                mission.completed = True
                self.log(f"миссия выполнена: {mission.title} -> {mission.reward}")

    def record_history(self) -> None:
        self.history.append(
            {
                "time": float(self.time),
                "population": float(self.get_alive_ants_count()),
                "food": float(self.resources.get("food", 0)),
                "protein": float(self.resources.get("protein", 0)),
                "water": float(self.resources.get("water", 0)),
                "antcoin": float(self.antcoin),
                "happiness": float(self.average_happiness()),
            }
        )
        self.history = self.history[-300:]

    def summary(self) -> str:
        return (
            f"{self.id}: t={self.time}, ants={self.get_alive_ants_count()}, "
            f"food={self.resources.get('food', 0)}, ANT={self.antcoin:.1f}"
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "time": self.time,
            "ant_type": self.ant_type,
            "population": self.get_alive_ants_count(),
            "total_ants": len(self.ants),
            "resources": dict(self.resources),
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "active_events": [e.to_dict() for e in self.active_events],
            "last_voting": self.last_voting.to_dict() if self.last_voting else None,
            "antcoin": self.antcoin,
            "ant_price": self.ant_price,
            "btc_price": self.btc_price,
            "nft_count": len(self.nft_registry),
            "average_stats": self.average_stats(),
            "average_happiness": self.average_happiness(),
            "history": list(self.history),
            "event_log": list(self.event_log),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "save_version": self.save_version,
            "id": self.id,
            "food": self.food,
            "time": self.time,
            "ant_type": self.ant_type,
            "ants": [ant.to_dict() for ant in self.ants],
            "resources": dict(self.resources),
            "rooms": {k: v.to_dict() for k, v in self.rooms.items()},
            "active_events": [event.to_dict() for event in self.active_events],
            "event_log": list(self.event_log),
            "last_voting": self.last_voting.to_dict() if self.last_voting else None,
            "queen_morale": self.queen_morale,
            "mushroom_fungus_level": self.mushroom_fungus_level,
            "mushroom_food": self.mushroom_food,
            "market_rates": dict(self.market_rates),
            "antcoin": self.antcoin,
            "antcoin_classic": self.antcoin_classic,
            "btc_price": self.btc_price,
            "ant_price": self.ant_price,
            "nft_registry": dict(self.nft_registry),
            "nft_market": list(self.nft_market),
            "neighbors": [neighbor.to_dict() for neighbor in self.neighbors],
            "campaign": [mission.to_dict() for mission in self.campaign],
            "ai": {
                "mode": self.ai.mode,
                "tokens_spent": self.ai.tokens_spent,
                "cache": dict(self.ai.cache),
            },
            "ai_lines_generated": self.ai_lines_generated,
            "history": list(self.history),
            "god_mode_enabled": self.god_mode_enabled,
            "tui_speed": self.tui_speed,
            "paused": self.paused,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Colony":
        ant_type = normalize_ant_type(data.get("ant_type", "Harvester"))
        food = int(data.get("food", data.get("resources", {}).get("food", 0)))
        colony = cls(data["id"], 0, food, ant_type)
        colony.time = int(data.get("time", 0))
        colony.ants = [ant_from_dict(ant_data) for ant_data in data.get("ants", [])]
        resources = data.get("resources")
        if resources:
            colony.resources = {str(k): int(v) for k, v in resources.items()}
            for name in RESOURCE_NAMES:
                colony.resources.setdefault(name, 0)
        else:
            colony.resources = {
                "food": int(data.get("food", 0)),
                "protein": max(len(colony.ants) * 2, 10),
                "water": max(len(colony.ants) * 2, 10),
            }
        if "rooms" in data:
            colony.rooms = {k: Room.from_dict(v) for k, v in data["rooms"].items()}
            for room_id, room in create_default_rooms().items():
                colony.rooms.setdefault(room_id, room)
        if "active_events" in data:
            colony.active_events = [
                RandomEvent.from_dict(event) for event in data["active_events"]
            ]
        colony.event_log = list(data.get("event_log", []))
        if data.get("last_voting"):
            colony.last_voting = VotingResult.from_dict(data["last_voting"])
        colony.queen_morale = int(data.get("queen_morale", 50))
        colony.mushroom_fungus_level = int(data.get("mushroom_fungus_level", 0))
        colony.mushroom_food = int(data.get("mushroom_food", 0))
        colony.market_rates = {
            str(k): float(v) for k, v in data.get("market_rates", colony.market_rates).items()
        }
        colony.antcoin = float(data.get("antcoin", 0.0))
        colony.antcoin_classic = float(data.get("antcoin_classic", 0.0))
        colony.btc_price = float(data.get("btc_price", 69420.0))
        colony.ant_price = float(data.get("ant_price", colony.btc_price * 0.0000001))
        colony.nft_registry = dict(data.get("nft_registry", {}))
        colony.nft_market = list(data.get("nft_market", []))
        colony.neighbors = [
            NeighborColony.from_dict(neighbor)
            for neighbor in data.get("neighbors", [n.to_dict() for n in colony.neighbors])
        ]
        if "campaign" in data:
            colony.campaign = [Mission.from_dict(item) for item in data["campaign"]]
        ai_data = data.get("ai", {})
        colony.ai = TemplateAI(mode=ai_data.get("mode", "off"))
        colony.ai.tokens_spent = int(ai_data.get("tokens_spent", 0))
        colony.ai.cache = dict(ai_data.get("cache", {}))
        colony.ai_lines_generated = int(data.get("ai_lines_generated", 0))
        colony.history = list(data.get("history", []))
        colony.god_mode_enabled = bool(data.get("god_mode_enabled", False))
        colony.tui_speed = int(data.get("tui_speed", 1))
        colony.paused = bool(data.get("paused", False))
        if not colony.history:
            colony.record_history()
        return colony
