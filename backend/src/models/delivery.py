"""DeliveryOutcome model for a single simulated delivery."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryOutcome:
    """Result of a single simulated delivery."""

    ball_number: int
    runs: int
    is_wicket: bool = False
    wicket_type: Optional[str] = None
    is_extra: bool = False
    extra_type: Optional[str] = None
    cumulative_score: int = 0
    cumulative_wickets: int = 0
    probability: float = 0.0

    # Enhanced realism fields
    event_type: str = "legal"
    is_legal_delivery: bool = True
    bat_runs: int = 0
    extra_runs: int = 0
    legal_ball_number: int = 0
    over_number: int = 0
    ball_in_over: int = 0

    # Full-context enrichment
    batter: str = ""
    non_striker: str = ""
    bowler: str = ""
    phase: str = "middle"
    wickets_in_hand: int = 10
    required_run_rate: float = 0.0
    pressure_band: str = "medium"
    partnership_runs: int = 0
    context_level_used: str = "league_prior"
    effective_sample_size: float = 0.0

    def __post_init__(self) -> None:
        if self.ball_number < 1:
            raise ValueError(f"ball_number must be >=1, got {self.ball_number}")
        if self.runs < 0:
            raise ValueError(f"runs must be >=0, got {self.runs}")
        if self.bat_runs and self.bat_runs not in (0, 1, 2, 3, 4, 5, 6):
            raise ValueError(f"bat_runs must be 0-6, got {self.bat_runs}")
        if self.extra_runs < 0:
            raise ValueError(f"extra_runs must be >=0, got {self.extra_runs}")
        if self.event_type not in {"legal", "wide", "no_ball"}:
            raise ValueError(f"event_type must be legal|wide|no_ball, got {self.event_type}")
        if self.is_extra and not self.extra_type:
            raise ValueError("extra_type required when is_extra=True")
        if self.is_wicket and not self.wicket_type:
            raise ValueError("wicket_type required when is_wicket=True")
        if not (0.0 <= self.probability <= 1.0):
            raise ValueError(f"probability must be 0.0-1.0, got {self.probability}")
        if not (0 <= self.wickets_in_hand <= 10):
            raise ValueError(f"wickets_in_hand must be 0-10, got {self.wickets_in_hand}")
        if self.legal_ball_number < 0:
            raise ValueError(f"legal_ball_number must be >=0, got {self.legal_ball_number}")
        if self.over_number < 0:
            raise ValueError(f"over_number must be >=0, got {self.over_number}")
        if not (0 <= self.ball_in_over <= 6):
            raise ValueError(f"ball_in_over must be 0-6, got {self.ball_in_over}")

        if self.bat_runs == 0 and self.extra_runs == 0 and self.runs > 0:
            # Backward-compat defaults when callers only provide runs.
            if self.is_extra:
                self.extra_runs = self.runs
            else:
                self.bat_runs = self.runs
        if self.bat_runs + self.extra_runs != self.runs:
            raise ValueError("runs must equal bat_runs + extra_runs")
        if self.event_type in {"wide", "no_ball"} and self.is_legal_delivery:
            raise ValueError("wide/no_ball must be non-legal deliveries")
        if self.event_type == "legal" and not self.is_legal_delivery:
            raise ValueError("legal event must be legal delivery")

    def to_dict(self) -> dict:
        return {
            "ball_number": self.ball_number,
            "runs": self.runs,
            "is_wicket": self.is_wicket,
            "wicket_type": self.wicket_type,
            "is_extra": self.is_extra,
            "extra_type": self.extra_type,
            "cumulative_score": self.cumulative_score,
            "cumulative_wickets": self.cumulative_wickets,
            "probability": self.probability,
            "event_type": self.event_type,
            "is_legal_delivery": self.is_legal_delivery,
            "bat_runs": self.bat_runs,
            "extra_runs": self.extra_runs,
            "legal_ball_number": self.legal_ball_number,
            "over_number": self.over_number,
            "ball_in_over": self.ball_in_over,
            "batter": self.batter,
            "non_striker": self.non_striker,
            "bowler": self.bowler,
            "phase": self.phase,
            "wickets_in_hand": self.wickets_in_hand,
            "required_run_rate": self.required_run_rate,
            "pressure_band": self.pressure_band,
            "partnership_runs": self.partnership_runs,
            "context_level_used": self.context_level_used,
            "effective_sample_size": self.effective_sample_size,
        }

    @property
    def is_boundary(self) -> bool:
        return self.bat_runs == 6

    @property
    def is_scoring_delivery(self) -> bool:
        return self.runs > 0
