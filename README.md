# TradeSpec

TradeSpec is a personal swing-trading decision tool built around three jobs:

1. **Pre-Trade Gate** — decide whether a setup is worth taking.
2. **Active Trade Stabilizer** — stay disciplined after entry.
3. **Trade Journal** — review outcomes and recurring mistakes.

This MVP is intentionally opinionated:

- single-user only
- no authentication
- no broker execution
- deterministic rules remain authoritative
- AI is advisory only

## Monorepo layout

```text
apps/
  api/   FastAPI backend
  web/   Next.js frontend
```

## Tech stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Storage: SQLite (planned in later steps)
- Market data: Yahoo Finance adapter seam
- AI: stubbed service interface for now

## Environment variables

### Backend

Create `apps/api/.env` from `apps/api/.env.example`.

- `TRADESPEC_APP_NAME` — API application name
- `TRADESPEC_ENVIRONMENT` — `development`, `test`, or `production`
- `TRADESPEC_ALLOWED_ORIGINS` — comma-separated frontend origins
- `TRADESPEC_SQLITE_URL` — SQLite connection string for later persistence
- `TRADESPEC_MARKET_DATA_PROVIDER` — defaults to `yahoo-finance`
- `TRADESPEC_AI_PROVIDER` — defaults to `stub`

### Frontend

Create `apps/web/.env.local` from `apps/web/.env.local.example`.

- `NEXT_PUBLIC_API_BASE_URL` — backend API base URL

## Run locally

### 1. Backend

```bash
cd apps/api
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/health
```

### 2. Frontend

```bash
cd apps/web
npm install
npm run dev
```

Open <http://localhost:3000>.

## Quality checks

### Backend

```bash
cd apps/api
python -m pytest
python -m ruff check .
```

### Frontend

```bash
cd apps/web
npm run test
npm run lint
npm run build
```

## Shared domain vocabulary

The MVP uses these core concepts:

- `VALID` — setup is acceptable under the rule engine
- `WAIT` — possible setup, but conditions are incomplete
- `INVALID` — setup fails the rule set
- **entry zone** — acceptable price range for opening a trade
- **stop loss** — the invalidation level
- **target** — expected profit objective
- **time horizon** — expected holding period
- **expected behavior envelope** — what normal post-entry price action should look like

## Future step plan

1. Domain models and API contracts
2. Market data layer
3. Pre-trade rule engine
4. Trade builder and validator
5. Active trade stabilizer
6. Journal and AI seams
7. Polish and hardening

## Current status

The repo is scaffolded and ready for the next implementation slices.
