"""Local CLI-backed Qwen adapter for podcast generation."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence

from .base import TTSBackendError, TTSBackendMetadata, wav_bytes_to_pcm16


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QWEN_MODULE = "scripts.qwen3_tts_chunk"
DEFAULT_QWEN_CONDA_ENV = "qwen3-tts-cuda"
DEFAULT_QWEN_JOURNALIST_VOICE = "Ryan"
DEFAULT_QWEN_AUTHOR_VOICE = "Aiden"
DEFAULT_QWEN_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"

Runner = Callable[..., Any]


class QwenTTSBackend:
    """Invoke a local Qwen batch synthesis script and consume its WAV output."""

    backend_id = "qwen"

    def __init__(
        self,
        *,
        conda_env: str = DEFAULT_QWEN_CONDA_ENV,
        model: str = DEFAULT_QWEN_MODEL,
        language: str = "english",
        extra_args: Sequence[str] | None = None,
        module_name: str = DEFAULT_QWEN_MODULE,
        runner: Runner = subprocess.run,
    ) -> None:
        self.conda_env = (conda_env or DEFAULT_QWEN_CONDA_ENV).strip()
        if not self.conda_env:
            raise TTSBackendError("The qwen TTS backend requires a Conda environment name.")
        self.model = model.strip()
        self.language = (language or "english").strip()
        self.extra_args = list(extra_args or [])
        self.module_name = (module_name or DEFAULT_QWEN_MODULE).strip()
        self._runner = runner

    def validate_voice(self, voice_id: str) -> None:
        if not voice_id or not voice_id.strip():
            raise TTSBackendError("Voice IDs must be non-empty for the qwen TTS backend.")

    def synthesize(
        self,
        text: str,
        voice_id: str,
        speed: float,
        speaker_role: str,
    ) -> tuple[int, bytes]:
        del speaker_role
        if abs(speed - 1.0) > 1e-9:
            raise TTSBackendError(
                "The local qwen TTS script does not expose playback speed control; use speed 1.0."
            )

        with tempfile.TemporaryDirectory(prefix="quortol-qwen-tts-") as temp_dir:
            temp_root = Path(temp_dir)
            text_path = temp_root / "input.txt"
            output_path = temp_root / "output.wav"
            text_path.write_text(text, encoding="utf-8")

            command = [
                "conda",
                "run",
                "--no-capture-output",
                "--name",
                self.conda_env,
                "python",
                "-m",
                self.module_name,
                "--text-file",
                str(text_path),
                "--out",
                str(output_path),
                "--speaker",
                voice_id,
                "--language",
                self.language,
            ]
            if self.model:
                command.extend(["--model", self.model])
            command.extend(self.extra_args)

            try:
                result = self._runner(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except Exception as exc:
                raise TTSBackendError(f"Qwen TTS command failed to start: {exc}") from exc

            if getattr(result, "returncode", 1) != 0:
                stderr = str(getattr(result, "stderr", "") or "").strip()
                stdout = str(getattr(result, "stdout", "") or "").strip()
                details = stderr or stdout or "unknown subprocess failure"
                raise TTSBackendError(f"Qwen TTS command failed: {details}")

            try:
                audio_bytes = output_path.read_bytes()
            except OSError as exc:
                raise TTSBackendError("Qwen TTS command did not produce an output WAV file.") from exc

        if not audio_bytes:
            raise TTSBackendError("Qwen TTS backend returned an empty audio payload.")

        return wav_bytes_to_pcm16(audio_bytes)

    def describe(self) -> dict[str, Any]:
        payload = TTSBackendMetadata(
            backend=self.backend_id,
            model=self.model or None,
        ).to_manifest_payload()
        payload["conda_env"] = self.conda_env
        payload["module"] = self.module_name
        payload["language"] = self.language
        return payload
