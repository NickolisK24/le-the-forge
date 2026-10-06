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
