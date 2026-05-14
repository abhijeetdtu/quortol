# Quickstart: Creating Dashboards

**Created**: May 13 2026  
**Feature**: 002-data-storytelling-tab

## Overview

This guide helps developers create their first dashboard page for the Data Storytelling feature using Dash/Plotly.

## Prerequisites

- Python 3.8+ installed
- Dash and Plotly installed
- Basic understanding of Python and Flask
- Access to the project repository

## Step-by-Step Dashboard Creation

### 1. Create Dashboard Directory

```bash
# Create dashboard directory structure
mkdir -p backend/dashboards/my_dashboard/data
```

### 2. Create Configuration File

Create `backend/dashboards/my_dashboard/config.py`:

```python
DASHBOARD_CONFIG = {
    'name': 'my_dashboard',
    'title': 'My Dashboard',
    'description': 'Description of your dashboard',
    'page_path': '/data-storytelling/my_dashboard',
    'nav_order': 1,
    'is_visible': True,
    'visualizations': [
        {
            'id': 'viz_001',
            'title': 'Chart Title',
            'chart_type': 'line',
            'data_source': 'load_data',
            'x_axis': 'X Label',
            'y_axis': 'Y Label',
            'filters': ['year'],
            'comparison_mode': True
        }
    ],
    'filters': [
        {
            'id': 'year_filter',
            'label': 'Year',
            'type': 'category',
            'options': [
                {'value': '2024', 'label': '2024'},
                {'value': '2025', 'label': '2025'},
            ],
            'default_value': '2024'
        }
    ]
}
```

### 3. Create Data Source

Create `backend/dashboards/my_dashboard/data.py`:

```python
import json
import os

def load_data():
    """Load data from JSON file."""
    file_path = os.path.join(
        os.path.dirname(__file__),
        'data',
        'data.json'
    )
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def get_filtered_data(data, filters=None):
    """Filter data based on user selections."""
    if not filters:
        return {
            'timestamps': ['Jan', 'Feb', 'Mar'],
            'values': [100, 150, 120],
            'labels': ['Month 1', 'Month 2', 'Month 3']
        }
    
    # Apply filters here
    return data
```

### 4. Create Page Layout

Create `backend/dashboards/my_dashboard/page.py`:

```python
from dash import dcc, html, Callback
import plotly.express as px
import pandas as pd
from .config import DASHBOARD_CONFIG
from . import data as data_module

def create_dashboard_page():
    """Create the main dashboard layout."""
    
    breadcrumbs = html.Div([
        html.A('Home', href='/'),
        ' | ',
        html.A('Data Storytelling', href='/data-storytelling'),
        ' | ',
        html.A(DASHBOARD_CONFIG['title'], href=DASHBOARD_CONFIG['page_path']),
    ])
    
    filter_controls = html.Div([
        dcc.Dropdown(
            id='year-filter',
            options=[
                {'label': '2024', 'value': '2024'},
                {'label': '2025', 'value': '2025'},
            ],
            value='2024',
            multi=False
        ),
    ])
    
    chart_container = html.Div([
        dcc.Graph(id='chart'),
    ])
    
    layout = html.Div([
        breadcrumbs,
        html.Div([
            html.H2(DASHBOARD_CONFIG['title']),
            html.P(DASHBOARD_CONFIG['description']),
            filter_controls,
            chart_container,
        ])
    ])
    
    return layout

def create_callbacks(dash_app):
    """Create Dash callbacks."""
    
    @dash_app.callback(
        Output('chart', 'figure'),
        Input('year-filter', 'value')
    )
    def update_chart(year):
        data = data_module.load_data()
        filtered = data_module.get_filtered_data(data, {'year': year})
        
        df = pd.DataFrame({
            'Month': filtered['timestamps'],
            'Value': filtered['values']
        })
        
        fig = px.line(df, x='Month', y='Value', title=DASHBOARD_CONFIG['title'])
        return fig
    
    return update_chart

PAGE_NAME = 'my_dashboard'
PAGE_TITLE = DASHBOARD_CONFIG['title']
PAGE_PATH = DASHBOARD_CONFIG['page_path']
```

### 5. Create Data File

Create `backend/dashboards/my_dashboard/data/data.json`:

```json
{
  "points": [
    {"date": "2024-01-01", "value": 100},
    {"date": "2024-02-01", "value": 150},
    {"date": "2024-03-01", "value": 120},
    {"date": "2025-01-01", "value": 110},
    {"date": "2025-02-01", "value": 160}
  ]
}
```

### 6. Register Dashboard

The dashboard will automatically be discovered when you navigate to its page.

### 7. Deploy

No deployment needed - simply run the Flask app:

```bash
python -m backend.app
```

Visit `/data-storytelling/my_dashboard` to see your dashboard!

## Adding Comparison Views

To enable comparison mode, set `'comparison_mode': True` in your visualization config:

```python
'visualizations': [
    {
        'id': 'viz_001',
        'comparison_mode': True,  # Enable comparison
        ...
    }
]
```

Users can then select multiple metrics to compare side-by-side.

## Common Patterns

### Multi-Metric Charts

```python
def create_multi_line_chart(dash_app):
    @dash_app.callback(
        Output('multi-chart', 'figure'),
        Input('metric1', 'value'),
        Input('metric2', 'value')
    )
    def update_multi_chart(metric1, metric2):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x1, y=y1, name=metric1))
        fig.add_trace(go.Scatter(x=x2, y=y2, name=metric2))
        return fig
```

### Export Functionality

```python
from backend.dashboards.export import dashboard_exporter

def export_png():
    success, path = dashboard_exporter.export_chart(figure, 'PNG', 'chart.png')
```

## Next Steps

- Add more visualization types (bar, scatter, pie)
- Implement complex filtering (range sliders, multi-select)
- Add caching for performance
- Implement accessibility features (ARIA labels)
