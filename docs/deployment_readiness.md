# Deployment Readiness Audit

**Audit date:** 2026-04-21
**Target:** Render (backend + static frontend) + Cloudflare DNS, domain `epochforge.gg`.
**Branch:** `chore/deployment-readiness-audit`.

**Summary:** every code/config item is now PRESENT or FIXED. The only
remaining work is operator-side (Render dashboard + Cloudflare DNS) and is
listed in [Manual Steps Required Before Launch](#manual-steps-required-before-launch).

Verification gates, all green as of this commit:

- `pytest tests/ -x -q` → 10,865 passed, 377 skipped (15 new deployment
  readiness tests in `tests/test_deployment_readiness.py`)
- `npx tsc --noEmit` → 0 errors
- `flask validate-data` → 52 files, no failures
- `yaml.safe_load(render.yaml)` → parses, declares `epochforge-db`,
  `epochforge-redis`, `epochforge-api`, `epochforge-frontend`

---

## Backend

| # | Requirement | State |
| - | --- | --- |
| B1  | `gunicorn` in `backend/requirements.txt` | PRESENT |
| B2  | `backend/wsgi.py` exposes Flask app as `app` | PRESENT |
| B3  | `backend/Procfile` with `web: gunicorn wsgi:app` | PRESENT |
| B4  | `DATABASE_URL` read from env (no hard-coded prod value) | PRESENT (dev fallback in `config.py`; `ProductionConfig.validate()` rejects localhost in prod) |
| B5  | `REDIS_URL` read from env | PRESENT (same pattern as B4) |
| B6  | `SECRET_KEY` safe-fail in production | PRESENT (`ProductionConfig.validate()` raises if default) |
| B7  | `JWT_SECRET_KEY` safe-fail in production | PRESENT |
| B8  | Production CORS allows only `epochforge.gg`, `www.epochforge.gg` | PRESENT |
| B9  | Development CORS allows `localhost:5173`, `localhost:3000`, `127.0.0.1:5173` | **FIXED** (was: single `FRONTEND_URL` only; now a dev origin list with credentials + max-age + expose_headers) |
| B10 | CORS logic switches on `FLASK_ENV` | PRESENT |
| B11 | `GET /api/health` returns `{status, version, patch_version, uptime_seconds}` | PRESENT |
| B12 | `/api/health` unauthenticated + rate-limited to 60/min | PRESENT |
| B13 | `/api/health` lives in a dedicated blueprint (`routes/health.py`) | **FIXED** (was inline in `app/__init__.py`; moved to `app/routes/health.py` registered in the factory) |
| B14 | Flask-Migrate usable in production (`flask db upgrade`) | PRESENT (called via `preDeployCommand` in `render.yaml` and `release` entry in `Procfile`) |
| B15 | All Discord OAuth URLs read from `DISCORD_REDIRECT_URI` env var | PRESENT (verified in `routes/auth.py`) |
| B16 | `FRONTEND_URL` used for links back to frontend (OG URL, OAuth redirect) | PRESENT (`services/build_report_service.py`, `routes/auth.py`) |
| B17 | No hard-coded `localhost` / `127.0.0.1` in backend source outside tests and `.env.example` | PRESENT (only dev-default fallbacks in `config.py`, `build_report_service.py` — rejected by `ProductionConfig.validate()` when env is production) |
| B18 | Logging goes to stdout, INFO in prod / DEBUG in dev, no Flask debug mode in prod | **FIXED** (added `LOG_LEVEL="DEBUG"` on `DevelopmentConfig` and `LOG_LEVEL="INFO"` on `ProductionConfig`; `configure_logging` already uses stdout + suppresses werkzeug/sqlalchemy) |
| B19 | DB pool settings appropriate for Render Starter (pool_size=10, max_overflow=20, pool_pre_ping, pool_recycle=300) | PRESENT |

## Frontend

| # | Requirement | State |
| - | --- | --- |
| F1 | `VITE_API_BASE_URL` is the canonical API base URL | PRESENT (`src/lib/api.ts`, `components/navigation/TopBar.tsx`, `components/features/build/BuildPlannerPage.tsx`, `pages/debug/BackendDebugDashboard.tsx`) |
| F2 | No hard-coded `localhost` / `127.0.0.1` / `:5050` / `:5173` / `:3000` in frontend source | PRESENT (only `vite.config.ts` dev-proxy fallback and `frontend/Dockerfile` internal health check, both intentional) |
| F3 | `frontend/public/_redirects` SPA fallback | PRESENT (`/* /index.html 200`) |
| F4 | `vite build` produces `dist/` | PRESENT (`npm run build` runs `tsc && vite build`) |
| F5 | OpenGraph meta on shared routes uses prod domain from env | PRESENT (`index.html` defaults to `https://epochforge.gg`; per-build OG URL built from backend `FRONTEND_URL`) |
| F6 | No `NODE_ENV`-dependent code that would break production | PRESENT (only harmless `import.meta.env.DEV` guards) |
| F7 | Favicon | **FIXED** (was: `index.html` referenced `/favicon.svg` but file was missing — added `frontend/public/favicon.svg`) |
| F8 | Web app manifest | **FIXED** (was: missing — added `frontend/public/manifest.webmanifest` and linked from `index.html`) |

## Root

| # | Requirement | State |
| - | --- | --- |
| R1 | `render.yaml` at repo root with all four services | **FIXED** (was: only two web services; now also declares `epochforge-db` Postgres and `epochforge-redis` key-value services, with `DATABASE_URL`/`REDIS_URL` wired via `fromDatabase`/`fromService`) |
| R2 | `.env.example` lists every required env var with comments | **FIXED** (was: missing `RATE_LIMIT_SIMULATE_STATS` / `_BUILD` / `_ENCOUNTER` — now documented; a pytest guard in `test_deployment_readiness.py` prevents future drift) |
| R3 | `.gitignore` excludes `.env`, `.env.*` (allowlist `.env.example`) | PRESENT |

## CI / CD

| # | Requirement | State |
| - | --- | --- |
| C1 | `.github/workflows/ci.yml` runs backend pytest, frontend tsc, and `flask validate-data` on every PR to `dev` or `main` | **FIXED** (was: PR only triggered on `main`; added `dev` to the pull_request branches list) |
| C2 | `.github/workflows/deploy.yml` triggers Render deploy hook on push to `main`, references `RENDER_DEPLOY_HOOK_URL` secret | PRESENT |

## Documentation

| # | Requirement | State |
| - | --- | --- |
| D1 | `docs/deployment.md` — service creation order, env-var catalogue, Cloudflare DNS table + Full-not-Strict SSL, custom domain setup, initial migration & seed, smoke tests | **FIXED** (was: covered DNS and custom domains but not an explicit DB-first-then-backend-then-frontend creation order, smoke tests were thin — expanded) |
| D2 | `docs/production_setup.md` — `flask db upgrade`, seed commands, health check verification, secret rotation | **FIXED** (was: covered upgrade+seed+health; added secret rotation section) |
| D3 | `docs/rollback.md` — Render rollback, Postgres backup restore, emergency CORS bypass | **FIXED** (was: missing — new file added) |

---

## Manual Steps Required Before Launch

These cannot be done from the repo; they must be performed in the Render
and Cloudflare dashboards by an operator with the right credentials.

1. **Render**: Connect the repo as a Blueprint (`render.yaml`). This creates
   `epochforge-db`, `epochforge-redis`, `epochforge-api`, `epochforge-frontend`
   in one pass.
2. **Render → `epochforge-api` → Environment**: populate the `sync: false`
   secrets (values sourced from Discord developer portal and
   `python -c "import secrets; print(secrets.token_hex(32))"`):
   `SECRET_KEY`, `JWT_SECRET_KEY`,
   `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`,
   `DISCORD_REDIRECT_URI=https://api.epochforge.gg/api/auth/discord/authorized`,
   `DISCORD_IMPORT_WEBHOOK_URL` (optional).
   `DATABASE_URL` and `REDIS_URL` are wired automatically by the blueprint.
3. **Render → each service → Custom Domains**:
   - `epochforge-api`: `api.epochforge.gg`
   - `epochforge-frontend`: `epochforge.gg`, `www.epochforge.gg`
4. **Render → each custom domain**: uncheck "Redirect HTTP to HTTPS" (Cloudflare
   handles that).
5. **Cloudflare → DNS → Records**: add three proxied CNAMEs
   (`@`, `www`, `api` → each target's `*.onrender.com` host).
6. **Cloudflare → SSL/TLS → Overview**: set mode to **Full** (not
   Full (strict)) until Render has issued the custom-domain cert, then
   re-evaluate.
7. **Cloudflare → SSL/TLS → Edge Certificates**: enable "Always Use HTTPS"
   and "Automatic HTTPS Rewrites".
8. **Render → `epochforge-api` → Settings → Deploy Hook**: copy the URL and
   save it in GitHub → Settings → Secrets and variables → Actions as
   `RENDER_DEPLOY_HOOK_URL`.
9. **Render → `epochforge-api` → Shell** (one-off, after first deploy):
   ```
   flask seed
   flask seed-passives
   ```
   `flask db upgrade` already runs on every deploy via `preDeployCommand`.
10. **Smoke test**: follow the checklist in `docs/deployment.md` §5.
