"""Kokoro adapter for podcast generation."""

from __future__ import annotations

from typing import Any, Callable

import kokoro_cli

from .base import TTSBackendError, TTSBackendMetadata


KokoroSynthesizer = Callable[[str, str, float, str], tuple[int, Any]]


class KokoroTTSBackend:
    """Wrap the existing Kokoro synthesis path behind a backend interface."""

    backend_id = "kokoro"

    def __init__(
        self,
        *,
        synthesizer: KokoroSynthesizer = kokoro_cli.synthesize_with_kokoro,
    ) -> None:
        self._synthesizer = synthesizer
        self._supported_voices = kokoro_cli.get_supported_voices()

    def validate_voice(self, voice_id: str) -> None:
        if voice_id not in self._supported_voices:
            supported = ", ".join(sorted(self._supported_voices))
            raise TTSBackendError(
                f"Unsupported Kokoro voice '{voice_id}'. Supported voices: {supported}."
            )

    def synthesize(
        self,
        text: str,
        voice_id: str,
        speed: float,
        speaker_role: str,
    ) -> tuple[int, Any]:
        del speaker_role
        lang_code = kokoro_cli.infer_lang_code(voice_id)
        return self._synthesizer(text, voice_id, speed, lang_code)

    def describe(self) -> dict[str, Any]:
        return TTSBackendMetadata(backend=self.backend_id).to_manifest_payload()
