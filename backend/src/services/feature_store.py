"""Recency-weighted delivery feature store for full-context simulation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .data_loader import load_ipl_data, normalize_team_name
from ..models.recency_bias import RecencyBiasWeight

logger = logging.getLogger(__name__)


def _phase_from_over(over: int) -> str:
    if over <= 5:
        return "powerplay"
    if over <= 15:
        return "middle"
    return "death"


def _wickets_band(wickets: int) -> str:
    if wickets <= 2:
        return "low"
    if wickets <= 5:
        return "medium"
    return "high"


def _pressure_band(required_rr: float, baseline_rr: float) -> str:
    delta = required_rr - baseline_rr
    if delta >= 1.5:
        return "high"
    if delta <= -1.5:
        return "low"
    return "medium"


def _map_outcome(total_run: int, is_wicket: int, extra_type: str) -> str:
    if int(is_wicket) == 1:
        return "W"
    extra = (extra_type or "").strip().lower()
    if extra in {"wides", "wide", "noballs", "no-ball", "no ball", "no_ball", "noball"}:
        return "X"
    if total_run in (0, 1, 2, 3, 4, 6):
        return str(total_run)
    if total_run >= 5:
        return "4"
    return "0"


@dataclass
class LineupData:
    batting_orders: Dict[str, pd.DataFrame]
    bowling_pools: Dict[str, pd.DataFrame]


class WeightedFeatureStore:
    """Build and cache weighted canonical delivery features by recency bucket."""

    def __init__(self) -> None:
        self._base_df = self._build_base_dataframe()

    @staticmethod
    def _load_match_info() -> pd.DataFrame:
        project_root = Path(__file__).resolve().parents[3]
        match_info_path = project_root / "analysis" / "ipl" / "data" / "Match_Info.csv"
        if match_info_path.exists():
            info = pd.read_csv(match_info_path, dtype=str, low_memory=False)
            info = info.fillna("")
            info["match_number"] = info["match_number"].astype(str)
            info["season"] = info["match_date"].astype(str).str[:4]
            if "venue" not in info.columns:
                info["venue"] = ""
            return info[["match_number", "season", "team1", "team2", "match_date", "venue"]]
        return pd.DataFrame(columns=["match_number", "season", "team1", "team2", "match_date", "venue"])

    def _build_base_dataframe(self) -> pd.DataFrame:
        df = load_ipl_data().copy()
        if "BattingTeam" not in df.columns:
            raise ValueError("Expected delivery-level IPL data with BattingTeam column")

        for col in ["ID", "Innings", "Overs", "BallNumber", "TotalRun", "IsWicketDelivery", "BatsmanRun", "ExtrasRun"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            else:
                df[col] = 0

        for col in ["Batter", "Bowler", "NonStriker", "ExtraType", "Kind", "BattingTeam"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
            else:
                df[col] = ""

        match_info = self._load_match_info()
        df["ID"] = df["ID"].astype(str)
        if not match_info.empty:
            df = df.merge(match_info, how="left", left_on="ID", right_on="match_number")
        else:
            df["season"] = ""
            df["team1"] = ""
            df["team2"] = ""
            df["match_date"] = ""
            df["venue"] = ""

        if "season" not in df.columns:
            df["season"] = ""
        df["season"] = pd.to_numeric(df["season"], errors="coerce").fillna(2025).astype(int)
        if "match_date" not in df.columns:
            df["match_date"] = ""
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
        if "venue" not in df.columns:
            df["venue"] = ""
        df["venue"] = df["venue"].fillna("").astype(str).str.strip()

        df["batting_team"] = df["BattingTeam"].map(normalize_team_name)
        df["team1"] = df.get("team1", "").map(normalize_team_name)
        df["team2"] = df.get("team2", "").map(normalize_team_name)
        df["bowling_team"] = np.where(df["batting_team"] == df["team1"], df["team2"], df["team1"])
        missing_bowling = df["bowling_team"].eq("")
        df.loc[missing_bowling, "bowling_team"] = "Unknown"

        df = df.sort_values(["ID", "Innings", "Overs", "BallNumber"], kind="stable").reset_index(drop=True)

        df["ball_index"] = df.groupby(["ID", "Innings"]).cumcount() + 1
        df["over_number"] = ((df["ball_index"] - 1) // 6).astype(int)
        df["phase"] = df["over_number"].map(_phase_from_over)

        df["wicket_flag"] = (df["IsWicketDelivery"] == 1).astype(int)
        df["wickets_before"] = (
            df.groupby(["ID", "Innings"])["wicket_flag"].cumsum() - df["wicket_flag"]
        ).astype(int)
        df["wickets_in_hand"] = (10 - df["wickets_before"]).clip(lower=0)
        df["wickets_band"] = df["wickets_before"].map(_wickets_band)

        innings_totals = df.groupby(["ID", "Innings"], as_index=False).agg(innings_total=("TotalRun", "sum"))
        first_innings = innings_totals[innings_totals["Innings"] == 1][["ID", "innings_total"]].rename(columns={"innings_total": "first_innings_total"})
        df = df.merge(first_innings, how="left", on="ID")
        df["first_innings_total"] = df["first_innings_total"].fillna(160)
        df["target"] = df["first_innings_total"] + 1
        df["cum_runs_before"] = (
            df.groupby(["ID", "Innings"])["TotalRun"].cumsum() - df["TotalRun"]
        ).astype(int)

        balls_remaining = (120 - (df["ball_index"] - 1)).clip(lower=1)
        df["required_run_rate"] = np.where(
            df["Innings"] == 2,
            ((df["target"] - df["cum_runs_before"]).clip(lower=0) * 6.0) / balls_remaining,
            0.0,
        )

        team_baseline_rr = (
            df.groupby("batting_team", as_index=False)["TotalRun"].mean().rename(columns={"TotalRun": "team_ball_run"})
        )
        team_baseline_rr["baseline_rr"] = team_baseline_rr["team_ball_run"] * 6.0
        df = df.merge(team_baseline_rr[["batting_team", "baseline_rr"]], how="left", on="batting_team")
        df["baseline_rr"] = df["baseline_rr"].fillna(8.0)
        df["pressure_band"] = [
            _pressure_band(rr, base) if inn == 2 else "medium"
            for rr, base, inn in zip(df["required_run_rate"], df["baseline_rr"], df["Innings"])
        ]

        df["outcome"] = [
            _map_outcome(total, wicket, extra)
            for total, wicket, extra in zip(df["TotalRun"], df["IsWicketDelivery"], df["ExtraType"])
        ]

        # Estimate batting role from weighted average first ball faced.
        first_appearance = (
            df.groupby(["batting_team", "Batter", "ID", "Innings"], as_index=False)["ball_index"].min()
            .groupby(["batting_team", "Batter"], as_index=False)["ball_index"].mean()
        )

        def _batter_role(avg_ball: float) -> str:
            if avg_ball <= 24:
                return "top"
            if avg_ball <= 72:
                return "middle"
            return "lower"

        first_appearance["batter_role"] = first_appearance["ball_index"].map(_batter_role)
        df = df.merge(first_appearance[["batting_team", "Batter", "batter_role"]], how="left", on=["batting_team", "Batter"])
        df["batter_role"] = df["batter_role"].fillna("middle")

        # Bowler role by workload share within bowling team.
        bowl_load = df.groupby(["bowling_team", "Bowler"], as_index=False).size().rename(columns={"size": "balls"})
        bowl_load["team_balls"] = bowl_load.groupby("bowling_team")["balls"].transform("sum")
        bowl_load["share"] = bowl_load["balls"] / bowl_load["team_balls"].clip(lower=1)

        def _bowler_role(share: float) -> str:
            if share >= 0.14:
                return "primary"
            if share >= 0.08:
                return "support"
            return "part_time"

        bowl_load["bowler_role"] = bowl_load["share"].map(_bowler_role)
        df = df.merge(bowl_load[["bowling_team", "Bowler", "bowler_role"]], how="left", on=["bowling_team", "Bowler"])
        df["bowler_role"] = df["bowler_role"].fillna("support")

        keep_cols = [
            "ID",
            "season",
            "match_date",
            "venue",
            "Innings",
            "ball_index",
            "phase",
            "batting_team",
            "bowling_team",
            "Batter",
            "NonStriker",
            "Bowler",
            "batter_role",
            "bowler_role",
            "wickets_before",
            "wickets_in_hand",
            "wickets_band",
            "cum_runs_before",
            "required_run_rate",
            "baseline_rr",
            "pressure_band",
            "TotalRun",
            "BatsmanRun",
            "ExtrasRun",
            "IsWicketDelivery",
            "ExtraType",
            "Kind",
            "outcome",
        ]
        return df[keep_cols].copy()

    @staticmethod
    def _recency_bucket(recency_bias: float) -> float:
        return round(float(recency_bias) / 0.05) * 0.05

    @staticmethod
    def _coerce_last_n_matches(last_n_matches: Optional[int]) -> Optional[int]:
        if last_n_matches is None:
            return None
        try:
            n = int(last_n_matches)
        except (TypeError, ValueError):
            return None
        return n if n > 0 else None

    @staticmethod
    def _filter_last_n_matches(frame: pd.DataFrame, last_n_matches: int) -> pd.DataFrame:
        match_meta = frame[["ID", "season", "match_date"]].drop_duplicates(subset=["ID"]).copy()
        match_meta["id_num"] = pd.to_numeric(match_meta["ID"], errors="coerce")
        # Order oldest->newest so we can tail(N) for the most recent window.
        match_meta = match_meta.sort_values(
            by=["season", "match_date", "id_num", "ID"],
            ascending=[True, True, True, True],
            kind="stable",
            na_position="last",
        )
        recent_ids = set(match_meta.tail(last_n_matches)["ID"].astype(str).tolist())
        return frame[frame["ID"].astype(str).isin(recent_ids)].copy()

    @staticmethod
    def _normalize_teams(teams: Optional[Tuple[str, ...]]) -> Tuple[str, ...]:
        if not teams:
            return tuple()
        normalized = [normalize_team_name(t) for t in teams if str(t).strip()]
        return tuple(sorted(set(normalized)))

    @staticmethod
    def _normalize_stadium(stadium: Optional[str]) -> Optional[str]:
        if stadium is None:
            return None
        value = str(stadium).strip()
        return value if value else None

    @staticmethod
    def _filter_last_n_matches_per_team(frame: pd.DataFrame, last_n_matches: int, teams: Tuple[str, ...]) -> pd.DataFrame:
        if not teams:
            return WeightedFeatureStore._filter_last_n_matches(frame, last_n_matches)

        selected_ids: set[str] = set()
        for team in teams:
            team_slice = frame[
                (frame["batting_team"] == team) | (frame["bowling_team"] == team)
            ][["ID", "season", "match_date"]].drop_duplicates(subset=["ID"]).copy()
            if team_slice.empty:
                continue

            team_slice["id_num"] = pd.to_numeric(team_slice["ID"], errors="coerce")
            team_slice = team_slice.sort_values(
                by=["season", "match_date", "id_num", "ID"],
                ascending=[True, True, True, True],
                kind="stable",
                na_position="last",
            )
            team_ids = team_slice.tail(last_n_matches)["ID"].astype(str).tolist()
            selected_ids.update(team_ids)

        if not selected_ids:
            return frame.copy()
        return frame[frame["ID"].astype(str).isin(selected_ids)].copy()

    @staticmethod
    def _filter_by_stadium(frame: pd.DataFrame, stadium: str) -> pd.DataFrame:
        return frame[frame["venue"].astype(str).str.casefold() == str(stadium).casefold()].copy()

    @lru_cache(maxsize=128)
    def get_weighted_features(
        self,
        recency_bucket: float,
        last_n_matches: Optional[int] = None,
        teams: Optional[Tuple[str, ...]] = None,
        stadium: Optional[str] = None,
    ) -> pd.DataFrame:
        weights = RecencyBiasWeight.calculate_weights(decay_slope=recency_bucket)
        work = self._base_df.copy()
        n = self._coerce_last_n_matches(last_n_matches)
        normalized_teams = self._normalize_teams(teams)
        normalized_stadium = self._normalize_stadium(stadium)
        if n is not None:
            work = self._filter_last_n_matches_per_team(work, n, normalized_teams)
        if normalized_stadium is not None:
            work = self._filter_by_stadium(work, normalized_stadium)
        work["season_weight"] = work["season"].map(weights).fillna(0.01)
        return work

    def weighted_features(
        self,
        recency_bias: float,
        last_n_matches: Optional[int] = None,
        teams: Optional[List[str]] = None,
        stadium: Optional[str] = None,
    ) -> pd.DataFrame:
        teams_tuple = tuple(teams) if teams else None
        return self.get_weighted_features(
            self._recency_bucket(recency_bias),
            self._coerce_last_n_matches(last_n_matches),
            teams_tuple,
            self._normalize_stadium(stadium),
        )

    def get_available_stadiums(self) -> List[str]:
        venues = (
            self._base_df["venue"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        venues = venues[venues != ""]
        return sorted(set(venues.tolist()))

    def get_lineup_data(self, recency_bias: float, last_n_matches: Optional[int] = None) -> LineupData:
        df = self.weighted_features(recency_bias, last_n_matches=last_n_matches)

        batting_order = (
            df.groupby(["batting_team", "bowling_team", "Batter"], as_index=False)
            .agg(
                first_ball=("ball_index", "mean"),
                weight=("season_weight", "sum"),
            )
        )
        batting_order["order_score"] = batting_order["first_ball"]
        batting_order = batting_order.sort_values(["batting_team", "bowling_team", "order_score", "weight"], ascending=[True, True, True, False])

        bowling_pool = (
            df.groupby(["bowling_team", "batting_team", "Bowler"], as_index=False)
            .agg(weight=("season_weight", "sum"), role=("bowler_role", lambda s: s.mode().iloc[0] if not s.mode().empty else "support"))
            .sort_values(["bowling_team", "batting_team", "weight"], ascending=[True, True, False])
        )

        batting_orders: Dict[str, pd.DataFrame] = {}
        for (bat_team, bowl_team), frame in batting_order.groupby(["batting_team", "bowling_team"]):
            batting_orders[f"{bat_team}__{bowl_team}"] = frame.reset_index(drop=True)

        bowling_pools: Dict[str, pd.DataFrame] = {}
        for (bowl_team, bat_team), frame in bowling_pool.groupby(["bowling_team", "batting_team"]):
            bowling_pools[f"{bowl_team}__{bat_team}"] = frame.reset_index(drop=True)

        return LineupData(batting_orders=batting_orders, bowling_pools=bowling_pools)
