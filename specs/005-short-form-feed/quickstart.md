# Quickstart: Short-Form Content Feed

**Branch**: `005-short-form-feed` | **Date**: 2026-05-30 | **Spec**: [spec.md](../specs/005-short-form-feed/spec.md)

## Overview

This guide provides setup and testing instructions for the short-form content feed feature. Follow these steps to get started quickly.

---

## Prerequisites

1. **Python 3.11+** installed (project minimum 3.8+)
2. **Flask** dependencies installed in virtual environment
3. **Node.js 16+** and **npm** for Vue frontend build
4. **Sample posts.json file** with test data (see "Setup" section below)
5. **Media files** in `backend/static/short_form/` directory (images/videos)

---

## Setup

### Step 1: Create Sample Data

Create the sample posts JSON file at `backend/data/short_form/posts.json`:

```bash
# Create directory structure
mkdir -p backend/data/short_form
mkdir -p backend/static/short_form/images
mkdir -p backend/static/short_form/videos
```

**Sample posts.json**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Amazing match highlights from yesterday's IPL game! #cricket #ipl",
    "media_url": "/static/short_form/images/post_001.jpg",
    "video_url": "/static/short_form/videos/post_001.mp4",
    "author": "Sports Desk",
    "timestamp": "2026-05-30T14:30:00Z",
    "tags": ["#cricket", "#ipl", "#match"],
    "created_at": "2026-05-30T14:25:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "text": "Player of the match award ceremony highlights #ipl #awards",
    "media_url": "/static/short_form/images/post_002.jpg",
    "author": "IPL Official",
    "timestamp": "2026-05-30T12:15:00Z",
    "tags": ["#ipl", "#awards"],
    "created_at": "2026-05-30T12:10:00Z"
  }
]
```

### Step 2: Add Sample Media Files

Create placeholder media files in `backend/static/short_form/`:

```bash
# Create sample image (can be any JPG/PNG)
touch backend/static/short_form/images/post_001.jpg
touch backend/static/short_form/images/post_002.png

# Create sample video (can be any MP4, max 60s duration)
touch backend/static/short_form/videos/post_001.mp4
```

### Step 3: Update Agent Context

Update the `AGENTS.md` file to reference this plan:

**Before**:
```markdown
<!-- SPECKIT START -->
Previous feature references here...
<!-- SPECKIT END -->
```

**After**:
```markdown
<!-- SPECKIT START -->
Current Plan Reference: specs/005-short-form-feed/plan.md
<!-- SPECKIT END -->
```

---

## Running the Application

### Start Flask Backend

```bash
cd backend
python app.py
```

The Flask API will be available at `http://localhost:5000`.

### Build and Run Vue Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vue application will be available at `http://localhost:8050` (or configured port).

### Access the Shorts Page

Navigate to the short-form feed in the Vue app:
```
http://localhost:8050/shorts
```

Note: The Flask backend serves API endpoints at `/api/short-form/feed` and `/api/short-form/posts/{id}`. The Vue frontend makes HTTP requests using Axios.

---

## Testing

### Unit Tests

Run pytest for backend logic:

```bash
cd backend
pytest backend/tests/contract/test_short_form_api.py -v
```

**Test Scenarios**:
- Feed loads posts correctly from JSON file
- Tag filtering works (AND logic)
- Keyword search returns correct results
- Empty feed displays placeholder message
- Broken media files are logged and skipped

### Integration Tests

#### Backend Tests (pytest)

```bash
cd backend
pytest backend/tests/contract/test_short_form_api.py -v
```

**Test Scenarios**:
- Feed loads posts correctly from JSON file
- Tag filtering works (AND logic)
- Keyword search returns correct results
- Empty feed displays placeholder message
- Broken media files are logged and skipped

#### Frontend Tests (Vue Test Utils + Vitest)

```bash
cd frontend
npm run test:short-form
```

**Test Scenarios**:
- Infinite scroll triggers post loading
- Filter dropdown updates feed correctly
- Search input filters posts in real-time
- Post detail modal opens on click

#### E2E Tests (Cypress)

```bash
cd frontend
npx cypress run --spec "tests/e2e/feed.cy.js"
```

**Test Scenarios**:
- User can browse feed with infinite scroll
- User can filter by tags and search keywords
- User can view post details in modal
- Empty state displays correctly

### Manual Testing

**Scenario 1: Browse Feed**
1. Navigate to `/shorts`
2. Scroll down — verify posts load automatically (infinite scroll)
3. Verify posts are sorted by timestamp descending (newest first)
4. **Expected**: 20 posts per page; full metadata visible

**Scenario 2: Filter by Tags**
1. Click tag filter dropdown
2. Select multiple tags (e.g., `#cricket`, `#ipl`)
3. Verify only posts with BOTH tags appear
4. Clear filters — verify all posts reappear
5. **Expected**: AND logic filtering; no duplicate posts

**Scenario 3: Keyword Search**
1. Enter keyword in search input (e.g., "match")
2. Verify matching posts appear (case-insensitive)
3. Combine with tag filter — verify both filters apply
4. Clear search — verify all posts reappear
5. **Expected**: Partial match across text and tags

**Scenario 4: View Post Details**
1. Click on any post card in feed
2. Verify modal opens with full metadata
3. Check author, timestamp, media gallery visible
4. Close modal — verify scroll position preserved
5. **Expected**: No page navigation; context maintained

**Scenario 5: Empty Feed State**
1. Delete all posts from `posts.json`
2. Refresh feed page
3. Verify placeholder message displays
4. **Expected**: "No posts available yet" message shown

**Scenario 6: Broken Media Handling**
1. Remove one media file from `backend/static/short_form/`
2. Refresh feed page
3. Verify post with broken media is skipped
4. Check console logs for error message
5. **Expected**: Post excluded; error logged

---

## Performance Verification

### SC-001: Browse Feed Performance

**Test**: Load 20 posts and measure backend response time
```bash
time curl -s "http://localhost:5000/api/short-form/feed?page=1&limit=20" > /dev/null
```

**Expected**: Backend response < 30 seconds for 20 posts

### SC-002: Media Rendering

**Test**: Load feed and check media errors in Vue console
```bash
# Open browser DevTools → Console tab
# Watch for failed image/video loads
# Check IntersectionObserver lazy loading works
```

**Expected**: 95%+ of media renders without errors (broken media excluded)

### SC-003: Search/Filter Performance

**Test**: Apply tag filter and keyword search, measure response time
```bash
time curl -s "http://localhost:5000/api/short-form/feed?page=1&limit=20&tags=#cricket&keyword=match" > /dev/null
```

**Expected**: Results returned within 10 seconds

### SC-004: Post Detail Load Time

**Test**: Click post card, measure modal open time
```bash
# Open browser DevTools → Network tab
# Click post card → observe API response time
# Check Vue component render time
```

**Expected**: Post details load within 2 seconds (including Axios request + Vue render)

---

## Troubleshooting

### Issue: Feed shows "No posts available yet" despite having data

**Solution**: Verify `posts.json` file exists and contains valid JSON array. Check file permissions allow read access.

### Issue: Media files don't display (broken image/video)

**Solution**: Verify media files exist in `backend/static/short_form/` directory. Check URLs in `posts.json` use `/static/short_form/` prefix.

### Issue: Tag filtering doesn't work

**Solution**: Verify tags in `posts.json` use hashtag format (`#cricket`). Check tag names match exactly (case-sensitive).

### Issue: Search returns no results for obvious keywords

**Solution**: Verify search is case-insensitive. Check keyword exists in either `text` field or `tags` array of posts.

---

## Next Steps

After completing setup and testing:
1. Run `/speckit.tasks` to generate implementation tasks
2. Assign tasks to team members
3. Begin development with backend-first approach (per Constitution)
4. Test each feature incrementally before proceeding

---

## References

- [Feature Specification](../specs/005-short-form-feed/spec.md)
- [Implementation Plan](../specs/005-short-form-feed/plan.md)
- [Data Model](../specs/005-short-form-feed/data-model.md)
- [API Contracts](../specs/005-short-form-feed/contracts/api.md)


