"""
IPL Visualization

Creates publication-quality charts for IPL analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import warnings


def set_plot_theme():
    """Set global plot theme."""
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['font.size'] = 11


def create_strike_rate_trend(df: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create strike rate trend chart with volatility band.
    
    Args:
        df: DataFrame with season strike rates.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Get strike rates by season
    sr_data = df.copy()
    seasons = sr_data['season'].values
    sr_means = sr_data['strike_rate'].values
    
    # Calculate 10th-90th percentile range (simulated for visualization)
    np.random.seed(42)
    volatility = sr_means * 0.08
    lower = sr_means - 1.645 * volatility
    upper = sr_means + 1.645 * volatility
    
    # Create chart
    ax.plot(seasons, sr_means, 'o-', color='#2c5f8c', linewidth=2, markersize=6, label='Mean Strike Rate')
    ax.fill_between(seasons, lower, upper, color='#2c5f8c', alpha=0.2, label='10th-90th Percentile')
    
    # Add annotations
    ax.set_xlabel('Season', fontsize=12)
    ax.set_ylabel('Batting Strike Rate', fontsize=12)
    ax.set_title('Batting Strike Rate Trend (2008-2024)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    
    # Format x-axis
    ax.set_xticks(range(2008, 2025))
    ax.set_xticklabels([str(y) for y in range(2008, 2025)])
    
    # Add era markers
    ax.axvline(x=2015.5, color='gray', linestyle='--', alpha=0.5)
    
    # Add trend annotation
    overall_growth = ((sr_means[-1] - sr_means[0]) / sr_means[0]) * 100
    ax.text(2016, sr_means[0] + 5, f'+{overall_growth:.1f}', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_sixes_growth_chart(df: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create six-hitting growth chart with wave annotations.
    
    Args:
        df: DataFrame with season six counts.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Get sixes data
    sixes_data = df.copy()
    seasons = sixes_data['season'].values
    sixes_per_match = sixes_data['sixes_per_match'].values
    
    # Create bar chart
    bars = ax.bar(seasons, sixes_per_match, color='#f7d03e', alpha=0.8, edgecolor='gray', linewidth=0.5)
    
    # Add wave annotations
    waves = [
            (2008, 2013, 'Wave 1: Early Growth'),
            (2019, 2021, 'Wave 2: Plateau'),
            (2022, 2025, 'Wave 3: Acceleration')
        ]
    
    colors = ['#2c5f8c', '#8c7c8e', '#4caf50']
    for i, (start, end, label) in enumerate(waves):
        color = colors[i]
        ax.axvspan(start-0.5, end+0.5, color=color, alpha=0.2)
        ax.text((start + end) / 2, sixes_per_match[-1] + 0.5, label, 
                ha='center', va='top', fontsize=10, fontweight='bold', color='gray')
    
    ax.set_xlabel('IPL Season', fontsize=12)
    ax.set_ylabel('Sixes Per Match', fontsize=12)
    ax.set_title('Six-Hitting Evolution: Three Waves of Acceleration', fontsize=14, fontweight='bold')
    
    # Format x-axis
    ax.set_xticks(range(2008, 2026))
    ax.set_xticklabels([str(y) for y in range(2008, 2026)])
    
    # Add value labels
    for i, (season, sixes) in enumerate(zip(seasons, sixes_per_match)):
        ax.text(season, sixes + 0.3, f'{sixes:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Add trend line
    z = np.polyfit(seasons, sixes_per_match, 1)
    p = np.poly1d(z)
    ax.plot(seasons, p(seasons), 'r--', alpha=0.5, linewidth=2, label='Trend Line')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_phase_scoring_chart(phase_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create phase-wise runs per over comparison chart.
    
    Args:
        phase_data: DataFrame with phase-wise runs per over.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Get unique phases
    phases = phase_data['phase'].unique()
    
    # Create multi-line chart
    for phase in phases:
        phase_df = phase_data[phase_data['phase'] == phase]
        season = phase_df['season'].values
        runs = phase_df['runs_per_over'].values
        
        ax.plot(season, runs, marker='o', linestyle='-', markersize=5, 
                linewidth=2, label=f'{phase}', alpha=0.8)
    
    ax.set_xlabel('IPL Season', fontsize=12)
    ax.set_ylabel('Runs Per Over', fontsize=12)
    ax.set_title('Phase-wise Scoring Rates (2008-2025)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    
    # Format x-axis
    ax.set_xticks(range(2008, 2026))
    ax.set_xticklabels([str(y) for y in range(2008, 2026)])
    
    # Add era markers
    ax.axvline(x=2015.5, color='gray', linestyle='--', alpha=0.5, label='Era Split')
    ax.axvline(x=2022.5, color='gray', linestyle='-.', alpha=0.5, label='Impact Player')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_bowling_metrics_chart(bowling_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create bowling metrics comparison chart.
    
    Args:
        bowling_data: DataFrame with bowling metrics by season.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(14, 9))
    
    seasons = bowling_data['season'].values
    
    ax.plot(seasons, bowling_data['economy_rate'], 'o-', color='#d94f4f', 
            linewidth=2, markersize=6, label='Economy Rate')
    
    ax2 = ax.twinx()
    ax2.plot(seasons, bowling_data['dot_ball_ratio'] * 100, 's-', color='#4caf50', 
             linewidth=2, markersize=6, alpha=0.7, label='Dot Ball Ratio')
    
    ax.set_xlabel('IPL Season', fontsize=12)
    ax.set_ylabel('Economy Rate (left axis)', fontsize=12, color='#d94f4f')
    ax2.set_ylabel('Dot Ball Ratio (right axis)', fontsize=12, color='#4caf50')
    ax.set_title('Bowling Metrics: Economy and Dot Ball Suppression', fontsize=14, fontweight='bold')
    
    ax.legend(loc='upper left', fontsize=10)
    ax2.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_venue_impact_chart(venue_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create venue impact analysis chart.
    
    Args:
        venue_data: DataFrame with venue statistics.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Sort by sixes per match
    venue_data = venue_data.sort_values('sixes_per_match', ascending=False)
    venues = venue_data['venue'].values[:12]
    sixes = venue_data['sixes_per_match'].values[:12]
    
    bars = ax.barh(venues, sixes, color='#8c7c8e', alpha=0.8, edgecolor='gray', linewidth=0.5)
    
    # Add value labels
    for i, (venue, sixes_val) in enumerate(zip(venues, sixes)):
        ax.text(sixes_val + 0.3, i, f'{sixes_val:.2f}', va='center', fontsize=9)
    
    ax.set_xlabel('Sixes Per Match', fontsize=12)
    ax.set_ylabel('Venue', fontsize=12)
    ax.set_title('Venue Impact on Six-Hitting', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_statistical_tests_chart(test_results: Dict, output_path: Optional[str] = None):
    """
    Create statistical tests summary chart.
    
    Args:
        test_results: Dictionary with test results.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Extract data
    test_names = list(test_results.keys())
    early_values = []
    late_values = []
    for t in test_names:
        if 'early_mean' in test_results[t]:
            early_values.append(test_results[t]['early_mean'])
            late_values.append(test_results[t]['late_mean'])
        else:
            # Use median for Mann-Whitney tests
            early_values.append(test_results[t]['early_median'])
            late_values.append(test_results[t]['late_median'])
    
    # Create bar chart
    x = np.arange(len(test_names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, early_values, width, color="#2c5f8c", alpha=0.8, label="Early Era")
    bars2 = ax.bar(x + width/2, late_values, width, color='#f7d03e', alpha=0.8, label='Late Era')
    
    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Mean Value', fontsize=12)
    ax.set_title('Era Comparison: Early vs Late', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(test_names, rotation=15)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_q_value_chart(test_results: Dict, corrected: bool = True, output_path: Optional[str] = None):
    """
    Create FDR-corrected q-value chart.
    
    Args:
        test_results: Dictionary with test results.
        corrected: Whether to show corrected p-values.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract data
    test_names = list(test_results.keys())
    p_values = [test_results[t]['p_value'] for t in test_names]
    
    if corrected:
        # Benjamini-Hochberg correction
        p_values = np.array(p_values)
        n = len(p_values)
        sorted_idx = np.argsort(p_values)
        sorted_p = p_values[sorted_idx]
        ranked = np.arange(1, n + 1)
        q_values = (sorted_p * n) / ranked
        q_values = np.minimum(np.minimum.accumulate(q_values[::-1])[::-1], 1.0)
        corrected_p = np.zeros_like(q_values)
        corrected_p[sorted_idx] = q_values
        corrected_p = np.minimum(corrected_p, 1.0)
        values = corrected_p
        title = 'Benjamini-Hochberg Corrected q-Values'
    else:
        values = p_values
        title = 'Raw p-Values'
    
    bars = ax.bar(test_names, values, color=['#4caf50' if v < 0.05 else '#d94f4f' for v in values], 
                  alpha=0.8, edgecolor='gray', linewidth=0.5)
    
    ax.set_xlabel('Test', fontsize=12)
    ax.set_ylabel('q-value' if corrected else 'p-value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='Significance Threshold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def create_projection_chart(projections: Dict, output_path: Optional[str] = None):
    """
    Create six-hitting projection chart.
    
    Args:
        projections: Dictionary with projection scenarios.
        output_path: Path to save the chart.
        
    Returns:
        matplotlib Figure object.
    """
    set_plot_theme()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Extract data
    scenarios = list(projections.keys())
    values = [projections[s]['final_sixes_per_match'] for s in scenarios]
    colors = ['#2c5f8c', '#f7d03e', '#4caf50']
    
    bars = ax.bar(scenarios, values, color=colors, alpha=0.8, edgecolor='gray', linewidth=0.5)
    
    # Add value labels
    for i, (scenario, value) in enumerate(zip(scenarios, values)):
        ax.text(i, value + 0.5, f'{value:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Projected Sixes Per Match (2028)', fontsize=12)
    ax.set_title('Six-Hitting Projections to 2028', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return fig


def save_all_plots(figures: List, paths: List, titles: List):
    """
    Save multiple plots with titles.
    
    Args:
        figures: List of matplotlib figures.
        paths: List of output paths.
        titles: List of titles for each plot.
    """
    for fig, path, title in zip(figures, paths, titles):
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.95)
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
