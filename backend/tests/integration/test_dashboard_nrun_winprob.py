"""Integration tests for N-run counterfactual win probability chart."""

from backend.dashboards.ball_by_ball import page
from backend.src.services.data_loader import get_available_teams, load_ipl_data


def test_run_n_simulations_counterfactual_winprob_has_variation(monkeypatch):
    # Keep runtime moderate in CI while still exercising continuation rollouts.
    monkeypatch.setitem(page.DASHBOARD_CONFIG, "winprob_rollouts_per_state", 10)
    monkeypatch.setitem(page.DASHBOARD_CONFIG, "winprob_max_states_per_ball", 4)
    monkeypatch.setitem(page.DASHBOARD_CONFIG, "winprob_max_total_states", 80)

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
        enable_counterfactual_value=["on"],
    )
    assert len(result) == 11
    winprob_fig = result[4]
    assert len(winprob_fig.data) >= 3

    mean_trace = None
    for trace in winprob_fig.data:
        if "Mean" in str(getattr(trace, "name", "")):
            mean_trace = trace
            break
    assert mean_trace is not None

    y_values = [float(y) for y in list(mean_trace.y)]
    assert y_values
    assert (max(y_values) - min(y_values)) > 0.03
