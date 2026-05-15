"""Tests for SimulatedMatch model — match state transitions, result computation."""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from models.match_simulation import SimulatedMatch
from models.innings import Innings


class TestSimulatedMatch:
    """Tests for SimulatedMatch model."""

    def test_creates_match(self):
        """Test basic SimulatedMatch creation."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            recency_bias=0.5,
            random_seed=42,
            created_at=datetime.now(timezone.utc),
        )
        
        assert match.team_a == "Mumbai Indians"
        assert match.team_b == "Chennai Super Kings"
        assert match.recency_bias == 0.5
        assert match.random_seed == 42
        assert match.status == "pending"
        assert len(match.innings) == 0

    def test_add_innings(self):
        """Test adding an innings to match."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
        )
        
        innings = Innings(
            innings_number=1,
            batting_team="Mumbai Indians",
        )
        
        match.add_innings(innings)
        
        assert len(match.innings) == 1
        assert match.innings[0].batting_team == "Mumbai Indians"

    def test_result_computation_team_a_wins(self):
        """Test result when Team A wins."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
        )
        
        innings_1 = Innings(innings_number=1, batting_team="Mumbai Indians")
        innings_1.total_runs = 180
        
        innings_2 = Innings(innings_number=2, batting_team="Chennai Super Kings")
        innings_2.total_runs = 175
        innings_2.wickets_lost = 6
        
        match.add_innings(innings_1)
        match.add_innings(innings_2)
        
        result = match.calculate_result()
        
        assert result == "Mumbai Indians won by 5 runs"

    def test_result_computation_team_b_wins(self):
        """Test result when Team B wins."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
        )
        
        innings_1 = Innings(innings_number=1, batting_team="Mumbai Indians")
        innings_1.total_runs = 170
        
        innings_2 = Innings(innings_number=2, batting_team="Chennai Super Kings")
        innings_2.total_runs = 175
        innings_2.wickets_lost = 4
        
        match.add_innings(innings_1)
        match.add_innings(innings_2)
        
        result = match.calculate_result()
        
        assert "Chennai Super Kings won" in result

    def test_result_computation_tie(self):
        """Test tie result when scores are equal."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
        )
        
        innings_1 = Innings(innings_number=1, batting_team="Mumbai Indians")
        innings_1.total_runs = 180
        
        innings_2 = Innings(innings_number=2, batting_team="Chennai Super Kings")
        innings_2.total_runs = 180
        innings_2.wickets_lost = 8
        
        match.add_innings(innings_1)
        match.add_innings(innings_2)
        
        result = match.calculate_result()
        
        assert result == "Tie"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        match = SimulatedMatch(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            recency_bias=0.5,
            random_seed=42,
        )
        
        match_dict = match.to_dict()
        
        assert "team_a" in match_dict
        assert "team_b" in match_dict
        assert "innings" in match_dict
        assert "recency_bias" in match_dict
        assert "random_seed" in match_dict
