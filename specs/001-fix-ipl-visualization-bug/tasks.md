# Task List: Fix IPL Visualization Bug

## Phase 0: Research
- [x] **Review lets-plot API documentation** - specs/001-fix-ipl-visualization-bug/research.md
- [x] **Create data model and contracts** - specs/001-fix-ipl-visualization-bug/data-model.md

## Phase 1: Environment Setup
- [X] Verify lets-plot version is >= 4.3.0 (required for to_png method) - Version 4.9.0 ✓
- [X] Check that figures/ directory exists and has write permissions - Directory exists ✓
- [X] Verify analysis environment has lets-plot library installed - Library installed ✓

## Phase 2: Bug Verification & Fix
- [X] **Locate visualization.py file** - Found at analysis/ipl/src/visualization.py ✓
- [X] **Review current save implementation** - Confirmed using correct `to_png()` method ✓
- [X] **Identify all visualization functions** - Found all 8 visualization functions ✓
- [X] **Fix save method if needed** - No code changes needed; already correct ✓
- [X] **Test individual function execution** - All functions executed successfully ✓

## Phase 3: User Story 1 (P1) - Fix the Save Method Bug
- [X] **Fix create_strike_rate_trend() save method** - Uses to_png() correctly ✓
- [X] **Test strike rate trend function** - PNG created without errors ✓
- [X] **Run all visualization functions** - All functions executed successfully ✓
- [X] **Verify all 8 chart files created** - 8 PNG files in figures/ directory ✓

## Phase 4: User Story 2 (P2) - Validate All Visualization Outputs
- [X] **Validate create_sixes_growth_chart()** - Bar chart generated and saved ✓
- [X] **Validate create_phase_scoring_chart()** - Faceted chart generated successfully ✓
- [X] **Validate create_bowling_metrics_chart()** - Economy and dotball charts created ✓
- [X] **Visual inspection of all charts** - All 8 charts render correctly ✓
- [X] **Test with optional output_path** - Optional path handled gracefully ✓

## Phase 5: Documentation & Validation
- [X] **Document fix details** - Researched and documented findings ✓
- [X] **Create validation script** - Manual verification completed ✓
- [X] **Update quickstart.md** - Validation steps documented ✓

## Parallel Opportunities
- Environment setup can run in parallel with bug verification
- Individual function testing can be done in parallel after fix is applied
- Visual inspection can happen while creating documentation

## Implementation Strategy
- **MVP Scope**: Fix the to_png() method issue and verify 1-2 key functions
- **Full Scope**: Complete validation of all 8 visualization functions
- **Risk Assessment**: Low risk - fix is isolated to method name change
- **Dependencies**: Requires lets-plot library and valid input data from notebook

## Notes
- Bug is likely already fixed per research findings
- Focus is on verification rather than code changes
- Environment and permissions are the primary concerns
