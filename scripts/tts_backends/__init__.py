"""Registry for podcast TTS backends."""

from __future__ import annotations

import subprocess
from typing import Any, Callable

import kokoro_cli

from .base import TTSBackendError
from .kokoro import KokoroTTSBackend
from .qwen import QwenTTSBackend


KokoroSynthesizer = Callable[[str, str, float, str], tuple[int, Any]]
Runner = Callable[..., Any]


def create_tts_backend(
    backend_id: str,
    *,
    tts_conda_env: str = "qwen3-tts-cuda",
    tts_model: str = "",
    tts_language: str = "english",
    tts_extra_args: list[str] | None = None,
    kokoro_synthesizer: KokoroSynthesizer = kokoro_cli.synthesize_with_kokoro,
    tts_runner: Runner | None = None,
):
    normalized = (backend_id or "kokoro").strip().lower()
    if normalized == "kokoro":
        return KokoroTTSBackend(synthesizer=kokoro_synthesizer)
    if normalized == "qwen":
        return QwenTTSBackend(
            conda_env=tts_conda_env,
            model=tts_model,
            language=tts_language,
            extra_args=tts_extra_args,
            runner=tts_runner if tts_runner is not None else subprocess.run,
        )
    raise TTSBackendError(
        f"Unsupported TTS backend '{backend_id}'. Supported backends: kokoro, qwen."
    )


__all__ = [
    "KokoroTTSBackend",
    "QwenTTSBackend",
    "TTSBackendError",
    "create_tts_backend",
]
