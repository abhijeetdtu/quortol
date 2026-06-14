"""Minimal Kokoro playback CLI for local agent use.

Examples:
    kokoro-cli play "hello world" --wait
    kokoro-cli play "hello world" --voice af_heart --wait
    kokoro-cli play "hello world" --speed 1.15 --volume 0.8 --wait
    kokoro-cli play "hello world" --output hello.wav --no-play
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence


DEFAULT_LANG = "a"
DEFAULT_SPEED = 1.0
DEFAULT_VOLUME = 1.0
DEFAULT_VOICE = "af_heart"
DEFAULT_SAMPLE_RATE = 24_000
HELP_PROG = "kokoro-cli"


class KokoroCLIError(Exception):
    """Base exception for CLI failures."""


class InputResolutionError(KokoroCLIError):
    """Raised when the CLI cannot determine input text."""


class DependencyError(KokoroCLIError):
    """Raised when required Kokoro dependencies are unavailable."""


class SynthesisError(KokoroCLIError):
    """Raised when Kokoro fails to synthesize speech."""


class PlaybackError(KokoroCLIError):
    """Raised when local audio playback fails."""


Synthesizer = Callable[[str, str, float, str], tuple[int, Any]]
AudioWriter = Callable[[Path, Any, int], None]
AudioPlayer = Callable[[Path, bool], None]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog=HELP_PROG,
        description=(
            "Synthesize text with Kokoro and optionally play it through local speakers."
        ),
        epilog=(
            "Examples:\n"
            "  kokoro-cli play \"hello world\" --wait\n"
            "  kokoro-cli play \"good morning\" --voice af_heart --wait\n"
            "  kokoro-cli play \"quick check\" --speed 1.15 --volume 0.8 --wait\n"
            "  kokoro-cli play \"status update\" --output status.wav --no-play\n\n"
            "Use --wait when the caller should block until playback completes."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    play_parser = subparsers.add_parser(
        "play",
        help="Synthesize speech and optionally play it.",
        description=(
            "Generate speech from text with Kokoro, play it locally, and optionally "
            "wait for playback to finish."
        ),
        epilog=(
            "Examples:\n"
            "  kokoro-cli play \"hello world\" --wait\n"
            "  kokoro-cli play \"agent update\" --voice af_heart --wait\n"
            "  kokoro-cli play \"quick check\" --speed 1.15 --volume 0.8 --wait\n"
            "  kokoro-cli play \"save this\" --output out.wav --no-play\n\n"
            "If no text argument is provided, the command reads text from stdin."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    play_parser.add_argument(
        "text",
        nargs="?",
        help="Text to speak. If omitted, stdin is used.",
    )
    play_parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Voice ID to use. Default: {DEFAULT_VOICE}.",
    )
    play_parser.add_argument(
        "--speed",
        type=float,
        default=DEFAULT_SPEED,
        help=f"Playback speed multiplier. Default: {DEFAULT_SPEED}.",
    )
    play_parser.add_argument(
        "--lang",
        default=DEFAULT_LANG,
        help=f"Kokoro language code. Default: {DEFAULT_LANG}.",
    )
    play_parser.add_argument(
        "--volume",
        type=float,
        default=DEFAULT_VOLUME,
        help=f"Output volume multiplier. Default: {DEFAULT_VOLUME}.",
    )
    play_parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to keep the generated WAV file.",
    )
    play_parser.add_argument(
        "--no-play",
        action="store_true",
        help="Synthesize and save audio without local playback.",
    )
    play_parser.add_argument(
        "--wait",
        action="store_true",
        help="Block until playback completes.",
    )

    return parser


def read_text_argument(text_arg: str | None, stdin: io.TextIOBase | None = None) -> str:
    """Resolve text from a positional argument or stdin."""
    if text_arg and text_arg.strip():
        return text_arg.strip()

    stdin = stdin or sys.stdin
    is_tty = getattr(stdin, "isatty", lambda: False)()
    if is_tty:
        raise InputResolutionError(
            "No input text provided. Pass text as an argument or pipe it through stdin."
        )

    piped_text = stdin.read()
    if piped_text and piped_text.strip():
        return piped_text.strip()

    raise InputResolutionError(
        "No input text provided. Pass text as an argument or pipe it through stdin."
    )


def ensure_valid_speed(speed: float) -> None:
    """Validate speed input."""
    if speed <= 0:
        raise InputResolutionError("--speed must be greater than 0.")


def ensure_valid_volume(volume: float) -> None:
    """Validate volume input."""
    if volume <= 0:
        raise InputResolutionError("--volume must be greater than 0.")


def apply_volume(audio_data: Any, volume: float) -> Any:
    """Scale synthesized audio amplitude."""
    if volume == 1.0:
        return audio_data

    if isinstance(audio_data, (bytes, bytearray)):
        return audio_data

    try:
        import numpy as np
    except ImportError:
        return audio_data

    scaled = np.asarray(audio_data, dtype=np.float32) * float(volume)
    return np.clip(scaled, -1.0, 1.0)


def synthesize_with_kokoro(
    text: str,
    voice: str,
    speed: float,
    lang: str,
) -> tuple[int, Any]:
    """Run Kokoro synthesis and return sample rate plus audio data."""
    try:
        import numpy as np
        from kokoro import KPipeline
    except ImportError as exc:
        raise DependencyError(
            "Kokoro CLI dependencies are missing. Install them with "
            "`pip install -r scripts/requirements-kokoro.txt`."
        ) from exc

    try:
        pipeline = KPipeline(lang_code=lang)
        segments: list[Any] = []

        for _, _, audio in pipeline(
            text,
            voice=voice,
            speed=speed,
            split_pattern=r"\n+",
        ):
            if audio is not None and len(audio) > 0:
                segments.append(audio)
    except Exception as exc:  # pragma: no cover - exercised by guarded manual test
        raise SynthesisError(f"Kokoro synthesis failed: {exc}") from exc

    if not segments:
        raise SynthesisError("Kokoro did not return any audio for the provided text.")

    return DEFAULT_SAMPLE_RATE, np.concatenate(segments)


def write_wav_file(path: Path, audio_data: Any, sample_rate: int) -> None:
    """Write synthesized audio to a WAV file."""
    try:
        import soundfile as sf
    except ImportError as exc:
        raise DependencyError(
            "SoundFile is required for WAV output. Install Kokoro CLI dependencies with "
            "`pip install -r scripts/requirements-kokoro.txt`."
        ) from exc

    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        sf.write(path, audio_data, sample_rate)
    except Exception as exc:  # pragma: no cover - exercised by guarded manual test
        raise SynthesisError(f"Failed to write WAV output: {exc}") from exc


def play_wav_file(path: Path, wait: bool) -> None:
    """Play a WAV file through the local speakers."""
    if os.name != "nt":
        raise PlaybackError(
            "Local playback is currently supported on Windows only. Use `--no-play` "
            "to synthesize without playback."
        )

    try:
        import winsound
    except ImportError as exc:  # pragma: no cover - Windows-only path
        raise PlaybackError("winsound is unavailable on this Python runtime.") from exc

    flags = winsound.SND_FILENAME
    if not wait:
        flags |= winsound.SND_ASYNC

    try:
        winsound.PlaySound(str(path), flags)
    except RuntimeError as exc:  # pragma: no cover - exercised by guarded manual test
        raise PlaybackError(f"Audio playback failed: {exc}") from exc


def resolve_output_path(output: Path | None) -> tuple[Path, bool]:
    """Return output path plus whether the file should be deleted afterward."""
    if output is not None:
        return output.expanduser().resolve(), False

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
        prefix="kokoro-cli-",
    )
    temp_path = Path(temp_file.name)
    temp_file.close()
    return temp_path, True


def run_play_command(
    args: argparse.Namespace,
    *,
    stdin: io.TextIOBase | None = None,
    stderr: io.TextIOBase | None = None,
    synthesizer: Synthesizer | None = None,
    writer: AudioWriter | None = None,
    player: AudioPlayer | None = None,
) -> int:
    """Execute the play subcommand."""
    stderr = stderr or sys.stderr
    synthesizer = synthesizer or synthesize_with_kokoro
    writer = writer or write_wav_file
    player = player or play_wav_file

    try:
        ensure_valid_speed(args.speed)
        ensure_valid_volume(args.volume)
        text = read_text_argument(args.text, stdin=stdin)
        output_path, should_cleanup = resolve_output_path(args.output)
        sample_rate, audio_data = synthesizer(text, args.voice, args.speed, args.lang)
        audio_data = apply_volume(audio_data, args.volume)
        writer(output_path, audio_data, sample_rate)

        if not args.no_play:
            player(output_path, args.wait)

        return 0
    except KokoroCLIError as exc:
        print(f"kokoro-cli: {exc}", file=stderr)
        return 1
    finally:
        if "should_cleanup" in locals() and should_cleanup:
            try:
                output_path.unlink(missing_ok=True)
            except OSError:
                pass


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    stdin: io.TextIOBase | None = None,
    stderr: io.TextIOBase | None = None,
    synthesizer: Synthesizer | None = None,
    writer: AudioWriter | None = None,
    player: AudioPlayer | None = None,
) -> int:
    """Run the CLI and return the exit code."""
    parser = build_parser()
    argv = list(argv) if argv is not None else sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)

    if args.command == "play":
        return run_play_command(
            args,
            stdin=stdin,
            stderr=stderr,
            synthesizer=synthesizer,
            writer=writer,
            player=player,
        )

    parser.print_help()
    return 0


def main() -> None:
    """CLI entrypoint."""
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
