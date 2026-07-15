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

import generate_blog_audiobooks as pipeline
from backend.blog_markdown import BlogMarkdownDocument, markdown_to_spoken_text


def _wav_bytes(*, sample_rate: int = 24000, frame_count: int = 24) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


def _doc(path: Path, slug: str = "sample-post", content: str = "# Heading\n\nBody copy.") -> BlogMarkdownDocument:
    return BlogMarkdownDocument(
        path=path,
        title="Sample Post",
        slug=slug,
        excerpt="Short excerpt",
        content=content,
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


def test_resolve_target_files_rejects_non_blog_file(tmp_path):
    blogs_dir = tmp_path / "blogs"
    blogs_dir.mkdir()
    outside_file = tmp_path / "outside.md"
    outside_file.write_text("# Outside", encoding="utf-8")

    try:
        pipeline.resolve_target_files(
            argparse.Namespace(file=str(outside_file), slug=None, all=False),
            blogs_dir=blogs_dir,
        )
    except pipeline.SelectionError as exc:
        assert "canonical blogs directory" in str(exc)
    else:
        raise AssertionError("Expected SelectionError for file outside the blogs directory.")


def test_build_spoken_text_uses_existing_markdown_normalization():
    content = (
        "# Title\n\n"
        "Paragraph with a [link](https://example.com).\n\n"
        "- bullet one\n"
        "- bullet two\n\n"
        "```python\nprint('hi')\n```"
    )
    document = _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md", content=content)

    spoken_text = pipeline.build_spoken_text(document)

    assert spoken_text == markdown_to_spoken_text(content)
    assert "Code example omitted." in spoken_text
    assert "Section: Title" in spoken_text


def test_build_chatterbox_command_includes_runtime_flags(tmp_path):
    command = pipeline.build_chatterbox_command(
        python_executable="python",
        module_name="scripts.chatterbox_tts_chunk",
        spoken_text_path=tmp_path / "spoken.txt",
        audio_path=tmp_path / "audiobook.wav",
        voice_path=tmp_path / "voice.wav",
        device="cuda",
        max_chars=256,
        chunk_dir=tmp_path / "chunks",
        resume=True,
        keep_chunks=True,
        high_priority=True,
        autocast=True,
        exaggeration=0.7,
        cfg_weight=0.6,
        temperature=0.9,
        top_p=0.8,
        min_p=0.02,
        repetition_penalty=1.3,
    )

    assert command[:3] == ["python", "-m", "scripts.chatterbox_tts_chunk"]
    assert "--voice" in command and str(tmp_path / "voice.wav") in command
    assert "--device" in command and "cuda" in command
    assert "--chunk-dir" in command and str(tmp_path / "chunks") in command
    assert "--resume" in command
    assert "--keep-chunks" in command
    assert "--high-priority" in command
    assert "--autocast" in command


def test_process_document_writes_failure_manifest_on_runner_error(tmp_path):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    document = _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md")

    result = pipeline.process_document(
        document,
        voice_path=voice_path,
        output_root=tmp_path,
        chunk_dir_root=None,
        force=False,
        dry_run=False,
        resume=False,
        keep_chunks=False,
        device=None,
        max_chars=300,
        high_priority=False,
        autocast=False,
        exaggeration=0.5,
        cfg_weight=0.5,
        temperature=0.8,
        top_p=1.0,
        min_p=0.05,
        repetition_penalty=1.2,
        runner=lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0],
            1,
            stdout="",
            stderr="synthesis boom",
        ),
    )

    manifest = json.loads((tmp_path / document.slug / "manifest.json").read_text(encoding="utf-8"))
    assert result.status == "failed"
    assert manifest["status"] == "failed"
    assert "synthesis boom" in manifest["error"]
    assert (tmp_path / document.slug / "spoken_text.txt").exists()


def test_process_document_writes_success_manifest_and_chunk_metadata(tmp_path):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    document = _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md")
    chunk_root = tmp_path / "chunk-cache"

    def fake_runner(command, capture_output, text, check):
        out_index = command.index("--out") + 1
        chunk_dir = Path(command[command.index("--chunk-dir") + 1])
        chunk_dir.mkdir(parents=True, exist_ok=True)
        (chunk_dir / "chunk_0001.wav").write_bytes(_wav_bytes(frame_count=4))
        Path(command[out_index]).write_bytes(_wav_bytes(sample_rate=16000, frame_count=8))
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    result = pipeline.process_document(
        document,
        voice_path=voice_path,
        output_root=tmp_path,
        chunk_dir_root=chunk_root,
        force=False,
        dry_run=False,
        resume=True,
        keep_chunks=True,
        device="cuda",
        max_chars=300,
        high_priority=True,
        autocast=True,
        exaggeration=0.9,
        cfg_weight=0.6,
        temperature=0.7,
        top_p=0.8,
        min_p=0.04,
        repetition_penalty=1.1,
        runner=fake_runner,
    )

    manifest = json.loads((tmp_path / document.slug / "manifest.json").read_text(encoding="utf-8"))
    assert result.status == "generated"
    assert manifest["status"] == "generated"
    assert manifest["audiobook"]["backend"] == "chatterbox"
    assert manifest["audiobook"]["sample_rate"] == 16000
    assert manifest["audiobook"]["duration_seconds"] == 0.001
    assert manifest["audiobook"]["chunk_count"] == 1
    assert manifest["audiobook"]["voice_reference"]["name"] == "voice.wav"
    assert manifest["files"]["audio"].endswith("audiobook.wav")
    assert manifest["files"]["spoken_text"].endswith("spoken_text.txt")
    assert manifest["files"]["chunks_dir"].endswith(document.slug)


def test_process_document_skips_existing_bundle_without_force(tmp_path):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    bundle_dir = tmp_path / "sample-post"
    bundle_dir.mkdir()
    (bundle_dir / "spoken_text.txt").write_text("spoken", encoding="utf-8")
    (bundle_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (bundle_dir / "audiobook.wav").write_bytes(_wav_bytes())

    result = pipeline.process_document(
        _doc(REPO_ROOT / "backend" / "blogs" / "sample-post.md"),
        voice_path=voice_path,
        output_root=tmp_path,
        chunk_dir_root=None,
        force=False,
        dry_run=False,
        resume=False,
        keep_chunks=False,
        device=None,
        max_chars=300,
        high_priority=False,
        autocast=False,
        exaggeration=0.5,
        cfg_weight=0.5,
        temperature=0.8,
        top_p=1.0,
        min_p=0.05,
        repetition_penalty=1.2,
    )

    assert result.status == "skipped"


def test_run_cli_dry_run_does_not_write_outputs(tmp_path, monkeypatch):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    path = tmp_path / "sample-post.md"
    path.write_text("# Sample", encoding="utf-8")
    document = _doc(path)

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: document)

    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--voice",
            str(voice_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--dry-run",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert "[dry-run] sample-post" in stdout.getvalue()
    assert not (tmp_path / "out").exists()


def test_run_cli_rejects_missing_voice(tmp_path):
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = pipeline.run_cli(
        [
            "--all",
            "--voice",
            str(tmp_path / "missing.wav"),
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert "Voice reference not found" in stderr.getvalue()
