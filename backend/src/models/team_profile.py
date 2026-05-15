"""TeamProfile model for historical team statistics."""

import logging
from dataclasses import dataclass, field
from typing import Dict

import pandas as pd

from ..services.data_loader import normalize_team_name

logger = logging.getLogger(__name__)


@dataclass
class TeamProfile:
    """Historical team data used for simulation probabilities.

    Attributes:
        team_name: Normalized team name.
        total_matches: Number of matches in IPL.csv.
        avg_score_first: Average score when batting first.
        avg_score_chasing: Average score when batting second.
        avg_run_rate: Average run rate across all matches.
        wicket_frequency: Average wickets per 120 balls.
        six_frequency: Average sixes per 120 balls.
        four_frequency: Average fours per 120 balls.
        season_weights: Recency bias weights per season (year -> weight).
    """

    team_name: str
    total_matches: int = 0
    avg_score_first: float = 0.0
    avg_score_chasing: float = 0.0
    avg_run_rate: float = 0.0
    wicket_frequency: float = 0.0
    six_frequency: float = 0.0
    four_frequency: float = 0.0
    season_weights: Dict[int, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if self.total_matches < 0:
            raise ValueError("total_matches must be >= 0")
        if self.avg_score_first < 0:
            raise ValueError("avg_score_first must be >= 0")
        if self.avg_score_chasing < 0:
            raise ValueError("avg_score_chasing must be >= 0")
        if self.avg_run_rate < 0:
            raise ValueError("avg_run_rate must be >= 0")
        if not (0.0 <= self.wicket_frequency <= 10.0):
            raise ValueError("wicket_frequency must be between 0.0 and 10.0")
        if not (0.0 <= self.six_frequency <= 20.0):
            raise ValueError("six_frequency must be between 0.0 and 20.0")
        if not (0.0 <= self.four_frequency <= 40.0):
            raise ValueError("four_frequency must be between 0.0 and 40.0")

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, team: str) -> "TeamProfile":
        """Create TeamProfile from IPL DataFrame.

        Args:
            df: Validated IPL DataFrame.
            team: Team name (will be normalized).

        Returns:
            TeamProfile instance with computed statistics.
        """
        team = normalize_team_name(team)

        if {"Batting Team", "Bowling Team", "First innings score", "Second innings score"}.issubset(df.columns):
            return cls._from_match_level_schema(df, team)
        if {"ID", "Innings", "BattingTeam", "TotalRun", "IsWicketDelivery"}.issubset(df.columns):
            return cls._from_delivery_level_schema(df, team)
        return cls(team_name=team)

    @classmethod
    def _from_match_level_schema(cls, df: pd.DataFrame, team: str) -> "TeamProfile":
        batting_first = df[df["Batting Team"] == team]
        batting_second = df[df["Bowling Team"] == team]

        avg_score_first = 0.0
        if not batting_first.empty:
            scores = batting_first["First innings score"].dropna()
            avg_score_first = float(scores.mean()) if len(scores) > 0 else 0.0

        avg_score_chasing = 0.0
        if not batting_second.empty:
            scores = batting_second["Second innings score"].dropna()
            avg_score_chasing = float(scores.mean()) if len(scores) > 0 else 0.0

        total_matches = len(batting_first) + len(batting_second)

        avg_run_rate = 0.0
        if total_matches > 0:
            all_scores = []
            if not batting_first.empty:
                all_scores.extend(batting_first["First innings score"].dropna().tolist())
            if not batting_second.empty:
                all_scores.extend(batting_second["Second innings score"].dropna().tolist())
            if all_scores:
                avg_run_rate = sum(all_scores) / (total_matches * 20.0)

        wicket_frequency = 7.0 if total_matches > 0 else 0.0
        six_frequency = 12.0 if total_matches > 0 else 0.0
        four_frequency = 25.0 if total_matches > 0 else 0.0

        return cls(
            team_name=team,
            total_matches=total_matches,
            avg_score_first=round(avg_score_first, 2),
            avg_score_chasing=round(avg_score_chasing, 2),
            avg_run_rate=round(avg_run_rate, 2),
            wicket_frequency=round(wicket_frequency, 2),
            six_frequency=round(six_frequency, 2),
            four_frequency=round(four_frequency, 2),
        )

    @classmethod
    def _from_delivery_level_schema(cls, df: pd.DataFrame, team: str) -> "TeamProfile":
        work = df.copy()
        work["BattingTeam"] = work["BattingTeam"].map(normalize_team_name)
        team_deliveries = work[work["BattingTeam"] == team]
        if team_deliveries.empty:
            return cls(team_name=team)

        innings_totals = (
            team_deliveries.groupby(["ID", "Innings"], as_index=False)
            .agg(
                total_runs=("TotalRun", "sum"),
                wickets=("IsWicketDelivery", "sum"),
                sixes=("BatsmanRun", lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) == 6).sum()))
                if "BatsmanRun" in team_deliveries.columns
                else ("TotalRun", lambda _: 0),
                fours=("BatsmanRun", lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) == 4).sum()))
                if "BatsmanRun" in team_deliveries.columns
                else ("TotalRun", lambda _: 0),
            )
        )

        total_matches = int(team_deliveries["ID"].astype(str).nunique())
        first_innings_runs = innings_totals.loc[innings_totals["Innings"] == 1, "total_runs"]
        second_innings_runs = innings_totals.loc[innings_totals["Innings"] == 2, "total_runs"]
        avg_score_first = float(first_innings_runs.mean()) if not first_innings_runs.empty else 0.0
        avg_score_chasing = float(second_innings_runs.mean()) if not second_innings_runs.empty else 0.0

        avg_runs_per_innings = float(innings_totals["total_runs"].mean()) if not innings_totals.empty else 0.0
        avg_run_rate = avg_runs_per_innings / 20.0 if avg_runs_per_innings else 0.0

        wicket_frequency = float(innings_totals["wickets"].mean()) if not innings_totals.empty else 0.0
        six_frequency = float(innings_totals["sixes"].mean()) if not innings_totals.empty else 0.0
        four_frequency = float(innings_totals["fours"].mean()) if not innings_totals.empty else 0.0

        return cls(
            team_name=team,
            total_matches=total_matches,
            avg_score_first=round(avg_score_first, 2),
            avg_score_chasing=round(avg_score_chasing, 2),
            avg_run_rate=round(avg_run_rate, 2),
            wicket_frequency=round(min(10.0, max(0.0, wicket_frequency)), 2),
            six_frequency=round(min(20.0, max(0.0, six_frequency)), 2),
            four_frequency=round(min(40.0, max(0.0, four_frequency)), 2),
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of TeamProfile.
        """
        return {
            "team_name": self.team_name,
            "total_matches": self.total_matches,
            "avg_score_first": self.avg_score_first,
            "avg_score_chasing": self.avg_score_chasing,
            "avg_run_rate": self.avg_run_rate,
            "wicket_frequency": self.wicket_frequency,
            "six_frequency": self.six_frequency,
            "four_frequency": self.four_frequency,
            "season_weights": self.season_weights,
        }
