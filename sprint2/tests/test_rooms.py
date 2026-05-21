"""Tests for room system."""
import pytest
from rooms import Room, create_default_rooms, ROOM_TRAIN_MAP


class TestRoom:
    """Test Room class."""

    def test_room_initialization(self):
        """Test Room initializes correctly."""
        room = Room(
            room_id="food_storage",
            name="Склад пищи",
            capacity=50,
            room_type="food_storage",
        )
        assert room.id == "food_storage"
        assert room.name == "Склад пищи"
        assert room.capacity == 50
        assert room.type == "food_storage"
        assert room.ant_ids == []

    def test_room_is_full_initially_false(self):
        """Test room is not full initially."""
        room = Room("id", "name", 10, "type")
        assert room.is_full is False

    def test_room_is_full_when_capacity_reached(self):
        """Test room is_full is True at capacity."""
        room = Room("id", "name", 2, "type")
        room.assign_ant("ant1")
        assert room.is_full is False
        room.assign_ant("ant2")
        assert room.is_full is True

    def test_room_assign_ant_returns_true(self):
        """Test assign_ant returns True when successful."""
        room = Room("id", "name", 5, "type")
        result = room.assign_ant("ant_id")
        assert result is True
        assert "ant_id" in room.ant_ids

    def test_room_assign_ant_returns_false_when_full(self):
        """Test assign_ant returns False when room is full."""
        room = Room("id", "name", 1, "type")
        room.assign_ant("ant1")
        result = room.assign_ant("ant2")
        assert result is False
        assert "ant2" not in room.ant_ids

    def test_room_remove_ant_returns_true(self):
        """Test remove_ant returns True when successful."""
        room = Room("id", "name", 5, "type")
        room.assign_ant("ant_id")
        result = room.remove_ant("ant_id")
        assert result is True
        assert "ant_id" not in room.ant_ids

    def test_room_remove_ant_returns_false_if_not_found(self):
        """Test remove_ant returns False if ant not in room."""
        room = Room("id", "name", 5, "type")
        result = room.remove_ant("nonexistent")
        assert result is False

    def test_room_to_dict(self):
        """Test room.to_dict serialization."""
        room = Room("room1", "Test Room", 10, "test_type")
        room.assign_ant("ant1")
        room.assign_ant("ant2")
        room.extra["key"] = "value"

        data = room.to_dict()
        assert data["id"] == "room1"
        assert data["name"] == "Test Room"
        assert data["capacity"] == 10
        assert data["type"] == "test_type"
        assert data["ant_ids"] == ["ant1", "ant2"]
        assert data["extra"]["key"] == "value"

    def test_room_from_dict(self):
        """Test room.from_dict deserialization."""
        data = {
            "id": "room2",
            "name": "Another Room",
            "capacity": 15,
            "type": "another_type",
            "ant_ids": ["ant_a", "ant_b"],
            "extra": {"setting": "value"},
        }
        room = Room.from_dict(data)
        assert room.id == "room2"
        assert room.name == "Another Room"
        assert room.capacity == 15
        assert room.type == "another_type"
        assert room.ant_ids == ["ant_a", "ant_b"]
        assert room.extra["setting"] == "value"

    def test_room_roundtrip_serialization(self):
        """Test Room serialization roundtrip."""
        room1 = Room("id3", "Room 3", 20, "type3")
        room1.assign_ant("ant_x")
        room1.extra["config"] = {"nested": "data"}

        room2 = Room.from_dict(room1.to_dict())
        assert room2.id == room1.id
        assert room2.name == room1.name
        assert room2.capacity == room1.capacity
        assert room2.type == room1.type
        assert room2.ant_ids == room1.ant_ids
        assert room2.extra == room1.extra


class TestDefaultRooms:
    """Test create_default_rooms function."""

    def test_create_default_rooms_returns_dict(self):
        """Test create_default_rooms returns dictionary."""
        rooms = create_default_rooms()
        assert isinstance(rooms, dict)

    def test_all_required_rooms_exist(self):
        """Test all required room types are created."""
        rooms = create_default_rooms()
        required_rooms = [
            "food_storage",
            "cemetery",
            "royal_chamber",
            "billiard_room",
            "soft_sign_room",
            "pheromone_circle",
            "mushroom_startup",
            "voting_room",
            "surface",
        ]
        for room_id in required_rooms:
            assert room_id in rooms

    def test_food_storage_room_properties(self):
        """Test food_storage room has correct properties."""
        rooms = create_default_rooms()
        room = rooms["food_storage"]
        assert room.id == "food_storage"
        assert room.type == "food_storage"
        assert room.capacity == 50

    def test_cemetery_room_properties(self):
        """Test cemetery room has correct properties."""
        rooms = create_default_rooms()
        room = rooms["cemetery"]
        assert room.id == "cemetery"
        assert room.type == "cemetery"
        assert room.capacity == 30

    def test_royal_chamber_room_properties(self):
        """Test royal_chamber room has correct properties."""
        rooms = create_default_rooms()
        room = rooms["royal_chamber"]
        assert room.id == "royal_chamber"
        assert room.capacity == 10

    def test_billiard_room_room_properties(self):
        """Test billiard_room has correct properties."""
        rooms = create_default_rooms()
        room = rooms["billiard_room"]
        assert room.id == "billiard_room"
        assert room.capacity == 20

    def test_surface_room_large_capacity(self):
        """Test surface room has large capacity."""
        rooms = create_default_rooms()
        room = rooms["surface"]
        assert room.capacity == 200


class TestRoomTrainMap:
    """Test ROOM_TRAIN_MAP."""

    def test_room_train_map_is_dict(self):
        """Test ROOM_TRAIN_MAP is dictionary."""
        assert isinstance(ROOM_TRAIN_MAP, dict)

    def test_food_storage_trains_stats(self):
        """Test food_storage trains Б and Л."""
        assert "Б" in ROOM_TRAIN_MAP["food_storage"]
        assert "Л" in ROOM_TRAIN_MAP["food_storage"]

    def test_billiard_room_trains_и(self):
        """Test billiard_room trains И."""
        assert "И" in ROOM_TRAIN_MAP["billiard_room"]

    def test_soft_sign_room_trains_ь(self):
        """Test soft_sign_room trains Ь."""
        assert "Ь" in ROOM_TRAIN_MAP["soft_sign_room"]

    def test_pheromone_circle_trains_р(self):
        """Test pheromone_circle trains Р."""
        assert "Р" in ROOM_TRAIN_MAP["pheromone_circle"]

    def test_mushroom_startup_trains_д(self):
        """Test mushroom_startup trains Д."""
        assert "Д" in ROOM_TRAIN_MAP["mushroom_startup"]

    def test_royal_chamber_trains_я(self):
        """Test royal_chamber trains Я."""
        assert "Я" in ROOM_TRAIN_MAP["royal_chamber"]

    def test_cemetery_no_training(self):
        """Test cemetery does not train any stats."""
        assert ROOM_TRAIN_MAP["cemetery"] == []

    def test_voting_room_no_training(self):
        """Test voting_room does not train stats."""
        assert ROOM_TRAIN_MAP["voting_room"] == []

    def test_surface_trains_б(self):
        """Test surface trains Б."""
        assert "Б" in ROOM_TRAIN_MAP["surface"]


class TestRoomEdgeCases:
    """Test edge cases for rooms."""

    def test_multiple_ants_in_room(self):
        """Test multiple ants can be in same room."""
        room = Room("id", "name", 5, "type")
        for i in range(5):
            assert room.assign_ant(f"ant{i}") is True

        assert len(room.ant_ids) == 5

    def test_remove_same_ant_twice(self):
        """Test removing same ant twice returns False second time."""
        room = Room("id", "name", 5, "type")
        room.assign_ant("ant1")
        assert room.remove_ant("ant1") is True
        assert room.remove_ant("ant1") is False

    def test_room_capacity_zero(self):
        """Test room with zero capacity."""
        room = Room("id", "name", 0, "type")
        assert room.is_full is True
        assert room.assign_ant("ant1") is False

    def test_room_with_extra_data(self):
        """Test room extra data persistence."""
        room = Room("id", "name", 10, "type")
        room.extra["custom_key"] = "custom_value"
        assert room.extra["custom_key"] == "custom_value"

        data = room.to_dict()
        room2 = Room.from_dict(data)
        assert room2.extra["custom_key"] == "custom_value"
