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
