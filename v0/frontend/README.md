# Stock Watch Frontend — v0

React + Vite frontend for the Stock Watch MVP.

## Setup

```bash
cd v0/frontend
npm install
npm run dev
```

The dev server runs at `http://127.0.0.1:5173`.

By default the frontend talks to the backend at `http://127.0.0.1:8000`.

If needed, create a `.env` file from `.env.example` and change:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## MVP Features

- add a ticker with threshold percentage
- view the current watchlist and baseline-relative change
- remove symbols from the watchlist
- refresh all watched symbols
- view recent alerts
- look up a single price snapshot
- check backend health from the UI
- toggle between light and dark themes
- use demo-only breach/reset tools when local dev helpers are enabled
