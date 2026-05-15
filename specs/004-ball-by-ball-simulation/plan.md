# Implementation Plan: Ball-by-Ball Match Simulation

**Branch**: `004-ball-by-ball-simulation` | **Date**: 2026-05-14 | **Spec**: [spec.md](specs/004-ball-by-ball-simulation/spec.md)
**Input**: Feature specification from `/specs/004-ball-by-ball-simulation/spec.md`

## Summary

Build a standalone Ball-by-Ball Match Simulation dashboard that allows users to select two IPL teams and run a probabilistic ball-by-ball simulation of a hypothetical match. The simulation uses Bayesian inference with uniform priors updated from weighted historical delivery data (IPL.csv), applies season-level recency bias via linear decay, and displays results through interactive Plotly charts with ball-by-ball replay. Single-user, single-simulation model.

## Technical Context

**Language/Version**: Python 3.11+ (per constitution: Python 3.8+ minimum)  
**Primary Dependencies**: Dash (web app framework), Plotly (interactive charts), Flask (backend), pandas (data processing), scipy.stats (Bayesian inference)  
**Storage**: Static CSV file (IPL.csv) — no database  
**Testing**: pytest (per constitution), coverage measurement required  
**Target Platform**: Desktop web browser (Chrome, Firefox, Edge) — mobile out of scope for v1  
**Project Type**: Web application (standalone Dash/Flask dashboard)  
**Performance Goals**: SC-001: Simulation completes within 5 seconds; SC-005: Charts render within 2 seconds; Constitution: API endpoints target p95 < 500ms  
**Constraints**: Single-user, single-simulation (new runs cancel previous); desktop-first; no venue/weather/pitch conditions; Team A bats first, Team B chases second  
**Scale/Scope**: 10 IPL teams, 2008–present historical data, 120 balls per innings (240 total), single dashboard instance

### Architecture Clarification

**Dash callbacks vs. Flask REST API**: Dash callbacks handle all UI interactions (team selection, recency bias slider, simulate button, replay navigation). Flask REST endpoints (/api/teams, /api/simulate, /api/simulation/{match_id}) serve as a backend API layer that Dash callbacks call internally via `requests` or direct Python function calls. This is NOT a separate transport layer — Dash is the primary UI framework, Flask provides the simulation engine and data services. The constitution's "backend-first" principle applies to the Flask/Python backend (probability model, simulation engine, data loader); the Dash frontend is built second.

### Constitution Deviation: Frontend Technology

The constitution specifies "Frontend: Vue 3 with standard project conventions." This feature uses Dash (Python-based web framework) instead of Vue 3. **Justification**: The existing IPL dashboard (feature 002) already uses Dash/Plotly for interactive visualizations. Dash provides built-in reactive state management, callback-based UI updates, and Plotly integration — all critical for this simulation feature. Introducing Vue 3 would require a separate build system, API communication layer, and charting library, adding unnecessary complexity for a single-user dashboard. **Decision**: Use Dash for v1. If future features require Vue 3, a migration path can be evaluated. This deviation is documented in the Constitution Check table below.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| **I. Code Quality** | ✅ Compliant | No existing code yet; plan requires type hints (mypy), linting (flake8), formatting (black) gates before merge |
| **II. Testing Standards** | ✅ Compliant | Plan includes unit tests (probability model, models, simulation engine), integration tests (simulation pipeline, replay), contract tests (API endpoints), edge case coverage. Constitution Principle II is NON-NEGOTIABLE. |
| **III. User Experience Consistency** | ✅ Compliant | Loading states, error states, edge cases documented in spec; shared design tokens to be defined; accessibility (aria attributes, keyboard nav) required |
| **IV. Performance Requirements** | ✅ Compliant | SC-001 (5s simulation), SC-005 (2s render) within constitution p95 < 500ms target for API; profiling required before optimization |
| **V. Simplicity & Maintainability** | ✅ Compliant | YAGNI: Single-user model, no over-engineering; Bayesian model justified by uncertainty quantification need; no premature abstractions |
| **Frontend Tech** | ⚠️ Deviation | Constitution specifies Vue 3; this feature uses Dash (Python-based). Justification: existing IPL dashboard uses Dash/Plotly; Dash provides reactive state, callbacks, and Plotly integration critical for simulation. Documented deviation — not a violation of a MUST principle. |

**Gates**: ALL PASSED — No violations requiring complexity tracking. Dash deviation is documented and justified.

## Project Structure

### Documentation (this feature)

```text
specs/004-ball-by-ball-simulation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── delivery.py          # Delivery outcome model
│   │   ├── match_simulation.py  # Simulated match logic
│   │   ├── recency_bias.py      # Season-level linear decay
│   │   └── validation.py        # Statistical fidelity validation (SC-008)
│   ├── services/
│   │   ├── data_loader.py       # IPL.csv reader (data-agnostic)
│   │   ├── probability_model.py # Bayesian inference engine
│   │   ├── simulation_engine.py # Ball-by-ball simulation loop
│   │   └── error_handler.py     # Centralized error responses
│   └── api/
│       └── routes.py            # Flask REST endpoints (called by Dash callbacks)
├── tests/
│   ├── unit/
│   │   ├── test_data_loader.py
│   │   ├── test_team_profile.py
│   │   ├── test_recency_bias.py
│   │   ├── test_probability_model.py
│   │   ├── test_simulation_engine.py
│   │   ├── test_delivery.py
│   │   ├── test_match_simulation.py
│   │   ├── test_innings.py
│   │   ├── test_recency_bias_integration.py
│   │   └── test_replay_player.py
│   ├── integration/
│   │   ├── test_simulation_pipeline.py
│   │   ├── test_recency_bias_simulation.py
│   │   └── test_replay_integration.py
│   └── contract/
│       └── test_api_endpoints.py
├── mypy.ini                     # Type-checking configuration (Constitution Principle I)
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── TeamSelector.py       # Two-team dropdown with validation (Dash dcc.Dropdown)
│   │   ├── RecencyBiasSlider.py  # Continuous slider control (Dash dcc.Slider)
│   │   ├── SimulationChart.py    # Plotly ball-by-ball progression (Dash dcc.Graph)
│   │   ├── ReplayPlayer.py       # Ball-by-ball step-through (Dash dcc.Graph + buttons)
│   │   ├── MatchSummary.py       # Post-simulation report
│   │   └── LoadingSpinner.py     # Progress indication during simulation (Dash dcc.Loading)
│   ├── pages/
│   │   └── simulation.py         # Main dashboard page (Dash layout + callbacks)
│   └── services/
│       └── api_client.py         # API calls to Flask backend (via requests or direct calls)
└── tests/
    └── unit/
        └── test_components.py

figures/                          # Generated visualizations (if needed)
```

**Note**: Dash components use `.py` extension (not `.vue`) because Dash is a Python-based framework. This is consistent with the existing IPL dashboard (feature 002) which also uses Dash/Plotly.

**Structure Decision**: Backend-first, frontend-second (per constitution). Standalone Dash/Flask dashboard with separate backend API layer and frontend component layer. Dash components use `.py` files (Python-based framework), not `.vue` files.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Dash vs. Vue 3 Deviation**: The constitution specifies "Frontend: Vue 3 with standard project conventions." This feature uses Dash instead. Complexity added: None — Dash is already used in feature 002 (IPL data storytelling dashboard), so the codebase already has Dash infrastructure, dependencies, and conventions. No additional build system or tooling required. This is a deviation from the constitution's frontend recommendation, not a complexity increase.
