"""Unit tests for reusable route-map helpers."""

import pytest

from backend.dashboards.maps import MapWaypoint, build_route_map_figure, validate_waypoints


def _sample_waypoints():
    return [
        MapWaypoint(
            id='b',
            sequence=2,
            title='Waypoint B',
            latitude=31.0,
            longitude=-92.0,
            phase='middle',
            date_label='1530',
            summary='Second stop.',
            confidence='approximate',
            notes='Approximate location.',
        ),
        MapWaypoint(
            id='a',
            sequence=1,
            title='Waypoint A',
            latitude=29.0,
            longitude=-90.0,
            phase='start',
            date_label='1529',
            summary='First stop.',
            confidence='high',
            notes='Well attested.',
        ),
        MapWaypoint(
            id='c',
            sequence=3,
            title='Waypoint C',
            latitude=33.0,
            longitude=-95.0,
            phase='end',
            date_label='1531',
            summary='Third stop.',
            confidence='debated',
            notes='Debated leg.',
        ),
    ]


def test_validate_waypoints_orders_by_sequence():
    ordered = validate_waypoints(_sample_waypoints())

    assert [waypoint.id for waypoint in ordered] == ['a', 'b', 'c']


def test_validate_waypoints_rejects_missing_required_fields():
    with pytest.raises(ValueError, match='missing a summary'):
        validate_waypoints(
            [
                MapWaypoint(
                    id='bad',
                    sequence=1,
                    title='Bad',
                    latitude=0.0,
                    longitude=0.0,
                    phase='phase',
                    date_label='1528',
                    summary='',
                    confidence='high',
                )
            ]
        )


def test_build_route_map_figure_trace_counts_depend_on_reveal_mode():
    waypoints = _sample_waypoints()

    full_route = build_route_map_figure(
        waypoints,
        active_waypoint_id='b',
        reveal_mode='full-route',
    )
    progressive = build_route_map_figure(
        waypoints,
        active_waypoint_id='b',
        reveal_mode='progressive-reveal',
    )

    assert len(full_route.data) == 4
    assert len(progressive.data) == 3


def test_build_route_map_figure_highlights_active_waypoint_and_uncertainty():
    figure = build_route_map_figure(
        _sample_waypoints(),
        active_waypoint_id='b',
        reveal_mode='full-route',
    )

    active_trace = figure.data[-1]
    first_segment = figure.data[0]

    assert active_trace.marker.symbol == 'diamond'
    assert 'Approximate reconstruction' in active_trace.hovertemplate
    assert first_segment.line.dash == 'dash'

