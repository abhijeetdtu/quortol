"""IPL Deep Dive dashboard page backed by CSV data using pandas."""

from functools import lru_cache
from pathlib import Path

import dash
from dash import Input, Output, callback, dcc, html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import DASHBOARD_CONFIG
from ..theme import (
    PRUSSIAN_BLUE,
    DEEP_TEAL,
    JASMINE,
    BRICK_EMBER,
    BLOOD_RED,
    CHART_COLORWAY,
    apply_chart_theme,
)

MAX_SERIES_CAP = 10


@lru_cache(maxsize=1)
def _load_dataset():
    """Load and cache IPL deliveries and match metadata from CSV files."""
    project_root = Path(__file__).resolve().parents[3]
    match_info_path = project_root / 'analysis' / 'ipl' / 'data' / 'Match_Info.csv'
    deliveries_path = project_root / 'analysis' / 'ipl' / 'data' / 'IPL.csv'

    match_df = pd.read_csv(match_info_path, dtype=str, low_memory=False)
    match_df = match_df.fillna('')
    match_df['season'] = match_df['match_date'].str.slice(0, 4).replace('', 'Unknown')
    match_df['venue'] = match_df['venue'].replace('', 'Unknown')

    deliveries_df = pd.read_csv(deliveries_path, low_memory=False)
    for col in ['Innings', 'Overs', 'BatsmanRun', 'TotalRun', 'IsWicketDelivery']:
        deliveries_df[col] = pd.to_numeric(deliveries_df[col], errors='coerce').fillna(0).astype(int)

    deliveries_df['ID'] = deliveries_df['ID'].astype(str)
    deliveries_df['Batter'] = deliveries_df['Batter'].fillna('Unknown').replace('', 'Unknown')
    deliveries_df['Bowler'] = deliveries_df['Bowler'].fillna('Unknown').replace('', 'Unknown')
    deliveries_df['BattingTeam'] = deliveries_df['BattingTeam'].fillna('').astype(str)

    match_meta = match_df[['match_number', 'season', 'venue', 'team1', 'team2']]
    deliveries_df = deliveries_df.merge(
        match_meta,
        how='left',
        left_on='ID',
        right_on='match_number'
    )
    deliveries_df = deliveries_df.drop(columns=['match_number'])
    deliveries_df['season'] = deliveries_df['season'].fillna('Unknown')
    deliveries_df['venue'] = deliveries_df['venue'].fillna('Unknown')
    deliveries_df['team1'] = deliveries_df['team1'].fillna('')
    deliveries_df['team2'] = deliveries_df['team2'].fillna('')
    deliveries_df['ExtraType'] = deliveries_df['ExtraType'].fillna('').astype(str).str.lower()
    deliveries_df['is_legal_ball'] = ~deliveries_df['ExtraType'].str.contains('wides|noballs', regex=True)
    deliveries_df['is_dot_ball'] = (deliveries_df['TotalRun'] == 0) & deliveries_df['is_legal_ball']
    deliveries_df['BowlingTeam'] = np.where(
        deliveries_df['BattingTeam'] == deliveries_df['team1'],
        deliveries_df['team2'],
        deliveries_df['team1']
    )

    teams = sorted({
        *set(match_df['team1']),
        *set(match_df['team2']),
        *set(deliveries_df['BattingTeam'])
    } - {''})
    seasons = sorted(set(match_df['season']) - {''})
    venues = sorted(set(match_df['venue']) - {''})

    return {
        'matches': match_df,
        'deliveries': deliveries_df,
        'teams': teams,
        'seasons': seasons,
        'venues': venues,
    }


def _empty_figure(title, message):
    fig = go.Figure()
    apply_chart_theme(fig, title=title, height=420)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(annotations=[{
        'text': message,
        'xref': 'paper',
        'yref': 'paper',
        'x': 0.5,
        'y': 0.5,
        'showarrow': False,
        'font': {'size': 14, 'color': PRUSSIAN_BLUE}
    }])
    return fig


def _filter_frames(data, season_value, team_value, venue_value):
    match_df = data['matches'].copy()

    if isinstance(season_value, list):
        season_filter = [s for s in season_value if s and s != 'ALL']
    elif season_value in (None, 'ALL'):
        season_filter = []
    else:
        season_filter = [season_value]

    if isinstance(team_value, list):
        team_filter = [t for t in team_value if t and t != 'ALL']
    elif team_value in (None, 'ALL'):
        team_filter = []
    else:
        team_filter = [team_value]

    if season_filter:
        match_df = match_df[match_df['season'].isin(season_filter)]
    if venue_value:
        match_df = match_df[match_df['venue'] == venue_value]
    if team_filter:
        match_df = match_df[
            match_df['team1'].isin(team_filter) | match_df['team2'].isin(team_filter)
        ]

    match_ids = set(match_df['match_number'].astype(str))
    deliveries = data['deliveries'][data['deliveries']['ID'].isin(match_ids)].copy()
    if team_filter:
        deliveries = deliveries[deliveries['BattingTeam'].isin(team_filter)]

    return match_df, deliveries


def _comparison_entities(season_value, team_value):
    """Return comparison mode and entity names for multi-select comparisons."""
    seasons = season_value if isinstance(season_value, list) else []
    teams = team_value if isinstance(team_value, list) else []

    if len(teams) > 1:
        return 'team', teams[:MAX_SERIES_CAP]
    if len(seasons) > 1:
        return 'season', seasons[:MAX_SERIES_CAP]
    return None, []


def _entity_deliveries(deliveries, mode, entities):
    """Split combined deliveries into one dataframe per comparison entity."""
    if mode == 'team':
        return [deliveries[deliveries['BattingTeam'] == team].copy() for team in entities]
    if mode == 'season':
        return [deliveries[deliveries['season'] == season].copy() for season in entities]
    return []


def _series_colors(n):
    return [CHART_COLORWAY[i % len(CHART_COLORWAY)] for i in range(max(1, n))]


def _apply_horizontal_legend(fig):
    fig.update_layout(
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        }
    )


def _build_over_run_rate_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        grouped = (
            frame.groupby('Overs', as_index=False)
            .agg(total_runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
            .sort_values('Overs')
        )
        if grouped.empty:
            continue
        grouped['run_rate'] = grouped['total_runs'] * 6 / grouped['balls']
        fig.add_trace(go.Scatter(
            x=grouped['Overs'],
            y=grouped['run_rate'],
            mode='lines+markers',
            name=name,
            line={'color': colors[i]},
            marker={'color': colors[i]}
        ))
    if not fig.data:
        return _empty_figure('Run Rate By Over', 'No deliveries for selected filters.')
    apply_chart_theme(fig, title='Run Rate By Over', xaxis_title='Over', yaxis_title='Runs Per Over', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _cumulative_runs_stats(deliveries):
    """Compute mean cumulative runs by over with 95% CI."""
    if deliveries.empty:
        return pd.DataFrame()

    per_over = (
        deliveries.groupby(['ID', 'Innings', 'Overs'], as_index=False)
        .agg(over_runs=('TotalRun', 'sum'))
        .sort_values(['ID', 'Innings', 'Overs'])
    )
    if per_over.empty:
        return pd.DataFrame()

    per_over['cum_runs'] = per_over.groupby(['ID', 'Innings'])['over_runs'].cumsum()
    stats = (
        per_over.groupby('Overs', as_index=False)
        .agg(
            mean_cum_runs=('cum_runs', 'mean'),
            std_cum_runs=('cum_runs', 'std'),
            innings_count=('cum_runs', 'size')
        )
        .sort_values('Overs')
    )
    stats['std_cum_runs'] = stats['std_cum_runs'].fillna(0.0)
    stats['se'] = np.where(stats['innings_count'] > 0, stats['std_cum_runs'] / np.sqrt(stats['innings_count']), 0.0)
    stats['ci95'] = 1.96 * stats['se']
    stats['lower'] = stats['mean_cum_runs'] - stats['ci95']
    stats['upper'] = stats['mean_cum_runs'] + stats['ci95']
    return stats


def _build_cumulative_runs_figure(deliveries):
    stats = _cumulative_runs_stats(deliveries)
    if stats.empty:
        return _empty_figure('Cumulative Runs By Over (95% CI)', 'No deliveries for selected filters.')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stats['Overs'],
        y=stats['lower'],
        mode='lines',
        line={'width': 0},
        hoverinfo='skip',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=stats['Overs'],
        y=stats['upper'],
        mode='lines',
        line={'width': 0},
        fill='tonexty',
        fillcolor='rgba(112,141,129,0.20)',
        name='95% CI',
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=stats['Overs'],
        y=stats['mean_cum_runs'],
        mode='lines+markers',
        name='Mean Cumulative Runs',
        line={'color': DEEP_TEAL},
        marker={'color': DEEP_TEAL},
        hovertemplate='Over: %{x}<br>Mean Cum Runs: %{y:.1f}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Cumulative Runs By Over (95% CI)',
        xaxis_title='Over',
        yaxis_title='Cumulative Runs',
        height=420
    )
    _apply_horizontal_legend(fig)
    return fig


def _build_cumulative_runs_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))

    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        stats = _cumulative_runs_stats(frame)
        if stats.empty:
            continue

        color = colors[i]
        fig.add_trace(go.Scatter(
            x=stats['Overs'],
            y=stats['lower'],
            mode='lines',
            line={'width': 0},
            hoverinfo='skip',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=stats['Overs'],
            y=stats['upper'],
            mode='lines',
            line={'width': 0},
            fill='tonexty',
            fillcolor='rgba(112,141,129,0.12)',
            name=f'{name} 95% CI',
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=stats['Overs'],
            y=stats['mean_cum_runs'],
            mode='lines+markers',
            name=name,
            line={'color': color},
            marker={'color': color}
        ))

    if not fig.data:
        return _empty_figure('Cumulative Runs By Over (95% CI)', 'No deliveries for selected filters.')

    apply_chart_theme(
        fig,
        title='Cumulative Runs By Over (95% CI)',
        xaxis_title='Over',
        yaxis_title='Cumulative Runs',
        height=420
    )
    _apply_horizontal_legend(fig)
    return fig


def _build_top_batters_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        grouped = (
            frame.groupby('Batter', as_index=False)
            .agg(runs=('BatsmanRun', 'sum'))
            .sort_values('runs', ascending=False)
            .head(8)
        )
        if grouped.empty:
            continue
        fig.add_trace(go.Bar(
            x=grouped['Batter'],
            y=grouped['runs'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Top Batters By Runs', 'No batting data for selected filters.')
    apply_chart_theme(fig, title='Top Batters By Runs', xaxis_title='Batter', yaxis_title='Runs', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_top_bowlers_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        wickets = frame[frame['IsWicketDelivery'] == 1]
        grouped = (
            wickets.groupby('Bowler', as_index=False)
            .agg(wickets=('IsWicketDelivery', 'sum'))
            .sort_values('wickets', ascending=False)
            .head(8)
        )
        if grouped.empty:
            continue
        fig.add_trace(go.Bar(
            x=grouped['Bowler'],
            y=grouped['wickets'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Top Wickets Against Selected Batting Teams', 'No bowling data for selected filters.')
    apply_chart_theme(
        fig,
        title='Top Wickets Against Selected Batting Teams',
        xaxis_title='Bowler',
        yaxis_title='Wickets',
        height=420
    )
    _apply_horizontal_legend(fig)
    return fig


def _build_team_bowlers_multi_figure(scope_deliveries, team_names):
    """Top wicket-taking bowlers belonging to each selected team."""
    fig = go.Figure()
    colors = _series_colors(len(team_names))
    for i, team_name in enumerate(team_names):
        team_frame = scope_deliveries[scope_deliveries['BowlingTeam'] == team_name]
        if team_frame.empty:
            continue
        wickets = team_frame[team_frame['IsWicketDelivery'] == 1]
        grouped = (
            wickets.groupby('Bowler', as_index=False)
            .agg(wickets=('IsWicketDelivery', 'sum'))
            .sort_values('wickets', ascending=False)
            .head(8)
        )
        if grouped.empty:
            continue
        fig.add_trace(go.Bar(
            x=grouped['Bowler'],
            y=grouped['wickets'],
            name=team_name,
            marker={'color': colors[i]},
            opacity=0.8
        ))

    if not fig.data:
        return _empty_figure('Top Bowlers Of Selected Teams', 'No bowling-team data for selected filters.')

    apply_chart_theme(
        fig,
        title='Top Bowlers Of Selected Teams',
        xaxis_title='Bowler',
        yaxis_title='Wickets',
        height=420
    )
    _apply_horizontal_legend(fig)
    return fig


def _build_venue_innings_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        innings_totals = (
            frame.groupby(['ID', 'Innings', 'venue'], as_index=False)
            .agg(innings_runs=('TotalRun', 'sum'))
        )
        grouped = (
            innings_totals.groupby('venue', as_index=False)
            .agg(avg_runs=('innings_runs', 'mean'))
            .sort_values('avg_runs', ascending=False)
            .head(8)
        )
        if grouped.empty:
            continue
        fig.add_trace(go.Bar(
            x=grouped['venue'],
            y=grouped['avg_runs'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Venue Scoring', 'No venue data for selected filters.')
    apply_chart_theme(fig, title='Top Venues By Average Innings Runs', xaxis_title='Venue', yaxis_title='Average Innings Runs', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_toss_impact_multi_figure(match_df, entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        match_ids = set(frame['ID'].unique())
        entity_matches = match_df[match_df['match_number'].astype(str).isin(match_ids)]
        if entity_matches.empty:
            continue
        toss_df = entity_matches.copy()
        toss_df['toss_decision'] = toss_df['toss_decision'].replace('', 'unknown')
        toss_df['toss_winner_won'] = (toss_df['winner'] == toss_df['toss_winner']).astype(int)
        grouped = (
            toss_df.groupby('toss_decision', as_index=False)
            .agg(win_rate=('toss_winner_won', 'mean'))
        )
        grouped['win_rate'] = grouped['win_rate'] * 100
        fig.add_trace(go.Bar(
            x=grouped['toss_decision'].str.title(),
            y=grouped['win_rate'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Toss Decision Impact', 'No match data for selected filters.')
    apply_chart_theme(fig, title='Toss Decision vs Toss-Winner Match Win Rate', xaxis_title='Toss Decision', yaxis_title='Win Rate (%)', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_season_trend_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        grouped = (
            frame.groupby('Overs', as_index=False)
            .agg(runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
            .sort_values('Overs')
        )
        if grouped.empty:
            continue
        grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
        fig.add_trace(go.Scatter(
            x=grouped['Overs'],
            y=grouped['run_rate'],
            mode='lines+markers',
            name=name,
            line={'color': colors[i]},
            marker={'color': colors[i]}
        ))
    if not fig.data:
        return _empty_figure('Season Trend: Scoring And Wickets', 'No season trend data for selected filters.')
    apply_chart_theme(fig, title='Season Trend: Scoring And Wickets', xaxis_title='Over', yaxis_title='Run Rate', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_phase_breakdown_multi_figure(entity_deliveries, entity_names):
    phases = ['Powerplay (0-5)', 'Middle (6-14)', 'Death (15-19)']
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        phase_df = frame.copy()
        phase_df['phase'] = pd.cut(phase_df['Overs'], bins=[-1, 5, 14, 19], labels=phases)
        grouped = (
            phase_df.dropna(subset=['phase'])
            .groupby('phase', as_index=False)
            .agg(runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
        )
        if grouped.empty:
            continue
        grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
        fig.add_trace(go.Bar(
            x=grouped['phase'],
            y=grouped['run_rate'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Phase Breakdown', 'No phase breakdown data for selected filters.')
    apply_chart_theme(fig, title='Phase Breakdown', xaxis_title='Phase', yaxis_title='Run Rate', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_team_breakdown_multi_figure(entity_deliveries, entity_names):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if frame.empty:
            continue
        grouped = (
            frame.groupby('BattingTeam', as_index=False)
            .agg(runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
            .sort_values('runs', ascending=False)
            .head(8)
        )
        if grouped.empty:
            continue
        grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
        fig.add_trace(go.Bar(
            x=grouped['BattingTeam'],
            y=grouped['run_rate'],
            name=name,
            marker={'color': colors[i]},
            opacity=0.8
        ))
    if not fig.data:
        return _empty_figure('Team Breakdown (Batting)', 'No team breakdown data for selected filters.')
    apply_chart_theme(fig, title='Team Breakdown (Batting Run Rate)', xaxis_title='Batting Team', yaxis_title='Run Rate', height=420)
    _apply_horizontal_legend(fig)
    return fig


def _build_over_run_rate_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Run Rate By Over', 'No deliveries for selected filters.')

    grouped = (
        deliveries.groupby('Overs', as_index=False)
        .agg(total_runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
        .sort_values('Overs')
    )
    grouped['run_rate'] = grouped['total_runs'] * 6 / grouped['balls']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grouped['Overs'],
        y=grouped['run_rate'],
        mode='lines+markers',
        name='Run Rate',
        line={'color': DEEP_TEAL},
        marker={'color': DEEP_TEAL}
    ))
    apply_chart_theme(
        fig,
        title='Run Rate By Over',
        xaxis_title='Over',
        yaxis_title='Runs Per Over',
        height=420
    )
    return fig


def _build_top_batters_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Top Batters By Runs', 'No batting data for selected filters.')

    grouped = (
        deliveries.groupby('Batter', as_index=False)
        .agg(runs=('BatsmanRun', 'sum'), balls=('BatsmanRun', 'size'))
        .sort_values('runs', ascending=False)
        .head(12)
    )
    if grouped.empty:
        return _empty_figure('Top Batters By Runs', 'No batting data for selected filters.')

    grouped = grouped.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['runs'],
        y=grouped['Batter'],
        orientation='h',
        marker={'color': PRUSSIAN_BLUE},
        customdata=grouped['balls'],
        hovertemplate='Batter: %{y}<br>Runs: %{x}<br>Balls: %{customdata}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Top Batters By Runs',
        xaxis_title='Runs',
        yaxis_title='Batter',
        height=420
    )
    return fig


def _build_top_bowlers_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Top Wickets Against Selected Batting Team(s)', 'No bowling data for selected filters.')

    wickets = deliveries[deliveries['IsWicketDelivery'] == 1]
    grouped = (
        wickets.groupby('Bowler', as_index=False)
        .agg(wickets=('IsWicketDelivery', 'sum'))
        .sort_values('wickets', ascending=False)
        .head(12)
    )
    if grouped.empty:
        return _empty_figure('Top Wickets Against Selected Batting Team(s)', 'No wickets in selected filters.')

    grouped = grouped.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['wickets'],
        y=grouped['Bowler'],
        orientation='h',
        marker={'color': BRICK_EMBER},
        hovertemplate='Bowler: %{y}<br>Wickets: %{x}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Top Wickets Against Selected Batting Team(s)',
        xaxis_title='Wickets',
        yaxis_title='Bowler',
        height=420
    )
    return fig


def _build_team_bowlers_figure(scope_deliveries, team_selection=None):
    """Top wicket-taking bowlers from selected bowling team(s)."""
    if scope_deliveries.empty:
        return _empty_figure('Top Bowlers Of Selected Team(s)', 'No bowling-team data for selected filters.')

    if isinstance(team_selection, list):
        selected_teams = [t for t in team_selection if t]
    elif isinstance(team_selection, str):
        selected_teams = [team_selection]
    else:
        selected_teams = []

    bowlers_scope = scope_deliveries
    if selected_teams:
        bowlers_scope = bowlers_scope[bowlers_scope['BowlingTeam'].isin(selected_teams)]

    wickets = bowlers_scope[bowlers_scope['IsWicketDelivery'] == 1]
    grouped = (
        wickets.groupby('Bowler', as_index=False)
        .agg(wickets=('IsWicketDelivery', 'sum'))
        .sort_values('wickets', ascending=False)
        .head(12)
    )
    if grouped.empty:
        return _empty_figure('Top Bowlers Of Selected Team(s)', 'No wickets in selected bowling-team scope.')

    grouped = grouped.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['wickets'],
        y=grouped['Bowler'],
        orientation='h',
        marker={'color': DEEP_TEAL},
        hovertemplate='Bowler: %{y}<br>Wickets: %{x}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Top Bowlers Of Selected Team(s)',
        xaxis_title='Wickets',
        yaxis_title='Bowler',
        height=420
    )
    return fig


def _build_venue_innings_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Venue Scoring', 'No venue data for selected filters.')

    innings_totals = (
        deliveries.groupby(['ID', 'Innings', 'venue'], as_index=False)
        .agg(innings_runs=('TotalRun', 'sum'))
    )
    venue_stats = (
        innings_totals.groupby('venue', as_index=False)
        .agg(avg_runs=('innings_runs', 'mean'), innings=('innings_runs', 'size'))
        .sort_values('avg_runs', ascending=False)
        .head(12)
    )
    if venue_stats.empty:
        return _empty_figure('Venue Scoring', 'No venue data for selected filters.')

    venue_stats = venue_stats.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=venue_stats['avg_runs'],
        y=venue_stats['venue'],
        orientation='h',
        marker={'color': JASMINE},
        customdata=venue_stats['innings'],
        hovertemplate='Venue: %{y}<br>Avg Innings Runs: %{x:.1f}<br>Innings: %{customdata}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Top Venues By Average Innings Runs',
        xaxis_title='Average Innings Runs',
        yaxis_title='Venue',
        height=420
    )
    return fig


def _build_toss_impact_figure(match_df):
    if match_df.empty:
        return _empty_figure('Toss Decision Impact', 'No match data for selected filters.')

    toss_df = match_df.copy()
    toss_df['toss_decision'] = toss_df['toss_decision'].replace('', 'unknown')
    toss_df['toss_winner_won'] = (toss_df['winner'] == toss_df['toss_winner']).astype(int)

    grouped = (
        toss_df.groupby('toss_decision', as_index=False)
        .agg(matches=('toss_winner_won', 'size'), win_rate=('toss_winner_won', 'mean'))
    )
    grouped['win_rate'] = grouped['win_rate'] * 100
    grouped = grouped.sort_values('toss_decision')
    if grouped.empty:
        return _empty_figure('Toss Decision Impact', 'No toss data for selected filters.')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['toss_decision'].str.title(),
        y=grouped['win_rate'],
        marker={'color': BLOOD_RED},
        customdata=grouped['matches'],
        hovertemplate='Decision: %{x}<br>Toss-Winner Win Rate: %{y:.1f}%<br>Matches: %{customdata}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Toss Decision vs Toss-Winner Match Win Rate',
        xaxis_title='Toss Decision',
        yaxis_title='Win Rate (%)',
        height=420
    )
    return fig


def _build_season_trend_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Season Trend: Scoring And Wickets', 'No season trend data for selected filters.')

    grouped = (
        deliveries.groupby('season', as_index=False)
        .agg(
            runs=('TotalRun', 'sum'),
            balls=('TotalRun', 'size'),
            wickets=('IsWicketDelivery', 'sum')
        )
        .sort_values('season')
    )
    grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
    grouped['wickets_per_over'] = grouped['wickets'] * 6 / grouped['balls']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=grouped['season'],
            y=grouped['run_rate'],
            mode='lines+markers',
            name='Run Rate',
            line={'color': DEEP_TEAL},
            marker={'color': DEEP_TEAL}
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=grouped['season'],
            y=grouped['wickets_per_over'],
            mode='lines+markers',
            name='Wickets / Over',
            line={'color': BRICK_EMBER},
            marker={'color': BRICK_EMBER}
        ),
        secondary_y=True
    )
    apply_chart_theme(
        fig,
        title='Season Trend: Scoring And Wickets',
        xaxis_title='Season',
        height=420
    )
    fig.update_yaxes(title_text='Run Rate', secondary_y=False)
    fig.update_yaxes(title_text='Wickets / Over', secondary_y=True)
    return fig


def _build_phase_breakdown_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Phase Breakdown', 'No phase breakdown data for selected filters.')

    phase_df = deliveries.copy()
    phase_df['phase'] = pd.cut(
        phase_df['Overs'],
        bins=[-1, 5, 14, 19],
        labels=['Powerplay (0-5)', 'Middle (6-14)', 'Death (15-19)']
    )
    grouped = (
        phase_df.dropna(subset=['phase'])
        .groupby('phase', as_index=False)
        .agg(
            runs=('TotalRun', 'sum'),
            balls=('TotalRun', 'size'),
            wickets=('IsWicketDelivery', 'sum')
        )
    )
    if grouped.empty:
        return _empty_figure('Phase Breakdown', 'No phase breakdown data for selected filters.')

    grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
    grouped['wickets_per_over'] = grouped['wickets'] * 6 / grouped['balls']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=grouped['phase'],
            y=grouped['run_rate'],
            name='Run Rate',
            marker={'color': DEEP_TEAL}
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=grouped['phase'],
            y=grouped['wickets_per_over'],
            mode='lines+markers',
            name='Wickets / Over',
            line={'color': BLOOD_RED},
            marker={'color': BLOOD_RED}
        ),
        secondary_y=True
    )
    apply_chart_theme(
        fig,
        title='Phase Breakdown',
        xaxis_title='Phase',
        height=420
    )
    fig.update_yaxes(title_text='Run Rate', secondary_y=False)
    fig.update_yaxes(title_text='Wickets / Over', secondary_y=True)
    return fig


def _build_team_breakdown_figure(deliveries):
    if deliveries.empty:
        return _empty_figure('Team Breakdown (Batting)', 'No team breakdown data for selected filters.')

    grouped = (
        deliveries.groupby('BattingTeam', as_index=False)
        .agg(runs=('TotalRun', 'sum'), balls=('TotalRun', 'size'))
        .sort_values('runs', ascending=False)
        .head(10)
    )
    if grouped.empty:
        return _empty_figure('Team Breakdown (Batting)', 'No team breakdown data for selected filters.')

    grouped['run_rate'] = grouped['runs'] * 6 / grouped['balls']
    grouped = grouped.iloc[::-1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['run_rate'],
        y=grouped['BattingTeam'],
        orientation='h',
        marker={'color': PRUSSIAN_BLUE},
        customdata=grouped['runs'],
        hovertemplate='Team: %{y}<br>Run Rate: %{x:.2f}<br>Total Runs: %{customdata}<extra></extra>'
    ))
    apply_chart_theme(
        fig,
        title='Team Breakdown (Batting Run Rate)',
        xaxis_title='Run Rate',
        yaxis_title='Batting Team',
        height=420
    )
    return fig


def _build_metric_trend_frames(batting_deliveries, segment_by, bowling_deliveries=None):
    if batting_deliveries.empty:
        return None

    if bowling_deliveries is None:
        bowling_deliveries = batting_deliveries

    batting_df = batting_deliveries.copy()
    bowling_df = bowling_deliveries.copy()

    batting_df['phase'] = pd.cut(
        batting_df['Overs'],
        bins=[-1, 5, 14, 19],
        labels=['Powerplay', 'Middle', 'Death']
    )
    bowling_df['phase'] = pd.cut(
        bowling_df['Overs'],
        bins=[-1, 5, 14, 19],
        labels=['Powerplay', 'Middle', 'Death']
    )

    if segment_by == 'team':
        batting_group = 'BattingTeam'
        bowling_group = 'BowlingTeam'
        sort_mode = 'descending_runs'
    elif segment_by == 'phase':
        batting_group = 'phase'
        bowling_group = 'phase'
        sort_mode = 'phase_order'
    else:
        batting_group = 'season'
        bowling_group = 'season'
        sort_mode = 'ascending'

    batting_metrics = (
        batting_df.groupby(batting_group, as_index=False)
        .agg(
            runs=('TotalRun', 'sum'),
            batter_runs=('BatsmanRun', 'sum'),
            legal_balls=('is_legal_ball', 'sum')
        )
    )

    bowling_metrics = (
        bowling_df.groupby(bowling_group, as_index=False)
        .agg(
            runs_conceded=('TotalRun', 'sum'),
            legal_balls=('is_legal_ball', 'sum'),
            dot_balls=('is_dot_ball', 'sum')
        )
    )

    if segment_by == 'team':
        batting_metrics = batting_metrics[batting_metrics[batting_group] != '']
        bowling_metrics = bowling_metrics[bowling_metrics[bowling_group] != '']

    batting_metrics = batting_metrics.rename(columns={batting_group: 'segment'})
    bowling_metrics = bowling_metrics.rename(columns={bowling_group: 'segment'})

    metrics = batting_metrics.merge(bowling_metrics, on='segment', how='outer').fillna(0)
    if metrics.empty:
        return None

    metrics['run_rate'] = np.where(
        metrics['legal_balls_x'] > 0,
        metrics['runs'] * 6 / metrics['legal_balls_x'],
        0
    )
    metrics['strike_rate'] = np.where(
        metrics['legal_balls_x'] > 0,
        metrics['batter_runs'] * 100 / metrics['legal_balls_x'],
        0
    )
    metrics['economy'] = np.where(
        metrics['legal_balls_y'] > 0,
        metrics['runs_conceded'] * 6 / metrics['legal_balls_y'],
        0
    )
    metrics['dot_ball_pct'] = np.where(
        metrics['legal_balls_y'] > 0,
        metrics['dot_balls'] * 100 / metrics['legal_balls_y'],
        0
    )

    metrics = metrics[['segment', 'runs', 'run_rate', 'strike_rate', 'economy', 'dot_ball_pct']]

    if sort_mode == 'phase_order':
        phase_order = pd.CategoricalDtype(['Powerplay', 'Middle', 'Death'], ordered=True)
        metrics['segment'] = metrics['segment'].astype(phase_order)
        metrics = metrics.sort_values('segment')
        metrics['segment'] = metrics['segment'].astype(str)
    elif sort_mode == 'descending_runs':
        metrics = metrics.sort_values('runs', ascending=False).head(10).sort_values('runs')
    else:
        # For year segments, sort numerically (e.g. 2008, 2009, ..., 2024)
        # instead of lexicographically as strings.
        if segment_by == 'year':
            metrics['segment'] = metrics['segment'].astype(str)
            metrics['_segment_num'] = pd.to_numeric(metrics['segment'], errors='coerce')
            metrics = (
                metrics.sort_values(
                    by=['_segment_num', 'segment'],
                    ascending=[True, True],
                    na_position='last'
                )
                .drop(columns=['_segment_num'])
            )
        else:
            metrics = metrics.sort_values('segment')

    return metrics


def _build_metric_trend_chart(metrics_df, metric_key, title, y_label, color):
    if metrics_df is None or metrics_df.empty:
        return _empty_figure(title, 'No metric trend data for selected filters.')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metrics_df['segment'],
        y=metrics_df[metric_key],
        mode='lines+markers',
        marker={'color': color},
        line={'color': color},
        name=y_label
    ))
    apply_chart_theme(
        fig,
        title=title,
        xaxis_title='Segment',
        yaxis_title=y_label,
        height=380
    )
    return fig


def _build_metric_trend_multi_chart(entity_deliveries, entity_names, segment_by, metric_key, title, y_label, compare_mode=None, scope_deliveries=None):
    fig = go.Figure()
    colors = _series_colors(len(entity_names))
    all_segments = []

    for i, (name, frame) in enumerate(zip(entity_names, entity_deliveries)):
        if compare_mode == 'team' and scope_deliveries is not None:
            batting_frame = scope_deliveries[scope_deliveries['BattingTeam'] == name].copy()
            bowling_frame = scope_deliveries[scope_deliveries['BowlingTeam'] == name].copy()
            metrics_df = _build_metric_trend_frames(batting_frame, segment_by, bowling_frame)
        else:
            metrics_df = _build_metric_trend_frames(frame, segment_by)
        if metrics_df is None or metrics_df.empty:
            continue
        all_segments.extend(metrics_df['segment'].astype(str).tolist())
        fig.add_trace(go.Scatter(
            x=metrics_df['segment'].astype(str),
            y=metrics_df[metric_key],
            mode='lines+markers',
            name=name,
            line={'color': colors[i]},
            marker={'color': colors[i]}
        ))

    if not fig.data:
        return _empty_figure(title, 'No metric trend data for selected filters.')

    apply_chart_theme(
        fig,
        title=title,
        xaxis_title='Segment',
        yaxis_title=y_label,
        height=380
    )
    if segment_by == 'year' and all_segments:
        seg_df = pd.DataFrame({'segment': pd.Series(all_segments, dtype='string')})
        seg_df['segment_num'] = pd.to_numeric(seg_df['segment'], errors='coerce')
        ordered = (
            seg_df.drop_duplicates(subset=['segment'])
            .sort_values(by=['segment_num', 'segment'], ascending=[True, True], na_position='last')['segment']
            .tolist()
        )
        fig.update_xaxes(categoryorder='array', categoryarray=ordered)
    _apply_horizontal_legend(fig)
    return fig


def _kpi_card(title, value, subtitle):
    return html.Div([
        html.Div(title, style={'fontSize': '0.8rem', 'opacity': 0.75}),
        html.Div(value, style={'fontSize': '1.6rem', 'fontWeight': 700}),
        html.Div(subtitle, style={'fontSize': '0.75rem', 'opacity': 0.7})
    ], style={
        'padding': '0.9rem 1rem',
        'border': f'1px solid {DEEP_TEAL}',
        'borderRadius': '8px',
        'background': '#fff',
        'color': PRUSSIAN_BLUE
    })


def _options_with_all(items):
    return [{'label': 'All', 'value': 'ALL'}] + [{'label': item, 'value': item} for item in items]


def layout():
    """Render IPL deep dive dashboard."""
    data = _load_dataset()

    return html.Div([
        html.H2(DASHBOARD_CONFIG['title']),
        html.P(DASHBOARD_CONFIG['description']),
        html.Div([
            html.Div([
                html.Label('Season'),
                dcc.Dropdown(
                    id='ipl-season-filter',
                    options=_options_with_all(data['seasons']),
                    value=['ALL'],
                    multi=True,
                    clearable=True
                )
            ], style={'minWidth': '220px', 'flex': '1 1 220px'}),
            html.Div([
                html.Label('Team'),
                dcc.Dropdown(
                    id='ipl-team-filter',
                    options=_options_with_all(data['teams']),
                    value=['ALL'],
                    multi=True,
                    clearable=True
                )
            ], style={'minWidth': '260px', 'flex': '1 1 260px'}),
            html.Div([
                html.Label('Venue'),
                dcc.Dropdown(
                    id='ipl-venue-filter',
                    options=_options_with_all(data['venues']),
                    value='ALL',
                    clearable=False
                )
            ], style={'minWidth': '280px', 'flex': '1 1 280px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px', 'marginBottom': '10px'}),
        html.Div([
            html.Div([
                html.Label('Metric Segment'),
                dcc.Dropdown(
                    id='ipl-metric-segment-filter',
                    options=[
                        {'label': 'Year', 'value': 'year'},
                        {'label': 'Team', 'value': 'team'},
                        {'label': 'Phase', 'value': 'phase'}
                    ],
                    value='year',
                    clearable=False
                )
            ], style={'minWidth': '220px', 'maxWidth': '300px', 'flex': '1 1 220px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px', 'marginBottom': '14px'}),
        html.Div(id='ipl-kpi-row', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(180px, 1fr))',
            'gap': '10px',
            'marginBottom': '14px'
        }),
        html.Div([dcc.Graph(id='ipl-over-run-rate-graph')], style={'marginBottom': '8px'}),
        html.Div([dcc.Graph(id='ipl-cumulative-runs-graph')], style={'marginBottom': '8px'}),
        html.Div([
            html.Div([dcc.Graph(id='ipl-top-batters-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-top-bowlers-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
        html.Div([dcc.Graph(id='ipl-team-bowlers-graph')], style={'marginBottom': '8px'}),
        html.Div([
            html.Div([dcc.Graph(id='ipl-venue-scoring-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-toss-impact-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
        html.Div([
            html.Div([dcc.Graph(id='ipl-season-trend-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-phase-breakdown-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
        html.Div([
            dcc.Graph(id='ipl-team-breakdown-graph')
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
        html.Hr(),
        html.H3('Metric Trend Charts'),
        html.Div([
            html.Div([dcc.Graph(id='ipl-run-rate-trend-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-strike-rate-trend-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
        html.Div([
            html.Div([dcc.Graph(id='ipl-economy-trend-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-dot-ball-trend-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'})
    ], style={'padding': '1rem'})


@callback(
    Output('ipl-kpi-row', 'children'),
    Output('ipl-over-run-rate-graph', 'figure'),
    Output('ipl-cumulative-runs-graph', 'figure'),
    Output('ipl-top-batters-graph', 'figure'),
    Output('ipl-top-bowlers-graph', 'figure'),
    Output('ipl-team-bowlers-graph', 'figure'),
    Output('ipl-venue-scoring-graph', 'figure'),
    Output('ipl-toss-impact-graph', 'figure'),
    Output('ipl-season-trend-graph', 'figure'),
    Output('ipl-phase-breakdown-graph', 'figure'),
    Output('ipl-team-breakdown-graph', 'figure'),
    Output('ipl-run-rate-trend-graph', 'figure'),
    Output('ipl-strike-rate-trend-graph', 'figure'),
    Output('ipl-economy-trend-graph', 'figure'),
    Output('ipl-dot-ball-trend-graph', 'figure'),
    Input('ipl-season-filter', 'value'),
    Input('ipl-team-filter', 'value'),
    Input('ipl-venue-filter', 'value'),
    Input('ipl-metric-segment-filter', 'value')
)
def update_dashboard(season_value, team_value, venue_value, metric_segment):
    """Update all dashboard views from current filters."""
    data = _load_dataset()

    def _normalize_multi(value):
        if value is None:
            return None
        if isinstance(value, list):
            cleaned = [item for item in value if item and item != 'ALL']
            return cleaned or None
        if value == 'ALL':
            return None
        return value

    season = _normalize_multi(season_value)
    team = _normalize_multi(team_value)
    venue = None if venue_value in (None, 'ALL') else venue_value

    match_df, deliveries = _filter_frames(data, season, team, venue)
    match_ids = set(match_df['match_number'].astype(str))
    scope_deliveries = data['deliveries'][data['deliveries']['ID'].isin(match_ids)].copy()
    metric_segment_value = metric_segment or 'year'
    compare_mode, entity_names = _comparison_entities(season, team)
    entity_deliveries = _entity_deliveries(deliveries, compare_mode, entity_names)
    is_multi_compare = compare_mode is not None and len(entity_names) > 1

    team_focus = None
    if isinstance(team, list) and len(team) == 1:
        team_focus = team[0]
    elif isinstance(team, str):
        team_focus = team

    bowling_deliveries = (
        scope_deliveries[scope_deliveries['BowlingTeam'] == team_focus].copy()
        if team_focus else scope_deliveries
    )
    metrics_df = _build_metric_trend_frames(deliveries, metric_segment_value, bowling_deliveries)

    total_runs = int(deliveries['TotalRun'].sum()) if not deliveries.empty else 0
    total_wickets = int(deliveries['IsWicketDelivery'].sum()) if not deliveries.empty else 0
    total_balls = int(deliveries.shape[0])
    run_rate = (total_runs * 6 / total_balls) if total_balls else 0
    matches = int(match_df.shape[0])

    kpi_row = [
        _kpi_card('Matches', f'{matches:,}', 'Selected match set'),
        _kpi_card('Runs', f'{total_runs:,}', 'Total runs in filtered deliveries'),
        _kpi_card('Wickets', f'{total_wickets:,}', 'Dismissals in filtered deliveries'),
        _kpi_card('Run Rate', f'{run_rate:.2f}', 'Runs per over')
    ]

    return (
        kpi_row,
        _build_over_run_rate_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_over_run_rate_figure(deliveries),
        _build_cumulative_runs_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_cumulative_runs_figure(deliveries),
        _build_top_batters_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_top_batters_figure(deliveries),
        _build_top_bowlers_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_top_bowlers_figure(deliveries),
        _build_team_bowlers_multi_figure(scope_deliveries, entity_names) if (is_multi_compare and compare_mode == 'team') else _build_team_bowlers_figure(scope_deliveries, team),
        _build_venue_innings_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_venue_innings_figure(deliveries),
        _build_toss_impact_multi_figure(match_df, entity_deliveries, entity_names) if is_multi_compare else _build_toss_impact_figure(match_df),
        _build_season_trend_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_season_trend_figure(deliveries),
        _build_phase_breakdown_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_phase_breakdown_figure(deliveries),
        _build_team_breakdown_multi_figure(entity_deliveries, entity_names) if is_multi_compare else _build_team_breakdown_figure(deliveries),
        _build_metric_trend_multi_chart(
            entity_deliveries,
            entity_names,
            metric_segment_value,
            'run_rate',
            f'Run Rate Trend By {metric_segment_value.title()}',
            'Run Rate',
            compare_mode,
            scope_deliveries
        ) if is_multi_compare else _build_metric_trend_chart(
            metrics_df,
            'run_rate',
            f'Run Rate Trend By {metric_segment_value.title()}',
            'Run Rate',
            DEEP_TEAL
        ),
        _build_metric_trend_multi_chart(
            entity_deliveries,
            entity_names,
            metric_segment_value,
            'strike_rate',
            f'Strike Rate Trend By {metric_segment_value.title()}',
            'Strike Rate',
            compare_mode,
            scope_deliveries
        ) if is_multi_compare else _build_metric_trend_chart(
            metrics_df,
            'strike_rate',
            f'Strike Rate Trend By {metric_segment_value.title()}',
            'Strike Rate',
            PRUSSIAN_BLUE
        ),
        _build_metric_trend_multi_chart(
            entity_deliveries,
            entity_names,
            metric_segment_value,
            'economy',
            f'Economy Trend By {metric_segment_value.title()}',
            'Economy',
            compare_mode,
            scope_deliveries
        ) if is_multi_compare else _build_metric_trend_chart(
            metrics_df,
            'economy',
            f'Economy Trend By {metric_segment_value.title()}',
            'Economy',
            BRICK_EMBER
        ),
        _build_metric_trend_multi_chart(
            entity_deliveries,
            entity_names,
            metric_segment_value,
            'dot_ball_pct',
            f'Dot Ball % Trend By {metric_segment_value.title()}',
            'Dot Ball %',
            compare_mode,
            scope_deliveries
        ) if is_multi_compare else _build_metric_trend_chart(
            metrics_df,
            'dot_ball_pct',
            f'Dot Ball % Trend By {metric_segment_value.title()}',
            'Dot Ball %',
            BLOOD_RED
        )
    )


dash.register_page(
    __name__,
    path='/ipl-deep-dive',
    redirect_from=['/strikes'],
    name=DASHBOARD_CONFIG.get('title', 'IPL Deep Dive Dashboard'),
    title=DASHBOARD_CONFIG.get('title', 'IPL Deep Dive Dashboard'),
    description=DASHBOARD_CONFIG.get('description', ''),
    order=DASHBOARD_CONFIG.get('nav_order', 1),
    dashboard_title=DASHBOARD_CONFIG.get('title', 'IPL Deep Dive Dashboard'),
    dashboard_description=DASHBOARD_CONFIG.get('description', ''),
    dashboard_visible=DASHBOARD_CONFIG.get('is_visible', True),
    layout=layout
)
