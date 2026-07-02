PY=.venv/Scripts/python

.PHONY: dev backend frontend ingest ablation

dev:
	bash run.sh

backend:
	$(PY) -m uvicorn backend.main:app --port 8000

frontend:
	cd frontend && npm run dev

ingest:
	curl -X POST localhost:8000/ingest

ablation:
	$(PY) scripts/ablation.py
