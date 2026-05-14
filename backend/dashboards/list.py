"""Dash Pages home/index for Data Storytelling."""

import dash
from dash import dcc, html


def _dashboard_pages():
    pages = []
    for page in dash.page_registry.values():
        if page.get('module') == __name__:
            continue
        if not page.get('path') or page.get('path') == '/':
            continue
        if page.get('dashboard_visible', True) is False:
            continue
        pages.append(page)
    pages.sort(key=lambda page: (page.get('order', 999), page.get('name', '')))
    return pages


def layout():
    """Render the Data Storytelling dashboard index."""
    cards = []
    for page in _dashboard_pages():
        title = page.get('dashboard_title') or page.get('name', 'Dashboard')
        description = (
            page.get('dashboard_description')
            or page.get('description')
            or 'No description available.'
        )
        href = page.get('relative_path') or dash.get_relative_path(page['path'])

        cards.append(html.Div([
            html.H3(title),
            html.P(description),
            dcc.Link(f'Open {title}', href=href)
        ], className='dashboard-card'))

    return html.Div([
        html.H1('Data Storytelling Dashboards'),
        html.P('Select a dashboard to explore visual data stories.'),
        html.Div(cards, className='dashboard-grid')
    ], style={'padding': '2rem'})


dash.register_page(
    __name__,
    path='/',
    name='Data Storytelling',
    title='Data Storytelling Dashboards',
    order=0,
    layout=layout
)
