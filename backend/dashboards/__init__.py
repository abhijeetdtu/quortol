"""Dash Pages registration for Data Storytelling dashboards."""

import importlib
from pathlib import Path

from dash import html, page_container

__all__ = ['register_dashboards', 'serialize_dashboard_registry']


def serialize_dashboard_registry(page_registry):
    """Return the public dashboard catalog from a Dash page registry."""
    dashboards = []
    for page in page_registry.values():
        path = str(page.get('path') or '').strip()
        if path in {'', '/'} or page.get('dashboard_visible', True) is False:
            continue

        slug = path.strip('/')
        if not slug:
            continue

        dashboards.append({
            'slug': slug,
            'title': page.get('dashboard_title') or page.get('name') or 'Dashboard',
            'description': (
                page.get('dashboard_description')
                or page.get('description')
                or ''
            ),
            'order': page.get('order', 999),
            'public_path': f'/data-storytelling/{slug}',
            'embed_path': f'/data-storytelling-app/{slug}',
        })

    dashboards.sort(key=lambda item: (item['order'], item['title']))
    return dashboards


def _iter_page_modules():
    """Yield all Dash Pages modules to import."""
    root = Path(__file__).resolve().parent

    # Home/index page
    yield f'{__name__}.list'

    # Dashboard pages
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        if (path / 'page.py').exists():
            yield f'{__name__}.{path.name}.page'


def register_dashboards(dash_app):
    """Register Dash Pages and set the app layout container."""
    for module_path in _iter_page_modules():
        importlib.import_module(module_path)

    dash_app.layout = html.Div([page_container])
