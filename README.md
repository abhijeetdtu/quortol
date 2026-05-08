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

```bash
# Terminal 2
cd frontend
npm run dev -- --host localhost --port 8050
```

```bash
# Terminal 3 (named tunnel)
cloudflared tunnel run quortol-dev
```

If your tunnel is installed as a system service, use this instead of Terminal 3:

```bash
sudo systemctl restart cloudflared
```

## Deployment

- Cloudflare Tunnel dev-stack guide for `https://pokhi.in/`: [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md)
