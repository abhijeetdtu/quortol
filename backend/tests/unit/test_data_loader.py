"""Tests for data_loader.py — schema validation, normalization, error handling."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from services.data_loader import (
    CorruptedDataError,
    DataLoadError,
    EmptyDataError,
    MissingDataError,
    get_available_teams,
    load_ipl_data,
    normalize_team_name,
)


class TestNormalizeTeamName:
    """Tests for team name normalization."""

    def test_normalizes_kings_xi_punjab(self):
        """Test Kings XI Punjab is normalized to Punjab Kings."""
        assert normalize_team_name("Kings XI Punjab") == "Punjab Kings"

    def test_normalizes_delhi_daredevils(self):
        """Test Delhi Daredevils is normalized to Delhi Capitals."""
        assert normalize_team_name("Delhi Daredevils") == "Delhi Capitals"

    def test_leaves_valid_team_unchanged(self):
        """Test that valid team names are unchanged."""
        assert normalize_team_name("Mumbai Indians") == "Mumbai Indians"
        assert normalize_team_name("Chennai Super Kings") == "Chennai Super Kings"

    def test_handles_empty_string(self):
        """Test empty string returns empty string."""
        assert normalize_team_name("") == ""

    def test_handles_none(self):
        """Test None input returns empty string."""
        assert normalize_team_name(None) == ""


class TestLoadIPLData:
    """Tests for IPL data loading."""

    def test_loads_valid_csv(self, tmp_path):
        """Test loading a valid CSV file."""
        csv_file = tmp_path / "IPL.csv"
        csv_file.write_text(
            "Season,MatchNo,Venue,Date,Team1,Team2,Toss_Winner,Toss_Decision,"
            "Winner,Win_Method,Win_Runs,Win_wickets,Player_of_Match\n"
            "2022,1,Wankhede,2022-05-21,Mumbai Indians,Chennai Super Kings,"
            "Mumbai Indians,field,Chennai Super Kings,runs,8,3,Devon Conway\n"
        )
        
        df = load_ipl_data(str(csv_file))
        
        assert df is not None
        assert len(df) == 1
        assert df.iloc[0]["Team1"] == "Mumbai Indians"
        assert df.iloc[0]["Winner"] == "Chennai Super Kings"

    def test_normalizes_teams_in_loaded_data(self, tmp_path):
        """Test that team names are normalized during load."""
        csv_file = tmp_path / "IPL.csv"
        csv_file.write_text(
            "Season,MatchNo,Venue,Date,Team1,Team2,Toss_Winner,Toss_Decision,"
            "Winner,Win_Method,Win_Runs,Win_wickets,Player_of_Match\n"
            "2022,1,Wankhede,2022-05-21,Kings XI Punjab,Chennai Super Kings,"
            "Kings XI Punjab,field,Chennai Super Kings,runs,8,3,Devon Conway\n"
        )
        
        df = load_ipl_data(str(csv_file))
        
        assert df.iloc[0]["Team1"] == "Punjab Kings"

    def test_raises_missing_data_error_for_missing_file(self):
        """Test FileNotFoundError is wrapped in MissingDataError."""
        with pytest.raises(MissingDataError, match="IPL.csv not found"):
            load_ipl_data("/nonexistent/path/IPL.csv")

    def test_raises_empty_data_error_for_empty_csv(self, tmp_path):
        """Test EmptyDataError is raised for empty CSV."""
        csv_file = tmp_path / "IPL.csv"
        csv_file.write_text("")
        
        with pytest.raises(EmptyDataError, match="IPL.csv is empty"):
            load_ipl_data(str(csv_file))

    def test_raises_corrupted_data_error_for_invalid_csv(self, tmp_path):
        """Test CorruptedDataError is raised for CSV with wrong columns."""
        csv_file = tmp_path / "IPL.csv"
        csv_file.write_text(
            "Col1,Col2,Col3\n"
            "val1,val2,val3\n"
        )
        
        with pytest.raises(CorruptedDataError, match="IPL.csv has invalid schema"):
            load_ipl_data(str(csv_file))


class TestGetAvailableTeams:
    """Tests for getting available teams."""

    def test_returns_unique_teams(self, sample_dataframe):
        """Test that unique teams are returned."""
        teams = get_available_teams(sample_dataframe)
        
        assert len(teams) == len(set(teams))
        assert "Mumbai Indians" in teams
        assert "Chennai Super Kings" in teams

    def test_returns_sorted_teams(self, sample_dataframe):
        """Test that teams are returned in sorted order."""
        teams = get_available_teams(sample_dataframe)
        
        assert teams == sorted(teams)

    def test_returns_empty_list_for_empty_dataframe(self):
        """Test empty list is returned for empty DataFrame."""
        import pandas as pd
        df = pd.DataFrame()
        
        teams = get_available_teams(df)
        
        assert teams == []

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        import pandas as pd
        
        return pd.DataFrame({
            "Team1": ["Mumbai Indians", "Chennai Super Kings", "Mumbai Indians"],
            "Team2": ["Chennai Super Kings", "Mumbai Indians", "Royal Challengers"],
        })
