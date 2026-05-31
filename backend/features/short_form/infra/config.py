"""Configuration management for short-form content feed."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ShortFormConfig:
    posts_json_path: Path
    media_dir: Path
    images_dir: Path
    videos_dir: Path
    media_url_prefix: str
    default_page_size: int
    max_page_size: int


BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _ensure_leading_slash(value: str) -> str:
    return value if value.startswith("/") else f"/{value}"


def get_short_form_config() -> ShortFormConfig:
    """Build runtime config from environment with backend-owned defaults."""
    posts_json_default = BACKEND_ROOT / "data" / "short_form" / "posts.json"
    media_dir_default = BACKEND_ROOT / "static" / "short_form"

    posts_json_path = Path(
        os.getenv("SHORT_FORM_POSTS_JSON", str(posts_json_default))
    )
    media_dir = Path(os.getenv("SHORT_FORM_MEDIA_DIR", str(media_dir_default)))

    prefix = os.getenv("SHORT_FORM_MEDIA_URL_PREFIX", "/static/short_form/")
    prefix = _ensure_leading_slash(prefix)
    if not prefix.endswith("/"):
        prefix = f"{prefix}/"

    return ShortFormConfig(
        posts_json_path=posts_json_path,
        media_dir=media_dir,
        images_dir=media_dir / "images",
        videos_dir=media_dir / "videos",
        media_url_prefix=prefix,
        default_page_size=int(os.getenv("SHORT_FORM_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("SHORT_FORM_MAX_PAGE_SIZE", "100")),
    )
