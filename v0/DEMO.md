# Stock Watch v0 Demo Runbook

Use this flow for a short local MVP demo before pushing.

## 1. Start the backend

```bash
cd v0/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

## 2. Start the frontend

```bash
cd v0/frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## 3. Reset to a clean local state

Use the "Reset Demo State" button in the UI, or:

```bash
curl -X POST http://127.0.0.1:8000/dev/reset \
  -H "Content-Type: application/json" \
  -d '{"scope":"all"}'
```

## 4. Demo script

1. Add `TSLA` with threshold `2.0`.
2. Show the captured baseline price and the current watchlist row.
3. Use "Fetch Price" with `AAPL` to prove live provider connectivity.
4. Click "Refresh Watchlist" to show the backend refresh flow.
5. In "Demo Tools", force an `UP` breach for `TSLA` at `6.0%`.
6. Point out that:
   - the watchlist row updates
   - an alert appears in recent history
   - the event is stored by the backend
7. Refresh the page to show the alert history persists.

## 5. Optional talking points

- `v0/backend` and `v0/frontend` are now fully separated components.
- The MVP intentionally stays focused on watchlist, price fetch, threshold alerts, persistence, and a minimal dashboard.
- AI, news ingestion, and streaming are deferred until after the MVP is demoable.
