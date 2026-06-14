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
        captured: list[str] = []

        def synthesizer(text: str, voice: str, speed: float, lang: str):
            captured.append(text)
            return _fake_synthesizer(text, voice, speed, lang)

        exit_code = kokoro_cli.run_cli(
            ["play", "--no-play"],
            stdin=io.StringIO("hello from stdin"),
            synthesizer=synthesizer,
            writer=_fake_writer,
            stderr=io.StringIO(),
        )

        assert exit_code == 0
        assert captured == ["hello from stdin"]

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
