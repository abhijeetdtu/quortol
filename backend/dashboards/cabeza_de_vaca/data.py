"""Dataset for the Cabeza de Vaca journey dashboard."""

from __future__ import annotations

from functools import lru_cache

from ..maps import MapWaypoint, validate_waypoints

PHASE_ORDER = (
    'shipwreck',
    'gulf-coast-survival',
    'interior-crossing',
    'new-spain-arrival',
)

PHASE_LABELS = {
    'shipwreck': 'Shipwreck',
    'gulf-coast-survival': 'Gulf Coast Survival',
    'interior-crossing': 'Interior Crossing',
    'new-spain-arrival': 'New Spain Arrival',
}


@lru_cache(maxsize=1)
def load_waypoints() -> tuple[MapWaypoint, ...]:
    """Return an ordered approximate reconstruction of the journey."""
    ordered = validate_waypoints(
        [
            MapWaypoint(
                id='florida-landing',
                sequence=1,
                title='Florida Landing',
                latitude=27.95,
                longitude=-82.46,
                phase='shipwreck',
                date_label='April 1528',
                summary='The Narváez expedition makes landfall on Florida’s Gulf Coast.',
                confidence='approximate',
                notes='The exact landing point is debated; Tampa Bay is a common teaching proxy.',
                days_since_shipwreck=0,
            ),
            MapWaypoint(
                id='apalachee-country',
                sequence=2,
                title='Apalachee Country',
                latitude=30.44,
                longitude=-84.28,
                phase='shipwreck',
                date_label='Summer 1528',
                summary='The overland march reaches Apalachee settlements and begins to unravel.',
                confidence='approximate',
                notes='The inland route is reconstructed from narrative clues rather than surveyed coordinates.',
                days_since_shipwreck=90,
            ),
            MapWaypoint(
                id='aute-coast',
                sequence=3,
                title='Aute on the Gulf',
                latitude=29.73,
                longitude=-84.98,
                phase='shipwreck',
                date_label='Autumn 1528',
                summary='The survivors return to the coast and build barges in a final escape attempt.',
                confidence='debated',
                notes='Aute’s precise location remains disputed in the historical literature.',
                days_since_shipwreck=180,
            ),
            MapWaypoint(
                id='malhado-island',
                sequence=4,
                title='Malhado / Galveston Island',
                latitude=29.30,
                longitude=-94.79,
                phase='gulf-coast-survival',
                date_label='Late 1528',
                summary='Cabeza de Vaca is cast ashore and begins years of captivity and adaptation.',
                confidence='approximate',
                notes='Galveston Island is the standard modern reference, though the identification is not absolute.',
                days_since_shipwreck=240,
            ),
            MapWaypoint(
                id='texas-mainland',
                sequence=5,
                title='Texas Mainland Communities',
                latitude=28.80,
                longitude=-96.80,
                phase='gulf-coast-survival',
                date_label='1529–1532',
                summary='He moves among coastal and inland communities, learning languages and exchange networks.',
                confidence='debated',
                notes='These movements summarize multiple years and communities rather than one pinpoint stop.',
                days_since_shipwreck=900,
            ),
            MapWaypoint(
                id='lower-rio-grande',
                sequence=6,
                title='Lower Rio Grande Corridor',
                latitude=26.10,
                longitude=-98.26,
                phase='gulf-coast-survival',
                date_label='1533',
                summary='The surviving companions begin regrouping and turn westward.',
                confidence='approximate',
                notes='This waypoint marks a regional corridor rather than a documented camp with fixed coordinates.',
                days_since_shipwreck=1735,
            ),
            MapWaypoint(
                id='rio-conchos-route',
                sequence=7,
                title='Río Conchos Route',
                latitude=28.63,
                longitude=-106.08,
                phase='interior-crossing',
                date_label='1534–1535',
                summary='The westward crossing moves through arid interior trade paths toward northwestern Mexico.',
                confidence='debated',
                notes='Scholars differ sharply on the exact inland arc taken across northern Mexico.',
                days_since_shipwreck=2370,
            ),
            MapWaypoint(
                id='sonora-frontier',
                sequence=8,
                title='Sonora Frontier',
                latitude=30.70,
                longitude=-110.95,
                phase='interior-crossing',
                date_label='Early 1536',
                summary='The travellers encounter communities already touched by Spanish slaving raids.',
                confidence='approximate',
                notes='This stop represents a frontier zone rather than a single unanimously agreed settlement.',
                days_since_shipwreck=2860,
            ),
            MapWaypoint(
                id='culiacan',
                sequence=9,
                title='Culiacán',
                latitude=24.80,
                longitude=-107.39,
                phase='new-spain-arrival',
                date_label='Spring 1536',
                summary='Cabeza de Vaca reaches a Spanish settlement and re-enters colonial society.',
                confidence='high',
                notes='Culiacán is securely placed in the surviving record.',
                days_since_shipwreck=2940,
            ),
            MapWaypoint(
                id='mexico-city',
                sequence=10,
                title='Mexico City',
                latitude=19.43,
                longitude=-99.13,
                phase='new-spain-arrival',
                date_label='Summer 1536',
                summary='The journey ends in the capital, where the survivors report what they saw.',
                confidence='high',
                notes='This closes the dashboard narrative at the administrative center of New Spain.',
                days_since_shipwreck=3030,
            ),
        ]
    )
    return tuple(ordered)
