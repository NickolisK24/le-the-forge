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
