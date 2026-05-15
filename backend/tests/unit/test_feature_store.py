"""Unit tests for weighted feature store."""

import pandas as pd

from backend.src.services.feature_store import WeightedFeatureStore


def test_weighted_feature_store_builds_canonical_columns():
    store = WeightedFeatureStore()
    df = store.weighted_features(0.5)

    required = {
        "season",
        "batting_team",
        "bowling_team",
        "Batter",
        "Bowler",
        "phase",
        "ball_index",
        "wickets_in_hand",
        "required_run_rate",
        "pressure_band",
        "outcome",
        "season_weight",
    }
    assert required.issubset(set(df.columns))
    assert not df.empty


def test_recency_weighting_changes_effective_weights():
    store = WeightedFeatureStore()
    low = store.weighted_features(0.0)
    high = store.weighted_features(1.0)

    # Same rows but different weights when recency bias changes.
    assert len(low) == len(high)
    assert float(low["season_weight"].sum()) != float(high["season_weight"].sum())


def _recent_ids_for_team(frame: pd.DataFrame, team: str, n: int) -> set[str]:
    team_slice = frame[
        (frame["batting_team"] == team) | (frame["bowling_team"] == team)
    ][["ID", "season", "match_date"]].drop_duplicates(subset=["ID"]).copy()
    team_slice["id_num"] = pd.to_numeric(team_slice["ID"], errors="coerce")
    team_slice = team_slice.sort_values(
        by=["season", "match_date", "id_num", "ID"],
        ascending=[True, True, True, True],
        kind="stable",
        na_position="last",
    )
    return set(team_slice.tail(n)["ID"].astype(str).tolist())


def test_last_n_matches_filters_per_team_not_globally():
    store = WeightedFeatureStore()
    full = store.weighted_features(0.5)
    teams = sorted(set(full["batting_team"].dropna().astype(str).tolist()))
    team_a, team_b = teams[0], teams[1]

    filtered = store.weighted_features(0.5, last_n_matches=5, teams=[team_a, team_b])
    filtered_ids = set(filtered["ID"].astype(str).unique().tolist())

    expected_a = _recent_ids_for_team(full, team_a, 5)
    expected_b = _recent_ids_for_team(full, team_b, 5)
    expected_union = expected_a.union(expected_b)

    assert expected_a.issubset(filtered_ids)
    assert expected_b.issubset(filtered_ids)
    assert filtered_ids.issubset(expected_union)


def test_stadium_filter_applies_when_stadium_selected():
    store = WeightedFeatureStore()
    venues = store.get_available_stadiums()
    assert venues

    stadium = venues[0]
    df = store.weighted_features(0.5, stadium=stadium)
    assert not df.empty
    assert set(df["venue"].dropna().astype(str).str.strip().unique().tolist()) == {stadium}
