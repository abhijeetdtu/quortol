# API Contract: Ball-by-Ball Match Simulation (Full-Context)

**Feature**: 004-ball-by-ball-simulation  
**Date**: 2026-05-14  
**Base URL**: `/api`

## Endpoints

### GET /api/teams

List all available IPL teams.

**Response** (`200 OK`):
```json
{
  "teams": ["Chennai Super Kings", "Mumbai Indians", "..."]
}
```

---

### POST /api/simulate

Trigger a full-context ball-by-ball simulation.

**Request Body**:
```json
{
  "team_a": "Chennai Super Kings",
  "team_b": "Mumbai Indians",
  "recency_bias": 0.6,
  "random_seed": 42,
  "model_depth": "full_context",
  "max_fallback_level": 6,
  "lineup_sampling_seed": 42
}
```

**Field Constraints**:
- `team_a`: String, valid IPL team
- `team_b`: String, valid IPL team, different from `team_a`
- `recency_bias`: Float, `0.0 <= value <= 1.0`
- `random_seed`: Integer, `>= 0`
- `model_depth`: Must be `"full_context"`
- `max_fallback_level`: Integer, `0..6`
- `lineup_sampling_seed`: Integer, `>= 0` (defaults to `random_seed`)

**Response** (`202 Accepted`):
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Simulation started",
  "model_depth": "full_context",
  "max_fallback_level": 6,
  "lineup_sampling_seed": 42
}
```

---

### GET /api/simulation/{match_id}

Retrieve simulation status/results.

**Response** (`200 OK`):
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "team_a": "Chennai Super Kings",
  "team_b": "Mumbai Indians",
  "innings": [
    {
      "innings_number": 1,
      "batting_team": "Chennai Super Kings",
      "total_runs": 185,
      "wickets_lost": 6,
      "overs_completed": 20.0,
      "balls": [
        {
          "ball_number": 1,
          "runs": 1,
          "is_wicket": false,
          "cumulative_score": 1,
          "cumulative_wickets": 0,
          "batter": "RD Gaikwad",
          "non_striker": "DP Conway",
          "bowler": "JJ Bumrah",
          "phase": "powerplay",
          "wickets_in_hand": 10,
          "required_run_rate": 0.0,
          "pressure_band": "medium",
          "partnership_runs": 1,
          "context_level_used": "drop_roles",
          "effective_sample_size": 134.7
        }
      ]
    }
  ],
  "result": "Chennai Super Kings wins by 3 runs",
  "status": "completed",
  "created_at": "2026-05-14T10:30:00Z",
  "metadata": {
    "model_depth": "full_context",
    "max_fallback_level": 6,
    "lineup_sampling_seed": 42,
    "diagnostics": {
      "context_usage": {"exact": 34, "drop_pressure": 61},
      "effective_sample_size_avg": 122.1
    },
    "lineups": {
      "Chennai Super Kings": ["..."],
      "Mumbai Indians": ["..."]
    }
  },
  "low_confidence_warning": ""
}
```

**Response** (`202 Accepted`):
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Simulation in progress"
}
```

**Response** (`409 Conflict`):
```json
{
  "match_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Cancelled by a newer simulation request"
}
```
