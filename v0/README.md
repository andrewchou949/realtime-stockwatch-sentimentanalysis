# Portfolio MVP v0 — Stock Watch (Baseline Alerts)

## Goal
Ship the smallest end-to-end version of the system that is portfolio-demoable:
**Watchlist → Price Fetch → Simple Metrics → Baseline Threshold Alert → Persisted Alert History → Minimal UI**

This version prioritizes momentum and correctness over advanced real-time pipelines and AI features.

---

## In Scope (v0)

### Core Features
1) **Watchlist Management**
- Add ticker symbol (e.g., AAPL)
- Remove ticker
- List current watchlist

2) **Price Fetching**
- Fetch latest price for a ticker from a single data source
- Expose a price snapshot endpoint returning:
  - `symbol`, `price`, `timestamp`

3) **Metrics (keep minimal)**
Compute and return at least **two** of the following (server-side):
- `pct_change_from_baseline`
- `current_price`
- `baseline_price`
- `last_updated_at`

> Note: For v0, the “baseline price” is the price recorded when the ticker is added to the watchlist.

4) **Alert Rule v0 (ONE rule only)**
Trigger an alert when:
- `abs(pct_change_from_baseline) >= threshold_pct`

Alert payload includes:
- `symbol`
- `direction` (UP / DOWN)
- `pct_change`
- `current_price`
- `baseline_price`
- `triggered_at`

5) **Alert History (Persisted)**
- Store alerts in a DB
- Expose an endpoint to view recent alerts (e.g., last 50)

6) **Minimal Dashboard UI**
A single page UI that supports:
- Add ticker
- View watchlist rows with latest price + % from baseline
- View recent alerts list

### Current v0 Layout
- `v0/backend/` contains the FastAPI API and SQLite persistence
- `v0/frontend/` contains the React + Vite dashboard

---

## Out of Scope (v0)
- News / Reddit / X ingestion
- Sentiment analysis, LLM summaries, emotion tagging
- Kafka / Redis streams / complex event buses
- WebSockets (polling is fine for v0)
- Authentication / multi-user support
- Backtesting and paper trading

---

## Tech Choices (Locked for v0)
- Backend: **FastAPI**
- Storage: **SQLite** (local file DB)
- Price source: **One provider only** (start simple; can swap later)
- UI: **React (Vite)** single page (no charts required)

---

## API Contract (v0)

### Watchlist
- `POST /watchlist`
  - body: `{ "symbol": "AAPL", "threshold_pct": 2.0 }`
- `GET /watchlist`
  - returns: `[{ "symbol": "AAPL", "threshold_pct": 2.0, "baseline_price": 123.45, "baseline_at": "..." }]`
- `DELETE /watchlist/{symbol}`

### Prices
- `GET /prices/{symbol}`
  - returns: `{ "symbol": "AAPL", "price": 125.10, "timestamp": "..." }`

### Alerts
- `GET /alerts?limit=50`
  - returns: list of alerts (most recent first)

### Refresh (optional but useful for v0)
- `POST /refresh`
  - fetch prices for all watchlist tickers, compute pct change, trigger alerts if needed

---

## Data Model (v0)

### watchlist
- symbol (PK)
- threshold_pct (float)
- baseline_price (float)
- baseline_at (datetime)
- last_price (float, nullable)
- last_updated_at (datetime, nullable)

### alerts
- id (PK)
- symbol (FK -> watchlist.symbol)
- direction (UP/DOWN)
- pct_change (float)
- current_price (float)
- baseline_price (float)
- triggered_at (datetime)

---

## Acceptance Criteria (Definition of Done)
v0 is complete when:
1) User can add `AAPL` via UI and see it listed immediately.
2) Backend can fetch `AAPL` price and return it through the API.
3) When `AAPL` crosses the configured threshold (±X%), an alert is created and visible in:
   - `GET /alerts`
   - the UI alerts panel
4) Restarting the app does NOT erase watchlist or alert history (SQLite persists).
5) `README` run instructions allow a fresh clone to start the system locally.

---

## Demo Script (30–60 seconds)
1) Add `TSLA` with threshold `2%`
2) Hit refresh (or wait for polling)
3) Show watchlist row with baseline + current + % change
4) Force a threshold breach (via a dev endpoint or mocked price) and show:
   - alert appears in UI
   - alert persists in history after refresh/restart
