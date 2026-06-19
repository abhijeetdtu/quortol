from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import wave
from io import BytesIO
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_blog_podcasts as pipeline
from backend.blog_markdown import BlogMarkdownDocument
from tts_backends import create_tts_backend


def _wav_bytes(*, sample_rate: int = 24000, frame_count: int = 24) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


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
            {"speaker": "journalist", "section": "intro", "text": "Hello there."},
            {"speaker": "author", "section": "discussion", "text": "Hi back."},
        ],
    }
    parsed = pipeline.validate_episode_payload(valid)
    assert parsed.episode_title == "Episode"
    assert [segment.speaker for segment in parsed.segments] == ["journalist", "author"]

    invalid = {
        "episode_title": "Episode",
        "episode_summary": "Summary",
        "segments": [
            {"speaker": "journalist", "section": "intro", "text": "Hello there."},
            {"speaker": "journalist", "section": "discussion", "text": "Still me."},
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
        "dialogue": (
            "JOURNALIST: First thought.\n"
            "AUTHOR: Second thought.\n"
            "JOURNALIST: Third thought.\n"
            "AUTHOR: Final thought."
        ),
    }

    parsed = pipeline.validate_episode_payload(payload)

    assert [segment.speaker for segment in parsed.segments] == [
        "journalist",
        "author",
        "journalist",
        "author",
    ]
    assert parsed.segments[0].section == "intro"
    assert parsed.segments[-1].section == "outro"


def test_validate_episode_payload_accepts_legacy_host_labels():
    payload = {
        "episode_title": "Episode",
        "dialogue": "HOST A: First thought.\nHOST B: Second thought.",
    }

    parsed = pipeline.validate_episode_payload(payload)

    assert [segment.speaker for segment in parsed.segments] == ["journalist", "author"]


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
                                    {"speaker": "journalist", "section": "intro", "text": "Hello."},
                                    {"speaker": "author", "section": "discussion", "text": "Hi."},
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
            pipeline.PodcastSegment("journalist", "intro", "One"),
            pipeline.PodcastSegment("author", "discussion", "Two"),
        ],
    )

    calls = []

    def synthesizer(text: str, voice: str, speed: float, lang: str):
        calls.append((voice, lang))
        return 10, [0.0, 0.25]

    tts_backend = create_tts_backend("kokoro", kokoro_synthesizer=synthesizer)
    episode_path, sample_rate = pipeline.merge_episode_audio(
        episode=episode,
        output_dir=tmp_path,
        voice_map={"journalist": "af_heart", "author": "am_fenrir"},
        keep_segments=False,
        tts_backend=tts_backend,
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
        journalist_voice="af_heart",
        author_voice="am_fenrir",
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


def test_resolve_voice_defaults_uses_qwen_defaults_when_not_explicit():
    journalist_voice, author_voice = pipeline.resolve_voice_defaults(
        argparse.Namespace(
            tts_backend="qwen",
            journalist_voice="af_heart",
            author_voice="am_fenrir",
        ),
        ["--slug", "sample-post", "--tts-backend", "qwen"],
    )

    assert journalist_voice == "Ryan"
    assert author_voice == "Aiden"


def test_resolve_voice_defaults_preserves_explicit_qwen_voices():
    journalist_voice, author_voice = pipeline.resolve_voice_defaults(
        argparse.Namespace(
            tts_backend="qwen",
            journalist_voice="CustomA",
            author_voice="CustomB",
        ),
        [
            "--slug",
            "sample-post",
            "--tts-backend",
            "qwen",
            "--journalist-voice",
            "CustomA",
            "--author-voice",
            "CustomB",
        ],
    )

    assert journalist_voice == "CustomA"
    assert author_voice == "CustomB"


def test_validate_voice_rejects_removed_voice_ids():
    tts_backend = create_tts_backend("kokoro")
    try:
        pipeline.validate_voice(tts_backend, "bf_omega")
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


def test_default_prompt_template_loads_successfully():
    template = pipeline.load_prompt_template(pipeline.DEFAULT_PROMPT_TEMPLATE)

    assert "{{SOURCE_MATERIAL}}" in template
    assert "{{PODCAST_TITLE}}" in template
    assert "{{WORD_COUNT}}" in template


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


def test_create_tts_backend_rejects_unknown_backend():
    try:
        create_tts_backend("made-up")
    except Exception as exc:
        assert "Unsupported TTS backend 'made-up'" in str(exc)
    else:
        raise AssertionError("Expected backend selection failure.")


def test_qwen_backend_builds_local_command_and_decodes_wav(tmp_path):
    calls = []
    output_bytes = _wav_bytes(sample_rate=16000, frame_count=8)

    def fake_runner(command, capture_output, text, check):
        calls.append((command, capture_output, text, check))
        out_index = command.index("--out") + 1
        Path(command[out_index]).write_bytes(output_bytes)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    backend = create_tts_backend(
        "qwen",
        tts_conda_env="qwen3-tts-cuda",
        tts_model="qwen3-tts",
        tts_language="English",
        tts_extra_args=["--device-map", "cuda:0"],
        tts_runner=fake_runner,
    )

    sample_rate, audio_data = backend.synthesize("Hello", "Ryan", 1.0, "journalist")

    assert sample_rate == 16000
    assert audio_data == b"\x00\x00" * 8
    command = calls[0][0]
    assert command[:7] == [
        "conda",
        "run",
        "--no-capture-output",
        "--name",
        "qwen3-tts-cuda",
        "python",
        "-m",
    ]
    assert command[7] == "scripts.qwen3_tts_chunk"
    assert "--speaker" in command and "Ryan" in command
    assert "--language" in command and "English" in command
    assert "--model" in command and "qwen3-tts" in command
    assert "--device-map" in command and "cuda:0" in command


def test_qwen_backend_rejects_non_default_speed():
    backend = create_tts_backend(
        "qwen",
        tts_runner=lambda *args, **kwargs: None,
    )

    try:
        backend.synthesize("Hello", "Ryan", 1.1, "journalist")
    except Exception as exc:
        assert "does not expose playback speed control" in str(exc)
    else:
        raise AssertionError("Expected unsupported speed failure.")


def test_qwen_backend_rejects_invalid_wav_payload():
    def fake_runner(command, capture_output, text, check):
        out_index = command.index("--out") + 1
        Path(command[out_index]).write_bytes(b"not-a-wav")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    backend = create_tts_backend(
        "qwen",
        tts_runner=fake_runner,
    )

    try:
        backend.synthesize("Hello", "voice-a", 1.0, "author")
    except Exception as exc:
        assert "valid WAV payload" in str(exc)
    else:
        raise AssertionError("Expected invalid WAV payload failure.")


def test_process_document_writes_tts_manifest_metadata(tmp_path):
    document = _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "episode_title": "Episode",
                                    "episode_summary": "Summary",
                                    "segments": [
                                        {
                                            "speaker": "journalist",
                                            "section": "intro",
                                            "text": "Hello there.",
                                        },
                                        {
                                            "speaker": "author",
                                            "section": "discussion",
                                            "text": "Hi back.",
                                        },
                                    ],
                                }
                            )
                        }
                    }
                ]
            }

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
        journalist_voice="af_heart",
        author_voice="am_fenrir",
        force=False,
        dry_run=False,
        keep_segments=False,
        requester=lambda *args, **kwargs: FakeResponse(),
        synthesizer=lambda *args, **kwargs: (24000, [0.0, 0.1]),
    )

    manifest = json.loads((tmp_path / document.slug / "manifest.json").read_text(encoding="utf-8"))
    assert result.status == "generated"
    assert manifest["episode"]["voices"] == {"journalist": "af_heart", "author": "am_fenrir"}
    assert manifest["episode"]["tts"]["backend"] == "kokoro"
    assert manifest["episode"]["tts"]["output_format"] == "wav"
    assert manifest["episode"]["tts"]["voices"] == {
        "journalist": "af_heart",
        "author": "am_fenrir",
    }
