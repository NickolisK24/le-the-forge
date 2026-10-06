# 16 — Infrastructure and Deployment Audit

Audit date: 2026-10-06. Scope: `le-the-forge` `main` @ `1efcef7` (the deployed commit). GitHub state was read through the API (read-only). No production systems were touched. Live HTTP checks were refused by the sandbox egress proxy (`CONNECT tunnel failed, response 403`), so the live state is **UNKNOWN**. That 403 is the proxy's, not the site's.

## 1. Headline facts

1. **The next deploy is very likely to fail at boot.** `backend/requirements.txt` pins `flask-sqlalchemy==3.1.1` but not `SQLAlchemy`. A fresh `pip install -r requirements.txt` (Python 3.11, today) resolves **SQLAlchemy 2.1.3**, where `postgresql://` defaults to the `psycopg` (v3) driver. Only `psycopg2-binary` is installed. Reproduced: `create_engine('postgresql://…')` raises `ModuleNotFoundError: No module named 'psycopg'`, and `create_app("production")` fails. Render runs `pip install -r requirements.txt` (`render.yaml:42`), then `preDeployCommand: flask db upgrade` (`render.yaml:43`), which calls `create_app` → the deploy fails. Render normally keeps the previous instance live when a pre-deploy step fails; this was not verified (**UNKNOWN**). `dev`'s `requirements.txt` is identical, so the problem is not fixed there either.
2. **`main` deploys without CI gating.** `ci.yml` triggers only on push to `dev` and on PRs to `dev`/`main` (`ci.yml:3-10`). `deploy.yml` fires on every push to `main` (`deploy.yml:3-6`) with no `needs:`/status dependency. Evidence: release PR #371 CI run #655 **started 23:43:30Z and concluded `failure` at 23:49:24Z** on 2026-05-14. The merge to `main` and the deploy run (`25892074924`, `success`) happened at **23:44:04Z**, before CI finished and while it was failing. `main` is marked `protected`, but this sequence shows that required status checks are either not enforced or were bypassed (branch-protection detail **UNKNOWN**).
3. **CI on `dev` has been red for 261 consecutive push runs** (since 2026-05-09, run #527). `dev` (`558557c`, PRs up to #571) is roughly 200 PRs ahead of deployed `main` (PR #372).
4. **Unauthenticated write endpoint in production.** `PATCH /api/admin/affixes/<id>` (`backend/app/routes/admin.py:68-87`) has no `@login_required` or admin check. It rewrites `data/items/affixes.json` on the instance disk. `GET /api/admin/affixes` is also unauthenticated. On Render the disk is ephemeral and per-instance: edits persist until the next deploy or restart and are invisible to version control. Only `/import-failures` (`admin.py:96-98`) is protected. See also report 17.

## 2. Actual production architecture (from `render.yaml`)

| Component | Render type / plan | Domain | Deploy | Notes |
|---|---|---|---|---|
| `epochforge-db` | Postgres 15, `starter` (`render.yaml:16-21`) | private | — | Backups: `docs/rollback.md:49` claims a daily snapshot on the Starter plan (**UNKNOWN**, dashboard-only) |
| `epochforge-redis` | Key Value, `starter`, `allkeys-lru` (`render.yaml:27-31`) | private | — | Used for rate limits, cache (`app/utils/cache.py`) and job state (`app/utils/jobs.py`) |
| `epochforge-api` | Python web, `starter`, oregon (`render.yaml:36-46`) | api.epochforge.gg | `autoDeploy: false`; deploy hook from GH Actions | `gunicorn --workers=4 --threads=2 --timeout=120 --preload`; `healthCheckPath: /api/health` |
| `epochforge-frontend` | static (`render.yaml:85-104`) | epochforge.gg, www | `autoDeploy: false` | `npm install && npm run build`; SPA rewrite; `VITE_API_BASE_URL=https://api.epochforge.gg` |
| Worker / cron | **none** | — | — | Background jobs run in-process threads inside web workers |

### Deploy path

`push main` → `deploy.yml` POSTs `secrets.RENDER_DEPLOY_HOOK_URL`. That is **one** hook, and a Render deploy hook targets **one** service. Both services have `autoDeploy: false`, so only one of the two (API or frontend) is deployed automatically. The other requires a manual dashboard deploy. Which service the hook belongs to is **UNKNOWN**. This setup risks frontend/backend version skew.

`deploy.yml` history: 7 runs. #1 (2026-04-21) failed (hook unset); #2–#7 succeeded; the last is #7 at 2026-05-15T00:08:56Z (`1efcef7`).

### Resource limits

- Render `starter` web = 512 MB RAM (Render published spec; plan specifics **UNKNOWN** for this account). A single `create_app("testing")` process measured **~105 MB max RSS** locally. With `--preload`, 1 master + 4 workers share pages copy-on-write at first, but Python refcounting gradually unshares them. Worst case is about 5 × 105 MB ≈ 525 MB before request load, numpy simulations and 2 threads per worker. **OOM risk is plausible.** Render memory graphs would confirm it (**UNKNOWN**).
- Each worker also has its own `ThreadPoolExecutor(max_workers=4)` for jobs (`app/utils/jobs.py:25`), so a single 0.5-CPU instance can run up to 4 × (2 + 4) = 24 concurrent threads.
- `docker-compose.prod.yml` sets a `memory: 1G` limit for the backend and 128M for the frontend. The prod compose file is not what Render runs.
- No autoscaling is configured (no `scaling:` block; instance count 1 by default).
- Persistent disk: none. Writes to `data/` (admin PATCH) are lost on deploy.

### Rollback

`docs/rollback.md` describes Render "Rollback" (redeploys the cached artifact, so it is not affected by the SQLAlchemy resolution problem), `flask db downgrade -1`, and restoring Postgres from a backup. Migrations have a single head (`dd1840cac963`; 15 revisions). One downgrade is a no-op merge (`e2f3a4b5c6d1`). Rollback has never been exercised in CI (**UNKNOWN** whether it has been rehearsed).

## 3. Environment variable contract

Legend: R = required by `ProductionConfig.validate()` (`config.py:100-134`); D = has a code default; S = `sync:false` secret in Render.

| Variable | config.py / code | .env.example | render.yaml | docker-compose.yml | docker-compose.prod.yml | Required in prod? | Notes |
|---|---|---|---|---|---|---|---|
| `SECRET_KEY` | `config.py:8` D | yes | S | yes (dev default) | yes | **R** | |
| `JWT_SECRET_KEY` | `config.py:9` D | yes | S | **missing** | yes | **R** | dev compose falls back to `jwt-dev-secret` |
| `JWT_ACCESS_TOKEN_EXPIRES` | `config.py:11` D | yes | — | — | — | no | |
| `DATABASE_URL` | `config.py:14` D | yes | fromDatabase | yes | yes | **R** (rejects localhost) | value scheme `postgresql://` → see headline 1 |
| `DB_PASSWORD` | — | yes | — | yes | yes | compose only | |
| `REDIS_URL` | `config.py:23,52` D | yes | fromService | yes | yes | no (silent in-memory fallback) | |
| `FLASK_ENV` | `wsgi.py:4` D=`production` | yes | `production` | `development` | `production` | — | |
| `FLASK_APP` | — | — | `wsgi.py` | — | Dockerfile | — | |
| `FRONTEND_URL` | `config.py:38` D | yes | set | yes | yes | **R** (rejects localhost) | CORS in prod is hard-coded anyway (`app/__init__.py:80-84`) |
| `DISCORD_CLIENT_ID` | `config.py:32` | yes | S | yes | yes | **R** | |
| `DISCORD_CLIENT_SECRET` | `config.py:33` | yes | S | yes | yes | **R** | |
| `DISCORD_REDIRECT_URI` | `config.py:34-36` D=localhost | yes | S | **missing** | yes | **not validated** | if unset in prod, OAuth redirects to localhost |
| `DISCORD_IMPORT_WEBHOOK_URL` | `discord_notifier.py:18` | yes (empty) | S | yes | yes | no | read at import time |
| `DATA_VERSION` / `CURRENT_PATCH` / `CURRENT_SEASON` | `config.py:26-30` D=`1.0.0`/`1.4.3`/`4` | yes | **missing** | — | — | no | prod reports defaults; disagrees with `data/version.json` ("unknown") |
| `DATA_BUNDLE_DIR` | **unused** | yes | — | — | — | — | code reads **`FORGE_DATA_BUNDLE_DIR`** (`app/game_data/bundle_compat.py:20,77`) → name mismatch |
| `FORGE_SAFE_AFFIX_*` (7 vars) | `config.py:42-70` | yes | — | — | — | no | `FORGE_SAFE_AFFIX_CATALOG_ENABLED` / `_EXPORT_PATH` are defined **twice** with different parsing (`config.py:42` vs `61`; the later one wins) |
| `RATE_LIMIT_SIMULATE_*` (3) | routes | yes | — | — | — | no | |
| `VITE_API_BASE_URL` | `frontend/src/lib/api.ts:52` | yes | set | `http://backend:5000/api` | — | build-time | dev compose value is a container hostname the browser cannot resolve |
| `VITE_API_URL` | legacy fallback `api.ts:53` | — | — | — | build arg `/api` | build-time | `frontend/Dockerfile` uses the legacy name |
| `GUNICORN_*` | Dockerfile | commented | — (inline flags) | — | yes | — | |
| `PYTHON_VERSION`, `NODE_VERSION`, `PYTHONUNBUFFERED` | — | — | set | — | — | Render | |
| `RENDER_DEPLOY_HOOK_URL` | GH secret (`deploy.yml`) | — | — | — | — | for deploy | presence confirmed only by run success (#2–#7) |
| `LOG_FORMAT_JSON`, `LOG_LEVEL` | class attrs, not env | — | — | — | — | — | cannot be overridden by env |

No secret values were read or printed.

## 4. Config that refers to unused or divergent services

| Item | Status |
|---|---|
| Redis | **Used** (limiter, cache, jobs). If it is unreachable at boot, the app silently degrades to per-process limits. |
| Celery / RQ | Not present |
| nginx (`frontend/nginx.conf`, `frontend/Dockerfile`) | Used only by `docker-compose.prod.yml`. Render serves the static site itself and ignores this config. Two prod paths diverge: nginx proxies `/api/` same-origin, while Render uses the cross-origin `api.` subdomain. |
| `backend/Procfile` (`web: gunicorn wsgi:app`, `release: flask db upgrade`) | Heroku-style. Not used by Render (`startCommand` overrides it). Divergent worker settings. |
| `backend/entrypoint.sh` | Docker only. Runs `flask seed` / `seed-passives` with `2>/dev/null \|\| echo skipped`, which hides seed failures. Render does not seed. |
| `docker-compose.yml` dev backend | `flask run --debug` with the `/app` bind-mount. `FRONTEND_URL` is localhost. |
| Electron (`electron/main.js`, root `package.json` `build:desktop`) | Spawns a local Flask backend (PyInstaller bundle or system Python). No release workflow, no signing and no distribution channel in the repo. Last touched 2026-03-31. Distribution status **UNKNOWN**/dormant. |
| `.github/workflows/sync-main-to-dev.yml` | Opens main→dev sync PRs as the GitHub Actions identity using `-X ours` |

## 5. Branches and CI

| Repo | Branches | Protected | CI on default branch |
|---|---|---|---|
| le-the-forge | `dev` (`558557c`), `main` (`1efcef7`) | both `protected: true` | `main`: no push-triggered CI. `dev`: 261 consecutive failures |
| last-epoch-data | `main` only (`73e2ab0`) | **false** | Regeneration gate failing for 62 consecutive `main` pushes |

CI coverage gaps (`ci.yml`): no frontend tests (vitest) and no `vite build`. No Postgres service, so 56 contract tests skip. `pytest -x`. No dependency lockfile or pip constraints, so builds are non-reproducible (`numpy>=1.26.0`, `pyyaml>=6.0`, and SQLAlchemy/Werkzeug/limits are transitive and unpinned). Locally they resolved to Werkzeug 3.1.9, limits 5.8.0 and numpy 2.5.3.

## 6. Commands used

```
cat render.yaml docker-compose.yml docker-compose.prod.yml backend/Dockerfile frontend/Dockerfile frontend/nginx.conf backend/entrypoint.sh backend/Procfile
sed -E 's/=.+/=<redacted>/' .env.example
cat -n backend/config.py backend/app/__init__.py backend/app/routes/health.py backend/app/routes/admin.py
python3.11 -m venv v && v/bin/pip install -r backend/requirements.txt && v/bin/pip list | grep -i sqlalchemy   # 2.1.3
v/bin/python -c "import sqlalchemy as sa; sa.create_engine('postgresql://u:p@h/db')"  # ModuleNotFoundError psycopg
v/bin/python -m pytest tests/test_deployment_readiness.py -x   # 3 passed, 1 error
python -c "...create_app('testing'); resource.getrusage(...).ru_maxrss"   # ~105 MB
GitHub API (read-only): list_branches, actions_list list_workflow_runs (ci.yml, deploy.yml), list_workflow_jobs, get_file_contents(ref=dev)
curl -sS -D - https://api.epochforge.gg/api/health   # proxy refused
```

## 7. UNKNOWNs

- Live health/version output; Render plan specs and memory graphs; whether the deploy hook targets the API or the frontend; branch-protection rule details (required checks, admin bypass); Postgres backup and PITR settings; whether `.git` exists at Render runtime (affects `/api/version.commit`); whether Render's build cache would pin an older SQLAlchemy (unlikely, since pip resolves anew).

## 8. What this does NOT prove

- It does not prove that production is currently down. The running instance was built on or before 2026-05-15 and may hold an older SQLAlchemy. The risk applies to the **next** build.
- The OOM estimate is an upper-bound calculation from one local RSS measurement, not an observed incident.
- The unauthenticated PATCH finding is based on code reading only. No request was sent to production.
