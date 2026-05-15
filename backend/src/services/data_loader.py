"""Data loader for IPL.csv with schema validation, normalization, and error handling."""

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

MATCH_LEVEL_REQUIRED_COLUMNS = {
    "Team",
    "Opposition",
    "Venue",
    "Date",
    "Batting Team",
    "Bowling Team",
    "Toss Winner",
    "Toss Decision",
    "First innings score",
    "Second innings score",
    "Winner",
    "Win margin",
    "Player of Match",
}

DELIVERY_LEVEL_REQUIRED_COLUMNS = {
    "ID",
    "Innings",
    "BattingTeam",
    "TotalRun",
    "IsWicketDelivery",
}


class DataLoadError(Exception):
    """Base exception for data loading errors."""

    pass


class MissingDataError(DataLoadError):
    """Raised when IPL.csv is missing or unreadable."""

    pass


class CorruptedDataError(DataLoadError):
    """Raised when IPL.csv has invalid or corrupted data."""

    pass


class EmptyDataError(DataLoadError):
    """Raised when IPL.csv contains no data rows."""

    pass


def load_ipl_data(data_path: Optional[str] = None) -> pd.DataFrame:
    """Load IPL.csv with schema validation and error handling.

    Args:
        data_path: Path to IPL.csv. Defaults to data/IPL.csv in repo root.

    Returns:
        Validated pandas DataFrame.

    Raises:
        MissingDataError: If file not found or unreadable.
        EmptyDataError: If file contains no data rows.
        CorruptedDataError: If required columns are missing.
    """
    if data_path is None:
        project_root = Path(__file__).resolve().parents[3]
        candidate_paths = [
            project_root / "analysis" / "ipl" / "data" / "IPL.csv",
            project_root / "data" / "IPL.csv",
        ]
        existing = next((path for path in candidate_paths if path.exists()), None)
        data_path = str(existing if existing is not None else candidate_paths[0])

    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        raise MissingDataError(
            f"IPL.csv not found at '{data_path}'. "
            "Ensure the file exists in the data/ directory."
        )
    except PermissionError:
        raise MissingDataError(
            f"Permission denied reading '{data_path}'. Check file permissions."
        )
    except pd.errors.EmptyDataError:
        raise EmptyDataError(f"IPL.csv at '{data_path}' is empty.")
    except Exception as e:
        raise CorruptedDataError(f"Failed to parse IPL.csv: {e}")

    if df.empty:
        raise EmptyDataError(f"IPL.csv at '{data_path}' contains no data rows.")

    columns = set(df.columns)
    has_match_level_schema = MATCH_LEVEL_REQUIRED_COLUMNS.issubset(columns)
    has_delivery_level_schema = DELIVERY_LEVEL_REQUIRED_COLUMNS.issubset(columns)
    if not has_match_level_schema and not has_delivery_level_schema:
        raise CorruptedDataError(
            "IPL.csv has an unsupported schema. Expected either "
            f"match-level columns ({', '.join(sorted(MATCH_LEVEL_REQUIRED_COLUMNS))}) or "
            f"delivery-level columns ({', '.join(sorted(DELIVERY_LEVEL_REQUIRED_COLUMNS))})."
        )

    logger.info("Loaded %d rows from IPL.csv", len(df))
    return df


def normalize_team_name(team: Optional[str]) -> str:
    """Normalize team name to standard format.

    Args:
        team: Raw team name from CSV.

    Returns:
        Standardized team name.
    """
    if team is None:
        return ""
    team = str(team).strip()
    team = team.replace("Kings XI Punjab", "Punjab Kings")
    team = team.replace("Delhi Daredevils", "Delhi Capitals")
    team = team.replace("Rising Pune Supergiant", "Rising Pune Supergiants")
    return team


def get_available_teams(df: pd.DataFrame) -> List[str]:
    """Extract list of unique team names from DataFrame.

    Args:
        df: Validated IPL DataFrame.

    Returns:
        Sorted list of unique team names.
    """
    teams = set()
    for col in ["Batting Team", "Bowling Team", "Winner", "BattingTeam"]:
        if col in df.columns:
            teams.update(df[col].dropna().unique())

    normalized = {normalize_team_name(t) for t in teams}
    normalized.discard("")
    return sorted(normalized)


def get_team_match_count(df: pd.DataFrame, team: str) -> int:
    """Count total matches involving a team.

    Args:
        df: Validated IPL DataFrame.
        team: Normalized team name.

    Returns:
        Number of matches the team participated in.
    """
    team = normalize_team_name(team)
    if "Batting Team" in df.columns and "Bowling Team" in df.columns:
        mask = (df["Batting Team"] == team) | (df["Bowling Team"] == team)
        return int(mask.sum())
    if "BattingTeam" in df.columns and "ID" in df.columns:
        batting = df["BattingTeam"].map(normalize_team_name) == team
        return int(df.loc[batting, "ID"].astype(str).nunique())
    return 0
