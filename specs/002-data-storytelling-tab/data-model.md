# Data Model: Data Storytelling Tab

**Created**: May 13 2026  
**Feature**: 002-data-storytelling-tab  
**Based on**: [spec.md](./spec.md)

## Entities

### Dashboard

A collection of related visualizations that tell a cohesive data story.

**Fields**:
- `name` (string, required) - Unique identifier for the dashboard
- `title` (string, required) - Human-readable display name
- `description` (string, optional) - Brief description of the dashboard
- `page_path` (string, required) - URL path for the dashboard (e.g., `/dashboard/strikes`)
- `nav_order` (integer, optional) - Order for navigation menu (defaults to alphabetical)
- `is_visible` (boolean, optional) - Whether dashboard is visible to users (default: true)
- `created_at` (datetime, optional) - When dashboard was created
- `updated_at` (datetime, optional) - When dashboard was last updated

**Constraints**:
- `name` must be unique across all dashboards
- `page_path` must be a valid URL path
- `is_visible` defaults to true for newly created dashboards

---

### Visualization

An interactive chart or graph within a dashboard.

**Fields**:
- `id` (string, required) - Unique identifier for the visualization
- `title` (string, required) - Chart title
- `chart_type` (string, required) - Type of chart (line, bar, scatter, etc.)
- `data_source` (string, required) - Reference to data source file or function
- `x_axis` (string, optional) - X-axis label
- `y_axis` (string, optional) - Y-axis label
- `filters` (array, optional) - List of filter configurations
- `comparison_mode` (boolean, optional) - Whether this chart supports comparison view
- `layout_config` (object, optional) - Plotly layout configuration

**Constraints**:
- `chart_type` must be a valid Plotly chart type
- `data_source` must reference a valid data source
- `filters` array must contain valid filter configurations

---

### Data Source

A structured dataset that feeds into visualizations.

**Fields**:
- `name` (string, required) - Unique identifier for the data source
- `description` (string, optional) - Description of the data source
- `file_path` (string, optional) - Path to JSON file (if static data)
- `function_path` (string, optional) - Path to Python function (if dynamic data)
- `data_type` (string, required) - Type of data (time_series, categorical, numeric, etc.)
- `refresh_interval` (integer, optional) - Cache refresh interval in seconds
- `cache_enabled` (boolean, optional) - Whether to cache this data source

**Constraints**:
- Either `file_path` or `function_path` must be provided
- `data_type` must match the expected data format
- `refresh_interval` must be a positive integer if provided

---

### Filter

A user-selectable constraint that modifies what data is displayed.

**Fields**:
- `id` (string, required) - Unique identifier for the filter
- `label` (string, required) - User-facing label for the filter
- `filter_type` (string, required) - Type of filter (date_range, category, metric, etc.)
- `options` (array, optional) - Available options for dropdown/select filters
- `default_value` (any, optional) - Default value when filter is applied
- `multiple_select` (boolean, optional) - Whether multiple values can be selected

**Constraints**:
- `filter_type` must be a valid filter type
- `options` must be provided for categorical filters
- `default_value` must be a valid option if provided

---

## Relationships

### Dashboard → Visualizations

A dashboard can contain multiple visualizations.

**Cardinality**: One-to-Many  
**Implementation**: Dashboard entity contains array of visualization IDs

```json
{
  "Dashboard": {
    "visualizations": ["viz_001", "viz_002", "viz_003"]
  }
}
```

### Dashboard → Data Sources

A dashboard uses multiple data sources.

**Cardinality**: Many-to-Many (via Visualizations)  
**Implementation**: Visualizations reference data sources

```json
{
  "Visualization": {
    "data_source": "ds_001"
  }
}
```

### Visualization → Filters

A visualization can have multiple filters.

**Cardinality**: One-to-Many  
**Implementation**: Visualization entity contains array of filter configurations

```json
{
  "Visualization": {
    "filters": ["filter_001", "filter_002"]
  }
}
```

## State Transitions

### Dashboard

| State | Trigger | Next State |
|-------|---------|------------|
| Draft | Developer deploys | Active |
| Active | Developer updates | Active |
| Active | Developer deletes | Deleted |
| Active | Developer hides | Inactive |

### Data Source

| State | Trigger | Next State |
|-------|---------|------------|
| Valid | Data changed | Valid |
| Valid | Data file missing | Invalid |
| Invalid | Data file restored | Valid |

## Validation Rules

### Dashboard
- `name` must be alphanumeric with hyphens (regex: `^[a-z0-9-]+$`)
- `page_path` must start with `/` and not contain `//`
- `nav_order` must be positive integer if provided

### Visualization
- `chart_type` must be one of: line, bar, scatter, pie, area, bubble, etc. (Plotly supported types)
- `data_source` must reference an existing data source
- `filters` must be valid filter configurations

### Data Source
- `file_path` must exist if provided (file validation on deployment)
- `function_path` must reference existing Python function (import validation)
- `refresh_interval` must be positive integer if provided

### Filter
- `filter_type` must be one of: date_range, category, numeric, boolean
- `options` must be provided for category filter type
- `default_value` must be in `options` array if provided

## Code Structure

### Dashboard File Structure

Each dashboard is defined in a Python file:

```python
# backend/dashboards/{name}/page.py

from dash import dcc, html
import plotly.express as px

def create_dashboard_page():
    return html.Div([
        # Page navigation
        dcc.Location(id='url', refresh='none'),
        
        # Navigation menu
        html.Div([
            dcc.Link('Back to Dashboard List', href='/'),
            dcc.Link('Dashboard Name', href='/dashboard/{name}'),
        ]),
        
        # Dashboard content
        html.Div([
            html.H1('Dashboard Title'),
            html.P('Dashboard description'),
            
            # Filters
            html.Div(id='filters-container'),
            
            # Visualizations
            html.Div(id='visualization-container'),
        ])
    ])
```

### Data Source File

```python
# backend/dashboards/{name}/data.py

import json

def load_data_source():
    """Load data from JSON file."""
    with open('data/{name}.json') as f:
        return json.load(f)

def get_filtered_data(data, filters):
    """Filter data based on user selections."""
    # Implement filtering logic
    return filtered_data
```

### Dashboard Configuration

```python
# backend/dashboards/{name}/config.py

DASHBOARD_CONFIG = {
    'name': 'dashboard_name',
    'title': 'Dashboard Title',
    'description': 'Dashboard description',
    'page_path': '/dashboard/name',
    'nav_order': 1,
    'is_visible': True,
    'visualizations': [
        {
            'id': 'viz_001',
            'title': 'Chart Title',
            'chart_type': 'line',
            'data_source': 'load_data_source',
            'x_axis': 'Time',
            'y_axis': 'Value',
            'filters': ['date_range'],
        }
    ]
}
```
