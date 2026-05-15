# Research: Ball-by-Ball Match Simulation

**Feature**: 004-ball-by-ball-simulation  
**Date**: 2026-05-14  
**Status**: Complete — All NEEDS CLARIFICATION resolved via clarification session

## Technical Decisions

### Decision 1: Bayesian Probability Model

**Chosen**: Bayesian inference with uniform priors, updated from weighted historical data.

**Rationale**: 
- Provides uncertainty quantification (unlike frequency distributions)
- More statistically rigorous than simple frequency counting
- Aligns with SC-008 statistical fidelity requirement (15% tolerance)
- scipy.stats provides well-tested Bayesian inference primitives
- Simpler than ML models (random forest, neural nets) while providing better uncertainty estimates

**Alternatives Considered**:
- **Historical frequency distributions** (Option A): Simpler, more transparent, but no uncertainty quantification
- **Machine learning model** (Option C): Over-engineered for v1, requires training pipeline, harder to validate against SC-008

**Implementation Notes**:
- Use Dirichlet prior for categorical outcomes (0,1,2,3,4,6,wicket,extra)
- Update priors with weighted historical data (recency bias applied at season level)
- scipy.stats.dirichlet for prior, scipy.stats.categorical for sampling

---

### Decision 2: Data-Agnostic CSV Handling

**Chosen**: Spec remains data-agnostic; implementation adapts to actual IPL.csv structure.

**Rationale**:
- IPL.csv schema may vary across features (002, 003, 004)
- Avoids spec bloat with column definitions that may change
- Implementation layer can validate and normalize data at runtime
- Reduces spec maintenance burden

**Alternatives Considered**:
- **Document schema in spec** (Option A): More upfront clarity, but higher maintenance cost
- **Defer to planning** (Option B): Risks misaligned implementation if schema assumptions are wrong

**Implementation Notes**:
- Create data_loader.py with schema validation and normalization
- Log warnings for missing/unknown columns
- Support fallback behavior for missing fields

---

### Decision 3: Loading State UX

**Chosen**: Loading spinner with progress indication and estimated time remaining.

**Rationale**:
- Standard UX pattern for async operations
- Prevents user confusion (app not frozen)
- Sets expectations about wait time (1–5 seconds)
- Dash provides dcc.Loading component for this purpose

**Alternatives Considered**:
- **Disable button + text message** (Option A): Less informative, no progress feedback
- **Synchronous wait** (Option C): Poor UX, user has no feedback
- **Background with no feedback** (Option D): User may click multiple times, causing confusion

**Implementation Notes**:
- Use Dash dcc.Loading component with custom children
- Estimate time based on simulation complexity (120 balls × 2 innings)
- Disable team selector and simulate button during loading

---

### Decision 4: IPL.csv Error Handling

**Chosen**: Show clear error message, disable "Simulate Match" button, display instructions for restoring data file.

**Rationale**:
- Most user-friendly approach (tells user what's wrong and how to fix)
- Prevents silent failures (Option B)
- Clear actionability for users (Option C > Option A)
- Auto-retry (Option D) adds complexity without solving root cause

**Alternatives Considered**:
- **User-friendly message only** (Option A): Doesn't prevent further errors
- **Log and continue** (Option B): Silent failure, poor UX
- **Auto-retry** (Option D): Unnecessary complexity for static file

**Implementation Notes**:
- Catch FileNotFoundError, PermissionError, pandas.errors.EmptyDataError
- Display error in Dash alert component
- Disable simulation button until file is restored
- Provide instructions: "Please ensure IPL.csv is in the data/ directory"

---

### Decision 5: Single-User Concurrency Model

**Chosen**: Single-user, single-simulation — new simulations cancel previous ones.

**Rationale**:
- Simplest implementation (no queuing, locking, or session management)
- Aligns with existing edge case behavior (FR-012: cancel previous run)
- Sufficient for data storytelling use case (individual analysts)
- Avoids complexity of concurrent session management

**Alternatives Considered**:
- **Multiple concurrent simulations** (Option B): Adds queuing complexity, not needed for v1
- **Unlimited concurrency** (Option C): Resource risks, over-engineered
- **Server-limited with queuing** (Option D): Complex, not needed for single-user model

**Implementation Notes**:
- Use threading.Lock to prevent concurrent simulation runs
- Cancel running simulation on new "Simulate Match" click
- Update UI to show "Simulation cancelled — running new simulation..."
- No session management or user authentication required

---

## Technology Stack Validation

### Dash + Plotly

**Validated**: Dash is the established framework for the IPL dashboard (features 002, 003). Plotly provides interactive charts required for ball-by-ball visualization.

**Key Components**:
- `dcc.Dropdown`: Team selector (multi-select disabled, two-team constraint)
- `dcc.Slider`: Recency bias control (continuous, 0.0–1.0)
- `dcc.Loading`: Loading spinner during simulation
- `dcc.Graph`: Plotly charts for ball-by-ball progression
- `dcc.Input`: Random seed input (editable, pre-populated)

### Flask Backend

**Validated**: Flask provides the API layer for Dash callbacks. REST endpoints for simulation trigger and result retrieval.

**Key Endpoints**:
- `POST /api/simulate`: Trigger simulation with team selection, recency bias, seed
- `GET /api/simulation/{id}`: Retrieve simulation results by ID
- `GET /api/teams`: List available teams (from IPL.csv)

### pandas + scipy.stats

**Validated**: pandas for data loading/processing, scipy.stats for Bayesian inference.

**Key Functions**:
- `pandas.read_csv()`: IPL.csv loading with schema validation
- `scipy.stats.dirichlet`: Dirichlet prior for categorical outcomes
- `scipy.stats.categorical.sample()`: Sample from posterior distribution

---

## Next Steps

1. **Phase 1**: Generate data-model.md, contracts/, quickstart.md
2. **Phase 2**: Generate tasks.md (task decomposition)
3. **Implementation**: Backend-first, frontend-second (per constitution)
