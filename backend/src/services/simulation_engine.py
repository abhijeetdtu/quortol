"""Simulation engine for full-context matchup-aware ball-by-ball simulation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..models.delivery import DeliveryOutcome
from ..models.innings import Innings
from ..models.match_simulation import SimulatedMatch
from ..models.team_profile import TeamProfile
from .calibration import CalibrationProfile, CalibrationService
from .feature_store import WeightedFeatureStore
from .probability_model import ProbabilityModel, SamplingContext


@dataclass(frozen=True)
class PreparedSimulationContext:
    """Reusable, precomputed simulation artifacts for repeated runs."""

    weighted_df: pd.DataFrame
    fallback_weighted_df: pd.DataFrame
    model: ProbabilityModel
    calibration: CalibrationProfile
    baseline_rr: Dict[str, float]
    selected_stadium: Optional[str]
    venue_filter_applied: bool
    last_n_matches: Optional[int]


@dataclass
class ChaseStateSnapshot:
    """Serializable innings-2 state used for counterfactual continuation rollouts."""

    legal_ball: int
    score: int
    wickets_lost: int
    runs_needed: int
    balls_left: int
    wickets_in_hand: int
    striker_idx: int
    non_striker_idx: int
    next_batter_idx: int
    balls_in_over: int
    current_bowler: str
    previous_bowler: Optional[str]
    legal_balls_bowled: Dict[str, int]
    target: int
    batting_team: str
    bowling_team: str
    batting_lineup: List[str]
    bowling_pool: List[Tuple[str, float, str]]
    bowling_plan: Dict[str, int]
    baseline_rr: float

    def to_dict(self) -> dict:
        return {
            "legal_ball": int(self.legal_ball),
            "score": int(self.score),
            "wickets_lost": int(self.wickets_lost),
            "runs_needed": int(self.runs_needed),
            "balls_left": int(self.balls_left),
            "wickets_in_hand": int(self.wickets_in_hand),
            "striker_idx": int(self.striker_idx),
            "non_striker_idx": int(self.non_striker_idx),
            "next_batter_idx": int(self.next_batter_idx),
            "balls_in_over": int(self.balls_in_over),
            "current_bowler": str(self.current_bowler),
            "previous_bowler": str(self.previous_bowler) if self.previous_bowler is not None else None,
            "legal_balls_bowled": {str(k): int(v) for k, v in self.legal_balls_bowled.items()},
            "target": int(self.target),
            "batting_team": str(self.batting_team),
            "bowling_team": str(self.bowling_team),
            "batting_lineup": [str(v) for v in self.batting_lineup],
            "bowling_pool": [(str(name), float(weight), str(role)) for name, weight, role in self.bowling_pool],
            "bowling_plan": {str(k): int(v) for k, v in self.bowling_plan.items()},
            "baseline_rr": float(self.baseline_rr),
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "ChaseStateSnapshot":
        bowling_pool = []
        for row in raw.get("bowling_pool", []):
            if isinstance(row, (list, tuple)) and len(row) == 3:
                bowling_pool.append((str(row[0]), float(row[1]), str(row[2])))
        return cls(
            legal_ball=int(raw.get("legal_ball", 0)),
            score=int(raw.get("score", 0)),
            wickets_lost=int(raw.get("wickets_lost", 0)),
            runs_needed=int(raw.get("runs_needed", 0)),
            balls_left=int(raw.get("balls_left", 0)),
            wickets_in_hand=int(raw.get("wickets_in_hand", 0)),
            striker_idx=int(raw.get("striker_idx", 0)),
            non_striker_idx=int(raw.get("non_striker_idx", 1)),
            next_batter_idx=int(raw.get("next_batter_idx", 2)),
            balls_in_over=int(raw.get("balls_in_over", 0)),
            current_bowler=str(raw.get("current_bowler", "")),
            previous_bowler=(str(raw.get("previous_bowler")) if raw.get("previous_bowler") is not None else None),
            legal_balls_bowled={str(k): int(v) for k, v in dict(raw.get("legal_balls_bowled", {})).items()},
            target=int(raw.get("target", 0)),
            batting_team=str(raw.get("batting_team", "")),
            bowling_team=str(raw.get("bowling_team", "")),
            batting_lineup=[str(v) for v in list(raw.get("batting_lineup", []))],
            bowling_pool=bowling_pool,
            bowling_plan={str(k): int(v) for k, v in dict(raw.get("bowling_plan", {})).items()},
            baseline_rr=float(raw.get("baseline_rr", 8.0)),
        )


class SimulationEngine:
    """Full-context ball-by-ball simulation engine."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.feature_store = WeightedFeatureStore()
        self.calibration_service = CalibrationService()

    @staticmethod
    def _phase_from_legal_ball(legal_ball_number: int) -> str:
        over = (max(1, legal_ball_number) - 1) // 6
        if over <= 5:
            return "powerplay"
        if over <= 15:
            return "middle"
        return "death"

    @staticmethod
    def _wickets_band(wickets: int) -> str:
        if wickets <= 2:
            return "low"
        if wickets <= 5:
            return "medium"
        return "high"

    @staticmethod
    def _pressure_band(required_rr: float, baseline_rr: float) -> str:
        delta = required_rr - baseline_rr
        if delta >= 1.5:
            return "high"
        if delta <= -1.5:
            return "low"
        return "medium"

    @staticmethod
    def _role_for_position(position: int) -> str:
        if position <= 2:
            return "top"
        if position <= 5:
            return "middle"
        return "lower"

    def _sample_batting_lineup(
        self,
        weighted_df: pd.DataFrame,
        batting_team: str,
        bowling_team: str,
        rng: np.random.Generator,
        fallback_weighted_df: Optional[pd.DataFrame] = None,
    ) -> List[str]:
        subset_vs_opp = weighted_df[
            (weighted_df["batting_team"] == batting_team)
            & (weighted_df["bowling_team"] == bowling_team)
        ]
        subset_team = weighted_df[weighted_df["batting_team"] == batting_team]
        subset = subset_vs_opp if not subset_vs_opp.empty else subset_team

        candidates = (
            subset.groupby("Batter", as_index=False)
            .agg(weight=("season_weight", "sum"), first_ball=("ball_index", "mean"))
            .sort_values(["first_ball", "weight"], ascending=[True, False])
        )
        candidates = candidates[candidates["Batter"].astype(str).str.strip() != ""].copy()

        # If matchup slice has too few unique names, backfill from team-global batters.
        if len(candidates) < 11 and not subset_team.empty:
            team_candidates = (
                subset_team.groupby("Batter", as_index=False)
                .agg(weight=("season_weight", "sum"), first_ball=("ball_index", "mean"))
                .sort_values(["first_ball", "weight"], ascending=[True, False])
            )
            team_candidates = team_candidates[team_candidates["Batter"].astype(str).str.strip() != ""].copy()
            missing = team_candidates[~team_candidates["Batter"].isin(set(candidates["Batter"].tolist()))]
            if not missing.empty:
                candidates = (
                    pd.concat([candidates, missing], ignore_index=True)
                    .groupby("Batter", as_index=False)
                    .agg(weight=("weight", "sum"), first_ball=("first_ball", "mean"))
                    .sort_values(["first_ball", "weight"], ascending=[True, False])
                )

        # Last-resort backfill from broader history (e.g., old franchises dropped by last_n window).
        if len(candidates) < 11 and fallback_weighted_df is not None and not fallback_weighted_df.empty:
            fb_team = fallback_weighted_df[fallback_weighted_df["batting_team"] == batting_team]
            if not fb_team.empty:
                fb_candidates = (
                    fb_team.groupby("Batter", as_index=False)
                    .agg(weight=("season_weight", "sum"), first_ball=("ball_index", "mean"))
                    .sort_values(["first_ball", "weight"], ascending=[True, False])
                )
                fb_candidates = fb_candidates[fb_candidates["Batter"].astype(str).str.strip() != ""].copy()
                missing = fb_candidates[~fb_candidates["Batter"].isin(set(candidates["Batter"].tolist()))]
                if not missing.empty:
                    candidates = (
                        pd.concat([candidates, missing], ignore_index=True)
                        .groupby("Batter", as_index=False)
                        .agg(weight=("weight", "sum"), first_ball=("first_ball", "mean"))
                        .sort_values(["first_ball", "weight"], ascending=[True, False])
                    )

        if candidates.empty:
            return [f"{batting_team} Batter {i}" for i in range(1, 12)]

        top = candidates.head(24).copy()
        # Build a stable batting core first, then sample fringe players.
        top["core_score"] = top["weight"] / top["first_ball"].clip(lower=1.0)
        core = (
            top.sort_values(["core_score", "first_ball", "weight"], ascending=[False, True, False])
            .head(min(7, len(top)))
            .copy()
        )
        core_names = core["Batter"].tolist()

        remaining = top[~top["Batter"].isin(core_names)].copy()
        lineup = list(core_names)
        remaining_slots = max(0, 11 - len(lineup))
        if remaining_slots > 0 and not remaining.empty:
            probs = remaining["weight"].to_numpy(dtype=float)
            probs = probs / probs.sum()
            sample_size = min(remaining_slots, len(remaining))
            picks = rng.choice(remaining.index.to_numpy(), size=sample_size, replace=False, p=probs)
            sampled = remaining.loc[picks]["Batter"].tolist()
            lineup.extend(sampled)

        lineup = (
            top[top["Batter"].isin(lineup)]
            .drop_duplicates(subset=["Batter"])
            .sort_values(["first_ball", "weight"], ascending=[True, False])["Batter"]
            .tolist()
        )

        while len(lineup) < 11:
            lineup.append(f"{batting_team} Batter {len(lineup) + 1}")
        return lineup[:11]

    def _build_bowling_pool(
        self,
        weighted_df: pd.DataFrame,
        bowling_team: str,
        batting_team: str,
    ) -> List[Tuple[str, float, str]]:
        subset = weighted_df[
            (weighted_df["bowling_team"] == bowling_team)
            & (weighted_df["batting_team"] == batting_team)
        ]
        if subset.empty:
            subset = weighted_df[weighted_df["bowling_team"] == bowling_team]

        frame = (
            subset.groupby("Bowler", as_index=False)
            .agg(
                weight=("season_weight", "sum"),
                role=("bowler_role", lambda s: s.mode().iloc[0] if not s.mode().empty else "support"),
            )
            .sort_values("weight", ascending=False)
        )
        if frame.empty:
            return [(f"{bowling_team} Bowler {i}", 1.0, "support") for i in range(1, 7)]

        return [(str(r.Bowler), float(r.weight), str(r.role)) for r in frame.head(7).itertuples()]

    def _build_bowling_plan(
        self,
        bowling_pool: List[Tuple[str, float, str]],
    ) -> Dict[str, int]:
        """Assign target legal balls (6-ball increments) per bowler."""
        if not bowling_pool:
            return {}

        roles = {name: role for name, _w, role in bowling_pool}
        weights = {name: max(1e-6, w) for name, w, _r in bowling_pool}
        overs_assigned = {name: 0 for name, _w, _r in bowling_pool}
        remaining_overs = 20

        primaries = [name for name, _w, role in bowling_pool if role == "primary"]
        supports = [name for name, _w, role in bowling_pool if role == "support"]

        for name in primaries[:3]:
            overs_assigned[name] = min(4, overs_assigned[name] + 2)
            remaining_overs -= 2

        for name in supports[:2]:
            if remaining_overs <= 0:
                break
            if overs_assigned[name] < 4:
                overs_assigned[name] += 1
                remaining_overs -= 1

        def _role_bonus(role: str) -> float:
            if role == "primary":
                return 1.35
            if role == "support":
                return 1.10
            return 0.85

        while remaining_overs > 0:
            candidates = [name for name in overs_assigned if overs_assigned[name] < 4]
            if not candidates:
                break
            best = max(
                candidates,
                key=lambda name: (weights[name] * _role_bonus(roles.get(name, "support"))) / (1.0 + 0.9 * overs_assigned[name]),
            )
            overs_assigned[best] += 1
            remaining_overs -= 1

        return {name: overs * 6 for name, overs in overs_assigned.items()}

    def _select_bowler_for_over(
        self,
        bowling_pool: List[Tuple[str, float, str]],
        legal_balls_bowled: Dict[str, int],
        target_legal_balls: Dict[str, int],
        previous_bowler: Optional[str],
        phase: str,
        rng: np.random.Generator,
    ) -> str:
        candidates: List[str] = []
        weights: List[float] = []

        for bowler, base_weight, role in bowling_pool:
            legal_used = legal_balls_bowled.get(bowler, 0)
            if legal_used >= 24:
                continue
            if previous_bowler == bowler:
                continue
            target = target_legal_balls.get(bowler, 12)
            target_remaining = max(0, target - legal_used)
            remaining_factor = max(0.55, (24 - legal_used) / 24)
            target_factor = 1.0 + min(1.8, target_remaining / 6.0)
            phase_factor = 1.0
            if phase == "death" and role == "primary":
                phase_factor = 1.45
            elif phase == "powerplay" and role == "part_time":
                phase_factor = 0.45
            elif phase == "middle" and role == "support":
                phase_factor = 1.1

            candidates.append(bowler)
            weights.append(base_weight * remaining_factor * phase_factor * target_factor)

        if not candidates:
            for bowler, base_weight, _ in bowling_pool:
                if legal_balls_bowled.get(bowler, 0) < 24:
                    candidates.append(bowler)
                    target = target_legal_balls.get(bowler, 12)
                    gap = max(0, target - legal_balls_bowled.get(bowler, 0))
                    weights.append(base_weight * (1.0 + min(1.2, gap / 6.0)))

        if not candidates:
            return bowling_pool[0][0]

        probs = np.array(weights, dtype=float)
        probs /= probs.sum()
        return str(rng.choice(np.array(candidates), p=probs))

    def prepare_match_context(
        self,
        *,
        team_a: str,
        team_b: str,
        recency_bias: float,
        max_fallback_level: int,
        last_n_matches: Optional[int],
        stadium: Optional[str],
    ) -> PreparedSimulationContext:
        """Prepare model/data once so callers can reuse it across many seeds."""
        teams_scope = [team_a, team_b]
        selected_stadium = str(stadium).strip() if stadium is not None else ""
        selected_stadium = selected_stadium or None

        weighted_df = self.feature_store.weighted_features(
            recency_bias,
            last_n_matches=last_n_matches,
            teams=teams_scope,
            stadium=selected_stadium,
        )
        venue_filter_applied = selected_stadium is not None
        if selected_stadium is not None and weighted_df.empty:
            raise ValueError(
                f"No historical delivery data found for stadium '{selected_stadium}' "
                f"with the selected teams/window."
            )

        fallback_weighted_df = (
            self.feature_store.weighted_features(
                recency_bias,
                last_n_matches=None,
                teams=teams_scope,
                stadium=selected_stadium,
            )
            if last_n_matches is not None
            else weighted_df
        )

        calibration = self.calibration_service.calibrate_for_matchup(weighted_df, team_a, team_b)
        model = ProbabilityModel(
            feature_store=self.feature_store,
            recency_bias=recency_bias,
            max_fallback_level=max_fallback_level,
            last_n_matches=last_n_matches,
            teams=teams_scope,
            stadium=selected_stadium,
            calibration_profile=calibration,
        )

        baseline_rr = (
            weighted_df.groupby("batting_team", as_index=False)["TotalRun"].mean()
            .assign(rr=lambda d: d["TotalRun"] * 6.0)
            .set_index("batting_team")["rr"]
            .to_dict()
        )
        return PreparedSimulationContext(
            weighted_df=weighted_df,
            fallback_weighted_df=fallback_weighted_df,
            model=model,
            calibration=calibration,
            baseline_rr=baseline_rr,
            selected_stadium=selected_stadium,
            venue_filter_applied=venue_filter_applied,
            last_n_matches=last_n_matches,
        )

    def _simulate_chase_continuation(
        self,
        snapshot: ChaseStateSnapshot,
        *,
        model: ProbabilityModel,
        calibration: CalibrationProfile,
        rng: np.random.Generator,
    ) -> float:
        """Resume innings-2 from a snapshot and return chase outcome as 1/0.5/0."""
        if snapshot.target <= 0:
            return 0.0
        if snapshot.score >= snapshot.target:
            return 1.0
        if snapshot.wickets_lost >= 10 or snapshot.legal_ball >= 120:
            return 0.5 if snapshot.score == (snapshot.target - 1) else 0.0

        score = int(snapshot.score)
        wickets = int(snapshot.wickets_lost)
        striker_idx = int(snapshot.striker_idx)
        non_striker_idx = int(snapshot.non_striker_idx)
        next_batter_idx = int(snapshot.next_batter_idx)
        legal_balls = int(snapshot.legal_ball)
        balls_in_over = int(snapshot.balls_in_over)
        current_bowler = str(snapshot.current_bowler)
        previous_bowler = snapshot.previous_bowler
        legal_balls_bowled = {str(k): int(v) for k, v in snapshot.legal_balls_bowled.items()}

        batting_lineup = snapshot.batting_lineup or [f"{snapshot.batting_team} Batter {i}" for i in range(1, 12)]
        bowling_pool = snapshot.bowling_pool or [(f"{snapshot.bowling_team} Bowler {i}", 1.0, "support") for i in range(1, 7)]
        bowling_plan = dict(snapshot.bowling_plan)
        batting_positions = {name: idx + 1 for idx, name in enumerate(batting_lineup)}
        bowler_roles = {name: role for name, _weight, role in bowling_pool}

        target = int(snapshot.target)
        baseline_rr = float(snapshot.baseline_rr)
        par_target_runs = max(80, int(round(calibration.historical_rr_first * 20.0)))

        while legal_balls < 120 and wickets < 10:
            if score >= target:
                break

            phase = self._phase_from_legal_ball(legal_balls + 1)
            if balls_in_over == 0:
                current_bowler = self._select_bowler_for_over(
                    bowling_pool=bowling_pool,
                    legal_balls_bowled=legal_balls_bowled,
                    target_legal_balls=bowling_plan,
                    previous_bowler=previous_bowler,
                    phase=phase,
                    rng=rng,
                )
                previous_bowler = current_bowler

            striker = batting_lineup[min(striker_idx, len(batting_lineup) - 1)]
            wickets_band = self._wickets_band(wickets)
            wickets_in_hand = max(0, 10 - wickets)

            balls_remaining = max(1, 120 - legal_balls)
            required_runs = max(0, target - score)
            if target > 0:
                required_rr = (required_runs * 6.0) / balls_remaining
            else:
                required_rr = (max(0, par_target_runs - score) * 6.0) / balls_remaining
            pressure_band = self._pressure_band(required_rr, baseline_rr)

            sampling_context = SamplingContext(
                batting_team=snapshot.batting_team,
                bowling_team=snapshot.bowling_team,
                batter_role=self._role_for_position(batting_positions.get(striker, striker_idx + 1)),
                bowler_role=bowler_roles.get(current_bowler, "support"),
                phase=phase,
                wickets_band=wickets_band,
                pressure_band=pressure_band,
                innings_number=2,
                wickets_in_hand=wickets_in_hand,
                required_run_rate=required_rr,
                baseline_rr=baseline_rr,
            )

            sampled = model.sample_delivery_event(rng, sampling_context)
            bat_runs = sampled.bat_runs
            extra_runs = sampled.extra_runs
            if sampled.is_wicket and sampled.event_type == "legal" and sampled.wicket_type != "run_out":
                bat_runs = 0
            runs = bat_runs + extra_runs
            score += runs

            if sampled.is_legal_delivery:
                legal_balls += 1
                balls_in_over += 1
                legal_balls_bowled[current_bowler] = legal_balls_bowled.get(current_bowler, 0) + 1

            if sampled.is_wicket:
                wickets += 1
                if next_batter_idx < len(batting_lineup):
                    striker_idx = next_batter_idx
                    next_batter_idx += 1

            if runs % 2 == 1 and wickets < 10:
                striker_idx, non_striker_idx = non_striker_idx, striker_idx

            if sampled.is_legal_delivery and balls_in_over == 6:
                striker_idx, non_striker_idx = non_striker_idx, striker_idx
                balls_in_over = 0

        if score >= target:
            return 1.0
        if score == (target - 1):
            return 0.5
        return 0.0

    def estimate_chase_win_probability_from_snapshot(
        self,
        snapshot: ChaseStateSnapshot,
        *,
        context: PreparedSimulationContext,
        rollouts: int,
        random_seed: int,
    ) -> float:
        """Estimate P(chasing team wins | snapshot state) with continuation Monte Carlo."""
        k = max(1, int(rollouts))
        wins = 0.0
        for idx in range(k):
            seed = int(random_seed) + idx
            rng = np.random.default_rng(seed)
            wins += self._simulate_chase_continuation(
                snapshot,
                model=context.model,
                calibration=context.calibration,
                rng=rng,
            )
        return float(wins / k)

    def simulate_match(
        self,
        team_a: str,
        team_b: str,
        team_a_profile: TeamProfile,
        team_b_profile: TeamProfile,
        recency_bias: float = 0.5,
        random_seed: int = 42,
        model_depth: str = "full_context",
        max_fallback_level: int = 6,
        lineup_sampling_seed: Optional[int] = None,
        last_n_matches: Optional[int] = None,
        realism_version: str = "enhanced_v1",
        stadium: Optional[str] = None,
        prepared_context: Optional[PreparedSimulationContext] = None,
        collect_chase_snapshots: bool = False,
    ) -> SimulatedMatch:
        rng = np.random.default_rng(random_seed)
        lineup_rng = np.random.default_rng(lineup_sampling_seed if lineup_sampling_seed is not None else random_seed)

        context = prepared_context or self.prepare_match_context(
            team_a=team_a,
            team_b=team_b,
            recency_bias=recency_bias,
            max_fallback_level=max_fallback_level,
            last_n_matches=last_n_matches,
            stadium=stadium,
        )
        weighted_df = context.weighted_df
        fallback_weighted_df = context.fallback_weighted_df
        model = context.model
        calibration = context.calibration
        baseline_rr = context.baseline_rr
        selected_stadium = context.selected_stadium
        venue_filter_applied = context.venue_filter_applied

        lineup_a = self._sample_batting_lineup(
            weighted_df,
            team_a,
            team_b,
            lineup_rng,
            fallback_weighted_df=fallback_weighted_df,
        )
        bowlers_b = self._build_bowling_pool(weighted_df, team_b, team_a)
        bowling_plan_b = self._build_bowling_plan(bowlers_b)
        lineup_b = self._sample_batting_lineup(
            weighted_df,
            team_b,
            team_a,
            lineup_rng,
            fallback_weighted_df=fallback_weighted_df,
        )
        bowlers_a = self._build_bowling_pool(weighted_df, team_a, team_b)
        bowling_plan_a = self._build_bowling_plan(bowlers_a)

        match = SimulatedMatch(
            team_a=team_a,
            team_b=team_b,
            recency_bias=recency_bias,
            random_seed=random_seed,
            created_at=datetime.now(timezone.utc),
        )

        innings_1, diag_1 = self._simulate_innings(
            batting_team=team_a,
            bowling_team=team_b,
            batting_lineup=lineup_a,
            bowling_pool=bowlers_b,
            bowling_plan=bowling_plan_b,
            model=model,
            rng=rng,
            innings_number=1,
            target=None,
            baseline_rr=baseline_rr.get(team_a, max(team_a_profile.avg_run_rate, 1.0)),
            calibration=calibration,
        )
        match.add_innings(innings_1)

        target = innings_1.total_runs + 1
        innings_2, diag_2 = self._simulate_innings(
            batting_team=team_b,
            bowling_team=team_a,
            batting_lineup=lineup_b,
            bowling_pool=bowlers_a,
            bowling_plan=bowling_plan_a,
            model=model,
            rng=rng,
            innings_number=2,
            target=target,
            baseline_rr=baseline_rr.get(team_b, max(team_b_profile.avg_run_rate, 1.0)),
            calibration=calibration,
            collect_chase_snapshots=collect_chase_snapshots,
        )
        match.add_innings(innings_2)

        match.result = match.calculate_result()
        match.status = "completed"

        combined_context_usage = dict(Counter(diag_1["context_usage"]) + Counter(diag_2["context_usage"]))
        combined_wicket_types = dict(Counter(diag_1["wicket_types"]) + Counter(diag_2["wicket_types"]))
        total_events = diag_1["total_events"] + diag_2["total_events"]
        total_legal_balls = diag_1["legal_balls"] + diag_2["legal_balls"]
        total_extras = diag_1["extras_runs"] + diag_2["extras_runs"]
        total_boundaries = diag_1["boundaries"] + diag_2["boundaries"]

        match.metadata = {
            "model_depth": model_depth,
            "max_fallback_level": max_fallback_level,
            "lineup_sampling_seed": lineup_sampling_seed if lineup_sampling_seed is not None else random_seed,
            "last_n_matches": int(context.last_n_matches) if context.last_n_matches is not None else None,
            "stadium": selected_stadium,
            "venue_filter_applied": venue_filter_applied,
            "realism_version": realism_version,
            "calibration": calibration.to_metadata(max_fallback_level),
            "diagnostics": {
                "context_usage": combined_context_usage,
                "effective_sample_size_avg": float(
                    np.mean(diag_1["effective_sample_sizes"] + diag_2["effective_sample_sizes"])
                )
                if (diag_1["effective_sample_sizes"] or diag_2["effective_sample_sizes"])
                else 0.0,
            },
            "realism_diagnostics": {
                "total_events": total_events,
                "legal_ball_count": total_legal_balls,
                "extras_runs": total_extras,
                "extras_rate": float(total_extras / max(1, total_events)),
                "boundary_rate": float(total_boundaries / max(1, total_legal_balls)),
                "wicket_type_distribution": combined_wicket_types,
                "fallback_usage": combined_context_usage,
            },
            "lineups": {
                team_a: lineup_a,
                team_b: lineup_b,
            },
            "bowling_plan": {
                team_b: {k: int(v / 6) for k, v in bowling_plan_b.items()},
                team_a: {k: int(v / 6) for k, v in bowling_plan_a.items()},
            },
        }
        if collect_chase_snapshots:
            match.metadata["counterfactual"] = {
                "chase_snapshots": list(diag_2.get("chase_snapshots", [])),
            }
        return match

    def _simulate_innings(
        self,
        batting_team: str,
        bowling_team: str,
        batting_lineup: List[str],
        bowling_pool: List[Tuple[str, float, str]],
        bowling_plan: Dict[str, int],
        model: ProbabilityModel,
        rng: np.random.Generator,
        innings_number: int,
        baseline_rr: float,
        target: Optional[int] = None,
        calibration: Optional[CalibrationProfile] = None,
        collect_chase_snapshots: bool = False,
    ) -> Tuple[Innings, Dict[str, object]]:
        innings = Innings(innings_number=innings_number, batting_team=batting_team)

        score = 0
        wickets = 0
        striker_idx = 0
        non_striker_idx = 1
        next_batter_idx = 2
        partnership_runs = 0
        legal_balls = 0
        total_events = 0
        balls_in_over = 0

        batting_positions = {name: idx + 1 for idx, name in enumerate(batting_lineup)}
        bowler_roles = {name: role for name, _weight, role in bowling_pool}

        context_usage: List[str] = []
        ess_values: List[float] = []
        wicket_types: List[str] = []
        chase_snapshots: List[dict] = []

        legal_balls_bowled: Dict[str, int] = {b: 0 for b, _, _ in bowling_pool}
        current_bowler = bowling_pool[0][0]
        previous_bowler: Optional[str] = None

        extras_runs_total = 0
        boundaries = 0
        calibration = calibration or CalibrationProfile(
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
        par_target_runs = max(80, int(round(calibration.historical_rr_first * 20.0)))

        while legal_balls < 120 and wickets < 10:
            if target is not None and score >= target:
                break

            phase = self._phase_from_legal_ball(legal_balls + 1)
            if balls_in_over == 0:
                current_bowler = self._select_bowler_for_over(
                    bowling_pool=bowling_pool,
                    legal_balls_bowled=legal_balls_bowled,
                    target_legal_balls=bowling_plan,
                    previous_bowler=previous_bowler,
                    phase=phase,
                    rng=rng,
                )
                previous_bowler = current_bowler

            striker = batting_lineup[min(striker_idx, len(batting_lineup) - 1)]
            non_striker = batting_lineup[min(non_striker_idx, len(batting_lineup) - 1)]
            wickets_band = self._wickets_band(wickets)
            wickets_in_hand = max(0, 10 - wickets)

            balls_remaining = max(1, 120 - legal_balls)
            required_rr = 0.0
            if target is not None:
                required_runs = max(0, target - score)
                required_rr = (required_runs * 6.0) / balls_remaining
                pressure_band = self._pressure_band(required_rr, baseline_rr)
            else:
                required_runs = max(0, par_target_runs - score)
                required_rr = (required_runs * 6.0) / balls_remaining
                pressure_band = self._pressure_band(required_rr, baseline_rr)

            sampling_context = SamplingContext(
                batting_team=batting_team,
                bowling_team=bowling_team,
                batter_role=self._role_for_position(batting_positions.get(striker, striker_idx + 1)),
                bowler_role=bowler_roles.get(current_bowler, "support"),
                phase=phase,
                wickets_band=wickets_band,
                pressure_band=pressure_band,
                innings_number=innings_number,
                wickets_in_hand=wickets_in_hand,
                required_run_rate=required_rr,
                baseline_rr=baseline_rr,
            )

            sampled = model.sample_delivery_event(rng, sampling_context)
            total_events += 1

            bat_runs = sampled.bat_runs
            extra_runs = sampled.extra_runs
            if sampled.is_wicket and sampled.event_type == "legal" and sampled.wicket_type != "run_out":
                # Most legal dismissals do not add batting runs on the wicket ball.
                bat_runs = 0
            runs = bat_runs + extra_runs
            score += runs
            partnership_runs += runs
            extras_runs_total += extra_runs
            if bat_runs in (4, 6):
                boundaries += 1

            legal_ball_number = legal_balls
            ball_in_over = balls_in_over
            if sampled.is_legal_delivery:
                legal_balls += 1
                balls_in_over += 1
                legal_balls_bowled[current_bowler] = legal_balls_bowled.get(current_bowler, 0) + 1
                legal_ball_number = legal_balls
                ball_in_over = balls_in_over

            if sampled.is_wicket:
                wickets += 1
                partnership_runs = 0
                wicket_types.append(sampled.wicket_type or "other")
                if next_batter_idx < len(batting_lineup):
                    striker_idx = next_batter_idx
                    next_batter_idx += 1

            # Strike can rotate on odd totals even for non-legal events.
            if runs % 2 == 1 and wickets < 10:
                striker_idx, non_striker_idx = non_striker_idx, striker_idx

            if sampled.is_legal_delivery and balls_in_over == 6:
                striker_idx, non_striker_idx = non_striker_idx, striker_idx
                balls_in_over = 0

            delivery = DeliveryOutcome(
                ball_number=total_events,
                runs=runs,
                is_wicket=sampled.is_wicket,
                wicket_type=sampled.wicket_type,
                is_extra=sampled.extra_runs > 0,
                extra_type=sampled.event_type if sampled.event_type != "legal" else None,
                cumulative_score=score,
                cumulative_wickets=wickets,
                probability=sampled.probability,
                event_type=sampled.event_type,
                is_legal_delivery=sampled.is_legal_delivery,
                bat_runs=bat_runs,
                extra_runs=extra_runs,
                legal_ball_number=legal_ball_number,
                over_number=legal_balls // 6,
                ball_in_over=ball_in_over,
                batter=striker,
                non_striker=non_striker,
                bowler=current_bowler,
                phase=phase,
                wickets_in_hand=wickets_in_hand,
                required_run_rate=required_rr,
                pressure_band=pressure_band,
                partnership_runs=partnership_runs,
                context_level_used=sampled.fallback_used,
                effective_sample_size=sampled.effective_sample_size,
            )
            innings.add_delivery(delivery)

            context_usage.append(sampled.fallback_used)
            ess_values.append(sampled.effective_sample_size)
            if collect_chase_snapshots and target is not None and sampled.is_legal_delivery:
                snapshot = ChaseStateSnapshot(
                    legal_ball=legal_balls,
                    score=score,
                    wickets_lost=wickets,
                    runs_needed=max(0, target - score),
                    balls_left=max(0, 120 - legal_balls),
                    wickets_in_hand=max(0, 10 - wickets),
                    striker_idx=striker_idx,
                    non_striker_idx=non_striker_idx,
                    next_batter_idx=next_batter_idx,
                    balls_in_over=balls_in_over,
                    current_bowler=current_bowler,
                    previous_bowler=previous_bowler,
                    legal_balls_bowled=dict(legal_balls_bowled),
                    target=target,
                    batting_team=batting_team,
                    bowling_team=bowling_team,
                    batting_lineup=list(batting_lineup),
                    bowling_pool=[(str(name), float(weight), str(role)) for name, weight, role in bowling_pool],
                    bowling_plan={str(k): int(v) for k, v in bowling_plan.items()},
                    baseline_rr=float(baseline_rr),
                )
                chase_snapshots.append(snapshot.to_dict())

        return innings, {
            "context_usage": context_usage,
            "effective_sample_sizes": ess_values,
            "wicket_types": wicket_types,
            "total_events": total_events,
            "legal_balls": legal_balls,
            "extras_runs": extras_runs_total,
            "boundaries": boundaries,
            "chase_snapshots": chase_snapshots,
        }
