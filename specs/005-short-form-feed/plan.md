# Implementation Plan: Short-Form Content Feed

**Branch**: `005-short-form-feed` | **Date**: 2026-05-30 | **Spec**: [spec.md](../specs/005-short-form-feed/spec.md)
**Input**: Feature specification from `/specs/005-short-form-feed/spec.md`

## Summary

Implement a short-form content feed page within the existing Quortol Vue 3 frontend. Users browse pre-populated posts (JPG/PNG images, MP4 videos 1-60s duration, blog-style text) in an infinite scroll layout. Posts have title, body text, author, timestamp, and tags. Users can discover content through tag-based filtering and keyword search, then view detailed post metadata. No user engagement features (likes, comments, shares) — passive consumption only. Backend is shared Flask API; frontend is new Vue 3 route (`/shorts`).

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vue 3.3+ (frontend)  
**Primary Dependencies**: Flask (backend API), Vue 3 + Vite (frontend), Axios (HTTP client), pandas (data processing)  
**Storage**: Static JSON files — `backend/data/short_form/posts.json` (post metadata, media URLs, tags); static media files in `backend/static/short_form/` directory  
**Testing**: pytest (backend logic), Vue Test Utils + Jest (frontend unit tests), Cypress (integration tests)  
**Target Platform**: Desktop browser (Chrome, Firefox, Edge) — mobile out of scope for v1  
**Project Type**: Web application (Vue 3 frontend page within Flask backend)  
**Performance Goals**: Feed loads 20 posts within 30 seconds; media renders in 95%+ of views; search/filter returns results within 10 seconds  
**Constraints**: Desktop-first, no mobile support; infinite scroll pagination; pre-populated content only (no upload UI); flat tag structure (no hierarchies); Vue 3 frontend route (`/feed`)  
**Scale/Scope**: ~1000 posts initially, expandable to 10k+; unlimited tags per post; media file sizes determined by system admin

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| **I. Code Quality** | ✅ Compliant | All new functions will have single responsibility; no dead code or debug artifacts |
| **II. Testing Standards** | ✅ Compliant | Tests will cover success paths (feed browsing, filtering), error states (broken media), and edge cases (empty feed, large post count) |
| **III. UX Consistency** | ✅ Compliant | Uses existing Vue 3 components; loading/empty/error states handled consistently with project design tokens |
| **IV. Performance Requirements** | ✅ Compliant | Filter operations use pandas vectorized operations; media lazy-loading prevents initial bundle bloat |
| **V. Simplicity & Maintainability** | ✅ Compliant | No new external dependencies (reuses existing Vue app); YAGNI principle followed (no engagement features) |

**GATE STATUS**: PASS — No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/005-short-form-feed/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Phase 1 output (feed API contract)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app.py               # MODIFY: Add /api/short-form/feed and /api/short-form/posts/{id} routes
└── api/
└── features/short_form/
        ├── __init__.py  # NEW: API blueprint registration
        ├── feed_api.py  # NEW: Feed endpoint handlers
        └── post_api.py  # NEW: Post detail endpoint handlers

frontend/
├── src/
│   ├── router/
│   │   └── index.js     # MODIFY: Add `/shorts` route
│   ├── views/
│   │   └── ShortFormFeed.vue  # NEW: Feed page component (route: /shorts)
│   ├── components/
│   │   ├── PostCard.vue         # NEW: Post card component
│   │   ├── PostModal.vue        # NEW: Post detail modal
│   │   ├── TagFilter.vue        # NEW: Tag filter dropdown
│   │   └── SearchBar.vue        # NEW: Keyword search input
│   └── api/
│       └── feedService.js       # NEW: API client for feed endpoints

frontend (shared)
├── stores/                    # Shared Pinia stores (auth, etc.)
└── assets/                    # Shared CSS, images
```

**Structure Decision**: New Vue 3 route (`/shorts`) within existing `frontend/` app. Backend adds new API routes in `backend/api/shorts/`. Reuses existing Vue components, design tokens, and authentication. No upload UI required — content management is admin-only (outside scope).

### Implementation Notes

- `_load_posts()` returns `List[Post]` — all posts from JSON file, sorted by timestamp descending
- `_filter_posts(posts, tags, keyword)` filters by tag list and/or keyword search
- `_get_post_detail(post_id)` returns single post with full metadata for detail view
- Infinite scroll uses server-side pagination (`?page=1&limit=20`) to prevent excessive data transfer
- Empty feed displays placeholder message: "No posts available yet. Check back soon!"

## Phase 0: Research

### Research Findings

See `research.md` for detailed technical decisions including:
- Server-side pagination with `?page&limit` (Decision 1 in research.md)
- Media lazy-loading using Intersection Observer (Decision 3 in research.md)
- Modal overlay for post details (Decision 6 in research.md)
- Empty state placeholder message pattern

**Key Decisions Summary**:
- Tag filtering: Vue 3 multi-select dropdown (consistent with project conventions)
- Pagination: Server-side with infinite scroll trigger (see research.md:Decision 1)
- Media loading: Lazy-load when in viewport (see research.md:Decision 3)

### Technical Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Feed pagination pattern | Dash `dcc.Dropdown` with multi-select + server-side pagination |
| Infinite scroll trigger | Scroll event listener triggers `_load_more_posts()` callback |
| Media lazy-loading | Plotly figure builder uses lazy image/video loading |
| Empty state handling | Placeholder message: "No posts available yet" |
| Search/filter performance | Pandas vectorized operations + caching with `@lru_cache` |

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for full entity definitions. Key entities:
- **Post**: Short-form content item with text, media (images/videos), metadata (author, timestamp), and multiple tags
- **Tag**: Flat classification label (e.g., #cricket, #ipl) — no hierarchies; each post can have multiple tags

### API Contracts

See `contracts/api.md` for the feed API contract. Key endpoints:
- `GET /api/short-form/feed?page=1&limit=20&tags=&keyword=` — Returns paginated posts with optional filters
- `GET /api/short-form/posts/{id}` — Returns single post details for detail view

### Quickstart

See `quickstart.md` for setup and testing instructions.

## Requirements Traceability

### Functional Requirements

| ID | Requirement | Tasks |
|----|-------------|-------|
| FR-001 | System MUST display a scrollable feed of short-form content posts to users | T001, T002 |
| FR-002 | System MUST render JPG/PNG images, MP4 videos (1-60 seconds duration), and text within each post; all media is pre-populated by the system | T003, T004 |
| FR-003 | System MUST allow users to filter posts by multiple tags (e.g., #cricket, #ipl, #match) and each post can have multiple associated tags | T005, T006 |
| FR-004 | System MUST enable keyword search across all posts | T007, T008 |
| FR-005 | Users MUST be able to view full post details including metadata (author, timestamp) | T009, T010 |

### Non-Functional Requirements

| ID | Requirement | Tasks |
|----|-------------|-------|
| SC-001 | Users can browse the feed and view at least 20 posts within 30 seconds of loading | T002 |
| SC-002 | Media (images/videos) renders correctly in 95%+ of post views without errors | T004 |
| SC-003 | Users can find specific content using filters or search within 10 seconds | T008 |
| SC-004 | Post details page loads fully visible metadata and media gallery within 2 seconds | T010 |


