# Data Model: IPL Dashboard Enhancements

**Feature**: `003-ipl-dashboard-enhancements`  
**Date**: 2026-05-13  
**Status**: Complete

## Overview

This document defines the data entities and relationships for the IPL Dashboard Enhancements feature. The feature extends the existing IPL dashboard's data processing pipeline to support multi-select filtering, unified comparison, and cross-segment analysis. All entities operate on top of the existing CSV data sources (`IPL.csv`, `Match_Info.csv`).

## Entities

### Multi-Selection State

Represents the current selection state across all filter dimensions.

| Field | Type | Description |
|-------|------|-------------|
| `seasons` | `list[str]` or `None` | Selected seasons; `None` or `[]` means "All" |
| `teams` | `list[str]` or `None` | Selected teams; `None` or `[]` means "All" |
| `venue` | `str` or `None` | Selected venue (single-select, unchanged from v1) |
| `metric_segment` | `str` | Segment dimension: `"year"`, `"team"`, or `"phase"` |

**Validation rules**:
- `seasons` and `teams` are mutable (0, 1, or N selections)
- `venue` remains single-select (backward compatibility)
- `metric_segment` is single-select (unchanged)

**Relationships**:
- Used as input to `_filter_frames()` to produce per-entity data frames
- Updated reactively via Dash callback on filter dropdown changes

---

### Unified Comparison Component

A single reusable component that accepts multi-selection inputs and renders both overlaid visualizations and a summary metrics panel.

| Field | Type | Description |
|-------|------|-------------|
| `selected_entities` | `list[str]` | Entities to compare (teams, seasons, or team-season combinations) |
| `entity_type` | `str` | Dimension type: `"team"`, `"season"`, or `"team-season"` |
| `active_filters` | `dict` | Current filter context (seasons, teams, venue) |
| `max_series_cap` | `int` | Configurable limit on series count (default 10) |
| `low_conf_threshold` | `int` | Match count threshold for low-confidence flagging (default 3) |

**Lifecycle**:
1. User selects entities via multi-select dropdowns
2. Component receives selection state from Dash callback
3. Component validates against `max_series_cap`
4. Component renders overlaid charts + summary panel (or single-series view if 1 entity)

**Relationships**:
- Consumes `Multi-Selection State` as input
- Produces `Data Series` objects for chart rendering
- Produces `Comparison Summary Panel` data for tabular display

---

### Data Series

A single visual trace on a chart representing one entity within a multi-selection context.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Display name (e.g., "CSK", "2019", "CSK-2019") |
| `color` | `str` | HEX color code from extended `CHART_COLORWAY` |
| `metrics` | `dict` | Computed metrics (run_rate, strike_rate, economy, dot_ball_pct) |
| `low_confidence` | `bool` | True if computed from < `low_conf_threshold` matches |
| `match_count` | `int` | Number of matches contributing to this series |

**Validation rules**:
- `name` must be unique within a chart
- `color` must be from the extended colorway (up to `max_series_cap` colors)
- `low_confidence` is True when `match_count < low_conf_threshold`

**Relationships**:
- Each `Data Series` belongs to one `Unified Comparison Component` instance
- Each `Data Series` contributes to one `Comparison Summary Panel` row

---

### Segmented Metric

A metric value computed for a specific entity within a specific filter context.

| Field | Type | Description |
|-------|------|-------------|
| `entity` | `str` | Entity name (team, season, or phase) |
| `dimension` | `str` | Segment dimension: `"year"`, `"team"`, `"phase"` |
| `run_rate` | `float` | Runs per over |
| `strike_rate` | `float` | Runs per 100 balls |
| `economy` | `float` | Runs per over (bowling) |
| `dot_ball_pct` | `float` | Percentage of legal balls that are dots |
| `match_count` | `int` | Number of matches in filter context |
| `low_confidence` | `bool` | True if `match_count < low_conf_threshold` |

**Validation rules**:
- All numeric metrics are non-negative floats
- `low_confidence` is True when `match_count < low_conf_threshold` (default 3)

**Relationships**:
- Produced by `_build_metric_trend_frames()` when `multi=True`
- Consumed by `_build_metric_trend_chart()` for chart rendering
- Consumed by `Comparison Summary Panel` for tabular display

---

### Comparison Summary Panel

A tabular display produced by the unified comparison component showing key metrics per series.

| Field | Type | Description |
|-------|------|-------------|
| `series_name` | `str` | Entity name (e.g., "CSK") |
| `run_rate` | `float` | Run rate for this series |
| `strike_rate` | `float` | Strike rate for this series |
| `economy` | `float` | Economy for this series |
| `dot_ball_pct` | `float` | Dot ball % for this series |
| `match_count` | `int` | Number of matches |
| `low_confidence` | `bool` | True if flagged |

**Validation rules**:
- One row per `Data Series`
- Rows sorted by `run_rate` descending by default
- `low_confidence` rows marked with asterisk in display

**Relationships**:
- Produced by `Unified Comparison Component`
- Consumed by dashboard layout as `html.Table` or `dash_table.DataTable`

---

### Filter Validation Result

Server-side validation result for filter combinations.

| Field | Type | Description |
|-------|------|-------------|
| `valid` | `bool` | True if filter combination is compatible |
| `incompatible_entities` | `list[str]` | List of entities that don't exist in selected seasons |
| `error_message` | `str` | User-facing error message |
| `compatible_subset` | `dict` | Filter subset that is valid (for partial compatibility) |

**Validation rules**:
- `valid` is False when any team was not active in any selected season
- `incompatible_entities` lists each team that has zero matches in selected seasons
- `error_message` is human-readable (no technical jargon per Constitution III)

**Relationships**:
- Produced by `_validate_filter_combination()` in `page.py`
- Consumed by Dash callback to show/hide error message
- Used before rendering to prevent invalid data processing

## Relationships Diagram

```
Multi-Selection State
    │
    ├──► _filter_frames() ──► Per-entity DataFrames
    │                           │
    │                           ├──► _build_*_figure() ──► Data Series (per entity)
    │                           │                            │
    │                           │                            └──► Chart traces
    │                           │
    │                           └──► _build_metric_trend_frames() ──► Segmented Metrics
    │                                                                    │
    │                                                                    ├──► Trend charts
    │                                                                    └──► Comparison Summary Panel
    │
    └──► _validate_filter_combination() ──► Filter Validation Result
                                              │
                                              └──► Error display in dashboard
```

## Configuration Parameters

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| `MAX_SERIES_CAP` | 10 | `config.py` | Maximum simultaneous series across all charts |
| `LOW_CONF_THRESHOLD` | 3 | `config.py` | Minimum match count before metrics are considered statistically significant |

## Data Sources (Existing, Unchanged)

| Source | Path | Records | Key Fields |
|--------|------|---------|------------|
| Match metadata | `analysis/ipl/data/Match_Info.csv` | ~800 | `match_number`, `season`, `venue`, `team1`, `team2`, `winner` |
| Ball-by-ball | `analysis/ipl/data/IPL.csv` | ~100k+ | `ID`, `Innings`, `Overs`, `BatsmanRun`, `TotalRun`, `IsWicketDelivery`, `BattingTeam`, `Bowler` |

These sources are unchanged. The enhancement operates entirely within the existing data processing pipeline.
