# 01 — System Map (Phase 0)

Audit date: 2026-10-06
Scope: `le-the-forge` @ `main` `1efcef76` (2026-05-14), `last-epoch-data` @ `73e2ab0` (2026-05-31), `le-parser` (archived).
Method: read code, configs and git metadata; dumped the live Flask URL map from an isolated snapshot (`git archive HEAD`) in a scratch virtualenv; static import-reachability analysis; ran backend and frontend test suites on the snapshot (results in section 9). Nothing in either repo was modified.

Legend for status: **active** = reachable from a production entrypoint; **dev-only** = only reachable from local tooling or dev builds; **legacy** = present and tested but not reachable from production runtime; **abandoned** = scaffold with no working path; **UNKNOWN** = cannot be verified from repo contents.

---

## 1. Repository boundaries

| Repo | Role | Location of truth | Reaches production? |
| --- | --- | --- | --- |
| `le-the-forge` (public, `github.com/NickolisK24/le-the-forge`) | Flask API, React SPA, Electron shell, committed runtime game data (`data/`), committed v2 generated bundles (`docs/generated/`) | `main` deploys to Render | Yes — the only repo Render builds |
| `last-epoch-data` (private) | Windows-host extraction from a local game install → `exports_json/`, governance reports `docs/generated/` (205 files), `data_bundle/` (phase1a) | Committed JSON | **No runtime link.** Data reaches production only after a human copies/transforms it into `le-the-forge` and commits it |
| `le-parser` (archived, 1 commit 2026-03-26) | Earlier JS parser | — | No. Only remnant is a gitlink `le-parser.worktrees/copilot-worktree-2026-03-31T22-17-24` (mode 160000, commit `5135ce4`, no `.gitmodules`) and a string in `backend/scripts/report_v2_source_inventory.py:39`; excluded by `.dockerignore:15-16` |

Branch reality (verified with `git ls-remote --heads origin` and `gh api repos/NickolisK24/le-the-forge/compare/main...dev`): remote has `main` (`1efcef7`) and `dev` (`558557c`, last commit 2026-05-29). **`dev` is 413 commits ahead of `main`, 0 behind, and touches at least 300 files** (the compare API caps at 300). Production deploys from `main`. Everything in this audit describes `main`; some drift may already be addressed on `dev` (UNKNOWN per item).

### How data actually crosses the repo boundary

There are **three incompatible path conventions** for finding `last-epoch-data`:

| Convention | Where | Evidence |
| --- | --- | --- |
| Nested inside `le-the-forge` root (gitignored) | `scripts/sync_game_data.py:21` `SRC_DIR = ROOT / "last-epoch-data" / "exports_json"`; `scripts/generate_tree_data.py:25`; `.gitignore:61-62` | Writes `data/**` and `frontend/src/data/{passiveTrees,skillTrees}/index.ts` |
| Sibling directory | `backend/app/game_data/affix_diagnostic_consumer.py:16` `REPO_ROOT.parent / "last-epoch-data" / "docs" / "generated"`; `docs/WORKSPACE_HEALTHCHECK.md:8-13` | Diagnostics only |
| Hard-coded Windows absolute path `D:\Forge\last-epoch-data\...` | 13 non-doc tracked files (`git grep -l 'D:\\Forge' -- ':!docs'`), incl. `backend/app/game_data/bundle_compat.py:19` and every `backend/scripts/report_v2_*_bundle.py` generator (e.g. `report_v2_item_bundles.py:20`, `report_v2_affix_bundle.py:23`); 28 doc files | Generates the committed `docs/generated/v2_*.json` bundles |

`FORGE_DATA_BUNDLE_DIR` (`bundle_compat.py:20`) is read only by `bundle_compat.resolve_bundle_dir`, whose callers are diagnostic scripts and diagnostic modules (`check_data_bundle.py`, `diff_bundle_items.py`, `report_bundle_item_adapter_map.py`, `bundle_item_diff.py`, `bundle_item_adapter_report.py`). It is **not** set in `render.yaml`, not consumed by any route, and `.env.example` documents a differently-named `DATA_BUNDLE_DIR` that no code reads.

**Conclusion: production runtime reads no `last-epoch-data` artifact.** It reads only files committed to `le-the-forge`:

1. `data/**` (52 files) — loaded at startup by `backend/app/game_data/pipeline.py:45-57` and by several routes directly (`routes/admin.py:24`, `routes/ref.py:126`, `routes/health.py:37`).
2. `backend/app/game_data/skills.json`, `classes.json` (`pipeline.py:47-48`).
3. `docs/generated/v2_*.json` (13 bundles, 97 MB directory) — read lazily by `/experimental/v2/*` and `/api/experimental/v2/*` (`routes/experimental.py:43-56`, `repositories/v2/paths.py:7-8`).
4. `VERSION` (`app/__init__.py:21`).
5. Frontend build-time inputs: `VERSION` (`frontend/vite.config.ts:10`), `frontend/src/data/**` (5.0 MB, generated tree data), `frontend/public/**` (460 files, 31 MB icons), `backend/src/constants/*.ts` (alias `@constants`, `vite.config.ts:33`).

### Render path resolution (rootDir = backend)

`render.yaml:42` sets `rootDir: backend`. Code resolves data paths from `__file__`, not CWD: `pipeline.py:34-36` (`backend/app/game_data/../../..` = repo root), `experimental.py:43` (`parents[3]` = repo root), `repositories/v2/paths.py:7` (`parents[4]` = repo root), `app/__init__.py:21` (`VERSION` at repo root). On Render a full checkout exists and `rootDir` only changes the working directory (Render platform behaviour; not verifiable from the repo — treat as **UNKNOWN but consistent with** the release doc's reported 200s at `docs/release/V2_5_MAIN_RELEASE_READINESS.md:44-63`, which were local test-client results, not production).
In the Docker image (`backend/Dockerfile`, build context `./backend`) the same expressions resolve to `/data`, `/docs/generated`, `/VERSION`: `docker-compose.yml` mounts `./data:/data` and `./docs/generated:/docs/generated:ro`; `docker-compose.prod.yml` mounts only `./data:/data:ro`, so v2 routes return 404 and `/api/health` reports version `0.0.0` (no `/VERSION`) in the Docker production profile.

---

## 2. Actual implementation path (source → user)

```
[Last Epoch game install, Windows host  D:\LastEpochTools\game_files\current\1.4.6_22986002]
   │  ACQUISITION — last-epoch-data/scripts/*.ps1, tools/ (705 files)        MANUAL, Windows-only
   ▼
[RAW PRESERVATION]  last-epoch-data/patch_versions/{1.3.7.1_22373561,1.4.3_22682302}/
                    (GameAssembly.dll + global-metadata.dat committed; 220 MB)
                    GAP: no 1.4.6 snapshot although exports are 1.4.6
                    extracted_raw/ (18 tracked files, 34 MB), il2cpp_dump/ (99 MB)
   │  PARSING / EXTRACTION — last-epoch-data pipeline (EXTRACTION_PIPELINE_PLAN.md §5)
   ▼
[EXPORTS]  last-epoch-data/exports_json/*.json  (metadata.json: 1.4.6 build 22986002, 2026-05-06)
   │  VALIDATION + GOVERNANCE — last-epoch-data/docs/generated/ (205 reports),
   │  .github/workflows/regeneration-gate.yml; data_bundle/manifest.json
   │  (affixes family = BLOCK; skills/passives/uniques/... = DEGRADE)
   │  README: trusted_public_visibility_ready=false, runtime_consumption_ready=false
   │
   ├──(A) LEGACY PRODUCTION PATH ─────────────────────────────────────────────────────────
   │   MANUAL: copy/clone last-epoch-data INTO le-the-forge/, run
   │   scripts/sync_game_data.py  → NORMALIZATION (slot map etc.) → data/**/*.json
   │   scripts/generate_tree_data.py → frontend/src/data/{passiveTrees,skillTrees}/index.ts
   │   then MANUAL git commit.  No trust classification is carried across.
   │   Last run: data/version.json synced_at 2026-04-26, patch_version "unknown",
   │   files_updated ["data\\items\\affixes.json"]  (pre-1.4.6; upstream refreshed 1.4.6 on 2026-05-05)
   │      ▼
   │   VALIDATION: `flask validate-data` (structure/type/min-count only; backend/app/utils/cli.py:368)
   │      ▼
   │   PERSISTENCE: committed JSON in git; PostgreSQL holds users/builds/votes/craft sessions plus
   │   seeded copies (affix_defs, passive_nodes, item_types) via `flask seed` / `seed-passives`
   │   (NOT run by render.yaml — only `flask db upgrade`, render.yaml:44)
   │      ▼
   │   SERVICE LAYER: create_app() → GameDataPipeline.load_all() (app/__init__.py:136-142)
   │   → AffixRegistry/SkillRegistry/EnemyRegistry → engines/services → /api/* blueprints
   │      ▼
   │   FRONTEND: React SPA (frontend/src/lib/api.ts) → planner, crafting, simulation
   │
   └──(B) V2 "TRUSTED DATA" PATH (display/debug only) ─────────────────────────────────────
       MANUAL: run backend/scripts/report_v2_*_bundle.py on the D:\Forge workstation
       (defaults hard-code D:\Forge\last-epoch-data\exports_json\... and
        ...\docs\generated\forge_safe_affix_bundle.json) → NORMALIZATION (app/normalization/v2)
       → docs/generated/v2_*.json (generated_on 2026-05-12, 1.4.6 provenance) → MANUAL commit
          ▼
       REPOSITORIES: app/repositories/v2/* (read-only, lazy file load per request path)
          ▼
       API: /experimental/v2/* and /api/experimental/v2/* — 41 GET rules × 2 prefixes,
            NO config gate (routes/experimental.py:197-1035; only forge-safe-affix routes are gated)
          ▼
       FRONTEND: /debug/v2*, /trusted-data* pages — exposed in production builds by
                 commit 9f38e8e "fix: expose v2 debug routes" (frontend/src/App.tsx:264-276)
       Planner math does NOT consume v2 (verified: only routes/experimental.py imports
       repositories.v2; no route/service imports planner_adapters).
```

Gaps and manual steps on the path: (1) acquisition is manual and Windows-only; (2) no 1.4.6 raw snapshot; (3) cross-repo hand-off is manual copy + commit with three conflicting path conventions; (4) the legacy path drops all upstream trust/quarantine metadata; (5) `data/version.json` patch is `"unknown"`; (6) no automated patch sync (ROADMAP "Patch auto-sync pipeline" is a future item); (7) DB seeding is not part of Render deploy; (8) production has two different patch vintages served side by side (pre-1.4.6 legacy data drives math; 1.4.6 v2 bundles drive trust/debug pages).

---

## 3. Applications and services

| Component | Path | Entry | Status | Notes |
| --- | --- | --- | --- | --- |
| Flask API | `backend/` | `wsgi.py` → `create_app(FLASK_ENV)` | active | Render `epochforge-api`, gunicorn 4 workers × 2 threads, `--preload` (`render.yaml:45`) |
| React SPA | `frontend/` | `src/main.tsx`, `src/App.tsx` | active | Render static site `epochforge-frontend`, SPA rewrite |
| PostgreSQL 15 | Render `epochforge-db` | `DATABASE_URL` | active | 11 tables (`app/models/__init__.py`), 15 Alembic revisions (`backend/migrations/versions`) |
| Redis | Render `epochforge-redis` (allkeys-lru) | `REDIS_URL` | active | rate-limit storage, response cache, job status (section 6) |
| Electron desktop | `electron/main.js`, root `package.json` | `npm run build:desktop` | abandoned | Production mode spawns `backend/forge-backend` PyInstaller bundle or `python -m flask` with `FLASK_ENV=production` (`electron/main.js:60-65`); no PyInstaller spec exists; `electron-builder` `files` excludes `backend/`; production config validation would refuse to start without Discord secrets/Postgres. ROADMAP lists it as future work |
| Discord OAuth | `routes/auth.py` | `/api/auth/discord*` | active | |
| Discord import-failure webhook | `services/discord_notifier.py:60` | fire-and-forget `threading.Thread` | active | `DISCORD_IMPORT_WEBHOOK_URL` |
| last-epoch-data pipeline | `/home/user/last-epoch-data` | PowerShell + Python, Windows host | active (offline) | not a runtime dependency |
| le-parser | `/home/user/le-parser`, gitlink in repo | — | abandoned | dangling gitlink without `.gitmodules` |

## 4. Backend package inventory (runtime reachability)

Static transitive import analysis from `wsgi`/`app` (AST, includes function-level imports; script in scratch, command reproduced in section 10):

| Top-level package | Modules | Reachable from runtime | Status |
| --- | ---: | ---: | --- |
| `app` | 256 | 177 | active (79 unreachable modules are mostly `app/game_data/*` diagnostics used by `backend/scripts/`) |
| `bis` | 29 | 16 | active (partial) |
| `builds` | 8 | 6 | active |
| `conditions`, `damage`, `encounter`, `events`, `metrics`, `modifiers`, `optimization`, `rotation`, `skills`, `state`, `targets`, `services`, `debug` | 2–12 each | partial/all | active |
| `data` (backend/data: loaders, mappers, repositories, versioning) | 22 | 18 | active |
| `crafting` | 23 | 3 | mostly legacy |
| `buffs`, `build`, `combat`, `integration`, `movement`, `projectiles`, `simulation`, `spatial`, `stats`, `status`, `visualization` | 129 total | **0** | legacy — tested (e.g. `spatial` imported by 27 test files) but unreachable from production |

## 5. Interfaces

### 5.1 HTTP API (actual URL map)
Dumped via `create_app('testing').url_map`: **172 rules**; 84 unique non-experimental paths; **83 experimental rules** (`/experimental/*` and `/api/experimental/*` register the same blueprint twice, `app/__init__.py:258-259`); 1 `/debug/forge-safe-affixes` (gated by `FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED`). 29 blueprints registered (`app/__init__.py:202-259`).

Unauthenticated state-changing endpoints relevant to data integrity:
- `PATCH /api/admin/affixes/<affix_id>` — only `@limiter.limit("30 per minute")` (`routes/admin.py:68-70`); rewrites `data/items/affixes.json` on the server filesystem (`admin.py:36-38,93`). Reachable from the production SPA route `/affixes` (`frontend/src/App.tsx:232`, `AffixEditorPage.tsx:363`). `GET /api/admin/affixes` is likewise open.
- `POST /api/load/game-data` — only rate-limited (`routes/load.py:21-23`); reloads the per-worker pipeline. Reachable from `/data-manager` (`App.tsx:244`).

### 5.2 Flask CLI (`backend/app/utils/cli.py`)
`seed` (:73), `reseed-affixes` (:99), `seed-builds` (:125), `seed-passives` (:183), `create-admin <username>` (:268), `reset-demo-votes --threshold` (:284), `remove-seeded-builds` (:326), `refresh-meta` (:356), `validate-data` (:368); plus Flask-Migrate `flask db *`.

### 5.3 Scripts
- `scripts/` (10): `sync_game_data.py`, `generate_tree_data.py`, `build_sprite_map.py`, `extract_images.py`, `diagnose_icons.py`, `verify_passive_coverage.py`, `check_forge_workspace.ps1`, `smoke_data_bundle_handoff.ps1`, `launch-electron.sh`, `screenshot.sh`.
- `backend/scripts/` (62 `.py`): 9 `report_v2_*_bundle`/registry generators that write committed `docs/generated/v2_*.json`; ~45 diagnostic/report generators; `validate_v2_trusted_data.py`, `validate_simulation.py`, `verify_base_stats.py`, `check_data_bundle.py`, `generate_item_constants.py`, `generate_subtype_map.py`, `merge_passive_edges.py`.

## 6. Workers, queues, caches, schedules

| Mechanism | Where | What it does | Durability |
| --- | --- | --- | --- |
| In-process thread pool | `app/utils/jobs.py:25` (`ThreadPoolExecutor(max_workers=4)`) per gunicorn worker | async simulations from `routes/simulate.py:144,323`; status in Redis `forge:job:<id>` TTL 3600 | jobs lost on worker restart/deploy; if Redis is down the job runs but status is unpollable (`jobs.py:65-66,118-122`) |
| Process pool | `app/engines/combat_engine.py:537` | parallel Monte Carlo | in-request |
| Fire-and-forget thread | `services/discord_notifier.py:60` | webhook POST | none |
| Redis response cache | `app/utils/cache.py`; `cached_route` used in `routes/ref.py`, `routes/entities.py`; manual keys in builds/optimize/analysis/compare/meta/report/views | `ref:*` 86400 s, `forge:*` 30 s–21600 s | Keys are **not versioned by data version**; no invalidation of `ref:*` on deploy, admin PATCH, or `/api/load/game-data` (only `forge:builds:*`/`forge:optimize:*` are ever deleted, `routes/builds.py:56-62`, `routes/skills.py:365`) |
| Rate limiting | Flask-Limiter, Redis storage, falls back to in-memory per worker if Redis ping fails (`app/__init__.py:31-45`) | | |
| Celery / RQ / APScheduler | — | none (grep: 0 hits) | |
| Cron / scheduled jobs | — | none: no Render cron service, no `schedule:` trigger in any workflow; `flask refresh-meta` is manual | |

## 7. CI/CD and deployment

| Item | File | Behaviour |
| --- | --- | --- |
| CI | `.github/workflows/ci.yml` | on push to `dev`, PRs to `dev`/`main`: backend `pytest tests/ -x -q`, frontend `tsc --noEmit`, `flask validate-data`. **No vitest run, no eslint, no build, no coverage, no push-to-main run** |
| Deploy | `.github/workflows/deploy.yml` | every push to `main` POSTs one `RENDER_DEPLOY_HOOK_URL` (one service; which one is UNKNOWN; `docs/deployment.md:122-129` says `epochforge-api`). Not gated on CI. `render.yaml` has `autoDeploy: false` for both services, so frontend deploy is manual/UNKNOWN |
| Sync | `.github/workflows/sync-main-to-dev.yml` | opens a main→dev merge PR as `github-actions[bot]` |
| Render | `render.yaml` | `preDeployCommand: flask db upgrade`; no seed; `healthCheckPath: /api/health` |
| Heroku-style | `backend/Procfile` | `web: gunicorn wsgi:app`, `release: flask db upgrade` (legacy, unused by Render blueprint) |
| Docker | `backend/Dockerfile`, `backend/entrypoint.sh`, `frontend/Dockerfile`+`nginx.conf`, `docker-compose.yml`, `docker-compose.prod.yml` | entrypoint runs `db upgrade`, `seed`, `seed-passives` (errors swallowed: `entrypoint.sh:13-14`) |
| Extractor CI | `last-epoch-data/.github/workflows/regeneration-gate.yml` | report determinism gate only |

## 8. Environment-variable contract (names only)

Read by code (`git grep` of `os.environ.get`/`getenv`/`import.meta.env`/`process.env`, excluding tests): `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES`, `DATABASE_URL`, `REDIS_URL`, `DATA_VERSION`, `CURRENT_PATCH`, `CURRENT_SEASON`, `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`, `DISCORD_IMPORT_WEBHOOK_URL`, `FRONTEND_URL`, `FLASK_ENV`, `FORGE_SAFE_AFFIX_CATALOG_ENABLED`, `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED`, `FORGE_SAFE_AFFIX_CONSUMPTION_MODE`, `FORGE_SAFE_AFFIX_EXPORT_PATH`, `FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED`, `FORGE_SAFE_AFFIX_BUNDLE_ENABLED`, `FORGE_SAFE_AFFIX_BUNDLE_PATH`, `FORGE_DATA_BUNDLE_DIR` (diagnostics), `RATE_LIMIT_SIMULATE_STATS`, `RATE_LIMIT_SIMULATE_BUILD`, `RATE_LIMIT_SIMULATE_ENCOUNTER`; frontend `VITE_API_BASE_URL`, `VITE_API_URL` (legacy), `VITE_FORGE_SAFE_AFFIX_CATALOG_ENABLED`, `NODE_ENV`, `DEV`; electron `BACKEND_PORT`-style locals (UNKNOWN names beyond `FLASK_*`).
Set in `render.yaml`: `FLASK_ENV`, `FLASK_APP`, `PYTHON_VERSION`, `PYTHONUNBUFFERED`, `FRONTEND_URL`, `DATABASE_URL`, `REDIS_URL`, secrets (`sync:false`) `SECRET_KEY`, `JWT_SECRET_KEY`, `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_REDIRECT_URI`, `DISCORD_IMPORT_WEBHOOK_URL`; frontend `NODE_VERSION`, `VITE_API_BASE_URL`. **Not set:** `CURRENT_PATCH`/`CURRENT_SEASON`/`DATA_VERSION` (defaults `1.4.3`/`4`/`1.0.0`, `config.py:25-30`), all `FORGE_SAFE_*` (default off), `FORGE_DATA_BUNDLE_DIR`.
Documented but unused: `DATA_BUNDLE_DIR` (`.env.example`), `DB_PASSWORD` (compose only).
Config smell: `FORGE_SAFE_AFFIX_CATALOG_ENABLED` and `FORGE_SAFE_AFFIX_EXPORT_PATH` are defined twice in `Config` with different parsing (`config.py:41,58-61` and `:43,62`); the later definition wins.

## 9. Tests (measured on snapshot of `1efcef7`)

| Suite | Count | Command |
| --- | --- | --- |
| Backend test files | 337 `tests/**/test_*.py` | `find backend/tests -name 'test_*.py' \| wc -l` |
| Backend collected | **11,800** | `python -m pytest tests/ --collect-only -q` |
| Backend run result | 11,415 passed, 379 skipped, 7 errors (6 × `ModuleNotFoundError: psycopg`, 1 SQLite teardown) | `python -m pytest tests/ -q -p no:cacheprovider` |
| Frontend test files | 49 `*.test.ts(x)` | `find frontend/src -name '*.test.ts*'` |
| Frontend run result | 899 passed, 17 failed (`navigation.test.tsx`, `integration/layout.test.tsx`) — not run in CI | `npx vitest run` |
| Coverage tooling | none (`pytest-cov` absent from `requirements.txt`; no `--cov`/coverage config anywhere) | |

## 10. Component status table (documents and generated artifacts)

| Artifact | Path | Producer | Consumer | Status |
| --- | --- | --- | --- | --- |
| Runtime game data | `data/**` (52 files) | `scripts/sync_game_data.py` (manual) + hand edits/PR merges (e.g. passive edges PRs #235-237) | pipeline, routes | active, stale (last affix sync 2026-04-25, uniques 2026-03-31) |
| Skills/classes | `backend/app/game_data/skills.json` (179 skills), `classes.json` | hand-maintained | pipeline | active |
| v2 bundles | `docs/generated/v2_*.json` (13) | `backend/scripts/report_v2_*` (D:\ defaults) | experimental routes, debug/trust pages | active (display-only), 1.4.6 |
| Governance reports (Forge) | `docs/generated/*` (80 tracked files) | `backend/scripts/report_*` | humans, some tests | active docs |
| Governance reports (extractor) | `last-epoch-data/docs/generated/` (205) | extractor scripts | humans, regeneration gate | active, not consumed by Forge runtime |
| Data bundle | `last-epoch-data/data_bundle/` | extractor | `bundle_compat` diagnostics only | dev-only |
| Frontend tree data | `frontend/src/data/**` | `scripts/generate_tree_data.py` | SPA bundle | active, last regenerated 2026-03-31 |
| Root docs | README, ARCHITECTURE, ROADMAP, CHANGELOG, KNOWN_LIMITATIONS | manual | users | stale (2026-04-22; see 19) |

## 11. Findings (system map)

| ID | Sev | Title |
| --- | --- | --- |
| SYS-1 | P0 | Unauthenticated `PATCH /api/admin/affixes/<id>` rewrites production `data/items/affixes.json`; `/affixes` editor page routed in production |
| SYS-2 | P1 | Unauthenticated `POST /api/load/game-data` reloads production pipeline per worker |
| SYS-3 | P1 | Production math runs on pre-1.4.6 legacy data with patch `"unknown"` while v2 trust pages show 1.4.6 bundles — two patch vintages served at once |
| SYS-4 | P1 | Legacy production data path strips upstream quarantine/trust status; extractor marks affix domain `remain_quarantined`, `runtime_consumption_ready=false` |
| SYS-5 | P1 | v2 experimental API (41 routes × 2 prefixes) is ungated in production and frontend debug/trust pages were deliberately exposed (`9f38e8e`) despite extractor `trusted_public_visibility_ready=false` |
| SYS-6 | P1 | Cross-repo hand-off is manual with three conflicting path conventions and hard-coded `D:\Forge` defaults in 13 tracked code files |
| SYS-7 | P2 | `main` (production) is 413 commits behind `dev`; audit baseline differs from active development |
| SYS-8 | P2 | Deploy workflow is not gated on CI; CI does not run on push to `main`, does not run vitest/eslint/build |
| SYS-9 | P2 | Redis `ref:*` cache (24 h) not keyed by data version and never invalidated on data change/deploy |
| SYS-10 | P2 | Background jobs are in-process threads with Redis-only status; lost on restart, no queue |
| SYS-11 | P2 | Render deploy does not seed DB; DB-backed reference tables state in production UNKNOWN |
| SYS-12 | P2 | No raw-preservation snapshot for exported patch 1.4.6; proprietary game binaries committed for 1.3.7.1/1.4.3 |
| SYS-13 | P3 | 11 backend top-level packages (129 modules) unreachable from production runtime but kept and tested |
| SYS-14 | P3 | Electron desktop packaging non-functional (no PyInstaller spec; backend excluded from bundle) |
| SYS-15 | P3 | Dangling `le-parser.worktrees` gitlink without `.gitmodules` |
| SYS-16 | P3 | Docker production profile lacks `docs/generated` and `VERSION` (v2 routes 404, version `0.0.0`) |
| SYS-17 | P3 | Duplicate `FORGE_SAFE_*` config definitions with divergent parsing; `.env.example` documents unused `DATA_BUNDLE_DIR` |
| SYS-18 | P1 | Unpinned transitive SQLAlchemy: a clean `pip install -r backend/requirements.txt` today resolves SQLAlchemy 2.1.3, which maps `postgresql://` to psycopg v3 (absent); Render's `buildCommand` reinstalls on every deploy, so `flask db upgrade` / first DB use would fail (verified in scratch venv: `make_url('postgresql://…').get_dialect().driver == 'psycopg'`; 6 test errors). `numpy>=1.26.0`, `pyyaml>=6.0` also unpinned |

Full JSON records are in the audit hand-off; evidence lines are cited inline above.

### Commands used
```
git -C /home/user/le-the-forge ls-files | wc -l; git log --oneline | head; git ls-remote --heads origin
gh api repos/NickolisK24/le-the-forge/compare/main...dev
git grep -l 'D:\\Forge' -- ':!docs'
grep -rn "FORGE_DATA_BUNDLE_DIR\|docs/generated\|last-epoch-data" backend/app
python -c "from app import create_app; app=create_app('testing'); print(app.url_map)"   (scratch venv, snapshot)
python - <<AST import-reachability walk from wsgi/app>>
python -m pytest tests/ --collect-only -q
grep -n "@app.cli.command" backend/app/utils/cli.py
python3 -c "<record counts of docs/generated/v2_*.json and data/*.json>"
cat last-epoch-data/exports_json/metadata.json data_bundle/manifest.json
```
