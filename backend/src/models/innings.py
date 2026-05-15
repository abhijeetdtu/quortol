"""Innings model for a single innings in a simulated match."""

from dataclasses import dataclass, field
from typing import List, Optional

from .delivery import DeliveryOutcome


@dataclass
class Innings:
    """One of two innings in a simulated match (120 balls each).

    Attributes:
        innings_number: 1 or 2.
        batting_team: Team batting in this innings.
        balls: Sequence of delivery outcomes.
        total_runs: Cumulative runs scored.
        wickets_lost: Wickets fallen.
        overs_completed: Overs bowled (e.g., 19.4).
        run_rate: Runs per over.
    """

    innings_number: int
    batting_team: str
    balls: List[DeliveryOutcome] = field(default_factory=list)
    total_runs: int = 0
    wickets_lost: int = 0
    overs_completed: float = 0.0
    run_rate: float = 0.0

    def add_delivery(self, delivery: DeliveryOutcome) -> None:
        """Add a delivery outcome to this innings.

        Args:
            delivery: DeliveryOutcome to add.
        """
        self.balls.append(delivery)
        self.total_runs = delivery.cumulative_score
        self.wickets_lost = delivery.cumulative_wickets
        self.overs_completed = self._calculate_overs()
        self.run_rate = self._calculate_run_rate()

    def _calculate_overs(self) -> float:
        """Calculate overs completed from ball count.

        Returns:
            Overs as float (e.g., 19.4 = 19 overs and 4 balls).
        """
        if not self.balls:
            return 0.0
        ball_count = sum(1 for ball in self.balls if ball.is_legal_delivery)
        overs = ball_count // 6
        balls = ball_count % 6
        return overs + balls / 10.0

    def _calculate_run_rate(self) -> float:
        """Calculate run rate (runs per over).

        Returns:
            Run rate, or 0.0 if no overs completed.
        """
        if self.overs_completed <= 0:
            return 0.0
        return self.total_runs / self.overs_completed

    def is_complete(self) -> bool:
        """Check if innings is complete.

        Returns:
            True if 120 balls bowled or all out (10 wickets).
        """
        legal_balls = sum(1 for ball in self.balls if ball.is_legal_delivery)
        return legal_balls >= 120 or self.wickets_lost >= 10

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of Innings.
        """
        return {
            "innings_number": self.innings_number,
            "batting_team": self.batting_team,
            "total_runs": self.total_runs,
            "wickets_lost": self.wickets_lost,
            "overs_completed": self.overs_completed,
            "run_rate": self.run_rate,
            "balls": [ball.to_dict() for ball in self.balls],
        }
