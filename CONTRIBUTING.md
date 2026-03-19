# Contributing to The Forge

## Prerequisites

- Docker Desktop running
- Python 3.11+
- Node.js 20+
- `.env` at the project root

## Local Setup

The native development flow maps Docker Postgres to `127.0.0.1:5433` so it does
not conflict with a host Postgres instance already using `5432`.

```bash
# Copy local environment
cp .env.example .env

# Start only shared services in Docker
docker compose up -d db redis

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db upgrade
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed-builds
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask run --port=5050 --debug
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Optional root helper scripts:

```bash
npm run dev:db
npm run db:upgrade
npm run db:seed
npm run db:seed-builds
npm run dev:backend
npm run dev:frontend
```

Optional full-container workflow:

```bash
docker compose up --build

# Seed the database (first run only)
docker compose exec -e PYTHONPATH=/app backend flask db upgrade
docker compose exec -e PYTHONPATH=/app backend flask seed
docker compose exec -e PYTHONPATH=/app backend flask seed-builds
```

Frontend: `http://localhost:5173`
Backend API: `http://localhost:5050/api`

## Running Tests

All 40+ tests must pass before committing.

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

Run a single test file:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/test_craft.py -v
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
# Restart Docker services only
docker compose restart db redis

# Run backend locally
npm run dev:backend

# DB migration after model changes
cd backend
source .venv/bin/activate
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db migrate -m "description"
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db upgrade

# Flush Redis (rate limit reset)
docker compose exec redis redis-cli FLUSHALL

# View Docker service logs
docker compose logs db redis --tail=50 -f
```
