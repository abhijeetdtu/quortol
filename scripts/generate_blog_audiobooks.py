"""Generate single-narrator audiobook artifacts from blog markdown files."""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import wave
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.blog_markdown import (  # noqa: E402
    BLOGS_DIR,
    BlogMarkdownDocument,
    default_slug_for_path,
    iter_blog_markdown_files,
    markdown_to_spoken_text,
    parse_markdown_file,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "backend" / "static" / "audiobooks"
DEFAULT_AUDIOBOOK_MODULE = "scripts.chatterbox_tts_chunk"


class AudiobookGenerationError(Exception):
    """Base error for audiobook generation failures."""


class SelectionError(AudiobookGenerationError):
    """Raised when CLI selection is invalid."""


@dataclass(frozen=True)
class ProcessResult:
    slug: str
    status: str
    source_path: str
    output_dir: str
    message: str = ""
    spoken_text_path: str = ""
    manifest_path: str = ""
    audio_path: str = ""
    chunk_count: int = 0


Runner = Callable[..., subprocess.CompletedProcess[str]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate-blog-audiobooks",
        description="Generate audiobook WAV bundles from blog markdown files.",
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--slug", help="Generate artifacts for one blog slug.")
    selection.add_argument("--file", help="Generate artifacts for one markdown file.")
    selection.add_argument(
        "--all",
        action="store_true",
        help="Generate artifacts for every blog markdown file.",
    )
    parser.add_argument(
        "--voice",
        type=Path,
        required=True,
        help="Reference WAV/MP3 file used for Chatterbox voice cloning.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output root for generated audiobook bundles. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--chunk-dir",
        type=Path,
        default=None,
        help="Optional root directory for per-blog chunk caches.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate outputs even when an audiobook bundle already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended work without writing any output files.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume synthesis from any previously cached chunks.",
    )
    parser.add_argument(
        "--keep-chunks",
        action="store_true",
        help="Keep per-chunk WAV files under the bundle or the explicit chunk root.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Target device passed through to Chatterbox (cuda, mps, cpu).",
    )
    parser.add_argument("--max-chars", type=int, default=300)
    parser.add_argument("--high-priority", action="store_true")
    parser.add_argument("--autocast", action="store_true")
    parser.add_argument("--exaggeration", type=float, default=0.5)
    parser.add_argument("--cfg-weight", type=float, default=0.5)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--min-p", type=float, default=0.05)
    parser.add_argument("--repetition-penalty", type=float, default=1.2)
    return parser


def resolve_target_files(args: argparse.Namespace, blogs_dir: Path = BLOGS_DIR) -> list[Path]:
    if args.file:
        path = Path(args.file).expanduser().resolve()
        if not path.is_file():
            raise SelectionError(f"Markdown file not found: {path}")
        try:
            path.relative_to(blogs_dir.resolve())
        except ValueError as exc:
            raise SelectionError(
                f"Markdown file must live under the canonical blogs directory: {blogs_dir}"
            ) from exc
        return [path]

    markdown_files = iter_blog_markdown_files(blogs_dir=blogs_dir)
    if args.all:
        return markdown_files

    assert args.slug
    for path in markdown_files:
        slug = default_slug_for_path(path, blogs_dir=blogs_dir)
        if slug == args.slug:
            return [path]
        if parse_markdown_file(path, blogs_dir=blogs_dir).slug == args.slug:
            return [path]
    raise SelectionError(f"Blog slug not found: {args.slug}")


def build_spoken_text(document: BlogMarkdownDocument) -> str:
    spoken_text = markdown_to_spoken_text(document.content).strip()
    if not spoken_text:
        raise AudiobookGenerationError("The blog did not produce any spoken-text content.")
    return spoken_text


def bundle_has_existing_outputs(output_dir: Path) -> bool:
    return (
        (output_dir / "audiobook.wav").exists()
        and (output_dir / "spoken_text.txt").exists()
        and (output_dir / "manifest.json").exists()
    )


def write_manifest(output_dir: Path, manifest: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def resolve_chunk_dir(
    *,
    output_dir: Path,
    chunk_dir_root: Path | None,
    keep_chunks: bool,
    resume: bool,
) -> Path | None:
    if chunk_dir_root is not None:
        return chunk_dir_root / output_dir.name
    if keep_chunks or resume:
        return output_dir / "chunks"
    return None


def build_chatterbox_command(
    *,
    python_executable: str,
    module_name: str,
    spoken_text_path: Path,
    audio_path: Path,
    voice_path: Path,
    device: str | None,
    max_chars: int,
    chunk_dir: Path | None,
    resume: bool,
    keep_chunks: bool,
    high_priority: bool,
    autocast: bool,
    exaggeration: float,
    cfg_weight: float,
    temperature: float,
    top_p: float,
    min_p: float,
    repetition_penalty: float,
) -> list[str]:
    command = [
        python_executable,
        "-m",
        module_name,
        "--text-file",
        str(spoken_text_path),
        "--out",
        str(audio_path),
        "--voice",
        str(voice_path),
        "--max-chars",
        str(max_chars),
        "--exaggeration",
        str(exaggeration),
        "--cfg-weight",
        str(cfg_weight),
        "--temperature",
        str(temperature),
        "--top-p",
        str(top_p),
        "--min-p",
        str(min_p),
        "--repetition-penalty",
        str(repetition_penalty),
    ]
    if device:
        command.extend(["--device", device])
    if chunk_dir is not None:
        command.extend(["--chunk-dir", str(chunk_dir)])
    if resume:
        command.append("--resume")
    if keep_chunks:
        command.append("--keep-chunks")
    if high_priority:
        command.append("--high-priority")
    if autocast:
        command.append("--autocast")
    return command


def read_audio_metadata(path: Path) -> tuple[int, float]:
    try:
        with closing(wave.open(str(path), "rb")) as wav_file:
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
    except (OSError, wave.Error) as exc:
        raise AudiobookGenerationError("Generated audiobook is not a valid WAV file.") from exc
    if sample_rate <= 0:
        raise AudiobookGenerationError("Generated audiobook WAV has an invalid sample rate.")
    return sample_rate, round(frame_count / sample_rate, 3)


def process_document(
    document: BlogMarkdownDocument,
    *,
    voice_path: Path,
    output_root: Path,
    chunk_dir_root: Path | None,
    force: bool,
    dry_run: bool,
    resume: bool,
    keep_chunks: bool,
    device: str | None,
    max_chars: int,
    high_priority: bool,
    autocast: bool,
    exaggeration: float,
    cfg_weight: float,
    temperature: float,
    top_p: float,
    min_p: float,
    repetition_penalty: float,
    runner: Runner = subprocess.run,
    python_executable: str = sys.executable,
    module_name: str = DEFAULT_AUDIOBOOK_MODULE,
) -> ProcessResult:
    output_dir = output_root / document.slug
    spoken_text_path = output_dir / "spoken_text.txt"
    audio_path = output_dir / "audiobook.wav"
    chunk_dir = resolve_chunk_dir(
        output_dir=output_dir,
        chunk_dir_root=chunk_dir_root,
        keep_chunks=keep_chunks,
        resume=resume,
    )

    if dry_run:
        return ProcessResult(
            slug=document.slug,
            status="dry-run",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message="Dry run only; no artifacts written.",
        )

    if bundle_has_existing_outputs(output_dir) and not force:
        return ProcessResult(
            slug=document.slug,
            status="skipped",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message="Existing audiobook artifacts found. Use --force to regenerate.",
            spoken_text_path=str(spoken_text_path),
            manifest_path=str(output_dir / "manifest.json"),
            audio_path=str(audio_path),
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        spoken_text = build_spoken_text(document)
        spoken_text_path.write_text(spoken_text, encoding="utf-8")
        if chunk_dir is not None:
            chunk_dir.mkdir(parents=True, exist_ok=True)

        command = build_chatterbox_command(
            python_executable=python_executable,
            module_name=module_name,
            spoken_text_path=spoken_text_path,
            audio_path=audio_path,
            voice_path=voice_path,
            device=device,
            max_chars=max_chars,
            chunk_dir=chunk_dir,
            resume=resume,
            keep_chunks=keep_chunks,
            high_priority=high_priority,
            autocast=autocast,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            temperature=temperature,
            top_p=top_p,
            min_p=min_p,
            repetition_penalty=repetition_penalty,
        )
        completed = runner(
            command,
            capture_output=False,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            details = stderr or stdout or "unknown synthesis failure; see console output above"
            raise AudiobookGenerationError(f"Chatterbox synthesis failed: {details}")
        if not audio_path.exists():
            raise AudiobookGenerationError("Chatterbox synthesis did not produce an audiobook WAV file.")

        sample_rate, duration_seconds = read_audio_metadata(audio_path)
        chunk_count = (
            len(list(chunk_dir.glob("chunk_*.wav")))
            if chunk_dir is not None and chunk_dir.exists()
            else 0
        )
        manifest = {
            "status": "generated",
            "generated_at": datetime.now(UTC).isoformat(),
            "source": {
                "slug": document.slug,
                "title": document.title,
                "path": str(document.path),
                "published_at": document.published_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                "tags": document.tags,
            },
            "audiobook": {
                "backend": "chatterbox",
                "module": module_name,
                "sample_rate": sample_rate,
                "duration_seconds": duration_seconds,
                "chunk_count": chunk_count,
                "voice_reference": {
                    "path": str(voice_path),
                    "name": voice_path.name,
                },
                "synthesis_settings": {
                    "device": device,
                    "max_chars": max_chars,
                    "high_priority": high_priority,
                    "autocast": autocast,
                    "exaggeration": exaggeration,
                    "cfg_weight": cfg_weight,
                    "temperature": temperature,
                    "top_p": top_p,
                    "min_p": min_p,
                    "repetition_penalty": repetition_penalty,
                    "resume": resume,
                    "keep_chunks": keep_chunks,
                },
            },
            "files": {
                "audio": str(audio_path),
                "spoken_text": str(spoken_text_path),
                "manifest": str(output_dir / "manifest.json"),
                **({"chunks_dir": str(chunk_dir)} if chunk_dir is not None else {}),
            },
        }
        manifest_path = write_manifest(output_dir, manifest)
        return ProcessResult(
            slug=document.slug,
            status="generated",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message="Audiobook artifacts generated successfully.",
            spoken_text_path=str(spoken_text_path),
            manifest_path=str(manifest_path),
            audio_path=str(audio_path),
            chunk_count=chunk_count,
        )
    except Exception as exc:
        error_manifest = {
            "status": "failed",
            "generated_at": datetime.now(UTC).isoformat(),
            "source": {
                "slug": document.slug,
                "title": document.title,
                "path": str(document.path),
            },
            "error": str(exc),
            "files": {
                **({"spoken_text": str(spoken_text_path)} if spoken_text_path.exists() else {}),
                **({"audio": str(audio_path)} if audio_path.exists() else {}),
                **({"chunks_dir": str(chunk_dir)} if chunk_dir is not None and chunk_dir.exists() else {}),
            },
        }
        manifest_path = write_manifest(output_dir, error_manifest)
        return ProcessResult(
            slug=document.slug,
            status="failed",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message=str(exc),
            spoken_text_path=str(spoken_text_path) if spoken_text_path.exists() else "",
            manifest_path=str(manifest_path),
            audio_path=str(audio_path) if audio_path.exists() else "",
        )


def summarize_results(results: list[ProcessResult]) -> str:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    parts = [f"{status}={count}" for status, count in sorted(counts.items())]
    return "Batch summary: " + ", ".join(parts)


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    stdout: io.TextIOBase | None = None,
    stderr: io.TextIOBase | None = None,
    runner: Runner = subprocess.run,
    python_executable: str = sys.executable,
    module_name: str = DEFAULT_AUDIOBOOK_MODULE,
) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        voice_path = args.voice.expanduser().resolve()
        if not voice_path.is_file():
            raise SelectionError(f"Voice reference not found: {voice_path}")
        target_files = resolve_target_files(args)
    except AudiobookGenerationError as exc:
        print(f"generate-blog-audiobooks: {exc}", file=stderr)
        return 1

    results: list[ProcessResult] = []
    for path in target_files:
        document = parse_markdown_file(path)
        result = process_document(
            document,
            voice_path=voice_path,
            output_root=args.output_dir.expanduser().resolve(),
            chunk_dir_root=args.chunk_dir.expanduser().resolve() if args.chunk_dir else None,
            force=args.force,
            dry_run=args.dry_run,
            resume=args.resume,
            keep_chunks=args.keep_chunks,
            device=args.device,
            max_chars=args.max_chars,
            high_priority=args.high_priority,
            autocast=args.autocast,
            exaggeration=args.exaggeration,
            cfg_weight=args.cfg_weight,
            temperature=args.temperature,
            top_p=args.top_p,
            min_p=args.min_p,
            repetition_penalty=args.repetition_penalty,
            runner=runner,
            python_executable=python_executable,
            module_name=module_name,
        )
        results.append(result)
        print(
            f"[{result.status}] {result.slug} -> {result.output_dir} {result.message}",
            file=stdout,
        )

    print(summarize_results(results), file=stdout)
    return 1 if any(result.status == "failed" for result in results) else 0


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
