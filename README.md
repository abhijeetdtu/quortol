# Quortol

A full-stack application with Vue 3 frontend and Flask backend.

## Prerequisites

- Node.js (v16+)
- Python (v3.8+)

## Getting Started

### Backend

1. Create environment from environment.yml (requires Conda):
   ```
   conda env create -f backend/environment.yml
   conda activate quortol
   ```

2. Start the backend server from the project root:
   ```
   python -m backend.app
   ```

The backend will run on `http://localhost:5000`

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

The frontend will run on `http://localhost:8050`

## Kokoro CLI

For local agent-friendly text-to-speech on Windows, install the Kokoro CLI dependencies:

```bash
pip install -r scripts/requirements-kokoro.txt
```

You also need `espeak-ng` installed for the Python Kokoro stack on Windows.

Quick usage:

```bash
python scripts/kokoro_cli.py --help
python scripts/kokoro_cli.py doctor
python scripts/kokoro_cli.py play "hello world" --wait
python scripts/kokoro_cli.py play "hello world" --speed 1.15 --volume 0.8 --wait
```

Windows launcher:

```bash
.\scripts\kokoro-cli.cmd --help
.\scripts\kokoro-cli.cmd doctor
.\scripts\kokoro-cli.cmd play "hello world" --wait
.\scripts\kokoro-cli.cmd play "hello world" --speed 1.15 --volume 0.8 --wait
```

## Batch Blog-to-Podcast

This repo also includes an offline batch generator that:

- reads blog markdown from `backend/blogs`
- asks a local `llama-server` to convert each post into a two-host podcast script
- synthesizes each speaker turn through a pluggable TTS backend (`kokoro` or `qwen`)
- writes `script.md`, `manifest.json`, and `episode.wav` per blog under `backend/static/podcasts`
- reuses an existing `script.md` and goes straight to TTS unless you pass `--force`

Quick usage:

```bash
python scripts/generate_blog_podcasts.py --slug india-political-parties-evolution
python scripts/generate_blog_podcasts.py --file backend/blogs/india-political-parties-evolution.md
python scripts/generate_blog_podcasts.py --all --dry-run
python scripts/generate_blog_podcasts.py --all --force --keep-segments
```

Windows launcher:

```bash
.\scripts\generate-blog-podcasts.cmd --slug india-political-parties-evolution
```

Useful flags:

- `--endpoint http://127.0.0.1:8080/v1/chat/completions`
- `--model <optional-model-name>`
- `--tts-backend kokoro`
- `--tts-conda-env qwen3-tts-cuda`
- `--tts-model <optional-tts-model-name>`
- `--tts-language English`
- `--tts-extra-arg --device-map`
- `--tts-extra-arg cuda:0`
- `--output-dir <custom-output-root>`
- `--host-a-voice af_heart`
- `--host-b-voice am_fenrir`

Qwen backend contract:

- `quortol` vendors and invokes `scripts.qwen3_tts_chunk` from this repo
- execution happens through `conda run --name <env> python -m scripts.qwen3_tts_chunk`
- the selected speaker voice ID is forwarded as `--speaker`
- language is forwarded as `--language`
- model is forwarded as `--model` when present
- the script must write a mono 16-bit PCM WAV file to the provided `--out` path
- generated manifests record `episode.tts.backend`, optional `episode.tts.model`, and backend-specific voice IDs
- qwen defaults are `Ryan` for journalist and `Aiden` for author unless overridden

## Batch Blog-to-Audiobook

This repo also includes an offline batch generator that:

- reads blog markdown from `backend/blogs`
- converts each post into cleaned spoken text via `backend.blog_markdown.markdown_to_spoken_text()`
- synthesizes a single-narrator audiobook WAV through local Chatterbox chunked TTS
- writes `spoken_text.txt`, `manifest.json`, and `audiobook.wav` per blog under `backend/static/audiobooks`
- optionally keeps reusable chunk WAVs for resume/retry workflows

Install the Chatterbox CLI dependencies:

```bash
pip install -r scripts/requirements-chatterbox.txt
```

Quick usage:

```bash
conda run --no-capture-output -n chatterbox-tts-blackwell python scripts/generate_blog_audiobooks.py --slug american-byways --voice "C:\Users\abhij\Code\bringalive\app\voices\voice_my.mp3" --keep-chunks

conda run --no-capture-output -n chatterbox-tts-blackwell `
python scripts/generate_blog_audiobooks.py --file "backend\blogs\nashua-mill-town-story.md" --voice "C:\Users\abhij\Code\bringalive\app\voices\voice_jake_baldino.mp3" --keep-chunks

python scripts/generate_blog_audiobooks.py --all --voice C:\path\to\voice.wav --dry-run
python scripts/generate_blog_audiobooks.py --all --voice C:\path\to\voice.wav --keep-chunks --resume
```

Windows launcher:

```bash
.\scripts\generate-blog-audiobooks.cmd --slug additive-arithmetic --voice C:\path\to\voice.wav
```

Useful flags:

- `--output-dir <custom-output-root>`
- `--chunk-dir <custom-chunk-root>`
- `--device cuda`
- `--max-chars 300`
- `--high-priority`
- `--autocast`
- `--temperature 0.8`
- `--top-p 1.0`
- `--min-p 0.05`
- `--cfg-weight 0.5`
- `--exaggeration 0.5`
- `--repetition-penalty 1.2`

## Notes

- Start the backend first, then the frontend
- Both must be running simultaneously for the application to work
- The router fix (importing `useAuthStore`) resolves the navigation guard errors

## Quick Production Startup (Backend + Frontend + Tunnel)

From the repo root, run these in 3 terminals:

```bash
# Terminal 1
python -m backend.app
```

restarting
```bash
pkill -f "backend.app" || true
source ~/Documents/code/ds/bin/activate
cd ~/Documents/code/quortol
nohup python -m backend.app > backend.log 2>&1 &
```
```bash
# Terminal 2
cd frontend
npm install
npm run build
npm run serve
```

`npm run serve` serves route-specific prerendered files such as
`dist/blog/index.html`, proxies backend paths to `127.0.0.1:5000`, and can proxy `/umami/*` to `UMAMI_ORIGIN`.

To run it in the background instead:

```bash
cd frontend
npm run build
pkill -f "serve-production.mjs" || true
nohup npm run serve > frontend.log 2>&1 &
disown
```

```bash
# Terminal 3 (named tunnel)
nohup cloudflared tunnel run quortol-dev
```

If your tunnel is installed as a system service, use this instead of Terminal 3:

```bash
sudo systemctl restart cloudflared
```

## Deployment

- Cloudflare Tunnel deployment guide for `https://quortol.pokhi.in/`: [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md)
- SEO indexing checklist: [docs/seo-indexing-checklist.md](docs/seo-indexing-checklist.md)
- Umami analytics setup: [docs/umami-setup.md](docs/umami-setup.md)

## Umami Analytics

Quortol supports optional Umami analytics without vendoring Umami into this repo.

- Browser traffic is sent to the same origin under `/umami/*`
- `frontend/scripts/serve-production.mjs` proxies `/umami/*` to `UMAMI_ORIGIN`
- Tracking stays off unless both `VITE_UMAMI_ENABLED=true` and `VITE_UMAMI_WEBSITE_ID` are set at build time

Recommended environment variables:

```bash
UMAMI_ORIGIN=http://127.0.0.1:3001
VITE_UMAMI_ENABLED=true
VITE_UMAMI_WEBSITE_ID=<your-umami-website-id>
VITE_UMAMI_HOST_URL=/umami
VITE_UMAMI_DOMAINS=quortol.pokhi.in
VITE_UMAMI_TRACK_PERFORMANCE=false
```

Build-time note: `VITE_*` values must be present when you run `npm run build`, for example by exporting them in your shell or placing them in `frontend/.env.local`.

## SEO Utilities

From `frontend/`, regenerate sitemap entries (including blog slugs from `backend/blogs/*.md`):

```bash
npm run seo:generate-sitemap
```

`npm run build` now runs sitemap generation automatically before Vite build.



## LLama Server

```bash
llama-server `
   -hf unsloth/Qwen3.5-35B-A3B-GGUF:IQ2_M `
   --host 127.0.0.1 `
   --port 8080 `
   -ngl all `
   -c 163840 `
   -b 4096 `
   -ub 512 `
   --flash-attn on `
   --cache-type-k q8_0 `
   --cache-type-v q8_0 `
   --cache-ram 0 `
   --ctx-checkpoints 4 `
   -np 1 `
   --cont-batching `
   --no-webui `
   --jinja
```

```bash
llama-server `
  -hf unsloth/Qwen3.5-35B-A3B-GGUF:IQ2_M `
  --host 127.0.0.1 `
  --port 8080 `
  -ngl all `
  -c 32768 `
  -b 4096 `
  -ub 512 `
  -np 1 `
  --cont-batching `
  --flash-attn on `
  --cache-type-k q8_0 `
  --cache-type-v q8_0 `
  --cache-ram 0 `
  --ctx-checkpoints 4 `
  --fit on `
  --fit-ctx 32000 `
  --jinja `
  --no-webui `
  --temp 0.6 `
  --top-p 0.95 `
  --top-k 20 `
  --min-p 0.0 `
  --presence-penalty 1.5 `
  --repeat-penalty 1.0 `
  --chat-template-kwargs '{\"preserve_thinking\":true}' `
  --log-verbosity 4
```

```bash
.\llama-server `
    -hf unsloth/GLM-4.7-Flash-GGUF:Q3_K_XL `
    --host 127.0.0.1 `
    --port 8080 `
    -ngl all `
    -c 40000 `
    -b 4096 `
    -ub 1024 `
    -np 1 `
    --cont-batching `
    --flash-attn on `
    --cache-type-k q4_0 `
    --cache-type-v q4_0 `
    --ctx-checkpoints 12 `
    --fit on `
    --fit-ctx 50000 `
    --jinja `
    --no-webui `
    --temp 0.6 `
    --top-p 0.95 `
    --top-k 20 `
    --min-p 0.0 `
    --presence-penalty 1.5 `
    --repeat-penalty 1.0 `
    --chat-template-kwargs '{\"preserve_thinking\":true}' `
    --log-verbosity 4
```


```bash
 .\llama-server `
     -hf unsloth/Qwen3.5-9B-GGUF:Q8_0 `
     --host 127.0.0.1 `
     --port 8080 `
     -ngl all `
     -np 1 `
     --cont-batching `
     --flash-attn on `
     --cache-type-k q4_0 `
     --cache-type-v q4_0 `
     --ctx-checkpoints 12 `
     --fit on `
     --fit-ctx 50000 `
     --jinja `
     --no-webui `
     --temp 0.75 `
     --top-p 1 `
     --top-k 20 `
     --min-p 0.0 `
     --presence-penalty 1.5 `
     --repeat-penalty 1 `
     --repeat-last-n 128 `
     --dry-multiplier 0.4 `
     --dry-base 1.75 `
     --dry-allowed-length 4 `
     --dry-penalty-last-n 512 `
     --log-verbosity 4
```
# blog removal

```bash
slug="readme" \
&& rm -f "backend/blogs/${slug}.md" \
&& SLUG="$slug" python3 - <<'PY'
import os
from backend.app import create_app
from backend.extensions import db
from backend.models import BlogPost

slug = os.environ["SLUG"]
app = create_app()
with app.app_context():
    post = BlogPost.query.filter_by(slug=slug).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        print(f"Deleted: {slug}")
    else:
        print(f"Not found in DB: {slug}")
PY
```


