# Quickstart: IPL Dashboard Enhancements

**Feature**: `003-ipl-dashboard-enhancements`
**Date**: 2026-05-13

## Prerequisites

- Python 3.11+ (project minimum 3.8+)
- Conda environment with `dash`, `plotly`, `pandas`, `numpy`, `flask`
- IPL data files: `analysis/ipl/data/Match_Info.csv` and `IPL.csv`

## Setup

1. **Activate the development environment**:
   ```bash
   conda activate quortol
   ```

2. **Ensure the project root is on the Python path**:
   ```bash
   cd C:\Users\abhij\Code\quortol
   ```

3. **Start the Flask backend** (which serves the Dash app):
   ```bash
   python backend/app.py
   ```

4. **Open the dashboard** in your browser:
   ```
   http://localhost:8050/ipl-deep-dive
   ```

## Running the Dashboard

The IPL Deep Dive dashboard is registered as a Dash page at `/ipl-deep-dive`. It is accessible from the main navigation or directly via URL.

**Default behavior** (before enhancements):
- Single-select dropdowns for Season, Team, Venue
- Single-series charts with one data trace
- No comparison panel

**After enhancements** (on `003-ipl-dashboard-enhancements` branch):
- Multi-select dropdowns for Season and Team (Dash `dcc.Dropdown` with `multi=True`)
- Multi-select Venue remains single-select (unchanged)
- Overlaid charts with distinct colors for each selected entity
- Comparison Summary Panel when 2+ entities selected
- Low-confidence indicators for metrics from < 3 matches
- Server-side validation with inline error messages

## Configuration

Edit `backend/dashboards/ipl_deep/config.py` to adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_SERIES_CAP` | 10 | Maximum simultaneous series across all charts |
| `LOW_CONF_THRESHOLD` | 3 | Minimum match count before metrics are considered statistically significant |

## Testing

### Manual Testing Checklist

1. **Multi-select teams**: Select 2+ teams from the Team filter. Verify all charts show overlaid series with distinct colors and a legend.

2. **Multi-select seasons**: Select 2+ seasons from the Season filter. Verify overlaid series with legend labels.

3. **Combined selection**: Select multiple teams AND multiple seasons. Verify team-season combinations appear as distinct series.

4. **Series cap**: Select enough teams to exceed `MAX_SERIES_CAP` (default 10). Verify a warning is displayed and only the first 10 series render.

5. **Low-confidence flagging**: Select a team with fewer than 3 matches in the selected seasons. Verify metrics show an asterisk and tooltip indicating low confidence.

6. **Incompatible filters**: Select a season where a selected team did not exist (e.g., KXIP in 2023). Verify an inline error message is displayed.

7. **Empty selection**: Deselect all items in any filter. Verify the dashboard defaults to "All" (full dataset).

8. **Single-select**: Select exactly one team. Verify the comparison panel is suppressed and charts show a single series (backward compatible).

9. **Filter change**: While multi-select is active, change the Season filter. Verify all charts and the comparison panel update reactively.

10. **Phase breakdown**: Select multiple teams and view the Phase Breakdown chart. Verify grouped bars with team-level segmentation.

### Performance Benchmarks (T029)

- **Comparison figure**: Renders 10 entities in ≤ 2 seconds
- **Filter callbacks**: Process 10 entities in ≤ 1 second after filter change

### Regression Tests (T030)

- **Single-select regression**: Verify that selecting exactly one team and one season produces identical output to pre-enhancement dashboard (manually verify via manual testing checklist scenario #8)
- **Dropdown fallback**: When `multi=False`, dropdown still works as before (single value, no array) — verified by code inspection
- **Existing test suite**: `pytest tests/test_ipl_dashboard.py -v` — no existing test file yet; regression coverage is manual via checklist scenarios #1-#10

### Unit Testing (pytest)

Run backend tests:
```bash
cd C:\Users\abhij\Code\quortol
python -m pytest backend/dashboards/ipl_deep/ -v
```

**Note**: No automated test suite exists for this feature yet. Testing is done manually via the checklist above. Future test files to create:
- `backend/dashboards/ipl_deep/tests/test_filter_validation.py` — filter validation logic
- `backend/dashboards/ipl_deep/tests/test_series_cap.py` — series cap enforcement
- `backend/dashboards/ipl_deep/tests/test_low_confidence.py` — low-confidence flagging
- `backend/dashboards/ipl_deep/tests/test_multi_select.py` — multi-select callback integration
- `backend/tests/test_ipl_dashboard.py` — backward compatibility regression tests

## Development Workflow

1. Create branch: `git checkout -b 003-ipl-dashboard-enhancements`
2. Modify `backend/dashboards/ipl_deep/page.py` and `config.py`
3. Run manual testing checklist
4. Run pytest
5. Commit with descriptive message (Constitution: "describe WHY, not just WHAT")
6. Create pull request for review

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Charts not updating after multi-select | Verify `multi=True` is set on dropdowns; check callback inputs include new filter IDs |
| Error: "too many series" | Increase `MAX_SERIES_CAP` in `config.py` or reduce selection |
| Low-confidence flagging not appearing | Verify `LOW_CONF_THRESHOLD` is set to 3; check match count in filter context |
| Incompatible filters not detected | Verify `_validate_filter_combination()` is called before rendering; check match data contains team/season info |
| Color clash with many series | Extend `CHART_COLORWAY` in `backend/dashboards/theme.py` with additional distinct colors |
