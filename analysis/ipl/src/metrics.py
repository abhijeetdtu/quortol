"""
IPL Metrics Calculator

Calculates all statistical metrics for the IPL analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Tuple, Dict, List
import sys
from pathlib import Path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))
from config import ERA_SPLIT, PHASES, POSITION_GROUPS, METRICS


def calculate_season_strike_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate batting strike rates by season.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with strike rates by season.
    """
    # Aggregate by season and match
    season_data = df.groupby('season').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    
    season_data.rename(columns={
        'batsman_runs': 'total_runs',
        'is_legal': 'balls_faced'
    }, inplace=True)
    
    season_data['strike_rate'] = (season_data['total_runs'] * 100) / (season_data['balls_faced'] + 0.001)
    season_data['average_runs_per_over'] = season_data['total_runs'] / (season_data['balls_faced'] / 6 + 0.001)
    
    return season_data[['season', 'total_runs', 'balls_faced', 'strike_rate', 'average_runs_per_over']]


def calculate_phase_scoring(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate runs per over by phase (powerplay, middle, death).
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with phase-wise runs per over by season.
    """
    # Add phase column
    df_with_phase = df.copy()
    df_with_phase['phase'] = df_with_phase['over'].apply(
        lambda x: 'powerplay' if x <= 5 else ('middle' if x <= 13 else 'death')
    )
    
    # Aggregate by phase and season
    phase_data = df_with_phase.groupby(['season', 'phase']).agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    
    phase_data.rename(columns={
        'batsman_runs': 'total_runs',
        'is_legal': 'legal_balls'
    }, inplace=True)
    
    phase_data['runs_per_over'] = phase_data['total_runs'] / (phase_data['legal_balls'] / 6 + 0.001)
    
    return phase_data[['season', 'phase', 'total_runs', 'runs_per_over']]


def calculate_six_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate six-hitting rates by season.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with six counts and rates by season.
    """
    season_sixes = df.groupby('season')['is_six'].sum().reset_index()
    season_sixes.rename(columns={'is_six': 'total_sixes'}, inplace=True)
    
    season_matches = df.groupby('season').agg({
        'match_id': 'first'
    }).reset_index()
    
    # Count unique matches
    season_matches = df.groupby('season').nunique()['match_id'].reset_index()
    season_matches.rename(columns={'match_id': 'matches'}, inplace=True)
    
    # Merge
    season_data = season_sixes.merge(season_matches, on='season')
    season_data['sixes_per_match'] = season_data['total_sixes'] / (season_data['matches'] + 0.001)
    
    return season_data[['season', 'total_sixes', 'matches', 'sixes_per_match']]


def calculate_bowling_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate bowling economy rates and dot-ball suppression by season.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with bowling metrics by season.
    """
    # Aggregate by season
    bowling_data = df.groupby('season').agg({
        'total_runs': 'sum',
        'is_legal': 'sum',
        'is_dot': 'sum'
    }).reset_index()
    
    bowling_data.rename(columns={
        'total_runs': 'runs_conceded',
        'is_legal': 'balls_bowled',
        'is_dot': 'dot_balls'
    }, inplace=True)
    
    bowling_data['economy_rate'] = bowling_data['runs_conceded'] / (bowling_data['balls_bowled'] / 6 + 0.001)
    bowling_data['dot_ball_ratio'] = bowling_data['dot_balls'] / (bowling_data['balls_bowled'] + 0.001)
    
    return bowling_data[['season', 'runs_conceded', 'balls_bowled', 'economy_rate', 'dot_ball_ratio']]


def calculate_wicket_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate wickets per 100 balls by season.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with wicket metrics by season.
    """
    wicket_data = df.groupby('season').agg({
        'is_wicket': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    
    wicket_data.rename(columns={
        'is_wicket': 'total_wickets',
        'is_legal': 'balls_bowled'
    }, inplace=True)
    
    wicket_data['wickets_per_100_balls'] = (wicket_data['total_wickets'] / wicket_data['balls_bowled']) * 100
    
    return wicket_data[['season', 'total_wickets', 'balls_bowled', 'wickets_per_100_balls']]


def get_era_summary(df: pd.DataFrame, era: str = 'early') -> Dict:
    """
    Get summary statistics for a specific era.
    
    Args:
        df: Cleaned IPL data.
        era: 'early' or 'late'.
        
    Returns:
        Dictionary with era summary statistics.
    """
    era_info = ERA_SPLIT[era]
    start, end = era_info['start'], era_info['end']
    
    era_df = df[(df['season'] >= start) & (df['season'] <= end)]
    
    summary = {
        'era_name': era_info['name'],
        'years': f"{era_info['start']}-{era_info['end']}",
        'description': era_info['description']
    }
    
    # Overall strike rate
    total_runs = era_df.groupby('season').agg({'batsman_runs': 'sum'}).reset_index()
    total_balls = era_df.groupby('season').agg({'is_legal': 'sum'}).reset_index()
    
    summary['total_runs'] = era_df.groupby('season')['batsman_runs'].sum().sum()
    summary['total_balls'] = era_df.groupby('season')['is_legal'].sum().sum()
    summary['strike_rate'] = (summary['total_runs'] * 100) / (summary['total_balls'] + 0.001)
    
    # Sixes
    summary['total_sixes'] = era_df.groupby('season')['is_six'].sum().sum()
    
    # Economy rate
    summary['total_runs_conceded'] = era_df.groupby('season')['total_runs'].sum().sum()
    summary['balls_bowled'] = era_df.groupby('season')['is_legal'].sum().sum()
    summary['economy_rate'] = summary['total_runs_conceded'] / (summary['balls_bowled'] / 6 + 0.001)
    
    return summary


def compare_eras(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare early era vs late era metrics.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with era comparison.
    """
    era_data = []
    
    for era in ['early', 'late']:
        summary = get_era_summary(df, era)
        summary['era'] = era
        era_data.append(summary)
    
    comparison = pd.DataFrame(era_data)
    comparison['sr_change'] = comparison['strike_rate'].pct_change() * 100
    comparison['sixes_change'] = comparison['total_sixes'].pct_change() * 100
    comparison['economy_change'] = comparison['economy_rate'].pct_change() * 100
    
    return comparison


def perform_statistical_tests(df: pd.DataFrame) -> Dict:
    """
    Perform statistical hypothesis tests on era comparisons.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        Dictionary with test results.
    """
    # Extract era-specific data
    early_df = df[(df['season'] >= 2008) & (df['season'] <= 2015)]
    late_df = df[(df['season'] >= 2016) & (df['season'] <= 2024)]
    
    # Calculate per-match metrics
    early_by_match = early_df.groupby('match_id').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum',
        'is_six': 'sum'
    }).reset_index()
    
    late_by_match = late_df.groupby('match_id').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum',
        'is_six': 'sum'
    }).reset_index()
    
    # Calculate per-match strike rates and sixes
    early_by_match['sr'] = (early_by_match['batsman_runs'] * 100) / (early_by_match['is_legal'] + 0.001)
    late_by_match['sr'] = (late_by_match['batsman_runs'] * 100) / (late_by_match['is_legal'] + 0.001)
    
    early_by_match['sixes_per_match'] = early_by_match['is_six']
    late_by_match['sixes_per_match'] = late_by_match['is_six']
    
    # Perform tests
    results = {}
    
    # Strike rate test (Welch t-test)
    sr_ttest = stats.ttest_ind(
        early_by_match['sr'],
        late_by_match['sr'],
        equal_var=False  # Welch's t-test
    )
    results['strike_rate'] = {
        'early_mean': early_by_match['sr'].mean(),
        'late_mean': late_by_match['sr'].mean(),
        't_statistic': sr_ttest.statistic,
        'p_value': sr_ttest.pvalue,
        'significant': sr_ttest.pvalue < 0.05
    }
    
    # Sixes test (Mann-Whitney U)
    six_mwu = stats.mannwhitneyu(
        early_by_match['sixes_per_match'],
        late_by_match['sixes_per_match'],
        alternative='two-sided'
    )
    results['sixes'] = {
        'early_median': early_by_match['sixes_per_match'].median(),
        'late_median': late_by_match['sixes_per_match'].median(),
        'u_statistic': six_mwu.statistic,
        'p_value': six_mwu.pvalue,
        'significant': six_mwu.pvalue < 0.05
    }
    
    # Dot ball ratio test
    early_dot_ratio = early_df.groupby('match_id').agg({
        'is_legal': 'sum',
        'is_dot': 'sum'
    }).reset_index()
    late_dot_ratio = late_df.groupby('match_id').agg({
        'is_legal': 'sum',
        'is_dot': 'sum'
    }).reset_index()
    
    early_dot_ratio['dot_ratio'] = early_dot_ratio['is_dot'] / (early_dot_ratio['is_legal'] + 0.001)
    late_dot_ratio['dot_ratio'] = late_dot_ratio['is_dot'] / (late_dot_ratio['is_legal'] + 0.001)
    
    dot_mwu = stats.mannwhitneyu(
        early_dot_ratio['dot_ratio'],
        late_dot_ratio['dot_ratio'],
        alternative='two-sided'
    )
    results['dot_ball_ratio'] = {
        'early_mean': early_dot_ratio['dot_ratio'].mean(),
        'late_mean': late_dot_ratio['dot_ratio'].mean(),
        'u_statistic': dot_mwu.statistic,
        'p_value': dot_mwu.pvalue,
        'significant': dot_mwu.pvalue < 0.05
    }
    
    # Economy rate test
    early_economy = early_df.groupby('match_id').agg({
        'total_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    late_economy = late_df.groupby('match_id').agg({
        'total_runs': 'sum',
        'is_legal': 'sum'
    }).reset_index()
    
    early_economy['economy'] = early_economy['total_runs'] / (early_economy['is_legal'] / 6 + 0.001)
    late_economy['economy'] = late_economy['total_runs'] / (late_economy['is_legal'] / 6 + 0.001)
    
    econ_ttest = stats.ttest_ind(
        early_economy['economy'],
        late_economy['economy'],
        equal_var=False
    )
    results['economy_rate'] = {
        'early_mean': early_economy['economy'].mean(),
        'late_mean': late_economy['economy'].mean(),
        't_statistic': econ_ttest.statistic,
        'p_value': econ_ttest.pvalue,
        'significant': econ_ttest.pvalue < 0.05
    }
    
    return results


def calculate_projected_sixes(
    current_sixes_per_match: float,
    annual_growth_rates: List[float],
    years_to_project: int = 3
) -> Dict:
    """
    Calculate projected six-hitting under different scenarios.
    
    Args:
        current_sixes_per_match: Current sixes per match.
        annual_growth_rates: List of annual growth rates for scenarios.
        years_to_project: Number of years to project.
        
    Returns:
        Dictionary with projections for each scenario.
    """
    projections = {}
    
    for rate in annual_growth_rates:
        scenario_name = f'{int(rate * 100)}_growth'
        projected = current_sixes_per_match
        
        for year in range(years_to_project):
            projected = projected * (1 + rate)
        
        projections[scenario_name] = {
            'annual_growth_rate': rate,
            'final_sixes_per_match': round(projected, 1)
        }
    
    return projections


def analyze_venue_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze six-hitting by venue.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with venue statistics.
    """
    venue_stats = df.groupby('venue').agg({
        'is_six': 'sum',
        'match_id': 'first'
    }).reset_index()
    
    # Count unique matches per venue
    venue_matches = df.groupby('venue').nunique()['match_id'].reset_index()
    venue_matches.rename(columns={'match_id': 'matches'}, inplace=True)
    
    venue_stats = venue_stats.merge(venue_matches, on='venue')
    venue_stats['sixes_per_match'] = venue_stats['is_six'] / (venue_stats['matches'] + 0.001)
    
    return venue_stats[['venue', 'sixes_per_match', 'matches']]


def calculate_position_contributions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate batting contributions by position group.
    
    Args:
        df: Cleaned IPL data.
        
    Returns:
        DataFrame with position-wise statistics.
    """
    # Note: This requires position data which may not be in ball-by-ball data
    # We'll use a proxy approach based on player roles
    
    # Aggregate by batsman
    player_stats = df.groupby('batsman').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum',
        'is_six': 'sum',
        'is_wicket': 'sum'
    }).reset_index()
    
    player_stats['strike_rate'] = (player_stats['batsman_runs'] * 100) / (player_stats['is_legal'] + 0.001)
    player_stats['sixes'] = player_stats['is_six']
    
    # Categorize by strike rate (proxy for position type)
    player_stats['role'] = player_stats['strike_rate'].apply(
        lambda x: 'power_hitter' if x > 140 else ('batting_allrounder' if x > 110 else 'anchor')
    )
    
    position_summary = player_stats.groupby('role').agg({
        'batsman_runs': 'sum',
        'is_legal': 'sum',
        'is_six': 'sum',
        'batsman': 'count'
    }).reset_index()
    
    return position_summary
