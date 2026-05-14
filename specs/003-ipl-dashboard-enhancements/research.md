# Research: IPL Dashboard Enhancements

**Feature**: `003-ipl-dashboard-enhancements`  
**Date**: 2026-05-13  
**Status**: Complete

## Research Findings

### 1. Multi-Select Dropdown Implementation

**Decision**: Use Dash `dcc.Dropdown` with `multi=True`.

**Rationale**: 
- Built-in Dash component — no new dependencies
- Supports search, toggle, and visual selection state
- Already used in the existing dashboard for single-select
- Returns a Python `list` when multiple items are selected, `None` when cleared
- Compatible with existing Dash callback architecture

**Implementation notes**:
- Current: `dcc.Dropdown(..., value='ALL', clearable=False)`
- New: `dcc.Dropdown(..., value=None, multi=True, clearable=True)`
- Empty selection (`None` or `[]`) maps to "All" behavior in filter logic
- The `_options_with_all()` helper function can remain unchanged for dropdown options

**Alternatives considered**:
- Custom checklist component — adds complexity, no Dash equivalent needed
- Tag-based input — not available in Dash core components
- Dual-list selector — high interaction cost, not standard for dashboard filters

### 2. Series Cap Configuration

**Decision**: Configurable `MAX_SERIES_CAP` in `config.py`, default 10.

**Rationale**:
- Prevents browser freeze with excessive series (15+ overlaid traces)
- Allows developers to adjust per deployment needs
- Documented in spec as FR-009
- Default of 10 provides meaningful comparison while maintaining readability

**Implementation notes**:
- Add `MAX_SERIES_CAP = 10` to `config.py`
- In `_filter_frames()` or figure builders, truncate series list to `MAX_SERIES_CAP`
- Show a warning banner when selections exceed the cap
- Extend `CHART_COLORWAY` in `theme.py` if more than 5 distinct colors needed

**Alternatives considered**:
- Hard-coded cap — inflexible, requires code change to adjust
- No cap — risk of browser performance degradation
- Per-chart cap — overly complex, same cap applies globally

### 3. Low-Confidence Metric Flagging

**Decision**: Flag metrics as low-confidence when computed from < 3 matches, using asterisk + tooltip.

**Rationale**:
- Statistical significance threshold of 3 matches prevents misleading comparisons
- Asterisk + tooltip pattern is clear and unobtrusive
- Metrics still displayed (unlike silent exclusion) so users can see the data
- Aligns with SC-006 acceptance criterion

**Implementation notes**:
- Add `LOW_CONF_THRESHOLD = 3` to `config.py`
- In metric computation functions, count matches per entity
- When count < threshold, add `'low_confidence': True` flag to metric dict
- In chart tooltips and summary panel, append `*` to value and show tooltip explaining threshold
- Document in Key Entities: "Segmented Metric" includes low-confidence flag

**Alternatives considered**:
- Silent exclusion — loses data, user unaware of filtering
- Higher threshold (5 matches) — too aggressive, loses more data
- No flagging — risks misleading comparisons

### 4. Server-Side Filter Validation

**Decision**: Server-side validation of incompatible filter combinations, returning error to user.

**Rationale**:
- Centralized validation ensures consistency across all dashboard views
- Error returned to user via inline message (not silent filtering)
- Aligns with FR-012 and SC-007 acceptance criteria
- Prevents confusing behavior where selections silently disappear

**Implementation notes**:
- Add validation function `_validate_filter_combination(seasons, teams, venue)` 
- Check that each selected team existed in each selected season (cross-reference `Match_Info.csv`)
- Return error dict with list of incompatible entities
- In callback, check validation result before rendering; show error message if invalid
- Use Dash `dcc.Store` or `html.Div` for inline error display

**Alternatives considered**:
- Client-side only — error-prone, requires duplicating validation logic
- Silent filtering — confusing, user unaware of constraint
- Modal dialog — too disruptive for a filter validation error

### 5. Empty Selection Behavior

**Decision**: Empty selection defaults to "All" (full dataset).

**Rationale**:
- Standard dashboard UX pattern
- Prevents empty/blank states
- Matches current "ALL" sentinel behavior in existing code
- Aligns with FR-013 and SC-008

**Implementation notes**:
- When `multi=True` dropdown returns `None` or `[]`, treat as "All"
- In `_filter_frames()`, check if selection is empty → skip that filter
- No special UI state needed — dashboard shows full dataset

### 6. Multi-Series Chart Rendering

**Decision**: Refactor existing `_build_*_figure()` functions to accept a list of data frames and render overlaid traces.

**Rationale**:
- Existing functions accept a single data frame; need to support multiple series
- Refactoring approach: each function accepts `data_frames: list[pd.DataFrame]` where each element represents one entity
- Each data frame gets a distinct trace with color from `CHART_COLORWAY` (extended if needed)
- Legend auto-generated by Plotly with series names (e.g., "CSK", "MI", "2019")
- Maintains backward compatibility: single-element list renders identically to current behavior

**Implementation notes**:
- `_filter_frames()` returns per-entity data frames when multi-select is active
- Each figure builder iterates over entities, computes metrics, adds trace
- Color assignment: cycle through `CHART_COLORWAY`, extend with additional distinct colors if > 5 series
- Legend positioning: top-right by default, adjustable

**Alternatives considered**:
- Separate comparison panel — rejected per spec (unified component approach)
- Tabbed comparison view — rejected per spec (single component)

## Dependencies & Best Practices

### Dash Multi-Select Best Practices
- Use `multi=True` with `clearable=True` for intuitive UX
- Handle `None` (cleared) and `[]` (empty selection) as "All"
- Use `getOptionLabel` equivalent via `options` list with `label`/`value` dicts
- Performance: Dash callbacks handle multi-value inputs natively, no special configuration needed

### Plotly Multi-Series Best Practices
- Each series = one `go.Scatter` or `go.Bar` trace
- Use `name` parameter for legend entries
- Use `colorway` or explicit `marker.color` / `line.color` for distinct colors
- For > 5 series, extend `CHART_COLORWAY` with additional distinct colors
- Use `legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)` for horizontal legend

### Pandas Multi-Entity Aggregation
- Group by entity column (e.g., `BattingTeam`) for per-entity metrics
- Use `groupby().agg()` for efficient computation
- Merge per-entity results for comparison panel
- Handle missing entities gracefully (fillna, dropna)

## Open Questions

None — all NEEDS CLARIFICATION items from Technical Context have been resolved.
