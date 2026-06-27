"""Solar System Scale dashboard page."""

import math

import dash
from dash import Input, Output, State, callback, ctx, dcc, html, no_update
import plotly.graph_objects as go

from .config import DASHBOARD_CONFIG
from .data import (
    apparent_sun_angular_diameter_degrees,
    build_comparison_summary,
    convert_distance,
    distance_unit_label,
    focus_body_names,
    get_body_lookup,
    load_solar_system_bodies,
)
from .simulation import (
    MAX_DISTANCE_AU,
    build_default_sandbox_state,
    compute_accelerations,
    get_state_body_lookup,
    reset_sandbox_state,
    set_running_state,
    step_sandbox_state,
    update_body_state,
    update_sandbox_config,
)
from ..theme import (
    BODY_FONT,
    BRICK_EMBER,
    DEEP_TEAL,
    DISPLAY_FONT,
    PRUSSIAN_BLUE,
    apply_chart_theme,
)

DEFAULT_BODY = 'Earth'
DEFAULT_FOCUS = 'whole-system'
DEFAULT_UNIT = 'au'
MIN_APPARENT_SUN_DIAMETER_PX = 4.0
SCALE_TAB = 'scale-explorer'
SANDBOX_TAB = 'gravity-sandbox'
MIN_TRAIL_LENGTH = 30
MAX_TRAIL_LENGTH = 1440
TRAIL_FADE_SEGMENTS = 24


def _rgba(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    return f'rgba({red}, {green}, {blue}, {alpha})'


def _card_style():
    return {
        'background': '#fff',
        'border': '1px solid #E6ECF1',
        'borderRadius': '10px',
        'boxShadow': '0 12px 30px rgba(0, 20, 39, 0.06)',
    }


def _metric_card(title, value, subtitle):
    return html.Div(
        [
            html.Div(title, style={'fontSize': '0.78rem', 'textTransform': 'uppercase', 'letterSpacing': '0.08em', 'opacity': 0.7}),
            html.Div(value, style={'fontSize': '1.55rem', 'fontWeight': 700, 'marginTop': '0.2rem'}),
            html.Div(subtitle, style={'fontSize': '0.9rem', 'opacity': 0.85, 'marginTop': '0.35rem'}),
        ],
        style={
            **_card_style(),
            'padding': '1rem',
            'color': PRUSSIAN_BLUE,
        },
    )


def _build_callout_cards(selected_name, unit, bodies=None):
    bodies = bodies or load_solar_system_bodies()
    summary = build_comparison_summary(selected_name, unit, bodies)
    distance_unit = summary['selected_distance_unit']
    distance_value = summary['selected_distance_value']
    orbit_days = summary['selected_orbital_period_days']
    orbit_text = 'Central reference point' if orbit_days == 0 else f'{orbit_days:,.0f} Earth days per orbit'
    selected_title = 'Star' if summary['selected_body_type'] == 'star' else 'Planet'
    earth_ratio = summary['diameter_ratio_vs_earth']
    sun_pct = summary['diameter_ratio_vs_sun'] * 100

    return [
        _metric_card(
            f'{summary["selected_name"]} at a glance',
            f'{distance_value:,.2f} {distance_unit}',
            f'{selected_title} · {summary["selected_diameter_km"]:,.0f} km wide · {orbit_text}',
        ),
        _metric_card(
            'Compared with Earth',
            f'{earth_ratio:,.2f}× Earth’s diameter',
            (
                'Baseline world: 1 Earth diameter and 1 Earth-Sun distance.'
                if selected_name == 'Earth'
                else f'Its orbit sits {summary["distance_ratio_vs_earth"]:,.2f}× Earth’s solar distance.'
            ),
        ),
        _metric_card(
            'Compared with the Sun',
            f'{sun_pct:,.3f}% of the Sun’s diameter',
            (
                'The Sun is the anchor for every orbit and every travel-time comparison.'
                if selected_name != 'Sun'
                else summary['selected_fact']
            ),
        ),
    ]


def _distance_axis_max(focus_mode, unit, lookup):
    inner_limit = lookup['Mars'].mean_distance_from_sun_km * 1.15
    full_limit = lookup['Neptune'].mean_distance_from_sun_km * 1.05
    max_distance_km = inner_limit if focus_mode == 'inner-planets' else full_limit
    return convert_distance(max_distance_km, unit)


def _distance_tickformat(unit):
    if unit == 'km':
        return '~s'
    if unit == 'light-minutes':
        return ',.0f'
    return ',.1f'


def _build_size_figure(bodies, selected_name, focus_mode):
    focus_names = set(focus_body_names(focus_mode, bodies))
    lookup = get_body_lookup(bodies)
    selected = lookup[selected_name]
    ordered = list(reversed(bodies))
    colors = [
        _rgba(
            body.color,
            1.0 if body.name == selected_name else 0.92 if body.name in focus_names else 0.25,
        )
        for body in ordered
    ]
    customdata = [
        (
            body.diameter_km / lookup['Earth'].diameter_km,
            body.diameter_km / lookup['Sun'].diameter_km * 100,
        )
        for body in ordered
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[body.diameter_km for body in ordered],
        y=[body.name for body in ordered],
        orientation='h',
        marker={'color': colors, 'line': {'width': 0}},
        customdata=customdata,
        hovertemplate=(
            '%{y}<br>'
            'Diameter: %{x:,.0f} km<br>'
            'Vs Earth: %{customdata[0]:.2f}×<br>'
            'Vs Sun: %{customdata[1]:.3f}%<extra></extra>'
        ),
    ))
    apply_chart_theme(
        fig,
        title='Size View: Planetary diameters on a log scale',
        xaxis_title='Diameter (km, log scale)',
        yaxis_title='',
        height=430,
    )
    fig.update_xaxes(type='log')
    fig.add_annotation(
        x=selected.diameter_km,
        y=selected.name,
        text=f'{selected.name}: {selected.diameter_km:,.0f} km wide',
        showarrow=False,
        xanchor='left',
        xshift=16,
        font={'family': BODY_FONT, 'size': 12, 'color': PRUSSIAN_BLUE},
        bgcolor='rgba(255,255,255,0.9)',
    )
    return fig


def _build_distance_figure(bodies, selected_name, focus_mode, unit):
    focus_names = set(focus_body_names(focus_mode, bodies))
    lookup = get_body_lookup(bodies)
    selected = lookup[selected_name]
    selected_unit_label = distance_unit_label(unit)
    ordered = list(reversed(bodies))
    distances = [convert_distance(body.mean_distance_from_sun_km, unit) for body in ordered]
    line_x = []
    line_y = []
    y_positions = list(range(len(ordered)))

    for index, distance in enumerate(distances):
        line_x.extend([0, distance, None])
        line_y.extend([index, index, None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line={'color': 'rgba(112, 141, 129, 0.35)', 'width': 2},
        hoverinfo='skip',
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=distances,
        y=y_positions,
        mode='markers+text',
        text=[body.name for body in ordered],
        textposition='middle left',
        marker={
            'size': [18 if body.name == selected_name else 12 for body in ordered],
            'color': [
                _rgba(
                    body.color,
                    1.0 if body.name == selected_name else 0.9 if body.name in focus_names else 0.28,
                )
                for body in ordered
            ],
            'line': {'color': '#ffffff', 'width': 1.5},
        },
        customdata=[body.light_time_minutes for body in ordered],
        hovertemplate=(
            '%{text}<br>'
            f'Distance from Sun: %{{x:,.2f}} {selected_unit_label}<br>'
            'Light-travel time: %{customdata:,.1f} minutes<extra></extra>'
        ),
        showlegend=False,
    ))
    apply_chart_theme(
        fig,
        title=f'Distance View: Orbit spacing from the Sun in {selected_unit_label}',
        xaxis_title=f'Distance from the Sun ({selected_unit_label})',
        yaxis_title='',
        height=460,
    )
    fig.update_yaxes(
        tickmode='array',
        tickvals=y_positions,
        ticktext=[body.name for body in ordered],
        showgrid=False,
    )
    fig.update_xaxes(range=[0, _distance_axis_max(focus_mode, unit, lookup)], tickformat=_distance_tickformat(unit))
    fig.add_annotation(
        x=convert_distance(selected.mean_distance_from_sun_km, unit),
        y=y_positions[ordered.index(selected)],
        text=f'{selected.name}: {convert_distance(selected.mean_distance_from_sun_km, unit):,.2f} {selected_unit_label}',
        showarrow=False,
        xanchor='left',
        xshift=12,
        font={'family': BODY_FONT, 'size': 12, 'color': PRUSSIAN_BLUE},
        bgcolor='rgba(255,255,255,0.92)',
    )
    return fig


def _build_light_time_figure(bodies, selected_name, focus_mode):
    focus_names = set(focus_body_names(focus_mode, bodies))
    planets = [body for body in bodies if body.name != 'Sun']
    colors = [
        _rgba(
            body.color,
            1.0 if body.name == selected_name else 0.9 if body.name in focus_names else 0.3,
        )
        for body in planets
    ]
    selected = get_body_lookup(bodies)[selected_name]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[body.name for body in planets],
        y=[body.light_time_minutes for body in planets],
        marker={'color': colors, 'line': {'width': 0}},
        customdata=[body.mean_distance_from_sun_km for body in planets],
        hovertemplate=(
            '%{x}<br>'
            'Light-travel time: %{y:,.1f} minutes<br>'
            'Distance from Sun: %{customdata:,.0f} km<extra></extra>'
        ),
    ))
    apply_chart_theme(
        fig,
        title='Light-Time View: How long sunlight takes to arrive',
        xaxis_title='Planet',
        yaxis_title='Light-travel time (minutes)',
        height=420,
    )
    if selected.name != 'Sun':
        fig.add_annotation(
            x=selected.name,
            y=selected.light_time_minutes,
            text=f'{selected.name}: {selected.light_time_minutes:,.1f} light-minutes',
            showarrow=False,
            yshift=18,
            font={'family': BODY_FONT, 'size': 12, 'color': PRUSSIAN_BLUE},
            bgcolor='rgba(255,255,255,0.92)',
        )
    return fig


def _build_apparent_sun_size_figure(bodies, selected_name, focus_mode):
    focus_names = set(focus_body_names(focus_mode, bodies))
    planets = [body for body in bodies if body.name != 'Sun']
    lookup = get_body_lookup(bodies)
    earth_angle = apparent_sun_angular_diameter_degrees('Earth', bodies)
    selected = lookup[selected_name]
    angle_arcminutes = [
        apparent_sun_angular_diameter_degrees(body.name, bodies) * 60
        for body in planets
    ]
    pixels_per_arcminute = MIN_APPARENT_SUN_DIAMETER_PX / min(angle_arcminutes)
    marker_sizes = [angle * pixels_per_arcminute for angle in angle_arcminutes]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[body.name for body in planets],
        y=angle_arcminutes,
        mode='markers',
        marker={
            'size': marker_sizes,
            'sizemode': 'diameter',
            'color': [
                _rgba(
                    body.color,
                    1.0 if body.name == selected_name else 0.9 if body.name in focus_names else 0.3,
                )
                for body in planets
            ],
            'line': {'width': 1.5, 'color': '#ffffff'},
        },
        customdata=[
            apparent_sun_angular_diameter_degrees(body.name, bodies) / earth_angle
            for body in planets
        ],
        hovertemplate=(
            '%{x}<br>'
            'Sun apparent diameter: %{y:,.2f} arcminutes<br>'
            'Vs Earth view: %{customdata:,.2f}×<extra></extra>'
        ),
    ))
    apply_chart_theme(
        fig,
        title='Apparent Sun Size: How large the Sun looks from each planet (to scale)',
        xaxis_title='Planet',
        yaxis_title='Sun angular diameter (arcminutes)',
        height=420,
    )
    fig.update_traces(cliponaxis=False)
    fig.add_hline(
        y=earth_angle * 60,
        line_width=1.5,
        line_dash='dash',
        line_color=DEEP_TEAL,
        annotation_text='Earth baseline',
        annotation_position='top left',
    )
    if selected.name != 'Sun':
        selected_angle_arcminutes = apparent_sun_angular_diameter_degrees(selected.name, bodies) * 60
        fig.add_annotation(
            x=selected.name,
            y=selected_angle_arcminutes,
            text=f'{selected.name}: {selected_angle_arcminutes:,.2f} arcminutes',
            showarrow=False,
            yshift=18,
            font={'family': BODY_FONT, 'size': 12, 'color': PRUSSIAN_BLUE},
            bgcolor='rgba(255,255,255,0.92)',
        )
    return fig


def _initial_scale_state():
    bodies = load_solar_system_bodies()
    return (
        _build_callout_cards(DEFAULT_BODY, DEFAULT_UNIT, bodies),
        _build_size_figure(bodies, DEFAULT_BODY, DEFAULT_FOCUS),
        _build_distance_figure(bodies, DEFAULT_BODY, DEFAULT_FOCUS, DEFAULT_UNIT),
        _build_light_time_figure(bodies, DEFAULT_BODY, DEFAULT_FOCUS),
        _build_apparent_sun_size_figure(bodies, DEFAULT_BODY, DEFAULT_FOCUS),
    )


def _initial_sandbox_state():
    return build_default_sandbox_state()


def _control_input(label, component_id, value, *, step='any', minimum=None, maximum=None):
    return html.Div(
        [
            html.Label(label, htmlFor=component_id, style={'fontSize': '0.92rem', 'fontWeight': 600, 'marginBottom': '0.3rem'}),
            dcc.Input(
                id=component_id,
                type='number',
                value=value,
                debounce=True,
                step=step,
                min=minimum,
                max=maximum,
                style={
                    'width': '100%',
                    'padding': '0.55rem 0.65rem',
                    'border': '1px solid #D8E0E8',
                    'borderRadius': '8px',
                },
            ),
        ],
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '0.15rem'},
    )


def _build_scale_explorer_tab(bodies, callout_cards, size_fig, distance_fig, light_time_fig, apparent_sun_size_fig):
    return html.Div(
        [
            html.Div(
                [
                    html.H3('Why three views?', style={'fontSize': '1.1rem', 'marginBottom': '0.5rem'}),
                    html.P(
                        'True size and true distance do not fit naturally on one chart. '
                        'This dashboard separates diameter, orbital spacing, and light-travel time '
                        'so each one stays intuitive instead of collapsing into a misleading single scale.',
                        style={'marginBottom': '0.65rem'},
                    ),
                    html.P(
                        'Pick a world, switch focus between the inner and outer Solar System, '
                        'and watch how the same neighborhood feels different when you measure it in kilometers, AU, or light-minutes.',
                        style={'marginBottom': 0},
                    ),
                ],
                style={**_card_style(), 'padding': '1rem 1.1rem', 'marginBottom': '1rem', 'color': PRUSSIAN_BLUE},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label('Highlighted object', htmlFor='solar-body-selector'),
                            dcc.Dropdown(
                                id='solar-body-selector',
                                options=[{'label': body.name, 'value': body.name} for body in bodies],
                                value=DEFAULT_BODY,
                                clearable=False,
                            ),
                        ],
                        style={'minWidth': '240px', 'flex': '1 1 240px'},
                    ),
                    html.Div(
                        [
                            html.Label('Focus preset'),
                            dcc.RadioItems(
                                id='solar-focus-mode',
                                options=[
                                    {'label': 'Inner Planets', 'value': 'inner-planets'},
                                    {'label': 'Outer Planets', 'value': 'outer-planets'},
                                    {'label': 'Whole System', 'value': 'whole-system'},
                                ],
                                value=DEFAULT_FOCUS,
                                inline=True,
                                inputStyle={'marginRight': '0.35rem', 'marginLeft': '0.75rem'},
                            ),
                        ],
                        style={'minWidth': '320px', 'flex': '2 1 320px'},
                    ),
                    html.Div(
                        [
                            html.Label('Distance unit'),
                            dcc.RadioItems(
                                id='solar-distance-unit',
                                options=[
                                    {'label': 'km', 'value': 'km'},
                                    {'label': 'AU', 'value': 'au'},
                                    {'label': 'light-minutes', 'value': 'light-minutes'},
                                ],
                                value=DEFAULT_UNIT,
                                inline=True,
                                inputStyle={'marginRight': '0.35rem', 'marginLeft': '0.75rem'},
                            ),
                        ],
                        style={'minWidth': '280px', 'flex': '1 1 280px'},
                    ),
                ],
                style={
                    **_card_style(),
                    'padding': '1rem',
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'gap': '12px',
                    'marginBottom': '1rem',
                    'color': PRUSSIAN_BLUE,
                },
            ),
            html.Div(
                id='solar-callout-cards',
                children=callout_cards,
                style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(230px, 1fr))',
                    'gap': '12px',
                    'marginBottom': '1rem',
                },
            ),
            html.Div(
                [
                    html.Div([dcc.Graph(id='solar-size-view', figure=size_fig)], style={'flex': '1 1 520px'}),
                    html.Div([dcc.Graph(id='solar-distance-view', figure=distance_fig)], style={'flex': '1 1 520px'}),
                ],
                style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px'},
            ),
            html.Div(
                [dcc.Graph(id='solar-light-time-view', figure=light_time_fig)],
                style={'marginTop': '0.35rem'},
            ),
            html.Div(
                [dcc.Graph(id='solar-apparent-sun-size-view', figure=apparent_sun_size_fig)],
                style={'marginTop': '0.35rem'},
            ),
        ],
        style={'paddingTop': '0.75rem'},
    )


def _build_sandbox_status(state):
    background = 'rgba(112, 141, 129, 0.12)' if state.get('running') else 'rgba(191, 6, 3, 0.08)' if 'paused' in state.get('status', '').lower() or 'collision' in state.get('status', '').lower() else 'rgba(0, 20, 39, 0.05)'
    return html.Div(
        state.get('status', ''),
        id='solar-sandbox-status',
        style={
            **_card_style(),
            'padding': '0.9rem 1rem',
            'background': background,
            'color': PRUSSIAN_BLUE,
        },
    )


def _build_sandbox_metric_cards(state, selected_name):
    body = get_state_body_lookup(state)[selected_name]
    accelerations = compute_accelerations(state['bodies'])
    body_index = next(index for index, candidate in enumerate(state['bodies']) if candidate['name'] == selected_name)
    acceleration = accelerations[body_index]
    distance_au = math.hypot(body['x_au'], body['y_au'])
    speed_km_s = math.hypot(body['vx_km_s'], body['vy_km_s'])
    acceleration_km_s2 = math.hypot(acceleration['ax_km_s2'], acceleration['ay_km_s2'])
    return [
        _metric_card(
            f'{selected_name} position',
            f'{distance_au:,.2f} AU',
            f'x={body["x_au"]:,.2f}, y={body["y_au"]:,.2f}',
        ),
        _metric_card(
            'Velocity',
            f'{speed_km_s:,.2f} km/s',
            f'vx={body["vx_km_s"]:,.2f}, vy={body["vy_km_s"]:,.2f}',
        ),
        _metric_card(
            'Gravity',
            f'{acceleration_km_s2:,.6f} km/s²',
            f'Mass {body["mass_kg"]:,.3e} kg · Diameter {body["diameter_km"]:,.0f} km',
        ),
        _metric_card(
            'Run state',
            f'{state["tick_count"]:,.0f} steps',
            f'{state["timestep_seconds"] / 3600:,.1f} hr timestep · {state["trail_length"]} trail points',
        ),
    ]


def _vector_endpoint(x_value, y_value, dx_value, dy_value, length_au):
    magnitude = math.hypot(dx_value, dy_value)
    if magnitude <= 0:
        return None
    return (
        x_value + (dx_value / magnitude) * length_au,
        y_value + (dy_value / magnitude) * length_au,
    )


def _marker_size(diameter_km, minimum_diameter_km):
    return 12 + 6 * math.log10(max(diameter_km / minimum_diameter_km, 1.0) + 1)


def _add_fading_trail_traces(fig, body):
    trail = body.get('trail', [])
    if len(trail) <= 1:
        return

    total_segments = min(TRAIL_FADE_SEGMENTS, len(trail) - 1)
    for segment_index in range(total_segments):
        start_index = round(segment_index * (len(trail) - 1) / total_segments)
        end_index = round((segment_index + 1) * (len(trail) - 1) / total_segments) + 1
        segment_points = trail[start_index:end_index]
        if len(segment_points) <= 1:
            continue

        age_ratio = (segment_index + 1) / total_segments
        alpha = 0.03 + 0.42 * (age_ratio ** 2.2)
        line_width = 1.2 + 0.9 * age_ratio
        fig.add_trace(go.Scatter(
            x=[point[0] for point in segment_points],
            y=[point[1] for point in segment_points],
            mode='lines',
            line={'color': _rgba(body['color'], alpha), 'width': line_width},
            hoverinfo='skip',
            showlegend=False,
        ))


def _build_sandbox_figure(state, selected_name):
    bodies = state['bodies']
    selected_body = get_state_body_lookup(state)[selected_name]
    accelerations = compute_accelerations(bodies)
    acceleration_lookup = {
        body['name']: acceleration
        for body, acceleration in zip(bodies, accelerations)
    }
    minimum_diameter_km = min(body['diameter_km'] for body in bodies if body['diameter_km'] > 0)
    axis_limit = max(2.0, max(math.hypot(body['x_au'], body['y_au']) for body in bodies) * 1.18)

    fig = go.Figure()
    for body in bodies:
        _add_fading_trail_traces(fig, body)

    for body in bodies:
        is_selected = body['name'] == selected_name
        fig.add_trace(go.Scatter(
            x=[body['x_au']],
            y=[body['y_au']],
            mode='markers+text' if is_selected else 'markers',
            text=[body['name']] if is_selected else None,
            textposition='top center',
            marker={
                'size': _marker_size(body['diameter_km'], minimum_diameter_km) + (5 if is_selected else 0),
                'color': _rgba(body['color'], 1.0 if is_selected else 0.9),
                'line': {'color': '#ffffff', 'width': 1.5},
            },
            customdata=[[body['diameter_km'], body['mass_kg'], body['vx_km_s'], body['vy_km_s']]],
            hovertemplate=(
                f'{body["name"]}<br>'
                'Position: (%{x:,.2f}, %{y:,.2f}) AU<br>'
                'Diameter: %{customdata[0]:,.0f} km<br>'
                'Mass: %{customdata[1]:.3e} kg<br>'
                'Velocity: (%{customdata[2]:,.2f}, %{customdata[3]:,.2f}) km/s<extra></extra>'
            ),
            showlegend=False,
        ))

    velocity_vector_length_au = max(0.4, axis_limit * 0.08)
    for body in bodies:
        velocity_endpoint = _vector_endpoint(
            body['x_au'],
            body['y_au'],
            body['vx_km_s'],
            body['vy_km_s'],
            velocity_vector_length_au,
        )
        if velocity_endpoint is None:
            continue
        is_selected = body['name'] == selected_name
        fig.add_trace(go.Scatter(
            x=[body['x_au'], velocity_endpoint[0]],
            y=[body['y_au'], velocity_endpoint[1]],
            mode='lines',
            line={
                'color': _rgba(DEEP_TEAL, 0.95 if is_selected else 0.38),
                'width': 3 if is_selected else 1.6,
            },
            name='Velocity vector' if is_selected else None,
            hoverinfo='skip',
            showlegend=is_selected,
        ))

    acceleration = acceleration_lookup[selected_name]
    acceleration_endpoint = _vector_endpoint(
        selected_body['x_au'],
        selected_body['y_au'],
        acceleration['ax_km_s2'],
        acceleration['ay_km_s2'],
        max(0.3, axis_limit * 0.06),
    )
    if acceleration_endpoint is not None:
        fig.add_trace(go.Scatter(
            x=[selected_body['x_au'], acceleration_endpoint[0]],
            y=[selected_body['y_au'], acceleration_endpoint[1]],
            mode='lines',
            line={'color': BRICK_EMBER, 'width': 3, 'dash': 'dash'},
            name='Gravity vector',
            hoverinfo='skip',
        ))

    apply_chart_theme(
        fig,
        title='Gravity Sandbox: Edit bodies and watch the system respond',
        xaxis_title='x position (AU)',
        yaxis_title='y position (AU)',
        height=620,
    )
    fig.update_layout(
        hovermode='closest',
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'left', 'x': 0},
        uirevision=f'gravity-sandbox-{selected_name}',
    )
    fig.update_xaxes(range=[-MAX_DISTANCE_AU, MAX_DISTANCE_AU], zeroline=True, zerolinecolor='#CED6DE')
    fig.update_yaxes(
        range=[-MAX_DISTANCE_AU, MAX_DISTANCE_AU],
        scaleanchor='x',
        scaleratio=1,
        zeroline=True,
        zerolinecolor='#CED6DE',
    )
    fig.add_annotation(
        x=selected_body['x_au'],
        y=selected_body['y_au'],
        text=f'{selected_name}',
        showarrow=False,
        yshift=16,
        font={'family': BODY_FONT, 'size': 12, 'color': PRUSSIAN_BLUE},
        bgcolor='rgba(255,255,255,0.92)',
    )
    return fig


def _build_sandbox_tab(bodies, state):
    selected_body = get_state_body_lookup(state)[DEFAULT_BODY]
    return html.Div(
        [
            html.Div(
                [
                    html.H3('Gravity Sandbox', style={'fontSize': '1.1rem', 'marginBottom': '0.5rem'}),
                    html.P(
                        'Edit one body at a time, then run a 2D Newtonian system with all planets still active. '
                        'Changing diameter keeps density fixed, so mass and gravity scale together.',
                        style={'marginBottom': '0.55rem'},
                    ),
                    html.P(
                        'Velocity and gravity vectors are shown for the selected body. '
                        'Collisions, runaway trajectories, and invalid states automatically pause the sandbox.',
                        style={'marginBottom': 0},
                    ),
                ],
                style={**_card_style(), 'padding': '1rem 1.1rem', 'marginBottom': '1rem', 'color': PRUSSIAN_BLUE},
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id='solar-sandbox-graph', figure=_build_sandbox_figure(state, DEFAULT_BODY))],
                        style={'flex': '1 1 640px'},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label('Selected body', htmlFor='solar-sandbox-selected-body'),
                                    dcc.Dropdown(
                                        id='solar-sandbox-selected-body',
                                        options=[{'label': body.name, 'value': body.name} for body in bodies],
                                        value=DEFAULT_BODY,
                                        clearable=False,
                                    ),
                                ],
                                style={'marginBottom': '0.85rem'},
                            ),
                            html.Div(
                                [
                                    _control_input('Diameter (km)', 'solar-sandbox-diameter', selected_body['diameter_km'], step=1, minimum=1),
                                    _control_input('x position (AU)', 'solar-sandbox-x-au', selected_body['x_au'], step='any', minimum=-60, maximum=60),
                                    _control_input('y position (AU)', 'solar-sandbox-y-au', selected_body['y_au'], step='any', minimum=-60, maximum=60),
                                    _control_input('vx (km/s)', 'solar-sandbox-vx', selected_body['vx_km_s'], step='any', minimum=-250, maximum=250),
                                    _control_input('vy (km/s)', 'solar-sandbox-vy', selected_body['vy_km_s'], step='any', minimum=-250, maximum=250),
                                    _control_input('Timestep (hours)', 'solar-sandbox-timestep', state['timestep_seconds'] / 3600, step=1, minimum=1, maximum=168),
                                    _control_input('Trail length (points)', 'solar-sandbox-trail-length', state['trail_length'], step=1, minimum=MIN_TRAIL_LENGTH, maximum=MAX_TRAIL_LENGTH),
                                ],
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': 'repeat(auto-fit, minmax(180px, 1fr))',
                                    'gap': '0.85rem',
                                },
                            ),
                            html.Div(
                                [
                                    html.Button('Play', id='solar-sandbox-play', n_clicks=0, style={'padding': '0.6rem 1rem'}),
                                    html.Button('Pause', id='solar-sandbox-pause', n_clicks=0, style={'padding': '0.6rem 1rem'}),
                                    html.Button('Reset', id='solar-sandbox-reset', n_clicks=0, style={'padding': '0.6rem 1rem'}),
                                ],
                                style={'display': 'flex', 'gap': '0.6rem', 'marginTop': '1rem', 'flexWrap': 'wrap'},
                            ),
                            html.Div(id='solar-sandbox-status-wrap', children=_build_sandbox_status(state), style={'marginTop': '1rem'}),
                        ],
                        style={**_card_style(), 'padding': '1rem', 'flex': '1 1 420px', 'color': PRUSSIAN_BLUE},
                    ),
                ],
                style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px'},
            ),
            html.Div(
                id='solar-sandbox-metrics',
                children=_build_sandbox_metric_cards(state, DEFAULT_BODY),
                style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(230px, 1fr))',
                    'gap': '12px',
                    'marginTop': '1rem',
                },
            ),
        ],
        style={'paddingTop': '0.75rem'},
    )


def _coerce_number(value, fallback, *, minimum=None, maximum=None, cast=float):
    if value is None:
        result = fallback
    else:
        result = cast(value)
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


def _apply_sandbox_action(
    triggered_id,
    state,
    selected_name,
    *,
    diameter_km,
    x_au,
    y_au,
    vx_km_s,
    vy_km_s,
    timestep_hours,
    trail_length,
):
    current_state = state or build_default_sandbox_state()
    selected_name = selected_name or DEFAULT_BODY

    if triggered_id == 'solar-sandbox-play':
        if current_state.get('running'):
            return current_state
        return set_running_state(current_state, True, status='Simulation running. Press Pause to freeze the system.')

    if triggered_id == 'solar-sandbox-pause':
        if not current_state.get('running'):
            return current_state
        return set_running_state(current_state, False, status='Simulation paused. Adjust the sandbox or press Play to resume.')

    if triggered_id == 'solar-sandbox-reset':
        return reset_sandbox_state()

    if triggered_id == 'solar-sandbox-interval':
        if not current_state.get('running'):
            return current_state
        return step_sandbox_state(current_state)

    if triggered_id in {'solar-sandbox-timestep', 'solar-sandbox-trail-length'}:
        next_timestep_seconds = _coerce_number(timestep_hours, current_state['timestep_seconds'] / 3600, minimum=1, maximum=168) * 3600
        next_trail_length = _coerce_number(trail_length, current_state['trail_length'], minimum=MIN_TRAIL_LENGTH, maximum=MAX_TRAIL_LENGTH, cast=int)
        if (
            math.isclose(next_timestep_seconds, current_state['timestep_seconds'], rel_tol=0, abs_tol=1e-9)
            and next_trail_length == current_state['trail_length']
        ):
            return current_state
        return update_sandbox_config(
            current_state,
            timestep_seconds=next_timestep_seconds,
            trail_length=next_trail_length,
        )

    if triggered_id in {
        'solar-sandbox-diameter',
        'solar-sandbox-x-au',
        'solar-sandbox-y-au',
        'solar-sandbox-vx',
        'solar-sandbox-vy',
    }:
        current_body = get_state_body_lookup(current_state)[selected_name]
        next_diameter = _coerce_number(diameter_km, current_body['diameter_km'], minimum=1)
        next_x = _coerce_number(x_au, current_body['x_au'], minimum=-60, maximum=60)
        next_y = _coerce_number(y_au, current_body['y_au'], minimum=-60, maximum=60)
        next_vx = _coerce_number(vx_km_s, current_body['vx_km_s'], minimum=-250, maximum=250)
        next_vy = _coerce_number(vy_km_s, current_body['vy_km_s'], minimum=-250, maximum=250)
        if (
            math.isclose(next_diameter, current_body['diameter_km'], rel_tol=0, abs_tol=1e-9)
            and math.isclose(next_x, current_body['x_au'], rel_tol=0, abs_tol=1e-12)
            and math.isclose(next_y, current_body['y_au'], rel_tol=0, abs_tol=1e-12)
            and math.isclose(next_vx, current_body['vx_km_s'], rel_tol=0, abs_tol=1e-12)
            and math.isclose(next_vy, current_body['vy_km_s'], rel_tol=0, abs_tol=1e-12)
        ):
            return current_state
        return update_body_state(
            current_state,
            selected_name,
            diameter_km=next_diameter,
            x_au=next_x,
            y_au=next_y,
            vx_km_s=next_vx,
            vy_km_s=next_vy,
        )

    return current_state


def layout():
    """Render the Solar System Scale dashboard."""
    bodies = load_solar_system_bodies()
    callout_cards, size_fig, distance_fig, light_time_fig, apparent_sun_size_fig = _initial_scale_state()
    sandbox_state = _initial_sandbox_state()

    return html.Div(
        [
            dcc.Store(id='solar-sandbox-state', data=sandbox_state),
            dcc.Interval(id='solar-sandbox-interval', interval=700, n_intervals=0, disabled=True),
            html.H2(DASHBOARD_CONFIG['title'], style={'fontFamily': DISPLAY_FONT}),
            html.P(
                'Explore the original scale comparisons or switch into a hands-on gravity sandbox '
                'to see how size, position, and velocity change the system.',
                style={'color': PRUSSIAN_BLUE, 'maxWidth': '72ch', 'marginBottom': '1rem'},
            ),
            dcc.Tabs(
                id='solar-dashboard-tabs',
                value=SCALE_TAB,
                children=[
                    dcc.Tab(
                        label='Scale Explorer',
                        value=SCALE_TAB,
                        children=_build_scale_explorer_tab(
                            bodies,
                            callout_cards,
                            size_fig,
                            distance_fig,
                            light_time_fig,
                            apparent_sun_size_fig,
                        ),
                    ),
                    dcc.Tab(
                        label='Gravity Sandbox',
                        value=SANDBOX_TAB,
                        children=_build_sandbox_tab(bodies, sandbox_state),
                    ),
                ],
            ),
        ],
        style={'padding': '1rem'},
    )


@callback(
    Output('solar-callout-cards', 'children'),
    Output('solar-size-view', 'figure'),
    Output('solar-distance-view', 'figure'),
    Output('solar-light-time-view', 'figure'),
    Output('solar-apparent-sun-size-view', 'figure'),
    Input('solar-body-selector', 'value'),
    Input('solar-focus-mode', 'value'),
    Input('solar-distance-unit', 'value'),
)
def update_dashboard(selected_name, focus_mode, unit):
    """Update all scale-explorer views from the current dashboard controls."""
    bodies = load_solar_system_bodies()
    selected_name = selected_name or DEFAULT_BODY
    focus_mode = focus_mode or DEFAULT_FOCUS
    unit = unit or DEFAULT_UNIT
    return (
        _build_callout_cards(selected_name, unit, bodies),
        _build_size_figure(bodies, selected_name, focus_mode),
        _build_distance_figure(bodies, selected_name, focus_mode, unit),
        _build_light_time_figure(bodies, selected_name, focus_mode),
        _build_apparent_sun_size_figure(bodies, selected_name, focus_mode),
    )


@callback(
    Output('solar-sandbox-state', 'data'),
    Output('solar-sandbox-interval', 'disabled'),
    Input('solar-sandbox-play', 'n_clicks'),
    Input('solar-sandbox-pause', 'n_clicks'),
    Input('solar-sandbox-reset', 'n_clicks'),
    Input('solar-sandbox-interval', 'n_intervals'),
    Input('solar-sandbox-diameter', 'value'),
    Input('solar-sandbox-x-au', 'value'),
    Input('solar-sandbox-y-au', 'value'),
    Input('solar-sandbox-vx', 'value'),
    Input('solar-sandbox-vy', 'value'),
    Input('solar-sandbox-timestep', 'value'),
    Input('solar-sandbox-trail-length', 'value'),
    State('solar-sandbox-selected-body', 'value'),
    State('solar-sandbox-state', 'data'),
    prevent_initial_call=True,
)
def update_sandbox_state(
    _play_clicks,
    _pause_clicks,
    _reset_clicks,
    _n_intervals,
    diameter_km,
    x_au,
    y_au,
    vx_km_s,
    vy_km_s,
    timestep_hours,
    trail_length,
    selected_name,
    state,
):
    """Update sandbox state from controls, actions, and simulation ticks."""
    current_state = state or build_default_sandbox_state()
    next_state = _apply_sandbox_action(
        ctx.triggered_id,
        current_state,
        selected_name,
        diameter_km=diameter_km,
        x_au=x_au,
        y_au=y_au,
        vx_km_s=vx_km_s,
        vy_km_s=vy_km_s,
        timestep_hours=timestep_hours,
        trail_length=trail_length,
    )
    if next_state == current_state:
        return no_update, no_update
    return next_state, not next_state.get('running', False)


@callback(
    Output('solar-sandbox-diameter', 'value'),
    Output('solar-sandbox-x-au', 'value'),
    Output('solar-sandbox-y-au', 'value'),
    Output('solar-sandbox-vx', 'value'),
    Output('solar-sandbox-vy', 'value'),
    Output('solar-sandbox-timestep', 'value'),
    Output('solar-sandbox-trail-length', 'value'),
    Input('solar-sandbox-selected-body', 'value'),
    Input('solar-sandbox-state', 'data'),
)
def sync_sandbox_controls(selected_name, state):
    """Sync editor controls with the current store state."""
    current_state = state or build_default_sandbox_state()
    selected_name = selected_name or DEFAULT_BODY
    body = get_state_body_lookup(current_state)[selected_name]
    return (
        body['diameter_km'],
        body['x_au'],
        body['y_au'],
        body['vx_km_s'],
        body['vy_km_s'],
        current_state['timestep_seconds'] / 3600,
        current_state['trail_length'],
    )


@callback(
    Output('solar-sandbox-graph', 'figure'),
    Output('solar-sandbox-status-wrap', 'children'),
    Output('solar-sandbox-metrics', 'children'),
    Input('solar-sandbox-state', 'data'),
    Input('solar-sandbox-selected-body', 'value'),
)
def render_sandbox(selected_state, selected_name):
    """Render the sandbox figure, status, and summary metrics."""
    state = selected_state or build_default_sandbox_state()
    selected_name = selected_name or DEFAULT_BODY
    return (
        _build_sandbox_figure(state, selected_name),
        _build_sandbox_status(state),
        _build_sandbox_metric_cards(state, selected_name),
    )


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
