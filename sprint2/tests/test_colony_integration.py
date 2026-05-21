"""Tests for colony integration and complex scenarios."""
import pytest
from colony import Colony, AntStatus
from uuid import uuid4
from ants import Harvester, RedReactiveAnt


class TestColonyRoomAssignment:
    """Test ant assignment to rooms."""

    def test_assign_ant_to_valid_room(self):
        """Test assigning ant to valid room."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        result = colony.assign_ant_to_room(0, "food_storage")
        assert result is True
        assert colony.ants[0].current_room == "food_storage"

    def test_assign_ant_invalid_ant_index(self):
        """Test assigning with invalid ant index."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        result = colony.assign_ant_to_room(10, "food_storage")
        assert result is False

    def test_assign_ant_negative_index(self):
        """Test assigning with negative ant index."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        result = colony.assign_ant_to_room(-1, "food_storage")
        assert result is False

    def test_assign_dead_ant_fails(self):
        """Test assigning dead ant fails."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        colony.ants[0].alive = False
        result = colony.assign_ant_to_room(0, "food_storage")
        assert result is False

    def test_assign_ant_invalid_room(self):
        """Test assigning to invalid room."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        result = colony.assign_ant_to_room(0, "nonexistent_room")
        assert result is False

    def test_assign_ant_removes_from_previous_room(self):
        """Test assigning ant removes it from previous room."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        colony.assign_ant_to_room(0, "food_storage")
        food_room = colony.rooms["food_storage"]
        assert "0" in food_room.ant_ids

        colony.assign_ant_to_room(0, "cemetery")
        assert "0" not in food_room.ant_ids
        assert "0" in colony.rooms["cemetery"].ant_ids

    def test_assign_multiple_ants_same_room(self):
        """Test assigning multiple ants to same room."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=200)
        for i in range(5):
            result = colony.assign_ant_to_room(i, "food_storage")
            assert result is True

        food_room = colony.rooms["food_storage"]
        assert len(food_room.ant_ids) == 5

    def test_assign_ant_room_full_returns_false(self):
        """Test assignment fails when room is full."""
        colony = Colony(colony_id=str(uuid4()), ant_count=20, food=500)
        room = colony.rooms["soft_sign_room"]

        for i in range(room.capacity):
            result = colony.assign_ant_to_room(i, "soft_sign_room")
            assert result is True

        result = colony.assign_ant_to_room(room.capacity, "soft_sign_room")
        assert result is False


class TestColonyTickMechanics:
    """Test colony tick mechanics."""

    def test_colony_tick_increases_time(self):
        """Test tick increments colony time."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        assert colony.time == 0
        colony.tick()
        assert colony.time == 1
        colony.tick()
        assert colony.time == 2

    def test_colony_tick_ages_ants(self):
        """Test tick ages all alive ants."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        ant = colony.ants[0]
        assert ant.age == 0
        colony.tick()
        assert ant.age == 1

    def test_colony_tick_consumes_food(self):
        """Test tick consumes food based on ants."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=100)
        initial_food = colony.food
        colony.tick()
        consumed = initial_food - colony.food
        expected = sum(ant.food_per_tick for ant in colony.get_alive_ants())
        assert consumed == expected

    def test_colony_tick_food_cannot_go_negative(self):
        """Test food is clamped to 0."""
        colony = Colony(colony_id=str(uuid4()), ant_count=100, food=10)
        colony.tick()
        assert colony.food >= 0

    def test_colony_tick_kills_old_ants(self):
        """Test ants die when reaching life period."""
        colony = Colony(colony_id=str(uuid4()), ant_count=1, food=1000)
        ant = colony.ants[0]
        life_period = ant.life_period

        for _ in range(life_period):
            colony.tick()
            assert ant.alive

        colony.tick()
        assert not ant.alive

    def test_colony_get_alive_ants_count(self):
        """Test get_alive_ants_count is accurate."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=1000)
        assert colony.get_alive_ants_count() == 10

        colony.ants[0].alive = False
        assert colony.get_alive_ants_count() == 9

    def test_colony_get_alive_ants_returns_list(self):
        """Test get_alive_ants returns list of alive ants."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=1000)
        alive = colony.get_alive_ants()
        assert len(alive) == 10
        assert all(ant.alive for ant in alive)


class TestColonyBirth:
    """Test ant birth mechanics."""

    def test_colony_birth_requires_food(self):
        """Test birth requires available food."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=0)
        initial_count = len(colony.ants)

        for _ in range(100):
            colony.tick()

        assert len(colony.ants) == initial_count

    def test_colony_birth_creates_same_type(self):
        """Test born ants are same type as colony."""
        colony = Colony(
            colony_id=str(uuid4()), ant_count=5, food=5000, ant_type="RedReactiveAnt"
        )
        initial_type = colony.ants[0].ant_type_name

        for _ in range(5000):
            colony.tick()
            if len(colony.ants) > 5:
                break

        for ant in colony.ants:
            assert ant.ant_type_name == initial_type


class TestColonyStatTraining:
    """Test stat training during colony work."""

    def test_ant_trains_stat_in_room(self):
        """Test ant assigned to room trains corresponding stats."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=1000)
        ant = colony.ants[0]
        initial_progress = ant.stat_progress["Б"]

        colony.assign_ant_to_room(0, "food_storage")
        colony.tick()

        assert ant.stat_progress["Б"] > initial_progress

    def test_multiple_stats_trained_in_room(self):
        """Test room trains multiple stats."""
        colony = Colony(colony_id=str(uuid4()), ant_count=5, food=1000)
        ant = colony.ants[0]

        colony.assign_ant_to_room(0, "food_storage")
        for _ in range(20):
            colony.tick()

        assert ant.stat_progress["Б"] > 0
        assert ant.stat_progress["Л"] > 0

    def test_different_rooms_train_different_stats(self):
        """Test different rooms train different stats."""
        colony1 = Colony(colony_id=str(uuid4()), ant_count=5, food=1000)
        colony2 = Colony(colony_id=str(uuid4()), ant_count=5, food=1000)

        colony1.assign_ant_to_room(0, "billiard_room")
        colony2.assign_ant_to_room(0, "pheromone_circle")

        for _ in range(10):
            colony1.tick()
            colony2.tick()

        and_stat = colony1.ants[0].stat_progress["И"]
        р_stat = colony2.ants[0].stat_progress["Р"]

        assert and_stat > 0
        assert р_stat > 0


class TestColonyDeath:
    """Test death handling."""

    def test_dead_ant_status_changes(self):
        """Test ant dies when reaching life period."""
        colony = Colony(colony_id=str(uuid4()), ant_count=1, food=5000)
        ant = colony.ants[0]
        life_period = ant.life_period

        for _ in range(life_period):
            colony.tick()
            assert ant.alive

        colony.tick()
        assert not ant.alive
        assert AntStatus.DEAD in ant.statuses


class TestColonySerialization:
    """Test colony serialization with all features."""

    def test_colony_serialize_deserialize(self):
        """Test colony can be serialized and deserialized."""
        colony1 = Colony(colony_id="test_col", ant_count=10, food=500)
        colony1.assign_ant_to_room(0, "food_storage")
        colony1.hold_voting("Test vote")

        data = colony1.to_dict()
        colony2 = Colony.from_dict(data)

        assert colony2.id == colony1.id
        assert colony2.food == colony1.food
        assert len(colony2.ants) == len(colony1.ants)
        assert colony2.ants[0].current_room == "food_storage"

    def test_colony_serialize_includes_voting_result(self):
        """Test last_voting is serialized."""
        colony1 = Colony(colony_id="col_vote", ant_count=10, food=100)
        colony1.hold_voting("Important decision")

        data = colony1.to_dict()
        assert data["last_voting"] is not None

        colony2 = Colony.from_dict(data)
        assert colony2.last_voting is not None
        assert colony2.last_voting.issue == "Important decision"


class TestColonyStateTracking:
    """Test colony state management."""

    def test_colony_queen_morale_tracking(self):
        """Test queen morale is tracked."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        assert colony.queen_morale == 50

    def test_colony_mushroom_fungus_level(self):
        """Test mushroom fungus level is tracked."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        assert colony.mushroom_fungus_level == 0

    def test_colony_has_multiple_ants_types(self):
        """Test colony can be created with different ant types."""
        harvester_colony = Colony(
            colony_id=str(uuid4()),
            ant_count=5,
            food=100,
            ant_type="Harvester",
        )
        assert all(ant.ant_type_name == "Harvester" for ant in harvester_colony.ants)

        red_colony = Colony(
            colony_id=str(uuid4()),
            ant_count=5,
            food=100,
            ant_type="RedReactiveAnt",
        )
        assert all(ant.ant_type_name == "RedReactiveAnt" for ant in red_colony.ants)


class TestColonyValidation:
    """Test colony input validation."""

    def test_colony_negative_ant_count_raises_error(self):
        """Test negative ant count raises ValueError."""
        with pytest.raises(ValueError):
            Colony(colony_id=str(uuid4()), ant_count=-5, food=100)

    def test_colony_negative_food_raises_error(self):
        """Test negative food raises ValueError."""
        with pytest.raises(ValueError):
            Colony(colony_id=str(uuid4()), ant_count=5, food=-10)

    def test_colony_non_int_ant_count_raises_error(self):
        """Test non-int ant count raises TypeError."""
        with pytest.raises(TypeError):
            Colony(colony_id=str(uuid4()), ant_count=5.5, food=100)

    def test_colony_non_string_id_raises_error(self):
        """Test non-string colony_id raises TypeError."""
        with pytest.raises(TypeError):
            Colony(colony_id=123, ant_count=5, food=100)

    def test_colony_bool_as_int_raises_error(self):
        """Test bool values are rejected for numeric fields."""
        with pytest.raises(TypeError):
            Colony(colony_id=str(uuid4()), ant_count=True, food=100)
