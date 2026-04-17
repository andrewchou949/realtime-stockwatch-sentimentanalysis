# Stock Watch API — Backend (v0)

FastAPI backend for the Stock Watch MVP v0.

## What Exists

The backend now includes:

- `GET /healthz`
- `POST /watchlist`
- `GET /watchlist`
- `DELETE /watchlist/{symbol}`
- `GET /prices/{symbol}`
- `GET /alerts?limit=50`
- `POST /refresh`
- `POST /dev/force-breach` for demo-only alert staging
- `POST /dev/reset` for clearing local demo data
- CORS support for the Vite frontend at `http://127.0.0.1:5173`

## Setup

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000/`

Dev helpers are enabled locally by default. To disable them:

```bash
STOCK_WATCH_ENABLE_DEV_TOOLS=false uvicorn app.main:app --reload
```

## Quick Checks

Health check:

```bash
curl http://127.0.0.1:8000/healthz
```

API root response:

```text
http://127.0.0.1:8000/
```

Run the separate frontend from `v0/frontend` at:

```text
http://127.0.0.1:5173/
```

## Demo Helpers

Force a visible threshold event for a tracked symbol:

```bash
curl -X POST http://127.0.0.1:8000/dev/force-breach \
  -H "Content-Type: application/json" \
  -d '{"symbol":"TSLA","direction":"UP","pct_change":6.0}'
```

Reset local demo data:

```bash
curl -X POST http://127.0.0.1:8000/dev/reset \
  -H "Content-Type: application/json" \
  -d '{"scope":"all"}'
```

## Testing

Run the backend test suite with:

```bash
pytest
```
