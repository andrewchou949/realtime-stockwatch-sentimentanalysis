# AGENTS.md

## Purpose

This file gives coding agents a shared operating brief for the Stock Watch repository.

The project goal is to build a portfolio-quality stock monitoring app in stages:

1. Deliver a small, working `v0` baseline alerts product.
2. Prove the end-to-end loop from watchlist to price fetch to persisted alerts.
3. Expand later into AI-assisted sentiment and event analysis.

Agents should optimize for shipping the current milestone before introducing broader platform or AI complexity.

## Source of Truth

Use these files in this order when deciding intent and scope:

1. `README.md`
2. `v0/README.md`
3. implementation files under `v0/backend/app/`
4. `ProjectDocumentation/Project_SRS.docx` for broader planning context

If planning docs and implementation differ, prefer the current implementation plus the explicitly stated `v0` scope.

## Current Project State

Implemented:

- FastAPI application bootstrap
- SQLite connection setup with SQLAlchemy
- `Watchlist` and `Alert` models
- automatic table creation on startup
- `/healthz` endpoint

Not yet implemented:

- watchlist CRUD API
- live price lookup endpoint
- refresh/alert evaluation flow
- frontend dashboard

Agents should not describe the app as fully real-time, AI-enabled, or production-ready unless that is actually implemented.

## Primary Goal For v0

The immediate product target is:

`Watchlist -> Price Fetch -> Simple Metrics -> Threshold Alert -> Persisted Alert History -> Minimal UI`

Every meaningful code change should help move the repo closer to that flow.

## v0 Scope Guardrails

In scope:

- add/remove/list watchlist tickers
- store `threshold_pct`, `baseline_price`, and timestamps
- fetch current price from one provider
- compute minimal price-change metrics
- trigger one alert rule based on percentage move from baseline
- persist alerts in SQLite
- expose API endpoints for watchlist, prices, alerts, and optional refresh
- build a minimal single-page UI later

Out of scope for now:

- sentiment analysis
- Reddit/X/news ingestion
- LangChain or Hugging Face pipelines
- Kafka, Redis Streams, or complex event buses
- authentication and multi-user support
- backtesting, paper trading, or advanced analytics

If an idea is attractive but does not directly support `v0`, defer it.

## Technical Direction

Current stack for `v0`:

- Backend: FastAPI
- Persistence: SQLite
- ORM: SQLAlchemy
- UI target: React with Vite
- Price source: exactly one provider at first

Keep the implementation simple, local, and easy to demo.

Preferred engineering traits:

- small vertical slices
- clear endpoint contracts
- deterministic local setup
- minimal dependencies
- explicit data models

## Existing Backend Structure

Important files:

- `v0/backend/app/main.py`: FastAPI app setup and startup hooks
- `v0/backend/app/db.py`: database engine, session factory, declarative base
- `v0/backend/app/models.py`: SQLAlchemy models for watchlist and alerts
- `v0/backend/app/api/health.py`: current API route example
- `v0/backend/requirements.txt`: backend dependencies
- `v0/backend/README.md`: local backend run instructions

When adding backend features, follow the existing module pattern unless there is a strong reason to refactor.

## Local Environment Notes

Backend local run flow:

```bash
cd v0/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/healthz
```

Agent-specific note:

- in restricted Codex sandbox environments, `uvicorn --reload` may fail because the reloader needs process or file-watch capabilities the sandbox blocks
- localhost bind attempts may also be blocked inside the sandbox even when the FastAPI app itself is valid
- if that happens, treat it as an environment limitation first, not an application bug
- for agent verification, use a smoke test like `./.venv/bin/python -c "import fastapi, uvicorn, sqlalchemy"` and, when allowed, rerun `uvicorn app.main:app` outside the sandbox to confirm `/healthz`

## Expected API Direction

Agents should align new work to this target contract from `v0/README.md`:

- `POST /watchlist`
- `GET /watchlist`
- `DELETE /watchlist/{symbol}`
- `GET /prices/{symbol}`
- `GET /alerts?limit=50`
- optional `POST /refresh`

If implementation details change, preserve the product behavior unless the user asks for a redesign.

## Data Expectations

`watchlist` should support:

- `symbol`
- `threshold_pct`
- `baseline_price`
- `baseline_at`
- `last_price`
- `last_updated_at`

`alerts` should support:

- `id`
- `symbol`
- `direction`
- `pct_change`
- `current_price`
- `baseline_price`
- `triggered_at`

Agents should avoid schema drift away from this model unless there is a clear need and the change is explained.

## Working Rules For Agents

- Keep solutions grounded in the current repository state.
- Favor incremental delivery over speculative architecture.
- Make README and setup instructions stay accurate as code evolves.
- When adding features, include the smallest useful validation path.
- Avoid introducing infrastructure that makes local demo setup harder.
- Preserve SQLite compatibility unless the user explicitly wants a different database.
- Keep naming and file organization straightforward for future contributors.

## Good Next Tasks

High-value next steps include:

- add request/response schemas for watchlist operations
- implement database session dependency wiring
- add watchlist CRUD routes
- add a simple price provider abstraction
- implement alert evaluation logic
- expose recent alert history endpoint
- add minimal tests for the core alert flow
- update docs as new endpoints land

## Documentation Standard

When agents update the codebase, they should also update whichever docs are affected:

- root `README.md` for project-level status changes
- `v0/README.md` for scope or contract changes
- `v0/backend/README.md` for backend run/setup changes

Do not leave aspirational claims in docs that are no longer true.

## Success Criteria

A successful agent contribution for this repo usually does one or more of the following:

- makes the `v0` alert workflow more complete
- keeps the app easier to run locally
- improves correctness of data or alert behavior
- keeps docs aligned with reality
- avoids overbuilding beyond the current milestone
