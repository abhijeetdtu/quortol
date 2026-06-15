"""Domain models for public podcast serving."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PodcastEpisode:
    slug: str
    title: str
    summary: str
    published_at: datetime
    generated_at: datetime | None
    source_type: str
    transcript_markdown: str
    audio_path: Path
    script_path: Path
    manifest_path: Path
    manifest: dict[str, Any]
    related_blog_slug: str | None
    related_blog_title: str | None
    audio_bytes: int
    audio_mimetype: str
    duration_seconds: float | None
    image_path: str
