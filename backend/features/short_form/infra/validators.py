"""Media validation utilities for short-form content feed."""

from __future__ import annotations

from pathlib import Path

from .config import get_short_form_config


ALLOWED_MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4"}


def _resolve_media_path(media_url: str) -> Path | None:
    config = get_short_form_config()
    if not media_url:
        return None

    if not media_url.startswith(config.media_url_prefix):
        return None

    relative = media_url[len(config.media_url_prefix) :].lstrip("/")
    resolved = (config.media_dir / relative).resolve()

    # Prevent path traversal outside backend/static/short_form
    media_root = config.media_dir.resolve()
    if media_root not in resolved.parents and resolved != media_root:
        return None

    return resolved


def validate_media_url(media_url: str) -> tuple[bool, str]:
    if not media_url:
        return True, ""

    resolved = _resolve_media_path(media_url)
    if resolved is None:
        return False, f"Media URL is not allowed: {media_url}"

    if resolved.suffix.lower() not in ALLOWED_MEDIA_EXTENSIONS:
        return False, f"Unsupported media extension: {resolved.suffix}"

    if not resolved.exists():
        return False, f"Media file not found: {resolved}"

    return True, ""


def validate_video_duration(video_url: str) -> tuple[bool, str]:
    # V1 keeps existence/type validation only.
    valid, message = validate_media_url(video_url)
    if not valid:
        return valid, message

    resolved = _resolve_media_path(video_url)
    if resolved is None or resolved.suffix.lower() != ".mp4":
        return False, "Video URL must point to an .mp4 file"

    return True, ""


def validate_post_media(post) -> tuple[bool, str]:
    if post.media_url:
        valid, message = validate_media_url(post.media_url)
        if not valid:
            return False, message

    if post.video_url:
        valid, message = validate_video_duration(post.video_url)
        if not valid:
            return False, message

    return True, ""
