# AUDIT-R0 — Emergency Production Breakages: Implementation Report

Date: 2026-10-06
Branch: `fix/audit-r0-emergency-production`
Base: `main` @ `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa`
Status: R0 complete locally, subject to the production verification listed in §10. **AUDIT-R1 has not begun** (§11).

---

## 1. Branch reconciliation decision

See `R0_BRANCH_RECONCILIATION.md`. Summary:
- dev (`558557c`) is 413 commits ahead of main and 0 behind.
- No R0 file differs between main and dev, except two additive lines (a new `/api/trust` blueprint and v3.1 config flags).
- Every R0 finding is `UNCHANGED_ON_DEV`.

**Base: `main`.** dev was rejected: it is red CI, ~995k unreviewed lines, and has no R0 fixes. Reconstructing from selected dev commits was also rejected, because no dev commit touches the R0 code paths.

## 2. Remediation branch

| Item | Value |
|---|---|
| Branch | `fix/audit-r0-emergency-production` |
| Base SHA | `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` (origin/main) |
| main / dev modified | No |
| Pushed / PR | See §12 |

## 3. Findings addressed

| Finding | Result | Commit |
|---|---|---|
| INFRA-1 (SYS-18, DB-2, RT-1) unpinned SQLAlchemy → psycopg3 | FIXED_LOCAL | `58d4448` |
| SYS-1 anonymous affix PATCH writes `data/items/affixes.json` | FIXED_LOCAL | `77e8a83` |
| SYS-2 anonymous `POST /api/load/game-data` | FIXED_LOCAL | `77e8a83` |
| API-4 skill-node IDOR | FIXED_LOCAL | `9016ddd` |
| API-5 anonymous build / craft mutation, deletion by others | FIXED_LOCAL (residual by design, §9) | `9016ddd` |
| API-6 private builds readable by slug | FIXED_LOCAL (residual by design, §9) | `9016ddd` |
| DB-1 delete of viewed build → 500 | FIXED_LOCAL | `c6ed5e4` |
| IMP-1 default UI sends LET URLs to the dead server fetch | FIXED_LOCAL | `e61429b` |
| IMP-2 server-side LET fetch, no diagnostics | FIXED_LOCAL (path retired + diagnostics) | `e61429b`, `79aeb15` |
| FE-4 importer dead ends | OPEN — partially addressed | `e61429b`, `79aeb15` |
| IMP-3 misleading alert (`build_data` forwarded, "Missing Fields: None") | FIXED_LOCAL | `79aeb15` |
| OBS-1 alert lacks stage/version/upstream metadata | OPEN — partially addressed | `79aeb15` |
| API-2 unbounded multi-target simulation | FIXED_LOCAL | `337fbd0` |
| FE-1 API base / render.yaml drift | FIXED_LOCAL (operator verification required) | `b996038` |

`AUDIT_EVIDENCE.json` was updated only for these IDs (`status`, `r0_commits`, `r0_notes`). No finding is marked `VERIFIED`.

## 4. What changed, per item

### R0-01 Deployability (`58d4448`)
Two independent layers:
- `backend/requirements.txt` pins `SQLAlchemy==2.0.54`, the 2.0 line main was built on.
- `config.normalize_database_url()` rewrites `postgresql://` and `postgres://` to `postgresql+psycopg2://`. It is applied in `Config` and again in `create_app`, so a URI patched in later is also normalized.

With only the URL layer and SQLAlchemy 2.1.3 installed, the app still boots on psycopg2. Only the pin test then fails, which is the drift detector working as intended.

### R0-02 Game-data mutation (`77e8a83`)
- New decorator `game_data_mutation_required` in `app/utils/auth.py`. It returns 404 unless `GAME_DATA_MUTATION_ENABLED` is set, then 401 without a JWT, then 403 for non-admins.
- `ProductionConfig.GAME_DATA_MUTATION_ENABLED = False` is a class constant, so environment variables cannot enable it.
- No operational need for remote mutation was found. These routes are local operator tools.
- The existing J14 reload tests now run as an admin with the flag on (`7c83b8a`), with all assertions unchanged.

### R0-03 Ownership / visibility (`9016ddd`)
`app/services/build_access.py` is the single policy, used by every build-by-slug route:
- **Routes covered:** GET, simulate, optimize (POST and GET), skills (GET and node PATCH), report, three analysis routes, compare, view, vote, PATCH and DELETE.
- **Reads:** public → anyone; private owned → owner only; anything unreadable → **404**. The existing report test moved from 403 to 404, which is stricter.
- **Caches:** the optimize, compare and report checks run **before** the cache lookup. Previously a cache hit skipped the build lookup entirely.
- **Writes:** owner only. Ownerless builds return 403 "Anonymous builds are read-only".
- **New private ownerless builds** (anonymous imports) get an unguessable slug (`token_urlsafe(12)`).
- **Craft sessions:** ownerless sessions can no longer be deleted by anyone.

### R0-04 Build deletion (`c6ed5e4`)
- `BuildView.build` backref now uses `cascade="all, delete-orphan"`, and the foreign key declares `ondelete="CASCADE"`.
- Migration `a7c3e91f4d20` (down_revision `dd1840cac963`) recreates `build_views_build_id_fkey` with `ON DELETE CASCADE`.
- Policy: view rows are analytics owned by their build and are deleted with it.

### R0-05 Retired LET server fetch (`e61429b`)
- **Frontend:** `lib/importRouting.ts` (`decideUrlImport`) never sends LET planner URLs to the server. The modal explains why another step is needed without calling the URL invalid or expired, keeps the original link ("Open your planner"), and continues to the existing JSON tab and bookmarklet.
- **Backend:** `POST /api/import/build` with a LET URL, and the legacy `POST /api/import/url`, return 422 with `errors[0].code = LET_SERVER_FETCH_UNSUPPORTED` and `meta.supported_endpoint = /api/import/let/json`. Nothing is fetched and no failure is alerted.
- Maxroll and LET JSON import are unchanged.
- No circumvention, proxying or browser automation was added.
- Seven existing route tests that used LET URLs only as carriers for a mocked importer now use Maxroll URLs, with identical assertions.

### R0-06 Telemetry (`79aeb15`)
- `app/services/import_diagnostics.py` builds the structured record with these fields:
  - stage, category, HTTP status
  - allowlisted upstream headers: `server`, `cf-ray`, `cf-mitigated`, `cf-cache-status`, `content-type`, `retry-after`
  - `parsing_started` and `missing_field_state` (`NOT_EVALUATED` / `NONE_MISSING` / `MISSING_FIELDS_PRESENT`)
  - a counts-only partial-data summary
  - URL, user (or "anonymous")
  - app version, commit (`RENDER_GIT_COMMIT` / `GIT_COMMIT` / `SOURCE_VERSION`), data version, extractor version ("unknown"; R1 must supply it)
  - replay status
- The record is stored in the new `import_failures.diagnostics` JSON column (migration `c5d8e2b7a913`). `failure_id` and `timestamp` are the existing `id` and `created_at`.
- **Importers:** LET and Maxroll attach diagnostics on fetch failures. Cookies, authorization headers and bodies are never stored.
- **Route:** hard failures now forward `result.partial_data`, not `build_data`. The alert is sent even if the record cannot be stored.
- **Discord embed** fields: Stage, Category, HTTP Status, Upstream, Missing Fields (rendered from the state), Parsed Data ("Not attempted (failed at fetch)" for transport failures), Versions, Replay, Failure ID. The raw gear JSON dump was replaced by slot names and affix counts, so imported build payloads no longer reach Discord; the full payload remains in the admin-only record.
- **Maxroll messages** no longer say "may be expired" when every attempt was refused with 401/403.

### R0-07 Multi-target bounds (`337fbd0`)

| Limit | Value |
|---|---|
| Duration | ≤ 300 s |
| Tick | 0.01–10 s |
| Targets | ≤ 20 |
| Health | (0, 1e12] |
| Base damage | ≤ 1e9 |
| Step budget (ticks × targets) | ≤ 120,000; applies to custom targets and templates |
| Events returned | ≤ 5,000, with `damage_events_total` and `damage_events_truncated` |

All limits are checked before simulation state is built. Basis:
- UI range: tick 0.01–1 s, duration 1–300 s, largest template 10 targets.
- Local measurements: 120k steps ≈ 0.4 s / ~110 MB; 300k steps 0.95 s / 200 MB; the audit payload (3.6M steps) took 17.1 s / 1,688 MB / 315 MB of JSON.

### R0-08 API base composition (`b996038`)
- `lib/apiBase.ts` resolves the base once and appends `/api` when the configured value does not end in it.
- The API client, TopBar, the planner sign-in link and the backend debug dashboard all use it.
- The `render.yaml` value is unchanged (`https://api.epochforge.gg`), with an operator note.
- There is no Render API access from this environment, so the live dashboard value was **not** read and **not** guessed.

## 5. Files changed

47 files, +2,307 / −305 in code, tests and config (`git diff --stat 1efcef7..b9b0bfe`), plus the audit documents in the final docs commit.

| Group | Files |
|---|---|
| Backend app | `config.py`, `requirements.txt`, `app/__init__.py`, `app/utils/auth.py`, `app/models/__init__.py`, `app/routes/{admin,load,builds,skills,analysis,compare,report,views,craft,import_route,multi_target}.py` |
| Backend services | `build_access.py` (new), `build_service.py`, `import_diagnostics.py` (new), `discord_notifier.py`, `importers/{base_importer,lastepochtools_importer,maxroll_importer}.py` |
| Migrations | `a7c3e91f4d20_cascade_build_views_on_build_delete.py`, `c5d8e2b7a913_add_import_failure_diagnostics.py` |
| Frontend | `lib/apiBase.ts` (new), `lib/importRouting.ts` (new), `lib/api.ts`, `types/index.ts`, `BuildImportModal.tsx`, `BuildPlannerPage.tsx`, `TopBar.tsx`, `pages/debug/BackendDebugDashboard.tsx` |
| Config | `render.yaml` (comment only), `.env.example` (`GAME_DATA_MUTATION_ENABLED`, commit vars) |
| Existing tests adjusted | `test_build_import.py` (LET→Maxroll carriers; gear-privacy assertion), `test_community_tools.py` (403→404), `test_game_data_api.py` (admin path) |

## 6. Migrations added

| Revision | Down | Purpose | PostgreSQL 16 verification |
|---|---|---|---|
| `a7c3e91f4d20` | `dd1840cac963` | `build_views_build_id_fkey` → `ON DELETE CASCADE` | upgrade, downgrade, re-upgrade; constraint def checked; raw SQL cascade verified |
| `c5d8e2b7a913` | `a7c3e91f4d20` | `import_failures.diagnostics JSON NULL` | upgrade, downgrade, re-upgrade; column checked |

Single head: `c5d8e2b7a913`. A fresh empty database upgrades through the full chain. History was not rewritten.

## 7. Tests added

**Backend (`backend/tests/test_r0_*.py`, 244 tests):**

| File | Covers |
|---|---|
| `test_r0_deployability.py` | URL normalization, SQLAlchemy pin, installed version, psycopg2 driver, create_app normalization |
| `test_r0_game_data_mutation.py` | anonymous / user / admin × disabled / enabled; file hash and in-memory pipeline unchanged on rejection |
| `test_r0_build_access.py` | read matrix (10 routes × 12 owner/visibility cases), cached-optimize bypass, compare, vote, listing, update/skill-node/delete matrices, unguessable slugs, craft sessions |
| `test_r0_build_delete.py` | viewed-build delete by owner / other / anonymous; FK cascade declaration; migration chain |
| `test_r0_let_import_routing.py` | no fetch / importer / alert for LET URLs on both routes; validation; unknown source; Maxroll and LET JSON still work |
| `test_r0_import_telemetry.py` | header allowlist; status classification; importer-level 403; **incident replay** (record and Discord embed); Maxroll 403 via route; `partial_data` forwarding; all three missing-field states; alert without DB; migration head |
| `test_r0_multi_target_bounds.py` | audit payload rejected before the engine; each bound; template budget; inclusive boundary; truncation; default UI and templates |

**Frontend (26 tests):**
- `src/__tests__/components/build-import-let-routing.test.tsx`: routing function, no server call, copy, JSON hand-off with the original URL, Maxroll unchanged, backend code fallback, JSON import.
- `src/__tests__/lib/api-base.test.ts`: base resolution, composition, the committed `render.yaml` value, no raw env composition elsewhere.

Each new test file was also run against the pre-fix code to confirm it detects the defect:

| Suite | Result on pre-fix code |
|---|---|
| game-data mutation | 10 / 14 fail |
| build access | 54 / 171 fail |
| build delete | 2 / 5 fail |
| LET routing (backend) | 4 / 8 fail |
| telemetry | 7 / 14 fail |
| multi-target | 11 / 18 fail |
| LET routing (frontend) | 4 / 9 fail |

The tests that pass on old code are the "allowed" cases of each matrix.

## 8. Tests run

| Run | Environment | Result |
|---|---|---|
| Focused R0 backend suite `pytest tests/test_r0_*.py` | Py 3.11, SQLAlchemy 2.0.54 | **244 passed** |
| Focused R0 frontend suite | Node, vitest | **26 passed** |
| Full backend `pytest tests/ -q` (no `-x`) | Py 3.11, SQLAlchemy 2.0.54 | **11,665 passed, 379 skipped, 0 failed, 1 error**. The error is `test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes`, the pre-existing order-dependent SQLite teardown error (audit RT-6); it passes in isolation and on base. |
| Full frontend `vitest run` | | 925 passed, **17 failed**: the same 17 in `navigation.test.tsx` (11) and `layout.test.tsx` (6) fail identically on base `1efcef7` |
| `tsc --noEmit` | | 0 errors |
| ESLint on changed frontend files | | 0 errors (14 pre-existing warnings on untouched lines) |
| Production-config frontend build + Chromium | `VITE_API_BASE_URL=https://api.epochforge.gg` | requests to `https://api.epochforge.gg/api/...`, Discord link `/api/auth/discord` |
| Fresh-install production boot | new venv, empty PG 16 DB, `FLASK_ENV=production` | driver psycopg2, `flask db upgrade` → `c5d8e2b7a913`, `/api/health` 200, reload 404 |

Audit baseline for comparison (main, before R0): backend 11,415 passed / 379 skipped / 7 errors (6 of the errors were the psycopg3 failure); frontend 899 passed / 17 failed.

## 9. Before / after reproductions

| Finding | Before (base `1efcef7`) | After (branch HEAD) |
|---|---|---|
| INFRA-1 | clean install → SQLAlchemy 2.1.3; `create_engine('postgresql://…')` → `ModuleNotFoundError: psycopg` | SQLAlchemy 2.0.54; driver `psycopg2`; production boot and full migration on PG 16 |
| SYS-1 / SYS-2 | anonymous PATCH → 200, file rewritten; anonymous reload → 200 | 404 (disabled) or 401/403 (enabled); file hash and pipeline identity unchanged |
| API-4 | anonymous PATCH of another user's skill nodes → 200 | 404 (private), 401 (public, anonymous), 403 (other user) |
| API-5 | anyone could PATCH ownerless builds; any user could DELETE them | 403 for everyone on ownerless builds; owner-only on owned builds |
| API-6 | private builds readable on GET/simulate/skills/optimize/analysis/compare; optimize cache served without a lookup | 404 for non-owners on every route, checked before caches |
| DB-1 | owner DELETE of a viewed build → 500 `NotNullViolation` (PG 16) | 204; view rows deleted (ORM and DB-level cascade) |
| IMP-1 / IMP-2 | LET URL → server `requests.get` → 403 → alert | no request leaves the browser for LET; backend returns `LET_SERVER_FETCH_UNSUPPORTED`, no fetch, no alert |
| IMP-3 | 403 alert: "Missing Fields: None", "Parsed Data: No data parsed", no status or headers | "Missing Fields: Not evaluated — parsing did not complete", "Parsed Data: Not attempted (failed at fetch)", HTTP 403, `upstream_blocked`, cf-ray / cf-mitigated, versions, failure ID |
| API-2 | 3600 s / 0.01 s / 10 targets → 17.1 s, 1,688 MB, 315 MB response | 422 before the engine runs; maximum accepted request ≈ 0.4 s / ~110 MB; response ≤ 5,000 events |
| FE-1 | committed blueprint build → `https://api.epochforge.gg/builds`, `/auth/discord` | `https://api.epochforge.gg/api/builds`, `/api/auth/discord` |

**Residual behaviour chosen deliberately in R0 (for R4 to resolve):**
- **Ownerless builds** are readable by whoever holds the link, because anonymous imports and saves depend on it. They are immutable through the API. New private ownerless builds get unguessable slugs; existing ones keep name-derived slugs.
- **Ownerless craft sessions** keep action/undo for whoever holds the 64-bit random slug (anonymous crafting depends on it), but can no longer be deleted.
- **The `LastEpochToolsImporter` class** still contains its fetch code for offline and library use, but no route reaches it.

## 10. Remaining failures and production verification still required

**Remaining test failures:** none introduced by R0. The first full run surfaced one: `GAME_DATA_MUTATION_ENABLED` was undocumented in `.env.example`, which the env-contract test caught. It was fixed in `b9b0bfe`, and the full run was repeated. The pre-existing ones are:
- the 17 vitest failures above;
- the pytest-ignored legacy files `test_craft.py` and `test_craft_engine.py` (11 failures, identical on base);
- the order-dependent weaver teardown error (RT-6).

**Before deploying this branch, an operator must:**
1. **Render frontend:** read `VITE_API_BASE_URL` in the dashboard. Either form now works; confirm the built site requests `https://api.epochforge.gg/api/...`.
2. **Render API build:** confirm the build log installs `SQLAlchemy 2.0.54` and that `flask db upgrade` applies `a7c3e91f4d20` and `c5d8e2b7a913` cleanly against production Postgres. Take a backup first.
3. **Smoke checks after deploy:**
   - `PATCH /api/admin/affixes/<id>` → 404 and `POST /api/load/game-data` → 404 (anonymous)
   - delete a test build that has views → 204
   - paste `https://www.lastepochtools.com/planner/B5P5P8M3` into Import URL → guidance panel, and no server request in the network tab
4. **Discord:** trigger a Maxroll failure (or wait for one) and confirm the new embed fields render.
5. **Rate limiting:** client IP behind Render (API-7) is still unverified. It affects how R0's rate limits behave per user, but not their correctness.

Until these pass, every R0 finding stays `FIXED_LOCAL`, not `VERIFIED`.

## 11. Declaration

**AUDIT-R1 has not begun.**

No Last Epoch data was updated, no extraction was run, and the extractor was not modified. Calculation accuracy, affix scaling, mastery mapping, dead code and dependencies beyond the SQLAlchemy pin are untouched.

## 12. Repository state

Commits on `fix/audit-r0-emergency-production` (oldest first):

| Commit | Message |
|---|---|
| `58d4448` | fix: restore backend deployment dependency contract |
| `77e8a83` | fix: close production data mutation endpoints |
| `7c83b8a` | test: exercise game-data reload through the admin path |
| `9016ddd` | fix: enforce build ownership and visibility |
| `c6ed5e4` | fix: repair build deletion cascade |
| `e61429b` | fix: retire unsupported LE Tools server import |
| `79aeb15` | fix: make import failures diagnosable |
| `337fbd0` | fix: bound multi-target simulation requests |
| `b996038` | fix: compose frontend API URLs under /api for any configured base |
| `b9b0bfe` | docs: document game-data mutation and commit env vars |
| (final) | docs: record R0 remediation evidence |

The final docs commit adds this report, the branch reconciliation, the audit artifacts and the updated `AUDIT_EVIDENCE.json`.

The R0 regression tests sit in each fix commit next to the code they cover, rather than in a separate "test:" commit, so every commit is independently verifiable.
- main and dev were not modified.
- Nothing was deployed or merged.

## 13. R0 exit gate (local)

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Can a clean backend install boot using the intended DB driver? | **YES** | fresh Py 3.11 venv → SQLAlchemy 2.0.54, psycopg2, production config boot, `flask db upgrade` to `c5d8e2b7a913` on empty PG 16 |
| 2 | Can unauthorized users modify production game data? | **NO** | `test_r0_game_data_mutation.py`; production reload → 404 |
| 3 | Can one user modify another user's build? | **NO** | update / skill-node / delete matrices in `test_r0_build_access.py` |
| 4 | Can anonymous users read private builds? | **NO** (owned private builds) | read matrix, 10 routes; cached-optimize test. Ownerless builds are link-readable by design (§9). |
| 5 | Can authorized users delete viewed builds without a 500? | **YES** | `test_r0_build_delete.py`; PG 16 reproduction 500 → 204 |
| 6 | Does the default UI avoid the known-dead LET server-side fetch? | **YES** | frontend routing tests; backend `LET_SERVER_FETCH_UNSUPPORTED` without fetch |
| 7 | Does a 403 produce truthful, actionable telemetry? | **YES** | incident replay test: NOT_EVALUATED, HTTP 403, `upstream_blocked`, cf-ray / cf-mitigated, versions, failure ID |
| 8 | Can one anonymous multi-target request allocate unbounded memory? | **NO** | `test_r0_multi_target_bounds.py`; maximum accepted ≈ 110 MB |
| 9 | Is committed API-base configuration internally correct? | **YES** | `api-base.test.ts`; Chromium check on a production-config build |
| 10 | Are focused R0 regression tests green? | **YES** | 244 backend + 26 frontend |

**R0 is complete locally.** Production verification (§10) is still required before any finding moves to `VERIFIED`.
