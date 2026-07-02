# Deployment

## Frontend (Vercel, static export)
The Next.js app is built with `output: 'export'` and served from `frontend/`.

```bash
cd frontend
vercel --prod --yes --scope <team>
vercel alias set <deployment-url> echomindai.vercel.app --scope <team>
```

Live: https://echomindai.vercel.app

`.npmrc` sets `legacy-peer-deps=true` so the cloud install matches local.

## Backend (local)
The retrieval stack (fastembed + embedded Qdrant + ADK) runs locally:

```bash
.venv/Scripts/python -m uvicorn backend.main:app --port 8000
```

The hosted frontend calls `http://localhost:8000` from the browser (Chrome's
localhost secure-context carve-out), so a locally-run backend powers live chat.
To point at a hosted backend, set `NEXT_PUBLIC_API_URL` in Vercel env and redeploy.

## Env vars
See `.env.example` — `GOOGLE_API_KEY` (agent), `QDRANT_URL` / `QDRANT_API_KEY`
(optional Cloud), `LYZR_API_KEY` (optional).
