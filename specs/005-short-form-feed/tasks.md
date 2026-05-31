---

description: "Task list for short-form content feed implementation"
---

# Tasks: 005-short-form-feed

**Input**: Design documents from `/specs/005-short-form-feed/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories)  
**Research**: `research.md`, data-model.md, contracts/api.md, quickstart.md  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in `backend/api/shorts/`
- [ ] T002 Initialize Flask API routes for short-form feed endpoints in `backend/app.py`
- [ ] T003 [P] Configure linting and formatting tools for new Python files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create Post data model in `backend/api/shorts/models.py` (Post entity with validation)
- [X] T005 [P] Implement post loading function `_load_posts()` in `backend/api/shorts/loader.py`
- [X] T006 [P] Implement filtering and search logic `_filter_posts()` in `backend/api/shorts/filter.py`
- [X] T007 Create media validation utilities in `backend/api/shorts/validators.py` (broken media detection)
- [X] T008 Setup environment configuration management for JSON file paths

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse Short-Form Content Feed (Priority: P1) 🎯 MVP

**Goal**: Display scrollable feed of pre-populated posts with media rendering and engagement metrics visibility

**Independent Test**: Can be fully tested by loading the `/shorts` page and scrolling through 10+ posts to verify display order, media rendering, and metadata visibility.

### Tests for User Story 1 ⚠️

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T009 [P] [US1] Contract test for `/api/short-form/feed` pagination in `backend/tests/contract/test_feed_api.py`
- [ ] T010 [P] [US1] Integration test for infinite scroll workflow in `frontend/cypress/e2e/infinite_scroll.cy.js`
- [ ] T011 [P] [US1] Jest unit test for PostCard.vue media rendering in `frontend/src/components/__tests__/PostCard.spec.js`

### Implementation for User Story 1

- [X] T012 [P] [US1] Create feed API endpoint `GET /api/short-form/feed` in `backend/api/shorts/feed_api.py`
- [X] T013 [P] [US1] Implement server-side pagination logic with query parameters (`?page&limit`)
- [ ] T014 [US1] Implement tag filtering and keyword search integration in feed API
- [ ] T015 [US1] Add empty state handling (placeholder message when no posts available)
- [X] T016 [P] [US1] Create Vue 3 router configuration for `/shorts` route in `frontend/src/router/index.js`
- [X] T017 [P] [US1] Create PostCard component in `frontend/src/features/short-form/components/PostCard\.vue` (media rendering, tags display)
- [X] T018 [US1] Create ShortFormFeed page component in `frontend/src/features/short-form/pages/ShortFormFeedPage\.vue` (feed layout, infinite scroll)
- [ ] T019 [P] [US1] Implement media lazy-loading using Intersection Observer API in PostCard.vue
- [ ] T020 [US1] Add loading states and error handling for feed page

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Discover Content (Priority: P2)

**Goal**: Enable users to filter posts by tags and search keywords to discover relevant content

**Independent Test**: Can be fully tested by applying filters (e.g., "#cricket" tag) and searching for keywords to verify results are filtered correctly.

### Tests for User Story 2 ⚠️

- [ ] T021 [P] [US2] Contract test for `/api/short-form/feed` with tag filters in `backend/tests/contract/test_feed_api.py`
- [ ] T022 [P] [US2] Integration test for filter workflow in `frontend/cypress/e2e/filter_workflow.cy.js`
- [ ] T023 [P] [US2] Jest unit test for TagFilter.vue component in `frontend/src/components/__tests__/TagFilter.spec.js`

### Implementation for User Story 2

- [X] T024 [P] [US2] Create TagFilter dropdown component in `frontend/src/features/short-form/components/TagFilter\.vue` (multi-select tag selection)
- [X] T025 [P] [US2] Create SearchBar component in `frontend/src/features/short-form/components/SearchBar\.vue` (keyword search input)
- [ ] T026 [US2] Integrate TagFilter and SearchBar into ShortFormFeed page layout
- [ ] T027 [US2] Implement tag selection state management in Pinia store or component ref
- [ ] T028 [US2] Add keyword search debouncing for performance optimization
- [X] T029 [US2] Update feed API client call with filter parameters in `frontend/src/api/short-form/feedService.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Post Details (Priority: P3)

**Goal**: Display full post metadata and media gallery when users click on a post

**Independent Test**: Can be fully tested by clicking a post in the feed to view its full details page with metadata and media gallery.

### Tests for User Story 3 ⚠️

- [ ] T030 [P] [US3] Contract test for `/api/short-form/posts/{id}` in `backend/tests/contract/test_post_api.py`
- [ ] T031 [P] [US3] Cypress integration test for post modal navigation in `frontend/cypress/e2e/post_detail.cy.js`
- [ ] T032 [P] [US3] Jest unit test for PostModal.vue component in `frontend/src/components/__tests__/PostModal.spec.js`

### Implementation for User Story 3

- [ ] T033 [P] [US3] Create PostModal component in `frontend/src/features/short-form/components/PostModal\.vue` (modal overlay for post details)
- [ ] T034 [P] [US3] Implement post detail API endpoint `GET /api/short-form/posts/{id}` in `backend/api/shorts/post_api.py`
- [ ] T035 [US3] Add modal state management to ShortFormFeed.vue (open/close handlers)
- [ ] T036 [US3] Display full post metadata (author, timestamp) in PostModal component
- [ ] T037 [US3] Implement click handler to open modal from PostCard component

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Performance Validation (Cross-Cutting) ⚠️

**Purpose**: Validate SC-001 through SC-004 measurable outcomes with actual performance measurements

> **NOTE**: Constitution Principle IV requires performance validation for all success criteria

- [ ] T038 Implement load time measurement tooling in `backend/tests/performance/test_load_times.py` using pytest-benchmark
- [ ] T039 Validate search/filter returns within 10s using Cypress assertions in `frontend/cypress/e2e/performance/search_performance.cy.js`
- [ ] T040 Validate post modal loads metadata within 2s using Jest timing tests in `frontend/src/components/__tests__/PostModal.performance.spec.js`
- [ ] T041 Measure initial bundle size and verify it stays under budget (target: <500KB) in `frontend/scripts/analyze-bundle.js`
- [ ] T042 Validate p95 API response time under 500ms using Locust load testing script in `backend/tests/load/test_feed_load.py`
- [ ] T043 Validate users can view 20 posts within 30s (SC-001) in `frontend/cypress/e2e/performance/feed_scroll.cy.js`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T044 [P] Documentation updates in `specs/005-short-form-feed/quickstart.md`
- [ ] T045 Code cleanup and refactoring across all new files
- [ ] T046 Performance optimization for infinite scroll performance (non-critical paths)
- [ ] T047 [P] Security hardening (input validation, XSS prevention)
- [ ] T048 Run quickstart.md validation scenarios
- [ ] T049 Add error boundary handling for broken media files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Performance Validation (Phase 6)**: Depends on all user story implementation complete
- **Polish (Final Phase)**: Depends on performance validation and all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 feed but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tests within a story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for /api/short-form/feed pagination in backend/tests/contract/test_feed_api.py"
Task: "Integration test for infinite scroll workflow in frontend/cypress/e2e/infinite_scroll.cy.js"
Task: "Jest unit test for PostCard.vue media rendering in frontend/src/components/__tests__/PostCard.spec.js"

# Launch all implementation tasks for User Story 1 together:
Task: "Create feed API endpoint GET /api/short-form/feed in backend/api/shorts/feed_api.py"
Task: "Implement server-side pagination logic with query parameters (?page&limit)"
Task: "Create Vue 3 router configuration for /shorts route in frontend/src/router/index.js"
Task: "Create PostCard component in frontend/src/features/short-form/components/PostCard\.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (tests + implementation)
4. **STOP and VALIDATE**: Test User Story 1 independently with all test tasks
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Run tests → Deploy/Demo (MVP!)
3. Add User Story 2 → Run tests → Deploy/Demo
4. Add User Story 3 → Run tests → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (feed browsing)
   - Developer B: User Story 2 (filters/search)
   - Developer C: User Story 3 (post details)
3. QA Team runs test tasks in parallel with implementation
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests MUST fail before implementation (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 49  
**Completed**: 12 tasks (25%)  
**Phase 1 (Setup)**: 3 tasks (1 complete)  
**Phase 2 (Foundational)**: 5 tasks (5 complete) ✅  
**Phase 3 (US1 - MVP)**: 12 tasks (6 complete, 6 pending)  
**Phase 4 (US2 - Filters/Search)**: 9 tasks (0 complete, 9 pending)  
**Phase 5 (US3 - Post Details)**: 8 tasks (0 complete, 8 pending)  
**Phase 6 (Performance Validation)**: 6 tasks (pending)  
**Phase 7 (Polish)**: 6 tasks (pending)  

**MVP Scope**: User Story 1 alone delivers a browsable short-form feed with media rendering and basic metadata display. Constitution Principle II satisfied - all user stories include test phases.

**Current Progress**:
- ✅ Foundational infrastructure complete (loader, filter, validators, config)
- ✅ Feed API endpoint created (GET /api/short-form/feed)
- ✅ Vue router configured for /shorts route
- ✅ Core components created: PostCard, ShortFormFeed, TagFilter, SearchBar
- ✅ feedService.js API client created
- ⏳ Test tasks pending (T009-T011 for US1, T021-T023 for US2, T030-T032 for US3)


