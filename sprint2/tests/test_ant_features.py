"""Tests for ant types and stat system."""
import pytest
from ants import (
    Ant,
    AntStatus,
    Harvester,
    WeaverAnt,
    RedReactiveAnt,
    ExplodingAnt,
    STAT_NAMES,
    create_ant,
    ant_from_dict,
)


class TestAntTypes:
    """Test ant type creation and characteristics."""

    def test_harvester_creation(self):
        """Test Harvester ant can be created."""
        ant = Harvester()
        assert ant.name == "Муравьи-жнецы"
        assert ant.carry_capacity == 5
        assert ant.life_period == 30
        assert ant.food_per_tick == 2
        assert ant.birth_rate == 1.5
        assert ant.speed == 1
        assert ant.role == "worker"

    def test_weaver_ant_creation(self):
        """Test WeaverAnt can be created."""
        ant = WeaverAnt()
        assert ant.name == "Азиатские муравьи-портные"
        assert ant.carry_capacity == 4
        assert ant.life_period == 35
        assert ant.food_per_tick == 3
        assert ant.birth_rate == 1.2
        assert ant.speed == 1
        assert ant.role == "builder"

    def test_red_reactive_ant_creation(self):
        """Test RedReactiveAnt can be created."""
        ant = RedReactiveAnt()
        assert ant.name == "Рыжие реактивные муравьи"
        assert ant.carry_capacity == 3
        assert ant.life_period == 25
        assert ant.food_per_tick == 3
        assert ant.birth_rate == 2.0
        assert ant.speed == 2
        assert ant.role == "worker"

    def test_exploding_ant_creation(self):
        """Test ExplodingAnt can be created."""
        ant = ExplodingAnt()
        assert ant.name == "Взрывающиеся муравьи"
        assert ant.carry_capacity == 2
        assert ant.life_period == 20
        assert ant.food_per_tick == 4
        assert ant.birth_rate == 1.0
        assert ant.speed == 1
        assert ant.role == "soldier"

    def test_all_ant_types_registered(self):
        """Test all ant types are in registry."""
        from ants import ANT_TYPES_REGISTRY

        assert "Harvester" in ANT_TYPES_REGISTRY
        assert "WeaverAnt" in ANT_TYPES_REGISTRY
        assert "RedReactiveAnt" in ANT_TYPES_REGISTRY
        assert "ExplodingAnt" in ANT_TYPES_REGISTRY

    def test_create_ant_by_type(self):
        """Test create_ant factory function."""
        ant1 = create_ant("Harvester")
        assert isinstance(ant1, Harvester)

        ant2 = create_ant("WeaverAnt")
        assert isinstance(ant2, WeaverAnt)

        ant3 = create_ant("RedReactiveAnt")
        assert isinstance(ant3, RedReactiveAnt)

        ant4 = create_ant("ExplodingAnt")
        assert isinstance(ant4, ExplodingAnt)

    def test_create_ant_unknown_type_raises_error(self):
        """Test create_ant raises ValueError for unknown type."""
        with pytest.raises(ValueError, match="Unknown ant type"):
            create_ant("UnknownType")


class TestAntStats:
    """Test ant stat system (Б.И.Л.Ь.Я.Р.Д)."""

    def test_stat_names_are_correct(self):
        """Test STAT_NAMES has all 7 stats."""
        assert len(STAT_NAMES) == 7
        assert "Б" in STAT_NAMES
        assert "И" in STAT_NAMES
        assert "Л" in STAT_NAMES
        assert "Ь" in STAT_NAMES
        assert "Я" in STAT_NAMES
        assert "Р" in STAT_NAMES
        assert "Д" in STAT_NAMES

    def test_ant_initialized_with_default_stats(self):
        """Test ant is initialized with default stats of 5."""
        ant = Harvester()
        for stat in STAT_NAMES:
            assert ant.stats[stat] == 5

    def test_ant_initialized_with_zero_stat_progress(self):
        """Test ant stat progress starts at 0."""
        ant = Harvester()
        for stat in STAT_NAMES:
            assert ant.stat_progress[stat] == 0.0

    def test_weaver_ant_custom_stats(self):
        """Test WeaverAnt has custom stat distribution."""
        ant = WeaverAnt()
        assert ant.stats["Б"] == 4
        assert ant.stats["И"] == 6
        assert ant.stats["Л"] == 4
        assert ant.stats["Ь"] == 7
        assert ant.stats["Я"] == 4
        assert ant.stats["Р"] == 6
        assert ant.stats["Д"] == 5

    def test_red_reactive_ant_custom_stats(self):
        """Test RedReactiveAnt has custom stat distribution."""
        ant = RedReactiveAnt()
        assert ant.stats["Б"] == 6
        assert ant.stats["И"] == 3
        assert ant.stats["Л"] == 5
        assert ant.stats["Ь"] == 4
        assert ant.stats["Я"] == 6
        assert ant.stats["Р"] == 5
        assert ant.stats["Д"] == 4

    def test_exploding_ant_custom_stats(self):
        """Test ExplodingAnt has custom stat distribution."""
        ant = ExplodingAnt()
        assert ant.stats["Б"] == 7
        assert ant.stats["И"] == 7
        assert ant.stats["Л"] == 3
        assert ant.stats["Ь"] == 3
        assert ant.stats["Я"] == 8
        assert ant.stats["Р"] == 4
        assert ant.stats["Д"] == 6


class TestAntTrainStat:
    """Test ant stat training mechanics."""

    def test_train_stat_increases_progress(self):
        """Test train_stat increases stat_progress."""
        ant = Harvester()
        ant.train_stat("Б", 0.5)
        assert ant.stat_progress["Б"] == 0.5
        assert ant.stats["Б"] == 5

    def test_train_stat_levels_up_at_1_0_progress(self):
        """Test stat levels up when progress reaches 1.0."""
        ant = Harvester()
        ant.train_stat("И", 1.0)
        assert ant.stats["И"] == 6
        assert ant.stat_progress["И"] == 0.0

    def test_train_stat_caps_at_10(self):
        """Test stats cannot go above 10."""
        ant = Harvester()
        ant.stats["Л"] = 10
        ant.train_stat("Л", 1.0)
        assert ant.stats["Л"] == 10

    def test_train_stat_ignores_unknown_stat(self):
        """Test train_stat ignores unknown stat names."""
        ant = Harvester()
        ant.train_stat("UNKNOWN", 1.0)
        for stat in STAT_NAMES:
            assert ant.stat_progress[stat] == 0.0

    def test_train_stat_dead_ant_doesnt_train(self):
        """Test dead ants cannot train stats."""
        ant = Harvester()
        ant.alive = False
        ant.train_stat("Б", 1.0)
        assert ant.stats["Б"] == 5
        assert ant.stat_progress["Б"] == 0.0

    def test_train_stat_smells_like_dead_doesnt_train(self):
        """Test ants with smells_like_dead status cannot train."""
        ant = Harvester()
        ant.statuses.add(AntStatus.SMELLS_LIKE_DEAD)
        ant.train_stat("Я", 1.0)
        assert ant.stats["Я"] == 5

    def test_train_stat_billiard_main_only_trains_и(self):
        """Test billiard_main ant only trains И stat."""
        ant = Harvester()
        ant.statuses.add(AntStatus.BILLIARD_MAIN)

        ant.train_stat("Б", 1.0)
        assert ant.stats["Б"] == 5

        ant.train_stat("И", 1.0)
        assert ant.stats["И"] == 6

    def test_train_stat_multiple_times_accumulates(self):
        """Test multiple train_stat calls accumulate progress."""
        ant = Harvester()
        ant.train_stat("Д", 0.3)
        assert ant.stat_progress["Д"] == pytest.approx(0.3)
        ant.train_stat("Д", 0.4)
        assert ant.stat_progress["Д"] == pytest.approx(0.7)
        ant.train_stat("Д", 0.4)
        assert ant.stats["Д"] == 6
        assert ant.stat_progress["Д"] == pytest.approx(0.1)

    def test_train_stat_default_amount(self):
        """Test train_stat default amount is 0.1."""
        ant = Harvester()
        ant.train_stat("Я")
        assert ant.stat_progress["Я"] == 0.1


class TestExplodingAntAbility:
    """Test ExplodingAnt explode ability."""

    def test_exploding_ant_explode_kills_ant(self):
        """Test explode method kills the ant."""
        ant = ExplodingAnt()
        assert ant.alive is True
        ant.explode(50)
        assert ant.alive is False
        assert AntStatus.DEAD in ant.statuses

    def test_exploding_ant_explode_limits_damage(self):
        """Test explode caps damage at 10."""
        ant = ExplodingAnt()
        damage = ant.explode(1000)
        assert damage == 10

    def test_exploding_ant_explode_uses_lifting_stat(self):
        """Test explode damage is influenced by Л stat."""
        ant1 = ExplodingAnt()
        ant1.stats["Л"] = 3
        damage1 = ant1.explode(1)

        ant2 = ExplodingAnt()
        ant2.stats["Л"] = 8
        damage2 = ant2.explode(1)

        assert damage1 <= damage2


class TestWeaverAntAbility:
    """Test WeaverAnt build_leaf_room ability."""

    def test_weaver_ant_build_leaf_room_with_larvae(self):
        """Test build_leaf_room returns True with enough larvae."""
        ant = WeaverAnt()
        result = ant.build_leaf_room(1)
        assert result is True

    def test_weaver_ant_build_leaf_room_without_larvae(self):
        """Test build_leaf_room returns False without larvae."""
        ant = WeaverAnt()
        result = ant.build_leaf_room(0)
        assert result is False


class TestAntSerialization:
    """Test ant serialization."""

    def test_ant_to_dict(self):
        """Test ant.to_dict returns complete data."""
        ant = Harvester()
        ant.age = 5
        ant.alive = True
        ant.statuses.add(AntStatus.ALIVE)

        data = ant.to_dict()
        assert data["type"] == "Harvester"
        assert data["name"] == "Муравьи-жнецы"
        assert data["age"] == 5
        assert data["alive"] is True
        assert data["statuses"] == ["alive"]

    def test_ant_from_dict(self):
        """Test ant.from_dict creates ant from dict."""
        data = {
            "type": "Harvester",
            "name": "Муравьи-жнецы",
            "age": 5,
            "alive": True,
            "statuses": ["alive"],
            "stats": {"Б": 5, "И": 5, "Л": 5, "Ь": 5, "Я": 5, "Р": 5, "Д": 5},
            "stat_progress": {"Б": 0.0, "И": 0.0, "Л": 0.0, "Ь": 0.0, "Я": 0.0, "Р": 0.0, "Д": 0.0},
            "current_room": None,
        }
        ant = Harvester.from_dict(data)
        assert ant.age == 5
        assert ant.alive is True

    def test_ant_from_dict_with_factory(self):
        """Test ant_from_dict factory function."""
        ant1 = Harvester()
        ant1.age = 10

        data = ant1.to_dict()
        ant2 = ant_from_dict(data)

        assert ant2.age == 10
        assert type(ant2).__name__ == type(ant1).__name__

    def test_ant_from_dict_unknown_type_raises_error(self):
        """Test ant_from_dict raises ValueError for unknown type."""
        data = {"type": "UnknownAnt"}
        with pytest.raises(ValueError, match="Unknown ant type"):
            ant_from_dict(data)
