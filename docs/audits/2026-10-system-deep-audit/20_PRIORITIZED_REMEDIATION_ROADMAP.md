# 20 — Prioritized Remediation Roadmap

Audit date: 2026-10-06
Scope: le-the-forge `main` @ `1efcef7`, last-epoch-data `main` @ `73e2ab0`.
Finding IDs refer to `AUDIT_EVIDENCE.json` and to reports 01–19.

This is not a wish list. Each package below is required either to stop active harm or to make a truthful claim about extraction and calculation correctness. Product features, UI polish and dependency modernization are deliberately excluded unless a finding forces them.

## Sequencing rule

```
R0 (emergency) ─┬─> R1 (extraction truth) ─┬─> R2 (schema/relationships) ─┬─> R4 (import reliability)
                │                          │                               └─> R6 (product consumption trust)
                │                          └─> R3 (patch drift / change detection)
                ├─> R5 (test/certification gates)   [can run alongside R1]
                └─> R7 (operational hardening)      [can run alongside R1]
```

**Decision required before R0 starts:** choose the remediation base branch. `dev` is 413 commits ahead of `main`, has been red for 261 consecutive CI runs, and fails 9 of its own production-boundary guards locally (RT-2). Fixing on `main` and then reconciling `dev`, or the other way round, is a project decision. The audit evidence is all against `main`, which is what is deployed.

---

## AUDIT-R0 — Emergency production breakages

**Objective:** stop active data tampering, stop the user-facing importer dead end, and make the API deployable again so every later fix can ship.

**Why it matters:** `main` cannot currently be safely rebuilt (INFRA-1). Anyone on the internet can rewrite the affix data the calculators use (SYS-1). The importer path that real users are hitting fails 100% of the time with an unhelpful message (IMP-1, IMP-2).

| Item | Findings | Files / components |
|---|---|---|
| Make the API rebuildable: pin SQLAlchemy (or select the psycopg2 driver explicitly) and add a constraints/lock file | INFRA-1 | `backend/requirements.txt`, `backend/config.py`, `render.yaml` |
| Remove or admin-gate the anonymous game-data write and reload routes; make runtime game data read-only | SYS-1, SYS-2 | `backend/app/routes/admin.py`, `backend/app/routes/load.py`, `frontend/src/App.tsx` (`/affixes`, `/data-manager`) |
| Close the ownership holes on build mutation | API-4, API-5 | `backend/app/routes/skills.py:281`, `builds.py`, `craft.py` |
| Enforce visibility for private builds | API-6 | `backend/app/services/build_service.py`, `routes/builds.py` |
| Bound the multi-target simulation inputs | API-2 | `backend/app/routes/multi_target.py` |
| Fix build deletion (BuildView FK cascade) through a new migration | DB-1 | `backend/app/models/__init__.py:352-361`, new migration |
| Stop sending LE Tools URLs to the server-side fetch; route users to the bookmarklet/JSON path with a clear message | IMP-1, IMP-2, FE-4 | `BuildImportModal.tsx`, `import_route.py`, `lastepochtools_importer.py:693-727` |
| Fix the alert so it carries `partial_data`, failure stage, HTTP status and upstream diagnostic headers | IMP-3 | `import_route.py:575`, `discord_notifier.py` |
| Reconcile `render.yaml` with the live Render configuration (read-only check of the dashboard first) | FE-1 | `render.yaml`, `frontend/src/lib/api.ts` |

**Acceptance criteria**
- A clean `pip install -r backend/requirements.txt` on Python 3.11 yields a SQLAlchemy that boots against `postgresql://`, and `flask db upgrade` succeeds against a throwaway Postgres.
- An anonymous `PATCH /api/admin/affixes/<id>`, `POST /api/load/game-data`, or `PATCH /api/builds/<slug>/skills/...` on another user's build returns 401/403. No route writes under `data/` at runtime.
- An anonymous GET of a private build returns 403/404 on every endpoint that reads it.
- Deleting a build that has views succeeds.
- Submitting `https://www.lastepochtools.com/planner/B5P5P8M3` in the URL tab never triggers a server fetch. The user is shown the supported import path.
- A failed import alert includes the failure stage, the upstream status, the app commit and the data version. The alert says "not attempted" rather than "None" when nothing was parsed.
- `render.yaml` and the live configuration agree, and this is documented.

**Required tests:** auth-negative tests for every mutating route; an ownership test per resource; a private-visibility test per read path; a schema-bound test for multi-target; a delete-with-views test; an importer modal test for LE Tools URLs; an alert content test using the incident's exact payload; a URL-composition test for the API base; a CI job that runs `flask db upgrade` on Postgres.

**Dependencies:** branch decision above. **Complexity:** M. **Blocks production promotion:** YES.

---

## AUDIT-R1 — Extraction truth and completeness

**Objective:** what production serves must be a reproducible, provenance-stamped projection of the current game patch, with every known value-scale and field-loss defect removed. "Complete" must have a measurable definition.

**Why it matters:**
- The served data is a 1.4.3-era snapshot stamped "unknown" (EXT-1). The game is on 1.5.x Season 5 (DRIFT-1).
- Affix values are stored at 100× (EXT-2, LOSS-1). Hybrid affix second properties, passive structured stats and unique/set modifiers are dropped (LOSS-2/3/5).
- 19 game tables are never extracted (EXT-4), and the 1.4.6 raw inputs are not preserved (EXT-5, SYS-12).
- Upstream BLOCK/DEGRADE governance is ignored by the consumer (SYS-4).

| Item | Findings |
|---|---|
| Archive a hashed raw snapshot for every extracted patch (outside git if needed) and commit a run manifest: game build, tool versions, script commit, output hashes | EXT-5, SYS-12, DRIFT-4 |
| Extract 1.5.x (current live) on the operator machine; record what fails to decode | DRIFT-1, DRIFT-8 |
| Enumerate every data table in the game's resource manifest. For each, record an explicit status (extracted / intentionally excluded with reason / not yet supported). This becomes the denominator for ENTITY COVERAGE. | EXT-4, EXT-9 |
| Replace the `×100` sync with a value-scale contract per property/modifier type; carry `property`, `modifierType`, `affixProperties`, `extraRolls`, `tiers2`, `specialAffixType` | EXT-2, LOSS-1, LOSS-2, EXT-7, DRIFT-6 |
| Carry passive structured stats (`property`, `downside`, `noScaling`, `requires`) and unique/set modifiers structurally, keyed by numeric ID | LOSS-3, LOSS-5 |
| Replace hand-authored core inputs (skills base damage/scaling, class per-level stats, base items, ailment constants) with extracted values, or label each family's provenance explicitly | EXT-3, LOSS-4, LOSS-6 |
| Make the Forge sync deterministic and idempotent: one env-configured source root, a manifest written into `data/` (source commit, bundle ID, patch, hashes), and a re-run that produces zero diff | EXT-1, SYS-6, DRIFT-2 |
| Make the consumer honour upstream manifest actions (BLOCK / DEGRADE / WARN) at load time | SYS-4, DOC-12 |

**Acceptance criteria**
- `data/` carries a machine-readable manifest naming the extractor commit, bundle ID, game version/build and per-file hashes. `patch_version` is never "unknown".
- Re-running the sync from the recorded source reproduces `data/` byte-for-byte (excluding the timestamp).
- A coverage report lists every game table and every exported family, with ENTITY / FIELD / RELATIONSHIP coverage percentages computed against named denominators. That report is regenerated in CI from committed artifacts.
- No stored affix value differs from the export after applying the declared scale contract; Added Health T1 = 5–15 and Strength values are correct.
- Families the upstream manifest marks BLOCK are not used for calculations.

**Required tests:** golden value tests sampling every modifier type against the raw export; a field-path survival test (export → `data/` → loader) that fails when a field disappears without a declared exclusion; a sync idempotency test; a manifest-enforcement test.

**Dependencies:** R0 (deployability). **Complexity:** XL. **Blocks production promotion:** YES.

---

## AUDIT-R2 — Schema and relationship integrity

**Objective:** every cross-domain reference resolves or is reported. Every persisted build is interpretable later.

**Why it matters:**
- 190 passive nodes carry the wrong mastery (REL-1).
- The skill-tree resolver covers 2,190 of 3,693 nodes (REL-4).
- Skill metadata collapses variants by name (REL-6).
- The export has dangling prerequisite edges and missing Warlock nodes (REL-2, EXT-6).
- Seeded affix rows lose class requirements and tags (REL-23).
- Saved builds have no data-version stamp (DB-3).

| Item | Findings |
|---|---|
| Derive mastery names from the export; regenerate and reseed passives | REL-1 |
| Generate skill-tree resolver data and frontend tree data from one source, keyed by tree ID and supporting multiple parents | REL-4, REL-6, REL-10, FE-10 |
| Add a referential-integrity validator in the extractor and the consumer (dangling IDs, duplicates, orphan trees, unresolved localization) as a gate | REL-2, EXT-6, REL-12, REL-16, REL-22 |
| Fix seeding so affix class requirements and tags survive; add an idempotent seed step to deploy | REL-23, DB-4 |
| Add server-set `data_version` / `patch` provenance columns to builds and import records | DB-3, DRIFT-3, IMP-6 |
| Replace silent fallbacks (`"Unknown"`, `or 0`, `except: pass`) on data paths with explicit degraded status | REL-24 |
| Run the migration chain on Postgres in CI and repair the broken downgrades | DB-5 |
| One canonical item-type vocabulary; derive ID maps from extracted enums and fail loudly on unknown IDs | REL-16, DRIFT-7 |

**Acceptance criteria**
- Zero dangling references across exported families, or each one is listed in a reviewed allowlist with a reason.
- Every mastery's passive list matches the export.
- Every allocatable skill node resolves in the backend resolver and the frontend tree, with parity enforced by a test.
- Every saved build records the data version it was created against.

**Required tests:** a referential-integrity suite; mastery-label tests; a skill-tree parity test (backend vs frontend vs export); a migration up/down on Postgres; a seed idempotency test.

**Dependencies:** R1. **Complexity:** L. **Blocks production promotion:** YES.

---

## AUDIT-R3 — Patch drift and change detection

**Objective:** a new Last Epoch patch must produce an automatic, reviewable report of what changed and what the extractor does not understand, before anything reaches production.

**Why it matters:**
- Extraction only runs on one Windows machine with a local game install (DRIFT-4).
- The validators detect only shrinkage (DRIFT-5).
- 1.4.7 and 1.5 were never extracted, and nothing flagged that (DRIFT-1, DRIFT-9).

| Item | Findings |
|---|---|
| Patch-diff report between consecutive extractions: added/removed/changed entities, fields and enum values | DRIFT-5 |
| Unknown-field / unknown-enum / unknown-table gate wired into the pipeline's run-all step (the existing 148-unknown diagnostic becomes a gate) | DRIFT-5, DRIFT-6, EXT-4 |
| Documented, reproducible operator procedure; a CI-runnable post-processing subset that runs from archived raw snapshots | DRIFT-4, DOC-10 |
| Replace hard-coded `D:\` defaults with one env-configured root in both repos | SYS-6, EXT-8 |
| A staleness check that compares the served data version with the latest known game version and raises an operational alert | DRIFT-1, DRIFT-3 |

**Acceptance criteria**
- Running the pipeline on two archived snapshots produces a deterministic diff report.
- Introducing an unknown enum value or new field in a fixture fails the gate.
- Production exposes its data version, and an alert fires when that version is behind the live game.

**Required tests:** patch-diff fixture tests; unknown-value gate tests; a path-configuration test on Linux.

**Dependencies:** R1. **Complexity:** L. **Blocks production promotion:** NO for current-state fixes, YES for any "current patch" claim.

---

## AUDIT-R4 — Import reliability

**Objective:** an imported build is classified EXACT / LOSSY / PARTIAL / UNSUPPORTED with per-field reasons, and never silently wrong.

**Why it matters:**
- Gear base IDs map through a sequential index, so imports come out silently wrong (IMP-4).
- Defaults are invented without disclosure (IMP-5).
- Most build state is never imported (IMP-7).
- No real-site fixture exists (IMP-8, TEST-3).

| Item | Findings |
|---|---|
| Correct base-item mapping via `(baseTypeID, subTypeID)`; report unresolved items rather than guessing | IMP-4, LOSS-4 |
| Remove invented defaults (class/level/mastery/rarity/unique guesses), or mark them experimental and list them in the response | IMP-5 |
| Emit and display an import coverage report per field, using the contract in report 09 | IMP-7 |
| Consented, user-captured real payload fixtures (via the bookmarklet) plus field-level assertions; 403 / challenge-page tests | IMP-8, TEST-3 |
| Decide the support status of Maxroll and LE Tools server-side fetches based on legitimate available representations; no evasion of upstream protection | IMP-2, IMP-10 |
| Define the anonymous ownership model (edit token) so import → edit → share has no dead ends | FE-5, API-5 |

**Acceptance criteria**
- Every import response includes a coverage classification with reasons.
- The golden sidecar fixture contains no wrong base names.
- Real captured fixtures pass with field-level assertions.

**Required tests:** mapping tests against extracted item data; coverage-report tests; negative tests for each upstream failure mode.

**Dependencies:** R0, R2. **Complexity:** L. **Blocks production promotion:** YES for advertising import.

---

## AUDIT-R5 — Test and certification gates

**Objective:** a green pipeline must mean something specific, and nothing reaches production without one.

**Why it matters:**
- CI is red in both repos (TEST-1).
- `main` deploys without CI (INFRA-2).
- 321 skips point at deleted files, real-bundle tests always skip, and Postgres contract tests never run (TEST-2).
- Frontend tests and lint never run in CI (TEST-4, FE-11).
- Calculation tests only check the implementation against itself (CALC-16).

| Item | Findings |
|---|---|
| Deploy depends on CI success; required checks on `main` | INFRA-2 |
| Restore green CI in both repos without lowering expectations; remove `-x` so all failures are visible | TEST-1, RT-2, RT-6, RT-7 |
| Re-point or retire tests that skip on deleted files; add a Postgres service; run the real committed bundle in CI | TEST-2 |
| Add frontend vitest, lint and build jobs; run the full extractor suite (minus host-only steps) | TEST-4, FE-11, RT-8 |
| Extraction certification job: coverage report (R1) + referential integrity (R2) + unknown-value gate (R3), with thresholds that block merges | TEST-2, EXT-10 |
| Report full-suite results (not focused subsets) in release documents | DOC-1, DOC-2 |

**Acceptance criteria**
- `main` cannot deploy on a red or missing CI result.
- The skip count is explained by a reviewed list.
- The extraction certification job exists and blocks merges.

**Dependencies:** R0. **Complexity:** M. **Blocks production promotion:** YES.

---

## AUDIT-R6 — Product consumption trust

**Objective:** every number shown to a user carries an honest trust label. Unsupported mechanics never look trusted.

**Why it matters:**
- 0 of 38 calculation domains are trusted (report 13).
- Skill base damage is hand-calibrated and contradicts extracted data by a median of 24.6× (CALC-1).
- There are 9 divergent armor implementations (CALC-4).
- DPS and EHP responses carry no trust fields (CALC-15).
- A mock Monte Carlo page is presented as a real simulation (DEAD-2).
- The 'trusted data' pages contradict upstream readiness flags (DOC-5, SYS-5).

| Item | Findings |
|---|---|
| Per-metric trust/provenance labels in API responses and UI; "unavailable" instead of 0 | CALC-15, FE-7, FE-8 |
| Declare one canonical engine per formula; label or retire the others | CALC-4, CALC-5, DEAD-1, DEAD-3 |
| Source skill damage, effectiveness and ailment constants from extracted data | CALC-1, CALC-2, CALC-3 |
| Remove fabricated stat fallbacks; fix the armor % mapping; wire spec trees and conversions into user paths | CALC-6, CALC-7, CALC-14 |
| Return "unsupported" for minion DPS and other unmodelled mechanics | CALC-11, CALC-12, CALC-13 |
| Gate or explicitly approve public exposure of the v2 trust/debug surfaces, and fix their fetch paths | SYS-5, FE-3, DOC-5 |
| Correct the public accuracy and limitation docs | CALC-17, DOC-9, DOC-11 |

**Acceptance criteria**
- No API response containing a computed metric lacks a trust classification.
- Each formula has one implementation, cited to a source, with an independent-ground-truth test (in-game capture or official documentation).

**Dependencies:** R1, R2. **Complexity:** XL. **Blocks production promotion:** YES for any accuracy claim.

---

## AUDIT-R7 — Operational hardening

**Objective:** failures are visible, attributable and recoverable.

| Item | Findings |
|---|---|
| Readiness health check (DB, Redis, data version); error tracking; external uptime monitor | OBS-2 |
| Structured import-failure records with replay payloads; dedupe and aggregation | OBS-1 |
| ProxyFix / correct client IP for rate limiting; fail loudly when Redis is missing | API-7 |
| Cache v2 repositories per process or gate them; remove the duplicate mount | API-3 |
| OAuth state/PKCE; token delivery off the query string; CSP | SEC-3, SEC-6, API-10 |
| Security-critical dependency patch upgrades only; Node LTS move | SEC-4, SEC-8, RT-4 |
| Pass HTTPException through the error handler; nested gear validation | API-9, API-8 |
| Per-service deploy hooks; memory sizing on the starter plan; env contract reconciliation | INFRA-4, INFRA-5 |
| Classify each dormant package as live / experimental / archived (no deletion required to close this) | SYS-13, DEAD-4 to DEAD-9 |

**Acceptance criteria**
- An import failure can be answered for WHAT / WHERE / WHY / which upstream / app / extractor / data version / isolated-vs-systemic / replayable from the stored record alone.

**Dependencies:** R0. **Complexity:** M. **Blocks production promotion:** Partially (OBS-1 and API-7 do).

---

## What must be true before anyone can say "The Forge extracts 100% of the Last Epoch data it needs"

1. **A denominator exists.** The game's own table manifest for the current patch is enumerated, and every table has a recorded status (R1).
2. **Entity coverage** is 100% for every table marked "needed", computed in CI from archived raw input (R1, R5).
3. **Field coverage:** every source field is either carried through to `data/` and the loaders, or listed with a reviewed exclusion reason. A test fails on any undeclared drop (R1).
4. **Relationship coverage:** zero unresolved references outside a reviewed allowlist (R2).
5. **Patch currency:** the served data version equals the live game patch, or the gap is shown to users (R3).
6. **Change detection:** new fields, enums and tables in a patch fail a gate rather than passing silently (R3).
7. **Reproducibility:** the dataset can be regenerated from an archived raw snapshot by a documented procedure, and the result matches the committed hashes (R1, R3).
8. **Semantic coverage** is tracked separately. "We have the data" is not the same as "we model the mechanic". Semantic coverage is currently 0/8,711 stable-calculable records (EXT-10), and it must never be presented as extraction completeness.
