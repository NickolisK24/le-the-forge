# The Forge / EpochForge — 2026-10 System Deep Audit (Combined Reports)

Audit date: 2026-10-06. This file concatenates reports 00–20 in order. The machine-readable findings are in AUDIT_EVIDENCE.json.

## Contents
- 00_EXECUTIVE_SUMMARY
- 01_SYSTEM_MAP
- 02_RUNTIME_AND_BUILD_HEALTH
- 03_EXTRACTION_ARCHITECTURE
- 04_EXTRACTION_COVERAGE_MATRIX
- 05_FIELD_LOSS_REPORT
- 06_RELATIONSHIP_INTEGRITY
- 07_PATCH_DRIFT_REPORT
- 08_LAST_EPOCH_TOOLS_IMPORT_FORENSICS
- 09_BUILD_IMPORT_CONTRACT
- 10_DATABASE_AUDIT
- 11_API_BACKEND_AUDIT
- 12_FRONTEND_PRODUCT_AUDIT
- 13_CALCULATION_TRUST_MATRIX
- 14_TEST_SUITE_AUDIT
- 15_OBSERVABILITY_AND_OPERATIONS
- 16_INFRASTRUCTURE_AUDIT
- 17_SECURITY_AND_DEPENDENCY_AUDIT
- 18_DEAD_CODE_AND_ARCHITECTURAL_DRIFT
- 19_DOCUMENTATION_DRIFT
- 20_PRIORITIZED_REMEDIATION_ROADMAP


---

<!-- FILE: 00_EXECUTIVE_SUMMARY.md -->

# 00 — Executive Summary: 2026-10 System Deep Audit

**Audit date:** 2026-10-06
**Systems audited:**

| Repository | Ref | Date | Role |
|---|---|---|---|
| `le-the-forge` | `main` @ `1efcef7` | 2026-05-14 | Production app: Flask API, React SPA, committed game data |
| `last-epoch-data` | `main` @ `73e2ab0` | 2026-05-31 | Private extractor: IL2CPP/Unity extraction, exports, data bundle |
| `le-parser` | `5135ce4` | 2026-03-26 | Archived JS parser; only referenced by a dangling gitlink |

**Method:**
- 10 parallel investigations covered phases 0–17, each producing reports 01–19.
- Every P0 and most P1 findings were independently re-verified against code or data before inclusion.
- All findings are in `AUDIT_EVIDENCE.json`: 140 findings, after folding duplicates.

**Not observed:**
- Live production: `epochforge.gg`, `api.epochforge.gg` and `lastepochtools.com` were unreachable from the audit environment because of its own egress proxy. These responses are not the sites' own responses.
- The Render dashboard.
- The `dev` branch, which is 413 commits ahead of `main`, except where stated.

No code, data, configuration, branch or production system was changed. The only tracked-file additions are the files in this directory.

Non-tracked side effects of running diagnostics:
- gitignored `frontend/node_modules/` and `frontend/dist/` (from `npm ci` / `npm run build`);
- gitignored `__pycache__/` files;
- `FETCH_HEAD` updated by a read-only `git fetch origin dev`.

`<scratch>` in the reports refers to the auditor's ephemeral working directory, which held virtualenvs, analysis scripts and scratch copies of data and migrations. It is not preserved. Every command needed to reproduce a result is listed in the relevant report.

---

## Platform verdict

# **D — FOUNDATION UNTRUSTWORTHY / REBUILD CORE AREAS**

The extractor repository holds a credible, directly-extracted 1.4.6 export for the core domains. The experimental v2 bundles regenerate record-for-record from it.

None of that reaches users intact. The production path rebuilds and corrupts it:
- The path is `last-epoch-data exports` → manual `scripts/sync_game_data.py` → committed `data/` → hand-authored engine tables → API → UI.
- It serves a 1.4.3-era snapshot stamped `patch_version: "unknown"`, while the game is on 1.5.x Season 5.
- Affix tier values are stored at 100× (EXT-2, LOSS-1).
- 190 of 541 passive nodes carry the wrong mastery (REL-1).
- Skill damage comes from a hand-calibrated table that contradicts the extracted values by a median of 24.6× (CALC-1).
- Anyone on the internet can rewrite the served affix data (SYS-1).
- The repository as committed cannot be rebuilt and booted against Postgres today (INFRA-1).

The sync/consumption layer and the calculation layer need rebuilding on top of the extractor. The extractor needs extension, preservation and gating, not replacement.

## Grades

| Area | Grade | Basis (finding IDs) |
|---|---|---|
| Extraction completeness | **D** | 19 game tables never extracted, weaver tree dropped (EXT-4); actors 23.4%; quests consumed 2/147; 1.4.7 and 1.5 never extracted (DRIFT-1) |
| Extraction correctness | **D** | Upstream export largely direct (`extractionConfidence: direct`), but has 19–23 garbage edges, 6 missing Warlock nodes and an undecoded enum (REL-2, EXT-6, DRIFT-6). The production sync adds 100× scaling and mastery swaps (EXT-2, REL-1). |
| Relationship integrity | **D** | Mastery labels (REL-1); skill-tree resolver 2,190/3,693 nodes (REL-4); name-keyed collisions (REL-6); timeline→monster-mod 54/453 = 11.9% |
| Patch resilience | **F** | A season behind; extraction possible on one Windows machine only; no gating change detection (DRIFT-1/4/5) |
| Importer reliability | **F** | LE Tools URL fetch fails 100% in production; JSON path maps gear to wrong bases; no real-site fixtures (IMP-1/2/4/8) |
| Data-model integrity | **C** | Single linear Alembic head; models match migrations except 5 server defaults. But: no provenance on builds, build delete fails with a 500, Postgres-only chain untested in CI (DB-1/3/5) |
| Calculation trust | **F** | 0/38 domains trusted, 13 known incorrect, 9 armor implementations, no trust labels on outputs (CALC-1..18) |
| Test confidence | **D** | 11,415 backend tests pass locally, but CI is red for 261 dev runs, `main` deploys without CI, 321 skips target deleted files, and HTTP is fully mocked (TEST-1/2/3, INFRA-2) |
| Production reliability | **D** | The next deploy will most likely fail (INFRA-1); 4 workers on a 512 MB plan; in-process jobs; no CI gate |
| Observability | **D** | Discord alert exists but lacks version, stage and upstream data; liveness-only health check; no error tracking or metrics (OBS-1/2, IMP-3) |
| Security | **D** | Anonymous game-data write (SYS-1), IDOR on builds (API-4/5), private builds readable (API-6), OAuth without state (SEC-3), 10 dependency advisories. No SSRF, deserialization or injection found. |
| Frontend usability | **D** | Import → edit → share dead-ends (FE-4/5); trust pages broken on the static host (FE-3); fallbacks render an outage as an empty site (FE-8) |

---

## The ten questions

**1. Can we trust the current extracted Last Epoch dataset?** — **PARTIALLY**
- The `last-epoch-data` 1.4.6 export is partially trustworthy. It was extracted directly from game assets and v2 bundles regenerate from it exactly. However, it has known decode defects (EXT-6, REL-2, DRIFT-6), is a season old, and cannot be regenerated because the 1.4.6 raw inputs are not preserved (EXT-5).
- The dataset production actually serves (`le-the-forge/data/` plus hand-authored engine tables) is **not trustworthy** (EXT-1, EXT-2, EXT-3, REL-1, CALC-1).

**2. Can we prove extraction completeness?** — **NO.**
- There is no denominator: the game's table manifest is not enumerated against exports.
- Validators check only that counts don't shrink.
- Semantic coverage is 0/8,711 stable-calculable records (EXT-4, EXT-10, DRIFT-5).
- The upstream completeness audit double-counts idol affixes (1,227 vs 1,112 distinct) and omits every un-extracted table (EXT-7).

**3. Can the current system detect newly introduced Last Epoch data it does not understand?** — **NO.**
- `validate_exports` passes on additions and value changes.
- The single unknown-value diagnostic (148 unknowns) is not part of the pipeline.
- The affix `_meta` reports `unknown_sp_count: 0` while 134 records carry the undecoded value `6` (DRIFT-5, DRIFT-6).

**4. Can an imported build be represented without meaningful data loss?** — **NO.**
- Blessings, implicits, roll values, sealed/experimental affixes, forging/legendary potential, the idol grid, weaver, attributes and config are never read.
- Gear bases resolve through a sequential index, giving wrong items.
- Skills are truncated to 5, and the slot and source provenance are dropped (IMP-4/5/6/7).

**5. Is the Last Epoch Tools importer currently production-capable?** — **NO.**
- The server-side fetch returns HTTP 403 in production, which the repository's own comments already call dead (`import_route.py:432-434`). Yet the default UI tab still routes LE Tools URLs to it (IMP-1/2).
- Whether Cloudflare or the origin issues the 403 cannot be determined, because only the status code is logged.
- The JSON/bookmarklet path works mechanically but maps gear wrongly (IMP-4).

**6. Is the platform safe to actively promote right now?** — **NO.**

**7. Exact P0 blockers (8):**

| ID | Blocker |
|---|---|
| **SYS-1** | `PATCH /api/admin/affixes/<id>` is unauthenticated and rewrites `data/items/affixes.json`. `POST /api/load/game-data` (also unauthenticated) hot-reloads it. Reproduced with the test client on a scratch copy. |
| **INFRA-1** | SQLAlchemy is unpinned. A fresh install resolves 2.1.x, whose `postgresql://` default driver (psycopg 3) is not installed, so `create_app`/`flask db upgrade` fail. Reproduced 3× including Python 3.11. Blocks deploying any fix. |
| **EXT-1** | Production `data/` is a 1.4.3-era snapshot (`patch_version: "unknown"`, synced 2026-04-26). Re-running the sync on current exports changes 37 of 52 files. |
| **DRIFT-1** | The live game is 1.5.x Season 5 (Oct 2026); the newest extraction is 1.4.6 (2026-05-06). No Season 5 content exists. |
| **EXT-2** | Every affix tier value is stored at 100×, and all 534 multi-property affixes lose their second property. Added Health T1: game 5–15, Forge 500–1500. |
| **LOSS-1** | The runtime ÷100 heuristic misses attribute affixes (Strength T8 = 2400–2800 reaches the stat engine). |
| **REL-1** | `MASTERY_MAP` swaps the mastery order for Mage, Primalist and Sentinel, so 190 of 541 passive nodes carry the wrong mastery. |
| **CALC-1** | Skill base damage/scaling is hand-calibrated and contradicts extracted data: 53/54 comparable skills off by >25%, median 24.6×. Fireball: Forge 110 vs extract 25. |

**8. Exact P1 blockers (64):**
- Security / availability: SYS-2, API-2, API-4, API-5, API-6, API-7, API-3, SEC-3, SEC-4
- Deploy and CI: INFRA-2, TEST-1, RT-2, RT-4, TEST-2, TEST-3, DOC-2
- Import: IMP-1, IMP-2, IMP-4, FE-4, FE-5, OBS-1
- Data and extraction: EXT-3, EXT-4, EXT-5, EXT-10, DRIFT-2, DRIFT-3, DRIFT-4, DRIFT-5, LOSS-2, LOSS-3, LOSS-4, LOSS-5, SYS-3, SYS-4, SYS-6
- Relationships and schema: REL-2, REL-4, REL-6, REL-7, REL-10, REL-23, DB-1, DB-3
- Calculation and trust exposure: CALC-2..8, CALC-11, CALC-12, CALC-14, CALC-15, DEAD-1, DEAD-3, SYS-5, FE-1, FE-3, DOC-3, DOC-5, DOC-9

Full text, evidence and file/line references are in `AUDIT_EVIDENCE.json`.

**9. What must be fixed BEFORE any new product feature work?**
- AUDIT-R0 in full: deployability, the anonymous write/IDOR/visibility holes, the importer dead end and the alert content.
- AUDIT-R1's value-scale, provenance-manifest and reproducible-sync items.
- AUDIT-R2's mastery fix.
- AUDIT-R5's "deploy requires green CI".
- Before that, decide the remediation base branch (`main` vs the 413-commits-ahead, persistently red `dev`).

**10. What must exist before we can truthfully claim "The Forge extracts 100% of the Last Epoch data it needs"?** See the final section of `20_PRIORITIZED_REMEDIATION_ROADMAP.md`. In short:
1. An enumerated denominator from the game's own table manifest.
2. 100% entity coverage of tables marked "needed".
3. Declared-or-carried field coverage, enforced by a field-survival test.
4. Zero unallowlisted dangling references.
5. Served data version equal to the live patch.
6. A gating unknown-field/enum/table detector.
7. Regeneration from an archived raw snapshot.

All of these must be computed in CI. Semantic coverage (understanding the mechanic) must be reported separately and must never be counted as extraction completeness.

---

## The 403 incident, in one paragraph

1. The user hit the default "Import URL" tab.
2. `POST /api/import/build` → `LastEpochToolsImporter.parse()` makes a single `requests.get` of `https://www.lastepochtools.com/planner/B5P5P8M3`, with a hard-coded Chrome/120 User-Agent and no retries, from a Render datacenter IP.
3. LE Tools (or its edge) answered 403.
4. The `HTTPError` branch (`lastepochtools_importer.py:716-727`) produced "Last Epoch Tools returned HTTP 403."
5. `_record_and_alert` (`import_route.py:568-576`) passed `result.build_data` (always `None` on failure) instead of `partial_data`. The alert therefore read "No data parsed" and "Missing Fields: None". "None" here means "not attempted", not "complete".

The repository already documents that this fetch path is dead and offers a bookmarklet/JSON alternative, but the default UI does not steer users to it. The importer kept no response headers or body, so whether Cloudflare or the origin issued the 403 cannot be determined. Bypassing upstream protection is not a remediation option.

## What was checked and found sound

- Alembic chain: a single head, no broken `down_revision`; models structurally match migrations.
- No SSRF in the importers (hosts are hard-coded); no pickle, `yaml.load`, `eval`, shell subprocess or SQL injection found.
- Electron window hardening (context isolation, no node integration, sandbox).
- No real secrets committed.
- The v2 bundle generators reproduce all 11 bundles record-for-record from the 1.4.6 export.
- `flask validate-data` passes on 52 files. That is a schema check only; it says nothing about correctness.

## Reading guide

| Report | Topic |
|---|---|
| 01 | System map: actual data path, repo boundaries |
| 02 | Runtime/build health: exact test results |
| 03–06 | Extraction architecture, coverage matrix, field loss, relationships |
| 07 | Patch drift |
| 08–09 | Importer forensics and import contract |
| 10–11 | Database and API (171-route endpoint table) |
| 12 | Frontend journey (includes the FE-1 reconciliation note) |
| 13 | Calculation trust matrix |
| 14–16 | Tests, observability, infrastructure |
| 17 | Security and dependencies |
| 18 | Dead code |
| 19 | Documentation drift |
| 20 | Remediation roadmap |
| `AUDIT_EVIDENCE.json` | All 140 findings, machine-readable |


---

<!-- FILE: 01_SYSTEM_MAP.md -->

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


---

<!-- FILE: 02_RUNTIME_AND_BUILD_HEALTH.md -->

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


---

<!-- FILE: 03_EXTRACTION_ARCHITECTURE.md -->

# 03 — Extraction System Architecture (Phase 2)

Audit date: 2026-10-06
Scope: `last-epoch-data` @ `73e2ab0` (2026-05-31, **694 commits, not shallow** — `git rev-parse --is-shallow-repository` → `false`), `le-the-forge` @ `1efcef7` (2026-05-14, shallow, 266 commits, history starts 2026-03-31 at `cf675f7`), `le-parser` @ `5135ce4` (archived 2026-03-26).
Method: read every extractor/transformer entry point, mapped each output file to its writer, inspected the il2cpp dump and the 1.4.6 `resources.assets` manifest for data-table classes, and **re-ran the Forge-side transforms in an isolated scratch copy** (sync job and all 11 v2 bundle generators) to test reproducibility. Nothing in any repository was modified; all generated output went to a scratch directory outside the repos.

Legend: **game-derived** = decoded from Last Epoch binaries/assets; **localization-derived** = built from string tables only (names, no structure); **third-party** = scraped/copied from a non-game source; **hand-authored** = typed in by a person, no extractor; **UNKNOWN** = provenance cannot be established from repo contents.

---

## 1. Actual-implementation pipeline (as built, not as documented)

```
 SOURCE                     ACQUISITION                       RAW PRESERVATION                       PARSING / DECODE
 ───────────────────────    ───────────────────────────────   ────────────────────────────────────   ──────────────────────────────────────────────
 Last Epoch 1.4.6           Manual copy of the Steam install  NOT IN REPO for 1.4.6.                 UnityPy + TypeTreeGenerator, TypeTrees built from
 (build 22986002,           to D:\LastEpochTools\game_files\  .gitignore excludes game_files/ and    il2cpp.h / DummyDll:
  Unity 6000.0.42f1)        current\1.4.6_22986002            extracted_raw/raw_bundles/.            tools/scripts/build_typetrees.py, env_loader.py,
                            (exports_json/metadata.json:8)    Only patch_versions/1.3.7.1_22373561   il2cpp_h_parser.py, il2cpp_h_to_typetree.py
                            tools/scripts/game_paths.py        and 1.4.3_22682302 (GameAssembly.dll  extract_enums.py (pythonnet + Mono.Cecil, Windows)
                            (env LAST_EPOCH_DIR → repo-local   + global-metadata, 106 MB / 114 MB).  extract_skill_trees_fast.py (sharedassets1.assets)
                            game_files → Steam registry)      Partial 1.4.6 intermediates committed: extract_skills_binary.py, extract_master_affixes.py
                            Tools pinned in tools/external.lock extracted_raw/MasterAffixesList.json, extract_localization_addressables.py
                            (Il2CppDumper 6.7.46, AssetRipper   resources_manifest.json (1.4.6 sha),  build_resources_manifest.py, build_monoscript_map.py
                            1.3.12, Mono.Cecil) via            raw_skill_trees_from_game.json,
                            scripts/fetch_tools.ps1 (Windows)  MonolithTimelines.json, enums.json,
                                                               il2cpp_dump/script.json (last commit
                                                               2026-03-31 → pre-1.4.6, version UNKNOWN)
        │                                │                                  │                                        │
        ▼                                ▼                                  ▼                                        ▼
 NORMALIZATION (last-epoch-data)                      VALIDATION                                 GOVERNANCE / TRUST
 ───────────────────────────────────────────────      ───────────────────────────────────────    ─────────────────────────────────────────────
 tools/scripts/run_all.py orchestrates 28 steps:      tools/scripts/validate_exports.py          ~345 governance/certification/ledger/review
 process_classes, process_ailments,                   → tools/verification/export_baselines.json  scripts in tools/scripts (597 files, 179
 enrich_skills_localization, enrich_skill_damage_      COUNT FLOORS ONLY for 9 files              generate_*, 181 test_*). Output: docs/generated/
 sources, process_skill_trees, process_affixes_tt,    (min_records == current count). 12 of 21   forge_safe_*_bundle.json etc. data_bundle/
 process_items, process_uniques, process_timelines,   exports have no baseline. Re-run here:     manifest.json (phase1a): 17 families declared,
 process_monster_mods, process_loot, process_set_     "Export validation passed for 9 baseline   2 materialized (base_items 1508, item_types 50);
 bonuses, process_quests, process_zones,              file(s)."                                  4 BLOCK, 10 DEGRADE; 3 family files present
 process_dungeons, emit_metadata.                     pipeline_status.json / output_manifest.json but undeclared. extractor_version: null.
 → exports_json/*.json (21 files + localization/21)   are NOT committed (no run record).
 actors.json: writer deleted (66c6498, 2026-05-04);
 file last written 2026-04-11 (pre-1.4.6).
        │
        │  (manual hand-off; no CI, no package, no API — see 01_SYSTEM_MAP §1)
        ▼
 PERSISTENCE (le-the-forge)                                         API                                     FRONTEND
 ─────────────────────────────────────────────────────────────     ──────────────────────────────────────  ─────────────────────────────────────
 Path A (production): scripts/sync_game_data.py (expects            Path A: backend/app/game_data/          frontend/src/data/raw/*.json
 <forge>/last-epoch-data/exports_json, line 21) → data/**.          pipeline.py:44-57 loads 13 files        (char/skill tree layout + metadata,
 Last real sync: data/version.json → patch "unknown",               (affixes, enemy_profiles, skills*,      provenance UNKNOWN, LET-format
 2026-04-26, files_updated only affixes (stamp bug:                 classes*, skills_metadata, uniques,     payload), frontend/src/data/
 sync_game_data.py:1431 is the only files_updated.append).          rarities, damage_types, implicit_stats, {passiveTrees,skillTrees}/index.ts
 Committed data/ PREDATES the 1.4.6 exports (2026-05-05).           base_items, crafting_rules, blessings,   (scripts/generate_tree_data.py),
 Hand-authored alongside: backend/app/game_data/skills.json,        weaver_tree). *skills.json/classes.json public/assets 400 passive + 54
 classes.json, constants.json; data/items/{base_items,               are the HAND-AUTHORED copies beside     skill icons (scripts/extract_images.py,
 crafting_rules, forging_potential_ranges, implicit_stats,          pipeline.py (lines 47-48).              needs a local game install).
 rarities, tags, item_types}.json; data/entities/enemy_             Other loaders: services/passive_stat_   community_skill_trees.json (third-party,
 profiles.json; data/combat/damage_types.json;                      resolver (passives.json),               github.com/prowner/last-epoch-data)
 data/classes/skill_tree_nodes.json; data/progression/              services/skill_tree_resolver            is read by SkillTreePanel.tsx and
 weaver_tree.json (scraped from LET 1.4.2).                         (skill_tree_nodes.json prose parser).   routes/skills.py.
                                                                    data_version always "unknown"
 Path B (experimental): backend/scripts/report_v2_*.py              (pipeline.py:467-471 reads _version
 (defaults D:\Forge\last-epoch-data\...) → docs/generated/          from a dict, but affixes.json is a list).
 v2_*_bundle.json (11 files, 2026-05-12, built from 1.4.6
 exports). production_consumed:false, stable_calculable 0.          Path B: app/repositories/v2/* behind
                                                                    /experimental and /api/experimental
 Path C (dormant): backend/app/game_data/bundle_compat.py:19        (registered unconditionally,
 DEFAULT_BUNDLE_DIR = D:\Forge\last-epoch-data\data_bundle,         app/__init__.py:249-250).
 env FORGE_DATA_BUNDLE_DIR. Diagnostics/report scripts only.
```

Gaps marked on the diagram, in pipeline order:

| # | Stage | Gap | Evidence |
| --- | --- | --- | --- |
| G1 | Source | Version of record for production is **not 1.4.6**. Production `data/` was synced 2026-04-26 with `patch_version: "unknown"`; the 1.4.6 exports are dated 2026-05-05/06. | `data/version.json`; `exports_json/metadata.json:12` (`generated_at 2026-05-06`); `git log -1 -- exports_json/affixes.json` → 2026-05-05 |
| G2 | Acquisition | Windows-only and manual. `game_paths.py` resolves via env var / repo-local `game_files/` / Steam registry (`winreg`). Tool fetch is `fetch_tools.ps1`; enum extraction needs pythonnet + Mono.Cecil. No Linux/CI acquisition path. | `tools/scripts/game_paths.py:1-40`; `tools/external.lock`; `scripts/fetch_tools.ps1` |
| G3 | Raw preservation | 1.4.6 game files and `extracted_raw/raw_bundles/` are gitignored and absent. **Exports cannot be regenerated from the repo.** Only 1.3.7.1 and 1.4.3 binaries are kept. `il2cpp_dump/script.json` last committed 2026-03-31 (predates 1.4.6; exact version UNKNOWN). | `.gitignore` (lines "game_files/", "extracted_raw/raw_bundles/"); `ls patch_versions` |
| G4 | Parsing | Some processors read inputs that are not in the repo: `process_loot.py` (`extracted_raw/raw_bundles/defaultlocalgroup`, `actors_misc`), `process_monster_mods.py` (`raw_bundles/duplicateasset`), `process_dungeons.py` (`raw_bundles/database`). `actors.json` has no writer since `66c6498` deleted `process_actors.py`. | file headers of those scripts; `git log --diff-filter=D -- 'tools/scripts/*actor*'` |
| G5 | Parsing | Decoded garbage survives into exports: 19 passive-tree and 4 skill-tree requirement edges point to nonexistent node ids such as `1684808296038400`; raw skill-tree extraction logs `nodeParseFailures: 11`. | §4 of 04 matrix; `extracted_raw/raw_skill_trees_from_game.json` `meta` |
| G6 | Normalization | Hand-coded enum maps instead of extracted enums: `SPECIAL_AFFIX_TYPE` (`process_affixes.py:74-77`) covers 0–5; value 6 leaks as the string `"6"` on 134 affixes. `SpecialAffixType` is absent from `extracted_raw/enums/enums.json` (354 enums). | `process_affixes.py:226` |
| G7 | Validation | `validate_exports.py` checks only record-count floors set to the current counts for 9 of 21 exports. It cannot detect domains or entities that were never extracted, and it does not check referential integrity. | `tools/verification/export_baselines.json` |
| G8 | Governance | Trust labelling is extensive in `last-epoch-data` (data_bundle manifest blocks all affix families), but **nothing in production reads it**: `bundle_compat.py` is only imported by report/diff modules. | `grep -rn bundle_compat backend/app` |
| G9 | Persistence | `sync_game_data.py` is **not idempotent with the committed `data/`**: a fresh run against the current exports changes 36 of 51 data files plus `version.json` (see §3). Several committed files carry hand edits that a re-sync would overwrite (`skills_metadata.json` loses the `_schema` block and 4 fields; `blessings.json` changes from 10 timeline groups to a flat 224-entry list that `pipeline.py:128-140` cannot index). | scratch re-run, §3 |
| G10 | Persistence | Two data generations live in one app: production (`data/`, pre-1.4.6) and experimental v2 bundles (`docs/generated/`, 1.4.6). | `docs/generated/v2_*` `source_*_path` fields; `data/version.json` |
| G11 | API | Production simulation inputs for skills, class base stats, mastery/keystone bonuses and constants come from hand-authored files next to the loader, not from any export. | `backend/app/game_data/pipeline.py:47-48`; `backend/app/game_data/{skills,classes,constants}.json` |
| G12 | Frontend | Tree layouts (`frontend/src/data/raw/*`) and community skill trees have non-game or UNKNOWN provenance; the weaver tree is a LET scrape even though the extractor already decodes the game's own `WeaverTree` (77 nodes) into `raw_skill_trees_from_game.json` and then drops it. | §5 |

---

## 2. Inventory of extractors, transformers and adapters

### 2.1 `last-epoch-data` (writer of `exports_json/`)

`tools/scripts/` has 597 files: 179 `generate_*`, 181 `test_*`, about 345 whose names match governance terms (`certif|governance|ledger|review|readiness|closeout|authoriz|blocker|planning|roadmap|policy`; `ls tools/scripts | grep -cE ...`), and 109 `probes/`. The extraction core is about 40 scripts:

| Output | Writer (current) | Input actually read | Method | Notes |
| --- | --- | --- | --- | --- |
| `metadata.json` | `emit_metadata.py` | install path, `GameAssembly.dll` sha | file hash | embeds `D:\LastEpochTools\...` installPath |
| `classes.json` | `process_classes.py` | `resources.assets` → `Character Class List` | TypeTree | `decode_failures 0` |
| `skills.json` | `extract_skills_binary.py` → `enrich_skills_localization.py` → `enrich_skill_damage_sources.py` (+ `ability_manager_resolver.py`) | `sharedassets*/resources.assets`, Addressables loc | binary + TypeTree | meta `rawFiles 195, deduplicated 40, binaryReplaced 14` |
| `skills_with_trees.json`, `passive_trees.json`, `unmatched_trees.json` | `process_skill_trees.py` (from `extract_skill_trees_fast.py` output `extracted_raw/raw_skill_trees_from_game.json`) | `sharedassets1.assets` | binary walker | WeaverTree decoded but not emitted (§5) |
| `affixes.json` | `process_affixes_tt.py` (equipment), `AffixImport.csv` (idol section) | `MasterAffixesList` via TypeTree; `extracted_raw/AffixImport.csv` | TypeTree + CSV | idol section is a 115-record **subset** of the 1112 equipment records (§4 of 04) |
| `items.json` | `process_items.py` | `MasterItemsList` | TypeTree | |
| `uniques.json` (+ `setBonusData` patch) | `process_uniques.py`, then `process_set_bonuses.py` patches it | `UniqueList` (path_id 254583), `SetBonusesList` | TypeTree | two writers for one file |
| `set_bonuses.json` | `process_set_bonuses.py` | `SetBonusesList` | TypeTree | `setName` null for 2 of 24 groups |
| `ailments.json` | `process_ailments.py` | `AilmentList`, `NonAilmentUIBuffList` | TypeTree | 143 ailments, of which `Ignite` id 1 appears 3 times |
| `timelines.json`, `blessings.json` | `process_timelines.py` | `MonolithTimeline` objects; blessings from `items.json` Blessing base type | TypeTree | |
| `quests.json` | `process_quests.py` | `MasterQuestList` | TypeTree | |
| `monster_mods.json` | `process_monster_mods.py` | `extracted_raw/raw_bundles/duplicateasset/MonoBehaviour` (**not in repo**) | legacy bundle dump | 20 records |
| `loot_tables.json` | `process_loot.py` | `raw_bundles/defaultlocalgroup`, `actors_misc` (**not in repo**) | legacy bundle dump | file last written 2026-03-30 (1.3.7.1 era) |
| `zones.json` | `process_zones.py` | `exports_json/localization/scene_strings.json`, `map_object_strings.json` | **localization-derived** | names only |
| `dungeons.json` | `process_dungeons.py` | `vault_mod_strings.json` + `raw_bundles/database` (**not in repo**) | localization-derived | `mods` empty for all 3 dungeons |
| `actors.json` | **none** (`process_actors.py` deleted in `66c6498`) | — | — | last written 2026-04-11 (`63539ac` "restore ... actors from 4a428c3") |
| `community_skill_trees.json` | `convert_community_skilltrees.py` | `extracted_raw/community_skilltrees.ts` | **third-party** (`meta.source` = `https://github.com/prowner/last-epoch-data`) | last written 2026-03-26 |
| `localization/*.json` (21) | `process_localization.py` / `process_localization_unified.py`, `extract_localization_addressables.py` | Addressables string tables | | 122,440 entries |
| `loot_filter_relevant_entities.json` | `loot_filter_entity_manifest_provenance.py` | other exports | governance manifest | 5 entries; not a game domain |
| `data_bundle/**` | `generate_data_bundle_skeleton.py` (+ idol/normalization generators) | `exports_json/items.json`, `metadata.json` | normalization | phase1a skeleton |

### 2.2 `le-the-forge` (consumer side)

| Component | Path | Reads | Writes | Runs on Linux? |
| --- | --- | --- | --- | --- |
| Sync job | `scripts/sync_game_data.py` (1,543 lines, 21 sync functions) | `<forge>/last-epoch-data/exports_json` | `data/**`, `data/version.json` | Yes, if the export directory is placed inside the Forge root (reproduced here with a symlink) |
| Tree enricher | `scripts/generate_tree_data.py` | exports + `frontend/src/data` | `frontend/src/data/{passiveTrees,skillTrees}/index.ts` | Yes (not re-run here) |
| Icon extractor | `scripts/extract_images.py`, `scripts/build_sprite_map.py` | local `Last Epoch_Data/resources.assets` | `frontend/public/assets/*` | Needs a game install |
| v2 bundle generators | `backend/scripts/report_v2_{affix_bundle,item_bundles,idol_bundles,unique_set_bundles,class_mastery_bundle,passive_tree_bundle,skill_tree_bundle}.py` | defaults `D:\Forge\last-epoch-data\...` (override via CLI) | `docs/generated/v2_*` | Yes with CLI overrides, **but** `report_v2_class_mastery_bundle.py:514-516` derives `patch_version` with `Path(installPath).name`, which on Linux returns the whole Windows path string |
| Bundle compat | `backend/app/game_data/bundle_compat.py` | `FORGE_DATA_BUNDLE_DIR` or `D:\Forge\...\data_bundle` | — | Only through report scripts |
| Runtime loader | `backend/app/game_data/pipeline.py`, `game_data_loader.py`, `data/loaders/raw_data_loader.py` | `data/**` + hand-authored JSON beside the loader | — | — |
| Legacy parser | `/home/user/le-parser` (JS) | — | `classes.json`, `properties.json`, `skillNodeTrees.json` | Not referenced by runtime (only `report_v2_source_inventory.py`) |

---

## 3. Reproducibility tests (run, not inferred)

### 3.1 Sync job against current exports

```bash
R=$SCRATCH/repro_root; mkdir -p $R/scripts $R/frontend/src/data/raw
cp -r le-the-forge/data $R/data; cp le-the-forge/scripts/sync_game_data.py $R/scripts/
cp le-the-forge/frontend/src/data/raw/char-tree-layout.json $R/frontend/src/data/raw/
ln -s /home/user/last-epoch-data $R/last-epoch-data
python3 -I $R/scripts/sync_game_data.py          # writes only inside $R
python3 -I $SCRATCH/diffdata.py $R/data          # structural JSON equality per file
```

Result: of 52 JSON files under `data/` (51 data files + `version.json`), **15 are identical and 37 differ** (36 data files + `version.json`). The identical set is the 11 files the sync never writes (hand-authored or curated: `damage_types`, `weaver_tree`, `base_items`, `crafting_rules`, `forging_potential_ranges`, `implicit_stats`, `item_types`, `rarities`, `tags`, `skill_tree_nodes`, `enemy_profiles`) plus 4 whose inputs did not change (`actors.json`, `loot_tables.json`, `localization/en.json`, `localization/id_lookup.json`). Selected deltas (committed → fresh):

| File | Committed | Fresh from 1.4.6 exports | Meaning |
| --- | --- | --- | --- |
| `combat/ailments.json` | 11 | 143 | committed file is a hand-picked subset; unconsumed |
| `world/quests.json` | 2 | 147 | committed is a stub; unconsumed |
| `progression/blessings.json` | 10 timeline groups (112 nested) | flat 224 | **shape change breaks `pipeline.py:128-140`** |
| `classes/passives.json` | 541 | 535 | 6 Acolyte nodes in Forge are absent from 1.4.6 export (ids 86, 88, 97, 98, 101, 103) |
| `classes/unmatched_trees.json` | 27 | 1 | stale |
| `classes/community_skill_trees.json` | 140 | 138 | committed copy differs from current third-party source |
| `classes/skills_metadata.json` | 161 skills × 9 fields + `_schema` | 161 × 5 fields | re-sync drops `base_damage_min/max`, `damage_scaling_stat`, `attack_type` (all currently null) and `_schema` |
| `classes/skills_with_trees.json` | 184; 137 with tree, 3,875 nodes | 184; 136 with tree, 3,919 nodes | stale tree content |
| `items/items.json` | 40 equippable | 42 | stale (missing `UNUSED`, `IDOL_ALTAR`) |
| `items/affixes.json` | 1,228 | 1,230 | 3 legacy entries are preserved (`sync_game_data.py:262-278`) |
| `items/uniques.json` | 403 | 409 (+9 new) | |
| `items/set_items.json` | 47 items | 59 (+15 new) | |
| `world/zones.json` | 368 | 385 | |
| `localization/property_strings.json` | 1,950 | 2,649 | 16 of 21 localization files grow, 1 shrinks (`item_strings` 2,236 → 2,219), 4 keep their count |

Conclusion: **committed production data is not the output of the committed sync job on the committed exports.** Its true generating inputs are UNKNOWN (earlier export generation plus hand edits).

### 3.2 v2 bundle generators against current exports

All 7 generators were run in a scratch virtualenv (`pip install -r backend/requirements.txt`), with every input path passed explicitly and every output in scratch (`$SCRATCH/runv2.py`). Record-level comparison after normalizing absolute/relative source-path strings:

| Bundle | Records | Identical to committed |
| --- | --- | --- |
| item_base / item_implicit | 542 / 1,182 | 542 / 1,182 |
| affix | 1,098 | 1,098 |
| idol / idol_affix | 71 / 483 | 71 / 483 (path-only diffs) |
| unique / set (sets, items, bonuses) | 409 / 23, 59, 45 | all |
| class_mastery (classes, masteries) | 5 / 15 | all, **except `patch_version`**: fresh run gives `D:\LastEpochTools\game_files\current\1.4.6_22986002`, committed `1.4.6_22986002` (Windows-only path parsing) |
| passive_tree (nodes, trees) | 535 / 5 | all |
| skill / skill_tree (nodes, trees) | 184 / 3,919, 136 | all |

Conclusion: **the v2 path is reproducible from the committed 1.4.6 exports** (Path B), apart from embedded paths and one platform-dependent field. The production path (Path A) is not.

### 3.3 Export validation

`python3 -I tools/scripts/validate_exports.py` → `Export validation passed for 9 baseline file(s).` This proves only that counts did not shrink below themselves.

---

## 4. Game data tables present vs extracted (discovery)

Denominator: data-table classes found in the **1.4.6** `extracted_raw/resources_manifest.json` (`by_script`, 1,170 script classes, 89,593 MonoBehaviours, `gameAssemblySha256` matches `exports_json/metadata.json`). Cross-checked against `il2cpp_dump/script.json` (38,956 type names; pre-1.4.6 dump). Each candidate was then searched for in `exports_json/**` and `tools/scripts/*.py` (`grep -l`).

| Game table (instances) | Domain | In exports? | Extractor exists? |
| --- | --- | --- | --- |
| `CharacterClassList` (1) | classes | yes | `process_classes.py` |
| `AffixList` "MasterAffixesList" (1) | affixes | yes | `process_affixes_tt.py` |
| `ItemList` "MasterItemsList" (1) | item bases | yes | `process_items.py` |
| `UniqueList` (1), `SetBonusesList` (1) | uniques, sets | yes | yes |
| `AilmentList` (1, 141 `Ailment`), `NonAilmentUIBuffList` (1, 225 `NonAilmentUIBuff`) | ailments, buffs | yes (143 / 225) | yes |
| `TimelineList` (1) | monolith timelines | yes (10) | yes |
| `QuestList` "MasterQuestList" (1; 169 `Quest`, 903 `QuestStep`) | quests | yes (147) | yes |
| `DungeonList` (1) | dungeons | names only (3, no mods) | localization-derived |
| `ActorDataList` (1; 1,020 `ActorData`) | actors | 248 (orphan file, pre-1.4.6) | **writer deleted** |
| `StatsMonsterMod` 236, `PseudoComponentMonsterMod` 33, `ComponentMonsterMod` 14, other 4 | monster mods | 20 | legacy raw_bundles reader |
| `BossLoot` (102) | boss loot | 3 boss tables | legacy |
| `GlobalTreeData` (1), `FactionDataWeaver` (1); raw `WeaverTree` 77 nodes | weaver tree | **no** (decoded into `raw_skill_trees_from_game.json`, dropped) | partial |
| `FactionsList` (1), `FactionData` (2: Circle of Fortune, Merchant's Guild); enum `FactionID` has 4 | factions | **no** | **no** |
| `ConstellationsList` (1), `ConstellationData` (16), `ProphecyReward` 203, `ProphecyTarget` 81, `ProphecyName` 31 | CoF prophecies / observatory | **no** | **no** |
| `WovenEchoList` (1) | woven echoes | **no** (only `Woven Echo` item subtypes, 44) | **no** |
| `ChampionDataList` (1) | champion affixes | **no** | **no** |
| `ArenaList` (1) | arena | **no** | **no** |
| `ShrineList` (1; 40 `Shrine`) | shrines | **no** | **no** |
| `MemoryList` "MasterMemoryList" (1) | weaver memories | **no** | **no** |
| `HarbingersData`, `TombData`, `OmenData`, `RoamingOmensData`, `PrimalHuntData`, `SilkenCocoonData`, `TimeBeastData`, `SpecialEchoChainData` (6) | endgame systems | **no** | **no** |
| `CorruptionOutcomeConfig` (1) | corruption | **no** (timelines carry corruption mod keys only) | **no** |
| `IdolAltarPropertyList` (1) | idol altars | **no** (only a PPtr in `items.json._extra`) | **no** |
| `GlyphOfInsightReplacementList` (1), `MaterialList` (1) | crafting materials, runes/glyphs | **no** (identity only: `Crafting Modifier Item` 13, `Crafting Support Item` 6, `Affix Shard` 502 subtypes) | **no** |
| `PropertyList` "MasterPropertyList", `PlayerPropertyList`, `AbilityPropertyList`, `TrackerPropertyList`, `ExtraStatData` | stat/property definitions | **no** (property names only through enums + `property_strings`) | **no** |
| `OneShotCacheList` (50 data), `ChestList`, `DroppableRewardList`, `ShardDropTable` | rewards / drop tables | **no** | **no** |
| `MonolithObjectiveList` | monolith objectives | strings only | no |
| `AchievementsList`, `LoadingTipsList`, `DialogueDatabase` (7) | non-planner | strings only | — |

Discovery result: **19 game data tables relevant to a build planner or crafting/endgame model have no extractor and no export** (factions, constellations/prophecies, woven echoes, champions, arena, shrines, memories, 8 endgame data singletons, corruption config, idol altar properties, crafting materials/glyph replacement, property definitions, caches/chests/rewards/shard drops). Weaver tree is decoded but not exported. This count is a lower bound: data stored in prefab components or plain `MonoBehaviour`s without a `*List` naming pattern was not enumerated.

---

## 5. Source and authority per domain

| Domain | Origin | Acquisition | Version | Authoritative? | Raw kept in repo? | Reproducible from repo? |
| --- | --- | --- | --- | --- | --- | --- |
| Affixes | game `MasterAffixesList` | TypeTree | 1.4.6 | yes (export) | yes (`MasterAffixesList.json`, re-extracted 2026-05-28 from `D:\Forge\...`) | partial: re-normalization yes, re-extraction no |
| Idol affix section | `extracted_raw/AffixImport.csv` | CSV import | UNKNOWN | no (duplicate subset) | yes | yes |
| Items/bases | `MasterItemsList` | TypeTree | 1.4.6 | yes | no | no |
| Uniques/sets | `UniqueList`, `SetBonusesList` | TypeTree | 1.4.6 | yes; set names partly from a manual `SET_NAMES` table | no | no |
| Skills | ability prefabs + trees | binary + TypeTree | 1.4.6 | partial (74 skills `none_found` damage) | partial (`raw_skill_trees_from_game.json`) | no |
| Skill/passive trees | `sharedassets1.assets` | binary walker | 1.4.6 | yes for structure | yes (raw trees) | normalization yes |
| Classes | `Character Class List` | TypeTree | 1.4.6 | yes; mastery `abilityPathIds` empty for all 20 masteries | no | no |
| Ailments/buffs | `AilmentList` / `NonAilmentUIBuffList` | TypeTree | 1.4.6 | yes | no | no |
| Timelines/blessings | `MonolithTimeline` + Blessing items | TypeTree | 1.4.6 | yes | yes (`MonolithTimelines.json`) | normalization yes |
| Monster mods | raw bundle dump | legacy | UNKNOWN (file refreshed 2026-05-05, reader unchanged) | partial | no | no |
| Actors | deleted extractor | legacy | pre-1.4.6 | stale | no | **no writer** |
| Loot tables | raw bundle dump | legacy | 1.3.7.1-era (2026-03-30) | stale | no | no |
| Quests | `MasterQuestList` | TypeTree | 1.4.6 | yes | no | no |
| Zones, dungeons | localization tables | string parse | 1.4.6 | names only | yes (localization) | yes |
| Localization | Addressables | bundle read | 1.4.6 | yes | yes (exports) | — |
| Community skill trees | GitHub `prowner/last-epoch-data` | file copy | UNKNOWN | **no** (third-party) | yes | yes |
| Weaver tree (Forge) | LET `window.LEWeaverTree`, game 1.4.2 | scrape | 1.4.2 | **no** | — | no |
| Tree layouts, icons (Forge frontend) | UNKNOWN (LET-format payloads); icons from local `resources.assets` | UNKNOWN / local | UNKNOWN | UNKNOWN | — | no |
| Skill base damage, class stats, mastery/keystone bonuses, constants (Forge backend) | hand-authored (constants cite "1.4.3 spec") | manual | 1.4.3 claim | no | — | — |
| Base items (Forge `data/items/base_items.json`) | hand-authored | manual | UNKNOWN | **no**: 17 of 115 names exist in the 1.4.6 item export | — | — |
| Crafting rules, FP ranges, rarities, implicit_stats, damage types, enemy profiles, tags | hand-authored | manual | UNKNOWN | no | — | — |

---

## 6. Platform and path hazards

* `last-epoch-data` embeds absolute Windows install paths in every TypeTree export `_meta.game_build.installPath` and in `exports_json/metadata.json:8`; `extracted_raw/MasterAffixesList.json` names a second root (`D:\Forge\last-epoch-data\game_files\...`), so at least two extraction hosts or layouts were used.
* `le-the-forge`: 12 tracked non-test Python files hard-code `D:\` defaults (`git grep -l 'D:\\' -- 'backend/*.py'`), including `bundle_compat.py:19` and all 7 `report_v2_*` generators. The committed v2 bundles record `D:\Forge\...` source paths, while `v2_affix_bundle.json` records 3,294 `/home/user/last-epoch-data/...` paths that came from an upstream artifact generated on a Linux host before `f9aa4ce` normalized them. Provenance strings therefore mix hosts.
* `report_v2_class_mastery_bundle.py:514-516` gives different `patch_version` values depending on the OS that runs it.

---

## 7. What this does NOT prove

* That any export value equals what the game uses at runtime. No in-game ground truth was available; raw 1.4.6 assets are not in the repo.
* That the 19 un-extracted tables in §4 are all needed by the planner. Relevance was judged by name and domain.
* That `script.json` type names describe 1.4.6. The dump predates 1.4.6; the 1.4.6 resources manifest was used as the primary denominator.
* Frontend generator reproducibility (`generate_tree_data.py`, icon extraction). Not re-run.
* Behaviour on `dev` (413 commits ahead of `main`; see 01_SYSTEM_MAP).

## 8. Missing instrumentation

1. No committed run record (`pipeline_status.json`, `output_manifest.json` with sha256 per output) for the 1.4.6 export run.
2. No `extractor_version` (`data_bundle/metadata.json` → `null`) and no per-file input hash in `exports_json`.
3. No sync manifest in `le-the-forge` mapping each `data/` file to its export sha, sync function and hand-edit status. `version.json` records one file.
4. No enumeration-based coverage check (game tables present vs exported).
5. No referential-integrity validator over exports (dangling requirements, unresolved monster mod keys, and similar problems pass validation).


---

<!-- FILE: 04_EXTRACTION_COVERAGE_MATRIX.md -->

# 04 — Extraction Coverage Matrix (Phase 3)

Audit date: 2026-10-06
Scope: `last-epoch-data` @ `73e2ab0` (exports for 1.4.6 build 22986002), `le-the-forge` @ `1efcef7`.
Companion: `03_EXTRACTION_ARCHITECTURE.md` (pipeline, writers, reproducibility runs).
All numbers below were computed by scripts run against the committed files. Nothing in either repo was modified. Where a number is a re-statement of a repo claim it is marked "claimed".

---

## 1. Formal definitions

Let *D* be a domain, *S* a pipeline stage (game assets, raw intermediate, `exports_json`, `data_bundle`, Forge `data/`, Forge v2 bundles, production runtime), and *P(D)* a declared **denominator population** (always named next to each value).

| Metric | Definition | Notes |
| --- | --- | --- |
| **Entity coverage** EC(D,S) | \|{ids present at S} ∩ P(D)\| / \|P(D)\| | Identity is joined on the game id when one exists (`id`, `affix_id`, `subTypeID`+`baseTypeID`, tree `sourceId`+node `id`), otherwise on a documented slug. Duplicates count once. Records at S that are not in P(D) are reported separately as *orphans*. |
| **Field coverage** FC(D,S,F) | Σ over entities of populated fields in F / (\|entities\| × \|F\|) | F is a declared minimal required-field set, listed per domain. "Populated" means not null, not empty string and not empty list. Unknown enum leakage (for example `"6"`) counts as not populated. |
| **Relationship coverage** RC(R,S) | references that resolve to an existing target / total references | Per declared relationship R (for example `timeline.mods[].monsterModKey → monster_mods.modKey`). |
| **Semantic coverage** SC(D,S) | entities whose mechanical effect is represented in machine-evaluable structured form, validated as such / entities | Prose, tooltip text, raw serialized hints and "partial" classifications do **not** count. Where the repo has no validated semantic model, SC is reported as the best available proxy or as "unmeasurable". |

Equal counts do not mean complete data. Two files can each hold 535 passive nodes while one has stale stats, dropped fields or hand edits. That is why EC, FC, RC and SC are reported separately.

---

## 2. Method and commands

```bash
# shapes and counts of every export / forge data file
python3 -I $SCRATCH/shape.py exports_json/*.json
python3 -I $SCRATCH/coverage.py      # entity/integrity battery -> coverage_out.json
python3 -I $SCRATCH/coverage2.py     # requirement edges, unique/set joins, forge passive orphans
# game-side denominators (1.4.6)
python3 -I -c "json.load(open('extracted_raw/resources_manifest.json'))['by_script'][...]"
# field coverage
python3 -I -c "...fc(records,[has('id'),...])..."      # see §5 field sets
# reproducibility (all outputs in scratch)
python3 -I $SCRATCH/repro_root/scripts/sync_game_data.py   # fresh Forge sync
$SCRATCH/venv/bin/python -I $SCRATCH/runv2.py              # all v2 bundle generators
python3 -I tools/scripts/validate_exports.py               # -> passed for 9 baseline files
```

Denominator sources: (a) **game** = 1.4.6 `extracted_raw/resources_manifest.json` `by_script` instance counts, `extracted_raw/raw_skill_trees_from_game.json`, `extracted_raw/MasterAffixesList.json`. (b) **export** = `exports_json`. Game-asset instance counts are upper bounds when a class is also used for non-planner content (for example `ActorData`).

---

## 3. Coverage inventory per domain (entity level)

Columns: **Game** = population in game assets (1.4.6) when measurable; **Export** = `exports_json`; **Bundle** = `last-epoch-data/data_bundle/families`; **Forge data/** = committed production data; **v2** = `le-the-forge/docs/generated/v2_*_bundle.json`; **Prod consumes?** = loaded by a production code path (see 03 §2.2).

| Domain | Game | Export | Bundle | Forge data/ | v2 | Prod consumes? | Integrity (dups / orphans / unknown enums / parse failures) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Affixes (distinct) | 1,112 (578 single + 534 multi, `MasterAffixesList`) | 1,112 equipment + 115 "idol" (**115/115 ids duplicate equipment ids**) | 0 (family deferred; BLOCK) | 1,228 records / 1,112 distinct `affix_id` (116 duplicates, from the idol section and legacy rows) | 1,098 | yes (`items/affixes.json`) | `specialAffixType:"6"` on 134 (unmapped enum); 34 tiers min>max (all negative-valued); 313 empty `displayName` |
| Affix property rows | 1,068 rows on 534 multi affixes + 578 single | all present (`affixProperties`) | 0 | **1 `stat_key` per affix; 0 of 534 multi affixes keep their second property rolls** | 1,624 modifier refs | yes | — |
| Item base types | 50 | 50 | 50 (`item_types`) | 40 equippable + 8 (stale) | 23 gear types | yes | — |
| Item subtypes | 1,508 | 1,508 (898 equippable) | 1,508 (`base_items`) | `items.json` stale copy; curated `base_items.json` 115 rows, **17 of 115 names exist in 1.4.6** | 542 gear + 71 idols | yes (curated `base_items.json`) | 0 duplicate (`baseTypeID`,`subTypeID`) |
| Uniques | 409 visible (+3 hidden, 471 binary entries total) | 409 | 0 (deferred) | 403 keys: 400 of the 409 export records + 3 hidden + numbered variants; **9 missing** (artifice_of_devastation, ash_wake, exulis, laups_path, natural_wrath, oculus_of_ruin, rahyehs_embrace, tabi_of_dusk_and_dawn, unbroken_charge) | 409 | yes | 0 dup ids |
| Set items | 59 | 59 | 0 | 47 items; **15 export items missing** (Weaver, Apiarist/"Bee Keeper" rename, Doppelganger, Jormun, Keplahan, Kuzon sets) | 59 | **no** (`set_items.json` unconsumed) | — |
| Set groups | 24 | 24 (2 `setName` null, 1 empty bonuses) | 0 | `_meta.set_count 18` | 23 | no | `mappingConfidence` from a manual `SET_NAMES` table |
| Skills (records) | 4,110 `Ability` instances (players + monsters, upper bound) | 184 (161 distinct names; 14 variants) | 0 (deferred) | `skills_with_trees.json` 184 (stale fields); hand `backend/app/game_data/skills.json` 179 names, **17 not present in 1.4.6 by name** | 184 | yes (hand file drives damage) | 1 skill with empty `id` ("Detonate Decoy"); 0 dup ids |
| Skill trees | 143 raw trees (`raw_skill_trees_from_game.json`) | 136 matched + 1 unmatched (`fs11` Fire Shield) | 0 | 137 with tree (stale) | 136 | partial | — |
| Skill tree nodes | 4,548 raw (all trees) → 3,919 in skill trees | 3,919 (3,783 allocatable) | 0 | `skill_tree_nodes.json` 2,190 nodes / 132 trees; **2,186 of 3,783 allocatable nodes (57.8%)** reach the production resolver | 3,919 | yes (prose parser) | 4 dangling requirement edges; raw `nodeParseFailures 11`; 50 node names differ between Forge and export |
| Passive trees / nodes | 5 / 535 (raw class trees 103+110+108+111+103) | 5 / 535 | 0 | 541 (**6 Acolyte orphans** not in 1.4.6: ids 86, 88, 97, 98, 101, 103) | 5 / 535 | yes | 19 dangling requirement edges (decoded garbage ids such as `1684808296038400`) |
| Weaver tree | 77 nodes (raw `WeaverTree`) | **0 (dropped)** | 0 | 77 (third-party LET scrape, game 1.4.2) | — | yes | — |
| Classes / masteries | 5 / 20 | 5 / 20 | 0 (deferred) | `data/classes/classes.json` 5 (stale shape); hand `backend/app/game_data/classes.json` drives stats | 5 / 15 | yes (hand file) | mastery `abilityPathIds` empty for 20/20 |
| Ailments | 141 `Ailment` | 143 records / 141 distinct ids (`Ignite` id 1 ×3) | — | 11 (hand subset) | — | **no** | `decode_failures 0` |
| Buffs (UI) | 225 | 225 | — | 0 | — | no | — |
| Blessings | 224 subtypes | 224 | 0 (deferred) | 10 timeline groups / 112 normal+grand pairs (curated; not sync output) | — | yes | — |
| Monolith timelines | 10 | 10 (21 fields) | — | 10 (7 fields; mods, echo weights, zones dropped) | — | **no** | — |
| Monster mods | 287 component instances (`StatsMonsterMod` 236 + others; upper bound) / **31 distinct keys referenced by timelines** | 20 | — | 20 (subset fields) | — | no | only 4 of 31 timeline-referenced keys resolve |
| Actors / enemies | 1,020 `ActorData` | 248 records / 239 distinct (9 dups); file pre-1.4.6, **no writer** | 0 (enemy_profiles deferred) | 239 unconsumed; production uses 8 hand-authored `enemy_profiles` | — | hand profiles only | `actorType` numeric, not decoded |
| Quests | 169 `Quest`, 903 `QuestStep` | 147 (903 steps referenced) | — | 2 | — | no | 0 dups |
| Zones | UNKNOWN (scene list not enumerated) | 385 names (localization-derived) + 233 map objects | — | 368 | — | no | — |
| Dungeons | `DungeonList` (enum `DungeonID` 3) | 3, **`mods` empty for all** | — | 3 | — | no | — |
| Loot tables | 102 `BossLoot` + generic tables | 24 (21 generic, 3 boss), last written 2026-03-30 | — | 24 | — | no | — |
| Localization | Addressables tables | 21 files / 122,440 entries | — | 21 files, stale (16 grow, 1 shrinks, 4 same on re-sync) | — | **no** (no runtime reader found) | — |
| Community skill trees | n/a (third-party) | 138 | — | 140 | — | yes (frontend + `routes/skills.py`) | not game data |
| Factions, constellations/prophecies, woven echoes, champions, arena, shrines, memories, harbingers, tombs, omens, primal hunt, cocoons, time beast, echo chains, corruption config, idol altar properties, crafting materials / glyph replacement, property definitions, caches/chests/rewards/shard drops | present (03 §4: 19 tables) | **0** | 0 (`corruption_scaling` deferred) | crafting/FP: hand-authored `crafting_rules.json`, `forging_potential_ranges.json` | — | hand files only | — |

### 3.1 Entity coverage values (EC)

| Domain | Stage | Value | Denominator |
| --- | --- | --- | --- |
| Affixes | export | 1,112 / 1,112 = **100%** | `MasterAffixesList` single+multi |
| Affixes | Forge data/ (distinct) | 1,112 / 1,112 = **100%** (+116 duplicate records) | same |
| Affixes | v2 | 1,098 / 1,112 = **98.7%** (14 excluded) | same |
| Affixes | data_bundle | 0 / 1,112 = **0%** (BLOCK) | same |
| Item subtypes | export / data_bundle | 1,508 / 1,508 = **100%** | export subtypes (game list not separately enumerated) |
| Gear subtypes | v2 | 542 / 542 = **100%** of 23 gear types; 0 / 224 blessings, 0 / 47 lenses, 0 / 13 idol altars | export equippable subtypes by type |
| Curated base items | Forge `base_items.json` | 17 / 115 = **14.8%** of curated rows are real 1.4.6 subtypes; 17 / 898 = **1.9%** of equippable subtypes | export subtype `name`/`displayName` |
| Uniques | Forge data/ | 400 / 409 = **97.8%** | export visible uniques |
| Set items | Forge data/ | 44 / 59 = **74.6%** | export set items (sync output "44 updated, 15 new") |
| Skills | export | 184 / UNKNOWN | player-skill population not enumerable from repo (4,110 `Ability` includes monster abilities) |
| Allocatable skill nodes | production resolver | 2,186 / 3,783 = **57.8%** | export allocatable nodes (`maxPoints>0`) |
| Raw tree nodes | export | 4,471 / 4,548 = **98.3%** (3,919 skill + 535 passive + 17 unmatched; 77 weaver dropped) | `raw_skill_trees_from_game.json` |
| Weaver nodes | export | 0 / 77 = **0%** | raw `WeaverTree` |
| Passive nodes | Forge data/ | 535 / 535 = **100%** + 6 orphans | export |
| Actors | export | 239 / 1,020 = **23.4%** (upper-bound denominator) | `ActorData` instances |
| Quests | export | 147 / 169 = **87.0%** | `Quest` instances |
| Quests | Forge data/ | 2 / 147 = **1.4%** | export |
| Ailments | Forge data/ | 11 / 141 = **7.8%** | distinct export ailment ids |
| Monster mods | export | 4 / 31 = **12.9%** of timeline-referenced keys | distinct `monsterModKey` in `timelines.json` |
| Factions & the other 18 tables | export | **0%** | 03 §4 |

---

## 4. Relationship coverage (RC)

| Relationship | Resolving / total | RC |
| --- | --- | --- |
| unique/set item `baseType`+`subTypes` → `items.json` | 468 / 468 | 100% |
| set item `setId` → `set_bonuses.setId` | 59 / 59 | 100% |
| skill tree node `requirements[].nodeId` → node in same tree | 4,456 / 4,460 | 99.9% |
| passive node `requirements[].nodeId` → node in same tree | 235 / 254 | **92.5%** |
| timeline `blessingsPairs` ids → `blessings.subTypeID` | 224 / 224 | 100% |
| timeline difficulty slot blessings → blessings | 224 / 224 | 100% |
| timeline `mods`/`empoweredMods.monsterModKey` → `monster_mods.modKey` | 54 / 453 refs (4 / 31 distinct) | **11.9%** |
| quest `timelineId` → timeline | 33 / 33 | 100% |
| class/mastery ability path ids → skill `source_ability_path_id` | 65 / 91 refs (60 / 63 distinct) | 71.4% |
| skill → owning class/mastery (reachable from any class ref) | 60 / 184 | **32.6%** |
| mastery → skill list (`abilityPathIds`) | 0 / 20 masteries populated | **0%** |
| skill tree → skill | 136 / 137 trees | 99.3% |
| dungeon → dungeon modifiers | 0 / 3 dungeons have mods | 0% |
| Forge hand `skills.json` names → 1.4.6 skills | 162 / 179 | 90.5% (17 hand entries have no 1.4.6 skill) |
| Forge hand class base stats → export `classes.stats` (10 fields × 5 classes) | 25 / 50 equal | 50%. The other 25 match a level-1 derivation (`baseHealth 100 + healthPerLevel 10 = 110`; `enduranceThresholdPerHealth 0.2 × 110 = 22`; `250+5 = 255` stun avoidance; endurance 0.2 shown as 20). That derivation is undocumented. |

---

## 5. Field coverage (FC), export stage

Field sets (F) are deliberately minimal: identity, display, the core mechanical payload and the key relationship.

| Domain | F | FC | Weakest fields |
| --- | --- | --- | --- |
| Affixes (1,112) | id, name, displayName, type, tiers, property\|affixProperties, canRollOn, specialAffixType-known | 8,449 / 8,896 = **95.0%** | displayName 799/1,112; specialAffixType known 978/1,112 |
| Uniques+sets (468) | id, name, displayName, baseType, subTypes, mods, tooltipDescriptions, loreText | 3,144 / 3,744 = **84.0%** | displayName 168/468 (`name` often carries it); tooltip 314/468; mods 444/468 |
| Skills (184) | id, name, description, tags, skillTree, source_ability_path_id, damage direct | 1,084 / 1,288 = **84.2%** | damage direct 81/184; tree 136/184; source path 140/184 |
| Passive nodes (535) | id, name, stats, maxPoints, description, altText | 2,600 / 3,210 = **81.0%** | altText 127/535; description 333/535 |
| Masteries (20) | name, localizationKey, masteryAbilityPathId, abilityPathIds | 60 / 80 = **75.0%** | abilityPathIds 0/20 (and masteryAbilityPathId is 0 for the 5 base-class rows) |
| Equippable subtypes (898) | name, displayName, implicits, levelRequirement | 2,961 / 3,592 = **82.4%** | displayName 345/898 |

Forge-stage field loss (sync transform `scripts/sync_game_data.py:152-238`):
* Affix fields dropped: `displayName`, `morphology`, `titleType`, `displayCategory`, `uniqueId`, `weaponEffect`, `derivedTags`, `affixProperties`, `tiers[].extraRolls`. `specialAffixType` is collapsed to 0/1. Tags are empty on 799/1,228 Forge records.
* Tier values: **every** tier is multiplied by 100 (`sync_game_data.py:159-166`). For the 387 Forge equipment affixes whose game T1 value is at least 1 (flat values such as Added Health 5–15, stored as 500–1,500), only 32 are divided back by the `get_affix_value` heuristic (`backend/app/engines/stat_engine.py:592-631`: stat_key allowlist and T1 midpoint > 100). **355 remain at 100× game scale** (249 multi-property, 28 `AbilityProperty`, 19 `PlayerProperty`, 18 `Damage`, 10 `IdolAltarProperty`, ...). Whether each one reaches a stat is a Phase 4 question; the data-level scale error is certain.
* Timelines: 21 → 7 fields.
* `skills_metadata.json`: 5 synced fields + 4 hand-added fields (all null) that a re-sync deletes.

---

## 6. Semantic coverage (SC)

| Domain | Measure | Value | Status |
| --- | --- | --- | --- |
| All v2 bundles | `stable_calculable_count` / records | **0 / 8,711 = 0%** (every bundle summary reports 0; all records `support_status: partial`) | measured (self-reported by generator, reproduced) |
| Skills (damage) | skills with serialized direct `damageSources` | 81 / 184 = 44.0% (proxy; components are "partial serialized evidence", not formulas) | proxy only |
| Skill tree nodes | v2 `partial_modifier` classification | 31 / 3,919 = 0.8% (3,888 unsupported or text-only) | proxy |
| Passive nodes | v2 `partial_modifier` | 72 / 535 = 13.5% (463 unsupported or text-only) | proxy |
| Production skill-tree effects | nodes parsed from prose `description` after a pipe | 2,186 nodes reach a regex parser, 0 validated | **unmeasurable**: no ground truth or validator |
| Affixes | single-property affixes with decoded SP property + modifierType | 578 / 1,112 structurally typed; multi-property 534 typed in export but **0 / 534 second properties survive into Forge** | structural only |
| Unique special effects | interpreted mechanics | 0 (claimed in completeness audit; not contradicted) | unmeasurable |
| Item implicits | `subtypes_with_interpreted_implicit_mods` | 0 / 821 (claimed; implicits are serialized property/value rows) | — |
| Minions, ailment payloads, enemy abilities | — | **unmeasurable**: not extracted as mechanics | — |

Overall SC is **unmeasurable as a single number**. The repo has no validated mechanical model and no ground-truth fixtures (in-game tooltips or combat logs) to score against. The best available upper-bound proxy is 0% stable-calculable across all v2 records.

---

## 7. Reproduction of `reports/pipeline_completeness_audit_1.4.6.json` (claimed)

| Claim | Reproduced? | Note |
| --- | --- | --- |
| classes 5, fully extracted | count yes; "fully" **no** | mastery `abilityPathIds` empty 20/20 |
| items 50, subtypes 1,508, with implicits 821 | yes | |
| affixes 1,227 (1,112 equipment + 115 idol) | count yes; **meaning no** | 115 idol records duplicate equipment ids; distinct = 1,112 |
| equipment tiers 5,907, idol tiers 526 | yes | |
| unknown_tag_count 0 | yes for SP/AT | does not count `specialAffixType` value 6 (134 records) |
| uniques 409 + 59 = 468 resolved, 0 unresolved, mods 2,334, resolved implicits 459 | yes | 468/468 base links verified independently |
| skills 184; direct 81, runtime/mutator 29, none_found 74; damageSources 89 | yes (status counts) | |
| skill_tree_nodes 3,919; with stats 3,768; with requirements 3,720; skills_with_trees 136 | yes | 4 requirement edges dangle |
| passive nodes 535, with stats 535, with requirements 197 | yes | 19 requirement edges dangle |
| summoned: 33 skills / 54 actors; mutator hints 50 skills | yes | |
| ailments 143, blessings 224, loot tables 24, timelines 10 | yes | ailments contain `Ignite` ×3; loot tables file dates from 2026-03-30 |
| enemy/monster data 268 | yes (248 + 20) | actors file has no writer, 9 dups, pre-1.4.6 |

The audit's counts reproduce exactly. Its domain list **omits** weaver tree, factions, prophecies, woven echoes, champions, arena, shrines, memories, crafting materials, idol altars, corruption, property definitions and reward tables. So its "coverage" describes only what was exported, not what exists in the game.

---

## 8. Findings summary (for the consolidated ledger)

1. Production runs on pre-1.4.6 data that the committed sync cannot reproduce. Experimental v2 is 1.4.6 and reproducible.
2. Forge flattens all 534 multi-property affixes to one stat and multiplies flat tier values by 100. Only 32 of 387 are heuristically corrected.
3. Production simulation inputs (skills, class stats, mastery/keystone bonuses, base items, crafting/FP rules, enemies, weaver tree) are hand-authored or third-party. Curated base items are 85% non-game names.
4. 19 game data tables (factions, woven echoes, champions, corruption config, idol altars, crafting materials, property definitions, etc.) are never extracted. The weaver tree is decoded and then dropped.
5. Relationship holes: monster mods 4/31 keys, skill→class 60/184, mastery→skills 0/20, dungeon mods 0/3, 23 garbage requirement edges.
6. Validation is count-floor only (9/21 files). The completeness audit counts the 115 duplicate idol affixes as extra coverage.

---

## 9. UNKNOWNs

* Player-skill population in the game (needs an `AbilityList`/`KnownAbilityList` decode to separate player from monster abilities).
* The true generating inputs of committed Forge `data/` (export generation, hand edits). `le-the-forge` history is shallow (starts 2026-03-31) and `version.json` records only affixes.
* Whether the 6 Forge-only Acolyte passive nodes were removed in 1.4.6 or are an extraction miss. That needs the raw 1.4.6 `AcolyteTree` (raw shows 103 nodes, matching the export).
* Correct value for `specialAffixType` 6 (enum not in `enums.json`).
* Zone population (scene list not decoded; zones are localization-derived).
* Provenance of `frontend/src/data/raw/*` and `data/classes/skill_tree_nodes.json`.

## 10. What this does NOT prove

* Values are correct. EC, RC and FC measure presence and linkage, not numeric fidelity against the running game.
* The 19 missing tables matter equally. Relevance was judged by name.
* Field sets are complete contracts. They are minimal sets chosen for this audit, and a different F changes FC.
* The 100× affixes produce wrong DPS or EHP in production. Reaching a stat depends on `stat_key` mapping (Phase 4).
* Behaviour of `dev` (413 commits ahead of `main`).

## 11. Missing instrumentation

* Enumeration-based coverage gate: game tables in `resources_manifest` vs exported domains.
* Referential-integrity validator over exports (requirements, mod keys, class→skill, dungeon→mods).
* Per-file sync manifest in Forge (export sha → sync function → hand-edit flag), plus an idempotency test (`sync` then `git diff --exit-code data/`).
* Affix value-scale contract per property/modifierType, replacing the blanket ×100 and the T1>100 heuristic.
* Ground-truth fixtures (tooltip values per affix tier, per skill level) to make SC measurable.


---

<!-- FILE: 05_FIELD_LOSS_REPORT.md -->

# 05 — Field-Loss / Data-Loss Report (Phase 2D)

Audit date: 2026-10-06. Scope: field paths that exist in the extractor output and disappear (or are blanked, defaulted, or re-scaled) on the way to the planner.

Repos and revisions inspected:

| Repo | HEAD | Notes |
|---|---|---|
| `le-the-forge` | `1efcef7` (2026-05-14) | `data/version.json`: `patch_version: "unknown"`, `synced_at: 2026-04-26`, `files_updated: ["data\\items\\affixes.json"]` |
| `last-epoch-data` | `73e2ab0` (2026-05-31) | `exports_json/metadata.json`: `1.4.6_22986002`, `generated_at 2026-05-06` |

Read-only audit. No repo file was modified other than this report and `06_RELATIONSHIP_INTEGRITY.md`.

---

## 1. Method

1. A recursive path profiler (`scratchpad/fl/paths.py`) walks each entity and records every key path. List elements are written as `[]`, so `tiers[].extraRolls[].minRoll` is one path. For each path it counts (a) entities carrying the path and (b) entities where the value is non-empty (`None`, `""`, `[]`, `{}` count as empty).
2. `cmp.py A-expr B-expr depth` diffs two stages: paths only in A, paths only in B, paths present but always empty in B, and paths whose non-empty count drops.
3. Transform code was read line by line: `scripts/sync_game_data.py` (1543 lines), `scripts/generate_tree_data.py` (337 lines), `backend/app/game_data/pipeline.py`, `backend/app/domain/item.py`, `backend/app/utils/cli.py` (DB seeding), `backend/app/routes/ref.py` (API serializers), `backend/app/services/skill_tree_resolver.py`, `backend/app/services/passive_stat_resolver.py`, `backend/app/engines/stat_engine.py`, and the frontend TS data/types.
4. Consumers were found with grep for exact data paths (for example `"items", "affixes.json"` and `data/classes/passives.json`) across `backend/app`, `backend/data`, `backend/scripts` and `frontend/src`.

Stages, using the names from the brief:

| Stage | Location | Present for this audit? |
|---|---|---|
| S0 raw | `last-epoch-data/extracted_raw` | Not profiled field by field. It is out of scope for loss, because the exports are the first structured stage. |
| S1 export | `last-epoch-data/exports_json/*.json` | yes |
| S2 data_bundle | `last-epoch-data/data_bundle/families/*.json` | **Only 2 of the 15 content families exist** (`base_items`, `item_types`). The manifest lists 13 more as `deferred: true` and their files are missing. |
| S3 forge data | `le-the-forge/data/**/*.json` | yes |
| S4 v2 bundles | `le-the-forge/docs/generated/v2_*_bundle.json` | yes. Experimental only: `production_consumed: false` in every bundle. |
| S5 backend loaders/models | `pipeline.py`, `AffixDefinition`, `PassiveNode`, `AffixDef`, resolvers | yes |
| S6 API serializers | `routes/ref.py`, `routes/passives.py` | yes |
| S7 frontend | `frontend/src/types`, `lib/api.ts`, `lib/gameData.ts`, `data/skillTrees`, `data/passiveTrees` | yes |

**Important caveat: S3 is a stale snapshot.** `scripts/sync_game_data.py` reads `ROOT/last-epoch-data/exports_json` (line 21), and that directory does not exist inside `le-the-forge`. `data/version.json` shows that the last sync touched only `affixes.json`. Several S3 files have shapes that the current sync code would not produce, for example `data/progression/blessings.json` (nested timelines) and `data/classes/passives.json` (has `requires`, which `sync_passives` never emits). Losses are therefore tagged:

- **T (transform-induced):** the current code drops or rewrites the field. Re-syncing will not fix it.
- **D (drift/stale):** the field exists in the current export but not in the older S3 snapshot. Re-syncing would add it only if the transform passes it through.
- **C (curated replacement):** S3 holds hand-authored data in place of the export field, and the sync preserves the curated value instead.

---

## 2. Entity-count deltas S1 → S3

| Domain | S1 export | S3 forge | Delta | Tag |
|---|---|---|---|---|
| Skills (`skills_with_trees`) | 184 | 184 | 0 | — |
| Skill trees (with nodes) | 136 | 137 (`fs11` extra) | +1 | D |
| `skill_tree_nodes.json` trees / nodes (backend resolver source) | 136 / 3919 | 132 / 2190 | −4 trees, −1729 nodes | C |
| `skills_metadata.json` (name-keyed) | 184 skills | 161 entries | −23 (name collisions) | T |
| Passive nodes | 535 | 541 | +6 Acolyte nodes absent from the export (see REL report) | D/extraction |
| Affixes (equipment + idol) | 1112 + 115 | 1113 + 115 | +1 legacy entry kept | T |
| Uniques | 409 | 403 | −9 missing, +7 forge-only, 3-variant collapse | D+T |
| Set items / sets | 59 / 23 | 47 / 18 | −12 / −5 | D |
| Set bonuses | 45 (27 `kind:"mod"`, 18 `kind:"description"`) | 14 text-only | −31 | T+D |
| Equippable base types / subtypes | 42 / 898 | `items.json` 40 / 857; `base_items.json` 115 curated rows | −2 / −41; curated 115 | D+C |
| Blessings | 224 | 112 curated pairs | different schema | C |
| Ailments | 143 | 11 | −132 | D |
| Actors | 248 (9 exact duplicate ids) | 239 | −9 (dedupe) | T (correct) |
| Quests | 147 | 2 | −145 | D |
| Zones | 385 | 368 | −17 | D |
| Classes | 5 | 5 (different schema) | 0 | C |
| Localization files | 21 | 21 | Content differs in 19/21 files. `en.json` and `id_lookup.json` are identical (see §6). | D |

---

## 3. Domain-by-domain field loss

Column meanings: **N** = entities carrying the field at the source stage. **Lost at** = first stage where the field is gone. Class = REQUIRED_NOW / REQUIRED_FUTURE / UNKNOWN / SAFE_TO_IGNORE.

### 3.1 Affixes (S1 `affixes.json` → S3 `data/items/affixes.json` → S5 `AffixDefinition` / `AffixDef` → S6 `/api/ref/affixes` → S7 `AffixDef` TS)

The transform is `sync_affixes`, `scripts/sync_game_data.py:112-279`.

| Field (S1) | N | Lost at | Tag | Class | Evidence / note |
|---|---|---|---|---|---|
| `property` (stat/property id, single-property affixes) | 578 | S3 | T | REQUIRED_NOW | Not emitted in the `entry` dict (lines 213-236). Forge `stat_key` is a name slug for 1113/1113 equipment affixes. |
| `affixProperties[]` (`property`, `modifierType`, `tags`, `displayName`) | 534 (all 2-property) | S3 | T | REQUIRED_NOW | Dropped. The second stat of every hybrid affix is unrepresented. |
| `tiers[].extraRolls[]` (second-property ranges) | 534 | S3 **and S4** | T | REQUIRED_NOW | The S3 tier loop (line 161) reads only `minRoll`/`maxRoll`. The S4 v2 bundle has no `extraRolls` (grep count 0), and **366 second-property modifiers in `v2_modifier_registry.json` carry the first property's range** (see REL-7). |
| `tags` for 2-property affixes (inside `affixProperties`) | 534 | S3 | T | REQUIRED_NOW | Forge `tags` are non-empty for only 429/1228 rows. |
| `modifierType` for 2-property affixes | 534 | S3 | T | REQUIRED_NOW | Forge `modifier_type` is non-empty for only 578/1228 rows. |
| `specialAffixType` (7 values: Standard 766, `"6"` 134, IdolWeaver 66, Set 59, IdolEnchantment 49, Personal 26, Experimental 12) | 1112 | S3 (collapsed) | T | REQUIRED_NOW | Line 224 maps `"Standard"` to 0 and everything else to 1. Set, Personal and Experimental are no longer distinguishable. |
| `t6Compatibility` (Normal 1103, MaximumAffixEffectModifier 7, Incompatible 2) | 1112 | S3 (collapsed to bool) | T | REQUIRED_FUTURE | Line 210. `MaximumAffixEffectModifier` becomes `False`, the same value as `Incompatible`. |
| `specificRerollChances[]` (per-slot weighting) | 78 | S3 | T | REQUIRED_FUTURE (crafting odds) | Dropped. |
| `affixIDToConvertTo`, `convertOnIncompatibleItemType`, `lootFilterName` | 9 | S3 | T | REQUIRED_FUTURE | Dropped. |
| `displayName` (≠ `name` for 586) | 799 | S3 | T | REQUIRED_NOW (UI text) | Forge `name` is the internal name, for example "Freeze Rate Multiplier and Cold Resistance". |
| `derivedTags`, `displayCategory`, `morphology`, `titleType`, `weaponEffect`, `uniqueId`, `_extra.extraTag` | 1112 | S3 | T | UNKNOWN | No consumer. |
| Idol `tiers2[]` (second-property ranges) | 115 | S3 | T | REQUIRED_NOW (idol builds) | Only `tiers` is read. |
| Idol `tags`, `applicable_to` | 115 | S3 (defaulted) | T | REQUIRED_NOW | Line 179 reads `cur.get("tags", [])` with `cur` always `{}` for idols, because `existing_by_name` excludes idols (line 142). All 115 idol rows have `tags: []` and `applicable_to: ["idol"]`, even though S1 `canRollOn` holds IDOL_1x1…4x1. |
| Tier **scale** | 1112 | S3 (rewritten) | T | REQUIRED_NOW | Every tier is multiplied by 100 (line 161ff), including flat ADDED values. "Added Health" T1 goes from 5–15 to 500–1500; 187 equipment affixes have a top tier ≥ 1000. `stat_engine.get_affix_value` (`stat_engine.py:609-631`) undoes this only when the T1 midpoint is > 100, so **Strength/Intelligence/Dexterity/Attunement/Vitality (T1 = 100) are never divided** (T8 = 2400–2800). |
| S3 → S5 `AffixDefinition` keeps only `name, stat_key, type, applicable_to, tiers{tier,min,max}, affix_id` | 1228 | S5 | T | REQUIRED_NOW | `domain/item.py:72-99`. `tags`, `class_requirement`, `level_requirement`, `modifier_type`, `special_affix_type`, `reroll_chance`, `group`, `title`, `t6_compatible` and `rolls_on` are all dropped. |
| `class_requirement`, `tags` → DB `AffixDef` | 668 / 429 non-empty | S5 (blanked) | T | REQUIRED_NOW | `utils/cli.py:19-37` builds seed rows from `get_all_affixes()`, which returns `AffixDefinition.to_dict()`. That dict has no `class_requirement` or `tags`, so every seeded `AffixDef` row has `class_requirement=None, tags=[]`. |
| S6 `/api/ref/affixes` (DB path) | — | S6 | T | REQUIRED_NOW | `ref.py:280-289` returns `id` = DB autoincrement (not the game `affix_id`), `name`, `type` (experimental/personal normalised to prefix), `stat_key`, `applicable_to`, `tiers`, `tags`, `class_requirement`. Dropped: `affix_id`, `level_requirement`, `modifier_type`, `reroll_chance`, `special_affix_type`. |
| S7 TS `AffixDef` | — | S7 | — | — | `types/index.ts:305-313` has `id, name, type, applicable_to, tiers, tags?, class_requirement?`. This matches S6, so nothing more is lost. |
| v2 S4 `class_restrictions`, `mastery_restrictions`, `patch_version` | 1098 records | S4 (always empty) | T | REQUIRED_NOW / FUTURE | Path profile: `class_restrictions` is non-empty 0/1098, while S1 `classSpecificity` is class-specific for ~734. `patch_version` is empty 0/1098. |
| v2 S4 coverage | — | S4 | T | REQUIRED_NOW | 28 equipment affixes (rollsOn Equipment) are absent from the v2 affix bundle, for example 74 "Less Damage Taken on Block", 369, 699, 710, 781, and 1088-1101 (Idol Altar affixes). |

### 3.2 Skills (S1 `skills_with_trees.json` → S3 `skills_with_trees.json`, `skills_metadata.json`, `skill_tree_nodes.json` → S5 resolvers → S7 `skillTrees/index.ts`)

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| `damageSources[]` (+`damage.*`, `damageTags`, `isHit`, `addedDamageScaling`, …) | 81 skills | S3 | D | REQUIRED_FUTURE | Not in the S3 snapshot. S4 keeps the `damage_source_*` summaries. |
| `summonedActors[]` (+`abilities[]`, `actorId`) | 33 skills / 54 refs | S3 | D | REQUIRED_FUTURE (minion calc) | |
| `mutatorHints[]` | 50 | S3 | D | UNKNOWN | |
| `sourceIdentity.*`, `source_ability_path_id`, `source_tree_path_id` | 140 | S3 | D | REQUIRED_NOW | These are the only join keys for class→skill (see REL-9). |
| `damageSourceStatus`, `damageSourceNotes`, `_mName` | 184/40/184 | S3 | D | SAFE_TO_IGNORE (`_mName` is an engine name) / REQUIRED_FUTURE | |
| `description`, `altText`, `lore` non-empty | 176/147/2 | S3 drops to 154/123/1 | D | REQUIRED_NOW (UI) | |
| `skills_metadata.json` keeps only `id,name,description,lore,class` | 184 | S3 | T | REQUIRED_NOW | `sync_game_data.py:296-306`. Keyed by display name, so 12 duplicate names collapse (184 → 161) and the **last** variant wins (Anomaly → `an0mz` with no tree, not `an0my`). |
| `class` in `skills_metadata.json` | 161 | S3 (always `""`) | T | REQUIRED_NOW | Line 305 reads `skill.get("class", "")`, but S1 skills have no `class` key (0/184). 161/161 entries are `""`. |
| `base_damage_min/max`, `damage_scaling_stat`, `attack_type` | 161 | S3 (always null) | C | REQUIRED_NOW | 0/161 populated. The pipeline logs `populated_0g=0`. |
| Skill-tree node structured `stats[]` (`statName`, `value`, `property`, `tags`, `noScaling`, `downside`) | 3768 nodes / 6383 rows | S3 `skill_tree_nodes.json` | C | REQUIRED_NOW | The backend resolver source keeps `id,name,type,maxPoints,description` only. Stats are flattened into text after `|`: 3034 fragments, of which 906 (29.9%) map to `_STAT_LABEL_MAP`. |
| Skill-tree node `requirements[]`, `mastery`, `masteryRequirement` | 3720 | S3 `skill_tree_nodes.json` and S7 | C | REQUIRED_NOW | The resolver cannot validate prerequisites. The frontend keeps a single `parentId` (675 nodes have >1 valid prerequisite). |
| Skill-tree **nodes** themselves | 3693 non-root | S3 `skill_tree_nodes.json` keeps 2190 | C | REQUIRED_NOW | 1 of 132 trees fully covered. Lowest coverage: `sw42ih` Summon Wraith 4%, `sbf4m` 9%, `aa989` 13%, `rn7iv` 13%. Allocations on missing nodes are skipped with a debug-level log (`skill_tree_resolver.py:350-353`). |
| Skill-tree `effectHints[]` | 3784 | S3 | D | UNKNOWN | S4 keeps them as `modifier_rows` (10843). |
| `pointBonusDescription` (skill nodes) | 3919 | S1 already | — | SAFE_TO_IGNORE | Always empty in S1 (0/3919). |
| v2 `owner_class_ids` (skills/trees/nodes), `connections`, `modifier_references`, `required_points` | 184/136/3919 | S4 (always empty/0) | T | REQUIRED_NOW | All 184 skills have `owner_class_ids: []`. `required_points` is 0 for all 3919 nodes. `connections` and `modifier_references` are always `[]`. |

### 3.3 Passive trees (S1 `passive_trees.json` → S3 `passives.json` → S5 `PassiveNode` → S6 `/api/ref/passives`, `/api/passives`)

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| `stats[].property` | 1335 of 1406 rows non-zero | S3 | T | REQUIRED_NOW | `sync_game_data.py:479-482` keeps only `{key: statName, value}`. The resolver then maps by label text: 555/1416 rows (39.2%) map. |
| `stats[].tags`, `downside`, `noScaling` | 38 / 34 / 324 rows true or non-zero | S3 | T | REQUIRED_NOW (`downside` changes sign, `noScaling` changes per-point math) | |
| `noScalingType`, `noScalingPointThreshold` | 219 nodes non-zero | S3 | T | REQUIRED_NOW | |
| `altText`, `nodeDescription`, `pointBonusDescription`, `loreText` | 127/117/169/3 | S3 | T | REQUIRED_NOW (`pointBonusDescription`) / SAFE_TO_IGNORE (`loreText`: flavour) | |
| `requirements[].requirement` (points) | 197 nodes | S3 | T | REQUIRED_NOW | `sync_passives` emits `connections` only (line 466-476). The S3 `requires` field comes from `backend/scripts/merge_passive_edges.py`, so **re-running sync would delete `requires` for 190 nodes**. |
| `effectHints[]` | 535 | S3 | T | UNKNOWN | Kept in S4. |
| `ability_granted` | 541 | S3 always null | T | REQUIRED_FUTURE | `sync_game_data.py:485` reads `abilityGrantedByNode`, which is absent from S1. 0/541 non-null. |
| `node_type` | — | S3 (inferred) | T | UNKNOWN | Line 507: `"core" if maxPoints>1 else "notable"`. This is a heuristic with no source field. |
| `mastery` name | 541 | S3 (**wrong for 190 nodes**) | T | REQUIRED_NOW | Wrong `MASTERY_MAP` in `sync_game_data.py:326-329`. See REL-1. |
| S6 `/api/ref/passives` | — | S6 | T | REQUIRED_NOW | `ref.py:323-349` drops `stats`, `requires`, `mastery_requirement`, `mastery_index`, `icon`, `raw_node_id` and `ability_granted`. |
| S4 `modifier_references` | 535 | S4 always empty | T | REQUIRED_FUTURE | 0/535. |

### 3.4 Items / base items / implicits

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| Real subtype list (898 equippable subtypes, 610 non-equippable) | 1508 | S3 `base_items.json` | C | REQUIRED_NOW | The engine/API source (`base_engine.py:32`, `item_engine`, `/api/ref/base-items`) uses 115 curated rows. **98/115 names do not exist** in the export ("Rusted Coif", "Iron Helm", "Visored Helm", "Bascinet", …). |
| Subtype `implicits[]` (`property`, `value`, `maxValue`, `modifierType`, `tags`, `specialTag`; up to 3 per subtype) | 821 subtypes | S3 `base_items.json` | C | REQUIRED_NOW | Replaced by a free-text `implicit` string ("20-35 Armour"). `implicit_stats.json` holds one stat per slot, with `null` for ring, amulet and relic. |
| Subtype `classRequirement`, `subClassRequirement`, `attackRate`, `addedWeaponRange`, `levelRequirement` | 898 | S3 `base_items.json` | C | REQUIRED_NOW (`levelRequirement`, `classRequirement`, `attackRate`) | `level_req` in `base_items.json` is curated. |
| `items.json` subtype `_extra.*` (`affixEffectiveness`, `isCorruptedSubtype`, `IMSetOverrides`, …) | 898 | S3 | D | UNKNOWN (`affixEffectiveness`), SAFE_TO_IGNORE (loot-filter flags: these are UI/loot-filter only) | |
| Base type `IDOL_ALTAR` (13 subtypes), `UNUSED` | 14 | S3 `items.json` | D | REQUIRED_FUTURE | |
| Lens types (GREATER/ARCTUS/MESEMBRIA/EOS/DYSIS, 47 subtypes) and Idol Altar | 60 | S4 (no v2 bundle covers them) | T | REQUIRED_FUTURE | The `v2_item_base_bundle` excludes 17 base types. Idols (71) go to `v2_idol_bundle` and blessings (224) to none. |
| S2 `base_items.tags` | 1508 | S2 always empty | T | UNKNOWN | 0/1508 non-empty. `requirements.mastery` is 0/1508. `item_types.parent` is 0/50. |
| S4 `tags`, `attribute_requirements`, `mastery_restrictions`, `normalized_fields` | 542 | S4 always empty | T | UNKNOWN | |
| Sound/visual (`hitSoundType`, `uiItemSoundType`, `weaponSwingSound`, `gridSize`) | 898/42 | partly S4 | T | SAFE_TO_IGNORE | Presentation and audio only; no calculation semantics. |

### 3.5 Uniques (+ mods, legendary potential)

`sync_uniques`, `sync_game_data.py:860-948`.

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| `mods[]` numeric (`property`, `value`, `maxValue`, `modifierType`, `tags`, `canRoll`, `rollId`, `hideInTooltip`) | 385 uniques | S3 | C | REQUIRED_NOW | Lines 916-918 preserve curated `affixes` strings ("+20–80% increased Fire Damage"). 1517 string affixes; 8 uniques have a curated count ≠ visible export mod count (e.g. `alluvion` 8 vs 6, `hollow_finger` 2 vs 3). |
| `resolvedImplicitMods[]` | 400 | S3 | C | REQUIRED_NOW | Replaced by a curated `implicit` string. |
| `id` (unique numeric id) | 409 | S3 | T | REQUIRED_NOW | Keyed by slug of `displayName` (line 901). |
| `effectiveLevelForLP` | 201 | S4 and S7 | T | REQUIRED_NOW (legendary potential) | Present in S3 (192 non-null). Absent from the v2 unique bundle (grep 0) and from TS `UniqueItem` (`lib/api.ts:603-614`). |
| `isPrimordialItem`, `primordialCosts.*`, `isCocoonedItem`, `isPreCorrupted`, `validPreCorrupts`, `preCorruptPositiveChance` | 25/25/23/2/2/2 | S3; S4 partial | T | REQUIRED_FUTURE | |
| `tooltipDescriptions[].altText` | 151 | S3 | T | REQUIRED_NOW (UI) | Only `.text` is kept. |
| `levelRequirement` | 243 | S3 (`level_req` on 2) | T/C | REQUIRED_NOW | |
| `rerollChance`, `canDropRandomly` | 409 | S4 / S7 | T | REQUIRED_FUTURE | Not in the v2 bundle or the TS type. |
| Variant uniques (Scales of Eterra ×3, Pearls of the Swine ×3) | 6 | S3 (collapse) | T | REQUIRED_NOW | The slug collides and `out[slug]` is overwritten (line 929); only legacy `_2`/`_3` curated entries survive. |
| `legendaryType`, `droppableLegendaryAffixes` … | 409 / 1 | S7 | T | REQUIRED_FUTURE | Not in TS `UniqueItem`. |

### 3.6 Sets

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| Set bonus `kind:"mod"` → `mod{property,value,modifierType,tags,specialTag}` | 27 of 45 bonuses (17 sets) | S3 | T | REQUIRED_NOW | `sync_game_data.py:1040-1045` copies `b.get("text","")` only; mod-kind bonuses have no `text`. S3 has 14 bonuses in total, and 11/18 sets have `bonuses: []`. |
| Set items for set ids 19-23 | 12 items / 5 sets | S3 | D | REQUIRED_NOW | |
| Set item `mods[]` | 59 | S3 | C | REQUIRED_NOW | Curated `affixes` strings, as for uniques. |

### 3.7 Classes / masteries

| Field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| Per-level scaling: `healthPerLevel`, `manaPerLevel`, `healthRegenPerLevel`, `stunAvoidancePerLevel`, `enduranceThresholdPerLevel/PerHealth` | 5 | S3 + engine | C | REQUIRED_NOW | The engine reads `backend/app/game_data/classes.json` (hand-authored level-1 values: health 110 = 100+10). Values at other levels cannot be derived. |
| `baseMoreDoTDamageTaken`, `minionScaling{firstLevelForScaling, moreDamagePerLevel, lessDamageTakenPerLevel}` | 5 | S3 | C | REQUIRED_NOW (minion builds) | Absent everywhere downstream. |
| `masteries[].masteryAbilityPathId`, `abilities.{defaultPathIds,knownPathIds,unlockable[]}` | 5 | S3 | D | REQUIRED_NOW | Class→skill join keys. |
| `startingItems[]`, `_extra.*` (visuals, animation) | 5 | S3 | D | SAFE_TO_IGNORE | Starting gear is irrelevant to endgame planning; the rest is presentation. |
| `masteries[].abilityPathIds` | 5 | S1 always empty | — | UNKNOWN | 0/5 non-empty at the source. |

### 3.8 Blessings, ailments, monster mods, actors

| Domain / field | N | Lost at | Tag | Class | Evidence |
|---|---|---|---|---|---|
| Blessing `implicits[]` (`property`, `value`, `maxValue`, `modifierType`, `tags`) | 224 | S3 | C | REQUIRED_NOW | S3 is a curated 112-row normal/grand pair list. `stat_key` is non-null for 38/112, so 74 blessings are not simulated. One S3 name ("persistence of will") is not in the export. |
| Blessing → timeline mapping | — | S1 has none on the blessing side | — | UNKNOWN | Timelines reference blessing `subTypeID`. The S3 nesting is curated. |
| `sync_blessings` output schema (flat list with `stats`) | — | — | T | REQUIRED_NOW | Incompatible with the loader (`pipeline.py:125-135` expects nested `timeline.blessings`). Running sync would empty `blessings_flat`. |
| Ailment `damage{baseDamage.damage[7], crit…}`, `heal`, `spread`, `flags`, `description`, `rawTagBits` | 143 | S3 | T + D | REQUIRED_NOW (ailment DPS) | `sync_ailments` (614-672) keeps 10 scalar fields. S3 holds 11 ailments (Ignite, Poison, Shock, Chill, Frostbite, Electrify and others are missing). The engine uses constants (`constants/combat.py:21-33`), not data. |
| Monster mod `modKey`, `effectModifierCap`, `increasedItemRarity`, `increasedExperience`, `incompatibleWithChampions`, `rarityRequirement`, … | 20 | S3 | T | REQUIRED_FUTURE | No consumer of `data/combat/monster_mods.json`. |
| Actor duplicate rows | 9 | S3 (deduped) | T | SAFE_TO_IGNORE | The duplicates are byte-identical payloads. |

### 3.9 Localization

| Item | Finding | Class |
|---|---|---|
| Consumers | No backend or frontend code reads `id_lookup.json`, `affix_id_to_name.json`, `item_id_to_name.json`, `property_strings.json`, `skill_tree_strings.json`, `ability_strings.json` or `affix_strings.json` (grep across `backend/app`, `backend/data`, `frontend/src`). | REQUIRED_FUTURE |
| Drift | S3 vs S1: `property_strings` 1950 vs 2649 (827 only in the export); `affix_id_to_name` 5770 vs 6271 (82 changed); `skill_tree_strings` 20819 vs 21368. | D |
| Internal inconsistency in S1 | `en.json` and `id_lookup.json` are byte-identical to the older S3 copies while the other 19 files changed, so the export's `en.json` was not regenerated with the rest. | UNKNOWN |

---

## 4. Populated-but-always-empty / defaulted fields (all stages)

| Stage | Path | Non-empty / total |
|---|---|---|
| S1 | skill node `pointBonusDescription` | 0 / 3919 |
| S1 | `attributeScaling[].stats[].moreValues`, `levelScaling[].stats[].moreValues` | 0 / 128, 0 / 34 |
| S1 | class `masteries[].abilityPathIds` | 0 / 5 classes |
| S2 | `base_items.tags`, `requirements.mastery`; `item_types.parent` | 0/1508, 0/1508, 0/50 |
| S3 | `passives.ability_granted` | 0 / 541 |
| S3 | `skills_metadata.class` | 0 / 161 (`""`) |
| S3 | `skills_metadata.base_damage_min/max, damage_scaling_stat, attack_type` | 0 / 161 |
| S3 | idol affix `tags` | 0 / 115 |
| S3 | `blessings[].stat_key` | 38 / 112 |
| S4 | affix `class_restrictions`, `mastery_restrictions`, `patch_version` | 0 / 1098 each |
| S4 | affix `raw_reference.deterministic_modifier_data.gameplay_semantics` | 0 / 572 |
| S4 | passive node `modifier_references`, `patch_version` | 0 / 535 |
| S4 | skill `owner_class_ids` / tree `owner_class_ids` / node `owner_class_ids`, `owner_mastery_ids`, `connections`, `modifier_references` | 0/184, 0/136, 0/3919 |
| S4 | skill node `required_points` | always 0 (3919) |
| S4 | item base `tags`, `attribute_requirements`, `mastery_restrictions`, `normalized_fields`; unique `class_restrictions`, `implicit_ids`, `patch_version`, `requirements.class/mastery/attributes` | 0 / 542; 0 / 409 |
| S5 | DB `AffixDef.class_requirement`, `AffixDef.tags` (seeded via `get_all_affixes`) | always None / [] |

---

## 5. Transform code that silently subsets or defaults (catalogue)

| File:line | Pattern | Effect |
|---|---|---|
| `scripts/sync_game_data.py:21` | `SRC_DIR = ROOT / "last-epoch-data" / "exports_json"` | The directory does not exist inside `le-the-forge`, so sync cannot run as written and S3 stays stale. |
| `:161-167` | tier loop reads `minRoll`/`maxRoll` only, ×100 for all | `extraRolls` lost; flat values inflated ×100. |
| `:179-180` | idol `tags`/`applicable_to` from `cur`, always `{}` for idols | 115 idol affixes untagged and unslotted. |
| `:210`, `:224` | `t6Compatibility == "Normal"`; `specialAffixType == "Standard" ? 0 : 1` | Enum collapse. |
| `:213-236` | `entry` dict omits `property`, `affixProperties`, `displayName`, `specificRerollChances` | Stat identity lost. |
| `:264-273` | legacy affixes kept when the name is not in the export | 1 stale row keeps `affix_id` 417, colliding with a live affix. |
| `:296-306` | `skills_metadata` keyed by `name`; `class` defaults to `""` | 23 skills lost; class always empty. |
| `:324-330` | hard-coded `MASTERY_MAP` | 190 nodes mislabelled (REL-1). |
| `:466-476` | `connections` built from raw ids without an existence check | Would emit 19 dangling ids (export garbage ids). |
| `:479-482` | stats keep `statName`/`value` only | Property id, tags, downside, noScaling lost. |
| `:485`, `:507` | `abilityGrantedByNode` (absent) and node_type heuristic | Always null; inferred type. |
| `:614-672` | ailments keep 10 scalars | Damage, spread and heal lost. |
| `:901`, `:929` | uniques keyed by `_slugify(displayName)` | Variant collapse; numeric id lost. |
| `:916-918`, `:1021-1022` | curated `base`/`implicit`/`affixes` preferred | Numeric mods never imported. |
| `:1040-1045` | set bonus `text` only | 27 mod-kind bonuses become empty or absent. |
| `scripts/generate_tree_data.py:180-221` | builds `SKILL_NAME_TO_CODE` from `skill["id"]`, last-wins on name | The committed TS map is not reproducible from the current export (it points Anomaly→`an0mz`, Cinder Strike→`cinss`, variants with no tree). |
| `backend/app/domain/item.py:88-99` | `AffixDefinition.to_dict()` omits tags/class | Feeds DB seeding and `get_affixes_by_tag`, which always returns `[]` (`game_data_loader.py:76-80`). |
| `backend/app/game_data/pipeline.py:163-171` | name-keyed `affix_tier_midpoints` / `affix_stat_keys` | 222 rows with 98 duplicate names collapse (last wins). |

---

## 6. UNKNOWNs

- Whether the deployed database was seeded from the current `data/classes/passives.json` and `data/items/affixes.json`, and with `seed` (first-by-name dedupe) or `reseed-affixes`. UNKNOWN: no DB was available.
- Semantics of S1 `effectHints`, `noScalingType`, `overrideSprite`, `IMSetTier`, `titleType`, `morphology` and `_extra.affixEffectiveness`. UNKNOWN; classified accordingly.
- Whether the ailment `baseDamage.damage[]` values are per-second or total. Bleed export 53 vs `BLEED_BASE_DPS = 43.0`. UNKNOWN; listed in the REL report only.
- `extracted_raw` → `exports_json` loss was not profiled field by field (34 MB of mixed raw artefacts). UNKNOWN.

## 7. What this does NOT prove

- It does not prove which of two disagreeing values is correct in game. The export is treated as the authority because it is extracted from game files. Where the export itself is wrong (for example the 19 garbage passive requirement ids and the 6 missing Warlock nodes), the report says so.
- Count differences tagged **D** may be fixed by a re-sync. Losses tagged **T** will not be.
- It does not measure user-visible impact in a running UI; impact is inferred from code paths.
- S4 losses affect experimental endpoints only (`production_consumed: false`).

## 8. Reproduction

Scripts are in `<scratch>/fl/`, run with `python3 -I`: `paths.py`, `probe.py`, `cmp.py`, `aff.py`, `pas.py`, `pas2.py`/`pas3.py`, `st.py`, `stn.py`, `stn2.py`, `fe.py`, `uq.py`, `sets.py`, `act.py`, `cov.py`.

Example commands:

```
python3 -I cmp.py $E/skills_with_trees.json "d['skills']" $F/classes/skills_with_trees.json "d" 2
python3 -I probe.py $E/affixes.json "d['equipment']"
python3 -I cmp.py $E/items.json "[s for b in d['equippable'] for s in b['subTypes']]" $F/items/items.json "[s for b in d['equippable'] for s in b['subTypes']]" 3
python3 -I probe.py $G/v2_unique_bundle.json "d['records']['uniques']"
```

(`E=/home/user/last-epoch-data/exports_json`, `F=/home/user/le-the-forge/data`, `G=/home/user/le-the-forge/docs/generated`)


---

<!-- FILE: 06_RELATIONSHIP_INTEGRITY.md -->

# 06 — Relationship Integrity Report (Phase 4)

Audit date: 2026-10-06. `le-the-forge` HEAD `1efcef7`; `last-epoch-data` HEAD `73e2ab0` (export `1.4.6_22986002`). Read-only. Stage names (S1 export, S2 data_bundle, S3 forge `data/`, S4 v2 bundles, S5 backend, S6 API, S7 frontend) follow `05_FIELD_LOSS_REPORT.md`.

## 1. Method

- Every relationship was recomputed from data with throwaway scripts in `scratchpad/fl/` (`pas.py`, `pas2.py`/`pas3.py`, `st.py`, `stn.py`, `stn2.py`, `fe.py`, `uq.py`, `sets.py`, `act.py`, `cov.py`, `aff.py`) and run with `python3 -I`. The frontend TS literals (`frontend/src/data/skillTrees/index.ts`, `passiveTrees/index.ts`) were parsed with regexes.
- **Dangling** = a reference whose target id is absent in the same scope. **Orphan** = an id that nothing references or reaches. **Duplicate** = the same key appears twice in one keyed scope. **Ambiguous** = one key maps to several targets, or a lookup returns the first or last match silently. **Cycle** = DFS back-edge on `requirements` graphs.
- Fallback code was found by grep (`.get(..., "Unknown")`, `or 0`, `except …: pass`, `?? "Unknown"`, `?? 0`) and by reading each relationship's lookup site.

## 2. Summary table

| # | Relationship | Result | Count | Severity |
|---|---|---|---|---|
| REL-1 | mastery index → mastery name (S3 passives) | **Wrong mapping** | 190 / 541 nodes in 6 of 15 masteries | P0 |
| REL-2 | passive node → prerequisite (S1) | Dangling garbage ids | 19 / 254 edges (19 nodes, all 5 classes); 16 duplicate edges | P1 |
| REL-3 | passive tree completeness (S1/S4 vs S3/S7) | 6 Acolyte Warlock nodes missing from export | 6 nodes; 3 nodes' prerequisites point at them | P1 |
| REL-4 | skill name → backend skill tree (`skill_tree_nodes.json`) | Unresolvable by name | 9 trees named by raw code or old name; 4 trees absent | P1 |
| REL-5 | skill tree → nodes (backend resolver) | Partial | 2190 / 3693 non-root nodes (59%); 1/132 trees complete | P1 |
| REL-6 | skill name → id (`skills_metadata.json`, name-keyed) | Many-to-one collapse | 184 → 161; 12 duplicate names; 7 tree ids unmappable by the LE Tools importer | P1 |
| REL-7 | affix → second property → value range (v2 registry) | **Misattributed** | 366 / 384 second-property modifiers carry the first property's range | P1 (experimental) |
| REL-8 | affix `stat_key` → engine stat | Name-derived, mostly unmapped; scale heuristic | 132 / 1113 map; 6 inflated ×100 undetected | P0 (calc) |
| REL-9 | class → skill (v2 cross-ref) | Reported unresolved but resolvable | 63/63 "unresolved", 60 resolvable by `source_ability_path_id` | P2 |
| REL-10 | frontend skill name → tree code | Points to tree-less variants | 2 (Anomaly, Cinder Strike); 3 export trees absent; 5 stale nodes | P1 |
| REL-11 | frontend single `parentId` vs multi-prerequisite | Many-to-one assumption broken | 675 nodes with >1 valid prerequisite; 67 `parentId` not among export reqs | P2 |
| REL-12 | skill-tree prerequisite graph | Bidirectional edges (cycles by design) | 378 mutual pairs / 381 back-edges; 4 dangling; 3 self-loops | P3 (documentation) |
| REL-13 | unique → identity (slug key) | Variant collapse | 2 slugs × 3 variants; 9 export uniques missing; 7 forge-only | P2 |
| REL-14 | set → bonuses / members | Bonus mods dropped; 5 sets missing | 27/45 bonuses; sets 19-23 | P1 |
| REL-15 | item base → implicits; forge base names → game subtypes | Curated names not in game | 98 / 115 | P1 |
| REL-16 | item type ↔ affix eligibility vocabularies | 4 incompatible slot vocabularies | 22 affix slot tokens not in `base_items` keys; 6 inverse | P2 |
| REL-17 | `affix_id` uniqueness (S3) | Duplicate ids | 116 duplicated `affix_id`s (115 equipment/idol overlap + 1 legacy collision on 417) | P2 |
| REL-18 | affix name uniqueness (name-keyed dicts) | Collapse | 98 names / 222 rows | P2 |
| REL-19 | minion (summoned actor) → actor / ability → localization | Partial | 15/54 actor refs resolve to `actors.json`; 28/76 abilities to `ability_strings` | P3 |
| REL-20 | property enum → localization key | No explicit link | 35/100 property names have no normalised `Property_Master_*` match | P3 |
| REL-21 | ailment ids / names | Duplicate id and names | id 1 ×3 ("Ignite"); 4 names ×9 rows | P3 |
| REL-22 | `unmatched_trees.json` | Stale in forge | export 1 vs forge 27 (26 now matched) | P3 |
| REL-23 | DB-seeded affix class restriction | Blanked | `AffixDef.class_requirement` always None, so the class filter is a no-op | P1 |
| REL-24 | fallback code hiding failures | See §5 | 21 `.get(...,"Unknown")`, 34 `or 0`, 18 `except…: pass` (backend); 11 `?? "Unknown"`, 186 `?? 0`/`|| 0` (frontend) | P2 |

---

## 3. Findings with examples

### REL-1 Mastery index → name is wrong in `sync_game_data.py` (P0)

`scripts/sync_game_data.py:324-330` hard-codes:

```
"Mage":     {0: None, 1: "Sorcerer",    2: "Runemaster", 3: "Spellblade"},
"Primalist":{0: None, 1: "Shaman",      2: "Beastmaster",3: "Druid"},
"Sentinel": {0: None, 1: "Paladin",     2: "Forge Guard",3: "Void Knight"},
```

The export's own `masteryNames` (S1 `passive_trees.json`) and S1 `classes.json` both give Mage `[Mage, Sorcerer, Spellblade, Runemaster]`, Primalist `[Primalist, Beastmaster, Shaman, Druid]` and Sentinel `[Sentinel, Void Knight, Forge Guard, Paladin]`. `scripts/generate_tree_data.py:33-36` uses the correct order, as does the frontend (`passiveTrees/index.ts:610-640`).

- 190 / 541 `data/classes/passives.json` nodes carry the wrong `mastery`: Shaman↔Beastmaster 33+32, Runemaster↔Spellblade 32+30, Void Knight↔Paladin 32+31.
- Examples: `mg_32` "Arcane Warden" is labelled Runemaster, but the export and the frontend place it in Spellblade. `mg_33` "Elemental Affinity", `mg_34` "Elemental Strikes" and `mg_38` "Flame Walker" are mislabelled the same way.
- Impact path: `flask seed-passives` (`utils/cli.py:210-247`) writes the label into `PassiveNode.mastery`. `routes/passives.py:118-123` and `:163-169` filter with `PassiveNode.mastery == mastery`, so a request for Mage/Spellblade returns Runemaster's nodes.
- The v2 bundle is correct (0 mismatches).

### REL-2 Dangling passive prerequisites in the export (P1)

254 S1 requirement edges: 19 point to ids that do not exist in the tree, and 16 are duplicate edges.

| Tree | Node | Bad target |
|---|---|---|
| ac-1 | 20 "Invigorated Dead" | 1684808296038400 |
| ac-1 | 90 "Crimson Favors" | 507232 (forge: `ac_86`) |
| ac-1 | 94 "Rancid Concoction" | 459272 (forge: `ac_88`) |
| mg-1 | 39 "Warden's Echo" | 1806699467898880 |
| rg-1 | 98 | 1496589944225792 |

These propagate unchanged into S4: `v2_passive_tree_bundle` has 19 `edge_requirements` targeting `passive_node:ac_1:1684808296038400` and similar. S4 also has 5 dangling `connections` (`ac_1:53 → ac_1:86`, `ac_1:90 → ac_1:86`, `ac_1:94 → ac_1:88`). The current `sync_passives` would emit `ac_1684808296038400`-style connection ids without any existence check (`sync_game_data.py:466-476`). The CLI seed only warns (`cli.py:207`). There are no cycles in any passive tree; roots without requirements are 64-70 per class.

### REL-3 Six Acolyte Warlock nodes missing from the export (P1)

S3 and S7 contain Acolyte nodes 86 "Cauldron of Blood", 88 "Vile Tide", 97 "Infernal Lash", 98 "Chains of Ruin", 101 "The Ashen One" and 103 "Scorched Reach". S1 and S4 do not (Acolyte: 103 export nodes vs 109 frontend nodes). The garbage ids in REL-2 sit exactly where these nodes are expected: `ac_90` requires `ac_86` in forge but 507232 in the export, and `ac_110` requires `ac_101` in forge but 504457 in the export. This is an extraction gap, not a forge transform issue.

### REL-4 / REL-5 Backend skill tree resolver lookups (P1)

`skill_tree_resolver.get_tree_for_skill` (`:159-166`) matches by lowercase `skill_name` over `data/classes/skill_tree_nodes.json`.

- Nine trees carry a raw code or an old name as `skill_name`: `an0my`→"an0my" (Anomaly), `f1b4d` (Firebrand), `cstri` (Cinder Strike), `htsk5` (Heartseeker), `fl44` (Flay), `sh4re` (Shadow Rend), `bl5st` (Bladestorm), `si4lgl` "sigils of hope" (export "Symbols of Hope"), `ssc50` "summon storm crow" (export "Summon Storm Crows"). All nine names exist in `backend/app/game_data/skills.json`, so these skills compute with **zero** tree bonuses. The only signal is a warning log (`:334-337`).
- Four trees are absent entirely: `dqv5` Dark Quiver, `tb47` Ice Thorns, `is58` Ice Ward, `md26kh` Mark For Death.
- Node coverage is 2190 of 3693 non-root export nodes. Unknown node ids are skipped at **debug** level (`:350-353`). Examples: `sw42ih` Summon Wraith 4%, `sbf4m` Swarmblade Form 9%, `aa989` Aerial Assault 13%.

### REL-6 `skills_metadata.json` name-keyed collapse (P1)

184 skills collapse to 161 entries; 12 display names are duplicated in S1 (variants). The last row wins, and that row is the tree-less variant:

| Name | `skills_metadata` id | Real tree id |
|---|---|---|
| Anomaly | `an0mz` | `an0my` |
| Teleport | `fl45` | `te44` |
| Umbral Blades | `na28` | `ub5d9` |
| Rive | `sndr1-` | `sndr1` |
| Dancing Strikes | `dacn37` | `dacn33` |

`lastepochtools_importer._get_skill_id_map` (`:83-102`) inverts this map, so 7 real tree ids (`an0my, cstri, dacn33, ds34l, sndr1, te44, ub5d9`) fall back to the raw code (`:876`, recorded in `missing_fields`). The Maxroll importer works around the problem explicitly (`maxroll_importer.py:74-120`). The S1 skill "Detonate Decoy" has `id: ""`.

### REL-7 Affix second-property value ranges misattributed in v2 (P1, experimental)

For the 534 two-property affixes, the export stores the second property's ranges in `tiers[].extraRolls`. `v2_affix_bundle.json` has no extraRolls (grep 0). `v2_modifier_registry.json` emits a modifier row per property but gives both rows the primary range: in 366 of 384 checked second-property rows the range differs from extraRolls.

| affix_id | Affix | 2nd property | v2 range | export extraRolls range |
|---|---|---|---|---|
| 14 | Freeze Rate Multiplier and Cold Resistance | ColdResistance | 0.2–7.0 | 0.05–0.36 |
| 29 | Health and Stun Avoidance | StunAvoidance | 12–234 | 40–1500 |
| 42 | Lightning Damage And Leech | HealthLeech | 3–45 | 0.03–0.6 |
| 67 | Freeze Rate and Freezing Concoction on Potion Use | PlayerProperty | 0.2–8.0 | 1.0–2.0 |
| 75 | Ward and Ailment Cleansing on Potion Use | PlayerProperty | 20–500 | 1.0–1.0 |

### REL-8 Affix → engine stat relationship (P0 for calculation)

- `stat_key` is a slug of the affix name for 1113/1113 equipment affixes (`sync_game_data.py:220`). Only 132 equal a `BuildStats` field or a composite key. The other 981 are silently ignored: `stat_engine._apply_stat_key` has no `else` branch (`:548`), and `apply_affix` returns early on an unknown key (`:493-495`).
- The modifier bucket is inferred from the key suffix, not from `modifierType` (`stat_engine.py:485-504`). For mapped affixes, export ADDED → `_pct` bucket happens 10 times and INCREASED → flat bucket 8 times.
- ×100 tier scaling with a compensating heuristic (`get_affix_value`, `:609-631`, divides only when the T1 midpoint is > 100) misses "Strength", "Intelligence", "Dexterity", "Attunement" and "Vitality" (T1 = 100, T8 = 2400–2800). It also misses "Level of All Skills and Added Mana", which has `stat_key` `max_mana` while its value comes from the "+1 level" property. Path: `aggregate_stats` (`:727-736`) → `apply_affix` → `get_affix_value`.

### REL-9 Class → skill links (P2)

`v2_skill_bundle.cross_reference`: `class_mastery_skill_link_count 63, resolved 0`. Against S1 `skills_with_trees[].source_ability_path_id` (140 skills, no duplicates), 60 of the 63 class/mastery ability path ids resolve. Examples: `260926`→Evade, `263799`→Rip Blood, `262912`→Lightning Blast. `261142` and `263498` do not resolve. All 184 v2 skills and 136 v2 trees have `owner_class_ids: []`. S3 `skills_metadata.class` is `""` for 161/161 entries. The only class→skill source in production is the hand-maintained `CLASS_META` in `routes/ref.py:74`.

### REL-10 Frontend skill-tree name map (P1)

`frontend/src/data/skillTrees/index.ts:16` `SKILL_NAME_TO_CODE` has 132 entries.

- "anomaly"→`an0mz` and "cinder strike"→`cinss` point at tree-less variants. `SKILL_TREES` has `an0my`/`cstri`, but `getSkillTree("Anomaly")` resolves to `[]` (`:4296-4302`).
- 9 entries disagree with the current export id or name, for example "runic bolt"→`fb8fe` (export name "Runebolt"), "summon mage"→`sm4g` (export "Summon Skeletal Mage") and "sigils of hope"→`si4lgl`.
- Export trees missing from the frontend: `tb47`, `is58`, `md26kh`.
- Frontend nodes absent from the export: `bh2:23`, `ss3tre:28,30`, `flur3:17`, `ch4bo:9`.
- Skill-tree layout coverage is complete: 0 export nodes lack layout.

### REL-11 Single `parentId` vs multi-prerequisite (P2)

`PassiveNode`/`SkillNode` TS has one `parentId` (`lib/gameData.ts:291-306`). In S1 skill trees, 675 nodes have more than one valid prerequisite. 67 frontend `parentId`s are not among the node's export requirements, for example `ms26:3` parent 2 (export: none), `gs15de:8` parent 22 and `va53st:9` parent 13. Passive trees carry `parentIds[]` in `passiveTrees/edges.ts`, so the problem is confined to skill trees.

### REL-12 Skill-tree "cycles" (P3)

381 DFS back-edges were found, but 378 are mutual pairs. Example: `ab0lh` 16 "Sanguine Eruption" requires 14, and 14 "Embrace the Darkness" requires 16. This is the game's OR-adjacency semantics, not corruption. Any consumer that assumes a DAG or a single parent will break. Real defects: 4 dangling edges (`flur3` 3→431549, `flur3` 12→431549, `fb8fe` 28→264015, `wo42` 0→243279) and 3 self-loops on root nodes (`wo42` 0→0).

### REL-13 Unique identity (P2)

`sync_uniques` keys entries by `_slugify(displayName)` (`sync_game_data.py:901`). "Scales of Eterra" ids 195/196/197 (Fire Cold / Cold Lightning / Fire Lightning) and "Pearls of the Swine" ids 374/375/376 collide on one slug each, and the last one overwrites the others. Curated `_2`/`_3` entries survive only because legacy entries are preserved. Nine export uniques are missing from S3 (`artifice_of_devastation`, `ash_wake`, `exulis`, `laups_path`, `natural_wrath`, …). Seven S3 keys are not in the export (`egg_of_the_forgotten`, `heirloom_of_light`, `sharktooth_saw`, …). For the 380 S3 uniques with a `base`, the base matches the export's `resolvedBaseItem` with 0 mismatches. In S4, 400/409 uniques have `base_item_id`.

### REL-14 Set → members / bonuses (P1)

- S1: 23 sets / 59 items / 45 bonuses; setId 0 has a bonus record and no items (an orphan).
- S3 `set_items.json`: 18 sets / 47 items. 11 sets have `bonuses: []` (3, 5, 6, 8, 9, 11, 13-17) because the 27 `kind:"mod"` bonuses carry no `text` (`sync_game_data.py:1040-1045`).
- No dangling `items` slugs in S3. S4 has 0 dangling `set_group_id`s and every set has bonuses.

### REL-15 Item base → implicits (P1)

`data/items/base_items.json` (consumed by `base_engine.py:32`, `item_engine`, `/api/ref/base-items`): 98 of 115 names do not match any export subtype `name`/`displayName`. Examples: "Rusted Coif", "Iron Helm", "Visored Helm", "Bascinet", "Ruined Tunic". The export's helmets are "Refuge Helmet", "Jewelled Circlet", "Iron Casque" and others. Implicits are free-text strings, so there is no subtype → implicit row relationship. S2 and S4 do link implicits structurally: `implicit_refs` on 821/1508 S2 records, `implicit_ids` on 541/542 S4 records.

### REL-16 Slot vocabularies (P2)

| Source | Tokens (examples) |
|---|---|
| affix `applicable_to` (S3) | `helm, chest, sword_1h, sword_2h, axe_1h, mace_2h, spear, idol_2x2 …` (36) |
| `base_items.json` keys | `helmet, body, sword, axe, mace, two_handed_spear …` (20) |
| `item_types.json` | `helm, chest, sword, polearm, idol_1x1 …` (25) |
| `implicit_stats.json` / `crafting_rules.base_item_fp` | `helmet, body, focus, default …` |

There are 22 affix tokens not in `base_items` keys and 6 the other way round. The bridging is ad-hoc and spread across `constants/item_type_to_slot.py`, `gear_upgrade_ranker.py:44-45`, `lastepochtools_importer.py:198, 1005` and `ref._normalize_slot`. `affix_engine.is_affix_valid_for_item` (exact membership) has no callers.

### REL-17 / REL-18 Affix id and name uniqueness (P2)

- `affix_id` in S3: the 115 idol-section ids overlap equipment ids. `game_data_loader.get_affix_by_id` (`:83-88`) returns the first match, which is always the equipment row. The legacy row "Acolyte Increased Projectile Speed With Marrow Shards And Bone Nova" keeps `affix_id` 417, which now belongs to "Acolyte More Damage Over Time to Bleeding Enemies for Marrow Shards".
- Names: 98 names cover 222 rows (17 among equipment). Affected structures are `pipeline.affix_tier_midpoints` / `affix_stat_keys` (name-keyed, last wins) and the `seed` command (`cli.py:84-85`, `filter_by(name=…).first()`, first wins). Examples: "Idol Increased Critical Strike Chance" ×2, "Idol Dodge Rating and Increased Dodge Rating" ×2.

### REL-19 Minions (P3)

54 `summonedActors` refs (32 distinct actors) across 33 skills. 15 resolve to `actors.json` by `actorId` (that file is mostly enemies). All 76 minion abilities are `resolved`, but only 28 of their `resolvedAbilityName`s exist in `ability_strings.internalName`. No minion data reaches S3, S5 or S7.

### REL-20 Property → localization (P3)

There is no explicit key. Of 100 property enum names used by affixes, uniques and implicits, 35 have no normalised `Property_Master_<name>_Name` match, for example `Armour`, `CriticalChance`, `CriticalMultiplier`, `CritAvoidance` and `AbilityProperty`. Passive and skill-tree `stats[].property` are integers with no lookup table in the exports. Localization files have no consumer (see LOSS report §3.9).

### REL-21 Ailments (P3)

S1 has ailment id 1 three times, all named "Ignite", and 4 display names spread over 9 rows (Ignite ×3, Abyssal Decay ×2, Aspect of the Shark ×2, Bone Curse ×2). `sync_ailments` slugs by display name. The engine does not reference ailment ids at all: it uses constants such as `constants/combat.py:21-33` (`BLEED_BASE_DPS = 43.0` vs export Bleed `baseDamage` 53; the semantics are UNKNOWN).

### REL-22 `unmatched_trees.json`

- S1 `exports_json/unmatched_trees.json`: **1** entry, `fs11` "FireShieldSkillTree" / "Fire Shield Skill", 17 nodes. `community_skill_trees` labels it "Pyre Golem InfernalAura", so it is a minion ability tree, not a player skill.
- S3 `data/classes/unmatched_trees.json`: **27** entries from an older export (ArcaneAscendanceTree, BlackHoleTree, DisintegrateTree, …). 26 of them are now matched in the export, and all 27 exist in S3 `skills_with_trees`.
- Neither file has a consumer (grep: none). S3 still carries `fs11` as a tree in `skills_with_trees.json` and the frontend layout.
- Related: `community_skill_trees` (S1 138, S3 140) also contains the 5 passive-tree ids `ac-1, kn-1, mg-1, pr-1, rg-1` and lacks `bl5st`, `fl44`, `htsk5`, `sh4re` (S3 lacks `fl44`, `htsk5`).

### REL-23 DB-backed affix API loses class restriction (P1)

The `seed` / `reseed-affixes` commands (`utils/cli.py:19-37, 84-94, 110-119`) build rows from `get_all_affixes()`, which returns `AffixDefinition.to_dict()` (`domain/item.py:88-99`, no `class_requirement` or `tags`). Every DB row therefore has `class_requirement=None, tags=[]`. In `/api/ref/affixes` (`ref.py:261`) the condition `if class_req and a.class_requirement and …` never excludes anything, so class-specific affixes (668 in S3) are offered to every class, and `?tag=` filtering returns nothing. The same root cause makes `game_data_loader.get_affixes_by_tag` (`:76-80`) always return `[]`.

---

## 4. Duplicate / orphan / circular summary

| Category | Count | Examples |
|---|---|---|
| Duplicate ids | actors 9 (identical payloads; deduped in S3); ailment id 1 ×3; S3 `affix_id` 116 | -1449057912, 297012611 (actors); 417 (affix) |
| Duplicate names used as keys | skills 12 names; affixes 98 names / 222 rows; uniques 2 slugs × 3; ailments 4 names | Anomaly, Teleport, Scales of Eterra, Ignite |
| Dangling | passive prereqs 19; skill-tree prereqs 4; v2 passive connections 5; v2 passive edge_requirements 19; frontend name→code 2 | see REL-2, REL-10, REL-12 |
| Orphans | set bonus setId 0; forge `unmatched_trees` (27, unused); localization files (7 unused); `data/combat/monster_mods.json`, `ailments.json`, `world/*` (no consumer) | — |
| Circular | passive 0; skill trees 381 back-edges (378 mutual by design), 3 self-loops | `ab0lh` 14↔16, `aacfl` 6↔7 |
| Broken 1:1 / many:1 assumptions | single `parentId` (675 nodes); `skills_metadata` by name; affix name dicts; unique slug; `get_affix_by_id` first match | — |

## 5. Fallbacks that hide failures (selected)

| File:line | Pattern | What it hides |
|---|---|---|
| `routes/ref.py:206-215` | `except Exception: … return ok(data=[])` | DB and JSON failure both answer 200 with an empty list. |
| `routes/ref.py:229-235`, `routes/passives.py:126-128`, `:145-147`, `:173-175` | DB exception → `[]` → seed-file fallback or empty | Missing DB seed is indistinguishable from "no data". |
| `skill_tree_resolver.py:334-337`, `:350-353`, `:601-605` | missing tree → empty result (warning); missing node → debug log; `except Exception: return []` | REL-4/5. |
| `passive_stat_resolver.py:374-377`, `:407-414` | unknown node ids skipped (warning); unmapped stat → `special_effects` | 60.8% of passive stat rows are not added to stats. |
| `stat_engine.py:493-498`, `:548` | unknown `stat_key` → return / no else | 981 affixes contribute nothing. |
| `stat_engine.py:624-631` | ×100 heuristic | REL-8. |
| `lastepochtools_importer.py:876` | `skill_id_map.get(tree_id, tree_id)` | Raw code used as skill name (partly surfaced in `missing_fields`). |
| `game_data_loader.py:25-36`, `affix_engine.py:44-52` | `except RuntimeError: pass` → load a private pipeline | A second, unregistered data copy outside the app context. |
| `pipeline.py:467-471` | `_detect_version` returns `"unknown"` because `affixes.json` is a list | `data_version` is always "unknown". |
| `frontend/src/data/skillTrees/index.ts:4296-4302` | `SKILL_TREES[code] ?? []` | An empty tree looks the same as "skill has no tree". |
| `frontend …/ImportPanel.tsx:33`, `crafting/BaseItemSelector.tsx:36,47` | `?? "Unknown"` | Missing class or name displayed as "Unknown". |

Counts (non-test): backend `.get(x, "Unknown"/"unknown…")` 21, `or 0` 34, `except …:` followed by `pass` 18. Frontend `?? / || "Unknown…"` 11, `?? 0 / || 0` 186.

## 6. UNKNOWNs

- Whether production DB rows match the current `data/` files (REL-1 and REL-23 impact assume seeding from the current files).
- Whether the S1 garbage requirement ids (REL-2) and missing Warlock nodes (REL-3) come from a specific extractor version; extractor code was not traced.
- Game semantics of ailment `baseDamage` (per-second vs total) and of skill-tree requirement OR-semantics. Inferred from data shape, not verified in game.

## 7. What this does NOT prove

- It does not run the app or the DB, so API impact is derived from code paths and current files.
- It does not prove the export is complete or correct. REL-2 and REL-3 show export-side defects, and others may exist.
- The cycle analysis treats `requirements` as directed prerequisite edges. The OR/adjacency interpretation (REL-12) is an inference.
- S4 issues (REL-7, REL-9) affect experimental artefacts only (`production_consumed: false`).

## 8. Reproduction

```
cd <scratch>/fl
python3 -I pas.py; python3 -I pas3.py      # passive edges, dangling, cycles, v2 edges
python3 -I st.py; python3 -I stn.py; python3 -I stn2.py   # skill-tree id sets, resolver coverage, cycles
python3 -I fe.py                            # frontend skill tree map/parentId vs export
python3 -I uq.py; python3 -I sets.py; python3 -I act.py; python3 -I aff.py; python3 -I cov.py
grep -rnE --include=*.py "\bor 0(\.0)?\b" backend/app | grep -v /tests/ | wc -l
```

Inline one-off checks (mastery mismatch, v2 registry second-property ranges, class→ability path ids, affix stat_key coverage) are recorded in the session commands and summarised above.


---

<!-- FILE: 07_PATCH_DRIFT_REPORT.md -->

# 07 — Patch / Game Version Drift Report

Audit date: 2026-10-06
Scope: Phase 5 (patch / game version drift) across `le-the-forge`, `last-epoch-data`, and `le-parser`.
Mode: read-only. No repository files were modified other than this report. Scratch work lived outside the repositories.

---

## 1. Headline

| Question | Answer | Confidence |
|---|---|---|
| Current live Last Epoch version (2026-10-06) | **1.5.x, Season 5 "Rage of the Frostborn"**, launched 2026-10-01; hotfix 1.5.1 on 2026-10-02 (a 1.5.1.2 hotfix dated 2026-10-05 is reported by one aggregator) | Medium (web search snippets only — direct fetches of official pages were blocked by the egress proxy) |
| Newest extraction anywhere | `last-epoch-data/exports_json` = **1.4.6 build 22986002**, generated 2026-05-06T00:03Z | High |
| Data the production Forge runtime reads (`le-the-forge/data/`) | **Pre-1.4.6** (matches the 1.4.3-snapshot exports from 2026-04-25 to 2026-05-01); stamped `"patch_version": "unknown"` | High |
| Patch the Forge claims to track | `/api/version` → `"1.4.3"`, season `4` (hard-coded defaults) | High |
| Can a fresh extraction run in this environment | **No** — Windows, a local game install, .NET tools and UnityPy are all required; no 1.4.6 or 1.5 game snapshot exists in the repository | High |
| Automated patch-diff / schema drift gate | **None** blocking. Only count/shrinkage/top-level-key checks; unknown-value detection exists as a non-gating diagnostic | High |

Net effect: the Forge's production data trails the live game by one patch cycle plus at least five patches (1.4.6 → 1.4.7 → 1.5.0 → 1.5.1 → 1.5.1.x). The extractor's newest output trails by the 1.4.7 hotfix and the whole of Season 5.

---

## 2. Method and commands

All commands ran read-only. Copies used for execution went to the scratchpad.

```bash
# provenance files
cat le-the-forge/data/version.json
cat last-epoch-data/exports_json/metadata.json last-epoch-data/data_bundle/metadata.json
# history (shallow clone deepened read-only)
git -C last-epoch-data fetch --depth=1000 origin main
git -C last-epoch-data log origin/main --format='%h %ci %s' -- exports_json/metadata.json exports_json/affixes.json extracted_raw/enums/enums.json schemas data_bundle
git -C le-the-forge log --format='%h %ci %s' -- data data/version.json
# re-run the Forge sync transform on historical extractor outputs, in a scratch root
python3 -I scratch/fakeroot/scripts/sync_game_data.py --affixes   # one run per LED commit bb4ab10, e32d3f8, 419603d
# record count drift across LED commits
git show <commit>:exports_json/<file>.json | python3 -c '...count lists...'
# validators on a scratch copy of last-epoch-data
python3 tools/scripts/validate_exports.py
python3 tools/scripts/validate_data_bundle.py
python3 tools/scripts/validate_bootstrap.py
python3 tools/scripts/validate_affix_tag_categories.py
# hard-coded patch strings
grep -rnoE "(patch|version)[^\n]{0,20}\b1\.[234](\.[0-9]+)?\b" backend/app frontend/src
# web: WebSearch for Last Epoch patch notes 2026 (sources in section 9)
```

---

## 3. Version provenance by data store

| Store | Location | Declared version | Generated / last changed | How provenance is stored | Verdict |
|---|---|---|---|---|---|
| Forge runtime static data | `le-the-forge/data/**` (52 files) | `data/version.json`: `"patch_version": "unknown"`, `synced_at 2026-04-26T01:32:48Z`, `files_updated: ["data\\items\\affixes.json"]` | Last data commit `d0016c5` 2026-04-25 (affixes); most other files 2026-03-31 to 2026-04-21 | One stamp file; no per-file version. Only `set_items.json` and `uniques.json` carry a `_meta`, and neither has a patch | **Stale, unlabeled.** Effectively 1.4.3-snapshot era (section 4) |
| Forge v2 bundles | `le-the-forge/docs/generated/v2_*_bundle.json` (11 bundles) | No patch string anywhere (`grep '"1.4.x"'` = 0 hits). 6 of 11 carry `gameAssemblySha256 d4a68f3f…`, which equals the 1.4.6 metadata hash | `generated_on 2026-05-12` | SHA only, nested under `source_metadata.game_build`; `v2_affix_bundle.json` holds only `source_bundle_path: D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json` | 1.4.6 by hash inference. Experimental, not consumed by the stable planner (`metadata.production_safe: false`) |
| Frontend bundled tree data | `frontend/src/data/raw/*.json`, `frontend/src/data/skillTrees/index.ts`, `frontend/src/lib/gameData.ts` | `gameData.ts:8` "In-game data from patch 1.2.x"; icon atlas `planner_skill_passive_icons_v142.webp` | raw JSON 2026-03-31; `gameData.ts` 2026-04-15; atlas 2026-04-08 | Comments and file names only | Mixed: hand-maintained plus pre-1.4 raw layouts. `skill-tree-metadata.json` (133 trees) has 0 hits for "Bladestorm" (a 1.4.0 skill), although `skillTrees/index.ts` has it |
| Extractor exports | `last-epoch-data/exports_json/*.json` | `metadata.json`: 1.4.6 / build 22986002 / Unity 6000.0.42f1 / sha d4a68f3f… | 2026-05-06T00:03Z (commit `c0a0d55` 2026-05-05 20:07 -0400) | Dedicated `metadata.json` plus per-file `_meta.game_build` (sha, Unity) | Consistent internally. Current as of May 2026 |
| Extractor canonical bundle | `last-epoch-data/data_bundle/` | `game_version 1.4.6`, `data_patch 1.4.6`, `bundle_id …-1.4.6-22986002-phase1a`, **`extractor_version: null`** | 2026-05-07 | `metadata.json` plus source hashes | Consistent with exports. Extractor version is unrecorded |
| Extractor enum table | `last-epoch-data/extracted_raw/enums/enums.json` | none in `meta` (only source DLL list, 354 enums) | last commit `853b053` **2026-04-10** ("data: patch 1.4.3_22682302") | none | **Not regenerated for 1.4.6** in git (section 6.2) |
| Patch snapshots | `last-epoch-data/patch_versions/` | `1.3.7.1_22373561`, `1.4.3_22682302` | `359f354` 2026-04-10 | Directory names | **No 1.4.6 or 1.5 snapshot** |
| Archived JS parser | `/home/user/le-parser` | none | single commit `5135ce4` 2026-03-26 | none | Abandoned. Predates 1.4 |

### 3.1 Provenance inconsistency inside the Forge (runtime answers to "what patch?")

| Surface | File:line | Returns today |
|---|---|---|
| `GET /api/health` | `backend/app/routes/health.py:37-46` reads `data/version.json` | `"unknown"` |
| `GET /api/version` | `backend/app/routes/version.py:64-66`; defaults in `backend/config.py:26-30` and `.env.example:64-66` | `current_patch "1.4.3"`, `current_season 4`, `data_version "1.0.0"` |
| `/api/load` VersionedLoader | `backend/data/versioning/versioned_loader.py:21-25` probes `items/affixes.json` etc. for `_version` | `{'version': 'unknown', 'source': 'none'}` (executed locally) |
| Meta snapshot | `backend/app/services/meta_analytics_service.py:185` | `"1.4.3"` |
| Dashboard fallback | `frontend/src/pages/DashboardPage.tsx:192-193` | `"1.4.3"` / season `4` |
| New build defaults | `backend/app/models/__init__.py:107-108`, `backend/app/schemas/__init__.py:90-91`, `backend/app/services/build_service.py:62-63` | `patch_version "1.2.1"`, `cycle "1.2"` |
| Seed builds | `backend/app/utils/cli.py:146-168` | `patch_version "1.4.3"` with `cycle "1.2"` (internally contradictory) |
| Frontend store default | `frontend/src/store/buildWorkspace.ts:96` | `version: "1.2.1"` |

Root cause of `"unknown"`: `scripts/sync_game_data.py:21` resolves its source as `<forge>/last-epoch-data/exports_json` (nested, not a sibling checkout), and `_detect_patch_version()` (`:25-32`) falls back to `"unknown"` when `metadata.json` is absent. `exports_json/metadata.json` was first committed in `last-epoch-data` on **2026-05-03** (`536add5`), eight days after the Forge's only recorded sync (2026-04-26). The stamp therefore could never have been populated by that sync.

---

## 4. Proven drift: Forge runtime affixes vs. 1.4.6

I re-applied the Forge's own transform (`scripts/sync_game_data.py --affixes`) to three historical `exports_json/affixes.json` revisions in a scratch root, then compared the results with `le-the-forge/data/items/affixes.json`:

| LED commit | Label | Result vs Forge `data/items/affixes.json` (1228 records) |
|---|---|---|
| `bb4ab10` 2026-04-25 21:12 -0400 | "regenerate against LE 1.4.x via TT-based affix pipeline" | 1228 records; 1 id rename and 1 changed record (a duplicate-name gloves affix). **Effectively the source** |
| `e32d3f8` 2026-05-01 | "refresh exports against patch 1.4.3" | Same as above |
| `419603d` 2026-05-05 | "refresh generated outputs for Last Epoch 1.4.6" | 1230 records; **3 new ids, 16 changed tier records** |

What the Forge is missing from 1.4.6:
- New affixes: `chance_for_non_critical_strikes_to_inflict_critical_vulnerability_for_4_seconds` (affix_id 980), `increased_melee_attack_speed_and_frenzy_after_using_evade` (989), and the `…ward_gain_on_direct_spell_cast_gloves` id split (1005).
- Changed values: 15 idol "X Penetration/Resistance and Minion X Penetration/Resistance" affixes (ids 863-870, 882-888). For example, T1 penetration is 1-2 in the Forge and 3-4 in 1.4.6; T1 resistance is 9-12 in the Forge and 18-24 in 1.4.6. Also `increased_cast_speed_and_ward_gain…_1005` T1 changed from 4 to 3.

Record-count drift from the extractor history (`git show <c>:exports_json/*.json`):

| File | 1.4.3 (`853b053`, 04-10) | 1.4.3 rerun (`e32d3f8`, 05-01) | 1.4.6 (HEAD) | Forge `data/` |
|---|---|---|---|---|
| affixes equipment / idol | 946 / 115 | 1112 / 115 | 1112 / 115 | 1228 flattened (≈1.4.3 rerun) |
| uniques / setItems | 403 / 47 | 403 / 47 | **409 / 59** | `uniques.json _meta.total 403`; `set_items.json` 47 items / 18 sets |
| skills | 155 | 184 | 184 | 184 |
| set_bonuses | 7 | 24 | 24 | n/a |
| items equippable base types | 40 | 42 | 42 | hand-curated `base_items.json` (20 slots) |

Caveat: the 1.4.3→1.4.6 idol value change could come from the game patch or from pipeline changes between `e32d3f8` and `419603d`. The only processor commit in between (`42e88da`) added derived tags and does not alter tiers, which points to the game patch, but that has not been verified against the game client.

---

## 5. What Last Epoch has released since 1.4.6 (web evidence)

| Version | Date | Content summary (from search snippets) |
|---|---|---|
| 1.4.0 Season 4 "Shattered Omens" | 2026-03-26 | New pinnacle boss, Rogue skills Bladestorm and Shadow Rend, item Corruption with corrupted affixes, Idol Altars |
| 1.4.6 | 2026-04-29 | (extracted, build 22986002) |
| **1.4.7** | 2026-05-13 | Erasing Strike fix, Silver Shroud consumption capped at 75%, Confluence of Oblivion Monolith scaling rework, Heoborea waypoint fix. **Not extracted** (LED HEAD 2026-05-31 is still 1.4.6) |
| **1.5.0 Season 5 "Rage of the Frostborn"** | 2026-10-01 | Seasonal encounter "Rage of Morditas" (timed slaughter that becomes an arena; 27 Rage buffs); new pinnacle boss "Morditas, God of Bloodshed"; new skills Radiant Lance (Paladin), Summon Tide Elemental (Shaman), Dreamslash (Bladedancer); 16 new uniques plus a new 2-item set; new Forging Potential kinds (Ice FP may be preserved, Blood FP raises critical-success chance; only on Rage of Morditas items); Circle of Fortune and Merchant's Guild rework (Guild no longer rank-locks item types); passive-node changes (e.g. Symbols of Hope now Paladin-only at 35 points; Synchronized Strike now Bladedancer-only at 35; Locust Master replaced by Stormslash; Winged Raptor changes) |
| 1.5.1 | 2026-10-02 | Lens of Tyranny charge rate, Pinnacle Morditas for Legacy/Offline, Circle of Fortune Rank 3 now procs omen idols, "already ruined" item fix |
| 1.5.1.2 (reported) | 2026-10-05 | Reported by an aggregator. Content UNKNOWN |

Verification in the current data: `grep -il` across `exports_json/*.json` and `localization/*` finds 0 hits for "radiant lance", "tide elemental", "dreamslash", "ice forging", "blood forging". Bladestorm and Shadow Rend (1.4.0) are present. Morditas appears in 1.4.6 lore/dialogue strings only.

No new masteries were announced. Paladin, Shaman and Bladedancer are existing masteries receiving their final skills.

### 5.1 What the existing extractor is likely not to understand
Everything here is **evidence from patch notes, unverified against game files**.

| Plausible new/changed domain | Why the current pipeline is at risk | Pipeline touchpoint |
|---|---|---|
| New skills (3) and their skill trees | `extract_skill_trees_fast.py` parses raw MonoBehaviour bytes with a layout "verified across all 4983 *TreeNode candidates in patch 1.4.3" (`:101`, `:159`). New trees add nodes, and a layout change would fail or silently corrupt | `extract_skill_trees_fast.py`, `extract_skills_binary.py`, baselines `skills.json min_records 184` |
| Passive-node requirement changes (mastery-only, 35-point gates) | `passive_trees.json` baseline is 5 trees with `max_shrinkage 0`. Changes to requirement semantics are not schema-checked | `process_skill_trees.py` |
| New Forging Potential kinds (Ice/Blood) | No FP-type field in item exports today. Forge `forging_potential_ranges.json` is rarity-only and hand-written | items/uniques processors; Forge crafting engine |
| Variant affix (Unsated Rage: 1 of 27 Rage buffs) | Unique-mod model has no "variant/one-of" construct | `process_uniques.py` |
| Rage of Morditas encounter, Rage buffs | New status/buff IDs. The `StatusEffectID`/`NonAilmentUIBuffID` enums in `enums.json` date from 1.4.3 | `extract_enums.py` |
| Faction rework (Merchant's Guild, Circle of Fortune ranks) | No faction rank export exists | none |
| New uniques (16) plus a 2-item set | Additive. Baselines only guard shrinkage, so they pass silently | `process_uniques.py`, `process_set_bonuses.py` |
| New item base types (if any) | Forge `BASE_TYPE_ID_TO_ITEM_TYPE_ID` stops at 33 (section 6.3) | Forge constants |

---

## 6. Hard-coded patch strings, IDs, enums and special cases

### 6.1 Forge (`le-the-forge`)
| Item | File:line | Notes |
|---|---|---|
| `CURRENT_PATCH "1.4.3"`, `CURRENT_SEASON 4` | `backend/config.py:28,30`; `.env.example:65-66`; `routes/version.py:13-14,65-66`; `meta_analytics_service.py:185`; `DashboardPage.tsx:192-193` | Season 4 was correct in Mar–Sep 2026. Today it is Season 5 / 1.5.x |
| `patch_version "1.2.1"`, `cycle "1.2"` defaults | `models/__init__.py:107-108`, `schemas/__init__.py:90-91`, `build_service.py:62-63`, `store/buildWorkspace.ts:96` | Two cycles old. New builds are mislabeled |
| `"In-game data from patch 1.2.x"` | `frontend/src/lib/gameData.ts:8` | Hand-maintained frontend data (672 lines, imported by 15 files) |
| `MAX_PASSIVE_POINTS = 113` | `frontend/src/logic/validatePassiveBuild.ts:20` | Game rule constant, not derived from data |
| `planner_skill_passive_icons_v142.webp` | `frontend/public/assets/`, used by `TreeIcon.tsx`, `atlasConfig.ts` | Atlas named for 1.4.2 |
| `BASE_TYPE_ID_TO_ITEM_TYPE_ID` keys 0–33 | `backend/src/constants/BASE_TYPE_ID_TO_ITEM_TYPE_ID.ts:11-47` | The comment says 34–39 are omitted. 1.4.6 exports also contain **40 `UNUSED` and 41 `IDOL_ALTAR`** (a Season 4 system) with no mapping and no comment |
| LE 1.4.x rename `rerollChance` → `weighting` | `scripts/sync_game_data.py:118-123,229-230` | Patch-specific compatibility branch. The comment notes the count changed from 946 to 840+272 |
| `"Weaver Tree (Season 4+)"` | `backend/app/game_data/game_data_loader.py:155` | Season label in code |
| Windows paths `D:\Forge\last-epoch-data\data_bundle` | `backend/app/game_data/bundle_compat.py:19`; `scripts/smoke_data_bundle_handoff.ps1:2` | Environment-coupled defaults |

### 6.2 Extractor (`last-epoch-data`)
| Item | File:line | Notes |
|---|---|---|
| `PINNED_VALID_FOR_BUILD = "22986002"` plus hard-coded `CLASS_REQ`/`SUBCLASS_REQ` maps | `tools/scripts/item_enum_authority.py:46-60` | Will be wrong for any newer build until re-pinned |
| Report file names fixed to `_1.4.6` | `generate_pipeline_completeness_audit.py:23-24`, `generate_item_mechanics_audit.py:30-31`, `validate_tree_effect_hints.py:29`, `items_trusted_subset_certification.py:62-63`, `skills_trusted_subset_certification.py:56`, and others (14 non-test scripts reference 1.4.6/22986002) | Must be renamed per patch |
| 1.4.3-specific binary-layout workarounds | `extract_skill_trees_fast.py:73,101,136-159`; `process_set_bonuses.py:32,102-169`; `extract_localization_addressables.py:94` (expected tables "as of 1.4.3") | 25 non-test scripts reference 1.4.3/22682302 |
| **Undecoded enum value** | `exports_json/affixes.json`: `specialAffixType` = `"6"` on **134** equipment affixes (e.g. id 951 "Frenzy and Reduced Frenzy Effect", tag `special:6`) | `_meta.unknown_sp_count: 0` does not cover this field. `affix_tag_category_validator.py:48` `KNOWN_SPECIAL_TYPES` lacks it. `enums.json` was last committed 2026-04-10 (1.4.3). Identity UNKNOWN (likely a Season 4 affix class) |
| Unity version / build detection | `game_paths.py` (`detect_unity_version`, `detect_game_build`) | Requires `UnityPlayer.dll`/`GameAssembly.dll` on disk |

---

## 7. Can a fresh extraction run here?

**No.** The blockers, from the code:

| Blocker | Evidence |
|---|---|
| Game install required | `tools/scripts/game_paths.py:58-104` resolves `$LAST_EPOCH_DIR` → `game_files/current/<ver>_<build>` → `game_files/current` → the Steam registry (`winreg`) → `C:\Program Files (x86)\Steam\…`. `game_files/` is git-ignored (`.gitignore` "stays on Windows only"). Executed `validate_bootstrap.py` failed: `FileNotFoundError: Could not locate Last Epoch install` |
| Windows-only tool chain | `tools/external.lock`: Il2CppDumper 6.7.46 (`.exe`), AssetRipper 1.3.12 (GUI-only `.exe`), Mono.Cecil 0.11.5 via pythonnet. `scripts/fetch_tools.ps1` and `scripts/setup.ps1` are PowerShell, need Python 3.11 specifically (`setup.ps1:61-85`) and the .NET 8 runtime (`:93-96`) |
| Python deps absent | `requirements.txt` pins UnityPy 1.25.0, TypeTreeGeneratorAPI 0.0.10, pythonnet 3.0.5, pefile. `import UnityPy` and `import clr` both raise ModuleNotFoundError here |
| No current snapshot | `patch_versions/` contains only 1.3.7.1 and 1.4.3. The 1.4.6 install path was `D:\LastEpochTools\game_files\current\1.4.6_22986002` (`metadata.json installPath`) |
| Runbook assumes the operator machine | `patch_update_guide.md` Prerequisites: "Windows machine…, Game installed locally via Steam"; Step 4 `py tools/scripts/run_all.py` |

What *does* run on Linux against committed data (on a scratch copy):
- `validate_exports.py` → `Export validation passed for 9 baseline file(s).` (exit 0)
- `validate_data_bundle.py` → `Result: WARN` (15 known gaps; 4 block, 10 degrade, 3 warn)
- `validate_affix_tag_categories.py` → `validation_status: warning`, **148 unknown or unsupported tag/category values**
- `validate_bootstrap.py` → fails (needs the game)
- Forge `backend/scripts/check_data_bundle.py` → could not run (`flask` not installed; it imports `app`)

---

## 8. Change detection in the extractor

| Mechanism | Exists | Gating in `run_all.py` | What it catches | What it misses |
|---|---|---|---|---|
| `validate_exports.py` plus `tools/verification/export_baselines.json` (`updated_for_patch 1.4.6_22986002`) | Yes | Yes (last step) | Missing file, stale mtime vs run start, missing top-level keys, count below the minimum, shrinkage % above the threshold, duplicate IDs, non-finite numbers | **Additions** (new records or fields), changed values, renamed fields inside records, new enum values |
| `validate_bootstrap.py` | Yes | Yes | Intermediate artifact integrity, game build match | Schema drift |
| Unknown-value detection | `affix_tag_category_validator.py` (diagnostic) and `_meta.unknown_*_count` fields | **No** | Unknown groups, special types, modifier types | Only affixes. Its result (148 unknowns) is a warning |
| Patch-to-patch diff | `deepdiff==7.*` pinned under "Patch-diff reporting (Phase 6)" in `requirements.txt`, but only `compare_tt_vs_legacy.py` uses it (legacy vs TT processor, not patch vs patch) | No | n/a | No patch-diff report exists |
| Relationship drift | `relationship_drift_intelligence_planning.py` | No | Docstring: "planning only… does NOT execute any drift check" | Everything |
| `t10_regeneration_drift_review.py` | Yes | No | Classification of one historical regeneration drift event | Ongoing drift |
| JSON-schema validation | `validate_forge_safe_export_schema.py` against `schemas/exports/*.schema.json` | No | Forge-safe export shape | Raw `exports_json` shape |

Test of the gap: the 1.4.3→1.4.6 transition added 6 uniques and 12 set items and changed 16 affix tier records (section 4). None of that would make `validate_exports.py` fail, because the gate looks only for shrinkage.

---

## 9. Sources (web)
Direct fetches of lastepoch.com, massivelyop.com and arpg-timeline.com were refused by the network egress proxy. The facts below come from search-result snippets only.
- Season 5 Patch Notes — lastepoch.com: https://lastepoch.com/1-5/patchnotes/
- Season 5 is now live — Last Epoch Forums: https://forum.lastepoch.com/t/season-5-rage-of-the-frostborn-is-now-live/81860
- Season 5 Patch Notes — Maxroll: https://maxroll.gg/last-epoch/news/season-5-patch-notes
- 1.5 Branch Update — Maxroll: https://maxroll.gg/last-epoch/news/last-epoch-1-5-branch-update-for-season-5-rage-of-the-frostborn
- Massively OP, 2026-10-01: https://massivelyop.com/2026/10/01/last-epoch-brings-new-random-encounters-a-new-boss-fight-and-new-class-skills-in-todays-season-5-release/
- 1.5.1 notes (2026-10-02): https://patched.gg/games/last-epoch/last-epoch-151-patch-notes
- 1.4.7 notes (2026-05-13): https://patched.gg/games/last-epoch/last-epoch-147-patch-notes
- 1.4.6 notes (2026-04-29): https://patched.gg/games/last-epoch/last-epoch-patch-146-notes
- Shattered Omens patch notes — Forums: https://forum.lastepoch.com/t/last-epoch-shattered-omens-patch-notes/80571
- 1.4 Branch Update — Maxroll: https://maxroll.gg/last-epoch/news/last-epoch-1-4-branch-update-for-season-4-shattered-omens

---

## 10. Key dates

| Event | Date | Evidence |
|---|---|---|
| LED initial extraction (1.3.7.1) | 2026-03-26 | `23dfae5` |
| LE 1.4.0 / Season 4 | 2026-03-26 | web |
| LED "data: patch 1.4.3_22682302" | 2026-04-10 | `853b053` |
| Forge last data sync | 2026-04-26 01:32Z | `data/version.json`, `d0016c5` |
| LE 1.4.6 | 2026-04-29 | web |
| LED `metadata.json` first emitted (1.4.3) | 2026-05-03 | `536add5` |
| **Last successful extraction (1.4.6)** | 2026-05-06 00:03Z | `exports_json/metadata.json`, `c0a0d55`/`419603d` |
| Baselines calibrated for 1.4.6 | 2026-05-05 | `f55fbb1` |
| Canonical bundle (1.4.6 phase1a) | 2026-05-07 | `data_bundle/metadata.json` |
| Forge v2 bundles generated | 2026-05-12 | `generated_on` |
| LE 1.4.7 | 2026-05-13 | web |
| Forge HEAD | 2026-05-14 | `1efcef7` |
| Last export-file change (additive loot-filter manifest) | 2026-05-29 | `7ed55e6` |
| Last schema change (`schemas/`) | 2026-05-26 | `f9aa4ce` |
| LED HEAD | 2026-05-31 | `73e2ab0` (governance work; no data refresh) |
| LE 1.5.0 / Season 5 | 2026-10-01 | web |
| LE 1.5.1 | 2026-10-02 | web |

Last supported patch: **1.4.6** for the extractor, **≈1.4.3 snapshot** for the Forge runtime, and **1.4.3** as declared by the Forge API.

---

## 11. UNKNOWNs
- The exact 1.5.x build number and whether any further hotfix exists after 1.5.1.x. Official pages could not be fetched.
- Whether 1.4.7 changed any extracted data. No extraction was done for it.
- What `specialAffixType == 6` means.
- Whether 1.5 changed Unity version, asset layout, or the TypeTree for the classes the binary parsers read. That cannot be determined without game files.
- Whether the production deployment sets `CURRENT_PATCH`/`CURRENT_SEASON` env vars to different values (`render.yaml` and docker-compose have none).
- Whether the frontend raw tree layout files miss Season 4 nodes in practice. Only a name grep was done.

## 12. What this does NOT prove
- It does not prove which specific numbers in the Forge are wrong *in game today*. Only differences between data snapshots were measured. 1.5 balance changes were not diffed, because no 1.5 extraction exists.
- The idol value differences are attributed to patch 1.4.6 by elimination, not by client verification.
- The web facts are third-party search snippets. They are not quoted from the official patch notes, which were unreachable.
- "Extractor would not understand X" (section 5.1) is a risk assessment, not a test result.


---

<!-- FILE: 08_LAST_EPOCH_TOOLS_IMPORT_FORENSICS.md -->

# 08 — Last Epoch Tools Import Forensics (Phase 6)

Audit date: 2026-10-06
Repo HEAD: `1efcef7` (shallow clone, 266 commits visible)
Scope: audit only. No code changed.

## 1. Incident

Discord import alert received twice for an anonymous user:

```
Source:         lastepochtools
URL:            https://www.lastepochtools.com/planner/B5P5P8M3
Missing Fields: None
Parsed Data:    No data parsed
Error:          Last Epoch Tools returned HTTP 403
```

## 2. Verdict (short)

| Question | Answer | Confidence |
|---|---|---|
| Which code path produced the alert? | `POST /api/import/build` → `LastEpochToolsImporter.parse()` → `HTTPError` branch → `_record_and_alert` | High (reproduced byte-for-byte locally with mocked 403) |
| Is the fetch broken? | Yes, in production: the server-side GET of the planner page received HTTP 403. The repo itself already states server-side fetching of LE Tools no longer works ("LET migrated to client-side rendering"), and the UI labels the path "Temporarily Unavailable" — yet one entry point still calls it. | High that it fails; origin of the 403 UNKNOWN (see §6) |
| Is the parser broken? | Not provable against live data. All LE Tools fixtures in the repo are synthetic ("not captured from live LET"). The code's own comments assert that `window.buildInfo` is no longer present in server HTML, which would make the HTML parser fail with 422 even if the fetch returned 200. The JSON mapper (bookmarklet path) has demonstrable mapping defects independent of the fetch (§9). | Medium |
| Is the alert accurate? | Partly. `Missing Fields: None` and `Parsed Data: No data parsed` are technically true but non-diagnostic: no status-code metadata, response headers, body markers, or `partial_data` are captured. The importer's own `partial_data` is discarded on hard failure. | High |
| Was this 403 from the audit container's proxy? | No. Production runs on Render and does not use this container's egress proxy. The local proxy did block all audit attempts to reach lastepochtools.com (see §6), so live behaviour could not be observed from here. | High |

## 3. End-to-end trace

### 3.1 Entry points (three backend routes, one frontend modal)

| Route | File:line | Fetches LE Tools? | Saves build? | Alerts on 403? | Used by UI? |
|---|---|---|---|---|---|
| `POST /api/import/build` | `backend/app/routes/import_route.py:502-547`, `_do_import` `:550-667` | Yes (via importer) | Yes (draft, `is_public=False` `:592`) | **Yes** (`:568-580`) | **Yes** — "Import URL" tab, `BuildImportModal.tsx:86-111` |
| `POST /api/import/url` | `import_route.py:306-414` | Yes (duplicated inline fetch `:336-348`) | No | No (returns 502 `:356`; alert only on unhandled exception `:401-414`) | No — "Quick Fetch" tab input and button are `disabled` (`BuildImportModal.tsx:394-439`) |
| `POST /api/import/let/json` | `import_route.py:421-481` | No (accepts browser-captured `window.buildInfo`) | No | Only on mapper exception (`:461-473`) | Yes — "{ } JSON" tab (`BuildImportModal.tsx:150-185`) |

### 3.2 Frontend → backend (the path the user took)

1. `BuildImportModal.tsx:49-53` `detectSource()` classifies `lastepochtools.com/planner/` URLs as `"lastepochtools"`.
2. `BuildImportModal.tsx:86-95` `handleFullImport()` only rejects `importSource === null`; an LE Tools URL **is accepted**.
3. The tab copy (`:263-289`) says "Last Epoch Tools cannot be fetched by URL (LET is client-side)" and shows a "Use JSON tab for LET" hint, but the "Import Build" button (`:304-317`) is enabled for LE Tools URLs (`disabled={importLoading || !importUrl.trim()}`).
4. `frontend/src/lib/api.ts:583-584` → `POST /import/build {url}`.

### 3.3 Backend request handling

1. Rate limit: `@limiter.limit(_dynamic_import_limit, key_func=_rate_key_import)` `import_route.py:488-503` — anonymous `2 per minute` keyed on `request.remote_addr`. No `ProxyFix` exists anywhere under `backend/app` or `backend/wsgi.py` (grep: no matches), so behind Render's proxy the key may be a shared proxy address (UNVERIFIED; depends on Render's forwarding behaviour). Two alerts from two attempts is consistent with the limit not blocking the second attempt.
2. URL validation / source detection: `importer_factory.py:162-173` `detect_source()` using `URL_PATTERN = re.compile(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)")` (`lastepochtools_importer.py:593`). Unanchored `search` — accepts any string containing that substring (e.g. `https://evil.example/?x=lastepochtools.com/planner/AB`). The code is extracted and re-inserted into a fixed host URL (`:694`), so this is not an SSRF, but validation is lax.
3. Importer selection: `importer_factory.py:176-186`.

### 3.4 Fetch (`lastepochtools_importer.py:691-733`)

| Property | Value | Evidence |
|---|---|---|
| Library | `requests==2.32.3` (urllib3 2.x, OpenSSL TLS stack, Python 3.11 in prod image) | `backend/requirements.txt:17`, `backend/Dockerfile:7,18` |
| Method / URL | `GET https://www.lastepochtools.com/planner/{code}` | `:693-694` |
| User-Agent | Hard-coded `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` | `:696-700` |
| Accept | `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | `:701` |
| Accept-Language | `en-US,en;q=0.9` | `:702` |
| Accept-Encoding | `gzip, deflate` (requests default; no brotli installed) | prepared-request check, §8 cmd C |
| Connection | `keep-alive` (default) | same |
| Referer / Origin / cookies / `sec-ch-ua` / `sec-fetch-*` | None | `:695-703` |
| Session | None (one-off `requests.get`) | `:693` |
| Redirects | Followed (requests default) | — |
| Timeout | 15 s single value (connect+read each) | `:704` |
| Retries / backoff | None | — |
| Caching of fetched pages | None | — |
| Logged on failure | `"LET importer: HTTP %d for code=%s"` only — no response headers, no body snippet, no `cf-ray` | `:718` |

Observation (factual, not a recommendation to change it): the request declares a 2023 Chrome user agent while sending none of the headers a real Chrome sends and using a non-browser TLS client, from a datacenter address. That combination is a common trigger for upstream bot-protection rules. Whether LE Tools applies such rules is UNKNOWN from this environment.

### 3.5 Exact line producing the message

`backend/app/services/importers/lastepochtools_importer.py:716-727`

```python
except _requests.HTTPError as exc:
    status = exc.response.status_code if exc.response is not None else 502
    logger.warning("LET importer: HTTP %d for code=%s", status, code)
    if status == 404:
        return ImportResult(...)
    return ImportResult(
        success=False, source=self.source_name,
        error_message=f"Last Epoch Tools returned HTTP {status}.",
    )
```

(An identical string exists at `import_route.py:356` for `/api/import/url`, but that path returns 502 and does not alert, so it is not the source of this incident.)

### 3.6 Failure recording and alert

1. `_do_import` hard-failure branch `import_route.py:567-580`:
   ```python
   _record_and_alert(..., error_message=result.error_message or ...,
                     missing_fields=result.missing_fields,
                     partial_data=result.build_data)   # line 575
   ```
   `partial_data=result.build_data` is always `None` on a hard failure; the importer's own `result.partial_data` (e.g. `{"html_length", "code"}` at `lastepochtools_importer.py:751`, `{"keys", "code"}` at `:774`, or the rich mapper-crash dict at `:811-820`) is **never forwarded**. This is why every hard failure shows "No data parsed".
2. `_record_and_alert` `import_route.py:281-299` writes an `ImportFailure` row (`backend/app/models/__init__.py:330-345`: `source, raw_url, missing_fields, partial_data, user_id, error_message`) and calls `send_import_failure_alert`.
3. `backend/app/services/discord_notifier.py`:
   - `WEBHOOK_URL = os.environ.get("DISCORD_IMPORT_WEBHOOK_URL", "")` (`:18`).
   - Snapshot `:48-57`; background daemon thread `:60-65`.
   - Embed fields `:116-134`: Source, URL, **Missing Fields** (`", ".join(missing) if missing else "None"`), **Parsed Data** (`_summarize_partial_data`, returns `"No data parsed"` when `partial_data` is falsy `:70-71`), Error, plus optional Raw Gear / Raw Top-Level Keys, User.
   - No HTTP status field, no upstream headers, no attempt count, no dedupe/throttle. Every attempt on a known-dead path produces a red "hard" alert.
4. User response: HTTP 422 `{"errors":[{"message":"Last Epoch Tools returned HTTP 403."}]}`. The modal shows that raw message (`BuildImportModal.tsx:100-102`) with no pointer to the JSON/bookmarklet workaround. The "This issue has been reported" footer (`:560`) checks `importError.includes("422")`, which this message never contains, so it does not render.

### 3.7 Parsing (only reached on HTTP 2xx)

`_extract_build_info` (`lastepochtools_importer.py:596-673`; duplicated verbatim in `import_route.py:90-168`):

1. Regex `window\s*(?:\[\s*["']buildInfo["']\s*\]|\.buildInfo)\s*=\s*` then `json.JSONDecoder().raw_decode` (`:599-614`).
2. `<script id="__NEXT_DATA__" type="application/json">` → `props.pageProps.{buildInfo|build}` or pageProps containing `bio`/`charTree` (`:617-645`). Speculative: nothing in the repo shows LE Tools ever used Next.js.
3. Scan every `<script>` for a JSON object with `bio` or `charTree` (`:648-670`).
4. Otherwise 422-style failure "Could not find build data in the page…" with `partial_data={"html_length", "code"}` (`:745-752`) — which, per §3.6, is then dropped by the route.

Post-extract: `buildLoadError` flag → "Build not found or deleted" (`:754-759`); optional `data` envelope unwrap (`:762-764`); requires `bio` or `charTree` (`:766-775`); then `_map` (`:828-936`).

No HTML-level detection of bot-challenge pages exists (no check for `cf-mitigated`, "Just a moment", `challenge-platform`). A 200 challenge page would be reported as "LE Tools may have updated their format".

### 3.8 Normalization, validation, persistence

- `_map` (`:828-936`) → class (`_CLASS_MAP` `:32-38`), mastery (`_MASTERY_MAP` `:40-46`), passives (`charTree.selected` expanded to repeated node IDs `:855-863`), skills (`skillTrees[]`, `hud` order `:866-903`), gear (`_parse_gear` `:938-1222`).
- `BaseImporter.validate` (`base_importer.py:111-146`) only checks class name, mastery name, non-empty skill names.
- Persistence: `build_service.create_build` (`backend/app/services/build_service.py:44-81`) — no Marshmallow schema validation on this path; see contract doc 09.
- Detailed field-level behaviour, defects, and the coverage matrix are in `09_BUILD_IMPORT_CONTRACT.md`.

## 4. The durable legitimate representation that exists today: the bookmarklet

`frontend/public/bookmarklets/let-import.js:17-51` (minified copy inlined at `BuildImportModal.tsx:23-26`, also `let-import.bookmarklet.txt`):

- Runs in the user's own browser on a LE Tools planner page, reads `window.buildInfo`, `JSON.stringify`s it, writes it to the clipboard, shows a toast. No network calls, no data sent anywhere.
- Header comment (`:9-11`): "Necessary because LET moved to client-side rendering — the server cannot fetch window.buildInfo any more".
- UX wiring: "{ } JSON" tab (`BuildImportModal.tsx:485-525`) shows drag-to-bookmark link plus a DevTools fallback `copy(window.buildInfo)`. `looksLikeLetBuildInfo` (`:28-38`) auto-detects and posts to `/api/import/let/json` (`:167-185`).
- It is **not** the default tab; the default "Import URL" tab still accepts LE Tools URLs and routes them to the dead server-fetch path (root cause of the alert noise).
- Durability caveat: it depends on LE Tools continuing to expose `window.buildInfo` as a global. That is an undocumented page internal. Current presence is UNKNOWN (not observable from this environment).
- Earliest commit in the shallow history containing the bookmarklet: `e2c64eb` 2026-04-21 (true first-introduction date UNKNOWN due to shallow clone).

Browser-side data loading: whether the planner page loads build data through a JSON endpoint (XHR) after hydration is UNKNOWN — no network capture exists in the repo and live access was blocked. The repo contains no reference to any LE Tools JSON/API endpoint.

## 5. Public documentation search (LE Tools API / export format / bot protection)

| Query | Result |
|---|---|
| "lastepochtools planner import API export build code" | No relevant results. |
| "Last Epoch Tools build planner import export" (reddit / lastepochtools.com) | LE Tools news post on online character import and character profiles: import into the planner by account/character name or offline save upload; builds shared via "Save / Share". No public developer API documented. Source: [LE Tools: Online character import and Character Profiles](https://www.lastepochtools.com/news/article/site-update-online-character-import-and-character-profiles) |
| "github lastepochtools planner buildInfo parser import" | No LE Tools API docs. Mentions the community offline planner [Musholic/LastEpochPlanner](https://repos.ecosyste.ms/topics/last-epoch) and the [LE Tools forum thread](https://forum.lastepoch.com/t/last-epoch-tools-build-planner/28469). Whether those projects import LE Tools links, and how, is UNKNOWN. |
| "lastepochtools.com cloudflare 403" | Only generic scraping/bypass vendor pages; nothing LE Tools specific. Not used. |

Conclusions: **No publicly documented LE Tools API or third-party export format was found** (UNKNOWN whether a private one exists). No public announcement of planner-page or bot-protection changes was found. The repo's "moved to client-side rendering" claim is unsourced in-repo.

## 6. Origin of the 403

### 6.1 Live observation attempts from this container (3 of 5 allowed)

| # | Command | Result |
|---|---|---|
| A | `curl -sS -o robots.body -D robots.hdr -w 'http=%{http_code} ip=%{remote_ip}\n' https://www.lastepochtools.com/robots.txt` | `curl: (56) CONNECT tunnel failed, response 403`; headers are the **local proxy's**: `HTTP/1.1 403 Forbidden`, `Content-Type: text/plain; charset=utf-8`, `X-Content-Type-Options: nosniff`, `Content-Length: 80`; `remote_ip=127.0.0.1`. No `server: cloudflare`, no `cf-ray`. |
| — | local egress-proxy status endpoint query | `{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"www.lastepochtools.com:443"}` |
| B | WebFetch `https://www.lastepochtools.com/robots.txt` | `EGRESS_BLOCKED: Access to www.lastepochtools.com is blocked by the network egress proxy.` |
| C | WebFetch `https://www.lastepochtools.com/planner/B5P5P8M3` | same `EGRESS_BLOCKED` |

These 403s are produced by the audit environment's egress policy at CONNECT time; no packet reached LE Tools. **They say nothing about production.** Per proxy guidance, no retries or workarounds were attempted.

### 6.2 What can be said about production

- Production backend runs on Render (`render.yaml`: `epochforge-api` Flask+Gunicorn). It does not traverse this container's proxy. The 403 in the alert therefore came from whatever answered Render's outbound request: LE Tools' origin or an edge/WAF in front of it.
- Cloudflare vs origin: **UNKNOWN**. The importer records only the integer status (`:717-718`); no `server`, `cf-ray`, `cf-mitigated` headers or body snippet are logged or stored, so the evidence needed to distinguish was never captured. Whether lastepochtools.com is fronted by Cloudflare could not be verified from here.
- Render outbound traffic originates from shared cloud-provider address ranges. Many bot-protection products score datacenter ASNs as higher risk; combined with the header/TLS profile in §3.4, a 403 for this request shape is plausible from any such product. This is an inference, not a verified cause.
- The repo independently states server fetch is dead (`import_route.py:432-434`, `let-import.js:9-11`, `BuildImportModal.tsx:272-275, 397-401`). So the failure is a known, pre-existing condition, not a new regression introduced in v2.5.

## 7. Tests run

Command (scratch venv already provisioned with `backend/requirements.txt`):

```
cd backend && FLASK_ENV=testing SECRET_KEY=dummy JWT_SECRET_KEY=dummy \
  $SCRATCH/venv-backend/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_importers.py tests/test_build_import.py \
  tests/test_le_tools_importer_stage_context.py \
  tests/test_le_tools_importer_fixture_context.py \
  tests/test_le_tools_import_context_sidecar.py
```

Result: `232 passed, 4 warnings in 1.90s`.

What they prove:
- All LE Tools HTTP is mocked (`@patch("app.services.importers.lastepochtools_importer._requests.get")`, `test_importers.py:159-217`; inline `_LET_HTML` `:31-42` with `window["buildInfo"]`). They prove the parser handles the *assumed* format and that 404/500 map to messages.
- Sidecar / stage-context tests run against fixtures declared `"source": "synthetic_offline_not_captured_from_live_let"` (`backend/tests/fixtures/le_tools_offline_buildinfo_*.json`), all committed in `d98bb4c` 2026-05-11. The sidecar golden file `le_tools_import_context_sidecar_current.json` (`generated_at: 2026-05-07`) records incorrect mappings as `"status": "resolved"` (see 09 §5, IMP-4).
- No test exercises a 403, a challenge page, the alert `partial_data` content on hard failure, or the frontend's acceptance of LE Tools URLs on the Import URL tab.

What they do NOT prove: anything about the live LE Tools page format, `window.buildInfo` presence, field semantics (affix encoding, tier base, item IDs), or reachability from Render.

## 8. Reproduction evidence (local, mocked, no network)

**Cmd R1 — exact alert reproduction** (`$SCRATCH/imp_route403.py`: Flask test client, `_requests.get` patched to raise `HTTPError` with status 403, `send_import_failure_alert` patched):

```
status 422 {'data': None, 'errors': [{'message': 'Last Epoch Tools returned HTTP 403.'}], 'meta': None}
fetch call kwargs: call('https://www.lastepochtools.com/planner/B5P5P8M3', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}, timeout=15)
alert: lastepochtools https://www.lastepochtools.com/planner/B5P5P8M3 [] None Last Epoch Tools returned HTTP 403. {'severity': 'hard'}
Parsed Data field -> No data parsed
```

Matches the production alert field-for-field.

**Cmd C — effective outbound headers** (prepared request, not sent): `{'User-Agent': ..., 'Accept-Encoding': 'gzip, deflate', 'Accept': ..., 'Connection': 'keep-alive', 'Accept-Language': 'en-US,en;q=0.9'}`; `brotli no`.

**Cmd R2 — mapper on repo fixture** (`$SCRATCH/imp_repro.py`): see 09 §5.

## 9. Fixture age vs current site

| Fixture | First commit (shallow) | Origin | Encodes |
|---|---|---|---|
| `le_tools_offline_buildinfo_equipment_sample.json` | 2026-05-11 `d98bb4c` | synthetic | `equipment[]` with integer `baseTypeID`, `slot` strings, `ir`/`ur` |
| `le_tools_offline_buildinfo_stage_context_sample.json` | 2026-05-11 | synthetic | same, plus `expected_diagnostic_category` |
| `le_tools_parsed_gear_context_sample.json` | 2026-05-11 | synthetic | already-mapped gear |
| `le_tools_import_context_sidecar_current.json` | 2026-05-11 (generated 2026-05-07) | generated from synthetic | diagnostic sidecar |
| Inline `_LET_HTML` in `test_importers.py` / `test_build_import.py` | UNKNOWN (shallow) | hand-written | server HTML with `window["buildInfo"]` |

No captured live LE Tools payload exists in the repo. Comparison against the current site: **UNKNOWN**. The code comments in `_parse_gear` (`:1079-1091`) record that `ir` and base64 `id` decoding turned out to be "item seed data, not type IDs" — evidence that the real format was reverse-engineered by trial and differs from the documented schema at the top of the module (`:7-14`).

## 10. Other importer (Maxroll) — brief

`backend/app/services/importers/maxroll_importer.py`: `URL_PATTERN` `:265`; probes **seven guessed endpoints** (`:275-281`) with spoofed browser UA plus `Referer`/`Origin: https://maxroll.gg` (`:735-744`), then falls back to HTML (`:783-810`). Diagnostics are better than LE Tools: per-attempt status list in the error (`test_build_import.py:3504-3519` asserts "HTTP 403" surfaces), `raw_keys` in `partial_data`. Same structural exposure (undocumented endpoints, datacenter egress, no retries), same `partial_data=result.build_data` drop on hard failure. Live status UNKNOWN.

## 11. What this audit does NOT prove

- It does not prove the 403 was issued by Cloudflare, by LE Tools' origin, or by any specific rule. No upstream response was observed.
- It does not prove that `window.buildInfo` still exists on LE Tools pages today, or that the bookmarklet works today.
- It does not prove the HTML parser would fail on a 200 response today (only that the repo itself asserts so).
- It does not measure how many users hit this path (ImportFailure table not queried; production DB not accessible).
- It does not verify Render outbound IP ranges or how Render forwards client IPs.

## 12. Commands used (summary)

```
sed/grep/cat over backend/app/services/importers/*, backend/app/routes/import_route.py,
  backend/app/services/discord_notifier.py, backend/app/models/__init__.py,
  backend/app/services/build_service.py, frontend/src/components/features/build/BuildImportModal.tsx,
  frontend/src/components/features/build/BuildPlannerPage.tsx, frontend/src/lib/api.ts,
  frontend/public/bookmarklets/let-import.js
git log --format='%ci %h %s' -- <fixtures, importer, bookmarklets>
git rev-parse --is-shallow-repository   # true
pytest (see §7)
python $SCRATCH/imp_route403.py; python $SCRATCH/imp_repro.py
curl robots.txt (blocked locally); local egress-proxy status query
WebFetch x2 (blocked); WebSearch x4
```


---

<!-- FILE: 09_BUILD_IMPORT_CONTRACT.md -->

# 09 — Build Import Contract and Coverage Matrix (Phase 7)

Audit date: 2026-10-06. Audit only; no code changed.
Companion: `08_LAST_EPOCH_TOOLS_IMPORT_FORENSICS.md`.

## 1. Classification definitions

| Class | Definition (applied per field and per build) |
|---|---|
| **EXACT** | Every source value for the field is carried into the Forge payload, persisted, and round-trips with identical meaning; or, if not representable, the import explicitly reports it. |
| **LOSSY** | The field is imported but information is dropped or approximated (counts lost, values guessed, names approximated) **and** the user is told nothing or too little. |
| **PARTIAL** | Some of the field is imported correctly; the remainder is explicitly reported as missing (`missing_fields` / warnings). |
| **UNSUPPORTED** | The Forge has no schema slot for the field, or the importer never reads it. |
| **WRONG** (sub-flag) | The importer emits a plausible-looking but incorrect value without reporting it. Worse than LOSSY because downstream consumers trust it. |

Build-level classification: the lowest class among the fields a typical build actually carries.

## 2. The Forge import schema (what importers must emit)

Producer: `LastEpochToolsImporter._map` (`backend/app/services/importers/lastepochtools_importer.py:915-928`) and `_map_let_build` (`backend/app/routes/import_route.py:253-274`).
Persistence: `build_service.create_build` (`backend/app/services/build_service.py:44-81`) into `Build` (`backend/app/models/__init__.py:75-126`) and `BuildSkill` (`:143-160`).
Frontend type: `ImportedBuild` (`frontend/src/lib/api.ts:553-578`), `GearSlot`/`AffixOnItem` (`frontend/src/types/index.ts:124-135`).

```
{
  name: str, description: str,
  character_class: str, mastery: str, level: int,
  passive_tree: [int]          # node id repeated once per point
  skills: [{skill_name, slot, points_allocated, spec_tree: [int]}],
  gear: [{slot, base_type_id?, item_name, rarity, affixes: [{id, name, tier, decoded?}], _raw?}],
  _source_code (importer) | _import_meta (preview routes)
}
```

Persisted `Build` columns relevant to imports: `name, description, character_class, mastery, level, passive_tree (JSON), gear (JSON), blessings (JSON), is_ssf, is_hc, is_ladder_viable, is_budget, patch_version (default "1.2.1"), cycle (default "1.2"), is_public`. There is **no** column for import provenance (source, source code/URL, import time, importer version, warnings). `_source_code` is silently dropped by `create_build`.

## 3. Import Coverage Matrix — Last Epoch Tools

"LE Tools state" = what the repo believes `window.buildInfo` contains. All such knowledge comes from code comments and synthetic fixtures; none is verified against a live payload (live access blocked, see 08 §6). Treat every cell in that column as **UNVERIFIED** unless marked otherwise.

| # | Field | LE Tools available state | Forge import schema | Parsed (file:line) | Persisted | Used by application | Class today |
|---|---|---|---|---|---|---|---|
| 1 | Class | `bio.characterClass` int 0-4 (mapping verified against game export `last-epoch-data/exports_json/classes.json`: 0 Primalist,1 Mage,2 Sentinel,3 Acolyte,4 Rogue) | `character_class` | `_map` `:832,836-843`. **Missing `bio` defaults to id 0 → Primalist** with no warning. `_map_let_build` `:188,192` same default (`.get(id, "Sentinel")` only for out-of-range). | `Build.character_class` | Planner form (`BuildPlannerPage.tsx:904`), analysis (`build_analysis_service.py:160`) | EXACT when present; WRONG when absent |
| 2 | Mastery | `bio.chosenMastery` 0-3 (0 = unmastered base class, per game export) | `mastery` | `:845-847`; unknown/0 → `missing_fields += "mastery"` but payload gets **first mastery substituted** (`:922`). `_map_let_build` leaves `""` (`:193`). | `Build.mastery` (NOT NULL) | Planner, analysis, meta stats | EXACT 1-3; LOSSY/WRONG for 0 (reported as "mastery" but value invented) |
| 3 | Level | `bio.level` | `level` | `:834` default 70 if missing, unreported | `Build.level` | Planner, analysis | EXACT when present; WRONG default |
| 4 | Attributes / stat points | UNKNOWN whether LE Tools stores | none | not read | none | — | UNSUPPORTED |
| 5 | Passive allocations | `charTree.selected {nodeId: pts}` | `passive_tree [int]` (repeated per point) | `:855-863`; bad keys → `passive_node:` warning | `Build.passive_tree` | Planner tree; analysis maps ints via `PassiveNode.raw_node_id` (`build_analysis_service.py:164,199-200`) | EXACT structurally; **ID-space equivalence between LE Tools node IDs and Forge `raw_node_id` UNVERIFIED** |
| 6 | Passive point totals / respec order / mastery-tree split | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 7 | Skill selection | `skillTrees[].treeID` | `skills[].skill_name` | `:866-879`; unknown treeID → name = raw ID + `skill_id:` warning | `BuildSkill.skill_name` | Planner, analysis (first slot = primary skill) | PARTIAL (reported) |
| 8 | Skill HUD slot | `hud[]` order / `slotNumber` | `skills[].slot` | `:880-884`, sorted `:902` | **Ignored**: `create_build` uses `slot=idx+1` (`build_service.py:73`); `>5` skills silently truncated (`:70`) | Primary-skill selection depends on order | LOSSY |
| 9 | Skill level | `skillTrees[].level` | `points_allocated` | `:898` | `BuildSkill.points_allocated` | Analysis uses as skill level (`build_analysis_service.py:194`) | EXACT (semantics of LE Tools `level` UNVERIFIED) |
| 10 | Skill spec-tree nodes | `skillTrees[].selected {nodeId: pts}` | `spec_tree [int]` | `:887-893` | `BuildSkill.spec_tree` | Analysis `Counter(spec_tree)` (`:206-210`) for primary skill only | EXACT structurally; ID space UNVERIFIED |
| 11 | Equipment slots | `equipment` list or dict; slot by `equipmentSlot`/`slot`/key/index | `gear[].slot` | `_parse_gear` `:1024-1042`, alias table `:1004-1019` | `Build.gear` | Planner, analysis | PARTIAL; unknown slots become `slot_<x>` silently |
| 12 | Base item | `id`/`baseTypeID` (int or base64) | `gear[].item_name`, `base_type_id` | int path `:1056-1068` looks up `_get_base_item_map()` which indexes **`data/items/base_items.json` by sequential enumeration order** (`:105-126`), not by game baseTypeID | `Build.gear` | Planner display, analysis unique lookup | **WRONG** (see §5): body armour → "Iron Helm", axe → "Ornate Helm", idol → "Imperial Boots"; zero warnings |
| 13 | Base item when no ID | — | `item_name: None` | `:1055` guard skips the `gear_base:` warning when `raw_item_id is None` (`:1076-1077`) | yes | — | LOSSY (silent) |
| 14 | Rarity | `ir` (code comment `:1086`: "item seed data, not a rarity code") | `gear[].rarity` | **Inferred from affix count** (`:1121-1131`) or `ur != 0` → unique | yes | Planner display | LOSSY (inferred mechanic, not marked experimental) |
| 15 | Unique identity | `ur` + base | `item_name` | `_resolve_unique_name` picks **first** unique sharing the base (`:278-293`); else `"Unknown Unique (base)"` | yes | Analysis matches `u["name"] == item_name` (`build_analysis_service.py:178-185`); importer writes `"Name (Base)"`, so it never matches → unique stats dropped | LOSSY / WRONG when several uniques share a base |
| 16 | Set items | rarity 5 per old map | — | never produced by heuristic | — | — | UNSUPPORTED |
| 17 | Explicit affixes | `affixes[]` base64 strings or dicts | `affixes[{id,name,tier}]` | `_decode_let_affix` heuristic "candidates" (`:482-549`), `_resolve_affix` first-candidate-wins incl. "second pass: accept any matching candidate regardless of slot" (`:583-587`) | yes | Analysis `gear_affixes` → stat aggregation | **LOSSY/WRONG**: unresolved ones reported (`gear_affix:`), resolved ones are guesses with no confidence flag |
| 18 | Affix tier | dict `tier`/`t` or guessed from varints (`:515-530`) | `tier` | tier base (0- vs 1-indexed) UNVERIFIED | yes | Analysis, craft (`craft_service.py:156` assumes ≥1) | LOSSY |
| 19 | Affix roll values (%) | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 20 | Implicits | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 21 | Sealed affix | UNKNOWN | `AffixOnItem.sealed` exists in frontend type | never set | no | Frontend expects `sealed: boolean` | UNSUPPORTED |
| 22 | Experimental affixes | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 23 | Forging potential | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 24 | Legendary potential / weaver's will | `ur` (meaning disputed in code `:950` vs `:1089`) | none | used only as unique flag | none | — | UNSUPPORTED |
| 25 | Idols | slot alias `idol_altar` exists | `gear[]` with slot `idol_altar` | through `_parse_gear`; base mapping WRONG as #12 | yes (inside gear) | No idol-grid consumer verified | LOSSY/WRONG |
| 26 | Idol altar / grid positions | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 27 | Monolith blessings | UNKNOWN | `Build.blessings` exists | **not read** by any LE Tools path | default `[]` | Planner has blessings UI (`draftBlessings`) | UNSUPPORTED (schema exists, importer gap) |
| 28 | Weaver tree | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 29 | Minion / companion config | UNKNOWN | none | not read | none | — | UNSUPPORTED |
| 30 | Combat config (buffs, enemy, conditions) | UNKNOWN | none | not read | none | Simulator has its own config | UNSUPPORTED |
| 31 | Build name / notes | UNKNOWN | `name`, `description` | synthesized "Imported — Class Mastery" | yes | UI | LOSSY (source title not read) |
| 32 | Game patch / version | UNKNOWN | `patch_version`, `cycle` | not set → defaults `"1.2.1"` / `"1.2"` (`build_service.py:62-63`) | yes (stale default) | Build listing, filters | WRONG (stale default) |
| 33 | Provenance (source, code, URL) | — | `_source_code` | emitted `:927` | **dropped** | — | UNSUPPORTED |
| 34 | SSF/HC/ladder/budget tags | UNKNOWN | booleans | not set (defaults; `is_ladder_viable=True`) | yes | Filters | UNSUPPORTED |

## 4. What a typical imported LE Tools build gets today

| Path | Outcome | Classification |
|---|---|---|
| Import URL tab (`/api/import/build`) | Server fetch → HTTP 403 (production evidence) → nothing saved, hard alert | **Nothing imported** (failure) |
| Quick Fetch tab (`/api/import/url`) | UI disabled | n/a |
| JSON tab + bookmarklet (`/api/import/let/json`) | Mapped preview applied to planner form, no warnings shown | **LOSSY with WRONG gear**, reported as success |

For the only working path:

- Class/mastery/level/passives/skills: largely EXACT structurally, conditional on unverified ID-space equivalence.
- Gear: base names WRONG for integer IDs, rarity inferred, affixes heuristically guessed, uniques unmatched, implicits/rolls/FP/LP/sealed absent.
- Blessings, idol grid, weaver, attributes, config: UNSUPPORTED.

**Overall build classification today: LOSSY (with silently WRONG gear). Never EXACT.**

### Can the system explain WHY?

| Mechanism | Reports | Gaps |
|---|---|---|
| `missing_fields` (`/api/import/build`) | unknown skill IDs, unparseable node keys, unresolved affixes, `gear_base:` for undecodable non-null IDs, `mastery` | Silent on: invented mastery value, default class/level, wrong base names, inferred rarity, guessed affixes, truncated skills, ignored HUD slot, absent blessings/implicits/FP/LP/sealed/idol grid. No list of UNSUPPORTED fields is ever emitted. |
| `_import_meta.gear_missing_fields` (`/url`, `/let/json`) | gear-only warnings | `_map_let_build` swallows passive/skill key errors (`:202-203, 228-229`), and `handleJsonImport` (`BuildImportModal.tsx:167-185`) shows only a success toast; `_import_meta` is never displayed on that path. |
| Discord alert | Source, URL, Missing Fields, Parsed Data, Error | For transport failures, "Missing Fields: None" reads as "nothing was missing" when in fact nothing was attempted; "Parsed Data" is always "No data parsed" on hard failures because the route passes `result.build_data` (always `None`) instead of `result.partial_data` (`import_route.py:575`). No HTTP status field, no upstream headers, no attempt count. |

Verdict: **"Missing Fields: None" on a fetch failure is misleading.** It conflates "not applicable — fetch failed before parsing" with "parsed fully". The system cannot currently explain WHY an LE Tools import is lossy, and for the 403 case cannot explain who returned the 403.

## 5. Evidence for the WRONG gear mapping

Command (local, no network): `$SCRATCH/imp_repro.py` runs `LastEpochToolsImporter()._parse_gear` on the repo's own fixture `backend/tests/fixtures/le_tools_offline_buildinfo_stage_context_sample.json`.

```
helm 0 -> helmet Rusted Coif normal
chest 1 -> body_armour Iron Helm normal
axe 5 -> weapon Ornate Helm normal
axe 12 -> weapon Plate Mail normal
mace 7 -> weapon Ruined Tunic normal
sword 16 -> weapon Chain Gloves normal
idol_1x1 25 -> idol_altar Imperial Boots normal
idol_1x1 26 -> idol_altar Leather Belt normal
axe None -> weapon None normal
belt None -> belt None normal
spear 14 -> weapon Fingerless Gloves normal
None None -> helmet None normal
missing_fields: []
no-bio map: True Primalist Beastmaster 70 ['mastery']
mastery0 map: Sorcerer ['mastery']
```

Root cause: `_get_base_item_map` (`lastepochtools_importer.py:105-126`) enumerates `data/items/base_items.json` (keys `helmet, body, gloves, boots, belt, …`, 115 entries) and uses the running index as the key; the integer-ID branch (`:1056-1061`) treats the game `baseTypeID` as that index. A correct `(baseTypeID, subTypeID)` map already exists in the same module (`_get_item_subtype_map`, `:135-171`) but is only used for base64 IDs.

The committed golden sidecar `backend/tests/fixtures/le_tools_import_context_sidecar_current.json` records these same mappings with `"resolver.status": "resolved"` (e.g. index 1 body_armour → "Iron Helm"; index 6 idol → "Imperial Boots"), so the test suite currently locks the defect in.

Caveat: fixtures are synthetic. Whether live LE Tools sends integer `baseTypeID` (this branch) or base64 `id` (the subtype branch) is UNKNOWN. The defect is real for any integer-ID payload, including the repo's own fixtures.

## 6. Other importers — brief

Maxroll (`backend/app/services/importers/maxroll_importer.py`, 1240 lines): same `ImportResult` contract and same `create_build` persistence, so rows 8, 21-24, 27-34 have the same persistence-side limits. It reports `raw_keys` and overflow counts (`:1194`), and includes per-endpoint HTTP status in errors, so its explainability is better than LE Tools. It relies on 7 guessed, undocumented endpoints (`:275-281`). Full Maxroll field coverage was not audited in depth (out of scope); live behaviour UNKNOWN.

In-house build strings (`frontend/src/logic/importBuild.ts`, `PassiveTreePage.tsx:391`) are a separate Forge-native format, not an external importer.

## 7. What this does NOT prove

- Live LE Tools `window.buildInfo` field names and semantics: every "LE Tools available state" cell is unverified.
- That LE Tools passive/skill node IDs equal Forge `raw_node_id` / spec-tree IDs.
- How often each gap affects real users: the `import_failures` table was not queried.
- Downstream numeric impact of the wrong gear on simulation results was not measured.

## 8. Commands used

```
sed -n / grep -n over the files cited above
python3 -c (inspect data/items/affixes.json, base_items.json, skills_metadata.json,
            last-epoch-data/exports_json/classes.json)
$SCRATCH/venv-backend/bin/python $SCRATCH/imp_repro.py
$SCRATCH/venv-backend/bin/python $SCRATCH/imp_route403.py
pytest run (08 §7): 232 passed
```


---

<!-- FILE: 10_DATABASE_AUDIT.md -->

# 10 — Database / Data Model Audit (Phase 8)

Audit date: 2026-10-06. Code: `HEAD 1efcef7` (2026-05-14). Audit only — no repo code, migrations, or production systems were changed.

## 1. Method and commands

All scratch work ran under the session scratchpad (`$S`), never in the repo or against production.

| Step | Command (abbreviated) | Result |
|---|---|---|
| venv | `python3 -m venv $S/venv && $S/venv/bin/pip install -r backend/requirements.txt` | OK. SQLAlchemy resolved to **2.1.3**, alembic 1.20.0 (both unpinned, transitive) |
| Local Postgres | `initdb`/`pg_ctl` from `/usr/lib/postgresql/16/bin` | **Not possible**: the scratchpad's parent dirs are mode 700 (root), so the `postgres` user cannot reach them, and the environment policy blocked changing those permissions. No online Postgres test was run |
| Migration graph | `flask db heads`, `flask db history` (`DATABASE_URL=postgresql+psycopg2://x:y@127.0.0.1:1/none`) | 1 head (`dd1840cac963`), 15 revisions, 1 branchpoint + 1 mergepoint |
| Offline Postgres DDL | `flask db upgrade --sql > $S/upgrade_offline_pg.sql` | rc=0, 350 lines. The full chain renders as valid Postgres DDL |
| Online replay (SQLite) | copied `backend/migrations` to `$S/migrations_copy`, removed the Postgres-only `'[]'::json` casts, and skipped the `3ffd55fa24ac` FK rename (a no-op on PG). Then `flask db upgrade -d $S/migrations_copy` with `DATABASE_URL=sqlite:///$S/mig.sqlite` | Chain applies cleanly with those 2 patches. **The unmodified chain fails on SQLite** (`ValueError: No such constraint: 'build_skills_build_id_fkey'`) |
| Model↔migration drift | `alembic.autogenerate.compare_metadata(..., compare_type=True, compare_server_default=True)` against the migrated SQLite DB (`$S/compare.py`) | **5 diffs, all `modify_default`** (server defaults in DB, not in models). No table, column, nullability, index, FK, or unique drift |
| Delete-cascade test | `$S/del_test.py`: create a Build, add a BuildView, call `build_service.delete_build` (SQLite with `PRAGMA foreign_keys=ON`) | **`IntegrityError: NOT NULL constraint failed: build_views.build_id`** |
| Payload tests | `$S/poison.py` (test client, testing config, in-memory SQLite) | see §6 |

## 2. Headline numbers

| Item | Count |
|---|---|
| ORM models / tables (excluding `alembic_version`) | **11**: users, builds, build_skills, votes, craft_sessions, craft_steps, item_types, affix_defs, passive_nodes, import_failures, build_views |
| Tables ever created and later dropped | 2 (`loot_filters`, `filter_rules`, dropped in `3ffd55fa24ac`) |
| Migration files | **15** (`backend/migrations/versions/*.py`) |
| Heads | **1** (`dd1840cac963`) |
| Branch / merge points | 1 branch (`a1b2c3d4e5f6` → `b2f8a3d1c7e9` and `f8953bcaab80`), merged by `e2f3a4b5c6d1` |
| `down_revision` inconsistencies | 0 (every `down_revision` resolves; `flask db history` renders the full graph) |
| Structural drift (model vs migrated schema) | 0 |
| Server-default drift | 5 (`import_failures.missing_fields/created_at/updated_at`, `passive_nodes.requires`, `users.is_admin`) |
| JSON columns | 14 (all `JSON`, none `JSONB`; none carry a schema version) |
| CHECK constraints | 0 |
| Enum types | 0 (all enumerations are free `String` columns) |
| Soft-delete columns | 0 |
| FKs with `ON DELETE` behaviour | 0 (all default `NO ACTION`) |

Migration chain (linear except the branch/merge):

```
cf57d3c33180 initial → 3ffd55fa24ac drop loot filters → 8d9b7a5c2e11 affix metadata → b4c1f0f6d2aa widen
→ e07407b85e20 widen → 93e06c1a641f widen → 21bc975a3016 craft_steps.affixes_before
→ f1a2b3c4d5e6 drop instability/fracture → a1b2c3d4e5f6 DROP+RECREATE passive_nodes (string ids)
   ├─ b2f8a3d1c7e9 users.is_admin + import_failures
   └─ f8953bcaab80 FK indexes → d1e2f3a4b5c6 build_views + builds.last_viewed_at
→ e2f3a4b5c6d1 merge → 654f2ebcd332 builds.blessings → dd1840cac963 passive_nodes.requires (HEAD)
```

## 3. Table inventory (final schema = models in `backend/app/models/__init__.py`)

| Table | PK | Key columns / types | Nullability notes | Indexes / uniques | FKs | JSON blobs | Timestamps | Owner |
|---|---|---|---|---|---|---|---|---|
| users (`:52`) | `id` String(36) uuid4 | discord_id S64, username S64, discriminator S8, avatar_url S512, is_active Bool, is_admin Bool | discriminator/avatar nullable | `ix_users_discord_id` UNIQUE | — | — | created/updated (ORM-side) | self |
| builds (`:76`) | `id` S36 | slug S64, name S120, description Text, character_class S32, mastery S32, level SmallInt, patch_version S16 (default "1.2.1"), cycle S16 (default "1.2"), tier S1, vote_count Int, view_count Int, last_viewed_at, is_public, is_ssf/is_hc/is_ladder_viable/is_budget | author_id nullable (anonymous builds) | `ix_builds_slug` UNIQUE, `ix_builds_author_id` | author_id→users | passive_tree, gear, blessings | created/updated, last_viewed_at | author_id or none |
| build_skills (`:140`) | `id` S36 | slot SmallInt, skill_name S64, points_allocated | — | `uq_build_skill_slot(build_id,slot)` | build_id→builds | spec_tree | none | via build |
| votes (`:165`) | `id` S36 | direction SmallInt | — | `uq_user_build_vote(user_id,build_id)`, `ix_votes_build_id` | user_id→users, build_id→builds | — | created/updated | user |
| craft_sessions (`:183`) | `id` S36 | slug S64, item_type S32, item_name S120, item_level, rarity S16, forge_potential | user_id nullable | `ix_craft_sessions_slug` UNIQUE, `ix_craft_sessions_user_id` | user_id→users | affixes | created/updated | user_id or none |
| craft_steps (`:213`) | `id` S36 | step_number, timestamp, action S32, affix_name S64, tier_before/after, roll Float, outcome S16, fp_before/after | — | `ix_craft_steps_session_id` | session_id→craft_sessions | affixes_before | timestamp | via session |
| item_types (`:249`) | `id` Int autoinc | name S64, category S32, base_implicit S120 | — | UNIQUE(name) | — | — | none | reference |
| affix_defs (`:260`) | `id` Int autoinc | name S256, affix_type S16, stat_key S256, class_requirement S128 | — | **no unique on name** (seed dedups by query) | — | tier_ranges, applicable_types, tags | none | reference |
| passive_nodes (`:281`) | `id` S16 (namespaced, e.g. `ac_0`) | raw_node_id Int, character_class, mastery, mastery_index, mastery_requirement, name S64, node_type S16, x, y, max_points, ability_granted, icon | — | PK only (no index on character_class, though `simulate.py:76` filters on it) | — | connections, requires, stats | none | reference |
| import_failures (`:322`) | `id` S36 | source S32, raw_url S2048, error_message S1024 | user_id nullable | **none** (no index on user_id or created_at, though the admin list orders by created_at) | user_id→users | missing_fields, partial_data | created/updated (server default now()) | user_id or none |
| build_views (`:345`) | `id` S36 | viewed_at, viewer_ip_hash S64 (unsalted SHA-256) | — | `ix_build_views_build_id` | build_id→builds | — | viewed_at | via build |

### JSON blob contents (from model comments and services; **no blob carries a schema/version marker**)

| Column | Shape (documented) | Enforced by |
|---|---|---|
| builds.passive_tree | list of node ids; **mixed legacy integers and namespaced strings** (`schemas/__init__.py:80-82`, `routes/builds.py:142-155` skips integer ids) | `fields.List(fields.Raw())`. Integers are never validated |
| builds.gear | list of `{slot, item_name, rarity, affixes:[...]}` | `fields.List(fields.Dict())`. Inner shape unvalidated |
| builds.blessings | list of `{timeline_id, blessing_id, is_grand, value}` | `fields.List(fields.Dict())` |
| build_skills.spec_tree | list of allocated node ids/points within the skill tree | none at create; `skills.py` PATCH rewrites it |
| craft_sessions.affixes / craft_steps.affixes_before | `[{name, tier, sealed}]` | service layer |
| affix_defs.tier_ranges/applicable_types/tags | `{"1":[min,max],...}` / list / list | seed command |
| passive_nodes.connections/requires/stats | id lists / `[{parent_id, points}]` / `[{key,value}]` | seed command |
| import_failures.missing_fields/partial_data | list / free dict | none |

## 4. Provenance / versioning (Phase 8 focus)

* `builds.patch_version` is the only provenance field. It is **client-supplied free text**: `BuildCreateSchema.patch_version = fields.Str(load_default="1.2.1")` (`schemas/__init__.py:90`), with no length validation (the column is `String(16)`). The frontend workspace default is also `"1.2.1"` (`frontend/src/store/buildWorkspace.ts:96`). Meanwhile the server tracks `CURRENT_PATCH=1.4.3` (`config.py:27`), and the seeded demo builds use `"1.4.3"` (`utils/cli.py:146`). New builds and all imported builds (the importer never sets it) are stamped `1.2.1` whatever data they were built with.
* `builds.cycle` defaults to `"1.2"`.
* There is **no data-bundle / game-data version** stored on builds, build_skills, craft sessions, or import_failures. The runtime data version is `'unknown'` anyway. `GameDataPipeline._detect_version` reads `_version` from `affixes.json`, which is a bare list (`pipeline.py:467-471`). `data/version.json` has `"patch_version": "unknown"`. `/api/health` returns `patch_version: unknown`. `/api/version` returns the env default `data_version: 1.0.0`.
* `passive_tree` stores raw node ids. Migration `a1b2c3d4e5f6` **dropped and recreated `passive_nodes`** (Integer ids → String ids). Builds saved before then hold integer ids that no longer match any PK. The create route explicitly skips validating them (`routes/builds.py:149-151`). Later, `flask seed-passives` **deletes** passive_nodes rows not present in the current JSON (`utils/cli.py:256-266`). Saved builds referencing those ids are not updated or flagged, and there is no FK from JSON ids. **The meaning of a saved passive tree cannot be reconstructed from the schema alone.** It depends on whichever `passives.json` was seeded at that time, and that version is not recorded.
* `affix_defs` (DB, seeded once and skip-if-name-exists, `utils/cli.py:73-97`) and `data/items/affixes.json` (read by the runtime pipeline) are **two sources of truth** for affix definitions. `/api/ref/affixes` serves the DB copy (`routes/ref.py:230`); simulations use the JSON copy. Re-running `flask seed` never updates existing rows.

## 5. Reconstructability of a clean database

* **Postgres:** the offline render (`flask db upgrade --sql`) is complete and deterministic: 350 lines, a single head, no data-dependent branching in any upgrade. Online application to an empty PG 15 was **UNKNOWN / not executed** (no runnable Postgres in this environment).
* **Non-Postgres:** the chain is Postgres-only (`'[]'::json` casts in `8d9b7a5c2e11:24` and `654f2ebcd332:25`; a named FK drop in `3ffd55fa24ac:26-32`). Tests use `db.create_all()` on SQLite (`config.py:139`), and `.github/workflows/ci.yml` has no Postgres service and no `flask db upgrade` step. **The migration chain is not exercised by CI.**
* **Schema only, not data.** On Render, `preDeployCommand` runs only `flask db upgrade` (`render.yaml`). The seed steps (`flask seed`, `seed-passives`) exist only in `backend/entrypoint.sh` (the Docker path). A rebuilt production DB would have empty `passive_nodes`/`affix_defs`/`item_types`. `create_build` validates string passive ids against `passive_nodes` (`routes/builds.py:142-155`), so every planner save with namespaced ids would be rejected until someone seeds manually. Whether production was seeded manually: **UNKNOWN**.
* **Downgrades are not reliable:** `3ffd55fa24ac.downgrade` calls `drop_constraint(None, ...)`, which fails. `f1a2b3c4d5e6.downgrade` adds NOT NULL columns without a server default (fails on non-empty tables). `a1b2c3d4e5f6.downgrade` drops passive data. Rollback must be done by restoring the DB, not with `flask db downgrade`.
* **Driver drift:** `SQLAlchemy` is not pinned. A fresh `pip install -r requirements.txt` resolved 2.1.3, whose default `postgresql://` dialect is **psycopg (v3)**, while only `psycopg2-binary` is installed. Verified: `create_app` raised `ModuleNotFoundError: No module named 'psycopg'` with a plain `postgresql://` URL. Render builds with `pip install -r requirements.txt` on every deploy and injects a `postgresql://...` connection string, so the next deploy would likely fail at `flask db upgrade` (preDeploy) before serving. Whether the currently running production build resolved SQLAlchemy 2.0.x or 2.1.x: **UNKNOWN**.

## 6. Integrity, constraints and runtime data behaviour

| # | Observation | Evidence |
|---|---|---|
| a | **Deleting any viewed build fails.** `BuildView.build` uses a plain `backref="views"` (no cascade, no `ON DELETE`). On `session.delete(build)` the ORM tries to null `build_views.build_id` (NOT NULL), which raises IntegrityError and returns 500. Every build opened in the UI gets a BuildView (`POST /api/builds/<slug>/view`), so in practice most builds cannot be deleted | `models/__init__.py:353-360`; `$S/del_test.py` output `IntegrityError ... build_views.build_id` |
| b | `import_failures.user_id → users` and all other FKs have no `ON DELETE`. There is no user-deletion path at all (no endpoint or CLI) | grep `delete` in routes/cli |
| c | No CHECK constraints: `votes.direction`, `builds.tier`, `builds.level`, `craft_steps.outcome`, `affix_defs.affix_type`, `passive_nodes.node_type` are free values enforced (if at all) only by marshmallow | models |
| d | Over-length strings: `patch_version` (S16), `cycle` (S16) and `mastery` have no length validation. A 40-char `patch_version` was accepted (201) on SQLite. On Postgres it raises `StringDataRightTruncation` → 500 | `$S/poison.py` |
| e | Malformed JSON accepted and later breaks aggregate readers: an anonymous `POST /api/builds` with `gear:[{"affixes":["not-a-dict"]}]` returned 201, and on the next cache miss `GET /api/meta/snapshot` returned **500 for every visitor** (`'str' object has no attribute 'get'`, `meta_analytics_service.py:85-90`) | `$S/poison.py` output `snapshot after 500` |
| f | Counter lost updates: `vote_count` and `view_count` are Python read-modify-write (`build_service.py:88-90,196-210`, `views.py:43`), not `UPDATE ... SET x = x + 1`. Concurrent votes/views can be lost. `tier` derives from `vote_count` | code |
| g | Slug race: `_unique_slug` checks then inserts (`build_service.py:32-37`). Concurrent same-name creates can hit the unique index and return 500. Slugs are derived from the build name (predictable). See API audit for private-build exposure | code |
| h | Indexing gaps: no index on `passive_nodes.character_class` (filtered on every `/api/simulate/stats|build`), `import_failures.created_at`, `build_views.viewed_at` (time-series reads), `builds.is_public`/`vote_count`/`created_at` (list sorting). Impact at current scale: UNKNOWN (row counts unknown) | models |
| i | Unbounded growth: `build_views` (one row per IP per build per hour, no retention), `import_failures` (anonymous writers via `/api/import/let/json`, no retention), and `craft_sessions` (anonymous creation) | routes |
| j | `viewer_ip_hash` is an unsalted SHA-256 of the IPv4 address, which is reversible by brute force over 2^32. If Render's proxy address is what `remote_addr` sees (no ProxyFix, see API audit), all rows hash the same value | `views.py:20-22,34` |
| k | `users.is_active` exists but is never checked by `login_required`/`get_current_user` | `utils/auth.py:78-94` |
| l | `build_skills.slot` comment says 0-4, but the service writes 1-5 (`build_service.py:69,108`) | code |
| m | Ownership model: builds/craft sessions with `author_id/user_id = NULL` are "anonymous" and **mutable by anyone** (see API audit). There is no claim/transfer flow and no soft delete | routes |
| n | Auth/session state: stateless JWT only (no session or token table, no revocation). JWT lifetime 3600 s (`config.py:9-11`) | — |
| o | Connection budget: production pool 10 + 20 overflow per process × 4 gunicorn workers = up to 120 connections, plus preDeploy and CLI. The Render Postgres starter connection limit is **UNKNOWN** | `config.py:86-91`, `render.yaml` |

## 7. Findings summary

| ID | Sev | Title |
|---|---|---|
| DB-1 | P1 | Build delete fails (500) for any build with a BuildView row (missing cascade) |
| DB-2 | P1 | Unpinned SQLAlchemy resolves to 2.1 → `postgresql://` needs psycopg3 (not installed) → app/migrations fail on fresh build |
| DB-3 | P1 | Builds carry no data-bundle version; `patch_version` is client free text defaulting to stale "1.2.1"; passive ids reinterpreted/pruned across reseeds |
| DB-4 | P2 | Render deploy runs migrations only; reference tables (passive_nodes/affix_defs/item_types) need manual seeding; create_build depends on them |
| DB-5 | P2 | Migration chain Postgres-only and untested in CI; downgrades broken |
| DB-6 | P2 | Unvalidated JSON blobs persisted; a single malformed anonymous build 500s `/api/meta/snapshot` sitewide |
| DB-7 | P2 | Over-length strings (patch_version/cycle/mastery) reach DB → 500 on Postgres |
| DB-8 | P3 | Counter lost updates (vote_count/view_count), slug check-then-insert race |
| DB-9 | P3 | Dual affix source of truth (affix_defs table vs affixes.json); seed never updates |
| DB-10 | P3 | No CHECK/enum constraints, no FK ON DELETE, missing indexes, unbounded build_views/import_failures growth, server-default drift (5) |
| DB-11 | P3 | `users.is_active` never enforced; weak IP pseudonymisation |

## 8. UNKNOWNs

* Production row counts, real data, whether prod reference tables are seeded, the production `alembic_version` value.
* Which SQLAlchemy version the currently running production image installed.
* Online behaviour of the chain on real Postgres 15 (only the offline SQL render was produced).
* Render Postgres connection limit and plan memory.

## 9. What this does NOT prove

* It does not prove the production schema equals the migration head. Production was not contacted.
* The SQLite-based drift comparison cannot detect Postgres-specific type differences (e.g. `JSON` vs `JSONB`, timestamp precision). It covers tables, columns, nullability, indexes, uniques and FKs.
* The BuildView delete failure was reproduced on SQLite with FK enforcement. On Postgres the same ORM behaviour (null-out of a NOT NULL column) is expected but was not executed.
* It does not quantify how many saved builds hold stale or legacy passive ids. That needs production data.


---

<!-- FILE: 11_API_BACKEND_AUDIT.md -->

# 11 — API / Backend Audit (Phase 9)

Audit date: 2026-10-06. Code: `HEAD 1efcef7` (2026-05-14). Audit only. Nothing in the repo was changed apart from these report files, and production (`api.epochforge.gg`) was not contacted.

## 1. Method and commands

| Step | Command / script (in the session scratchpad `$S`) | Purpose |
|---|---|---|
| URL map | `$S/urlmap.py`: `create_app("testing")`, iterate `app.url_map`, resolve each view to `file:line` via `inspect` | Endpoint inventory (171 rules + static) |
| Rate limits | `$S/lim.py`: `create_app("development")`, read `limiter.limit_manager._decorated_limits` / `_default_limits` | Per-route limits (46 decorated) and default limits |
| Auth/ownership probes | `$S/admin_test.py`, `$S/poison.py`, `$S/err.py` (Flask test client, `testing` config, in-memory SQLite; `admin.AFFIXES_PATH` monkeypatched to a **scratch copy** so no repo file was written; `git status` confirmed clean) | Verify unauthenticated access and IDOR |
| CPU/memory probes | `$S/cpu.py`, `$S/v2_timing.py`, `$S/rss.py` (in-process test client, `ulimit -v 3000000` guard) | Measure wall time / peak RSS of expensive endpoints |
| Frontend usage | `grep -rnoE` over `frontend/src` for `"/<prefix>..."` literals (excluding tests), stored at `$S/fe_paths.txt` | Which endpoints the SPA calls |
| Deploy config | `render.yaml`, `backend/Procfile`, `backend/entrypoint.sh`, `backend/config.py` | Runtime: `gunicorn wsgi:app --workers=4 --threads=2 --timeout=120 --preload`, starter plan |

Measurements are single-process, on this audit machine, not on Render hardware. Treat absolute numbers as order-of-magnitude.

## 2. Headline numbers

| Item | Count |
|---|---|
| URL rules (excl. `static`) | **171** |
| Distinct view functions | **130** (the `experimental` blueprint is registered twice, at `/experimental` and `/api/experimental`, giving 41 duplicate rules) |
| Blueprints registered | 28 (29 registrations) |
| Methods | GET 138, POST 28, PATCH 3, DELETE 2 |
| Rules requiring login | **7** (`auth.me`, builds delete/vote, profile ×3, admin import-failures (+is_admin)) |
| Rules with optional JWT (anonymous allowed) | 10 |
| Rules with **no auth at all** | **154**, including **all 3 mutating "admin/load" endpoints** (`PATCH /api/admin/affixes/<id>`, `GET /api/admin/affixes`, `POST /api/load/game-data`) |
| Unauthenticated CPU-heavy compute endpoints | 25 (11 `/api/simulate/*`, `/api/optimize/build`, `/api/bis/search`, `/api/craft/{predict,simulate}`, 7 `/api/builds/<slug>/{simulate,optimize×2,report,analysis×3}`, `/api/compare/...`, `/api/load/game-data`) |
| Unauthenticated, **not env-gated** v2 bundle endpoints that re-parse large JSON from disk per request | 76 (38 × 2 mounts). Bundles up to 37 MB (`v2_modifier_registry.json`) |
| Routes with an explicit `@limiter.limit` | 46. All others get production default `1000/day;200/hour;30/minute` per key per route |
| Endpoints the frontend calls (grep) | 77 rules. Not called: the 41 `/experimental/*` duplicates, `/api/simulate/{stats,combat,defense,optimize,sensitivity}`, `/api/jobs/<id>`, `/api/craft/{simulate,<slug>/undo, DELETE <slug>}`, `POST /api/builds/<slug>/optimize`, 6 `/api/ref/*` detail routes, `/api/admin/import-failures`, forge-safe experimental routes, `/debug/forge-safe-affixes`, `/api/health` (Render probe) |

## 3. Cross-cutting backend behaviour

* **Auth model:** Discord OAuth2 → JWT (HS256, 1 h, `config.py:9-11`) returned to the SPA **in the redirect URL query string** (`routes/auth.py:144-146`). The SPA keeps it in memory and sends a Bearer header (`frontend/src/lib/api.ts:81-83`). The OAuth authorize URL carries **no `state` parameter** (`routes/auth.py:49-55`), so login CSRF is possible. Logout is a no-op and tokens cannot be revoked. `users.is_active` is never checked. `owner_required` (`utils/auth.py:97-125`) is unused and would raise a NameError (`unauthorized` is not imported in its scope).
* **Dev login:** `GET /api/auth/dev-login` is gated by `current_app.debug`. Production config sets `DEBUG=False`, and the testing probe returned 404. Production `wsgi.py` defaults `FLASK_ENV=production`, so this is safe unless `FLASK_ENV=development` is set on Render (`render.yaml` sets `production`).
* **Admin:** there is **no admin decorator**. Only `/api/admin/import-failures` checks `is_admin`. `/api/admin/affixes` (GET, PATCH) and `/api/load/game-data` have **no authentication**. The frontend ships an anonymous "Affix Editor" at SPA route `/affixes` (`frontend/src/App.tsx:232`) and a Data Manager at `/data-manager` (`App.tsx:244`) that call them.
* **Rate limiting:** Flask-Limiter 3.7, `key_func=get_remote_address` (`app/__init__.py:16`), storage `REDIS_URL`. If the Redis ping fails at boot it silently falls back to `memory://` (`app/__init__.py:31-45`), which gives per-worker counters (×4 effective). **No `ProxyFix` / `X-Forwarded-For` handling exists anywhere in the backend** (grep). Behind Render's proxy, `request.remote_addr` is expected to be the proxy's address. That would make every limit a **sitewide shared bucket** (one heavy user can 429 everyone, e.g. 30/min across all users on undecorated routes, or `2 per minute` for all anonymous imports). It would also collapse `build_views` dedupe to a single hash. Whether Render presents the client IP as the TCP peer: **UNKNOWN (likely not)**. This must be verified in production logs (`rate_limit_exceeded ip=` lines).
* **Error handling:** `@app.errorhandler(Exception)` (`app/__init__.py:260-264`) also catches werkzeug `HTTPException`s. Verified: a 405 (POST to `/api/health`) and a 400 (malformed JSON body to `POST /api/builds` / `/api/bis/search`) both return **500 "Internal server error"** and are logged as unhandled exceptions. Several routes echo raw exception text to clients (`load.py:41`, `optimize.py:68`, `import_route.py:357,488,603`, the v2 routes' `message: str(exc)` with absolute server paths).
* **Request size:** `MAX_CONTENT_LENGTH` is not set. JSON bodies are unbounded (limited only by the gunicorn/Render proxy). The lists `gear`, `passive_tree`, `skills`, `blessings`, `affixes`, `targets` and `steps` have no length caps in several schemas.
* **Timeouts:** gunicorn `--timeout 120`. There are no per-request compute budgets. The async job mode (`"async": true` on `/api/simulate/combat` and `/build`) submits to a per-worker `ThreadPoolExecutor(max_workers=4)` with an **unbounded queue** (`utils/jobs.py:24`), so it bypasses the request timeout. Job ids are 8 hex chars and readable by anyone. Jobs are lost on worker restart.
* **Caching:** Redis cache helpers (`utils/cache.py`). `delete_pattern` uses Redis **`KEYS`** (`cache.py:72`), which is O(N) and blocking, and is called on every build create/update/delete/vote and skill PATCH. Build list is cached 30 s, meta 120 s, optimize 30 min, ref data via `cached_route`.
* **Observability:** stdlib logging, JSON in production. Slow-request warning at more than 500 ms (`app/__init__.py:170-175`), `X-Response-Time` header, 429 logging. No request id, no error tracker (no Sentry), no metrics. `/api/health` returns `ok` without checking DB or Redis. `/api/version` forks `git rev-parse` on every call (`version.py:47-55`).
* **External network:** Discord OAuth (10 s timeouts), Discord webhook for import failures (synchronous in the request, 10 s), LastEpochTools fetch (15 s), Maxroll importer that tries **7 API URLs + 1 HTML URL sequentially, each with a 15 s timeout** (`maxroll_importer.py:275-281,749-790`). The worst case of ~120 s+ reaches the gunicorn worker timeout. All outbound hosts are hard-coded and no SSRF was found (`import/url` and the importers build URLs from a regex-captured code only).
* **"fix: expose v2 debug routes" (9f38e8e):** this commit changed **only the frontend** (`frontend/src/App.tsx`, plus one test). It moved 10 SPA routes (`/debug/v2`, `/debug/forge-safe-affixes`, `/debug/v2-{affixes,items,unique-sets,idols,classes,passives,skills,stats-modifiers}`) out of the `IS_DEV` guard so they render in production builds. The backend endpoints they call (`/api/experimental/v2/...`) were **already unauthenticated and not env-gated**. Only the forge-safe catalog routes (`FORGE_SAFE_AFFIX_CATALOG_ENABLED`) and `/debug/forge-safe-affixes` (`FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED`) are env-gated, and `render.yaml` sets neither, so they return 404 in production. The practical effect is that public SPA pages now drive the heaviest read endpoints in the API (`/api/experimental/v2/modifiers/debug`: ~2.6 s and ~135 MB transient RSS per call, measured). They also expose absolute server file paths (`source_path`) and internal validation reports to any visitor.

## 4. Verified security / reliability findings

| ID | Sev | Finding | Evidence (verified unless noted) |
|---|---|---|---|
| API-1 | **P0** | Unauthenticated write to server game data: `PATCH /api/admin/affixes/<id>` rewrites `data/items/affixes.json` on disk. `POST /api/load/game-data` (also no auth) hot-reloads the pipeline from disk, so tampered affixes feed simulations and crafting for that worker until redeploy. A malformed value can also make `load_all()` raise after it has cleared the cache, leaving the worker with empty data | `admin.py:68-90`, `load.py:21-41`, `pipeline.py:110-148`. Probe: anon PATCH → 200, scratch file name changed to `AUDIT-TAMPER` |
| API-2 | **P1** | Unauthenticated memory/CPU exhaustion: `POST /api/simulate/multi-target` has no upper bounds on `max_duration`, `tick_size` or number of `targets`, and returns every damage event. One request (3600 s / 0.01 tick / 10 targets) took 17.3 s and **1.66 GB RSS**. A larger input was **SIGKILLed** (rc 137). The starter-plan instance (4 workers) would be OOM-killed | `multi_target.py:40-70,122-135`; `$S/cpu.py mt` |
| API-3 | P1 | Unauthenticated, ungated v2 endpoints re-read and parse multi-MB bundles on every request (modifiers 37 MB: ~2.7 s, about +135 MB; skills 20 MB: ~1.6 s). Two concurrent modifiers calls peaked at 384 MB RSS. They are now linked from public SPA pages (9f38e8e). 76 such rules, rate limit default 30/min per key | `experimental.py:1304-1350`; `$S/v2_timing.py`, `$S/rss.py` |
| API-4 | P1 | IDOR: `PATCH /api/builds/<slug>/skills/<skill_id>/nodes/<node_id>` has **no auth or ownership check**. An anonymous caller changed the skill allocation of another user's *private* build (200) | `skills.py:281-375`; `$S/poison.py` |
| API-5 | P1 | Anonymous builds are writable by anyone (`PATCH /api/builds/<slug>`, `builds.py:205-212`) and **deletable by any logged-in user** (`builds.py:239`, verified 204). Anonymous craft sessions likewise (`craft.py:139-142,166-169,207-209`) | `$S/poison.py` |
| API-6 | P1 | Private builds (`is_public=False`, including every imported build, forced private at `import_route.py:592`) are fully readable via `GET /api/builds/<slug>`, `/simulate`, `/skills`, `/optimize`, `/analysis/*` and `/api/compare/...`. Only `/report` checks. Slugs are derived from the build name (`build_service.py:26-37`), so they are guessable | verified 200 on GET, simulate and skills; 403 on report |
| API-7 | P1 | No ProxyFix: rate limits, import anon limits and view dedupe key on `remote_addr`, which on Render is probably the proxy (UNKNOWN), giving sitewide shared buckets / ineffective per-client limiting | grep (no `ProxyFix`/`X-Forwarded`) |
| API-8 | P1 | `DELETE /api/builds/<slug>` returns 500 for any build that has a view record (see DB-1) | `$S/del_test.py` |
| API-9 | P2 | HTTP errors (400/405/415...) are converted to 500 by the catch-all handler, and logged as unhandled exceptions | `$S/err.py` |
| API-10 | P2 | OAuth: no `state` (login CSRF), JWT in URL query (history/logs/Referer), no revocation, `is_active` ignored | `auth.py:49-55,144-146,193-196` |
| API-11 | P2 | A malformed `gear` blob from an anonymous create makes `/api/meta/snapshot` return 500 sitewide (see DB-6) | `$S/poison.py` |
| API-12 | P2 | Async job mode: unbounded per-worker queue, 4 extra compute threads per worker, results world-readable by 8-hex id, no auth | `utils/jobs.py`, `simulate.py:139-152,306-321` |
| API-13 | P2 | Bounded but heavy anonymous compute: `/api/simulate/encounter` worst case 11.7 s, `/api/optimize/build` (1000 variants × depth 10) 8.3 s, `/api/simulate/rotation` 7.6 s. 8 request threads per instance means a handful of anonymous clients can saturate it | `$S/cpu.py` |
| API-14 | P2 | Maxroll import can hold a worker for more than 120 s (8 sequential fetches × 15 s, plus a sync Discord webhook), reaching the gunicorn timeout | `maxroll_importer.py:749-790` |
| API-15 | P2 | Anonymous callers can create unbounded `import_failures` rows and Discord webhook alerts (`/api/import/let/json`, 20/min/key) | `import_route.py:455-474` |
| API-16 | P2 | `/api/import/build` bypasses `BuildCreateSchema` and passive validation (calls `build_service.create_build` directly) and stamps `patch_version` "1.2.1" | `import_route.py:590-605` |
| API-17 | P3 | Redis `KEYS` in hot write paths; `/api/version` subprocess per call; `/api/health` without dependency checks; `/api/profile/sessions` has unbounded `per_page`, N+1 on `steps`, and returns 500 on a non-integer `page`; `create_build` does one query per passive id | code |
| API-18 | P3 | Dead / legacy surface: 41 duplicate `/experimental/*` rules, 5 unused `/api/simulate/*` stateless routes, `POST /api/builds/<slug>/optimize`, `/api/jobs`, craft simulate/undo/delete, unused `owner_required`, `admin.list_import_failures` (no UI) | grep |

## 5. Endpoint inventory

Columns: **Auth** = none / optional JWT (anonymous allowed) / required. **Rate limit** = the explicit decorator, or "default" (prod: `1000/day;200/hour;30/minute` per key). **FE uses** = a literal path found in `frontend/src` (non-test). This is grep-based and may miss dynamically built paths. **Source** is relative to `backend/`.

| # | Method | Path | Endpoint | Auth | Rate limit | FE uses | Source | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | GET | `/api/admin/affixes` | admin.list_affixes | none | default | yes | app/routes/admin.py:41 | NO AUTH; dumps full affixes.json (1.2MB) |
| 2 | PATCH | `/api/admin/affixes/<affix_id>` | admin.update_affix | none | 30 per 1 minute | yes | app/routes/admin.py:68 | **NO AUTH; writes data/items/affixes.json on server disk** (verified) |
| 3 | GET | `/api/admin/import-failures` | admin.list_import_failures | required+admin | 60 per 1 minute | no (grep) | app/routes/admin.py:96 | login + is_admin check in body |
| 4 | GET | `/api/affixes/catalog` | affixes.list_catalog_affixes | none | default | yes | app/routes/affixes.py:25 |  |
| 5 | GET | `/api/affixes/catalog/<affix_id>` | affixes.catalog_affix_detail | none | default | yes | app/routes/affixes.py:59 |  |
| 6 | GET | `/api/affixes/catalog/summary` | affixes.catalog_summary | none | default | yes | app/routes/affixes.py:47 |  |
| 7 | GET | `/api/affixes/experimental/forge-safe-affixes` | affixes.experimental_forge_safe_affixes | none | default | no (grep) | app/routes/affixes.py:74 |  |
| 8 | GET | `/api/auth/dev-login` | auth.dev_login | none | default | yes | app/routes/auth.py:150 | 404 unless app.debug |
| 9 | GET | `/api/auth/discord` | auth.discord_login | none | 20 per 1 minute | yes | app/routes/auth.py:29 |  |
| 10 | GET | `/api/auth/discord/authorized` | auth.discord_authorized | none | 20 per 1 minute | yes | app/routes/auth.py:59 | no OAuth state param; JWT returned in URL query |
| 11 | POST | `/api/auth/logout` | auth.logout | none | default | no (grep) | app/routes/auth.py:193 | stateless no-op |
| 12 | GET | `/api/auth/me` | auth.me | required | default | yes | app/routes/auth.py:184 |  |
| 13 | POST | `/api/bis/search` | bis.bis_search | none | 15 per 1 minute | yes | app/routes/bis_search.py:52 |  |
| 14 | GET | `/api/builds` | builds.list_builds | none | default | yes | app/routes/builds.py:69 | per_page capped 100; cached 30s |
| 15 | POST | `/api/builds` | builds.create_build | optional JWT | 20 per 1 minute | yes | app/routes/builds.py:154 | validates passive IDs one query per node (N queries) |
| 16 | GET | `/api/builds/<slug>` | builds.get_build | optional JWT | default | yes | app/routes/builds.py:178 | no is_public check (verified); view_count RMW |
| 17 | PATCH | `/api/builds/<slug>` | builds.update_build | optional JWT | 20 per 1 minute | yes | app/routes/builds.py:199 | anon-authored builds editable by anyone (verified) |
| 18 | DELETE | `/api/builds/<slug>` | builds.delete_build | required | 10 per 1 minute | yes | app/routes/builds.py:230 | any logged-in user can delete anon builds (verified); 500 if build has views (verified) |
| 19 | GET | `/api/builds/<slug>/analysis/boss/<boss_id>` | analysis.boss_analysis | none | 10 per 1 minute | yes | app/routes/analysis.py:89 | no is_public check |
| 20 | GET | `/api/builds/<slug>/analysis/corruption` | analysis.corruption_analysis | none | 10 per 1 minute | yes | app/routes/analysis.py:145 | no is_public check |
| 21 | GET | `/api/builds/<slug>/analysis/gear-upgrades` | analysis.gear_upgrades | none | 10 per 1 minute | yes | app/routes/analysis.py:181 | no is_public check |
| 22 | POST | `/api/builds/<slug>/optimize` | builds.optimize_build | none | 10 per 1 minute | no (grep) | app/routes/builds.py:267 | no is_public check; not called by FE |
| 23 | GET | `/api/builds/<slug>/optimize` | builds.optimize_build_v2 | none | 10 per 1 minute | yes | app/routes/builds.py:286 | no is_public check; cached 30 min |
| 24 | GET | `/api/builds/<slug>/report` | report.get_report | none | 20 per 1 minute | yes | app/routes/report.py:21 | checks is_public/owner (verified 403) |
| 25 | POST | `/api/builds/<slug>/simulate` | builds.simulate_build | none | 10 per 1 minute | yes | app/routes/builds.py:252 | no is_public check (verified) |
| 26 | GET | `/api/builds/<slug>/skills` | skills.get_build_skills | none | 20 per 1 minute | yes | app/routes/skills.py:218 | no is_public check (verified) |
| 27 | PATCH | `/api/builds/<slug>/skills/<skill_id>/nodes/<int:node_id>` | skills.allocate_skill_node | none | 30 per 1 minute | yes | app/routes/skills.py:281 | **NO ownership check: anon can edit any build (verified)** |
| 28 | POST | `/api/builds/<slug>/view` | views.track_view | none | 60 per 1 minute | yes | app/routes/views.py:27 | writes BuildView row; IP hash keyed on remote_addr |
| 29 | POST | `/api/builds/<slug>/vote` | builds.vote | required | 30 per 1 minute | yes | app/routes/builds.py:363 |  |
| 30 | GET | `/api/builds/meta/snapshot` | builds.meta_snapshot | none | default | yes | app/routes/builds.py:120 |  |
| 31 | GET | `/api/compare/<slug_a>/<slug_b>` | compare.compare | none | 15 per 1 minute | yes | app/routes/compare.py:33 | no is_public check |
| 32 | POST | `/api/craft` | craft.create_session | optional JWT | 30 per 1 minute | yes | app/routes/craft.py:45 |  |
| 33 | GET | `/api/craft/<slug>` | craft.get_session | none | default | yes | app/routes/craft.py:120 |  |
| 34 | DELETE | `/api/craft/<slug>` | craft.delete_session | optional JWT | 10 per 1 minute | no (grep) | app/routes/craft.py:201 | anon sessions deletable by anyone with slug |
| 35 | POST | `/api/craft/<slug>/action` | craft.apply_action | optional JWT | 60 per 1 minute | yes | app/routes/craft.py:129 | anon sessions mutable by anyone with slug (slug=token_urlsafe(8)) |
| 36 | GET | `/api/craft/<slug>/summary` | craft.get_summary | none | default | yes | app/routes/craft.py:193 |  |
| 37 | POST | `/api/craft/<slug>/undo` | craft.undo_action | optional JWT | 30 per 1 minute | no (grep) | app/routes/craft.py:157 | same as action |
| 38 | POST | `/api/craft/predict` | craft.predict | none | 30 per 1 minute | yes | app/routes/craft.py:58 |  |
| 39 | POST | `/api/craft/simulate` | craft.simulate | none | 20 per 1 minute | no (grep) | app/routes/craft.py:99 |  |
| 40 | GET | `/api/entities/bosses` | entities.list_bosses | none | default | yes | app/routes/entities.py:17 |  |
| 41 | GET | `/api/experimental/forge-safe-affixes` | api_experimental.forge_safe_affix_catalog | none | default | no (grep) | app/routes/experimental.py:78 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 42 | GET | `/api/experimental/forge-safe-affixes/<affix_id>` | api_experimental.forge_safe_affix_detail | none | default | no (grep) | app/routes/experimental.py:170 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 43 | GET | `/api/experimental/forge-safe-affixes/compare-legacy` | api_experimental.compare_forge_safe_affixes_to_legacy | none | default | no (grep) | app/routes/experimental.py:102 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 44 | GET | `/api/experimental/v2/affixes` | api_experimental.v2_affix_catalog | none | default | yes | app/routes/experimental.py:197 | NOT env-gated; parses bundle JSON from disk per request |
| 45 | GET | `/api/experimental/v2/affixes/<path:affix_id>` | api_experimental.v2_affix_detail | none | default | no (grep) | app/routes/experimental.py:241 | NOT env-gated; parses bundle JSON from disk per request |
| 46 | GET | `/api/experimental/v2/affixes/debug` | api_experimental.v2_affix_debug | none | default | no (grep) | app/routes/experimental.py:279 | NOT env-gated; parses bundle JSON from disk per request |
| 47 | GET | `/api/experimental/v2/classes` | api_experimental.v2_classes | none | default | yes | app/routes/experimental.py:691 | NOT env-gated; parses bundle JSON from disk per request |
| 48 | GET | `/api/experimental/v2/classes/<path:class_id>` | api_experimental.v2_class_detail | none | default | no (grep) | app/routes/experimental.py:721 | NOT env-gated; parses bundle JSON from disk per request |
| 49 | GET | `/api/experimental/v2/classes/debug` | api_experimental.v2_class_mastery_debug | none | default | no (grep) | app/routes/experimental.py:708 | NOT env-gated; parses bundle JSON from disk per request |
| 50 | GET | `/api/experimental/v2/idols` | api_experimental.v2_idols | none | default | yes | app/routes/experimental.py:599 | NOT env-gated; parses bundle JSON from disk per request |
| 51 | GET | `/api/experimental/v2/idols/<path:idol_id>` | api_experimental.v2_idol_detail | none | default | no (grep) | app/routes/experimental.py:623 | NOT env-gated; parses bundle JSON from disk per request |
| 52 | GET | `/api/experimental/v2/idols/affixes` | api_experimental.v2_idol_affixes | none | default | yes | app/routes/experimental.py:639 | NOT env-gated; parses bundle JSON from disk per request |
| 53 | GET | `/api/experimental/v2/idols/affixes/<path:affix_id>` | api_experimental.v2_idol_affix_detail | none | default | no (grep) | app/routes/experimental.py:662 | NOT env-gated; parses bundle JSON from disk per request |
| 54 | GET | `/api/experimental/v2/idols/debug` | api_experimental.v2_idol_debug | none | default | no (grep) | app/routes/experimental.py:678 | NOT env-gated; parses bundle JSON from disk per request |
| 55 | GET | `/api/experimental/v2/items/bases` | api_experimental.v2_item_bases | none | default | yes | app/routes/experimental.py:308 | NOT env-gated; parses bundle JSON from disk per request |
| 56 | GET | `/api/experimental/v2/items/bases/<path:item_base_id>` | api_experimental.v2_item_base_detail | none | default | no (grep) | app/routes/experimental.py:345 | NOT env-gated; parses bundle JSON from disk per request |
| 57 | GET | `/api/experimental/v2/items/debug` | api_experimental.v2_item_debug | none | default | no (grep) | app/routes/experimental.py:416 | NOT env-gated; parses bundle JSON from disk per request |
| 58 | GET | `/api/experimental/v2/items/implicits` | api_experimental.v2_item_implicits | none | default | yes | app/routes/experimental.py:383 | NOT env-gated; parses bundle JSON from disk per request |
| 59 | GET | `/api/experimental/v2/masteries` | api_experimental.v2_masteries | none | default | yes | app/routes/experimental.py:737 | NOT env-gated; parses bundle JSON from disk per request |
| 60 | GET | `/api/experimental/v2/masteries/<path:mastery_id>` | api_experimental.v2_mastery_detail | none | default | no (grep) | app/routes/experimental.py:754 | NOT env-gated; parses bundle JSON from disk per request |
| 61 | GET | `/api/experimental/v2/modifiers` | api_experimental.v2_modifiers | none | default | no (grep) | app/routes/experimental.py:987 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 62 | GET | `/api/experimental/v2/modifiers/<path:modifier_id>` | api_experimental.v2_modifier_detail | none | default | no (grep) | app/routes/experimental.py:1035 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 63 | GET | `/api/experimental/v2/modifiers/debug` | api_experimental.v2_modifier_debug | none | default | yes | app/routes/experimental.py:1021 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 64 | GET | `/api/experimental/v2/passives` | api_experimental.v2_passives | none | default | yes | app/routes/experimental.py:770 | NOT env-gated; parses bundle JSON from disk per request |
| 65 | GET | `/api/experimental/v2/passives/<path:tree_id>` | api_experimental.v2_passive_detail | none | default | no (grep) | app/routes/experimental.py:806 | NOT env-gated; parses bundle JSON from disk per request |
| 66 | GET | `/api/experimental/v2/passives/<path:tree_id>/nodes/<path:node_id>` | api_experimental.v2_passive_node_detail | none | default | no (grep) | app/routes/experimental.py:825 | NOT env-gated; parses bundle JSON from disk per request |
| 67 | GET | `/api/experimental/v2/passives/debug` | api_experimental.v2_passive_debug | none | default | no (grep) | app/routes/experimental.py:793 | NOT env-gated; parses bundle JSON from disk per request |
| 68 | GET | `/api/experimental/v2/sets` | api_experimental.v2_sets | none | default | yes | app/routes/experimental.py:518 | NOT env-gated; parses bundle JSON from disk per request |
| 69 | GET | `/api/experimental/v2/sets/<path:set_id>` | api_experimental.v2_set_detail | none | default | no (grep) | app/routes/experimental.py:547 | NOT env-gated; parses bundle JSON from disk per request |
| 70 | GET | `/api/experimental/v2/sets/debug` | api_experimental.v2_set_debug | none | default | no (grep) | app/routes/experimental.py:592 | NOT env-gated; parses bundle JSON from disk per request |
| 71 | GET | `/api/experimental/v2/skills` | api_experimental.v2_skills | none | default | yes | app/routes/experimental.py:841 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 72 | GET | `/api/experimental/v2/skills/<path:skill_id>` | api_experimental.v2_skill_detail | none | default | no (grep) | app/routes/experimental.py:931 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 73 | GET | `/api/experimental/v2/skills/<path:skill_id>/tree` | api_experimental.v2_skill_tree_by_skill | none | default | no (grep) | app/routes/experimental.py:912 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 74 | GET | `/api/experimental/v2/skills/debug` | api_experimental.v2_skill_debug | none | default | no (grep) | app/routes/experimental.py:864 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 75 | GET | `/api/experimental/v2/skills/trees/<path:tree_id>` | api_experimental.v2_skill_tree_detail | none | default | no (grep) | app/routes/experimental.py:877 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 76 | GET | `/api/experimental/v2/skills/trees/<path:tree_id>/nodes/<path:node_id>` | api_experimental.v2_skill_node_detail | none | default | no (grep) | app/routes/experimental.py:896 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 77 | GET | `/api/experimental/v2/stats` | api_experimental.v2_stats | none | default | no (grep) | app/routes/experimental.py:947 | NOT env-gated; parses bundle JSON from disk per request |
| 78 | GET | `/api/experimental/v2/stats/<path:stat_id>` | api_experimental.v2_stat_detail | none | default | no (grep) | app/routes/experimental.py:971 | NOT env-gated; parses bundle JSON from disk per request |
| 79 | GET | `/api/experimental/v2/uniques` | api_experimental.v2_uniques | none | default | yes | app/routes/experimental.py:445 | NOT env-gated; parses bundle JSON from disk per request |
| 80 | GET | `/api/experimental/v2/uniques/<path:unique_id>` | api_experimental.v2_unique_detail | none | default | no (grep) | app/routes/experimental.py:482 | NOT env-gated; parses bundle JSON from disk per request |
| 81 | GET | `/api/experimental/v2/uniques/debug` | api_experimental.v2_unique_debug | none | default | no (grep) | app/routes/experimental.py:585 | NOT env-gated; parses bundle JSON from disk per request |
| 82 | GET | `/api/health` | health.health | none | 60 per 1 minute | no (grep) | app/routes/health.py:49 | no DB/Redis check |
| 83 | POST | `/api/import/build` | import.import_build | optional JWT | 2 per 1 minute | no (grep) | app/routes/import_route.py:502 | external fetch (LET/Maxroll up to 8x15s); writes Build+ImportFailure; Discord webhook sync |
| 84 | POST | `/api/import/let/json` | import.import_let_from_json | optional JWT | 20 per 1 minute | no (grep) | app/routes/import_route.py:421 | anon can create ImportFailure rows + Discord alerts |
| 85 | POST | `/api/import/url` | import.import_from_url | optional JWT | 20 per 1 minute | no (grep) | app/routes/import_route.py:306 | external fetch LET (15s timeout) |
| 86 | GET | `/api/jobs/<job_id>` | jobs.get_job | none | default | no (grep) | app/routes/jobs.py:29 | 8-hex job id; any caller can read any job |
| 87 | POST | `/api/load/game-data` | load.load_game_data | none | 5 per 1 minute | yes | app/routes/load.py:21 | **NO AUTH; hot-reloads pipeline from disk; leaks exception text** |
| 88 | GET | `/api/meta/snapshot` | meta.snapshot | none | 30 per 1 minute | yes | app/routes/meta.py:17 |  |
| 89 | GET | `/api/meta/trending` | meta.trending | none | 30 per 1 minute | yes | app/routes/meta.py:24 |  |
| 90 | POST | `/api/optimize/build` | optimize.optimize_build | none | 5 per 1 minute | yes | app/routes/optimize.py:30 | max_variants<=1000; 8.3s measured |
| 91 | GET | `/api/passives` | passives.list_passives | none | default | yes | app/routes/passives.py:98 |  |
| 92 | GET | `/api/passives/<character_class>` | passives.get_class_tree | none | default | yes | app/routes/passives.py:132 |  |
| 93 | GET | `/api/passives/<character_class>/<mastery>` | passives.get_mastery_tree | none | default | yes | app/routes/passives.py:151 |  |
| 94 | GET | `/api/profile` | profile.get_profile | required | default | yes | app/routes/profile.py:25 |  |
| 95 | GET | `/api/profile/builds` | profile.profile_builds | required | default | yes | app/routes/profile.py:77 | per_page capped 100 in service |
| 96 | GET | `/api/profile/sessions` | profile.profile_sessions | required | default | yes | app/routes/profile.py:98 | per_page unbounded; N+1 on steps; int() ValueError->500 |
| 97 | GET | `/api/ref/affix-categories` | ref.get_affix_categories_endpoint | none | default | no (grep) | app/routes/ref.py:295 |  |
| 98 | GET | `/api/ref/affixes` | ref.get_affixes | none | default | yes | app/routes/ref.py:204 |  |
| 99 | GET | `/api/ref/base-items` | ref.get_base_items_endpoint | none | default | yes | app/routes/ref.py:389 |  |
| 100 | GET | `/api/ref/base-items/<base_type>` | ref.get_base_item_endpoint | none | default | no (grep) | app/routes/ref.py:420 |  |
| 101 | GET | `/api/ref/blessings` | ref.get_blessings_endpoint | none | default | yes | app/routes/ref.py:575 |  |
| 102 | GET | `/api/ref/classes` | ref.get_classes | none | default | yes | app/routes/ref.py:170 |  |
| 103 | GET | `/api/ref/crafting-rules` | ref.get_crafting_rules_endpoint | none | default | yes | app/routes/ref.py:382 |  |
| 104 | GET | `/api/ref/damage-types` | ref.get_damage_types_endpoint | none | default | yes | app/routes/ref.py:470 |  |
| 105 | GET | `/api/ref/enemy-profiles` | ref.get_enemy_profiles_endpoint | none | default | yes | app/routes/ref.py:452 |  |
| 106 | GET | `/api/ref/enemy-profiles/<enemy_id>` | ref.get_enemy_profile_endpoint | none | default | no (grep) | app/routes/ref.py:460 |  |
| 107 | GET | `/api/ref/fp-ranges` | ref.get_fp_ranges_endpoint | none | default | yes | app/routes/ref.py:430 |  |
| 108 | GET | `/api/ref/fp-ranges/<rarity>` | ref.get_fp_range_endpoint | none | default | no (grep) | app/routes/ref.py:437 |  |
| 109 | GET | `/api/ref/implicit-stats` | ref.get_implicit_stats_endpoint | none | default | yes | app/routes/ref.py:486 |  |
| 110 | GET | `/api/ref/implicit-stats/<item_type>` | ref.get_implicit_stat_endpoint | none | default | no (grep) | app/routes/ref.py:494 |  |
| 111 | GET | `/api/ref/item-types` | ref.get_item_types | none | default | yes | app/routes/ref.py:176 |  |
| 112 | GET | `/api/ref/passives` | ref.get_passives | none | default | no (grep) | app/routes/ref.py:301 |  |
| 113 | GET | `/api/ref/rarities` | ref.get_rarities_endpoint | none | default | yes | app/routes/ref.py:478 |  |
| 114 | GET | `/api/ref/skills` | ref.get_skills | none | default | yes | app/routes/ref.py:354 |  |
| 115 | GET | `/api/ref/uniques` | ref.get_uniques_endpoint | none | default | yes | app/routes/ref.py:525 |  |
| 116 | GET | `/api/ref/uniques/<slug>` | ref.get_unique_endpoint | none | default | yes | app/routes/ref.py:561 |  |
| 117 | POST | `/api/simulate/build` | simulate.simulate_build | none | 30 per 1 minute | yes | app/routes/simulate.py:281 | async mode -> job pool |
| 118 | POST | `/api/simulate/combat` | simulate.simulate_combat | none | 20 per 1 minute | no (grep) | app/routes/simulate.py:120 | n_simulations<=50k; async mode -> unbounded thread-pool queue |
| 119 | POST | `/api/simulate/conditional` | conditional.simulate_conditional | none | 30 per 1 minute | yes | app/routes/conditional.py:98 |  |
| 120 | POST | `/api/simulate/defense` | simulate.simulate_defense | none | 30 per 1 minute | no (grep) | app/routes/simulate.py:165 |  |
| 121 | POST | `/api/simulate/encounter` | simulate.simulate_encounter | none | 15 per 1 minute | yes | app/routes/simulate.py:244 | bounded; 11.7s worst case measured |
| 122 | POST | `/api/simulate/encounter-build` | simulate.simulate_encounter_from_build | none | 20 per 1 minute | yes | app/routes/simulate.py:261 |  |
| 123 | POST | `/api/simulate/multi-target` | multi_target.simulate_multi_target | none | 20 per 1 minute | yes | app/routes/multi_target.py:80 | **unbounded max_duration/tick/targets; 17s+1.6GB measured, larger inputs OOM-killed** |
| 124 | POST | `/api/simulate/optimize` | simulate.simulate_optimize | none | 10 per 1 minute | no (grep) | app/routes/simulate.py:186 |  |
| 125 | POST | `/api/simulate/rotation` | rotation.simulate_rotation | none | 10 per 1 minute | yes | app/routes/rotation.py:29 | 7.6s worst case measured |
| 126 | POST | `/api/simulate/sensitivity` | simulate.simulate_sensitivity | none | 10 per 1 minute | no (grep) | app/routes/simulate.py:217 |  |
| 127 | POST | `/api/simulate/stats` | simulate.simulate_stats | none | 60 per 1 minute | no (grep) | app/routes/simulate.py:86 |  |
| 128 | GET | `/api/skills/<skill_id>/tree` | skills.get_skill_tree | none | 30 per 1 minute | yes | app/routes/skills.py:180 |  |
| 129 | GET | `/api/version` | version.get_version | none | default | yes | app/routes/version.py:58 | spawns git subprocess per request |
| 130 | GET | `/debug/forge-safe-affixes` | debug.forge_safe_affixes | none | default | no (grep) | app/routes/debug.py:25 | env-gated (FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED); 404 by default |
| 131 | GET | `/experimental/forge-safe-affixes` | experimental.forge_safe_affix_catalog | none | default | no (dup mount) | app/routes/experimental.py:78 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 132 | GET | `/experimental/forge-safe-affixes/<affix_id>` | experimental.forge_safe_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:170 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 133 | GET | `/experimental/forge-safe-affixes/compare-legacy` | experimental.compare_forge_safe_affixes_to_legacy | none | default | no (dup mount) | app/routes/experimental.py:102 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 134 | GET | `/experimental/v2/affixes` | experimental.v2_affix_catalog | none | default | no (dup mount) | app/routes/experimental.py:197 | NOT env-gated; parses bundle JSON from disk per request |
| 135 | GET | `/experimental/v2/affixes/<path:affix_id>` | experimental.v2_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:241 | NOT env-gated; parses bundle JSON from disk per request |
| 136 | GET | `/experimental/v2/affixes/debug` | experimental.v2_affix_debug | none | default | no (dup mount) | app/routes/experimental.py:279 | NOT env-gated; parses bundle JSON from disk per request |
| 137 | GET | `/experimental/v2/classes` | experimental.v2_classes | none | default | no (dup mount) | app/routes/experimental.py:691 | NOT env-gated; parses bundle JSON from disk per request |
| 138 | GET | `/experimental/v2/classes/<path:class_id>` | experimental.v2_class_detail | none | default | no (dup mount) | app/routes/experimental.py:721 | NOT env-gated; parses bundle JSON from disk per request |
| 139 | GET | `/experimental/v2/classes/debug` | experimental.v2_class_mastery_debug | none | default | no (dup mount) | app/routes/experimental.py:708 | NOT env-gated; parses bundle JSON from disk per request |
| 140 | GET | `/experimental/v2/idols` | experimental.v2_idols | none | default | no (dup mount) | app/routes/experimental.py:599 | NOT env-gated; parses bundle JSON from disk per request |
| 141 | GET | `/experimental/v2/idols/<path:idol_id>` | experimental.v2_idol_detail | none | default | no (dup mount) | app/routes/experimental.py:623 | NOT env-gated; parses bundle JSON from disk per request |
| 142 | GET | `/experimental/v2/idols/affixes` | experimental.v2_idol_affixes | none | default | no (dup mount) | app/routes/experimental.py:639 | NOT env-gated; parses bundle JSON from disk per request |
| 143 | GET | `/experimental/v2/idols/affixes/<path:affix_id>` | experimental.v2_idol_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:662 | NOT env-gated; parses bundle JSON from disk per request |
| 144 | GET | `/experimental/v2/idols/debug` | experimental.v2_idol_debug | none | default | no (dup mount) | app/routes/experimental.py:678 | NOT env-gated; parses bundle JSON from disk per request |
| 145 | GET | `/experimental/v2/items/bases` | experimental.v2_item_bases | none | default | no (dup mount) | app/routes/experimental.py:308 | NOT env-gated; parses bundle JSON from disk per request |
| 146 | GET | `/experimental/v2/items/bases/<path:item_base_id>` | experimental.v2_item_base_detail | none | default | no (dup mount) | app/routes/experimental.py:345 | NOT env-gated; parses bundle JSON from disk per request |
| 147 | GET | `/experimental/v2/items/debug` | experimental.v2_item_debug | none | default | no (dup mount) | app/routes/experimental.py:416 | NOT env-gated; parses bundle JSON from disk per request |
| 148 | GET | `/experimental/v2/items/implicits` | experimental.v2_item_implicits | none | default | no (dup mount) | app/routes/experimental.py:383 | NOT env-gated; parses bundle JSON from disk per request |
| 149 | GET | `/experimental/v2/masteries` | experimental.v2_masteries | none | default | no (dup mount) | app/routes/experimental.py:737 | NOT env-gated; parses bundle JSON from disk per request |
| 150 | GET | `/experimental/v2/masteries/<path:mastery_id>` | experimental.v2_mastery_detail | none | default | no (dup mount) | app/routes/experimental.py:754 | NOT env-gated; parses bundle JSON from disk per request |
| 151 | GET | `/experimental/v2/modifiers` | experimental.v2_modifiers | none | default | no (dup mount) | app/routes/experimental.py:987 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 152 | GET | `/experimental/v2/modifiers/<path:modifier_id>` | experimental.v2_modifier_detail | none | default | no (dup mount) | app/routes/experimental.py:1035 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 153 | GET | `/experimental/v2/modifiers/debug` | experimental.v2_modifier_debug | none | default | no (dup mount) | app/routes/experimental.py:1021 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 154 | GET | `/experimental/v2/passives` | experimental.v2_passives | none | default | no (dup mount) | app/routes/experimental.py:770 | NOT env-gated; parses bundle JSON from disk per request |
| 155 | GET | `/experimental/v2/passives/<path:tree_id>` | experimental.v2_passive_detail | none | default | no (dup mount) | app/routes/experimental.py:806 | NOT env-gated; parses bundle JSON from disk per request |
| 156 | GET | `/experimental/v2/passives/<path:tree_id>/nodes/<path:node_id>` | experimental.v2_passive_node_detail | none | default | no (dup mount) | app/routes/experimental.py:825 | NOT env-gated; parses bundle JSON from disk per request |
| 157 | GET | `/experimental/v2/passives/debug` | experimental.v2_passive_debug | none | default | no (dup mount) | app/routes/experimental.py:793 | NOT env-gated; parses bundle JSON from disk per request |
| 158 | GET | `/experimental/v2/sets` | experimental.v2_sets | none | default | no (dup mount) | app/routes/experimental.py:518 | NOT env-gated; parses bundle JSON from disk per request |
| 159 | GET | `/experimental/v2/sets/<path:set_id>` | experimental.v2_set_detail | none | default | no (dup mount) | app/routes/experimental.py:547 | NOT env-gated; parses bundle JSON from disk per request |
| 160 | GET | `/experimental/v2/sets/debug` | experimental.v2_set_debug | none | default | no (dup mount) | app/routes/experimental.py:592 | NOT env-gated; parses bundle JSON from disk per request |
| 161 | GET | `/experimental/v2/skills` | experimental.v2_skills | none | default | no (dup mount) | app/routes/experimental.py:841 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 162 | GET | `/experimental/v2/skills/<path:skill_id>` | experimental.v2_skill_detail | none | default | no (dup mount) | app/routes/experimental.py:931 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 163 | GET | `/experimental/v2/skills/<path:skill_id>/tree` | experimental.v2_skill_tree_by_skill | none | default | no (dup mount) | app/routes/experimental.py:912 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 164 | GET | `/experimental/v2/skills/debug` | experimental.v2_skill_debug | none | default | no (dup mount) | app/routes/experimental.py:864 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 165 | GET | `/experimental/v2/skills/trees/<path:tree_id>` | experimental.v2_skill_tree_detail | none | default | no (dup mount) | app/routes/experimental.py:877 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 166 | GET | `/experimental/v2/skills/trees/<path:tree_id>/nodes/<path:node_id>` | experimental.v2_skill_node_detail | none | default | no (dup mount) | app/routes/experimental.py:896 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 167 | GET | `/experimental/v2/stats` | experimental.v2_stats | none | default | no (dup mount) | app/routes/experimental.py:947 | NOT env-gated; parses bundle JSON from disk per request |
| 168 | GET | `/experimental/v2/stats/<path:stat_id>` | experimental.v2_stat_detail | none | default | no (dup mount) | app/routes/experimental.py:971 | NOT env-gated; parses bundle JSON from disk per request |
| 169 | GET | `/experimental/v2/uniques` | experimental.v2_uniques | none | default | no (dup mount) | app/routes/experimental.py:445 | NOT env-gated; parses bundle JSON from disk per request |
| 170 | GET | `/experimental/v2/uniques/<path:unique_id>` | experimental.v2_unique_detail | none | default | no (dup mount) | app/routes/experimental.py:482 | NOT env-gated; parses bundle JSON from disk per request |
| 171 | GET | `/experimental/v2/uniques/debug` | experimental.v2_unique_debug | none | default | no (dup mount) | app/routes/experimental.py:585 | NOT env-gated; parses bundle JSON from disk per request |

## 6. UNKNOWNs

* Whether Render passes the real client IP as the TCP peer (decides API-7 severity). Check production logs for the `ip=` field in `rate_limit_exceeded` lines.
* Whether `REDIS_URL` was reachable at boot in production (otherwise the limiter is in-memory per worker).
* Render instance memory (starter is commonly 512 MB) and whether OOM restarts have occurred.
* Whether `docs/generated/*.json` bundles are present in the production checkout (`rootDir: backend`; the bundles live at the repo root `docs/generated/`). If they are absent, the v2 endpoints return 404 and API-3 does not apply.
* Whether production `data/items/affixes.json` has been modified through API-1. The filesystem is ephemeral per deploy, so tampering would not survive a redeploy, and there is no audit trail.
* Actual traffic and abuse volume. No production logs were read.

## 7. What this does NOT prove

* All probes ran against the `testing` config (rate limiting disabled, in-memory SQLite, no Redis) in a single process. They prove the code paths, not production behaviour under gunicorn/Render.
* Timing and RSS numbers come from this machine, not Render hardware.
* Frontend usage is grep-based. A route not found by grep may still be called through a dynamically assembled path.
* No production endpoint was called. The live presence of each route, the env flags, and the deployed commit were not verified (`/api/version` would report the commit but was not queried).
* This audit did not review the correctness of simulation math (covered elsewhere), dependency CVEs, or the frontend's own XSS surface.


---

<!-- FILE: 12_FRONTEND_PRODUCT_AUDIT.md -->

# 12 — Frontend / Product Reality Audit (Phase 10)

- Repo HEAD: `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` (2026-05-14)
- Audit date: 2026-10-06
- Scope: `frontend/` (Vite + React + TS), router, API client, importer UX, trust labeling, frontend game-data copies, vitest coverage. Electron shell checked only briefly.
- Mode: audit only. No repo files were changed except this report. All scratch output is in the session scratchpad (`.../scratchpad/fe/`).

---

## 0. Headline facts

1. **Production API base URL is missing `/api` (P0, static + simulated proof).** `render.yaml:95-96` sets `VITE_API_BASE_URL=https://api.epochforge.gg`. `frontend/src/lib/api.ts:51-54` uses that value as the base, and every client path is written relative to `/api` (`/builds`, `/auth/me`, `/import/build`, ...). Every Flask blueprint is mounted under `/api/...` (`backend/app/__init__.py:222-250`). A production-mode build made with the render.yaml value contains the literal `https://api.epochforge.gg/auth/discord`. Driving that build with Playwright showed **100% of API requests going to un-prefixed paths** (`GET /builds`, `POST /import/build`, `POST /builds`, ...). The backend answers these with its JSON 404 handler (`backend/app/__init__.py:266-269`). The repo's own docs expect `https://api.epochforge.gg/api/...` (`docs/production_setup.md:94`). `docker-compose.yml:66` includes `/api`, which is correct. Whether the live Render dashboard overrides this value is **UNKNOWN**: production could not be reached (the egress proxy refused CONNECT with 403, which is the proxy's response, not the site's).
2. **Sign-in is affected too.** The "Sign In" links (`TopBar.tsx:69-71`, `BuildPlannerPage.tsx:1187`) render as `https://api.epochforge.gg/auth/discord`. That path has no route; the only route is `/api/auth/discord`.
3. **The v2.5 "trust" debug pages cannot work on the static site.** Eight public routes (`App.tsx:267-276`) call `fetch()` with root-relative `/experimental/v2/...` or `/api/experimental/...` and never use the API base. On Render, the `/* → /index.html` rewrite (`render.yaml:101-102`) returns HTML with status 200. This was observed: "Debug endpoint unavailable — Backend returned an unreadable response (200)." These paths only work through the Vite dev proxy (`vite.config.ts` proxies `/api` and `/experimental`).
4. **Importer UX:** a Maxroll 403 is shown as red text saying the build "may be expired, or Maxroll may have changed their format (attempts: HTTP 403; ...)". There is no fallback for Maxroll: the JSON tab accepts only Last Epoch Tools `window.buildInfo` or Forge JSON. The Last Epoch Tools (LET) bookmarklet and paste path exists and is well explained. However, the "Import URL" tab still accepts and submits LET URLs, and the "Quick Fetch" tab is permanently disabled.
5. **Anonymous user dead ends:** anonymous saving is allowed. But anonymous or imported builds have no Edit button (`isOwner` requires an author), there is no share or copy-link control, and no UI can change `is_public`. Imported builds are forced private (`import_route.py:592`), so they can never be published from the UI. The `/workspace/*` editor has no save path at all.
6. **Trust labeling stops at the trust pages.** The trust components (`components/v2/*`) are imported only by the `/trusted-data/*` and `/debug/v2*` pages. The production DPS, EHP and letter-grade surfaces (planner "Analyze Build", `/encounter`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target`, `/monte-carlo`, `/crafting`) show numbers without trust or experimental badges. The only caveats are a benchmark disclaimer and a footer "known limitations" link.
7. **Tests:** 49 vitest files and 916 tests; 17 failed and 899 passed (a concurrent run on the same HEAD). Failures are stale navigation and GlobalSearch expectations. **There are zero tests** for `BuildImportModal`, planner save/edit, `lib/api.ts` base-URL composition, or the v2 debug pages' fetch base.

---

## 1. Method and commands

| Step | Command / action |
|---|---|
| Router | `sed -n 1,300p frontend/src/App.tsx` |
| Frontend API paths | `grep -rnoE "(get|post|patch|del|apiGet|apiPost)...\(['\"\`]/..."` over `frontend/src` (excluding `__tests__`); manual read of `lib/api.ts:140-677` and `services/*.ts` |
| Backend routes (static) | AST script `scratchpad/fe/routes.py` over `backend/app/routes/*.py` and `register_blueprint(..., url_prefix=)` → `scratchpad/fe/backend_routes.tsv` (171 rules) |
| Backend routes (live URL map) | Reused another investigator's `scratchpad/urlmap.json` (`create_app("testing").url_map`, 172 rules). Static and live differ only by `/static/<path>`, so the static extraction is exact. |
| Prod-config build | `VITE_API_BASE_URL=https://api.epochforge.gg npx vite build --outDir scratchpad/fe/dist` (exit 0). `grep -o "https://api.epochforge.gg..." dist/assets/*.js` |
| Behavior simulation | `scratchpad/fe/pw.cjs` and `pw2.cjs` (Playwright 1.56.1, Chromium from `/opt/pw-browsers`). A Node static server mimics the Render rewrite. Requests to `api.epochforge.gg` are intercepted (never sent): un-prefixed paths get the backend's 404 JSON body, and `/api/*` gets 503 "unmodeled". 20 routes were visited, plus the importer flow. Outputs: `scratchpad/fe/pw-out/pw-results.json`, `pw2-prodcfg.json`, `pw2-hypo403.json`, and screenshots. |
| Production reachability | `curl https://epochforge.gg/` and `curl https://api.epochforge.gg/api/health` both returned `CONNECT tunnel failed, response 403` (proxy policy; see `$HTTPS_PROXY/__agentproxy/status` recentRelayFailures). **UNKNOWN** live state. |
| Data comparison | Python regex over `frontend/src/data/{passiveTrees,skillTrees}/index.ts` vs `data/classes/{passives,skills_with_trees}.json` |
| Bookmarklet parity | Node: parse the inline `LET_BOOKMARKLET` literal and compare it with `public/bookmarklets/let-import.bookmarklet.txt`: **identical (781 chars)** |
| Orphans | grep of `import ... '/<Basename>'` across `src` (excluding tests) |
| Tests | Read `scratchpad/vitest.log` (concurrent `npx vitest run`, same HEAD; this investigator did not rerun, to avoid racing). `frontend/node_modules` already existed; no `npm ci` was run by this investigator. |

---

## 2. Route table

Legend:
- **Code status** assumes the API base is correct (`.../api`): **works**, **partial**, **stale** (unlinked or superseded), or **dead** (cannot function).
- **Prod-config sim** is the behavior observed under the render.yaml value.
- **Nav** means the route is linked from the Sidebar (`Sidebar.tsx:165-174`).
- All listed frontend API paths exist in the backend URL map once `/api` is prepended. No frontend-called path is missing from the backend.

| Route | Component | Nav | Frontend API calls (→ backend `/api` + path) | Code status | Prod-config sim | Notes |
|---|---|---|---|---|---|---|
| `/` | DashboardPage | Y | GET /builds, /meta/snapshot, /ref/affixes, /ref/skills, /version | works | **misleading**: "0 COMMUNITY BUILDS · 0 SKILLS · 0 AFFIXES", "No builds yet", "Season 4 · Patch 1.4.3" | Hardcoded fallbacks at `DashboardPage.tsx:159,192-193` |
| `/home` | HomePage | N | none | stale | static | Unlinked marketing page; features hardcoded as `status: "Live"` (`HomePage.tsx:11,21,31`) |
| `/builds` | BuildsPage | Y | GET /builds | works | "No builds found — Be the first to share a build" | API failure looks the same as an empty catalog |
| `/build` | BuildPlannerPage (create) | Y | GET /passives/:class, /ref/blessings, /version; POST /builds; POST /import/build, /import/let/json, /import/url | works | Save → toast "Not found"; Import → "Not found" | See §3 |
| `/build/:slug` | BuildPlannerPage (BuildSummary) | via links | GET /builds/:slug, POST /builds/:slug/view, POST /builds/:slug/simulate, GET /builds/:slug/optimize, /analysis/*, /entities/bosses, /skills/:id/tree, /builds/:slug/skills, PATCH node, POST vote | partial | "Build not found" | No Edit for anonymous or imported builds (§3); untrusted DPS grade (§4) |
| `/workspace/new`, `/workspace/:slug` | UnifiedBuildPage | N | GET /builds/:slug, POST /simulate/build (debounced) | partial (no save) | renders; analysis would fail | Store `store/buildWorkspace.ts` has no persist; no create/update call anywhere in workspace |
| `/craft`, `/craft/:slug` | CraftSimulatorPage | Y | GET /ref/affixes, /ref/base-items, /ref/fp-ranges; craft session CRUD | works (local sim + server sessions) | renders local sim | Labeled "LOCAL / Simulating locally". FP mirror matches `data/items/crafting_rules.json` |
| `/affixes` | AffixEditorPage | N | GET /admin/affixes, PATCH /admin/affixes/:id | works | "Not found" | **Unauthenticated admin write** (`admin.py:66-69` has no auth decorator; writes `affixes.json`). No frontend gate either. |
| `/affix-catalog` | AffixCatalogPage | N | GET /affixes/catalog, /affixes/catalog/summary | works | error | Unlinked |
| `/passives` | PassiveTreePage | Y | GET /passives/:class (+ bundled tree data) | works | "Error loading passive tree — Not found" | |
| `/compare` | BuildComparisonPage | via links | GET /builds/:a, /builds/:b | works | n/a | `compareApi` (`/compare/:a/:b`) is defined but unused |
| `/report/:slug` | ReportPage | N | GET /builds/:slug/report | works | n/a | 0 in-app links found |
| `/meta` | MetaSnapshotPage | Y | GET /meta/snapshot, /meta/trending | works | header only, no data, no error | Silent empty state |
| `/encounter` (`/simulation` alias) | SimulationPage → BuildEditorPage / EncounterSimulatorPage | Y | POST /simulate/encounter-build, /simulate/encounter | works | renders form | DPS shown with no trust label |
| `/build-editor` | BuildEditorPage | N | POST /simulate/encounter-build | stale (duplicate of `/encounter` Build mode) | | |
| `/optimizer` | OptimizerPage | N | POST /optimize/build | works | | Unlinked; no trust label |
| `/rotation` | RotationBuilderPage | N | POST /simulate/rotation | works | | Unlinked; no trust label |
| `/conditional` | ConditionalBuilderPage | N | POST /simulate/conditional | works | | Unlinked; no trust label |
| `/multi-target` | MultiTargetSimulatorPage | N | POST /simulate/multi-target | works | | Unlinked; no trust label |
| `/data-manager` | DataManagerPage | N | POST /load/game-data | works | | Unlinked; `load.py` route has only a rate limit and no auth |
| `/monte-carlo` | MonteCarloPage | N | none (client-side Box-Muller on toy inputs) | stale or misleading | renders | Claims to "characterise build consistency"; inputs are not a build; comparison panel is a placeholder |
| `/crafting` | CraftingPage | N | POST /craft/predict | partial or misleading | | Fabricated ±5% "confidence interval" and `fracture_rate = 1 - completion` (`CraftingPage.tsx:100-105`) |
| `/classes` | ClassesPage | Y | GET /ref/classes | works | "Error loading classes — Not found" | |
| `/bis-search` | BisSearchPage | Y | POST /bis/search, GET /ref/affixes | works | renders form | |
| `/crafting-workspace` | CraftingWorkspace | N | POST /craft/predict | stale | | Unlinked |
| `/profile` | UserProfilePage | Y | GET /profile, /profile/builds, /profile/sessions | works (auth) | redirects to `/` | Anonymous users are silently redirected (`UserProfilePage.tsx:311`), with no explanation |
| `/trusted-data` | TrustedDataExplanationPage | footer/debug | none (static copy) | works | works | |
| `/trusted-data/support` | TrustedDataSupportMatrixPage | — | none | works | works | Says "Production planner consumption is false" |
| `/trusted-data/pre-v3-readiness` | PreV3MechanicalReadinessPage | — | none | works | works | |
| `/debug/v2` | V2DebugNavigationPage | — | none | works | works | Links to the 8 pages below |
| `/debug/forge-safe-affixes` (`/debug/v2-affixes` alias) | ForgeSafeAffixesDebugPage | — | fetch `/experimental/v2/affixes` (root-relative) | **dead in prod** | (not visited; same pattern) | `ForgeSafeAffixesDebugPage.tsx:48,56` |
| `/debug/v2-items` | V2ItemsDebugPage | — | fetch `/experimental/v2/items/*` | **dead in prod** | | `:37,41` |
| `/debug/v2-unique-sets` | V2UniqueSetDebugPage | — | fetch `/experimental/v2/{uniques,sets}` | **dead in prod** | | `:38,42` |
| `/debug/v2-idols` | V2IdolsDebugPage | — | fetch `/experimental/v2/idols*` | **dead in prod** | | `:35,39` |
| `/debug/v2-classes` | V2ClassMasteryDebugPage | — | fetch `/experimental/v2/{classes,masteries}` | **dead in prod** | | `:35,39` |
| `/debug/v2-passives` | V2PassivesDebugPage | — | fetch `/experimental/v2/passives` | **dead in prod** | | `:36,40` |
| `/debug/v2-skills` | V2SkillsDebugPage | — | fetch `/experimental/v2/skills` | **dead in prod** | **observed**: "Backend returned an unreadable response (200)" | `:36,40` |
| `/debug/v2-stats-modifiers` | V2StatsModifiersDebugPage | — | fetch `/api/experimental/v2/modifiers/debug` | **dead in prod** | **observed**: same message | `:33` |
| `/movement-debug`, `/viz-debug`, `/craft-debug`, `/debug`, `/data-flow` | dev-only (`IS_DEV`) | — | various | dev only | 404 in prod build | `App.tsx:278-287` |
| `/passive-tree`, `/planner` | aliases | — | — | works | | |
| `/auth/callback` | AuthCallbackPage | — | GET /auth/me | works | | |
| `*` | NotFoundPage | — | — | works | | `/builds/:slug` (GlobalSearch result link) lands here (observed) |

Counts: 52 `<Route>` elements in `App.tsx` (`grep -c "<Route "`): 1 layout route, 1 index route and 50 path routes. The path routes include 3 legacy aliases, 1 debug alias, 5 dev-only routes, `/auth/callback` and the catch-all. 10 routes are in the Sidebar. 17 non-debug routes have no in-app link (grep count 0, or only self/test references): `/home`, `/affix-catalog`, `/report/:slug`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target`, `/data-manager`, `/monte-carlo`, `/crafting`, `/crafting-workspace`, `/build-editor`, `/workspace/*`, `/affixes` (linked only from 5 internal refs to `?q=` search), and others. The list is approximate; see the command in §1.

**Orphan source (not imported anywhere outside tests):** `pages/shared/SharedBuildPage.tsx` (126 lines), `pages/library/BuildLibraryPage.tsx` (142), `pages/user/UserBuildDashboard.tsx` (132), `pages/debug/IntegrationDebugPage.tsx` (252), `pages/bis/BisWorkspace.tsx` (267, uses `Math.random` scores), `pages/build/BuildWorkspace.tsx` (219), `components/features/build/SimulationDashboard.tsx` (739), `UniqueItemPicker.tsx` (247), `PassiveTreeGraph.tsx` (752), `SkillTreeGraph.tsx` (471), `lib/simulation.ts` (client-side DPS/EHP formulas, e.g. `Armor/(Armor+1000)`; unreferenced). `App.tsx:38-40` comments say several of these were "Removed", but the files remain. Test-only modules (`services/sharing/build_import_service.ts`, `services/build/build_manager.ts`, `services/presets/preset_manager.ts`, `components/comparison/*`, `components/history/*`, `components/diagnostics/PerformancePanel`) have 0 production importers. 8 of the 49 test files (`phase-ui-plus/*`) mostly exercise this unused code.

---

## 3. User journey (anonymous user), with dead ends

| # | Step | What happens (code) | Under render.yaml config (simulated) | Dead end? |
|---|---|---|---|---|
| 1 | Land on `/` | Dashboard: stats, top classes, CTA "Start planning" → `/build` | Shows **0 / 0 / 0** and "No builds yet" with no error. Season and patch fall back to hardcoded "4 / 1.4.3". | Misleading (looks like an empty, healthy site) |
| 2 | Click Sign In (TopBar or planner banner) | `href = ${VITE_API_BASE_URL}/auth/discord` | `https://api.epochforge.gg/auth/discord` → backend JSON 404 | **DE-1** (prod config) |
| 3 | `/build` → "Import Build" → **Import URL** tab, paste Maxroll URL | `POST /import/build`; anonymous allowed, rate limit **2/min** (`import_route.py:496-503`) | Red text: "Not found" | **DE-2** (prod config) |
| 3a | Same, routing fixed, Maxroll returns 403 (hypothetical, message copied verbatim from `maxroll_importer.py:716-719`) | Red text: "Could not fetch build data from Maxroll. The build may be expired, or Maxroll may have changed their format. (attempts: HTTP 403; HTTP 403; HTTP 403)" | observed in `pw2-hypo403.json` | **DE-3**: the cause is shown as expiry or format change, and nothing points to an alternative. The JSON tab does not accept Maxroll data. The "This issue has been reported" footer (`BuildImportModal.tsx:560`) checks `importError.includes("422")`, but backend messages never contain "422", so it never renders (even though the backend does record and alert). |
| 3b | Paste a LET URL in the Import URL tab | Accepted (`detectSource` returns `lastepochtools`; button stays enabled, verified) and POSTed. The inline hint says "Use JSON tab for LET". The validation message (`:93`) still lists LET as supported. | "Not found" | Contradictory copy. With correct routing, the backend fetches LET server-side, which the modal itself says cannot work. |
| 3c | **Quick Fetch** tab | Input and button are hard-disabled (`:419,432`) with the label "Temporarily Unavailable" | — | **DE-4**: permanent dead tab |
| 3d | **JSON** tab + bookmarklet | Bookmarklet link (draggable; copy is identical to `public/bookmarklets/let-import.bookmarklet.txt`); `copy(window.buildInfo)` fallback; auto-detect; `POST /import/let/json` | "Not found" | Workable path once routing is correct; best-explained path in the modal |
| 4 | Import success (URL) | Backend creates the build immediately (anonymous, `is_public=False`), modal offers "Open Build" → `/build/:slug` | — | — |
| 4b | Import success (JSON) | Applies the build to the create form; user must Save | — | — |
| 5 | Save (create) | `POST /builds`; anonymous allowed ("will be saved anonymously", `BuildPlannerPage.tsx:1431-1435`). Schema default `is_public=True` (`schemas/__init__.py:92`), so an anonymous save is public immediately. | toast "Not found" | DE-5 (prod config) |
| 6 | Edit saved or imported build | `BuildSummary` shows **Edit** only if `user && build.author?.id === user.id` (`:257,495-497`). Anonymous builds have no author, so there is no Edit button for anyone, even though the backend lets *anyone* PATCH an authorless build (`builds.py:206-213`). | — | **DE-6**: the user cannot edit their own anonymous or imported build in the UI |
| 7 | Make public / share | No `is_public` control anywhere in the frontend (grep: only type definitions). No share or copy-link button in BuildSummary; only "Export JSON" to the clipboard. Imported builds are forced private (`import_route.py:592`) but readable by anyone with the slug (`builds.py:178-196` has no `is_public` check). | — | **DE-7**: imported builds can never be published; sharing means copying the address bar by hand |
| 8 | Alternative editor `/workspace/:slug` | Loads the build into a Zustand store and runs a debounced `/simulate/build` | — | **DE-8**: no save; store not persisted; not linked from nav |
| 9 | Search a build (Ctrl+K) → click result | GlobalSearch links to `/builds/${slug}` (`GlobalSearch.tsx:155`); no such route | NotFound page (observed) | **DE-9** |
| 10 | `/profile` while anonymous | `<Navigate to="/" replace />` (`UserProfilePage.tsx:311`) | Silent bounce to the dashboard | Minor dead end |

---

## 4. Fallback and misleading-display inventory

Counts are over `frontend/src`, excluding tests.

| Pattern | Count | Notes |
|---|---|---|
| `?? 0` | 179 | 37 of these are on DPS, EHP, armor, crit or resistance values (see the list below) |
| `\|\| 0` | 5 | |
| `?? / \|\| "Unknown"` | 6 | `ImportPanel.tsx:33` (`character_class ?? "Unknown"`); `BaseItemSelector.tsx:36,47`; error strings |
| `?? / \|\| "—"/"-"/"N/A"` | 53 | mostly display placeholders (acceptable) |
| `Math.random` | 29 | CraftSimulator local sim (labeled LOCAL); MonteCarlo (unlabeled); BisWorkspace (orphan) |
| `mock` word | 14 | `CraftOutcomeChart.tsx:4` "mock normal-distribution outcome spread"; `CraftingPage.tsx:7` "client-side mock simulation" (comment, while the code now calls `/craft/predict`) |

High-impact fallbacks and misleading displays:

| ID | Location | Behavior | Trust label? |
|---|---|---|---|
| M1 | `BuildPlannerPage.tsx:634` → `simulation/BuildScoreCard.tsx:43-63` | Letter grade S–D from hardcoded caps (20,000 DPS, 8,000 EHP, survivability /100; weights 40/30/30). DPS `?? 0` means missing DPS produces a "D" grade. | **No** |
| M2 | `simulation/OffenseDefenseSplit.tsx:98-100,211-213` | DPS, crit and multiplier `?? 0`; benchmark bars | Only "Benchmarks are approximate…" plus a known-limitations link |
| M3 | `build-workspace/analysis/{OffenseCard:82-98, DefenseCard:100-103, BuildScoreCard:384-386, PrimarySkillBreakdown:53-54,148, SkillsSummaryTable:322}` | Missing fields render as 0 (for example "0 EHP", "0% armor") rather than "unavailable" | No |
| M4 | `DashboardPage.tsx:159,192-193` | `buildsTotal ?? 0`; patch `?? "1.4.3"`, season `?? 4` | No; shown even when `/version` fails (observed) |
| M5 | `MonteCarloPage.tsx` | Toy stochastic model presented as build consistency analysis | No |
| M6 | `CraftingPage.tsx:100-105` | `confidence_interval = completion ± 0.05` (made up); `fracture_rate = 1 - completion` (inferred) | No |
| M7 | `/encounter`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target` results panels | DPS and damage numbers | No |
| M8 | `HomePage.tsx:11,21,31` | Every feature hardcoded as "Live" | n/a |
| M9 | `/builds`, `/meta`, `/` empty states | API failure shown as "No builds yet / be the first" | No error surfaced |

Where trust labeling **does** exist: `components/v2/{V2TrustBadge, V2StatusBadgeGroup, V2LimitationNotice, V2TrustSummaryPanels, V2PlannerAdapterStatusPanel, V2EnvelopePanels}`. These are used only by `pages/Trusted*`, `PreV3MechanicalReadinessPage` and `pages/debug/V2*`. `V2PlannerAdapterStatusPanel` is rendered only on `/debug/v2-stats-modifiers` (`V2StatsModifiersDebugPage.tsx:114`), which is itself dead in prod (§0.3). Elsewhere: the sidebar "BETA" pill (`Sidebar.tsx:237-239`) and the footer "known limitations" link (`AppLayout.tsx:103-111`) to GitHub. The trust pages state that no v2 data drives production planner output. Production planner numbers do not link back to those pages.

---

## 5. Frontend game data vs backend `data/`

| Asset | Frontend | Backend | Delta |
|---|---|---|---|
| Passive nodes | `src/data/passiveTrees/index.ts` (137 KB): 541 nodes, 535 distinct names | `data/classes/passives.json`: 541 entries, 537 names | Same count; **55 FE-only and 57 BE-only names** (for example FE "Blood Armour" vs BE "Blood Armor", "Argent Veil", "Berserker"). Spelling and patch drift. |
| Skill trees | `src/data/skillTrees/index.ts` (1.06 MB): 133 trees, 3,863 nodes | `data/classes/skills_with_trees.json`: 184 skills, 137 with `skillTree`, 3,875 nodes | **4 trees and 12 nodes missing in FE** |
| Raw tree metadata | `src/data/raw/{skill,char}-tree-{metadata,layout}.json` (3.85 MB) | No same-named file outside `frontend/` | Frontend-only source; provenance header only says "Auto-generated by merge script" (no version or patch stamp) |
| Skill damage table | `lib/gameData.ts:405+` `SKILL_STATS` (108 entries with `baseDamage`, `levelScaling`) | backend skill registry | Used only by orphan `lib/simulation.ts` (dead) |
| Class and mastery constants | `@constants` alias → `backend/src/constants` (`vite.config.ts`) | same files | Shared, no drift (by construction) |
| Crafting FP costs | `CraftSimulatorPage.tsx:49-55` | `data/items/crafting_rules.json` | Identical values |
| `frontend/public` | 460 files: 400 passive icons, 54 skill icons, 1 sprite webp, 2 bookmarklet files, `_redirects`, favicon, manifest. **No JSON game data.** | — | — |
| `data/version.json` | — | `patch_version: "unknown"`, synced 2026-04-26 | The frontend has no data-version marker at all |

---

## 6. Frontend tests (vitest)

- 49 test files and 916 tests (from `scratchpad/vitest.log`): **17 failed, 899 passed**. Two files fail:
  - `components/navigation.test.tsx`: 11 failures. The test expects "Data Manager" in the sidebar (removed) and an old GlobalSearch placeholder.
  - `integration/layout.test.tsx`: 6 failures (GlobalSearch open/close).
  - These failures are stale tests, not detected regressions.
- Coverage by area:
  - v2 debug and trust pages: 14 page tests plus 4 component tests. All of them mock `fetch` with relative URLs, so none would catch the production base-URL problem.
  - Workspace store and pages: 3 files.
  - Analysis cards: 6 files.
  - Hooks: 3 files.
  - `config/vite-proxy-routing.test.ts` asserts only that `vite.config.ts` contains `"/api"` and not `"/debug"`.
- **Not covered:**
  - `BuildImportModal` (0 references in tests)
  - `BuildPlannerPage` save, edit and ownership logic
  - `lib/api.ts` URL composition and the render.yaml env combination
  - GlobalSearch link targets vs routes
  - `AffixEditorPage` and its admin auth
  - Craft, BIS and simulation pages
- `tsc --noEmit` (another investigator's `scratchpad/tsc.log`) printed no diagnostics. The exit code was not captured: **UNKNOWN**.

---

## 7. Electron (brief)

`electron/main.js:20-22,113,154-157`: loads `http://localhost:5173` in dev and health-checks `http://localhost:5050/api/health`. This was not exercised. Whether a packaged Electron build points at the correct API base is **UNKNOWN**.

---

## 8. UNKNOWNs

- U1. The live production frontend bundle and the actual Render dashboard value of `VITE_API_BASE_URL`. Could differ from `render.yaml`; production was unreachable from this container (proxy 403).
- U2. Whether `api.epochforge.gg` sits behind a proxy or rewrite that adds `/api`. Nothing in the repo indicates one.
- U3. Whether Maxroll currently returns 403 to the backend. The UX for that case was simulated with the backend's own message string.
- U4. Real end-to-end import, save and simulation with a running backend. Not executed: a local backend was not started for this phase, and requests were intercepted.
- U5. `tsc` exit status (log has timing only).

## 9. What this does NOT prove

- It does not prove production is broken today. It proves that the committed deploy config plus the committed client code produce un-prefixed API URLs, and that a build made with that config fails exactly as described. A dashboard override would invalidate FE-1 and FE-2 in production (but not the repo defect).
- It does not validate any DPS, EHP or crafting number. It only shows where numbers are displayed without trust context. Calculation correctness is covered in `13_CALCULATION_TRUST_MATRIX.md`.
- The Playwright runs used a stubbed API, so page behavior *with real data* (rendering bugs, data-shape mismatches) is not covered.
- Route reachability counts come from grep and may miss dynamically built links.
- The vitest results come from a concurrent run on the same HEAD, not rerun by this investigator.

---

## Reconciliation note (cross-report review)

The FE-1/FE-2 analysis above is correct **for the committed configuration**: `frontend/src/lib/api.ts:51-54,88` builds `${VITE_API_BASE_URL}${path}`, the paths are `/api`-relative, and `render.yaml:95-96` sets `https://api.epochforge.gg` without `/api`.

Production evidence contradicts this as a *live* outage. The 2026-10 Discord import alert can only come from the backend handler behind `POST /api/import/build` (see 08_LAST_EPOCH_TOOLS_IMPORT_FORENSICS.md). So at least one production request reached the correctly prefixed route. The likely explanation is a Render-dashboard value that differs from the blueprint, but that is UNKNOWN until the dashboard is checked.

Final classification used in AUDIT_EVIDENCE.json:
- **FE-1:** P1, "committed blueprint drifts from production; re-applying it would break all API calls and Discord login".
- **FE-2:** merged into FE-1.

This note is not a confirmed live P0 outage.


---

<!-- FILE: 13_CALCULATION_TRUST_MATRIX.md -->

# 13 — Calculation / Simulation Trust Matrix (Phase 11)

- Audit date: 2026-10-06
- Code under audit: `le-the-forge` HEAD `1efcef7` (2026-05-14)
- Reference data: `/home/user/last-epoch-data/exports_json/*` (extracted from game build `1.4.6_22986002`, generated 2026-05-06)
- Mode: read-only. No code was changed. Scratch scripts lived outside the repo.

## 0. Headline

| Classification | Count (of 38 rows in §3) |
|---|---|
| TRUSTED | 0 |
| PARTIALLY TRUSTED | 12 |
| UNVERIFIED | 9 |
| KNOWN INCORRECT | 13 |
| NOT IMPLEMENTED (in user-facing paths) | 4 |

Nothing reaches TRUSTED. No calculation has a test that checks it against an independent source such as an in-game measurement, extracted game data or official documentation. Every DPS and EHP number on the main build page comes from the hand-entered skill table in `backend/app/game_data/skills.json`. Compared with the 1.4.6 game extract, that table's base damage is off by more than 25% for 53 of the 54 skills that can be compared. The median gap is 24.6×.

The API responses that the main frontend uses for DPS, EHP and boss numbers have no trust, provenance or confidence fields. The `V2TrustBadge` component is used only on the informational "Trusted Data" pages.

## 1. Method and commands

```bash
# Reachability from Flask routes (static import graph over every import statement, including lazy ones)
python3 scratchpad/reach.py   # seeds: backend/app/routes/*.py + backend/app/__init__.py
#  -> 282 reachable modules; of 166 calc-candidate modules in the scanned dirs, 92 reachable, 74 not

# Duplicate-formula discovery
grep -rnE "armou?r\s*/\s*\(|armou?r\s*\+\s*[0-9]|ARMOR_DIVISOR|ARMOR_AREA_LEVEL_FACTOR" backend frontend/src
grep -rnE "dodge\w*\s*/\s*\(|DODGE_DIVISOR|DODGE_CAP|BLOCK_DIVISOR|block_effectiveness" backend frontend/src
grep -rnE "^\s*[A-Z_]*(CRIT|ARMOR|RES|DODGE|BLOCK|LEECH|WARD|ENDURANCE|BLEED|IGNITE|POISON|VARIANCE)[A-Z_]*\s*=" backend

# Route -> engine tracing
grep -nE "post\(|get\(" frontend/src/lib/api.ts          # frontend calls
sed -n 213,286p backend/app/services/simulation_service.py
sed -n 132,300p backend/app/services/build_analysis_service.py

# Extracted-data comparison (skills, ailments)
python3 - <<'EOF'   # forge skills.json vs last-epoch-data exports_json/skills.json damageSources[isHit]
...  # see §5; result: 179 forge skills, 159 name-matched, 56 with an extracted hit source, 54 comparable
EOF
python3 -c "... exports_json/ailments.json ..."   # Bleed 53/3.0s, Ignite 40/2.5s, Poison 28/3.0s, Electrify 44/2.5s

# Runtime probes (venv in scratchpad, requirements.txt)
venv/bin/python scratchpad/probe.py   # minion DPS, armor/EHP across implementations, penetration semantics, Increased Armor affix
venv/bin/python -m pytest -q -p no:cacheprovider <25 calc test files>   # 607 passed, 1 failed
```

Web sources: `support.lastepoch.com` and `maxroll.gg` could not be fetched because egress to them is blocked. Only search-result snippets were available, so every web-derived statement below is marked **[community]** or **[official-snippet]** and counts as secondary evidence.

## 2. Production call graph (what users actually see)

| Frontend call (`frontend/src/lib/api.ts`) | Route | Engine chain |
|---|---|---|
| `POST /builds/<slug>/simulate` (:464), report, compare | `routes/builds.py:252` | `build_service.simulate_build` → `build_analysis_service.analyze_build` → `stat_engine.aggregate_stats` → `combat_engine.calculate_dps` + `monte_carlo_dps` → `defense_engine.calculate_defense` → `optimization_engine.get_stat_upgrades`. **No conversions are passed (:229-238)** |
| `POST /simulate/build` (:466) | `routes/simulate.py:281` | `simulation_service.simulate_full_build`. **`SimulateBuildSchema` (schemas/simulate.py:310-318) has no `spec_tree`, so skill-tree modifiers and conversions are always empty on this route.** With no `passive_tree`, `aggregate_stats` uses the synthetic modulo stat cycle (`stat_engine.py:559-583`) |
| `GET /builds/<slug>/analysis/boss/<id>` (:640), `/analysis/corruption` | `routes/analysis.py:129` | `boss_encounter.simulate_boss_encounter` → `_phase_dps` (own armor/res formula, `boss_encounter.py:145-182`) |
| `/simulate/encounter`, `/simulate/encounter-build` | `routes/simulate.py:244,261` | `builds.build_stats_engine.to_encounter_params` (`:151-164`) → `encounter.state_machine.EncounterMachine` → `encounter.enemy_damage_pipeline` → `domain.combat_validation.resolve_hit` |
| `/simulate/conditional` (:468) | `routes/conditional.py` | `StateEncounterIntegration.evaluate_damage` (`services/state_encounter_integration.py:76-83`) |
| `/simulate/multi-target`, `/simulate/rotation` | `routes/multi_target.py`, `routes/rotation.py` | caller-supplied `base_damage`, `cooldown`, `cast_time` (sandbox engines) |
| `/simulate/stats` | `routes/simulate.py:86` | `stat_engine.aggregate_stats`, **not** `stat_resolution_pipeline` (this contradicts `docs/KNOWN_LIMITATIONS.md`, "Verified Systems" bullet 1) |

Not reachable from any route (static import graph): `app/engines/combat_simulator.py`, `app/combat/*`, `app/domain/{fight_simulator,full_combat_loop,ward,resistance_shred,mana,cooldown,speed_scaling,ailments,ailment_stacking,ailment_scaling,status_interactions,…}`, `app/enemies/enemy_defense.py`, `stats/stat_data_integration.py`, `combat/*`, `buffs/*`, `build/*`, `frontend/src/lib/simulation.ts` (zero importers). `calculate_dps_vs_enemy` (`combat_engine.py:589`) has **no production caller**.

## 3. Trust matrix

Legend: "Data?" asks whether the inputs come from extracted game data. "Mechanic?" asks whether the formula has been shown to match the game. Tests are marked **self** when they only pin the implementation's own output or restate its formula, and **indep** when they check against an outside source. No row has **indep** tests.

| # | Domain | Used by API? (file:line) | Formula as implemented / constants | Data? | Mechanic? | Tests | Class | Justification |
|---|---|---|---|---|---|---|---|---|
| 1 | Skill base damage + level scaling | yes, `combat_engine.py:353-354`, `skill_calculator.py:83` | `base × (1 + level_scaling × (lvl−1))`; base and scaling hand-entered in `game_data/skills.json` (179) **and** duplicated in `SKILL_STATS` (`combat_engine.py:56-243`, 179, 4 drift) | **No.** `docs/skill_damage_audit.md` says the values were "estimated"/"calibrated" | **No.** In the 1.4.6 extract, 150/184 skills have empty `levelScaling`; no uniform per-level coefficient exists | self (snapshot `test_regression_suite.py:137`) | KNOWN INCORRECT | 53/54 comparable skills differ from the extracted hit base by >25% (median 24.6×, e.g. Fireball 110 vs 25) |
| 2 | Added-damage effectiveness | yes, `combat_engine.py:359` | `flat × added_damage_effectiveness`, default 1.0 | 4/179 set | Yes in principle [extracted `addedDamageScaling`] | self | KNOWN INCORRECT | 34/56 comparable skills disagree with the extracted `addedDamageScaling` (e.g. Earthquake 1.0 vs 6.0) |
| 3 | Flat added damage routing | yes, `skill_calculator.py:95-161` | sums `added_{spell,melee,throw,bow}_<type>` by tag/type | affix values from `affixes.json` midpoints | Plausible | self | PARTIALLY TRUSTED | Routing is reasonable. The weapon base damage of melee attacks is not modeled |
| 4 | Increased (additive) pool | yes, `increased_damage_calculator.py:42-60` | Σ of matching `*_pct` fields | partial | Matches the community model "increased adds, more multiplies" | self | PARTIALLY TRUSTED | Correct structure. Depends on stat-key mapping (39.2% passive coverage per KNOWN_LIMITATIONS) |
| 5 | More multipliers (main path) | yes, `more_multiplier_calculator.py:26-29`, `final_damage_calculator.py:78` | `Π(1+v/100)` over `[stats.more_damage_pct, spec_more]` | partial | Correct form | self | PARTIALLY TRUSTED | Only two "more" buckets exist, and `stats.more_damage_pct` is a single summed value, so several "more" sources would be added together |
| 6 | Encounter-build damage aggregation | yes, `builds/build_stats_engine.py:151-158` | `base × (1 + (spell+phys+elemental+more)/100)` | SKILL_STATS (row 1) | **No.** "More" is treated as additive, all type pools are summed regardless of the skill, and there is no level scaling or flat damage | self | KNOWN INCORRECT | Contradicts the main pipeline (row 5) |
| 7 | Damage conversion | partly: `simulation_service.py:253` but **dropped** in `build_analysis_service.py:229-238`; never on `/simulate/build` | `apply_conversions` then type re-pool | parsed from narrative text (`skill_tree_resolver`) | Plausible | self | PARTIALLY TRUSTED | Two of three user paths never apply it |
| 8 | Crit chance | yes, `stat_engine.py:780`, `combat_engine.py:375` | `(base + flat) × (1 + inc)`, cap 1.0; spec-tree crit added **after** increased | n/a | Formula matches the "1.4.3 spec" (owner-provided, not a public source) | self | PARTIALLY TRUSTED | Order bug for spec-tree crit. The dead `frontend/src/lib/simulation.ts:213` uses an additive formula with a 0.95 cap |
| 9 | Crit multiplier | yes, `crit_calculator.py:35` | `max(1, 2.0 + bonus/100)` | n/a | Base 200% matches [community] | self | PARTIALLY TRUSTED | Reasonable. Not checked against independent data |
| 10 | Hit variance (Monte Carlo) | yes, `combat_engine.py:403-441`, `constants/combat.py:17` | uniform ×[0.75, 1.25] | n/a | Only low-quality web pages give ±25% | self | UNVERIFIED | No authoritative source |
| 11 | Attack/cast speed | yes, `speed_calculator.py:30-33` | `skill.attack_speed × (1 + Σbonus)` | **No.** Hand-entered `attack_speed` often differs from extracted `1/useDuration` (e.g. Surge 1.6 vs 5.0, Void Cleave 1.1 vs 0.5) | Weapon attack speed and speed multipliers are not modeled | self | UNVERIFIED | Inputs are unsourced |
| 12 | Hits per cast | yes, `skill_calculator.py:90` | `1 + added` | spec tree | Simplified | self | PARTIALLY TRUSTED | Ailment stacking ignores it (row 13) |
| 13 | Ailment DPS (bleed/ignite/poison) | yes, `ailment_calculator.py:62-105`, `constants/combat.py:22-28` | `base_dps × (aps × chance × duration) × (1+inc)`. Bleed **43/4.0 s**, Ignite 40/**3.0 s**, Poison 28/3.0 s | **No.** `data/combat/ailments.json` (Bleed 3.0 s) exists but no code reads it | Extract 1.4.6: **Bleed 53/3.0 s, Ignite 40/2.5 s**, Poison 28/3.0 s; [community] Bleed 53/3 s | self. **1 failing**: `test_combat_engine.py:398` expects the chance capped at 100 | KNOWN INCORRECT | Bleed base −19%, bleed stacks +33%, ignite stacks +20%. Ignores hits-per-cast. Electrify (44/2.5), Frostbite (50), Damned, Time Rot are missing |
| 14 | Boss ailment reduction | **no**: `is_boss` never passed (`ailment_calculator.py:67`) | ×0.40 | constant | UNKNOWN | self | NOT IMPLEMENTED | Constant exists but nothing applies it |
| 15 | Enemy armor vs player DPS | main DPS: **not applied**. Boss: `boss_encounter.py:164-166` | boss: `a/(a+1000)`, **cap 0.80**; calculator: `a/(a+10·AL)`, cap 0.85; `combat_simulator.py:64` `a/(a+300)`; `stat_data_integration.py:92` `a/(a+300)` | enemy profiles community-estimated (KNOWN_LIMITATIONS) | Official-snippet: `x/(x+10a)`, cap 85% | self | KNOWN INCORRECT | Four formulas and two caps. The headline DPS includes no enemy mitigation and the response does not say so |
| 16 | Enemy resistance + penetration | boss: `boss_encounter.py:169-178`; encounter: `domain/penetration.py:36-51`; calculator (no caller): `enemy_mitigation_calculator.py:66-91` | boss: **min** resistance across all 6 types, no penetration; domain: `clamp(res−shred−pen, −100, 75)` (penetration before the cap); calculator: `max(0, min(75,res)−pen)` | community estimates | [community] penetration applies **after** the cap and can go negative; shred applies before the cap | self | KNOWN INCORRECT | Three incompatible semantics. Probe: pen 30 vs res 20 gives 0 (calculator) and −10 (domain); pen 10 vs res 100 gives 65 and 75 |
| 17 | Armor/resistance shred | encounter only (`armor_shred.py`, reached via `combat_validation`); `resistance_shred.py` unreachable | 100 armor per stack, 4 s; res 5%/2% boss, **max 10 stacks** | extract: shred ailments `maxInstances` 10 | [community] says 20 stacks, which conflicts with the extract | self | NOT IMPLEMENTED | Not in the main DPS path (KNOWN_LIMITATIONS #246) |
| 18 | Player armor mitigation | yes, `defense_engine.py:101-104` | `armour·(1+pct)/(…+1000)`, cap 0.85, applied to **all** damage | stats | [official-snippet] `x/(x+10a)`, cap 85%, **70% vs non-physical**, does not apply to DoT | self (`test_defense_engine.py:66` restates the formula) | KNOWN INCORRECT | Ignores the 70% non-physical rule. Area level fixed at 100. The calculators treat 70% as an armor multiplier (0.41 at 1000 armor), while the community describes 70% of the mitigation (0.35). Docstrings in `domain/armor.py:15,49-50` still say 75% |
| 19 | Player resistances | yes, `defense_engine.py:107-122` | each capped at 75, then the **mean of 7** becomes one mitigation layer | stats | Cap 75% matches [community] | self | PARTIALLY TRUSTED | Cap is right. Collapsing everything to the average is a modeling choice. Enemy penetration of +1%/area level [community] is ignored |
| 20 | EHP | yes, `defense_engine.py:125-176`; second impl `derived_stats.py:105-121` (`/simulate/stats` pipeline path) | `HP/(1−total)/(block·dodge·crit)·endurance + ward` vs armor-only `HP/(1−mit)` (no `armour_pct`, no resistances) | stats | Heuristic composite | self | UNVERIFIED | Two different EHP definitions. Neither is labelled as an estimate |
| 21 | Dodge | yes, `defense_engine.py:135-139` | `r/(r+1000)`, cap 0.85 | stats | `x/(x+10a)`, 85% [community, consistent] | self | PARTIALLY TRUSTED | Area level fixed at 100 |
| 22 | Block | yes, `defense_engine.py:129-132`; `domain/block.py` uses a different semantic (fraction input, chance cap 0.85) | `BE/(BE+1000)`, **no 85% cap** | stats | [official-snippet] depends on area level, cap 85%; exact formula UNKNOWN | self | UNVERIFIED | Divisor unsourced. Cap missing in the production path |
| 23 | Endurance | yes, `defense_engine.py:160-169` | factor `1/(1 − t·r)`, cap 60 | class base 20 / threshold 22 | The exact value is `(1−t) + t/(1−r)`, so this is an approximation | self | PARTIALLY TRUSTED | About 1.5% low at default values. Does not handle DoT or ward ordering |
| 24 | Ward decay | yes, `defense_engine.py:181-183`; dup `domain/ward.py` | `0.4·W/(1+0.5R)` (`constants/defense.py:13`) | n/a | [community + dev patch notes] current formula `(0.2W + 0.00005W²)/(1+0.5R)`; `0.4W` is the **old** formula | self | KNOWN INCORRECT | Outdated formula. The module docstring (`defense_engine.py:12`) describes a third formula |
| 25 | Ward retention per INT | yes, `stat_engine.py:313` (2.0) | 2%/pt; `constants/defense.py:16` and `domain/ward.py:56` use **4%/pt**; `ACCURACY_AUDIT.md` C-15 claims 4 | n/a | [official-snippet] 2%/pt, [community] 4% | self | PARTIALLY TRUSTED | The production value matches the official snippet. The constant and the audit doc are stale |
| 26 | Crit avoidance / glancing blow | yes, `defense_engine.py:142-154` | enemy crit rate 0.35 and ×1.5 (`constants/defense.py:51-52`, invented); glancing turns crits into normal hits | n/a | `constants.json` and ACCURACY_AUDIT both note glancing blow = 35% less damage on glancing hits | self | KNOWN INCORRECT | Mechanic misread and constants invented |
| 27 | Stun avoidance | yes, `defense_engine.py:188` | `s/(s+1000)` | stats | UNKNOWN | self | UNVERIFIED | Unsourced |
| 28 | Class base stats + attributes | yes, `stat_engine.py:225-316,764-771` | 110 HP, 51 mana, Vit 6 HP, Dex 4 dodge, Str 4% armor | n/a | Comments say "in-game sheet". Not reproducible from the repo | self | PARTIALLY TRUSTED | Plausible but not independently checked |
| 29 | Mastery / keystone / passive fallback | yes, `stat_engine.py:264-297,559-583,670-675` | hard-coded bonuses (e.g. Juggernaut +200 armor); unknown keystone defaults to `{spell 10, hp 50}`; Lich +8 ward/pt; modulo stat cycle when no passive data | **No.** Fabricated | No | self | KNOWN INCORRECT | Injects invented stats into DPS and EHP. The `/simulate/build` route triggers the modulo cycle whenever `passive_tree` is omitted |
| 30 | "Increased Armor" affix | yes, `stat_engine.py:609-631` + StatPool | stat_key `armour` (flat); the T5 roll adds **+29 flat armour** instead of +29% | affix data | No | none found | KNOWN INCORRECT | Probe: `armour 0 → 29`, `armour_pct` unchanged |
| 31 | Minion damage | yes, through `calculate_dps` | minion skills scaled by player crit/speed and `minion_damage_pct` only; `minion_attack_speed/crit/*` unused | No | No | self | KNOWN INCORRECT | Probe: Summon Wolf DPS 343, Summon Bear 492. `KNOWN_LIMITATIONS.md` says these show 0 |
| 32 | Leech / sustain | defense: sustain score only (`defense_engine.py:191-196`); encounter `domain/leech.py` (cap 10%) | heuristic points | n/a | Leech duration (3 s) not modeled | self | UNVERIFIED | The score is a made-up heuristic |
| 33 | Mana / costs | no (`mana_cost` in skills.json is never read by DPS; `domain/mana.py` unreachable) | — | partial data | — | self (unit only) | NOT IMPLEMENTED | DPS assumes infinite mana |
| 34 | Cooldowns / rotation | `/simulate/rotation` only | caller-supplied `cooldown`, `cast_time` | caller input | Sandbox | self | UNVERIFIED | Correctness depends entirely on user input |
| 35 | Conditional modifiers | `/simulate/conditional` (`state_encounter_integration.py:76-83`); not in main DPS | "multiplicative" modifiers turned into a % and **added** to the increased pool; only spell/physical/damage_pct counted | caller input | More-vs-increased violated | self | KNOWN INCORRECT | Contradicts row 5 |
| 36 | Boss/encounter templates | encounter + boss routes | hard-coded HP, armor, res (`encounter/boss_templates.py:119-163`) | No | — | self | UNVERIFIED | Invented enemies |
| 37 | Area-level scaling | none in API paths (fixed 100: `constants/defense.py:42-47`) | — | — | Every armor, dodge and block formula depends on area level | — | NOT IMPLEMENTED | All defense numbers assume area level 100 |
| 38 | Composite scores (survivability, sustain, Build Score, "Overall Winner 60/40") | yes, `defense_engine.py:198-206`; `frontend/.../BuildScoreCard.tsx:34,70`; `SimulationComparison.tsx:85` | weighted heuristics | n/a | Not game mechanics | self | UNVERIFIED | Shown without a "heuristic" label |

Extra cross-cutting row: DPS vs enemy (`calculate_dps_vs_enemy`) is fully implemented and tested but is **dead in production**. Its tests prove nothing about anything users see.

## 4. Duplicate-implementation table

| Formula | Implementations (file:line) | Divergence |
|---|---|---|
| Armor mitigation | `defense_engine.py:101-104` (`/(a+1000)`, cap .85, all damage); `derived_stats.py:87,118` (`/(a+10·100)`, no `armour_pct`); `domain/armor.py:62` (`/(a+10·AL)`, non-physical ×0.70, cap .85·.70); `enemy_mitigation_calculator.py:53` (same as domain); `combat_validation.py:149-153` (physical only, non-physical **bypasses** armor); `boss_encounter.py:165-166` (`/(a+1000)`, **cap 0.80**); `engines/combat_simulator.py:64-65,143` (`/(a+300)`, cap 0.80); `stats/stat_data_integration.py:92` (`/(a+300)`); `frontend/src/lib/simulation.ts:299` (`/(a+1000)`, dead) | **9 implementations, 3 divisors (300 / 1000 / 10·AL), 3 caps (0.80 / 0.85 / 0.595), 3 non-physical rules (100% / 70%-of-armor / 0%)** |
| Dodge | `defense_engine.py:136-137`; `derived_stats.py:128-141`; `domain/dodge.py:43-45` | Same form. Area level fixed in two of the three |
| Block | `defense_engine.py:130` (`BE/(BE+1000)`, no cap); `domain/block.py:33-55` (effectiveness given as a fraction, chance cap 0.85) | Different input semantics |
| Resistance cap / penetration | `defense_engine.py:107-113`; `domain/resistance.py:31-53` (floor −100); `domain/penetration.py:49-51` (before cap); `enemy_mitigation_calculator.py:66-84` (after cap, floor 0); `boss_encounter.py:169-178` (min across all types) | 3 penetration semantics |
| Ward decay | `defense_engine.py:181-183`; `domain/ward.py` (+INT 4%/pt) | Same outdated formula. INT retention 2 vs 4 |
| INT → ward retention | `stat_engine.py:313` (2.0); `stat_resolution_pipeline.py:70` (2.0); `constants/defense.py:16` (4.0, used by `domain/ward.py:56`) | 2 vs 4 |
| Crit | `crit_calculator.py:26-35`; `domain/critical.py:24-26`; `combat/crit/critical_engine.py`; `frontend/src/lib/simulation.ts:213` (additive, cap 0.95) | Frontend copy is dead but contradicts the backend |
| Skill table | `game_data/skills.json` (registry, Flask context); `combat_engine.SKILL_STATS` (fallback **and** the only source for `build_stats_engine.py:125` and encounter-build) | 179 each. 4 drifted entries (Aura of Decay 25 vs 20, Umbral Blades ls .08 vs .10, plus case-duplicate keys "Aura Of Decay" and "Mark For Death" with different values) |
| Constants source | `app/constants/*.py`; `app/game_data/constants.json` (e.g. `endurance_threshold_default: 0`, `endurance_damage_reduction: 0.6`, `base_hit_chance: 0.92`); `backend/src/constants/defense.ts` | Three constant stores that disagree |
| Stat aggregation | `stat_engine.aggregate_stats`; `stat_resolution_pipeline` (8-layer, reached via `domain/build_state`); `builds/build_stats_engine` (wraps stat_engine and adds its own damage formula); `build/*` (unreachable) | Docs say the 8-layer pipeline serves `/simulate/stats`. It does not |
| EHP | `defense_engine.calculate_defense`; `derived_stats.compute_effective_health` | Different definitions |

## 5. "We have the data" vs "we understand the mechanic"

| Item | Data available? | Used? | Mechanic understood? |
|---|---|---|---|
| Skill hit base damage | Partly. The extract has direct `damageSources` for 81/184 skills (`skill_mechanics_coverage_1.4.6.md`), and the extractor says these are "not complete base damage" | **No.** Forge uses hand-calibrated values | No. For melee skills the extract shows base 2 plus effectiveness, which implies weapon-damage scaling that Forge does not model |
| Added damage effectiveness | Yes (`addedDamageScaling`) | No (4/179 set by hand) | Yes |
| Skill use speed | Yes (`useDuration`, `speedMultiplier`) | No | Partly |
| Ailment base / duration | Yes (`exports_json/ailments.json`, 1.4.6; `data/combat/ailments.json` in repo) | No (hard-coded constants) | Stacking model plausible |
| Armor/dodge/block curves | Not in the extract | — | Armor/dodge: community-consistent. Block: UNKNOWN |
| Ward decay | Not in the extract | — | Outdated |
| Enemy armor / resistances | `actors.json` exists in the extract (not evaluated here, UNKNOWN) | No; enemy profiles are community estimates | Penetration semantics inconsistent |

## 6. Trust labels in API output

- `simulate_full_build` / `analyze_build` return `stats, dps, monte_carlo, defense, stat_upgrades, …`. They carry **no** `trust`, `provenance`, `data_version` or `confidence` field. The only data-quality fields are `conversion_data_gap` (`simulation_service.py:75-105`) and `warnings` (`boss_encounter.py:102,138`).
- `SkillStatDef.data_version="hardcoded"` exists internally (`combat_engine.py:46-49`) but is never serialized.
- Frontend: `V2TrustBadge` appears only on `TrustedDataSupportMatrixPage`, `TrustedDataExplanationPage` and `PreV3MechanicalReadinessPage`. The analysis cards (`OffenseCard`, `DefenseCard`, `AnalysisPanel`, `BuildScoreCard`) have no estimate or trust wording. The only notices are a global Known Limitations link (`AppLayout.tsx:108`) and a benchmark disclaimer in `OffenseDefenseSplit.tsx:211`.
- `docs/migration/V2_5_SUPPORT_MATRIX.md:48-49` admits "planner-calculable count is 0 / stable-calculable count is 0". So the V2 trusted-data effort does not yet power any calculation, and the legacy engines described above do.

## 7. Claims-doc verification

| Claim | Doc | Verdict |
|---|---|---|
| "Ailment DPS … BLEED_BASE_RATIO=0.70, IGNITE_DPS_RATIO=0.20, POISON_DPS_RATIO=0.30" | KNOWN_LIMITATIONS.md | **Stale.** The code uses flat 43/40/28 per second |
| "34 skills" have approximate base damage | KNOWN_LIMITATIONS.md, skill_damage_audit.md | **Understated.** All 179 are hand-entered, and 53/54 comparable skills disagree with the extract |
| Minion skills "will see 0 hit-DPS" | KNOWN_LIMITATIONS.md | **False.** Non-zero DPS is computed from player stats |
| `/api/simulate/stats` returns the post-Layer-8 pipeline snapshot | KNOWN_LIMITATIONS.md | **False.** The route calls `stat_engine.aggregate_stats` |
| Armor shred consumed at `combat_engine.py:642` | KNOWN_LIMITATIONS.md | Only inside `calculate_dps_vs_enemy`, which has no production caller |
| "Int = 4% Ward Retention" (C-15 fixed) | ACCURACY_AUDIT.md | Production now uses 2%. The constant still says 4 |
| ward decay `0.4×(W−T)/(1+0.5R)` "✓" | ACCURACY_AUDIT.md | Outdated per [community / dev patch notes] |
| `BOSS_AILMENT_REDUCTION` "constant ✓, application MISSING" | ACCURACY_AUDIT.md | Still not applied |
| "This formula is correct per Last Epoch mechanics" | dps_audit_report.md §1 | Structure only. Inputs (row 1, 2, 11) are wrong |
| Everything "VERIFIED: 1.4.3 spec §…" | code comments | The "spec" was supplied by the owner and is not in the repo. UNVERIFIABLE |

## 8. Tests

- Ran 25 calculation-related test files: **607 passed, 1 failed** (`tests/test_combat_engine.py::TestAilmentDPS::test_ailment_chance_capped_at_100`, which expects bleed DPS at 200% chance to equal 100%; the engine gives 619 vs 310). Either the test or the engine is wrong. Both cannot be right.
- Kinds of assertion: formula restatement (e.g. `test_defense_engine.py:66` "Armor/(Armor+1000)") and pinned snapshots (`test_regression_suite.py:123-170`, e.g. Fireball DPS == 549). The file says outright that snapshots are "pinned output values from the live engine". 0 tests compare against extracted game data, in-game measurements or an independent calculator.

## 9. UNKNOWNs

- Exact block-effectiveness formula and area-level coefficient (official page unreachable).
- Whether ±25% hit variance exists in 1.4.x.
- Max shred stacks (extract `maxInstances` 10 vs [community] 20). The meaning of `maxInstances` was not confirmed.
- Whether enemy penetration of +1%/area level still applies in 1.4.x.
- Whether extracted ailment `damage` values are per second or per full duration. The per-second reading was assumed because Poison 28 and Electrify 44 match the Forge per-second constants.
- How extracted melee "base 2" combines with weapon damage. This decides whether Forge's 80–160 bases are approximating weapon damage.
- Enemy armor/resistance values in `last-epoch-data/exports_json/actors.json` (not examined).
- Correctness of class base stats (110 HP, 51 mana, endurance threshold 22). The repo says they come from in-game sheets, and no capture is stored.
- Runtime behaviour when the DB has no passive nodes (DB-dependent; not run).

## 10. What this does NOT prove

- It does not show that any formula marked PARTIALLY TRUSTED is correct. It only shows that the formula is consistent with secondary sources.
- Web evidence is search-snippet level only (support.lastepoch.com and maxroll.gg fetches were blocked). Treat [official-snippet] as unconfirmed.
- The extracted-data comparison covers only the 54 skills that have a direct hit damage source. The extractor itself calls `damageSources` partial. A large ratio proves that Forge values are not the extracted values. It does not prove what the in-game tooltip shows.
- Reachability comes from static import analysis. A reachable module may still go unused at runtime, and the reverse can happen through dynamic imports.
- No in-game measurement was taken. No DPS or EHP number was checked against the live game.
- Crafting, FP, BIS search and optimizer ranking are only covered where they consume the engines above.


---

<!-- FILE: 14_TEST_SUITE_AUDIT.md -->

# 14 — Test Suite Quality Audit

Audit date: 2026-10-06. Scope: `le-the-forge` at `main` HEAD `1efcef7` (2026-05-14, the commit Render last deployed) plus CI history for `dev` (`558557c`), and `last-epoch-data` at `main` HEAD `73e2ab0` (2026-05-31). This is a read-only audit. Nothing in either repository was modified. All test runs used throwaway copies (`git archive` / `git clone`) in a scratch directory.

## 1. Headline answers

| Question | Answer |
|---|---|
| Does a green backend suite say anything about extraction completeness? | **Very little.** No test reads the live upstream extractor output (`last-epoch-data`). The only "real bundle" test is hard-wired to a Windows path (`D:\Forge\...`) and always skips. The bundle snapshot guard skips unless `FORGE_DATA_BUNDLE_DIR` is set, and CI never sets it. Completeness tests for enemies and items skip on every run (303 skips). What is tested is a vendored, committed snapshot inside `le-the-forge` (for example the pinned `19398` modifier-row counts). |
| Is the importer's HTTP layer exercised for real? | **No.** Every LET and Maxroll fetch is replaced with `unittest.mock.patch` and a hand-written HTML/JSON body (`tests/test_importers.py:159-283`, 76 `patch(` sites in `tests/test_build_import.py`). The suite has no recorded real page, no live canary and no contract test against the current LET page shape. HTTP 403 handling is tested as a mocked status code (`test_build_import.py:3508-3519`), so the production 403 alert counts as "expected" behaviour. |
| Is CI currently green? | **No, and it has not been for months.** `dev`: **261 consecutive failed push runs** since run #527 (2026-05-09, PR #306). The last green push run was #525. All 40 most recent CI runs failed. In the latest run (`26659275258`) only "Backend Tests" failed; type-check and data validation passed. |
| Does the current `main` tree pass today? | **No, on a fresh install.** Running Python 3.11 with `pip install -r requirements.txt` resolves **SQLAlchemy 2.1.3**, which is unpinned and comes in transitively. In SQLAlchemy 2.1, `postgresql://` defaults to the `psycopg` (v3) driver, which is not installed. Result: `tests/test_deployment_readiness.py` errors (6 tests) and `pytest -x` stops after 3 passes and 1 error. See INFRA-1 in report 16. |
| `last-epoch-data` tests | 181 test files and about 2,319 test functions exist. **CI runs only 16 of them** (`tools/scripts/test_regeneration_gate.py`) plus the regeneration gate. The gate fails on `main` (62 consecutive failing `main` pushes since 2026-05-29, PR #155). Reproduced locally: `drift=7`. |

## 2. Method and commands

```
git ls-files backend/tests | wc -l                       # 357 tracked files, 337 test_*.py
grep -rhoE "^\s*(async )?def test_\w+" backend/tests | wc -l   # 7,225 test functions (static)
grep -rnE "pytest\.mark\.skip|pytest\.skip\(|skipif|importorskip|xfail" backend/tests   # 11 sites / 8 files
# full run (Python 3.13 venv; repeated for the key file with Python 3.11):
git archive HEAD | tar -x -C <scratch>/forge
FLASK_ENV=testing SECRET_KEY=.. JWT_SECRET_KEY=.. python -m pytest tests/ -q -p no:cacheprovider --junitxml=junit.xml
# fixture age
git log -1 --format=%ci -- <fixture>; git log --diff-filter=A --format=%ci -- <fixture>
# CI history (GitHub API, read-only): actions_list list_workflow_runs ci.yml branch=dev (300 runs paged)
# last-epoch-data
git clone <local> <scratch>/c/last-epoch-data
python tools/scripts/regeneration_gate.py --strict
python -m pytest tools/scripts -q --continue-on-collection-errors
```

## 3. Result of the full local run (`le-the-forge` main @1efcef7)

`11415 passed, 379 skipped, 7 errors` (Python 3.13, about 6 minutes; the process was later OOM-killed during teardown on the first run).

| Errors | Cause |
|---|---|
| 6 × `tests/test_deployment_readiness.py::test_*_cors_*` | `create_app("production"/"development")` → `ModuleNotFoundError: No module named 'psycopg'` (SQLAlchemy 2.1.3 default PG driver). Reproduced on Python 3.11 with CI's env vars. |
| 1 × `tests/test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes` | Teardown cascade on the session `app` fixture (`sqlite3.ProgrammingError: Cannot operate on a closed database`) after the failure above. |

These are the same kind of failures CI's `pytest -x` would stop on. The CI logs for runs older than the retention window return `410 Gone`, so the exact failing test in the historical dev runs is **UNKNOWN**.

## 4. Skips: what is silently not tested

From the JUnit XML (379 skipped):

| Count | File | Skip reason | Condition | Ever runs in CI? |
|---|---|---|---|---|
| 292 + 3 | `test_game_data_completeness.py`, `test_architecture_determinism.py` | `enemies.json removed — data consolidated…` | file missing (permanent) | **Never** |
| 16 | `test_combat_simulator.py:292,460` | `enemies.json not present` | file missing | **Never** |
| 7 + 2 + 1 | `test_game_data_completeness.py:197`, `test_architecture_determinism.py:37` | `items.json` / `affixes.json` removed | file missing | **Never** |
| 56 | `test_api_contracts.py:34` | needs seeded PostgreSQL | `psycopg2.connect` to localhost fails | **Never** (CI has no Postgres service) |
| 1 | `test_bundle_item_adapter_report.py:169` | needs `FORGE_DATA_BUNDLE_DIR` | env var | **Never** (CI does not set it) |
| 1 | `test_forge_safe_affix_bundle_loader.py:12,28` | `D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json` | Windows absolute path | **Never** on Linux |
| 0 (conditional) | `test_passive_tree_validator.py:169`, `test_optimization_api.py:90`, `test_api_contracts.py:299` | data-dependent skip inside test | runtime | Can turn a regression into a skip |

Plus **6 whole files excluded** by `backend/pytest.ini:13-19` (`--ignore=`): `test_affix_engine.py` (29 tests), `test_base_engine.py` (8), `test_craft_engine.py` (27), `test_craft.py` (17), `test_combat_engine.py` (57), `test_calculation_snapshots.py` (9). That is **147 tests**, last touched 2026-03-31 to 2026-04-15, and they are excluded because the code under test changed. The excluded `test_calculation_snapshots.py` is the only value-level calculation snapshot. It is excluded because "snapshot expected values are stale after calc refactor" (`pytest.ini:12`).

**321 of the 379 skips (85%) target data files that no longer exist.** As a result, the tests that claim to check enemy and item completeness check nothing on any machine.

## 5. What the tests prove, by area (heuristic filename classification)

| Area | Files | Test fns | What they prove | What they do NOT prove |
|---|---|---|---|---|
| Combat / simulation / stats engines | 121 | ~2,495 | Internal arithmetic consistency on synthetic inputs and determinism | That the inputs match the game (constants are hand-entered and the value snapshot file is ignored) |
| Uncategorised engine / misc | 91 | ~2,121 | Same as above (AoE, cooldowns, conditions, etc.) | Same |
| v2 trust / governance / diagnostic reports | 68 | ~620 | Report schemas are stable, keys exist, and counts are pinned (`19398` rows, `2070` stats). The planner is "non-calculating" (0 calculable modifiers) | Correctness of any extracted value. Several tests assert that a report generator's output matches counts derived from the same committed snapshot (self-referential) |
| Game data / validation / loaders | 26 | ~655 | `data/*.json` loads and constants have positive values. `len(affixes) > 1000` (`test_data_loading_performance.py:46`), `>= 1000` (`test_api_contracts.py:105`, which always skips) | Completeness against upstream. Weak lower bounds would still pass after a large drop (for example, 1,100 affixes out of 1,300+) |
| Crafting | 11 | ~621 | Craft rules on current data | Real FP/tier mechanics. The original craft engine tests are excluded |
| Importers (LET / Maxroll) | 5 (+ parts of others) | ~237 | Parser behaviour on **hand-authored** HTML/JSON and error mapping (404/403/500/timeout) | Behaviour against the **current** real LET/Maxroll pages, anti-automation protection, or field-level completeness of a real build |
| API / routes / auth | 15 | ~476 | Route wiring on SQLite in-memory | Postgres behaviour (56 contract tests skip) and production config (errors above) |

### Specific quality findings

1. **Mocked-away importer risk.** `test_importers.py:159-171` asserts only `character_class`, `mastery` and `len(skills) == 1`. A regression that dropped gear, affix rolls, passives or idols would still pass this test. `test_build_import.py` has more gear assertions, but its inputs are all synthetic `window["buildInfo"] = {...}` blocks (`test_build_import.py:60-64, 828-829`). The fixture files `le_tools_offline_buildinfo_*_sample.json` (added 2026-05-11) are small hand-curated samples of 2–4 KB. They are not real captured pages.
2. **Golden baselines are scaffolds, not goldens.** `tests/fixtures/v2/golden_baselines/*.json` (7 files, 231–377 bytes, added 2026-05-13) contain field-name lists and flags (`"mechanical_calculation_involved": false`). `test_v2_golden_baseline_plan.py` only checks that the paths exist and are unique. These files cannot detect a value regression.
3. **Pinned-count tests are useful but local.** `test_v2_stat_modifier_dry_run.py:31-64`, `test_v2_planner_metadata_remap.py:40` and `test_v2_experimental_planner_adapter_mode.py:32` pin `19398` and `2070`. They do detect drift of the committed snapshot in this repo. They cannot detect upstream patch drift, because upstream is never read.
4. **No round-trip or relationship tests against real data.** Examples of missing tests: import a real LET build, export it, and compare the result. Check that every affix referenced by uniques or items resolves in the affix catalog. A `grep` for such cross-file resolution in tests found only diagnostic-report key checks.
5. **Few negative cases for data loss.** No test asserts that a missing field produces a warning or `missing_fields` entry for real-shaped input (only synthetic shapes).
6. **Fixture ages.** `sample_character.json` was last changed 2026-03-31. All LET fixtures date from 2026-05-11 and the goldens from 2026-05-13. Nothing has been refreshed since the last deploy (2026-05-14), even though the 403 alert shows that the upstream behaviour changed.
7. **Frontend tests are not in CI.** There are 49 vitest files with about 916 `it/test` blocks, but CI runs only `npx tsc --noEmit` (`.github/workflows/ci.yml:81`). CI also does not run `vite build`.
8. **CI stops at the first failure** (`pytest -x`, `ci.yml:44`). One environment break hides every other failure, and the reported "passed" count is then meaningless.

## 6. `last-epoch-data` tests

| Item | Value |
|---|---|
| Test files | 181 (`tools/scripts/test_*.py`) |
| Test functions (static) | ~2,319 |
| Files with skip logic | 96 |
| Run in CI | **only** `tools/scripts/test_regeneration_gate.py` (16 tests) + `regeneration_gate.py --strict` (`.github/workflows/regeneration-gate.yml`) |
| Full local run (Python 3.13, jsonschema+pytest only) | `9 failed, 2293 passed, 1 skipped, 5 errors` (collection errors: `UnityPy` / `pefile` missing, which are extraction-host deps) |
| The 9 failures | Committed-report vs regenerated-report mismatches (same root cause as the gate drift) |
| Regeneration gate on clean clone @73e2ab0 | `total=185 drift=7 match=163 skipped_no_generator=15` → **GATE FAILED** |
| Drifting artifacts | `affixes_/items_/passive_nodes_/skills_trusted_subset_remediation_report.json`, `items_certification_reevaluation_report.json` (`schema_validation_result`), `domain_gap_closure_planning_report.json`, `extraction_coverage_gap_certification_report.json` (`…present` flags) |
| CI history | 62 consecutive failing `main` pushes since 2026-05-29 (#155). The last green run was #61 (PR #154). The `main` branch is **not protected**. |

Environment sensitivity observed: when run from a directory not named `last-epoch-data`, the gate reported 93 drifts (`$.repository_context.repository_name`). When run without `.git` it reported 4 errors (generators read `git show HEAD:`). The `…present` drifts depend on which gitignored local files exist on the machine that generated the report. The governance reports therefore pass only on the author's extraction host.

## 7. UNKNOWNs

- The exact first failing test in the historical `dev` CI runs (logs expired, `410 Gone`).
- Whether CI on GitHub currently resolves SQLAlchemy 2.1.x. It is highly likely because pip installs fresh with only the pip-download cache, but this was not observed in a CI log.
- Whether any manual or real-page importer testing happens outside the repo.
- Frontend vitest pass/fail status (another investigator runs the suite; not run here).

## 8. What this audit does NOT prove

- It does not prove that the engine math is wrong. It shows only that the tests cannot confirm it matches the game.
- The heuristic category counts come from filename regexes and are approximate.
- The local runs used Python 3.13 (full suite) and 3.11 (targeted). CI uses 3.11.
- A passing gate in `last-epoch-data` would show only that the reports are self-consistent, not that the extraction is complete.


---

<!-- FILE: 15_OBSERVABILITY_AND_OPERATIONS.md -->

# 15 — Observability and Operations Audit

Audit date: 2026-10-06. Scope: `le-the-forge` `main` @ `1efcef7` (deployed), with `dev` @ `558557c` checked where noted. Read-only.

## 1. Headline

The only operational signal is a Discord embed that fires per failed import. It has no app version, no upstream response metadata, no build/commit, no dedupe or aggregation, and no way to replay the failure. `/api/health` is a liveness probe that touches neither the DB, Redis nor game-data freshness. There is no error tracker (Sentry or similar), no metrics, no uptime monitor in the repo, no retry queue and no dead-letter store beyond the `import_failures` table. The only way to read that table is an admin JSON endpoint that has no UI.

Live check: `https://api.epochforge.gg/api/health` and `https://epochforge.gg` could **not** be reached. The sandbox egress proxy refused the CONNECT (`curl: (56) CONNECT tunnel failed, response 403`; WebFetch: `EGRESS_BLOCKED`). This is a **proxy** refusal, not the site's response. Live production state is **UNKNOWN**.

## 2. Inventory

| Capability | Present? | Evidence |
|---|---|---|
| Structured logging | Partial | `backend/app/utils/logging.py:28-41` JsonFormatter; `ProductionConfig.LOG_FORMAT_JSON = True` (`config.py:86`). `ForgeLogger` is used in 42 app modules; the rest use plain `logging` with %-format strings, so their fields are not structured. |
| Request IDs / correlation | **No** | `grep -rn "request_id\|X-Request-ID\|correlation" backend/app` → 0 hits |
| Slow-request logging | Yes | `app/__init__.py:163-175`: logs a warning above 500 ms and sets the `X-Response-Time` header |
| Unhandled-exception logging | Yes | `app/__init__.py:260-264` (`logger.exception`, then a generic 500) |
| Error tracking (Sentry etc.) | **No** | not in `backend/requirements.txt` or `frontend/package.json`; grep for sentry/datadog/prometheus/statsd → 0 |
| Metrics | **No** (ops) | `backend/metrics/` holds simulation metrics, not service metrics |
| Product analytics | **No** | no gtag/plausible/posthog in `frontend/src` or `index.html` |
| Health check | Liveness only | `backend/app/routes/health.py:49-58` returns `status/version/patch_version/uptime_seconds`. **No DB ping, no Redis ping, no data-load status.** It always returns 200. |
| Version endpoint | Yes | `app/routes/version.py:58-67`. `commit` comes from `git rev-parse` at request time and is null when `.git` is absent at runtime (Render runtime: **UNKNOWN**) |
| Data freshness signal | Broken | `data/version.json` has `"patch_version": "unknown"` (synced 2026-04-26), so health reports `patch_version: "unknown"`. `CURRENT_PATCH` defaults to `1.4.3` (`config.py:28`), and test fixtures reference `game_version: "1.4.6"`. That gives three different "versions". |
| Import failure persistence | Yes | `ImportFailure` model (`app/models/__init__.py:330-345`): source, raw_url, missing_fields, partial_data, user_id, error_message (≤1024 chars), timestamps |
| Import failure UI | **No** | `GET /api/admin/import-failures` (`app/routes/admin.py:96-`; `login_required` + `is_admin`). No frontend consumer (`grep import-failures frontend/src` → 0) |
| Discord alert | Yes | `app/services/discord_notifier.py` (see §3) |
| Retry queue / dead-letter | **No** | Failed imports are recorded and nothing re-tries them |
| Job history | Ephemeral | `app/utils/jobs.py:25-34`: in-process `ThreadPoolExecutor(max_workers=4)` per gunicorn worker, state in Redis with a 1 h TTL. Errors are swallowed (`except Exception: pass`, lines 65-66, 79-80). Jobs are lost on restart or deploy. |
| Scheduler / cron | **No** | No Render cron in `render.yaml` and no APScheduler/Celery |
| Extractor health | **No runtime signal** | Upstream `last-epoch-data` CI has been red since 2026-05-29 (report 14). Nothing in the app surfaces upstream bundle age or version. |
| Upstream dependency health (LET, Maxroll) | **No** | Only visible indirectly through per-failure alerts |
| Dashboards | **No** | `docs/migration/V2_5_PRE_V3_MECHANICAL_READINESS_DASHBOARD.md` is a doc. `frontend/src/pages/debug/BackendDebugDashboard.tsx` is a dev page. |
| Uptime monitor | **UNKNOWN** | Nothing configured in the repo, and `docs/rollback.md` mentions "first alert" without naming a monitor |
| Incident runbook | Yes | `docs/rollback.md` (129 lines) |
| Committed stray log | — | `backend/error_log.txt` is tracked (2026-04-12) and contains a Windows venv path error. It is noise, not a log sink. |

## 3. The Discord import alert: forensic review

Code path: `POST /api/import/build` → `_do_import` → `LastEpochToolsImporter.parse` (`lastepochtools_importer.py:693-727`) catches `HTTPError` and returns `ImportResult(success=False, error_message="Last Epoch Tools returned HTTP {status}.")`. `import_route.py:568-580` then calls `_record_and_alert`, which runs `ImportFailure(...)`, `commit` and `send_import_failure_alert` (`import_route.py:281-298`). The notifier then sends a daemon-thread POST (`discord_notifier.py:59-65, 109-182`).

The observed alert ("Source: lastepochtools; URL: …/planner/B5P5P8M3; Missing Fields: None; Parsed Data: No data parsed; Error: Last Epoch Tools returned HTTP 403", twice) maps exactly to `discord_notifier.py:116-133`.

### What the alert can and cannot answer

| Question | Answerable from alert? | Why / missing field |
|---|---|---|
| WHAT failed | Partly | The HTTP status is shown, but "Missing Fields: None" is misleading for a fetch failure. No failure class is attached (fetch/parse/map/save). |
| WHERE (which build) | Yes | raw_url |
| WHY (upstream reason) | **No** | No response headers (`server`, `cf-ray`, `cf-mitigated`), body snippet, or egress IP. A Cloudflare challenge cannot be told apart from an auth wall or a removed build. |
| Upstream version / page format | **No** | Not captured |
| App version / commit | **No** | Not in the embed; `__version__` and the commit are not attached |
| Extractor / data bundle version | **No** | Not attached (and `patch_version` is "unknown") |
| Build source (LET / Maxroll) | Yes | source |
| Isolated vs systemic | **No** | No counter, rate or "N failures in last hour" field, and no dedupe. The "twice" event produced two identical embeds. |
| Replayable | **No** | The fetched HTML is never stored on failure. `partial_data` is null for a fetch failure. |
| Which user | Partly | user_id or "anonymous" |
| Request correlation | **No** | No request ID |
| Severity routing | Minimal | Only red/orange by "hard"/"partial" |

### Reliability gaps in the alert path

1. If the DB `commit` fails, the alert is **not** sent, because both are inside the same `try` (`import_route.py:286-299`). An outage of the DB hides import failures too.
2. `WEBHOOK_URL` is read once at import time (`discord_notifier.py:18`), so rotating it requires a restart.
3. Each failure starts an unbounded daemon thread with no rate limit. A systemic upstream block (such as the 403) produces one Discord message per user attempt and can hit Discord webhook rate limits (HTTP 429). That outcome is logged only as `discord_notifier: webhook returned 429`.
4. Discord failures are logged only as text, with no counter.
5. The prose error string is persisted (≤1024 chars). The status code is not stored as a field, so `import_failures` cannot be aggregated by cause without parsing strings.

## 4. Health-check depth

`/api/health` returns 200 whenever the process is up. It does not detect:
- DB unreachable (only `pool_pre_ping` per request)
- Redis unreachable. At boot, `_init_limiter` silently falls back to per-process in-memory rate limiting (`app/__init__.py:31-45`), which multiplies the effective limits by the worker count with no signal.
- Game data failed or partial load (the pipeline loads at `create_app` and a hard failure crashes boot, but a degraded load is not reported)
- Upstream import sources blocked

## 5. Recommended minimum ops contract (for the remediation phase; no changes made)

- Add `app_version`, `commit`, `data_version`/bundle hash, `upstream_status`, selected `upstream_headers` (server, cf-ray, cf-mitigated) and a `failure_stage` enum to `ImportFailure` and the embed.
- Store a capped snippet of the upstream response (for example the first 2 KB) so failures can be replayed.
- Aggregate: dedupe by (source, status) per N minutes and emit "X failures / Y attempts in last hour".
- Readiness endpoint: DB `SELECT 1`, Redis ping, data loaded with counts and version. Keep `/api/health` as liveness.
- Add an error tracker and an external uptime monitor on both domains.

## 6. Commands used

```
grep -rn "DISCORD_IMPORT_WEBHOOK_URL\|ImportFailure\|import_failure" backend --include=*.py
sed -n 1,182p backend/app/services/discord_notifier.py
sed -n 270,320p,500-620p backend/app/routes/import_route.py
sed -n 680,740p backend/app/services/importers/lastepochtools_importer.py
grep -rn "sentry|prometheus|statsd|datadog|posthog|plausible|gtag" -i backend frontend/src
grep -rln ForgeLogger backend/app | wc -l          # 42
curl -sS -D - https://api.epochforge.gg/api/health  # proxy 403 (CONNECT refused)
cat data/version.json
```

## 7. UNKNOWNs

- Live `/api/health` and `/api/version` responses (egress blocked).
- Render-side alerting, log retention and metrics configuration (dashboard-only settings).
- Whether an external uptime monitor exists.
- Volume of rows in `import_failures` in production.

## 8. What this does NOT prove

- It does not prove that production is unhealthy. It shows that nothing in the repo would tell anyone if it were.
- It does not identify the root cause of the LET 403. It shows that the alert lacks the fields needed to determine it. Datacenter-IP or anti-automation blocking is a hypothesis only.


---

<!-- FILE: 16_INFRASTRUCTURE_AUDIT.md -->

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


---

<!-- FILE: 17_SECURITY_AND_DEPENDENCY_AUDIT.md -->

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


---

<!-- FILE: 18_DEAD_CODE_AND_ARCHITECTURAL_DRIFT.md -->

# 18 — Dead Code and Architectural Drift

Audit date: 2026-10-06
Scope: Phase 16. Abandoned systems, duplicate implementations, old extractors, legacy schemas, compatibility shims, unused endpoints/components, obsolete flags, old generated data, and TODO markers.
Mode: read-only classification. Nothing was deleted or changed. The terms "dead", "test-only" and "orphan" below are classifications, not removal decisions.

---

## 1. Summary

- The backend has **31 top-level Python packages** besides `tests`, `scripts` and `migrations`, covering **553 non-test modules**. Static import-graph analysis from the runtime entry points (`wsgi.py`, `app`, `config`) gives:
  - **283 modules runtime-reachable**
  - **237 modules imported only by tests or scripts** (192 tests-only, 45 tests plus scripts)
  - **33 modules imported by nothing**
- There are **at least five combat/fight simulator implementations**. Only one path is wired to the HTTP API: `simulation_service` → `app/engines/{stat_engine, combat_engine, defense_engine}` plus `builds/build_stats_engine` plus `encounter/`. The other four are test-only or orphaned.
- There are **at least four affix data paths**: legacy `data/items/affixes.json` (read directly by four or more modules), the Forge-safe export (env path), the Forge-safe bundle (env path), and v2 bundles in `docs/generated`. Feature flags select between them, and every flag defaults to off, so legacy is authoritative in production. The parallel paths make it ambiguous which one is canonical.
- `/monte-carlo` is a routed frontend page that **produces mock, unseeded `Math.random` results client-side** while presenting itself as a stochastic damage simulation. Meanwhile the backend Monte Carlo package (`backend/simulation`, 17 modules) is fully orphaned.
- Code markers are almost unused: **1 TODO, 0 FIXME/XXX/HACK** across backend, scripts and frontend source. Debt lives in Markdown docs instead: 9 root `.md` files and 43 entries in `docs/`.

---

## 2. Method and commands

```bash
# module-level import graph (AST; absolute and relative imports; lazy in-function imports included)
python3 scratch/modgraph.py scratch/mod_class.json      # roots: wsgi, app, config; tests/*; scripts/*
python3 scratch/imports.py  scratch/import_graph.json   # package-level edges
grep -rn "importlib\|__import__" backend/app             # 0 hits -> no dynamic imports to miss
grep -n "register_blueprint" backend/app/__init__.py      # 28 blueprints, all route files registered
# generated-file references
for f in docs/generated/*; do grep -rl "<stem>" backend/app backend/data frontend/src | backend/scripts scripts | backend/tests; done
# frontend
grep -rlw <Name> frontend/src --include=*.ts --include=*.tsx
# markers
grep -rnwE "TODO|FIXME|XXX|HACK" backend scripts frontend/src electron
```

Limitations of the method: static AST only. "Runtime-reachable" means importable from the app's entry points, **not** that the code executes on a request path. String-based dispatch, `getattr` plugin patterns and subprocess calls are not modeled.

---

## 3. Backend package classification (module level)

| Package | Runtime | Tests/scripts only | Unreferenced | Classification |
|---|---|---|---|---|
| `app` | 177 | 74 | 5 | Core. 74 modules are diagnostic or experimental and test-only (section 4) |
| `bis` | 16 | 13 | 0 | Partly live (`/api/bis`) |
| `builds` | 6 | 2 | 0 | Live (simulation_service, optimize) |
| `encounter` | 11 | 1 | 0 | Live (simulation_service boss encounter) |
| `rotation` | 9 | 2 | 0 | Live (`/api/simulate` rotation) |
| `optimization` | 10 | 0 | 0 | Live (`/api/optimize`) |
| `targets` | 7 | 1 | 0 | Live (multi_target) |
| `data` | 18 | 4 | 0 | Live (forge-safe loaders, VersionedLoader) |
| `conditions`, `modifiers`, `state`, `events`, `skills`, `damage` | 4/4/3/2/3/2 | 1/0/3/0/0/2 | 0 | Live via conditional and multi-target routes |
| `metrics`, `services`, `debug` | 2/2/2 | 2/6/7 | 1/1/1 | Mostly test-only |
| `crafting` | 3 | 20 | 0 | **Parallel crafting stack.** Only `crafting.models.craft_state` is reachable (via `bis`). Runtime crafting is `app/engines/craft_engine.py` and `fp_engine.py` |
| `buffs` | 0 | 10 | 0 | **Test-only system** |
| `movement` | 0 | 22 | 0 | **Test-only system** (pathfinding, kiting, behaviours) |
| `spatial` | 0 | 12 | 0 | **Test-only system** |
| `projectiles` | 0 | 6 | 0 | **Test-only system** |
| `status` | 0 | 5 | 0 | **Test-only system** |
| `visualization` | 0 | 17 | 0 | **Test-only system** |
| `integration` | 0 | 15 | 4 | **Test-only plus orphan** (external API, share links, `import/build_import_parser` unreferenced) |
| `build` (singular) | 0 | 7 | 0 | **Test-only.** It duplicates `builds` (plural: `gear_aggregator`, `passive_aggregator`, `rotation_engine`) |
| `stats` | 0 | 2 | 0 | **Test-only** (`stat_data_integration`) |
| `combat` | 0 | 3 | 4 | **Test-only plus orphan** (`combat/crit/critical_engine`, `combat/proc/proc_resolver` unreferenced) |
| `simulation` | 0 | 0 | **17** | **Fully orphaned** Monte Carlo stack (runner, parallel executor, seed manager, confidence intervals, result store) |

Non-Python items inside `backend/`:
- `backend/src/constants/*.ts` (14 TS files) is the frontend's `@constants` alias (`frontend/vite.config.ts:34`, `frontend/tsconfig.json:26-27`, mounted read-only in `docker-compose.yml:71`). It is mirrored in Python by `backend/app/constants/` (`__init__.py:3`: "Mirrors backend/src/constants/"). That is **two hand-synchronized copies of game constants**, plus `frontend/src/constants/` (4 more files).
- `backend/error_log.txt` (74 bytes, tracked since `c3324f9` 2026-04-12) contains a single Windows venv error line: `../.venv/Scripts/python: No such file or directory`. It is a stale artifact.

---

## 4. Duplicate implementations

### 4.1 Combat / fight simulation
| Implementation | File | Reachability | Self-description |
|---|---|---|---|
| **Runtime path** | `app/services/simulation_service.py:10-15` → `app/engines/stat_engine.py`, `combat_engine.py`, `defense_engine.py`, `optimization_engine.py`; lazy `builds.build_stats_engine` (`:313-314`), `encounter.*` (`:343-348`) | Runtime (`/api/simulate`, `/api/builds/*`) | Authoritative by wiring |
| Monte Carlo combat simulator "Upgrade 2" | `app/engines/combat_simulator.py` | Tests only | "Simulates real combat behavior via seeded Monte Carlo" |
| Deterministic tick combat simulator | `app/combat/combat_simulator.py` (+ `combat_scenario.py`) | Tests only | "deterministic time-based execution loop" |
| "Realistic Fight Simulation (Step 10)" | `app/domain/fight_simulator.py` plus `combat_timeline.py`, `full_combat_loop.py`, `timeline.py`, `enemy_behavior.py` | Tests and `backend/scripts/validate_simulation.py` only | top-level `simulate_fight()` |
| Hit-resolution / crit / proc engines | `backend/combat/*` | Tests only (crit/proc unreferenced) | — |
| Monte Carlo framework | `backend/simulation/*` (17 modules) plus `services/monte_carlo_integration.py`, `debug/monte_carlo_logger.py`, `metrics/statistical_metrics.py` | **Nothing** | — |
| Frontend Monte Carlo | `frontend/src/pages/MonteCarloPage.tsx:6,31-32,49-80` (route `App.tsx:245`) | Routed. No nav link found | "Generates mock results client-side using a Box-Muller normal approximation". Unseeded `Math.random` |

Ambiguity: five non-runtime simulators each claim to be the "full", "realistic" or "deterministic" simulator. A contributor reading `app/engines/combat_simulator.py` (which sits next to the live `combat_engine.py` in the same directory) has no in-code signal that it is unused.

### 4.2 Stat engines
| Engine | File | Reachability |
|---|---|---|
| `BuildStats` / stat engine | `app/engines/stat_engine.py` | Runtime |
| Stat resolution pipeline | `app/engines/stat_resolution_pipeline.py` | Runtime |
| `BuildStatsEngine` | `builds/build_stats_engine.py` | Runtime (lazy, simulation_service `:313`) |
| Stat calculator | `app/domain/calculators/stat_calculator.py` | Runtime |
| Conditional/derived stats | `app/stats/*` | Runtime |
| Gear/passive aggregators | `build/gear_aggregator.py`, `build/passive_aggregator.py` | Tests only |
| Stat data integration | `stats/stat_data_integration.py` | Tests only |
| v2 stat registry / modifier dry run | `app/normalization/v2/stat_registry.py`, `app/planner_adapters/v2/stat_modifier_dry_run.py` | Registry runtime-importable. Planner adapter tests/scripts only |

At least **four reachable stat-aggregation code paths** exist (stat_engine, stat_resolution_pipeline, build_stats_engine, stat_calculator). Which one is canonical for a given endpoint is not documented in code.

### 4.3 Affix data loaders
| Path | Source file | Reader(s) | Default state |
|---|---|---|---|
| Legacy | `data/items/affixes.json` | `app/engines/affix_engine.py:30`, `app/game_data/pipeline.py:45` → `AffixRegistry`, `app/engines/stat_engine.py:398`, `app/services/importers/lastepochtools_importer.py:182` (direct file read), `app/services/forge_safe_affix_comparison_service.py:163`, `app/utils/cli.py:101` (DB seed) | **Authoritative in production** |
| Forge-safe export | `$FORGE_SAFE_AFFIX_EXPORT_PATH` | `data/loaders/forge_safe_affixes_loader.py`, `app/services/affix_catalog_service.py:112`, `/debug` | Off (`FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=false`, mode `shadow`) |
| Forge-safe bundle | `$FORGE_SAFE_AFFIX_BUNDLE_PATH` | `data/loaders/forge_safe_affix_bundle_loader.py`, `routes/experimental.py:1122-1210` | Off |
| v2 bundle | `docs/generated/v2_affix_bundle.json` | `app/repositories/v2/affix_repository.py` via `paths.py:11`, `routes/experimental.py:44` | Experimental routes only (`metadata.production_safe: false`) |
| Controlled resolver prototypes | `app/game_data/controlled_affix_resolver_*`, `controlled_modifier_resolver_*` | Tests/scripts only | — |

`affix_catalog_service.py:3` calls itself "the single selection point between legacy affix data and the …", but four other modules read `affixes.json` directly and bypass it.

### 4.4 Other duplicates
| Domain | Implementations | Notes |
|---|---|---|
| Optimizer | `optimization/` (runtime), `app/engines/optimization_engine.py` (runtime), `app/engines/build_optimizer.py` (tests only), `crafting/optimization/*` (tests only) | Two live, two dormant |
| Crafting | `app/engines/craft_engine.py`, `fp_engine.py` (runtime); `app/engines/craft_simulator.py` (tests only); `crafting/engines/*` (tests only; forging potential, fracture, glyph, rune, instability) | Dormant parallel crafting engine |
| Build model | `builds/` (runtime) vs `build/` (tests only) | Near-identical names |
| Constants | `backend/src/constants/*.ts`, `backend/app/constants/*.py`, `frontend/src/constants/*.ts` | Manual mirror |
| Game data on frontend | `frontend/src/lib/gameData.ts` ("patch 1.2.x", fandom/maxroll sources), `frontend/src/data/skillTrees/index.ts` (4334 lines), `frontend/src/data/raw/*.json` (2026-03-31) vs backend `data/` | Two sources of truth for skill and passive identity |
| Versioning | `data/version.json` (health), `config.CURRENT_PATCH` (version route), `data/versioning/versioned_loader.py` (load route), `integration/versioning/version_compatibility.py` (tests only) | See report 07 §3.1 |

---

## 5. Obsolete or inconsistent feature flags

| Flag | Location | Issue |
|---|---|---|
| `FORGE_SAFE_AFFIX_CATALOG_ENABLED` | `backend/config.py:42` **and** `:61` (same class `Config`) | The second definition silently overrides the first. Their semantics differ: `== "true"` vs `in {"1","true","yes","on"}`. Line 42 is dead |
| `FORGE_SAFE_AFFIX_EXPORT_PATH` | `backend/config.py:44` **and** `:65` | Duplicate definition |
| `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED`, `…_CONSUMPTION_MODE="shadow"`, `…_BUNDLE_ENABLED`, `…_DEBUG_ENDPOINT_ENABLED` | `config.py:43,45,57,66` | All default off. Production behaviour equals legacy only |
| `CURRENT_PATCH="1.4.3"`, `CURRENT_SEASON=4`, `DATA_VERSION="1.0.0"` | `config.py:26-30` | Stale defaults (report 07) |

---

## 6. Unused or test-only app modules (selected from 74)

- **Whole `app/planner_adapters/v2/` package** (13 modules: adapter, contracts, eligibility, golden_baselines, experimental_mode, …): tests/scripts only. The experimental routes use `app/repositories/v2`, not the adapter.
- **25 `app/game_data/*` diagnostic modules** (`bundle_item_*`, `controlled_*_resolver_*`, `le_tools_*sidecar*`, `malformed_tier_value_shape_validator`, `missing_modifier_reference_mapping_validator`, `modifier_unresolved_category_triage`, `affix_diagnostic_consumer`, `bundle_compat`): tests/scripts only. These are report generators kept inside the runtime package.
- `app/domain/{ailment_duration_scaling, ailment_scaling, aoe_falloff, buff_duration_scaling, buff_snapshot, cooldown, mana, proc_chain, rotation, speed_scaling, stability, triggers, ward, ailment_stacking, ailments, resistance_shred, status_interactions}`: tests only.
- `app/engines/{build_optimizer, build_serializer, combat_simulator, craft_simulator, validators}`, `app/enemies/enemy_defense`, `app/skills/skill_execution`, `app/utils/profiling`, `app/schemas/api_contracts`: tests only.
- **Unreferenced by anything:** `app/domain/multi_target.py`, `app/domain/stat_groups.py`, `app/schemas/{analysis, community, sensitivity}.py`.

Endpoints: all 28 blueprint modules in `app/routes/` are registered (`app/__init__.py:193-250`). `experimental_bp` is registered twice, under `/experimental` and `/api/experimental` (`:249-250`). No unregistered route file was found.

## 7. Frontend
- Routed but mock: `/monte-carlo` (section 4.1).
- Six service modules are imported only by `__tests__`: `services/presets/preset_manager.ts`, `services/session/session_restore.ts`, `services/keyboard/shortcut_manager.ts`, `services/build/build_manager.ts`, `services/favorites/favorite_manager.ts`, `services/sharing/build_import_service.ts`.
- Not imported anywhere (name grep): `logic/parseSkillTree.ts`, `logic/computeSkillStats.ts`.
- A broader filename heuristic flagged 44 candidates, but spot checks showed false positives (pages imported in `App.tsx` under other paths). The frontend component-level dead-code count is therefore **UNKNOWN** and needs a bundler-based analysis (e.g. a `vite build` module graph or `ts-prune`), which was not run.

## 8. Old extractors, legacy schemas, generated data

| Item | Status | Evidence |
|---|---|---|
| `/home/user/le-parser` | Archived JS parser, single commit `5135ce4` 2026-03-26 | Not referenced by Forge code except `.dockerignore:15-16`, `.gitignore:81`, `backend/scripts/report_v2_source_inventory.py:39` |
| `le-parser.worktrees/copilot-worktree-2026-03-31T22-17-24` | Gitlink (mode 160000 → `5135ce4`) with **no `.gitmodules`**. The directory is empty | Orphan submodule pointer. `git submodule` commands will error |
| `scripts/sync_game_data.py` | The only data-sync path. Hard-codes `<forge>/last-epoch-data/exports_json` (`:21`) | Last effective run 2026-04-26 |
| `scripts/generate_tree_data.py` | Same nested `SRC_DIR` convention | Generated `frontend/src/data/*` |
| `docs/generated/` (80 files) | 28 referenced from `backend/app`/`backend/data`/`frontend/src` (often from test-only modules or docstrings), 36 script-only, 1 test-only, **15 referenced by nothing** | The 15 are all diagnostic reports dated 2026-05-11: `affix_diagnostic_consumer_report.{json,md}`, `controlled_affix_resolver_comparison_report.{json,md}`, `fresh_le_tools_sidecar_diagnostic_report.md`, 7× `le_tools_*` reports, `modifier_unresolved_category_triage_report.{json,md}` |
| Root docs | `ACCURACY_AUDIT.md` (2026-04-15), `GAMEPLAY_EXPANSION.md` (04-02), `POLISH_REPORT.md` (04-08), `CONTRIBUTING.md` (04-08), `ARCHITECTURE.md`/`CHANGELOG.md`/`README.md`/`ROADMAP.md` (04-22) | None updated after 2026-04-22, although the v2/forge-safe architecture landed in May |
| Version files | `VERSION` 0.8.0 (served by `/api/version`), root `package.json` 0.3.0, `frontend/package.json` 0.1.0 | Three app versions |

### 8.1 Extractor repository (`last-epoch-data`) drift
- `tools/scripts/` holds **596 Python files**: 181 `test_*`, 179 `generate_*`, **338** with review/certification/governance/authorization/planning/blocker/readiness/policy in the name, and only ~31 extraction/processing scripts.
- Legacy/duplicate processors are kept next to the canonical ones: `process_affixes.py` vs `process_affixes_tt.py` (the canonical one in `run_all.py`), `extract_skill_trees_tt.py` vs `extract_skill_trees_fast.py`, `process_localization.py` vs `process_localization_unified.py`, `run_all.py` vs `run_all_safe.py`, and `extract_missing_mage_skills.py` (a one-off).
- `requirements.txt` pins `deepdiff` for "Patch-diff reporting (Phase 6)", but no patch-diff tool exists (report 07 §8).
- The last 50 commits on `main` (through 2026-05-31) are governance/planning documents and gates. **No data refresh or extraction-logic change happened after 2026-05-29.**

## 9. TODO / FIXME / XXX / HACK

| Marker | Python (backend + scripts) | TS/JS (frontend/src + electron) |
|---|---|---|
| TODO | 1 (`backend/tests/test_forge_safe_production_non_consumption.py:150`: "Add a planner-specific non-consumption guard when there is a stable…") | 0 |
| FIXME | 0 | 0 |
| XXX | 0 | 0 |
| HACK | 0 | 0 |

Interpretation: inline markers are not a usable debt signal here. Debt is tracked in Markdown (`docs/KNOWN_LIMITATIONS.md`, `FORGE_MIGRATION_TRACKER.md`, `V2_*`, and so on).

## 10. Does old code make the authoritative implementation ambiguous?

**Yes, in four areas:**
1. **Simulation.** Five non-runtime simulators sit alongside the live path, two of them in the same `app/engines` and `app/` trees.
2. **Affixes.** Legacy JSON is authoritative by default, yet three alternative pipelines are importable and four modules bypass the "single selection point" service.
3. **Version/patch identity.** Four different mechanisms give three different answers (`unknown`, `1.4.3`, `1.2.1`).
4. **Constants and game data.** There are three constant trees and a separate hand-maintained frontend game-data module labeled patch 1.2.x.

It is unambiguous for: route registration (all registered), Monte Carlo in the backend (wholly unreferenced, so clearly dormant), and test-only packages (`buffs`, `movement`, `spatial`, `projectiles`, `status`, `visualization`, `integration`, `build`, `stats`), which are isolated rather than competing.

## 11. UNKNOWNs
- Whether any test-only package is loaded through a path the AST scan cannot see (Celery tasks, CLI entry points outside `backend/`, Electron).
- Frontend component-level dead code (heuristic unreliable; no bundler graph).
- Which runtime stat engine each endpoint actually exercises per request (no execution tracing done).
- Whether the empty gitlink directory breaks deploys. `.dockerignore` excludes it.

## 12. What this does NOT prove
- "Runtime-reachable" means importable from the Flask app. It does not mean exercised by users.
- "Tests only" does not mean worthless. Several packages (`movement`, `buffs`, `crafting/engines`) may be deliberate work in progress.
- No deletion is recommended as an action already taken. The classification is input for a separate decision.
- Counts come from one static scan at HEAD `1efcef7`. Re-running `modgraph.py` after changes will shift them.


---

<!-- FILE: 19_DOCUMENTATION_DRIFT.md -->

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


---

<!-- FILE: 20_PRIORITIZED_REMEDIATION_ROADMAP.md -->

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
