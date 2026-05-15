"""SimulatedMatch model for a complete ball-by-ball simulation."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


@dataclass
class SimulatedMatch:
    """Probabilistic ball-by-ball reconstruction of a hypothetical match."""

    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    team_a: str = ""
    team_b: str = ""
    innings: List = field(default_factory=list)
    recency_bias: float = 0.5
    random_seed: int = 42
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "running"
    result: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_innings(self, innings) -> None:
        self.innings.append(innings)

    def calculate_result(self) -> str:
        if len(self.innings) < 2:
            return "Incomplete"

        score_a = self.innings[0].total_runs
        score_b = self.innings[1].total_runs

        if score_a > score_b:
            return f"{self.team_a} wins by {score_a - score_b} runs"
        if score_b > score_a:
            wickets_remaining = 10 - self.innings[1].wickets_lost
            return f"{self.team_b} wins by {wickets_remaining} wickets"
        return "Tie"

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "team_a": self.team_a,
            "team_b": self.team_b,
            "innings": [innings.to_dict() for innings in self.innings],
            "recency_bias": self.recency_bias,
            "random_seed": self.random_seed,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "result": self.result,
            "metadata": self.metadata,
        }
