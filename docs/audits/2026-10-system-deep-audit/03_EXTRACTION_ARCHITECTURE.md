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
