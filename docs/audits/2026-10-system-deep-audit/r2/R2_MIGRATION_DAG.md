# R2 Migration DAG (R2-13)

**Status: design only.** Package details (components, acceptance, tests, rollback, complexity) are in `R2_IMPLEMENTATION_PACKAGES.json`. This document is the dependency order and the code evidence behind it.

## DAG

```
                    R2-P00 (DONE: R1 contract defects)
                         │
                    R2-P17 contract tests + fixtures
                    │            │
              R2-P01 importer   R2-P16 fallback gate (ratchet)      R2-P15 migrations + Postgres CI (independent)
                    │
              R2-P02 CanonicalDataStore (flag off)
               │            │
        R2-P03 typed ids   R2-P09 reference API envelope
               │      ╲
               │       R2-P05 affixes ──────────────────────────────┐
               │                                                    │
   ═══════ certified 1.5 snapshot (operator run) ══════             │
               │                                                    │
        R2-P04 upstream typed views (last-epoch-data)               │
          │          │                 │                            │
   R2-P06 classes/  R2-P11 items/uniques/sets/blessings ◀───────────┤
   masteries        (needs P05: affix can_roll_on base types)       │
          │                                                         │
   R2-P07 passives (graph) ────────────────┐                        │
          │                                │                        │
   R2-P08 skills/abilities/trees           │                        │
          │                                │                        │
   R2-P12 game-fact constants (needs P06, P11; inventory can start earlier)
          │
   R2-P13 build provenance + single validator (needs P05, P07, P08, P11)
   R2-P14 retire DB reference seeding (needs P05, P07, P09)
   R2-P19 version surfaces (needs P02, P13)
   R2-P10 frontend artifacts + parity (needs P07, P08, P09)
          │
   R2-P20 production cutover (needs all of the above + certified bundle)
          │  (+ one release)
   R2-P18 legacy retirement
```

**Critical path:**
- **Before the run:** P17 → P01 → P02 → P03.
- **After the certified snapshot:** P04 → P06 → P07 → P08 → P13 → P10 → P20 → P18.

P05, P09, P11, P12, P14 and P19 run beside the critical path.

## Why this order (code evidence)

| Edge | Evidence (R2_CURRENT_CONSUMPTION_GRAPH.md) |
| --- | --- |
| P17 before everything | No R2 contract test exists today. CI never runs `db upgrade`, vitest, or any data parity check (Part C §8). Each package's acceptance is a test that must exist first. |
| P01 → P02 → P03 | Every registry today is built from `data/` inside `GameDataPipeline` at app creation (`app/__init__.py:140-158`). The store must exist before typed registries can be built from it, and the importer must exist before the store has anything to load. |
| P03 → P05 (before the snapshot) | Affix consumers (`stat_engine.py:398-401`, `efficiency_scorer`, `gear_upgrade_ranker`, `craft_engine`, `affix_catalog_service`, `ref.py`, LET importer) depend only on affix data. Canonical affixes already exist (1.4.6, QUARANTINED), so P05 can be built and tested now and switched at cutover. |
| P04 → P06 | Mastery order exists only positionally in `CharacterClass.masteries`. The certified class view is the only production authority. The 1.4.6 legacy order is a fixture, not a source. |
| P06 → P07 | Passive node mastery membership (`node.mastery`) resolves through the class's masteries. `/api/passives` filters, `validatePassiveBuild` and `BuildPassiveTree` all group by mastery (Part B M.2 #6-#19). |
| P06 → P08 | Skills are abilities a class knows or unlocks (`CharacterClass.knownAbilities` / `unlockableAbilities`). Importers resolve class → mastery → skills (Part B §4). |
| P04 + snapshot → P08 | Tree → ability requires `SkillTree.ability`. That reference was carried only from R2-P00 onward, and the 1.4.6 dump has `ability_ref: NOT_IN_RAW_DUMP`. `ability_id` needs the Ability view. |
| P05 → P11 | Affix eligibility (`can_roll_on[].raw` = base type id) and item crafting (`item_engine`, `craft_service`) join affixes to item base types. Item identity must follow affix identity to avoid a third slot vocabulary. |
| P05, P07, P08, P11 → P13 | One build validator for create, PATCH and import needs every referenced family: passives, skills and trees, affixes, items and uniques. Today PATCH and import bypass validation (`builds.py:200-216`, `import_route.py:603`). |
| P05, P07, P09 → P14 | `affix_defs` readers (`ref.py`, `craft_service`) and `passive_nodes` readers (`routes/passives.py`, `passive_stat_resolver`, `build_analysis_service`, `builds._validate_passive_tree`, `optimization_engine`, `simulate.py`) must move to the store before the seed commands can be retired (Part C §3). |
| P07, P08, P09 → P10 | The frontend artifact holds the tree graphs, and the API holds catalogues. Parity (T8) compares both with the store. |
| P02, P13 → P19 | Version surfaces read the manifest, and the build banner compares `build.data_version`. |
| All → P20 → P18 | Legacy paths are deleted only after one release on the canonical path. Until then they are the rollback. |

## Package summary

| Package | Scope | Old source → new source | Depends on | Production behaviour change | Rollback | Size |
| --- | --- | --- | --- | --- | --- | --- |
| P00 | R1 contract fixes (done) | — | — | none | revert | S |
| P17 | Contract harness and fixtures | — → R1 canonical (pinned) | P00 | none | remove | M |
| P01 | Canonical bundle importer | `sync_game_data.py` → R1 artifacts | P17 | none until P20 | delete bundle dir | M |
| P02 | CanonicalDataStore | `GameDataPipeline` → `data/canonical/CURRENT` | P01 | none (flag off) | flag | M |
| P03 | Typed ids and registry factories | name/slug/index dicts → typed ids | P02 | none | remove | M |
| P15 | Migrations and Postgres CI | sqlite `create_all` → Postgres upgrade/downgrade | — | none | remove job | M |
| P16 | Fallback gate | — → ratchet at 575 | P17 | none | disable | S |
| P09 | Reference API envelope | DB/JSON fallbacks → store + envelope | P02 | at switch | flag | M |
| P05 | Affixes | 5 paths → canonical affixes | P03 | at switch: source-scale values, all properties | flag | L |
| P12 | Game-fact constants | literals → data or declared `FORGE_RULE` | P02, P06, P11 | where replaced | revert | M |
| P04 | Upstream typed views (last-epoch-data) | legacy exports → typed canonical views | certified snapshot | none (upstream) | drop view | XL |
| P06 | Classes and masteries (REL-1) | `MASTERY_MAP` and 4 orderings → `(class_id, mastery_index)` | P03, P04 | at switch: 190 nodes change mastery | flag | M |
| P07 | Passives as a graph | `passives.json` / DB / frontend TS → canonical graph | P03, P06 | at switch: phantom nodes, 25 prerequisites, points | flag | L |
| P08 | Skills / abilities / trees | name maps, `skill_tree_nodes.json`, community trees → `ability_id` / `tree_id` graph | P03, P04, P06, snapshot | at switch: correct trees, all slotted skills | flag | XL |
| P11 | Items / uniques / sets / blessings | curated bases, slugs, text implicits → typed views | P03, P04, P05 | at switch: identity and content | flag | XL |
| P13 | Build provenance | client `patch_version` → server `data_version`, `LEGACY_UNKNOWN` | P02, P05, P07, P08, P11 | yes: provenance shown, validation on all writes | downgrade migration | L |
| P14 | Retire DB reference seeding | DB tables + seeds → store | P02, P05, P07, P09 | yes: no seeding step | flag; tables kept until P18 | M |
| P19 | Version surfaces | hard-coded / unknown → manifest | P02, P13 | at switch | flag | S |
| P10 | Frontend authority | hand TS copies → generated artifact + parity | P07, P08, P09 | yes: UI trees canonical | revert switch commit | L |
| P20 | Production cutover | legacy `data/` → certified bundle | all above + snapshot | **the R2 change** | flag off, `CURRENT` back | M |
| P18 | Legacy retirement | — | P20 + one release | none visible | revert; downgrade restores tables | M |

## Identity hazards → package

| Hazard class (Part A H-numbers / Part B hazard numbers) | Hazards | Removed by |
| --- | --- | --- |
| Affix name/slug keying, duplicate `affix_id` first/last wins, name-keyed midpoints, seeding by name, unstable API ids, weapon-slot tag mismatch, frontend affix table, craft `type` field bug, tier semantics | A: H1–H9, H13, H17, H18, H20–H23 (16) | P05 |
| Base items by sequential index, varint first-hit, first unique per base, unique slug keying and first-match, slot key returning first item, gear persisted by name | A: H10–H12, H14–H16, H19 (7) | P11 (+P13 for persisted gear) |
| `MASTERY_MAP`, 4 mastery orderings, first-mastery defaults, base-class name accepted as mastery | B: 1, 13–18 | P06 |
| Passive id formats, requirement points dropped, garbage edges, contradictory prerequisite semantics, int ids unvalidated, points de-duplicated, phantom nodes, layout from a frontend file | B: 3-12 | P07 (+P10 for the frontend, P13 for validation) |
| Skill name collapse, corrupted skill names, `skill_tree_nodes.json` name scan, single `parentId`, slot-0 only, community-tree name heuristic | B: 19-25 | P08 (+P10) |
| Blessing shape mismatch and slug id | B: 26 | P11 |
| Modulo stat fabrication, `.title()` normalization, invented node type and unreachable keystone path | B: 7, 27–28 | P07 / P08 (data), R6 (math semantics) |
| Sync path, patch identity per file | B: 2, 29 | P01, P19 |
| Weaver / ailments not consumed | B: 30 | P04 (typed views), R6 (ailment math) |
| Canonical mastery positional only | B: 31 | P04 (class view carries the source list) |

## Interim production risk (not R2 work, recorded for the owner)

Until P20, production keeps serving the legacy path. Three defects are provable today from 1.4.6 evidence, and could be fixed narrowly before R2 if the owner chooses:

| Defect | Evidence |
| --- | --- |
| REL-1 mastery labels | The 1.4.6 export carries a correct `masteryName` per node |
| REL-23 seeding fields | `class_requirement` and tags are dropped by `to_dict` during seeding |
| Corrupted skill name pairs | The upstream export has the correct names |

R2 preparation does not apply them. The instruction was to not implement R2.
