"""Contract tests for simulation API endpoints (breaking v2 schema)."""

import json

from backend.src.api.routes import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def test_teams_endpoint_returns_list():
    client = _client()
    response = client.get("/api/teams")
    assert response.status_code == 200
    payload = json.loads(response.data)
    assert "teams" in payload
    assert isinstance(payload["teams"], list)


def test_simulate_rejects_invalid_model_depth():
    client = _client()
    response = client.post(
        "/api/simulate",
        data=json.dumps(
            {
                "team_a": "Mumbai Indians",
                "team_b": "Chennai Super Kings",
                "recency_bias": 0.5,
                "random_seed": 42,
                "model_depth": "legacy",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_simulate_accepts_new_optional_fields():
    client = _client()
    teams_response = client.get("/api/teams")
    teams = json.loads(teams_response.data)["teams"]
    team_a, team_b = teams[0], teams[1]

    response = client.post(
        "/api/simulate",
        data=json.dumps(
            {
                "team_a": team_a,
                "team_b": team_b,
                "recency_bias": 0.55,
                "random_seed": 101,
                "model_depth": "full_context",
                "max_fallback_level": 4,
                "lineup_sampling_seed": 202,
                "realism_version": "enhanced_v1",
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 202
    payload = json.loads(response.data)
    assert payload["model_depth"] == "full_context"
    assert payload["max_fallback_level"] == 4
    assert payload["lineup_sampling_seed"] == 202
    assert payload["realism_version"] == "enhanced_v1"
    assert "match_id" in payload


def test_get_simulation_returns_running_or_completed_schema():
    client = _client()
    teams = json.loads(client.get("/api/teams").data)["teams"]
    team_a, team_b = teams[0], teams[1]

    start = client.post(
        "/api/simulate",
        data=json.dumps(
            {
                "team_a": team_a,
                "team_b": team_b,
                "recency_bias": 0.5,
                "random_seed": 7,
                "model_depth": "full_context",
            }
        ),
        content_type="application/json",
    )
    match_id = json.loads(start.data)["match_id"]

    poll = client.get(f"/api/simulation/{match_id}")
    assert poll.status_code in {200, 202}
    payload = json.loads(poll.data)
    assert "status" in payload
