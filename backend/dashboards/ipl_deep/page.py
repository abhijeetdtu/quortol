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
    apply_chart_theme,
)


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

    if season_value:
        match_df = match_df[match_df['season'] == season_value]
    if venue_value:
        match_df = match_df[match_df['venue'] == venue_value]
    if team_value:
        match_df = match_df[(match_df['team1'] == team_value) | (match_df['team2'] == team_value)]

    match_ids = set(match_df['match_number'].astype(str))
    deliveries = data['deliveries'][data['deliveries']['ID'].isin(match_ids)].copy()
    if team_value:
        deliveries = deliveries[deliveries['BattingTeam'] == team_value]

    return match_df, deliveries


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
        return _empty_figure('Top Wicket Takers', 'No bowling data for selected filters.')

    wickets = deliveries[deliveries['IsWicketDelivery'] == 1]
    grouped = (
        wickets.groupby('Bowler', as_index=False)
        .agg(wickets=('IsWicketDelivery', 'sum'))
        .sort_values('wickets', ascending=False)
        .head(12)
    )
    if grouped.empty:
        return _empty_figure('Top Wicket Takers', 'No wickets in selected filters.')

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
        title='Top Wicket Takers',
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


def _build_metric_trend_frames(deliveries, segment_by):
    if deliveries.empty:
        return None

    trend_df = deliveries.copy()
    trend_df['phase'] = pd.cut(
        trend_df['Overs'],
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
        trend_df.groupby(batting_group, as_index=False)
        .agg(
            runs=('TotalRun', 'sum'),
            batter_runs=('BatsmanRun', 'sum'),
            legal_balls=('is_legal_ball', 'sum')
        )
    )

    bowling_metrics = (
        trend_df.groupby(bowling_group, as_index=False)
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
                    value='ALL',
                    clearable=False
                )
            ], style={'minWidth': '220px', 'flex': '1 1 220px'}),
            html.Div([
                html.Label('Team'),
                dcc.Dropdown(
                    id='ipl-team-filter',
                    options=_options_with_all(data['teams']),
                    value='ALL',
                    clearable=False
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
        html.Div([
            html.Div([dcc.Graph(id='ipl-top-batters-graph')], style={'flex': '1 1 520px'}),
            html.Div([dcc.Graph(id='ipl-top-bowlers-graph')], style={'flex': '1 1 520px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '8px'}),
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
    Output('ipl-top-batters-graph', 'figure'),
    Output('ipl-top-bowlers-graph', 'figure'),
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
    season = None if season_value in (None, 'ALL') else season_value
    team = None if team_value in (None, 'ALL') else team_value
    venue = None if venue_value in (None, 'ALL') else venue_value

    match_df, deliveries = _filter_frames(data, season, team, venue)
    metrics_df = _build_metric_trend_frames(deliveries, metric_segment or 'year')

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
        _build_over_run_rate_figure(deliveries),
        _build_top_batters_figure(deliveries),
        _build_top_bowlers_figure(deliveries),
        _build_venue_innings_figure(deliveries),
        _build_toss_impact_figure(match_df),
        _build_season_trend_figure(deliveries),
        _build_phase_breakdown_figure(deliveries),
        _build_team_breakdown_figure(deliveries),
        _build_metric_trend_chart(
            metrics_df,
            'run_rate',
            f'Run Rate Trend By {metric_segment.title() if metric_segment else "Year"}',
            'Run Rate',
            DEEP_TEAL
        ),
        _build_metric_trend_chart(
            metrics_df,
            'strike_rate',
            f'Strike Rate Trend By {metric_segment.title() if metric_segment else "Year"}',
            'Strike Rate',
            PRUSSIAN_BLUE
        ),
        _build_metric_trend_chart(
            metrics_df,
            'economy',
            f'Economy Trend By {metric_segment.title() if metric_segment else "Year"}',
            'Economy',
            BRICK_EMBER
        ),
        _build_metric_trend_chart(
            metrics_df,
            'dot_ball_pct',
            f'Dot Ball % Trend By {metric_segment.title() if metric_segment else "Year"}',
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
