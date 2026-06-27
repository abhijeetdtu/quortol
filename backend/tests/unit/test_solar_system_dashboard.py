"""Unit tests for the Solar System dashboard helpers."""

from functools import lru_cache

from dash import Dash
import pytest

from backend.dashboards.solar_system.data import (
    AU_IN_KM,
    apparent_sun_angular_diameter_degrees,
    build_comparison_summary,
    convert_distance,
    focus_body_names,
    load_solar_system_bodies,
)
from backend.dashboards.solar_system.simulation import (
    build_default_sandbox_state,
    compute_accelerations,
    mass_for_resized_body,
    reset_sandbox_state,
    step_sandbox_state,
    update_body_state,
    validate_state_message,
    volume_from_diameter_km,
)


@lru_cache(maxsize=1)
def _page_module():
    Dash(__name__, use_pages=True, pages_folder='')
    from backend.dashboards.solar_system import page as solar_page

    return solar_page


def test_load_solar_system_bodies_orders_and_normalizes():
    bodies = load_solar_system_bodies()

    assert len(bodies) == 9
    assert bodies[0].name == 'Sun'
    assert bodies[-1].name == 'Neptune'
    assert [body.order for body in bodies] == sorted(body.order for body in bodies)


def test_earth_derived_metrics_are_calculated_from_distance():
    earth = next(body for body in load_solar_system_bodies() if body.name == 'Earth')

    assert earth.distance_au == pytest.approx(earth.mean_distance_from_sun_km / AU_IN_KM, rel=1e-6)
    assert earth.distance_au == pytest.approx(1.0, rel=5e-5)
    assert earth.light_time_minutes == pytest.approx(8.3167, rel=2e-3)


def test_convert_distance_supports_all_units():
    earth = next(body for body in load_solar_system_bodies() if body.name == 'Earth')

    assert convert_distance(earth.mean_distance_from_sun_km, 'km') == pytest.approx(149_598_262)
    assert convert_distance(earth.mean_distance_from_sun_km, 'au') == pytest.approx(1.0, rel=5e-5)
    assert convert_distance(earth.mean_distance_from_sun_km, 'light-minutes') == pytest.approx(8.3167, rel=2e-3)


def test_build_comparison_summary_for_earth_and_sun():
    earth_summary = build_comparison_summary('Earth', 'au')
    sun_summary = build_comparison_summary('Sun', 'km')

    assert earth_summary['diameter_ratio_vs_earth'] == pytest.approx(1.0)
    assert earth_summary['selected_distance_value'] == pytest.approx(1.0, rel=5e-5)
    assert earth_summary['diameter_ratio_vs_sun'] == pytest.approx(12_742 / 1_392_700, rel=1e-6)

    assert sun_summary['selected_distance_value'] == 0.0
    assert sun_summary['diameter_ratio_vs_sun'] == pytest.approx(1.0)
    assert sun_summary['diameter_ratio_vs_earth'] > 100
    assert earth_summary['apparent_sun_ratio_vs_earth'] == pytest.approx(1.0)
    assert earth_summary['apparent_sun_angle_arcminutes'] == pytest.approx(31.97, rel=2e-2)


def test_apparent_sun_angle_shrinks_with_distance():
    mercury_angle = apparent_sun_angular_diameter_degrees('Mercury')
    earth_angle = apparent_sun_angular_diameter_degrees('Earth')
    neptune_angle = apparent_sun_angular_diameter_degrees('Neptune')

    assert mercury_angle > earth_angle > neptune_angle
    assert earth_angle == pytest.approx(0.533, rel=2e-2)


def test_focus_body_names_match_expected_presets():
    assert focus_body_names('inner-planets') == ('Sun', 'Mercury', 'Venus', 'Earth', 'Mars')
    assert focus_body_names('outer-planets') == ('Sun', 'Jupiter', 'Saturn', 'Uranus', 'Neptune')
    assert 'Neptune' in focus_body_names('whole-system')


def test_figure_builders_render_data_and_annotations():
    bodies = load_solar_system_bodies()
    solar_page = _page_module()

    size_fig = solar_page._build_size_figure(bodies, 'Earth', 'whole-system')
    distance_fig = solar_page._build_distance_figure(bodies, 'Earth', 'inner-planets', 'au')
    light_time_fig = solar_page._build_light_time_figure(bodies, 'Earth', 'whole-system')
    apparent_sun_size_fig = solar_page._build_apparent_sun_size_figure(bodies, 'Earth', 'whole-system')

    assert len(size_fig.data) >= 1
    assert len(distance_fig.data) >= 2
    assert len(light_time_fig.data) >= 1
    assert len(apparent_sun_size_fig.data) >= 1

    assert any('Earth:' in annotation.text for annotation in size_fig.layout.annotations)
    assert any('Earth:' in annotation.text for annotation in distance_fig.layout.annotations)
    assert any('Earth:' in annotation.text for annotation in light_time_fig.layout.annotations)
    assert any('Earth:' in annotation.text for annotation in apparent_sun_size_fig.layout.annotations)


def test_distance_view_updates_axis_label_for_selected_unit():
    bodies = load_solar_system_bodies()
    solar_page = _page_module()

    au_fig = solar_page._build_distance_figure(bodies, 'Earth', 'whole-system', 'au')
    light_fig = solar_page._build_distance_figure(bodies, 'Earth', 'whole-system', 'light-minutes')

    assert 'AU' in au_fig.layout.xaxis.title.text
    assert 'light-minutes' in light_fig.layout.xaxis.title.text


def test_default_sandbox_state_includes_mass_and_orbital_state():
    bodies = load_solar_system_bodies()
    sandbox_state = build_default_sandbox_state()
    earth = next(body for body in bodies if body.name == 'Earth')
    earth_state = next(body for body in sandbox_state['bodies'] if body['name'] == 'Earth')

    assert earth.mass_kg > 0
    assert earth.default_phase_degrees > 0
    assert earth_state['mass_kg'] == pytest.approx(earth.mass_kg)
    assert math_hypot(earth_state['x_au'], earth_state['y_au']) == pytest.approx(earth.distance_au, rel=5e-5)
    assert math_hypot(earth_state['vx_km_s'], earth_state['vy_km_s']) > 20
    assert earth_state['trail'] == [[earth_state['x_au'], earth_state['y_au']]]


def test_fixed_density_resizing_changes_mass_by_volume_ratio():
    bodies = load_solar_system_bodies()
    earth = next(body for body in bodies if body.name == 'Earth')
    doubled_diameter_km = earth.diameter_km * 2
    resized_mass = mass_for_resized_body('Earth', doubled_diameter_km, bodies)

    assert resized_mass / earth.mass_kg == pytest.approx(
        volume_from_diameter_km(doubled_diameter_km) / volume_from_diameter_km(earth.diameter_km),
    )


def test_pairwise_gravity_is_directionally_correct_and_symmetric():
    bodies = [
        {'name': 'Left', 'diameter_km': 1_000, 'mass_kg': 2e24, 'x_au': 0.0, 'y_au': 0.0, 'vx_km_s': 0.0, 'vy_km_s': 0.0},
        {'name': 'Right', 'diameter_km': 1_000, 'mass_kg': 3e24, 'x_au': 1.0, 'y_au': 0.0, 'vx_km_s': 0.0, 'vy_km_s': 0.0},
    ]
    accelerations = compute_accelerations(bodies)

    assert accelerations[0]['ax_km_s2'] > 0
    assert accelerations[1]['ax_km_s2'] < 0
    assert accelerations[0]['ay_km_s2'] == pytest.approx(0.0)
    assert accelerations[1]['ay_km_s2'] == pytest.approx(0.0)
    assert bodies[0]['mass_kg'] * accelerations[0]['ax_km_s2'] == pytest.approx(
        -bodies[1]['mass_kg'] * accelerations[1]['ax_km_s2'],
    )


def test_single_step_updates_position_velocity_and_trail():
    state = {
        'bodies': [
            {'name': 'Sun', 'diameter_km': 1_392_700, 'mass_kg': 1.9885e30, 'x_au': 0.0, 'y_au': 0.0, 'vx_km_s': 0.0, 'vy_km_s': 0.0, 'trail': [[0.0, 0.0]]},
            {'name': 'Earth', 'diameter_km': 12_742, 'mass_kg': 5.97237e24, 'x_au': 1.0, 'y_au': 0.0, 'vx_km_s': 0.0, 'vy_km_s': 29.78, 'trail': [[1.0, 0.0]]},
        ],
        'running': True,
        'timestep_seconds': 3600.0,
        'trail_length': 10,
        'tick_count': 0,
        'status': '',
    }

    stepped = step_sandbox_state(state)
    earth = next(body for body in stepped['bodies'] if body['name'] == 'Earth')

    assert stepped['tick_count'] == 1
    assert earth['y_au'] > 0
    assert earth['vx_km_s'] < 0
    assert len(earth['trail']) == 2


def test_collision_and_instability_pause_simulation():
    collision_state = reset_sandbox_state()
    collision_state = update_body_state(collision_state, 'Earth', x_au=0.0, y_au=0.0)
    collision_state['running'] = True
    collision_result = step_sandbox_state(collision_state)

    assert collision_result['running'] is False
    assert 'Collision detected' in collision_result['status']

    instability_state = reset_sandbox_state()
    instability_state = update_body_state(instability_state, 'Neptune', x_au=61.0, y_au=0.0)
    instability_state['running'] = True
    instability_result = step_sandbox_state(instability_state)

    assert instability_result['running'] is False
    assert 'drifted beyond 60 AU' in instability_result['status']
    assert validate_state_message(instability_result['bodies']) is not None


def test_sandbox_figure_renders_selected_vectors():
    solar_page = _page_module()
    sandbox_fig = solar_page._build_sandbox_figure(build_default_sandbox_state(), 'Earth')

    assert len(sandbox_fig.data) >= 3
    trace_names = {trace.name for trace in sandbox_fig.data if getattr(trace, 'name', None)}
    assert 'Velocity vector' in trace_names
    assert 'Gravity vector' in trace_names


def math_hypot(x_value, y_value):
    return (x_value ** 2 + y_value ** 2) ** 0.5
