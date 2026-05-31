# Data Model: Short-Form Content Feed

**Branch**: `005-short-form-feed` | **Date**: 2026-05-30 | **Spec**: [spec.md](../specs/005-short-form-feed/spec.md)

## Entity Definitions

This document defines the data entities for the short-form content feed feature. All entities are stored in static JSON files with media files in `backend/static/short_form/` directory.

---

### Post Entity

**Description**: A single piece of short-form content containing text, media (images/videos), metadata, and tags. Pre-populated by the system (no user uploads).

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ Yes | Unique post identifier (UUID v4) |
| `text` | string | ⚠️ Conditional | Post caption/body text (max 2000 chars); required if no media |
| `media_url` | string | ⚠️ Conditional | URL to image file (JPG/PNG); required if image post |
| `video_url` | string | ⚠️ Conditional | URL to video file (MP4); required if video post |
| `author` | string | ✅ Yes | Post author name or identifier |
| `timestamp` | datetime | ✅ Yes | ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`) — reverse chronological sort key |
| `tags` | array<string> | ✅ Yes | Flat tags (e.g., `["#cricket", "#ipl", "#match"]`); minimum 1 tag required |
| `created_at` | datetime | ✅ Yes | ISO 8601 format — system creation timestamp |
| `updated_at` | datetime | ⚠️ Conditional | ISO 8601 format — last update timestamp; optional for read-only posts |

**Validation Rules**:
- At least one of `text`, `media_url`, or `video_url` must be present (cannot be empty post)
- `media_url` must be valid JPG/PNG file (server validates on upload)
- `video_url` must be valid MP4 file with duration 1-60 seconds (server validates on upload)
- `tags` array must have minimum 1 element; no duplicates within same post
- `timestamp` must be in the future or present (no past timestamps allowed)

**State Transitions**:
```python
# Valid transitions (admin-only operations)
Post = {status: "draft"} → {status: "published"}  # Admin publishes post
Post = {status: "published"} → {status: "archived"}  # Admin archives post
Post = {status: "archived"} → {status: "deleted"}  # Admin deletes post (permanent)

# No user-triggered transitions (passive consumption only)
```

**Clarification**: For v1 implementation, posts are pre-populated from static JSON file. 
Admin publish workflow is OUT OF SCOPE - all posts start as "published" status.
The state transition model is documented for future admin panel enhancement but not implemented in this feature.

**Relationships**:
- **Many-to-many with Tag**: Each post can have multiple tags; each tag can belong to multiple posts
- **One-to-many with Media**: Post has optional image + optional video (at least one required if text absent)
- **Many-to-one with Author**: Multiple posts can be authored by same person/entity

**Example Post Object**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Amazing match highlights from yesterday's IPL game! #cricket #ipl",
  "media_url": "backend/static/short_form/images/post_001.jpg",
  "video_url": "backend/static/short_form/videos/post_001.mp4",
  "author": "Sports Desk",
  "timestamp": "2026-05-30T14:30:00Z",
  "tags": ["#cricket", "#ipl", "#match"],
  "created_at": "2026-05-30T14:25:00Z",
  "updated_at": "2026-05-30T14:30:00Z"
}
```

---

### Tag Entity

**Description**: Flat classification label that groups posts by topic for filtering. No hierarchical relationships; each post can have multiple tags.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Tag name (e.g., "cricket", "ipl", "match"); no hash symbol stored in database |
| `slug` | string | ✅ Yes | URL-safe identifier (`#cricket`, `#ipl`, `#match`) — used for display and API |
| `created_at` | datetime | ✅ Yes | ISO 8601 format — system creation timestamp |

**Validation Rules**:
- `name` must be unique across all tags (case-insensitive)
- `slug` must match hashtag pattern (`#<word>`) for consistent display
- No special characters allowed in `name` except alphanumeric and underscores
- Tags are immutable once created (no renaming; delete + recreate if needed)

**State Transitions**:
```python
# No state transitions (tags are static reference data)
Tag = {status: "active"}  # Always active; no archiving or deletion allowed
```

**Relationships**:
- **Many-to-many with Post**: Each tag can belong to multiple posts; each post can have multiple tags
- **Zero-to-one with Category**: Future enhancement (not in scope for v1) — could group related tags

**Example Tag Object**:
```json
{
  "name": "cricket",
  "slug": "#cricket",
  "created_at": "2026-05-30T14:00:00Z"
}
```

---

## Data Storage Structure

### JSON File Layout

**Location**: `backend/data/short_form/posts.json`

**Format**: Array of Post objects (not individual files) for efficient batch loading

**Example Structure**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Amazing match highlights from yesterday's IPL game! #cricket #ipl",
    "media_url": "backend/static/short_form/images/post_001.jpg",
    "video_url": "backend/static/short_form/videos/post_001.mp4",
    "author": "Sports Desk",
    "timestamp": "2026-05-30T14:30:00Z",
    "tags": ["#cricket", "#ipl", "#match"],
    "created_at": "2026-05-30T14:25:00Z"
  },
  ...
]
```

### Media File Directory Layout

**Location**: `backend/static/short_form/`

**Subdirectories**:
```
backend/static/short_form/
├── images/       # JPG/PNG files for image posts
│   ├── post_001.jpg
│   ├── post_002.png
│   └── ...
├── videos/       # MP4 files for video posts
│   ├── post_001.mp4
│   ├── post_002.mp4
│   └── ...
└── thumbnails/   # Optional: Pre-generated thumbnails for faster loading
    ├── post_001_thumb.jpg
    └── ...
```

---

## Data Loading & Caching Strategy

### Post Retrieval Pattern

**Function**: `_load_posts()`

**Return Type**: `List[Post]`

**Behavior**:
- Loads entire posts array from JSON file on first request
- Uses `@lru_cache(maxsize=1)` for caching (single in-memory instance)
- Sorts by `timestamp` descending (reverse chronological order)
- Returns empty list if JSON file missing or corrupted

**Implementation**:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_posts():
    try:
        with open("backend/data/short_form/posts.json", "r") as f:
            posts = json.load(f)
            return sorted(posts, key=lambda p: p["timestamp"], reverse=True)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
```

### Filtering & Search Pattern

**Function**: `_filter_posts(posts, tags=None, keyword=None)`

**Return Type**: `List[Post]`

**Behavior**:
- Filters by tag list (AND logic — post must have ALL selected tags)
- Searches keyword across `text` field and `tags` array (case-insensitive partial match)
- Returns empty list if no matches found (not None)

**Implementation**:
```python
def filter_posts(posts, tags=None, keyword=None):
    filtered = posts
    
    # Tag filtering (AND logic)
    if tags:
        filtered = [p for p in filtered if all(t in p["tags"] for t in tags)]
    
    # Keyword search
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [
            p for p in filtered 
            if keyword_lower in p["text"].lower() or 
               any(keyword_lower in tag.lower() for tag in p["tags"])
        ]
    
    return filtered
```

---

## Edge Cases & Error Handling

### Broken Media Files

**Scenario**: Post references a media file that doesn't exist or is corrupted.

**Handling**:
- Server validates media existence on load (check file path)
- If broken: skip post in feed; log error to console
- User sees: "Media unavailable" placeholder instead of broken image/video

**Implementation**:
```python
def validate_media(post):
    if post["media_url"] and not os.path.exists(post["media_url"]):
        logger.warning(f"Broken media reference: {post['id']} → {post['media_url']}")
        return False
    
    if post["video_url"] and not os.path.exists(post["video_url"]):
        logger.warning(f"Broken video reference: {post['id']} → {post['video_url']}")
        return False
    
    return True
```

### Empty Feed State

**Scenario**: No posts available (empty JSON array).

**Handling**:
- Display user-friendly placeholder message
- No error state (not a failure condition)
- Consistent with Constitution Principle III (UX consistency)

**Implementation**:
```python
def build_empty_state():
    return html.Div([
        h2("No posts available yet"),
        p("Check back soon for new short-form content!"),
    ], className="empty-state")
```

### No Tags on Post

**Scenario**: Post has empty tags array (invalid data).

**Handling**:
- Server validates minimum 1 tag required on post creation
- If violated: skip post in feed; log error to console
- Prevents display of uncategorized content

**Implementation**:
```python
def validate_post(post):
    if not post.get("tags") or len(post["tags"]) == 0:
        logger.warning(f"Post missing tags: {post['id']}")
        return False
    return True
```

---

## Summary

| Entity | Fields | Relationships | Validation |
|--------|--------|---------------|------------|
| **Post** | id, text, media_url, video_url, author, timestamp, tags, created_at, updated_at | Many-to-many with Tag; One-to-many with Media | At least one of text/media/video required; video duration 1-60s |
| **Tag** | name, slug, created_at | Many-to-many with Post | Unique name; hashtag pattern for slug |

All entities support passive consumption only (no user modifications). Content is pre-populated by system admin.


