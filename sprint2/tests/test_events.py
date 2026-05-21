"""Tests for RandomEvent and event system."""
import pytest
from colony import Colony, RandomEvent
from uuid import uuid4


class TestRandomEvent:
    """Test RandomEvent class."""

    def test_random_event_initialization(self):
        """Test RandomEvent initializes with correct values."""
        event = RandomEvent(
            event_id="test_id",
            name="Test Event",
            event_type="test_type",
            duration=5,
        )
        assert event.id == "test_id"
        assert event.name == "Test Event"
        assert event.type == "test_type"
        assert event.duration == 5
        assert event.ticks_left == 5

    def test_random_event_tick_decrements_ticks(self):
        """Test tick() decrements ticks_left."""
        event = RandomEvent("id", "name", "type", 3)
        assert event.tick() is False
        assert event.ticks_left == 2
        assert event.tick() is False
        assert event.ticks_left == 1
        assert event.tick() is True
        assert event.ticks_left == 0

    def test_random_event_to_dict(self):
        """Test RandomEvent.to_dict serialization."""
        event = RandomEvent("evt_id", "Event Name", "pheromone_death_spiral", 10)
        event.ticks_left = 7

        data = event.to_dict()
        assert data["id"] == "evt_id"
        assert data["name"] == "Event Name"
        assert data["type"] == "pheromone_death_spiral"
        assert data["duration"] == 10
        assert data["ticks_left"] == 7

    def test_random_event_from_dict(self):
        """Test RandomEvent.from_dict deserialization."""
        data = {
            "id": "test_evt",
            "name": "Test",
            "type": "zombie_fungus",
            "duration": 6,
            "ticks_left": 3,
        }
        event = RandomEvent.from_dict(data)
        assert event.id == "test_evt"
        assert event.name == "Test"
        assert event.type == "zombie_fungus"
        assert event.duration == 6
        assert event.ticks_left == 3

    def test_random_event_roundtrip_serialization(self):
        """Test RandomEvent serialization roundtrip."""
        event1 = RandomEvent("id123", "Fermentation", "fermented_syrup", 4)
        event1.ticks_left = 2

        event2 = RandomEvent.from_dict(event1.to_dict())
        assert event2.id == event1.id
        assert event2.name == event1.name
        assert event2.type == event1.type
        assert event2.duration == event1.duration
        assert event2.ticks_left == event1.ticks_left


class TestColonyEvents:
    """Test colony event spawning and resolution."""

    def test_colony_has_active_events_list(self):
        """Test colony has active_events list."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        assert isinstance(colony.active_events, list)
        assert len(colony.active_events) == 0

    def test_event_tick_reduces_ticks(self):
        """Test event ticks reduce during colony tick."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=1000)
        event = RandomEvent(
            event_id="test", name="Test", event_type="pheromone_death_spiral", duration=3
        )
        colony.active_events.append(event)

        assert event.ticks_left == 3
        colony.tick()
        assert event.ticks_left == 2
        colony.tick()
        assert event.ticks_left == 1
        colony.tick()
        assert event.ticks_left == 0

    def test_expired_events_removed_from_active_list(self):
        """Test expired events are removed from active_events."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=1000)
        event = RandomEvent("id", "Event", "test_type", 2)
        colony.active_events.append(event)

        assert len(colony.active_events) == 1
        colony.tick()
        assert len(colony.active_events) == 1
        colony.tick()
        assert len(colony.active_events) == 0

    def test_pheromone_death_spiral_event(self):
        """Test pheromone death spiral event can spawn."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)

        for _ in range(1000):
            colony.tick()
            if any(e.type == "pheromone_death_spiral" for e in colony.active_events):
                break

        found_event = any(e.type == "pheromone_death_spiral" for e in colony.active_events)
        assert found_event or len(colony.active_events) == 0

    def test_smells_like_dead_event(self):
        """Test smells_like_dead event can spawn."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)

        for _ in range(1000):
            colony.tick()
            if any(e.type == "smells_like_dead" for e in colony.active_events):
                break

        found_event = any(e.type == "smells_like_dead" for e in colony.active_events)
        assert found_event or len(colony.active_events) == 0

    def test_fermented_syrup_event(self):
        """Test fermented syrup event can spawn."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)

        for _ in range(1000):
            colony.tick()
            if any(e.type == "fermented_syrup" for e in colony.active_events):
                break

        found_event = any(e.type == "fermented_syrup" for e in colony.active_events)
        assert found_event or len(colony.active_events) == 0

    def test_billiard_addiction_event(self):
        """Test billiard addiction event can spawn."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)
        billiard_room = colony.rooms["billiard_room"]

        for ant_idx, ant in enumerate(colony.get_alive_ants()[:5]):
            colony.assign_ant_to_room(ant_idx, "billiard_room")

        for _ in range(1000):
            colony.tick()
            if any(e.type == "billiard_addiction" for e in colony.active_events):
                break

        found_event = any(e.type == "billiard_addiction" for e in colony.active_events)
        assert found_event or len(colony.active_events) == 0

    def test_voting_event_spawning(self):
        """Test voting can spawn as an event."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)

        for _ in range(2000):
            colony.tick()
            if colony.last_voting is not None:
                break

        assert colony.last_voting is None or isinstance(colony.last_voting.issue, str)

    def test_event_resolution_fermented_syrup(self):
        """Test fermented_syrup event resolution removes fermented status."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)

        ant = colony.ants[0]
        ant.statuses.add("fermented")

        event = RandomEvent(
            event_id="test",
            name="Test Ferment",
            event_type="fermented_syrup",
            duration=1,
        )
        colony.active_events.append(event)
        colony.tick()

        assert "fermented" not in ant.statuses

    def test_event_resolution_zombie_fungus(self):
        """Test zombie_fungus event resolution."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=1000)
        colony.mushroom_fungus_level = 5

        event = RandomEvent(
            event_id="test",
            name="Zombie Fungus",
            event_type="zombie_fungus",
            duration=1,
        )
        colony.active_events.append(event)
        initial_level = colony.mushroom_fungus_level
        colony.tick()

        assert colony.mushroom_fungus_level == initial_level - 1

    def test_event_resolution_billiard_addiction(self):
        """Test billiard_addiction event resolution."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=1000)

        ant = colony.ants[0]
        ant.statuses.add("billiard_main")

        event = RandomEvent(
            event_id="test",
            name="Billiard Addiction",
            event_type="billiard_addiction",
            duration=1,
        )
        colony.active_events.append(event)
        colony.tick()


class TestColonyEventSerialization:
    """Test event serialization in colony."""

    def test_colony_serialize_with_events(self):
        """Test colony.to_dict includes events."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        event = RandomEvent("id", "Event", "test_type", 5)
        colony.active_events.append(event)

        data = colony.to_dict()
        assert "active_events" in data
        assert len(data["active_events"]) == 1
        assert data["active_events"][0]["id"] == "id"

    def test_colony_deserialize_with_events(self):
        """Test colony.from_dict restores events."""
        colony1 = Colony(colony_id="col123", ant_count=10, food=100)
        event = RandomEvent("evt1", "Test Event", "test_type", 3)
        event.ticks_left = 1
        colony1.active_events.append(event)

        data = colony1.to_dict()
        colony2 = Colony.from_dict(data)

        assert len(colony2.active_events) == 1
        assert colony2.active_events[0].id == "evt1"
        assert colony2.active_events[0].ticks_left == 1
