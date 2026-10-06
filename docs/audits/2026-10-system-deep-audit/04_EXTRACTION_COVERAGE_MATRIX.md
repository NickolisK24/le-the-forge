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
