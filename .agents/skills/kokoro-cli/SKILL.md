---
name: kokoro-cli
description: Use the local Kokoro playback CLI to speak text aloud on Windows with minimal agent effort. Trigger this skill when Codex needs to play short text through local speakers, wait for playback to finish, adjust speed or volume, save a WAV file, or inspect the CLI with `--help`.
---

# Kokoro CLI

Use the existing local CLI instead of building a new TTS flow.

## Command

Prefer the Windows launcher:

```powershell
.\scripts\kokoro-cli.cmd play "hello world" --wait
```

Fallback to Python directly if needed:

```powershell
python scripts/kokoro_cli.py play "hello world" --wait
```

## Workflow

1. Check usage first if flags or behavior are unclear:

```powershell
.\scripts\kokoro-cli.cmd --help
.\scripts\kokoro-cli.cmd play --help
```

2. Use quoted positional text for normal playback:

```powershell
.\scripts\kokoro-cli.cmd play "hello world" --wait
```

3. Adjust pacing or loudness when requested:

```powershell
.\scripts\kokoro-cli.cmd play "hello world" --speed 1.15 --volume 0.8 --wait
```

4. Save audio instead of playing it when the user wants a file:

```powershell
.\scripts\kokoro-cli.cmd play "hello world" --output hello.wav --no-play
```

## Defaults

- Use `--wait` for normal agent-driven playback so the caller can block until audio finishes.
- Omit `--voice` unless the user asks for a specific voice. The default is already tuned for the repo.
- Keep utterances fairly short when possible for faster response.
- Use stdin only when quoted positional text is awkward:

```powershell
"hello world" | .\scripts\kokoro-cli.cmd play --wait
```

## Troubleshooting

- If playback dependencies are missing, install:

```powershell
pip install -r scripts/requirements-kokoro.txt
```

- If Kokoro fails on Windows, ensure `espeak-ng` is installed.
- If local playback is not desired, switch to `--no-play --output <file>`.
