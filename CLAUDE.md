# CLAUDE.md — The Forge

This file is the single source of truth for Claude Code working in this repository. Read it fully before touching any code.

---

## Project Overview

**The Forge** is a full-stack community theorycrafting platform for the ARPG *Last Epoch*. Players use it to plan builds, simulate crafting, and browse community builds.

This is a portfolio project with a real audience goal. Code quality, correctness, and UX matter. Do not cut corners.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript, Vite, TailwindCSS |
| Backend | Flask (Python), SQLAlchemy ORM, Marshmallow schemas |
| Database | PostgreSQL 15 |
| Cache / Rate Limiting | Redis 7 |
| Auth | Discord OAuth2 + JWT (Bearer tokens) |
| Dev Infrastructure | Docker Compose |

---

## Repository Layout

```
the-forge/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory, blueprint registration
│   │   ├── models/__init__.py   # All SQLAlchemy ORM models
│   │   ├── routes/
│   │   │   ├── auth.py          # Discord OAuth + JWT exchange
│   │   │   ├── builds.py        # Build CRUD + voting
│   │   │   ├── craft.py         # Craft session management
│   │   │   ├── profile.py       # Authenticated user profile
│   │   │   └── ref.py           # Reference data (classes, affixes, items)
│   │   ├── schemas/__init__.py  # Marshmallow serialization schemas
│   │   ├── services/
│   │   │   ├── build_service.py # Build CRUD + vote logic
│   │   │   └── craft_service.py # Crafting math engine (authoritative)
│   │   └── utils/
│   │       ├── auth.py          # @login_required decorator, get_current_user()
│   │       ├── cli.py           # `flask seed` and `flask seed-builds` commands
│   │       └── responses.py     # ok(), error(), not_found(), paginate_meta()
│   ├── config.py                # Dev/prod/test Flask configs
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_builds.py
│   │   └── test_craft.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wsgi.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                          # Router + AuthBootstrapper
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── layout/AppLayout.tsx          # Nav, avatar, auth state
│   │   │   ├── ui/index.tsx                 # Shared primitives (Panel, Button, Badge, ConfirmModal, etc.)
│   │   │   └── features/
│   │   │       ├── HomePage.tsx
│   │   │       ├── AuthCallbackPage.tsx
│   │   │       ├── UserProfilePage.tsx
│   │   │       ├── build/BuildPlannerPage.tsx
│   │   │       ├── builds/BuildsPage.tsx
│   │   │       └── craft/CraftSimulatorPage.tsx
│   │   ├── hooks/index.ts        # All React Query hooks
│   │   ├── lib/
│   │   │   ├── api.ts            # Typed API client (authApi, buildsApi, craftApi, etc.)
│   │   │   ├── crafting.ts       # Client-side crafting math (mirrors craft_service.py)
│   │   │   └── gameData.ts       # LE game data: skills, items, affixes, passive regions
│   │   ├── store/index.ts        # Zustand stores (auth, meta filters, craft)
│   │   ├── types/index.ts        # TypeScript types mirroring Marshmallow schemas
│   │   └── styles/globals.css
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
│
├── docker-compose.yml
└── .env
```

---

## Running the Project

### Prerequisites

- Docker Desktop running on Windows (WSL2 backend)
- `.env` file at project root with `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`

### Start everything

```bash
cd /mnt/d/Programming/the-forge
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api`
- Postgres: `localhost:5432` (user: `forge`, db: `the_forge`)
- Redis: `localhost:6379`

### After first run — seed the database

```bash
docker compose exec -e PYTHONPATH=/app backend flask db upgrade
docker compose exec -e PYTHONPATH=/app backend flask seed
docker compose exec -e PYTHONPATH=/app backend flask seed-builds
```

### Run tests

```bash
docker compose exec -e PYTHONPATH=/app backend pytest tests/ -v
```

All 40 tests must pass. Never commit if tests are failing.

### Restart backend after Python changes

```bash
docker compose restart backend
```

Vite hot-reloads the frontend automatically.

### Flush Redis (rate limit reset)

```bash
docker compose exec redis redis-cli FLUSHALL
```

---

## Environment Variables

Set in `.env` at the project root. Docker Compose reads this automatically.

| Variable | Required | Notes |
|---|---|---|
| `DISCORD_CLIENT_ID` | Yes | From Discord Developer Portal |
| `DISCORD_CLIENT_SECRET` | Yes | From Discord Developer Portal |
| `SECRET_KEY` | No | Defaults to `dev-secret-change-in-prod` |
| `JWT_SECRET_KEY` | No | Defaults to `jwt-dev-secret` |
| `DB_PASSWORD` | No | Defaults to `forgedev` |

---

## Database

### Models (all in `backend/app/models/__init__.py`)

| Model | Table | Notes |
|---|---|---|
| `User` | `users` | Discord OAuth identity |
| `Build` | `builds` | UUID PK, slug, passive_tree as JSON array |
| `BuildSkill` | `build_skills` | Up to 5 per build, `ON DELETE CASCADE` |
| `Vote` | `votes` | Unique per (user, build), `ON DELETE CASCADE` |
| `CraftSession` | `craft_sessions` | Instability, FP, affixes as JSON |
| `CraftStep` | `craft_steps` | Full audit log per action |
| `ItemType` | `item_types` | Reference, seeded |
| `AffixDef` | `affix_defs` | Reference, seeded |
| `PassiveNode` | `passive_nodes` | Reference, seeded |

### Migrations

```bash
# Generate migration after model changes
docker compose exec -e PYTHONPATH=/app backend flask db migrate -m "description"

# Apply pending migrations
docker compose exec -e PYTHONPATH=/app backend flask db upgrade
```

### Manual DB inspection

```bash
docker compose exec db psql -U forge -d the_forge -c "SELECT name, vote_count FROM builds;"
```

### Cascade delete

Both `build_skills` and `votes` have database-level `ON DELETE CASCADE` on `build_id`. Deleting a build from raw SQL will clean up both automatically. This was applied manually:

```sql
ALTER TABLE build_skills DROP CONSTRAINT build_skills_build_id_fkey;
ALTER TABLE build_skills ADD CONSTRAINT build_skills_build_id_fkey
  FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE;
ALTER TABLE votes DROP CONSTRAINT votes_build_id_fkey;
ALTER TABLE votes ADD CONSTRAINT votes_build_id_fkey
  FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE;
```

---

## Backend Conventions

### Response format

All endpoints use helpers from `app/utils/responses.py`. Always use these — never return raw dicts.

```python
from app.utils.responses import ok, error, not_found, unauthorized, forbidden, paginate_meta

return ok(data=schema.dump(obj))
return ok(data=schema.dump(items), meta=paginate_meta(page, per_page, total, pages))
return error("message", status=400)
return not_found("Build not found")
```

### Authentication

```python
from app.utils.auth import login_required, get_current_user

@bp.get("/protected")
@login_required
def protected_route():
    user = get_current_user()
    ...
```

**Critical**: `app/utils/auth.py` must NOT import from `app.utils.responses` at module level — this causes a circular import. Import locally inside each function:

```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.utils.responses import unauthorized  # local import — required
        ...
```

### Blueprint registration

All blueprints are registered in `app/__init__.py`. When adding a new route file, register it there:

```python
from app.routes.newfeature import newfeature_bp
app.register_blueprint(newfeature_bp, url_prefix="/api/newfeature")
```

### Rate limiting

Dev config overrides to `"10000 per day;2000 per hour;200 per minute"`. If you hit a 429 during dev, flush Redis.

---

## Frontend Conventions

### API calls

Use the typed clients in `src/lib/api.ts`. Never use raw `fetch` in components.

```typescript
import { buildsApi } from "@/lib/api";
const res = await buildsApi.get(slug);
if (res.data) { ... }
if (res.errors) { ... }
```

### React Query hooks

All data fetching goes through hooks in `src/hooks/index.ts`. Query keys are centralised in the `qk` object at the top of that file.

```typescript
import { useBuild, useDeleteBuild } from "@/hooks";
const { data, isLoading } = useBuild(slug);
const deleteBuild = useDeleteBuild();
await deleteBuild.mutateAsync(slug);
```

### State management

Zustand stores in `src/store/index.ts`:
- `useAuthStore` — current user, JWT token, login/logout
- `useCraftStore` — active craft session UI state

### Shared UI components

All shared primitives live in `src/components/ui/index.tsx`. Use them instead of building one-offs:

- `Panel` — card container with optional title and action slot
- `Button` — variants: `primary`, `outline`, `ghost`, `danger`
- `Badge` — variants: `ssf`, `hc`, `ladder`, `tier-s/a/b/c`, `class`, etc.
- `ConfirmModal` — use for any destructive action (delete)
- `Spinner`, `EmptyState`, `SectionLabel`, `RiskBar`, `Divider`

### Design tokens (Tailwind)

Defined in `tailwind.config.js`. Always use these — never hardcode hex values in className.

| Token | Use |
|---|---|
| `forge-bg` | Page background (`#0a0806`) |
| `forge-surface` | Card background |
| `forge-surface2` | Input / header background |
| `forge-border` | Default border |
| `forge-border-hot` | Hover border |
| `forge-amber` | Primary accent (`#e8891a`) |
| `forge-gold` | Keystone / S-tier (`#f5d060`) |
| `forge-green` | Success / show (`#7cb87a`) |
| `forge-red` | Danger / hide (`#e05050`) |
| `forge-purple` | Mastery (`#9a7ac8`) |
| `forge-text` | Body text |
| `forge-muted` | Secondary text |
| `forge-dim` | Tertiary / disabled text |

### Typography

| Font | Class | Use |
|---|---|---|
| Cinzel | `font-display` | Headings, names, titles |
| Crimson Pro | `font-body` | Body text, descriptions |
| JetBrains Mono | `font-mono` | Labels, stats, numbers, codes |

### Routing

Routes are defined in `src/App.tsx`:

| Path | Component |
|---|---|
| `/` | `HomePage` |
| `/build`, `/build/:slug` | `BuildPlannerPage` |
| `/craft`, `/craft/:slug` | `CraftSimulatorPage` |
| `/builds` | `BuildsPage` |
| `/profile` | `UserProfilePage` |
| `/auth/callback` | `AuthCallbackPage` |

### Auth flow

1. User clicks "Sign In" → navigates to `http://localhost:5000/api/auth/discord`
2. Backend redirects to Discord OAuth
3. Discord redirects to `/auth/callback?token=...`
4. `AuthCallbackPage` stores token in `sessionStorage` under `forge_token`, calls `login()` on the auth store, navigates to `/`
5. On page refresh, `AuthBootstrapper` in `App.tsx` reads `sessionStorage` and restores the session via `GET /api/auth/me`

The Sign In link in `AppLayout.tsx` must always point to the full backend URL `http://localhost:5000/api/auth/discord`, not a relative path — the proxy doesn't handle OAuth redirects correctly.

---

## Game Data

All Last Epoch game data lives in `src/lib/gameData.ts`. This is the single source of truth for the frontend.

### Skills

`CLASS_SKILLS` contains the full skill pool per class including mastery-exclusive skills tagged with `mastery?: string`. Players pick any 5 to specialize. Skill level cap is 20 by default; gear affixes can push beyond via the `bonusLevels` field on `SelectedSkill`.

### Passive tree

`PASSIVE_REGIONS` defines four visual sections per class: base class tree + three mastery trees. Each mastery has `yStart`/`yEnd` as fractions of canvas height, a `color`, and `isBase` flag. The canvas in `BuildPlannerPage` uses these to draw distinct colored regions.

---

## Crafting Math

The crafting engine is implemented twice and must stay in sync:

- **Authoritative (backend)**: `backend/app/services/craft_service.py`
- **Display only (frontend)**: `frontend/src/lib/crafting.ts`

### Fracture risk formula

```
effective_instability = instability - (sealed_affix_count × 12)
fracture_risk = (effective_instability / 80)²  × 100%
```

Key thresholds:
- 0 instability → 0% risk
- 40 instability → 25% risk
- 55 instability → ~47% risk
- 80 instability → 100% risk (guaranteed fracture)

### Forge Potential costs

| Action | FP Cost |
|---|---|
| Add Affix | 4 |
| Upgrade Affix | 5 |
| Seal Affix | 8 |
| Unseal Affix | 2 |
| Remove Affix | 3 |

---

## API Reference

All responses follow the envelope `{ data, meta, errors }`.

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/auth/discord` | No | Begin OAuth flow |
| GET | `/api/auth/callback` | No | OAuth callback |
| GET | `/api/auth/me` | Yes | Current user |
| POST | `/api/auth/logout` | Yes | Invalidate session |

### Builds
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/builds` | No | List builds (filterable) |
| POST | `/api/builds` | Yes | Create build |
| GET | `/api/builds/:slug` | No | Get build |
| PATCH | `/api/builds/:slug` | Yes (owner) | Update build |
| DELETE | `/api/builds/:slug` | Yes (owner) | Delete build |
| POST | `/api/builds/:slug/vote` | Yes | Vote `{ direction: 1 \| -1 }` |
| GET | `/api/builds/meta/snapshot` | No | Class distribution, top builds |

Query params for `GET /api/builds`: `class`, `mastery`, `tier`, `ssf`, `hc`, `ladder`, `budget`, `cycle`, `sort` (`votes`/`new`/`tier`/`views`), `q`, `page`, `per_page`

### Craft
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/craft` | Yes | Create session |
| GET | `/api/craft/:slug` | Yes (owner) | Get session |
| POST | `/api/craft/:slug/action` | Yes (owner) | Perform craft action |
| GET | `/api/craft/:slug/summary` | Yes (owner) | Session summary + optimal path |
| DELETE | `/api/craft/:slug` | Yes (owner) | Delete session |

### Profile
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/profile` | Yes | Full profile with stats + recent items |
| GET | `/api/profile/builds` | Yes | All user's builds (incl. private), paginated |
| GET | `/api/profile/sessions` | Yes | All user's craft sessions, paginated |

---

## Known Issues and Decisions

### Docker volume configuration

Frontend volumes must only mount source directories, not the entire frontend folder — mounting `/app` hides `node_modules` inside the container:

```yaml
volumes:
  - ./frontend/src:/app/src
  - ./frontend/public:/app/public
  - ./frontend/index.html:/app/index.html
```

### SQLAlchemy deprecation warning

`User.query.get(id)` is legacy. Replace with `db.session.get(User, id)` when touching that code.

### JWT key length warning in tests

`TestingConfig` uses short JWT keys which triggers a warning. Acceptable in tests, fix before production by setting a 32+ character `JWT_SECRET_KEY`.

### Passive tree nodes are procedurally generated

The passive tree canvas in `BuildPlannerPage` generates nodes algorithmically based on class/mastery. It is not the real Last Epoch passive tree data. Real node positions would require game file extraction or a community data source.

---

## Pending Work

In priority order:

1. **Real passive tree data** — replace procedural node generation with actual node positions from game data
4. **Production deployment** — Railway (recommended for this Docker Compose stack); update Discord OAuth redirect URI, set production env vars
5. **SQLAlchemy legacy cleanup** — replace all `Model.query.get()` with `db.session.get(Model, id)`

---

## Useful Commands Quick Reference

```bash
# Start
docker compose up --build

# Backend shell
docker compose exec backend bash

# Run tests
docker compose exec -e PYTHONPATH=/app backend pytest tests/ -v

# Run a single test
docker compose exec -e PYTHONPATH=/app backend pytest tests/test_builds.py::test_create_build -v

# DB migration
docker compose exec -e PYTHONPATH=/app backend flask db migrate -m "description"
docker compose exec -e PYTHONPATH=/app backend flask db upgrade

# Seed reference data
docker compose exec -e PYTHONPATH=/app backend flask seed
docker compose exec -e PYTHONPATH=/app backend flask seed-builds

# Inspect DB
docker compose exec db psql -U forge -d the_forge

# Flush Redis
docker compose exec redis redis-cli FLUSHALL

# Restart backend only
docker compose restart backend

# View logs
docker compose logs backend --tail=50 -f
docker compose logs frontend --tail=50 -f

# Nuclear reset (destroys DB volume)
docker compose down -v && docker compose up --build
```