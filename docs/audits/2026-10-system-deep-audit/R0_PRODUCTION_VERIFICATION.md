# AUDIT-R0 — Production Verification

Date: 2026-10-06
Status: **R0 DEPLOYMENT VERIFICATION PENDING**. PR #572 is merged; the production deployment and smoke tests still need operator confirmation.

## Update — merge (2026-10-06 13:55 UTC)

### Operator-verified pre-deploy gates
| Gate | Operator result |
|---|---|
| Database | `epochforge-db` |
| Fresh logical export | completed 2026-10-06 9:41 AM; artifact shown in Render |
| Point-in-time recovery | enabled, 3-day window |
| epochforge-api | healthy; branch `main`; root `backend`; build installs `requirements.txt`; pre-deploy `flask db upgrade`; Gunicorn start; auto-deploy enabled |
| epochforge-frontend | branch `main`; root `frontend`; static site; publish `dist`; auto-deploy On Commit |
| `VITE_API_BASE_URL` | `https://epochforge-api.onrender.com/api`. It already ends in `/api`, so `resolveApiBase()` keeps it and requests compose to `https://epochforge-api.onrender.com/api/...`. Compatible. |

These differ from the committed `render.yaml` (auto-deploy is on; the API host is the Render hostname). The blueprint still drifts from live configuration, which is a known R7 item.

### Final PR revalidation (all passed)
- PR #572 open; head `409607d91a43e2b325381ec2bfdfb9608eeb369c` (the tested revision)
- CI 3/3 `success`, none pending
- 0 reviews, review threads and comments
- `mergeable_state: clean`; base `main` @ `1efcef7`

### Merge record
| Item | Value |
|---|---|
| PR | #572 |
| PR head SHA | `409607d91a43e2b325381ec2bfdfb9608eeb369c` |
| Merge method | merge commit (repository convention), pinned with `expectedHeadSha` |
| Resulting main SHA | `80bd559dbdcc950fbf69b62946ff49b130ba51b9` (parents `1efcef7`, `409607d`) |
| Merge timestamp | 2026-10-06T13:55:11Z |
| R0 commits in main | all 11 confirmed with `git merge-base --is-ancestor`; `SQLAlchemy==2.0.54` and both migration files present on main |

### Post-merge automation observed (GitHub only)
- **Deploy to Render** run #8 (`37474647287`) on `80bd559`: `success` at 13:55:23Z. This proves only that the deploy hook accepted the request. **It does not show that Render built, migrated or booted successfully.** Both services also have auto-deploy enabled, so Render may start its own deploy from the push as well.
- **Sync main back to dev** run #6 (`37474647247`): started automatically by the push; still in progress when checked. It opens a PR merging main into dev with `-X ours` (dev wins conflicting hunks). Per the R0 instructions, **main → dev reconciliation is not performed and that PR must not be merged until R0 is production-verified.** A `-X ours` merge could silently keep dev's side of any conflicting hunk in an R0 file, so it needs a hand-checked merge later.

### Classification
**R0 DEPLOYMENT VERIFICATION PENDING.** No finding is promoted to `VERIFIED`; `AUDIT_EVIDENCE.json` is unchanged.

---

## Previous state (before operator confirmation)


Date: 2026-10-06
Status: **R0 NOT VERIFIED — BLOCKED** (before merge; production was not touched)

## Summary

| Item | Value |
|---|---|
| PR | #572 `fix/audit-r0-emergency-production` → `main` — **open, not merged** |
| PR head | `409607d91a43e2b325381ec2bfdfb9608eeb369c` (unchanged from the tested revision) |
| main head | `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` |
| Merge SHA | — (not merged) |
| Backend deployed SHA/version | — (no deploy) |
| Frontend deployed SHA/version | — (no deploy) |
| Migration head (repo) | `c5d8e2b7a913` (single head; chain `dd1840cac963 → a7c3e91f4d20 → c5d8e2b7a913`) |
| Production config checked | **NO**. Render dashboard and API unreachable; PRODUCTION CONFIG VERIFICATION REQUIRED |
| Backup verified | **NO**. Production database unreachable |
| Smoke / security / importer / telemetry / simulation tests in production | **Not executed** |
| Production observations | None possible |
| dev reconciliation | **Not started**. It is gated on R0 being merged and production-verified |
| Remaining R0 findings | 12 `FIXED_LOCAL`; FE-4 and OBS-1 `OPEN` (partial); none `VERIFIED` |

## Blocker

From this environment, outbound connections to every production host are refused by the network policy (curl returns `000`, connection rejected at the proxy):

- `https://api.epochforge.gg` (backend)
- `https://epochforge.gg` (frontend)
- `https://api.render.com` (Render API)
- `https://dashboard.render.com`

No Render credential (for example `RENDER_API_KEY`) or production database access is available either.

Merging PR #572 pushes to `main`, which triggers `.github/workflows/deploy.yml`. That calls the Render deploy hook, whose `preDeployCommand` runs `flask db upgrade` against production. Merging would therefore:

1. deploy and migrate production without a confirmed backup (Phase 3 requires one first), and
2. leave the deploy, migrations, boot and every R0 smoke test unobservable, so a failure could not be detected or verified.

The Phase 2 allowance (merge even if the dashboard can't be read) applies only when production verification can safely detect failure. From here it cannot. The merge was therefore not performed.

## Phase 1 — Final PR verification (completed)

| # | Check | Result |
|---|---|---|
| 1 | PR open | YES (state `open`, not draft) |
| 2 | CI green | YES: Backend Tests, Frontend Type-Check and Data Validation all `success` on `409607d` |
| 3 | No pending required check | YES: 3/3 completed |
| 4 | No unresolved blocking review comment | YES: 0 reviews, 0 review threads, 0 comments |
| 5 | PR head | `409607d91a43e2b325381ec2bfdfb9608eeb369c` = tested revision |
| 6 | main head | `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` = branch base |
| 7 | No unexpected commits | YES: exactly the 11 R0 commits |
| 8 | Tested commits present | YES: `58d4448 77e8a83 7c83b8a 9016ddd c6ed5e4 e61429b 79aeb15 337fbd0 b996038 b9b0bfe 409607d` |
| 9 | Single migration head | YES: `c5d8e2b7a913` |
| 10 | No merge conflict | YES: `mergeable_state: clean`; main is an ancestor of the PR head |

## Phase 2 — Production config (not possible)

**PRODUCTION CONFIG VERIFICATION REQUIRED.** An operator must check the following in the Render dashboard. Report shapes and presence only, never secret values.

| Service | Check | Expected for R0 |
|---|---|---|
| epochforge-frontend | `VITE_API_BASE_URL` | Any of `https://api.epochforge.gg` or `https://api.epochforge.gg/api` (with or without a trailing `/`). After R0 both compose to `https://api.epochforge.gg/api/...`. A value pointing at another host, or a path under the API host other than `/api`, is incompatible. |
| epochforge-frontend | branch, build command, auto-deploy | branch `main`; `npm install && npm run build`; the blueprint says `autoDeploy: false`. **Record whether the deploy hook in GitHub targets the frontend at all**: the repo has one hook (`RENDER_DEPLOY_HOOK_URL`) and two services, so the frontend may need a manual deploy. |
| epochforge-api | branch, build command | `main`; `pip install -r requirements.txt` |
| epochforge-api | pre-deploy | `flask db upgrade` |
| epochforge-api | start | `gunicorn wsgi:app --workers=4 --threads=2 --timeout=120 ...` |
| epochforge-api | `PYTHON_VERSION` | `3.11` (R0 was verified on 3.11) |
| epochforge-api | `DATABASE_URL` | present, from `epochforge-db`. R0 accepts `postgres://` or `postgresql://`. |
| epochforge-api | `GAME_DATA_MUTATION_ENABLED` | any value is fine: production ignores it |
| GitHub | `RENDER_DEPLOY_HOOK_URL` secret | present; record which service it deploys |

## Phase 3 — Database safety

**Backup: NOT VERIFIED.** The production database is unreachable from here. An operator must create an on-demand backup/snapshot of `epochforge-db` (Render Postgres → Backups / Recovery) and record its timestamp before the merge.

Migration review (rendered with `flask db upgrade dd1840cac963:c5d8e2b7a913 --sql`), identical to what was tested on PostgreSQL 16:

```sql
BEGIN;
ALTER TABLE build_views DROP CONSTRAINT build_views_build_id_fkey;
ALTER TABLE build_views ADD CONSTRAINT build_views_build_id_fkey
  FOREIGN KEY(build_id) REFERENCES builds (id) ON DELETE CASCADE;
ALTER TABLE import_failures ADD COLUMN diagnostics JSON;
UPDATE alembic_version SET version_num='c5d8e2b7a913' ...;
COMMIT;
```

| Concern | Assessment |
|---|---|
| Destructive operations | None on data. A constraint is dropped and re-created inside the same transaction. |
| Table rewrites | None. `ADD COLUMN ... JSON` (nullable, no default) is metadata-only in PostgreSQL. |
| Lock risk | Adding the FK validates existing `build_views` rows while holding `SHARE ROW EXCLUSIVE` on `build_views` and `builds`. Writes to both block for the scan, expected to be short at current scale. |
| Nullable / default | `diagnostics` is nullable with no default; existing rows read NULL. The code tolerates NULL. |
| Existing-data compatibility | Existing rows already satisfy the FK (the same constraint exists today). |
| Failure mode | If production's constraint name differed from PostgreSQL's default `build_views_build_id_fkey`, the transaction rolls back atomically and pre-deploy fails. Render keeps the previous release running. |
| Downgrade | Exact inverse; dropping `diagnostics` discards only the new diagnostics data. |

Nothing differs from what was locally tested.

## Phases 4–9 — Not executed

Merge, deploy observation, the production smoke suite (A–G), health observation, the evidence upgrade to `VERIFIED`, and dev reconciliation all depend on the blocker above. `AUDIT_EVIDENCE.json` is unchanged: no finding is promoted to `VERIFIED`.

## Gates

| # | Gate | Answer |
|---|---|---|
| 1 | Production backend deploys successfully? | **NO**: not deployed / not verified |
| 2 | Production frontend deploys successfully? | **NO**: not deployed / not verified |
| 3 | Production DB migrated successfully? | **NO**: not run |
| 4 | Unauthorized game-data mutation blocked? | **NO** (not verified in production; production still runs pre-R0 `main`, where it is **not** blocked) |
| 5 | Cross-user build mutation blocked? | **NO** (not verified; pre-R0 code still live) |
| 6 | Private build disclosure blocked? | **NO** (not verified; pre-R0 code still live) |
| 7 | Viewed-build deletion works? | **NO** (not verified; pre-R0 code still live) |
| 8 | LET dead fetch removed from user flow? | **NO** (not verified; pre-R0 code still live) |
| 9 | Import telemetry truthful? | **NO** (not verified; pre-R0 code still live) |
| 10 | Multi-target resource attack bounded? | **NO** (not verified; pre-R0 code still live) |
| 11 | API URL composition correct? | **NO** (not verified in production) |
| 12 | No R0-introduced production regression detected? | **NO**: nothing deployed, so nothing observed |

All 12 are YES locally (see `R0_IMPLEMENTATION_REPORT.md` §13). None are verified in production.

## Final verdict

**R0 NOT VERIFIED — BLOCKED**

**Exact blocker:** this environment has no network path or credentials to production (`api.epochforge.gg`, `epochforge.gg`, `api.render.com`, the production database). So:

- a pre-migration backup cannot be confirmed;
- the deploy triggered by merging cannot be observed;
- no production smoke test can run.

**To unblock, either:**

1. **Give this environment access:**
   - Network access to `api.epochforge.gg`, `epochforge.gg` and `api.render.com` (environment settings → Network access → Custom → Allowed domains).
   - A Render API key as an environment secret. Read access covers the config check; deploy/log access covers observation.
   - Confirmation that a fresh `epochforge-db` backup exists.

   Then rerun this task: the merge and every phase continue from here.

2. **Or have an operator:**
   - take the backup and check the Phase 2 table;
   - explicitly authorise the merge without in-environment observation;
   - report the deploy result and smoke-test results back.

   This verification would then be completed from those observations.

R1 has not begun.
