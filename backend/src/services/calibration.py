"""Recency-aware calibration service for simulation pressure dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CalibrationProfile:
    """Data-driven calibration outputs for pressure modeling."""

    historical_chase_rate: float
    historical_rr_first: float
    historical_rr_second: float
    target_bucket_chase_rates: Dict[str, float]
    boundary_pressure_coeff: float
    wicket_pressure_coeff: float
    wicket_boundary_elasticity: float
    first_innings_pressure_scale: float
    second_innings_pressure_scale: float
    sample_matches: int
    pressure_coefficients_version: str = "recency_aware_v1"
    source: str = "matchup"

    def to_metadata(self, fallback_level: int) -> Dict[str, object]:
        """Return metadata payload for match diagnostics."""
        return {
            "historical_chase_rate": float(self.historical_chase_rate),
            "historical_rr_first": float(self.historical_rr_first),
            "historical_rr_second": float(self.historical_rr_second),
            "pressure_coefficients_version": self.pressure_coefficients_version,
            "target_bucket_chase_rates": dict(self.target_bucket_chase_rates),
            "boundary_pressure_coeff": float(self.boundary_pressure_coeff),
            "wicket_pressure_coeff": float(self.wicket_pressure_coeff),
            "wicket_boundary_elasticity": float(self.wicket_boundary_elasticity),
            "first_innings_pressure_scale": float(self.first_innings_pressure_scale),
            "second_innings_pressure_scale": float(self.second_innings_pressure_scale),
            "sample_matches": int(self.sample_matches),
            "source": self.source,
            "fallback_level": int(fallback_level),
        }


class CalibrationService:
    """Build recency-aware calibration baselines from weighted delivery data."""

    _TARGET_BUCKETS: Tuple[Tuple[str, int, int], ...] = (
        ("<=139", 0, 139),
        ("140-159", 140, 159),
        ("160-179", 160, 179),
        ("180-199", 180, 199),
        (">=200", 200, 999),
    )

    @staticmethod
    def _is_wide(extra_type: str) -> bool:
        tokens = [t.strip().lower() for t in str(extra_type or "").split(",") if t.strip()]
        return "wides" in tokens or "wide" in tokens

    @staticmethod
    def _is_no_ball(extra_type: str) -> bool:
        tokens = [t.strip().lower() for t in str(extra_type or "").split(",") if t.strip()]
        return any(tok in {"noballs", "no-ball", "no ball", "no_ball", "noball"} for tok in tokens)

    @classmethod
    def _is_legal_mask(cls, frame: pd.DataFrame) -> pd.Series:
        extras = frame.get("ExtraType", "").astype(str)
        is_wide = extras.map(cls._is_wide)
        is_no_ball = extras.map(cls._is_no_ball)
        return ~(is_wide | is_no_ball)

    @staticmethod
    def _safe_rate(numerator: float, denominator: float, fallback: float) -> float:
        if denominator <= 0:
            return fallback
        return float(numerator / denominator)

    @staticmethod
    def _clip(value: float, lo: float, hi: float) -> float:
        return float(max(lo, min(hi, value)))

    def _pair_match_frame(self, frame: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
        pair = {str(team_a), str(team_b)}
        pair_slice = frame[
            frame["batting_team"].isin(pair) & frame["bowling_team"].isin(pair)
        ].copy()
        if pair_slice.empty:
            return pair_slice

        by_match = pair_slice.groupby("ID")["batting_team"].agg(lambda s: set(map(str, s.unique())))
        valid_ids = by_match[by_match.map(lambda x: x == pair)].index
        if len(valid_ids) == 0:
            return pd.DataFrame(columns=pair_slice.columns)
        return pair_slice[pair_slice["ID"].isin(valid_ids)].copy()

    @classmethod
    def _innings_summary(cls, frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame(columns=["ID", "Innings", "total_runs", "legal_balls", "batting_team"])
        work = frame.copy()
        work["is_legal"] = cls._is_legal_mask(work)
        summary = (
            work.groupby(["ID", "Innings"], as_index=False)
            .agg(
                total_runs=("TotalRun", "sum"),
                legal_balls=("is_legal", "sum"),
                batting_team=("batting_team", "first"),
            )
        )
        return summary

    def _compute_match_baselines(self, frame: pd.DataFrame) -> Dict[str, float]:
        innings_summary = self._innings_summary(frame)
        if innings_summary.empty:
            return {
                "chase_rate": 0.5,
                "rr_first": 8.0,
                "rr_second": 8.0,
                "sample_matches": 0,
            }

        rr_first = 8.0
        rr_second = 8.0
        first = innings_summary[innings_summary["Innings"] == 1]
        second = innings_summary[innings_summary["Innings"] == 2]

        if not first.empty:
            rr_first = float((first["total_runs"] * 6.0 / first["legal_balls"].clip(lower=1)).mean())
        if not second.empty:
            rr_second = float((second["total_runs"] * 6.0 / second["legal_balls"].clip(lower=1)).mean())

        pivot = innings_summary.pivot(index="ID", columns="Innings", values="total_runs")
        pivot = pivot.dropna(subset=[1, 2], how="any")
        sample_matches = int(len(pivot))
        if sample_matches == 0:
            return {
                "chase_rate": 0.5,
                "rr_first": rr_first,
                "rr_second": rr_second,
                "sample_matches": 0,
            }

        chase_rate = float((pivot[2] > pivot[1]).mean())
        return {
            "chase_rate": chase_rate,
            "rr_first": rr_first,
            "rr_second": rr_second,
            "sample_matches": sample_matches,
        }

    def _target_bucket_curve(self, frame: pd.DataFrame) -> Dict[str, float]:
        innings_summary = self._innings_summary(frame)
        if innings_summary.empty:
            return {label: 0.5 for label, _lo, _hi in self._TARGET_BUCKETS}

        pivot = innings_summary.pivot(index="ID", columns="Innings", values="total_runs")
        pivot = pivot.dropna(subset=[1, 2], how="any")
        if pivot.empty:
            return {label: 0.5 for label, _lo, _hi in self._TARGET_BUCKETS}

        outcomes: Dict[str, float] = {}
        for label, lo, hi in self._TARGET_BUCKETS:
            band = pivot[(pivot[1] >= lo) & (pivot[1] <= hi)]
            if band.empty:
                outcomes[label] = float((pivot[2] > pivot[1]).mean())
            else:
                outcomes[label] = float((band[2] > band[1]).mean())
        return outcomes

    def _pressure_coefficients(self, frame: pd.DataFrame, baselines: Dict[str, float]) -> Dict[str, float]:
        if frame.empty:
            return {
                "boundary_pressure_coeff": 0.18,
                "wicket_pressure_coeff": 0.13,
                "wicket_boundary_elasticity": 1.0,
                "first_innings_pressure_scale": 1.0,
                "second_innings_pressure_scale": 1.0,
            }

        work = frame.copy()
        work = work[work["Innings"] == 2]
        if work.empty:
            return {
                "boundary_pressure_coeff": 0.18,
                "wicket_pressure_coeff": 0.13,
                "wicket_boundary_elasticity": 1.0,
                "first_innings_pressure_scale": 1.0,
                "second_innings_pressure_scale": 1.0,
            }

        work["is_legal"] = self._is_legal_mask(work)
        legal = work[work["is_legal"]].copy()
        if legal.empty:
            return {
                "boundary_pressure_coeff": 0.18,
                "wicket_pressure_coeff": 0.13,
                "wicket_boundary_elasticity": 1.0,
                "first_innings_pressure_scale": 1.0,
                "second_innings_pressure_scale": 1.0,
            }

        legal["rr_delta"] = legal["required_run_rate"].astype(float) - legal["baseline_rr"].astype(float)
        high = legal[legal["rr_delta"] >= 1.5]
        low = legal[legal["rr_delta"] <= -1.5]
        if len(high) < 80 or len(low) < 80:
            q_lo = float(legal["rr_delta"].quantile(0.30))
            q_hi = float(legal["rr_delta"].quantile(0.70))
            low = legal[legal["rr_delta"] <= q_lo]
            high = legal[legal["rr_delta"] >= q_hi]

        def _rates(part: pd.DataFrame) -> Tuple[float, float]:
            if part.empty:
                return 0.14, 0.055
            bat_runs = pd.to_numeric(part.get("BatsmanRun", 0), errors="coerce").fillna(0).astype(int)
            boundaries = float(((bat_runs == 4) | (bat_runs == 6)).sum())
            wickets = float((part.get("IsWicketDelivery", 0) == 1).sum())
            balls = float(len(part))
            return self._safe_rate(boundaries, balls, 0.14), self._safe_rate(wickets, balls, 0.055)

        b_high, w_high = _rates(high)
        b_low, w_low = _rates(low)
        eps = 1e-6

        boundary_lift = (b_high / max(eps, b_low)) - 1.0
        wicket_lift = (w_high / max(eps, w_low)) - 1.0

        boundary_pressure_coeff = self._clip(boundary_lift, 0.06, 0.60)
        wicket_boundary_elasticity = self._clip(
            wicket_lift / max(eps, boundary_lift),
            0.50,
            2.50,
        )
        wicket_pressure_coeff = self._clip(
            boundary_pressure_coeff * wicket_boundary_elasticity,
            0.05,
            0.85,
        )

        chase_delta = float(baselines["chase_rate"]) - 0.5
        rr_gap = float(baselines["rr_second"]) - float(baselines["rr_first"])
        delta_std = float(legal["rr_delta"].std(ddof=0)) if len(legal) > 1 else 0.0
        second_scale = self._clip((delta_std / 3.5) * (1.0 - chase_delta), 0.60, 1.35)
        first_scale = self._clip(1.0 + (rr_gap / max(1.0, float(baselines["rr_first"]))), 0.75, 1.35)

        return {
            "boundary_pressure_coeff": boundary_pressure_coeff,
            "wicket_pressure_coeff": wicket_pressure_coeff,
            "wicket_boundary_elasticity": wicket_boundary_elasticity,
            "first_innings_pressure_scale": first_scale,
            "second_innings_pressure_scale": second_scale,
        }

    def calibrate_for_matchup(self, weighted_df: pd.DataFrame, team_a: str, team_b: str) -> CalibrationProfile:
        """Compute a calibration profile from recency-aware weighted data."""
        pair_frame = self._pair_match_frame(weighted_df, team_a, team_b)
        source = "matchup"
        if pair_frame.empty:
            source = "league_fallback"
            pair_frame = weighted_df

        baselines = self._compute_match_baselines(pair_frame)
        coeffs = self._pressure_coefficients(pair_frame, baselines)
        buckets = self._target_bucket_curve(pair_frame)

        return CalibrationProfile(
            historical_chase_rate=float(baselines["chase_rate"]),
            historical_rr_first=float(baselines["rr_first"]),
            historical_rr_second=float(baselines["rr_second"]),
            target_bucket_chase_rates=buckets,
            boundary_pressure_coeff=float(coeffs["boundary_pressure_coeff"]),
            wicket_pressure_coeff=float(coeffs["wicket_pressure_coeff"]),
            wicket_boundary_elasticity=float(coeffs["wicket_boundary_elasticity"]),
            first_innings_pressure_scale=float(coeffs["first_innings_pressure_scale"]),
            second_innings_pressure_scale=float(coeffs["second_innings_pressure_scale"]),
            sample_matches=int(baselines["sample_matches"]),
            source=source,
        )
