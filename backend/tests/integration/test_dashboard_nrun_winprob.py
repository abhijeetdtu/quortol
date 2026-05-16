"""Integration tests for N-run win probability by first-innings score chart."""

from backend.dashboards.ball_by_ball import page
from backend.src.services.data_loader import get_available_teams, load_ipl_data


def test_run_n_simulations_score_conditioned_winprob_has_series():
    df = load_ipl_data()
    teams = get_available_teams(df)
    team_a, team_b = teams[0], teams[1]

    result = page.run_n_simulations(
        n_clicks=1,
        team_a=team_a,
        team_b=team_b,
        stadium="",
        recency_bias=0.5,
        last_n_matches=120,
        random_seed=2026,
        max_fallback=6,
        n_runs=8,
    )
    assert len(result) == 12
    score_winprob_fig = result[4]
    assert len(score_winprob_fig.data) >= 3
    state_data = result[5]
    assert isinstance(state_data, dict)
    assert isinstance(state_data.get("points"), list)
    assert len(state_data.get("points", [])) > 0
