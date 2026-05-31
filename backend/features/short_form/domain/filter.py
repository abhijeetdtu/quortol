"""Filtering and pagination utilities for short-form content feed."""

from __future__ import annotations

from .models import Post


def filter_posts(
    posts: list[Post], tags: list[str] | None = None, keyword: str | None = None
) -> list[Post]:
    filtered = posts

    if tags:
        normalized_tags = [tag for tag in tags if tag]
        filtered = [post for post in filtered if all(tag in post.tags for tag in normalized_tags)]

    if keyword:
        keyword_lower = keyword.lower()
        filtered = [
            post
            for post in filtered
            if keyword_lower in (post.text or "").lower()
            or any(keyword_lower in tag.lower() for tag in post.tags)
        ]

    return filtered


def paginate_posts(posts: list[Post], page: int, limit: int) -> tuple[list[Post], dict]:
    safe_page = max(1, page)
    safe_limit = max(1, limit)

    total_posts = len(posts)
    total_pages = (total_posts + safe_limit - 1) // safe_limit if total_posts > 0 else 0

    start_idx = (safe_page - 1) * safe_limit
    end_idx = start_idx + safe_limit

    return posts[start_idx:end_idx], {
        "current_page": safe_page,
        "total_pages": total_pages,
        "total_posts": total_posts,
        "posts_per_page": safe_limit,
    }
