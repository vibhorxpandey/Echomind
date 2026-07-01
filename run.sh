#!/usr/bin/env bash
# EchoMind dev-up (Git Bash / Linux / macOS).
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY=".venv/Scripts/python.exe"; [ -f "$PY" ] || PY=".venv/bin/python"

if [ ! -d .venv ]; then
  echo "[echomind] creating venv + installing python deps..."
  python -m venv .venv
  "$PY" -m pip install -q -r requirements.txt
fi

if [ ! -f data/club_docs.json ]; then
  echo "[echomind] generating dataset..."
  "$PY" data/generate_dataset.py
fi

if [ ! -d frontend/node_modules ]; then
  echo "[echomind] installing frontend deps..."
  (cd frontend && npm install --no-audit --no-fund)
fi

echo "[echomind] starting backend on :8000 (ingests into Qdrant on first run)..."
"$PY" -m uvicorn backend.main:app --port 8000 &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null" EXIT

echo "[echomind] starting frontend on :3000..."
cd frontend && npm run dev
