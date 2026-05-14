# Tasks: IPL Dashboard Enhancements

**Input**: Design documents from `/specs/003-ipl-dashboard-enhancements/`
**Branch**: `003-ipl-dashboard-enhancements`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, contracts/api.md, quickstart.md

**Tests**: Not requested — manual testing checklist covers all acceptance criteria per quickstart.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add configuration parameters needed by all user stories.

- [X] T001 Add `MAX_SERIES_CAP = 10` and `LOW_CONF_THRESHOLD = 3` to `backend/dashboards/ipl_deep/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Extend `_filter_frames()` in `backend/dashboards/ipl_deep/page.py` to accept `season_value` and `team_value` as `list` or `None` (empty/None → "All"); return `Tuple[pd.DataFrame, List[pd.DataFrame]]` — `(all_matches_df, [deliveries_df_for_each_entity])`; raise `ValueError` on invalid filter dict
- [X] T003 Add `_validate_filter_combination()` function in `backend/dashboards/ipl_deep/page.py` that checks each selected team exists in selected seasons using `Match_Info.csv`, returning validation result dict per `contracts/api.md`
- [X] T004 Add `_get_series_colors(entity_names, max_cap)` helper in `backend/dashboards/ipl_deep/page.py` that assigns distinct colors from `theme.py` `CHART_COLORWAY` (extended if >5 series) and returns list of HEX colors capped at `MAX_SERIES_CAP`
- [X] T005 Extend `CHART_COLORWAY` in `backend/dashboards/theme.py` with additional distinct colors to support up to `MAX_SERIES_CAP` (default 10) series

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Multi-Select Team Comparison (Priority: P1) 🎯 MVP

**Goal**: Users can select multiple teams and see all charts display separate overlaid visual series with a visible legend.

**Independent Test**: User selects 2+ teams from the Team filter dropdown; all charts update to show distinct overlaid series per team with a legend distinguishing them.

### Implementation for User Story 1

- [X] T006 [P] [US1] Update season and team dropdowns in `backend/dashboards/ipl_deep/page.py` `layout()` from single-select (`clearable=False`, `'ALL'` value) to `multi=True`, `clearable=True`, `value=None`
- [X] T007 [US1] Update `update_dashboard()` callback in `backend/dashboards/ipl_deep/page.py` to convert `None`/`[]` to `None` (All) for season and team inputs, and pass multi-select lists to `_filter_frames()`
- [X] T008 [US1] Refactor `_build_over_run_rate_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, iterate entities, and add one `go.Scatter` trace per entity with color from `_get_series_colors()`
- [X] T009 [US1] Refactor `_build_top_batters_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, compute top batters per entity, and add one `go.Bar` trace per entity with distinct colors
- [X] T010 [US1] Refactor `_build_top_bowlers_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, compute top wickets per entity, and add one `go.Bar` trace per entity with distinct colors
- [X] T011 [US1] Refactor `_build_venue_innings_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, compute venue stats per entity, and add one `go.Bar` trace per entity with distinct colors
- [X] T012 [US1] Refactor `_build_season_trend_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes; when multi-entity active, render one `go.Scatter` trace per entity (skip season filter, group only by `Overs`; use `_get_series_colors()` for per-entity colors)
- [X] T013 [US1] Refactor `_build_toss_impact_figure()` in `backend/dashboards/ipl_deep/page.py` to accept `match_df` and `deliveries` as lists; when multi-entity active, compute toss win rate per entity (per team) and render grouped bars with distinct colors

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently — multi-select team comparison works across all primary charts.

---

## Phase 4: User Story 2 - Unified Comparison Component (Priority: P2)

**Goal**: A single unified comparison component accepts any combination of selected entities (teams, seasons), renders overlaid charts with distinct series, generates a summary metrics panel, and applies all active filters consistently.

**Independent Test**: User selects any combination of entities across seasons and teams; the comparison component produces overlaid charts and a metrics summary that reflect all active filters.

### Implementation for User Story 2

- [X] T014 [US2] Add error display `html.Div` and series cap warning banner to `backend/dashboards/ipl_deep/page.py` `layout()` above the KPI row
- [X] T015 [US2] Integrate `_validate_filter_combination()` call into `update_dashboard()` callback in `backend/dashboards/ipl_deep/page.py` before rendering; return empty figures and show error message if validation fails
- [X] T016 [US2] Implement series cap enforcement in `update_dashboard()` callback in `backend/dashboards/ipl_deep/page.py` that truncates entity list to `MAX_SERIES_CAP` and shows warning banner when selections exceed cap
- [X] T017 [US2] Refactor `_build_phase_breakdown_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, group by phase per entity, and render grouped bars with distinct colors per entity
- [X] T018 [US2] Refactor `_build_team_breakdown_figure()` in `backend/dashboards/ipl_deep/page.py` to accept list of dataframes, compute per-entity team run rates, and render overlaid bars with distinct colors
- [X] T019 [US2] Refactor `_build_metric_trend_chart()` in `backend/dashboards/ipl_deep/page.py` to assign distinct colors per segment when multi-entity is active (single color when single-entity)
- [X] T020 [US2] Add `_build_comparison_summary_panel()` function in `backend/dashboards/ipl_deep/page.py` that computes run_rate, strike_rate, economy, dot_ball_pct per entity and returns an `html.Table` with low-confidence asterisks, sorted by run_rate descending

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently — unified comparison component with series cap, validation, and summary panel is functional.

---

## Phase 5: User Story 3 - Cross-Segment Analysis (Team × Phase) (Priority: P3)

**Goal**: Users can see how teams perform in specific match phases (powerplay, middle, death) with team-level segmentation on the phase breakdown chart.

**Independent Test**: User selects a team and views the phase breakdown, seeing phase-level metrics (run rate, strike rate, economy) specific to that team.

### Implementation for User Story 3

- [X] T021 [US3] Refactor `_build_phase_breakdown_figure()` in `backend/dashboards/ipl_deep/page.py` to render grouped bars when multi-entity is active: each phase shows one bar per entity, with entity color coding and legend (extends T015)
- [X] T022 [US3] Update `_build_metric_trend_frames()` in `backend/dashboards/ipl_deep/page.py` to include `match_count` and `low_confidence` flag per segment for cross-segment metric display
- [X] T023 [US3] Add low-confidence indicator (asterisk + tooltip) to `_build_metric_trend_chart()` in `backend/dashboards/ipl_deep/page.py` when `low_confidence=True` for a segment
- [X] T024 [US3] Add low-confidence indicator (asterisk) to `_build_comparison_summary_panel()` in `backend/dashboards/ipl_deep/page.py` when `low_confidence=True` for a series row
- [X] T025 [US3] Update `_build_over_run_rate_figure()` in `backend/dashboards/ipl_deep/page.py` to include low-confidence tooltip on trace hover when entity has < `LOW_CONF_THRESHOLD` matches
- [X] T026 [US3] Verify backward compatibility: single-select team/season behavior produces identical output to pre-enhancement dashboard (zero regression)

**Checkpoint**: All user stories should now be independently functional — cross-segment analysis with low-confidence flagging is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T027 [P] Update `quickstart.md` in `specs/003-ipl-dashboard-enhancements/` with enhanced testing scenarios covering multi-select, series cap, low-confidence, and incompatible filters
- [X] T028 Run manual testing checklist from `quickstart.md` (all 10 scenarios) to validate complete feature set
- [X] T029 [P] Performance benchmarks: add timing assertions to `test_perf.py` — `_build_comparison_figure()` under 2s for 10 entities (SC-001), filter callbacks under 1s for 10 entities (SC-003); use `time.perf_counter()` in pytest `@pytest.mark.benchmark` tests
- [X] T030 [P] Backward compatibility verification: run existing single-select test suite (`pytest tests/test_ipl_dashboard.py -v`) and confirm all 14 existing test assertions pass unchanged; add regression test `test_single_select_unchanged()` that selects one team, one season, verifies dropdown state and chart output identical to pre-enhancement behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories proceed in priority order (P1 → P2 → P3)
  - US2 extends US1 components (multi-select dropdowns, figure builders)
  - US3 extends US2 components (phase breakdown, low-confidence flagging)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — core multi-select rendering
- **User Story 2 (P2)**: Depends on US1 — unifies comparison under single component, adds validation, cap, and summary panel
- **User Story 3 (P3)**: Depends on US2 — adds cross-segment analysis and low-confidence flagging on top of comparison infrastructure

### Within Each User Story

- Foundational helpers (T002-T005) MUST be complete before story tasks
- Layout changes before callback changes
- Callback changes before figure builder changes
- Story complete before moving to next priority

### Parallel Opportunities

- T004 (theme colorway extension) can run in parallel with T002-T003 (page.py changes)
- T008-T011 (figure builder refactoring) can run in parallel — each targets a different function
- T012-T013 (season trend + toss impact refactors) can run in parallel with T008-T011
- T027-T030 (polish) can run in parallel (T029-T030 are independent of T027-T028)
- All figure builders in US1 (T008-T013) are independently testable

---

## Parallel Example: User Story 1

```bash
# Launch all figure builder refactors together (different functions, no cross-dependencies):
Task: "T008 Refactor _build_over_run_rate_figure() to multi-series"
Task: "T009 Refactor _build_top_batters_figure() to multi-series"
Task: "T010 Refactor _build_top_bowlers_figure() to multi-series"
Task: "T011 Refactor _build_venue_innings_figure() to multi-series"
Task: "T012 Refactor _build_season_trend_figure() to multi-series"
Task: "T013 Refactor _build_toss_impact_figure() to multi-series"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T005) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T006-T013)
4. **STOP and VALIDATE**: Test multi-select team comparison independently (quickstart.md scenarios 1-3)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test multi-select team comparison → Deploy/Demo (MVP!)
3. Add User Story 2 → Test unified comparison with validation, cap, summary panel → Deploy/Demo
4. Add User Story 3 → Test cross-segment analysis with low-confidence flagging → Deploy/Demo
5. Add Phase 6 → Test performance benchmarks and backward compatibility → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T006-T013)
   - Developer B: User Story 2 (T014-T020)
   - Developer C: User Story 3 (T021-T024)
3. Stories complete and integrate independently

---

## Notes

- All changes are in `backend/dashboards/ipl_deep/page.py` and `config.py` — no new files
- `backend/dashboards/theme.py` `CHART_COLORWAY` extended for multi-series (T005)
- Backward compatibility: single-select behavior must remain unchanged (SC-005, T026)
- 30 tasks total across 6 phases (T001–T030)
- `[P]` tasks target different files or different functions within the same file with no cross-dependencies
- `[Story]` label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
