# Data Model: IPL Visualization Bug Fix

## Overview
This document describes the entities and data model for the IPL visualization bug fix.

## Entities

### Plot
**Type:** `lets_plot.gggplot`

**Description:** The core plot object representing a lets-plot visualization that can be rendered, modified, and saved.

**Methods:**
- `to_png(path, width=14, height=9, dpi=300)` - Export plot to PNG file
- `to_svg(path)` - Export plot to SVG file
- `to_html(path)` - Export plot to HTML file
- `to_pdf(path)` - Export plot to PDF file

**Usage:**
```python
from lets_plot import ggplot

p = ggplot(df, aes(x='season', y='value'))
p = p + geom_line()
p.to_png('output.png', width=14, height=9, dpi=300)
```

### Visualization Function
**Type:** Python function

**Description:** A reusable function that creates a specific visualization chart with defined data inputs and styling.

**Common Parameters:**
- `df`: `pandas.DataFrame` - Input data for the visualization
- `output_path`: `Optional[str]` - Path to save the output file (optional)

**Return Type:** `lets_plot.gggplot` or tuple of `lets_plot.gggplot` objects

**Implementation Pattern:**
```python
def create_chart(data: pd.DataFrame, output_path: Optional[str] = None):
    p = (ggplot(data, aes(x='x_field', y='y_field'))
          + geom_line(color='#2c5f8c', size=2)
          + theme_minimal()
          + labs(title='Chart Title'))
    
    if output_path:
        p.to_png(output_path, width=14, height=9, dpi=300)
    
    return p
```

## Visualization Functions

### create_strike_rate_trend
**Input:** `df: pd.DataFrame` with `season`, `strike_rate` columns  
**Output:** `ggplot` plot object  
**File:** `strike_rate_trend.png`  
**Purpose:** Display batting strike rate trend from 2008-2024 with volatility band

### create_sixes_growth_chart
**Input:** `df: pd.DataFrame` with `season`, `sixes_per_match` columns  
**Output:** `ggplot` plot object  
**File:** `sixes_growth.png`  
**Purpose:** Show six-hitting evolution with three waves of acceleration

### create_phase_scoring_chart
**Input:** `phase_data: pd.DataFrame` with `season`, `runs_per_over`, `phase` columns  
**Output:** `ggplot` plot object  
**File:** `phase_scoring.png`  
**Purpose:** Faceted comparison of runs per over across different phases

### create_bowling_metrics_chart
**Input:** `bowling_data: pd.DataFrame` with `season`, `economy_rate`, `dot_ball_ratio` columns  
**Output:** `tuple` of `(p_econ, p_dot)` plot objects  
**Files:** `bowling_economy.png`, `bowling_dotball.png`  
**Purpose:** Display bowling economy rate and dot ball ratio trends

### create_venue_impact_chart
**Input:** `venue_data: pd.DataFrame` with `venue`, `sixes_per_match` columns  
**Output:** `ggplot` plot object  
**File:** `venue_impact.png`  
**Purpose:** Horizontal bar chart showing top 12 venues by six-hitting impact

### create_statistical_tests_chart
**Input:** `test_results: Dict` with statistical test results  
**Output:** `ggplot` plot object  
**File:** `statistical_tests.png`  
**Purpose:** Comparison chart of early vs late era metrics

### create_q_value_chart
**Input:** `test_results: Dict`, `corrected: bool`, `output_path: str`  
**Output:** `ggplot` plot object  
**File:** `q_values.png` or `raw_pvalues.png`  
**Purpose:** Display FDR-corrected q-values or raw p-values with significance threshold

### create_projection_chart
**Input:** `projections: Dict` with scenario projections  
**Output:** `ggplot` plot object  
**File:** `projections_2028.png`  
**Purpose:** Projected sixes per match for 2028 under different scenarios

## Data Flow

```
Input Data (CSV/JSON)
    ↓
Data Loader (src/data_loader.py)
    ↓
Visualization Function (src/visualization.py)
    ↓
Plot Object (ggplot)
    ↓
to_png() Export
    ↓
PNG File (figures/ directory)
```

## Bug Fix Context

**Issue:** The visualization script was using an incorrect save method  
**Root Cause:** Misunderstanding of lets-plot API  
**Solution:** Use `to_png()` method with proper dimensions and DPI settings  

**Key Fix:**
```python
# Correct usage (already in code):
p.to_png(output_path, width=14, height=9, dpi=300)
```

## Dependencies

- **lets_plot:** Version 4.3.0+ for `to_png()` support
- **pandas:** For DataFrame manipulation
- **numpy:** For numerical computations
- **pathlib:** For path handling
- **IPython.display:** Optional, for inline rendering in Jupyter
