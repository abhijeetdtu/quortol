"""Repository and serialization helpers for podcast episodes."""

from __future__ import annotations

import json
import wave
from contextlib import closing
from datetime import UTC, datetime
from email.utils import format_datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from backend.blog_markdown import BLOGS_DIR, BlogMarkdownDocument, iter_blog_markdown_files, parse_markdown_file

from .config import PodcastConfig, ensure_absolute_url, get_podcast_config
from .models import PodcastEpisode


def _parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None

    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None

    if parsed.tzinfo is not None:
        return parsed.astimezone(UTC).replace(tzinfo=None)
    return parsed


def _fallback_datetime(*values: datetime | None) -> datetime:
    for value in values:
        if value is not None:
            return value
    return datetime.utcnow()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _audio_duration_seconds(path: Path) -> float | None:
    try:
        with closing(wave.open(str(path), "rb")) as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
    except (OSError, wave.Error):
        return None

    if sample_rate <= 0:
        return None
    return round(frame_count / sample_rate, 3)


@lru_cache(maxsize=4)
def _load_blog_index(blogs_dir_str: str) -> dict[str, BlogMarkdownDocument]:
    blogs_dir = Path(blogs_dir_str)
    index: dict[str, BlogMarkdownDocument] = {}
    for markdown_file in iter_blog_markdown_files(blogs_dir=blogs_dir):
        try:
            document = parse_markdown_file(markdown_file, blogs_dir=blogs_dir)
        except OSError:
            continue
        index[document.slug] = document
    return index


def _episode_image_path(config: PodcastConfig) -> str:
    image_path = config.show_image_path.strip() or "/quortol-podcast-cover.svg"
    return image_path if image_path.startswith("/") else f"/{image_path}"


@lru_cache(maxsize=4)
def _load_episodes_from_path(bundles_dir_str: str, blogs_dir_str: str) -> tuple[PodcastEpisode, ...]:
    bundles_dir = Path(bundles_dir_str)
    blog_index = _load_blog_index(blogs_dir_str)

    episodes: list[PodcastEpisode] = []
    if not bundles_dir.exists():
        return tuple()

    for bundle_dir in sorted((path for path in bundles_dir.iterdir() if path.is_dir()), key=lambda path: path.name):
        manifest_path = bundle_dir / "manifest.json"
        script_path = bundle_dir / "script.md"
        audio_path = bundle_dir / "episode.wav"
        if not manifest_path.is_file() or not script_path.is_file() or not audio_path.is_file():
            continue

        manifest = _read_json(manifest_path)
        if not manifest or manifest.get("status") != "generated":
            continue

        slug = bundle_dir.name
        source = manifest.get("source") if isinstance(manifest.get("source"), dict) else {}
        episode_meta = manifest.get("episode") if isinstance(manifest.get("episode"), dict) else {}
        blog_document = blog_index.get(slug)

        generated_at = _parse_datetime(manifest.get("generated_at"))
        manifest_published_at = _parse_datetime(source.get("published_at"))
        published_at = _fallback_datetime(
            blog_document.published_at if blog_document else None,
            manifest_published_at,
            generated_at,
            datetime.fromtimestamp(audio_path.stat().st_mtime, tz=UTC).replace(tzinfo=None),
        )

        title = (
            str(episode_meta.get("episode_title") or "").strip()
            or str(source.get("title") or "").strip()
            or slug.replace("-", " ").title()
        )
        summary = str(episode_meta.get("episode_summary") or "").strip()
        transcript_markdown = _read_text(script_path)
        audio_bytes = audio_path.stat().st_size
        duration_seconds = _audio_duration_seconds(audio_path)
        source_type = "blog" if blog_document else "standalone"

        episodes.append(
            PodcastEpisode(
                slug=slug,
                title=title,
                summary=summary,
                published_at=published_at,
                generated_at=generated_at,
                source_type=source_type,
                transcript_markdown=transcript_markdown,
                audio_path=audio_path,
                script_path=script_path,
                manifest_path=manifest_path,
                manifest=manifest,
                related_blog_slug=blog_document.slug if blog_document else None,
                related_blog_title=blog_document.title if blog_document else None,
                audio_bytes=audio_bytes,
                audio_mimetype="audio/wav",
                duration_seconds=duration_seconds,
                image_path="/quortol-podcast-cover.svg",
            )
        )

    return tuple(sorted(episodes, key=lambda episode: episode.published_at, reverse=True))


def clear_podcast_cache() -> None:
    _load_blog_index.cache_clear()
    _load_episodes_from_path.cache_clear()


def load_podcast_episodes() -> list[PodcastEpisode]:
    config = get_podcast_config()
    episodes = _load_episodes_from_path(
        str(config.bundles_dir.resolve()),
        str(BLOGS_DIR.resolve()),
    )
    return list(episodes)


def get_podcast_episode(slug: str) -> PodcastEpisode | None:
    for episode in load_podcast_episodes():
        if episode.slug == slug:
            return episode
    return None


def episode_relative_url(episode: PodcastEpisode) -> str:
    return f"/podcasts/{episode.slug}"


def episode_audio_relative_url(episode: PodcastEpisode) -> str:
    return f"/api/podcasts/{episode.slug}/audio"


def episode_canonical_url(episode: PodcastEpisode, config: PodcastConfig) -> str:
    return ensure_absolute_url(config.canonical_origin, episode_relative_url(episode))


def episode_audio_canonical_url(episode: PodcastEpisode, config: PodcastConfig) -> str:
    return ensure_absolute_url(config.canonical_origin, episode_audio_relative_url(episode))


def episode_feed_guid(episode: PodcastEpisode, config: PodcastConfig) -> str:
    return episode_canonical_url(episode, config)


def channel_guid(config: PodcastConfig) -> str:
    return str(uuid5(NAMESPACE_URL, config.feed_url))


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def serialize_podcast_summary(
    episode: PodcastEpisode,
    config: PodcastConfig | None = None,
) -> dict[str, Any]:
    active_config = config or get_podcast_config()
    return {
        "slug": episode.slug,
        "title": episode.title,
        "summary": episode.summary,
        "published_at": episode.published_at.isoformat(),
        "generated_at": _iso_or_none(episode.generated_at),
        "audio_url": episode_audio_relative_url(episode),
        "source_type": episode.source_type,
        "related_blog_slug": episode.related_blog_slug,
        "related_blog_title": episode.related_blog_title,
        "image_url": _episode_image_path(active_config),
        "detail_url": episode_relative_url(episode),
        "guid": episode_feed_guid(episode, active_config),
    }


def serialize_podcast_detail(
    episode: PodcastEpisode,
    config: PodcastConfig | None = None,
) -> dict[str, Any]:
    active_config = config or get_podcast_config()
    payload = serialize_podcast_summary(episode, config=active_config)
    payload.update(
        {
            "transcript_markdown": episode.transcript_markdown,
            "transcript_url": episode_relative_url(episode),
            "manifest": episode.manifest,
            "audio_meta": {
                "content_type": episode.audio_mimetype,
                "content_length": episode.audio_bytes,
                "duration_seconds": episode.duration_seconds,
            },
            "asset_flags": {
                "has_manifest": True,
                "has_audio": True,
                "has_script": True,
            },
        }
    )
    return payload


def serialize_podcast_for_export(
    episode: PodcastEpisode,
    config: PodcastConfig | None = None,
) -> dict[str, Any]:
    active_config = config or get_podcast_config()
    payload = serialize_podcast_detail(episode, config=active_config)
    payload.update(
        {
            "canonical_url": episode_canonical_url(episode, active_config),
            "absolute_audio_url": episode_audio_canonical_url(episode, active_config),
        }
    )
    return payload


def rfc2822_datetime(value: datetime) -> str:
    aware_value = value.replace(tzinfo=UTC)
    return format_datetime(aware_value)
