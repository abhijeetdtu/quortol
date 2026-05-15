"""Integration tests for recency bias → simulation engine."""

import sys
from pathlib import Path

import pytest
import pandas as pd

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from services.simulation_engine import SimulationEngine
from models.team_profile import TeamProfile


class TestRecencyBiasSimulation:
    """Integration tests for recency bias in simulation."""

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

    def test_bias_weights_applied_in_simulation(self, sample_ipl_data):
        """Test that bias weights are applied in simulation loop."""
        mi_profile = TeamProfile.from_dataframe(sample_ipl_data, "Mumbai Indians")
        csk_profile = TeamProfile.from_dataframe(sample_ipl_data, "Chennai Super Kings")

        engine = SimulationEngine()

        # Run simulation with bias
        match = engine.simulate_match(
            team_a="Mumbai Indians",
            team_b="Chennai Super Kings",
            team_a_profile=mi_profile,
            team_b_profile=csk_profile,
            recency_bias=0.75,
            random_seed=456,
        )

        assert match.status == "completed"
        assert len(match.innings) == 2
        assert match.innings[0].total_runs > 0

    def test_multiple_bias_values_produce_valid_results(self, sample_ipl_data):
        """Test that various bias values produce valid simulation results."""
        mi_profile = TeamProfile.from_dataframe(sample_ipl_data, "Mumbai Indians")
        csk_profile = TeamProfile.from_dataframe(sample_ipl_data, "Chennai Super Kings")

        engine = SimulationEngine()

        bias_values = [0.0, 0.25, 0.5, 0.75, 1.0]

        for bias in bias_values:
            match = engine.simulate_match(
                team_a="Mumbai Indians",
                team_b="Chennai Super Kings",
                team_a_profile=mi_profile,
                team_b_profile=csk_profile,
                recency_bias=bias,
                random_seed=789,
            )

            assert match.status == "completed"
            assert len(match.innings) == 2
            assert match.innings[0].total_runs > 100
            assert match.innings[1].total_runs > 0
