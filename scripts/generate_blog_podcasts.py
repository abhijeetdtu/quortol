"""Generate two-host podcast artifacts from blog markdown files."""

from __future__ import annotations

import argparse
import io
import json
import sys
import wave
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Callable, Sequence

import requests


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
import kokoro_cli  # noqa: E402


DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "backend" / "static" / "podcasts"
DEFAULT_PROMPT_TEMPLATE = REPO_ROOT / "docs" / "podcast-instructions.md"
DEFAULT_HOST_A_VOICE = "af_heart"
DEFAULT_HOST_B_VOICE = "am_fenrir"
SHORT_PAUSE_MS = 250
SECTION_PAUSE_MS = 600
SUPPORTED_VOICES = kokoro_cli.get_supported_voices()


class PodcastGenerationError(Exception):
    """Base error for podcast generation failures."""


class SelectionError(PodcastGenerationError):
    """Raised when CLI selection is invalid."""


class LLMContractError(PodcastGenerationError):
    """Raised when the model response violates the expected JSON contract."""


class PromptTemplateError(PodcastGenerationError):
    """Raised when the podcast prompt template is missing or invalid."""


@dataclass(frozen=True)
class PodcastSegment:
    speaker: str
    section: str
    text: str


@dataclass(frozen=True)
class EpisodeScript:
    episode_title: str
    episode_summary: str
    segments: list[PodcastSegment]


@dataclass(frozen=True)
class ProcessResult:
    slug: str
    status: str
    source_path: str
    output_dir: str
    message: str = ""
    script_path: str = ""
    manifest_path: str = ""
    episode_path: str = ""
    segment_count: int = 0


Requester = Callable[..., Any]
Synthesizer = Callable[[str, str, float, str], tuple[int, Any]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate-blog-podcasts",
        description=(
            "Generate two-host podcast scripts and WAV episodes from blog markdown files."
        ),
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
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output root for generated podcast bundles. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"llama-server chat completions endpoint. Default: {DEFAULT_ENDPOINT}",
    )
    parser.add_argument("--model", default="", help="Optional model identifier.")
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=DEFAULT_PROMPT_TEMPLATE,
        help=f"Prompt template file to use. Default: {DEFAULT_PROMPT_TEMPLATE}",
    )
    parser.add_argument(
        "--host-a-voice",
        default=DEFAULT_HOST_A_VOICE,
        help=f"Kokoro voice for host_a. Default: {DEFAULT_HOST_A_VOICE}",
    )
    parser.add_argument(
        "--host-b-voice",
        default=DEFAULT_HOST_B_VOICE,
        help=f"Kokoro voice for host_b. Default: {DEFAULT_HOST_B_VOICE}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate outputs even when an episode already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended work without writing any output files.",
    )
    parser.add_argument(
        "--keep-segments",
        action="store_true",
        help="Keep per-segment WAV files alongside the final merged episode.",
    )
    return parser


def validate_voice(voice: str) -> None:
    if voice not in SUPPORTED_VOICES:
        supported = ", ".join(sorted(SUPPORTED_VOICES))
        raise SelectionError(f"Unsupported Kokoro voice '{voice}'. Supported voices: {supported}.")


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


def load_prompt_template(path: Path) -> str:
    try:
        template = path.expanduser().resolve().read_text(encoding="utf-8")
    except OSError as exc:
        raise PromptTemplateError(f"Could not read prompt template: {path}") from exc
    required_tokens = ("{{SOURCE_MATERIAL}}", "{{PODCAST_TITLE}}", "{{WORD_COUNT}}")
    missing = [token for token in required_tokens if token not in template]
    if missing:
        raise PromptTemplateError(
            f"Prompt template is missing required placeholder(s): {', '.join(missing)}."
        )
    return template


def estimate_target_word_count(source_text: str) -> int:
    word_count = len(source_text.split())
    return max(1600, min(3600, int(word_count * 0.85)))


def extract_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        raise LLMContractError("Model response did not contain a JSON object.")

    depth = 0
    in_string = False
    escape = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])

    raise LLMContractError("Model response contained incomplete JSON.")


def validate_episode_payload(payload: dict[str, Any]) -> EpisodeScript:
    episode_title = str(payload.get("episode_title", "")).strip()
    episode_summary = str(payload.get("episode_summary", "")).strip()
    raw_dialogue = str(payload.get("dialogue", "")).strip()
    raw_segments = payload.get("segments")
    if not episode_title:
        raise LLMContractError("Missing episode_title.")
    if raw_dialogue:
        segments = parse_dialogue_text(raw_dialogue)
    else:
        if not isinstance(raw_segments, list) or not raw_segments:
            raise LLMContractError("Missing non-empty segments array or dialogue field.")
        segments = parse_segment_objects(raw_segments)
    if not episode_summary:
        episode_summary = derive_episode_summary(segments)

    return EpisodeScript(
        episode_title=episode_title,
        episode_summary=episode_summary,
        segments=segments,
    )


def parse_segment_objects(raw_segments: list[dict[str, Any]]) -> list[PodcastSegment]:
    segments: list[PodcastSegment] = []
    seen_speakers: set[str] = set()
    previous_speaker = ""
    for raw_segment in raw_segments:
        if not isinstance(raw_segment, dict):
            raise LLMContractError("Each segment must be an object.")
        speaker = str(raw_segment.get("speaker", "")).strip()
        section = str(raw_segment.get("section", "")).strip() or "discussion"
        text = " ".join(str(raw_segment.get("text", "")).split())
        if speaker not in {"host_a", "host_b"}:
            raise LLMContractError("Segments must use only host_a or host_b speakers.")
        if not text:
            raise LLMContractError("Each segment must include non-empty text.")
        if previous_speaker and speaker == previous_speaker:
            raise LLMContractError("Segments must alternate speakers.")
        previous_speaker = speaker
        seen_speakers.add(speaker)
        segments.append(PodcastSegment(speaker=speaker, section=section, text=text))

    if seen_speakers != {"host_a", "host_b"}:
        raise LLMContractError("Episode must include both host_a and host_b.")
    return segments


def parse_dialogue_text(dialogue: str) -> list[PodcastSegment]:
    lines = [line.strip() for line in dialogue.splitlines() if line.strip()]
    if not lines:
        raise LLMContractError("Dialogue field was empty.")

    segments: list[PodcastSegment] = []
    previous_speaker = ""
    seen_speakers: set[str] = set()
    total_lines = len(lines)
    for index, line in enumerate(lines):
        if line.startswith("HOST A:"):
            speaker = "host_a"
            text = line.removeprefix("HOST A:").strip()
        elif line.startswith("HOST B:"):
            speaker = "host_b"
            text = line.removeprefix("HOST B:").strip()
        else:
            raise LLMContractError("Dialogue lines must start with 'HOST A:' or 'HOST B:'.")
        if not text:
            raise LLMContractError("Dialogue lines must include spoken text after the speaker label.")
        if previous_speaker and speaker == previous_speaker:
            raise LLMContractError("Dialogue lines must alternate speakers.")
        previous_speaker = speaker
        seen_speakers.add(speaker)
        section = classify_dialogue_section(index, total_lines)
        segments.append(PodcastSegment(speaker=speaker, section=section, text=text))

    if seen_speakers != {"host_a", "host_b"}:
        raise LLMContractError("Dialogue must include both HOST A and HOST B.")
    return segments


def classify_dialogue_section(index: int, total_lines: int) -> str:
    if index < 4:
        return "intro"
    if index >= max(0, total_lines - 2):
        return "outro"
    return "discussion"


def derive_episode_summary(segments: list[PodcastSegment]) -> str:
    combined = " ".join(segment.text for segment in segments[:2]).strip()
    if not combined:
        return "Two hosts explore the source material in conversation."
    return " ".join(combined.split()[:40]).strip()


def build_generation_prompt(document: BlogMarkdownDocument, prompt_template: str) -> str:
    source_text = markdown_to_spoken_text(document.content)
    prompt_body = (
        prompt_template.replace("{{SOURCE_MATERIAL}}", source_text)
        .replace("{{PODCAST_TITLE}}", document.title)
        .replace("{{WORD_COUNT}}", str(estimate_target_word_count(source_text)))
    )
    return (
        "Use the following podcast-writing instructions to create the conversation.\n\n"
        f"{prompt_body}\n\n"
        "Return JSON only with this exact shape:\n"
        "{\n"
        '  "episode_title": "string",\n'
        '  "episode_summary": "string",\n'
        '  "dialogue": "HOST A: ...\\nHOST B: ..."\n'
        "}\n\n"
        "Encoding rules for the JSON:\n"
        "- The dialogue value must contain the full script in the exact HOST A / HOST B format requested by the prompt file.\n"
        "- Keep the dialogue conversational, not outline-like or sectioned.\n"
        "- Do not compress this into a short recap; aim to use most of the requested target length.\n"
        "- Preserve the important chronology, names, institutions, conflicts, and consequences from the source.\n"
        "- Keep speakers alternating exactly as written in the dialogue.\n"
        "- Write episode_summary as a short production summary, not as a replacement for the conversation.\n"
    ).strip()


def build_repair_prompt(
    document: BlogMarkdownDocument,
    prompt_template: str,
    error_message: str,
) -> str:
    return (
        build_generation_prompt(document, prompt_template)
        + "\n\nThe previous attempt failed validation for this reason:\n"
        + error_message
        + "\n\nReturn a corrected JSON object only."
    )


def request_episode_script(
    document: BlogMarkdownDocument,
    endpoint: str,
    model: str,
    prompt_template: str,
    requester: Requester = requests.post,
) -> EpisodeScript:
    prompt = build_generation_prompt(document, prompt_template)
    repair_prompt = ""
    last_error = "Unknown failure"

    for attempt in range(2):
        current_prompt = prompt if attempt == 0 else repair_prompt
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful podcast adaptation editor. "
                        "Return valid JSON only."
                    ),
                },
                {"role": "user", "content": current_prompt},
            ],
            "temperature": 0.4,
        }
        if model:
            payload["model"] = model

        response = requester(endpoint, json=payload, timeout=300)
        response.raise_for_status()
        response_payload = response.json()
        content = extract_completion_content(response_payload)

        try:
            return validate_episode_payload(extract_json_object(content))
        except (LLMContractError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            last_error = str(exc)
            repair_prompt = build_repair_prompt(document, prompt_template, last_error)

    raise LLMContractError(last_error)


def extract_completion_content(response_payload: dict[str, Any]) -> str:
    choices = response_payload.get("choices")
    if isinstance(choices, list) and choices:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get("message")
            if isinstance(message, dict) and message.get("content"):
                return str(message["content"])
            if first_choice.get("text"):
                return str(first_choice["text"])
    raise LLMContractError("Model response did not include a completion message.")


def audio_samples_to_pcm16(audio_data: Any) -> bytes:
    if isinstance(audio_data, (bytes, bytearray)):
        return bytes(audio_data)

    pcm = bytearray()
    for sample in audio_data:
        clamped = max(-1.0, min(1.0, float(sample)))
        scaled = int(clamped * 32767)
        pcm.extend(int(scaled).to_bytes(2, byteorder="little", signed=True))
    return bytes(pcm)


def silence_pcm(sample_rate: int, duration_ms: int) -> bytes:
    frame_count = max(0, int(sample_rate * duration_ms / 1000))
    return b"\x00\x00" * frame_count


def write_pcm_wav(path: Path, pcm_frames: bytes, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_frames)


def merge_episode_audio(
    episode: EpisodeScript,
    output_dir: Path,
    voice_map: dict[str, str],
    keep_segments: bool,
    synthesizer: Synthesizer,
) -> tuple[Path, int]:
    sample_rate: int | None = None
    merged_frames = bytearray()
    previous_section = ""
    segments_dir = output_dir / "segments"

    for index, segment in enumerate(episode.segments, start=1):
        voice = voice_map[segment.speaker]
        lang_code = kokoro_cli.infer_lang_code(voice)
        current_rate, audio_data = synthesizer(segment.text, voice, 1.0, lang_code)
        if sample_rate is None:
            sample_rate = current_rate
        elif sample_rate != current_rate:
            raise PodcastGenerationError("All segment audio must use the same sample rate.")

        pcm_frames = audio_samples_to_pcm16(audio_data)
        if keep_segments:
            segment_path = segments_dir / f"{index:03d}-{segment.speaker}.wav"
            write_pcm_wav(segment_path, pcm_frames, current_rate)

        if merged_frames:
            pause_ms = SECTION_PAUSE_MS if segment.section != previous_section else SHORT_PAUSE_MS
            merged_frames.extend(silence_pcm(current_rate, pause_ms))
        merged_frames.extend(pcm_frames)
        previous_section = segment.section

    if sample_rate is None:
        raise PodcastGenerationError("No audio segments were produced.")

    episode_path = output_dir / "episode.wav"
    write_pcm_wav(episode_path, bytes(merged_frames), sample_rate)
    return episode_path, sample_rate


def render_script_markdown(document: BlogMarkdownDocument, episode: EpisodeScript) -> str:
    lines = [
        f"# {episode.episode_title}",
        "",
        f"Source blog: {document.title}",
        f"Slug: `{document.slug}`",
        "",
    ]
    for segment in episode.segments:
        speaker_label = "HOST A" if segment.speaker == "host_a" else "HOST B"
        lines.extend(
            [
                f"{speaker_label}: {segment.text}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def bundle_has_existing_outputs(output_dir: Path) -> bool:
    return (output_dir / "episode.wav").exists() and (output_dir / "manifest.json").exists()


def write_manifest(output_dir: Path, manifest: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def process_document(
    document: BlogMarkdownDocument,
    *,
    output_root: Path,
    endpoint: str,
    model: str,
    prompt_template: str,
    host_a_voice: str,
    host_b_voice: str,
    force: bool,
    dry_run: bool,
    keep_segments: bool,
    requester: Requester = requests.post,
    synthesizer: Synthesizer = kokoro_cli.synthesize_with_kokoro,
) -> ProcessResult:
    output_dir = output_root / document.slug
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
            message="Existing podcast artifacts found. Use --force to regenerate.",
            manifest_path=str(output_dir / "manifest.json"),
            episode_path=str(output_dir / "episode.wav"),
        )

    voice_map = {"host_a": host_a_voice, "host_b": host_b_voice}

    try:
        episode = request_episode_script(
            document=document,
            endpoint=endpoint,
            model=model,
            prompt_template=prompt_template,
            requester=requester,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        script_path = output_dir / "script.md"
        script_path.write_text(
            render_script_markdown(document, episode),
            encoding="utf-8",
        )
        episode_path, sample_rate = merge_episode_audio(
            episode=episode,
            output_dir=output_dir,
            voice_map=voice_map,
            keep_segments=keep_segments,
            synthesizer=synthesizer,
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
            "episode": {
                "episode_title": episode.episode_title,
                "episode_summary": episode.episode_summary,
                "segment_count": len(episode.segments),
                "sample_rate": sample_rate,
                "voices": voice_map,
            },
            "files": {
                "script": str(script_path),
                "manifest": str(output_dir / "manifest.json"),
                "episode": str(episode_path),
            },
        }
        manifest_path = write_manifest(output_dir, manifest)
        return ProcessResult(
            slug=document.slug,
            status="generated",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message="Podcast artifacts generated successfully.",
            script_path=str(script_path),
            manifest_path=str(manifest_path),
            episode_path=str(episode_path),
            segment_count=len(episode.segments),
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
        }
        manifest_path = write_manifest(output_dir, error_manifest)
        return ProcessResult(
            slug=document.slug,
            status="failed",
            source_path=str(document.path),
            output_dir=str(output_dir),
            message=str(exc),
            manifest_path=str(manifest_path),
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
    requester: Requester = requests.post,
    synthesizer: Synthesizer = kokoro_cli.synthesize_with_kokoro,
) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        validate_voice(args.host_a_voice)
        validate_voice(args.host_b_voice)
        prompt_template = load_prompt_template(args.prompt_template)
        target_files = resolve_target_files(args)
    except PodcastGenerationError as exc:
        print(f"generate-blog-podcasts: {exc}", file=stderr)
        return 1

    results: list[ProcessResult] = []
    for path in target_files:
        document = parse_markdown_file(path)
        result = process_document(
            document,
            output_root=args.output_dir.expanduser().resolve(),
            endpoint=args.endpoint,
            model=args.model,
            prompt_template=prompt_template,
            host_a_voice=args.host_a_voice,
            host_b_voice=args.host_b_voice,
            force=args.force,
            dry_run=args.dry_run,
            keep_segments=args.keep_segments,
            requester=requester,
            synthesizer=synthesizer,
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

