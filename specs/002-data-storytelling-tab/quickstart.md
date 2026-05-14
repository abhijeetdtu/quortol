# Quickstart: Data Storytelling Tab

**Created**: May 13 2026  
**Feature**: 002-data-storytelling-tab  
**For**: Developers

## Overview

This guide helps developers create their first dashboard page for the Data Storytelling feature.

## Prerequisites

- Python 3.8+ installed
- Dash library installed (`pip install dash plotly flask`)
- Basic understanding of Python and Flask
- Access to the project repository

## Create Your First Dashboard

### Step 1: Create Dashboard Directory

Create a new directory under `backend/dashboards/`:

```bash
# Create dashboard directory
mkdir -p backend/dashboards/strike_rate_trend

# Create dashboard files
touch backend/dashboards/strike_rate_trend/__init__.py
touch backend/dashboards/strike_rate_trend/page.py
touch backend/dashboards/strike_rate_trend/data.py
touch backend/dashboards/strike_rate_trend/config.py
```

### Step 2: Define Dashboard Configuration

Create `config.py`:

```python
# backend/dashboards/strike_rate_trend/config.py

DASHBOARD_CONFIG = {
    'name': 'strike_rate_trend',
    'title': 'Strike Rate Trend Analysis',
    'description': 'Analyze strike rate trends across different time periods',
    'page_path': '/dashboard/strike_rate_trend',
    'nav_order': 1,
    'is_visible': True,
    'created_at': '2026-01-01T00:00:00Z',
    'updated_at': '2026-01-01T00:00:00Z',
    'visualizations': [
        {
            'id': 'viz_001',
            'title': 'Strike Rate Over Time',
            'chart_type': 'line',
            'data_source': 'load_strike_rate_data',
            'x_axis': 'Date',
            'y_axis': 'Strike Rate',
            'filters': ['date_range'],
        }
    ],
    'filters': [
        {
            'id': 'date_range',
            'label': 'Date Range',
            'type': 'date_range',
            'options': [
                {'value': '2024', 'label': '2024'},
                {'value': '2025', 'label': '2025'},
            ],
            'default_value': '2024',
        }
    ]
}
```

### Step 3: Define Data Source

Create `data.py`:

```python
# backend/dashboards/strike_rate_trend/data.py

import json
import os
from datetime import datetime

def load_strike_rate_data():
    """Load strike rate data from JSON file."""
    file_path = os.path.join(
        os.path.dirname(__file__),
        'data',
        'strike_rate.json'
    )
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def get_filtered_data(data, filters):
    """Filter data based on date range."""
    date_range = filters.get('date_range', '2024')
    
    # Filter by year
    filtered = [
        point for point in data['points']
        if date_range in point['date']
    ]
    
    return {
        'timestamps': [p['date'] for p in filtered],
        'values': [p['strike_rate'] for p in filtered],
        'labels': [p['team'] for p in filtered]
    }
```

### Step 4: Create Dashboard Page

Create `page.py`:

```python
# backend/dashboards/strike_rate_trend/page.py

from dash import dcc, html, Callback
import plotly.express as px
import pandas as pd
from config import DASHBOARD_CONFIG

def create_dashboard_page():
    """Create the main dashboard layout."""
    
    # Create navigation
    navigation = html.Div([
        dcc.Link('Data Storytelling', href='/data-storytelling'),
        dcc.Link('Strike Rate Trend', href='/dashboard/strike_rate_trend'),
    ], className='breadcrumbs')
    
    # Create filter controls
    filter_controls = html.Div([
        dcc.Dropdown(
            id='date-filter',
            options=DASHBOARD_CONFIG['filters'][0]['options'],
            value=DASHBOARD_CONFIG['filters'][0]['default_value'],
            placeholder='Select date range'
        ),
    ], className='filter-container')
    
    # Create visualization container
    visualization_container = html.Div([
        dcc.Graph(
            id='strike-rate-chart',
            config={'responsive': True}
        ),
    ], className='visualization-container')
    
    # Create main layout
    layout = html.Div([
        navigation,
        html.Div([
            html.H1(DASHBOARD_CONFIG['title']),
            html.P(DASHBOARD_CONFIG['description']),
            
            filter_controls,
            visualization_container,
        ], className='dashboard-content')
    ])
    
    return layout

def create_callbacks():
    """Create Dash callbacks for interactivity."""
    
    @callback(
        Output('strike-rate-chart', 'figure'),
        Input('date-filter', 'value')
    )
    def update_chart(selected_year):
        # Load and filter data
        data = load_strike_rate_data()
        filtered = get_filtered_data(data, {'date_range': selected_year})
        
        # Create chart
        chart = px.line(
            x=filtered['timestamps'],
            y=filtered['values'],
            labels={'x': 'Date', 'y': 'Strike Rate'},
            title='Strike Rate Over Time'
        )
        
        return chart
    
    return update_chart
```

### Step 5: Create Dashboard Data File

Create `data/strike_rate.json`:

```json
{
  "points": [
    {"date": "2024-01-15", "strike_rate": 85.2, "team": "Team A"},
    {"date": "2024-02-15", "strike_rate": 88.5, "team": "Team A"},
    {"date": "2024-03-15", "strike_rate": 90.1, "team": "Team A"},
    {"date": "2024-04-15", "strike_rate": 87.3, "team": "Team A"},
    {"date": "2025-01-15", "strike_rate": 82.0, "team": "Team B"},
    {"date": "2025-02-15", "strike_rate": 85.5, "team": "Team B"}
  ]
}
```

### Step 6: Register Dash in Flask App

Integrate Dash into the existing Flask application at `backend/app.py`:

```python
# backend/app.py

from flask import Flask
from dash import Dash
from dashboards import register_dashboards  # New import

def create_app(config_class=None):
    # Existing Flask setup
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register existing routes
    from .routes.blog import blog_bp
    from .routes.portfolio import portfolio_bp
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    
    # Register Dash application within Flask
    dash_app = Dash(__name__, 
                    server=app,  # Use existing Flask server
                    url_prefix='/data-storytelling')
    
    # Register Dash dashboard pages
    register_dashboards(dash_app)
    
    return app
```

**Key Integration Points**:
- `server=app`: Dash uses existing Flask server (no separate port)
- `url_prefix='/data-storytelling'`: Dash routes at `/data-storytelling/*`
- All routes (Vue API, Dash pages) served from port 5000

### Step 7: Create Dashboard Registration

Create `backend/dashboards/__init__.py`:

```python
# backend/dashboards/__init__.py

from . import strike_rate_trend

def register_dashboards(dash_app):
    """Register all dashboards with Dash application."""
    
    # Register dashboard page
    dash_app.layout = create_dashboard_layout()
    
    # Register callbacks
    from . import strike_rate_trend.page
    strike_rate_trend.page.create_callbacks(dash_app)

def create_dashboard_layout():
    """Create main dashboard navigation layout."""
    from dash import dcc, html
    
    return html.Div([
        dcc.Location(id='url', refresh='none'),
        html.Div([
            dcc.Link('Home', href='/'),
            dcc.Link('Data Storytelling', href='/data-storytelling'),
        ]),
        html.Div(id='page-content')
    ])
```

**Key Integration Points**:
- Dash layout created once, shared across dashboards
- Navigation added to existing app structure
- Callbacks registered per dashboard

## Testing Your Dashboard

### Unit Tests

Create `tests/backend/test_strike_rate_trend.py`:

```python
import pytest
from dashboards.strike_rate_trend import data, config

def test_load_data():
    """Test data loading."""
    result = data.load_strike_rate_data()
    assert 'points' in result
    assert len(result['points']) > 0

def test_filter_data():
    """Test data filtering."""
    data = data.load_strike_rate_data()
    filtered = data.get_filtered_data(data, {'date_range': '2024'})
    
    assert len(filtered['timestamps']) > 0

def test_dashboard_config():
    """Test dashboard configuration."""
    assert config.DASHBOARD_CONFIG['name'] == 'strike_rate_trend'
    assert config.DASHBOARD_CONFIG['is_visible'] == True
```

### Integration Tests

Create `tests/backend/test_dashboard_page.py`:

```python
import pytest
from dash import Dash, dcc
from dashboards.strike_rate_trend import page

def test_dashboard_page_loads():
    """Test dashboard page renders correctly."""
    app = Dash(__name__)
    app.layout = page.create_dashboard_page()
    
    with app.test_client() as client:
        response = client.get('/dashboard/strike_rate_trend')
        assert response.status_code == 200

def test_interactive_filters():
    """Test filter interactivity."""
    app = Dash(__name__)
    app.layout = page.create_dashboard_page()
    page.create_callbacks()
    
    with app.test_client() as client:
        # Test filter change
        response = client.get('/dashboard/strike_rate_trend')
        assert response.status_code == 200
```

## Deploying Your Dashboard

### 1. Code Review

Ensure your dashboard code:
- Passes linting (`flake8`, `black`)
- Passes type checking (`mypy`)
- Includes all necessary tests
- Follows project conventions

### 2. Run Tests

```bash
# Run all tests
pytest tests/backend/

# Run specific dashboard tests
pytest tests/backend/test_strike_rate_trend.py -v
```

### 3. Deploy

```bash
# Commit dashboard code
git add backend/dashboards/strike_rate_trend/
git commit -m "Add Strike Rate Trend dashboard"
git push origin 002-data-storytelling-tab

# Deploy to production
# (Follow standard deployment process)
```

## Adding More Dashboards

To add additional dashboards, repeat the process:

1. Create new dashboard directory
2. Define configuration
3. Create data source
4. Create page
5. Register dashboard
6. Test
7. Deploy

For complex dashboards with multiple visualizations:

```python
# Add more visualizations to config.py

DASHBOARD_CONFIG['visualizations'] = [
    {
        'id': 'viz_001',
        'title': 'Chart 1',
        'chart_type': 'line',
        # ...
    },
    {
        'id': 'viz_002',
        'title': 'Chart 2',
        'chart_type': 'bar',
        # ...
    },
    # Add more as needed
]
```

## Common Patterns

### Comparison View

Enable comparison mode in visualization config:

```python
'comparison_mode': True
```

Users can select multiple metrics to compare side-by-side.

### Export Functionality

Add export buttons to visualizations:

```python
html.Div([
    dcc.Graph(id='chart'),
    html.Button('Download PNG', id='download-btn'),
])
```

## Troubleshooting

### Dashboard Not Showing

- Check `is_visible` is `True` in config
- Verify `page_path` matches registration
- Check dashboard is registered in `__init__.py`

### Data Not Loading

- Verify data file exists and is valid JSON
- Check data source function path
- Review server logs for errors

### Charts Not Rendering

- Check Plotly chart type is valid
- Verify data structure matches expected format
- Review browser console for JavaScript errors

## Next Steps

- Add more visualization types (scatter, pie, bubble)
- Implement complex filtering (multi-select, range sliders)
- Add caching for performance
- Implement export functionality
- Add accessibility features (ARIA labels, keyboard navigation)
