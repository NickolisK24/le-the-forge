# R2 Current Consumption Graph (R2-01)

**Status: evidence, read-only.**
- **Forge snapshot:** le-the-forge `9e1356a` (identical to production `80bd559` for the code paths traced; R1 changed docs and `scripts/sync_game_data.py` trust carry-through only).
- **Upstream:** last-epoch-data `0111f1e`.
- **Date:** 2026-10-06.

Every claim below cites file:line. Parts A–D below come from four structured code-reading passes:
- A: item families;
- B: character families;
- C: persistence and versioning;
- D: the v2 path.

They are reproduced unchanged apart from heading levels. The per-family summary and the cross-cutting facts are the synthesis.

## Cross-cutting facts

1. **The sync cannot run as written.** `scripts/sync_game_data.py:21` and `scripts/generate_tree_data.py:25` read `<forge>/last-epoch-data/exports_json`, which does not exist. The upstream repository is a sibling checkout.
   - **Data provenance:** the committed `data/` files come from older runs and from unknown merge scripts, with no provenance.
   - **`data/version.json`:** it says `patch_version: "unknown"`, lists only `data\items\affixes.json`, and carries no `upstream_trust` (the R1 carry-through code has never run).
2. **No provenance, trust or patch identity survives into any runtime record, DB row or API response.** Nothing in `backend/app` or `frontend/src` reads trust. Every upstream family is QUARANTINED, yet production uses all of them unlabelled.
3. **Identity is lost at the first hop for most families:**
   - affixes merged by name and re-keyed by slug, with ×100 scaling;
   - uniques keyed by slug of display name, numeric id dropped;
   - skills keyed by name (184 → 161);
   - masteries assigned by a wrong index table;
   - base items hand-curated with no game ids.
4. **There are parallel authorities for the same facts:**
   - 5 affix paths;
   - 4 mastery orderings;
   - 6 slot vocabularies;
   - 3 skill-tree sources (`skill_tree_nodes.json`, `community_skill_trees.json`, frontend `skillTrees/index.ts`);
   - 2 passive sources (DB `passive_nodes` / `passives.json` vs frontend `passiveTrees/index.ts`), which disagree on mastery membership for 6 masteries;
   - class base stats in backend and frontend that contradict each other.
5. **Reference data has a second, divergent authority in the DB.** It is never seeded on Render, and reads silently fall back to JSON (Part C).
6. **New finding (not in the audit): corrupted name↔id pairs in skill metadata.** The committed `skills_metadata.json` and `skills_with_trees.json` pair four tree ids with wrong names: `fi9` "Frigid Tempest", `en6` "Create Shadow", `me27` "Shocking Impact", `rf1azz` "Reap". Fireball, Meteor, Elemental Nova and Reaper Form have no metadata entry, and both importers inherit the wrong names (Part B §4, hazard 20).
7. **R1 contract defects found while tracing (fixed upstream):**
   - the run manifest never bound canonical exports to the snapshot, and outputs marked the extractor dirty, so C7 and C8 could never pass (`7dc1ad6`);
   - the walker dropped the `SkillTree.ability` reference, so no canonical tree could be joined to its ability (`0111f1e`).

## Per-family summary

PROV / TRUST / PATCH = does provenance / trust state / patch identity survive to runtime.

| Family | Current path (short) | Identity used | Main transformations | PROV | TRUST | PATCH | R2 package |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Affixes | `exports_json/affixes.json` → `sync_affixes` → `data/items/affixes.json` → pipeline / `AffixRegistry` / `game_data_loader` / stat engine; plus direct JSON readers, DB `affix_defs` → `/api/ref/affixes`, forge-safe/v2, and a 33-entry hand-coded frontend table | name, slug, autoincrement, `affix_id` (116 duplicates) | ×100 on every tier; 534 multi-property affixes flattened to property 0 (`extraRolls` dropped); property and modifier ids dropped; `class_requirement` and tags lost in seeding (REL-23); ×100 "correction" heuristic fixes 32 of 212 | no | no | no | P05 |
| Base items / item types | Hand-curated `base_items.json` (115 bases, no game ids); `items.json` synced with `_meta` dropped; `BASE_TYPE_ID_TO_ITEM_TYPE_ID` (TS + Py) used only by diagnostics; DB `item_types` from a literal | slot slug + name; importer uses a sequential index (IMP-4) | 1-H/2-H collapsed; invented FP/armour/implicit text; 6 slot vocabularies | no | no | no | P11 |
| Implicits | Hand-curated `implicit_stats.json` (one per slot); upstream per-subtype structured implicits unused; base/unique implicits are text parsed by regex | slot | structured → text | no | no | no | P11 |
| Uniques | `uniques.json` → `sync_uniques` (merge by slug of display name) → `data/items/uniques.json` → pipeline; build analysis resolves by name, first match | slug | numeric id, `subTypes`, structured mods, `resolvedBaseItem` dropped; curated text preserved | no | no | no | P11 |
| Sets | `setItems` + `set_bonuses.json` → `set_items.json` (47 of 59 items) | slug + `setId` | mods dropped; stale `_meta` | no | no | no | P11 |
| Classes | `classes.json` synced with `_meta` dropped (committed file is an older schema); hand `backend/app/game_data/classes.json` (dead), `stat_engine` class/mastery/keystone constants, frontend `CLASS_BASE_STATS` (contradicts backend) | class name | — | no | no | no | P06, P12 |
| Masteries | `MASTERY_MAP` index table in the sync (wrong for Mage/Primalist/Sentinel) → `passives.json` → DB → `/api/passives?mastery=`; 4 orderings in code; first-mastery defaults | name / position | 190 of 541 nodes mislabelled (REL-1) | no | no | no | P06 |
| Passives | `passive_trees.json` → `sync_passives` (+ an unknown merge script) → `passives.json` (541 nodes, 6 phantom Warlock nodes) → DB `passive_nodes` → API → frontend; separate frontend `passiveTrees/index.ts` + `edges.ts` with no generator | `"{prefix}_{raw}"` string + raw int | requirement points dropped; garbage edges emitted; property ids dropped; stats re-derived from display text; `node_type` invented; x/y from a third-party frontend file; analysis de-duplicates points | no | no | no | P07 |
| Skills | `skills.json` → `sync_skills_metadata` (keyed by name, 184 → 161) → `skills_metadata.json` (corrupted names) → pipeline / importers; hand `backend/app/game_data/skills.json` (179) + `combat_engine.SKILL_STATS`; frontend `CLASS_SKILLS` / `SKILL_STATS` | display name | collapse to tree-less variants (REL-6) | no | no | no | P08 |
| Skill trees | `skill_tree_nodes.json` (no generator; 2,190 of 3,936 nodes; stats as text; no edges; name lookup) for DPS; `community_skill_trees.json` (third-party) for `/api/skills`; frontend `skillTrees/index.ts` (single `parentId`, name → code map to tree-less variants) | name / code | multi-prerequisite cut to one parent (683 nodes); only the slot-0 skill's tree applied | no | no | no | P08 |
| Abilities | `classes.json` ability path ids not in the committed old schema; `ability_granted` null on 541 of 541 | — | dropped | no | no | no | P04, P08 |
| Ailments | `ailments.json` synced, never read (engines use `constants/combat.py` literals, CALC-3) | — | — | no | no | no | P04 (data), R6 (math) |
| Blessings | Hand-authored nested `blessings.json`; `sync_blessings` would produce an incompatible flat shape, silently emptying `blessings_flat` | slug of display name | — | no | no | no | P11 |
| Weaver | LET 1.4.2 copy `weaver_tree.json`; loaded, never consumed | `wv_<raw>` | — | no | no | no | P07 (graph model), P18 |
| Enums / properties / localization | Localization synced, never read; stat semantics re-derived from display strings (`STAT_KEY_MAP`, frontend mirror `passiveStatMap.ts`); `property_definitions.json` used by v2 normalization only | display string | numeric property id dropped | no | no | no | P03, P05, P07 |
| Monolith timelines, set bonuses | Synced, not consumed (R1 denominator `SYNCED_NOT_CONSUMED`) | — | — | no | no | no | P04 (typed views) |
| Player attributes, tree registry, property lists, game enums | No export consumed (R1 `NO_EXPORT`) | — | — | — | — | — | P04 |

## Identity hazards

Part A lists 23 item-side hazards (§ "Identity hazards"). Part B lists 31 character-side hazards (§ "Identity hazards") and the 39 mastery consumers (§ M.2). R2_MIGRATION_DAG.md assigns each to the package that removes it.

## Part A — Item families (affixes, base items, item types, implicits, uniques, sets)


Repo under study: `/home/user/le-the-forge` (abbrev. **F**). Upstream: `/home/user/last-epoch-data` (abbrev. **U**).
Method: read-only code reading plus Python profiling of the JSON files. No repo files were modified.

Scope note. `scripts/sync_game_data.py:21` sets `SRC_DIR = ROOT / "last-epoch-data" / "exports_json"`, where ROOT is the Forge repo root. There is no `F/last-epoch-data` directory, so the sync cannot run as written against the sibling checkout. `data/version.json` records the last run as `synced_at 2026-04-26`, `patch_version "unknown"`, `files_updated ["data\\items\\affixes.json"]` (a Windows path). It has **no `upstream_trust` key**, and `data/upstream_trust_manifest.json` **does not exist**. The current `data/` files therefore came from a run before the trust code was added.

---

### 0. Upstream inventory (what exists to consume)

| Upstream file | Shape / identity | Provenance carried | Trust (U/exports_canonical/TRUST_MANIFEST.json, patch 1.4.6 build 22986002) |
|---|---|---|---|
| `U/exports_json/affixes.json` | `{_meta, equipment[1112], idol[115]}`; record key `id` (int). The 115 `idol[]` ids reuse ids already present in `equipment[]` (`rollsOn: "Idols"`, ids 826+). 578 single-property records (`property`/`tags`/`modifierType` at top level). 534 multi-property records (`affixProperties[]`, second-property ranges in `tiers[].extraRolls[]`). Idol records also carry `tiers2[]`. | `_meta.pipeline/source`, no build stamp | QUARANTINED, not eligible: "legacy export: not reproducible…", "data_bundle action BLOCK for affixes/affix_tiers/affix_eligibility" |
| `U/exports_json/items.json` | `{_meta,_extra,equippable[40],nonEquippable}`; `baseTypeID` 0–39, `subTypes[].subTypeID` (resets per base type), `subTypes[].implicits[]` | `_meta.game_build` (unity, assembly sha) | QUARANTINED (WARN base_items/item_types, RAW_MISSING) |
| `U/exports_json/uniques.json` | `{_meta, uniques[409], setItems[59], setBonusData}`; `id` int, structured `mods[]` (property/tags/modifierType/value/maxValue/rollId), `subTypes[]`, `resolvedBaseItem{baseTypeID, subType{subTypeID,…}}`, `resolvedImplicitMods[]`, `tooltipDescriptions[]` | `_meta` counts | QUARANTINED (DEGRADE uniques, RAW_MISSING) |
| `U/exports_json/set_bonuses.json` | `setBonuses[]` keyed `setId` | `_meta.game_build` | QUARANTINED |
| `U/exports_json/metadata.json` | `version/patchVersion "1.4.6"`, `build "22986002"` | yes | n/a |
| `U/exports_canonical/affixes.json` | `{_meta, affixes[1112]}`, identity `affix_id` (0 duplicates) | full: `_meta.source` (raw sha256, game_assembly_sha256, unity, tool versions), `schema r1_canonical_affix/1`, enum decode provenance per field | QUARANTINED ("undecodable enum values displayCategory 42,43; specialAffixType 6") |
| `U/exports_canonical/property_definitions.json` | property id → name/value-type families | yes | QUARANTINED (RAW_MISSING) |
| `U/exports_canonical/TRUST_MANIFEST.json` | `families[]{family, consumer_state, trusted_calculation_eligible, reasons}`, `patch{patch, build, …}`, `report_hash` | n/a | 0 CERTIFIED, 44 QUARANTINED, 3 UNKNOWN families |

---

### 1. AFFIXES

#### 1.1 The affix paths that exist today

| # | Path | Entry point | Who reads it |
|---|---|---|---|
| **P1** | `data/items/affixes.json` → `GameDataPipeline` → `AffixDefinition` → `AffixRegistry` / `game_data_loader` | `pipeline.py:45,229-240`; `app/__init__.py:140-158` | `stat_engine` (module constants `:398-401`), `efficiency_scorer` via `routes/builds.py:327-331`, `gear_upgrade_ranker.py:126-130`, `affix_catalog_service._legacy_records` (`:126-131`), `craft_engine` via `affix_engine.get_affix_by_name` (`affix_engine.py:98-110`), `cli.py` seeding (`:19-37`), `/api/ref/affix-categories` |
| **P2** | `data/items/affixes.json` read **directly** with `json.load` | many (see §6) | `affix_engine.load_affix_data` (`:30-35`, fallback), `routes/ref.py:_get_affix_seed_data` (`:117-151`, JSON fallback for `/api/ref/affixes`), `routes/admin.py:26-39` (GET **and PATCH-writes** the file), `lastepochtools_importer._get_affix_map` (`:178-196`), `forge_safe_affix_comparison_service._load_legacy_affix_records` (`:155-176`), `routes/load.py:74` (via `RawDataLoader` + `DataMapper.affixes_from_bundle`) |
| **P3** | `affixes.json` → P1 `to_dict()` → `flask seed` / `reseed-affixes` → DB `affix_defs` → `/api/ref/affixes` | `cli.py:72-123`; `models/__init__.py:265-286`; `ref.py:204-292` | Frontend `GearEditor.tsx:558-562` (`refApi.affixes({slot})`), `api.ts:264` |
| **P4** | Forge-safe / v2 bundles (experimental). (a) `FORGE_SAFE_AFFIX_EXPORT_PATH` → `ForgeSafeAffixLoader` → `ForgeSafeAffixRepository` → `AffixCatalogService` when `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED` and mode is read_only/active. (b) `FORGE_SAFE_AFFIX_BUNDLE_PATH` → `ForgeSafeAffixBundleRepository` (experimental routes and comparison). (c) `docs/generated/v2_affix_bundle.json` → `V2AffixRepository` | `config.py:58-93`; `affix_catalog_service.py:41-124`; `data/loaders/forge_safe_affixes_loader.py`; `repositories/v2/paths.py:10-25` | `/api/affixes/catalog*` (`routes/affixes.py:25-84`), `/api/experimental/*` (`routes/experimental.py:22-31,1128-1210`). All are flagged `production_consumer: false` |
| **P5** | Hand-coded frontend affix table (does not use the data file) | `frontend/src/lib/gameData.ts:525-653` `AFFIX_DEFINITIONS` (33 entries) + `getAffixValue` | `frontend/src/lib/simulation.ts:19,189-196`, `GearSlotEditor.tsx:9,40,121`, `BuildPlannerPage.tsx:78-89` |

#### 1.2 Hop table: P1/P2/P3 (production legacy)

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | `U/exports_json/affixes.json` `equipment[]` | `data/items/affixes.json` (`sync_affixes`, `sync_game_data.py:151-318`) | numeric `id`; merged with existing records **by `name`** (`:181-186` `existing_by_name`) | `id` = existing slug or `_slugify(name)` (`:196`), with `_<numeric>` appended on slug collision (`:284-289`); `affix_id` = numeric id | `displayName`, `morphology`, `titleType`, `displayCategory`, `uniqueId`, `weaponEffect`, `derivedTags`, `_extra`, `specificRerollChances`, `affixIDToConvertTo`, `convertOnIncompatibleItemType`, `property` (property identity is lost), **`affixProperties[]` (all property identities for 534 multi-property affixes)**, **`tiers[].extraRolls` (2nd-property ranges)** | `type` lowercased; `applicable_to` from `canRollOn` via `SLOT_MAP` (`:88-114,145-148,237-240`); `tags` lowercased with "none" removed (`:243`), so multi-property affixes get `[]`; `class_requirement` = first class or comma-joined (`:132-138,246`); `t6_compatible` bool (`:249`); `special_affix_type` collapsed to 0 if Standard else 1 (`:263`), which loses Experimental/Personal/Set/IdolEnchantment/IdolWeaver; `rolls_on` lowercased; `reroll_chance` from `weighting` | **×100 on every tier** (`:199-205`: `round(minRoll*100,4)`, int-coerced). This is correct only for fractional percent stats. It inflates flat stats ×100 (e.g. Added Health T1 500–1500, Strength T8 2400–2800) | Multi-property affix flattened to one record with one `stat_key` and only property-0 ranges. Second property is gone | `_meta` (pipeline, source) not carried | none at record level; `_write_version_stamp` copies only `exports_json/*` families into `version.json.upstream_trust` (`:38-62`) | `version.json.patch_version` from `metadata.json` (`:25-33`); not stamped on records |
| A1-idol | `U/exports_json/affixes.json` `idol[]` | same file, entries `idol_<id>` (`:208-230`) | numeric `id` | `id` = `stat_key` = `idol_<id>`, `type: "idol"`, `applicable_to` from old data or `["idol"]` | `tiers2[]`, `displayName`, tags (uses `cur.get("tags", [])`, which is empty for idol), class | `title` = `shardName` | ×100 (same loop). 115 records end with every tier \|max\| < 1, many all-zero (e.g. `idol_827`) | Duplicates the equipment-list record with the same id → **116 duplicate `affix_id` values** (115 idol + 417) | no | no | no |
| A1-legacy | previous `data/items/affixes.json` | same file (`:306-315`) | `name` / `id` | unchanged | — | — | — | Legacy entries whose name is not in the export are preserved. Example: `acolyte_increased_projectile_speed_with_marrow_shards_and_bone_nova` keeps stale `affix_id 417` at index 1227 and collides with the real 417 at index 417 | no | no | no |
| A2 | `data/items/affixes.json` (list, 1228 recs) | `AffixDefinition` (`pipeline._load_affixes` `:229-240`; `domain/item.py:53-82`) | array order; `affix_id` or `id` | `name`, `stat_key`, `affix_id` | **`id` slug, `tags`, `class_requirement`, `level_requirement`, `rolls_on`, `special_affix_type`, `title`, `group`, `modifier_type`, `reroll_chance`, `t6_compatible`** (only name/stat_key/type/applicable_to/tiers/affix_id kept) | `data_version` | `AffixTier` → float; midpoint = `math.floor((min+max)/2)` (`item.py:45-47`), so fractional idol tiers floor to 0 | — | `data_version` from `_detect_version` (`pipeline.py:466-470`) = `"unknown"` because the file is a list | no | no |
| A3 | `AffixDefinition[]` | `AffixRegistry` (`affix_registry.py:39-80`) | name / affix_id / (slot,type) | dicts | — | — | — | **Last-wins** by `name` (98 dup names, 124 shadowed) and by `affix_id` (116 dups; 826–940 resolve to `type:"idol"` copies, 417 resolves to the stale legacy record). `all()` returns name-deduped values (`:104-106`), so 1104 of 1228 records | `data_version` "unknown"; mixed-version check is effectively inert | no | no |
| A4 | pipeline | `game_data_loader` (`:39-88`) | name | name-keyed dicts | — | `affix_tier_midpoints`, `affix_stat_keys` (`pipeline.py:163-171`, last-wins by name); `get_affix_types` returns prefix/suffix/idol, **not** the modifier type its docstring claims (`:49-51`) | — | `get_affixes_by_tag` always `[]` (tags dropped at A2, `:76-80`); `get_affix_by_id` **first-wins** loop (`:83-88`) | no | no | no |
| A5 | game_data_loader | `stat_engine` module globals `AFFIX_TIER_MIDPOINTS`, `AFFIX_STAT_KEYS`, `AFFIX_TYPES` (`stat_engine.py:398-401`) | display name | name | — | — | **x100 correction heuristic** `get_affix_value` (`:588-631`): divides by 100 only if `stat_key ∈ _FLAT_SCALE_STAT_KEYS` (`:592-606`) **and** T1 midpoint > 100. Of 212 records with T1 midpoint > 100, 32 are corrected. Strength/Int/Dex/Vit/Att (T1 = 100) and slug-keyed flat stats (e.g. `minion_dodge_rating` T1 3500–6500) stay ×100 | Bucket chosen by key suffix (`_pct` → increased, `more_` → more, else flat; `:482-504`), not by `modifier_type`. 1113/1228 `stat_key` values are slugs (== `id`) that are not `BuildStats` fields, so `StatPool.resolve_to` drops them silently (`hasattr` check, `:441-448`) | Computed **once at import**. Fallback pipeline if outside app context (`game_data_loader.py:23-36`). Not refreshed by `/api/load/game-data` reload | no | no |
| A6 | build gear `{name, tier}` | `aggregate_stats` (`stat_engine.py:724-736`) | affix **display name**; default `tier = 3` | stat field | — | — | midpoint (floored) | Unique-item synthetic `{stat_key,value}` path (`:728-731`) bypasses the bucket logic | no | no | no |
| A7 | `get_all_affixes()` (`AffixDefinition.to_dict`) | DB `affix_defs` (`cli.py:19-37,72-123`; `models/__init__.py:265-286`) | `name` (`seed` skips an existing name, `:85`, so first-wins per name); `reseed-affixes` inserts all | autoincrement int `id` | `affix_id` (numeric game id), slug `id`, and everything dropped at A2. **`class_requirement` always None, `tags` always `[]`** (REL-23) | `tier_ranges` dict `{"1":[lo,hi]}` | — | — | none (no version column) | none | none |
| A8 | DB `affix_defs` **or** JSON fallback (`ref.py:117-151`) | `/api/ref/affixes` (`ref.py:204-292`) | DB row or JSON record | `id` = str(DB autoinc) **or** slug (fallback) | `affix_id` in both branches; also level/modifier/group/etc. | `type` normalisation for experimental/personal (`:226-227`) | tiers rebuilt `int(k.lstrip("T"))` | `class` filter is a no-op on DB rows (REL-23), `tag` filter returns nothing on DB rows, but both work on the JSON fallback. Behaviour depends on whether the DB is seeded. Slot aliases `_SLOT_ALIASES` (`:37-67`) | no | no | no |
| A9 | `/api/ref/affixes` | Frontend `GearEditor` (`GearEditor.tsx:539-575`) | `name` | `{name, tier, sealed}` stored on build gear | `id` | max tier from `tiers` | — | `SLOT_TO_AFFIX_SLOT` (`:540-548`): `sword→sword_1h`, `axe→axe_1h`, `mace→mace_1h`, `two_handed_spear→spear`, `helmet→helm`, `body→chest`. 2-H sword/axe/mace and crossbow/fist affix pools are never requested | no | no | no |
| A10 | `affixes.json` (direct) | LE Tools importer `_AFFIX_MAP` (`lastepochtools_importer.py:178-196`) | `affix.get("affix_id") or affix.get("id")` | `str(affix_id)` key, **but `affix_id 0` is falsy, so it is keyed by slug `"void_penetration"`** | — | `affix_by_num` rebuilt per call (`:563-569`, `:1181-1183`) | tier = LE Tools varint guess 0–7 (`:520-531`), passed raw into gear; base unverified | **Last-wins** per id string (116 dups → idol-type copies / stale 417). Slot validation uses `_FORGE_SLOT_TO_AFFIX_TAGS` (`:442-465`) with weapon tags `sword/axe/two_handed_sword…` that never match `applicable_to` (`sword_1h/axe_2h…`), so weapons fall to the second pass "any slot" (`:588-592`) | no | no | no |
| A11 | `affixes.json` (direct) | `/api/admin/affixes` GET/PATCH (`admin.py:26-95`) | slug `id`, first match (`:79`) | — | — | — | **Writes the file in place** (allowlisted fields incl. `tiers`, `stat_key`) | — | no audit trail / provenance | none | none |
| A12 | `affixes.json` (direct) | `/api/load/game-data` integrity (`load.py:74-76`; `data_mapper.py:124-170`) | `id or affix_id or name` | `<id>_t<tier>` AffixModel | most fields | — | none | — | `VersionedLoader` probes `_version`/`_meta.version` → none present | no | no |

#### 1.3 Hop table: P4 (experimental Forge-safe / v2)

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | U `docs/generated/forge_safe_affix_bundle.json` (hard-coded `D:\Forge\…`, `backend/scripts/report_v2_affix_bundle.py:22-23`) | `F/docs/generated/v2_affix_bundle.json` (1098 recs, 615 equipment + 483 idol) | source affix id | `canonical_id "affix:equipment:<id>"` | **`extraRolls`** (grep 0) | `modifier_references[]` (property_path), `consumer_safe_fields`, `support_status: partial`, `stable_calculable: false` | none; `value_scale: "source_units"` kept | REL-7: `v2_modifier_registry.json` gives second-property rows the **primary** range (366/384 rows wrong, audit 06 §REL-7) | `source_bundle_path`, `schema_version`, `generated_on`; per-record `provenance` | `metadata.production_safe: false`, `trust_level generated_from_game_data` | not stamped with build |
| B2 | `FORGE_SAFE_AFFIX_EXPORT_PATH` JSON | `ForgeSafeAffixLoader` → `ForgeSafeAffixRepository` (`forge_safe_affixes_loader.py:44-155`; repo `:44-77`) | `affix_id` (dups rejected, `:127-133`) | `str(affix_id)` | — | — | none | — | `source_path`, `summary`, `export_policy` kept | record `safety.forge_safe` required; top-level `production_safe:true` rejected | not checked |
| B3 | repo or legacy registry | `AffixCatalogService` → `/api/affixes/catalog*` (`affix_catalog_service.py:55-170`; `routes/affixes.py`) | `affix_id` string, or legacy: `affix_id` else name (`:134-144`); legacy `get_affix` matches `id` or `affix_id`, first-wins over the name-deduped `registry.all()` (`:79-81`) | — | legacy mode returns only id/name/source_type/item_types | `data_source` | — | — | `data_source`, `mode`, `production_consumer:false` | flag-gated, defaults `shadow` → legacy | no |

#### 1.4 Hop table: P5 (frontend hard-coded)

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | hand-written literal | `AFFIX_DEFINITIONS` (`gameData.ts:536-643`) | display name | name | n/a (33 invented affixes) | — | 5 tiers; **T1 = best** (`gameData.ts:313-316,521-523`), the reverse of backend "1 = lowest" (`stat_engine.py:610`) and of data tiers 1..8 ascending | Slot vocab `"Helm","Chest","Wand",…` (capitalised); `Endurance` mapped to `max_health` | none | none | none |
| C2 | `AFFIX_DEFINITIONS` | `simulation.ts:189-196`, `getAffixValue` (`gameData.ts:648-653`) | `name` `.find` (first-wins) | stat_key | — | `Math.round` midpoint | — | — | — | — | — |

#### 1.5 Canonical replacement available (`U/exports_canonical/affixes.json`)

`_meta`: `schema r1_canonical_affix/1`; `builder tools/scripts/build_canonical_affixes.py`; `identity_contract: "affix_id is identity; names are presentation and may be empty or repeated."`; `roll_mapping_contract: "tiers[].rolls[property_index=0] = tier minRoll/maxRoll; property_index=i+1 = tier extraRolls[i]."`; `value_scale_contract: "All roll values are the raw serialized floats, unscaled. No x100 …"`; `source{raw_sha256, game_assembly_sha256, unity_version, tool_versions}`; `counts{affixes 1112, multi_property 534, single_property 578, property_rows 1646, tiers 5907, rolls 9332, property_sign_corrections 28, by_special_affix_type{Standard 766, Experimental 12, Personal 26, Set 59, IdolEnchantment 49, IdolWeaver 66, UNKNOWN(6) 134}}`; `enums.label_sources` per field (GAME_ENUM vs HAND_CODED_LEGACY); `anomalies []`.

Record fields: `affix_id`, `names{name, display_name, title, loot_filter_override_name}`, `type{name,raw,decode}`, `structure SINGLE_PROPERTY|MULTI_PROPERTY`, `source{list}`, `properties[]{index, property{name,raw}, modifier_type{name,raw}, tags{names,raw}, special_tag, extra_tag, set_property, mod_display_name, origin}`, `tiers[]{tier, rolls[]{property_index, min, max}}`, `can_roll_on[]{name, raw (= baseTypeID)}`, `class_specificity{names,raw}`, `rolls_on`, `special_affix_type`, `t6_compatibility`, `display_category`, `group`, `morphology`, `title_type`, `weapon_effect`, `level_requirement`, `weighting`, `specific_reroll_chances`, `unique_id`, `affix_id_to_convert_to`, `convert_on_incompatible_item_type`, `standard_affix_effect_modifier`, `maximum_affix_effect_modifier_for_t6`, `shard_*`, `value_scale: "SOURCE_UNSCALED"`. 0 duplicate `affix_id` (idol duplicates are folded in).

| Forge field (data/items/affixes.json) | Canonical replacement |
|---|---|
| `affix_id` / `id` slug / `idol_<id>` | `affix_id` (sole identity; removes the 116 duplicates and the slug/name keying) |
| `name`, `title` | `names.name`, `names.display_name`, `names.title` (presentation only) |
| `type` prefix/suffix/idol | `type.name` + `rolls_on.name` |
| `applicable_to` (Forge slot slugs) | `can_roll_on[].raw` = game `baseTypeID` (joins `items.json` / `BASE_TYPE_ID_TO_ITEM_TYPE_ID` without the slot-vocabulary layer) |
| `tags` (lowercased; empty for multi-property) | `properties[i].tags.names/raw` per property |
| `class_requirement` (string) | `class_specificity.names/raw` |
| `modifier_type` (empty for 535 records) | `properties[i].modifier_type` per property |
| `stat_key` (slug for 1113) | `properties[i].property{name,raw}` + `property_definitions.json` (no direct BuildStats mapping, which still has to be authored) |
| `tiers[{tier,min,max}]` ×100, property 0 only | `tiers[].rolls[{property_index,min,max}]` unscaled, all properties (fixes REL-7 and the ×100 heuristic) |
| `special_affix_type` 0/1 | `special_affix_type{name,raw}` (6 values + UNKNOWN(6)) |
| `t6_compatible`, `reroll_chance`, `level_requirement`, `group` | `t6_compatibility`, `weighting`, `level_requirement`, `group` |
| (absent) | `specific_reroll_chances`, `affix_id_to_convert_to`, `display_category`, `weapon_effect`, effect modifiers |
| (no provenance) | `_meta.source` hashes + TRUST_MANIFEST family `exports_canonical/affixes.json` (QUARANTINED) |

---

### 2. BASE ITEMS and ITEM TYPES / baseTypeID maps

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | `U/exports_json/items.json` | `data/items/items.json` (`sync_items`, `sync_game_data.py:1222-1247`) | `baseTypeID`, `(baseTypeID, subTypeID)` | same | **`_meta`, `_extra`** (game_build stamp lost) | key rename `nonEquippable → non_equippable` | none | none | **lost** | none | lost |
| D2 | (none, hand-curated) | `data/items/base_items.json`: dict keyed by slot `helmet, body, gloves, boots, belt, amulet, ring, relic, sword, axe, mace, dagger, sceptre, wand, staff, bow, quiver, shield, catalyst, two_handed_spear`; 115 named bases `{name, level_req, min_fp, max_fp, armor, implicit (text), tags}` | — | `name` within slot list; **no baseTypeID/subTypeID** (`bundle_item_diff.py:297` notes this) | — | — | invented FP/armor/implicit text | 1-H/2-H collapsed (`sword`), no crossbow/fist/idols | none | none | none |
| D3 | `base_items.json` | `base_engine` (`base_engine.py:32-110`) | slot key **or** lowercase name | dict | — | `_name_cache` (last-wins by lowercase name, `:46-50`) | — | Slot key → returns **first item** of list (`:64-68`) | — | — | — |
| D4 | `base_engine` | `/api/ref/base-items` (`ref.py:389-427`) | `?slot=` → `_SLOT_CATEGORIES` (`:509-522`) or `_normalize_slot` | list | — | — | — | `_normalize_slot("helmet")` → `["helm"]`, which is **not** a base_items key; falls through to `get_bases_for_slot("helmet")` (`:414-415`). `body` passes. Weapon category uses `sword/axe/mace/two_handed_spear` (matches base_items, not uniques) | no | no | no |
| D5 | `base_engine.get_base(item_type)` | `item_engine.create_item` (`item_engine.py:55-100`) → `craft_service.create_session` (`craft_service.py:180-215`) | `item_type.lower()` must be a base_items slot key | item dict | base `min_fp/max_fp` **unused**: FP comes from `forging_potential_ranges.json` by rarity (`item_engine.py:22-53`) | `implicit` text, `armor` | — | — | — | — | — |
| D6 | `base_items.json` | LE Tools `_BASE_ITEM_MAP` (`lastepochtools_importer.py:109-131`) | **sequential flattened index** (`idx` over slot dicts, `:120-125`) | int | — | `_slot` | — | **IMP-4**: a game `baseTypeID` int is looked up as this index (`:1080-1093`). Example: baseTypeID 1 (BODY_ARMOR) → index 1 = helmet "Iron Helm" | — | — | — |
| D7 | `data/items/items.json` | LE Tools `_ITEM_SUBTYPE_MAP` (`:139-176`) | `(baseTypeID, subTypeID)` | `displayName` | everything else | `_BASE_TYPE_TO_SLOT` (built, never read) | — | Varint candidate scan (`:381-423`) tries `varints[1]` then any 0–200 value. The importer itself says decoded names are unreliable (`:1104-1108`) | — | — | — |
| D8 | `data/items/item_types.json` (hand-curated, 25 entries; `id helm/chest/...`, `slot head/body/feet/...`) + `data/items/items.json` | `backend/scripts/generate_item_constants.py` → `backend/src/constants/*.ts` (BASE_TYPE_ID_TO_ITEM_TYPE_ID, itemTypeIds, itemTypeToSlot, gameTypeToItemTypeId, equipmentSlots) and hand-mirrored Python `backend/app/constants/*.py` | `baseTypeID` | ItemTypeId slug | 1-H/2-H distinction (`axe` for 5 and 12, `sword` for 9 and 16, `polearm` for 14), `IDOL_1x1_ETERRA`/`LAGON` both `idol_1x1`; non-equipment 34–39 omitted | `ITEM_TYPE_TO_SLOT` (`head/body/feet/...`) | — | — | none | none | none |
| D9 | Python `BASE_TYPE_ID_TO_ITEM_TYPE_ID` etc. | diagnostics only: `bundle_item_adapter_report.py:327-336`, `bundle_item_type_context_report.py:41-54`, `le_tools_import_context_report.py:10,207`, `bundle_item_diff.py:199-209` | baseTypeID | slug | — | — | — | — | — | — | — |
| D10 | TS constants | frontend via `@constants` alias (`frontend/tsconfig.json:26-27`, `vite.config.ts:34`) | — | — | — | — | — | Only `BASE_CLASSES`, `CLASS_MASTERIES`, `ITEM_RARITIES` and the `EquipmentSlot` type are imported (`gameData.ts:18`, `CraftSimulatorPage.tsx:27`, `types/index.ts:76`). `getItemSlotByBaseTypeId` (`backend/src/utils/getItemSlot.ts`) has no consumer. `SUBTYPE_ID_TO_ITEM_TYPE_ID` is empty in both TS and Python | — | — | — |
| D11 | `cli._ITEM_TYPES` literal (`cli.py:39-70`) | DB `item_types` → `/api/ref/item-types` (`ref.py:176-201`, plus its own static fallback list `:186-196`) | `name` | autoinc id | — | `base_implicit` text | — | Third and fourth item-type lists (`Polearm`, `Idol_1X1`; fallback omits Relic/Quiver/Catalyst/idols) | none | none | none |

---

### 3. IMPLICITS

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | (hand-curated; **no sync function**) | `data/items/implicit_stats.json` keyed by slot `helmet, body, gloves, boots, belt, ring(null), amulet(null), relic(null), wand, staff, sceptre, sword, axe, mace, dagger, shield, bow, quiver, focus` → `{stat, values{min,max}, description}` | slot slug | slot slug | upstream `items.json subTypes[].implicits[]` (per-subtype property/modifierType/value/maxValue) **not used** | — | invented ranges | One implicit per slot, not per base | none | none | none |
| E2 | `implicit_stats.json` | `pipeline._load_optional("implicit_stats")` (`pipeline.py:121`) → `game_data_loader.get_implicit_stat/get_all_implicit_stats` (`:221-226`) → `/api/ref/implicit-stats[/<item_type>]` (`ref.py:486-501`) | slot | — | — | — | — | **Not consumed by any calculation.** `Item.implicit_stats` (`domain/item.py:135,168-171`) comes from the build gear dict. Frontend reads it only in debug pages (`BackendDebugDashboard.tsx:35`) | — | — | — |
| E3 | `base_items.json[].implicit` (text) / `uniques.json[].implicit` (text) | `item_engine.create_item` `item["implicit"]` (`item_engine.py:96`) / `build_analysis_service._extract_unique_affixes` (`:111-114`) | — | — | — | regex stat_key | `_midpoint` of text range | `;`-split text lines → one stat per line, first regex wins (`:124-127`) | — | — | — |

---

### 4. UNIQUES and SETS

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | `U/exports_json/uniques.json uniques[409]` | `data/items/uniques.json` (`sync_uniques`, `sync_game_data.py:899-987`) | numeric `id`; merge **by `_slugify(displayName or name)`** (`:940`) | **slug key** (no numeric id kept, 0/403 records have `id`) | **`id`, `subTypes`, structured `mods[]` (property/tags/modifierType/value/maxValue/rollId), `resolvedBaseItem` (baseTypeID/subTypeID), `resolvedImplicitMods`**, `displayName` vs `name` distinction | `slot` via `_convert_slot(baseType)` (`:943`), `unique_effects` from tooltip text, `legendary_type`, `effective_level_for_lp`, `can_drop_randomly`, `reroll_chance` | `_format_tooltip_text` (`:872-896`): `[lo,hi,step]` → "lo–hi"; values with \|x\| < 1 are ×100 and rounded | `base`, `implicit`, `affixes` (text), `tags` **preserved from previous curated file** (`:955-959`), never refreshed from export mods. Slug collisions overwrite (`out[slug]`, `:968`); old `_2/_3` keys preserved unrefreshed (`:975-977`) | `_meta` preserved from old file (claims "Auto-generated from exports_json") | none | none |
| F2 | `U/exports_json/uniques.json setItems[59]` + `set_bonuses.json` | `data/items/set_items.json` (`sync_set_items`, `:990-1110`) | `setId`; item merged by slug of displayName (`:1044`) | slug key + `sets{str(setId)}` | `id`, `mods[]`, subTypes, resolved base | `set_id`, `set` name, `sets[].items` (slug list), `bonuses[{pieces_required,text,alt_text}]` | tooltip formatting | `base/affixes/tags` preserved from curated file. File has 47 items vs 59 upstream | `_meta` stale (`set_count 18, total_items 47`) | none | none |
| F3 | `uniques.json` | `pipeline._load_optional("uniques")` (`pipeline.py:117`) → `get_all_uniques/get_unique_by_id` (`game_data_loader.py:194-206`) | slug | `{"id": slug, …}` | — | — | — | — | — | — | — |
| F4 | `get_all_uniques` | `/api/ref/uniques`, `/api/ref/uniques/<slug>` (`ref.py:525-570`) | `?slot=`, `?q=` | list | — | — | — | `_SLOT_CATEGORIES["weapon"]` = `sword, axe, mace, dagger, sceptre, wand, staff, bow, two_handed_spear` (`:510-513`) vs unique slots `sword_1h/sword_2h/axe_1h/axe_2h/mace_1h/mace_2h/spear`, so **78 weapon uniques are unreachable** via `?slot=weapon`. Idol category lists 4 sizes | — | — | — |
| F5 | `/api/ref/uniques` | Frontend `GearEditor`/`ItemPicker`/`UniqueItemPicker` (`GearEditor.tsx:24-26,263,735`; `ItemPicker.tsx:21-45,72`) | slot (`sword`, `two_handed_spear`, …) | build gear `{slot, item_name: <unique display name>, rarity:"legendary", affixes: []}` (`GearEditor.tsx:735`) | slug | — | — | Unique is persisted **by display name** | — | — | — |
| F6 | build gear `item_name` | `build_analysis_service` (`:170-185`) → `_extract_unique_affixes` (`:100-129`) → `aggregate_stats` synthetic path | **name, first match** (`next(... u.get("name") == item_name)`, `:183`) | `{stat_key, value}` | all non-regex-matched lines, `unique_effects` | regex `_UNIQUE_STAT_PATTERNS` (`:22-84`) | `_midpoint` of "lo–hi" text (`:89-97`). Text values were previously ×100'd by `_format_tooltip_text` for fractions | One stat per line, first pattern wins | — | — | — |
| F7 | `uniques.json` | LE Tools `_UNIQUE_ITEMS` / `_UNIQUE_BY_BASE` (`lastepochtools_importer.py:201-279`) | `(forge_slot, base name lower)` | unique **name** | — | — | — | `_UNIQUE_SLOT_TO_FORGE` (`:201-213`) maps to `helmet/body_armour/weapon/off_hand/idol_altar`; `_resolve_unique_name` returns **`matches[0]`** (`:282-297`) among uniques sharing a base. `item_name = f"{unique} ({base})"` (`:1133`), which then fails the exact-name lookup in F6 | — | — | — |
| F8 | `U/.../uniques.json` (`D:\Forge\…` default) | `docs/generated/v2_unique_bundle.json`, `v2_set_bundle.json` (`backend/scripts/report_v2_unique_set_bundles.py:21-22`) → `V2UniqueSetRepository` → `/api/experimental` | upstream id | canonical id | — | provenance `source_path` required (`item_repository.py:202`) | — | — | yes (per record) | experimental | — |

---

### 5. CRAFTING RULES / FP RANGES / RARITIES / TAGS / SLOT VOCABULARIES

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | hand-curated `data/items/crafting_rules.json` (`fp_costs{add/upgrade/seal/unseal/remove}`, `base_item_fp{helmet, body, sword, …, default}`) | `fp_engine.load_fp_rules` (`fp_engine.py:27-41`) → `roll_fp_cost`, `fp_cost_range`; `craft_engine.FP_COSTS` (`craft_engine.py:54-59`, mean); `/api/ref/crafting-rules` (`ref.py:382-386`) | action name | — | — | integer mean | `int((min+max)/2)` | `base_item_fp` only read by `roll_base_fp` (`fp_engine.py:83-88`), which has **no callers** | none | none | none |
| G2 | `crafting_rules.json` | `pipeline` path `_PATHS["crafting_rules"]` (`pipeline.py:55`) | — | — | **never loaded** (no `load_all` entry, no property) | — | — | `efficiency_scorer._get_avg_fp_cost` checks `hasattr(pipeline, "crafting_rules")` → False → hard-coded 4 (`efficiency_scorer.py:82-97`) | — | — | — |
| G3 | crafting_rules mirror | Frontend `CraftSimulatorPage.FP_COST_RANGES` (`:47-55`), `lib/crafting.ts:22-26` (`TARGET_TIER = 5`, FP_COSTS literal) | — | — | — | — | — | Hand-copied. Backend `TARGET_TIER = 4` (`constants/crafting.py`), `MAX_PREFIXES/SUFFIXES = 2` vs `constants.json` max 3 (`craft_engine.py:168-169`), `optimal_path_search` caps tier at 5 (`craft_engine.py:263`) although data has 8 tiers | — | — | — |
| G4 | hand-curated `forging_potential_ranges.json` | `fp_engine.load_fp_ranges` (`:174-191`) → `item_engine.resolve_fp_for_item` → craft sessions; `/api/ref/fp-ranges` | rarity lowercase | (min,max) | — | — | — | Authoritative FP for crafting | none | none | none |
| G5 | hand-curated `rarities.json` (min_fp/max_fp per rarity, **different**: rare 20–50 vs 20–40, exalted 35–55 vs 40–60) | pipeline (`:119`) → `/api/ref/rarities` (`ref.py:478-483`) | `id` | — | — | — | — | Display only (debug pages). `ITEM_RARITIES` constant (`constants/item_rarities.py`) is a fifth list used by schema validation (`schemas/__init__.py:18-27`) | none | none | none |
| G6 | hand-curated `data/items/tags.json` | **no reader** in backend/frontend/scripts | — | — | — | — | — | Affix tags in data are lowercased export AT tags. tags.json is unused | — | — | — |

#### Slot vocabularies (identity of "where an item/affix goes")

| Vocabulary | Values (examples) | Defined at | Consumers |
|---|---|---|---|
| V1 game enum | `HELMET, BODY_ARMOR, ONE_HANDED_SWORD, TWO_HANDED_SPEAR, IDOL_1x1_ETERRA`; numeric baseTypeID 0–39 | U exports, canonical `can_roll_on[].raw` | sync `SLOT_MAP` input; TS/Py `GAME_TYPE_TO_ITEM_TYPE_ID` |
| V2 affix/unique slot | `helm, chest, sword_1h, sword_2h, axe_1h, mace_2h, spear, idol_1x4, idol_1x1_eterra, idol` | `sync_game_data.py:88-114,145-148` | `affixes.json applicable_to`, `uniques.json slot`, `set_items.json slot`, `AffixRegistry._by_slot_type` |
| V3 base-items slot | `helmet, body, sword, axe, mace, two_handed_spear, focus` | `base_items.json`, `implicit_stats.json`, `crafting_rules.base_item_fp` keys | `base_engine`, `item_engine`, craft sessions; `ref._SLOT_CATEGORIES`; frontend `GearEditor/ItemPicker` slot names; `validators.VALID_SLOTS` (`validators.py:54-61`, plus `idol_small/large/grand/stout`) |
| V4 item-type / equipment slot | itemTypeId `helm, chest, axe, sword, polearm, idol_1x1`; slot `head, body, feet, hands, neck, finger, waist, weapon, offhand` | `item_types.json`; `backend/src/constants/*.ts`; `backend/app/constants/*.py`; `domain/equipment_set.VALID_EQUIPMENT_SLOTS` (`:27-33`) | diagnostics, `EquipmentSet` |
| V5 importer slot | `helmet, body_armour, weapon1, weapon2, off_hand, ring_1, idol_altar` | `lastepochtools_importer.py:53-65,201-213,358-371,442-465,1028-1043` | imported build gear |
| V6 frontend AFFIX_DEFINITIONS | `"Helm","Chest","Wand","Ring"` (capitalised) | `gameData.ts:536-643`; `BuildPlannerPage.tsx:78-89` `slotType` | frontend quick sim |
| Bridges | `ref._SLOT_ALIASES` V3/V4→V2 (`ref.py:37-54`); `GearEditor.SLOT_TO_AFFIX_SLOT` V3→V2 (`:540-548`); `gear_upgrade_ranker._SLOT_ALIASES` V2→V3 (**reverse direction**: `helm→helmet`, `chest→body`, `ring→ring1`, `gear_upgrade_ranker.py:43-53`). For `body`, neither `body` nor `body` matches `chest`, so there are no candidates. | | |

---

### 6. Every module reading item JSON directly (file I/O, not via pipeline)

| File:line | Reads | Notes |
|---|---|---|
| `backend/app/game_data/pipeline.py:45-55` | affixes, uniques, rarities, implicit_stats (loaded); base_items, crafting_rules (declared, never loaded) | canonical loader |
| `backend/app/engines/affix_engine.py:30-35,51-54` | `data/items/affixes.json` | fallback when no app context |
| `backend/app/engines/base_engine.py:32,39-51` | `data/items/base_items.json` | sole base reader for craft/ref |
| `backend/app/engines/fp_engine.py:27,174` | `crafting_rules.json`, `forging_potential_ranges.json` | |
| `backend/app/routes/ref.py:126` | `data/items/affixes.json` | `/api/ref/affixes` JSON fallback |
| `backend/app/routes/admin.py:26-39` | `data/items/affixes.json` (read **and write**) | |
| `backend/app/routes/load.py:74` | `items/affixes.json` via `RawDataLoader` | integrity counts |
| `backend/data/versioning/versioned_loader.py:22` | `items/affixes.json` | version probe |
| `backend/data/mappers/data_mapper.py:79-170` | base_items / affixes bundles | |
| `backend/app/services/importers/lastepochtools_importer.py:117,154,186,228` | base_items.json, items.json, affixes.json, uniques.json | |
| `backend/app/services/forge_safe_affix_comparison_service.py:163` | `data/items/affixes.json` | diagnostic |
| `backend/app/game_data/bundle_item_adapter_report.py:323`, `bundle_item_diff.py:179-180` | item_types.json, base_items.json | diagnostics |
| `backend/app/utils/cli.py:385-394` (`validate-data`) | all item files (shape only) | |
| `backend/scripts/generate_item_constants.py:13,22`; `generate_subtype_map.py:18` | item_types.json, items.json | codegen |
| `backend/scripts/report_v2_*`, `compare/inspect_forge_safe_affixes.py` | `D:\Forge\last-epoch-data\exports_json\*.json` hard-coded defaults | v2 bundle generation |
| `scripts/sync_game_data.py:167,915,923,1004,1023,1228,1461` | upstream exports + current `data/items/*` | writer |
| Frontend | **none** (no JSON copies of item data). All item data arrives via `/api/ref/*`, except the hand-coded `AFFIX_DEFINITIONS` and FP tables | |

---

### 7. Legacy authorities (files/constants acting as an authoritative item source)

| Authority | Path | What it is | Readers |
|---|---|---|---|
| Synced+curated affix table | `data/items/affixes.json` (1228 recs, ×100 tiers, slug ids, 116 dup affix_ids, 98 dup names) | Primary affix truth for production | P1, P2, P3 (see §1, §6) |
| Hand-curated base items | `data/items/base_items.json` (115 bases, 20 slot keys, no game ids) | Base list, FP, armour, implicit text | `base_engine`, `item_engine`, `/api/ref/base-items`, frontend `ItemPicker` (`:209`), LE Tools `_BASE_ITEM_MAP` (by index) |
| Raw base types | `data/items/items.json` (synced, `_meta` stripped) | baseTypeID/subTypeID names | LE Tools subtype map; codegen |
| Hand-curated implicits | `data/items/implicit_stats.json` | one implicit per slot | `/api/ref/implicit-stats` only |
| Hand-curated item types | `data/items/item_types.json` | 25 type ids + slot | codegen, diagnostics |
| Uniques (sync + curated text) | `data/items/uniques.json` (403 slug keys) | unique metadata; stats only as text | `/api/ref/uniques`, `build_analysis_service`, LE Tools |
| Sets | `data/items/set_items.json` | 47 items + `sets` | **no runtime reader found** (only sync writes it) |
| FP by rarity | `data/items/forging_potential_ranges.json` | craft FP truth | `fp_engine`, `/api/ref/fp-ranges` |
| FP costs | `data/items/crafting_rules.json` | action costs | `fp_engine`, craft_engine, `/api/ref/crafting-rules` |
| Rarities | `data/items/rarities.json` | rarity metadata with **conflicting FP** | `/api/ref/rarities` |
| Tags | `data/items/tags.json` | tag vocabulary | none |
| baseTypeID maps | `backend/src/constants/BASE_TYPE_ID_TO_ITEM_TYPE_ID.ts`, `gameTypeToItemTypeId.ts`, `itemTypeIds.ts`, `itemTypeToSlot.ts`, `equipmentSlots.ts`, `subTypeIdToItemTypeId.ts` (empty); Python mirrors in `backend/app/constants/*.py` | 1-H/2-H collapsing type map | diagnostics; frontend type-only |
| Importer maps | `lastepochtools_importer.py` `_EQUIP_SLOT_MAP :53`, `_UNIQUE_SLOT_TO_FORGE :201`, `_SLOT_TO_BASE_TYPE_IDS :358`, `_FORGE_SLOT_TO_AFFIX_TAGS :442`, `_LET_SLOT_ALIASES :1028`, `_RARITY_MAP :1016` | hard-coded LE Tools ↔ Forge | importer |
| DB seeds | `cli._ITEM_TYPES :39-70`; DB `affix_defs` (REL-23 lossy) | DB authority for `/api/ref/affixes`, `/api/ref/item-types` | ref routes |
| Static fallbacks | `ref.get_item_types` fallback list `:186-196`; `ref._SLOT_ALIASES :37`; `ref._SLOT_CATEGORIES :510-522` | | ref routes |
| x100 correction | `stat_engine._FLAT_SCALE_STAT_KEYS :592-606` + `get_affix_value :609-631` | heuristic value authority | `aggregate_stats` |
| Unique stat regexes | `build_analysis_service._UNIQUE_STAT_PATTERNS :22-84` | text→stat authority | `analyze_build` |
| Slot validators | `validators.VALID_SLOTS :54-61`; `equipment_set.VALID_EQUIPMENT_SLOTS :27-33`; `gear_upgrade_ranker._SLOT_ALIASES :43` | | |
| Frontend affixes | `frontend/src/lib/gameData.ts:536-643` `AFFIX_DEFINITIONS` (33 invented, T1=best) | frontend sim | `simulation.ts`, `GearSlotEditor.tsx`, `BuildPlannerPage.tsx` |
| Frontend FP/craft | `CraftSimulatorPage.tsx:47-55`, `lib/crafting.ts:22-26` | copied FP costs/target tier | craft UI |
| Experimental | `docs/generated/v2_*_bundle.json`, `FORGE_SAFE_AFFIX_EXPORT_PATH`, `FORGE_SAFE_AFFIX_BUNDLE_PATH` | flagged non-production | `/api/affixes/catalog`, `/api/experimental` |

---

### 8. Identity hazards (name / slug / index / first-match / last-match)

| # | Location | Mechanism | Effect |
|---|---|---|---|
| H1 | `sync_game_data.py:181-186,196` | existing affix matched **by name** to inherit slug/stat_key/tags | 98 duplicate names → wrong slug/stat_key inheritance possible |
| H2 | `sync_game_data.py:284-289` | slug collision → `<slug>_<numeric>` | id depends on file order |
| H3 | `sync_game_data.py:306-315` | legacy records preserved by name | stale `affix_id 417` duplicate (index 1227) |
| H4 | `sync_game_data.py:208-230` + equipment loop | idol list re-emits ids already emitted from equipment | 115 duplicate `affix_id`s (`idol_<id>` vs slug) |
| H5 | `pipeline.py:163-171` (`affix_tier_midpoints`, `affix_stat_keys`) | dict by **name**, last-wins | 124 records shadowed; 96 of 98 dup-name groups differ in tiers, 97 in stat_key |
| H6 | `affix_registry.py:63-67,104-106` | `_by_name`, `_by_id` last-wins; `all()` name-deduped | `get_by_id(826..940)` → `type:"idol"` copy (`applicable_to ["idol"]`, often zero tiers); `get_by_id(417)` → stale record; `all()` hides 124 affixes from catalog/optimizer/seeding consumers |
| H7 | `game_data_loader.py:83-88`; `affix_catalog_service.py:79-81`; `affix_engine.py:107-118`; `admin.py:79` | **first-match** loops | resolves differently from H6 for the same id |
| H8 | `stat_engine.py:493,619` | affix resolved by **display name** | gear stored by name inherits H5 |
| H9 | `lastepochtools_importer.py:190` | `affix.get("affix_id") or affix.get("id")` | affix_id 0 (Void Penetration) keyed by slug; dict last-wins per id |
| H10 | `lastepochtools_importer.py:120-125,1080-1093` | **baseTypeID looked up as sequential index** into flattened base_items (IMP-4) | wrong base names (baseTypeID 1 → "Iron Helm") |
| H11 | `lastepochtools_importer.py:398-423,300-353` | varint candidate scan, first hit wins | unreliable subtype/unique resolution |
| H12 | `lastepochtools_importer.py:282-297` | `_resolve_unique_name` → `matches[0]` | multiple uniques per base, first wins |
| H13 | `lastepochtools_importer.py:442-465,576-592` | weapon slot tags never match `applicable_to` | weapon affix id ambiguity resolved by "any slot" pass |
| H14 | `sync_game_data.py:940,968` | uniques keyed by **slug of displayName/name** | upstream dup names "Scales of Eterra", "Pearls of the Swine" overwrite one slug; `_2/_3` keys are stale carry-overs |
| H15 | `build_analysis_service.py:183` | unique resolved by **name, first match** | dup-name uniques; LE Tools `"X (Base)"` names never match |
| H16 | `base_engine.py:46-50,64-68` | name cache last-wins; slot key → first item | `create_item("helmet")` always uses "Rusted Coif" metadata |
| H17 | `cli.py:85` | `seed` skips existing **name** | first record per dup name only; `reseed-affixes` inserts all → DB content depends on which command ran |
| H18 | `ref.py:142,283` | API `id` = slug (fallback) or DB autoinc int | `affix_id` never reaches frontend; ids are unstable across reseeds |
| H19 | `GearEditor.tsx:735,752`; `ItemPicker` | gear persisted by `item_name`; affixes by `name` | all downstream joins are name joins |
| H20 | `gameData.ts:649`; `simulation.ts:193`; `GearSlotEditor.tsx:121` | frontend `.find(d => d.name === …)` over hand-coded table | separate identity universe |
| H21 | `craft_engine.py:176-183,195,214,222,423,427,453,507,527` | affix by name; `getattr(def, "type")` on `AffixDefinition` (field is `affix_type`) → None | prefix/suffix caps not enforced in `apply_craft_action`; `add_affix`/`unseal_affix` index `affix["type"]` on a dataclass |
| H22 | `affix_engine.py:44-54,72-75` | `registry.all()` (dataclasses) treated as dicts (`a["type"]`) | `get_affixes_by_type` breaks inside app context |
| H23 | tier semantics | data tiers 1..8 ascending; `stat_engine` "1=lowest"; frontend "T1 = best" (`gameData.ts:313-316,521`); LE Tools tier guess 0–7 (`:520-531`); default tier 3 (`stat_engine.py:735`) | the same `tier` integer means different things on different paths |

---

### 9. Provenance / trust / patch identity: summary

- **Provenance**: lost at the first hop for every family. `sync_affixes` drops `_meta`. `sync_items` drops `_meta/_extra`. `sync_uniques/set_items` keep the **old** curated `_meta`. `pipeline._detect_version` returns `"unknown"` for the list-shaped affixes file (`pipeline.py:466-470`). `AffixDefinition.data_version` and `AffixRegistry.data_version` are both `"unknown"`. `/api/version` `data_version` is the `DATA_VERSION` env default `"1.0.0"` (`config.py:42`, `version.py:64`). `/health` `patch_version` reads `data/version.json` `patch`/`patch_version`, which is `"unknown"` (`health.py:37-46`).
- **Trust**: `_upstream_trust()` (`sync_game_data.py:38-62`) copies only `exports_json/*` families into `version.json.upstream_trust`, so `exports_canonical/*` families are excluded. `_write_upstream_trust_copy()` (`:65-69`) writes `data/upstream_trust_manifest.json`. **No runtime code reads either.** Grep finds only `backend/tests/test_r1_sync_trust_contract.py`. Neither artefact exists in the current `data/`. Upstream marks every item family QUARANTINED / `trusted_calculation_eligible: false`, yet every production path (stat engine, craft, importer, API) consumes it unlabelled.
- **Patch identity**: `metadata.json` provides `1.4.6 / build 22986002`. Only `version.json.patch_version` would carry it, and it currently says `"unknown"`. No record, DB row (`affix_defs` has no version column) or API response carries patch/build. `Build.patch_version` defaults to `"1.2.1"` (`models/__init__.py:107`) and is unrelated to data.

## Part B — Character families (classes, masteries, passives, skills, skill trees, abilities, ailments, blessings, Weaver, enums/properties/localization)


Scope: `/home/user/le-the-forge` (Forge) consuming `/home/user/last-epoch-data` (upstream). The audit was read-only. Nothing was modified.
Counts and comparisons below were computed on 2026-10-06 against the working trees.

### 0. Key facts that frame every table

* **The sync cannot run as written.** `scripts/sync_game_data.py:21` sets `SRC_DIR = ROOT / "last-epoch-data" / "exports_json"`. That path is inside the Forge repo, and `/home/user/le-the-forge/last-epoch-data` does not exist. The upstream repo is a sibling directory. `scripts/generate_tree_data.py:25` has the same problem. The v2 report scripts default to `D:\Forge\last-epoch-data\...` (`backend/scripts/report_v2_passive_tree_bundle.py:21`, `report_v2_class_mastery_bundle.py:21`, `report_v2_skill_tree_bundle.py:21`).
* **The committed `data/` files are not the output of the current sync code. They come from an older, different snapshot:**
  * `data/classes/passives.json` has 541 nodes. Upstream `exports_json/passive_trees.json` (1.4.6) has 535. The Forge has 6 extra Acolyte/Warlock nodes: `ac_86`, `ac_88`, `ac_97`, `ac_98`, `ac_101`, `ac_103`. Canonical lists these as 6 `missing_nodes` (decode failures).
  * Each node carries a `requires: [{parent_id, points}]` field, and `connections` is a *symmetric* adjacency list (400/400 edge refs are bidirectional). The current `sync_passives` emits neither: it emits only directed `connections` from `requirements` and no `requires`. No writer of `requires`/`parent_id` exists anywhere in `scripts/` or `backend/app` (`passive_tree_validator.py` mentions a "0E-2 merge script", which is not in the repo). Last data commit: `e2c64eb` (2026-04-21).
  * `data/classes/skills_with_trees.json`, `community_skill_trees.json` and `unmatched_trees.json` are not byte-equal to the current upstream (184/184, 140 vs 138, 27 vs list).
  * `data/classes/classes.json` uses an older flat schema (`baseHealth`, `baseMana`…, Mage has `_fallback`, there is no `abilities`). Current upstream nests `stats{}` and adds `abilities`/`startingItems`.
  * `data/progression/blessings.json` is **hand-authored** (10 timelines → nested `blessings[]` with `stat_key`, `normal_min/max`, `grand_min/max`, `simulation_relevant`). `sync_blessings` would overwrite it with a flat 224-row list. `pipeline.load_all` (`backend/app/game_data/pipeline.py:132-140`) expects the nested shape, so after a sync, `blessings_flat` would silently become empty.
  * `data/progression/weaver_tree.json` (77 nodes) is sourced from **LastEpochTools (LET) window.LEWeaverTree, game 1.4.2** per its own `_schema._comment`. No sync function exists for it.
  * `data/version.json` → `patch_version: "unknown"`, `files_updated: ["data\\items\\affixes.json"]` only. There is no `upstream_trust` key and no `data/upstream_trust_manifest.json`, so the trust-carry code (`sync_game_data.py:38-86`, commit `6bdb436`) has never been run against the current data.
* **The upstream trust manifest** (`exports_canonical/TRUST_MANIFEST.json`, patch 1.4.6 build 22986002) marks **every** character-side family `QUARANTINED`, `trusted_calculation_eligible: false`. That covers `exports_json/{classes,passive_trees,skills,skills_with_trees,community_skill_trees,blessings,ailments}.json`, every `localization/*`, and `exports_canonical/{passive_trees,skill_trees,weaver_tree,property_definitions}.json`. None of this trust state reaches any Forge runtime consumer.
* **The Forge has two parallel worlds:**
  1. **Production (legacy):** `data/` JSON → DB/pipeline → `/api/passives`, `/api/skills/...`, `/api/ref/...` → stat/combat engines; plus frontend TS copies.
  2. **Experimental v2** (`/api/experimental/v2/{classes,masteries,passives,skills}`): bundles in `docs/generated/v2_*_bundle.json`, built from `exports_json` (not `exports_canonical`) by `backend/scripts/report_v2_*`. Every response says `production_consumer: False`. v2 joins mastery **by `masteryName`** and is correct: its 535 nodes give the right owner_mastery_id for all 15 masteries.

---

### 1. CLASSES

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch identity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | `exports_json/classes.json` `classes[]` (id 0-4, `treeID` pr-1/mg-1/kn-1/ac-1/rg-1, `masteries[]` positional, `_meta.game_build`) | `sync_classes` `scripts/sync_game_data.py:1147-1168` → `data/classes/classes.json` | numeric class id + name | same list (passthrough of `raw["classes"]`, `:1160`) | `_meta` (game_build, gameAssemblySha256, source_pathid) | none | none (verbatim) | mastery order preserved positionally | lost (`_meta` dropped) | lost | lost. Committed file is an older schema and does not match the current sync output. |
| C2 | `data/classes/classes.json` | `base_importer._load_game_data` `backend/app/services/importers/base_importer.py:30-48` | class `name` | `_VALID_CLASSES` set; `_VALID_MASTERIES[name] = [m.name for m in masteries]` | numeric ids, treeID, stats | n/a | none | **Index 0 (the base-class name, e.g. "Acolyte") is accepted as a valid mastery** | none | none | none |
| C3 | (hand) `backend/app/game_data/classes.json` (`base_stats`, `mastery_bonuses`, `mastery_per_point`, `keystone_bonuses`, `attribute_scaling`) | `GameDataPipeline._load_classes` `pipeline.py:260-269` → `game_data_loader.get_class_base_stats/get_mastery_bonuses/get_keystone_bonuses/get_attribute_scaling` (`game_data_loader.py:95-117`) | class/mastery/keystone **display name** | dict | n/a | n/a | n/a | n/a | hand-authored, no source | none | none |
| C3a | — | No caller of the `get_*` accessors outside `game_data_loader.py` (grep) | | | | | | | **Dead registry.** The engine uses duplicated literals instead (C4). | | |
| C4 | (hand) `backend/app/engines/stat_engine.py:226-262` `CLASS_BASE_STATS`, `:264-273` `MASTERY_BONUSES`, `:275-297` `KEYSTONE_BONUSES`, `ATTRIBUTE_SCALING`, `CORE_STAT_CYCLE`/`CLASS_STAT_CYCLES` `:333+` | `aggregate_stats` `stat_engine.py:680-732` | class name / build.mastery string / node **name** | `BuildStats` | — | synthetic mastery bonuses (e.g. Paladin +200 HP; Lich +8 ward per allocated node; Forge Guard +15 armour per node, `:703-706`) | `pts_used = len(allocated_node_ids)` | keystone bonus keyed by node **name**. `node_type=="keystone"` never occurs (passives.json has only core/notable), so KEYSTONE_BONUSES is unreachable via DB nodes. Modulo fallback `cycle[node_id % len]` (`:569`) invents stats when passive_stats is empty. | "VERIFIED in-game" comment only | none | none |
| C5 | (hand) `frontend/src/lib/gameData.ts:329-345` `CLASS_BASE_STATS` (health 340-520, base_damage) | `frontend/src/lib/simulation.ts:17-25,174-181` | class name | FE BuildStats | — | per-point Lich/Forge Guard bonuses `simulation.ts:179-181` | — | — | header cites fandom/maxroll/"patch 1.2.x" `gameData.ts:1-15` | none | 1.2.x claim. **Contradicts** backend C4 (110 HP for all classes). |
| C6 | (hand) `backend/app/routes/ref.py:74-115` `CLASS_META` (color, masteries, 5 skills) | `GET /api/ref/classes` `ref.py:170-173`, `/api/ref/skills` `:354-380` | class name | JSON | — | — | — | own mastery order (see §M) | none | none | none |
| C7 | (hand) `backend/app/constants/classes.py:11-17` and `backend/src/constants/classes.ts:1-22` (`BASE_CLASSES`, `CLASS_MASTERIES`) | `routes/passives.py:40-44` VALID_*; FE via the `@constants` alias (`frontend/vite.config.ts:34`, `tsconfig.json:27`) → `lib/gameData.ts:18,36` `MASTERIES`; `services/buildApi.ts:62-70` duplicate | class/mastery name | arrays | — | `[0]` is used as the default mastery | — | display order ≠ game order (§M) | none | none | none |
| C8 | `exports_json/classes.json` | `backend/scripts/report_v2_class_mastery_bundle.py:48-70` → `docs/generated/v2_class_mastery_bundle.json` → `V2ClassMasteryRepository` → `/api/experimental/v2/classes`, `/v2/masteries` (`routes/experimental.py:691-768`) | class id + `masteries[index]` | `class:<slug>`, `mastery:<class>:<slug>`; `source_mastery_index`, `source_mastery_id = localizationKey` (`:347-377`) | index-0 entry skipped (base) | canonical ids, provenance block, `patch_version` | none | mastery index retained as `source_mastery_index` | **kept** (`source_file`, `source_metadata`) | `TrustLevel.GENERATED_FROM_GAME_DATA`, `stable_calculable False` | from `_meta` |

### 2. MASTERIES (see also §M, Mastery consumers)

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | `exports_json/passive_trees.json` node `mastery` (int 0-3) + **`masteryName`** (string, correct) + tree `masteryNames[]` | `sync_passives` `sync_game_data.py:432-579` | `(class, mastery int)` | `mastery` (name) + `mastery_index` | **`masteryName` and `masteryNames` ignored** | `mastery_name = MASTERY_MAP[cls].get(mastery_idx)` `:502` using the hard-coded `MASTERY_MAP` `:363-369` | — | **mastery by index through a wrong table**: 190/535 current nodes mislabelled (Mage idx2/3 swapped, Primalist idx1/2 swapped, Sentinel idx1/3 swapped) | lost | lost | lost |
| M2 | `data/classes/passives.json` (committed, 541 nodes) | — | — | `mastery` label | — | — | — | Same 190 mislabels present (Mage 62, Primalist 65, Sentinel 63). Verified against upstream `masteryName`. | | | |
| M3 | build `mastery` string from LET/Maxroll | importers `_MASTERY_MAP[class][chosenMastery]` `lastepochtools_importer.py:44-50,830,869`, `maxroll_importer.py:214-229,892,1236`, `routes/import_route.py:55-61,206` | external planner mastery int (1-3) | display name | — | default `.get(1)` when missing (`maxroll:1236`, `LET:946`) | — | **index table here is CORRECT** (matches classes.json), so it disagrees with sync `MASTERY_MAP` | none | none | none |
| M4 | build.mastery string | `stat_engine.MASTERY_BONUSES` (C4), FE `MASTERY_BONUSES` `gameData.ts:346-358`, `validators.VALID_MASTERIES` `engines/validators.py:67-73,246-252`, `routes/passives.py` VALID_MASTERIES | name | — | — | — | — | name-keyed | — | — | — |

### 3. PASSIVES

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | `exports_json/passive_trees.json` (`passiveTrees[]{class,treeId,masteryNames,nodes[]}`; node keys: id,name,description,loreText,altText,nodeDescription,maxPoints,mastery,masteryRequirement,pointBonusDescription,noScalingType,noScalingPointThreshold,stats[statName,value,noScaling,downside,property,tags,overrideSprite],requirements[nodeId,requirement],effectHints[],masteryName) | `sync_passives` `sync_game_data.py:432-579` → `data/classes/passives.json` | `(class, raw node id int)` | `"{prefix}_{raw}"` (prefix ac/mg/pr/rg/sn `:372-378`); collision form `"{prefix}_m{idx}_{raw}"` `:492-495` (0 collisions in current data) | loreText, altText, nodeDescription, pointBonusDescription, noScaling*, **stats.property (numeric property id)**, stats.tags, noScaling/downside/overrideSprite flags, **effectHints (+extractionConfidence)**, masteryName/masteryNames, treeId, `meta` | `node_type = "core" if maxPoints>1 else "notable"` `:546` (structural classification invented); `mastery` via MASTERY_MAP; x/y/icon **from `frontend/src/data/raw/char-tree-layout.json`** `_build_layout_lookup :390-429` because the export has no `transform`/`icon`; `ability_granted` from absent key `abilityGrantedByNode` → always null | stats → `{key: statName, value: string}` `:518-521` (value stays text such as "+9%"; docstring says `statNameKey`) | `requirements[{nodeId,requirement}]` → `connections: [ids]`, **dropping the `requirement` points** `:506-515`; collision branch `next(n for n in all_nodes if id==...)` `:511` picks the first match regardless of mastery; legacy garbage refs (`nodeId 0, requirement 208`, `nodeId 1684808296038400`) would become edges to `ac_0`/bogus ids (canonical: 48 NULL_REFERENCE, 16 IMPLAUSIBLE, 3 UNRESOLVED in 19 nodes) | lost | lost | lost |
| P1' | (unknown "0E-2 merge script") | committed `data/classes/passives.json` | | adds `requires:[{parent_id,points}]` (directed), symmetric `connections` | | | | 25 nodes' `requires` ≠ upstream requirements; 22 point mismatches; 6 phantom Warlock nodes | none | none | none |
| P2 | `data/classes/passives.json` | `flask seed-passives` `backend/app/utils/cli.py:183-270` → table `passive_nodes` (`models/__init__.py:289-323`) | string id | PK `id` String(16); `raw_node_id` Int | none beyond P1 | prunes rows not in JSON (`:260+`) | verbatim | stores `connections` (symmetric) and `requires` ("OR-of-parents" per model comment `:311-314`) | none | none | none |
| P3 | `passive_nodes` (fallback: `passives.json` read directly `routes/passives.py:24-35`, `routes/ref.py:154-167`) | `GET /api/passives`, `/api/passives/<class>`, `/api/passives/<class>/<mastery>` `routes/passives.py:101-176`; `GET /api/ref/passives` `ref.py:301-351` | `?class=`, `?mastery=` **name** | `{nodes, grouped{mastery name or __base__}}` | ref.py drops stats/requires/raw_node_id | `grouped` keyed by mislabelled mastery | — | `?mastery=Runemaster` returns **Spellblade** nodes + base, and so on (filter on mislabelled `mastery` column `:160-167`) | none | none | none |
| P4 | API P3 | FE `services/passiveTreeService.ts:69-80` → `components/features/build/BuildPassiveTree.tsx:87-120` (tabs = `["__base__", ...CLASS_MASTERIES[cls]]`, sections by `node.mastery`), `pages/PassiveTreePage.tsx`, `components/PassiveTree/PassiveTreeRenderer.tsx:185-188` (legend label from `n.mastery`, color from `mastery_index`), `PassiveTreeGraph.tsx:162-174` (tooltips keyed by `raw_node_id`) | string id + raw_node_id | `Map<raw_node_id, node>` | | | | tab "Runemaster" shows Spellblade nodes; legend names wrong while colors are right | | | |
| P5 | API P3 nodes | FE `logic/validatePassiveBuild.ts:20-60` (MAX_PASSIVE_POINTS 113, MASTERY_UNLOCK_THRESHOLD 20, mastery points by `node.mastery === masteryName`) | string id | validity | | | | **"one mastery" and per-mastery point checks use the mislabelled names** | | | |
| P6 | build.passive_tree (list of raw **ints**, repeated per point; importers `lastepochtools_importer.py:881-887`, `maxroll_importer.py:929-950`) | `routes/builds.py:137-169` `_validate_passive_tree` (create only) | int or str | — | — | — | — | **int ids are skipped**, so imported builds are not validated. There is no prerequisite, mastery or budget check, and PATCH is not validated. `game_data/passive_tree_validator.validate_allocation` (AND-of-parents, `:63-104`) is used only by tests. | | | |
| P7 | build.passive_tree ints | `services/build_analysis_service.py:159-201` | `raw_node_id` per class | `raw_id_to_str[nid]` → string ids | **points (repeats) collapse**: `PassiveNode.id.in_(ids)` `passive_stat_resolver.py:370` dedups, so each node is applied once regardless of points | | | | | | |
| P8 | `passive_nodes.stats` `{key,value}` | `services/passive_stat_resolver.py:350-416` | stat display **name** (`statName`) | `STAT_KEY_MAP[name]` → BuildStats field `:57+` (39.2% coverage per header) | unmapped → special_effects | composite fan-out | regex `_VALUE_RE` on text | — | — | — | — |
| P9 | P8 output | `stat_engine.aggregate_stats` `:739-741`; `routes/simulate.py:104,299` (string ids direct); `engines/optimization_engine.py:34-60,577`; `engines/gear_upgrade_ranker.py:292,350`; `engines/stat_resolution_pipeline.py:322-333` | | BuildStats | | modulo fallback when additive is empty `stat_engine.py:716-724` | | | | | |
| P10 | (hand/third-party) `frontend/src/data/raw/char-tree-layout.json` (LET-style, keyed pr-1/mg-1/kn-1/ac-1/rg-1, `rect[x,y,w,h]`) | consumed by **backend sync** P1 for x/y/icon and by `scripts/diagnose_icons.py`, `extract_images.py` | `(treeID, nodeId)` | x,y,icon | w,h | | | | none | none | none |
| P11 | (no generator in repo; header "Auto-generated by merge script") `frontend/src/data/passiveTrees/index.ts` (541 nodes, `{id,x,y,type,name,regionId,maxPoints,parentId,description,iconId}`) | `PassiveTreeGraph.tsx:146-200`, `PassiveProgressBar.tsx:13` | `(class lower, regionId slug, raw id)` | same | stats, requirement points, multiple parents | `type` = "notable" for all 541; description = flattened stats text for many | `scripts/generate_tree_data.py:81-173` patches only **names/descriptions in place** by regex from `exports_json/passive_trees.json` `(class, id)` | **single `parentId`** (25 nodes inconsistent with upstream requirements; 24 upstream nodes have >1 prerequisite) | none | none | none. 64 names differ from 1.4.6. |
| P12 | (no generator; "generated from char-tree-metadata.json") `frontend/src/data/passiveTrees/edges.ts` `PASSIVE_TREE_META[class][rawId] = {parentIds[], masteryRequirement, region}` | `PassiveTreeGraph.tsx:5,148,188-200,268-277,625` | `(class, raw id)` | edges, lock rules | requirement points | `SECONDARY_MASTERY_DEPTH = 20` (`PassiveTreeGraph.tsx:27`) | | multi-parent kept here, but 25 nodes ≠ upstream | none | none | none |
| P13 | `frontend/src/data/raw/char-tree-metadata.json` (LET `characterTree version 12`, loc keys `Skills.Skill_pr-1_0_Name`, stats with property/tags/sprite) | **no runtime consumer** (comment in edges.ts only) | | | | | | | third-party | none | none |
| P14 | `exports_json/passive_trees.json` + `data/classes/passives.json` (layout via `ac_23`-style id) | `backend/scripts/report_v2_passive_tree_bundle.py:51-90,337-374` → `docs/generated/v2_passive_tree_bundle.json` → `/api/experimental/v2/passives*` | `(treeId, node id)` | `passive_node:ac_1:23` | — | `owner_mastery_id` from **`masteryName`** joined to the class bundle (`:343-344`) → correct | | `connections`, `edge_requirements` | kept (`source_path`, `layout_provenance`) | `generated_from_game_data`, `planner_consumed:false` | `generated_on 2026-05-12` |

### 4. SKILLS

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `exports_json/skills.json` (184 skills, 184 unique ids, **161 unique names**; `class` is null for all) | `sync_skills_metadata` `sync_game_data.py:321-356` → `data/classes/skills_metadata.json` | skill id (tree code, e.g. `an0my`) | **dict keyed by display name** `:339` (last row wins) | 23 ids lost to name collisions; tags/tagsDecoded, mana, timing, altText, levelScaling, attributeScaling, meta | `class: ""` | — | **name-keyed collapse (REL-6)**. For 11 of the 12 duplicate names the surviving id is a tree-less variant: Anomaly→an0mz, Armblade Slash→abs2, Cinder Strike→cinss, Dancing Strikes→dacn37, Death Seal→ds34i, Evade→werebearevade1, Human Form→wbthf, Rampage→ch2ge, Rive→sndr1-, Teleport→fl45, Umbral Blades→na28. Only Gathering Storm→ga2st has a tree. | lost | lost | lost |
| S1' | committed `skills_metadata.json` (161 + `_schema`) | | | | | hand-added `base_damage_min/max`, `damage_scaling_stat`, `attack_type` (all null, "0G-1") that sync would erase | | **Contains corrupted names absent upstream:** `Frigid Tempest`=fi9 (upstream Fireball), `Create Shadow`=en6 (Elemental Nova), `Shocking Impact`=me27 (Meteor), `Reap`=rf1azz (Reaper Form), `Familiar Rage`=fs11, `Spirit Thorns`=tb47. **`Fireball`, `Meteor`, `Elemental Nova` and `Reaper Form` are missing.** | none | none | none |
| S2 | `skills_metadata.json` | `GameDataPipeline._load_skills_metadata` `pipeline.py:275-319` → `get_skill_metadata(name)` `game_data_loader.py:125-155` | name | name | `_`-prefixed keys | validates 0G fields | — | name-keyed | — | — | — |
| S3 | `skills_metadata.json` | `base_importer` `_VALID_SKILL_IDS` `base_importer.py:52-61`; LET `_get_skill_id_map` `lastepochtools_importer.py:87-106`; Maxroll `_get_skill_id_map` `maxroll_importer.py:48-73` | id | `{id: name}` | collapsed ids | | | LET tree id `an0my`, `cstri`, `dacn33`, `ds34l`, `te44`, `ub5d9`, `sndr1` are **not in map**, so skill_name falls back to the raw tree code (`LET :900-903`). `fi9` maps to "Frigid Tempest". | | | |
| S4 | `skills_with_trees.json` entries with `hasTree` | Maxroll `_get_skill_tree_id_map` `maxroll_importer.py:76-121`, reverse `name_to_tree_id` `:966-968` | tree id | name | non-hasTree rows | | | name→tree via reverse dict (hasTree names unique, 137) | | | |
| S5 | (hand) `backend/app/game_data/skills.json` (179 skills: base_damage, level_scaling, attack_speed, scaling_stats, is_spell, mana_cost) | `pipeline._load_skills` `:250-258` → `SkillRegistry` `domain/registries/skill_registry.py:31-61` (`app/__init__.py:145`) | display name | `SkillStatDef` | — | — | — | name-keyed; includes the corrupted names (Frigid Tempest, Create Shadow, …) and 20 names absent upstream | none | none | none |
| S6 | S5 + (hand) `combat_engine.SKILL_STATS` `engines/combat_engine.py:56+` | `_get_skill_def(name)` `combat_engine.py:292-307` → `calculate_dps` `:337,482,626`; `optimization_engine._normalize_skill_name` `:65-90` (`.title()`, so "Mark for Death"→"Mark For Death") | name | def | | | | lossy case normalization | | | |
| S7 | (hand) FE `lib/gameData.ts:52-240` `CLASS_SKILLS` (with **per-skill mastery**), `:405+` `SKILL_STATS` | BuildPlannerPage, simulation.ts | name | | | | | mastery-to-skill by hand | fandom/maxroll | none | "1.2.x" |
| S8 | (hand) `ref.py` `CLASS_META[*].skills` + SkillRegistry names | `/api/ref/skills` `ref.py:354-380` | name | | | "Other" bucket | | | | | |
| S9 | `exports_json/skills_with_trees.json` | v2 `report_v2_skill_tree_bundle.py` → `v2_skill_bundle.json`, `v2_skill_tree_bundle.json` → `/api/experimental/v2/skills*` | id | `skill:…`, `skill_tree:…` | | | | | kept | generated | kept |

### 5. SKILL TREES

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value transforms | Relationship transforms | Provenance | Trust | Patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `exports_json/skills_with_trees.json` | `sync_skills_with_trees` `sync_game_data.py:1298-1320` → `data/classes/skills_with_trees.json` | skill id | same | `meta` | — | verbatim | — | lost | lost | lost. The committed copy differs from upstream and carries corrupted names (S1'). |
| T2 | `exports_json/community_skill_trees.json` (meta.source = **github prowner/last-epoch-data, "may not reflect current patch"**) | `sync_community_skill_trees` `:1171-1192` → `data/classes/community_skill_trees.json` (140 trees, 4,360 nodes) | tree id | same | meta (incl. community-source note) | | | | lost | lost | lost |
| T3 | `exports_json/unmatched_trees.json` | `sync_unmatched_trees` `:1323-1346` → `data/classes/unmatched_trees.json` (27) | id | same | | | | | | | **No runtime consumer** |
| T4 | **unknown generator** (no producer in repo; oldest commit `cf675f7`) | `data/classes/skill_tree_nodes.json` (132 trees, **2,190 nodes**) | tree code key | `{skill_name (lowercase), nodes[{id,name,type,maxPoints,description}]}` | requirements/edges, mastery, stats[] (property, tags), icons | `description = "<prose> \| Stat +X; Stat +Y (downside)"` (structured stats **flattened to text**) | — | **no edges at all** | none | none | none. Coverage: swt with trees 137 / 3,875 nodes; canonical 137 / 3,936. 131 trees have fewer nodes than swt. Missing trees: dqv5, fs11, is58, md26kh, tb47. `skill_name` is a raw code for 7 trees (an0my, f1b4d, cstri, htsk5, fl44, sh4re, bl5st), so a name lookup misses them. |
| T5 | `skill_tree_nodes.json` | `services/skill_tree_resolver.py:150-168` `get_tree_for_skill(name)` (case-insensitive scan, first match) → `resolve_skill_tree_stats` `:297-381`, `extract_damage_conversions` `:440+` | **skill display name** | node by int id | prose before `\|` → special_effects | `_STAT_LABEL_MAP` `:55-140` label→field; scale = points `:251` | regex-parse text values; `_parse_value` uses `.rstrip("(downside)")` (a char-set strip) `:179` | name→tree | — | — | — |
| T6 | build skill `spec_tree` ints (repeated per point) | `build_analysis_service.py:189-210` (Counter → `{node_id, points}`), **primary skill only** (`sorted_skills[0]`) | int | | other 4 skills ignored | | | | | | |
| T7 | `community_skill_trees.json` | `routes/skills.py:41-67` `_load_trees` keyed by `id`; `GET /api/skills/<skill_id>/tree` `:181-216`; allocate `:284+`; reachability `_is_reachable_from_root` `:74-137` (**AND of all requirements**, `max(req,1)`); `_skill_name_to_id` `:256-275` (match `ability` e.g. "RogueMultishot" or `nodes[0].name`, else `name.lower().replace(" ","_")`) | tree id / name | | | | | name→tree-id heuristic | none | none | none |
| T8 | (no generator; "Auto-generated by merge script") `frontend/src/data/skillTrees/index.ts` (133 trees, 3,863 nodes, `{id,x,y,type,name,maxPoints,parentId,iconId,description}`) + `SKILL_NAME_TO_CODE` (132 names) | `getSkillTree`/`getSkillCode`/`hasSkillTree`/`resolveSkillName`/`getEntryIconId` `skillTrees/index.ts:4296-4335` → `SkillSelector.tsx:23,83,113,116`, `SkillTreePanel.tsx:15,82`, `SkillTreeDraftPanel.tsx:18,71`, `SkillTreeGraph.tsx:4`, `BuildPlannerPage.tsx:34,1409` | lower-case **name** → code; or code | node by int | stats, multiple prerequisites, requirement points | `type: "mastery-gate"` for root | `generate_tree_data.py:180-305` rewrites `SKILL_NAME_TO_CODE` (from swt name→id, last wins) and loc-key names in place | **single `parentId` (REL-10)**: 683 FE nodes have >1 upstream prerequisite (canonical: 680). Name→code points at **tree-less** variants for `anomaly→an0mz` and `cinder strike→cinss` (no FE tree under that code). `resolveSkillName` uses `nodes[0].name`. | none | none | 4 trees missing (md26kh, fs11, tb47, is58). 54 trees differ in node count from swt. |
| T9 | `frontend/src/data/raw/skill-tree-layout.json`, `skill-tree-metadata.json` | only `backend/scripts/report_v2_skill_tree_bundle.py:22` (layout) | | | | | | | third-party | | |

### 6. ABILITIES

| Hop | From | To | Notes |
|---|---|---|---|
| A1 | `exports_json/classes.json` `abilities{defaultPathIds,knownPathIds,unlockable[{abilityPathId,level}]}`, `masteries[].masteryAbilityPathId` | — | **Not in the committed `data/classes/classes.json`** (old schema). There is no consumer. Path ids are numeric Unity PPtr ids with no resolver to skill tree codes. |
| A2 | `exports_json/passive_trees.json` (no `abilityGrantedByNode` key) | `sync_passives:524` → `ability_granted` | Always null (0/541). Canonical has `ability_granted_by_node` on 37 nodes (e.g. "263446"). FE shows "Grants:" (`PassiveTreeRenderer.tsx:442`, `PassiveTreeGraph.tsx:609`, `PassiveTreeCanvas.tsx:94`), which is dead in practice. |
| A3 | `data/localization/ability_strings.json` | — | No runtime consumer (only `sync_localization` and `r1_forge_consumption_inventory.py`). |

### 7. AILMENTS

| Hop | From | To | Notes |
|---|---|---|---|
| L1 | `exports_json/ailments.json` (typetree, game_build stamped) | `sync_ailments` `sync_game_data.py:653-711` → `data/combat/ailments.json` (id, slug, …) | `_meta.game_build` dropped. |
| L2 | `data/combat/ailments.json` | **no reader** in backend/frontend (grep) | Confirms CALC-3. Engines use hand constants: `backend/app/constants/combat.py:21-28` (`IGNITE_BASE_DPS 40`, `IGNITE_DURATION 3.0`, `BLEED_BASE_DPS 43`, `BLEED_DURATION 4.0`, POISON_…), consumed by `domain/ailments.py`, `ailment_scaling.py`, `ailment_stacking.py`, `fight_simulator.py`, `combat/combat_simulator.py`. |

### 8. BLESSINGS

| Hop | From | To | Input identity | Output identity | Dropped | Derived | Value | Relationship | Prov | Trust | Patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | `exports_json/blessings.json` (224, `name`="27" internal, displayName, subTypeID, implicits[property,tags,modifierType,value,maxValue]) | `sync_blessings` `sync_game_data.py:583-650` | internal name | `id = _slugify(displayName)` `:632` | itemTags, subClassRequirement, specialTag, `_extra` | `tier = subTypeID` | none (raw floats kept) | flat list | lost | lost | lost |
| B1' | (hand) committed `data/progression/blessings.json` (10 timelines × nested 112 blessings; `stat_key`, `stat_type`, `normal/grand min/max`, `simulation_relevant` 38 true) | `pipeline.load_all` `:127-140` flattens to `blessings_flat{id}` | slug id | | | | | **Shape incompatible with B1**: after a sync, `blessings_flat` = {} | none | none | none |
| B2 | `blessings_flat` | `get_blessing_by_id` `game_data_loader.py:238-240` → `stat_resolution_pipeline.resolve_blessing_stats` `:160-215` → `stat_engine.aggregate_stats` `:743-756`; `GET /api/ref/blessings` `ref.py:577-580` (nested list) | slug | `{stat_key,value,stat_type}` | | value default = normal_max/grand_max | | | | | |

### 9. WEAVER

| Hop | From | To | Notes |
|---|---|---|---|
| W1 | LET `window.LEWeaverTree` (1.4.2, payload v10) + LET i18n | committed `data/progression/weaver_tree.json` (77 nodes, `wv_<raw>`, symmetric connections derived from requirements) | No sync function. Provenance only in `_schema._comment`. |
| W2 | `weaver_tree.json` | `pipeline._load_weaver_tree` `:321-352` (validated) → `get_weaver_tree_nodes/node` `game_data_loader.py:158-171` | **No caller** anywhere (backend/frontend grep). |
| W3 | `exports_canonical/weaver_tree.json` (77 nodes, DEFECTIVE, 18 field-shift suspects, 148 RESOLVED reqs) | — | Not consumed. |

### 10. ENUMS / PROPERTIES / LOCALIZATION

| Hop | From | To | Notes |
|---|---|---|---|
| E1 | `exports_json/localization/*.json` (20 files) | `sync_localization` `sync_game_data.py:1376-1412` → `data/localization/*` (verbatim) | **No runtime reader** (grep for `localization/`, `ability_strings`, `skill_tree_strings`, `property_strings`, `id_lookup`, `en.json` hits only scripts). |
| E2 | node `stats[].property` (numeric) | dropped at P1 `:518-521` | All passive stat semantics are re-derived from **display name** strings (`passive_stat_resolver.STAT_KEY_MAP`, FE mirror `frontend/src/constants/passiveStatMap.ts` "MIRRORS backend") and skill-tree label text (`skill_tree_resolver._STAT_LABEL_MAP`). |
| E3 | `exports_canonical/property_definitions.json` (families master/player/ability/conditional/tracker/idol_altar/tree_stat_name_table, `reference_encodings.tree_stat_bands`) | v2 normalization only (`backend/app/normalization/v2/*`, experimental) | Not used by production engines. |

### 11. Canonical replacements vs current Forge use

**`exports_canonical/passive_trees.json`** (`schema r1_canonical_tree/1`, builder `tools/scripts/build_canonical_trees.py`)
* Identity contract: "node identity = (tree_class, node_id); path_id kept; names are presentation". Trees: `tree_class` (AcolyteTree/KnightTree/MageTree/PrimalistTree/RogueTree), `tree_id` (ac-1/kn-1/mg-1/pr-1/rg-1), `tree_path_id`, `declared_node_count`, `node_count`, `missing_nodes[]` (6 Acolyte decode failures), `integrity_status` (**all 5 DEFECTIVE**), `integrity_problems`, `requirement_resolution` (RESOLVED 187, NULL_REFERENCE 48, IMPLAUSIBLE_REFERENCE 16, UNRESOLVED_REFERENCE 3).
* Node: `node_id`, `path_id`, `tree_path_id`, `name`, `description`, `node_description`, `alt_text`, `lore_text`, `point_bonus_description`, `max_points`, **`mastery` (int only)**, `mastery_requirement`, `no_scaling_type`, `no_scaling_point_threshold`, `ability_granted_by_node` (37 non-null), `decode_suspect`, `field_shift_suspect`, `requirements[{node_id, node_path_id, points_required, resolution}]` (multiple, with points), `stats[{stat_name, value_text, downside, no_scaling, override_sprite, property{raw, namespace, index, band, status (RESOLVED 1149 / UNKNOWN_PROPERTY_TYPE 257), target}, tags{raw, names, decode}}]`.
* Not present: x/y/icon (still needs a layout source), numeric `nodeStats` ("not decoded by current walker"), mastery **name**, and build provenance ("ABSENT … cannot be proven to come from 1.4.6"; decoder `LEGACY_HEURISTIC (EXT-12)`).
* **Mastery identity per node:** integer index only. The name is obtained by joining `tree_id` ↔ `exports_json/classes.json` `classes[].treeID` and then `masteries[node.mastery].name`. Verified: 0/535 mismatches against legacy `masteryName`. classes.json has **no numeric mastery id**. Masteries are identified by position in `masteries[]` (0 = base class), `localizationKey` (`Mastery_Beastmaster`) and `masteryAbilityPathId` (e.g. 264437). Classes use numeric `id` 0-4 (Primalist 0, Mage 1, Sentinel 2, Acolyte 3, Rogue 4, matching importer `_CLASS_MAP`).
* Versus the Forge: the Forge uses none of this. It drops property ids, requirement points, multi-prereq resolution status, ability grants and integrity flags. Mastery comes from the wrong index table. The tree is the older 541-node snapshot including 6 nodes canonical cannot decode.

**`exports_canonical/skill_trees.json`**: 137 trees / 3,936 nodes, **all DEFECTIVE** (mostly "1 node with text fields shifted (EXT-12)"; 167 field-shift-suspect nodes, 5 missing), requirement_resolution RESOLVED 4,465 / NULL 7 / UNRESOLVED 4, stat property RESOLVED 4,512 / UNKNOWN_PROPERTY_TYPE 1,872 (namespaces such as `AilmentID` band 10000-15000, `SP`). `tree_id` equals legacy skill/tree code (fi9, ab0lh…) and `tree_class` (FireballSkillTree). There is no skill-id or ability linkage field, so skill→tree must join on `tree_id`. Versus the Forge: the Forge uses `skill_tree_nodes.json` (2,190 nodes, text-flattened stats, no edges, name-keyed) for calculation, and FE single-parentId trees for UI.

**`exports_canonical/weaver_tree.json`**: 1 tree (`weaver`/`WeaverTree`), 77 nodes, DEFECTIVE. The Forge uses the LET 1.4.2 copy, and nothing reads it.

---

### M. Mastery consumers

#### M.1 The 15 masteries: game index vs every code location's assumption

Game truth = `exports_json/classes.json` `classes[].masteries[i]` (i = 1..3; 0 = base). It is identical to `exports_json/passive_trees.json` `masteryNames` (verified for all 5 trees). There is no `masteryNames` key in classes.json itself; the `masteries[]` array plays that role.

Legend: number = index/position the location assumes; ✗ = disagrees with game index; "set" = order irrelevant.

| Class (id, tree) | Mastery | **Game idx** | sync `MASTERY_MAP` `sync_game_data.py:363-369` (index semantics) | What `data/passives.json` nodes labelled with this name actually are | importers `_MASTERY_MAP` (LET `:44-50`, Maxroll `:214-220`, import_route `:55-61`) | `generate_tree_data.MASTERY_REGION` `:31-37` | `CLASS_MASTERIES` pos+1 (py `constants/classes.py:11-17`, ts `backend/src/constants/classes.ts:13-19`, `buildApi.ts:62-68`; used as index by dead `getMasteryIndex` `BuildPassiveTree.tsx:69-73`) | `ref.py CLASS_META` pos `:74-115` | FE `PASSIVE_REGIONS` pos `gameData.ts:252-283` (y-band) | FE `PASSIVE_TREES` key pos `passiveTrees/index.ts:610-641` | `validators.VALID_MASTERIES` `:67-73` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Acolyte (3, ac-1) | Necromancer | 1 | 1 | Necromancer ✓ | 1 | 1 | 1 | 1 | 1 | 1 | set |
| Acolyte | Lich | 2 | 2 | Lich ✓ | 2 | 2 | 2 | 2 | 2 | 2 | set |
| Acolyte | Warlock | 3 | 3 | Warlock ✓ (+6 phantom nodes) | 3 | 3 | 3 | 3 | 3 | 3 | set |
| Mage (1, mg-1) | Sorcerer | 1 | 1 | Sorcerer ✓ | 1 | 1 | **2 ✗** | **2 ✗** | **2 ✗** | 1 | set |
| Mage | Spellblade | 2 | **3 ✗** | label "Spellblade" = **Runemaster** nodes (30) | 2 | 2 | **3 ✗** | **3 ✗** | **3 ✗** | 2 | set |
| Mage | Runemaster | 3 | **2 ✗** | label "Runemaster" = **Spellblade** nodes (32) | 3 | 3 | **1 ✗** | **1 ✗** | **1 ✗** | 3 | set |
| Primalist (0, pr-1) | Beastmaster | 1 | **2 ✗** | label "Beastmaster" = **Shaman** nodes (32) | 1 | 1 | 1 | **2 ✗** | **2 ✗** | 1 | set |
| Primalist | Shaman | 2 | **1 ✗** | label "Shaman" = **Beastmaster** nodes (33) | 2 | 2 | 2 | **3 ✗** | **3 ✗** | 2 | set |
| Primalist | Druid | 3 | 3 | Druid ✓ | 3 | 3 | 3 | **1 ✗** | **1 ✗** | 3 | set |
| Sentinel (2, kn-1) | Void Knight | 1 | **3 ✗** | label "Void Knight" = **Paladin** nodes (32) | 1 | 1 | **2 ✗** | **3 ✗** | **3 ✗** | 1 | set |
| Sentinel | Forge Guard | 2 | 2 | Forge Guard ✓ | 2 | 2 | **3 ✗** | **1 ✗** | **1 ✗** | 2 | set |
| Sentinel | Paladin | 3 | **1 ✗** | label "Paladin" = **Void Knight** nodes (31) | 3 | 3 | **1 ✗** | **2 ✗** | **2 ✗** | 3 | set |
| Rogue (4, rg-1) | Bladedancer | 1 | 1 | ✓ | 1 | 1 | 1 | 1 | 1 | 1 | set |
| Rogue | Marksman | 2 | 2 | ✓ | 2 | 2 | 2 | 2 | 2 | 2 | set |
| Rogue | Falconer | 3 | 3 | ✓ | 3 | 3 | 3 | 3 | 3 | 3 | set |

Mislabel total in `passives.json`: Mage 62 + Primalist 65 + Sentinel 63 = **190** (of 541 committed; the same 190 of 535 if re-synced today).

#### M.2 Every consumer of mastery identity / ordering

| # | Location | Construct | Key type | Effect |
|---|---|---|---|---|
| 1 | `scripts/sync_game_data.py:363-369` | `MASTERY_MAP` | class → {index → name} | **Root cause REL-1.** Writes the wrong `mastery` name per node (`:502`, `:567-568`). |
| 2 | `scripts/sync_game_data.py:568` | `mastery_index` | raw int | Correct index persisted alongside the wrong name, so the two fields disagree within a row. |
| 3 | `data/classes/passives.json` | `mastery`, `mastery_index` | name + int | Carries the 190 mislabels. |
| 4 | `backend/app/utils/cli.py:213-235` | seed `PassiveNode.mastery/mastery_index` | — | Persists the mislabels to the DB. |
| 5 | `backend/app/models/__init__.py:296-297` | `mastery` String(32), `mastery_index` SmallInt | — | Storage. |
| 6 | `backend/app/routes/passives.py:24-35,40-44,115-176` | `?mastery=` filter, `grouped` by `mastery`, `order_by(mastery_index)` | name | `/api/passives/Mage/Runemaster` returns Spellblade nodes. |
| 7 | `backend/app/routes/ref.py:154-167,301-351` | `/api/ref/passives?mastery=` | name | Same. |
| 8 | `backend/app/routes/ref.py:74-115` | `CLASS_META.masteries` | ordered list | Own order (Mage R,S,Sb; Primalist D,B,S; Sentinel FG,P,VK). |
| 9 | `backend/app/constants/classes.py:11-17` | `CLASS_MASTERIES` | ordered list | Validation (`routes/passives.py:43-44`). Order differs from game. |
| 10 | `backend/src/constants/classes.ts:13-19` | `CLASS_MASTERIES` (TS, imported by the FE via `@constants`) | ordered list | Drives FE tabs and defaults. |
| 11 | `frontend/src/lib/gameData.ts:36` | `MASTERIES = CLASS_MASTERIES` | — | Re-export. |
| 12 | `frontend/src/services/buildApi.ts:62-70` | duplicate `CLASS_MASTERIES`, `CLASSES` | ordered list | `SkillSelector.tsx:59-64` default = `[0]` (Mage→Runemaster, Sentinel→Paladin, Primalist→Beastmaster). |
| 13 | `frontend/src/components/features/build/BuildPlannerPage.tsx:377,878,968,1043,1047,1224` | `MASTERIES[cls][0]` default mastery; options | — | Default mastery = first in the display list. |
| 14 | `frontend/src/components/features/build/BuildPassiveTree.tsx:69-73,94-107` | `getMasteryIndex` = indexOf+1 (**dead**); tabs in CLASS_MASTERIES order; `groupBySection` by `node.mastery` | name | Tab "X" shows nodes mislabelled as X. |
| 15 | `frontend/src/components/PassiveTree/PassiveTreeControls.tsx:9,37` | `MASTERIES[selectedClass]` | — | Selector options. |
| 16 | `frontend/src/components/features/builds/BuildsPage.tsx:15,280` | `MASTERIES[filters.character_class]` | — | Filter options. |
| 17 | `frontend/src/pages/PassiveTreePage.tsx:21-22` | `MASTERIES`, `BASE_CLASSES` | — | Page selector. |
| 18 | `frontend/src/components/PassiveTree/PassiveTreeRenderer.tsx:18,185-188,265,290,403` | `PALETTE[mastery_index]`; legend `n.mastery` | index + name | Colors correct, legend names wrong. |
| 19 | `frontend/src/logic/validatePassiveBuild.ts:42-64` (+ rules below) | `node.mastery === masteryName` | name | Per-mastery point and "one mastery" rules evaluate the wrong nodes for 6 masteries. |
| 20 | `frontend/src/components/features/build/PassiveTreeGraph.tsx:37-54,151,209-214,268-277,625` | `REGION_LABEL` slug→name map; `chosenMasteryRegion = mastery.toLowerCase().replace(/\s+/g,'-')`; secondary-mastery depth 20 | slug from name | Uses `PASSIVE_TREES` regionIds, which are correct. This UI path is correct, so it disagrees with BuildPassiveTree. |
| 21 | `frontend/src/data/passiveTrees/index.ts:9-641` | `const _<CLASS>_<MASTERY>` blocks; `PASSIVE_TREES[class][slug]` | slug | Regions correct (0 mismatches vs `masteryName`). |
| 22 | `frontend/src/data/passiveTrees/edges.ts` | `region` per node | slug | Correct. |
| 23 | `frontend/src/lib/gameData.ts:243-283` | `PASSIVE_REGIONS` (id, label, y-band 0-0.28/…/1.0) | ordered list | Fourth ordering (by position). Consumers: none found by grep outside the file. |
| 24 | `scripts/generate_tree_data.py:31-37` | `MASTERY_REGION` (index→slug) | index | Correct but **unused** (declared only). |
| 25 | `backend/app/services/importers/lastepochtools_importer.py:44-50,830-832,869,946` | `_MASTERY_MAP[class][chosenMastery]`; default `.get(1)` | index | Correct. |
| 26 | `backend/app/services/importers/maxroll_importer.py:214-229,892-902,1236` | `_MASTERY_MAP`, `_MASTERY_TO_CLASS` (mastery-name-as-class fix-up) | index / name | Correct. |
| 27 | `backend/app/routes/import_route.py:55-61,206` | `_MASTERY_MAP` | index | Correct (third duplicate). |
| 28 | `backend/app/services/importers/base_importer.py:41-45,134-137` | `_VALID_MASTERIES` from `data/classes/classes.json` (incl. index 0 base name) | name | Accepts a class name as a mastery. |
| 29 | `backend/app/engines/validators.py:67-73,246-252` | `VALID_MASTERIES` sets | name | `MASTERY_MISMATCH`. |
| 30 | `backend/app/engines/stat_engine.py:264-273,698-706` | `MASTERY_BONUSES`, Lich/Forge Guard per-point | name | Invented bonuses. |
| 31 | `backend/app/game_data/classes.json` `mastery_bonuses`/`mastery_per_point` | name | Dead duplicate of #30. |
| 32 | `frontend/src/lib/gameData.ts:346-358`, `frontend/src/lib/simulation.ts:174-181` | FE `MASTERY_BONUSES`, Lich/Forge Guard/Paladin | name | FE duplicate of #30. |
| 33 | `frontend/src/lib/gameData.ts:52-240` | `CLASS_SKILLS[*].mastery` | name | Hand mastery→skill ownership. |
| 34 | `frontend/src/pages/classes/ClassesPage.tsx:28-48,154` | `MASTERY_COLORS` | name | Display only. |
| 35 | `frontend/src/data/presets.ts:29-102` | preset `mastery` names | name | Display/seed. |
| 36 | `backend/app/utils/cli.py:139-164,339-341` | sample builds "Bone Curse Lich", "Frozen Ruins Runemaster", "Manifest Armor Forge Guard" | name | Seed. |
| 37 | `backend/app/services/passive_stat_resolver.py:42-43,89` | comments only | — | — |
| 38 | `backend/scripts/report_v2_class_mastery_bundle.py:55-70,347-377`, `report_v2_passive_tree_bundle.py:337-374,476-490` | v2 masteries by `enumerate(masteries)` + `masteryName` join | index + name | Correct; experimental only. |
| 39 | `frontend/src/types/canonicalPassive.ts:7-30`, `canonicalClassMastery.ts:6-20`, `canonicalSkill.ts` | `owner_mastery_id`, `mastery_index`, `source_mastery_index` | canonical id | v2 debug pages only (`pages/debug/V2PassivesDebugPage.tsx`). |

---

### N. Every name-keyed or index-keyed skill / tree lookup

| # | Location | Key | Target | Hazard |
|---|---|---|---|---|
| 1 | `sync_game_data.py:336-345` | skill display name | `skills_metadata.json` | 184 → 161 collapse (last wins). |
| 2 | `pipeline.py:275-319`, `game_data_loader.py:125-155` `get_skill_metadata(name)` | name | metadata | Fireball/Meteor/Elemental Nova/Reaper Form absent. |
| 3 | `base_importer.py:52-61` | id set from metadata values | validation | Only surviving ids. |
| 4 | `lastepochtools_importer.py:87-106,900-903` | id → name from metadata | skill_name | Tree ids an0my/cstri/dacn33/ds34l/te44/ub5d9/sndr1 unresolved, so the code is stored as the name. fi9 maps to "Frigid Tempest". |
| 5 | `maxroll_importer.py:48-73` | id → name (metadata) | | Same collapse. |
| 6 | `maxroll_importer.py:76-121,957-968` | tree id → name (hasTree) and reverse name → tree id | spec tree | Names come from the corrupted swt copy (fi9 "Frigid Tempest", en6 "Create Shadow", me27 "Shocking Impact", rf1azz "Reap"). |
| 7 | `combat_engine.py:292-307` `_get_skill_def(name)`; `domain/registries/skill_registry.py` | name | `skills.json` / `SKILL_STATS` | name-keyed; hand values. |
| 8 | `optimization_engine.py:65-90` `_normalize_skill_name` | `.title()` name | registry | "Mark for Death" vs "Mark For Death" mismatch class. |
| 9 | `skill_tree_resolver.py:159-166` `get_tree_for_skill(name)` | lower-case `skill_name` scan | `skill_tree_nodes.json` | 7 trees keyed by raw code; corrupted importer names never match; 5 trees missing; first match wins. |
| 10 | `skill_tree_resolver.py:332-345` | node int id | node | `n["id"]` within tree. |
| 11 | `build_analysis_service.py:189-210` | `sorted(skills, key=slot)[0]` | primary skill | Only slot-0 skill tree is applied. |
| 12 | `routes/skills.py:41-67` | tree `id` | `community_skill_trees.json` | Community (prowner) data. |
| 13 | `routes/skills.py:256-275` `_skill_name_to_id` | `ability` / `nodes[0].name` / `name.lower().replace(" ","_")` | tree id | Heuristic; `ability` is CamelCase internal ("RogueMultishot"). |
| 14 | `routes/skills.py:353-357` (allocate) | `_skill_name_to_id(s.skill_name)==skill_id` or name equality | build skill | |
| 15 | `routes/ref.py:354-380` | class name → 5 hand skill names | catalogue | |
| 16 | `skills/skill_classifier.py:22` | tags by skill name | classification | name-keyed. |
| 17 | `frontend/src/data/skillTrees/index.ts:16-150` `SKILL_NAME_TO_CODE` | lower-case name | tree code | anomaly→an0mz, cinder strike→cinss (no tree); REL-10. |
| 18 | `skillTrees/index.ts:4296-4303` `getSkillTree` | code, then name, then `name.replace(/\s+/g,"_")` | nodes | Fallback slug never matches codes. |
| 19 | `skillTrees/index.ts:4306-4319` `getSkillCode`, `hasSkillTree` | name/code | | |
| 20 | `skillTrees/index.ts:4323-4327` `resolveSkillName` | code → `nodes[0].name` | display | |
| 21 | `skillTrees/index.ts:4330-4335` `getEntryIconId` | code → `nodes[0].iconId` | icon | Array index 0 assumed root. |
| 22 | `scripts/generate_tree_data.py:180-220,239-256` | swt name.lower() → id (last wins); `Skills.Skill_<code>_<n>_Name` regex | FE TS rewrite | Generator of #17. |
| 23 | `scripts/generate_tree_data.py:53-78,95-160` | `(class lower, raw id)`; class from TS `const _CLASS_` names | FE passive names | regex patching of TS source. |
| 24 | `frontend/src/lib/gameData.ts:405+` `SKILL_STATS`, `:52-240` `CLASS_SKILLS` | name | FE sim | hand. |
| 25 | `build_analysis_service.py:164,199-200` | `raw_node_id` per class → string id | passives | Relies on unique raw ids per class (true now; the collision branch would break it). |
| 26 | `PassiveTreeGraph.tsx:168-170` | `raw_node_id` | API node | Same. |
| 27 | `BuildPassiveTree.tsx:110-118` | `raw_node_id ↔ id` maps | | Same. |
| 28 | `passive_stat_resolver.py:57+` `STAT_KEY_MAP`; `frontend/src/constants/passiveStatMap.ts` | stat display name | BuildStats field | numeric `property` dropped. |
| 29 | `skill_tree_resolver.py:55-140` `_STAT_LABEL_MAP` | lower-case label parsed from text | field | |
| 30 | `stat_engine.py:275-297,563` `KEYSTONE_BONUSES` | node name | bonus | unreachable (no keystone type). |
| 31 | `stat_engine.py:569` modulo cycle | `node_id % len(cycle)` | synthetic stat | index-keyed fabrication. |
| 32 | importers `_CLASS_MAP` (`LET:36-42`, `maxroll:206-212`, `import_route:47-53`) | class int 0-4 | class name | Correct (matches classes.json ids). |

---

### Legacy authorities (files/constants acting as authoritative character data)

| Authority | Kind | Origin | Readers |
|---|---|---|---|
| `data/classes/passives.json` | synced (older snapshot + unknown merge) | exports_json (pre-1.4.6) + char-tree-layout.json | `cli.py seed-passives`; `routes/passives.py` fallback; `routes/ref.py` fallback; `scripts/verify_passive_coverage.py`; v2 report (layout join) |
| `passive_nodes` DB table | seeded | passives.json | routes/passives, routes/ref, `passive_stat_resolver`, `build_analysis_service`, `routes/builds._validate_passive_tree`, `optimization_engine` |
| `MASTERY_MAP` / `CLASS_PREFIX` / `TREE_ID_TO_CLASS` `sync_game_data.py:363-387` | hand constants | — | `sync_passives` |
| `data/classes/classes.json` | synced (old schema) | exports_json | `base_importer` |
| `backend/app/game_data/classes.json` | hand | — | pipeline (dead accessors) |
| `backend/app/game_data/constants.json` (`passives.max_allocated_nodes 113`) | hand | — | `engines/validators.py:231`, other engines |
| `backend/app/game_data/skills.json` (179) | hand | — | SkillRegistry → combat/optimization engines, `/api/ref/skills` |
| `combat_engine.SKILL_STATS` | hand | — | `_get_skill_def` fallback |
| `stat_engine` `CLASS_BASE_STATS`, `MASTERY_BONUSES`, `KEYSTONE_BONUSES`, `ATTRIBUTE_SCALING`, `*_STAT_CYCLE` | hand | — | `aggregate_stats` |
| `backend/app/constants/classes.py` / `backend/src/constants/classes.ts` (`BASE_CLASSES`, `CLASS_MASTERIES`) | hand | — | routes/passives; FE via `@constants` |
| `engines/validators.py VALID_MASTERIES` | hand | — | build validation |
| `routes/ref.py CLASS_META` | hand | — | `/api/ref/classes`, `/api/ref/skills` |
| importer `_CLASS_MAP`/`_MASTERY_MAP` ×3 | hand | — | LET/Maxroll import |
| `data/classes/skills_metadata.json` | synced+hand fields, corrupted names | exports_json | pipeline; base/LET/Maxroll importers |
| `data/classes/skills_with_trees.json` | synced (corrupted copy) | exports_json | Maxroll importer; skill_classifier (tags) |
| `data/classes/skill_tree_nodes.json` | unknown generator | ? | `skill_tree_resolver` (DPS skill modifiers, conversions) |
| `data/classes/community_skill_trees.json` | synced; community (prowner) | exports_json | `routes/skills.py` (tree API, allocation, reachability) |
| `data/classes/unmatched_trees.json` | synced | exports_json | none |
| `data/progression/blessings.json` | hand | — | pipeline → `resolve_blessing_stats` → stat engine; `/api/ref/blessings` |
| `data/progression/weaver_tree.json` | LET 1.4.2 | third-party | pipeline only (no consumer) |
| `data/combat/ailments.json` | synced | exports_json | none; engines use `constants/combat.py` hand values |
| `data/localization/*` | synced | exports_json | none |
| `frontend/src/data/passiveTrees/index.ts` | unknown merge + `generate_tree_data.py` name patch | LET/raw + exports_json names | `PassiveTreeGraph`, `PassiveProgressBar` |
| `frontend/src/data/passiveTrees/edges.ts` | unknown generator | char-tree-metadata.json | `PassiveTreeGraph` |
| `frontend/src/data/skillTrees/index.ts` | unknown merge + `generate_tree_data.py` | LET raw + swt | SkillSelector, SkillTreePanel, SkillTreeDraftPanel, SkillTreeGraph, BuildPlannerPage |
| `frontend/src/data/raw/char-tree-layout.json` | third-party layout | LET | **backend `sync_passives` (x/y/icon)**, scripts |
| `frontend/src/data/raw/char-tree-metadata.json`, `skill-tree-metadata.json` | third-party | LET | none at runtime |
| `frontend/src/data/raw/skill-tree-layout.json` | third-party | LET | v2 report script |
| `frontend/src/data/iconSpriteMap.json` | `scripts/build_sprite_map.py` | — | `TreeIcon.tsx` |
| `frontend/src/lib/gameData.ts` (`CLASS_COLORS`, `MASTERIES`, `CLASS_SKILLS`, `PASSIVE_REGIONS`, `CLASS_BASE_STATS`, `MASTERY_BONUSES`, `KEYSTONE_BONUSES`, `SKILL_STATS`, `AFFIX_DEFINITIONS`, `ATTRIBUTE_SCALING`) | hand ("single source of truth for the frontend", fandom/maxroll 1.2.x) | — | simulation.ts, BuildPlannerPage, BuildsPage, PassiveTreeControls, PassiveTreePage |
| `frontend/src/services/buildApi.ts CLASS_MASTERIES` | hand dup | — | encounter SkillSelector |
| `frontend/src/constants/passiveStatMap.ts` | hand mirror of backend STAT_KEY_MAP | — | FE passive stat pipeline (`types/passiveEffects.ts`, logic/*) |
| `frontend/src/logic/validatePassiveBuild.ts` (113, 20) | hand | — | PassiveTreePage, PointEconomyPanel |
| `PassiveTreeGraph.tsx:27,57` (`SECONDARY_MASTERY_DEPTH 20`, `MAX_PASSIVE_POINTS 113`) | hand dup | — | itself |
| `frontend/src/data/presets.ts`, `cli.py` sample builds | hand | — | UI/seed |
| `docs/generated/v2_{class_mastery,passive_tree,skill,skill_tree}_bundle.json` | generated (experimental) | exports_json + passives.json/skill-tree-layout.json | `/api/experimental/v2/*` only |

---

### Identity hazards (file:line)

1. `scripts/sync_game_data.py:363-369,502`: `MASTERY_MAP` assigns mastery by index with the wrong order for Mage/Primalist/Sentinel, mislabelling 190 nodes. The export's own correct `masteryName` (present on every node) is ignored.
2. `scripts/sync_game_data.py:21` and `scripts/generate_tree_data.py:25`: `SRC_DIR` points inside the Forge repo (does not exist), so no sync is reproducible. `backend/scripts/report_v2_*.py:21` default to Windows `D:\Forge\…`.
3. `scripts/sync_game_data.py:506-515`: `requirements[].requirement` (points) is dropped. Garbage/NULL references (canonical NULL 48 / IMPLAUSIBLE 16 / UNRESOLVED 3 across 19 nodes, e.g. ac-1 node 20 `nodeId 0, requirement 208`) are emitted as real edges.
4. `scripts/sync_game_data.py:511`: collision resolution `next(n for n in all_nodes if n["id"]==req_raw_id)` ignores mastery and picks the first match.
5. `scripts/sync_game_data.py:492-495` + `backend/app/models/__init__.py:293` (String(16)) + `cli.py:258-266` prune: node id format depends on collision state (`ac_5` vs `ac_m1_5`), so ids are not stable across syncs; stored builds referencing old ids become ghost or invalid.
6. `scripts/sync_game_data.py:518-521`: numeric `property` id and tags are dropped, and all stat semantics are re-derived from display strings (`passive_stat_resolver.py:57+`, `frontend/src/constants/passiveStatMap.ts`).
7. `scripts/sync_game_data.py:546`: `node_type` is invented from `maxPoints>1`. `stat_engine.py:563` KEYSTONE path is unreachable.
8. `scripts/sync_game_data.py:390-429,527-543`: the backend sync depends on a **frontend** third-party file (`frontend/src/data/raw/char-tree-layout.json`) for x/y/icon.
9. `data/classes/passives.json` (`requires` field): produced by an unknown script; 25 nodes disagree with upstream prerequisites, and there are 6 phantom Warlock nodes (`ac_86, ac_88, ac_97, ac_98, ac_101, ac_103`).
10. `backend/app/models/__init__.py:311-314` (requires = "OR-of-parents") vs `backend/app/game_data/passive_tree_validator.py:63-104` (AND of all parents) vs `backend/app/routes/skills.py:113-131` (AND) vs FE single `parentId` (`frontend/src/lib/gameData.ts:299-300`): prerequisite semantics are contradictory.
11. `backend/app/routes/builds.py:137-151`: integer passive ids (the format all importers produce) are skipped, so there is no class, prerequisite, mastery or budget validation on create. PATCH is unvalidated. `validate_allocation` is test-only.
12. `backend/app/services/passive_stat_resolver.py:370`: `IN (...)` dedups repeated ids, so allocated **points are ignored** (each node is applied once).
13. `backend/app/routes/passives.py:160-167`, `routes/ref.py:166,309-312`: mastery filter by the mislabelled name returns the wrong subtree.
14. `frontend/src/components/features/build/BuildPassiveTree.tsx:61-67,104-107`: tabs from `CLASS_MASTERIES` and sections from the API `mastery` label give wrong tab contents for 6 masteries. `:69-73` `getMasteryIndex` (CLASS_MASTERIES order) is wrong for all Mage/Sentinel masteries (dead today).
15. `frontend/src/logic/validatePassiveBuild.ts:42-64`: mastery point accounting uses mislabelled names.
16. `PassiveTreeGraph.tsx` (static TS regions, correct) vs `BuildPassiveTree.tsx` (API labels, wrong): two UIs disagree on mastery membership for the same node.
17. Four distinct mastery orderings: `CLASS_MASTERIES` (`backend/src/constants/classes.ts:13-19`, `backend/app/constants/classes.py:11-17`, `frontend/src/services/buildApi.ts:62-68`), `ref.py:74-115`, `gameData.ts:252-283` PASSIVE_REGIONS, and `MASTERY_MAP`. Only the importers (`lastepochtools_importer.py:44-50`, `maxroll_importer.py:214-220`, `import_route.py:55-61`), `generate_tree_data.py:31-37` and FE `PASSIVE_TREES` match the game. Default mastery `[0]` (`BuildPlannerPage.tsx:878,968,1047,1224`; `encounter/SkillSelector.tsx:64`) depends on the arbitrary display order.
18. `base_importer.py:41-45`: valid masteries include index-0 base-class names.
19. `scripts/sync_game_data.py:336-345`: skills keyed by name, collapsing 184 → 161. Survivors are tree-less variants for 11/12 duplicate names (REL-6).
20. `data/classes/skills_metadata.json` / `skills_with_trees.json`: corrupted name↔id pairs (fi9 "Frigid Tempest", en6 "Create Shadow", me27 "Shocking Impact", rf1azz "Reap"). Fireball, Meteor, Elemental Nova and Reaper Form have no metadata entry. These propagate into LET/Maxroll import names (`lastepochtools_importer.py:900`, `maxroll_importer.py:966`) and do not match `skill_tree_nodes.json` (`fi9.skill_name = "fireball"`), so imported Fireball builds get no tree stats.
21. `data/classes/skill_tree_nodes.json`: unknown generator; 2,190 of 3,875 swt nodes (canonical 3,936); stats flattened into text; no edges; 7 trees keyed by code in `skill_name`. `skill_tree_resolver.py:159-166` is a name scan.
22. `skill_tree_resolver.py:179`: `raw.strip().rstrip("(downside)")` is a char-set strip that can eat trailing value characters ('d','o','w','n','s','i','e').
23. `build_analysis_service.py:189-210`: only the slot-0 skill's spec tree is applied.
24. `frontend/src/data/skillTrees/index.ts:16-150`: `SKILL_NAME_TO_CODE` "anomaly"→an0mz and "cinder strike"→cinss resolve to codes with no tree. `parentId` is single, losing 683 multi-prerequisite edges (REL-10). `getSkillTree` fallback `name.replace(/\s+/g,"_")` (`:4300`) never matches codes.
25. `backend/app/routes/skills.py:256-275`: name→tree heuristic over community data (prowner, "may not reflect current patch"); community tree count differs from upstream (140 vs 138).
26. `backend/app/game_data/pipeline.py:127-140` vs `scripts/sync_game_data.py:583-650`: blessings shape mismatch. A sync would silently zero `blessings_flat`. Blessing id = `_slugify(displayName)` (`:632`) drops the upstream internal id.
27. `backend/app/engines/stat_engine.py:569`: `node_id % len(cycle)` fabricates stats when resolver output is empty (index-keyed synthetic data).
28. `backend/app/optimization_engine.py:65-90`: `.title()` normalization changes canonical names ("for" → "For").
29. `scripts/sync_game_data.py:25-32,72-86,1471`: `patch_version` read from `metadata.json` `version`/`patchVersion`; `files_updated` lists only affixes; the upstream `game_build`/`_meta` of classes, ailments and passives is dropped per file; current `data/version.json` has no trust block. No character-side record carries patch or trust identity at runtime.
30. Weaver (`data/progression/weaver_tree.json`, LET 1.4.2) and ailments (`data/combat/ailments.json`) are loaded or synced but never consumed. Ailment math uses `backend/app/constants/combat.py:21-28` literals.
31. Canonical passive `mastery` is an int only. Name resolution requires a join `tree_id` → `exports_json/classes.json` `treeID` → `masteries[i].name` (no numeric mastery id exists; `localizationKey`/`masteryAbilityPathId` are the only stable non-positional handles). That join is verified 535/535 consistent.

## Part C — Persistence, seeding and version surfaces


READ-ONLY investigation. Repo root: `/home/user/le-the-forge`. All paths relative to it. No files modified.

---

### 1. Database models (`backend/app/models/__init__.py`)

| Table | Model (line) | PK | Game-data identity columns | Notes |
|---|---|---|---|---|
| `users` | User :52 | String(36) uuid | none | `is_admin` :61 |
| `builds` | Build :75 | String(36) uuid; `slug` unique :80 | `character_class` String(32) :86, `mastery` String(32) :87 (free strings, names); `passive_tree` JSON :92; `gear` JSON :95; `blessings` JSON :99 | `patch_version` String(16) NOT NULL ORM default `"1.2.1"` :107; `cycle` String(16) NOT NULL default `"1.2"` :108. No `data_version`, no `source`, no import provenance, no schema version column. |
| `build_skills` | BuildSkill :143 | uuid | `skill_name` String(64) :151 (display name, or tree code for some imports); `spec_tree` JSON :155 (int node ids) | `slot` comment says 0-4 :149, but service writes 1..5 (build_service.py:78/119). UNIQUE(build_id, slot) :160 |
| `votes` | Vote :168 | uuid | none | UNIQUE(user_id, build_id) :180 |
| `craft_sessions` | CraftSession :188 | uuid | `item_type` String(32) :199, `item_name` :200, `affixes` JSON `{name,tier,sealed}` :208 (by affix NAME) | no patch/version |
| `craft_steps` | CraftStep :219 | uuid | `affix_name` String(64) :233; `affixes_before` JSON :245 | by NAME |
| `item_types` | ItemType :254 | Integer autoincrement | `name` unique :259 | seeded from hardcoded list (cli.py:39-71) |
| `affix_defs` | AffixDef :265 | Integer autoincrement :269 | `name` String(256) NOT unique :270, `stat_key` :273 | Game `id` (slug, e.g. `void_penetration`) and `affix_id` (int) from data/items/affixes.json are NOT persisted. |
| `passive_nodes` | PassiveNode :289 | String(16) namespaced e.g. `"ac_0"` :293 | `raw_node_id` Integer :294 (in-game int); `connections` JSON of string ids :309; `requires` JSON :314; `stats` JSON :317 | No version/patch column. |
| `import_failures` | ImportFailure :330 | uuid | `source`, `raw_url`, `diagnostics` JSON :343 (holds app/data/extractor versions) | Only place source/URL provenance persists — and only for failures/partials. |
| `build_views` | BuildView :355 | uuid | none | FK ondelete CASCADE :361 |

- Docstring lists a `SkillDef` reference table (:16) — **no SkillDef model/table exists**. Skills are identified only by `BuildSkill.skill_name` strings; skill reference data lives in JSON (`data/classes/skills_metadata.json`, skill trees) loaded by the pipeline.
- No FK from any user table to any reference table: builds reference game data by **name strings** (class, mastery, skill_name, item_name, affix name) and **integer raw ids** (passive_tree, spec_tree), all inside JSON blobs or free-text columns.
- `docs/data_models.md:44` claims `patch_version = String(20), nullable=True` — contradicts model (String(16), NOT NULL).

### 2. Schemas (`backend/app/schemas/__init__.py`)

| Field | Line | Client-supplied? | Validation | Default |
|---|---|---|---|---|
| `BuildCreateSchema.passive_tree` | :82 | yes | `List(Raw())` — any JSON (ints, strings, dicts) | `[]` |
| `.gear` / `.skills` / `.blessings` | :83-85 | yes | `List(Dict())` — shape unvalidated | `[]` |
| `.patch_version` | :90 | yes | `Str()` only — no format, no allow-list, no comparison to CURRENT_PATCH | `"1.2.1"` |
| `.cycle` | :91 | yes | `Str()` only | `"1.2"` |
| `.character_class` | :76 | yes | OneOf(BASE_CLASSES) | required |
| `.mastery` | :79,:94-113 | yes | must be in CLASS_MASTERIES & match class | required |
| `BuildUpdateSchema.patch_version` | :132 | yes (owner may rewrite any string) | `Str()` | none |
| `BuildUpdateSchema` — `cycle` | — | not updatable (absent) | unknown=EXCLUDE :119 | — |
| `BuildListSchema.patch_version/cycle` | :149-150 | dump only | — | — |

### 3. Seeding

#### Commands (`backend/app/utils/cli.py`)
| Command | Line | Behaviour |
|---|---|---|
| `flask seed` | :73-97 | ItemType from hardcoded `_ITEM_TYPES` (:39-71); AffixDef from `get_all_affixes()` (pipeline → data/items/affixes.json). **Insert-only, skip if `name` exists** (:80, :85). Never updates or prunes existing rows. |
| `flask reseed-affixes` | :99-123 | `AffixDef.query.delete()` then re-insert all (no dedupe). Changes autoincrement ids. Not run by any deploy path. |
| `flask seed-passives` | :183-266 | Upsert from `data/classes/passives.json` keyed by string `id` (:210); warns on dangling connections (:205-208); **prunes rows not in JSON** (:256-266). If JSON missing: prints ERROR and `return` → **exit code 0** (:191-193). |
| `flask seed-builds` | :125-181 | 3 demo shells via `create_build` with `patch_version "1.4.3"`, `cycle "1.2"` (:146-147, :157-158, :167-168) — inconsistent pair; no passives/gear/skills. |
| `flask remove-seeded-builds` | :326-354 | Delete the 3 demo builds by name. |
| `flask validate-data` | :368-441 | JSON parse/type/min-entries checks on data/ files; does not check DB. |

Note: brief's "cli.py ~256 pipeline version 'unknown'" — cli.py:256 is the passive prune comment. The `"unknown"` data version comes from `backend/app/game_data/pipeline.py:104,467-471` (`_detect_version` reads `_version`/`_meta.version` from affixes.json, which is a top-level **list** → always `"unknown"`).

#### Who runs seeding
| Path | File:line | Runs migrations | Runs seed | Runs seed-passives |
|---|---|---|---|---|
| Render API | render.yaml:43 `preDeployCommand: flask db upgrade`; start :44 gunicorn | yes | **NO** | **NO** (DB-4) |
| Heroku-style Procfile | backend/Procfile:2 `release: flask db upgrade` | yes | no | no |
| Docker image entrypoint | backend/entrypoint.sh:9-14 | yes | yes, but `2>/dev/null \|\| echo "skipped (command not registered)"` masks real failures (:13-14) | same masking |
| docker-compose.yml (dev) | :55 `flask db upgrade && flask seed && flask seed-passives && flask run` | yes | yes | yes |
| docker-compose.prod.yml | uses Dockerfile ENTRYPOINT (Dockerfile:60) | yes | yes (masked) | yes (masked) |
| Docs | docs/production_setup.md:30-42 manual `flask seed`, `seed-passives`, `seed-builds` | — | manual | manual |

Docker path note: Dockerfile build context is `./backend` only (docker-compose.prod.yml:121-123), so `data/` must come from the `./data:/data:ro` mount (prod.yml:145); cli/health/passives resolve `parents[3]` → `/data/...`. `VERSION` is not in the image → `app.__version__` (app/__init__.py:19-28) and `/api/version` `_read_version` (routes/version.py:39-44) fall back to `"0.0.0"` in Docker.

#### Seeding facts
- data/items/affixes.json: 1228 entries, **1104 distinct names, 98 duplicated names**, 1228 unique `id` slugs, only 1112 unique `affix_id` ints. `flask seed` (name-keyed skip) therefore stores ≤1104 rows and silently drops 124 entries; `reseed-affixes` stores all 1228 (with duplicate names). The two commands produce different tables.
- `flask seed` never updates existing AffixDef rows → after a data sync, affix tier ranges in DB stay stale on any environment that seeded previously (Render never runs it at all).
- data/classes/passives.json: 541 nodes; no `(character_class, raw_node_id)` collisions today; ids are namespaced strings (`ac_0`…).
- `seed-passives` is the only seeder that prunes; it upserts all columns.
- No seeding run records a version/hash (no seed-metadata table; data/version.json is not read during seeding).
- Render prod: if passive_nodes / affix_defs / item_types were never manually seeded they are **empty**, and stay whatever was last manually seeded across data syncs.

#### What validates against / reads seeded tables, and empty-table behaviour
| Consumer | File:line | Reads | If table empty |
|---|---|---|---|
| POST /api/builds passive validation | routes/builds.py:137-152, :163-167 | `db.session.get(PassiveNode, nid)` for **string** ids only; int ids skipped (:147-148) | every string id rejected → `400 Invalid passive node`; int ids (what the frontend sends) pass unchecked |
| PATCH /api/builds | routes/builds.py:200-216 | **no passive validation** | n/a |
| Import → create_build | routes/import_route.py:603 | bypasses schema AND passive validation | n/a |
| Build simulate/analysis | services/build_analysis_service.py:149-200 | PassiveNode by class; maps int `raw_node_id` → string id (:163,:199-200); string ids in passive_tree are **dropped** | zero passive stats, silent |
| passive_stat_resolver | services/passive_stat_resolver.py:352-376 | PassiveNode by string id | logs warning, skips |
| /api/simulate | routes/simulate.py:75-79 | PassiveNode by class → raw ids | empty node list |
| optimization_engine | engines/optimization_engine.py:50-53, :576 | PassiveNode | documented fallback when empty |
| GET /api/passives* | routes/passives.py:73-77, :27-35 | PassiveNode | **falls back to data/classes/passives.json** |
| GET /api/ref/passives | routes/ref.py:304-330 | PassiveNode | falls back to JSON |
| GET /api/ref/item-types | routes/ref.py:176-201 | ItemType | hardcoded 16-item fallback (no Spear/Polearm/idols) |
| GET /api/ref/affixes | routes/ref.py:203-292 | AffixDef | falls back to JSON; **id differs**: DB path returns `str(AffixDef.id)` autoincrement (:282), fallback returns JSON slug `id` — affix id identity unstable across reseeds and between paths |
| craft_service | services/craft_service.py:12 | imports AffixDef | — |

Net: DB-backed reads silently fall back to JSON when empty, so an unseeded prod looks healthy on read paths while analysis loses passive stats and string-id build creation fails.

### 4. Migrations (`backend/migrations/versions/`)

17 revision files (brief said 15). Single head: **`c5d8e2b7a913`** (computed from revision/down_revision; also asserted by tests test_r0_import_telemetry.py:249 and test_r0_build_delete.py:72).

Chain: `cf57d3c33180` (initial) → `3ffd55fa24ac` → `8d9b7a5c2e11` → `b4c1f0f6d2aa` → `e07407b85e20` → `93e06c1a641f` → `21bc975a3016` → `f1a2b3c4d5e6` → `a1b2c3d4e5f6` → {`b2f8a3d1c7e9`, `f8953bcaab80`→`d1e2f3a4b5c6`} → merge `e2f3a4b5c6d1` → `654f2ebcd332` → `dd1840cac963` → `a7c3e91f4d20` → `c5d8e2b7a913`.

| Issue | File:line |
|---|---|
| Postgres-only `'[]'::json` server_default | 8d9b7a5c2e11:28; 654f2ebcd332:27 |
| Named FK drop assumes Postgres auto-name `build_views_build_id_fkey` (created unnamed in d1e2f3a4b5c6:27) | a7c3e91f4d20:21,26,34 |
| Upgrade drops `build_skills_build_id_fkey`/`votes_build_id_fkey` and recreates with `None` name and **without ondelete CASCADE** | 3ffd55fa24ac:27-31 |
| Broken downgrade: `drop_constraint(None, ...)` | 3ffd55fa24ac:40,44 |
| Lossy rebuild: passive_nodes dropped/recreated (int id → String(16)); downgrade recreates old int schema, data lost | a1b2c3d4e5f6:30-50, :53-68 |
| `requires` server_default `"[]"` (string literal) | dd1840cac963:27 |
| `builds.patch_version`/`cycle` NOT NULL with no server_default (ORM-only default) | cf57d3c33180:80-81 |
| Tests use `sqlite:///:memory:` + `db.create_all()` (config.py:163-165; tests/conftest.py:19) — migrations never executed in CI | — |

### 5. Version / identity surfaces

| Surface | File:line | Value today | Source | Consumers |
|---|---|---|---|---|
| `Build.patch_version` ORM default | models/__init__.py:107 | `"1.2.1"` | hardcoded | DB rows |
| `Build.cycle` ORM default | models/__init__.py:108 | `"1.2"` | hardcoded | DB rows, list filter `?cycle=` (build_service.py:176-177) |
| BuildCreateSchema.patch_version | schemas/__init__.py:90 | `"1.2.1"` default, any string accepted | client / hardcoded default | create_build |
| BuildCreateSchema.cycle | schemas/__init__.py:91 | `"1.2"` | client / hardcoded | create_build |
| BuildUpdateSchema.patch_version | schemas/__init__.py:132 | any string | client | update_build (:105-107 in service) |
| create_build defaults | services/build_service.py:67-68 | `"1.2.1"` / `"1.2"` | hardcoded | imports (route bypasses schema), seed-builds |
| Seed demo builds | utils/cli.py:146-147,157-158,167-168 | `"1.4.3"` / cycle `"1.2"` | hardcoded | demo rows |
| `Config.CURRENT_PATCH` | backend/config.py:44 | `"1.4.3"` (env CURRENT_PATCH) | env/hardcoded | /api/version, meta snapshot |
| `Config.CURRENT_SEASON` | backend/config.py:46 | `4` | env/hardcoded | /api/version |
| `Config.DATA_VERSION` | backend/config.py:42 | `"1.0.0"` | env/hardcoded (never bumped by sync) | /api/version `data_version` |
| /api/version | routes/version.py:58-67 (fallbacks :64-66 `1.0.0`/`1.4.3`/`4`) | version from VERSION, commit via `git rev-parse` (:47-55, fails on Render w/o .git → null), data_version 1.0.0, current_patch 1.4.3, season 4 | config/file | TopBar.tsx:85, AppLayout.tsx:22,117-121, DashboardPage.tsx:192-193, BuildPlannerPage.tsx:472-473, DataManagerDashboard.tsx:87 |
| /api/health patch_version | routes/health.py:40-46,56 | **`"unknown"`** (reads data/version.json `patch`→`patch_version`; file says "unknown") | file | Render health check, docs/deployment.md:144 claims "1.4.3" |
| /api/health version | routes/health.py:55; app/__init__.py:19-28 | `"0.8.0"` (VERSION) — `"0.0.0"` in Docker image | file | monitors |
| VERSION file | /VERSION | `0.8.0` | file | app.__version__, /api/version, vite `__APP_VERSION__` (frontend/vite.config.ts:38) |
| data/version.json | data/version.json | `patch_version:"unknown"`, `synced_at:2026-04-26T01:32:48Z`, `files_updated:["data\\items\\affixes.json"]`; **no `upstream_trust` key** (file predates R1 change) | file (written by sync) | health.py only |
| sync stamp writer | scripts/sync_game_data.py:25-32 (`_detect_patch_version`→"unknown" w/o metadata.json), :38-62 `_upstream_trust`, :65-69 copy manifest, :72-86 `_write_version_stamp` | would add `upstream_trust` {status ABSENT/PRESENT,…} | script | nothing at runtime |
| data/upstream_trust_manifest.json | (written by sync :69) | **does not exist** in data/ | file | none |
| GameDataPipeline.data_version | game_data/pipeline.py:104,116,152,467-471 | `"unknown"` (affixes.json is a list) | file-derived | AffixDefinition/SkillStatDef/EnemyProfile `.data_version` (:240,:248,:256); registries version-equality gate app/__init__.py:147-156 (passes since all "unknown") |
| affix_engine data_version | engines/affix_engine.py:109,117 | `"file"` | hardcoded | AffixDefinition |
| combat_engine data_version | engines/combat_engine.py:44-49 | `"hardcoded"` | hardcoded | SkillStatDef |
| VersionedLoader | backend/data/versioning/versioned_loader.py:21-25,59-78 | `"unknown"` (probes `_version` in affixes/enemy/damage_types) | file-derived | POST /api/load/game-data response (routes/load.py:52-54,108-109) |
| Import diagnostics | services/import_diagnostics.py:108-115,178-181 | `data_version` "unknown", `extractor_version` hardcoded "unknown", app_commit from RENDER_GIT_COMMIT/… (:99-105) | server | ImportFailure.diagnostics, discord_notifier.py:182 |
| Meta snapshot current_patch | services/meta_analytics_service.py:185,195 | `"1.4.3"` fallback | config | MetaSnapshotPage.tsx:428 |
| Meta patch_breakdown | services/meta_analytics_service.py:168-177 | group-by Build.patch_version | DB | meta page |
| Frontend workspace default | frontend/src/store/buildWorkspace.ts:96-97 | `"1.2.1"` / `"1.2"` | hardcoded | workspace state |
| Frontend planner create payload | frontend/src/components/features/build/BuildPlannerPage.tsx:1105-1124 | omits patch_version/cycle → server default `1.2.1` | client (omitted) | — |
| Outdated-build banner | BuildPlannerPage.tsx:472-485 | compares build.patch_version vs current_patch | client | **every new build (1.2.1) vs 1.4.3 → always "Outdated build"** |
| Dashboard hero | frontend/src/pages/DashboardPage.tsx:192-193,205-207 | fallback `"1.4.3"`, season `4` | hardcoded fallback | UI |
| Frontend gameData comment | frontend/src/lib/gameData.ts:8 | "patch 1.2.x" | hardcoded doc | — |
| Canonical provenance types | frontend/src/types/sourceProvenance.ts:5, canonicalBase.ts:12 | `patch_version?` | type only | canonical* types |
| README | README.md:14, :226 | "patch 1.4.3, Season 4 (last sync 2026-04-21)" | doc | — |
| KNOWN_LIMITATIONS (DOC-3) | docs/KNOWN_LIMITATIONS.md:45-47 | "1.4.3, Season 4 (from data/version.json)", "last modified 2026-04-21", schema 1.0.0-beta | doc — **false**: version.json says "unknown", synced 2026-04-26 | — |
| deployment/production docs | docs/deployment.md:144; docs/production_setup.md:66 | health patch_version "1.4.3" | doc — false | — |
| docker-compose.prod APP_VERSION | docker-compose.prod.yml:158 | `0.8.0` | env default | frontend build arg |

Summary: there are at least 5 disagreeing "patch" values: `1.2.1` (DB/schema/service/workspace default), `1.4.3` (config/version route/dashboard/seed builds/docs), `"unknown"` (data/version.json, health, pipeline, VersionedLoader, diagnostics), `1.0.0` (DATA_VERSION), `1.2` cycle paired with 1.4.3. None is derived from the synced data.

### 6. Saved-build storage and identity

#### Saved build identity facts
- **Passives**: `Build.passive_tree` JSON list (models:92). Frontend persists **in-game `raw_node_id` integers**, one entry per point in allocation order (types/index.ts:96; PassivesSection.tsx:15-21; BuildPassiveTree.tsx:110-116,294 maps raw↔string and emits raw). Importers also persist raw ints (lastepochtools_importer.py:881-884; maxroll_importer.py:929-950). Schema also accepts namespaced strings (`"ac_0"`); those are validated on create (builds.py:146-151) but **ignored by analysis** (build_analysis_service.py:199). Ints are never validated. Raw ids are only unique per class today (0 collisions in passives.json), and nothing pins them to a data version.
- **Skills**: `build_skills` rows (FK to build) with `skill_name` free string (display name; Maxroll may store canonical or raw name, maxroll_importer.py:1015; LET name from tree). `_skill_name_to_id` (routes/skills.py:256-275) resolves by tree code, ability name, or root node name, falling back to slugify. `spec_tree` = JSON list of int node ids per point. Client `slot` ignored; service assigns 1..5.
- **Gear**: `Build.gear` JSON. Planner shape `{slot, item_name, rarity, affixes:[{name,tier,sealed}]}` (types/index.ts:126-137) — affixes identified by **name**. LET import shape adds `base_type_id` (int), affix `{id: str(affix_id) or encoded id, name, tier}`, unresolved `{id, name:None, decoded}`, and `_raw` item (lastepochtools_importer.py:1200-1230). Uniques resolved later by `item_name` string match against uniques.json (build_analysis_service.py:171-179).
- **Blessings**: JSON `{timeline_id, blessing_id, is_grand, value}` (models:97-99); resolved via pipeline `blessings_flat` by id (pipeline.py:133-140).
- **Craft sessions**: affixes and steps by affix **name** (models:208,233).
- Meta analytics aggregates popular affixes by name from gear JSON (meta_analytics_service.py:81-95) and skills by `skill_name` (:68-78).
- **No build stores**: data version, data hash, source (manual/LET/Maxroll), source URL/code, import timestamp, importer version, or the identity scheme of its passive ids.

#### Importers provenance
| Path | File:line | What is persisted on Build |
|---|---|---|
| POST /api/import/build → `_do_import` | routes/import_route.py:547-680 | `build_service.create_build(build_data)` (:603) directly — no schema, no passive validation; forced `is_public=False` (:600); **patch_version/cycle default 1.2.1/1.2**; `_source_code` (LET :951; Maxroll :1241) and `_import_meta` silently discarded (create_build ignores unknown keys). Source returned in response only (:678). |
| POST /api/import/let/json | routes/import_route.py:410-468 | not saved; returns mapped payload with `_import_meta {source:"lastepochtools", char_class_id, mastery_id, counts}` (:278-286) to client; client then saves via normal create (no provenance carried) |
| Failures/partials | routes/import_route.py:325-375; models ImportFailure :330 | `source`, `raw_url`, `missing_fields`, `partial_data`, `diagnostics` (app_version, app_commit, data_version="unknown", extractor_version="unknown"; import_diagnostics.py:163-183). Not linked to the created Build except `slug` inside partial_data (:619). |
| Importer validation | services/importers/base_importer.py:114-149 | checks class/mastery vs game data; skills only non-empty name; no passive/affix validation |

### 7. Upstream trust at runtime
- `upstream_trust` / `upstream_trust_manifest.json` / `consumer_state` / `trusted_calculation_eligible`: **zero references in backend/app or frontend/src** (grep). Only in scripts/sync_game_data.py:35-86, tests/test_r1_sync_trust_contract.py, and audit docs.
- Current data/version.json has no `upstream_trust` field and data/upstream_trust_manifest.json does not exist (sync has not been re-run since R1).
- health.py reads only `patch`/`patch_version` (:46). Trust is **not enforced anywhere** at runtime; not surfaced via any API; not checked in CI.

### 8. CI workflows (`.github/workflows/`)
| Workflow | Trigger | Checks |
|---|---|---|
| ci.yml `backend-test` | push dev; PR to dev/main (:3-10) | `pytest tests/ -x -q` with FLASK_ENV=testing → sqlite in-memory + create_all (:35-48). No Postgres, **no `flask db upgrade`**, no seeding. Migration graph single-head checked only via pytest tests. |
| ci.yml `frontend-lint` | same | `npx tsc --noEmit` only (:79-81). No vitest, no build. |
| ci.yml `data-validate` | same | `flask validate-data` (:105-111) — JSON parse/type/min-count. No data↔DB parity, no version.json/trust check, no sync re-run/diff, no generated-file freshness check. |
| deploy.yml | push main | curl Render deploy hook (:25-30); no gating on CI; Render then runs only `flask db upgrade`. |
| sync-main-to-dev.yml | push main | opens main→dev merge PR (`-X ours`); no checks. |

### Key risks (for remediation planning)
1. Render never seeds reference tables (render.yaml:43); reads silently fall back to JSON; analysis silently loses passive stats.
2. Build patch identity is client-writable free text defaulting to `1.2.1` while UI's current patch is `1.4.3` → all new builds flagged outdated; imports likewise.
3. Data version is `"unknown"` everywhere it is derived from data; `1.0.0`/`1.4.3` are hardcoded config.
4. Passive identity split: ints (persisted, unvalidated, used by analysis) vs strings (validated, ignored by analysis).
5. Affix identity: DB autoincrement id vs JSON slug vs LET `affix_id`; `flask seed` vs `reseed-affixes` yield different tables (1104 vs 1228 rows); affixes in builds stored by name.
6. No provenance (source, data version, importer version) persisted on Build.
7. Migrations are Postgres-only in places, downgrades broken, never executed in CI.
8. Upstream trust exists only in the sync script; nothing consumes it.

## Part D — The experimental v2 path


Repo: `/home/user/le-the-forge` at HEAD `9e1356a`. This was a read-only investigation. Upstream checked: `/home/user/last-epoch-data/exports_json` (`metadata.json`: `patch_full 1.4.6_22986002`, `gameAssemblySha256 d4a68f3f…`, generated 2026-05-06).

### 0. Bottom line

- **No user-facing calculation uses v2.** The v2 bundles are read only by the `experimental` blueprint (`backend/app/routes/experimental.py`). Planner adapters, scripts and tests also read them, but no engine, service or other route does.
  - No module in `app/engines`, `app/services` or any other route imports `app.repositories.v2`, `app.normalization.v2`, `app.planner_adapters` or `app.api_contracts`.
  - `planner_adapters` has **zero** importers inside `app/`. It is used only by scripts and tests.
- **v2 is exposed in production without a gate (SYS-5).**
  - `app/__init__.py:253-254` registers `experimental_bp` twice, at `/experimental` and at `/api/experimental`.
  - It has 41 routes (`experimental.py`): 38 `/v2/*` routes plus 3 forge-safe routes. Only the 3 forge-safe routes check a config flag (`experimental.py:82,106,174`). The 38 v2 routes have no gate.
  - Frontend routes `/debug/v2*` and `/trusted-data*` are deliberately outside the `IS_DEV` gate (`frontend/src/App.tsx:49-51,251-276` vs `:279`).
- **The routes behave differently per deploy target:**
  - **Render** (`render.yaml:39 rootDir: backend` on a full clone): `docs/generated` is present, so the routes work and serve data. Each request re-parses the JSON with no cache: `V2ModifierRegistry.load` reads the 37 MB registry on every hit (`normalization/v2/modifier_registry.py:22-26`, `experimental.py:1347-1348`).
  - **Docker** (`docker-compose.prod.yml:44 context ./backend`, `Dockerfile COPY . .`): `docs/generated` is not in the image. `experimental.py:43` computes `ROOT = parents[3]`, which is `/`, so the routes 404 with `v2_*_bundle_missing`.
- **FE-3 is confirmed.** The pages fetch root-relative `/experimental/v2/...`:
  - `ForgeSafeAffixesDebugPage.tsx:48`, `V2ClassMasteryDebugPage.tsx:35`, `V2IdolsDebugPage.tsx:35`, `V2ItemsDebugPage.tsx:37`, `V2PassivesDebugPage.tsx:36`, `V2SkillsDebugPage.tsx:36`, `V2UniqueSetDebugPage.tsx:38`.
  - `V2StatsModifiersDebugPage.tsx:33` fetches `/api/experimental/v2/modifiers/debug`.
  - On Render the static site rewrites `/*` to `/index.html` (`render.yaml:102-107`) and the API lives on `api.epochforge.gg` (`render.yaml:100-101`). Every one of these fetches therefore gets HTML.
  - On Docker nginx only `/api/` is proxied (`frontend/nginx.conf:38`), so `/experimental/...` falls through to the SPA (`:51-52`).
  - Only the Vite dev proxy (`vite.config.ts:47-50`) makes them work.

---

### 1. Bundle provenance table

Generators live in **`backend/scripts/`**, not in `scripts/`. Every upstream default is a hard-coded Windows path `D:\Forge\last-epoch-data\...`, so a rebuild on Linux needs explicit `--source-*` arguments. Every bundle carries `metadata.experimental=true, production_safe=false, production_consumed=false` and `generated_on 2026-05-12` (2026-05-13 for the registries).

| Bundle (`docs/generated/`) | Size | Generator (file:line of default in/out) | Upstream input | Record identity (`canonical_id`) | Per-record provenance and trust | Build or patch carried |
|---|---|---|---|---|---|---|
| `v2_affix_bundle.json` | 7.5 MB, 1,098 records | `report_v2_affix_bundle.py:22-25` | `last-epoch-data/docs/generated/forge_safe_affix_bundle.json` (upstream controlled bundle, schema 1.0.0), **not** `exports_json` directly | `affix:{equipment\|idol}:{affix_id}` | `provenance{extraction_method:"forge_safe_affix_bundle", source_path:"/home/user/last-epoch-data/exports_json/affixes.json", source_id, raw_reference}`, `trust_level=generated_from_game_data`, `support_status=partial`, `stable_calculable=false` | **None.** `patch_version: None` is hard-coded (`report_v2_affix_bundle.py:170`) even though the upstream bundle has `game_version:"1.4.6_22986002"`, which is dropped. No SHA. |
| `v2_item_base_bundle.json` | 1.35 MB, 542 | `report_v2_item_bundles.py:20-21` | `exports_json/items.json` | `item_base:equippable:{baseTypeID}:{subTypeID}` | same shape, `extraction_method:"last_epoch_items_export"` | `patch_version "1.4.6_22986002"` per record. It is derived by splitting the Windows `installPath` (`report_v2_item_bundles.py:534-539`). Top level: `source_metadata.game_build.gameAssemblySha256`. |
| `v2_item_implicit_bundle.json` | 4.2 MB, 1,182 | `report_v2_item_bundles.py:22` | `items.json` | `implicit:equippable:{base}:{sub}:{idx}` (positional) | same | same as item_base |
| `v2_unique_bundle.json` | 5.3 MB, 409 | `report_v2_unique_set_bundles.py:21,24` | `exports_json/uniques.json` | `unique:{id}` | `extraction_method:"last_epoch_unique_set_export"` | **None** (`patch_version` null for 409/409). No SHA, because `uniques.json` has no `game_build`. |
| `v2_set_bundle.json` | 0.9 MB: 23 sets, 59 items, 45 bonuses | `report_v2_unique_set_bundles.py:22,25` | `uniques.json` + `set_bonuses.json` | `set_group:{setId}`, `set_item:{id}`, `set_bonus:{setId}:{idx}` | same | Bonuses carry patch 1.4.6_22986002. Sets and set items carry null. SHA is under `source_metadata.set_bonuses.game_build`. |
| `v2_idol_bundle.json` | 155 KB, 71 | `report_v2_idol_bundles.py:20,22` | `items.json` | `idol:{baseTypeID}:{subTypeID}` | `last_epoch_items_export` | patch 1.4.6_22986002 and SHA |
| `v2_idol_affix_bundle.json` | 3.1 MB, 483 | `report_v2_idol_bundles.py:21,23` | **`v2_affix_bundle.json`** (projection) | `idol_affix:{affix_id}` | `extraction_method:"v2_affix_bundle_idol_projection"` | None; `source_metadata` is `{}` |
| `v2_class_mastery_bundle.json` | 44 KB: 5 classes, 15 masteries | `report_v2_class_mastery_bundle.py:21,28` | `exports_json/classes.json` + 6 other v2 bundles (cross-reference of restriction labels) | `class:{slug}`, `mastery:…` | `last_epoch_data_export` | patch 1.4.6_22986002 and SHA |
| `v2_passive_tree_bundle.json` | 2.7 MB: 5 trees, 535 nodes | `report_v2_passive_tree_bundle.py:21-24` | `exports_json/passive_trees.json` + **legacy layout `data/classes/passives.json`** + class_mastery bundle | `passive_tree:{ac_1}`, `passive_node:{tree}:{node}` | `provenance` + `layout_provenance` | **None.** Null is hard-coded (`:313,:358`). No SHA. |
| `v2_skill_bundle.json` | 0.67 MB, 184 | `report_v2_skill_tree_bundle.py:21,24` | `exports_json/skills_with_trees.json` + **`frontend/src/data/raw/skill-tree-layout.json`** + class_mastery bundle | `skill:{source_skill_id}` (e.g. `skill:ab0lh`) | `last_epoch_data_export` | None. Null is hard-coded (`:387,:458,:504`). |
| `v2_skill_tree_bundle.json` | 19.9 MB: 136 trees, 3,919 nodes | `report_v2_skill_tree_bundle.py:25` | same | `skill_tree:…`, `skill_node:{tree}:{node}` | `provenance` + `layout_provenance` | None |
| `v2_stat_registry.json` | 2.7 MB, 2,070 | `report_v2_stat_modifier_normalization.py:31-41,57` | the 9 v2 bundles above | `stat:{slug}` (`modifier_policy.normalize_stat_id`) | `provenance.source_path:"docs/generated/v2_*_bundle.json"` | None |
| `v2_modifier_registry.json` | **37 MB, 19,398** | `report_v2_stat_modifier_normalization.py:58` | the 9 v2 bundles + `v2_skill_identity_alignment_report.json` | `modifier:{src_type}:{src_id}:{row}:{index}:{sha1[:10]}` (positional, `:507-510`) | Inherits the source record's provenance. Every row has `support_status partial`; 0 rows are `stable_calculable`. Blocked reasons: `value_scale_not_planner_normalized` 19,398/19,398. | None |
| `v2_value_normalization_policy_report.json` (artifact read by repositories) | – | `report_v2_value_normalization_policy.py` | modifier registry | families | audit-only | – |

**Correcting the audit's "SHA only" claim:**
- Five record families carry a per-record `patch_version` of `1.4.6_22986002`: item_base, item_implicit, idol, class/mastery and set_bonus. Their top-level `source_metadata.game_build` carries the GameAssembly SHA, the Unity version and `installPath`.
- The other eight families carry **neither** a patch nor a SHA: affix, idol_affix, unique, set/set_item, passive, skill, skill_tree, stat and modifier.
- No bundle records an input-file hash, a Forge-side generator version, or an R1 `consumer_state` (CERTIFIED / QUARANTINED). The v2 validators report `missing_provenance_count: 0` even though half the families have no patch.

Other generated v2 artifacts are all offline reports. Generator → output:
- `report_v2_source_inventory.py` → `v2_source_inventory.json`
- `report_v2_canonical_contract.py` → `v2_canonical_contract_report.json`
- `*_validation_report.json` and `*_unsupported_report.json` come from the matching bundle scripts.
- `report_v2_skill_identity_alignment.py:19-24` → `v2_skill_identity_alignment_report.json`
- `report_v2_value_normalization_policy.py` → `v2_value_normalization_policy_report.json`, `v2_value_normalization_candidate_families.json`
- `report_v2_backend_repository_layer.py:151`, `report_v2_api_contract.py:164`, `validate_v2_trusted_data.py:242` → `v2_validation_ci_report.json`
- `report_v2_planner_adapter*.py`, `report_v2_planner_metadata_remap.py`, `report_v2_planner_remap_readiness.py`, `report_v2_passive_skill_identity_remap.py`, `report_v2_item_base_display_metadata.py`, `report_v2_affix_display_provenance.py`
- `report_v2_stat_modifier_dry_run.py`, `report_v2_golden_baseline_plan.py`, `report_v2_experimental_planner_adapter_mode.py`
- `report_v2_release_readiness.py:13-25,393`, `report_v2_5_release_readiness.py:511`, `report_v2_5_trust_ux_plan.py:458`

In total there are 51 `v2_*` files under `docs/generated` (90 MB of the folder's 97 MB) and 38 `docs/migration/V2_*.md` documents. `validate_v2_trusted_data.py` is **not** wired into `.github/workflows/ci.yml`. The `test_v2_*` tests (28 files) run in pytest and mostly build fixtures in `tmp_path`.

#### Known defects (verified)

**REL-7: secondary-property ranges are misattributed.**
- Root cause is in `report_v2_stat_modifier_normalization.py:226-238` (`_collect_affix_modifiers`). It computes `raw_min = min(tier_ranges.min_value)` and `raw_max = max(tier_ranges.max_value)` across **all tiers of the primary roll**, then assigns that pair to **every** `modifier_reference` index.
- The loss happens before this step. The upstream `forge_safe_affix_bundle.json` `tier_data` contains only `minRoll`/`maxRoll` (no `extraRolls`). `report_v2_affix_bundle.py:377-387` `_tier_range` keeps only those two fields.
- My count is broader than the audit's: **690 of 690 non-primary affix modifier rows (526 equipment + 164 idol_affix) carry exactly the primary's range by construction.** The audit's 366/384 is the subset where this differs from the export's `extraRolls`.
- Example: `affix:equipment:14` ColdResistance has 0.2–7.0 (the FreezeRateMultiplier T1min–T8max), while the export says 0.05–0.36.
- Primary rows are also lossy: one min–max spans T1..T8 and the per-tier structure is lost.

**REL-9: class-to-skill links are reported as unresolved.**
- `report_v2_skill_tree_bundle.py:654-664` builds its lookup with keys `f"skill:{source_skill_id}"` (e.g. `skill:ab0lh`). The class/mastery links are `skill_path:{numeric ability path id}` (`:645-651`). The key spaces never intersect, so the summary reports `resolved 0 / 63` (`v2_skill_bundle.json summary.class_mastery_unresolved_skill_link_count=63`).
- Re-run against `exports_json/skills_with_trees.json[].source_ability_path_id`: **60/63 resolve**. The three that do not are `skill_path:261142`, `262953` and `263498`.
- Separately, `owner_class_ids` is `[]` for all 184 skills.

**Other defects:**
- Positional IDs (`implicit:…:{idx}`, `set_bonus:{set}:{idx}`, modifier `…:{index}:{sha1}`) are not stable across patches.
- Patch is derived from a Windows path string (`report_v2_item_bundles.py:534-539`).
- The affix bundle's top-level `source_bundle_path` is a `D:\` path, but each record's `provenance.source_path` is `/home/user/...affixes.json`, so the two disagree.
- v2 passive and skill layouts depend on **legacy** Forge files (`data/classes/passives.json`, `frontend/src/data/raw/skill-tree-layout.json`), so v2 is not independent of the legacy path.

---

### 2. Runtime consumers

| Bundle | Runtime reader | Route(s) (`experimental.py` line) | Kind |
|---|---|---|---|
| affix | `V2AffixRepository` (`repositories/v2/affix_repository.py:27-31`) | `/v2/affixes` :197, `/v2/affixes/<id>` :241, `/v2/affixes/debug` :279 | debug, ungated |
| item_base + implicit | `V2ItemRepository` | :308, :345, :383, :416 | debug, ungated |
| unique + set | `V2UniqueSetRepository` | :445, :482, :518, :547, :585, :592 | debug, ungated |
| idol + idol_affix | `V2IdolRepository` | :599, :623, :639, :662, :678 | debug, ungated |
| class_mastery | `V2ClassMasteryRepository` | :691, :708, :721, :737, :754 | debug, ungated |
| passive_tree | `V2PassiveRepository` | :770, :793, :806, :825 | debug, ungated |
| skill + skill_tree | `V2SkillRepository` | :841, :864, :877, :896, :912, :931 | debug, ungated |
| stat_registry | `V2StatRegistry` (`normalization/v2/stat_registry.py`) | :947, :971 | debug, ungated |
| modifier_registry | `V2ModifierRegistry` | :987, :1021, :1035 | debug, ungated |
| (forge-safe, not v2) `FORGE_SAFE_AFFIX_*` paths | `data/loaders/forge_safe_*`, `data/repositories/forge_safe_*` | :78, :102, :170; `debug.py:25`; `routes/affixes.py` via `services/affix_catalog_service.py:41-50` | flag-gated (`config.py:58-61,80-93`, default off). `FORGE_SAFE_AFFIX_CATALOG_ENABLED` is defined twice in `config.py` (:58 and :84). |

Other readers, none of them runtime:
- `repositories/v2/registry.py`, `repositories/v2/paths.py:10-25`, and all of `planner_adapters/v2/*`. Their importers are only `backend/scripts/report_v2_*` and `backend/tests/test_v2_*`.
- `planner_adapters/v2/experimental_mode.py:19` gates on an `enabled=` argument (`GATE_MECHANISM = "explicit_enabled_argument"`) that no runtime caller passes.

`routes/meta.py` and `routes/entities.py` are **not** v2. They import only `meta_analytics_service` and `utils.responses`/`cache`.

Frontend consumers:
- The 8 debug pages under `frontend/src/pages/debug/` (`V2*DebugPage.tsx` and `ForgeSafeAffixesDebugPage.tsx`, which in fact reads `/experimental/v2/affixes`) plus `V2DebugNavigationPage`.
- 3 static explainer pages: `TrustedDataExplanationPage`, `TrustedDataSupportMatrixPage` and `PreV3MechanicalReadinessPage`. These do no fetch; they use only v2 badge and notice components.
- No main-nav component links to them (grep for `/trusted-data` and `/debug/v2` outside these pages and `App.tsx` finds nothing).
- No planner, build, crafting or simulation page imports any `v2*` lib.

---

### 3. `backend/app/game_data/*` — runtime vs offline

Method: grep for importers in `app/routes`, `app/services`, `app/engines`, `app/domain`, `app/utils`, `app/__init__.py` and `wsgi.py`, including relative imports. Only `pipeline.py` (`app/__init__.py:135`) and `game_data_loader.py` (engines, services, `routes/ref.py`, `routes/load.py`) are runtime. **Every other module is offline tooling.** Each one's own docstring says "Developer-only".

| Module | LOC | Imported by (non-test) | Class |
|---|---|---|---|
| `pipeline.py` | 471 | `app/__init__.py:135`, `game_data_loader.py` | RUNTIME (legacy path) |
| `game_data_loader.py` | 245 | `engines/stat_engine`, `combat_engine`, `stat_resolution_pipeline`, `services/build_analysis_service`, `routes/ref`, `routes/load`, `utils/cli` | RUNTIME (legacy path) |
| `passive_tree_validator.py` | 120 | tests only | dead or offline |
| `bundle_compat.py` | 397 | `bundle_item_adapter_report`, `bundle_item_diff`; `backend/scripts/check_data_bundle.py`, `diff_bundle_items.py`, `report_bundle_item_adapter_map.py` | OFFLINE |
| `bundle_item_adapter_report.py` | 458 | 10 `backend/scripts/*` | OFFLINE |
| `bundle_item_adapter_translations.py`, `bundle_item_mapping_review.py` | 115, 83 | `bundle_item_type_dry_run_resolver` | OFFLINE |
| `bundle_item_diff.py`, `bundle_item_type_context_report.py`, `bundle_item_type_dry_run_resolver.py` | 393, 195, 215 | scripts and the le_tools_* modules | OFFLINE |
| `controlled_affix_resolver_prototype.py` / `_comparison.py` / `_per_affix_diagnostic.py` | 588, 350, 351 | scripts only | OFFLINE |
| `controlled_modifier_resolver_prototype.py` / `_comparison.py` | 461, 386 | scripts only | OFFLINE |
| `affix_diagnostic_consumer.py` | 390 | other controlled_* modules; reads `../last-epoch-data/docs/generated` (`:16`) | OFFLINE |
| `malformed_tier_value_shape_validator.py`, `missing_modifier_reference_mapping_validator.py`, `modifier_unresolved_category_triage.py` | 248, 340, 360 | scripts only | OFFLINE |
| `le_tools_import_context_report.py`, `_sidecar.py`, `_sidecar_validator.py`, `le_tools_import_stage_context_report.py`, `le_tools_fresh_sidecar_diagnostic.py`, `le_tools_sidecar_diagnostic_consumer.py`, `le_tools_sidecar_diagnostic_comparison.py` | 262, 338, 164, 217, 397, 231, 257 | scripts only (the importers in `services/importers` do **not** import them) | OFFLINE |

About 8,000 LOC of offline diagnostics live inside the runtime package `app/game_data/` and ship in the image (`COPY . .`). Their outputs are the non-`v2_` `.md`/`.json` files in `docs/generated`.

---

### 4. Trust, quarantine, envelope and provenance semantics

#### Backend vocabulary (`backend/app/data_contracts/`)

- **`TrustLevel`** (`trust_level.py:8-14`): `game_extracted`, `generated_from_game_data`, `manual_bridge`, `inferred`, `placeholder`, `deprecated`. `STABLE_TRUST_LEVELS = {game_extracted, generated_from_game_data}` (`:17-22`). **Every v2 record uses `generated_from_game_data`**, so the trust level never discriminates anything.
- **`SupportStatus`** (`trust_status.py:8-14`): `trusted`, `partial`, `text_only`, `unsupported`, `experimental`, `unknown`. `STABLE_CALCULABLE_STATUSES={trusted}` (`:17`), `DISPLAY_ONLY_STATUSES` (`:18-25`). **Every v2 record is `partial`**, and 0 records anywhere are `trusted` or `stable_calculable`.
- **`SourceProvenance`** (`source_provenance.py:9-40`): requires `source_path`, `source_type` and `extraction_method`. `patch_version` and `source_id` are optional; also `schema_version`, `notes` and `raw_reference`. There is no raw sha256, no build SHA and no consumer_state.
- **`canonical_id.py:8`**: `^[a-z0-9][a-z0-9._:-]*$`.
- **Eligibility gates:**
  - `normalization/v2/modifier_policy.py:101-128` `is_stable_modifier_eligible` returns these blocked reasons: `support_status_not_trusted`, `trust_level_not_stable`, `stat_id_unknown`, `operation_unknown`, `value_scale_not_planner_normalized`, `source_identity_not_resolved`, `source_record_not_calculable`, `special_behavior_not_calculable`, and a missing-provenance reason.
  - `planner_adapters/v2/eligibility.py` duplicates this with different reason codes, and in one place maps the trust-level failure to the support-status reason (`unstable_support_status` is appended for both checks).

This is a **"deny-by-default calculability" model**: nothing is calculable. It is not a quarantine model. It has no per-family defect ledger, does not ingest R1's `consumer_state`, and never refuses input; it only labels it. That makes it **conceptually compatible with R1's `PRESERVED_ONLY`/`QUARANTINED`**, but the vocabularies do not map one-to-one.

#### API envelope (`backend/app/api_contracts/v2/response.py`)

`experimental.py:59-71` adds the envelope in an `after_request` hook for `/experimental/v2/*` and `/api/experimental/v2/*` only. `standardize_v2_payload` (`:11-28`) keeps the legacy keys and uses `setdefault` to add:

- `data`: copies of `record`, `records`, `debug_summary`, `implicits`, `masteries`, `nodes`, `comparison`, `count` and `result_count` (`:56-65`).
- `meta`: `{domain, route, route_version:"v2", status_code, experimental:true, read_only:true, production_consumer:false, data_source, total_records, schema_version:"v2.experimental", generated_at?}` (`:68-91`).
- `support_summary`: counts for each `SUPPORT_STATUSES` value (`:8`), plus `stable_calculable`, `audit_only` and `unresolved` (`:94-106`).
- `warnings` (`:136-143`).
- `provenance`: `{data_source, source_path, production_consumed:false, record_provenance?}` (`:109-118`).
- `debug`: `{route, repository_debug_summary, validation_error_count, validation_warning_count, read_only, production_consumer:false, value_policy_audit_only, unresolved_skill_identity_count}` (`:121-133`).

Errors are rewritten to `error:{code,message,details}` plus `meta` and `debug` (`:31-49`). Because of `setdefault`, the payload duplicates `records` and `data.records`.

#### Frontend vocabulary

- **`frontend/src/lib/v2ApiEnvelope.ts`** (88 lines): a loose `V2ApiEnvelope<T>` interface that accepts both the legacy top-level keys and `data.*` (`:7-34`). Accessors: `getV2Records`, `getV2Summary`, `getV2SourcePath`, `getV2ErrorMessage` and `summarizeV2Support` (`:36-76`).
- **`v2TrustStatus.ts`**:
  - Support badges are `trusted` ("Trusted Data", green), `supported`, `partial`, `unsupported`, `audit-only`, `display-only`, `experimental`, `not-planner-calculable` and `unknown`.
  - Trust badges are `trusted`, `generated`, `validated`, `provenance-available`, `blocked`, `warning` and `unknown`.
  - Normalizers are at `:123-149`. `getV2EnvelopeBadges` (`:151-170`) derives badges from `support_summary`, `trust_level_counts`, `meta.experimental`/`read_only`, provenance presence, warnings and `stable_calculable==0`.
- **`v2Limitations.ts:4-15`** codes: `display_only`, `audit_only_value_normalization`, `not_planner_calculable`, `unsupported_mechanics`, `partial_support`, `unresolved_skill_identity`, `missing_provenance`, `experimental_only`, `stable_calculable_unavailable`, `production_not_consuming_v2` and `unknown_limitation`, with user copy at `:24-102`.
- **`v2TrustSummaries.ts`**: provenance and warning summarizers.

#### Reuse vs retire for R2

- **Reusable as concepts:**
  - the `SourceProvenance` dataclass, extended with `raw_sha256`, `game_assembly_sha256`, `patch` and `consumer_state`
  - the `canonical_id` regex
  - the blocked-reason list in `is_stable_modifier_eligible`, as a starting point for R2 "refuse QUARANTINED" enforcement
  - the envelope's `meta`/`provenance`/`warnings` split
  - the limitation-copy idea in the frontend
- **Must retire or replace:**
  - The "Trusted Data" branding and the green `trusted` badge. No record is trusted, and R1 marks all families QUARANTINED (`r1/R1_TRUST_CONTRACT.md:21,33,46,50-54`).
  - `STABLE_TRUST_LEVELS` treating `generated_from_game_data` as stable.
  - The two diverging eligibility implementations.
  - `schema_version:"v2.experimental"`.
  - The `setdefault` dual-shape envelope.
  - Hard-coded `production_consumer:false` literals in place of a real consumer_state.

---

### 5. Inventory and disposition

Key: **REMOVE_AFTER_R2** = delete once R2's canonical consumer and enforcement land. **KEEP_TEMPORARILY** = needed until a stated replacement exists. **ARCHIVE** = move out of the runtime and shipped tree (e.g. to `docs/archive` or `tools/`) with no further maintenance. **STILL_REQUIRED** = live dependency.

| Artifact or module | Disposition | Reason |
|---|---|---|
| `docs/generated/v2_*_bundle.json` (11) + `v2_stat_registry.json` | REMOVE_AFTER_R2 | Debug-only, no patch on 8 families, positional IDs, superseded by R1 canonical families |
| `docs/generated/v2_modifier_registry.json` | REMOVE_AFTER_R2 (do not consume before then) | REL-7 corrupts 690 secondary rows; 37 MB parsed per request |
| `docs/generated/v2_*_report.json`, `v2_*plan.json`, `v2_source_inventory.json`, `v2_5_*` (38) | ARCHIVE | Point-in-time migration evidence; not read at runtime |
| `docs/migration/V2_*.md` (38) | ARCHIVE | Narrative for the abandoned v2/v2.5 track |
| `docs/generated/{controlled_*,le_tools_*,forge_safe_*,bundle_item_*,malformed_*,missing_modifier_*,modifier_unresolved_*,affix_diagnostic_*}` | ARCHIVE | Offline diagnostic outputs |
| `backend/scripts/report_v2_*_bundle(s).py` (7 generators) | KEEP_TEMPORARILY | Only way to regenerate what the debug routes serve. Fix or retire together with the routes. |
| `backend/scripts/report_v2_*` other reports (20), `validate_v2_trusted_data.py` | ARCHIVE | Report-only; not in CI |
| `backend/app/routes/experimental.py` v2 section (:197-1050, 1213-1348) | REMOVE_AFTER_R2; **gate now** (SYS-5) | Ungated public API over quarantined and defective data |
| `experimental.py` forge-safe section (:78-195, 1051-1210) + `routes/debug.py` | KEEP_TEMPORARILY | Flag-gated and off by default; tied to the forge_safe affix catalog in `routes/affixes.py` |
| `app/__init__.py:253-254` double registration | REMOVE_AFTER_R2 (gate now) | Doubles the attack surface |
| `backend/app/repositories/v2/*` (1,779 LOC) | REMOVE_AFTER_R2 | Used only by experimental routes, scripts and tests |
| `backend/app/normalization/v2/*` | REMOVE_AFTER_R2 (salvage `modifier_policy.is_stable_modifier_eligible` reasons into R2) | Runtime only via experimental routes |
| `backend/app/planner_adapters/v2/*` (2,111 LOC) | ARCHIVE | Zero runtime importers; scripts and tests only |
| `backend/app/api_contracts/v2/response.py` | KEEP_TEMPORARILY | Envelope for the debug routes; redesign it as the R2 contract rather than extend it |
| `backend/app/data_contracts/*` | KEEP_TEMPORARILY (candidate base for the R2 contract) | Used by the generators and v2 repositories. `SourceProvenance` and `canonical_id` are worth evolving. |
| `app/game_data/pipeline.py`, `game_data_loader.py` | STILL_REQUIRED | Legacy runtime data path |
| `app/game_data/bundle_compat.py`, `bundle_item_*` (6) | ARCHIVE (move to `backend/tools/`) | Offline last-epoch-data bundle migration tooling inside the runtime package |
| `app/game_data/controlled_*` (5), `affix_diagnostic_consumer`, `malformed_*`, `missing_modifier_*`, `modifier_unresolved_*` | ARCHIVE | Offline prototype and diagnostic tooling |
| `app/game_data/le_tools_*` (7) | ARCHIVE (or KEEP_TEMPORARILY if R4 import work wants the sidecar) | Not used by `services/importers` |
| `app/game_data/passive_tree_validator.py` | REMOVE_AFTER_R2 | Test-only, no runtime caller |
| `frontend/src/pages/debug/V2*DebugPage.tsx` (7), `ForgeSafeAffixesDebugPage.tsx`, `V2DebugNavigationPage.tsx` | REMOVE_AFTER_R2; **move under `IS_DEV` now** | Broken in production (FE-3); expose quarantined data publicly |
| `TrustedDataExplanationPage`, `TrustedDataSupportMatrixPage`, `PreV3MechanicalReadinessPage` | REMOVE_AFTER_R2 (or rewrite to R1/R2 vocabulary) | "Trusted Data" copy contradicts R1 QUARANTINED (DOC-5) |
| `frontend/src/lib/v2ApiEnvelope.ts`, `v2TrustSummaries.ts` | REMOVE_AFTER_R2 | Only used by v2 debug pages |
| `frontend/src/lib/v2TrustStatus.ts`, `v2Limitations.ts`, `components/v2/*` | KEEP_TEMPORARILY | Badge and limitation-copy pattern is reusable for R2 trust display, but the vocabulary must change |
| `vite.config.ts:47-50` `/experimental` proxy | REMOVE_AFTER_R2 | Exists only for the v2 debug pages |
| `backend/tests/test_v2_*` (28), forge-safe/bundle/le_tools tests | Follow their subject | Mostly `tmp_path` fixture-based. Removing the code removes the tests. |

