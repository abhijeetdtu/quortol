import json
import wave
from pathlib import Path

import pytest

from backend.app import create_app
from backend.features.podcast.repository import clear_podcast_cache, serialize_podcast_detail


def _write_wav(path: Path, *, sample_rate: int = 24000, frame_count: int = 2400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)


def _write_bundle(
    base_dir: Path,
    slug: str,
    manifest: dict,
    script_text: str = "# Episode\n\nJOURNALIST: Hello.",
) -> None:
    bundle_dir = base_dir / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (bundle_dir / "script.md").write_text(script_text, encoding="utf-8")
    _write_wav(bundle_dir / "episode.wav")


@pytest.fixture
def podcast_env(tmp_path, monkeypatch):
    bundles_dir = tmp_path / "podcasts"
    bundles_dir.mkdir(parents=True, exist_ok=True)

    _write_bundle(
        bundles_dir,
        "india-political-parties-evolution",
        {
            "status": "generated",
            "generated_at": "2026-06-15T22:19:43.998487+00:00",
            "source": {
                "slug": "india-political-parties-evolution",
                "title": "The Fractured Mandate",
                "published_at": "2026-05-15T12:53:13.796148",
                "updated_at": "2026-05-15T12:53:13.796148",
            },
            "episode": {
                "episode_title": "The Fractured Mandate",
                "episode_summary": "How India's political parties evolved across eras.",
            },
        },
    )

    _write_bundle(
        bundles_dir,
        "standalone-episode",
        {
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
        },
    )

    failed_dir = bundles_dir / "failed-episode"
    failed_dir.mkdir(parents=True, exist_ok=True)
    (failed_dir / "manifest.json").write_text(
        json.dumps({"status": "failed", "generated_at": "2026-06-20T10:00:00+00:00"}),
        encoding="utf-8",
    )
    (failed_dir / "script.md").write_text("# Failed", encoding="utf-8")
    _write_wav(failed_dir / "episode.wav")

    monkeypatch.setenv("PODCASTS_DIR", str(bundles_dir))
    monkeypatch.setenv("PUBLIC_SITE_ORIGIN", "https://pokhi.in")
    monkeypatch.setenv("DATABASE_URI", "sqlite:///:memory:")

    clear_podcast_cache()
    yield {"bundles_dir": bundles_dir}
    clear_podcast_cache()


@pytest.fixture
def client(podcast_env):
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_podcast_list_contract_filters_unpublished_bundles(client):
    response = client.get("/api/podcasts/")
    assert response.status_code == 200

    payload = response.get_json()
    assert "podcasts" in payload
    assert [episode["slug"] for episode in payload["podcasts"]] == [
        "standalone-episode",
        "india-political-parties-evolution",
    ]
    assert all(episode["slug"] != "failed-episode" for episode in payload["podcasts"])


def test_podcast_detail_contract_includes_transcript_and_blog_linkage(client):
    response = client.get("/api/podcasts/india-political-parties-evolution")
    assert response.status_code == 200

    payload = response.get_json()["podcast"]
    assert payload["slug"] == "india-political-parties-evolution"
    assert payload["source_type"] == "blog"
    assert payload["related_blog_slug"] == "india-political-parties-evolution"
    assert payload["tts_backend"] == "unknown"
    assert "transcript_markdown" in payload
    assert payload["audio_meta"]["content_length"] > 0


def test_podcast_detail_contract_exposes_explicit_tts_backend(client, podcast_env):
    qwen_manifest = {
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
            "tts": {
                "backend": "qwen",
                "model": "qwen3-tts",
                "output_format": "wav",
                "voices": {"journalist": "voice-a", "author": "voice-b"},
            },
        },
    }
    manifest_path = podcast_env["bundles_dir"] / "standalone-episode" / "manifest.json"
    manifest_path.write_text(json.dumps(qwen_manifest), encoding="utf-8")
    clear_podcast_cache()

    response = client.get("/api/podcasts/standalone-episode")
    assert response.status_code == 200
    payload = response.get_json()["podcast"]
    assert payload["tts_backend"] == "qwen"


def test_podcast_audio_route_streams_episode(client):
    response = client.get("/api/podcasts/standalone-episode/audio")
    assert response.status_code == 200
    assert response.mimetype in {"audio/wav", "audio/x-wav"}
    assert len(response.data) > 0


def test_podcast_rss_feed_contains_namespace_and_transcript_tag(client):
    response = client.get("/podcasts/rss.xml")
    assert response.status_code == 200

    xml_text = response.get_data(as_text=True)
    assert 'xmlns:podcast="https://podcastindex.org/namespace/1.0"' in xml_text
    assert "<podcast:medium>podcast</podcast:medium>" in xml_text
    assert "<podcast:guid>" in xml_text
    assert 'url="https://pokhi.in/podcasts/standalone-episode"' in xml_text
    assert 'type="text/html"' in xml_text
    assert "https://pokhi.in/api/podcasts/standalone-episode/audio" in xml_text
