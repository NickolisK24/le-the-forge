# AUDIT-R0 — Production Verification

Date: 2026-10-06
Final classification: **R0 NOT VERIFIED — BLOCKED on unperformed production security probes** (no failure observed; see Verdict)

## Summary

| Item | Value |
|---|---|
| PR | #572 `fix/audit-r0-emergency-production` → `main`, merged |
| PR head | `409607d91a43e2b325381ec2bfdfb9608eeb369c` |
| Merge SHA | `80bd559dbdcc950fbf69b62946ff49b130ba51b9` (merge commit; parents `1efcef7`, `409607d`), 2026-10-06T13:55:11Z |
| Backend deployed | `80bd559`, Live on `epochforge-api` (operator-observed) |
| Frontend deployed | `80bd559`, Live on `epochforge-frontend` (operator-observed) |
| Migration head | `c5d8e2b7a913`; pre-deploy ran `dd1840cac963 → a7c3e91f4d20 → c5d8e2b7a913` |
| Production config checked | YES (operator); no configuration changed |
| Backup verified | YES (operator): logical export of `epochforge-db` completed 2026-10-06 9:41 AM; point-in-time recovery enabled (3-day window) |
| Smoke tests | Partial: LET user flow and API routing verified; security/ownership/telemetry/simulation probes **not performed** |
| Production observations | Several minutes post-deploy: no 500s, SQLAlchemy/psycopg errors, restarts, migration errors or routing regressions |
| dev reconciliation | **Not performed** (gated on production verification; see below) |
| Remaining R0 findings | VERIFIED 3, FIXED_LOCAL 9, OPEN (partial) 2 |

All production facts below were observed and reported by the operator. Nothing in this document was observed from the verification environment, which has no network path to production.

## Pre-deploy gates (operator)

| Gate | Result |
|---|---|
| Backup | PASS: fresh logical export completed 2026-10-06 9:41 AM; artifact present; PITR on, 3-day window |
| epochforge-api config | PASS: branch `main`, root `backend`, requirements-based build, pre-deploy `flask db upgrade`, Gunicorn start, auto-deploy on |
| epochforge-frontend config | PASS: branch `main`, root `frontend`, static site, publish `dist`, auto-deploy On Commit |
| `VITE_API_BASE_URL` | `https://epochforge-api.onrender.com/api`. It already ends in `/api`, so `resolveApiBase()` keeps it; compatible |
| Final PR revalidation | PASS: head `409607d`, CI 3/3 green, no reviews/comments, `mergeable_state: clean` |

## Deployment (operator)

**Backend: PASS.** Commit `80bd559` Live. The pre-deploy log shows:

```
Running upgrade dd1840cac963 -> a7c3e91f4d20, Cascade build_views rows when their build is deleted
Running upgrade a7c3e91f4d20 -> c5d8e2b7a913, Add diagnostics JSON to import_failures
Pre-deploy complete!
Running 'gunicorn wsgi:app'
Starting gunicorn 22.0.0
Booting worker
GET /api/health -> 200
Your service is live
```

No ModuleNotFoundError, NotNullViolation, OperationalError, migration failure or boot loop. The INFRA-1 failure mode (SQLAlchemy 2.1 selecting the uninstalled psycopg3) did not occur.

The logs still report data version `unknown`. That is the known R1/R2 provenance gap, not an R0 regression.

**Frontend: PASS.** Commit `80bd559` Live. `tsc && vite build` completed (1001 modules) and was uploaded. npm reported the already-audited dependency advisories (SEC-4/SEC-8), which are out of R0 scope.

## Production smoke results

| Test | Status | Evidence |
|---|---|---|
| D. LET import flow (`planner/B5P5P8M3` on epochforge.gg) | **PASS** | LET recognised; no HTTP 403; "ONE MORE STEP FOR LAST EPOCH TOOLS BUILDS" with "CONTINUE WITH LAST EPOCH TOOLS IMPORT" and "Open your planner"; **no new #forge-alerts Import Failure alert** |
| G. API base URL | **PASS** | epochforge.gg traffic reached `/api` routes: `GET /api/version`, `/api/ref/affixes`, `/api/ref/blessings`, `/api/passives/Sentinel` → 200; CORS preflight from `https://epochforge.gg` → 200 |
| Post-deploy health | **PASS** | repeated `GET /api/health` → 200; no 500s, DB-driver errors, worker restarts or migration errors |
| A. Anonymous affix PATCH / game-data reload | **NOT PERFORMED** | operator chose not to issue security probes |
| B. Build privacy / ownership | **NOT PERFORMED** | |
| C. Viewed-build delete | **NOT PERFORMED** | migration that enables it is applied |
| E. Import-failure telemetry | **NOT PERFORMED** | no controlled failure triggered; the LET flow correctly generated *no* alert |
| F. Multi-target bounds | **NOT PERFORMED** | |

Untested behaviour is not inferred from the deployment. Its evidence remains the focused R0 regression suite (244 backend + 26 frontend tests, each shown to fail on pre-fix code), green CI on `409607d`, and the PostgreSQL 16 migration verification.

## Finding status (AUDIT_EVIDENCE.json)

| Finding | Status | Basis |
|---|---|---|
| INFRA-1 | **VERIFIED** | production build, migrations, boot and health |
| IMP-1 | **VERIFIED** | production LET flow shows guidance; no alert |
| FE-1 | **VERIFIED** | production frontend reaches `/api` routes with the live base value |
| DB-1 | FIXED_LOCAL | cascade migration applied in production; delete behaviour not exercised |
| IMP-2 | FIXED_LOCAL | user path verified via IMP-1; direct-API response and importer diagnostics not exercised |
| IMP-3 | FIXED_LOCAL | diagnostics column migrated; no failure record produced in production |
| SYS-1, SYS-2 | FIXED_LOCAL | game-data mutation probes not run |
| API-4, API-5, API-6 | FIXED_LOCAL | ownership/privacy probes not run |
| API-2 | FIXED_LOCAL | bound probe not run |
| FE-4 | OPEN (partial) | LET guidance verified; remaining Quick Fetch tab, footer and Maxroll fallback → R4 |
| OBS-1 | OPEN (partial) | diagnostics migrated; dedupe/grouping → R7; extractor-version provenance → R1 |

`AUDIT_EVIDENCE.json` already supports `OPEN`, `FIXED_LOCAL`, `VERIFIED`, `DEFERRED_WITH_REASON` and `INFO`. It has no `PARTIAL` status, so partial findings stay `OPEN`, and each finding's `production_evidence` field says what is done and what remains. No finding is `DEFERRED_WITH_REASON`.

## Gate assessment

| # | Gate | Answer |
|---|---|---|
| 1 | Production backend deploys successfully? | **YES** |
| 2 | Production frontend deploys successfully? | **YES** |
| 3 | Production DB migrated successfully? | **YES** (both upgrades in the pre-deploy log; pre-deploy complete) |
| 4 | Unauthorized game-data mutation blocked? | **NO**: not verified in production (locally YES; code deployed) |
| 5 | Cross-user build mutation blocked? | **NO**: not verified in production (locally YES; code deployed) |
| 6 | Private build disclosure blocked? | **NO**: not verified in production (locally YES; code deployed) |
| 7 | Viewed-build deletion works? | **NO**: not verified in production (locally YES; migration applied) |
| 8 | LET dead fetch removed from user flow? | **YES** |
| 9 | Import telemetry truthful? | **NO**: not verified in production. No false alert was generated, but no failure record was exercised (locally YES) |
| 10 | Multi-target resource attack bounded? | **NO**: not verified in production (locally YES; code deployed) |
| 11 | API URL composition correct? | **YES** |
| 12 | No R0-introduced production regression detected? | **YES**, within the observed window |

## Verdict

**R0 NOT VERIFIED — BLOCKED**

The gate requires production confirmation for gates 4, 5, 6, 7, 9 and 10, and those probes were not performed. This verdict does not weaken the gate. **Nothing failed.** The deployment is healthy and no regression was observed. The block is purely that six security and behaviour gates are verified locally but not in production.

**Do the FIXED_LOCAL findings block R1?** Not technically. R1 (extraction truth and completeness) works in the extractor repository, the sync pipeline and `data/`. It does not depend on the authorization, ownership, telemetry or simulation-bound code paths. Starting R1 with these findings at `FIXED_LOCAL` is a governance decision, which is the owner's to make, and does not create a dependency risk.

**To reach `R0 VERIFIED — READY FOR R1`,** run these non-destructive probes against `https://epochforge-api.onrender.com/api`:
1. `PATCH /admin/affixes/<id>` and `POST /load/game-data` anonymously → 404.
2. Two-account build checks for private read/mutate, public mutate, and anonymous-build mutate/delete, using throwaway builds deleted afterwards.
3. Open a throwaway owned build page, then delete it as the owner → 204.
4. `POST /import/build` with `https://maxroll.gg/last-epoch/planner/r0telemetrytest` → 422. The Discord embed shows "Not evaluated", Stage `fetch`, an HTTP status, and no raw payload.
5. An oversized multi-target body (3600 s / 0.01 s / 10 targets) → fast 422. A `single_boss` template request → 200.

Then mark SYS-1, SYS-2, API-4, API-5, API-6, DB-1, IMP-2, IMP-3 and API-2 `VERIFIED` as their probes pass.

## dev reconciliation

**Not performed.** The R0 rule permits main → dev reconciliation only after R0 is merged **and production-verified**, and the verdict above is not verified.

State recorded for when it is permitted:
- The merge triggered the repository's `sync-main-to-dev` workflow (run #6). It pushed `chore/sync-main-to-dev-80bd559` (`1057806`, parents dev `558557c` + main `80bd559`) but failed before opening a PR. **dev is unchanged.**
- That branch contains both histories in full. Every R0 file (routes, services, importers, models, migrations, auth utils, frontend lib/modal, R0 tests) is identical to main. Its only differences from main are dev's additive changes (the `/api/trust` blueprint, the v3.1 config flags, trust-surface frontend modules). The workflow's `-X ours` strategy did **not** drop any R0 change.
- When permitted: merge main into dev (as that branch does, or with a fresh `git merge origin/main` on dev), then run `pytest tests/test_r0_*.py` and the two R0 vitest files against the result.

## History

- **Earlier the same day:** verification was blocked before merge because the verification environment had no production access and no backup confirmation. The operator then supplied the backup and configuration evidence above.
- **13:55:11Z:** merged; the Deploy to Render workflow (run #8) accepted the hook. Render's own deploy result is the operator evidence above.

R1 has not begun.
