# Feature Specification: Fix IPL Visualization Script Bug

**Feature Branch**: `001-fix-ipl-visualization-bug`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "identify and fix bugs in analysis/ipl visualization script"

## User Scenarios & Testing

### User Story 1 - Fix Plot Save Method Bug (Priority: P1)

As an IPL data analyst, I need the visualization script to correctly save charts so that I can export analysis results for reports and presentations.

**Why this priority**: This is a critical blocking bug that prevents any visualization output, making the entire analysis incomplete.

**Independent Test**: Can be tested by running the visualization function and verifying that PNG files are successfully generated in the figures directory.

**Acceptance Scenarios**:

1. **Given** the visualization script has been updated to use the correct save method, **When** I call `create_strike_rate_trend()` with an output path, **Then** the chart should be saved as a PNG file without throwing errors.

2. **Given** the visualization script has been updated, **When** I run all visualization functions, **Then** all 8 chart files should be created successfully in the figures/ directory.

3. **Given** the visualization script has been updated, **When** I execute the notebook cell that generates the strike rate trend chart, **Then** the chart should be saved and no AttributeError should be raised.

---

### User Story 2 - Validate All Visualization Outputs (Priority: P2)

As an IPL data analyst, I need all visualization functions to work correctly with their respective data inputs so that I can produce a complete analysis.

**Why this priority**: While the primary bug fix enables chart generation, validating all visualization functions ensures the entire analysis workflow functions correctly.

**Independent Test**: Can be tested by running each visualization function independently and verifying the generated PNG files render correctly.

**Acceptance Scenarios**:

1. **Given** the visualization script is bug-free, **When** I call `create_sixes_growth_chart()` with season sixes data, **Then** the bar chart should be saved without errors.

2. **Given** the visualization script is bug-free, **When** I call `create_phase_scoring_chart()` with phase-wise data, **Then** the faceted line chart should be generated and saved.

3. **Given** the visualization script is bug-free, **When** I call `create_bowling_metrics_chart()` with bowling metrics data, **Then** both economy rate and dot ball ratio charts should be generated.

---

## Requirements

### Functional Requirements

- **FR-001**: The visualization script MUST use the correct `to_png()` method from lets-plot API instead of the non-existent `save()` method.
- **FR-002**: The script MUST successfully save all 8 visualization charts when executed in the notebook environment.
- **FR-003**: The script MUST handle optional output_path parameters gracefully, allowing chart generation without file output for quick testing.
- **FR-004**: All visualization functions MUST maintain their existing aesthetic specifications (colors, themes, labels) after the bug fix.

### Key Entities

- **Visualization Functions**: Reusable functions that generate lets-plot charts with specific data inputs and styling.
- **Chart Files**: PNG output files saved to the figures/ directory containing the visualization results.
- **Plot Object**: The lets-plot `ggplot` object representing a chart that can be rendered and saved.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 8 visualization functions execute without AttributeError when called with valid input data.
- **SC-002**: All PNG chart files are successfully created in the figures/ directory when output_path is specified.
- **SC-003**: The notebook execution completes without errors in the visualization code cells.
- **SC-004**: Generated charts render correctly and display expected data visualizations (verified by visual inspection).

## Assumptions

- **A1**: The lets-plot library is installed and available in the analysis environment.
- **A2**: The figures/ directory exists and has write permissions.
- **A3**: The notebook environment supports HTML output for lets-plot visualization display.
- **A4**: All input data (season_sr, season_sixes, phase_data, etc.) is correctly formatted and available from previous notebook cells.
- **A5**: The bug is isolated to the save method call and does not affect other aspects of the visualization functions.
- **A6**: No other bugs exist in the visualization.py file beyond the identified save method issue.
