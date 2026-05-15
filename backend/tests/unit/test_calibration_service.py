"""Unit tests for recency-aware calibration service."""

from __future__ import annotations

import pandas as pd

from backend.src.services.calibration import CalibrationService


def _phase(ball_index: int) -> str:
    over = (ball_index - 1) // 6
    if over <= 5:
        return "powerplay"
    if over <= 15:
        return "middle"
    return "death"


def _build_weighted_frame() -> pd.DataFrame:
    rows = []
    team_a = "Chennai Super Kings"
    team_b = "Mumbai Indians"
    for match_id in range(1, 9):
        first_total = 150 + (match_id % 4) * 8
        second_total = first_total + (4 if match_id <= 5 else -10)
        for innings, batting, bowling, target_total in [
            (1, team_a, team_b, first_total),
            (2, team_b, team_a, second_total),
        ]:
            cum_runs = 0
            wickets = 0
            baseline_rr = 8.0 if innings == 1 else 8.2
            for ball in range(1, 121):
                runs = 1 if ball <= target_total else 0
                if ball % 30 == 0:
                    runs = min(4, runs + 2)
                cum_before = cum_runs
                cum_runs += runs
                is_wicket = 1 if (ball % 40 == 0) else 0
                wickets_before = wickets
                wickets += is_wicket
                balls_remaining = max(1, 120 - (ball - 1))
                required_rr = 0.0
                pressure_band = "medium"
                if innings == 2:
                    required_runs = max(0, first_total + 1 - cum_before)
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


def test_calibration_is_deterministic_for_fixed_frame():
    frame = _build_weighted_frame()
    service = CalibrationService()

    p1 = service.calibrate_for_matchup(frame, "Chennai Super Kings", "Mumbai Indians")
    p2 = service.calibrate_for_matchup(frame, "Chennai Super Kings", "Mumbai Indians")

    assert p1 == p2
    assert 0.0 <= p1.historical_chase_rate <= 1.0
    assert p1.historical_rr_first > 0.0
    assert p1.historical_rr_second > 0.0
    assert set(p1.target_bucket_chase_rates.keys()) == {"<=139", "140-159", "160-179", "180-199", ">=200"}

