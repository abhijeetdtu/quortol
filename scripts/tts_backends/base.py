"""Shared primitives for pluggable podcast TTS backends."""

from __future__ import annotations

import io
import wave
from dataclasses import dataclass
from typing import Any


class TTSBackendError(Exception):
    """Raised when a configured TTS backend cannot fulfill a request."""


@dataclass(frozen=True)
class TTSBackendMetadata:
    """Serializable metadata describing a backend invocation."""

    backend: str
    output_format: str = "wav"
    model: str | None = None

    def to_manifest_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "backend": self.backend,
            "output_format": self.output_format,
        }
        if self.model:
            payload["model"] = self.model
        return payload


def wav_bytes_to_pcm16(audio_bytes: bytes) -> tuple[int, bytes]:
    """Validate a WAV payload and return sample rate plus raw PCM frames."""
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            frames = wav_file.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise TTSBackendError("TTS backend did not return a valid WAV payload.") from exc

    if channels != 1:
        raise TTSBackendError("TTS backend must return mono WAV audio.")
    if sample_width != 2:
        raise TTSBackendError("TTS backend must return 16-bit PCM WAV audio.")
    if sample_rate <= 0:
        raise TTSBackendError("TTS backend returned an invalid sample rate.")

    return sample_rate, frames
