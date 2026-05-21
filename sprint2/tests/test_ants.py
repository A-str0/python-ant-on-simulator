import pytest

# Remake this shit to work with different ant types

harvester_characteristics = dict(
    carry_capacity=5,
    life_period=30,
    food_per_tick=2,
    birth_rate=1.5,
    speed=1,
    role="worker",
)


@pytest.mark.usefixtures("harvester")
class TestAnts:
    @pytest.mark.parametrize(
        "harvester, characteristic, expected_value",
        [
            pytest.param(None, characteristic, expected_val, id=characteristic)
            for characteristic, expected_val in harvester_characteristics.items()
        ],
        indirect=["harvester"],
    )
    def test_harvester_characteristics(self, harvester, characteristic, expected_value):
        assert (val := getattr(harvester, characteristic)) == expected_value, (
            f"`{characteristic}` expected to be {expected_value!r}, but is {val!r}"
        )

    def test_harvester_life_period(self, harvester):
        assert harvester.alive, "why harvester is born-dead..."
        assert harvester.age == 0, "harvester is not newborn"

        for _ in range(harvester_characteristics["life_period"]):
            harvester.tick()

        assert harvester.age == harvester_characteristics["life_period"], (
            "something wrong with changing age during `.tick()`"
        )

        assert harvester.alive, (
            "why harvester leaves less than its `life_period`... he was so young..."
        )

        harvester.tick()

        assert not harvester.alive, "No long-living ants here broo"

    @pytest.mark.skip(reason="non-realised feature")
    def test_play_billiards(self, harvester):
        # no field `happiness` in Harvester
        init_happiness = harvester.happiness

        for _ in range(2):
            harvester.play_billiards()

        assert harvester.happiness > init_happiness, (
            "why playing billiards with friends not making our lil harvester happy...((("
        )

        for _ in range(100000000000):
            harvester.play_billiards()
        assert harvester.happiness <= 0, (
            "playing TOOOO much billiard definitely won't make lil harvey happy, every margin billiard game with homies after some moment will become struggle"
        )

    def test_harvester_dies_after_life_period(self, harvester):
        """Test that harvester dies exactly at life_period + 1 tick."""
        life_period = harvester_characteristics["life_period"]
        for _ in range(life_period):
            assert harvester.alive, f"Ant should be alive before reaching life_period"
            harvester.tick()
        
        assert harvester.alive, "Ant should still be alive at exactly life_period ticks"
        harvester.tick()
        assert not harvester.alive, "Ant should be dead after life_period"

    def test_harvester_age_increments(self, harvester):
        """Test that ant age increments correctly on each tick."""
        assert harvester.age == 0, "Initial age must be 0"
        for i in range(1, 6):
            harvester.tick()
            assert harvester.age == i, f"Age should be {i} after {i} ticks"
