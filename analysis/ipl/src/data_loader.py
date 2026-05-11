"""
IPL Data Loader

Loads, cleans, and preprocesses IPL ball-by-ball match data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


class IPLDataLoader:
    """Load and clean IPL ball-by-ball match data."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to IPL CSV file.
        """
        self.data_path = Path(data_path) if data_path else self._get_default_path()
        self.raw_data: Optional[pd.DataFrame] = None
        self.cleaned_data: Optional[pd.DataFrame] = None
        
    def _get_default_path(self) -> Path:
        """Get default data path."""
        base_path = Path(__file__).parent.parent / 'data'
        return base_path / 'IPL.csv'
    
    def load(self, verbose: bool = True) -> pd.DataFrame:
        """
        Load raw IPL data from CSV.
        
        Args:
            verbose: Print loading info.
            
        Returns:
            Raw DataFrame.
        """
        self.raw_data = pd.read_csv(self.data_path)
        
        if verbose:
            print(f"Loaded {len(self.raw_data)} records from {self.data_path}")
            print(f"Columns: {list(self.raw_data.columns)}")
            
        return self.raw_data
    
    def clean(self) -> pd.DataFrame:
        """
        Clean and preprocess data.
        
        Returns:
            Cleaned DataFrame.
        """
        if self.raw_data is None:
            self.load(verbose=False)
        
        df = self.raw_data.copy()
        
        # Load match info if available for accurate seasons and venues (BEFORE renaming)
        match_info_path = self.data_path.parent / 'Match_Info.csv'
        if match_info_path.exists():
            try:
                match_info = pd.read_csv(match_info_path)
                match_info['match_number'] = match_info['match_number'].astype(int)
                df['match_number'] = df['ID']  # Map ID to match_number for merge
                df = df.merge(match_info[['match_number', 'venue', 'match_date']], 
                             on='match_number', how='left')
            except Exception as e:
                df['venue'] = 'Unknown'
                df['match_date'] = None
        else:
            df['venue'] = 'Unknown'
            df['match_date'] = None
        
        # Map column names to expected format
        column_mappings = {
            'ID': 'match_id',
            'Innings': 'inning',
            'Overs': 'over',
            'BallNumber': 'ball_number',
            'Batter': 'batsman',
            'Bowler': 'bowler',
            'NonStriker': 'non_striker',
            'ExtraType': 'extras_type',
            'BatsmanRun': 'batsman_runs',
            'ExtrasRun': 'extra_runs',
            'TotalRun': 'total_runs',
            'IsWicketDelivery': 'is_wicket',
            'PlayerOut': 'player_dismissed',
            'Kind': 'dismissal_kind',
            'FieldersInvolved': 'fielder',
            'BattingTeam': 'batting_team',
            'match_number': None,  # Remove after merge
        }
        
        df = df.rename(columns=column_mappings)
        df = df.drop(columns=['match_number'], errors='ignore')
        
        # Parse dates and extract season
        df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce')
        df['season'] = df['match_date'].dt.year
        
        # Add bowling team
        df['bowling_team'] = df.groupby('inning')['batting_team'].shift(-1).bfill()
        
        # Add derived columns
        df['is_boundary'] = (df['batsman_runs'] >= 4)
        df['is_six'] = (df['batsman_runs'] == 6)
        df['is_dot'] = (df['batsman_runs'] == 0)
        df['is_legal'] = 1
        
        # Handle missing values
        df = df.replace({np.nan: None, 'nan': None, 'None': None, '': None})
        
        # Fix team name inconsistencies
        team_aliases = {
            'Royal Challengers Bangalore': 'Royal Challengers Bangalore',
            'RCB': 'Royal Challengers Bangalore',
            'Chennai Super Kings': 'Chennai Super Kings',
            'CSK': 'Chennai Super Kings',
            'Mumbai Indians': 'Mumbai Indians',
            'MI': 'Mumbai Indians',
            'Kolkata Knight Riders': 'Kolkata Knight Riders',
            'KKR': 'Kolkata Knight Riders',
            'Delhi Capitals': 'Delhi Capitals',
            'DC': 'Delhi Capitals',
            'Delhi Daredevils': 'Delhi Capitals',
            'Punjab Kings': 'Punjab Kings',
            'PBKS': 'Punjab Kings',
            'Kings XI Punjab': 'Punjab Kings',
            'Rajasthan Royals': 'Rajasthan Royals',
            'RR': 'Rajasthan Royals',
            'Sunrisers Hyderabad': 'Sunrisers Hyderabad',
            'SRH': 'Sunrisers Hyderabad',
            'Gujarat Titans': 'Gujarat Titans',
            'GT': 'Gujarat Titans',
            'Lucknow Super Giants': 'Lucknow Super Giants',
            'LSG': 'Lucknow Super Giants',
        }
        
        for col in ['batting_team', 'bowling_team']:
            if col in df.columns:
                df[col] = df[col].replace(team_aliases)
        
        self.cleaned_data = df
        
        print(f"\nCleaned data shape: {self.cleaned_data.shape}")
        print(f"\nSeasons available: {sorted(self.cleaned_data['season'].dropna().unique())}")
        print(f"Total matches: {self.cleaned_data['match_id'].nunique()}")
        print(f"Total sixes: {self.cleaned_data['is_six'].sum()}")
            
        return self.cleaned_data
    
    def get_era_data(self, era: str = 'all') -> pd.DataFrame:
        """
        Get data filtered by era.
        
        Args:
            era: 'early' (2008-2015), 'late' (2016-2024), or 'all'
            
        Returns:
            Filtered DataFrame.
        """
        if self.cleaned_data is None:
            raise ValueError("Data not loaded. Call clean() first.")
            
        df = self.cleaned_data
        
        era_info = {
            'early': (2008, 2015),
            'late': (2016, 2024),
            'all': (0, 9999)
        }
        
        start, end = era_info.get(era, (0, 9999))
        return df[(df['season'] >= start) & (df['season'] <= end)].copy()
    
    def save_cleaned_data(self, output_path: Optional[str] = None, verbose: bool = True) -> str:
        """
        Save cleaned data to CSV.
        
        Args:
            output_path: Output path.
            verbose: Print save info.
            
        Returns:
            Output file path.
        """
        if self.cleaned_data is None:
            raise ValueError("Data not loaded. Call clean() first.")
            
        out_path = Path(output_path) if output_path else self.data_path.parent / 'IPL_cleaned.csv'
        self.cleaned_data.to_csv(out_path, index=False)
        
        if verbose:
            print(f"Saved cleaned data to {out_path}")
            
        return str(out_path)


def load_ipl_data(data_path: Optional[str] = None, clean: bool = True, verbose: bool = True) -> pd.DataFrame:
    """
    Convenience function to load and clean IPL data.
    
    Args:
        data_path: Path to CSV file.
        clean: Whether to clean the data.
        verbose: Print info.
        
    Returns:
        Cleaned DataFrame.
    """
    loader = IPLDataLoader(data_path)
    loader.load(verbose=verbose)
    
    if clean:
        data = loader.clean()
        loader.save_cleaned_data(verbose=verbose)
        return data
    else:
        return loader.raw_data
