# Implementation Plan: IPL Dashboard Enhancements

**Branch**: `003-ipl-dashboard-enhancements` | **Date**: 2026-05-13 | **Spec**: [spec.md](../specs/003-ipl-dashboard-enhancements/spec.md)
**Input**: Feature specification from `/specs/003-ipl-dashboard-enhancements/spec.md`

## Summary

Enhance the existing IPL Deep Dive dashboard (`backend/dashboards/ipl_deep/page.py`) to support multi-select filtering (teams, seasons), a unified comparison component that overlays multiple data series on all charts, and cross-segment team × phase analysis. The implementation extends the current single-select Dash callback architecture with multi-value inputs, server-side filter validation, configurable series capping, and low-confidence metric flagging. All changes maintain backward compatibility — single-select behavior remains unchanged.

## Technical Context

**Language/Version**: Python 3.11+ (project minimum 3.8+)  
**Primary Dependencies**: Dash 2.x (web app framework), Plotly 5.x (interactive charts), pandas (data processing), Flask (backend)  
**Storage**: Static CSV files — `analysis/ipl/data/IPL.csv` (ball-by-ball), `analysis/ipl/data/Match_Info.csv` (match metadata)  
**Testing**: pytest (backend logic), Dash testing utilities (callback integration)  
**Target Platform**: Desktop browser (Chrome, Firefox, Edge) — mobile out of scope for v1  
**Project Type**: Web application (Dash/Plotly dashboard within Flask backend)  
**Performance Goals**: Charts render within 2 seconds for up to 5 teams; unified comparison component updates within 1 second of filter change  
**Constraints**: Desktop-first, no mobile support; `MAX_SERIES_CAP` configurable in `config.py` (default 10); existing Dash callback architecture must be preserved  
**Scale/Scope**: ~17 IPL seasons (2008–2024), ~18 teams, ~50 venues, ~100k+ ball-by-ball records  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| **I. Code Quality** | ✅ Compliant | All new functions will have single responsibility; no dead code or debug artifacts |
| **II. Testing Standards** | ✅ Compliant | Tests will cover success paths (multi-select), error states (incompatible filters), and edge cases (sparse data, series cap) |
| **III. UX Consistency** | ✅ Compliant | Uses existing Dash components (`dcc.Dropdown` with `multi=True`); loading/empty/error states handled consistently with `_empty_figure()` pattern |
| **IV. Performance Requirements** | ✅ Compliant | `@lru_cache` already used for dataset loading; filter operations use pandas vectorized operations; series cap prevents rendering overload |
| **V. Simplicity & Maintainability** | ✅ Compliant | Reuses existing `_filter_frames()`, `_build_*_figure()` patterns; no new external dependencies; flat callback structure maintained |

**GATE STATUS**: PASS — No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-ipl-dashboard-enhancements/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Phase 1 output (server validation endpoint contract)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/dashboards/ipl_deep/
├── config.py            # ADD: MAX_SERIES_CAP, LOW_CONF_THRESHOLD
├── page.py              # MODIFY: multi-select dropdowns, filter logic, comparison component
└── __init__.py          # No changes

backend/dashboards/
└── theme.py             # READ ONLY: CHART_COLORWAY extended for multi-series (existing)
```

**Structure Decision**: Single-dashboard modification. No new files or directories required. All changes are contained within `backend/dashboards/ipl_deep/`. The existing `dcc.Dropdown` filters are modified to `multi=True`; the `_filter_frames()` function is extended to accept lists; figure builders are refactored to handle multi-series rendering.

### Implementation Notes

- `_filter_frames(match_df, deliveries, filters)` returns `Tuple[pd.DataFrame, List[pd.DataFrame]]` — `(all_matches_df, [deliveries_df_for_each_entity])`. Caller must unpack and validate: `matches, entity_deliveries = _filter_frames(...)`. If `len(entity_deliveries) == 0`, return `None` to signal empty result.
- `_validate_filter_combination()` returns a dict with keys: `valid` (bool), `error` (str or None), `compatible_teams` (list). Caller checks `valid` before rendering.
- `_get_series_colors()` uses round-robin assignment from `CHART_COLORWAY`; if entities exceed colorway length, appends distinct shades by lightening/darkening the base color.
- All figure builders that previously accepted a single dataframe now accept `List[pd.DataFrame]`; they iterate and add one trace per entity.

## Complexity Tracking

> No constitution violations — table omitted.

## Phase 0: Research

### Research Findings

**Decision**: Use Dash `dcc.Dropdown` with `multi=True` for multi-select filters.  
**Rationale**: Built-in Dash component, no new dependencies, consistent with project conventions, supports search and toggle.  
**Alternatives considered**: Custom checklist component, tag-based input, dual-list selector — all rejected as they add complexity and external dependencies.

**Decision**: Series cap configurable via `config.py` parameter `MAX_SERIES_CAP` (default 10).  
**Rationale**: Allows developers to adjust per deployment; prevents browser freeze with excessive series; documented in spec.  
**Alternatives considered**: Hard-coded cap, no cap — rejected for being inflexible and risky respectively.

**Decision**: Low-confidence flagging for metrics computed from < 3 matches.  
**Rationale**: Statistical significance threshold of 3 matches prevents misleading comparisons; asterisk + tooltip pattern is clear and unobtrusive.  
**Alternatives considered**: Silently exclude, require minimum 5 matches — rejected for being too aggressive and losing data.

**Decision**: Server-side validation of incompatible filter combinations (e.g., teams not existing in selected seasons).  
**Rationale**: Centralized validation ensures consistency; error returned to user via inline message.  
**Alternatives considered**: Client-side only, silent filtering — rejected for being error-prone and confusing.

**Decision**: Empty selection defaults to "All" (full dataset).  
**Rationale**: Standard dashboard UX pattern; prevents empty/blank states; matches current "ALL" sentinel behavior.

### Technical Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Multi-select UI pattern | Dash `dcc.Dropdown` with `multi=True` |
| Series cap behavior | Configurable `MAX_SERIES_CAP` in `config.py`, default 10 |
| Sparse data handling | Low-confidence flag when < 3 matches |
| Incompatible filters | Server-side validation with user-facing error |
| Empty selection behavior | Default to "All" (full dataset) |

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for full entity definitions. Key entities:
- **Multi-Selection State**: Filter dimension selections (seasons, teams, venue) — zero, one, or multiple per dimension
- **Unified Comparison Component**: Single component rendering overlaid series + summary panel
- **Data Series**: Single visual trace per entity (team, season, or team-season combination)
- **Segmented Metric**: Metric per entity per filter context, with low-confidence flag

### API Contracts

See `contracts/api.md` for the server-side filter validation contract. Key endpoint:
- `POST /api/validate-filters` — Validates filter combination, returns compatible subset or error

### Quickstart

See `quickstart.md` for setup and testing instructions.

## Requirements Traceability

### Functional Requirements

| ID | Requirement | Tasks |
|----|-------------|-------|
| FR-001 | Multi-select dropdowns for Season and Team filters | T006, T007 |
| FR-002 | Server-side validation of incompatible filter combinations | T003, T015 |
| FR-003 | Configurable series cap with warning banner | T001, T016 |
| FR-004 | Overlaid visual series with legend for multi-entity selection | T006, T008, T010, T012, T013 |
| FR-005 | Unified comparison component with summary panel | T014, T017, T020 |
| FR-006 | Low-confidence flagging for metrics from < 3 matches | T021, T022, T023, T024, T025 |
| FR-007 | Empty filter selection defaults to "All" (full dataset) | T007 |
| FR-008 | Backward compatibility — single-select behavior unchanged | T026, T030 |

### Non-Functional Requirements

| ID | Requirement | Tasks |
|----|-------------|-------|
| SC-001 | Comparison figure renders 10 entities in ≤2s | T029 |
| SC-002 | No new external dependencies introduced | T001–T030 (all in existing files) |
| SC-003 | Filter callbacks process 10 entities in ≤1s | T029 |
| SC-004 | Desktop browser support (Chrome, Firefox, Edge) | T006–T030 (Dash native) |
| SC-005 | Single-select behavior unchanged | T026, T030 |
| SC-006 | Inline error messages for validation failures | T014, T015 |
| SC-007 | Distinct colors for up to MAX_SERIES_CAP series | T004, T005, T016 |
| SC-008 | Loading state shown during computation | T007, T015 |
| SC-009 | Tooltip on low-confidence indicators | T023, T025 |
