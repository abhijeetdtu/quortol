"""Flask REST API routes for Ball-by-Ball Match Simulation."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from threading import Lock, Thread
from typing import Any, Dict

from flask import Flask, jsonify, request

from ..models.team_profile import TeamProfile
from ..services.data_loader import DataLoadError, get_available_teams, load_ipl_data
from ..services.error_handler import log_simulation_error, setup_error_handler
from ..services.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

active_simulations: Dict[str, Dict[str, Any]] = {}
simulation_lock = Lock()
simulation_engine = SimulationEngine()


def run_simulation(match_id: str) -> None:
    with simulation_lock:
        sim = active_simulations.get(match_id)
        if sim is None:
            logger.error("Simulation %s not found in active_simulations", match_id)
            return
        sim_request = sim.copy()

    try:
        team_a = sim_request["team_a"]
        team_b = sim_request["team_b"]
        recency_bias = float(sim_request["recency_bias"])
        random_seed = int(sim_request["random_seed"])
        model_depth = str(sim_request.get("model_depth", "full_context"))
        max_fallback_level = int(sim_request.get("max_fallback_level", 6))
        realism_version = str(sim_request.get("realism_version", "enhanced_v1"))
        stadium = sim_request.get("stadium")
        stadium = str(stadium).strip() if stadium is not None else None
        stadium = stadium or None
        lineup_sampling_seed = sim_request.get("lineup_sampling_seed")
        lineup_sampling_seed = int(lineup_sampling_seed) if lineup_sampling_seed is not None else None

        df = load_ipl_data()
        team_a_profile = TeamProfile.from_dataframe(df, team_a)
        team_b_profile = TeamProfile.from_dataframe(df, team_b)

        match = simulation_engine.simulate_match(
            team_a=team_a,
            team_b=team_b,
            team_a_profile=team_a_profile,
            team_b_profile=team_b_profile,
            recency_bias=recency_bias,
            random_seed=random_seed,
            model_depth=model_depth,
            max_fallback_level=max_fallback_level,
            lineup_sampling_seed=lineup_sampling_seed,
            realism_version=realism_version,
            stadium=stadium,
        )

        low_confidence = team_a_profile.total_matches < 3 or team_b_profile.total_matches < 3
        warning_msg = (
            "Low-confidence simulation: one or both teams have fewer than 3 historical matches."
            if low_confidence
            else ""
        )

        with simulation_lock:
            active_simulations[match_id] = {
                **sim_request,
                **match.to_dict(),
                "status": "completed",
                "low_confidence_warning": warning_msg,
            }
    except Exception as exc:
        log_simulation_error(match_id, exc)
        with simulation_lock:
            if match_id in active_simulations:
                active_simulations[match_id]["status"] = "failed"
                active_simulations[match_id]["error"] = str(exc)


def create_app() -> Flask:
    app = Flask(__name__)
    setup_error_handler(app)
    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.route("/api/teams", methods=["GET"])
    def get_teams() -> Any:
        try:
            df = load_ipl_data()
            teams = get_available_teams(df)
            return jsonify({"teams": teams}), 200
        except DataLoadError as exc:
            logger.error("Failed to load teams: %s", str(exc))
            return jsonify({"error": "Data Error", "message": str(exc)}), 500

    @app.route("/api/simulate", methods=["POST"])
    def simulate() -> Any:
        try:
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Bad Request", "message": "Request body must be JSON"}), 400

            team_a = str(data.get("team_a", "")).strip()
            team_b = str(data.get("team_b", "")).strip()

            try:
                recency_bias = float(data.get("recency_bias", 0.5))
            except (TypeError, ValueError):
                return jsonify({"error": "Bad Request", "message": "recency_bias must be a number between 0.0 and 1.0"}), 400

            try:
                random_seed = int(data.get("random_seed", 42))
            except (TypeError, ValueError):
                return jsonify({"error": "Bad Request", "message": "random_seed must be a non-negative integer"}), 400

            model_depth = str(data.get("model_depth", "full_context")).strip() or "full_context"
            stadium = str(data.get("stadium", "")).strip() or None
            try:
                max_fallback_level = int(data.get("max_fallback_level", 6))
            except (TypeError, ValueError):
                return jsonify({"error": "Bad Request", "message": "max_fallback_level must be an integer between 0 and 6"}), 400
            realism_version = str(data.get("realism_version", "enhanced_v1")).strip() or "enhanced_v1"

            lineup_sampling_seed_raw = data.get("lineup_sampling_seed", None)
            if lineup_sampling_seed_raw is None:
                lineup_sampling_seed = random_seed
            else:
                try:
                    lineup_sampling_seed = int(lineup_sampling_seed_raw)
                except (TypeError, ValueError):
                    return jsonify({"error": "Bad Request", "message": "lineup_sampling_seed must be a non-negative integer"}), 400

            if not team_a or not team_b:
                return jsonify({"error": "Bad Request", "message": "team_a and team_b are required"}), 400
            if team_a == team_b:
                return jsonify({"error": "Bad Request", "message": "Cannot simulate a team against itself"}), 400
            if not (0.0 <= recency_bias <= 1.0):
                return jsonify({"error": "Bad Request", "message": "recency_bias must be between 0.0 and 1.0"}), 400
            if random_seed < 0:
                return jsonify({"error": "Bad Request", "message": "random_seed must be a non-negative integer"}), 400
            if lineup_sampling_seed < 0:
                return jsonify({"error": "Bad Request", "message": "lineup_sampling_seed must be a non-negative integer"}), 400
            if model_depth != "full_context":
                return jsonify({"error": "Bad Request", "message": "model_depth must be 'full_context'"}), 400
            if not (0 <= max_fallback_level <= 6):
                return jsonify({"error": "Bad Request", "message": "max_fallback_level must be between 0 and 6"}), 400
            if realism_version not in {"enhanced_v1"}:
                return jsonify({"error": "Bad Request", "message": "realism_version must be 'enhanced_v1'"}), 400

            df = load_ipl_data()
            available_teams = set(get_available_teams(df))
            if team_a not in available_teams or team_b not in available_teams:
                return jsonify({"error": "Bad Request", "message": "team_a and team_b must be valid IPL teams"}), 400

            match_id = str(uuid.uuid4())

            with simulation_lock:
                # single-user model: mark existing running simulations as cancelled
                for sim_id, sim in active_simulations.items():
                    if sim.get("status") == "running":
                        sim["status"] = "cancelled"
                        sim["message"] = "Cancelled by a newer simulation request"

                active_simulations[match_id] = {
                    "match_id": match_id,
                    "team_a": team_a,
                    "team_b": team_b,
                    "recency_bias": recency_bias,
                    "random_seed": random_seed,
                    "model_depth": model_depth,
                    "max_fallback_level": max_fallback_level,
                    "realism_version": realism_version,
                    "stadium": stadium,
                    "lineup_sampling_seed": lineup_sampling_seed,
                    "status": "running",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

            thread = Thread(target=run_simulation, args=(match_id,), daemon=True)
            thread.start()

            logger.info("Simulation started: match_id=%s, %s vs %s", match_id, team_a, team_b)
            return (
                jsonify(
                    {
                        "match_id": match_id,
                        "status": "running",
                        "message": "Simulation started",
                        "model_depth": model_depth,
                        "max_fallback_level": max_fallback_level,
                        "realism_version": realism_version,
                        "stadium": stadium,
                        "lineup_sampling_seed": lineup_sampling_seed,
                    }
                ),
                202,
            )
        except DataLoadError as exc:
            return jsonify({"error": "Data Error", "message": str(exc)}), 500
        except Exception as exc:
            logger.error("Unexpected error in /api/simulate: %s", str(exc), exc_info=True)
            return jsonify({"error": "Internal Server Error", "message": "Failed to start simulation"}), 500

    @app.route("/api/simulation/<match_id>", methods=["GET"])
    def get_simulation(match_id: str) -> Any:
        with simulation_lock:
            sim = active_simulations.get(match_id)

        if not sim:
            return jsonify({"error": "Not Found", "message": f"Simulation {match_id} not found"}), 404

        status = sim.get("status")
        if status == "running":
            return jsonify({"match_id": match_id, "status": "running", "message": "Simulation in progress"}), 202
        if status == "failed":
            return jsonify({"match_id": match_id, "status": "failed", "error": sim.get("error", "Unknown error")}), 500
        if status == "cancelled":
            return jsonify({"match_id": match_id, "status": "cancelled", "message": sim.get("message", "Cancelled")}), 409

        return jsonify(sim), 200


app = create_app()
