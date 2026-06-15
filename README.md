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
- synthesizes each speaker turn with Kokoro
- writes `script.md`, `manifest.json`, and `episode.wav` per blog under `backend/static/podcasts`

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
- `--output-dir <custom-output-root>`
- `--host-a-voice af_heart`
- `--host-b-voice am_fenrir`

## Notes

- Start the backend first, then the frontend
- Both must be running simultaneously for the application to work
- The router fix (importing `useAuthStore`) resolves the navigation guard errors

## Quick Startup (Backend + Frontend + Tunnel)

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
npm run dev -- --host localhost --port 8050
```

```bash
nohup npm run dev > frontend.log 2>&1 &
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

- Cloudflare Tunnel dev-stack guide for `https://pokhi.in/`: [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md)
- SEO indexing checklist: [docs/seo-indexing-checklist.md](docs/seo-indexing-checklist.md)

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


