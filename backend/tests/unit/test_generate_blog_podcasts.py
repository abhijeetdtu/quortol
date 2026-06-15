from __future__ import annotations

import argparse
import io
import json
import sys
import wave
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_blog_podcasts as pipeline
from backend.blog_markdown import BlogMarkdownDocument


def _doc(path: Path, slug: str = "sample-post") -> BlogMarkdownDocument:
    return BlogMarkdownDocument(
        path=path,
        title="Sample Post",
        slug=slug,
        excerpt="Short excerpt",
        content="# Heading\n\nBody copy.",
        tags=["news"],
        published_at=pipeline.datetime(2026, 1, 1),
        updated_at=pipeline.datetime(2026, 1, 2),
        has_explicit_published_at=True,
        has_explicit_updated_at=True,
    )


def test_resolve_target_files_supports_slug_file_and_all(tmp_path):
    blogs_dir = tmp_path / "blogs"
    series_dir = blogs_dir / "series"
    series_dir.mkdir(parents=True)
    file_a = blogs_dir / "alpha.md"
    file_b = series_dir / "beta.md"
    file_a.write_text("# Alpha", encoding="utf-8")
    file_b.write_text("# Beta", encoding="utf-8")

    by_file = pipeline.resolve_target_files(
        argparse.Namespace(file=str(file_a), slug=None, all=False),
        blogs_dir=blogs_dir,
    )
    by_slug = pipeline.resolve_target_files(
        argparse.Namespace(file=None, slug="beta", all=False),
        blogs_dir=blogs_dir,
    )
    all_files = pipeline.resolve_target_files(
        argparse.Namespace(file=None, slug=None, all=True),
        blogs_dir=blogs_dir,
    )

    assert by_file == [file_a.resolve()]
    assert by_slug == [file_b]
    assert all_files == [file_a, file_b]


def test_validate_episode_payload_accepts_valid_shape_and_rejects_repeated_speaker():
    valid = {
        "episode_title": "Episode",
        "episode_summary": "Summary",
        "segments": [
            {"speaker": "host_a", "section": "intro", "text": "Hello there."},
            {"speaker": "host_b", "section": "discussion", "text": "Hi back."},
        ],
    }
    parsed = pipeline.validate_episode_payload(valid)
    assert parsed.episode_title == "Episode"
    assert [segment.speaker for segment in parsed.segments] == ["host_a", "host_b"]

    invalid = {
        "episode_title": "Episode",
        "episode_summary": "Summary",
        "segments": [
            {"speaker": "host_a", "section": "intro", "text": "Hello there."},
            {"speaker": "host_a", "section": "discussion", "text": "Still me."},
        ],
    }

    try:
        pipeline.validate_episode_payload(invalid)
    except pipeline.LLMContractError as exc:
        assert "alternate speakers" in str(exc)
    else:
        raise AssertionError("Expected LLMContractError for repeated speaker.")


def test_validate_episode_payload_accepts_raw_dialogue_contract():
    payload = {
        "episode_title": "Episode",
        "dialogue": "HOST A: First thought.\nHOST B: Second thought.\nHOST A: Third thought.\nHOST B: Final thought.",
    }

    parsed = pipeline.validate_episode_payload(payload)

    assert [segment.speaker for segment in parsed.segments] == ["host_a", "host_b", "host_a", "host_b"]
    assert parsed.segments[0].section == "intro"
    assert parsed.segments[-1].section == "outro"


def test_request_episode_script_repairs_bad_first_response():
    responses = [
        {
            "choices": [
                {
                    "message": {
                        "content": '{"episode_title":"Bad","episode_summary":"x","segments":[{"speaker":"host_a","text":"one"},{"speaker":"host_a","text":"two"}]}'
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "episode_title": "Fixed",
                                "episode_summary": "All set",
                                "segments": [
                                    {"speaker": "host_a", "section": "intro", "text": "Hello."},
                                    {"speaker": "host_b", "section": "discussion", "text": "Hi."},
                                ],
                            }
                        )
                    }
                }
            ]
        },
    ]

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    calls = []

    def fake_requester(endpoint, json, timeout):
        calls.append((endpoint, json, timeout))
        return FakeResponse(responses[len(calls) - 1])

    episode = pipeline.request_episode_script(
        document=_doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md"),
        endpoint="http://127.0.0.1:8080/v1/chat/completions",
        model="",
        prompt_template=(
            "SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}\n\n"
            "PODCAST TITLE:\n{{PODCAST_TITLE}}\n\n"
            "TARGET LENGTH:\n{{WORD_COUNT}} words\n"
        ),
        requester=fake_requester,
    )

    assert episode.episode_title == "Fixed"
    assert len(calls) == 2


def test_merge_episode_audio_inserts_section_pause_and_writes_wav(tmp_path):
    episode = pipeline.EpisodeScript(
        episode_title="Episode",
        episode_summary="Summary",
        segments=[
            pipeline.PodcastSegment("host_a", "intro", "One"),
            pipeline.PodcastSegment("host_b", "discussion", "Two"),
        ],
    )

    calls = []

    def synthesizer(text: str, voice: str, speed: float, lang: str):
        calls.append((voice, lang))
        return 10, [0.0, 0.25]

    episode_path, sample_rate = pipeline.merge_episode_audio(
        episode=episode,
        output_dir=tmp_path,
        voice_map={"host_a": "af_heart", "host_b": "am_fenrir"},
        keep_segments=False,
        synthesizer=synthesizer,
    )

    assert sample_rate == 10
    assert calls == [("af_heart", "a"), ("am_fenrir", "a")]
    assert episode_path.exists()
    with wave.open(str(episode_path), "rb") as wav_file:
        assert wav_file.getframerate() == 10
        assert wav_file.getnframes() == 10


def test_process_document_writes_failure_manifest_on_error(tmp_path):
    document = _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md")

    result = pipeline.process_document(
        document,
        output_root=tmp_path,
        endpoint="http://127.0.0.1:8080/v1/chat/completions",
        model="",
        prompt_template=(
            "SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}\n\n"
            "PODCAST TITLE:\n{{PODCAST_TITLE}}\n\n"
            "TARGET LENGTH:\n{{WORD_COUNT}} words\n"
        ),
        host_a_voice="af_heart",
        host_b_voice="am_fenrir",
        force=False,
        dry_run=False,
        keep_segments=False,
        requester=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
        synthesizer=lambda *args, **kwargs: (24_000, [0.0]),
    )

    manifest = json.loads((tmp_path / document.slug / "manifest.json").read_text(encoding="utf-8"))
    assert result.status == "failed"
    assert manifest["status"] == "failed"
    assert manifest["error"] == "boom"


def test_run_cli_dry_run_does_not_write_outputs(tmp_path, monkeypatch):
    path = tmp_path / "sample-post.md"
    path.write_text("# Sample", encoding="utf-8")
    document = _doc(path)

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: document)
    monkeypatch.setattr(
        pipeline,
        "load_prompt_template",
        lambda current_path: (
            "SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}\n\n"
            "PODCAST TITLE:\n{{PODCAST_TITLE}}\n\n"
            "TARGET LENGTH:\n{{WORD_COUNT}} words\n"
        ),
    )

    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--output-dir",
            str(tmp_path / "out"),
            "--dry-run",
        ],
        stdout=stdout,
        stderr=stderr,
        requester=lambda *args, **kwargs: None,
        synthesizer=lambda *args, **kwargs: (24_000, [0.0]),
    )

    assert exit_code == 0
    assert "[dry-run] sample-post" in stdout.getvalue()
    assert not (tmp_path / "out").exists()


def test_validate_voice_rejects_removed_voice_ids():
    try:
        pipeline.validate_voice("bf_omega")
    except pipeline.SelectionError as exc:
        assert "Unsupported Kokoro voice 'bf_omega'" in str(exc)
    else:
        raise AssertionError("Expected SelectionError for removed voice id.")


def test_load_prompt_template_requires_placeholders(tmp_path):
    template_path = tmp_path / "prompt.md"
    template_path.write_text("SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}", encoding="utf-8")

    try:
        pipeline.load_prompt_template(template_path)
    except pipeline.PromptTemplateError as exc:
        assert "{{PODCAST_TITLE}}" in str(exc)
    else:
        raise AssertionError("Expected PromptTemplateError for missing placeholders.")


def test_build_generation_prompt_uses_external_template():
    prompt = pipeline.build_generation_prompt(
        _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md"),
        (
            "SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}\n\n"
            "PODCAST TITLE:\n{{PODCAST_TITLE}}\n\n"
            "TARGET LENGTH:\n{{WORD_COUNT}} words\n"
        ),
    )

    assert "PODCAST TITLE:\nSample Post" in prompt
    assert "SOURCE MATERIAL:" in prompt
    assert "Return JSON only with this exact shape:" in prompt
