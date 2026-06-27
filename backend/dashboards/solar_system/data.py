"""Curated solar system reference data and comparison helpers."""

from dataclasses import dataclass
from functools import lru_cache
import math

AU_IN_KM = 149_597_870.7
LIGHT_SPEED_KM_PER_SECOND = 299_792.458
MINUTES_PER_DAY = 1_440


@dataclass(frozen=True)
class SolarSystemBody:
    """Normalized record for a solar system body."""

    name: str
    order: int
    body_type: str
    diameter_km: float
    mass_kg: float
    mean_distance_from_sun_km: float
    distance_au: float
    light_time_minutes: float
    orbital_period_days: float
    default_phase_degrees: float
    color: str
    short_fact: str


_RAW_BODIES = (
    {
        'name': 'Sun',
        'order': 0,
        'body_type': 'star',
        'diameter_km': 1_392_700,
        'mass_kg': 1.9885e30,
        'mean_distance_from_sun_km': 0,
        'orbital_period_days': 0,
        'default_phase_degrees': 0,
        'color': '#F4D58D',
        'short_fact': 'The Sun contains more than 99.8% of the Solar System’s mass.',
    },
    {
        'name': 'Mercury',
        'order': 1,
        'body_type': 'planet',
        'diameter_km': 4_879,
        'mass_kg': 3.3011e23,
        'mean_distance_from_sun_km': 57_909_227,
        'orbital_period_days': 87.97,
        'default_phase_degrees': 18,
        'color': '#9A8C98',
        'short_fact': 'Mercury races around the Sun in under 88 Earth days.',
    },
    {
        'name': 'Venus',
        'order': 2,
        'body_type': 'planet',
        'diameter_km': 12_104,
        'mass_kg': 4.8675e24,
        'mean_distance_from_sun_km': 108_209_475,
        'orbital_period_days': 224.70,
        'default_phase_degrees': 74,
        'color': '#D4A373',
        'short_fact': 'Venus is almost Earth-sized, but its surface is hotter than Mercury’s.',
    },
    {
        'name': 'Earth',
        'order': 3,
        'body_type': 'planet',
        'diameter_km': 12_742,
        'mass_kg': 5.97237e24,
        'mean_distance_from_sun_km': 149_598_262,
        'orbital_period_days': 365.26,
        'default_phase_degrees': 134,
        'color': '#3A86FF',
        'short_fact': 'Earth defines the baseline: 1 AU and about 8.3 light-minutes from the Sun.',
    },
    {
        'name': 'Mars',
        'order': 4,
        'body_type': 'planet',
        'diameter_km': 6_779,
        'mass_kg': 6.4171e23,
        'mean_distance_from_sun_km': 227_943_824,
        'orbital_period_days': 686.98,
        'default_phase_degrees': 194,
        'color': '#C1121F',
        'short_fact': 'Mars looks close on posters, but it orbits about 1.5 times farther out than Earth.',
    },
    {
        'name': 'Jupiter',
        'order': 5,
        'body_type': 'planet',
        'diameter_km': 139_820,
        'mass_kg': 1.8982e27,
        'mean_distance_from_sun_km': 778_340_821,
        'orbital_period_days': 4_332.59,
        'default_phase_degrees': 252,
        'color': '#BC6C25',
        'short_fact': 'Jupiter is so large that more than 1,300 Earths could fit inside it by volume.',
    },
    {
        'name': 'Saturn',
        'order': 6,
        'body_type': 'planet',
        'diameter_km': 116_460,
        'mass_kg': 5.6834e26,
        'mean_distance_from_sun_km': 1_426_666_422,
        'orbital_period_days': 10_759.22,
        'default_phase_degrees': 308,
        'color': '#C9B79C',
        'short_fact': 'Saturn’s rings spread wide, but the planet itself still sits almost 10 AU from the Sun.',
    },
    {
        'name': 'Uranus',
        'order': 7,
        'body_type': 'planet',
        'diameter_km': 50_724,
        'mass_kg': 8.6810e25,
        'mean_distance_from_sun_km': 2_870_658_186,
        'orbital_period_days': 30_688.5,
        'default_phase_degrees': 22,
        'color': '#8ECAE6',
        'short_fact': 'Uranus takes about 84 Earth years to finish one orbit.',
    },
    {
        'name': 'Neptune',
        'order': 8,
        'body_type': 'planet',
        'diameter_km': 49_244,
        'mass_kg': 1.02413e26,
        'mean_distance_from_sun_km': 4_498_396_441,
        'orbital_period_days': 60_182,
        'default_phase_degrees': 102,
        'color': '#1D4ED8',
        'short_fact': 'Neptune is nearly 30 AU from the Sun, where sunlight is faint and slow to arrive.',
    },
)


def _normalize_body(record):
    distance_km = float(record['mean_distance_from_sun_km'])
    distance_au = distance_km / AU_IN_KM if distance_km else 0.0
    light_time_minutes = distance_km / LIGHT_SPEED_KM_PER_SECOND / 60 if distance_km else 0.0
    return SolarSystemBody(
        name=record['name'],
        order=int(record['order']),
        body_type=record['body_type'],
        diameter_km=float(record['diameter_km']),
        mass_kg=float(record['mass_kg']),
        mean_distance_from_sun_km=distance_km,
        distance_au=distance_au,
        light_time_minutes=light_time_minutes,
        orbital_period_days=float(record['orbital_period_days']),
        default_phase_degrees=float(record['default_phase_degrees']),
        color=record['color'],
        short_fact=record['short_fact'],
    )


@lru_cache(maxsize=1)
def load_solar_system_bodies():
    """Return normalized solar system bodies sorted from the Sun outward."""
    return tuple(sorted(
        (_normalize_body(record) for record in _RAW_BODIES),
        key=lambda body: body.order,
    ))


def get_body_lookup(bodies=None):
    """Return a name-indexed lookup for the provided bodies."""
    bodies = bodies or load_solar_system_bodies()
    return {body.name: body for body in bodies}


def focus_body_names(focus_mode, bodies=None):
    """Return the bodies emphasized by the selected focus mode."""
    bodies = bodies or load_solar_system_bodies()
    if focus_mode == 'inner-planets':
        return ('Sun', 'Mercury', 'Venus', 'Earth', 'Mars')
    if focus_mode == 'outer-planets':
        return ('Sun', 'Jupiter', 'Saturn', 'Uranus', 'Neptune')
    return tuple(body.name for body in bodies)


def distance_unit_label(unit):
    """Return a human-readable distance unit label."""
    return {
        'km': 'km',
        'au': 'AU',
        'light-minutes': 'light-minutes',
    }.get(unit, 'AU')


def convert_distance(distance_km, unit):
    """Convert a distance in kilometers to the selected unit."""
    if unit == 'km':
        return float(distance_km)
    if unit == 'light-minutes':
        return float(distance_km) / LIGHT_SPEED_KM_PER_SECOND / 60
    return float(distance_km) / AU_IN_KM


def build_comparison_summary(selected_name, unit='au', bodies=None):
    """Build reusable comparison metrics for the selected body."""
    bodies = bodies or load_solar_system_bodies()
    lookup = get_body_lookup(bodies)
    selected = lookup[selected_name]
    earth = lookup['Earth']
    sun = lookup['Sun']
    selected_distance_value = convert_distance(selected.mean_distance_from_sun_km, unit)
    earth_distance_value = convert_distance(earth.mean_distance_from_sun_km, unit)
    selected_apparent_sun_angle_degrees = apparent_sun_angular_diameter_degrees(selected.name, bodies)
    earth_apparent_sun_angle_degrees = apparent_sun_angular_diameter_degrees('Earth', bodies)

    return {
        'selected_name': selected.name,
        'selected_body_type': selected.body_type,
        'selected_distance_value': selected_distance_value,
        'selected_distance_unit': distance_unit_label(unit),
        'selected_light_time_minutes': selected.light_time_minutes,
        'selected_orbital_period_days': selected.orbital_period_days,
        'selected_diameter_km': selected.diameter_km,
        'selected_fact': selected.short_fact,
        'diameter_ratio_vs_earth': selected.diameter_km / earth.diameter_km,
        'diameter_ratio_vs_sun': selected.diameter_km / sun.diameter_km,
        'distance_ratio_vs_earth': (
            selected_distance_value / earth_distance_value if earth_distance_value else 0.0
        ),
        'apparent_sun_angle_degrees': selected_apparent_sun_angle_degrees,
        'apparent_sun_angle_arcminutes': selected_apparent_sun_angle_degrees * 60,
        'apparent_sun_ratio_vs_earth': (
            selected_apparent_sun_angle_degrees / earth_apparent_sun_angle_degrees
            if earth_apparent_sun_angle_degrees
            else 0.0
        ),
        'earth_distance_value': earth_distance_value,
        'earth_distance_unit': distance_unit_label(unit),
    }


def apparent_sun_angular_diameter_degrees(body_name, bodies=None):
    """Return the Sun's apparent angular diameter from a body's orbit in degrees."""
    bodies = bodies or load_solar_system_bodies()
    lookup = get_body_lookup(bodies)
    selected = lookup[body_name]
    sun = lookup['Sun']

    if selected.name == 'Sun' or selected.mean_distance_from_sun_km <= 0:
        return 180.0

    half_angle_radians = math.atan((sun.diameter_km / 2) / selected.mean_distance_from_sun_km)
    return math.degrees(half_angle_radians * 2)
