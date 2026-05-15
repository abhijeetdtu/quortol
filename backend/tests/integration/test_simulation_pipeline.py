"""Integration tests for end-to-end full-context simulation pipeline."""

from backend.src.models.team_profile import TeamProfile
from backend.src.services.data_loader import get_available_teams, load_ipl_data
from backend.src.services.simulation_engine import SimulationEngine


def test_full_pipeline_generates_match_with_context_metrics():
    df = load_ipl_data()
    teams = get_available_teams(df)
    team_a, team_b = teams[0], teams[1]

    profile_a = TeamProfile.from_dataframe(df, team_a)
    profile_b = TeamProfile.from_dataframe(df, team_b)

    match = SimulationEngine().simulate_match(
        team_a=team_a,
        team_b=team_b,
        team_a_profile=profile_a,
        team_b_profile=profile_b,
        recency_bias=0.65,
        random_seed=2026,
        model_depth="full_context",
        max_fallback_level=6,
        lineup_sampling_seed=2026,
    )

    assert match.status == "completed"
    assert match.result
    assert len(match.innings) == 2
    assert "diagnostics" in match.metadata

    # Replay-critical invariants
    second = match.innings[1]
    assert second.total_runs >= 0
    assert all(ball.required_run_rate >= 0 for ball in second.balls)
    assert all(ball.wickets_in_hand <= 10 for ball in second.balls)
    assert all(ball.legal_ball_number >= 0 for ball in second.balls)

    realism = match.metadata.get("realism_diagnostics", {})
    assert realism.get("total_events", 0) >= realism.get("legal_ball_count", 0)
