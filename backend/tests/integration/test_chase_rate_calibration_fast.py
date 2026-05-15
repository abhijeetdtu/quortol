"""Fast integration test: simulated chase rate tracks recency-aware baseline."""

from __future__ import annotations

import pandas as pd

from backend.src.models.team_profile import TeamProfile
from backend.src.services.simulation_engine import SimulationEngine


class _FakeFeatureStore:
    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame

    def weighted_features(self, *_args, **_kwargs) -> pd.DataFrame:
        return self._frame.copy()


def _phase(ball_index: int) -> str:
    over = (ball_index - 1) // 6
    if over <= 5:
        return "powerplay"
    if over <= 15:
        return "middle"
    return "death"


def _synthetic_weighted_frame() -> pd.DataFrame:
    rows = []
    team_a = "Chennai Super Kings"
    team_b = "Mumbai Indians"
    for match_id in range(1, 13):
        first_total = 154 + (match_id % 4) * 6
        # Chase succeeds for ~7 out of 12 matches.
        second_total = first_total + (3 if match_id <= 7 else -6)
        for innings, batting, bowling, innings_total, chase_target in [
            (1, team_a, team_b, first_total, None),
            (2, team_b, team_a, second_total, first_total + 1),
        ]:
            cum_runs = 0
            wickets = 0
            baseline_rr = 8.0 if innings == 1 else 8.3
            for ball in range(1, 121):
                runs = 1 if ball <= innings_total else 0
                if ball % 24 == 0:
                    runs = min(4, runs + 1)
                cum_before = cum_runs
                cum_runs += runs
                is_wicket = 1 if (ball % 37 == 0) else 0
                wickets_before = wickets
                wickets += is_wicket
                balls_remaining = max(1, 120 - (ball - 1))
                required_rr = 0.0
                pressure_band = "medium"
                if innings == 2 and chase_target is not None:
                    required_runs = max(0, chase_target - cum_before)
                    required_rr = (required_runs * 6.0) / balls_remaining
                    delta = required_rr - baseline_rr
                    if delta >= 1.5:
                        pressure_band = "high"
                    elif delta <= -1.5:
                        pressure_band = "low"

                batter_no = ((ball - 1) // 12) % 11 + 1
                bowler_no = ((ball - 1) // 24) % 6 + 1
                rows.append(
                    {
                        "ID": str(match_id),
                        "season": 2022 + (match_id % 3),
                        "match_date": pd.Timestamp(2022, 4, 1),
                        "venue": "Wankhede Stadium",
                        "Innings": innings,
                        "ball_index": ball,
                        "phase": _phase(ball),
                        "batting_team": batting,
                        "bowling_team": bowling,
                        "Batter": f"{batting} Batter {batter_no}",
                        "NonStriker": f"{batting} Batter {((batter_no) % 11) + 1}",
                        "Bowler": f"{bowling} Bowler {bowler_no}",
                        "batter_role": "top" if batter_no <= 2 else ("middle" if batter_no <= 5 else "lower"),
                        "bowler_role": "primary" if bowler_no <= 3 else "support",
                        "wickets_before": wickets_before,
                        "wickets_in_hand": max(0, 10 - wickets_before),
                        "wickets_band": "low" if wickets_before <= 2 else ("medium" if wickets_before <= 5 else "high"),
                        "cum_runs_before": cum_before,
                        "required_run_rate": required_rr,
                        "baseline_rr": baseline_rr,
                        "pressure_band": pressure_band if innings == 2 else "medium",
                        "TotalRun": runs,
                        "BatsmanRun": runs,
                        "ExtrasRun": 0,
                        "IsWicketDelivery": is_wicket,
                        "ExtraType": "",
                        "Kind": "caught" if is_wicket else "",
                        "outcome": str(runs) if runs in (0, 1, 2, 3, 4, 6) else "0",
                        "season_weight": 1.0,
                    }
                )
    return pd.DataFrame(rows)


def _profile_df(weighted: pd.DataFrame) -> pd.DataFrame:
    return weighted.rename(columns={"batting_team": "BattingTeam"})[
        ["ID", "Innings", "BattingTeam", "TotalRun", "IsWicketDelivery", "BatsmanRun"]
    ].copy()


def test_fast_calibrated_chase_rate_stays_near_historical_baseline():
    weighted = _synthetic_weighted_frame()
    engine = SimulationEngine()
    engine.feature_store = _FakeFeatureStore(weighted)

    profile_df = _profile_df(weighted)
    team_a = "Chennai Super Kings"
    team_b = "Mumbai Indians"
    profile_a = TeamProfile.from_dataframe(profile_df, team_a)
    profile_b = TeamProfile.from_dataframe(profile_df, team_b)

    baseline = engine.calibration_service.calibrate_for_matchup(weighted, team_a, team_b).historical_chase_rate

    chase_wins = 0
    sims = 6
    for seed in range(100, 100 + sims):
        match = engine.simulate_match(
            team_a=team_a,
            team_b=team_b,
            team_a_profile=profile_a,
            team_b_profile=profile_b,
            recency_bias=0.5,
            random_seed=seed,
            model_depth="full_context",
            max_fallback_level=6,
            lineup_sampling_seed=seed,
            last_n_matches=12,
            stadium="Wankhede Stadium",
        )
        if match.innings[1].total_runs > match.innings[0].total_runs:
            chase_wins += 1

    sim_chase_rate = chase_wins / sims
    assert abs(sim_chase_rate - baseline) <= 0.35

