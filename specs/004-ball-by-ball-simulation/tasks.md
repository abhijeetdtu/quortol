---

description: "Task list for Ball-by-Ball Match Simulation feature"
---

# Tasks: Ball-by-Ball Match Simulation

**Input**: Design documents from `/specs/004-ball-by-ball-simulation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Constitution Principle II is NON-NEGOTIABLE — every feature MUST include tests covering success paths, error states, and edge cases. Test tasks included for every phase (T035-T048, T034b-T034f). Test failures BLOCK all merges.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths follow the structure defined in plan.md

<!-- 
  ============================================================================
  TASKS GENERATED FROM:
  - spec.md (3 user stories: P1, P2, P3)
  - plan.md (tech stack, structure)
  - data-model.md (5 entities)
  - contracts/api.md (3 REST endpoints + 4 Dash callbacks)
  - research.md (5 technical decisions)
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md (backend/src/, frontend/src/, figures/)
- [X] T002 Initialize backend with Python 3.11+ and install dependencies (dash, plotly, flask, pandas, scipy, pytest) in backend/requirements.txt
- [X] T003 [P] Configure linting (flake8) and formatting (black) tools in backend/
- [X] T003b [P] Configure type-checking (mypy) with strict mode in backend/mypy.ini, add type stubs for external libs in backend/src/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create data_loader.py in backend/src/services/data_loader.py — IPL.csv reader with schema validation, normalization, and error handling (FileNotFoundError, PermissionError, EmptyDataError)
- [X] T005 [P] Create TeamProfile model in backend/src/models/team_profile.py — fields: team_name, total_matches, avg_score_first, avg_score_chasing, avg_run_rate, wicket_frequency, six_frequency, four_frequency, season_weights
- [X] T006 [P] Create RecencyBiasWeight model in backend/src/models/recency_bias.py — linear decay calculation: weight = 1.0 - (decay_slope * (current_year - season) / years_range)
- [X] T007 Setup Flask API routes structure in backend/src/api/routes.py — register /api/teams, /api/simulate, /api/simulation/{match_id} endpoints
- [X] T008 Configure error handling and logging infrastructure in backend/src/services/error_handler.py — centralized error responses, logging for simulation failures

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

### Tests for Foundational Phase

- [X] T035 [TEST] [P] Write tests for data_loader.py — schema validation, normalization, error handling for FileNotFoundError/PermissionError/EmptyDataError in tests/unit/test_data_loader.py
- [X] T036 [TEST] [P] Write tests for TeamProfile model — field validation, season_weights calculation in tests/unit/test_team_profile.py
- [X] T037 [TEST] [P] Write tests for RecencyBiasWeight model — linear decay formula, edge cases (decay_slope=0, decay_slope=1) in tests/unit/test_recency_bias.py
- [X] T038 [TEST] [P] Write contract tests for API endpoints — /api/teams, /api/simulate, /api/simulation/{match_id} in tests/contract/test_api_endpoints.py

---

## Phase 3: User Story 1 - Ball-by-Ball Match Simulation (Priority: P1) 🎯 MVP

**Goal**: Users select two IPL teams and run a complete ball-by-ball simulation of both innings, viewing results via interactive Plotly charts with key events highlighted.

**Independent Test**: User selects two teams, triggers the simulation, and sees a complete ball-by-ball visualization of both innings with a final score summary.

### Implementation for User Story 1

- [X] T009 [P] [US1] Create DeliveryOutcome model in backend/src/models/delivery.py — fields: ball_number, runs, is_wicket, wicket_type, is_extra, extra_type, cumulative_score, cumulative_wickets, probability
- [X] T010 [P] [US1] Create SimulatedMatch model in backend/src/models/match_simulation.py — fields: match_id, team_a, team_b, innings, recency_bias, random_seed, created_at, status, result
- [X] T011 [P] [US1] Create Innings model in backend/src/models/innings.py — fields: innings_number, batting_team, balls, total_runs, wickets_lost, overs_completed, run_rate
- [X] T012 [US1] Implement ProbabilityModel (Bayesian inference) in backend/src/services/probability_model.py — Dirichlet prior, posterior update from weighted historical data, outcome sampling
- [X] T013 [US1] Implement SimulationEngine (ball-by-ball loop) in backend/src/services/simulation_engine.py — 120 balls × 2 innings, handles wickets, extras, early chase completion, threading.Lock for single-user model
- [X] T014 [US1] Implement POST /api/simulate endpoint in backend/src/api/routes.py — accepts team_a, team_b, recency_bias, random_seed; returns match_id with status "running"
- [X] T015 [US1] Implement GET /api/simulation/{match_id} endpoint in backend/src/api/routes.py — returns completed simulation data or "running" status
- [X] T016 [US1] Create TeamSelector component in frontend/src/components/TeamSelector.py — dcc.Dropdown with two-team constraint, validation error for same-team selection
- [X] T017 [US1] Create SimulationChart component in frontend/src/components/SimulationChart.py — Plotly ball-by-ball progression chart with key events (wicket, six, four) highlighted
- [X] T018 [US1] Create MatchSummary component in frontend/src/components/MatchSummary.py — final scores, result (win/loss/tie), key statistics (highest partnerships, best bowling figures)
- [X] T019 [US1] Create main dashboard page in frontend/src/pages/simulation.py — integrates TeamSelector, SimulationChart, MatchSummary; wire up Dash callbacks for simulate button

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

### Tests for User Story 1

- [X] T039 [TEST] [US1] [P] Write tests for DeliveryOutcome model — ball outcome validation, cumulative score calculation in tests/unit/test_delivery.py
- [X] T040 [TEST] [US1] [P] Write tests for SimulatedMatch model — match state transitions, result computation in tests/unit/test_match_simulation.py
- [X] T041 [TEST] [US1] [P] Write tests for Innings model — over completion, run rate calculation, all-out detection in tests/unit/test_innings.py
- [X] T042 [TEST] [US1] Write tests for ProbabilityModel — Bayesian inference, Dirichlet prior updates, outcome sampling in tests/unit/test_probability_model.py
- [X] T043 [TEST] [US1] Write tests for SimulationEngine — 120-ball loop, wicket handling, early chase completion, single-user threading in tests/unit/test_simulation_engine.py
- [X] T044 [TEST] [US1] Write integration tests for simulation pipeline — team selection → simulation → result in tests/integration/test_simulation_pipeline.py

---

## Phase 4: User Story 2 - Recency Bias Configuration (Priority: P2)

**Goal**: Users adjust a recency bias slider to control how much recent data influences simulation probabilities, observing visibly different outcomes.

**Independent Test**: User adjusts the recency bias setting and observes that the simulation outcomes change — higher bias produces results more aligned with recent team form.

### Implementation for User Story 2

- [X] T020 [US2] Create RecencyBiasSlider component in frontend/src/components/RecencyBiasSlider.py — dcc.Slider with values 0.0–1.0, labels "Low" to "High", pre-populated default 0.5
- [X] T021 [US2] Integrate recency bias control with simulation probabilities in backend/src/services/probability_model.py — update Dirichlet prior weights based on slider value
- [X] T022 [US2] Update SimulationEngine to use recency bias weights in backend/src/services/simulation_engine.py — apply season-level linear decay to historical data weighting
- [X] T023 [US2] Wire up RecencyBiasSlider to Simulate Match callback in frontend/src/pages/simulation.py — pass slider value to POST /api/simulate request

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

### Tests for User Story 2

- [X] T045 [TEST] [US2] Write tests for recency bias integration — slider value affects simulation probabilities, verify weight calculation at min/max bias in tests/unit/test_recency_bias_integration.py
- [X] T046 [TEST] [US2] Write integration tests for recency bias → simulation engine — verify bias weights are applied in simulation loop in tests/integration/test_recency_bias_simulation.py

---

## Phase 5: User Story 3 - Simulation Replay and Exploration (Priority: P3)

**Goal**: Users replay the simulated match ball by ball, stepping through each delivery to see score, match context, and key event highlights.

**Independent Test**: User can step through a completed simulation ball by ball, seeing the score update along with match context (batsmen, bowler, run rate) after each delivery.

### Implementation for User Story 3

- [X] T024 [US3] Create ReplayPlayer component in frontend/src/components/ReplayPlayer.py — step-through navigation with dcc.Graph updates, ball-by-ball progression
- [X] T025 [US3] Add match context display in frontend/src/components/ReplayPlayer.py — current batsmen, bowler, required run rate (2nd innings), partnerships, cumulative score
- [X] T026 [US3] Implement ball-by-ball step-through logic in frontend/src/components/ReplayPlayer.py — forward/backward buttons, jump to over/milestone, event highlighting (wicket, boundary)
- [X] T027 [US3] Wire up ReplayPlayer to Simulate Match callback in frontend/src/pages/simulation.py — enable replay after simulation completes, jump-to-ball functionality

**Checkpoint**: All user stories should now be independently functional

### Tests for User Story 3

- [X] T047 [TEST] [US3] Write tests for ReplayPlayer — step-through navigation, forward/backward buttons, jump-to-over functionality in tests/unit/test_replay_player.py
- [X] T048 [TEST] [US3] Write integration tests for replay → simulation data — verify replay displays correct ball-by-ball data from completed simulation in tests/integration/test_replay_integration.py

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T028 [P] Create LoadingSpinner component in frontend/src/components/LoadingSpinner.py — dcc.Loading with "Running simulation..." message, estimated time remaining, disables team selector and simulate button during simulation
- [X] T029 [P] Implement IPL.csv error handling UI in frontend/src/pages/simulation.py — clear error message, disable "Simulate Match" button, display instructions for restoring data file
- [X] T030 [P] Implement low-confidence warning for teams with < 3 matches in backend/src/services/probability_model.py and frontend/src/components/MatchSummary.py
- [X] T031 [P] Implement random seed input in frontend/src/pages/simulation.py — dcc.Input with pre-populated seed, editable by user, same seed = same result; placed alongside TeamSelector and RecencyBiasSlider in main dashboard
- [X] T032 Code cleanup and refactoring — type hints, docstrings, remove debug artifacts
- [X] T033 Performance optimization — ensure charts render within 2 seconds (SC-005), simulation completes within 5 seconds (SC-001)
- [X] T034 Update quickstart.md with final instructions and validation
- [X] T034b [P] Implement tie detection logic in backend/src/services/simulation_engine.py — detect when both innings end with equal scores, display "Tie" result in MatchSummary component (FR-011, SC-007)
- [X] T034c [P] Implement all-out innings handling in backend/src/services/simulation_engine.py — end innings early when team loses 10 wickets before 120 balls; update MatchSummary to reflect early completion
- [X] T034d [P] Implement statistical fidelity validation in backend/src/services/validation.py — load real IPL data, run 100 simulations per team pair, compare aggregate stats (average scores, win/loss/tie distribution, run rates) against actual IPL historical averages; verify results fall within 15% threshold (SC-008)
- [X] T034e [P] Implement usability validation instrumentation — track simulation completion rate, chart rendering success, and user ability to identify match result without help documentation; verify ≥90% success rate (SC-002)
- [X] T034f [P] Add accessibility compliance — semantic HTML, keyboard navigation, aria attributes for all interactive components (Constitution Principle III); add design token definitions for colors, spacing, typography

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Integrates with US1 components (ProbabilityModel, SimulationEngine) but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — Integrates with US1/US2 components (SimulationChart, MatchSummary) but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create DeliveryOutcome model in backend/src/models/delivery.py"
Task: "Create SimulatedMatch model in backend/src/models/match_simulation.py"
Task: "Create Innings model in backend/src/models/innings.py"

# Launch services after models complete:
Task: "Implement ProbabilityModel in backend/src/services/probability_model.py"
Task: "Implement SimulationEngine in backend/src/services/simulation_engine.py"

# Launch endpoints after services complete:
Task: "Implement POST /api/simulate endpoint in backend/src/api/routes.py"
Task: "Implement GET /api/simulation/{match_id} endpoint in backend/src/api/routes.py"

# Launch frontend components in parallel:
Task: "Create TeamSelector component in frontend/src/components/TeamSelector.py"
Task: "Create SimulationChart component in frontend/src/components/SimulationChart.py"
Task: "Create MatchSummary component in frontend/src/components/MatchSummary.py"
Task: "Create main dashboard page in frontend/src/pages/simulation.py"

# Launch tests in parallel after implementation:
Task: "Write tests for DeliveryOutcome model in tests/unit/test_delivery.py"
Task: "Write tests for SimulatedMatch model in tests/unit/test_match_simulation.py"
Task: "Write tests for Innings model in tests/unit/test_innings.py"
Task: "Write tests for ProbabilityModel in tests/unit/test_probability_model.py"
Task: "Write tests for SimulationEngine in tests/unit/test_simulation_engine.py"
Task: "Write integration tests for simulation pipeline in tests/integration/test_simulation_pipeline.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003b)
2. Complete Phase 2: Foundational (T004-T008) — CRITICAL — blocks all stories
3. Complete Phase 3: User Story 1 (T009-T019)
4. Complete Phase 3 Tests (T035-T044)
5. **STOP and VALIDATE**: Test User Story 1 independently — verify all tests pass, simulation completes within 5s, charts render within 2s
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T008)
2. Add User Story 1 → Test independently (T009-T019, T039-T044) → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently (T020-T023, T045-T046) → Deploy/Demo
4. Add User Story 3 → Test independently (T024-T027, T047-T048) → Deploy/Demo
5. Add Polish & Cross-Cutting (T028-T034f) → Final validation → Release
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T008)
2. Once Foundational is done:
   - Developer A: User Story 1 (T009-T019) + Tests (T039-T044)
   - Developer B: User Story 2 (T020-T023) + Tests (T045-T046)
   - Developer C: User Story 3 (T024-T027) + Tests (T047-T048)
3. Once all stories complete:
   - Developer D (or any): Polish & Cross-Cutting (T028-T034f)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- [TEST] label = test task (Constitution Principle II — NON-NEGOTIABLE)
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Total tasks: 48 (34 implementation + 8 test + 6 polish/edge case)
