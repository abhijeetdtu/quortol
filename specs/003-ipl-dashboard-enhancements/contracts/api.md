# API Contract: Filter Validation

**Feature**: `003-ipl-dashboard-enhancements`
**Date**: 2026-05-13
**Status**: Complete

## Overview

This document defines the server-side filter validation contract for the IPL Dashboard Enhancements. The validation runs within the existing Dash callback (no separate API endpoint is required — validation is inline in the callback). This contract documents the validation logic, expected behavior, and error responses for integration testing.

## Validation Function

### `_validate_filter_combination(seasons, teams, venue, matches_df)`

Validates that selected filter combinations are compatible against the match dataset.

**Parameters**:
| Name | Type | Description |
|------|------|-------------|
| `seasons` | `list[str]` or `None` | Selected seasons (None = "All") |
| `teams` | `list[str]` or `None` | Selected teams (None = "All") |
| `venue` | `str` or `None` | Selected venue (None = "All") |
| `matches_df` | `pd.DataFrame` | Cached match metadata from `Match_Info.csv` |

**Returns**: `dict` with the following structure:
```python
{
    "valid": bool,           # True if all selections are compatible
    "incompatible_entities": list[str],  # Teams with zero matches in selected seasons
    "error_message": str or None,        # Human-readable error or None
    "compatible_subset": {
        "seasons": list[str] or None,
        "teams": list[str] or None,
        "venue": str or None
    }
}
```

## Validation Logic

1. Load `matches_df` (cached via `@lru_cache` in `_load_dataset()`)
2. If `seasons` is None or empty, filter to all seasons
3. For each team in `teams`:
   a. Check if team appears as `team1` or `team2` in any match within selected seasons
   b. If zero matches found → team is incompatible
4. Return result dict with incompatible entities and error message

## Error Messages

Error messages follow Constitution Principle III (clear, no technical jargon):

| Scenario | Error Message |
|----------|---------------|
| One incompatible team | "{team} did not play in the selected season(s). Please deselect {team} or adjust your season selection." |
| Multiple incompatible teams | "{teams} did not play in the selected season(s). Please deselect these teams or adjust your season selection." |
| No matches for venue | "No matches found at '{venue}' in the selected season(s). Please adjust your venue or season selection." |

## Dash Integration

The validation runs inline within the existing `update_dashboard` callback:

```python
# Pseudocode for callback integration
validation_result = _validate_filter_combination(season_value, team_value, venue_value, data['matches'])

if not validation_result['valid']:
    # Show error in dashboard
    error_div = html.Div(validation_result['error_message'], style={'color': 'red', 'padding': '8px'})
    # Return empty figures for all charts
    return [empty_div] * 13

# Proceed with normal rendering using compatible_subset
```

## Test Cases

| Test | Input | Expected |
|------|-------|----------|
| Valid: all teams, all seasons | seasons=None, teams=None, venue=None | `valid=True`, `incompatible_entities=[]` |
| Valid: specific team in season | seasons=["2023"], teams=["CSK"], venue=None | `valid=True`, `incompatible_entities=[]` |
| Invalid: team not in season | seasons=["2023"], teams=["KXIP"], venue=None | `valid=False`, `incompatible_entities=["KXIP"]` |
| Partial: mix of valid/invalid | seasons=["2023"], teams=["CSK", "KXIP"], venue=None | `valid=False`, `incompatible_entities=["KXIP"]` |
| Valid: venue in season | seasons=["2023"], teams=None, venue="Wankhede" | `valid=True`, `incompatible_entities=[]` |
