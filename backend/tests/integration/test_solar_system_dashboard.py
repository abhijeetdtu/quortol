"""Integration tests for the Solar System dashboard route."""

from dash import Dash, page_registry

from backend.app import create_app
from backend.dashboards.solar_system.simulation import build_default_sandbox_state, set_running_state


def _collect_component_ids(component):
    component_id = getattr(component, 'id', None)
    collected = {component_id} if component_id else set()
    children = getattr(component, 'children', None)
    if isinstance(children, (list, tuple)):
        for child in children:
            collected.update(_collect_component_ids(child))
    elif children is not None:
        collected.update(_collect_component_ids(children))
    return collected


def _page_module():
    Dash(__name__, use_pages=True, pages_folder='')
    from backend.dashboards.solar_system import page as solar_page

    return solar_page


def _body_values(state, name):
    body = next(body for body in state['bodies'] if body['name'] == name)
    return {
        'diameter_km': body['diameter_km'],
        'x_au': body['x_au'],
        'y_au': body['y_au'],
        'vx_km_s': body['vx_km_s'],
        'vy_km_s': body['vy_km_s'],
        'timestep_hours': state['timestep_seconds'] / 3600,
        'trail_length': state['trail_length'],
    }


def test_solar_system_dashboard_is_registered_and_served():
    app = create_app(enable_dash=True)
    client = app.test_client()

    response = client.get('/data-storytelling-app/solar-system-scale')

    assert response.status_code == 200

    solar_pages = [
        page
        for page in page_registry.values()
        if page.get('path') == '/solar-system-scale'
    ]
    assert solar_pages
    assert solar_pages[0]['title'] == 'Solar System Scale Dashboard'
    assert callable(solar_pages[0]['layout'])


def test_layout_contains_scale_and_sandbox_components():
    app = create_app(enable_dash=True)
    assert app is not None

    solar_page = _page_module()
    layout = solar_page.layout()
    component_ids = _collect_component_ids(layout)

    assert 'solar-size-view' in component_ids
    assert 'solar-distance-view' in component_ids
    assert 'solar-apparent-sun-size-view' in component_ids
    assert 'solar-sandbox-state' in component_ids
    assert 'solar-sandbox-interval' in component_ids
    assert 'solar-sandbox-graph' in component_ids
    assert 'solar-sandbox-selected-body' in component_ids
    assert 'solar-sandbox-play' in component_ids
    assert 'solar-sandbox-pause' in component_ids
    assert 'solar-sandbox-reset' in component_ids
    assert 'solar-dashboard-tabs' in component_ids


def test_reset_restores_canonical_sandbox_state():
    solar_page = _page_module()
    default_state = build_default_sandbox_state()
    edited_state = solar_page._apply_sandbox_action(
        'solar-sandbox-diameter',
        default_state,
        'Earth',
        diameter_km=20_000,
        x_au=1.8,
        y_au=0.3,
        vx_km_s=0.0,
        vy_km_s=15.0,
        timestep_hours=default_state['timestep_seconds'] / 3600,
        trail_length=default_state['trail_length'],
    )
    reset_state = solar_page._apply_sandbox_action(
        'solar-sandbox-reset',
        edited_state,
        'Earth',
        **_body_values(edited_state, 'Earth'),
    )

    default_earth = next(body for body in default_state['bodies'] if body['name'] == 'Earth')
    reset_earth = next(body for body in reset_state['bodies'] if body['name'] == 'Earth')

    assert reset_state['running'] is False
    assert reset_earth['diameter_km'] == default_earth['diameter_km']
    assert reset_earth['mass_kg'] == default_earth['mass_kg']
    assert reset_earth['x_au'] == default_earth['x_au']
    assert reset_earth['y_au'] == default_earth['y_au']


def test_interval_tick_advances_when_running_and_not_when_paused():
    solar_page = _page_module()
    paused_state = build_default_sandbox_state()
    paused_result = solar_page._apply_sandbox_action(
        'solar-sandbox-interval',
        paused_state,
        'Earth',
        **_body_values(paused_state, 'Earth'),
    )

    running_state = set_running_state(build_default_sandbox_state(), True)
    earth_before = next(body for body in running_state['bodies'] if body['name'] == 'Earth')
    running_result = solar_page._apply_sandbox_action(
        'solar-sandbox-interval',
        running_state,
        'Earth',
        **_body_values(running_state, 'Earth'),
    )
    earth_after = next(body for body in running_result['bodies'] if body['name'] == 'Earth')

    assert paused_result == paused_state
    assert running_result['tick_count'] == 1
    assert earth_after['x_au'] != earth_before['x_au'] or earth_after['y_au'] != earth_before['y_au']
