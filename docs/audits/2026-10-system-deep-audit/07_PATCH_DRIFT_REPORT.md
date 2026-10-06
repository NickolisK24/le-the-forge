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
