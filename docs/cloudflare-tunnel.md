# Quortol Cloudflare Tunnel Setup (`quortol.pokhi.in`)

This guide exposes Quortol through Cloudflare Tunnel at `https://quortol.pokhi.in/`.

## What This Setup Does

- Serves the frontend from `http://127.0.0.1:8050` through Cloudflare Tunnel.
- Keeps API requests on the same domain via the production server proxy:
  - Browser calls `https://quortol.pokhi.in/api/...`
  - The production server proxies `/api` to backend `http://127.0.0.1:5000`
- Serves route-specific files from `frontend/dist` so `/blog` resolves to
  `frontend/dist/blog/index.html` instead of the generic SPA shell.

## Preconditions

- Domain `pokhi.in` is active in your Cloudflare account and DNS is managed by Cloudflare.
- Ubuntu/Debian host with sudo access.
- Quortol backend running on `127.0.0.1:5000`.
- Quortol production build served on `127.0.0.1:8050`.

## Install Node.js and npm (if missing)

Install `nvm`:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Activate `nvm` in the current shell (or restart terminal):

```bash
source ~/.bashrc
```

Install Node.js LTS (includes `npm`):

```bash
nvm install --lts
```

Verify install:

```bash
node -v
npm -v
```

Start Quortol first:

```bash
# From repo root
python -m backend.app
```

```bash
# In another terminal
cd frontend
npm install
npm run build
npm run serve
```

## 1) Install cloudflared

```bash
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-main.gpg
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update
sudo apt install -y cloudflared
```

## 2) Authenticate and Create Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create quortol-dev
```

Save the generated tunnel UUID shown in output. It appears in `~/.cloudflared/` and is used below as `<TUNNEL_UUID>`.

## 3) Route `quortol.pokhi.in` DNS to the Tunnel

```bash
cloudflared tunnel route dns quortol-dev quortol.pokhi.in
```

This creates or updates the Cloudflare DNS record for the canonical subdomain.

## 4) Create Tunnel Config

Create `/etc/cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /root/.cloudflared/<TUNNEL_UUID>.json

ingress:
  - hostname: quortol.pokhi.in
    service: http://127.0.0.1:8050
  - service: http_status:404
```

```bash
cp ~/Documents/code/quortol/docs/cloudflare.yaml /home/pi/.cloudflared/config.yml
```
If you ran `cloudflared tunnel login` as a non-root user, either:
- copy credentials to `/root/.cloudflared/`, or
- adjust `credentials-file` to the correct user path and run the service under that user.

## 5) Run as a Systemd Service

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl restart cloudflared
```

## 6) Verify

```bash
sudo systemctl status cloudflared --no-pager
cloudflared tunnel list
```

Then test in a browser or with curl:

```bash
curl -I https://quortol.pokhi.in/
curl -i https://quortol.pokhi.in/api/blog/
curl -i https://quortol.pokhi.in/robots.txt
curl -i https://quortol.pokhi.in/sitemap.xml
```

Expected:
- `https://quortol.pokhi.in/` returns the frontend app.
- `https://quortol.pokhi.in/api/blog/` returns backend JSON, proving `/api` proxying works.
- Public routes return prerendered HTML with `quortol.pokhi.in` canonical URLs.

## Troubleshooting

### `/api` endpoints fail but homepage loads

- Confirm frontend is running on `127.0.0.1:8050`.
- Confirm backend is running on `127.0.0.1:5000`.
- Confirm `BACKEND_ORIGIN` is unset or points to the backend:
  - default: `http://127.0.0.1:5000`

### Port mismatch or service unavailable

- Check local listeners:
  ```bash
  ss -ltnp | grep -E ':(5000|8050)\b'
  ```
- Ensure the tunnel ingress points to `http://127.0.0.1:8050`.

### DNS not resolving to tunnel yet

- Wait for propagation (usually quick, can take a few minutes).
- Re-run:
  ```bash
  cloudflared tunnel route dns quortol-dev quortol.pokhi.in
  ```
- Verify DNS in Cloudflare dashboard.

### Cloudflared service errors

- Check logs:
  ```bash
  sudo journalctl -u cloudflared -n 200 --no-pager
  ```
- Verify `tunnel`, `credentials-file`, and ingress entries in `/etc/cloudflared/config.yml`.

### Flask-SQLAlchemy "app is not registered" on Raspberry Pi

If you see:

`RuntimeError: The current Flask app is not registered with this 'SQLAlchemy' instance`

- Start backend from the project root (not from inside `backend/`):
  ```bash
  cd /home/pi/path/to/quortol
  python -m backend.app
  ```
- Avoid mixed startup/import patterns in the same environment (for example combining `python backend/app.py` and `flask run` with different `FLASK_APP` values).
- If using systemd or gunicorn, keep one canonical import path:
  - `backend.app:create_app()` (factory), or
  - `python -m backend.app` for dev.

## Reboot Persistence Check

After reboot:

```bash
systemctl is-enabled cloudflared
systemctl is-active cloudflared
```

Expected:
- `is-enabled` returns `enabled`
- `is-active` returns `active`
