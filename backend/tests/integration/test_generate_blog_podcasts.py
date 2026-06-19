from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from io import BytesIO
import wave


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_blog_podcasts as pipeline
from backend.blog_markdown import BlogMarkdownDocument


def _wav_bytes(*, sample_rate: int = 24000, frame_count: int = 24) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


def _doc(path: Path, slug: str, title: str) -> BlogMarkdownDocument:
    return BlogMarkdownDocument(
        path=path,
        title=title,
        slug=slug,
        excerpt=f"{title} excerpt",
        content=f"# {title}\n\nSome content for {title}.",
        tags=["tag"],
        published_at=pipeline.datetime(2026, 1, 1),
        updated_at=pipeline.datetime(2026, 1, 1),
        has_explicit_published_at=True,
        has_explicit_updated_at=True,
    )


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_run_cli_generates_one_bundle_and_continues_after_failure(tmp_path, monkeypatch):
    path_a = tmp_path / "alpha.md"
    path_b = tmp_path / "beta.md"
    path_a.write_text("# Alpha", encoding="utf-8")
    path_b.write_text("# Beta", encoding="utf-8")
    documents = {
        path_a: _doc(path_a, "alpha", "Alpha"),
        path_b: _doc(path_b, "beta", "Beta"),
    }

    success_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "episode_title": "Alpha Episode",
                            "episode_summary": "Summary",
                            "segments": [
                                {"speaker": "journalist", "section": "intro", "text": "Intro."},
                                {"speaker": "author", "section": "discussion", "text": "Response."},
                            ],
                        }
                    )
                }
            }
        ]
    }

    def fake_requester(endpoint, json, timeout):
        prompt = json["messages"][1]["content"]
        if "title: Alpha" in prompt:
            return FakeResponse(success_payload)
        raise RuntimeError("llm offline")

    def fake_synthesizer(text: str, voice: str, speed: float, lang: str):
        return 24_000, [0.0, 0.1, -0.1]

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path_a, path_b])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: documents[current_path])
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
    output_dir = tmp_path / "out"
    exit_code = pipeline.run_cli(
        ["--all", "--output-dir", str(output_dir)],
        stdout=stdout,
        stderr=stderr,
        requester=fake_requester,
        synthesizer=fake_synthesizer,
    )

    assert exit_code == 1
    assert (output_dir / "alpha" / "episode.wav").exists()
    assert (output_dir / "alpha" / "script.md").exists()
    assert (output_dir / "beta" / "manifest.json").exists()
    failed_manifest = json.loads((output_dir / "beta" / "manifest.json").read_text(encoding="utf-8"))
    assert failed_manifest["status"] == "failed"
    assert "[generated] alpha" in stdout.getvalue()
    assert "[failed] beta" in stdout.getvalue()


def test_run_cli_qwen_force_regenerates_bundle_and_updates_manifest(tmp_path, monkeypatch):
    path = tmp_path / "ipl-slogfest-transformation.md"
    path.write_text("# IPL", encoding="utf-8")
    document = _doc(path, "ipl-slogfest-transformation", "IPL Slogfest")
    output_dir = tmp_path / "out"

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

    llm_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "episode_title": "IPL Episode",
                            "episode_summary": "Summary",
                            "segments": [
                                {"speaker": "journalist", "section": "intro", "text": "Intro."},
                                {"speaker": "author", "section": "discussion", "text": "Reply."},
                            ],
                        }
                    )
                }
            }
        ]
    }

    class FakeLLMResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return llm_payload

    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--output-dir",
            str(output_dir),
        ],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        requester=lambda *args, **kwargs: FakeLLMResponse(),
        synthesizer=lambda *args, **kwargs: (24000, [0.0, 0.1]),
    )

    assert exit_code == 0
    kokoro_manifest = json.loads(
        (output_dir / "ipl-slogfest-transformation" / "manifest.json").read_text(encoding="utf-8")
    )
    assert kokoro_manifest["episode"]["tts"]["backend"] == "kokoro"

    qwen_stderr = io.StringIO()
    def successful_qwen_runner(command, capture_output, text, check):
        Path(command[command.index("--out") + 1]).write_bytes(_wav_bytes())
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--output-dir",
            str(output_dir),
            "--tts-backend",
            "qwen",
            "--tts-conda-env",
            "qwen3-tts-cuda",
            "--tts-model",
            "qwen3-tts",
            "--tts-language",
            "English",
            "--force",
        ],
        stdout=io.StringIO(),
        stderr=qwen_stderr,
        requester=lambda *args, **kwargs: FakeLLMResponse(),
        tts_runner=successful_qwen_runner,
    )

    assert exit_code == 0, qwen_stderr.getvalue()
    qwen_manifest = json.loads(
        (output_dir / "ipl-slogfest-transformation" / "manifest.json").read_text(encoding="utf-8")
    )
    assert (output_dir / "ipl-slogfest-transformation" / "episode.wav").exists()
    assert (output_dir / "ipl-slogfest-transformation" / "script.md").exists()
    assert qwen_manifest["episode"]["tts"]["backend"] == "qwen"
    assert qwen_manifest["episode"]["tts"]["model"] == "qwen3-tts"
    assert qwen_manifest["episode"]["tts"]["conda_env"] == "qwen3-tts-cuda"
    assert qwen_manifest["episode"]["tts"]["voices"] == {
        "journalist": "Ryan",
        "author": "Aiden",
    }


def test_run_cli_qwen_failure_writes_failure_manifest(tmp_path, monkeypatch):
    path = tmp_path / "ipl-slogfest-transformation.md"
    path.write_text("# IPL", encoding="utf-8")
    document = _doc(path, "ipl-slogfest-transformation", "IPL Slogfest")
    output_dir = tmp_path / "out"

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

    class FakeLLMResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "episode_title": "IPL Episode",
                                    "episode_summary": "Summary",
                                    "segments": [
                                        {"speaker": "journalist", "section": "intro", "text": "Intro."},
                                        {"speaker": "author", "section": "discussion", "text": "Reply."},
                                    ],
                                }
                            )
                        }
                    }
                ]
            }

    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--output-dir",
            str(output_dir),
            "--tts-backend",
            "qwen",
            "--tts-conda-env",
            "qwen3-tts-cuda",
        ],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        requester=lambda *args, **kwargs: FakeLLMResponse(),
        tts_runner=lambda command, capture_output, text, check: (
            Path(command[command.index("--out") + 1]).write_bytes(b"bad-wav"),
            subprocess.CompletedProcess(command, 0, stdout="ok", stderr=""),
        )[1],
    )

    assert exit_code == 1
    manifest = json.loads(
        (output_dir / "ipl-slogfest-transformation" / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "failed"
    assert "valid WAV payload" in manifest["error"]
