import pytest
from colony import Colony
from uuid import uuid4
from ants import Harvester


@pytest.fixture
def colony_id() -> str:
    return str(uuid4())


@pytest.fixture
def colony(colony_id, request) -> Colony:
    params = getattr(request, "param", {"ant_count": 0, "food": 0})

    return Colony(
        colony_id=colony_id, ant_count=params["ant_count"], food=params["food"]
    )


@pytest.fixture
def harvester() -> Harvester:
    return Harvester()
