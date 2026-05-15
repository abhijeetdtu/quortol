"""Unit tests for full-context probability model."""

import numpy as np
import pytest

from backend.src.services.feature_store import WeightedFeatureStore
from backend.src.services.probability_model import ProbabilityModel, SamplingContext


def _context(innings_number=2, required_rr=10.0, wickets_in_hand=6):
    return SamplingContext(
        batting_team="Chennai Super Kings",
        bowling_team="Mumbai Indians",
        batter_role="top",
        bowler_role="primary",
        phase="death",
        wickets_band="medium",
        pressure_band="high",
        innings_number=innings_number,
        wickets_in_hand=wickets_in_hand,
        required_run_rate=required_rr,
        baseline_rr=8.0,
    )


def test_sampling_is_seed_deterministic():
    store = WeightedFeatureStore()
    model = ProbabilityModel(store, recency_bias=0.5, max_fallback_level=6)

    rng1 = np.random.default_rng(123)
    rng2 = np.random.default_rng(123)

    o1 = [model.sample_outcome(rng1, _context())[0] for _ in range(20)]
    o2 = [model.sample_outcome(rng2, _context())[0] for _ in range(20)]
    assert o1 == o2


def test_fallback_level_with_sparse_context():
    store = WeightedFeatureStore()
    model = ProbabilityModel(store, recency_bias=0.5, max_fallback_level=6)

    sparse = SamplingContext(
        batting_team="Imaginary Team",
        bowling_team="Unknown",
        batter_role="lower",
        bowler_role="part_time",
        phase="death",
        wickets_band="high",
        pressure_band="high",
        innings_number=2,
        wickets_in_hand=2,
        required_run_rate=18.0,
        baseline_rr=8.0,
    )
    _, _, level, ess = model.sample_outcome(np.random.default_rng(7), sparse)
    assert level in {"team_global", "league", "league_prior"}
    assert ess >= 0.0


def test_pressure_adjustment_increases_aggressive_outcomes():
    store = WeightedFeatureStore()
    model = ProbabilityModel(store, recency_bias=0.5, max_fallback_level=6)

    rng = np.random.default_rng(99)
    high_pressure = _context(required_rr=13.0, wickets_in_hand=7)
    low_pressure = _context(required_rr=6.0, wickets_in_hand=7)

    high = [model.sample_outcome(rng, high_pressure)[0] for _ in range(300)]
    low = [model.sample_outcome(rng, low_pressure)[0] for _ in range(300)]

    high_aggr = sum(1 for x in high if x in {"4", "6"})
    low_aggr = sum(1 for x in low if x in {"4", "6"})
    assert high_aggr >= low_aggr


def test_sample_delivery_event_exposes_table_fallback_usage():
    store = WeightedFeatureStore()
    model = ProbabilityModel(store, recency_bias=0.5, max_fallback_level=6)
    event = model.sample_delivery_event(np.random.default_rng(11), _context())
    assert event.event_type in {"legal", "wide", "no_ball"}
    assert "channel:" in event.fallback_used
    assert event.effective_sample_size >= 0.0


def test_no_ball_or_wide_wicket_is_run_out():
    store = WeightedFeatureStore()
    model = ProbabilityModel(store, recency_bias=0.5, max_fallback_level=6)
    rng = np.random.default_rng(2026)

    for _ in range(5000):
        event = model.sample_delivery_event(rng, _context(required_rr=13.0, wickets_in_hand=3))
        if event.event_type in {"no_ball", "wide"} and event.is_wicket:
            assert event.wicket_type == "run_out"
            return

    pytest.skip("No no-ball/wide wicket generated in finite sample; probabilistic path not observed.")
