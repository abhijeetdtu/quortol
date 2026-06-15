"""Tests for the Kokoro CLI wrapper."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import kokoro_cli


def _fake_synthesizer(text: str, voice: str, speed: float, lang: str):
    """Return deterministic fake audio data."""
    return 24_000, b"fake-audio"


def _fake_writer(path: Path, audio_data, sample_rate: int) -> None:
    """Write fake bytes to a target path."""
    path.write_bytes(audio_data)


class TestKokoroCLIHelp:
    """Help text and top-level command behavior."""

    def test_top_level_help_lists_primary_example(self):
        """Top-level help should advertise the shortest successful command."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "kokoro_cli.py"), "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        assert 'kokoro-cli play "hello world" --wait' in result.stdout
        assert "--volume" in result.stdout
        assert "doctor" in result.stdout
        assert "Use --wait when the caller should block until playback completes." in result.stdout

    def test_play_help_lists_supported_flags(self):
        """Subcommand help should list the supported v1 flags."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "kokoro_cli.py"), "play", "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        assert result.returncode == 0
        for flag in ("--voice", "--speed", "--lang", "--volume", "--output", "--no-play", "--wait"):
            assert flag in result.stdout


class TestKokoroCLIPlay:
    """Play command behavior and cleanup."""

    def test_voice_language_defaults_follow_voice_id(self):
        """Known voices should auto-select the correct Kokoro language code."""
        assert kokoro_cli.infer_lang_code("af_heart") == "a"
        assert kokoro_cli.infer_lang_code("bf_emma") == "b"
        assert kokoro_cli.infer_lang_code("jf_alpha") == "j"

    def test_play_command_waits_for_playback_and_cleans_temp_file(self):
        """Temporary WAV files should be deleted after playback completes."""
        written_paths: list[Path] = []
        played: list[tuple[Path, bool]] = []

        def writer(path: Path, audio_data, sample_rate: int) -> None:
            written_paths.append(path)
            path.write_bytes(audio_data)

        def player(path: Path, wait: bool) -> None:
            played.append((path, wait))
            assert path.exists()

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--wait"],
            synthesizer=_fake_synthesizer,
            writer=writer,
            player=player,
            stderr=io.StringIO(),
        )

        assert exit_code == 0
        assert len(written_paths) == 1
        assert played == [(written_paths[0], True)]
        assert not written_paths[0].exists()

    def test_play_command_keeps_output_file_when_requested(self, tmp_path):
        """Explicit output files should be preserved."""
        output_path = tmp_path / "hello.wav"
        player_calls: list[tuple[Path, bool]] = []

        def player(path: Path, wait: bool) -> None:
            player_calls.append((path, wait))

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--output", str(output_path), "--wait"],
            synthesizer=_fake_synthesizer,
            writer=_fake_writer,
            player=player,
            stderr=io.StringIO(),
        )

        assert exit_code == 0
        assert output_path.exists()
        assert player_calls == [(output_path.resolve(), True)]

    def test_reads_text_from_stdin_when_argument_missing(self):
        """Piped stdin should be used when the text argument is omitted."""
        captured: list[tuple[str, str]] = []

        def synthesizer(text: str, voice: str, speed: float, lang: str):
            captured.append((text, lang))
            return _fake_synthesizer(text, voice, speed, lang)

        exit_code = kokoro_cli.run_cli(
            ["play", "--no-play"],
            stdin=io.StringIO("hello from stdin"),
            synthesizer=synthesizer,
            writer=_fake_writer,
            stderr=io.StringIO(),
        )

        assert exit_code == 0
        assert captured == [("hello from stdin", "a")]

    def test_invalid_voice_returns_nonzero(self):
        """Unknown voice IDs should fail early with a helpful message."""
        stderr = io.StringIO()

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--voice", "bf_omega"],
            synthesizer=_fake_synthesizer,
            writer=_fake_writer,
            player=lambda path, wait: None,
            stderr=stderr,
        )

        assert exit_code == 1
        assert "Unsupported Kokoro voice 'bf_omega'" in stderr.getvalue()

    def test_invalid_speed_returns_nonzero(self):
        """Invalid speed should return a non-zero exit code and stderr message."""
        stderr = io.StringIO()

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--speed", "0"],
            synthesizer=_fake_synthesizer,
            writer=_fake_writer,
            player=lambda path, wait: None,
            stderr=stderr,
        )

        assert exit_code == 1
        assert "--speed must be greater than 0." in stderr.getvalue()

    def test_invalid_volume_returns_nonzero(self):
        """Invalid volume should return a non-zero exit code and stderr message."""
        stderr = io.StringIO()

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--volume", "0"],
            synthesizer=_fake_synthesizer,
            writer=_fake_writer,
            player=lambda path, wait: None,
            stderr=stderr,
        )

        assert exit_code == 1
        assert "--volume must be greater than 0." in stderr.getvalue()

    def test_volume_scaling_is_applied_before_writing(self):
        """Volume should scale synthesized audio before the writer runs."""
        written_audio = []

        def synthesizer(text: str, voice: str, speed: float, lang: str):
            return 24_000, [-0.5, 0.25, 0.75]

        def writer(path: Path, audio_data, sample_rate: int) -> None:
            written_audio.append(list(audio_data))
            path.write_text("ok")

        exit_code = kokoro_cli.run_cli(
            ["play", "hello world", "--volume", "0.5", "--no-play"],
            synthesizer=synthesizer,
            writer=writer,
            stderr=io.StringIO(),
        )

        assert exit_code == 0
        assert written_audio == [[-0.25, 0.125, 0.375]]


class TestKokoroCLIDoctor:
    """Doctor command environment reporting."""

    def test_doctor_reports_missing_runtime_cleanly(self):
        stdout = io.StringIO()

        def module_finder(name: str):
            return None

        exit_code = kokoro_cli.run_doctor_command(
            stdout=stdout,
            python_executable="C:\\Python\\python.exe",
            module_finder=module_finder,
            espeak_finder=lambda name: None,
        )

        report = stdout.getvalue()
        assert exit_code == 0
        assert "python_executable: C:\\Python\\python.exe" in report
        assert "kokoro_installed: False" in report
        assert "torch_installed: False" in report
        assert "likely_device: cpu" in report
        assert "kokoro_gpu_ready: False" in report

    def test_doctor_reports_cuda_when_torch_supports_it(self):
        stdout = io.StringIO()

        class FakeCuda:
            @staticmethod
            def is_available():
                return True

            @staticmethod
            def device_count():
                return 1

            @staticmethod
            def get_device_name(index: int):
                assert index == 0
                return "NVIDIA RTX Test"

        class FakeTorch:
            __version__ = "2.5.0"
            cuda = FakeCuda()

        def module_finder(name: str):
            return object() if name in {"torch", "kokoro", "soundfile"} else None

        def module_importer(name: str):
            if name == "torch":
                return FakeTorch
            if name == "kokoro":
                return object()
            raise ImportError(name)

        exit_code = kokoro_cli.run_doctor_command(
            stdout=stdout,
            module_finder=module_finder,
            module_importer=module_importer,
            espeak_finder=lambda name: "C:\\Program Files\\eSpeak NG\\espeak-ng.exe",
        )

        report = stdout.getvalue()
        assert exit_code == 0
        assert "torch_version: 2.5.0" in report
        assert "cuda_available: True" in report
        assert "cuda_device_count: 1" in report
        assert "cuda_devices: NVIDIA RTX Test" in report
        assert "kokoro_import: ok" in report
        assert "likely_device: cuda" in report
        assert "kokoro_gpu_ready: True" in report
