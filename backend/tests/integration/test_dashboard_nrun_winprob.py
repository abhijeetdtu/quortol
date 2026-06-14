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


def test_current_rr_winprob_chart_empty_and_insufficient_samples_are_safe():
    empty_fig = page._multi_run_crr_wickets_winprob_figure(
        [],
        team_a="Team A",
        team_b="Team B",
        target_input=180,
        target_mode=">=",
    )
    assert len(empty_fig.data) == 0
    assert empty_fig.layout.annotations

    sparse_points = [
        {"team": "Team A", "current_run_rate": 8.0, "wickets_left": 9, "team_win": 1, "target": 190},
        {"team": "Team A", "current_run_rate": 8.5, "wickets_left": 8, "team_win": 0, "target": 190},
        {"team": "Team B", "current_run_rate": 9.0, "wickets_left": 9, "team_win": 1, "target": 190},
    ]
    sparse_fig = page._multi_run_crr_wickets_winprob_figure(
        sparse_points,
        team_a="Team A",
        team_b="Team B",
        target_input=180,
        target_mode=">=",
    )
    assert len(sparse_fig.data) == 0
    assert sparse_fig.layout.annotations


def test_target_filter_supports_both_gte_and_lte_modes():
    points = [
        {"target": 170},
        {"target": 180},
        {"target": 190},
    ]
    gte_points, gte_threshold, gte_mode = page._filter_chase_states_by_target(points, 180, ">=")
    lte_points, lte_threshold, lte_mode = page._filter_chase_states_by_target(points, 180, "<=")

    assert gte_mode == ">="
    assert lte_mode == "<="
    assert gte_threshold == 180
    assert lte_threshold == 180
    assert [p["target"] for p in gte_points] == [180, 190]
    assert [p["target"] for p in lte_points] == [170, 180]
