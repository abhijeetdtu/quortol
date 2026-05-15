"""Unit tests for pressure adjustment coupling and probability validity."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.src.services.calibration import CalibrationProfile
from backend.src.services.probability_model import ProbabilityModel, SamplingContext


class _FakeFeatureStore:
    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame

    def weighted_features(self, *_args, **_kwargs) -> pd.DataFrame:
        return self._frame.copy()


def _frame() -> pd.DataFrame:
    rows = []
    for idx in range(300):
        pressure = "high" if idx % 3 == 0 else ("low" if idx % 3 == 1 else "medium")
        rows.append(
            {
                "batting_team": "Chennai Super Kings",
                "bowling_team": "Mumbai Indians",
                "batter_role": "top",
                "bowler_role": "primary",
                "phase": "death" if idx % 2 == 0 else "middle",
                "wickets_band": "medium",
                "pressure_band": pressure,
                "season_weight": 1.0,
                "ExtraType": "",
                "BatsmanRun": 4 if pressure == "high" and idx % 5 == 0 else (1 if idx % 2 == 0 else 0),
                "ExtrasRun": 0,
                "IsWicketDelivery": 1 if pressure == "high" and idx % 11 == 0 else 0,
                "Kind": "caught",
            }
        )
    return pd.DataFrame(rows)


def _ctx(required_rr: float, innings_number: int = 2) -> SamplingContext:
    return SamplingContext(
        batting_team="Chennai Super Kings",
        bowling_team="Mumbai Indians",
        batter_role="top",
        bowler_role="primary",
        phase="death",
        wickets_band="medium",
        pressure_band="high",
        innings_number=innings_number,
        wickets_in_hand=6,
        required_run_rate=required_rr,
        baseline_rr=8.0,
    )


def _model(boundary_coeff: float) -> ProbabilityModel:
    calibration = CalibrationProfile(
        historical_chase_rate=0.55,
        historical_rr_first=8.2,
        historical_rr_second=8.5,
        target_bucket_chase_rates={},
        boundary_pressure_coeff=boundary_coeff,
        wicket_pressure_coeff=boundary_coeff * 0.8,
        wicket_boundary_elasticity=1.2,
        first_innings_pressure_scale=1.0,
        second_innings_pressure_scale=1.0,
        sample_matches=20,
    )
    return ProbabilityModel(
        feature_store=_FakeFeatureStore(_frame()),
        recency_bias=0.5,
        max_fallback_level=6,
        calibration_profile=calibration,
    )


def test_pressure_adjustments_keep_probabilities_valid():
    model = _model(boundary_coeff=0.35)
    base = np.array([0.40, 0.26, 0.10, 0.03, 0.14, 0.07], dtype=float)
    adjusted = model._apply_pressure_to_bat_runs(base, _ctx(required_rr=12.0))
    wicket = model._apply_pressure_to_wicket_binary(np.array([0.93, 0.07]), _ctx(required_rr=12.0))

    assert np.isclose(adjusted.sum(), 1.0)
    assert np.isclose(wicket.sum(), 1.0)
    assert np.all(adjusted > 0)
    assert np.all(wicket > 0)


def test_aggression_couples_boundary_and_wicket_risk():
    model = _model(boundary_coeff=0.35)
    base_runs = np.array([0.40, 0.26, 0.10, 0.03, 0.14, 0.07], dtype=float)
    base_wickets = np.array([0.93, 0.07], dtype=float)

    high_runs = model._apply_pressure_to_bat_runs(base_runs, _ctx(required_rr=12.0))
    low_runs = model._apply_pressure_to_bat_runs(base_runs, _ctx(required_rr=6.0))
    high_wk = model._apply_pressure_to_wicket_binary(base_wickets, _ctx(required_rr=12.0))
    low_wk = model._apply_pressure_to_wicket_binary(base_wickets, _ctx(required_rr=6.0))

    high_boundary_prob = high_runs[4] + high_runs[5]
    low_boundary_prob = low_runs[4] + low_runs[5]
    assert high_boundary_prob > low_boundary_prob
    assert high_wk[1] > low_wk[1]


def test_higher_boundary_coeff_yields_higher_wicket_risk_boost():
    conservative = _model(boundary_coeff=0.15)
    aggressive = _model(boundary_coeff=0.45)
    base_wickets = np.array([0.93, 0.07], dtype=float)

    neutral_ctx = _ctx(required_rr=8.0)
    high_ctx = _ctx(required_rr=12.0)

    neutral_cons = conservative._apply_pressure_to_wicket_binary(base_wickets, neutral_ctx)[1]
    neutral_aggr = aggressive._apply_pressure_to_wicket_binary(base_wickets, neutral_ctx)[1]
    high_cons = conservative._apply_pressure_to_wicket_binary(base_wickets, high_ctx)[1]
    high_aggr = aggressive._apply_pressure_to_wicket_binary(base_wickets, high_ctx)[1]

    cons_boost = high_cons - neutral_cons
    aggr_boost = high_aggr - neutral_aggr
    assert aggr_boost > cons_boost

