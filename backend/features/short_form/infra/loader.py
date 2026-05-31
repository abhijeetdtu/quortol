"""Post loading and caching utilities for short-form content feed."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ..domain.models import Post
from .config import get_short_form_config


@lru_cache(maxsize=8)
def _load_posts_from_path(path: str) -> list[Post]:
    posts_path = Path(path)
    try:
        if not posts_path.exists():
            return []
        with posts_path.open("r", encoding="utf-8") as handle:
            raw_posts = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        return []

    posts: list[Post] = []
    for raw in raw_posts if isinstance(raw_posts, list) else []:
        if isinstance(raw, dict):
            posts.append(Post.from_dict(raw))

    return sorted(posts, key=lambda post: post.timestamp, reverse=True)


def load_posts() -> list[Post]:
    """Load posts from configured JSON source."""
    config = get_short_form_config()
    return _load_posts_from_path(str(config.posts_json_path.resolve()))


def clear_posts_cache() -> None:
    """Clear in-process post cache (useful in tests)."""
    _load_posts_from_path.cache_clear()


def get_post_by_id(post_id: str) -> Optional[Post]:
    for post in load_posts():
        if post.id == post_id:
            return post
    return None
