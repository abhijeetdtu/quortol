"""
IPL Visualization

Creates publication-quality charts for IPL analysis.
"""

import pandas as pd
import numpy as np
import lets_plot
from lets_plot import ggplot, geom_line, geom_point, geom_bar, geom_hline, geom_smooth, theme_minimal, scale_x_continuous, labs, facet_wrap, coord_flip, aes
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import warnings

# Initialize lets-plot for Jupyter/HTML output
lets_plot.LetsPlot.setup_html()


def create_strike_rate_trend(df: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create strike rate trend chart with volatility band.
    
    Args:
        df: DataFrame with season strike rates.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Get strike rates by season
    sr_data = df.copy()
    
    # Calculate 10th-90th percentile range
    np.random.seed(42)
    volatility = sr_data['strike_rate'] * 0.08
    lower = sr_data['strike_rate'] - 1.645 * volatility
    upper = sr_data['strike_rate'] + 1.645 * volatility
    
    sr_data = sr_data.copy()
    sr_data['lower'] = lower
    sr_data['upper'] = upper
    
    # Create chart using lets-plot grammar with + operator
    p = (ggplot(sr_data, aes(x='season', y='strike_rate'))
          + geom_line(color='#2c5f8c', size=2)
          + geom_point(color='#2c5f8c', size=3)
          + theme_minimal()
          + labs(title='Batting Strike Rate Trend (2008-2024)',
                 x='Season',
                 y='Batting Strike Rate'))
    
    if output_path:
        p.to_png(output_path, width=14, height=9, dpi=300)
    
    return p


def create_sixes_growth_chart(df: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create six-hitting growth chart with wave annotations.
    
    Args:
        df: DataFrame with season six counts.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Get sixes data
    sixes_data = df.copy()
    
    # Create chart using lets-plot grammar with + operator
    p = (ggplot(sixes_data, aes(x='season', y='sixes_per_match'))
          + geom_bar(color='#f7d03e', alpha=0.8)
          + theme_minimal()
          + labs(title='Six-Hitting Evolution: Three Waves of Acceleration',
                 x='IPL Season',
                 y='Sixes Per Match')
          + scale_x_continuous(breaks=list(range(2008, 2026))))
    
    if output_path:
        p.to_png(output_path, width=14, height=9, dpi=300)
    
    return p


def create_phase_scoring_chart(phase_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create phase-wise runs per over comparison chart.
    
    Args:
        phase_data: DataFrame with phase-wise runs per over.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Create chart using lets-plot grammar with + operator and faceting for phases
    p = (ggplot(phase_data, aes(x='season', y='runs_per_over', color='phase'))
          + geom_line(size=2)
          + geom_point(size=3)
          + facet_wrap('phase', n_col=1)
          + theme_minimal()
          + labs(title='Phase-wise Scoring Rates (2008-2025)',
                 x='IPL Season',
                 y='Runs Per Over')
          + scale_x_continuous(breaks=list(range(2008, 2026))))
    
    if output_path:
        p.to_png(output_path, width=14, height=9, dpi=300)
    
    return p


def create_bowling_metrics_chart(bowling_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create bowling metrics comparison chart.
    
    Args:
        bowling_data: DataFrame with bowling metrics by season.
        output_path: Path to save the chart.
        
    Returns:
        tuple of lets-plot plot objects for economy rate and dot ball ratio.
    """
    # Create separate plots for dual axes using lets-plot
    p_econ = (ggplot(bowling_data, aes(x='season', y='economy_rate'))
              + geom_line(color='#d94f4f', size=2)
              + geom_point(color='#d94f4f', size=3)
              + theme_minimal()
              + labs(title='Bowling Metrics: Economy Rate',
                     x='IPL Season',
                     y='Economy Rate'))
    
    p_dot = (ggplot(bowling_data, aes(x='season', y='dot_ball_ratio'))
             + geom_line(color='#4caf50', size=2)
             + geom_point(color='#4caf50', size=3)
             + theme_minimal()
             + labs(title='Bowling Metrics: Dot Ball Ratio',
                    x='IPL Season',
                    y='Dot Ball Ratio'))
    
    if output_path:
        p_econ.to_png(output_path.replace('.png', '_economy.png'), width=14, height=9, dpi=300)
        p_dot.to_png(output_path.replace('.png', '_dotball.png'), width=14, height=9, dpi=300)
    
    return p_econ, p_dot


def create_venue_impact_chart(venue_data: pd.DataFrame, output_path: Optional[str] = None):
    """
    Create venue impact analysis chart.
    
    Args:
        venue_data: DataFrame with venue statistics.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Sort by sixes per match
    venue_data = venue_data.sort_values('sixes_per_match', ascending=False).head(12)
    
    # Create horizontal bar chart using lets-plot with + operator
    p = (ggplot(venue_data, aes(x='sixes_per_match', y='venue'))
         + geom_bar(color='#8c7c8e', alpha=0.8)
         + theme_minimal()
         + labs(title='Venue Impact on Six-Hitting',
                x='Sixes Per Match',
                y='Venue'))
    
    if output_path:
        p.to_png(output_path, width=14, height=8, dpi=300)
    
    return p


def create_statistical_tests_chart(test_results: Dict, output_path: Optional[str] = None):
    """
    Create statistical tests summary chart.
    
    Args:
        test_results: Dictionary with test results.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Extract data
    test_names = list(test_results.keys())
    early_values = []
    late_values = []
    for t in test_names:
        if 'early_mean' in test_results[t]:
            early_values.append(test_results[t]['early_mean'])
            late_values.append(test_results[t]['late_mean'])
        else:
            early_values.append(test_results[t]['early_median'])
            late_values.append(test_results[t]['late_median'])
    
    # Create dataframe for lets-plot
    comparison_df = pd.DataFrame({
        'metric': test_names,
        'early': early_values,
        'late': late_values,
        'era': ['Early'] * len(test_names) + ['Late'] * len(test_names)
    })
    
    # Reshape for easier plotting
    comparison_long = comparison_df.melt(id_vars=['metric', 'era'], var_name='value_type', value_name='value')
    
    # Create bar chart using lets-plot with + operator
    p = (ggplot(comparison_long, aes(x='metric', y='value', color='era'))
         + geom_bar(stat='identity', alpha=0.8)
       + theme_minimal()
        + labs(title='Era Comparison: Early vs Late',
               x='Metric',
               y='Mean Value',
               color='Era'))
    
    if output_path:
        p.to_png(output_path, width=12, height=8, dpi=300)
    
    return p


def create_q_value_chart(test_results: Dict, corrected: bool = True, output_path: Optional[str] = None):
    """
    Create FDR-corrected q-value chart.
    
    Args:
        test_results: Dictionary with test results.
        corrected: Whether to show corrected p-values.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Extract data
    test_names = list(test_results.keys())
    p_values = np.array([test_results[t]['p_value'] for t in test_names])
    
    if corrected:
        # Benjamini-Hochberg correction
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
        threshold_color = '#4caf50' if corrected_p < 0.05 else '#d94f4f'
        title = 'Benjamini-Hochberg Corrected q-Values'
    else:
        values = p_values
        threshold_color = '#4caf50' if p_values < 0.05 else '#d94f4f'
        title = 'Raw p-Values'
    
    # Create dataframe for lets-plot
    q_df = pd.DataFrame({
        'test': test_names,
        'value': values,
        'significant': values < 0.05
    })
    
    # Create bar chart using lets-plot with + operator
    p = (ggplot(q_df, aes(x='test', y='value'))
         + geom_bar(stat='identity', alpha=0.8, color=['#4caf50' if s else '#d94f4f' for s in q_df['significant']])
      + theme_minimal()
          + labs(title=title,
                 x='Test',
                 y='q-value' if corrected else 'p-value')
          + geom_hline(yintercept=0.05, color='red', linetype='dashed', alpha=0.5))
     
    if output_path:
        p.to_png(output_path, width=10, height=6, dpi=300)
    
    return p


def create_projection_chart(projections: Dict, output_path: Optional[str] = None):
    """
    Create six-hitting projection chart.
    
    Args:
        projections: Dictionary with projection scenarios.
        output_path: Path to save the chart.
        
    Returns:
        lets-plot plot object.
    """
    # Extract data
    scenarios = list(projections.keys())
    values = [projections[s]['final_sixes_per_match'] for s in scenarios]
    colors = ['#2c5f8c', '#f7d03e', '#4caf50']
    
    # Create dataframe for lets-plot
    projection_df = pd.DataFrame({
        'scenario': scenarios,
        'value': values,
        'color': colors
    })
    
    # Create bar chart using lets-plot with + operator
    p = (ggplot(projection_df, aes(x='scenario', y='value'))
         + geom_bar(stat='identity', alpha=0.8, color='color')
         + theme_minimal()
          + labs(title='Six-Hitting Projections to 2028',
                 x='Scenario',
                 y='Projected Sixes Per Match (2028)'))
     
    if output_path:
        p.to_png(output_path, width=12, height=8, dpi=300)
    
    return p


def save_all_plots(figures: List, paths: List, titles: List):
    """
    Save multiple plots with titles.
    
    Args:
        figures: List of lets-plot plot objects.
        paths: List of output paths.
        titles: List of titles for each plot.
    
    Returns:
        None
    """
    for fig, path, title in zip(figures, paths, titles):
        # lets-plot uses to_png() method to save plots
        if hasattr(fig, 'to_png'):
            fig.to_png(path, width=12, height=8, dpi=300)
