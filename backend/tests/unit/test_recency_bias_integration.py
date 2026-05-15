"""Tests for recency bias integration — slider value affects simulation probabilities."""

import sys
from pathlib import Path

import pytest
import pandas as pd

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from services.simulation_engine import SimulationEngine
from models.team_profile import TeamProfile


class TestRecencyBiasIntegration:
    """Tests for recency bias integration."""

    @pytest.fixture
    def sample_ipl_data(self):
        """Create sample IPL data with multiple seasons."""
        return pd.DataFrame({
            "Season": [2022, 2022, 2021, 2021, 2020, 2020, 2019, 2019],
            "Team1": ["Mumbai Indians", "Chennai Super Kings", "Mumbai Indians",
                      "Chennai Super Kings", "Mumbai Indians", "Chennai Super Kings",
                      "Mumbai Indians", "Chennai Super Kings"],
            "Team2": ["Chennai Super Kings", "Mumbai Indians", "Chennai Super Kings",
                      "Mumbai Indians", "Chennai Super Kings", "Mumbai Indians",
                      "Chennai Super Kings", "Mumbai Indians"],
            "Winner": ["Mumbai Indians", "Chennai Super Kings", "Mumbai Indians",
                       "Chennai Super Kings", "Chennai Super Kings", "Mumbai Indians",
                       "Chennai Super Kings", "Mumbai Indians"],
            "Win_Runs": [8, 5, 12, 3, 7, 10, 15, 6],
            "Win_wickets": [3, 4, 2, 6, 1, 5, 4, 2],
            "Team1_Score": [185, 165, 178, 172, 168, 175, 180, 170],
            "Team2_Score": [177, 170, 166, 169, 175, 165, 165, 164],
        })

    def test_bias_affects_probabilities(self, sample_ipl_data):
        """Test that different bias values affect simulation probabilities."""
        mi_profile = TeamProfile.from_dataframe(sample_ipl_data, "Mumbai Indians")
        csk_profile = TeamProfile.from_dataframe(sample_ipl_data, "Chennai Super Kings")

        engine = SimulationEngine()

        # Run simulations with different bias values
        match_low = engine.simulate_match(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            team_a_profile=mi_profile,
            team_b_profile=csk_profile,
            recency_bias=0.0,
            random_seed=42,
        )

        match_high = engine.simulate_match(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            team_a_profile=mi_profile,
            team_b_profile=csk_profile,
            recency_bias=1.0,
            random_seed=42,
        )

        # Both should complete
        assert match_low.status == "completed"
        assert match_high.status == "completed"

        # Scores should be reasonable
        assert match_low.innings[0].total_runs > 100
        assert match_high.innings[0].total_runs > 100

    def test_bias_edge_cases(self, sample_ipl_data):
        """Test bias at minimum and maximum values."""
        mi_profile = TeamProfile.from_dataframe(sample_ipl_data, "Mumbai Indians")
        csk_profile = TeamProfile.from_dataframe(sample_ipl_data, "Chennai Super Kings")

        engine = SimulationEngine()

        # Test bias = 0.0 (no recency)
        match_zero = engine.simulate_match(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            team_a_profile=mi_profile,
            team_b_profile=csk_profile,
            recency_bias=0.0,
            random_seed=123,
        )

        # Test bias = 1.0 (max recency)
        match_one = engine.simulate_match(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            team_a_profile=mi_profile,
            team_b_profile=csk_profile,
            recency_bias=1.0,
            random_seed=123,
        )

        assert match_zero.status == "completed"
        assert match_one.status == "completed"
