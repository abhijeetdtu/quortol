"""Configuration for public podcast serving."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_BUNDLES_DIR = Path(__file__).resolve().parents[2] / "static" / "podcasts"
DEFAULT_SITE_ORIGIN = "https://quortol.pokhi.in"
DEFAULT_SHOW_TITLE = "Quortol Podcast"
DEFAULT_SHOW_DESCRIPTION = (
    "Listen to Quortol podcast episodes adapted from essays and original conversations."
)
DEFAULT_SHOW_LANGUAGE = "en-us"
DEFAULT_SHOW_IMAGE_PATH = "/quortol-podcast-cover.svg"
DEFAULT_SHOW_LINK_PATH = "/podcasts"
DEFAULT_FEED_PATH = "/podcasts/rss.xml"


@dataclass(frozen=True)
class PodcastConfig:
    bundles_dir: Path
    canonical_origin: str
    show_title: str
    show_description: str
    show_language: str
    show_image_path: str
    show_link_path: str
    feed_path: str

    @property
    def feed_url(self) -> str:
        return ensure_absolute_url(self.canonical_origin, self.feed_path)

    @property
    def show_url(self) -> str:
        return ensure_absolute_url(self.canonical_origin, self.show_link_path)

    @property
    def show_image_url(self) -> str:
        return ensure_absolute_url(self.canonical_origin, self.show_image_path)


def ensure_absolute_url(origin: str, value: str) -> str:
    normalized_origin = (origin or DEFAULT_SITE_ORIGIN).rstrip("/")
    if not value:
        return normalized_origin
    if value.startswith("http://") or value.startswith("https://"):
        return value
    normalized_path = value if value.startswith("/") else f"/{value}"
    return f"{normalized_origin}{normalized_path}"


def get_podcast_config() -> PodcastConfig:
    return PodcastConfig(
        bundles_dir=Path(os.environ.get("PODCASTS_DIR", str(DEFAULT_BUNDLES_DIR))).expanduser(),
        canonical_origin=os.environ.get("PUBLIC_SITE_ORIGIN", DEFAULT_SITE_ORIGIN).rstrip("/"),
        show_title=os.environ.get("PODCAST_SHOW_TITLE", DEFAULT_SHOW_TITLE).strip(),
        show_description=os.environ.get("PODCAST_SHOW_DESCRIPTION", DEFAULT_SHOW_DESCRIPTION).strip(),
        show_language=os.environ.get("PODCAST_SHOW_LANGUAGE", DEFAULT_SHOW_LANGUAGE).strip(),
        show_image_path=os.environ.get("PODCAST_SHOW_IMAGE_PATH", DEFAULT_SHOW_IMAGE_PATH).strip(),
        show_link_path=os.environ.get("PODCAST_SHOW_LINK_PATH", DEFAULT_SHOW_LINK_PATH).strip(),
        feed_path=os.environ.get("PODCAST_FEED_PATH", DEFAULT_FEED_PATH).strip(),
    )
