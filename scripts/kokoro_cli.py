"""Minimal Kokoro playback CLI for local agent use.

Examples:
    kokoro-cli play "hello world" --wait
    kokoro-cli play "hello world" --voice af_heart --wait
    kokoro-cli play "hello world" --speed 1.15 --volume 0.8 --wait
    kokoro-cli play "hello world" --output hello.wav --no-play
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence


DEFAULT_SPEED = 1.0
DEFAULT_VOLUME = 1.0
DEFAULT_VOICE = "af_heart"
DEFAULT_SAMPLE_RATE = 24_000
HELP_PROG = "kokoro-cli"
VOICE_LANG_CODES = {
    "af_heart": "a",
    "af_alloy": "a",
    "af_aoede": "a",
    "af_bella": "a",
    "af_jessica": "a",
    "af_kore": "a",
    "af_nicole": "a",
    "af_nova": "a",
    "af_river": "a",
    "af_sarah": "a",
    "af_sky": "a",
    "am_adam": "a",
    "am_echo": "a",
    "am_eric": "a",
    "am_fenrir": "a",
    "am_liam": "a",
    "am_michael": "a",
    "am_onyx": "a",
    "am_puck": "a",
    "am_santa": "a",
    "bf_alice": "b",
    "bf_emma": "b",
    "bf_isabella": "b",
    "bf_lily": "b",
    "bm_daniel": "b",
    "bm_fable": "b",
    "bm_george": "b",
    "bm_lewis": "b",
    "jf_alpha": "j",
    "jf_gongitsune": "j",
    "jf_nezumi": "j",
    "jf_tebukuro": "j",
    "jm_kumo": "j",
    "zf_xiaobei": "z",
    "zf_xiaoni": "z",
    "zf_xiaoxiao": "z",
    "zf_xiaoyi": "z",
    "zm_yunjian": "z",
    "zm_yunxi": "z",
    "zm_yunxia": "z",
    "zm_yunyang": "z",
    "ef_dora": "e",
    "em_alex": "e",
    "em_santa": "e",
    "ff_siwis": "f",
    "hf_alpha": "h",
    "hf_beta": "h",
    "hm_omega": "h",
    "hm_psi": "h",
    "if_sara": "i",
    "im_nicola": "i",
    "pf_dora": "p",
    "pm_alex": "p",
    "pm_santa": "p",
}
DEFAULT_LANG = VOICE_LANG_CODES[DEFAULT_VOICE]


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
        default=None,
        help="Optional Kokoro language code. Defaults to the selected voice's language.",
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

    subparsers.add_parser(
        "doctor",
        help="Inspect the local Kokoro runtime and device support.",
        description=(
            "Report whether Kokoro dependencies are installed and whether the "
            "current Python environment appears to have CUDA available."
        ),
    )

    return parser


def get_supported_voices() -> set[str]:
    """Return the set of supported Kokoro voices."""
    return set(VOICE_LANG_CODES)


def infer_lang_code(voice: str, explicit_lang: str | None = None) -> str:
    """Return the appropriate Kokoro language code for a voice."""
    if explicit_lang:
        return explicit_lang
    if voice in VOICE_LANG_CODES:
        return VOICE_LANG_CODES[voice]
    raise InputResolutionError(
        f"Unsupported Kokoro voice '{voice}'. Supported voices: {', '.join(sorted(VOICE_LANG_CODES))}."
    )


def gather_doctor_info(
    *,
    python_executable: str | None = None,
    module_finder: Callable[[str], Any] | None = None,
    module_importer: Callable[[str], Any] | None = None,
    espeak_finder: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    """Collect environment diagnostics for the Kokoro runtime."""
    module_finder = module_finder or importlib.util.find_spec
    module_importer = module_importer or importlib.import_module
    espeak_finder = espeak_finder or shutil.which

    info: dict[str, Any] = {
        "python_executable": python_executable or sys.executable,
        "kokoro_installed": module_finder("kokoro") is not None,
        "torch_installed": module_finder("torch") is not None,
        "soundfile_installed": module_finder("soundfile") is not None,
        "espeak_ng_path": espeak_finder("espeak-ng"),
        "espeak_ng_exe_path": espeak_finder("espeak-ng.exe"),
    }

    try:
        torch_module = module_importer("torch") if info["torch_installed"] else None
    except Exception as exc:
        info["torch_import_error"] = repr(exc)
        torch_module = None

    if torch_module is not None:
        info["torch_version"] = getattr(torch_module, "__version__", "unknown")
        try:
            cuda = torch_module.cuda
            info["cuda_available"] = bool(cuda.is_available())
            info["cuda_device_count"] = int(cuda.device_count())
            if info["cuda_available"]:
                info["cuda_devices"] = [
                    str(cuda.get_device_name(index))
                    for index in range(info["cuda_device_count"])
                ]
            else:
                info["cuda_devices"] = []
        except Exception as exc:
            info["cuda_check_error"] = repr(exc)

    try:
        if info["kokoro_installed"]:
            module_importer("kokoro")
            info["kokoro_import"] = "ok"
        else:
            info["kokoro_import"] = "missing"
    except Exception as exc:
        info["kokoro_import_error"] = repr(exc)

    cuda_available = bool(info.get("cuda_available"))
    kokoro_ready = info.get("kokoro_import") == "ok"
    info["likely_device"] = "cuda" if cuda_available else "cpu"
    info["kokoro_gpu_ready"] = bool(kokoro_ready and cuda_available)
    return info


def format_doctor_report(info: dict[str, Any]) -> list[str]:
    """Render collected diagnostics as readable CLI lines."""
    espeak_path = info.get("espeak_ng_path") or info.get("espeak_ng_exe_path") or "missing"
    lines = [
        f"python_executable: {info.get('python_executable', 'unknown')}",
        f"kokoro_installed: {info.get('kokoro_installed', False)}",
        f"torch_installed: {info.get('torch_installed', False)}",
        f"soundfile_installed: {info.get('soundfile_installed', False)}",
        f"espeak_ng: {espeak_path}",
    ]

    if "torch_version" in info:
        lines.append(f"torch_version: {info['torch_version']}")
    if "torch_import_error" in info:
        lines.append(f"torch_import_error: {info['torch_import_error']}")
    if "cuda_available" in info:
        lines.append(f"cuda_available: {info['cuda_available']}")
        lines.append(f"cuda_device_count: {info.get('cuda_device_count', 0)}")
    if info.get("cuda_devices"):
        lines.append("cuda_devices: " + ", ".join(info["cuda_devices"]))
    if "cuda_check_error" in info:
        lines.append(f"cuda_check_error: {info['cuda_check_error']}")
    if "kokoro_import" in info:
        lines.append(f"kokoro_import: {info['kokoro_import']}")
    if "kokoro_import_error" in info:
        lines.append(f"kokoro_import_error: {info['kokoro_import_error']}")

    lines.append(f"likely_device: {info.get('likely_device', 'unknown')}")
    lines.append(f"kokoro_gpu_ready: {info.get('kokoro_gpu_ready', False)}")
    return lines


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
        lang_code = infer_lang_code(args.voice, args.lang)
        output_path, should_cleanup = resolve_output_path(args.output)
        sample_rate, audio_data = synthesizer(text, args.voice, args.speed, lang_code)
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


def run_doctor_command(
    *,
    stdout: io.TextIOBase | None = None,
    python_executable: str | None = None,
    module_finder: Callable[[str], Any] | None = None,
    module_importer: Callable[[str], Any] | None = None,
    espeak_finder: Callable[[str], str | None] | None = None,
) -> int:
    """Inspect the local runtime and print Kokoro diagnostics."""
    stdout = stdout or sys.stdout
    info = gather_doctor_info(
        python_executable=python_executable,
        module_finder=module_finder,
        module_importer=module_importer,
        espeak_finder=espeak_finder,
    )
    for line in format_doctor_report(info):
        print(line, file=stdout)
    return 0


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
    if args.command == "doctor":
        return run_doctor_command()

    parser.print_help()
    return 0


def main() -> None:
    """CLI entrypoint."""
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
