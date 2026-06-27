# Umami Analytics Setup

This repo integrates with a separately hosted Umami instance through the Quortol production server.

## Architecture

- Quortol frontend loads the tracker from `/umami/script.js`
- Quortol production server proxies `/umami/*` to `UMAMI_ORIGIN`
- Umami itself is not vendored or deployed from this repo

## 1) Run Umami on the host

The example below is intentionally host-side only. Keep it outside this repo, for example in `~/services/umami/compose.yaml`.

```yaml
services:
  umami:
    image: docker.umami.is/umami-software/umami:latest
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      DATABASE_URL: postgresql://umami:umami@db:5432/umami
      APP_SECRET: change-this-secret
    depends_on:
      - db

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: umami
      POSTGRES_USER: umami
      POSTGRES_PASSWORD: umami
    volumes:
      - umami-postgres:/var/lib/postgresql/data

volumes:
  umami-postgres:
```

Start it:

```bash
docker compose up -d
```

Then open `http://127.0.0.1:3001`, create or log in to the admin user, and add `quortol.pokhi.in` as a website to get the website ID.

## 2) Configure Quortol

Set these environment variables before building and serving Quortol:

```bash
export UMAMI_ORIGIN=http://127.0.0.1:3001
export VITE_UMAMI_ENABLED=true
export VITE_UMAMI_WEBSITE_ID=<website-id-from-umami>
export VITE_UMAMI_HOST_URL=/umami
export VITE_UMAMI_DOMAINS=quortol.pokhi.in
export VITE_UMAMI_TRACK_PERFORMANCE=false
```

Build and serve:

```bash
cd frontend
npm run build
npm run serve
```

## 3) Validate

Confirm the tracker is reachable through Quortol:

```bash
curl -I http://127.0.0.1:8050/umami/script.js
```

Open `https://quortol.pokhi.in/blog` and verify pageviews appear in Umami.

The current Quortol integration tracks:

- manual SPA pageviews on public routes
- `podcast_audio_play`
- `blog_external_link_click`
- `shorts_search`
- `shorts_filter_apply`

## 4) Privacy defaults

This integration intentionally:

- skips `/agent/*` pages
- does not send raw search terms
- does not send full outbound URLs for blog link clicks
- respects browser Do Not Track through the tracker script configuration

## References

- Umami install docs: `https://docs.umami.is/docs/install`
- Umami tracker functions: `https://docs.umami.is/docs/tracker-functions`
- Umami tracker configuration: `https://docs.umami.is/docs/tracker-configuration`
