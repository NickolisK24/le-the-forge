# R2 Legacy Retirement Plan (R2-15)

**Status: inventory only. Nothing is deleted during preparation.**

Every legacy source of game data, every duplicate authority and every legacy loader that R2 makes obsolete is listed below, with its disposition:

| Disposition | Meaning | Count |
| --- | --- | --- |
| REMOVE_AFTER_R2 | Deleted in R2-P18, one release after the R2-P20 cutover, once T11 shows no reader | 60 |
| KEEP_TEMPORARILY | Still needed until a named replacement exists (often an R4 or R6 dependency or a declared `FORGE_RULE`) | 11 |
| ARCHIVE | Moved out of the runtime and shipped tree (`docs/archive/`, `backend/tools/`) with no further maintenance | 6 |
| STILL_REQUIRED | Live dependency through R2, removed later or kept | 2 |
| **Total legacy authorities** | | **79** |

## Retirement rules

1. **No deletion before cutover plus one release.** Until R2-P20 has run one release, every legacy path is the rollback. R2-P18 deletes only what T11 (the static reader scan plus the store's `FOREIGN_SOURCE` guard) shows has no runtime reader.
2. **DB tables are dropped by migration with a real downgrade.** `affix_defs`, `passive_nodes` and `item_types` are dropped in R2-P18, never before, and the downgrade recreates them empty.
3. **Archived evidence keeps its provenance.** The v2 reports and migration narratives are moved, not edited.
4. **The fallback ratchet closes with retirement.** 163 of the 744 dangerous fallbacks disappear with deleted or archived code (R2_FALLBACK_AUDIT.md).

## Inventory

| # | Area | Authority | Kind | Current readers | Disposition | Replacement / reason | Package |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L-001 | items | `data/items/affixes.json` | synced + curated (×100, flattened, 116 duplicate ids) | pipeline, AffixRegistry, stat engine, craft, ref, admin (writes it), LE Tools, forge-safe, load | REMOVE_AFTER_R2 | bundle `affixes.json` | P05 |
| L-002 | items | `data/items/base_items.json` | hand-curated, no game ids | base_engine, item_engine, `/api/ref/base-items`, ItemPicker, LE Tools by index | REMOVE_AFTER_R2 | item typed view `(base_type_id, sub_type_id)` | P11 |
| L-003 | items | `data/items/items.json` | synced, `_meta` stripped | LE Tools subtype map, codegen | REMOVE_AFTER_R2 | item typed view | P11 |
| L-004 | items | `data/items/implicit_stats.json` | hand-curated, one per slot | `/api/ref/implicit-stats` | REMOVE_AFTER_R2 | structured implicits per subtype | P11 |
| L-005 | items | `data/items/item_types.json` | hand-curated | codegen, diagnostics | REMOVE_AFTER_R2 | game EquipmentType enum + item view | P11 |
| L-006 | items | `data/items/uniques.json` | synced + curated text, slug keys | `/api/ref/uniques`, build analysis, LE Tools | REMOVE_AFTER_R2 | unique typed view by `unique_id` | P11 |
| L-007 | items | `data/items/set_items.json` | synced subset (47/59), stale meta | none at runtime | REMOVE_AFTER_R2 | set typed view | P11 |
| L-008 | items | `data/items/forging_potential_ranges.json` | FP by rarity (one of 4 FP sources) | fp_engine, `/api/ref/fp-ranges` | KEEP_TEMPORARILY | declared `FORGE_RULE` or canonical data if extracted (crafting rules are REQUIRED_FUTURE upstream) | P12 |
| L-009 | items | `data/items/crafting_rules.json` | hand FP costs | fp_engine, craft_engine, `/api/ref/crafting-rules` | KEEP_TEMPORARILY | declared `FORGE_RULE` until crafting data is extracted | P12 |
| L-010 | items | `data/items/rarities.json` | conflicting FP | `/api/ref/rarities` | REMOVE_AFTER_R2 | rarity enum + declared rule | P12 |
| L-011 | items | `data/items/tags.json` | tag vocabulary | none | REMOVE_AFTER_R2 | AT enum (flags) | P18 |
| L-012 | items | `backend/src/constants/BASE_TYPE_ID_TO_ITEM_TYPE_ID.ts` + 5 sibling TS maps + Python mirrors `backend/app/constants/*.py` | generated from item_types + items, truncated at 33, 1-H/2-H merged | diagnostics; frontend imports classes/rarities only | REMOVE_AFTER_R2 | item typed view | P11 |
| L-013 | items | `backend/scripts/generate_item_constants.py` | codegen for the maps above | manual | REMOVE_AFTER_R2 | none needed | P11 |
| L-014 | items | LE Tools importer maps (`_EQUIP_SLOT_MAP`, `_UNIQUE_SLOT_TO_FORGE`, `_SLOT_TO_BASE_TYPE_IDS`, `_FORGE_SLOT_TO_AFFIX_TAGS`, `_LET_SLOT_ALIASES`, `_RARITY_MAP`, `_BASE_ITEM_MAP`, `_AFFIX_MAP`) | hand + index-based | importer | KEEP_TEMPORARILY | `external_id_map/<provider>/<data_version>.json` (R2 shape, R4 repair) | P11 / R4 |
| L-015 | items | `cli._ITEM_TYPES` + DB `item_types` | seed literal | `/api/ref/item-types` | REMOVE_AFTER_R2 | store | P14 |
| L-016 | items | DB `affix_defs` | lossy seed (REL-23), autoincrement ids | `/api/ref/affixes`, craft_service | REMOVE_AFTER_R2 | store | P14 → dropped P18 |
| L-017 | items | `ref.py` static item-type fallback, `_SLOT_ALIASES`, `_SLOT_CATEGORIES` | hand | ref routes | REMOVE_AFTER_R2 | EquipmentType from the store | P09 / P11 |
| L-018 | items | `stat_engine._FLAT_SCALE_STAT_KEYS` + `get_affix_value` ×100 correction heuristic | heuristic value authority | `aggregate_stats` | REMOVE_AFTER_R2 | source-scale canonical values (nothing to correct) | P05 |
| L-019 | items | `build_analysis_service._UNIQUE_STAT_PATTERNS` | text→stat regexes | build analysis | REMOVE_AFTER_R2 | structured unique mods | P11 |
| L-020 | items | Slot validators `validators.VALID_SLOTS`, `equipment_set.VALID_EQUIPMENT_SLOTS`, `gear_upgrade_ranker._SLOT_ALIASES` | hand slot vocabularies | validation, ranking | REMOVE_AFTER_R2 | EquipmentType | P11 |
| L-021 | items | `frontend/src/lib/gameData.ts` `AFFIX_DEFINITIONS` (33 invented, T1 = best) | hand | simulation.ts, GearSlotEditor, BuildPlannerPage | REMOVE_AFTER_R2 | API affixes | P05 / P10 |
| L-022 | items | Frontend FP / craft copies (`CraftSimulatorPage.tsx:47-55`, `lib/crafting.ts:22-26`, `gameData.ts`) | hand duplicates | craft UI | REMOVE_AFTER_R2 | API (declared FORGE_RULE values) | P12 / P10 |
| L-023 | character | `data/classes/passives.json` | synced (older snapshot) + unknown merge script; 6 phantom nodes; 190 mislabels | seed-passives, passives/ref fallbacks, scripts, v2 report | REMOVE_AFTER_R2 | bundle `passive_trees.json` | P07 |
| L-024 | character | DB `passive_nodes` | seeded copy | passives/ref routes, passive_stat_resolver, build analysis, build validation, optimization_engine, simulate | REMOVE_AFTER_R2 | store | P14 → dropped P18 |
| L-025 | character | `MASTERY_MAP` / `CLASS_PREFIX` / `TREE_ID_TO_CLASS` (`sync_game_data.py:363-387`) | hand | sync_passives | REMOVE_AFTER_R2 | class view masteries (source order) | P06 |
| L-026 | character | `data/classes/classes.json` | synced, old schema | base_importer | REMOVE_AFTER_R2 | class typed view | P06 |
| L-027 | character | `backend/app/game_data/classes.json` | hand, dead accessors | pipeline (no callers) | REMOVE_AFTER_R2 | class view + declared FORGE_RULEs (R6 semantics) | P12 |
| L-028 | character | `backend/app/game_data/constants.json` (`max_allocated_nodes 113`, ...) | hand | validators, engines | KEEP_TEMPORARILY | derived from canonical data or declared FORGE_RULE | P12 |
| L-029 | character | `backend/app/game_data/skills.json` (179) + `combat_engine.SKILL_STATS` | hand skill values, name-keyed | SkillRegistry, combat/optimization engines, `/api/ref/skills` | KEEP_TEMPORARILY | identity moves to `ability_id` (P08); numeric values remain until R6 replaces them with extracted skill data | P08 / R6 |
| L-030 | character | `stat_engine` `CLASS_BASE_STATS`, `MASTERY_BONUSES`, `KEYSTONE_BONUSES`, `ATTRIBUTE_SCALING`, `*_STAT_CYCLE` | hand, partly fabricated (CALC-6) | aggregate_stats | KEEP_TEMPORARILY | class view base stats (P06); bonus semantics are R6 | P06 / R6 |
| L-031 | character | `backend/app/constants/classes.py` + `backend/src/constants/classes.ts` (`BASE_CLASSES`, `CLASS_MASTERIES`) | hand, wrong order | routes/passives validation, frontend via @constants | REMOVE_AFTER_R2 | `/api/ref/classes` ids | P06 |
| L-032 | character | `engines/validators.py` `VALID_MASTERIES` | hand | build validation | REMOVE_AFTER_R2 | class view | P06 |
| L-033 | character | `routes/ref.py` `CLASS_META` | hand (own mastery order, 5 skills) | `/api/ref/classes`, `/api/ref/skills` | REMOVE_AFTER_R2 | class view + ability view | P06 / P08 |
| L-034 | character | Importer `_CLASS_MAP` / `_MASTERY_MAP` ×3 | hand (correct order) | LE Tools, Maxroll, import_route | REMOVE_AFTER_R2 | canonical class view + external id map | P06 |
| L-035 | character | `data/classes/skills_metadata.json` | synced name-keyed + corrupted names | pipeline, importers | REMOVE_AFTER_R2 | ability view + skill trees by id | P08 |
| L-036 | character | `data/classes/skills_with_trees.json` | synced (corrupted copy) | Maxroll importer, skill_classifier | REMOVE_AFTER_R2 | skill trees + ability view | P08 |
| L-037 | character | `data/classes/skill_tree_nodes.json` | unknown generator, partial, text stats | skill_tree_resolver (DPS) | REMOVE_AFTER_R2 | bundle `skill_trees.json` | P08 |
| L-038 | character | `data/classes/community_skill_trees.json` | third-party community data | `/api/skills/*` tree API | REMOVE_AFTER_R2 | bundle `skill_trees.json` | P08 |
| L-039 | character | `data/classes/unmatched_trees.json` | synced | none | REMOVE_AFTER_R2 | — | P18 |
| L-040 | character | `data/progression/blessings.json` | hand-authored nested | pipeline → stat engine, `/api/ref/blessings` | REMOVE_AFTER_R2 | blessing typed view (item subtypes) | P11 |
| L-041 | character | `data/progression/weaver_tree.json` | LET 1.4.2 copy | pipeline only | REMOVE_AFTER_R2 | bundle `weaver_tree.json` | P07 |
| L-042 | character | `data/combat/ailments.json` | synced, never read | none | REMOVE_AFTER_R2 | ailment typed view (P04); math constants in `constants/combat.py` are R6 | P04 / R6 |
| L-043 | character | `data/localization/*` | synced, never read | none | REMOVE_AFTER_R2 | localization keys via property definitions / typed views | P18 |
| L-044 | character | `frontend/src/data/passiveTrees/index.ts`, `edges.ts` | no generator | PassiveTreeGraph, PassiveProgressBar | REMOVE_AFTER_R2 | generated artifact | P10 |
| L-045 | character | `frontend/src/data/skillTrees/index.ts` (+ `SKILL_NAME_TO_CODE`) | no generator | SkillSelector, SkillTreePanel, SkillTreeDraftPanel, SkillTreeGraph, BuildPlannerPage | REMOVE_AFTER_R2 | generated artifact | P10 |
| L-046 | character | `frontend/src/data/raw/char-tree-layout.json` | third-party layout (read by the backend sync) | sync_passives, scripts | ARCHIVE | layout overlay generated once, versioned per data_version | P10 |
| L-047 | character | `frontend/src/data/raw/char-tree-metadata.json`, `skill-tree-metadata.json`, `skill-tree-layout.json` | third-party | none at runtime / v2 script | ARCHIVE | — | P18 |
| L-048 | character | `frontend/src/lib/gameData.ts` game facts (`MASTERIES`, `CLASS_SKILLS`, `PASSIVE_REGIONS`, `CLASS_BASE_STATS`, `MASTERY_BONUSES`, `KEYSTONE_BONUSES`, `SKILL_STATS`, `ATTRIBUTE_SCALING`) | hand, patch 1.2.x | simulation, planner, builds, passive pages | REMOVE_AFTER_R2 | API + generated artifact (colors stay) | P10 |
| L-049 | character | `frontend/src/services/buildApi.ts` `CLASS_MASTERIES` | hand duplicate | encounter SkillSelector | REMOVE_AFTER_R2 | `/api/ref/classes` | P06 |
| L-050 | character | `frontend/src/constants/passiveStatMap.ts` | hand mirror of STAT_KEY_MAP | frontend passive stats | REMOVE_AFTER_R2 | property ids resolved server-side | P07 |
| L-051 | character | `passive_stat_resolver.STAT_KEY_MAP`, `skill_tree_resolver._STAT_LABEL_MAP` | name/label → stat | stat resolution | REMOVE_AFTER_R2 | stat mapping by property id (P05 table) | P07 / P08 |
| L-052 | character | `validatePassiveBuild.ts` and `PassiveTreeGraph.tsx` constants (113, 20) | hand | passive pages | REMOVE_AFTER_R2 | derived or declared FORGE_RULE via API | P12 |
| L-053 | character | `frontend/src/data/presets.ts`, `cli.py` sample builds | hand display/seed | UI, dev seed | KEEP_TEMPORARILY | re-expressed with canonical ids | P13 |
| L-054 | sync/ops | `scripts/sync_game_data.py` (transforming sync, SRC_DIR inside the repo) | legacy sync | manual | REMOVE_AFTER_R2 | `scripts/import_canonical_bundle.py` | P01 (then P18) |
| L-055 | sync/ops | `scripts/generate_tree_data.py` | regex patcher of frontend TS | manual | REMOVE_AFTER_R2 | `scripts/build_frontend_data.py` | P10 |
| L-056 | sync/ops | `data/version.json` (`patch_version: unknown`) | sync stamp | `/api/health` | REMOVE_AFTER_R2 | `CANONICAL_DATA_MANIFEST.json` | P19 |
| L-057 | sync/ops | `GameDataPipeline` (`pipeline.py`) + `game_data_loader.py` | legacy runtime loader (`data_version` 'unknown') | app factory, all registries | STILL_REQUIRED | stays until P20 (rollback path); replaced by CanonicalDataStore, removed in P18 | P02 → P18 |
| L-058 | sync/ops | `backend/data/versioning/versioned_loader.py` + `/api/load/game-data` | legacy reload/integrity path | load route | REMOVE_AFTER_R2 | store (immutable; no reload) | P18 |
| L-059 | sync/ops | `AffixRegistry`, `SkillRegistry` (name-keyed), `routes/admin.py` affix file writer | legacy registries / writer | engines, admin | REMOVE_AFTER_R2 | typed registries from the store; no runtime writes to game data | P03 / P05 |
| L-060 | sync/ops | `flask seed`, `reseed-affixes`, `seed-passives` | reference seeding | docker entrypoint, dev compose, manual | REMOVE_AFTER_R2 | none (no reference data in DB) | P14 |
| L-061 | sync/ops | `backend/entrypoint.sh` masking (`2>/dev/null \|\| echo`) | ops | Docker | REMOVE_AFTER_R2 | fail-loud startup | P14 |
| L-062 | sync/ops | `config.py` `CURRENT_PATCH`, `CURRENT_SEASON`, `DATA_VERSION`; `/api/version` fallbacks | hard-coded version | version route, meta snapshot, frontend | REMOVE_AFTER_R2 | manifest | P19 |
| L-063 | sync/ops | Build `patch_version` / `cycle` defaults (model, schema, service, frontend workspace) | client text defaults 1.2.1 / 1.2 | builds | REMOVE_AFTER_R2 | server `data_version`; `declared_patch` kept as history | P13 |
| L-064 | sync/ops | `scripts/sync_game_data.py` `_upstream_trust` carry-through (R1) | trust copy into `data/version.json` | none at runtime | REMOVE_AFTER_R2 | trust in the manifest and store | P01 |
| L-065 | sync/ops | `backend/scripts/r1_forge_consumption_inventory.py` (R1) | inventory tool | R1 evidence | STILL_REQUIRED | keeps measuring consumption during migration | — |
| L-066 | v2 | `docs/generated/v2_*_bundle.json` (11) + `v2_stat_registry.json` | experimental bundles (positional ids, no patch on 8 families) | `/api/experimental/v2/*` | REMOVE_AFTER_R2 | canonical bundle | P18 |
| L-067 | v2 | `docs/generated/v2_modifier_registry.json` | REL-7 corrupt (690 secondary rows) | experimental routes | REMOVE_AFTER_R2 | never consume | P18 |
| L-068 | v2 | `docs/generated/v2_*_report.json`, plans, inventories (38) and `docs/migration/V2_*.md` (38) | point-in-time evidence | none | ARCHIVE | — | P18 |
| L-069 | v2 | `backend/scripts/report_v2_*` generators (7) and report scripts (20), `validate_v2_trusted_data.py` | offline | manual | ARCHIVE | — | P18 |
| L-070 | v2 | `routes/experimental.py` v2 section + double registration (`app/__init__.py:253-254`) | ungated public API (SYS-5, R6) | public | REMOVE_AFTER_R2 | —; gating is R6 and should happen sooner | P18 / R6 |
| L-071 | v2 | `experimental.py` forge-safe section + `routes/debug.py` + forge-safe loaders/config | flag-gated, off by default | affix catalog | KEEP_TEMPORARILY | remove with P05 (affix catalog from the store) | P05 → P18 |
| L-072 | v2 | `backend/app/repositories/v2/*`, `backend/app/normalization/v2/*` | experimental runtime | experimental routes | REMOVE_AFTER_R2 | salvage `is_stable_modifier_eligible` reasons into the trust model | P18 |
| L-073 | v2 | `backend/app/planner_adapters/v2/*` | zero runtime importers | scripts, tests | ARCHIVE | — | P18 |
| L-074 | v2 | `backend/app/api_contracts/v2/response.py` | debug envelope | experimental routes | KEEP_TEMPORARILY | superseded by the R2 envelope (P09) | P09 → P18 |
| L-075 | v2 | `backend/app/data_contracts/*` (`SourceProvenance`, `canonical_id`) | provenance types | v2 generators | KEEP_TEMPORARILY | candidate base for R2 provenance types | P02 / P03 |
| L-076 | v2 | `backend/app/game_data/` offline modules (`bundle_compat`, `bundle_item_*`, `controlled_*`, `le_tools_*`, validators, triage; ~25 modules, ~8k LOC) | offline tooling inside the runtime package | scripts, tests | ARCHIVE | move to `backend/tools/`; `le_tools_*` may serve R4 | P18 |
| L-077 | v2 | `backend/app/game_data/passive_tree_validator.py` | test-only | tests | REMOVE_AFTER_R2 | P07 validator | P07 |
| L-078 | v2 | Frontend v2 debug pages (7 + ForgeSafe + navigation), TrustedData pages, `v2ApiEnvelope.ts`, `v2TrustSummaries.ts`, vite `/experimental` proxy | debug UI (FE-3, DOC-5) | public routes | REMOVE_AFTER_R2 | —; move under IS_DEV is R6 | P18 / R6 |
| L-079 | v2 | `frontend/src/lib/v2TrustStatus.ts`, `v2Limitations.ts`, `components/v2/*` | badge / limitation pattern | v2 pages | KEEP_TEMPORARILY | reuse the pattern with R1/R2 vocabulary in P09/P10 | P10 |

## Sequence

1. **R2-P05 / P07 / P08 / P11 / P06** move readers to the store, behind `CANONICAL_DATA_ENABLED`. Legacy files are still present.
2. **R2-P14** stops reference reads from the DB. Seeds are retired, tables are kept.
3. **R2-P20** switches production.
4. **R2-P18** (after one release), in four steps:
   1. delete REMOVE_AFTER_R2 items;
   2. move ARCHIVE items;
   3. drop the three tables;
   4. empty the T11 allowlist and close the fallback ratchet at zero R2-owned records.
5. **KEEP_TEMPORARILY items** stay until their stated replacement lands. Each must carry a tracking note naming the package or phase (R4, R6) that removes it.
