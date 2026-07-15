"""Integration tests for the Cabeza de Vaca dashboard route."""

from dash import Dash, page_registry

from backend.app import create_app


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


def _collect_text(component):
    if component is None:
        return []
    if isinstance(component, str):
        return [component]
    children = getattr(component, 'children', None)
    if isinstance(children, (list, tuple)):
        collected = []
        for child in children:
            collected.extend(_collect_text(child))
        return collected
    if children is not None:
        return _collect_text(children)
    return []


def _page_module():
    Dash(__name__, use_pages=True, pages_folder='')
    from backend.dashboards.cabeza_de_vaca import page as cabeza_page

    return cabeza_page


def test_cabeza_de_vaca_dashboard_is_registered_and_served():
    app = create_app(enable_dash=True)
    client = app.test_client()

    response = client.get('/data-storytelling-app/cabeza-de-vaca-journey')

    assert response.status_code == 200

    story_pages = [
        page
        for page in page_registry.values()
        if page.get('path') == '/cabeza-de-vaca-journey'
    ]
    assert story_pages
    assert story_pages[0]['title'] == 'Cabeza de Vaca Journey'
    assert callable(story_pages[0]['layout'])


def test_dashboard_is_listed_on_the_storytelling_index():
    create_app(enable_dash=True)
    from backend.dashboards import list as dashboard_list

    layout = dashboard_list.layout()
    rendered_text = ' '.join(_collect_text(layout))

    assert 'Cabeza de Vaca Journey' in rendered_text


def test_layout_contains_route_story_components():
    app = create_app(enable_dash=True)
    assert app is not None

    cabeza_page = _page_module()
    layout = cabeza_page.layout()
    component_ids = _collect_component_ids(layout)

    assert 'cabeza-route-map' in component_ids
    assert 'cabeza-stop-slider' in component_ids
    assert 'cabeza-reveal-mode' in component_ids
    assert 'cabeza-phase-jump' in component_ids
    assert 'cabeza-timeline' in component_ids
    assert 'cabeza-detail-panel' in component_ids
