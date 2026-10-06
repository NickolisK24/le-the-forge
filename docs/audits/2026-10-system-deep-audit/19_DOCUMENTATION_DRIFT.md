# 19 — Documentation Drift (Phase 17)

Audit date: 2026-10-06
Baseline: `le-the-forge` `main` @ `1efcef76`; `last-epoch-data` @ `73e2ab0`.
Rule applied: neither the document nor the code is presumed correct. Each item states what was measured.
Note: the remote `dev` branch is 413 commits ahead of `main` (last commit 2026-05-29, `docs: audit trusted data promotion readiness`, README modified). Some drift below may already be corrected on `dev`; production serves `main`.

## Measured baselines

| Fact | Value | How measured |
| --- | --- | --- |
| Backend tests collected | 11,800 | `cd backend && python -m pytest tests/ --collect-only -q` (snapshot, scratch venv) |
| Backend test files | 337 | `find backend/tests -name 'test_*.py' \| wc -l` |
| Backend full run | **11,415 passed, 379 skipped, 7 errors** (438 s). 6 errors = `ModuleNotFoundError: psycopg` in `tests/test_deployment_readiness.py` CORS tests because unpinned SQLAlchemy resolved to 2.1.3, whose default `postgresql://` driver is psycopg v3 (not in `requirements.txt`); 1 teardown error `sqlite3.ProgrammingError: Cannot operate on a closed database` in `tests/test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes`. Scratch venv was Python 3.13 (Render pins 3.11) | `python -m pytest tests/ -q -p no:cacheprovider` on `git archive HEAD` snapshot |
| Frontend tests | 916 tests / 49 files: **899 passed, 17 failed (2 files)** | `npx vitest run` on snapshot |
| Failing frontend files | `src/__tests__/components/navigation.test.tsx` (11: GlobalSearch ×10, Sidebar "renders all 7 nav items"), `src/__tests__/integration/layout.test.tsx` (6: GlobalSearch open/close/search) | same |
| Test coverage tooling | none (no `pytest-cov`, no `--cov`, no vitest coverage config) | `grep -rn "cov" backend/requirements.txt backend/pytest.ini frontend/vitest.config.ts .github/workflows` |
| Registered blueprints | 29 (`app/__init__.py:231-259`; `experimental_bp` registered twice) | code read |
| URL rules | 172 total; 84 unique non-experimental paths; 83 experimental rules | `app.url_map` dump |
| Version strings | `VERSION` 0.8.0; `package.json` 0.3.0; `frontend/package.json` 0.1.0; CHANGELOG top 0.8.1; release branch naming "v2.5" | file reads |
| Runtime data patch | `data/version.json`: `patch_version: "unknown"`, `synced_at: 2026-04-26T01:32:48Z`, only `data\items\affixes.json` updated | file read |
| Upstream export patch | `last-epoch-data/exports_json/metadata.json`: 1.4.6 build 22986002, generated 2026-05-06 | file read |
| Affix counts | `data/items/affixes.json` 1,228; upstream `exports_json/affixes.json` 1,112 equipment + 115 idol = 1,227; `docs/generated/v2_affix_bundle.json` 1,098 (129 excluded upstream) | python count |

---

## Discrepancies

### DOC-1 — Test counts are stale in every top-level document (P2)
- **DOCUMENTATION SAYS:** README badge and text "10,865 passing / 377 skipped", "10,865 tests across 264 test files" (`README.md:6,15,30,74,183,261`); `backend/ARCHITECTURE.md:56` "9900+ tests"; `ACCURACY_AUDIT.md:179` "10664 passed, 377 skipped"; `docs/release/V2_5_MAIN_RELEASE_READINESS.md:99-101` "11477 passed, 323 skipped".
- **CODE ACTUALLY DOES:** 11,800 collected across 337 files (11,477 + 323 = 11,800, so the release doc matches the collection count). A fresh install today yields 11,415 passed / 379 skipped / 7 errors (see baselines) — the suite is no longer green on a clean `pip install -r requirements.txt`. README/ARCHITECTURE numbers are from April.
- **RISK:** Readers cannot tell which document is current; test-count claims are used as a quality signal on the public README.
- **ACTION:** Generate the count in CI (already printed by `ci.yml` "Publish test count") and reference the CI summary instead of hard-coding numbers; mark April numbers as historical.

### DOC-2 — "Tests passing" claims omit a red frontend suite that CI never runs (P1)
- **DOCUMENTATION SAYS:** README "Testing | pytest (10,865 tests), TypeScript strict mode, Vitest" (`README.md:74`); release doc "PASS: frontend focused v2.5 page tests, 7 files, 43 tests" and "READY for main" (`V2_5_MAIN_RELEASE_READINESS.md:85-88,118`).
- **CODE ACTUALLY DOES:** Full `vitest run` = 17 failed / 899 passed (2 files). `.github/workflows/ci.yml` runs only backend pytest, `tsc --noEmit`, and `flask validate-data`; no vitest, eslint or `vite build` step.
- **RISK:** Frontend regressions in navigation/GlobalSearch ship unnoticed; "ready" claims rest on a hand-picked subset.
- **ACTION:** Add `npm test` to CI as a required check; fix or quarantine the 17 failures with a tracked issue; release docs must state full-suite results, not focused subsets.

### DOC-3 — Patch version claims contradict the runtime data stamp and upstream (P1)
- **DOCUMENTATION SAYS:** "Game data synced to: patch 1.4.3, Season 4 (last sync 2026-04-21)" (`README.md:14,226`); "Last Epoch patch: 1.4.3, Season 4 (from `data/version.json`)" and "last modified 2026-04-21" (`docs/KNOWN_LIMITATIONS.md:45-46`); ACCURACY_AUDIT title "Patch 1.4.3".
- **CODE ACTUALLY DOES:** `data/version.json` says `"unknown"`, synced 2026-04-26. `/api/health` returns `patch_version` from that file → `"unknown"` (`backend/app/routes/health.py:37-46`). `/api/version` returns `CURRENT_PATCH` env default `"1.4.3"` (`config.py:28`; not set in `render.yaml`). Upstream is 1.4.6 since 2026-05-05; v2 bundles in `docs/generated/` carry 1.4.6 provenance.
- **RISK:** Two production endpoints disagree on the patch; users and maintainers cannot tell which game version drives calculations; the documented provenance source (`data/version.json`) does not contain the documented value.
- **ACTION:** Make `data/version.json` the single source; fail `flask validate-data` when `patch_version == "unknown"`; derive `/api/version` from the same file; re-sync or explicitly label the planner data as pre-1.4.6.

### DOC-4 — Version numbers disagree across five sources (P2)
- **DOCUMENTATION SAYS:** CHANGELOG latest `[0.8.1] -- 2026-04-21` and ROADMAP "Phase 9 -- Deploy & Launch (v0.8.1)"; README badge/text "v0.8.0"; release work is named "v2.5" (`docs/release/V2_5_MAIN_RELEASE_READINESS.md`).
- **CODE ACTUALLY DOES:** `VERSION` = 0.8.0 (served by `/api/health` and the frontend badge via `vite.config.ts:10`); root `package.json` 0.3.0; `frontend/package.json` 0.1.0. CHANGELOG/ROADMAP have zero mentions of v2/v2.5/trusted data (`grep -c "v2\|trusted" CHANGELOG.md ROADMAP.md README.md ARCHITECTURE.md` → 0 each) although ~25 v2.5 PRs (#355–#372) merged to `main` on 2026-05-12..14.
- **RISK:** Production cannot be tied to a release; "v2.5" is a program label with no corresponding app version; changelog gives users no record of the trusted-data features now live.
- **ACTION:** Define one version policy (app semver in `VERSION`, program phase names separate), bump `VERSION`, add CHANGELOG entry for the v2.5 merge, align `package.json` versions or mark them non-authoritative.

### DOC-5 — Extraction-trust status: Forge UI says "rely on", extractor says not ready for public visibility (P1)
- **DOCUMENTATION SAYS (last-epoch-data):** `README.md` "Current Extraction Baseline": `trusted_public_visibility_ready=false`, `runtime_consumption_ready=false`, affix domain `remain_quarantined`, scoped certification `forge_safe_subset_only`; `docs/generated/forge_safe_affix_bundle.json` `forbidden_usage`: "Do not treat this artifact as production integration".
- **CODE ACTUALLY DOES (le-the-forge):** Production SPA routes `/trusted-data`, `/trusted-data/support`, `/debug/v2*` are unconditional (`frontend/src/App.tsx:251-276`, made so by commit `9f38e8e` "fix: expose v2 debug routes"); page copy says "Today, users can rely on v2 trusted data for inspection, source context, support status, provenance…" (`frontend/src/pages/TrustedDataExplanationPage.tsx`); `/api/experimental/v2/affixes` serves the Forge-safe-derived bundle with no config gate (`backend/app/routes/experimental.py:197-238`).
- **RISK:** The public site labels data "trusted" that the data owner's governance explicitly withholds from public trust; the word "trusted" means different things in the two repos.
- **ACTION:** Either (a) gate v2 routes/pages behind a config flag until upstream grants `trusted_public_visibility_ready`, or (b) record an explicit cross-repo decision that "trusted data" in the Forge UI means "provenance-traced display", and rename the UI term. Add a shared glossary to `FORGE_DATA_CONTRACT.md`.

### DOC-6 — Release-readiness doc says debug surfaces are not production-exposed; the next commit exposed them (P2)
- **DOCUMENTATION SAYS:** "Existing pre-v3 readiness and v2 debug surfaces remain documentation/debug-only and are not production-consumed" (`V2_5_MAIN_RELEASE_READINESS.md:109`); `docs/FORGE_MIGRATION_TRACKER.md` (2026-05-11) "No public API response includes sidecar data", "No frontend behavior changes", "No affix bundle family is generated or consumed".
- **CODE ACTUALLY DOES:** `9f38e8e` (after the readiness doc `eb59c93`) moved the v2 routes out of the `IS_DEV` block (`App.tsx:263-276`); 83 experimental API rules are publicly routable; `docs/generated/v2_affix_bundle.json` was generated 2026-05-12 and is served. "Not production-consumed" remains true for planner math (verified: only `routes/experimental.py` imports `app.repositories.v2`; no route/service imports `planner_adapters`).
- **RISK:** Readiness sign-off predates the change that altered the production surface; the tracker is the self-described "living" document but is three days and ~25 PRs stale.
- **ACTION:** Re-issue the readiness note after `9f38e8e` with the exposure decision recorded; update the tracker's "Current Program State" and "Not Activated" lists; require tracker update in the PR template for any route exposure change.

### DOC-7 — V2_CHECKPOINTS says work stops at Checkpoint 1 (P3)
- **DOCUMENTATION SAYS:** "This session stops at Checkpoint 1 after Phase 0 policy docs and Phase 1 inventory reports are complete. Phase 2 must not begin until the inventory is reviewed." (`docs/V2_CHECKPOINTS.md:41-42`).
- **CODE ACTUALLY DOES:** Contract layer (`app/data_contracts/`), repositories, normalization, planner adapters, API contract, frontend pages and a "v2.5 main release" all exist on `main`.
- **RISK:** No record of which checkpoints were reviewed/approved; the gate process the doc defines is unverifiable.
- **ACTION:** Convert the checkpoint table into a status ledger with reviewer, date, PR for each checkpoint.

### DOC-8 — V2_SHIP_CRITERIA isolation rule vs actual exposure (P2)
- **DOCUMENTATION SAYS:** "Experimental diagnostics are isolated from stable planner, crafting, stat aggregation, simulation, and reference routes" and "Validation failures are visible…not silently swallowed" (`docs/V2_SHIP_CRITERIA.md:11-14`).
- **CODE ACTUALLY DOES:** Isolation from calculation paths holds. But experimental routes share the production app, rate limits and `/api` prefix (`/api/experimental/*`), and the API reference states "All endpoints are prefixed with `/api`" without listing them. `entrypoint.sh:13-14` swallows seed failures (`2>/dev/null || echo skipped`).
- **RISK:** Moderate; criteria are met for math isolation, not for surface isolation.
- **ACTION:** Clarify whether "isolated" includes public routing; if yes, gate experimental blueprints by config.

### DOC-9 — API reference: accurate for stable routes, silent on experimental, misleading on admin auth (P1)
- **DOCUMENTATION SAYS:** 77 documented paths under "All endpoints are prefixed with `/api`" (`docs/api_reference.md:3`); "## Admin" section lists `PATCH /api/admin/affixes/<affix_id>` "Update a single affix definition. Rate limit: 30/min" (`:371-376`); `ARCHITECTURE.md` blueprint table lists 25 blueprints.
- **CODE ACTUALLY DOES:** All 77 documented paths exist (diff of doc vs `url_map` → 0 missing). Undocumented: `/api/affixes/catalog`, `/api/affixes/catalog/<id>`, `/api/affixes/catalog/summary`, `/api/import/let/json`, `/api/ref/blessings`, `/debug/forge-safe-affixes`, and all 83 `/experimental/*` + `/api/experimental/*` rules. ARCHITECTURE omits `affixes_bp`, `debug_bp`, `experimental_bp`. The "Admin" endpoints have **no authentication decorator** (`backend/app/routes/admin.py:41,68-70`), and the PATCH writes `data/items/affixes.json` on the server.
- **RISK:** The "Admin" heading implies protection that does not exist; a public write path to production game data is undocumented as such.
- **ACTION:** Add `@admin_required` (or remove the route from production) and document auth on every write endpoint; add the v2 experimental surface to the API reference under its own prefix.

### DOC-10 — Data-flow documentation assumes three different workspace layouts (P2)
- **DOCUMENTATION SAYS:** README "Game data is synced from Last Epoch exports using `scripts/sync_game_data.py`" (`README.md:226`); `.gitignore:61` "Raw game data — clone separately, run scripts/sync_game_data.py"; `docs/WORKSPACE_HEALTHCHECK.md` and `docs/FORGE_MIGRATION_TRACKER.md:5-6` describe sibling repos under `D:\Forge\`; `docs/LOCAL_DEVELOPMENT.md:36-130` uses `D:\Forge\le-the-forge`; last-epoch-data `patch_update_guide.md` "Step 10 — Sync Consumers: Downstream projects: git pull".
- **CODE ACTUALLY DOES:** `sync_game_data.py:21` needs `last-epoch-data/` **nested inside** `le-the-forge`; `affix_diagnostic_consumer.py:16` needs it as a **sibling**; 13 tracked code files default to `D:\Forge\...`. "git pull" in a downstream repo does nothing — the Forge has no submodule or runtime link; data moves only via manual script run + commit. `.env.example` documents `DATA_BUNDLE_DIR`; code reads `FORGE_DATA_BUNDLE_DIR`.
- **RISK:** Patch-day refresh is not reproducible by anyone without the original Windows workstation; the documented "sync consumers" step is a no-op.
- **ACTION:** Pick one layout (recommend sibling + a single `FORGE_LED_ROOT` env var), remove `D:\` defaults, rewrite patch_update_guide Step 10 with the real Forge commands (`sync_game_data.py`, `generate_tree_data.py`, `report_v2_*`, `validate-data`, commit).

### DOC-11 — "Data confidence"/"verified" labels rest on an owner-provided spec, not extraction (P2)
- **DOCUMENTATION SAYS:** `ACCURACY_AUDIT.md:7-10` audited constants "against the Last Epoch 1.4.3 specification provided by the owner"; fixed sites are tagged `# VERIFIED: 1.4.3 spec §…` (`ACCURACY_AUDIT.md:176`); README presents a confidence table with percentages (`README.md:240-250`, e.g. "Skill base damage (34 skills) | 70-80%").
- **CODE ACTUALLY DOES:** Constants match the audit's fixed values (`constants/combat.py:13` crit 2.0, `constants/defense.py:30` 0.70, `game_data/constants.json:21` armor_cap 0.85, `domain/block.py:13` 0.85) — so the fix claims are true. But "VERIFIED" marks trace to a prose spec, not to `last-epoch-data` extraction, and the confidence percentages have no computation in code.
- **RISK:** "Verified" in code comments and "trusted" in v2 UI and "certified" in last-epoch-data are three unrelated trust vocabularies.
- **ACTION:** Re-label `# VERIFIED: 1.4.3 spec` as `# SPEC-SOURCED` (or equivalent) unless backed by an extraction report; publish the confidence-percentage method or drop the numbers.

### DOC-12 — Extraction completeness claims (P2)
- **DOCUMENTATION SAYS:** last-epoch-data README: "latest validated extraction target is Last Epoch 1.4.6… Consumer-critical outputs passed bootstrap and export validation"; `data_bundle/manifest.json` action summary blocks `affixes, affix_tiers, affix_eligibility, affix_tags` and degrades `uniques, idols, blessings, passives, passive_trees, skills, skill_trees, class_mastery_stats, enemy_profiles, corruption_scaling`; `FORGE_DATA_CONTRACT.md:283` weaver tree "Keep planned unless the audit identifies a live runtime consumer".
- **CODE ACTUALLY DOES:** Forge production loads all of those families from its own pre-1.4.6 `data/` copies at startup (`pipeline.py:45-57`), including `data/progression/weaver_tree.json` (a live runtime consumer the contract says should not yet exist). Enemy profiles are documented in Forge as "community-sourced approximations" (`KNOWN_LIMITATIONS.md:28`). Raw preservation (`patch_versions/`) holds 1.3.7.1 and 1.4.3 only — no 1.4.6 snapshot for the "validated" target.
- **RISK:** Upstream "validated" and "blocked/degraded" status never reaches the consumer; Forge consumes blocked families as authoritative inputs.
- **ACTION:** Have `flask validate-data` read the bundle manifest and fail/warn for families marked `block`/`degrade`; add a 1.4.6 raw snapshot or document why not.

### DOC-13 — README feature/structure claims (P3)
- **DOCUMENTATION SAYS:** "25 Flask blueprints", "11 orchestration services", "264 test files", `data/items` "1,160+ affixes" (`README.md:171-183,222`); Electron "Desktop app wrapper" (`README.md:203`).
- **CODE ACTUALLY DOES:** 29 blueprint registrations (28 blueprints); 13 service modules plus `services/importers/`; 337 test files; 1,228 affixes; Electron production mode cannot start (no PyInstaller artifact; backend not in `electron-builder` `files`; `FLASK_ENV=production` requires Discord secrets) — ROADMAP correctly lists packaging as future work.
- **RISK:** Low; cosmetic but compounds trust erosion.
- **ACTION:** Regenerate structure counts or drop them.

### DOC-14 — Deployment docs vs workflows (P2)
- **DOCUMENTATION SAYS:** CHANGELOG/ROADMAP "CI-driven deploys via Render deploy hook" and "CI expanded to run on PRs into both dev and main"; `docs/deployment.md:122-129` one hook for `epochforge-api`, "repeat … for both services".
- **CODE ACTUALLY DOES:** `deploy.yml` fires on every push to `main` independently of CI (no `needs:`/`workflow_run`), so "CI-driven" means "push-driven". Only one hook exists; `render.yaml` `autoDeploy: false` for the frontend → frontend deploy path is UNKNOWN/manual. `render.yaml` runs only `flask db upgrade`; Docker `entrypoint.sh` additionally seeds. `backend/Procfile` is an unused third deploy definition.
- **RISK:** A red build can deploy; frontend and API can drift in production.
- **ACTION:** Gate deploy on CI success; add the frontend hook or document the manual step; remove `Procfile` or mark legacy.

### DOC-15 — ARCHITECTURE Redis section incomplete (P3)
- **DOCUMENTATION SAYS:** Redis key table (`ARCHITECTURE.md:137-155`) lists cache keys only.
- **CODE ACTUALLY DOES:** Also `forge:job:<id>` (job state, `utils/jobs.py:29`), `forge:meta:skills|class_dist|affixes`; `ref:*` keys are not versioned and are never invalidated on data reload/admin edit.
- **RISK:** Stale reference data for up to 24 h after a data deploy; undocumented job-state dependency on Redis.
- **ACTION:** Document job keys; include `DATA_VERSION` or data hash in `ref:*` keys.

### DOC-16 — docs/data_models.md (no material drift)
- 11 documented models match the 11 `db.Model` classes in `backend/app/models/__init__.py` (`users`, `builds`, `build_skills`, `votes`, `craft_sessions`, `craft_steps`, `item_types`, `affix_defs`, `passive_nodes`, `import_failures`, `build_views`). Recorded for completeness.

### DOC-17 — docs/FULL_REPO_AUDIT.md (2026-05-11) partially superseded (P3)
- Its structure section is accurate for `main`, but predates v2/v2.5 (no mention of `app/repositories/v2`, `app/normalization/v2`, `app/planner_adapters/v2`, experimental v2 routes, or production-exposed debug pages).
- **ACTION:** Mark as historical and point to this audit set.

---

## Summary table

| ID | Sev | Document(s) | One-line drift |
| --- | --- | --- | --- |
| DOC-1 | P2 | README, backend/ARCHITECTURE, ACCURACY_AUDIT | test counts 9,900/10,664/10,865 vs 11,800 collected |
| DOC-2 | P1 | README, V2_5 release readiness | frontend suite 17 failing; CI never runs vitest |
| DOC-3 | P1 | README, KNOWN_LIMITATIONS | patch "1.4.3 from data/version.json" vs file says "unknown"; upstream 1.4.6 |
| DOC-4 | P2 | VERSION, CHANGELOG, ROADMAP, package.json | 0.8.0 / 0.8.1 / 0.3.0 / 0.1.0 / "v2.5"; v2.5 missing from changelog |
| DOC-5 | P1 | TrustedData page vs last-epoch-data README | "users can rely on trusted data" vs `trusted_public_visibility_ready=false` |
| DOC-6 | P2 | V2_5 readiness, FORGE_MIGRATION_TRACKER | "not production-exposed" vs `9f38e8e` exposing routes |
| DOC-7 | P3 | V2_CHECKPOINTS | stops at checkpoint 1 vs v2.5 shipped |
| DOC-8 | P2 | V2_SHIP_CRITERIA | surface isolation unmet |
| DOC-9 | P1 | api_reference, ARCHITECTURE | "Admin" write endpoint unauthenticated; 89 routes undocumented |
| DOC-10 | P2 | README, WORKSPACE_HEALTHCHECK, LOCAL_DEVELOPMENT, patch_update_guide, .env.example | three workspace layouts; "git pull" sync is a no-op |
| DOC-11 | P2 | ACCURACY_AUDIT, README | "VERIFIED" = owner spec, not extraction |
| DOC-12 | P2 | last-epoch-data README/manifest/FORGE_DATA_CONTRACT | blocked/degraded families consumed by Forge runtime |
| DOC-13 | P3 | README | structure counts, Electron |
| DOC-14 | P2 | CHANGELOG, ROADMAP, deployment.md | deploy not gated on CI; frontend deploy undefined |
| DOC-15 | P3 | ARCHITECTURE | Redis jobs/invalidation undocumented |
| DOC-16 | — | data_models | no drift |
| DOC-17 | P3 | FULL_REPO_AUDIT | predates v2 |

## Commands used
```
grep -nE "tests|passing|patch|version" README.md backend/ARCHITECTURE.md ACCURACY_AUDIT.md docs/KNOWN_LIMITATIONS.md
for f in <docs>; do git log -1 --format='%ad %h' --date=short -- $f; done
python -m pytest tests/ --collect-only -q ; python -m pytest tests/ -q -p no:cacheprovider   (snapshot)
npx vitest run   (snapshot)
create_app('testing').url_map dump; grep -oE '^### `(GET|POST|PUT|PATCH|DELETE) [^`]+' docs/api_reference.md; comm -3
git show 9f38e8e --stat; sed -n 240,290p frontend/src/App.tsx
gh api repos/NickolisK24/le-the-forge/compare/main...dev
cat data/version.json last-epoch-data/exports_json/metadata.json last-epoch-data/data_bundle/manifest.json
grep -n "BASE_CRIT_MULTIPLIER\|ARMOR_NON_PHYSICAL_EFFECTIVENESS\|armor_cap\|BLOCK_CHANCE_CAP" backend/app/...
```
