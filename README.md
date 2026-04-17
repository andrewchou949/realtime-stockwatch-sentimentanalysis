# Stock Watch

Stock Watch is a portfolio project for building a real-time stock monitoring app, starting with a small alerting MVP and expanding toward AI-assisted market insight features.

The repository currently contains:

- project-level planning and requirements
- a defined `v0` MVP scope
- a working `v0` backend and separated frontend app

## Current Status

This repo is in an early implementation phase.

Implemented today:

- FastAPI app bootstrap
- SQLite database setup with SQLAlchemy
- `watchlist` and `alerts` data models
- startup table creation
- watchlist, prices, alerts, and refresh endpoints
- `/healthz` API endpoint
- separated React + Vite frontend in `v0/frontend`

Planned next:

- frontend polish
- provider hardening and error handling
- end-to-end demo workflow cleanup

## Repository Layout

```text
.
├── README.md
├── LICENSE
├── ProjectDocumentation/
│   └── Project_SRS.docx
└── v0/
    ├── README.md
    ├── backend/
    │   ├── README.md
    │   ├── requirements.txt
    │   ├── app/
    │   └── tests/
    └── frontend/
        ├── README.md
        ├── package.json
        └── src/
```

## Product Direction

The longer-term goal is an end-to-end dashboard that combines:

- stock watchlists and threshold alerts
- market/news ingestion
- sentiment and emotion analysis
- event-to-price correlation
- eventually, richer real-time pipelines and strategy tooling

That broader vision is intentionally staged. The project starts with a narrow, demoable `v0` before moving into AI-heavy features.

## MVP Scope

The first milestone is a portfolio-ready baseline:

1. Add and remove ticker symbols from a watchlist.
2. Store a baseline price and threshold per ticker.
3. Fetch current prices from a single provider.
4. Trigger alerts when price movement crosses the threshold.
5. Persist alert history in SQLite.
6. Expose the flow through a small API and minimal UI.

Detailed `v0` scope lives in [`v0/README.md`](v0/README.md).

## v0 Quick Start

Start the backend:

```bash
cd v0/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```bash
cd v0/frontend
npm install
npm run dev
```

Then open:

- API root: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/healthz`
- Frontend UI: `http://127.0.0.1:5173`

## Notes

- The root README describes the project and roadmap.
- The implementation-specific setup lives under `v0/backend/README.md` and `v0/frontend/README.md`.
- The SRS document in `ProjectDocumentation/` captures broader requirements and planning context.

## License

MIT
