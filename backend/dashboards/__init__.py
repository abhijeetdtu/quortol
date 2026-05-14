"""Dash Pages registration for Data Storytelling dashboards."""

import importlib
from pathlib import Path

from dash import html, page_container

__all__ = ['register_dashboards']


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
