# Short-Form Feature

This feature serves the `/shorts` page with namespaced API endpoints.

## Module Layout

- `api/routes.py`: Flask blueprint and route handlers
- `domain/models.py`: Post model and serialization
- `domain/filter.py`: filtering and pagination logic
- `infra/config.py`: environment-driven paths and limits
- `infra/loader.py`: JSON loading + cache
- `infra/validators.py`: local media URL and file validation

## API Contract

- `GET /api/short-form/feed?page=1&limit=20&tags=#tag&keyword=text`
- `GET /api/short-form/posts/{post_id}`

Response shape for feed:

```json
{
  "posts": [],
  "pagination": {
    "current_page": 1,
    "total_pages": 0,
    "total_posts": 0,
    "posts_per_page": 20
  },
  "empty_state": true,
  "available_tags": []
}
```

## Data and Media Ownership

- Posts JSON: `backend/data/short_form/posts.json`
- Static media root: `backend/static/short_form/`
- Media URLs in JSON must be local and start with `/static/short_form/`

Examples:

- `/static/short_form/images/post_001.jpg`
- `/static/short_form/videos/post_002.mp4`

## Add a Test Post

1. Open `backend/data/short_form/posts.json`
2. Append a new object with `id`, `text`, `author`, `timestamp`, `tags`, and optional media URLs
3. If media is used, place files under `backend/static/short_form/images` or `backend/static/short_form/videos`
4. Restart backend (or clear loader cache in-process) to ensure new data is picked up immediately

## Environment Overrides

- `SHORT_FORM_POSTS_JSON`
- `SHORT_FORM_MEDIA_DIR`
- `SHORT_FORM_MEDIA_URL_PREFIX`
- `SHORT_FORM_PAGE_SIZE`
- `SHORT_FORM_MAX_PAGE_SIZE`
