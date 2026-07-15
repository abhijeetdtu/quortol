#!/usr/bin/env python3
"""Local Chatterbox batch TTS chunker vendored into this repository."""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
import time
from contextlib import nullcontext
from pathlib import Path

import perth
import psutil
import soundfile as sf
import torch

from chatterbox.tts import ChatterboxTTS, S3GEN_SR

from scripts.tts_helpers import (
    chunk_text,
    read_text_with_fallback,
    stitch_wav_files,
)


logger = logging.getLogger("scripts.chatterbox_tts_chunk")


def _patch_perth_watermarker() -> None:
    watermarker_cls = getattr(perth, "PerthImplicitWatermarker", None)
    if watermarker_cls is None:
        logger.warning(
            "PerthImplicitWatermarker is unavailable; falling back to DummyWatermarker."
        )
        perth.PerthImplicitWatermarker = perth.DummyWatermarker


def _sync_device(device: str) -> None:
    if device == "cuda" and torch.cuda.is_available():
        torch.cuda.synchronize()
    elif device == "mps" and torch.backends.mps.is_available():
        torch.mps.synchronize()


def _set_process_priority(high_priority: bool) -> None:
    if not high_priority:
        return
    try:
        process = psutil.Process(os.getpid())
        if os.name == "nt":
            process.nice(psutil.HIGH_PRIORITY_CLASS)
            logger.info("Process priority set to HIGH_PRIORITY_CLASS")
        else:
            process.nice(-5)
            logger.info("Raised process priority via niceness")
    except Exception as exc:
        logger.warning("Unable to raise process priority: %s", exc)


def _resolve_device(requested_device: str | None) -> str:
    if requested_device is not None:
        return requested_device
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _autocast_context(device: str, enabled: bool):
    if not enabled or device not in {"cuda", "mps"}:
        return nullcontext()
    return torch.autocast(device_type=device, dtype=torch.float16, enabled=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        prog="chatterbox-tts-chunk",
        description="Chunk long text and synthesize it to a mono WAV via Chatterbox.",
    )
    parser.add_argument("--text", type=str, help="Text to synthesize.")
    parser.add_argument("--text-file", type=Path, help="Path to a text file to synthesize.")
    parser.add_argument(
        "--text-encoding",
        type=str,
        default=None,
        help="Optional input file encoding (e.g. utf-8, cp1252).",
    )
    parser.add_argument("--out", type=Path, default=Path("chatterbox_out.wav"))
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Target device: cuda, mps, or cpu.",
    )
    parser.add_argument("--max-chars", type=int, default=300)
    parser.add_argument("--voice", type=Path, required=True, help="Reference WAV/MP3 for cloning.")
    parser.add_argument(
        "--chunk-dir",
        type=Path,
        default=None,
        help="Directory to store per-chunk WAV files.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip chunks that already exist in the chunk directory.",
    )
    parser.add_argument(
        "--keep-chunks",
        action="store_true",
        help="Keep per-chunk WAV files after stitching the final output.",
    )
    parser.add_argument(
        "--high-priority",
        action="store_true",
        help="Raise process priority during synthesis.",
    )
    parser.add_argument(
        "--autocast",
        action="store_true",
        help="Enable float16 autocast on CUDA/MPS for faster inference.",
    )
    parser.add_argument(
        "--exaggeration",
        type=float,
        default=0.5,
        help="Emotion/exaggeration strength passed to conditioning.",
    )
    parser.add_argument(
        "--cfg-weight",
        type=float,
        default=0.5,
        help="Classifier-free guidance weight.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Sampling temperature.",
    )
    parser.add_argument("--top-p", type=float, default=1.0, help="Nucleus sampling value.")
    parser.add_argument(
        "--min-p",
        type=float,
        default=0.05,
        help="Minimum probability threshold.",
    )
    parser.add_argument(
        "--repetition-penalty",
        type=float,
        default=1.2,
        help="Penalty for repeated tokens.",
    )
    args = parser.parse_args()

    if not args.text and not args.text_file:
        parser.error("Provide --text or --text-file")

    text = (
        read_text_with_fallback(args.text_file, args.text_encoding)
        if args.text_file
        else args.text or ""
    ).strip()
    if not text:
        raise SystemExit("Empty text")

    if not args.voice.exists():
        raise SystemExit(f"Voice reference not found: {args.voice}")

    device = _resolve_device(args.device)
    logger.info("Config: %s", vars(args))
    logger.info("Device: %s", device)

    _set_process_priority(args.high_priority)
    _patch_perth_watermarker()

    model = ChatterboxTTS.from_pretrained(device=device)
    model.prepare_conditionals(
        str(args.voice),
        exaggeration=args.exaggeration,
    )

    chunks = chunk_text(text, args.max_chars)
    if not chunks:
        raise SystemExit("No chunks to synthesize")

    temp_paths: list[Path] = []
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.chunk_dir is not None:
        chunk_root = args.chunk_dir
        chunk_root.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="quortol-chatterbox-")
        chunk_root = Path(temp_dir.name)

    synthesis_wall_seconds = 0.0
    generated_audio_seconds = 0.0

    for index, chunk in enumerate(chunks, start=1):
        temp_path = chunk_root / f"chunk_{index:04d}.wav"
        if args.resume and temp_path.exists():
            print(f"[{index}/{len(chunks)}] exists, skipping")
            temp_paths.append(temp_path)
            continue

        print(f"[{index}/{len(chunks)}] {len(chunk)} chars")
        _sync_device(device)
        started = time.perf_counter()
        with torch.inference_mode():
            with _autocast_context(device, args.autocast):
                wav = model.generate(
                    chunk,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    min_p=args.min_p,
                    cfg_weight=args.cfg_weight,
                    exaggeration=args.exaggeration,
                    repetition_penalty=args.repetition_penalty,
                )
                wav_np = wav.squeeze().detach().cpu().numpy()
        _sync_device(device)

        elapsed = time.perf_counter() - started
        audio_seconds = float(len(wav_np)) / float(S3GEN_SR)
        chunk_rtf = elapsed / audio_seconds if audio_seconds > 0 else float("inf")
        synthesis_wall_seconds += elapsed
        generated_audio_seconds += audio_seconds

        sf.write(temp_path, wav_np, S3GEN_SR, subtype="FLOAT")
        temp_paths.append(temp_path)
        print(
            f"[{index}/{len(chunks)}] wall={elapsed:.2f}s "
            f"audio={audio_seconds:.2f}s rtf={chunk_rtf:.3f}"
        )

        if index % 10 == 0:
            time.sleep(5)

    if not temp_paths:
        if temp_dir is not None and not args.keep_chunks:
            temp_dir.cleanup()
        raise SystemExit("No audio generated")

    total_output_audio_seconds = 0.0
    for path in temp_paths:
        with sf.SoundFile(path, mode="r") as input_file:
            total_output_audio_seconds += len(input_file) / float(input_file.samplerate)

    stitch_wav_files(temp_paths, args.out, samplerate=S3GEN_SR, subtype="PCM_16")

    if not args.keep_chunks:
        if temp_dir is not None:
            temp_dir.cleanup()

    print(f"Saved: {args.out}")
    if generated_audio_seconds > 0:
        overall_rtf = synthesis_wall_seconds / generated_audio_seconds
        print(
            f"Generated audio: {generated_audio_seconds:.2f}s, "
            f"synthesis wall time: {synthesis_wall_seconds:.2f}s, "
            f"RTF: {overall_rtf:.3f}"
        )
    if total_output_audio_seconds > 0:
        print(f"Final stitched audio duration: {total_output_audio_seconds:.2f}s")


if __name__ == "__main__":
    main()
