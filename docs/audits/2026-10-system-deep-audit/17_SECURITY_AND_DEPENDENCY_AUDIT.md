# 17 — Security and Dependency Audit

Audit date: 2026-10-06
Scope: `le-the-forge` at `main` HEAD `1efcef7` (2026-05-14), plus dependency posture of `last-epoch-data` at `73e2ab0` (2026-05-31).
Mode: read-only. No source, config, lockfile, branch, or deployment was changed. All installs went into throwaway virtualenvs / gitignored `node_modules`.

## 1. Purpose

Establish, with evidence, (a) how stale and how vulnerable the dependency set is after ~5 months of inactivity, and (b) the current security posture of the web app (auth, tokens, CORS, CSRF, secrets, SSRF, injection, filesystem access, debug routes, rate limiting, desktop shell, committed artifacts).

## 2. Method (commands verbatim)

Scratch root: `$S=<scratch>`

```
# Python deps (backend), Python 3.11.17
python3.11 -m venv $S/venv-backend
$S/venv-backend/bin/pip install -r backend/requirements.txt
$S/venv-backend/bin/pip list --outdated --format=columns
python3.11 -m venv $S/venv-audit && $S/venv-audit/bin/pip install pip-audit
$S/venv-audit/bin/pip-audit -r backend/requirements.txt --format json -o $S/pip-audit-req.json
$S/venv-audit/bin/pip-audit --path $S/venv-backend/lib/python3.11/site-packages --format json -o $S/pip-audit-env.json
# extractor deps
$S/venv-led/bin/pip list --outdated
$S/venv-audit/bin/pip-audit --path $S/venv-led/lib/python3.11/site-packages --format json -o $S/pip-audit-led.json

# Node deps (Node v20.20.0 / npm 10.8.2 from /opt/node20)
cd frontend && npm ci && npm outdated
npm audit --json ; npm audit --omit=dev --json
cd .. && npm audit --json ; npm audit --omit=dev --json     # root (lockfile only)
npm view <pkg> version                                        # root latest versions

# Code review
grep -rnE "pickle\.loads?|yaml\.load\(|\beval\(|\bexec\(|subprocess|os\.system|shell=True" backend --include=*.py
python3 (script) — enumerate every POST/PUT/PATCH/DELETE route in backend/app/routes and whether login_required is on it
git grep -nIE "(AKIA…|ghp_…|github_pat_|xox[baprs]-|sk-…|BEGIN … PRIVATE KEY|discord.com/api/webhooks/…|postgres(ql)?://user:pw@)"   # values redacted
git log --all --diff-filter=A --name-only | grep -E "\.env|\.pem$|\.key$"
git ls-files | grep -E "error_log|settings.local|\.env"

# Dynamic proofs (test client, TestingConfig, scratch data copies only)
PYTHONPATH=. python $S/poc_admin.py $S      # PATCH /api/admin/affixes/<id> without auth, AFFIXES_PATH redirected to $S/affixes-copy.json
PYTHONPATH=. python $S/poc_limiter.py memory://  and  redis://127.0.0.1:6391/0   (local throwaway redis-server)
python -c "import sqlalchemy as sa; sa.create_engine('postgresql://u:p@h/db')"
```

`git status --short` was checked after every dynamic proof; the repository working tree was unchanged (only the new audit folder is untracked).

## 3. Findings summary

| ID | Severity | Title |
|---|---|---|
| SEC-1 | P0 | Unauthenticated `PATCH /api/admin/affixes/<id>` rewrites `data/items/affixes.json` on the server |
| SEC-2 | P0 (runtime) | Unpinned SQLAlchemy resolves to 2.1.x → default Postgres driver becomes `psycopg` (not installed) → backend cannot create its engine on any fresh build |
| SEC-3 | P1 | IDOR: `PATCH /api/builds/<slug>/skills/<skill_id>/nodes/<node_id>` has no auth/ownership check |
| SEC-4 | P1 | Discord OAuth flow has no `state` parameter (login CSRF / account-swap) and no PKCE despite docstring |
| SEC-5 | P1 | Known CVEs in pinned backend deps: flask-cors 4.0.1 (5 advisories), requests 2.32.3 (2), flask 3.0.3, marshmallow 3.21.3, python-dotenv 1.0.1 |
| SEC-6 | P2 | Rate limiting keyed on `request.remote_addr` with no `ProxyFix` behind Render's proxy; silent fallback to per-worker memory storage |
| SEC-7 | P2 | JWT delivered in redirect query string and persisted in `sessionStorage`; no CSP anywhere; no server-side revocation |
| SEC-8 | P2 | Unauthenticated `POST /api/load/game-data` reloads the live pipeline and echoes exception text |
| SEC-9 | P2 | Production-shipped `react-router-dom` 6.30.3 has 3 moderate advisories (open redirect family) |
| SEC-10 | P2 | Dev/build toolchain: 55 npm advisories in frontend (5 critical, 37 high), 31 in root (2 critical, 23 high); Electron 39/41 unsupported |
| SEC-11 | P3 | `ProductionConfig.validate()` gaps: no minimum secret length; default DB URL uses `127.0.0.1` which the `"localhost"` check misses |
| SEC-12 | P3 | Public v2 debug UI routes in production (commit `9f38e8e`); backend experimental `/v2/*` endpoints ungated |
| SEC-13 | P3 | Committed local artifacts: `backend/error_log.txt`, `.claude/settings.local.json` (no secrets found) |
| SEC-14 | P3 | Importer error messages echo raw `requests` exception text to clients |
| SEC-15 | P3 | Electron: secure `webPreferences`, but packaged app cannot start its backend (backend not in `files`, spawned with `FLASK_ENV=production`) |
| SEC-16 | P3 | Unused / unpinned dependencies: `flask-dance` unused; `numpy>=`, `pyyaml>=` and all transitive deps unpinned; no lock/constraints file |
| SEC-17 | P3 | Extractor repo deps: deepdiff 7.0.1 (2 advisories), pytest 8.4.2, setuptools 79.0.1 |

Items reviewed and found **not** to be issues: SSRF in importers, SQL injection, unsafe deserialization, subprocess injection, committed real secrets, Electron renderer isolation, CSRF on the JSON API. Details in §6.

## 4. Detailed findings

### SEC-1 (P0) — Unauthenticated admin write to game data file
- `backend/app/routes/admin.py:68-93` — `@admin_bp.patch("/affixes/<affix_id>")` has only `@limiter.limit("30 per minute")`; no `login_required`, no `is_admin` check (contrast `admin.py:96-108`, where `/import-failures` does check `is_admin`).
- `admin.py:36-38` — `_save_affixes` opens `data/items/affixes.json` for **write**. Field values are not type-validated (`admin.py:83-86`; allowlisted keys only).
- Blueprint is mounted in production: `backend/app/__init__.py:234` (`/api/admin`).
- Request-time readers of that file: `backend/app/routes/ref.py:126-127`, and `admin.py:28-33`.
- **Dynamic proof:** test client, no `Authorization` header, `AFFIXES_PATH` redirected to a scratch copy → `status 200`, `persisted_name_changed True`.
- Impact: any anonymous internet client can rename/retag affixes or inject malformed `tiers` into reference data served to every user until the next deploy/restart (Render disk is ephemeral). Malformed types can also break dependent endpoints (DoS). Exploitability against production: HIGH confidence for the code path; whether production currently exposes it was **not** tested (no production traffic allowed in this audit).

### SEC-2 (P0, runtime-incompatible) — SQLAlchemy 2.1 changes the default Postgres driver
- `backend/requirements.txt` pins `flask-sqlalchemy==3.1.1` and `psycopg2-binary==2.9.10` but **not** `sqlalchemy`. Fresh install on 2026-10-06 resolved `sqlalchemy-2.1.3` (`$S/pip-backend.log`).
- SQLAlchemy 2.1.0 was released 2026-09-24 (PyPI upload time); in 2.1 `postgresql://` maps to the `psycopg` (v3) dialect (`site-packages/sqlalchemy/dialects/postgresql/__init__.py:99` → `base.dialect = dialect = psycopg.dialect`).
- `python -c "import sqlalchemy as sa; sa.create_engine('postgresql://u:p@h/db')"` → `ModuleNotFoundError: No module named 'psycopg'`.
- The same error makes 6 tests in `tests/test_deployment_readiness.py` error at setup (`create_app("production")` → `db.init_app` → `create_engine`). With `sqlalchemy<2.1` (2.0.54) those tests pass (34/34 for that file + weaver file).
- Render `buildCommand: pip install -r requirements.txt` (`render.yaml:42`) and `backend/Dockerfile:15` both resolve fresh. `wsgi.py:4` calls `create_app` at import, so gunicorn workers and the `preDeployCommand: flask db upgrade` (`render.yaml:43`) would fail on the next build.
- Impact: the currently running production instance (built 2026-05-15) is presumably unaffected, but **any redeploy, rebuild, or new container from today fails to boot**. Classified here as dependency staleness; cross-referenced as RT-1 in report 02.

### SEC-3 (P1) — IDOR on skill-node allocation
- `backend/app/routes/skills.py:281-370` — `allocate_skill_node` loads any build by slug and commits `build_skill.spec_tree` (`skills.py:360-362`) with no `get_current_user()` / author check. Compare `builds.py:199-215` (`update_build`) which enforces ownership for owned builds.
- Impact: anyone who knows a build slug (slugs are public in listings) can modify skill allocations on another user's saved build. Confidence high (static).

### SEC-4 (P1) — OAuth without `state`/PKCE
- `backend/app/routes/auth.py:29-56` builds the Discord authorize URL with `client_id`, `redirect_uri`, `response_type=code`, `scope` only — no `state`, no `code_challenge`. Docstring at `auth.py:32` claims "PKCE flow".
- `auth.py:59-155` callback accepts any `code` without binding to the initiating browser.
- Impact: login CSRF — an attacker can make a victim's browser complete login with the attacker's Discord code, so builds the victim saves land in the attacker's account. `flask-dance` is listed in requirements but unused (`grep -rn flask_dance backend/app` → 0 hits).

### SEC-5 (P1) — Known vulnerabilities in pinned backend dependencies
pip-audit (`-r backend/requirements.txt`): **20 records / 6 packages** (deduplicated: 10 distinct advisories). Environment scan adds setuptools (22 records / 7 packages).

| Package | Pinned | Advisories (aliases) | Fixed in | Category |
|---|---|---|---|---|
| flask-cors | 4.0.1 | PYSEC-2024-71 (CVE-2024-6221), CVE-2024-6844, CVE-2024-6866, CVE-2024-6839 | 4.0.2 / 6.0.0 | SECURITY-CRITICAL (CORS matching/path/case handling) |
| requests | 2.32.3 | CVE-2024-47081 (netrc credential leak), CVE-2026-25645 | 2.32.4 / 2.33.0 | SECURITY-CRITICAL |
| flask | 3.0.3 | CVE-2026-27205 | 3.1.3 | IMPORTANT |
| marshmallow | 3.21.3 | CVE-2025-68480 | 3.26.2 | IMPORTANT (all request validation goes through it) |
| python-dotenv | 1.0.1 | CVE-2026-28684 | 1.2.2 | IMPORTANT |
| pytest | 8.2.2 | CVE-2025-71176 | 9.0.3 | OPTIONAL (test-only) |
| setuptools (venv) | 79.0.1 | CVE-2026-59890 | 83.0.0 | OPTIONAL (build-time) |

Impact assessment of flask-cors CVEs is limited by the fact that production uses a fixed origin list (`app/__init__.py:79-104`) and Bearer tokens, not cookies; still upgrade-worthy.

### SEC-6 (P2) — Rate limiting effectiveness
- `app/__init__.py:16` `Limiter(key_func=get_remote_address)`; `grep -rn "ProxyFix|X-Forwarded-For" backend/app backend/wsgi.py` → 0 hits. On Render, `remote_addr` is the edge proxy, so all clients likely share buckets (one abuser can lock everyone out of `/api/import/url` at 20/min) — **medium** confidence; Render's exact header behaviour UNKNOWN from repo.
- `app/__init__.py:31-45`: if Redis ping fails at boot, limiter silently switches to `memory://` → per-gunicorn-worker counters (4 workers, `render.yaml:44`) = ~4× limits, reset per deploy.
- Dynamic check: limiter works with both `memory://` and a local Redis (`codes … [400, 429, 429]` after 20 calls); `X-Forwarded-For` is ignored (good against spoofing, bad behind a proxy).
- Note: `RATELIMIT_ENABLED = False` in `TestingConfig` (`config.py:146`), so the 11k-test suite never exercises limiter/limits compatibility (`limits` 5.8.0 resolved unpinned).

### SEC-7 (P2) — Token handling
- JWT is placed in the redirect URL: `auth.py:153-155` (`/auth/callback?token=…`); also `auth.py:181-183` for dev login.
- Frontend persists it: `frontend/src/components/features/AuthCallbackPage.tsx:28` `sessionStorage.setItem("forge_token", token)`; restored in `frontend/src/App.tsx:107`. The comment at `frontend/src/lib/api.ts:7` ("stored in module-level memory (not localStorage)") is accurate about localStorage but omits the sessionStorage persistence.
- No Content-Security-Policy: none in `render.yaml` static-site headers (`render.yaml:103-106` only sets Cache-Control), `frontend/nginx.conf`, or `frontend/index.html`. Any XSS would expose the token.
- Logout is client-side only (`auth.py:193-197`); tokens remain valid for `JWT_ACCESS_TOKEN_EXPIRES` (default 3600 s, `config.py:10-12`).
- Positive: Bearer header auth (no cookies) means classic CSRF does not apply to the JSON API; no `dangerouslySetInnerHTML`/`eval`/`new Function` in `frontend/src` (grep → 0 hits outside tests).

### SEC-8 (P2) — Unauthenticated pipeline reload
- `backend/app/routes/load.py:21-45` — `POST /api/load/game-data`, limit 5/min, no auth; calls `pipeline.reload()` on the live app and returns `f"Pipeline reload failed: {exc}"`. CPU-heavy endpoint reachable anonymously; information disclosure via exception text.

### SEC-9 (P2) — Production frontend dependency advisories
`npm audit --omit=dev` (frontend): **3 moderate, 0 high, 0 critical** — `react-router-dom` 6.30.3 / `react-router` / `@remix-run/router` (open redirect via protocol-relative or backslash paths). Fix available within 6.x (`npm outdated`: wanted 6.30.6). Root `--omit=dev`: 0.

### SEC-10 (P2) — Dev/build toolchain advisories and unsupported Electron
| Lockfile | info | low | moderate | high | critical | total |
|---|---|---|---|---|---|---|
| `frontend/package-lock.json` (all) | 0 | 1 | 12 | 37 | 5 | 55 |
| `frontend/package-lock.json` (`--omit=dev`) | 0 | 0 | 3 | 0 | 0 | 3 |
| `package-lock.json` root (all) | 0 | 1 | 5 | 23 | 2 | 31 |
| `package-lock.json` root (`--omit=dev`) | 0 | 0 | 0 | 0 | 0 | 0 |

Criticals (frontend): `vitest` ≤4.0.0-beta.19 (UI server file read/exec), `tinypool` (prototype-pollution RCE gadget), `tar`, `shell-quote` (via `concurrently`). Highs include `vite` ≤6.4.2 (path traversal in dev server), `postcss` ≤8.5.22, `electron` ≤41.10.5, `electron-builder` chain, `axios`, `lodash`, `ws`. These affect developer machines/CI and the desktop build, not the deployed static bundle.
Electron versions: root lock `39.8.3`, frontend lock `41.0.3` (two different Electron majors declared: `package.json` `^39.8.3` vs `frontend/package.json` `^41.0.3`); latest is `44.5.1` (`npm view electron version`). Both are outside Electron's three-latest-majors support window.

### SEC-11 (P3) — Production config validation gaps
- `backend/config.py:107-115` only rejects the exact literal defaults (`"dev-secret"`, `"jwt-dev-secret"`, empty). No minimum length/entropy.
- `config.py:119-121` checks `"localhost" in DATABASE_URL`, but the default is `postgresql://forge:forgedev@127.0.0.1:5432/the_forge` (`config.py:14-16`) — the default would pass validation.
- `config.py:43-67` defines `FORGE_SAFE_AFFIX_CATALOG_ENABLED` and `FORGE_SAFE_AFFIX_EXPORT_PATH` twice with different truthiness parsing; second definition wins.
- `wsgi.py:4` defaults to `production` when `FLASK_ENV` is unset (good); `config["default"]` is Development (`config.py:153`) and is only reached via `create_app()` default arg.
- Dev login gate: `auth.py:166-170` uses `current_app.debug`; safe while production never sets DEBUG.

### SEC-12 (P3) — Public debug surfaces
- Commit `9f38e8e` ("fix: expose v2 debug routes") moved 10 `/debug/v2*` frontend routes out of the `IS_DEV` guard (`frontend/src/App.tsx:264-276`). They call backend `/api/experimental/v2/*` (41 GET routes, `backend/app/routes/experimental.py:78-1035`); only the `forge-safe-affixes` routes are env-gated (`experimental.py:82,106,174`; `debug.py:29`). All are read-only GETs over committed bundles; file paths come from config, not request input (`experimental.py:1195-1300`). Risk: information exposure / unexpected load, not code execution.
- General debug pages (`/debug`, `/viz-debug`, `/craft-debug`, `/movement-debug`, `/data-flow`) remain dev-only (`App.tsx:279-287`).

### SEC-13 (P3) — Committed local artifacts
- `backend/error_log.txt` (74 bytes; a local Windows venv path error) and `.claude/settings.local.json` (37 local command-allow entries; no tokens/secrets matched) were committed in `c3324f9` (2026-04-12). Hygiene only; both should be gitignored.

### SEC-14 (P3) — Error text reflection
- `backend/app/routes/import_route.py:358` and `backend/app/services/importers/lastepochtools_importer.py:727-731` return `f"Network error fetching build: {exc}"` to clients.

### SEC-15 (P3) — Electron
- Good: `electron/main.js:143-146` `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`; `preload.js` exposes 3 members via `contextBridge`; `setWindowOpenHandler` denies new windows (`main.js:169-172`).
- Gaps: `shell.openExternal` for any `http*` URL (`main.js:170`) with no allowlist; no `will-navigate` guard. Packaged app spawns backend with `FLASK_ENV=production` (`main.js:65`), which will hit `ProductionConfig.validate()` (requires Discord secrets and non-localhost `FRONTEND_URL`), and `package.json` `build.files` does not include `backend/`. Desktop build is very likely non-functional (UNKNOWN whether it is distributed).

### SEC-16 (P3) — Dependency pinning hygiene
- `numpy>=1.26.0`, `pyyaml>=6.0` unbounded (`backend/requirements.txt:18-19`); all transitive deps (SQLAlchemy, Werkzeug, PyJWT, limits, alembic) unpinned — root cause of SEC-2.
- `flask-dance==7.1.0` unused. `pytest`, `pytest-flask`, `factory-boy` are installed into the production image (no dev/prod split).
- Render frontend uses `npm install` (`render.yaml:89`), not `npm ci`, so production builds may drift from `frontend/package-lock.json`.

### SEC-17 (P3) — Extractor repo dependency posture
pip-audit on `last-epoch-data` venv: 8 records / 3 packages — `deepdiff` 7.0.1 (PYSEC-2026-2445, PYSEC-2026-327; fixed 8.6.1/8.6.2), `pytest` 8.4.2, `setuptools` 79.0.1. Outdated: `pythonnet` 3.0.5→3.2.0, `UnityPy` 1.25.0→1.25.4, `deepdiff` 7.0.1→9.1.0. Requirements use wildcard majors (`pydantic==2.*`, `jsonschema==4.*`, `pytest==8.*`, `deepdiff==7.*`, `vdf==3.*`). Offline tooling; low exposure.

## 5. Outdated dependency inventory

### Backend (`pip list --outdated`, venv-backend)
| Package | Current | Latest | Category |
|---|---|---|---|
| Flask-Cors | 4.0.1 | 6.0.5 | SECURITY-CRITICAL |
| requests | 2.32.3 | 2.34.2 | SECURITY-CRITICAL |
| SQLAlchemy (transitive) | 2.1.3 resolved | — | RUNTIME-INCOMPATIBLE (needs explicit pin `<2.1` or psycopg3) |
| Flask | 3.0.3 | 3.1.3 | IMPORTANT (CVE) |
| marshmallow | 3.21.3 | 4.3.1 | IMPORTANT (CVE; 3.26.2 fixes within 3.x) |
| python-dotenv | 1.0.1 | 1.2.4 | IMPORTANT (CVE) |
| gunicorn | 22.0.0 | 26.2.0 | IMPORTANT |
| Flask-Limiter | 3.7.0 | 4.1.1 | IMPORTANT |
| redis | 5.0.7 | 8.1.0 | OPTIONAL MODERNIZATION |
| Flask-JWT-Extended | 4.6.0 | 4.7.4 | OPTIONAL |
| Flask-Migrate | 4.0.7 | 4.1.0 | OPTIONAL |
| marshmallow-sqlalchemy | 1.1.0 | 1.5.0 | OPTIONAL |
| psycopg2-binary | 2.9.10 | 2.9.13 | OPTIONAL |
| pytest | 8.2.2 | 9.1.1 | OPTIONAL (CVE, test-only) |
| factory-boy | 3.3.0 | 3.3.3 | OPTIONAL |
| rich (transitive) | 13.9.4 | 15.0.0 | OPTIONAL |
| setuptools | 79.0.1 | 84.0.0 | OPTIONAL |

16 outdated packages in total.

### Frontend (`npm outdated`, 27 packages behind latest)
Major-behind: react/react-dom 18→19, react-router-dom 6→7, vite 5.4.21→8.3.3, vitest 1.6.1→4.1.11, typescript 5.9.3→7.0.2, eslint 8.57.1→10.12.0 (8.x EOL), @typescript-eslint 7→8, tailwindcss 3→4, jsdom 24→29, zustand 4→5, tailwind-merge 2→3, @testing-library/react 14→16, @vitejs/plugin-react 4→6. Within-range: @tanstack/react-query 5.91→5.104, recharts 3.8.1→3.10.1, postcss 8.5.8→8.5.29, electron 41.0.3→41.7.1, electron-builder 26.8.1→26.15.3.
Categories: vite/vitest/postcss → SECURITY-CRITICAL for dev machines; react-router-dom 6.30.6 → IMPORTANT (shipped); remaining majors → OPTIONAL MODERNIZATION.

### Root (lockfile vs `npm view … version`)
electron 39.8.3→44.5.1, electron-builder 25.1.8→26.15.3, concurrently 8.2.2→10.0.5, wait-on 8.0.5→9.5.1, recharts 3.8.0→3.10.1. Root also declares `recharts` as a runtime dependency although no root code uses it (frontend has its own).

### Runtimes
| Runtime | Declared | Status on 2026-10-06 |
|---|---|---|
| Node | 20 (`ci.yml`, `render.yaml:93-94`, `frontend/Dockerfile`) | Node 20 EOL 2026-04-30 — RUNTIME/SECURITY |
| GitHub Actions | `actions/checkout@v4`, `setup-python@v5`, `setup-node@v4` | check-run annotations: Node 20 actions deprecated, removed from runners 2026-09-16 |
| Python | 3.11 (`render.yaml:52-53`, Dockerfile, CI) | supported until 2027-10; `mypy.ini` targets 3.12 (mismatch) |
| Postgres | 15 | supported |
| Redis | 7 (compose) / Render managed | supported |

## 6. Reviewed and not found to be an issue (with evidence)

- **SSRF in importers:** host is hard-coded; only a `[A-Za-z0-9_\-]+` code is taken from user input — `import_route.py:322-337`, `lastepochtools_importer.py:593,693-694`, `maxroll_importer.py:265-267,750-786`. Not exploitable for arbitrary hosts.
- **Unsafe deserialization / eval:** no `pickle`, `yaml.load` (non-safe), `eval`, `exec`, `os.system`, `shell=True` in `backend/` or `scripts/` Python. Only `subprocess.check_output(["git","rev-parse","--short","HEAD"])` with fixed args (`app/routes/version.py:47-55`).
- **SQL injection:** no f-string/`%` SQL in `backend/app` (grep for `text(f"`, `execute(f"`).
- **Filesystem from request input:** all file paths are module constants or config values (`experimental.py:1195-1300`, `debug.py:81-85`, `ref.py:126,159`, `passives.py:24`). Only write path is SEC-1.
- **CORS:** production origins fixed to `https://epochforge.gg` and `https://www.epochforge.gg` (`app/__init__.py:79-83`); `supports_credentials=True` but no cookies are used.
- **Security headers:** nosniff, DENY framing, Referrer-Policy, Permissions-Policy, HSTS in production (`app/__init__.py:108-127`) — API only; static site has none besides Cache-Control.
- **Secrets in repo:** pattern scan hit 9 lines, all local-development Postgres URLs with the dev password or test fixtures (`.env.example:14`, `config.py:15`, `docker-compose.yml:41`, `docs/LOCAL_DEVELOPMENT.md:22,28`, two test files); `docker-compose.prod.yml` uses `${…}` interpolation. No `.env`, `.pem`, or `.key` was ever added in history (only `.env.example`). Render secrets are `sync: false` (`render.yaml:70-80`).
- **JWT identity type:** `User.id` is `String(36)` (`app/models/__init__.py:55`) so PyJWT ≥2.10's string-`sub` rule is satisfied.

## 7. UNKNOWNs

- Whether production currently runs with Redis reachable (limiter storage) — requires production access.
- Render proxy client-IP behaviour (SEC-6 severity depends on it).
- Whether the desktop (Electron) build is distributed to anyone.
- Whether `/api/admin/affixes` PATCH has already been abused in production (no log access).
- Branch protection settings on `main` (`gh api …/branches/main/protection` → HTTP 403 for this token).

## 8. What this does NOT prove

- No penetration test or traffic was sent to epochforge.gg / api.epochforge.gg; all exploit confirmations are against a local test client with scratch data copies.
- pip-audit/npm audit reflect advisory databases as of 2026-10-06; reachability of each advisory in this codebase was not individually proven except where stated.
- Absence of grep hits is not proof of absence (e.g. obfuscated secrets, dynamic SQL built elsewhere).
- Frontend XSS was only screened for obvious sinks; no DOM-level review of all components.
