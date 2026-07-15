from __future__ import annotations

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
from backend.blog_markdown import BlogMarkdownDocument


def _wav_bytes(*, sample_rate: int = 24000, frame_count: int = 24) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


def _doc(path: Path, slug: str, title: str, content: str | None = None) -> BlogMarkdownDocument:
    return BlogMarkdownDocument(
        path=path,
        title=title,
        slug=slug,
        excerpt=f"{title} excerpt",
        content=content or f"# {title}\n\nSome content for {title}.",
        tags=["tag"],
        published_at=pipeline.datetime(2026, 1, 1),
        updated_at=pipeline.datetime(2026, 1, 1),
        has_explicit_published_at=True,
        has_explicit_updated_at=True,
    )


def test_run_cli_generates_one_bundle_and_continues_after_failure(tmp_path, monkeypatch):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    path_a = tmp_path / "alpha.md"
    path_b = tmp_path / "beta.md"
    path_a.write_text("# Alpha", encoding="utf-8")
    path_b.write_text("# Beta", encoding="utf-8")
    documents = {
        path_a: _doc(path_a, "alpha", "Alpha"),
        path_b: _doc(path_b, "beta", "Beta"),
    }

    def fake_runner(command, capture_output, text, check):
        spoken_path = Path(command[command.index("--text-file") + 1])
        out_path = Path(command[command.index("--out") + 1])
        if spoken_path.parent.name == "alpha":
            out_path.write_bytes(_wav_bytes())
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="model offline")

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path_a, path_b])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: documents[current_path])

    stdout = io.StringIO()
    stderr = io.StringIO()
    output_dir = tmp_path / "out"
    exit_code = pipeline.run_cli(
        ["--all", "--voice", str(voice_path), "--output-dir", str(output_dir)],
        stdout=stdout,
        stderr=stderr,
        runner=fake_runner,
    )

    assert exit_code == 1
    assert (output_dir / "alpha" / "audiobook.wav").exists()
    assert (output_dir / "alpha" / "spoken_text.txt").exists()
    assert (output_dir / "beta" / "manifest.json").exists()
    failed_manifest = json.loads((output_dir / "beta" / "manifest.json").read_text(encoding="utf-8"))
    assert failed_manifest["status"] == "failed"
    assert "[generated] alpha" in stdout.getvalue()
    assert "[failed] beta" in stdout.getvalue()


def test_run_cli_forwards_resume_and_chunk_retention(tmp_path, monkeypatch):
    voice_path = tmp_path / "voice.wav"
    voice_path.write_bytes(b"voice")
    path = tmp_path / "sample.md"
    path.write_text("# Sample", encoding="utf-8")
    document = _doc(path, "sample", "Sample")
    captured_commands: list[list[str]] = []

    def fake_runner(command, capture_output, text, check):
        captured_commands.append(command)
        chunk_dir = Path(command[command.index("--chunk-dir") + 1])
        chunk_dir.mkdir(parents=True, exist_ok=True)
        (chunk_dir / "chunk_0001.wav").write_bytes(_wav_bytes(frame_count=4))
        out_path = Path(command[command.index("--out") + 1])
        out_path.write_bytes(_wav_bytes())
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: document)

    output_dir = tmp_path / "out"
    chunk_dir_root = tmp_path / "chunks"
    exit_code = pipeline.run_cli(
        [
            "--file",
            str(path),
            "--voice",
            str(voice_path),
            "--output-dir",
            str(output_dir),
            "--chunk-dir",
            str(chunk_dir_root),
            "--resume",
            "--keep-chunks",
        ],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        runner=fake_runner,
    )

    assert exit_code == 0
    assert len(captured_commands) == 1
    command = captured_commands[0]
    assert "--resume" in command
    assert "--keep-chunks" in command
    chunk_dir = Path(command[command.index("--chunk-dir") + 1])
    assert chunk_dir == chunk_dir_root / "sample"
    manifest = json.loads((output_dir / "sample" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["audiobook"]["chunk_count"] == 1
