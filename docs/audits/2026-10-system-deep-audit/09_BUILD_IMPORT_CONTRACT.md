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
