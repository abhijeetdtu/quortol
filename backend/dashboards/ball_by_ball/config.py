"""Configuration for the Ball-by-Ball Match Simulation dashboard."""

DASHBOARD_CONFIG = {
    "name": "ball-by-ball-simulation",
    "title": "Ball-by-Ball Match Simulation",
    "description": (
        "Simulate IPL match outcomes ball-by-ball using a configurable recent-match window and "
        "interactive replay."
    ),
    "page_path": "/ball-by-ball-simulation",
    "nav_order": 2,
    "is_visible": True,
    "n_runs_default": 20,
    "n_runs_max": 500,
    "winprob_rollouts_per_state": 32,
    "winprob_max_states_per_ball": 8,
    "winprob_max_total_states": 240,
}
