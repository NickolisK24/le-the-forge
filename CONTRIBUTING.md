# Contributing to The Forge

## Prerequisites

- Docker Desktop running (WSL2 backend on Windows)
- `.env` at the project root with `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`

## Local Setup

```bash
# Start everything
docker compose up --build

# Seed the database (first run only)
docker compose exec -e PYTHONPATH=/app backend flask db upgrade
docker compose exec -e PYTHONPATH=/app backend flask seed
docker compose exec -e PYTHONPATH=/app backend flask seed-builds
```

Frontend: `http://localhost:5173`
Backend API: `http://localhost:5000/api`

## Running Tests

All 40+ tests must pass before committing.

```bash
docker compose exec -e PYTHONPATH=/app backend pytest tests/ -v
```

Run a single test file:

```bash
docker compose exec -e PYTHONPATH=/app backend pytest tests/test_craft.py -v
```

## Branch Conventions

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `feat/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, deps, refactors |

## Architecture

```
routes → services → engines → models
```

- **routes/** — HTTP request/response only, no business logic
- **services/** — orchestration and DB operations
- **engines/** — pure calculation modules (no DB, no HTTP)
- **models/** — SQLAlchemy ORM

All new engines go in `backend/app/engines/` and must have corresponding tests in `backend/tests/`.

## Code Conventions

### Backend

- All responses use helpers from `app/utils/responses.py` (`ok()`, `error()`, `not_found()`)
- Auth via `@login_required` decorator and `get_current_user()` from `app/utils/auth`
- New blueprints must be registered in `app/__init__.py`
- Import `unauthorized` from `app/utils/responses` **locally** inside functions in `app/utils/auth.py` (circular import prevention)

### Frontend

- API calls go through typed clients in `src/lib/api.ts` — never raw `fetch` in components
- Data fetching goes through React Query hooks in `src/hooks/index.ts`
- State lives in Zustand stores in `src/store/index.ts`
- Shared UI components live in `src/components/ui/index.tsx` — use them, don't reinvent
- Always use Tailwind design tokens (`forge-bg`, `forge-amber`, etc.) — no hardcoded hex values

## PR Checklist

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New features have tests
- [ ] Engine modules have no DB/HTTP imports
- [ ] Frontend API calls use `src/lib/api.ts` typed clients
- [ ] No raw hex values in Tailwind classNames
- [ ] `craft_service.py` and `crafting.ts` math stays in sync

## Common Commands

```bash
# Restart backend after Python changes
docker compose restart backend

# DB migration after model changes
docker compose exec -e PYTHONPATH=/app backend flask db migrate -m "description"
docker compose exec -e PYTHONPATH=/app backend flask db upgrade

# Flush Redis (rate limit reset)
docker compose exec redis redis-cli FLUSHALL

# View backend logs
docker compose logs backend --tail=50 -f
```
