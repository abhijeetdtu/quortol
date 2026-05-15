"""Deep (non-CI) validation for simulation calibration fidelity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.src.models.team_profile import TeamProfile
from backend.src.services.data_loader import get_available_teams, load_ipl_data
from backend.src.services.simulation_engine import SimulationEngine


def _pair_list(teams: List[str], team_a: str | None, team_b: str | None) -> List[Tuple[str, str]]:
    if team_a and team_b:
        return [(team_a, team_b)]
    if len(teams) < 2:
        return []
    return [(teams[0], teams[1])]


def _safe_rel_err(sim: float, hist: float) -> float:
    if abs(hist) < 1e-9:
        return 0.0
    return abs(sim - hist) / abs(hist)


def run_validation(
    *,
    team_a: str,
    team_b: str,
    recency_bias: float,
    last_n_matches: int | None,
    stadium: str | None,
    n_runs: int,
    seed_start: int,
    tolerance: float,
) -> Dict[str, object]:
    engine = SimulationEngine()
    data = load_ipl_data()
    profile_a = TeamProfile.from_dataframe(data, team_a)
    profile_b = TeamProfile.from_dataframe(data, team_b)

    weighted = engine.feature_store.weighted_features(
        recency_bias,
        last_n_matches=last_n_matches,
        teams=[team_a, team_b],
        stadium=stadium,
    )
    calibration = engine.calibration_service.calibrate_for_matchup(weighted, team_a, team_b)

    chase_wins = 0
    rr_first = []
    rr_second = []
    ties = 0

    for i in range(n_runs):
        seed = seed_start + i
        match = engine.simulate_match(
            team_a=team_a,
            team_b=team_b,
            team_a_profile=profile_a,
            team_b_profile=profile_b,
            recency_bias=recency_bias,
            random_seed=seed,
            model_depth="full_context",
            max_fallback_level=6,
            lineup_sampling_seed=seed,
            last_n_matches=last_n_matches,
            stadium=stadium,
        )
        innings_a = match.innings[0]
        innings_b = match.innings[1]
        if innings_b.total_runs > innings_a.total_runs:
            chase_wins += 1
        elif innings_b.total_runs == innings_a.total_runs:
            ties += 1
        rr_first.append(float(innings_a.run_rate))
        rr_second.append(float(innings_b.run_rate))

    sim_chase_rate = chase_wins / max(1, n_runs)
    sim_rr_first = sum(rr_first) / max(1, len(rr_first))
    sim_rr_second = sum(rr_second) / max(1, len(rr_second))

    errors = {
        "chase_rate_abs_error": abs(sim_chase_rate - calibration.historical_chase_rate),
        "rr_first_rel_error": _safe_rel_err(sim_rr_first, calibration.historical_rr_first),
        "rr_second_rel_error": _safe_rel_err(sim_rr_second, calibration.historical_rr_second),
    }
    pass_fail = all(v <= tolerance for v in errors.values())

    return {
        "context": {
            "team_a": team_a,
            "team_b": team_b,
            "recency_bias": recency_bias,
            "last_n_matches": last_n_matches,
            "stadium": stadium,
            "n_runs": n_runs,
            "seed_start": seed_start,
        },
        "historical": {
            "chase_rate": calibration.historical_chase_rate,
            "rr_first": calibration.historical_rr_first,
            "rr_second": calibration.historical_rr_second,
            "target_bucket_chase_rates": calibration.target_bucket_chase_rates,
            "sample_matches": calibration.sample_matches,
            "source": calibration.source,
        },
        "simulated": {
            "chase_rate": sim_chase_rate,
            "rr_first": sim_rr_first,
            "rr_second": sim_rr_second,
            "tie_rate": ties / max(1, n_runs),
        },
        "errors": errors,
        "tolerance": tolerance,
        "passed": pass_fail,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deep calibration validation. Intended for manual/periodic runs (non-CI)."
    )
    parser.add_argument("--team-a", type=str, default=None)
    parser.add_argument("--team-b", type=str, default=None)
    parser.add_argument("--recency-bias", type=float, default=0.5)
    parser.add_argument("--last-n-matches", type=int, default=None)
    parser.add_argument("--stadium", type=str, default=None)
    parser.add_argument("--n-runs", type=int, default=120)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--tolerance", type=float, default=0.15)
    parser.add_argument("--output-json", type=str, default="")
    args = parser.parse_args()

    data = load_ipl_data()
    teams = get_available_teams(data)
    pairs = _pair_list(teams, args.team_a, args.team_b)
    if not pairs:
        print("No valid team pairs found.")
        return 2

    reports = []
    overall_passed = True
    for team_a, team_b in pairs:
        report = run_validation(
            team_a=team_a,
            team_b=team_b,
            recency_bias=float(args.recency_bias),
            last_n_matches=args.last_n_matches,
            stadium=args.stadium,
            n_runs=int(args.n_runs),
            seed_start=int(args.seed_start),
            tolerance=float(args.tolerance),
        )
        reports.append(report)
        overall_passed = overall_passed and bool(report["passed"])

    output = {"reports": reports, "overall_passed": overall_passed}
    text = json.dumps(output, indent=2)
    print(text)

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
