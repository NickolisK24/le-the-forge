# Contributing to The Forge

---

## Getting Started

See the [README](README.md) for full setup instructions. The short version:

```bash
cp .env.example .env
docker compose up -d db redis

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db upgrade
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed-passives
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask run --port=5050 --debug

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:5050/api

---

## Branch Conventions

All work is done on feature branches off of `dev`. Never commit directly to `dev` or `main`.

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/skill-rotation-builder` |
| `fix/` | Bug fixes | `fix/passive-tree-overflow` |
| `refactor/` | Structural changes, no behavior change | `refactor/engine-extraction` |
| `chore/` | Dependency updates, config changes | `chore/update-flask-3.1` |
| `docs/` | Documentation only | `docs/api-reference-update` |

**Merge flow:** feature branch --> PR into `dev` --> `dev` PR into `main` for releases.

---

## Commit Message Format

```
<type>: <short description>
```

| Type | When to use |
|------|-------------|
| `feat` | New feature | 
| `fix` | Bug fix |
| `refactor` | Code restructure without behavior change |
| `chore` | Maintenance, dependency updates, config |
| `docs` | Documentation changes |
| `test` | Test additions or fixes |

Examples:

```
feat: add corruption scaling analysis endpoint
fix: handle naive datetimes from SQLite in trending builds
refactor: extract craft math into craft_engine.py
chore: bump Flask to 3.0.3
docs: update API reference with analysis endpoints
test: add boss encounter simulation coverage
```

---

## Pull Request Checklist

Before opening a PR, verify:

- [ ] All existing tests pass: `cd backend && PYTHONPATH=. pytest tests/ -x -q`
- [ ] New code has test coverage
- [ ] TypeScript compiles clean: `cd frontend && npx tsc --noEmit`
- [ ] Data validation passes: `cd backend && FLASK_APP=wsgi.py PYTHONPATH=. flask validate-data`
- [ ] No `console.log` left in frontend code
- [ ] No bare `except:` in backend code (catch specific exceptions)
- [ ] All new API endpoints have rate limits
- [ ] All new response shapes have Marshmallow schemas
- [ ] All new frontend components handle loading, error, and empty states

---

## Code Style

### Backend

- PEP 8 style, snake_case naming
- Type hints on all function signatures
- All responses use helpers from `app/utils/responses.py` (`ok()`, `error()`, `not_found()`, etc.)
- Auth via `@login_required` decorator and `get_current_user()` from `app/utils/auth`
- New blueprints must be registered in `app/__init__.py`
- Engine modules (`app/engines/`) must be pure -- no database imports, no HTTP, no side effects
- No magic numbers -- use named constants

### Frontend

- TypeScript strict mode, explicit interfaces for all component props
- API calls go through typed clients in `src/lib/api.ts` -- never raw `fetch` in components
- Data fetching via TanStack Query hooks in `src/hooks/index.ts`
- State management via Zustand stores in `src/store/index.ts`
- Shared UI components from `src/components/ui/` -- use them, don't reinvent
- Tailwind design tokens (`forge-bg`, `forge-amber`, `forge-cyan`, etc.) -- no hardcoded hex values
- No `any` type except where absolutely unavoidable

---

## Architecture

```
Routes --> Services --> Engines --> Results
             |
          Database
```

- **Routes** (`app/routes/`) -- HTTP request/response only, no business logic
- **Services** (`app/services/`) -- orchestration, database operations, engine coordination
- **Engines** (`app/engines/`) -- pure calculation modules (no DB, no HTTP)
- **Models** (`app/models/`) -- SQLAlchemy ORM

All new engines go in `backend/app/engines/` and must have corresponding tests in `backend/tests/`.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design.

---

## Adding Game Data

Game data lives in `/data/` and is synced from Last Epoch game exports.

```bash
# Sync from last-epoch-data/ export directory
cd backend
python ../scripts/sync_game_data.py --source ../last-epoch-data

# Validate all data files
FLASK_APP=wsgi.py PYTHONPATH=. flask validate-data

# Re-seed database from updated data
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask reseed-affixes
FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask seed-passives
```

If `flask validate-data` fails, check:
1. The JSON file is valid JSON (no trailing commas, no comments)
2. The root type matches expectations (array for lists, object for dictionaries)
3. The file meets the minimum entry count threshold
4. Required fields are present in each entry

---

## Common Commands

```bash
# Run all tests
cd backend && PYTHONPATH=. pytest tests/ -x -q

# Run a single test file
cd backend && PYTHONPATH=. pytest tests/test_combat.py -v

# Type-check frontend
cd frontend && npx tsc --noEmit

# Validate game data
cd backend && FLASK_APP=wsgi.py PYTHONPATH=. flask validate-data

# Create a database migration
cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db migrate -m "description"
cd backend && FLASK_APP=wsgi.py FLASK_ENV=development PYTHONPATH=. flask db upgrade

# Flush Redis (reset rate limits and cache)
docker compose exec redis redis-cli FLUSHALL

# Force-refresh meta analytics cache
cd backend && FLASK_APP=wsgi.py PYTHONPATH=. flask refresh-meta
```
