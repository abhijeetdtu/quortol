# Feature Specification: Ball-by-Ball Match Simulation

**Feature Branch**: `004-ball-by-ball-simulation`  
**Created**: 2026-05-14  
**Status**: Draft  
**Input**: User description: "feature to add ball by ball simulation based on delivery level historicaldata available to the ipl data storytelling dashboard. Feature to allow for recency bias, select any two teams and get the simulation for both innings"  
**Note**: User later clarified this should be its own standalone dashboard, not a tab within the IPL data storytelling dashboard.

## Clarifications

### Session 2026-05-14

- Q: How should recency bias be applied to the historical delivery data? → A: Season-level linear decay — each IPL season gets a weight that decreases linearly with age (e.g., 2025 = 1.0, 2024 = 0.8, 2023 = 0.6), with the bias control adjusting the slope of decay.
- Q: Should the simulation's probabilistic model be validated against real IPL match data? → A: Statistical fidelity required — simulation distributions (average scores, win rates, run rates) must closely match real IPL historical averages, validated against actual match data.
- Q: What context and information should be displayed during ball-by-ball replay? → A: Score + match context — replay shows cumulative score, current over/ball count, key event highlights, current batsmen, bowler, required run rate (2nd innings), and partnerships.
- Q: Should the simulation be deterministic or randomized for the same inputs? → A: User-controlled via seed — a pre-populated random seed is displayed in the UI and can be modified by the user; same seed always produces the same result, different seeds produce different outcomes.
- Q: Should team selection use full historical data or be season-aware? → A: Full-history team profile — selecting a team uses all their data from 2008–present; season-specific weighting is handled by the recency bias control (no separate season selector needed for team profiles).
- Q: Should this feature be a tab within the IPL data storytelling dashboard or a standalone dashboard? → A: Standalone dashboard — this is its own separate dashboard with its own entry point, URL, and navigation context, not embedded within the IPL data storytelling dashboard (feature 002).
- Q: Should the IPL.csv data schema be documented in the spec or kept abstract? → A: Keep it abstract — the spec should remain data-agnostic; the implementation will adapt to whatever CSV structure exists.
- Q: What should the UI display while a simulation is running? → A: Loading spinner with progress indication — shows a spinner, "Running simulation..." message, and estimated time remaining during the 1–5 second computation window.
- Q: How should the probability distribution for each ball be calculated? → A: Bayesian model with priors — start with uniform priors and update based on historical data, allowing for uncertainty quantification.
- Q: What should happen if IPL.csv is missing, corrupted, or unreadable? → A: Show a clear error message, disable the "Simulate Match" button, and display instructions for restoring the data file.
- Q: How many concurrent simulations should the system support? → A: Single-user only — only one simulation can run at a time; new simulations cancel previous ones.

## User Scenarios & Testing

### User Story 1 - Ball-by-Ball Match Simulation (Priority: P1)

A cricket fan or analyst selects two IPL teams from a dropdown and triggers a ball-by-ball simulation of a hypothetical match between them. The system uses the available delivery-level historical data to probabilistically simulate each ball of the match — runs scored, wickets, extras — for both innings (Team A batting first, Team B chasing). The user sees a visual progression of the match showing how the score builds over 120 balls per innings, with key moments (wickets, sixes, boundaries) highlighted. The simulation applies recency bias so that more recent seasonal data has greater influence on the outcome probabilities.

**Why this priority**: This is the core feature. It transforms static historical data into an engaging, interactive experience that lets users explore "what if" match scenarios. It leverages the existing delivery-level data in a novel way and provides immediate visual feedback.

**Independent Test**: User selects two teams, triggers the simulation, and sees a complete ball-by-ball visualization of both innings with a final score summary.

**Acceptance Scenarios**:

1. **Given** the user is on the Ball-by-Ball Match Simulation dashboard, **When** they select two distinct teams from a team selector and click "Simulate Match", **Then** the system shows a loading spinner with progress indication and estimated time remaining while the simulation runs, then displays the results.

2. **Given** a simulation is running, **When** the user views the output, **Then** they see a ball-by-ball run progression chart for each innings, with each ball showing runs scored, and key events (wicket, six, four) visually highlighted.

3. **Given** a simulation has completed, **When** the user views the match summary, **Then** they see the final score for each team, the result (win/loss/tie), and key match statistics (highest partnerships, best bowling figures in the simulation).

---

### User Story 2 - Recency Bias Configuration (Priority: P2)

A data-savvy user or analyst wants to control how much the simulation weights recent data versus historical data. They can adjust a recency bias setting (e.g., a slider or dropdown) that determines how strongly recent seasons' delivery-level performance influences the simulation probabilities. A higher recency bias means the simulation is more likely to reflect how teams performed in recent years; a lower bias produces simulations based on the full historical dataset.

**Why this priority**: Recency bias is a core differentiator of this feature. It lets users test hypotheses about team evolution (e.g., "How would CSK from 2023 fare against MI from 2017?"). Without configurable recency bias, the simulation would treat all historical data equally, which may not reflect how competitive teams actually evolve.

**Independent Test**: User adjusts the recency bias setting and observes that the simulation outcomes change — higher bias produces results more aligned with recent team form.

**Acceptance Scenarios**:

1. **Given** the user has selected two teams and triggered a simulation, **When** they adjust the recency bias control (e.g., move a slider from "Low" to "High"), **Then** the simulation re-runs with updated probabilities that reflect the new recency weighting.

2. **Given** the recency bias is set to maximum, **When** the user views the simulation output, **Then** the results are driven primarily by the most recent seasons' delivery-level data (e.g., last 3–5 seasons).

3. **Given** the recency bias is set to minimum (flat weighting), **When** the user views the simulation output, **Then** the results are driven equally by all available historical data (full IPL history).

---

### User Story 3 - Simulation Replay and Exploration (Priority: P3)

A user wants to replay the simulated match ball by ball, stepping through each delivery to see the context and outcome of individual balls. They can scrub through the overs, view the current score and required run rate at any point, and replay key moments (wickets, milestones). The replay displays match context including current batsmen, bowler, required run rate (2nd innings), and partnerships alongside the score progression. This lets them experience the match narratively rather than just seeing the final chart.

**Why this priority**: This enhances engagement and storytelling value. A static chart shows the outcome; a replay lets users experience the match as it unfolded, which is more compelling for content creation, discussion, and deeper understanding.

**Independent Test**: User can step through a completed simulation ball by ball, seeing the score update along with match context (batsmen, bowler, run rate) after each delivery.

**Acceptance Scenarios**:

1. **Given** a simulation has completed, **When** the user clicks "Replay" or "Step Through", **Then** the visualization advances ball by ball, updating the score, current batsmen, bowler, and highlighting each delivery's outcome.

2. **Given** the user is in replay mode, **When** they jump to a specific over or milestone, **Then** the visualization navigates directly to that point in the match, showing the full match context at that moment.

3. **Given** the user is replaying, **When** a wicket or boundary occurs, **Then** the event is visually highlighted (e.g., color change, icon, animation).

4. **Given** the user is in the 2nd innings replay, **When** they view the replay, **Then** the required run rate is displayed and updates after each ball.

---

### Edge Cases

- What happens when the user selects the same team twice? — System prevents selection and shows an error message.
- What happens when one or both selected teams have very little historical delivery data? — System flags the simulation with a low-confidence warning and still runs it, but displays a disclaimer that results may be unreliable.
- What happens when the simulation produces a tie? — System displays "Tie" as the result and highlights the final-over tension.
- What happens if the user changes team selections while a simulation is running? — System cancels the running simulation and applies the new selection once complete.
- What happens when the user triggers multiple simulations in quick succession? — System cancels the previous run and only displays the most recent result (single-user, single-simulation model).
- What happens while a simulation is running? — System shows a loading spinner with progress indication and estimated time remaining; user interactions (team selection, simulate button) are disabled until completion.
- What happens if IPL.csv is missing, corrupted, or unreadable? — System shows a clear error message, disables the "Simulate Match" button, and displays instructions for restoring the data file.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to select exactly two distinct teams from a team selector control on the Ball-by-Ball Match Simulation dashboard
- **FR-002**: System MUST simulate a complete match (both innings, 120 balls each) using delivery-level historical data from the existing IPL dataset (IPL.csv)
- **FR-003**: System MUST apply recency bias to the simulation probabilities, weighting more recent seasons' delivery data more heavily than older data
- **FR-004**: System MUST display a ball-by-ball run progression chart for each innings, showing cumulative score over overs
- **FR-005**: System MUST visually highlight key events in the simulation (wickets, sixes, fours) on the progression chart
- **FR-006**: System MUST display a match summary including final scores for both teams, the result (win/loss/tie), and key match statistics
- **FR-007**: System MUST provide a recency bias control that allows users to adjust the weighting of recent versus historical data
- **FR-008**: System MUST allow users to replay the simulation ball by ball with step-through navigation
- **FR-009**: System MUST prevent the user from selecting the same team twice and display a clear error message
- **FR-010**: System MUST flag simulations involving teams with fewer than 3 matches of available delivery data with a low-confidence warning
- **FR-011**: System MUST handle the case where a simulation produces a tie, displaying an appropriate result indicator
- **FR-012**: System MUST allow the user to change team selections while a simulation is in progress, canceling the previous run and applying the new selection (single-user, single-simulation model)
- **FR-013**: System MUST display a pre-populated random seed in the UI that users can modify; changing the seed produces a different simulation outcome while all other inputs remain the same

### Key Entities *(include if feature involves data)*

- **Simulated Match**: A probabilistic ball-by-ball reconstruction of a hypothetical match between two selected teams, comprising two innings of 120 balls each, with each ball having an outcome (runs scored, wicket, extra) derived from historical delivery data
- **Delivery Outcome**: The result of a single simulated delivery — runs (0, 1, 2, 3, 4, 5, 6), wicket, or extra (wide, no-ball, bye, leg-bye) — determined probabilistically based on weighted historical data
- **Recency Bias Weighting**: A season-level linear decay model where each IPL season receives a weight that decreases linearly with age, controlled by a continuous slider that adjusts the decay slope from flat (all seasons equal weight) to steep (most recent season dominates)
- **Match Summary**: A post-simulation report containing final scores, result, and key statistics (highest partnerships, best bowling figures, man-of-the-match equivalent)
- **Simulation State**: The current state of an in-progress or completed simulation, including the set of selected teams, active recency bias setting, and the sequence of delivery outcomes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select two teams and complete a full ball-by-ball simulation (both innings) within 5 seconds of clicking "Simulate Match"
- **SC-002**: 90% of users can successfully run a simulation, view the ball-by-ball chart, and identify the match result without help documentation
- **SC-003**: Adjusting the recency bias control produces visibly different simulation outcomes — at least 30% of key metrics (final score, result, top scorer) change when moving bias from minimum to maximum
- **SC-004**: Users can replay a completed simulation ball by ball and navigate to any over or key event without error
- **SC-005**: Ball-by-ball progression charts render within 2 seconds of simulation completion
- **SC-006**: Simulations involving teams with fewer than 3 matches of delivery data display a low-confidence warning, and the simulation still completes successfully
- **SC-007**: The system prevents same-team selection and displays a user-friendly error message in under 1 second
- **SC-008**: Simulation aggregate statistics (average total scores, win/loss/tie distribution, average run rates) fall within 15% of actual IPL historical averages across a sample of 100 simulated matches

## Assumptions

- The existing IPL delivery-level dataset (IPL.csv) contains sufficient historical coverage (2008–present) to produce meaningful simulations for all IPL teams; the spec remains data-agnostic and the implementation will adapt to the actual CSV structure
- Recency bias is implemented as a season-level linear decay model — each IPL season receives a weight that decreases linearly with age (e.g., 2025 = 1.0, 2024 = 0.8, 2023 = 0.6), controlled by a continuous slider that adjusts the decay slope from flat (all seasons equal) to steep (only the most recent season dominates)
- The simulation uses a Bayesian model with uniform priors that are updated based on weighted historical data, allowing for uncertainty quantification in outcome probabilities
- The simulation uses a random seed that is pre-populated in the UI and editable by the user; same seed always produces identical results, enabling reproducibility and comparison across settings
- The simulation model must achieve statistical fidelity: aggregate statistics from 100+ simulated matches (average scores, win/loss/tie distribution, run rates) must fall within 15% of actual IPL historical averages, validated against real match data
- The ball-by-ball visualization uses the existing Plotly/Dash charting infrastructure already in the dashboard
- Recency bias is applied at the season level — entire seasons' data is weighted, not individual matches within seasons
- The simulation assumes Team A bats first and Team B chases second (standard cricket format)
- Team selection uses full historical data (2008–present) for the selected team; season-specific weighting is handled entirely by the recency bias control — no separate season selector is needed for team profiles in v1
- This feature is its own standalone dashboard — not a tab within the IPL data storytelling dashboard (feature 002). It has its own entry point, URL, and navigation context.
- Mobile support is out of scope for v1 — desktop-first experience only
- The system supports a single user at a time — only one simulation can run concurrently; new simulations cancel previous ones
- The simulation does not account for venue, weather, or pitch conditions — it uses team-level historical delivery data only
