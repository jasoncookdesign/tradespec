# TradeSpec

Personal swing-trading decision tool (pre-trade gate, trade stabilizer, journal): FastAPI backend in `apps/api`, Next.js frontend in `apps/web`. Merging to main deploys nothing.

- Preview / run: backend `cd apps/api && python -m uvicorn app.main:app --reload --port 8000`; frontend `npm run dev` from the repo root. Env setup is in `README.md`.
- Checks: backend `cd apps/api && python -m pytest && python -m ruff check .`; frontend `npm run test && npm run lint && npm run build` from the root.
- Generated output (never hand-edit): none.
- Repo conventions: deterministic rules are authoritative and AI is advisory only. Backend AI stays behind the stub service interface. Document new env vars in `README.md` in the same change.

## TDD exception (recorded ruling)
No exception. Both apps have test runners (pytest, jest), so all behavior changes get full TDD. Docs-only and config-only changes are exempt.
