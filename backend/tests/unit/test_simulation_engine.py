"""Unit tests for full-context simulation engine."""

import copy

from backend.src.models.team_profile import TeamProfile
from backend.src.services.data_loader import load_ipl_data, get_available_teams
from backend.src.services.simulation_engine import ChaseStateSnapshot, SimulationEngine


def _profiles():
    df = load_ipl_data()
    teams = get_available_teams(df)
    team_a, team_b = teams[0], teams[1]
    return team_a, team_b, TeamProfile.from_dataframe(df, team_a), TeamProfile.from_dataframe(df, team_b)


def test_simulation_outputs_enriched_timeline_fields():
    team_a, team_b, p_a, p_b = _profiles()
    match = SimulationEngine().simulate_match(
        team_a=team_a,
        team_b=team_b,
        team_a_profile=p_a,
        team_b_profile=p_b,
        recency_bias=0.5,
        random_seed=42,
        model_depth="full_context",
        max_fallback_level=6,
        lineup_sampling_seed=42,
    )

    assert match.status == "completed"
    assert len(match.innings) == 2
    assert "diagnostics" in match.metadata
    assert "calibration" in match.metadata
    calibration = match.metadata["calibration"]
    assert "historical_chase_rate" in calibration
    assert "historical_rr_first" in calibration
    assert "historical_rr_second" in calibration
    assert "pressure_coefficients_version" in calibration

    sample_ball = match.innings[0].balls[0].to_dict()
    assert "batter" in sample_ball
    assert "bowler" in sample_ball
    assert "pressure_band" in sample_ball
    assert "context_level_used" in sample_ball
    assert "effective_sample_size" in sample_ball


def test_same_seed_reproducible_results():
    team_a, team_b, p_a, p_b = _profiles()
    engine = SimulationEngine()

    m1 = engine.simulate_match(team_a, team_b, p_a, p_b, recency_bias=0.7, random_seed=123)
    m2 = engine.simulate_match(team_a, team_b, p_a, p_b, recency_bias=0.7, random_seed=123)

    assert m1.result == m2.result
    assert m1.innings[0].total_runs == m2.innings[0].total_runs
    assert m1.innings[1].total_runs == m2.innings[1].total_runs


def test_legal_ball_accounting_and_realism_diagnostics():
    team_a, team_b, p_a, p_b = _profiles()
    match = SimulationEngine().simulate_match(team_a, team_b, p_a, p_b, recency_bias=0.6, random_seed=77)

    assert "realism_diagnostics" in match.metadata
    diagnostics = match.metadata["realism_diagnostics"]
    assert diagnostics["legal_ball_count"] <= 240
    assert diagnostics["total_events"] >= diagnostics["legal_ball_count"]
    assert diagnostics["extras_rate"] >= 0.0

    for innings in match.innings:
        legal_balls = sum(1 for ball in innings.balls if ball.is_legal_delivery)
        assert legal_balls <= 120
        assert innings.overs_completed <= 20.0


def test_bowler_constraints_no_consecutive_overs_and_max_four_overs():
    team_a, team_b, p_a, p_b = _profiles()
    match = SimulationEngine().simulate_match(team_a, team_b, p_a, p_b, recency_bias=0.5, random_seed=99)

    for innings in match.innings:
        starts = [ball for ball in innings.balls if ball.is_legal_delivery and ball.ball_in_over == 1]
        over_bowlers = [ball.bowler for ball in starts]
        for i in range(1, len(over_bowlers)):
            assert over_bowlers[i] != over_bowlers[i - 1]

        legal_by_bowler = {}
        for ball in innings.balls:
            if ball.is_legal_delivery:
                legal_by_bowler[ball.bowler] = legal_by_bowler.get(ball.bowler, 0) + 1
        assert all(count <= 24 for count in legal_by_bowler.values())


def _counterfactual_fixture(seed: int = 321):
    team_a, team_b, p_a, p_b = _profiles()
    engine = SimulationEngine()
    prepared = engine.prepare_match_context(
        team_a=team_a,
        team_b=team_b,
        recency_bias=0.55,
        max_fallback_level=6,
        last_n_matches=120,
        stadium=None,
    )
    match = engine.simulate_match(
        team_a=team_a,
        team_b=team_b,
        team_a_profile=p_a,
        team_b_profile=p_b,
        recency_bias=0.55,
        random_seed=seed,
        max_fallback_level=6,
        last_n_matches=120,
        prepared_context=prepared,
        collect_chase_snapshots=True,
    )
    snapshots = match.metadata.get("counterfactual", {}).get("chase_snapshots", [])
    assert snapshots
    raw_snapshot = copy.deepcopy(snapshots[min(10, len(snapshots) - 1)])
    return engine, prepared, ChaseStateSnapshot.from_dict(raw_snapshot)


def test_counterfactual_continuation_terminal_states():
    engine, prepared, snapshot = _counterfactual_fixture(seed=322)

    won_raw = snapshot.to_dict()
    won_raw["score"] = int(won_raw["target"])
    won_raw["runs_needed"] = 0
    won_raw["legal_ball"] = 120
    won_raw["balls_left"] = 0
    won = ChaseStateSnapshot.from_dict(won_raw)
    won_prob = engine.estimate_chase_win_probability_from_snapshot(
        won,
        context=prepared,
        rollouts=8,
        random_seed=7,
    )
    assert won_prob == 1.0

    lost_raw = snapshot.to_dict()
    lost_raw["score"] = max(0, int(lost_raw["target"]) - 15)
    lost_raw["runs_needed"] = int(lost_raw["target"]) - int(lost_raw["score"])
    lost_raw["legal_ball"] = 120
    lost_raw["balls_left"] = 0
    lost = ChaseStateSnapshot.from_dict(lost_raw)
    lost_prob = engine.estimate_chase_win_probability_from_snapshot(
        lost,
        context=prepared,
        rollouts=8,
        random_seed=7,
    )
    assert lost_prob == 0.0


def test_counterfactual_continuation_reproducible_for_fixed_seed():
    engine, prepared, snapshot = _counterfactual_fixture(seed=333)

    p1 = engine.estimate_chase_win_probability_from_snapshot(
        snapshot,
        context=prepared,
        rollouts=16,
        random_seed=1111,
    )
    p2 = engine.estimate_chase_win_probability_from_snapshot(
        snapshot,
        context=prepared,
        rollouts=16,
        random_seed=1111,
    )
    assert p1 == p2


def test_counterfactual_monotonic_sanity_for_runs_needed_at_same_terminal_ball():
    engine, prepared, snapshot = _counterfactual_fixture(seed=334)

    easier_raw = snapshot.to_dict()
    easier_raw["legal_ball"] = 120
    easier_raw["balls_left"] = 0
    easier_raw["score"] = int(easier_raw["target"])
    easier_raw["runs_needed"] = 0
    easier = ChaseStateSnapshot.from_dict(easier_raw)

    harder_raw = snapshot.to_dict()
    harder_raw["legal_ball"] = 120
    harder_raw["balls_left"] = 0
    harder_raw["score"] = max(0, int(harder_raw["target"]) - 2)
    harder_raw["runs_needed"] = int(harder_raw["target"]) - int(harder_raw["score"])
    harder = ChaseStateSnapshot.from_dict(harder_raw)

    p_easy = engine.estimate_chase_win_probability_from_snapshot(
        easier,
        context=prepared,
        rollouts=8,
        random_seed=11,
    )
    p_hard = engine.estimate_chase_win_probability_from_snapshot(
        harder,
        context=prepared,
        rollouts=8,
        random_seed=11,
    )
    assert p_easy >= p_hard
