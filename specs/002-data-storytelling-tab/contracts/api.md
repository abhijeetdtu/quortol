# Interface Contracts: Data Storytelling Tab

**Created**: May 13 2026  
**Feature**: 002-data-storytelling-tab  
**Based on**: [spec.md](./spec.md)

## Overview

This document defines the interface contracts for the Data Storytelling feature. Dash/Plotly handles all data serving and visualization rendering through its built-in callback system.

## Integration Contract

### Dash Application Registration

The Dash application is registered as a Flask blueprint within the existing Flask app.

**Registration Pattern**:

```python
# backend/dashboards/dashboard.py
from flask import Blueprint
from dash import Dash, dcc, html
from flask_dashes import DashFlask  # or register via Flask

# Register Dash routes within Flask app
dash_app = Dash(__name__, url_prefix='/data-storytelling')
```

**URL Structure**:
- Dashboard pages: `/data-storytelling/{dashboard_name}`
- Data callbacks: `/data-storytelling/{dashboard_name}/callback/{visualization_id}`
- All handled automatically by Dash

### Data Callback Contract

Dash callbacks automatically handle data requests. The contract is defined in Python callbacks.

**Callback Signature**:

```python
@dash_app.callback(
    Output('visualization_id', 'figure'),
    Input('filter_id', 'value')
)
def update_chart(selected_value):
    """
    Contract: 
    - Input: filter_id (string)
    - Output: Plotly figure object
    """
    # Load data from data source
    data = load_data_source()
    
    # Apply filters
    filtered = apply_filters(data, selected_value)
    
    # Return Plotly figure
    return px.line(filtered['x'], filtered['y'])
```

**Automatic Handling**:
- Dash converts callback inputs to HTTP requests
- Automatic JSON response for data
- Automatic client-side rendering
- No manual API endpoint definition needed

### Page Layout Contract

Dash pages are defined via `app.layout` in Python.

**Layout Definition**:

```python
dash_app.layout = html.Div([
    dcc.Location(id='url', refresh='none'),
    
    html.Div([
        dcc.Link('Home', href='/'),
        dcc.Link('Dashboard', href='/data-storytelling/dashboard-name'),
    ]),
    
    html.Div(id='page-content')
])
```

**Automatic Routing**:
- Dash handles URL routing via `dcc.Location`
- Page navigation is built-in
- No manual route definition needed

### Data Loading Contract

Data sources are loaded via Python functions within the dashboard.

**Data Source Pattern**:

```python
def load_strike_rate_data():
    """
    Contract: Returns dictionary with chart data
    """
    with open('data/strike_rate.json') as f:
        return json.load(f)
```

**Automatic Integration**:
- Dash callbacks call data source functions
- Data is automatically serialized to JSON
- No manual API endpoint needed

### Filter Contract

Filters are defined via Dash components.

**Filter Definition**:

```python
dcc.Dropdown(
    id='date-filter',
    options=[{'label': '2024', 'value': '2024'}],
    value='2024',
    placeholder='Select year'
)
```

**Callback Integration**:

```python
@callback(
    Output('chart', 'figure'),
    Input('date-filter', 'value')
)
def update_chart(year):
    # year is automatically passed as filter value
    return generate_chart(year)
```

## Implementation Notes

1. **Dash Handles Everything**: Dash/Plotly handles all data serving, routing, and rendering
2. **No Manual API**: Dash callbacks automatically create API endpoints
3. **Flask Integration**: Dash runs within existing Flask server (port 5000)
4. **Callbacks**: Define data flow in Python, Dash handles HTTP layer
5. **Components**: Plotly components handle client-side rendering

## Dash-Flask Integration Example

```python
# backend/app.py
from flask import Flask
from dash import Dash, dcc
from dashboards import register_dashboard

app = Flask(__name__)

# Register existing routes
app.register_blueprint(blog_bp, url_prefix='/api/blog')

# Register Dash application
dash_app = Dash(__name__, 
                server=app,  # Use existing Flask server
                url_prefix='/data-storytelling')

# Register dashboard pages
register_dashboard(dash_app)

# Existing routes continue to work alongside Dash
```

**Result**: Single Flask server serving both Vue API and Dash pages at port 5000.
