"""Cabeza de Vaca journey dashboard page."""

from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html, no_update
import plotly.graph_objects as go

from ..maps import MapWaypoint, build_route_map_figure
from ..theme import BODY_FONT, DEEP_TEAL, DISPLAY_FONT, JASMINE, PRUSSIAN_BLUE, apply_chart_theme
from .config import DASHBOARD_CONFIG
from .data import PHASE_LABELS, PHASE_ORDER, load_waypoints

DEFAULT_REVEAL_MODE = 'full-route'


def _card_style():
    return {
        'background': '#fff',
        'border': '1px solid #E6ECF1',
        'borderRadius': '10px',
        'boxShadow': '0 12px 30px rgba(0, 20, 39, 0.06)',
    }


def _confidence_badge(confidence: str) -> html.Span:
    colors = {
        'high': ('rgba(112, 141, 129, 0.16)', DEEP_TEAL),
        'approximate': ('rgba(244, 213, 141, 0.28)', '#8A6500'),
        'debated': ('rgba(191, 139, 46, 0.18)', '#9B5D12'),
    }
    background, color = colors.get(confidence, ('rgba(0,0,0,0.08)', PRUSSIAN_BLUE))
    return html.Span(
        confidence.replace('-', ' ').title(),
        style={
            'display': 'inline-flex',
            'padding': '0.2rem 0.55rem',
            'borderRadius': '999px',
            'fontSize': '0.8rem',
            'fontWeight': 600,
            'background': background,
            'color': color,
        },
    )


def _waypoint_lookup() -> dict[int, MapWaypoint]:
    return {waypoint.sequence: waypoint for waypoint in load_waypoints()}


def _phase_start_lookup() -> dict[str, int]:
    lookup: dict[str, int] = {}
    for waypoint in load_waypoints():
        lookup.setdefault(waypoint.phase, waypoint.sequence)
    return lookup


def _phase_dropdown_options() -> list[dict[str, str]]:
    return [
        {'label': PHASE_LABELS[phase], 'value': phase}
        for phase in PHASE_ORDER
    ]


def _slider_marks() -> dict[int, dict[str, str]]:
    marks: dict[int, dict[str, str]] = {}
    for waypoint in load_waypoints():
        label = str(waypoint.sequence)
        if waypoint.sequence == 1 or waypoint.phase != load_waypoints()[waypoint.sequence - 2].phase:
            label = f'{waypoint.sequence}: {waypoint.title}'
        marks[waypoint.sequence] = {'label': label}
    return marks


def _selected_waypoint(sequence: int | None) -> MapWaypoint:
    waypoints = load_waypoints()
    if sequence is None:
        return waypoints[0]
    return _waypoint_lookup().get(sequence, waypoints[0])


def _build_timeline_figure(active_sequence: int | None) -> go.Figure:
    ordered = list(load_waypoints())
    active_waypoint = _selected_waypoint(active_sequence)
    x_values = [
        waypoint.days_since_shipwreck
        if waypoint.days_since_shipwreck is not None
        else waypoint.sequence
        for waypoint in ordered
    ]
    y_values = [PHASE_LABELS[waypoint.phase] for waypoint in ordered]
    marker_sizes = [18 if waypoint.sequence == active_waypoint.sequence else 12 for waypoint in ordered]
    marker_colors = [
        PRUSSIAN_BLUE if waypoint.sequence == active_waypoint.sequence else DEEP_TEAL
        if waypoint.confidence == 'high'
        else '#BF8B2E'
        if waypoint.confidence == 'debated'
        else JASMINE
        for waypoint in ordered
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            line={'color': 'rgba(112, 141, 129, 0.35)', 'width': 3},
            marker={
                'size': marker_sizes,
                'color': marker_colors,
                'line': {'color': '#ffffff', 'width': 1.5},
            },
            customdata=[
                [
                    waypoint.title,
                    waypoint.date_label,
                    waypoint.days_since_shipwreck
                    if waypoint.days_since_shipwreck is not None
                    else waypoint.sequence,
                    waypoint.summary,
                    waypoint.confidence.replace('-', ' ').title(),
                ]
                for waypoint in ordered
            ],
            hovertemplate=(
                '<b>%{customdata[0]}</b>'
                '<br>%{customdata[1]}'
                '<br>Days since shipwreck: %{customdata[2]}'
                '<br>%{customdata[3]}'
                '<br>Confidence: %{customdata[4]}'
                '<extra></extra>'
            ),
            showlegend=False,
        )
    )
    apply_chart_theme(
        fig,
        title='Journey Timeline',
        xaxis_title='Days since shipwreck',
        yaxis_title='Story phase',
        height=320,
    )
    fig.update_xaxes(
        tickmode='array',
        tickvals=x_values,
        ticktext=[str(value) for value in x_values],
    )
    fig.update_yaxes(categoryorder='array', categoryarray=[PHASE_LABELS[phase] for phase in PHASE_ORDER])
    return fig


def _build_detail_panel(active_sequence: int | None) -> html.Div:
    waypoint = _selected_waypoint(active_sequence)
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div('Selected stop', style={'fontSize': '0.78rem', 'textTransform': 'uppercase', 'letterSpacing': '0.08em', 'opacity': 0.7}),
                            html.H3(waypoint.title, style={'margin': '0.25rem 0 0.35rem', 'fontFamily': DISPLAY_FONT}),
                        ]
                    ),
                    _confidence_badge(waypoint.confidence),
                ],
                style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '0.75rem', 'alignItems': 'flex-start'},
            ),
            html.P(
                f'{waypoint.date_label} · {PHASE_LABELS[waypoint.phase]}',
                style={'color': PRUSSIAN_BLUE, 'fontWeight': 600, 'marginBottom': '0.75rem'},
            ),
            html.P(waypoint.summary, style={'marginBottom': '0.75rem'}),
            html.P(
                waypoint.notes or 'No additional note recorded for this stop.',
                style={'marginBottom': 0, 'color': '#3A4B5C'},
            ),
        ],
        style={**_card_style(), 'padding': '1rem', 'color': PRUSSIAN_BLUE},
    )


def render_story(active_sequence: int | None, reveal_mode: str):
    """Render the route map, the timeline, and the narrative detail panel."""
    waypoint = _selected_waypoint(active_sequence)
    reveal_mode = (
        reveal_mode
        if reveal_mode in {'full-route', 'progressive-reveal'}
        else DEFAULT_REVEAL_MODE
    )
    return (
        build_route_map_figure(
            load_waypoints(),
            active_waypoint_id=waypoint.id,
            reveal_mode=reveal_mode,
        ),
        _build_timeline_figure(waypoint.sequence),
        _build_detail_panel(waypoint.sequence),
    )


def jump_to_phase(selected_phase: str | None):
    """Jump the stop slider to the first waypoint in a selected phase."""
    if not selected_phase:
        return no_update
    return _phase_start_lookup().get(selected_phase, no_update)


def layout():
    """Render the Cabeza de Vaca journey dashboard."""
    waypoints = load_waypoints()
    route_map, timeline_fig, detail_panel = render_story(waypoints[0].sequence, DEFAULT_REVEAL_MODE)

    return html.Div(
        [
            html.H2(DASHBOARD_CONFIG['title'], style={'fontFamily': DISPLAY_FONT}),
            html.P(
                'This dashboard treats the route as a careful reconstruction. '
                'Some stops are well anchored in the record, while others stand in for regions '
                'where the documentary trail is suggestive rather than exact.',
                style={'color': PRUSSIAN_BLUE, 'maxWidth': '76ch', 'marginBottom': '1rem'},
            ),
            html.Div(
                [
                    html.H3('Uncertainty model', style={'fontSize': '1.05rem', 'marginBottom': '0.45rem'}),
                    html.P(
                        'High-confidence points reflect places securely named in the surviving account. '
                        'Approximate and debated points are intentionally muted and explicitly labeled so '
                        'the map communicates uncertainty instead of hiding it.',
                        style={'marginBottom': 0},
                    ),
                ],
                style={**_card_style(), 'padding': '1rem 1.1rem', 'marginBottom': '1rem', 'color': PRUSSIAN_BLUE},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label('Reveal mode'),
                            dcc.RadioItems(
                                id='cabeza-reveal-mode',
                                options=[
                                    {'label': 'Full route', 'value': 'full-route'},
                                    {'label': 'Progressive reveal', 'value': 'progressive-reveal'},
                                ],
                                value=DEFAULT_REVEAL_MODE,
                                inline=True,
                                inputStyle={'marginRight': '0.35rem', 'marginLeft': '0.75rem'},
                            ),
                        ],
                        style={'flex': '1 1 280px', 'minWidth': '280px'},
                    ),
                    html.Div(
                        [
                            html.Label('Jump to phase'),
                            dcc.Dropdown(
                                id='cabeza-phase-jump',
                                options=_phase_dropdown_options(),
                                placeholder='Select a phase',
                                clearable=True,
                            ),
                        ],
                        style={'flex': '1 1 260px', 'minWidth': '260px'},
                    ),
                ],
                style={
                    **_card_style(),
                    'padding': '1rem',
                    'display': 'flex',
                    'gap': '12px',
                    'flexWrap': 'wrap',
                    'marginBottom': '1rem',
                    'color': PRUSSIAN_BLUE,
                },
            ),
            html.Div(
                [
                    html.Label('Journey stop', style={'display': 'block', 'marginBottom': '0.5rem'}),
                    dcc.Slider(
                        id='cabeza-stop-slider',
                        min=waypoints[0].sequence,
                        max=waypoints[-1].sequence,
                        step=1,
                        value=waypoints[0].sequence,
                        marks=_slider_marks(),
                        tooltip={'placement': 'bottom', 'always_visible': False},
                    ),
                ],
                style={**_card_style(), 'padding': '1rem', 'marginBottom': '1rem', 'color': PRUSSIAN_BLUE},
            ),
            html.Div(
                [
                    html.Div([dcc.Graph(id='cabeza-route-map', figure=route_map)], style={'flex': '1 1 720px'}),
                    html.Div(
                        [
                            html.Div(id='cabeza-detail-panel', children=detail_panel),
                            html.Div(
                                [
                                    html.H4('Story phases', style={'fontSize': '1rem'}),
                                    html.Ul(
                                        [
                                            html.Li('Shipwreck: landfall, collapse, and the failed barge escape.'),
                                            html.Li('Gulf Coast Survival: captivity, trade, and years of adaptation.'),
                                            html.Li('Interior Crossing: the westward turn through contested inland routes.'),
                                            html.Li('New Spain Arrival: entry into Spanish settlements and formal reporting.'),
                                        ],
                                        style={'paddingLeft': '1.1rem', 'marginBottom': 0},
                                    ),
                                ],
                                style={**_card_style(), 'padding': '1rem', 'marginTop': '1rem', 'color': PRUSSIAN_BLUE},
                            ),
                        ],
                        style={'flex': '1 1 340px'},
                    ),
                ],
                style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px'},
            ),
            html.Div(
                [dcc.Graph(id='cabeza-timeline', figure=timeline_fig)],
                style={'marginTop': '1rem'},
            ),
        ],
        style={'padding': '1rem', 'fontFamily': BODY_FONT},
    )


@callback(
    Output('cabeza-stop-slider', 'value'),
    Input('cabeza-phase-jump', 'value'),
    prevent_initial_call=True,
)
def sync_phase_jump(selected_phase):
    """Sync the phase selector into the stop slider."""
    return jump_to_phase(selected_phase)


@callback(
    Output('cabeza-route-map', 'figure'),
    Output('cabeza-timeline', 'figure'),
    Output('cabeza-detail-panel', 'children'),
    Input('cabeza-stop-slider', 'value'),
    Input('cabeza-reveal-mode', 'value'),
)
def update_story(active_sequence, reveal_mode):
    """Update the route story when controls change."""
    return render_story(active_sequence, reveal_mode)


dash.register_page(
    __name__,
    path=DASHBOARD_CONFIG['page_path'],
    name=DASHBOARD_CONFIG['title'],
    title=DASHBOARD_CONFIG['title'],
    description=DASHBOARD_CONFIG['description'],
    order=DASHBOARD_CONFIG['nav_order'],
    dashboard_title=DASHBOARD_CONFIG['title'],
    dashboard_description=DASHBOARD_CONFIG['description'],
    dashboard_visible=DASHBOARD_CONFIG['is_visible'],
    layout=layout,
)
