import pytest
from colony import Colony
from contextlib import nullcontext as no_raise
import datetime
from uuid import uuid4
from ants import Harvester


def _id() -> str:
    return str(uuid4())


# VERY BAD STAFF GOING ON DOWN HERE:
HARVESTER_NEEDS = Harvester().food_per_tick
HARVESTER_LIFE_PERIOD = Harvester().life_period


class TestColony:
    @pytest.mark.parametrize(
        "colony_id, ant_count, food, expectation",
        [
            # VALID VALUES I GUESS?:
            pytest.param(_id(), 10, 5, no_raise(), id="valid-1"),
            pytest.param(_id(), 1, 500, no_raise(), id="valid-2"),
            pytest.param(_id(), 1, 500, no_raise(), id="valid-3"),
            pytest.param(_id(), 234, 0, no_raise(), id="valid-4"),
            pytest.param(_id(), 0, 100, no_raise(), id="valid-5"),
            pytest.param(_id(), 0, 0, no_raise(), id="valid-6"),
            # spornaya huynia (non-int food): pytest.param(_id(), 1, 10.1, no_raise(), id=''),
            # INVALID colony_id:
            pytest.param(
                1, 1, 1, pytest.raises(TypeError), id="invalid `colony_id` type: 1"
            ),
            pytest.param(
                datetime.datetime.now(),
                1,
                1,
                pytest.raises(TypeError),
                id="invalid `colony_id` type: 2",
            ),
            # INVALID ant_count type:
            pytest.param(
                _id(),
                "invalid count",
                1,
                pytest.raises(TypeError),
                id="invalid `ant_count` type: 1",
            ),
            pytest.param(
                _id(),
                2.5,
                1,
                pytest.raises(TypeError),
                id="invalid `ant_count` type: 2",
            ),
            pytest.param(
                _id(),
                3 + 4j,
                1,
                pytest.raises(TypeError),
                id="invalid `ant_count` type: 3",
            ),
            # INVALID food type:
            pytest.param(
                _id(),
                1,
                "invalid food amount 1",
                pytest.raises(TypeError),
                id="invalid `food` type: 1",
            ),
            pytest.param(
                _id(), 1, -100, pytest.raises(TypeError), id="invalid `food` type: 2"
            ),
            pytest.param(
                _id(), 1, 4j, pytest.raises(TypeError), id="invalid `food` type: 3"
            ),
            # INVALID numeric values (ant_count, food):
            pytest.param(
                _id(),
                -100,
                10,
                pytest.raises(ValueError),
                id="invalid `ant_count` value (negative)",
            ),  # INVALID count
            pytest.param(
                _id(),
                1,
                -30,
                pytest.raises(ValueError),
                id="invalid `food` value (negative)",
            ),  # INVALID food
            pytest.param(
                _id(),
                -101,
                -15,
                pytest.raises(ValueError),
                id="invalid `ant_count` and `food` value (both negative)",
            ),  # INVALID food + count
        ],
    )
    def test_initialization(self, ant_count, colony_id, food, expectation):
        with expectation:
            Colony(colony_id=colony_id, ant_count=ant_count, food=food)

    # VERY BAD STAFF GOING ON DOWN HERE. I'M SORRY...
    # btw don't know why i didn't skipped this test with message like "this stimulation sucks", but whatever
    @pytest.mark.parametrize(
        "ticks_amount, colony",
        [
            pytest.param(
                10, {"ant_count": 8, "food": HARVESTER_NEEDS * 100}, id="positive food"
            ),
            pytest.param(
                HARVESTER_LIFE_PERIOD,
                {"ant_count": 8, "food": HARVESTER_NEEDS * 8 * HARVESTER_LIFE_PERIOD},
                id="0 food",
            ),
            pytest.param(120, {"ant_count": 10, "food": 0}, id="negative food"),
        ],
        indirect=["colony"],
    )
    def test_simulation_food(self, ticks_amount, colony):
        food_left = max(
            colony.food - ticks_amount * len(colony.ants) * HARVESTER_NEEDS, 0
        )
        for _ in range(ticks_amount):
            colony.tick()
        assert food_left == colony.food, (
            f"Ожидалось, что в колонии останется `{food_left}` еп, фактически осталось: `{colony.food}`"
        )
