import json
import wave
from pathlib import Path

from backend.features.podcast.repository import (
    clear_podcast_cache,
    get_podcast_episode,
    load_podcast_episodes,
    serialize_podcast_detail,
)


def _write_wav(path: Path, *, sample_rate: int = 24000, frame_count: int = 2400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)


def test_podcast_guid_is_stable_across_manifest_regeneration(tmp_path, monkeypatch):
    bundles_dir = tmp_path / "podcasts"
    bundle_dir = bundles_dir / "standalone-episode"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = bundle_dir / "manifest.json"
    (bundle_dir / "script.md").write_text("# Episode\n\nHOST A: Hello.", encoding="utf-8")
    _write_wav(bundle_dir / "episode.wav")

    base_manifest = {
        "status": "generated",
        "generated_at": "2026-06-20T09:00:00+00:00",
        "source": {
            "slug": "standalone-episode",
            "title": "Standalone Episode",
            "published_at": "2026-06-20T09:00:00+00:00",
        },
        "episode": {
            "episode_title": "Standalone Episode",
            "episode_summary": "A standalone Quortol audio release.",
        },
    }
    manifest_path.write_text(json.dumps(base_manifest), encoding="utf-8")

    monkeypatch.setenv("PODCASTS_DIR", str(bundles_dir))
    monkeypatch.setenv("PUBLIC_SITE_ORIGIN", "https://pokhi.in")

    clear_podcast_cache()
    first_guid = serialize_podcast_detail(get_podcast_episode("standalone-episode"))["guid"]

    updated_manifest = dict(base_manifest)
    updated_manifest["generated_at"] = "2026-07-01T00:00:00+00:00"
    manifest_path.write_text(json.dumps(updated_manifest), encoding="utf-8")

    clear_podcast_cache()
    second_guid = serialize_podcast_detail(get_podcast_episode("standalone-episode"))["guid"]

    assert first_guid == second_guid == "https://pokhi.in/podcasts/standalone-episode"


def test_repository_marks_existing_blog_slug_as_blog_source(tmp_path, monkeypatch):
    bundles_dir = tmp_path / "podcasts"
    bundle_dir = bundles_dir / "india-political-parties-evolution"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "manifest.json").write_text(
        json.dumps(
            {
                "status": "generated",
                "generated_at": "2026-06-15T22:19:43.998487+00:00",
                "source": {
                    "slug": "india-political-parties-evolution",
                    "title": "The Fractured Mandate",
                    "published_at": "2026-05-15T12:53:13.796148",
                },
                "episode": {
                    "episode_title": "The Fractured Mandate",
                    "episode_summary": "How India's political parties evolved across eras.",
                },
            }
        ),
        encoding="utf-8",
    )
    (bundle_dir / "script.md").write_text("# Episode\n\nHOST A: Hello.", encoding="utf-8")
    _write_wav(bundle_dir / "episode.wav")

    monkeypatch.setenv("PODCASTS_DIR", str(bundles_dir))
    monkeypatch.setenv("PUBLIC_SITE_ORIGIN", "https://pokhi.in")

    clear_podcast_cache()
    episodes = load_podcast_episodes()

    assert len(episodes) == 1
    assert episodes[0].source_type == "blog"
    assert episodes[0].related_blog_slug == "india-political-parties-evolution"
