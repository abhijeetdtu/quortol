"""Gravity sandbox helpers for the solar system dashboard."""

from copy import deepcopy
from math import cos, hypot, isfinite, pi, radians, sin, sqrt

from .data import AU_IN_KM, get_body_lookup, load_solar_system_bodies

G_KM = 6.67430e-20
DEFAULT_TIMESTEP_SECONDS = 43_200.0
DEFAULT_TRAIL_LENGTH = 360
DEFAULT_STATUS = 'Ready. Adjust a body, then press Play.'
MAX_DISTANCE_AU = 60.0


def volume_from_diameter_km(diameter_km):
    """Return a sphere volume in cubic kilometers."""
    radius_km = float(diameter_km) / 2
    return (4.0 / 3.0) * pi * radius_km ** 3


def density_for_body(body):
    """Return the average density of a body in kg per cubic kilometer."""
    volume = volume_from_diameter_km(body.diameter_km)
    return body.mass_kg / volume if volume else 0.0


def mass_for_resized_body(body_name, diameter_km, bodies=None):
    """Scale mass by fixed density for a resized body."""
    lookup = get_body_lookup(bodies or load_solar_system_bodies())
    body = lookup[body_name]
    return density_for_body(body) * volume_from_diameter_km(diameter_km)


def _body_record(body, sun_mass_kg):
    if body.name == 'Sun' or body.mean_distance_from_sun_km <= 0:
        x_au = 0.0
        y_au = 0.0
        vx_km_s = 0.0
        vy_km_s = 0.0
    else:
        phase_radians = radians(body.default_phase_degrees)
        orbit_radius_km = body.mean_distance_from_sun_km
        x_au = orbit_radius_km * cos(phase_radians) / AU_IN_KM
        y_au = orbit_radius_km * sin(phase_radians) / AU_IN_KM
        orbital_speed_km_s = sqrt(G_KM * sun_mass_kg / orbit_radius_km)
        vx_km_s = -orbital_speed_km_s * sin(phase_radians)
        vy_km_s = orbital_speed_km_s * cos(phase_radians)

    return {
        'name': body.name,
        'body_type': body.body_type,
        'color': body.color,
        'diameter_km': float(body.diameter_km),
        'mass_kg': float(body.mass_kg),
        'x_au': float(x_au),
        'y_au': float(y_au),
        'vx_km_s': float(vx_km_s),
        'vy_km_s': float(vy_km_s),
        'trail': [[float(x_au), float(y_au)]],
    }


def build_default_sandbox_state(
    bodies=None,
    *,
    timestep_seconds=DEFAULT_TIMESTEP_SECONDS,
    trail_length=DEFAULT_TRAIL_LENGTH,
    status=DEFAULT_STATUS,
):
    """Return the initial gravity sandbox state."""
    bodies = bodies or load_solar_system_bodies()
    sun_mass_kg = get_body_lookup(bodies)['Sun'].mass_kg
    return {
        'bodies': [_body_record(body, sun_mass_kg) for body in bodies],
        'running': False,
        'timestep_seconds': float(timestep_seconds),
        'trail_length': int(trail_length),
        'tick_count': 0,
        'status': status,
    }


def get_state_body_lookup(state):
    """Return a name-indexed lookup for sandbox state bodies."""
    return {
        body['name']: body
        for body in (state or {}).get('bodies', [])
    }


def compute_accelerations(bodies):
    """Compute gravitational accelerations for each body in km/s²."""
    accelerations = [{'ax_km_s2': 0.0, 'ay_km_s2': 0.0} for _ in bodies]

    for left_index, left_body in enumerate(bodies):
        left_x_km = left_body['x_au'] * AU_IN_KM
        left_y_km = left_body['y_au'] * AU_IN_KM
        for right_index in range(left_index + 1, len(bodies)):
            right_body = bodies[right_index]
            dx_km = right_body['x_au'] * AU_IN_KM - left_x_km
            dy_km = right_body['y_au'] * AU_IN_KM - left_y_km
            distance_km = hypot(dx_km, dy_km)
            if distance_km <= 0:
                continue
            scale = G_KM / (distance_km ** 3)
            accelerations[left_index]['ax_km_s2'] += scale * right_body['mass_kg'] * dx_km
            accelerations[left_index]['ay_km_s2'] += scale * right_body['mass_kg'] * dy_km
            accelerations[right_index]['ax_km_s2'] -= scale * left_body['mass_kg'] * dx_km
            accelerations[right_index]['ay_km_s2'] -= scale * left_body['mass_kg'] * dy_km

    return accelerations


def detect_collision_message(bodies):
    """Return a collision status message if any bodies overlap."""
    for left_index, left_body in enumerate(bodies):
        left_radius_km = left_body['diameter_km'] / 2
        for right_body in bodies[left_index + 1:]:
            dx_km = (right_body['x_au'] - left_body['x_au']) * AU_IN_KM
            dy_km = (right_body['y_au'] - left_body['y_au']) * AU_IN_KM
            distance_km = hypot(dx_km, dy_km)
            if distance_km <= left_radius_km + right_body['diameter_km'] / 2:
                return f'Collision detected between {left_body["name"]} and {right_body["name"]}. Simulation paused.'
    return None


def validate_state_message(bodies, *, max_distance_au=MAX_DISTANCE_AU):
    """Return a validation status message if the state becomes unstable."""
    for body in bodies:
        numeric_values = (
            body['diameter_km'],
            body['mass_kg'],
            body['x_au'],
            body['y_au'],
            body['vx_km_s'],
            body['vy_km_s'],
        )
        if any(not isfinite(float(value)) for value in numeric_values):
            return f'Invalid numeric state for {body["name"]}. Simulation paused.'
        if body['diameter_km'] <= 0 or body['mass_kg'] <= 0:
            return f'{body["name"]} must keep a positive size and mass.'
        if hypot(body['x_au'], body['y_au']) > max_distance_au:
            return f'{body["name"]} drifted beyond {max_distance_au:.0f} AU. Simulation paused.'
    return None


def _trim_trail(trail, trail_length):
    return trail[-int(trail_length):] if trail else []


def update_body_state(
    state,
    selected_name,
    *,
    diameter_km=None,
    x_au=None,
    y_au=None,
    vx_km_s=None,
    vy_km_s=None,
):
    """Return a new state with an edited body."""
    new_state = deepcopy(state)
    body = get_state_body_lookup(new_state)[selected_name]

    if diameter_km is not None:
        body['diameter_km'] = float(diameter_km)
        body['mass_kg'] = float(mass_for_resized_body(selected_name, diameter_km))
    if x_au is not None:
        body['x_au'] = float(x_au)
    if y_au is not None:
        body['y_au'] = float(y_au)
    if vx_km_s is not None:
        body['vx_km_s'] = float(vx_km_s)
    if vy_km_s is not None:
        body['vy_km_s'] = float(vy_km_s)

    body['trail'] = [[body['x_au'], body['y_au']]]
    new_state['status'] = f'{selected_name} updated. Press Play to continue.'
    return new_state


def update_sandbox_config(state, *, timestep_seconds=None, trail_length=None):
    """Return a new state with updated run configuration."""
    new_state = deepcopy(state)
    if timestep_seconds is not None:
        new_state['timestep_seconds'] = float(timestep_seconds)
    if trail_length is not None:
        new_state['trail_length'] = int(trail_length)
        for body in new_state['bodies']:
            body['trail'] = _trim_trail(body.get('trail', []), new_state['trail_length'])
    new_state['status'] = 'Sandbox controls updated.'
    return new_state


def set_running_state(state, running, *, status=None):
    """Return a new state with updated run state."""
    new_state = deepcopy(state)
    new_state['running'] = bool(running)
    if status is not None:
        new_state['status'] = status
    return new_state


def reset_sandbox_state():
    """Return the canonical reset state."""
    return build_default_sandbox_state(status='Sandbox reset to default orbital assumptions.')


def step_sandbox_state(state, *, max_distance_au=MAX_DISTANCE_AU):
    """Advance the simulation by one timestep with a velocity-Verlet update."""
    new_state = deepcopy(state)
    bodies = new_state['bodies']
    pre_step_collision = detect_collision_message(bodies)
    if pre_step_collision:
        new_state['running'] = False
        new_state['status'] = pre_step_collision
        return new_state

    timestep_seconds = float(new_state['timestep_seconds'])
    initial_accelerations = compute_accelerations(bodies)

    staged_bodies = deepcopy(bodies)
    for body, acceleration in zip(staged_bodies, initial_accelerations):
        current_x_km = body['x_au'] * AU_IN_KM
        current_y_km = body['y_au'] * AU_IN_KM
        next_x_km = current_x_km + body['vx_km_s'] * timestep_seconds + 0.5 * acceleration['ax_km_s2'] * timestep_seconds ** 2
        next_y_km = current_y_km + body['vy_km_s'] * timestep_seconds + 0.5 * acceleration['ay_km_s2'] * timestep_seconds ** 2
        body['x_au'] = next_x_km / AU_IN_KM
        body['y_au'] = next_y_km / AU_IN_KM

    next_accelerations = compute_accelerations(staged_bodies)
    for body, staged_body, initial_acceleration, next_acceleration in zip(
        bodies,
        staged_bodies,
        initial_accelerations,
        next_accelerations,
    ):
        body['x_au'] = staged_body['x_au']
        body['y_au'] = staged_body['y_au']
        body['vx_km_s'] = body['vx_km_s'] + 0.5 * (initial_acceleration['ax_km_s2'] + next_acceleration['ax_km_s2']) * timestep_seconds
        body['vy_km_s'] = body['vy_km_s'] + 0.5 * (initial_acceleration['ay_km_s2'] + next_acceleration['ay_km_s2']) * timestep_seconds
        trail = body.get('trail', [])
        trail.append([body['x_au'], body['y_au']])
        body['trail'] = _trim_trail(trail, new_state['trail_length'])

    new_state['tick_count'] = int(new_state['tick_count']) + 1
    status_message = detect_collision_message(bodies) or validate_state_message(bodies, max_distance_au=max_distance_au)
    if status_message:
        new_state['running'] = False
        new_state['status'] = status_message
        return new_state

    timestep_hours = timestep_seconds / 3600
    new_state['status'] = (
        f'Running simulation · step {new_state["tick_count"]} '
        f'with a {timestep_hours:,.1f}-hour timestep.'
    )
    return new_state
