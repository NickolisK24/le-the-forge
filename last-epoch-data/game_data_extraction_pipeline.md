# Game Data Extraction Pipeline

## Purpose

Extract **structured game data** from Last Epoch into versioned JSON
files that power:

- Build planners
- Crafting simulators
- Item databases
- Skill / passive planners
- Patch-diff tracking

---

## Platform Roles

| Machine                    | Role                                                                         |
| -------------------------- | ---------------------------------------------------------------------------- |
| **Windows PC**             | Game files live here. Run AssetStudio + IL2CPP tools + Python pipeline here. |
| **MacBook (main project)** | Consumes `exports_json/`. All app development happens here.                  |

**Transfer strategy:** Commit `exports_json/` and `extracted_raw/enums/` to git after each extraction. Pull on Mac. Never manually edit exported JSONs.

---

## Actual Folder Structure

```
LastEpochTools/
│
├── game_files/
│   └── current/                        ← Steam game install copy
│       └── Last Epoch_Data/
│           ├── resources.assets        ← Binary: MasterAffixesList, MasterItemsList
│           └── StreamingAssets/aa/StandaloneWindows64/
│               ├── database_assets_all.bundle          ⭐ PRIMARY
│               ├── defaultlocalgroup_assets_all.bundle ⭐ PRIMARY
│               ├── pcg_data_assets_all.bundle          ⭐ PRIMARY
│               ├── actors_misc_gameplay_assets_all.bundle
│               ├── actors_player_gameplay_assets_all.bundle
│               └── monolith_gameplay_assets_all.bundle
│
├── il2cpp_dump/
│   ├── DummyDll/                       ← ~170 dummy DLLs (enum/class structure)
│   ├── il2cpp.h                        ← C++ header dump
│   ├── script.json
│   └── stringliteral.json
│
├── extracted_raw/
│   ├── raw_bundles/                    ← 18,065 MonoBehaviour JSONs from AssetStudio
│   │   ├── database/
│   │   ├── defaultlocalgroup/
│   │   ├── pcg_data/
│   │   ├── player_gameplay/
│   │   ├── player_specific/
│   │   ├── actors_misc/
│   │   ├── localization_en/
│   │   ├── monolith/
│   │   └── duplicateasset/
│   ├── enums/
│   │   └── enums.json                  ← All extracted enums (42+ types)
│   ├── affixes/                        ← Raw affix MonoBehaviour exports
│   ├── items/                          ← Raw item MonoBehaviour exports
│   ├── skills/                         ← Raw skill MonoBehaviour exports (NEEDS EXTRACTION)
│   ├── passives/                       ← Raw passive MonoBehaviour exports (NEEDS EXTRACTION)
│   ├── classes/                        ← Raw class MonoBehaviour exports (NEEDS EXTRACTION)
│   ├── ailments/                       ← Raw ailment exports (NEEDS EXTRACTION)
│   ├── blessings/                      ← Raw blessing exports (NEEDS EXTRACTION)
│   ├── factions/                       ← Faction data (NEEDS EXTRACTION)
│   ├── loot/                           ← Loot table exports (NEEDS EXTRACTION)
│   ├── zones/                          ← Zone/waypoint exports (NEEDS EXTRACTION)
│   ├── localization/                   ← Localization string exports
│   ├── MasterAffixesList.json          ← Cached binary parse from resources.assets
│   ├── MasterItemsList.json            ← Cached binary parse from resources.assets
│   ├── UniqueList.json                 ← Unique item definitions
│   ├── AffixImport.csv                 ← 115 idol affixes
│   ├── manifest.json                   ← CRITICAL: 18,065 file classifications
│   ├── ggm_monoscripts.json            ← MonoScript ID → type name mapping
│   ├── resources_manifest.json
│   ├── community_skilltrees.ts         ← Community-sourced skill tree data
│   └── MonolithTimelines.json
│
├── tools/
│   ├── AssestStudio/                   ← AssetStudio GUI (Unity asset extractor)
│   ├── Cpp2IL/                         ← IL2CPP decompiler
│   ├── Il2CppDumper/                   ← IL2CPP dumper
│   ├── Il2CppInspector/                ← IL2CPP inspection tool
│   └── scripts/                        ← Python pipeline (entry point: run_all.py)
│       ├── run_all.py                  ← MASTER ORCHESTRATOR
│       ├── extract_enums.py            ← Step 1: Extract enums from DummyDlls
│       ├── classify.py                 ← Step 2: Classify all raw bundle JSONs
│       ├── resources_reader.py         ← Utility: Unity binary format reader
│       ├── odin_binary_reader.py       ← Utility: Odin Serializer binary parser
│       ├── process_affixes.py          ← Affixes (equipment + idol)
│       ├── process_items.py            ← Base items (equippable + non-equippable)
│       ├── process_skills.py           ← Abilities and scaling
│       ├── process_skill_trees.py      ← Skill tree node linking
│       ├── process_classes.py          ← Character classes & masteries
│       ├── process_ailments.py         ← Ailments & status effects
│       ├── process_localization.py     ← Localization strings
│       ├── process_localization_unified.py
│       ├── process_loot.py             ← Loot tables
│       ├── process_monster_mods.py     ← Monster modifiers
│       ├── process_timelines.py        ← Monolith timelines
│       ├── process_uniques.py          ← Unique items
│       └── convert_community_skilltrees.py
│
├── exports_json/                       ← FINAL OUTPUT — commit and pull on Mac
│   ├── affixes.json
│   ├── items.json
│   ├── skills.json
│   ├── skills_with_trees.json
│   ├── passive_trees.json
│   ├── ailments.json
│   ├── blessings.json
│   ├── classes.json
│   ├── loot_tables.json
│   ├── monster_mods.json
│   ├── timelines.json
│   ├── uniques.json
│   ├── community_skill_trees.json
│   ├── unmatched_trees.json
│   └── localization/                   ← 12 string mapping files
│
├── patch_versions/                     ← Archived snapshots per game version
│   └── 1.3.7.1_22373561/
│
├── assetstudio_search_guide.md         ← Reference: what to search in AssetStudio
└── game_data_extraction_pipeline.md    ← This file
```

---

## Pipeline Overview

```
Game Files (Windows)
      │
      ▼
[Stage 1] AssetStudio
   Load .bundle files → export MonoBehaviour assets → extracted_raw/raw_bundles/
      │
      ▼
[Stage 2] IL2CPP Tools
   GameAssembly.dll + global-metadata.dat → DummyDll/ (done once per patch)
      │
      ▼
[Stage 3] Python Pipeline  (run from LastEpochTools/)
   python tools/scripts/run_all.py
      │
      ├── extract_enums.py   → extracted_raw/enums/enums.json
      ├── classify.py        → extracted_raw/manifest.json
      ├── process_*.py (×10) → exports_json/*.json
      └── localization       → exports_json/localization/*.json
      │
      ▼
[Stage 4] Commit & Sync
   git add exports_json/ extracted_raw/enums/
   git commit -m "data: patch X.X.X"
   → Pull on MacBook
```

---

## Stage 1 — AssetStudio Extraction

> Reference: `assetstudio_search_guide.md`

**Tool:** `tools/AssestStudio/AssetStudioGUI.exe`

1. **File → Load File** — load these bundles (in order):

   ```
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\database_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\defaultlocalgroup_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\pcg_data_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_misc_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\actors_player_gameplay_assets_all.bundle
   game_files\current\Last Epoch_Data\StreamingAssets\aa\StandaloneWindows64\monolith_gameplay_assets_all.bundle
   ```

2. Filter **Asset List** by type: `MonoBehaviour`

3. Export to matching subfolder under `extracted_raw/raw_bundles/<bundle_name>/`

**Priority assets to export (see search guide for full list):**

| Category  | Search Term                          | Output Folder              |
| --------- | ------------------------------------ | -------------------------- |
| Affixes   | `AffixList`, `UniqueAffix`           | `extracted_raw/affixes/`   |
| Items     | `ItemList`, `UniqueList`, `IdolList` | `extracted_raw/items/`     |
| Skills    | `AbilityList`, `AbilityTreeData`     | `extracted_raw/skills/`    |
| Passives  | `PassiveTree`, `PassiveNodeData`     | `extracted_raw/passives/`  |
| Classes   | `CharacterClassList`, `MasteryList`  | `extracted_raw/classes/`   |
| Blessings | `BlessingList`, `TimelineList`       | `extracted_raw/blessings/` |
| Ailments  | `AilmentList`, `AilmentData`         | `extracted_raw/ailments/`  |
| Loot      | `LootTableList`, `ProphecyList`      | `extracted_raw/loot/`      |
| Zones     | `WaypointList`, `ZoneList`           | `extracted_raw/zones/`     |
| Factions  | `FactionList`, `ReputationList`      | `extracted_raw/factions/`  |

> **Note:** The raw_bundles mass export covers most of these automatically. Individual exports to named subfolders are for targeted re-extraction.

---

## Stage 2 — IL2CPP Extraction

> Run once per major patch. Skip if DummyDll/ is already current.

**Tools:** `tools/Il2CppDumper/` or `tools/Cpp2IL/`

**Source files:**

```
game_files\current\GameAssembly.dll
game_files\current\Last Epoch_Data\il2cpp_data\Metadata\global-metadata.dat
```

**Output:** `il2cpp_dump/DummyDll/*.dll` (~170 files)

These provide enum definitions, class structure, field names, and method signatures — the structural skeleton used by the Python processors.

---

## Stage 3 — Python Pipeline

> Run from the `LastEpochTools/` root directory.

**Requirements:** Python 3.9+ with `pythonnet` (for Mono.Cecil enum extraction)

```bash
python tools/scripts/run_all.py
```

### Pipeline Steps (in order)

| Step | Script                    | Output                                | Status      |
| ---- | ------------------------- | ------------------------------------- | ----------- |
| 1    | `extract_enums.py`        | `extracted_raw/enums/enums.json`      | ✅ Complete |
| 2    | `classify.py`             | `extracted_raw/manifest.json`         | ✅ Complete |
| 3    | `process_skills.py`       | `exports_json/skills.json`            | ✅ Complete |
| 4    | `process_classes.py`      | `exports_json/classes.json`           | ✅ Complete |
| 5    | `process_ailments.py`     | `exports_json/ailments.json`          | ✅ Complete |
| 6    | `process_localization.py` | `exports_json/localization/`          | ✅ Complete |
| 7    | `process_skill_trees.py`  | `exports_json/skills_with_trees.json` | ✅ Complete |
| 8    | `process_affixes.py`      | `exports_json/affixes.json`           | ✅ Complete |
| 9    | `process_items.py`        | `exports_json/items.json`             | ✅ Complete |
| 10   | `process_uniques.py`      | `exports_json/uniques.json`           | ✅ Complete |
| 11   | `process_timelines.py`    | `exports_json/timelines.json`         | ✅ Complete |
| 12   | `process_monster_mods.py` | `exports_json/monster_mods.json`      | ✅ Complete |
| 13   | `process_loot.py`         | `exports_json/loot_tables.json`       | ✅ Complete |

### Key Utility Scripts

| Script                            | Role                                                 |
| --------------------------------- | ---------------------------------------------------- |
| `resources_reader.py`             | Unity binary format reader (used by affixes + items) |
| `odin_binary_reader.py`           | Odin Serializer binary parser                        |
| `convert_community_skilltrees.py` | Converts community skill tree TS → JSON              |

---

## Stage 4 — Commit & Sync to Mac

After a successful pipeline run:

```bash
# Archive current version snapshot if needed
# (copy game_files/current/ → patch_versions/X.X.X.X_buildnum/)

# Commit the data exports
git add exports_json/
git add extracted_raw/enums/enums.json
git add extracted_raw/manifest.json
git commit -m "data: update to patch X.X.X"
git push

# On MacBook:
git pull
```

**What to commit:**

- ✅ `exports_json/` — all processed JSONs (this is the Mac's data source)
- ✅ `extracted_raw/enums/enums.json` — enum definitions
- ✅ `extracted_raw/manifest.json` — file classification index

**What NOT to commit:**

- ❌ `extracted_raw/raw_bundles/` — 18,065 files, too large
- ❌ `extracted_raw/MasterAffixesList.json` / `MasterItemsList.json` — large binary caches
- ❌ `game_files/` — full game install, gigabytes
- ❌ `il2cpp_dump/DummyDll/` — large, regeneratable

---

## Current Data Coverage

| System                | Output File                      | Coverage                                     |
| --------------------- | -------------------------------- | -------------------------------------------- |
| Affixes               | `affixes.json`                   | ✅ Equipment + idol (946 total)              |
| Items                 | `items.json`                     | ✅ All equippable + non-equippable bases     |
| Skills                | `skills.json`                    | ✅ 195 abilities with scaling & tags         |
| Skill Trees           | `skills_with_trees.json`         | ✅ Skills enriched with community tree nodes |
| Passive Trees         | `passive_trees.json`             | ✅ All 5 classes                             |
| Ailments              | `ailments.json`                  | ✅ 11 status effects                         |
| Classes               | `classes.json`                   | ✅ 5 base classes + masteries                |
| Blessings             | `blessings.json`                 | ✅ Monolith blessings                        |
| Loot Tables           | `loot_tables.json`               | ✅ 41 drop tables                            |
| Unique Items          | `uniques.json`                   | ✅ All uniques with mods                     |
| Monster Mods          | `monster_mods.json`              | ✅ Monster affix modifiers                   |
| Timelines             | `timelines.json`                 | ✅ Monolith zone definitions                 |
| Enums                 | `extracted_raw/enums/enums.json` | ✅ 42+ priority types                        |
| Localization          | `exports_json/localization/`     | ✅ 12 string mapping files                   |
| Factions / Reputation | —                                | ⚠️ Not yet extracted                         |
| Weapon scaling data   | —                                | ⚠️ Not yet extracted                         |
| Crafting recipes      | —                                | ⚠️ Not yet extracted                         |
| Prophecy system       | —                                | ⚠️ Not yet extracted                         |
| Zone / waypoint map   | —                                | ⚠️ Not yet extracted                         |

---

## Patch Update Workflow

When a new game patch releases:

### Windows PC (extraction machine)

1. **Update game files** — let Steam update normally, or copy new install to `game_files/current/`
2. **Archive old version** — copy `game_files/current/` (or key files) to `patch_versions/<version>/`
3. **Re-run IL2CPP** — only needed if assembly changed (check DLL timestamps)
4. **Re-run AssetStudio** — reload bundles, re-export changed asset types
5. **Run pipeline** — `python tools/scripts/run_all.py`
6. **Validate outputs** — check file counts and spot-check values (see checklist below)
7. **Commit and push** — `git commit -m "data: patch X.X.X"`

### MacBook (development machine)

1. `git pull`
2. New JSONs are available in `exports_json/`
3. Update any app-layer schema handling if data shape changed

---

## Validation Checklist

After each pipeline run, verify:

```
exports_json/
  affixes.json          — exists, > 100 KB
  items.json            — exists, > 100 KB
  skills.json           — exists, > 50 KB
  skills_with_trees.json — exists
  passive_trees.json    — exists, has 5 class entries
  ailments.json         — exists
  classes.json          — exists, has 5 base classes
  blessings.json        — exists
  loot_tables.json      — exists
  monster_mods.json     — exists
  timelines.json        — exists
  uniques.json          — exists
  localization/en.json  — exists, > 500 KB
```

Spot check:

- Open `affixes.json` — confirm affix names are human-readable (not raw IDs)
- Open `skills.json` — confirm skill names match in-game names
- Open `passive_trees.json` — confirm all 5 classes present

---

## IL2CPP Notes

IL2CPP extraction gives:

- Class structure and field names
- Method signatures
- Enum definitions
- String literals

It does NOT give:

- Runtime-populated ScriptableObject data (items, affixes, skill definitions)

That runtime data lives in Unity asset bundles → extracted via AssetStudio → parsed by Python processors.

---

## Important Notes

- **Never manually edit** files in `exports_json/` — they are regenerated by the pipeline
- **`manifest.json`** is the index for all 18,065 raw files — if classification changes, re-run `classify.py` first
- **`MasterAffixesList.json` and `MasterItemsList.json`** are cached binary parses from `resources.assets` — if affixes/items are wrong, delete these and re-run `process_affixes.py` / `process_items.py` to force re-parse
- The pipeline is **incremental** — each processor is independent; you can re-run a single script without re-running everything
- **`resources.assets`** (939 MB) is the source for affix and item binary data; AssetStudio loads it automatically when the game folder is loaded
