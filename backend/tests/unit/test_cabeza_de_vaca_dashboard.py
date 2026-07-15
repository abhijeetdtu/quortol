"""Unit tests for the Cabeza de Vaca dashboard helpers and dataset."""

from functools import lru_cache

from dash import Dash, no_update

from backend.dashboards.cabeza_de_vaca.data import PHASE_ORDER, load_waypoints


@lru_cache(maxsize=1)
def _page_module():
    Dash(__name__, use_pages=True, pages_folder='')
    from backend.dashboards.cabeza_de_vaca import page as cabeza_page

    return cabeza_page


def _extract_text(component):
    if component is None:
        return []
    if isinstance(component, str):
        return [component]
    children = getattr(component, 'children', None)
    if isinstance(children, (list, tuple)):
        collected = []
        for child in children:
            collected.extend(_extract_text(child))
        return collected
    if children is not None:
        return _extract_text(children)
    return []


def test_dataset_has_valid_bounds_and_required_text():
    waypoints = load_waypoints()

    assert waypoints
    assert all(-90 <= waypoint.latitude <= 90 for waypoint in waypoints)
    assert all(-180 <= waypoint.longitude <= 180 for waypoint in waypoints)
    assert all(waypoint.title.strip() for waypoint in waypoints)
    assert all(waypoint.summary.strip() for waypoint in waypoints)


def test_dataset_sequences_and_phases_are_monotonic():
    waypoints = load_waypoints()

    assert [waypoint.sequence for waypoint in waypoints] == list(range(1, len(waypoints) + 1))
    assert set(waypoint.phase for waypoint in waypoints).issubset(set(PHASE_ORDER))
    elapsed_days = [waypoint.days_since_shipwreck for waypoint in waypoints]
    assert elapsed_days == sorted(elapsed_days)
    assert elapsed_days[0] == 0


def test_render_story_updates_detail_and_progressive_trace_count():
    cabeza_page = _page_module()

    full_route_map, timeline_fig, full_detail = cabeza_page.render_story(4, 'full-route')
    progressive_map, _timeline_fig_progressive, progressive_detail = cabeza_page.render_story(4, 'progressive-reveal')

    full_text = ' '.join(_extract_text(full_detail))
    progressive_text = ' '.join(_extract_text(progressive_detail))

    assert len(full_route_map.data) > len(progressive_map.data)
    assert 'Malhado / Galveston Island' in full_text
    assert 'Approximate' in progressive_text
    assert timeline_fig.layout.xaxis.title.text == 'Days since shipwreck'
    assert list(timeline_fig.data[0].x)[:4] == [0, 90, 180, 240]


def test_phase_jump_returns_first_stop_for_phase():
    cabeza_page = _page_module()

    assert cabeza_page.jump_to_phase('interior-crossing') == 7
    assert cabeza_page.jump_to_phase(None) is no_update
