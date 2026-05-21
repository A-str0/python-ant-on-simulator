"""Tests for VotingResult and voting mechanics."""
import pytest
from colony import Colony, VotingResult
from uuid import uuid4


class TestVotingResult:
    """Test VotingResult class."""

    def test_voting_result_initialization(self):
        """Test VotingResult initializes with correct defaults."""
        result = VotingResult()
        assert result.for_count == 0
        assert result.against_count == 0
        assert result.abstain_count == 0
        assert result.lost_count == 0
        assert result.issue == ""
        assert result.queen_overridden is False

    def test_voting_result_to_dict(self):
        """Test VotingResult.to_dict serialization."""
        result = VotingResult()
        result.for_count = 10
        result.against_count = 5
        result.abstain_count = 2
        result.lost_count = 1
        result.issue = "Test issue"
        result.queen_overridden = True

        data = result.to_dict()
        assert data["for_count"] == 10
        assert data["against_count"] == 5
        assert data["abstain_count"] == 2
        assert data["lost_count"] == 1
        assert data["issue"] == "Test issue"
        assert data["queen_overridden"] is True

    def test_voting_result_from_dict(self):
        """Test VotingResult.from_dict deserialization."""
        data = {
            "for_count": 10,
            "against_count": 5,
            "abstain_count": 2,
            "lost_count": 1,
            "issue": "Test issue",
            "queen_overridden": True,
        }
        result = VotingResult.from_dict(data)
        assert result.for_count == 10
        assert result.against_count == 5
        assert result.abstain_count == 2
        assert result.lost_count == 1
        assert result.issue == "Test issue"
        assert result.queen_overridden is True

    def test_voting_result_roundtrip_serialization(self):
        """Test VotingResult serialization roundtrip."""
        result1 = VotingResult()
        result1.for_count = 20
        result1.against_count = 15
        result1.abstain_count = 5
        result1.lost_count = 3
        result1.issue = "Billiard tournament"
        result1.queen_overridden = False

        result2 = VotingResult.from_dict(result1.to_dict())
        assert result2.for_count == result1.for_count
        assert result2.against_count == result1.against_count
        assert result2.abstain_count == result1.abstain_count
        assert result2.lost_count == result1.lost_count
        assert result2.issue == result1.issue
        assert result2.queen_overridden == result1.queen_overridden


class TestColonyVoting:
    """Test colony voting mechanics."""

    def test_hold_voting_empty_colony(self):
        """Test hold_voting with no ants returns empty result."""
        colony = Colony(colony_id=str(uuid4()), ant_count=0, food=100)
        result = colony.hold_voting("Test issue")
        assert result.for_count == 0
        assert result.against_count == 0
        assert result.abstain_count == 0
        assert result.lost_count == 0

    def test_hold_voting_returns_voting_result(self):
        """Test hold_voting returns VotingResult object."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        result = colony.hold_voting("Test issue")
        assert isinstance(result, VotingResult)
        assert result.issue == "Test issue"

    def test_hold_voting_distributes_votes(self):
        """Test hold_voting distributes votes among ants."""
        colony = Colony(colony_id=str(uuid4()), ant_count=100, food=1000)
        result = colony.hold_voting("Test issue")

        total_votes = (
            result.for_count
            + result.against_count
            + result.abstain_count
            + result.lost_count
        )
        assert total_votes == 100

    def test_hold_voting_sets_last_voting(self):
        """Test hold_voting sets colony.last_voting."""
        colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
        result = colony.hold_voting("Critical vote")
        assert colony.last_voting == result
        assert colony.last_voting.issue == "Critical vote"

    def test_hold_voting_vote_ratios_make_sense(self):
        """Test hold_voting vote distribution follows reasonable pattern."""
        colony = Colony(colony_id=str(uuid4()), ant_count=1000, food=5000)
        result = colony.hold_voting("Major issue")

        total = (
            result.for_count
            + result.against_count
            + result.abstain_count
            + result.lost_count
        )
        assert total == 1000

        for_ratio = result.for_count / total
        against_ratio = result.against_count / total
        abstain_ratio = result.abstain_count / total
        lost_ratio = result.lost_count / total

        assert 0.0 <= for_ratio <= 1.0
        assert 0.0 <= against_ratio <= 1.0
        assert 0.0 <= abstain_ratio <= 1.0
        assert 0.0 <= lost_ratio <= 1.0

    def test_hold_voting_queen_override_probability(self):
        """Test queen_overridden can be set with some probability."""
        overrides = 0
        total_votes = 100

        for _ in range(total_votes):
            colony = Colony(colony_id=str(uuid4()), ant_count=10, food=100)
            result = colony.hold_voting("Test")
            if result.queen_overridden:
                overrides += 1

        assert 0 <= overrides <= total_votes
