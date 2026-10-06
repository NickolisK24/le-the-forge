# R0 Branch Reconciliation

Date: 2026-10-06
Purpose: choose the remediation base for AUDIT-R0 before any implementation.

## Refs compared

| Ref | SHA | Notes |
|---|---|---|
| `origin/main` | `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` | Deployed production baseline (2026-05-14); audited ref |
| `origin/dev` | `558557c222f9cb3daa0a6fb152cb4cbe5f33456e` | Last commit 2026-05-29 |
| main..dev | 413 commits ahead, 0 behind | `git rev-list --count` both directions |

Commands:

```
git fetch origin dev main
git rev-list --count origin/main..origin/dev     # 413
git rev-list --count origin/dev..origin/main     # 0
git diff --stat origin/main origin/dev -- <R0 file set>
git diff --numstat origin/main origin/dev | awk '$2>0'
git log --oneline origin/main..origin/dev -- <R0 file set>
```

## Diff summary

`git diff --stat origin/main origin/dev` reports 1,622 files changed, 994,938 insertions and **23 deletions**. dev is almost purely additive.

| Area | Files changed on dev |
|---|---|
| backend/app | 662 (new v3/v4 trust/orchestration modules) |
| backend/tests | 280 |
| docs/generated | 242 (large generated reports; the top 5 alone are ~220k lines) |
| docs/migration | 209 |
| backend/scripts | 205 |
| frontend/src | 14 (trust-surface types/components) |

Every line deleted on dev falls in `ARCHITECTURE.md`, `README.md`, `ROADMAP.md`, `docs/README.md`, `docker-compose.yml` (1 line) or `frontend/vite.config.ts` (3 lines). Nothing on dev removes or edits runtime backend logic that main already has.

## R0 file set: main vs dev

Compared: `backend/requirements.txt`, `backend/config.py`, `render.yaml`, `backend/app/routes/{admin,load,builds,skills,craft,import_route,auth,multi_target}.py`, `backend/app/services/{build_service,discord_notifier}.py`, `backend/app/services/importers/lastepochtools_importer.py`, `backend/app/models/**`, `backend/migrations/**`, `backend/app/schemas/**`, `backend/app/utils/auth.py`, `backend/app/__init__.py`, `frontend/src/components/features/build/BuildImportModal.tsx`, `frontend/src/lib/api.ts`.

Result: only two of these files differ, and both changes are additive.

| File | Change on dev | Commits |
|---|---|---|
| `backend/app/__init__.py` | +2 lines: registers a new `trust_bp` at `/api/trust` (read-only GET `/visibility`) | `c400073` |
| `backend/config.py` | +12 lines: `V3_1_TRUSTED_PRODUCTION_SHADOW_*` flags (default off) | `f0cca42` |

Adjacent non-R0 changes: `backend/pytest.ini` (`testpaths`, `norecursedirs`; `816a5a4`), `frontend/vite.config.ts` and `docker-compose.yml` (a dev-proxy `VITE_API_PROXY_TARGET`; `3cbe344`). The docker/vite change touches local development only; `render.yaml` is unchanged on dev.

## Finding-by-finding comparison

| Finding | Status on dev | Evidence |
|---|---|---|
| INFRA-1 (unpinned SQLAlchemy / psycopg3) | UNCHANGED_ON_DEV | `backend/requirements.txt` identical |
| SYS-1 (anonymous affix PATCH writes file) | UNCHANGED_ON_DEV | `admin.py` identical |
| SYS-2 (anonymous game-data reload) | UNCHANGED_ON_DEV | `load.py` identical |
| API-4 (skill-node IDOR) | UNCHANGED_ON_DEV | `skills.py` identical |
| API-5 (anonymous build/craft mutation) | UNCHANGED_ON_DEV | `builds.py`, `craft.py`, `build_service.py` identical |
| API-6 (private builds readable by slug) | UNCHANGED_ON_DEV | same |
| DB-1 (BuildView delete 500) | UNCHANGED_ON_DEV | `models/**` and `migrations/**` identical |
| IMP-1 / IMP-2 / FE-4 (dead LET URL path) | UNCHANGED_ON_DEV | `BuildImportModal.tsx`, `import_route.py`, `lastepochtools_importer.py` identical |
| IMP-3 / OBS-1 (misleading alert) | UNCHANGED_ON_DEV | `import_route.py`, `discord_notifier.py` identical |
| API-2 (unbounded multi-target sim) | UNCHANGED_ON_DEV | `multi_target.py` identical |
| FE-1 (API base / render.yaml drift) | UNCHANGED_ON_DEV | `render.yaml` and `lib/api.ts` identical; dev only adds a local docker proxy variable |

No R0 finding is FIXED, PARTIALLY_FIXED, REGRESSED or ARCHITECTURALLY_CHANGED on dev.

## Recommendation

**Base: A — `main` @ `1efcef7`.**

Remediation branch: `fix/audit-r0-emergency-production`, created from `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa`.

Rationale:
- Production is `main`, and all audit evidence was gathered against `main`.
- dev contains **no** R0-relevant fix, so nothing on dev is required to repair main safely.
- dev's changes do not overlap the R0 file set, apart from two additive lines in the app factory and config. Every R0 fix made on main should therefore merge forward into dev with little or no conflict.

## Rejected alternatives

- **B — dev as base.** It would ship 413 unreviewed commits (~995k lines, mostly generated reports) to production alongside emergency fixes. dev CI has been red since 2026-05-09, and it fails 9 of its own production-boundary guards locally (audit RT-2). That violates "smallest trustworthy base", and none of dev's work is needed for R0.
- **C — main plus selected dev commits.** There is nothing to select: no dev commit touches the R0 code paths. Cherry-picking the trust blueprint or v3.1 flags would add unaudited surface to an emergency branch.

## Risks

1. **Forward-merge to dev.** R0 changes `builds.py`, `skills.py`, `import_route.py`, models and migrations. dev has the same content for these files, so merging main into dev after R0 should be clean. The new R0 migration must have `down_revision` equal to dev's head, which is the same head as main (`dd1840cac963`, since dev adds no migrations). This needs checking at merge time.
2. **dev's experimental surfaces remain unreviewed** for the R0 security invariants (for example, the new `/api/trust/visibility` route is read-only and unauthenticated by design). They are out of R0 scope and must be re-checked before dev is ever released.
3. **The shallow local clone** (history from 2026-03-31) is sufficient for this comparison because main..dev is entirely after that date.
