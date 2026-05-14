# Research: Derivative Art Analysis

**Feature**: Derivative Art Analysis  
**Date**: May 13 2026  
**Source**: [specs/001-derivative-art-analysis/spec.md](../spec.md)

---

## Technology Decisions

### 1. Visualization Library: lets-plot 4.9.0+

**Decision**: Use lets-plot for all chart visualizations

**Rationale**: 
- Consistent chart rendering across all analyses
- Already validated in previous project features (001-fix-ipl-visualization-bug)
- Supports PNG export for static reports
- Version 4.9.0+ provides necessary `to_png()` functionality
- Works well with Python backend for data processing

**Alternatives Considered**:
- D3.js: More flexibility but higher development overhead
- Plotly: Good interactivity but heavier dependencies
- Chart.js: Limited for complex influence chain visualizations

**Chosen**: lets-plot 4.9.0+ - Proven track record, consistent with project standards

---

### 2. Backend Framework: Flask

**Decision**: Use Flask for API endpoints

**Rationale**:
- Constitution specifies Python/Flask as approved backend
- Lightweight and simple for CRUD operations on art data
- Easy to test with pytest
- Well-documented for RESTful APIs
- Compatible with existing project architecture

**Alternatives Considered**:
- FastAPI: More modern but requires framework shift
- Django: Overkill for this analysis dashboard
- Bottle: Too minimal for structured API development

**Chosen**: Flask - Constitution-compliant, proven in project

---

### 3. Frontend Framework: Vue 3

**Decision**: Use Vue 3 for user interface

**Rationale**:
- Constitution specifies Vue 3 as approved frontend
- Component-based architecture matches dashboard needs
- Reactive state management for filter interactions
- Good ecosystem for charts (Vue wrapper for lets-plot)
- TypeScript support for type safety

**Alternatives Considered**:
- React: Not aligned with constitution standards
- Angular: Over-engineered for this scope
- Svelte: Good performance but less mature ecosystem

**Chosen**: Vue 3 - Constitution-compliant, component-driven architecture

---

### 4. Data Source: Wikipedia + WikiArt.org + Web Sources

**Decision**: Use flexible web sources for historical art data

**Rationale**:
- User clarified: "Use Wikipedia or other web sources as needed"
- Broader coverage than dedicated museum APIs
- Flexible source selection allows adapting to data availability
- Historical art records are static (no refresh cycles needed)
- Privacy-first approach (no user tracking required)

**Alternatives Considered**:
- Getty API: Higher quality but limited to museum collections
- Rijksmuseum API: Excellent data but restricted access
- MET API: Good coverage but rigid selection

**Chosen**: Flexible web sources - Aligns with user preferences and privacy goals

---

### 5. Data Storage: Static JSON Files

**Decision**: Store art data in local JSON files

**Rationale**:
- Historical art data doesn't change (static dataset)
- No automatic refresh cycles required (user decision)
- Simple to query and process
- Easier to test than dynamic database connections
- Consistent with privacy-first approach (no external calls)

**Alternatives Considered**:
- SQLite: Lightweight but unnecessary complexity
- PostgreSQL: Overkill for static data
- Redis: Unnecessary caching layer

**Chosen**: JSON files - Simple, static, testable

---

### 6. Testing Strategy: pytest + Jest

**Decision**: Use pytest for backend, Jest/Vitest for frontend

**Rationale**:
- Constitution requires testing for all features
- pytest well-integrated with Python/Flask
- Jest standard for Vue 3 testing
- Supports unit, integration, and E2E tests
- Fast execution for CI gates

**Alternatives Considered**:
- unittest: Built-in but less feature-rich
- Cypress: Good for E2E but heavier than needed

**Chosen**: pytest + Jest - Constitution-compliant, proven standards

---

### 7. Performance Targets: Defined in Success Criteria

**Decision**: Align with SC-001 to SC-005 from spec

**Rationale**:
- SC-001: 3-second dashboard load time
- SC-002: 10,000+ relationships renderable
- SC-003: 95% task completion rate
- SC-004: 3-click navigation average
- SC-005: 90% user satisfaction

**Implementation Notes**:
- Lazy-load components to meet load time target
- Paginate influence chains if >10k relationships
- Optimize chart rendering with canvas backend
- Cache filter state to reduce re-renders

---

## Integration Patterns

### API Contracts

**Endpoint Structure**:
```
GET /api/art/overview          # Dashboard overview with summary stats
GET /api/art/influences/{id}   # Influence chain for specific artwork/artist
GET /api/art/compare           # Comparative metrics for multiple entities
GET /api/art/filter            # Filter results by period/movement/medium
```

**Data Flow**:
1. Frontend triggers filter/action
2. Backend queries JSON data store
3. Process derivative metrics (originality index, influence density)
4. Return JSON response
5. Frontend renders charts with lets-plot

### Data Processing Pipeline

**Steps**:
1. Load static JSON art records
2. Parse influence chains (predecessors → successors)
3. Calculate derivative metrics:
   - Originality Index (0-100 scale)
   - Influence Density (connections per peer group)
   - Trend Analysis (time-series shifts)
4. Apply filters (period, movement, medium)
5. Return processed results

---

## Privacy & Security

**Decision**: Zero user tracking, no analytics

**Rationale**:
- User explicitly chose privacy-first approach
- Historical art analysis doesn't require user behavior data
- Simplifies compliance and reduces data storage needs
- Aligns with ethical research practices

**Implementation**:
- No cookies or local storage for tracking
- No external analytics services
- No telemetry or error reporting to external services

---

## Edge Cases & Failure Handling

**Documented in Spec**:
- No documented influences: Display "insufficient data" message
- Incomplete provenance: Use available data with disclaimer
- Conflicting sources: Show "multiple sources" indicator
- Missing artworks: Filter out of results with warning

---

## Summary

All technology decisions are aligned with:
- ✅ Constitution standards (Vue 3 + Flask)
- ✅ User preferences (privacy-first, flexible sources)
- ✅ Project constraints (desktop-first, static data)
- ✅ Performance targets (SC-001 to SC-005)
- ✅ Testing requirements (pytest + Jest)

**No additional clarifications needed**. Plan can proceed to Phase 1 design.
