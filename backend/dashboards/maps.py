"""Reusable geographic route-map helpers for Data Storytelling dashboards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import plotly.graph_objects as go

from .theme import BODY_FONT, DEEP_TEAL, JASMINE, PRUSSIAN_BLUE

RevealMode = Literal['full-route', 'progressive-reveal']
ConfidenceLevel = Literal['high', 'approximate', 'debated']

_CONFIDENCE_LABELS: dict[str, str] = {
    'high': 'High confidence',
    'approximate': 'Approximate reconstruction',
    'debated': 'Debated segment',
}
_CONFIDENCE_ALPHA: dict[str, float] = {
    'high': 0.92,
    'approximate': 0.52,
    'debated': 0.34,
}
_CONFIDENCE_DASH: dict[str, str] = {
    'high': 'solid',
    'approximate': 'dash',
    'debated': 'dot',
}
_CONFIDENCE_COLOR: dict[str, str] = {
    'high': DEEP_TEAL,
    'approximate': JASMINE,
    'debated': '#BF8B2E',
}


@dataclass(frozen=True)
class MapWaypoint:
    """A reusable waypoint contract for narrative route dashboards."""

    id: str
    sequence: int
    title: str
    latitude: float
    longitude: float
    phase: str
    date_label: str
    summary: str
    confidence: ConfidenceLevel
    notes: str = ''
    days_since_shipwreck: int | None = None


def _rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    return f'rgba({red}, {green}, {blue}, {alpha})'


def _phase_label(phase: str) -> str:
    return phase.replace('-', ' ').replace('_', ' ').title()


def _confidence_label(confidence: str) -> str:
    return _CONFIDENCE_LABELS.get(confidence, confidence.replace('-', ' ').title())


def validate_waypoints(waypoints: Iterable[MapWaypoint]) -> list[MapWaypoint]:
    """Validate waypoint shape and return them in stable sequence order."""
    ordered = sorted(list(waypoints), key=lambda waypoint: (waypoint.sequence, waypoint.id))
    if not ordered:
        raise ValueError('At least one waypoint is required.')

    seen_ids: set[str] = set()
    seen_sequences: set[int] = set()

    for waypoint in ordered:
        if not waypoint.id.strip():
            raise ValueError('Waypoint id is required.')
        if waypoint.id in seen_ids:
            raise ValueError(f'Duplicate waypoint id: {waypoint.id}')
        seen_ids.add(waypoint.id)

        if waypoint.sequence in seen_sequences:
            raise ValueError(f'Duplicate waypoint sequence: {waypoint.sequence}')
        seen_sequences.add(waypoint.sequence)

        if not waypoint.title.strip():
            raise ValueError(f'Waypoint {waypoint.id} is missing a title.')
        if not waypoint.phase.strip():
            raise ValueError(f'Waypoint {waypoint.id} is missing a phase.')
        if not waypoint.date_label.strip():
            raise ValueError(f'Waypoint {waypoint.id} is missing a date label.')
        if not waypoint.summary.strip():
            raise ValueError(f'Waypoint {waypoint.id} is missing a summary.')
        if waypoint.confidence not in _CONFIDENCE_LABELS:
            raise ValueError(
                f'Waypoint {waypoint.id} confidence must be one of '
                f'{", ".join(sorted(_CONFIDENCE_LABELS))}.'
            )
        if waypoint.days_since_shipwreck is not None and waypoint.days_since_shipwreck < 0:
            raise ValueError(f'Waypoint {waypoint.id} days_since_shipwreck must be non-negative.')
        if not -90 <= waypoint.latitude <= 90:
            raise ValueError(f'Waypoint {waypoint.id} latitude is out of range.')
        if not -180 <= waypoint.longitude <= 180:
            raise ValueError(f'Waypoint {waypoint.id} longitude is out of range.')

    return ordered


def build_hover_text(waypoint: MapWaypoint) -> str:
    """Build route hover content with explicit uncertainty messaging."""
    notes = (
        f'<br><b>Notes:</b> {waypoint.notes}'
        if waypoint.notes.strip()
        else ''
    )
    return (
        f'<b>{waypoint.title}</b>'
        f'<br>{waypoint.date_label}'
        f'<br>Phase: {_phase_label(waypoint.phase)}'
        f'<br>Confidence: {_confidence_label(waypoint.confidence)}'
        f'<br>{waypoint.summary}'
        f'{notes}'
    )


def partition_route_segments(
    waypoints: Iterable[MapWaypoint],
    *,
    active_waypoint_id: str | None = None,
    reveal_mode: RevealMode = 'full-route',
) -> list[dict[str, object]]:
    """Partition visible route legs for rendering."""
    ordered = validate_waypoints(waypoints)
    active_id = active_waypoint_id or ordered[0].id
    active_index = next(
        (index for index, waypoint in enumerate(ordered) if waypoint.id == active_id),
        0,
    )
    cutoff = len(ordered) - 1 if reveal_mode == 'full-route' else active_index
    segments: list[dict[str, object]] = []

    for index in range(len(ordered) - 1):
        if index >= cutoff:
            break
        start = ordered[index]
        end = ordered[index + 1]
        confidence = (
            'high'
            if start.confidence == 'high' and end.confidence == 'high'
            else 'debated'
            if 'debated' in {start.confidence, end.confidence}
            else 'approximate'
        )
        segments.append(
            {
                'start': start,
                'end': end,
                'confidence': confidence,
            }
        )
    return segments


def build_route_map_figure(
    waypoints: Iterable[MapWaypoint],
    *,
    active_waypoint_id: str | None = None,
    reveal_mode: RevealMode = 'full-route',
) -> go.Figure:
    """Render a narrative route map using Plotly geo traces."""
    ordered = validate_waypoints(waypoints)
    active_id = active_waypoint_id or ordered[0].id
    active_index = next(
        (index for index, waypoint in enumerate(ordered) if waypoint.id == active_id),
        0,
    )
    active_waypoint = ordered[active_index]
    visible_segments = partition_route_segments(
        ordered,
        active_waypoint_id=active_waypoint.id,
        reveal_mode=reveal_mode,
    )

    fig = go.Figure()

    for segment in visible_segments:
        start = segment['start']
        end = segment['end']
        confidence = str(segment['confidence'])
        fig.add_trace(
            go.Scattergeo(
                lon=[start.longitude, end.longitude],
                lat=[start.latitude, end.latitude],
                mode='lines',
                line={
                    'color': _rgba(_CONFIDENCE_COLOR[confidence], _CONFIDENCE_ALPHA[confidence]),
                    'width': 4 if confidence == 'high' else 3,
                    'dash': _CONFIDENCE_DASH[confidence],
                },
                hovertemplate=(
                    f'{start.title} → {end.title}'
                    f'<br>Confidence: {_confidence_label(confidence)}'
                    '<extra></extra>'
                ),
                showlegend=False,
            )
        )

    inactive_waypoints = [waypoint for waypoint in ordered if waypoint.id != active_waypoint.id]
    if inactive_waypoints:
        marker_opacity = [
            0.95
            if reveal_mode == 'full-route' or waypoint.sequence <= active_waypoint.sequence
            else 0.35
            for waypoint in inactive_waypoints
        ]
        marker_sizes = [
            13 if waypoint.sequence <= active_waypoint.sequence else 10
            for waypoint in inactive_waypoints
        ]
        marker_colors = [
            _rgba(_CONFIDENCE_COLOR[waypoint.confidence], opacity)
            for waypoint, opacity in zip(inactive_waypoints, marker_opacity)
        ]
        fig.add_trace(
            go.Scattergeo(
                lon=[waypoint.longitude for waypoint in inactive_waypoints],
                lat=[waypoint.latitude for waypoint in inactive_waypoints],
                mode='markers',
                marker={
                    'size': marker_sizes,
                    'color': marker_colors,
                    'line': {'color': '#ffffff', 'width': 1.5},
                },
                text=[build_hover_text(waypoint) for waypoint in inactive_waypoints],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scattergeo(
            lon=[active_waypoint.longitude],
            lat=[active_waypoint.latitude],
            mode='markers+text',
            text=[active_waypoint.title],
            textposition='top center',
            marker={
                'size': 18,
                'color': _rgba(PRUSSIAN_BLUE, 0.98),
                'line': {'color': '#ffffff', 'width': 2.4},
                'symbol': 'diamond',
            },
            hovertemplate=f'{build_hover_text(active_waypoint)}<extra></extra>',
            name='Selected stop',
            showlegend=False,
        )
    )

    latitudes = [waypoint.latitude for waypoint in ordered]
    longitudes = [waypoint.longitude for waypoint in ordered]
    latitude_padding = max(4, (max(latitudes) - min(latitudes)) * 0.18)
    longitude_padding = max(6, (max(longitudes) - min(longitudes)) * 0.12)

    fig.update_geos(
        scope='north america',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(248, 246, 238)',
        showocean=True,
        oceancolor='rgb(233, 241, 247)',
        showcountries=True,
        countrycolor='rgb(214, 221, 229)',
        coastlinecolor='rgb(176, 190, 197)',
        lataxis_range=[min(latitudes) - latitude_padding, max(latitudes) + latitude_padding],
        lonaxis_range=[min(longitudes) - longitude_padding, max(longitudes) + longitude_padding],
    )
    fig.update_layout(
        title='Route Map',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'color': PRUSSIAN_BLUE, 'family': BODY_FONT, 'size': 12},
        title_font={'size': 18},
        height=620,
        margin={'l': 0, 'r': 0, 't': 52, 'b': 0},
        geo_bgcolor='white',
    )
    return fig
