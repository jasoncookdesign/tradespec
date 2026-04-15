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

## AI scope today

The current UI only integrates the post-trade AI observation inside the journal flow.
The pre-trade summary and critique seams exist in the backend service interface, but
they are intentionally not yet wired into the user-facing workflow.

## Monorepo layout

```text
apps/
  api/   FastAPI backend
  web/   Next.js frontend
```

## Tech stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Storage: SQLite for local trade and journal persistence
- Market data: Yahoo Finance adapter seam
- AI: stubbed service interface for now

## Environment variables

### Backend

Create `apps/api/.env` from `apps/api/.env.example`.

- `TRADESPEC_APP_NAME` — API application name
- `TRADESPEC_ENVIRONMENT` — `development`, `test`, or `production`
- `TRADESPEC_ALLOWED_ORIGINS` — comma-separated frontend origins
- `TRADESPEC_SQLITE_URL` — SQLite connection string for local trade and journal persistence
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

You can also run the frontend from the repo root:

```bash
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

## Known limitations

- localhost-focused, single-user workflow
- no authentication or broker integration
- journal and trade persistence use local SQLite only
- AI output is advisory and currently limited to the post-trade journal flow
- market data depends on the Yahoo Finance adapter seam

## Current status

The repo is now a locally usable MVP with deterministic evaluation, validation,
active-trade guidance, and journaling flows.
