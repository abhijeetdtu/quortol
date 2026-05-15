"""Tests for TeamProfile model — field validation, season_weights calculation."""

import sys
from pathlib import Path

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from models.team_profile import TeamProfile


class TestTeamProfile:
    """Tests for TeamProfile model."""

    def test_creates_team_profile(self):
        """Test basic TeamProfile creation."""
        profile = TeamProfile(
            team_name="Mumbai Indians",
            total_matches=237,
            avg_score_first=175.5,
            avg_score_chasing=168.2,
            avg_run_rate=8.75,
            wicket_frequency=0.065,
            six_frequency=0.12,
            four_frequency=0.22,
            season_weights={2022: 1.0, 2021: 0.9, 2020: 0.8},
        )
        
        assert profile.team_name == "Mumbai Indians"
        assert profile.total_matches == 237
        assert abs(profile.avg_run_rate - 8.75) < 0.01

    def test_from_dataframe(self, sample_dataframe):
        """Test creating TeamProfile from DataFrame."""
        profile = TeamProfile.from_dataframe(sample_dataframe, "Mumbai Indians")
        
        assert profile.team_name == "Mumbai Indians"
        assert profile.total_matches > 0
        assert 0 <= profile.wicket_frequency <= 1
        assert 0 <= profile.six_frequency <= 1
        assert 0 <= profile.four_frequency <= 1

    def test_from_dataframe_missing_team(self, sample_dataframe):
        """Test handling of team not found in DataFrame."""
        profile = TeamProfile.from_dataframe(sample_dataframe, "Nonexistent Team")
        
        assert profile.team_name == "Nonexistent Team"
        assert profile.total_matches == 0
        assert profile.avg_score_first == 0.0
        assert profile.avg_score_chasing == 0.0

    def test_season_weights_calculated(self, sample_dataframe):
        """Test that season_weights are calculated from DataFrame."""
        profile = TeamProfile.from_dataframe(sample_dataframe, "Mumbai Indians")
        
        assert profile.season_weights is not None
        assert isinstance(profile.season_weights, dict)
        
        # All weights should be between 0 and 1
        for weight in profile.season_weights.values():
            assert 0 <= weight <= 1


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    import pandas as pd
    
    return pd.DataFrame({
        "Season": [2022, 2022, 2021, 2021, 2020],
        "Team1": ["Mumbai Indians", "Chennai Super Kings", "Mumbai Indians", 
                  "Royal Challengers", "Mumbai Indians"],
        "Team2": ["Chennai Super Kings", "Mumbai Indians", "Royal Challengers",
                  "Mumbai Indians", "Chennai Super Kings"],
        "Winner": ["Mumbai Indians", "Chennai Super Kings", "Mumbai Indians",
                   "Mumbai Indians", "Chennai Super Kings"],
        "Win_Runs": [8, 5, 12, 3, 7],
        "Win_wickets": [3, 4, 2, 6, 1],
        "Team1_Score": [185, 165, 178, 172, 168],
        "Team2_Score": [177, 170, 166, 169, 175],
    })
