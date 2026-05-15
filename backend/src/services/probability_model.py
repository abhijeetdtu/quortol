"""Full-context probability model with hierarchical fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .feature_store import WeightedFeatureStore
from .calibration import CalibrationProfile

OUTCOME_LABELS = ["0", "1", "2", "3", "4", "6", "W", "X"]
CHANNEL_LABELS = ["legal", "wide", "no_ball"]
BAT_RUN_LABELS = ["0", "1", "2", "3", "4", "6"]
EXTRA_RUN_LABELS = ["1", "2", "3", "4", "5"]
WICKET_BINARY_LABELS = ["N", "Y"]
WICKET_TYPE_LABELS = [
    "bowled",
    "caught",
    "lbw",
    "run_out",
    "stumped",
    "caught_and_bowled",
    "hit_wicket",
    "other",
]


@dataclass(frozen=True)
class SamplingContext:
    batting_team: str
    bowling_team: str
    batter_role: str
    bowler_role: str
    phase: str
    wickets_band: str
    pressure_band: str
    innings_number: int
    wickets_in_hand: int
    required_run_rate: float
    baseline_rr: float


@dataclass(frozen=True)
class DeliverySample:
    event_type: str
    is_legal_delivery: bool
    bat_runs: int
    extra_runs: int
    is_wicket: bool
    wicket_type: Optional[str]
    total_runs: int
    probability: float
    fallback_used: str
    effective_sample_size: float


class ProbabilityModel:
    """Context-conditioned Bayesian inference engine with fallback hierarchy."""

    def __init__(
        self,
        feature_store: WeightedFeatureStore,
        recency_bias: float = 0.5,
        max_fallback_level: int = 6,
        last_n_matches: Optional[int] = None,
        teams: Optional[List[str]] = None,
        stadium: Optional[str] = None,
        calibration_profile: Optional[CalibrationProfile] = None,
    ) -> None:
        self.feature_store = feature_store
        self.recency_bias = recency_bias
        self.max_fallback_level = max(0, min(6, int(max_fallback_level)))
        self.calibration = calibration_profile or CalibrationProfile(
            historical_chase_rate=0.5,
            historical_rr_first=8.0,
            historical_rr_second=8.0,
            target_bucket_chase_rates={},
            boundary_pressure_coeff=0.18,
            wicket_pressure_coeff=0.13,
            wicket_boundary_elasticity=1.0,
            first_innings_pressure_scale=1.0,
            second_innings_pressure_scale=1.0,
            sample_matches=0,
            source="default",
        )

        self.frame = self.feature_store.weighted_features(
            recency_bias,
            last_n_matches=last_n_matches,
            teams=teams,
            stadium=stadium,
        ).copy()
        self.lookup_defs: List[Tuple[str, List[str]]] = [
            ("exact", ["batting_team", "bowling_team", "batter_role", "bowler_role", "phase", "wickets_band", "pressure_band"]),
            ("drop_pressure", ["batting_team", "bowling_team", "batter_role", "bowler_role", "phase", "wickets_band"]),
            ("drop_wickets", ["batting_team", "bowling_team", "batter_role", "bowler_role", "phase"]),
            ("drop_roles", ["batting_team", "bowling_team", "phase", "wickets_band", "pressure_band"]),
            ("team_vs_opposition_phase", ["batting_team", "bowling_team", "phase"]),
            ("team_global", ["batting_team", "phase"]),
            ("league", []),
        ]

        self._prepare_feature_labels()

        self.channel_tables = self._build_lookup_tables(self.frame, "event_channel", CHANNEL_LABELS)
        legal_frame = self.frame[self.frame["event_channel"] == "legal"].copy()
        self.legal_bat_tables = self._build_lookup_tables(legal_frame, "bat_run_label", BAT_RUN_LABELS)
        self.legal_wicket_tables = self._build_lookup_tables(legal_frame, "wicket_label", WICKET_BINARY_LABELS)

        no_ball_frame = self.frame[self.frame["event_channel"] == "no_ball"].copy()
        self.no_ball_bat_tables = self._build_lookup_tables(no_ball_frame, "bat_run_label", BAT_RUN_LABELS)
        self.no_ball_extra_tables = self._build_lookup_tables(no_ball_frame, "extra_run_label", EXTRA_RUN_LABELS)
        self.no_ball_wicket_tables = self._build_lookup_tables(no_ball_frame, "wicket_label", WICKET_BINARY_LABELS)

        wide_frame = self.frame[self.frame["event_channel"] == "wide"].copy()
        self.wide_extra_tables = self._build_lookup_tables(wide_frame, "extra_run_label", EXTRA_RUN_LABELS)
        self.wide_wicket_tables = self._build_lookup_tables(wide_frame, "wicket_label", WICKET_BINARY_LABELS)

        legal_wickets = legal_frame[legal_frame["wicket_label"] == "Y"].copy()
        self.wicket_type_tables = self._build_lookup_tables(legal_wickets, "wicket_type_label", WICKET_TYPE_LABELS)

        self.priors = {
            "channel": self._prior_from_empirical(self.frame, "event_channel", CHANNEL_LABELS, strength=200.0),
            "legal_bat": self._prior_from_empirical(legal_frame, "bat_run_label", BAT_RUN_LABELS, strength=50.0),
            "legal_wicket": self._prior_from_empirical(legal_frame, "wicket_label", WICKET_BINARY_LABELS, strength=120.0),
            "no_ball_bat": self._prior_from_empirical(no_ball_frame, "bat_run_label", BAT_RUN_LABELS, strength=40.0),
            "no_ball_extra": self._prior_from_empirical(no_ball_frame, "extra_run_label", EXTRA_RUN_LABELS, strength=30.0),
            "no_ball_wicket": self._prior_from_empirical(no_ball_frame, "wicket_label", WICKET_BINARY_LABELS, strength=80.0),
            "wide_extra": self._prior_from_empirical(wide_frame, "extra_run_label", EXTRA_RUN_LABELS, strength=40.0),
            "wide_wicket": self._prior_from_empirical(wide_frame, "wicket_label", WICKET_BINARY_LABELS, strength=80.0),
            "wicket_type": self._prior_from_empirical(legal_wickets, "wicket_type_label", WICKET_TYPE_LABELS, strength=40.0),
        }

    @staticmethod
    def _is_wide(extra_type: str) -> bool:
        tokens = [t.strip().lower() for t in str(extra_type or "").split(",") if t.strip()]
        return "wides" in tokens or "wide" in tokens

    @staticmethod
    def _is_no_ball(extra_type: str) -> bool:
        tokens = [t.strip().lower() for t in str(extra_type or "").split(",") if t.strip()]
        return any(tok in {"noballs", "no-ball", "no ball", "no_ball", "noball"} for tok in tokens)

    @classmethod
    def _event_channel(cls, extra_type: str) -> str:
        if cls._is_wide(extra_type):
            return "wide"
        if cls._is_no_ball(extra_type):
            return "no_ball"
        return "legal"

    @staticmethod
    def _normalize_bat_runs_label(value: int) -> str:
        if value in (0, 1, 2, 3, 4, 6):
            return str(value)
        if value >= 5:
            return "4"
        return "0"

    @staticmethod
    def _normalize_extra_runs_label(value: int) -> str:
        if value <= 1:
            return "1"
        if value >= 5:
            return "5"
        return str(int(value))

    @staticmethod
    def _normalize_wicket_type(kind: str) -> str:
        val = str(kind or "").strip().lower()
        if val in {"caught", "bowled", "lbw", "run out", "stumped", "caught and bowled", "hit wicket"}:
            return val.replace(" ", "_")
        return "other"

    def _prepare_feature_labels(self) -> None:
        if "ExtraType" not in self.frame.columns:
            self.frame["ExtraType"] = ""
        if "BatsmanRun" not in self.frame.columns:
            self.frame["BatsmanRun"] = 0
        if "ExtrasRun" not in self.frame.columns:
            self.frame["ExtrasRun"] = 0
        if "Kind" not in self.frame.columns:
            self.frame["Kind"] = ""

        self.frame["event_channel"] = self.frame["ExtraType"].map(self._event_channel)
        self.frame["bat_run_label"] = (
            pd.to_numeric(self.frame["BatsmanRun"], errors="coerce")
            .fillna(0)
            .astype(int)
            .map(self._normalize_bat_runs_label)
        )
        self.frame["extra_run_label"] = (
            pd.to_numeric(self.frame["ExtrasRun"], errors="coerce")
            .fillna(1)
            .astype(int)
            .map(self._normalize_extra_runs_label)
        )
        self.frame["wicket_label"] = np.where(self.frame["IsWicketDelivery"] == 1, "Y", "N")
        self.frame["wicket_type_label"] = self.frame["Kind"].map(self._normalize_wicket_type)

    @staticmethod
    def _prior_from_empirical(frame: pd.DataFrame, label_col: str, labels: List[str], strength: float) -> np.ndarray:
        if frame.empty or label_col not in frame.columns:
            return np.ones(len(labels), dtype=float)
        counts = frame[label_col].astype(str).value_counts()
        vector = np.array([float(counts.get(label, 0.0)) for label in labels], dtype=float)
        total = vector.sum()
        if total <= 0:
            return np.ones(len(labels), dtype=float)
        probs = vector / total
        prior = np.clip(probs * float(strength), 1e-6, None)
        return prior

    def _build_lookup_tables(
        self,
        frame: pd.DataFrame,
        label_col: str,
        labels: List[str],
    ) -> List[Tuple[Dict[Tuple[str, ...], np.ndarray], Dict[Tuple[str, ...], float]]]:
        tables: List[Tuple[Dict[Tuple[str, ...], np.ndarray], Dict[Tuple[str, ...], float]]] = []
        if frame.empty:
            empty = {tuple(): np.zeros(len(labels), dtype=float)}
            ess = {tuple(): 0.0}
            return [(empty, ess) for _ in self.lookup_defs]

        for _, cols in self.lookup_defs:
            group_cols = cols + [label_col] if cols else [label_col]
            grouped = frame.groupby(group_cols, as_index=False)["season_weight"].sum()

            by_key: Dict[Tuple[str, ...], np.ndarray] = {}
            ess_map: Dict[Tuple[str, ...], float] = {}
            if cols:
                for key_vals, part in grouped.groupby(cols):
                    key = key_vals if isinstance(key_vals, tuple) else (key_vals,)
                    vector = np.zeros(len(labels), dtype=float)
                    for _, row in part.iterrows():
                        raw_label = str(row[label_col])
                        if raw_label not in labels:
                            continue
                        idx = labels.index(raw_label)
                        vector[idx] = float(row["season_weight"])
                    by_key[tuple(str(v) for v in key)] = vector
                    ess_map[tuple(str(v) for v in key)] = float(vector.sum())
            else:
                vector = np.zeros(len(labels), dtype=float)
                for _, row in grouped.iterrows():
                    raw_label = str(row[label_col])
                    if raw_label not in labels:
                        continue
                    idx = labels.index(raw_label)
                    vector[idx] = float(row["season_weight"])
                by_key[tuple()] = vector
                ess_map[tuple()] = float(vector.sum())

            tables.append((by_key, ess_map))
        return tables

    def _key_for_level(self, context: SamplingContext, level: int) -> Tuple[str, ...]:
        values = {
            "batting_team": context.batting_team,
            "bowling_team": context.bowling_team,
            "batter_role": context.batter_role,
            "bowler_role": context.bowler_role,
            "phase": context.phase,
            "wickets_band": context.wickets_band,
            "pressure_band": context.pressure_band,
        }
        cols = self.lookup_defs[level][1]
        return tuple(str(values[c]) for c in cols)

    def _pressure_signal(self, context: SamplingContext) -> float:
        rr_delta = context.required_run_rate - context.baseline_rr
        scale = (
            self.calibration.second_innings_pressure_scale
            if context.innings_number == 2
            else self.calibration.first_innings_pressure_scale
        )
        return float(np.clip((rr_delta / 4.0) * scale, -0.9, 1.2))

    def _apply_pressure_to_bat_runs(self, probs: np.ndarray, context: SamplingContext) -> np.ndarray:
        adjusted = probs.copy()
        aggression = self._pressure_signal(context)
        boundary_coeff = self.calibration.boundary_pressure_coeff
        idx_0, idx_1, idx_4, idx_6 = 0, 1, 4, 5

        if aggression > 0:
            adjusted[idx_4] *= 1.0 + aggression * boundary_coeff
            adjusted[idx_6] *= 1.0 + aggression * (boundary_coeff * 1.35)
            adjusted[idx_0] *= 1.0 - aggression * (boundary_coeff * 0.55)
            adjusted[idx_1] *= 1.0 + aggression * (boundary_coeff * 0.20)
        else:
            cool = abs(aggression)
            adjusted[idx_0] *= 1.0 + cool * 0.30
            adjusted[idx_1] *= 1.0 + cool * 0.12
            adjusted[idx_6] *= 1.0 - cool * 0.24

        adjusted = np.clip(adjusted, 1e-12, None)
        adjusted /= adjusted.sum()
        return adjusted

    def _apply_pressure_to_wicket_binary(self, probs: np.ndarray, context: SamplingContext) -> np.ndarray:
        adjusted = probs.copy()
        aggression = self._pressure_signal(context)
        wicket_risk = np.clip((6 - context.wickets_in_hand) / 6.0, 0.0, 1.0)

        if aggression > 0:
            risk_boost = aggression * (
                self.calibration.boundary_pressure_coeff * self.calibration.wicket_boundary_elasticity
            )
            risk_boost = min(0.95, max(0.0, risk_boost))
            adjusted[1] *= 1.0 + risk_boost * (1.0 + 0.35 * wicket_risk)
            adjusted[0] *= 1.0 - risk_boost * 0.45
        else:
            cool = abs(aggression)
            adjusted[1] *= 1.0 - cool * 0.16
            adjusted[0] *= 1.0 + cool * 0.08

        adjusted = np.clip(adjusted, 1e-12, None)
        adjusted /= adjusted.sum()
        return adjusted

    def _sample_label(
        self,
        rng: np.random.Generator,
        context: SamplingContext,
        tables: List[Tuple[Dict[Tuple[str, ...], np.ndarray], Dict[Tuple[str, ...], float]]],
        labels: List[str],
        prior_alpha: Optional[np.ndarray] = None,
        min_ess: float = 0.0,
        adjuster: Optional[Callable[[np.ndarray, SamplingContext], np.ndarray]] = None,
    ) -> Tuple[str, float, str, float]:
        counts = None
        fallback_used = "league_prior"
        effective_sample_size = 0.0

        for level, (level_name, _cols) in enumerate(self.lookup_defs):
            if level > self.max_fallback_level:
                break
            key = self._key_for_level(context, level)
            vectors, ess_map = tables[level]
            if key in vectors and ess_map.get(key, 0.0) >= min_ess:
                counts = vectors[key]
                effective_sample_size = ess_map[key]
                fallback_used = level_name
                break

        if counts is None:
            counts = np.zeros(len(labels), dtype=float)
            effective_sample_size = 0.0

        if prior_alpha is None:
            prior_alpha = np.ones(len(labels), dtype=float)
        posterior = counts + prior_alpha
        probs = posterior / posterior.sum()
        if adjuster is not None:
            probs = adjuster(probs, context)

        label_idx = int(rng.choice(len(labels), p=probs))
        label = labels[label_idx]
        return label, float(probs[label_idx]), fallback_used, float(effective_sample_size)

    def sample_delivery_event(
        self,
        rng: np.random.Generator,
        context: SamplingContext,
    ) -> DeliverySample:
        channel, p_channel, fb_channel, ess_channel = self._sample_label(
            rng,
            context,
            self.channel_tables,
            CHANNEL_LABELS,
            prior_alpha=self.priors["channel"],
            min_ess=150.0,
        )

        fallback_parts = [f"channel:{fb_channel}"]
        ess_parts = [ess_channel]
        probability = p_channel

        if channel == "legal":
            bat_label, p_bat, fb_bat, ess_bat = self._sample_label(
                rng,
                context,
                self.legal_bat_tables,
                BAT_RUN_LABELS,
                prior_alpha=self.priors["legal_bat"],
                min_ess=60.0,
                adjuster=self._apply_pressure_to_bat_runs,
            )
            wicket_label, p_wk, fb_wk, ess_wk = self._sample_label(
                rng,
                context,
                self.legal_wicket_tables,
                WICKET_BINARY_LABELS,
                prior_alpha=self.priors["legal_wicket"],
                min_ess=180.0,
                adjuster=self._apply_pressure_to_wicket_binary,
            )
            fallback_parts.extend([f"bat:{fb_bat}", f"wicket:{fb_wk}"])
            ess_parts.extend([ess_bat, ess_wk])
            probability *= p_bat * p_wk

            is_wicket = wicket_label == "Y"
            wicket_type = None
            if is_wicket:
                wicket_type, p_type, fb_type, ess_type = self._sample_label(
                    rng,
                    context,
                    self.wicket_type_tables,
                    WICKET_TYPE_LABELS,
                    prior_alpha=self.priors["wicket_type"],
                    min_ess=25.0,
                )
                fallback_parts.append(f"type:{fb_type}")
                ess_parts.append(ess_type)
                probability *= p_type

            bat_runs = int(bat_label)
            extra_runs = 0
            total_runs = bat_runs
            return DeliverySample(
                event_type="legal",
                is_legal_delivery=True,
                bat_runs=bat_runs,
                extra_runs=extra_runs,
                is_wicket=is_wicket,
                wicket_type=wicket_type,
                total_runs=total_runs,
                probability=float(min(1.0, max(0.0, probability))),
                fallback_used="|".join(fallback_parts),
                effective_sample_size=float(np.mean(ess_parts)),
            )

        if channel == "wide":
            extra_label, p_extra, fb_extra, ess_extra = self._sample_label(
                rng,
                context,
                self.wide_extra_tables,
                EXTRA_RUN_LABELS,
                prior_alpha=self.priors["wide_extra"],
                min_ess=40.0,
            )
            wicket_label, p_wk, fb_wk, ess_wk = self._sample_label(
                rng,
                context,
                self.wide_wicket_tables,
                WICKET_BINARY_LABELS,
                prior_alpha=self.priors["wide_wicket"],
                min_ess=40.0,
            )
            fallback_parts.extend([f"extra:{fb_extra}", f"wicket:{fb_wk}"])
            ess_parts.extend([ess_extra, ess_wk])
            probability *= p_extra * p_wk

            is_wicket = wicket_label == "Y"
            return DeliverySample(
                event_type="wide",
                is_legal_delivery=False,
                bat_runs=0,
                extra_runs=int(extra_label),
                is_wicket=is_wicket,
                wicket_type="run_out" if is_wicket else None,
                total_runs=int(extra_label),
                probability=float(min(1.0, max(0.0, probability))),
                fallback_used="|".join(fallback_parts),
                effective_sample_size=float(np.mean(ess_parts)),
            )

        bat_label, p_bat, fb_bat, ess_bat = self._sample_label(
            rng,
            context,
            self.no_ball_bat_tables,
            BAT_RUN_LABELS,
            prior_alpha=self.priors["no_ball_bat"],
            min_ess=30.0,
            adjuster=self._apply_pressure_to_bat_runs,
        )
        extra_label, p_extra, fb_extra, ess_extra = self._sample_label(
            rng,
            context,
            self.no_ball_extra_tables,
            EXTRA_RUN_LABELS,
            prior_alpha=self.priors["no_ball_extra"],
            min_ess=25.0,
        )
        wicket_label, p_wk, fb_wk, ess_wk = self._sample_label(
            rng,
            context,
            self.no_ball_wicket_tables,
            WICKET_BINARY_LABELS,
            prior_alpha=self.priors["no_ball_wicket"],
            min_ess=25.0,
        )
        fallback_parts.extend([f"bat:{fb_bat}", f"extra:{fb_extra}", f"wicket:{fb_wk}"])
        ess_parts.extend([ess_bat, ess_extra, ess_wk])
        probability *= p_bat * p_extra * p_wk

        is_wicket = wicket_label == "Y"
        bat_runs = int(bat_label)
        extra_runs = int(extra_label)
        return DeliverySample(
            event_type="no_ball",
            is_legal_delivery=False,
            bat_runs=bat_runs,
            extra_runs=extra_runs,
            is_wicket=is_wicket,
            wicket_type="run_out" if is_wicket else None,
            total_runs=bat_runs + extra_runs,
            probability=float(min(1.0, max(0.0, probability))),
            fallback_used="|".join(fallback_parts),
            effective_sample_size=float(np.mean(ess_parts)),
        )

    def sample_outcome(
        self,
        rng: np.random.Generator,
        context: SamplingContext,
    ) -> Tuple[str, float, str, float]:
        sampled = self.sample_delivery_event(rng, context)
        legacy_fallback = sampled.fallback_used.split("|")[0].split(":", 1)[-1]
        if sampled.event_type != "legal":
            return "X", sampled.probability, legacy_fallback, sampled.effective_sample_size
        if sampled.is_wicket:
            return "W", sampled.probability, legacy_fallback, sampled.effective_sample_size
        runs = sampled.bat_runs
        if runs in (0, 1, 2, 3, 4, 6):
            return str(runs), sampled.probability, legacy_fallback, sampled.effective_sample_size
        return "0", sampled.probability, legacy_fallback, sampled.effective_sample_size
