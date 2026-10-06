# R2 Fallback Audit (R2-11)

**Status: census complete; nothing changed.** Finding: REL-24, plus fallbacks inside REL-1, REL-4, REL-6, DB-4, DRIFT-3, SYS-3, IMP-5 (R4) and FE-8 (R6).

Machine-readable census: `R2_FALLBACK_CENSUS.jsonl` (1,557 records, `FB-0001`…`FB-1557`). Each record carries:
- `file`, `line`, `pattern`, `snippet`;
- the data `family`;
- `class`, with a `reason`;
- `tier` (`RUNTIME`, `RETIRED_BY_R2`, `ARCHIVED_TOOLING`, `OTHER_SCRIPT`);
- for dangerous records, the `owner` package that removes it.

## Method

- **Scope:**
  - `backend/app/**`, excluding tests and migrations;
  - the data-writing scripts `scripts/sync_game_data.py`, `scripts/generate_tree_data.py` and `scripts/build_sprite_map.py`;
  - `frontend/src/**`, excluding tests.
- **Patterns:**
  - `.get(k, default)` and `or 0 / [] / {} / '' / 'unknown'`;
  - every `except` and `catch` body (pass, continue, return-empty, assign-empty, log-and-continue);
  - `next(iter(...))` and `next(..., None)`, plus first-match `[0]` picks;
  - name lookups that silently return `None`;
  - `logger.debug` on skipped records;
  - frontend `?? 0`, `|| 0`, `?? []`, `?? "Unknown"`, `.find()`, `?.[0]`;
  - literal identity defaults ("Sentinel", first mastery).
- **Classification:** rule-based first. Then every backend DANGEROUS record and every frontend non-SAFE record was reviewed by hand (more than 250 per-line corrections). SAFE records were spot-checked only.
- **Exclusions:** 665 candidates are excluded, each with a reason. Examples: 157 handlers that already return an explicit error; 147 sparse-map or accumulator lookups where absent equals zero by construction; 104 request-input defaults; 88 in infrastructure files.

| Class | Definition used | Count |
| --- | --- | --- |
| SAFE_PRESENTATION_FALLBACK | Affects only display text or formatting; the UI does not imply data truth | 693 |
| EXPLICIT_UNSUPPORTED_STATE | Surfaced as an explicit unknown or unsupported state that cannot be mistaken for data | 120 |
| **DANGEROUS_SILENT_FALLBACK** | Missing or invalid game data silently becomes a value that changes meaning (0 in a calculation, first mastery/unique/item, "Unknown" persisted or used as identity, `[]` as if valid, swallowed exceptions dropping records, `unknown` presented as a version) | **744** |

## The audit's headline numbers, recounted today

| Metric | Audit | Today |
| --- | --- | --- |
| Backend `.get(..., 'Unknown')` | 21 | 23 (25 with "Unknown Boss" / "Unknown Item") + 1 in scripts |
| Backend `or 0` | 34 | 34 |
| Backend `except: pass` | 18 | 19 (5 in infrastructure) + 8 `except: continue` |
| Frontend `?? "Unknown"` | 11 | 6 (13 including `\|\|` and ternaries) |
| Frontend `?? 0` / `\|\| 0` | 186 | 186 |
| DB error → `200 []` | yes | confirmed: `ref.py:181,209,213,233,317`, `passives.py:126,145,173` |
| `data_version` always `unknown` | yes | confirmed: `pipeline.py:104,470` (`affixes.json` is a list) |

## Dangerous fallbacks: where they are and who removes them

| Owner | Dangerous | What it covers |
| --- | --- | --- |
| R2-P08 skills / abilities / skill trees | 139 | Name-keyed skill and tree lookups; first-slot primary skill; swallowed tree-modifier and conversion errors; Maxroll fuzzy name match |
| R2-P11 items / uniques / sets / blessings | 116 | First unique for a shared base; slot's first base type; invented forging potential 50; zero-filled implicits |
| R2-P05 affixes | 111 | Unknown affix name or tier midpoint contributes 0; tier number used as a stat value; name-keyed maps |
| R2-P06 classes / masteries | 56 | Missing class becomes Sentinel (backend in 3 places, frontend default); missing mastery becomes the class's first mastery in both importers and the planner; base-class name accepted as a mastery |
| R2-P13 builds / persistence | 43 | `character_class: 'Unknown'` written by file import; meta-analytics errors served as an empty snapshot; analysis errors become `(None, None, '', 20)` |
| R2-P07 passives | 23 | Allocations dropped with `pass` on load; non-integer node ids silently dropped on import; DB node lookups skipped |
| R2-P19 version surfaces | 10 | `unknown`, `1.0.0`, `1.4.3` and season 4 served as facts |
| R2-P09 reference API | 8 | DB errors → seed JSON or `[]` with 200; hard-coded item-type list |
| R2-P16 (other scripts, lint gate) | 6 | Data-writing helper scripts |
| **Subtotal owned by R2** | **512** | |
| R6 (calculation constants) | 69 | Enemy, boss and combat defaults (for example the `boss_standard` substitution, zero-filled enemy armour and resists). These are calculation semantics, out of R2's data scope. |
| Removed with retired code (R2-P18) | 156 | The legacy sync (122 in `sync_game_data.py` alone), the tree generator, and the v2/experimental modules |
| Archived offline tooling (R2-P18) | 7 | Diagnostic modules moved out of the runtime package |
| **Total** | **744** | |

Runtime split: 575 dangerous fallbacks are in runtime code (500 backend, 75 frontend). Of those, 506 are R2-owned and 69 belong to R6.

## The most consequential dangerous fallbacks

| # | Record | Location | Effect |
| --- | --- | --- | --- |
| 1 | FB-0469 / FB-0452 | `backend/app/game_data/pipeline.py:104,470` | `data_version` is always `unknown`, yet is stamped on every affix, enemy and skill definition and on the registries. The registry version-equality gate passes trivially. |
| 2 | FB-0789 / FB-0790 | `backend/app/routes/version.py:64-66` | `/api/version` serves `data_version 1.0.0`, `current_patch 1.4.3`, season 4, with no link to data |
| 3 | FB-0751–0753 | `backend/app/routes/ref.py:209,213,233` | Affix catalogue: DB error, then seed JSON, then `200 []`. An outage is indistinguishable from an empty catalogue. |
| 4 | FB-0750, FB-0762, FB-0739 | `ref.py:181,317`, `passives.py:126,145,173` | DB errors served as hard-coded lists, seed JSON or `[]`, with 200 |
| 5 | FB-0947 / FB-0992 | `lastepochtools_importer.py:946`, `maxroll_importer.py:1236` | Unknown mastery persisted as the class's first mastery |
| 6 | FB-0904 / FB-0907 / FB-0910 | `lastepochtools_importer.py:296,348,412` | First unique among several on a base; undecodable item gets the slot's first base type |
| 7 | FB-0016 / FB-0227 / FB-0188 | `domain/build_state.py:278`, `stat_resolution_pipeline.py:320`, `gear_upgrade_ranker.py:289` | Missing class becomes Sentinel in stats and ranking |
| 8 | FB-1310 | `BuildPlannerPage.tsx:877-878,968,1047,1224` | New build defaults to Sentinel with first mastery; class changes silently pick the first mastery and persist it |
| 9 | FB-0810 / FB-1024 / FB-1455 | `build_analysis_service.py:193`, `skill_classifier.py:134`, `useDebouncedAnalysis.ts:62` | Primary skill = first slot, so a utility skill can drive DPS |
| 10 | FB-1004 / FB-1005 / FB-1007 / FB-1018 | `simulation_service.py:42,63,270`, `skill_tree_resolver.py:602` | Tree modifiers and conversions dropped on exception, with 200 results. `:270` always yields `skills = []` (`"kwargs" in dir()` is always false). |
| 11 | FB-0115 | `combat_engine.py:305` | Registry miss silently switches to the hard-coded `SKILL_STATS` table |
| 12 | FB-0209 / FB-0211 | `stat_engine.py:493,620` | Unknown affix or missing tier midpoint contributes 0 |
| 13 | FB-1461 | `useLiveStats.ts:58-59` | Affix `type` used as stat key and tier number as stat value |
| 14 | FB-1443 | `ImportPanel.tsx:33` | Imported build without class saved as `character_class: 'Unknown'` |
| 15 | FB-1230 | `BaseItemSelector.tsx:38` | Missing forging potential becomes 50 |
| 16 | FB-1103 | `sync_game_data.py:488,499,527,554` | Missing coordinates or mastery written into `data/` as 0 / 0,0 (base tree), which every consumer then reads as real |
| 17 | FB-0858 | `build_service.py:302` | Meta-analytics error served as a real (empty) community snapshot |
| 18 | FB-0015 | `domain/build_state.py:274` | Passive allocations failing dependency checks dropped with `pass` on load |
| 19 | FB-0888 | `base_importer.py:47` | If `classes.json` fails to load, class and mastery validation silently turn off |
| 20 | FB-0959 | `maxroll_importer.py:189` | difflib fuzzy match (cutoff 0.75) taken as canonical skill/node identity |

The census lists 44 of these with full explanations (`R2_FALLBACK_CENSUS.jsonl`, filter `class == DANGEROUS_SILENT_FALLBACK`).

## Replacement rules (what R2 code does instead)

| Situation | Replacement |
| --- | --- |
| Canonical record missing for an id | `Missing(id, family, reason)`. API: 404 with `{error: REFERENCE_NOT_FOUND, family, id, data_version}`. Calculation: `UNSUPPORTED_DATA` listing the references. |
| Dataset not loaded or rejected | `503 DATASET_UNAVAILABLE` with the rejection reason. Never JSON seed, never `[]`. |
| DB error on a read | 5xx with an error code. Reference reads no longer touch the DB (R2-P14). |
| Value absent in canonical data | `null` with the field's provenance (`NOT_IN_AVAILABLE_EVIDENCE`, `UNKNOWN_VALUE`). Adapters never substitute 0. A calculation needing it reports which field. |
| Ambiguous identity (several candidates) | `AMBIGUOUS` with the candidate ids. Never `[0]`, never fuzzy matching (importers report to the user, R4). |
| Missing class, mastery or primary skill | Request validation error (400). The planner requires an explicit choice; "Sentinel" and "first mastery" defaults are removed. |
| Version or data version unknown | Explicit `version unavailable` state. A hard-coded patch is never shown. |
| Presentation-only fallback (missing icon, empty description) | Allowed (SAFE). Must not be persisted and must not feed identity or calculation. |

## Gate

R2-P16 adds a CI lint gate on data-consumption paths: the backend `app/` runtime packages and the frontend data and logic modules.

- **What it fails on:** new occurrences of the dangerous patterns, namely:
  - `.get(<game field>, 0 | '' | [] | 'Unknown')`;
  - `except ...: pass / continue / return []`;
  - `?? 0` / `|| 0` on game-data values;
  - `[0]` first-match picks over lookup results.
- **Exceptions:** each needs an inline `# fallback: SAFE_PRESENTATION — <reason>` or `EXPLICIT_UNSUPPORTED — <reason>` annotation.
- **Rollout:** the gate starts as a ratchet. The count may only go down, from the 575 runtime dangerous records. It reaches zero R2-owned records before R2 closes (R2-P18 acceptance).
- **R6 records:** the 69 R6-owned records stay allowlisted with an `R6` tag until R6.
