# 02 — Runtime and Build Health

Audit date: 2026-10-06
Scope: `le-the-forge` `main` HEAD `1efcef7` (2026-05-14); `dev` tip `558557c` (exported read-only for comparison); `last-epoch-data` HEAD `73e2ab0` (2026-05-31).
Mode: read-only. No repo file, branch, lockfile, or deployment was changed. Installs went to scratch virtualenvs and to gitignored `frontend/node_modules` (created by `npm ci`; also `frontend/dist/` from `npm run build`, gitignored). `git fetch origin dev` updated only `FETCH_HEAD`.

## 1. Purpose

Determine whether the project builds, tests, and would boot today on its declared runtimes, after ~5 months without commits, and whether the code currently on `main` (and deployed) was ever validated by CI.

## 2. Runtime inventory

| Item | Declared by project | Evidence | Available in audit container | Status on 2026-10-06 |
|---|---|---|---|---|
| Python | 3.11 | `render.yaml:52-53`, `backend/Dockerfile:7,18`, `.github/workflows/ci.yml` (setup-python 3.11) | 3.11.17 (used), 3.12, 3.13.16 default | Supported (EOL 2027-10) |
| mypy target | 3.12 | `backend/mypy.ini:2` | — | Mismatch with 3.11 runtime |
| Node | 20 | `ci.yml` (setup-node 20), `render.yaml:93-94`, `frontend/Dockerfile:15,26` | 20.20.0 (`/opt/node20`, used), 22.22.0 default | **Node 20 EOL 2026-04-30** |
| npm | lockfileVersion 3 | `frontend/package-lock.json`, `package-lock.json` | 10.8.2 (with Node 20) | OK |
| Postgres | 15 | `render.yaml:21`, `docker-compose*.yml` | client only | Supported |
| Redis | 7 / Render managed | `docker-compose*.yml` | redis-server present | Supported |
| Electron | `^39.8.3` (root) **and** `^41.0.3` (frontend devDeps) | `package.json`, `frontend/package.json` | — | Both unsupported (latest 44.5.1); two conflicting declarations |
| GitHub Actions | checkout@v4, setup-python@v5, setup-node@v4 | `ci.yml` | — | Runner annotation: Node 20 actions deprecated, removed from runners 2026-09-16 |
| No version pin files | — | no `.nvmrc`, `.python-version`, `runtime.txt`, `engines` field | — | Version only implied by CI/Render config |

`npm ci` under Node 20 emitted `EBADENGINE` for `@electron/rebuild@4.0.3` and `node-abi@4.28.0` (require Node ≥22.12.0) — the declared Node 20 is already below what the locked toolchain needs.

## 3. Method (commands verbatim)

`$S=<scratch>`

```
# Backend (mirrors ci.yml, but full run without -x)
python3.11 -m venv $S/venv-backend
$S/venv-backend/bin/pip install -r backend/requirements.txt
cd backend && FLASK_ENV=testing SECRET_KEY=ci-test-secret-key-minimum-length JWT_SECRET_KEY=ci-test-secret-key-minimum-length \
  $S/venv-backend/bin/python -m pytest tests/ -q -p no:cacheprovider -rfE --durations=15
FLASK_ENV=testing SECRET_KEY=… JWT_SECRET_KEY=… $S/venv-backend/bin/flask validate-data
# Control run with SQLAlchemy held to 2.0.x
python3.11 -m venv $S/venv-backend-sa20 && $S/venv-backend-sa20/bin/pip install -r backend/requirements.txt 'sqlalchemy<2.1'
… same pytest command with venv-backend-sa20
# mypy (not in CI; installed separately)
$S/venv-mypy/bin/mypy --config-file mypy.ini --python-executable $S/venv-backend/bin/python --cache-dir $S/mypy-cache app

# Frontend (Node 20.20.0)
export PATH=/opt/node20/bin:$PATH; cd frontend
npm ci
npx tsc --noEmit
npx vitest run
npm run build
npm run lint

# dev branch comparison (no checkout; archive into scratch)
git fetch origin dev        # FETCH_HEAD only
git archive 558557c | tar -x -C $S/dev-copy
cd $S/dev-copy/backend && … pytest (venv-backend-sa20)

# last-epoch-data
python3.11 -m venv $S/venv-led && $S/venv-led/bin/pip install -r /home/user/last-epoch-data/requirements.txt
git clone --no-hardlinks /home/user/last-epoch-data $S/led-clone      # tests read committed HEAD via git
cd $S/led-clone && $S/venv-led/bin/python -m pytest tools/scripts -q -p no:cacheprovider -rfE

# CI history
git ls-remote origin
gh api repos/NickolisK24/le-the-forge/commits/<sha>/check-runs
gh api 'repos/NickolisK24/le-the-forge/actions/runs?branch=dev&per_page=100'
gh api 'repos/NickolisK24/le-the-forge/actions/runs?branch=main&per_page=5'
gh api repos/NickolisK24/le-the-forge/check-runs/<id>/annotations
gh api 'repos/NickolisK24/last-epoch-data/actions/runs?branch=main&per_page=100'
```

## 4. Results

### 4.1 Results table

| Check | In CI? | Result | Counts |
|---|---|---|---|
| Backend `pip install -r requirements.txt` | yes | success, but resolves **SQLAlchemy 2.1.3** | 49 packages installed |
| Backend pytest (fresh resolve, SA 2.1.3) | yes (`-x`) | **exit 1** | 11,415 passed / 379 skipped / **7 errors** / 0 failed (429.6 s) |
| Backend pytest (control, SA 2.0.54) | — | exit 1 | 11,420 passed / 379 skipped / 1 failed / 1 error (351.3 s) |
| `flask validate-data` | yes | pass | "52 files checked" |
| mypy (`mypy.ini`) | **no** | exit 1 | 169 errors in 42 files (256 checked) |
| `npm ci` (frontend, Node 20) | `npm install` in CI | success | 2 EBADENGINE warnings, 10 deprecation warnings, 55 audit advisories |
| `npx tsc --noEmit` | yes | **pass** | 0 errors (25 s) |
| `npx vitest run` | **no** | **exit 1** | 49 files (2 failed); 916 tests: 899 passed / **17 failed** |
| `npm run build` | no (Render runs it) | pass | main chunk `index-*.js` 2,459 kB (613 kB gzip) — over 500 kB warning |
| `npm run lint` | **no** | **exit 1** | 263 problems: **8 errors**, 255 warnings |
| last-epoch-data pytest (`tools/scripts`, git clone) | partially (1 file) | **exit 1** | 2,319 tests: 2,296 passed / **23 failed** (294.7 s) |
| last-epoch-data `regeneration_gate.py --strict` | yes | **exit 1** | 185 artifacts: 76 match / **88 drift** / 6 non_deterministic_timestamp / 15 skipped_no_generator |
| dev tip `558557c` backend pytest (SA 2.0, archive copy) | yes (failing) | **exit 1** | 14,456 collected: 14,059 passed / 379 skipped / **17 failed** / 1 error (1,084 s); 5 of the 17 are artifacts of running outside a git checkout |

Backend test collection: 330 `test_*.py` in `backend/tests` + 7 in `backend/tests/builds`; 11,801 tests collected. Six further files are excluded by `backend/pytest.ini` `--ignore` (test_affix_engine, test_base_engine, test_craft_engine, test_craft, test_combat_engine, test_calculation_snapshots) as stale.

### 4.2 Backend failures (exact)

Fresh resolve (SA 2.1.3), short summary:
```
ERROR tests/test_deployment_readiness.py::test_production_cors_allows_bare_domain
ERROR tests/test_deployment_readiness.py::test_production_cors_allows_www_subdomain
ERROR tests/test_deployment_readiness.py::test_production_cors_blocks_unknown_origin
ERROR tests/test_deployment_readiness.py::test_development_cors_allows_localhost_vite
ERROR tests/test_deployment_readiness.py::test_development_cors_allows_localhost_cra
ERROR tests/test_deployment_readiness.py::test_development_cors_allows_loopback_ip
ERROR tests/test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes   (teardown)
```
- 6 × setup error: `create_app(...)` → `db.init_app` → `sqlalchemy.create_engine("postgresql://…")` → `ModuleNotFoundError: No module named 'psycopg'` (fixture `tests/test_deployment_readiness.py:86`).
- 1 × teardown error: `sqlite3.ProgrammingError: Cannot operate on a closed database.` Reproduces with SA 2.0 too, does **not** reproduce when the file runs alone (19 passed) → order-dependent leaked SQLite connection finalised during this test.

Control (SA 2.0.54):
```
FAILED tests/test_crafting_performance.py::TestPerformance::test_fracture_engine_zero_chance_fast   assert 3.2033… < 2.0
ERROR  tests/test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes      (teardown, same as above)
```
The timing failure occurred while 3 other suites ran concurrently on 4 vCPUs; it passed in the first (uncontended) run → wall-clock flake.

### 4.3 Frontend failures (exact)

Vitest — 17 failures in 2 files, all stale-UI assertions, not crashes:
- `src/__tests__/components/navigation.test.tsx`: `Sidebar > renders all 7 nav items when expanded` (no "Data Manager" item; `src/components/navigation/Sidebar.tsx:178` notes it is now URL-only); 10 × `GlobalSearch > …` (tests look for placeholder `Search items, skills, affixes, builds…`, component uses `Search skills, affixes, builds…` at `src/components/search/GlobalSearch.tsx:314`; item results such as "Ravenous Void"/"Rive"/"Items" no longer rendered).
- `src/__tests__/integration/layout.test.tsx`: 6 × `AppLayout > GlobalSearch …` (same placeholder).

ESLint — 8 errors:
- `src/__tests__/integration/workspace-routes.test.tsx:60` `@typescript-eslint/no-var-requires`
- 7 × `Definition for rule 'react-hooks/exhaustive-deps' was not found` in `src/pages/debug/{ForgeSafeAffixesDebugPage:101, V2ClassMasteryDebugPage:74, V2IdolsDebugPage:74, V2ItemsDebugPage:80, V2PassivesDebugPage:74, V2SkillsDebugPage:74, V2UniqueSetDebugPage:81}.tsx` — disable comments reference a plugin that `.eslintrc.cjs` does not load.

### 4.4 mypy

169 errors / 42 files. By code: union-attr 61, arg-type 43, index 16, return-value 11, misc 11, assignment 9, var-annotated 4, name-defined 3, call-overload 3, typeddict-item 2. The 3 `name-defined` were checked: `app/services/simulation_service.py:270` (`kwargs` guarded by `"kwargs" in dir()` — dead code, always `[]`), `app/game_data/game_data_loader.py:179,185` (string annotations; harmless). mypy is not run in CI and is not in requirements; `mypy.ini` targets 3.12.

### 4.5 CI coverage and validation of deployed code

- `ci.yml` triggers: push to `dev`, PRs to `dev`/`main`. `deploy.yml` and `sync-main-to-dev.yml` trigger on push to `main`. `git ls-remote origin`: `refs/heads/dev` = `558557c`, `refs/heads/main` = `1efcef7`. `dev` is **413 commits ahead** of `main`, 0 behind.
- `main` HEAD `1efcef7` (merge of PR #372): **no check runs for CI** on the merge commit itself (only "Trigger Render Deploy" success and "Open main → dev sync PR" failure). The PR head `9f38e8e` was CI-validated: Data Validation success 00:09:10Z, Frontend Type-Check success 00:09:30Z, Backend Tests success 00:13:45Z (2026-05-15).
- **Deploy did not wait for CI:** "Deploy to Render" run for `1efcef7` was created 2026-05-15T00:08:56Z, i.e. before Backend Tests on the PR head finished (00:13:45Z). `deploy.yml` has no `needs:`/status dependency on CI.
- `dev`: the last 100 CI runs on `dev` are all `failure` (latest 2026-05-29T20:00:31Z on `558557c`; its failing job is Backend Tests, Type-Check and Data Validation passed). Last successful `dev` CI: 2026-05-09 (`fbda64c`). Job logs have expired (HTTP 410); annotation only says "Process completed with exit code 1".
- "Sync main back to dev" has failed on every `main` push sampled (`1efcef7`, `d49e8fa`, `a7d50cd`).
- CI checks only `tsc` for the frontend — vitest, lint and `vite build` are never run in CI, which is how 17 stale vitest failures and 8 lint errors accumulated.
- CI runs pytest with `-x`, so a single order-dependent teardown error (4.2) stops the whole run.
- last-epoch-data "Regeneration Gate": main runs in last 100 = 70 failure / 23 success; last success 2026-05-29 (`2e39538`); HEAD `73e2ab0` failed.

## 5. Findings

| ID | Sev | Title | Evidence |
|---|---|---|---|
| RT-1 | P0 | Fresh backend install resolves SQLAlchemy 2.1.x; `postgresql://` now needs `psycopg` (v3) which is not installed → app factory cannot create engine → any rebuild/redeploy of the API (Render build, Docker) fails to boot and `flask db upgrade` fails | `backend/requirements.txt` (no sqlalchemy pin); SA 2.1.0 released 2026-09-24; `sqlalchemy/dialects/postgresql/__init__.py:99`; 6 errors in `tests/test_deployment_readiness.py`; `create_engine('postgresql://…')` → ModuleNotFoundError; control run with `sqlalchemy<2.1` clears them; `render.yaml:42-44`, `wsgi.py:4` |
| RT-2 | P1 | `main` (deployed) is 413 commits behind `dev`, and `dev` CI has failed on every run since 2026-05-09; locally `dev` has 12 genuine failures incl. 9 experimental-vs-production boundary guards → integration branch is unreleasable as-is | §4.5, §4.7 |
| RT-3 | P1 | Deploy workflow fires on push to `main` without waiting for CI; merge commit `1efcef7` was never CI-checked | `.github/workflows/deploy.yml`; run timestamps §4.5 |
| RT-4 | P1 | Node 20 (declared for CI, Render frontend build, Docker) is EOL since 2026-04-30; locked toolchain already requires Node ≥22.12 (`EBADENGINE`) | `ci.yml`, `render.yaml:93-94`, `frontend/Dockerfile:15,26`, `$S/npm-ci-frontend.log` |
| RT-5 | P2 | GitHub Actions pinned to Node-20-based action majors; runners removed Node 20 on 2026-09-16 — CI behaviour from now is UNKNOWN until a run occurs | check-run annotation on `558557c` |
| RT-6 | P2 | Frontend test suite red: 17/916 vitest failures (stale UI expectations); not run in CI | §4.3 |
| RT-7 | P2 | Order-dependent SQLite teardown error in backend suite; with CI's `-x` it can abort CI non-deterministically | §4.2 |
| RT-8 | P2 | No reproducible Python lock: transitive deps unpinned; Render frontend uses `npm install` not `npm ci` | `backend/requirements.txt`, `render.yaml:89` |
| RT-9 | P2 | last-epoch-data CI (Regeneration Gate) failing on `main` HEAD; local suite 23/2,319 failing, strict gate 88 drifted artifacts | §4.5, §4.6 |
| RT-10 | P3 | ESLint red (8 errors), not in CI; missing `eslint-plugin-react-hooks` while code references its rule | §4.3 |
| RT-11 | P3 | mypy red (169 errors), not in CI, targets wrong Python version | §4.4 |
| RT-12 | P3 | Wall-clock performance assertion flakes under load | `tests/test_crafting_performance.py` (`assert elapsed < 2.0`) |
| RT-13 | P3 | 2.46 MB single JS chunk; build warns | `npm run build` output |
| RT-14 | P3 | Two different Electron majors declared (root ^39, frontend ^41); packaged desktop app does not bundle backend and starts it in production mode | `package.json`, `frontend/package.json`, `electron/main.js:65` |
| RT-15 | P3 | 6 backend test files permanently `--ignore`d as stale since the Phase F refactor | `backend/pytest.ini` |

### 4.6 last-epoch-data detail

- First attempt ran on a `git archive` copy and produced 69 failures, many `FileNotFoundError: … is not present in committed HEAD` — those tests read committed files via git, so the run was repeated in a local `git clone` (authoritative numbers above).
- All 23 remaining failures are the same two checks: `test_real_committed_report_matches_generator_if_present` (16) and `test_real_generated_report_matches_builder_if_present` (7) — i.e. committed generated reports no longer match what their generators produce (17 `test_relationship_*` files, plus affixes/items/passive_nodes/skills remediation, items certification re-evaluation, extraction coverage gap, domain gap closure).
- `python tools/scripts/regeneration_gate.py --strict` (same command as `.github/workflows/regeneration-gate.yml`) → `GATE FAILED: 94 artifact(s) drifted or errored` (88 drift + 6 non-deterministic timestamp). This matches the failing CI on `main` HEAD `73e2ab0`.
- Extraction itself (UnityPy/Il2CppDumper/AssetRipper, Windows-only) was not run; `pip install -r requirements.txt` succeeded on Linux (UnityPy 1.25.0, pythonnet 3.0.5 install, .NET runtime not tested).

### 4.7 dev tip detail (`558557c`, not deployed)

Genuine failures (12):
- 9 × `test_v2_*_bundle_is_not_referenced_by_production_modules` / `test_v2_repository_registry_…` / `test_v2_modifier_registries_…` — production-module boundary guards now see `backend/app/game_data/trusted_gameplay_data_coverage_audit.py` and `backend/app/planner_adapters/v3_1/trusted_shadow_consumption.py` referencing v2 bundles. This is the experimental-vs-production separation guard firing.
- `test_deployment_readiness.py::test_every_referenced_env_var_is_documented` — `V3_1_TRUSTED_PRODUCTION_SHADOW_ALLOWED_DOMAINS`, `V3_1_TRUSTED_PRODUCTION_SHADOW_CONSUMPTION_ENABLED` not documented.
- 2 × `test_report_aggregation_from_generated_phase_reports` (v3.4 closeout / readiness) — expected status `v3_4_closed_…v3_5_planning`, got `blocked_miss…`.
- Environment artifacts (5): `test_macbook_transition_safety_audit.py` — `git ls-files` exit 128 because the archive copy is not a git checkout.
- Same order-dependent weaver teardown error as `main`.
With a fresh (SA 2.1) install, `dev` would additionally hit the RT-1 `psycopg` errors because its `requirements.txt` is identical to `main`'s.

## 6. UNKNOWNs

- Whether production (api.epochforge.gg) is still running the 2026-05-15 build — Render dashboard not accessible; no production traffic sent.
- Whether Render's `PYTHON_VERSION: "3.11"` resolves to a still-available patch release.
- Current behaviour of the CI workflows on GitHub-hosted runners after the 2026-09-16 Node 20 removal (no runs since 2026-06-01).
- Why `dev` CI Backend Tests failed in May (logs expired); local reproduction is in §4.1 row "dev tip".
- Skip reasons for the 379 skipped backend tests were not enumerated (run used `-rfE`); static scan shows 9 `pytest.skip(` and 2 `skipif` sites, mostly "data file removed/consolidated" and "real bundle not available".

## 7. What this does NOT prove

- Tests were run against SQLite in-memory (`TestingConfig`), not Postgres; migrations (`flask db upgrade`) were not executed against a real database.
- A green local suite under Python 3.11.17 / Node 20.20.0 does not prove behaviour on Render's exact images.
- The production frontend bundle was built locally with default env (no `VITE_API_BASE_URL`); it was not served or browser-tested.
- Passing `validate-data` proves structural checks over 52 files only, not game-data correctness.
- No conclusion is drawn here about the Last Epoch Tools HTTP 403 import failure; the importer code path is covered in the security report (host is fixed; the 403 originates upstream).
