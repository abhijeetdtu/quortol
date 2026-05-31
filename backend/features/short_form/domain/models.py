"""Post data model for short-form content feed."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


class Post:
    """Represents a single piece of short-form content."""

    def __init__(
        self,
        id: str | None = None,
        text: str | None = None,
        media_url: str | None = None,
        video_url: str | None = None,
        author: str = "",
        timestamp: datetime | None = None,
        tags: list[str] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.media_url = media_url
        self.video_url = video_url
        self.author = author
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or []
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "media_url": self.media_url,
            "video_url": self.video_url,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Post":
        return Post(
            id=data.get("id"),
            text=data.get("text"),
            media_url=data.get("media_url"),
            video_url=data.get("video_url"),
            author=data.get("author", ""),
            timestamp=_parse_iso_datetime(data.get("timestamp")),
            tags=list(data.get("tags") or []),
            created_at=_parse_iso_datetime(data.get("created_at")),
        )

    def validate(self) -> tuple[bool, str]:
        if not self.text and not self.media_url and not self.video_url:
            return False, "Post must have text, media, or video"
        if not self.tags:
            return False, "Post must have at least one tag"
        for tag in self.tags:
            if not str(tag).startswith("#"):
                return False, f"Tag '{tag}' must start with #"
        return True, ""
