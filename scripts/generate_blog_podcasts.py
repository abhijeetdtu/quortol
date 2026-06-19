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
from tts_backends import TTSBackendError, create_tts_backend  # noqa: E402
from tts_backends.qwen import (  # noqa: E402
    DEFAULT_QWEN_AUTHOR_VOICE,
    DEFAULT_QWEN_CONDA_ENV,
    DEFAULT_QWEN_JOURNALIST_VOICE,
    DEFAULT_QWEN_MODEL,
)


DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "backend" / "static" / "podcasts"
DEFAULT_PROMPT_TEMPLATE = REPO_ROOT / "docs" / "podcast-instructions.md"
DEFAULT_JOURNALIST_VOICE = "af_heart"
DEFAULT_AUTHOR_VOICE = "am_fenrir"
DEFAULT_TTS_BACKEND = "kokoro"
SHORT_PAUSE_MS = 250
SECTION_PAUSE_MS = 600
SPEAKER_LABELS = {
    "journalist": "JOURNALIST",
    "author": "AUTHOR",
}
LEGACY_SPEAKER_ALIASES = {
    "host_a": "journalist",
    "host_b": "author",
}


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
            "Generate interview-style podcast scripts and WAV episodes from blog markdown files."
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
        "--tts-backend",
        default=DEFAULT_TTS_BACKEND,
        help="TTS backend to synthesize episode audio. Supported: kokoro, qwen.",
    )
    parser.add_argument(
        "--tts-conda-env",
        default=DEFAULT_QWEN_CONDA_ENV,
        help=f"Conda environment name used for local qwen TTS synthesis. Default: {DEFAULT_QWEN_CONDA_ENV}",
    )
    parser.add_argument(
        "--tts-model",
        default=DEFAULT_QWEN_MODEL,
        help="Optional TTS model identifier stored in manifest metadata.",
    )
    parser.add_argument(
        "--tts-language",
        default="english",
        help="Language passed to the local qwen TTS script. Default: english",
    )
    parser.add_argument(
        "--tts-extra-arg",
        action="append",
        default=[],
        help="Additional argument to forward to the local qwen TTS script. Repeat as needed.",
    )
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=DEFAULT_PROMPT_TEMPLATE,
        help=f"Prompt template file to use. Default: {DEFAULT_PROMPT_TEMPLATE}",
    )
    parser.add_argument(
        "--journalist-voice",
        "--host-a-voice",
        dest="journalist_voice",
        default=DEFAULT_JOURNALIST_VOICE,
        help=f"Kokoro voice for the journalist role. Default: {DEFAULT_JOURNALIST_VOICE}",
    )
    parser.add_argument(
        "--author-voice",
        "--host-b-voice",
        dest="author_voice",
        default=DEFAULT_AUTHOR_VOICE,
        help=f"Kokoro voice for the author role. Default: {DEFAULT_AUTHOR_VOICE}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate outputs even when an episode already exists and ignore any existing script.md.",
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


def validate_voice(tts_backend: Any, voice: str) -> None:
    try:
        tts_backend.validate_voice(voice)
    except TTSBackendError as exc:
        raise SelectionError(str(exc)) from exc


def resolve_voice_defaults(args: argparse.Namespace, argv: Sequence[str]) -> tuple[str, str]:
    journalist_explicit = "--journalist-voice" in argv or "--host-a-voice" in argv
    author_explicit = "--author-voice" in argv or "--host-b-voice" in argv

    journalist_voice = args.journalist_voice
    author_voice = args.author_voice

    if args.tts_backend.strip().lower() == "qwen":
        if not journalist_explicit:
            journalist_voice = DEFAULT_QWEN_JOURNALIST_VOICE
        if not author_explicit:
            author_voice = DEFAULT_QWEN_AUTHOR_VOICE

    return journalist_voice, author_voice


def normalize_speaker(raw_speaker: str) -> str:
    speaker = raw_speaker.strip().lower()
    speaker = LEGACY_SPEAKER_ALIASES.get(speaker, speaker)
    if speaker not in SPEAKER_LABELS:
        raise LLMContractError("Segments must use only journalist or author speakers.")
    return speaker


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
        speaker = normalize_speaker(str(raw_segment.get("speaker", "")))
        section = str(raw_segment.get("section", "")).strip() or "discussion"
        text = " ".join(str(raw_segment.get("text", "")).split())
        if not text:
            raise LLMContractError("Each segment must include non-empty text.")
        if previous_speaker and speaker == previous_speaker:
            raise LLMContractError("Segments must alternate speakers.")
        previous_speaker = speaker
        seen_speakers.add(speaker)
        segments.append(PodcastSegment(speaker=speaker, section=section, text=text))

    if seen_speakers != set(SPEAKER_LABELS):
        raise LLMContractError("Episode must include both journalist and author.")
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
        speaker = ""
        text = ""
        for label, normalized in (
            ("JOURNALIST:", "journalist"),
            ("AUTHOR:", "author"),
            ("HOST A:", "journalist"),
            ("HOST B:", "author"),
        ):
            if line.startswith(label):
                speaker = normalized
                text = line.removeprefix(label).strip()
                break
        if not speaker:
            raise LLMContractError(
                "Dialogue lines must start with 'JOURNALIST:' or 'AUTHOR:'."
            )
        if not text:
            raise LLMContractError("Dialogue lines must include spoken text after the speaker label.")
        if previous_speaker and speaker == previous_speaker:
            raise LLMContractError("Dialogue lines must alternate speakers.")
        previous_speaker = speaker
        seen_speakers.add(speaker)
        section = classify_dialogue_section(index, total_lines)
        segments.append(PodcastSegment(speaker=speaker, section=section, text=text))

    if seen_speakers != set(SPEAKER_LABELS):
        raise LLMContractError("Dialogue must include both JOURNALIST and AUTHOR.")
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
        return "A journalist interviews the author about the source material."
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
        '  "dialogue": "JOURNALIST: ...\\nAUTHOR: ..."\n'
        "}\n\n"
        "Encoding rules for the JSON:\n"
        "- The dialogue value must contain the full script in the exact JOURNALIST / AUTHOR format requested by the prompt file.\n"
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
    tts_backend: Any,
) -> tuple[Path, int]:
    sample_rate: int | None = None
    merged_frames = bytearray()
    previous_section = ""
    segments_dir = output_dir / "segments"

    for index, segment in enumerate(episode.segments, start=1):
        voice = voice_map[segment.speaker]
        current_rate, audio_data = tts_backend.synthesize(
            segment.text,
            voice,
            1.0,
            segment.speaker,
        )
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
        speaker_label = SPEAKER_LABELS[segment.speaker]
        lines.extend(
            [
                f"{speaker_label}: {segment.text}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def load_script_markdown(path: Path, document: BlogMarkdownDocument) -> EpisodeScript:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PodcastGenerationError(f"Could not read existing script: {path}") from exc

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise PodcastGenerationError(f"Existing script is empty: {path}")

    episode_title = document.title
    dialogue_lines: list[str] = []
    for line in lines:
        if line.startswith("# "):
            episode_title = line.removeprefix("# ").strip() or episode_title
            continue
        if line.startswith("Source blog:") or line.startswith("Slug:"):
            continue
        if any(
            line.startswith(label)
            for label in ("JOURNALIST:", "AUTHOR:", "HOST A:", "HOST B:")
        ):
            dialogue_lines.append(line)

    if not dialogue_lines:
        raise PodcastGenerationError(f"Existing script does not contain dialogue: {path}")

    segments = parse_dialogue_text("\n".join(dialogue_lines))
    return EpisodeScript(
        episode_title=episode_title,
        episode_summary=derive_episode_summary(segments),
        segments=segments,
    )


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
    journalist_voice: str,
    author_voice: str,
    force: bool,
    dry_run: bool,
    keep_segments: bool,
    requester: Requester = requests.post,
    synthesizer: Synthesizer = kokoro_cli.synthesize_with_kokoro,
    tts_runner: Callable[..., Any] | None = None,
    tts_backend: Any | None = None,
    tts_backend_id: str = DEFAULT_TTS_BACKEND,
    tts_conda_env: str = DEFAULT_QWEN_CONDA_ENV,
    tts_model: str = "",
    tts_language: str = "english",
    tts_extra_args: list[str] | None = None,
) -> ProcessResult:
    output_dir = output_root / document.slug
    script_path = output_dir / "script.md"
    episode_path = output_dir / "episode.wav"
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
            episode_path=str(episode_path),
        )

    voice_map = {"journalist": journalist_voice, "author": author_voice}
    active_tts_backend = tts_backend or create_tts_backend(
        tts_backend_id,
        tts_conda_env=tts_conda_env,
        tts_model=tts_model,
        tts_language=tts_language,
        tts_extra_args=tts_extra_args,
        kokoro_synthesizer=synthesizer,
        tts_runner=tts_runner,
    )

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        reused_existing_script = script_path.exists() and not force
        if reused_existing_script:
            episode = load_script_markdown(script_path, document)
        else:
            episode = request_episode_script(
                document=document,
                endpoint=endpoint,
                model=model,
                prompt_template=prompt_template,
                requester=requester,
            )
            script_path.write_text(
                render_script_markdown(document, episode),
                encoding="utf-8",
            )
        episode_path, sample_rate = merge_episode_audio(
            episode=episode,
            output_dir=output_dir,
            voice_map=voice_map,
            keep_segments=keep_segments,
            tts_backend=active_tts_backend,
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
                "tts": {
                    **active_tts_backend.describe(),
                    "voices": voice_map,
                },
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
            message=(
                "Podcast audio generated from existing script."
                if reused_existing_script
                else "Podcast artifacts generated successfully."
            ),
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
    tts_runner: Callable[..., Any] | None = None,
) -> int:
    parser = build_parser()
    parsed_argv = list(argv) if argv is not None else None
    args = parser.parse_args(parsed_argv)
    current_argv = parsed_argv if parsed_argv is not None else sys.argv[1:]
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        journalist_voice, author_voice = resolve_voice_defaults(args, current_argv)
        tts_backend = create_tts_backend(
            args.tts_backend,
            tts_conda_env=args.tts_conda_env,
            tts_model=args.tts_model,
            tts_language=args.tts_language,
            tts_extra_args=args.tts_extra_arg,
            kokoro_synthesizer=synthesizer,
            tts_runner=tts_runner,
        )
        validate_voice(tts_backend, journalist_voice)
        validate_voice(tts_backend, author_voice)
        prompt_template = load_prompt_template(args.prompt_template)
        target_files = resolve_target_files(args)
    except (PodcastGenerationError, TTSBackendError) as exc:
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
            journalist_voice=journalist_voice,
            author_voice=author_voice,
            force=args.force,
            dry_run=args.dry_run,
            keep_segments=args.keep_segments,
            requester=requester,
            synthesizer=synthesizer,
            tts_runner=tts_runner,
            tts_backend=tts_backend,
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

