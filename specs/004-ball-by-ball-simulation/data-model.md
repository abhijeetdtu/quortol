# Data Model: Ball-by-Ball Match Simulation

**Feature**: 004-ball-by-ball-simulation  
**Date**: 2026-05-14  
**Source**: [spec.md](specs/004-ball-by-ball-simulation/spec.md)

## Entities

### SimulatedMatch

A probabilistic ball-by-ball reconstruction of a hypothetical match between two selected teams.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `match_id` | `str` | Unique identifier for this simulation | UUID v4, auto-generated |
| `team_a` | `str` | Name of first batting team | Must exist in IPL.csv |
| `team_b` | `str` | Name of chasing team | Must exist in IPL.csv, != team_a |
| `innings` | `list[Innings]` | Two innings, 120 balls each | len(innings) == 2 |
| `recency_bias` | `float` | Bias control value (0.0–1.0) | 0.0 <= bias <= 1.0 |
| `random_seed` | `int` | Seed for reproducibility | int >= 0 |
| `created_at` | `datetime` | Simulation creation timestamp | Auto-set |
| `status` | `str` | Simulation state | "running", "completed", "failed" |
| `result` | `str` | Match result | "Team A wins", "Team B wins", "Tie" |

**Relationships**:
- Contains 2 `Innings` objects
- References team data from IPL.csv (via `data_loader.py`)

---

### Innings

One of two innings in a simulated match (120 balls each).

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `innings_number` | `int` | 1 or 2 | innings_number in [1, 2] |
| `batting_team` | `str` | Team batting in this innings | Must be team_a (innings 1) or team_b (innings 2) |
| `balls` | `list[DeliveryOutcome]` | Sequence of 120 delivery outcomes | len(balls) == 120 |
| `total_runs` | `int` | Cumulative runs scored | Sum of all ball runs |
| `wickets_lost` | `int` | Wickets fallen | 0 <= wickets <= 9 |
| `overs_completed` | `float` | Overs bowled (e.g., 19.4) | 0.0 <= overs <= 20.0 |
| `run_rate` | `float` | Runs per over | total_runs / overs_completed (if overs > 0) |

**State Transitions**:
- "batting" → "completed" (after 120 balls or all out)
- Innings 2 ends early if chasing team reaches target

**Relationships**:
- Contains 120 `DeliveryOutcome` objects
- Parent: `SimulatedMatch`

---

### DeliveryOutcome

The result of a single simulated delivery.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `ball_number` | `int` | Ball number within innings (1–120) | 1 <= ball <= 120 |
| `runs` | `int` | Runs scored | runs in [0, 1, 2, 3, 4, 5, 6] |
| `is_wicket` | `bool` | Whether a wicket fell | boolean |
| `wicket_type` | `str` | Type of wicket (if applicable) | "bowled", "caught", "lbw", "run_out", "stumped", None |
| `is_extra` | `bool` | Whether delivery was an extra | boolean |
| `extra_type` | `str` | Type of extra (if applicable) | "wide", "no-ball", "bye", "leg-bye", None |
| `cumulative_score` | `int` | Score after this ball | Running total |
| `cumulative_wickets` | `int` | Wickets after this ball | Running total |
| `probability` | `float` | Probability of this outcome | 0.0 <= prob <= 1.0 |

**Relationships**:
- Parent: `Innings`
- Ordered by `ball_number`

---

### RecencyBiasWeight

Season-level weight for recency bias application.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `season` | `int` | IPL season year | 2008 <= season <= 2025 |
| `weight` | `float` | Weight for this season | weight > 0 |
| `decay_slope` | `float` | Slope parameter for linear decay | 0.0 <= slope <= 1.0 |

**Calculation**:
- Linear decay: `weight = 1.0 - (decay_slope * (current_year - season) / years_range)`
- Example: 2025 = 1.0, 2024 = 0.8, 2023 = 0.6 (slope = 0.2)

**Relationships**:
- 18 weights (2008–2025), one per season
- Parent: `SimulatedMatch` (via `recency_bias` parameter)

---

### TeamProfile

Historical team data used for simulation probabilities.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `team_name` | `str` | Team name (e.g., "CSK", "MI") | Must exist in IPL.csv |
| `total_matches` | `int` | Matches in IPL.csv | total_matches >= 0 |
| `avg_score_first` | `float` | Average score batting first | avg_score_first >= 0 |
| `avg_score_chasing` | `float` | Average score batting second | avg_score_chasing >= 0 |
| `avg_run_rate` | `float` | Average run rate | avg_run_rate >= 0 |
| `wicket_frequency` | `float` | Wickets per 120 balls | 0.0 <= wicket_freq <= 10.0 |
| `six_frequency` | `float` | Sixes per 120 balls | 0.0 <= six_freq <= 20.0 |
| `four_frequency` | `float` | Fours per 120 balls | 0.0 <= four_freq <= 40.0 |
| `season_weights` | `dict[int, float]` | Recency bias weights per season | len(season_weights) == 18 |

**Relationships**:
- Referenced by `SimulatedMatch` (team_a, team_b)
- Loaded from IPL.csv via `data_loader.py`

---

## Data Flow

```
IPL.csv → data_loader.py → TeamProfile (per team)
                                  ↓
                    Bayesian inference (uniform priors + weighted data)
                                  ↓
                    ProbabilityModel (posterior distribution per team)
                                  ↓
                    SimulationEngine (ball-by-ball loop, 120 balls × 2 innings)
                                  ↓
                    SimulatedMatch (result: Innings, DeliveryOutcome, etc.)
                                  ↓
                    Dash UI (charts, replay, match summary)
```

## Validation Rules

1. **Team Selection**: team_a != team_b, both must exist in IPL.csv
2. **Ball Count**: Exactly 120 balls per innings (unless all out)
3. **Wicket Limit**: Maximum 9 wickets per innings
4. **Run Limit**: No upper limit on runs (theoretical max: 120 × 6 = 720)
5. **Recency Bias**: 0.0 <= recency_bias <= 1.0
6. **Random Seed**: int >= 0
7. **Statistical Fidelity**: Aggregate statistics from 100+ simulations must fall within 15% of IPL historical averages (SC-008)

## Error Handling

| Error | Handling | Source |
|-------|----------|--------|
| IPL.csv missing | Disable "Simulate Match" button, show error message | FR-002, clarification Q4 |
| IPL.csv corrupted | Same as missing | clarification Q4 |
| Same team selected | Show error message, prevent simulation | FR-009 |
| Low-data team (< 3 matches) | Low-confidence warning, still run | FR-010 |
| Simulation failure | Show error message, log details | Edge case |
