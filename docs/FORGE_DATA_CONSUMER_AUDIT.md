# Forge Data Consumer Audit

## 1. Purpose

This document audits the current `le-the-forge` consumer application as the published EpochForge.gg app, with `last-epoch-data` treated as the canonical extraction/compiler/source-of-truth repo. It identifies which Last Epoch data families are currently consumed, where they are consumed, what fields are used, whether the usage is production/experimental/planned/dead, and what that implies for a consumer-facing `FORGE_DATA_CONTRACT.md`.

This is a planning audit only. No runtime behavior, UI behavior, refactors, or simulation math were changed.

## 2. Summary

The production app consumes game data from three broad places:

1. **Canonical JSON under `/data` loaded by backend pipeline and endpoints.** The Flask app starts `GameDataPipeline`, loads selected JSON files, builds affix/skill/enemy registries, and rejects mismatched registry `data_version` values. This is the closest thing to the production data contract.
2. **Seeded database models with JSON fallbacks.** Passive nodes, item types, and affixes often try the database first, then fall back to JSON or static lists if the database is empty/unavailable.
3. **Frontend-maintained static data.** Several production UI/simulation paths still use `frontend/src/lib/gameData.ts`, `frontend/src/data/passiveTrees`, and `frontend/src/data/skillTrees` instead of canonical backend data.

Conservative Required Now families are those used by active production routes/pages or production analysis systems. The most important Required Now families are affixes, affix tiers, affix eligibility, base items, item types, unique items, blessings, passives, skill trees, skills/tuning, class/mastery stat data, enemy profiles, and corruption formulas. Metadata is consumed only superficially and should be treated as Required Now as a safety/control-plane family even though the current app does not validate most metadata fields.

The largest correctness risks are HYBRID data paths: frontend hardcoded skill/affix/passive data mixed with backend canonical data, tooltip/prose parsing for unique and skill/passive mechanics, hardcoded fallback skill stats, synthetic passive stat fallbacks, hardcoded enemy archetypes/profiles, and hardcoded corruption formulas.

## 3. Data Loading Architecture

### Backend startup pipeline

`GameDataPipeline` loads these files at startup:

- `data/items/affixes.json`
- `data/entities/enemy_profiles.json`
- `backend/app/game_data/skills.json`
- `backend/app/game_data/classes.json`
- `data/classes/skills_metadata.json`
- `data/items/uniques.json`
- `data/items/rarities.json`
- `data/combat/damage_types.json`
- `data/items/implicit_stats.json`
- `data/progression/blessings.json`
- `data/progression/weaver_tree.json`

It currently does **not** load `data/items/items.json`, `data/items/item_types.json`, `data/items/set_items.json`, `data/classes/community_skill_trees.json`, `data/classes/passives.json`, `data/classes/skill_tree_nodes.json`, `data/world/timelines.json`, or `data/combat/ailments.json` through this central pipeline.

At app creation, the pipeline is loaded once, then `AffixRegistry`, `SkillRegistry`, and `EnemyRegistry` are built from the pipeline. The app checks that the three registry `data_version` values match. This is useful, but it is not a full metadata compatibility check: it does not verify game version, build number, generated timestamp, schema version, pipeline version, validation status, source confidence, stale/deferred markers, or the freshness of optional data families.

### Backend direct JSON loaders outside the pipeline

Several production paths bypass the central pipeline:

- `base_engine.py` loads `data/items/base_items.json` directly.
- `fp_engine.py` loads `data/items/crafting_rules.json` and `data/items/forging_potential_ranges.json` directly.
- `routes/passives.py` falls back to `data/classes/passives.json` if the `PassiveNode` table is empty or DB access fails.
- `routes/skills.py` loads `data/classes/community_skill_trees.json` directly for API skill tree rendering and allocation legality.
- `skill_tree_resolver.py` loads `data/classes/skill_tree_nodes.json` directly for build analysis/stat resolution.
- `routes/ref.py` reads `data/items/affixes.json` directly for seed-compatible fallback data.
- `/api/load/game-data` uses the standalone `RawDataLoader`, `VersionedLoader`, and `DataMapper` for dev/admin integrity reporting.

### Database-backed reference data

The app also consumes seeded reference data from SQLAlchemy models:

- `ItemType` for `/api/ref/item-types`.
- `AffixDef` for `/api/ref/affixes`, with JSON fallback.
- `PassiveNode` for `/api/passives` and `/api/ref/passives`, with JSON fallback in `/api/passives`.

These DB tables are effectively derived game-data caches. Their seed path and source version are not checked at runtime by the consumer.

### Frontend static/generated data

The frontend still includes production-visible data and generated data:

- `frontend/src/lib/gameData.ts` contains manually maintained class skills, skill tuning, affix definitions, passive region metadata, mastery/attribute constants, and helper functions.
- `frontend/src/data/passiveTrees/index.ts` contains generated passive tree data from game assets, but the main `/passives` page currently uses the backend API first.
- `frontend/src/data/skillTrees/index.ts` contains generated skill trees and is a production fallback when the skill-tree API is unavailable.
- `frontend/src/data/iconSpriteMap.json` and `atlasConfig.ts` provide icon display mapping.

## 4. Data Family Requirement Matrix

| Data Family | Requirement Level | Current Consumer(s) | Usage Type | Risk If Missing/Stale | Notes |
|---|---:|---|---|---|---|
| `metadata.json` / dataset metadata | Required Now | `/api/version`; backend registry version match; `/api/load/game-data` version detection | UI display; data safety; dev tooling | High false confidence: app can show patch/version while accepting stale/partial data | No actual `metadata.json` consumer found. Current metadata surface is `VERSION`, app config, `_version/_meta.version` probes, and registry `data_version`. |
| `data/version.json` | Planned / Unknown | No current direct runtime consumer found | Planned metadata | Low immediate runtime risk; high contract gap | `VersionedLoader` probes data-bearing files instead of `data/version.json`. |
| Items / `data/items/items.json` | Unused | No current consumer found | None | None today | Base items and uniques are consumed; the full item catalogue is not. |
| Base items / `data/items/base_items.json` | Required Now | `/api/ref/base-items`; `base_engine`; crafting/base FP helpers | UI display; planner/crafting setup; FP validation | Crafting/base picker and FP ranges become wrong or empty | Direct JSON loader, outside central pipeline. |
| Item types / subtypes | Required Now | `/api/ref/item-types` DB; constants maps in backend and TS; hardcoded fallback list | UI display; slot mapping; planner legality | Wrong slot categories/eligibility; missing selectors | `data/items/item_types.json` is not central source; DB/static constants dominate. Subtype maps are manually generated constants. |
| Affixes | Required Now | `GameDataPipeline`; `AffixRegistry`; `/api/ref/affixes`; craft/BIS target UIs; stat aggregation | UI display; planner legality; stat aggregation; optimizer/BIS | Crafting, BIS, gear stats, and search break or silently degrade | Fields used: `id/affix_id`, `name`, `type`, `stat_key`, `tiers`, `applicable_to`, `class_requirement`, `tags`. |
| Affix tiers | Required Now | Affix domain model; `/api/ref/affixes`; `getAffixValue`; craft/BIS tier sliders | UI display; stat aggregation; optimizer | Tier midpoint/value calculations wrong | Backend expects array tiers with `tier/min/max`; frontend hardcoded affixes use `Tn: [lo, hi]`. Contract should define canonical shape and adapters. |
| Affix eligibility | Required Now | `/api/ref/affixes?slot=...`; frontend target pickers; `GearSlotEditor`; BIS/crafting | Planner legality; UI filtering; optimizer | Invalid affixes shown or valid affixes hidden | Slot vocab is normalized through manual alias maps and constants. |
| Affix tags | Required Now | `/api/ref/affixes?tag=...`; uniques search; target/search UI | UI filtering; planner/search | Search/filter degradation | Tags also carry normalized `experimental`/`personal` affix types. |
| Implicits / `data/items/implicit_stats.json` | Experimental / Planned | `GameDataPipeline`; `/api/ref/implicit-stats`; `Item.apply_to_stat_pool` consumes item instance implicits | UI/API display; stat aggregation when supplied | Low current risk unless gear imports include structured implicits | Endpoint exists, but no obvious production frontend caller found. Unique implicit prose is parsed separately. |
| Uniques / `data/items/uniques.json` | Required Now | `/api/ref/uniques`; `UniqueItemPicker`; build analysis unique stat extraction | UI display; stat aggregation; planner gear selection | Unique picker and unique contribution to simulation incorrect | Fields used: slug/id, `name`, `slot`, `base`, `implicit`, `affixes`, `unique_effects`, `tags`, `lore`. Mechanic extraction parses prose. |
| Sets / `data/items/set_items.json` | Unused | No current runtime consumer found | None | None today | `EquipmentSet` domain exists, but no current canonical set-data loader found. |
| Idols | Required Now | Slot alias/category maps; unique idol slot filtering; affix slot filtering | UI display; planner legality | Idol affixes/uniques missing or incorrectly bucketed | There is no dedicated idol dataset consumed; idols are represented as item/slot categories. |
| Blessings / `data/progression/blessings.json` | Required Now | `GameDataPipeline`; `/api/ref/blessings`; `BlessingsPanel`; build model migration | UI display; build/import-export state | Blessing selector empty/wrong; build state loses blessing semantics | Fields used include timeline `id/name/order/blessings[]`; blessing `id`, names, values as typed in frontend. |
| Passives / `data/classes/passives.json` / DB `PassiveNode` | Required Now | `/api/passives`; `PassiveTreePage`; `passive_stat_resolver`; build analysis | UI display; planner legality; stat aggregation; import/export | Passive planner and analysis stats wrong or empty | API returns `id/raw_node_id/character_class/mastery/mastery_index/mastery_requirement/name/description/node_type/x/y/max_points/connections/requires/stats/ability/icon`. |
| Passive trees / edges/layout | Required Now | `/api/passives`; `PassiveTreePage`; graph utilities; `frontend/src/data/passiveTrees` as generated local data | UI display; planner legality | Allocation legality/pathing wrong | Uses DB/API for main page; local generated data remains a parallel source. |
| Skills / skill stats | Required Now | `SkillRegistry`; `combat_engine`; `/api/ref/skills`; frontend `SKILL_STATS`; build analysis | UI display; DPS simulation; import/export | DPS zero/wrong; skills missing from selectors/search | Backend registry uses `backend/app/game_data/skills.json`; combat has hardcoded fallback. Frontend has its own hardcoded tuning. |
| Skill metadata / `data/classes/skills_metadata.json` | Experimental / Planned | Pipeline; `get_skill_metadata`; `get_skill_base_damage` | Planned DPS metadata | Low immediate production risk | Loader validates Phase-0 damage fields but permits missing/null values. |
| Skill trees / `community_skill_trees.json`, `skill_tree_nodes.json`, frontend generated trees | Required Now | `/api/skills/<id>/tree`; skill allocation PATCH; `SkillTreePanel`; `skill_tree_resolver`; `build_analysis_service` | UI display; planner legality; stat aggregation; DPS simulation modifiers | Skill tree UI/allocation and build analysis modifiers wrong | Multiple formats and sources exist. `SkillTreePanel` silently falls back to local read-only trees when API fails. |
| Enemies / `data/entities/enemy_profiles.json` | Required Now | `GameDataPipeline`; `EnemyRegistry`; `/api/ref/enemy-profiles`; analysis boss endpoints | DPS simulation; EHP/survivability | Boss/corruption analysis unavailable or wrong | Fields used: `id/name/category/description/health/armor/resistances/crit_chance/crit_multiplier/tags`. |
| Timelines / monolith / `data/world/timelines.json` | Planned | No current runtime consumer of timelines found; blessings imply timelines | Planned UI/modeling | Low immediate runtime risk | Blessing timelines are required via blessings, but world timeline data itself is not consumed. |
| Corruption/scaling data | Required Now | `corruption_scaler.py`; analysis routes | DPS simulation; EHP/survivability | Corruption recommendations false | Not data-driven: formulas and breakpoints are hardcoded. Contract should either supply canonical scaling or explicitly mark approximation. |
| Damage types / `data/combat/damage_types.json` | Required Now | Pipeline endpoint; `DamageType` enum/router; skill stats derive damage channels | DPS simulation; UI/API display | Damage routing/scaling wrong | Runtime math mostly uses code enums/constants, not the JSON endpoint. Still required because skill data and calculators depend on stable damage-type vocabulary. |
| Ailments / `data/combat/ailments.json` | Planned / Experimental | Ailment calculators/constants/tests; no central production JSON consumer found | DPS simulation planned/partial | Potential DoT/ailment inaccuracy | Ailment mechanics are mostly code constants and stat fields, not JSON-driven. |
| Minion data | Planned / Experimental | Minion stat fields in `BuildStats`; skill/affix/passive mappings | DPS simulation planned/partial | Minion builds approximate | No canonical minion entity/skill stat dataset consumed. |
| Tooltip/prose parsing | Required Now as debt, not a source family | Unique extraction; passive/skill stat resolvers | Stat aggregation; DPS simulation | High false confidence; ambiguous mechanics can be misparsed | Contract should prefer structured stat/effect records over prose. |
| Weaver tree / `data/progression/weaver_tree.json` | Planned | Pipeline validates and exposes empty scaffold | Planned | None today | Empty scaffold accepted by design. |

## 5. Production Consumers

### Backend production consumers

| File/module | Source loaded/imported | Data family | Fields used | Feature/system | Usage type | Status |
|---|---|---|---|---|---|---|
| `backend/app/__init__.py` | `GameDataPipeline`, `AffixRegistry`, `SkillRegistry`, `EnemyRegistry` | affixes, skills, enemies, data versions | registry `data_version` | App startup | Data loading/safety | Production |
| `backend/app/game_data/pipeline.py` | See startup list above | affixes, enemies, skills, classes, metadata, uniques, rarities, damage types, implicits, blessings, weaver tree | See loaders/properties | Central data cache | Data loading/API/service dependencies | Production |
| `backend/app/routes/ref.py` | DB `ItemType`, `AffixDef`, `PassiveNode`; direct `affixes.json`; pipeline wrappers; base/fp engines | item types, affixes, tiers, tags, eligibility, passives, skills, base items, FP ranges, enemies, damage types, rarities, implicits, uniques, blessings | API-specific serialized fields | `/api/ref/*` | UI display, planner legality, optimizer inputs | Production |
| `backend/app/routes/passives.py` | DB `PassiveNode`; fallback `data/classes/passives.json` | passives/passive trees | node id, raw id, class, mastery, requirements, connections, stats, icon, layout | `/api/passives`, passive planner | UI display, planner legality, stat aggregation inputs | Production |
| `backend/app/routes/skills.py` | `data/classes/community_skill_trees.json`; build skill records | skill trees | id, ability, nodes, maxPoints, requirements, root, allocations | Skill tree UI/API and node allocation | UI display, planner legality, import/export state | Production |
| `backend/app/engines/stat_engine.py` | game-data loader affix helpers; `classes.json`; passive resolver input | affixes, tiers, stat keys, class/mastery stats, passive stats | stat_key, tier midpoint, type, base/mastery/attribute fields | Build stat aggregation | Stat aggregation, EHP/DPS inputs | Production |
| `backend/app/engines/combat_engine.py` | `SkillRegistry`; hardcoded fallback `SKILL_STATS`; enemy profile helper | skills, damage types, ailment stats | base damage, level scaling, attack speed, scaling stats, damage types, added effectiveness | DPS calculation | DPS simulation | Production |
| `backend/app/services/build_analysis_service.py` | `PassiveNode` DB, `get_all_uniques`, skill tree resolver, stat/combat/defense engines | passives, uniques, skill trees, skills, affixes | passive stats, unique implicit/affix prose, skill modifiers | Full build analysis | Stat aggregation, DPS, EHP, optimizer inputs | Production |
| `backend/app/services/passive_stat_resolver.py` | DB `PassiveNode.stats`; hardcoded stat-key map | passives, stat mappings | `stats[].key/value`, node IDs | Build analysis passive resolution | Stat aggregation | Production |
| `backend/app/services/skill_tree_resolver.py` | `data/classes/skill_tree_nodes.json`; hardcoded stat-label parser/maps | skill trees, skill effects | node stats, values, requirements, descriptions/special effects | Skill tree modifier resolution | Stat aggregation, DPS modifiers | Production |
| `backend/app/routes/analysis.py` | pipeline enemies; corruption scaler; boss encounter simulator | enemies, corruption scaling | enemy id/stats/resists; corruption int | Boss/corruption analysis endpoints | DPS simulation, EHP/survivability | Production |
| `backend/app/engines/boss_encounter.py` | boss dict from enemy profiles | enemies | health, armor, resistances, phases if present | Boss encounter simulation | DPS/EHP | Production |
| `backend/app/engines/corruption_scaler.py` | hardcoded formulas | corruption/scaling | breakpoints, health/damage multipliers | Corruption recommendation | DPS/EHP | Production |
| `backend/app/engines/base_engine.py` | `data/items/base_items.json` | base items | name, slot category, min_fp, max_fp, implicit/tags | Base picker/crafting FP | UI display, planner/crafting legality | Production |
| `backend/app/engines/fp_engine.py` | `data/items/crafting_rules.json`, `forging_potential_ranges.json` | crafting rules, FP ranges | cost min/max, rarity min/max | Craft simulation | Optimizer/crafting | Production |
| `backend/app/routes/bis_search.py`, `backend/bis/*` | hardcoded affixes/base items plus request targets | affixes/base items (mock/manual) | affix ids, tiers, slot/base names, FP | BIS search | Optimizer | Production route, but data is experimental/mock-like |

### Frontend production consumers

| File/module | Source | Data family | Fields used | Feature/page/system | Usage type | Status |
|---|---|---|---|---|---|---|
| `frontend/src/lib/api.ts` | `/ref/*`, `/skills/*`, `/passives`, `/version`, `/load/game-data`, `/builds/*/analysis` | API data families | typed response shapes | API client | UI/API | Production |
| `frontend/src/hooks/index.ts` | `refApi` | classes, affixes, item types, base items, FP ranges | API payloads | Shared hooks | UI display | Production |
| `frontend/src/pages/PassiveTreePage.tsx` | `/api/passives`; constants from `gameData.ts` | passives/passive trees, class/mastery | node graph, stats, class/mastery names | Passive planner | UI display, planner legality, stat aggregation | Production |
| `frontend/src/services/passiveTreeService.ts` | `/passives/*` | passives/passive trees | typed node fields | Passive planner | UI/API | Production |
| `frontend/src/logic/computePassiveStats.ts`, `types/passiveEffects`, `constants/passiveStatMap.ts` | API `node.stats`; hardcoded stat map/parser | passives, stat mappings | key/value stat entries | Passive planner stats | Stat aggregation | Production |
| `frontend/src/components/features/build/SkillTreePanel.tsx` | `/skills/<id>/tree`; local `@/data/skillTrees` fallback | skill trees | nodes, root, requirements, icon, name | Build planner skill trees | UI display, planner legality | Production |
| `frontend/src/components/features/build/GearSlotEditor.tsx` | hardcoded `AFFIX_DEFINITIONS` | affixes, tiers, eligibility | name, tier ranges, applicable, stat_key | Build gear editor | UI display, stat aggregation | Production |
| `frontend/src/lib/simulation.ts` | hardcoded `AFFIX_DEFINITIONS`, `SKILL_STATS`, `ATTRIBUTE_SCALING` | affixes, skills, class/stat constants | stat_key, tier values, skill damage/speed/scaling | Client simulation | Stat aggregation, DPS | Production/local simulation |
| `frontend/src/components/features/build/UniqueItemPicker.tsx` | `/ref/uniques` | uniques, idols via slots | name, slot, base, tags, effects | Gear selection | UI display | Production |
| `frontend/src/components/blessings/BlessingsPanel.tsx` | `/ref/blessings` | blessings/timelines | timeline order/name/blessings | Build planner blessings | UI display, import/export state | Production |
| `frontend/src/components/bis/AffixTargetPanel.tsx`, `components/crafting/TargetAffixBuilder.tsx` | `/ref/affixes` through hooks | affixes, tiers | id, name, type, tier targets | BIS/crafting target selection | Optimizer/crafting UI | Production/experimental feature areas |
| `frontend/src/pages/bis/BisSearchPage.tsx` | `/bis/search`; hardcoded preset | affixes | affix ids/names/tiers | BIS search | Optimizer | Production route; experimental quality |
| `frontend/src/components/data/DataManagerDashboard.tsx` | `/version`; mock source table | metadata | app patch only | Data manager | Debug/dev tooling | Production route, mock data reachable |
| `frontend/src/components/navigation/TopBar.tsx` | `/version` | metadata | app version display | Global nav | UI display | Production |
| `frontend/src/components/TreeIcon.tsx` | `iconSpriteMap.json`, `atlasConfig.ts` | icon assets | sprite ids/atlas positions | Passive/skill tree icons | UI display | Production |

## 6. Experimental / Dev Consumers

- `/api/load/game-data` reloads the pipeline and runs partial integrity checks for skills, affixes, enemies, and passives. It is a dev/admin-style endpoint and not a user-facing data compatibility gate.
- `DataManagerDashboard` shows mock source rows and reload steps while only using `/version` for current patch display. This is reachable UI but should be considered debug/admin/planned, not authoritative production validation.
- `DataLoaderPanel` calls `/load/game-data` and displays the dev integrity result.
- BIS workspace variants contain mock result generation and hardcoded base/affix data; the newer `/bis-search` page calls backend BIS, but the backend BIS engine still uses simplified hardcoded affix pools and base items.
- Weaver tree is loaded/validated as an empty scaffold; no active production feature consumes real nodes.
- `skills_metadata.json` base-damage fields are loaded and validated if present, but null/missing values are allowed and the main DPS path still uses `backend/app/game_data/skills.json` plus hardcoded fallback.
- Ailment/minion/scaling data exists mostly in engine constants, enums, and stat maps rather than canonical extracted JSON.

## 7. Hardcoded Data and Approximation Debt

| Debt item | Location(s) | Classification | Why it matters |
|---|---|---:|---|
| Frontend `CLASS_SKILLS`, skill tags, emojis, `SKILL_STATS`, `AFFIX_DEFINITIONS`, `ATTRIBUTE_SCALING` | `frontend/src/lib/gameData.ts`; `frontend/src/lib/simulation.ts`; `GearSlotEditor` | HYBRID risk / production correctness risk | Production UI and client simulation can diverge from backend canonical data and extracted data. |
| Backend hardcoded `SKILL_STATS` fallback | `backend/app/engines/combat_engine.py` | HYBRID risk | If registry is unavailable or a skill is missing, DPS can use stale hardcoded tuning instead of failing loudly. |
| Backend/frontend class/mastery constants and static class skill presets | `routes/ref.py`, `frontend/src/lib/gameData.ts`, constants files | Acceptable temporary adapter / HYBRID risk | Useful for UI, but not canonical and incomplete by class/patch. |
| Static item type fallback list | `backend/app/routes/ref.py` | Acceptable temporary adapter | Keeps UI alive if DB is empty, but hides seeding/data failures and omits many item types/subtypes/idols. |
| Slot aliases and meta-slot categories | `routes/ref.py`, frontend API constants, constants maps | Acceptable temporary adapter | Needed compatibility layer, but should be generated from canonical item-type/subtype/slot vocabulary. |
| Tooltip/prose parsing for unique item stats | `build_analysis_service.py` | Production correctness risk | Unique implicit/affix strings are parsed with regex and midpoint heuristics, likely missing conditional, transformed, or complex mechanics. |
| Skill-tree stat text parser and `_STAT_LABEL_MAP` | `skill_tree_resolver.py` | HYBRID risk / approximation debt | Parses text/stat labels into build stats; unmapped mechanics fall into `special_effects`. Structured effects should come from extraction. |
| Passive stat key maps | `passive_stat_resolver.py`, `frontend/src/constants/passiveStatMap.ts` | HYBRID risk | Manual maps must stay in sync across frontend/backend and with extracted node stat labels. |
| Synthetic passive fallback stat cycle | `stat_engine.py` | Production correctness risk | If real passive data is absent, synthetic bonuses are generated from node IDs. It logs a warning, but callers can still receive plausible false stats. |
| Hardcoded corruption formulas and breakpoints | `corruption_scaler.py` | Approximation debt / production correctness risk | Corruption recommendations are not sourced from extracted canonical scaling data. |
| Hardcoded enemy archetype base stats | `domain/enemy.py` | Approximation debt | Runtime enemy archetypes can bypass canonical enemy profiles. |
| Single-phase boss fallback | `boss_encounter.py` | Acceptable temporary adapter / approximation debt | Enables analysis without phase data but can misrepresent bosses. |
| BIS hardcoded affix pool and base items | `backend/bis/generator/*`; `/bis/search` route defaults | Experimental / production correctness risk if marketed as authoritative | Optimizer does not use canonical affix/base item eligibility or full item catalogue. |
| Data manager mock source rows and reload steps | `DataManagerDashboard` | Harmless UI constant / false-confidence risk | Looks like validation telemetry but is not tied to actual source health. |
| Silent empty defaults for optional pipeline data | `pipeline._load_optional`, many accessors | Silent fallback risk | Missing files can become empty lists/dicts with no user-facing warning. |
| Frontend skill tree API fallback to local static trees | `SkillTreePanel` | HYBRID risk | Users see a read-only local tree when API data is missing; this avoids a crash but can mask stale backend data. |

## 8. Metadata Compatibility Checks

Current checks found:

- App startup detects a version from `affixes.json` and stamps it on affix/enemy/skill domain objects.
- App startup compares `data_version` across affix, skill, and enemy registries and raises on mismatch.
- `/api/version` returns app version, git commit, configured `DATA_VERSION`, configured `CURRENT_PATCH`, and season.
- `VersionedLoader.detect_version()` probes `items/affixes.json`, `entities/enemy_profiles.json`, and `combat/damage_types.json` for `_version` or `_meta.version`.
- `/api/load/game-data` reports detected version source and partial counts/integrity issues for skills, affixes, enemies, and passives.

Missing or insufficient checks:

- No current consumer of a canonical `metadata.json` was found.
- No check for `game_version` beyond configured `CURRENT_PATCH` display.
- No check for build number.
- No check for data patch vs app-supported data patch.
- No check for `generated_at` freshness.
- No schema-version compatibility gate for each family.
- No pipeline-version compatibility gate.
- No validation-status gate from `last-epoch-data`.
- No source-confidence threshold gate.
- No stale/deferred/partial output marker handling.
- Optional loaded families (`uniques`, `rarities`, `damage_types`, `implicit_stats`, `blessings`) can default to empty payloads without blocking startup.
- DB-derived reference tables do not appear tied to source metadata or checked against the JSON dataset version.
- Frontend caches reference data with long/infinite stale times and does not compare metadata/version headers to detect stale client data.

## 9. Silent Fallback / False Confidence Risks

- `/api/ref/affixes` catches broad errors, falls back to direct JSON, and finally returns `ok(data=[])` if both DB and JSON fail. Users can see an empty selector without a patch-readiness failure.
- `/api/ref/item-types` returns a static fallback list when the DB table is empty or the query fails.
- `/api/passives` falls back to `data/classes/passives.json` when the DB has no rows; helpful but it hides DB seed failures and has no source-version check.
- `GameDataPipeline._load_optional()` returns empty defaults for optional datasets, so missing uniques/blessings/damage types/implicits can reach APIs as empty data.
- `combat_engine._get_skill_def()` falls back to hardcoded `SKILL_STATS` if the skill registry is not present.
- `combat_engine.calculate_dps()` returns zero DPS for unknown skills instead of blocking analysis.
- `stat_engine` can synthesize passive stats from node IDs if real passive stats are not supplied; it logs warnings but returns plausible stats.
- `SkillTreePanel` silently falls back to local generated trees when the API tree is unavailable. It disables allocation writes for local trees but still renders a tree.
- `UniqueItemPicker` treats missing API data as an empty item list (`res?.data ?? []`).
- `BlessingsPanel` shows “No blessing timelines available” on an empty successful payload; it only warns on request error, not on empty/stale data.
- `DataManagerDashboard` uses mock source rows and simulated reload steps, creating a risk that users/operators interpret them as real pipeline health.
- BIS search has real endpoints but simplified hardcoded candidate/affix data; results can look authoritative while not representing canonical game data.

## 10. Recommended Updates to `FORGE_DATA_CONTRACT.md`

1. Add a **consumer requirement matrix** matching this audit, with Required Now families clearly separated from Experimental, Planned, and Unused.
2. Define a required `metadata.json` (or equivalent manifest) including:
   - game version
   - build number
   - data patch
   - generated_at
   - schema version per family
   - pipeline version
   - validation status
   - source confidence
   - stale/deferred/partial output markers
3. Require each data family to declare source status and freshness so `le-the-forge` can fail loudly or degrade visibly.
4. Standardize affix schema across backend/frontend:
   - stable id and numeric game id
   - display name
   - type/category
   - stat_key/effect ids
   - tier ranges
   - eligible item types/subtypes/slots
   - class/mastery requirements
   - tags
5. Add canonical slot/item-type/subtype vocabulary, including idols and meta-slot mappings, so consumer adapters can be generated instead of manually maintained.
6. Add structured unique item effects and implicit stats. Do not require consumers to parse tooltip prose for mechanics.
7. Add structured passive and skill tree node effects, including conditional/proc/special effect flags, so stat resolvers do not rely on label maps and prose parsing.
8. Add canonical skill tuning fields required for DPS:
   - base damage
   - damage types
   - attack/cast speed
   - level scaling
   - added damage effectiveness
   - hit count / interval
   - mana cost
   - minion ownership/scaling metadata where relevant
9. Add enemy/boss schema that supports phases, armor/resistances, damage profile, tags, boss/category, and monolith/corruption compatibility.
10. Add canonical corruption/scaling data or explicitly mark formulas as consumer approximations until extracted.
11. Include a consumer compatibility contract: `le-the-forge` should know which data families must block patch-day readiness and which may be empty/experimental.
12. Include “no silent fallback” guidance: fallback data should include visible warnings and metadata indicating fallback mode.

## 11. Recommended Next Implementation Targets

1. **Implement consumer metadata gate.** Load a canonical dataset manifest at backend startup and expose it via `/api/version` or `/api/data-status`; validate game version, schema versions, generated_at, validation status, and stale/deferred markers.
2. **Replace frontend `AFFIX_DEFINITIONS` and `SKILL_STATS` with API/canonical data or visibly mark client simulation as legacy/local.** This removes major HYBRID risk.
3. **Make optional Required Now datasets fail loudly.** Missing/empty uniques, blessings, base items, affixes, passives, skill trees, enemies, and skills should block affected production features or display explicit warnings.
4. **Move unique/passive/skill tree mechanics from prose parsing to structured extracted effects.** Keep prose for display only.
5. **Generate slot/item-type/subtype/idol adapters from canonical data.** Remove manual alias drift where possible.
6. **Data-drive corruption scaling or label it as approximation in UI/API responses.**
7. **Separate experimental/dev routes in UI.** BIS mock/simplified data and Data Manager mock statuses should be labeled clearly until backed by canonical data health.

## 12. Open Questions

- Should `metadata.json` be a single repo-level manifest, per-family `_meta`, or both?
- Which fields in `last-epoch-data` are stable IDs vs display/localized IDs for affixes, items, passives, and skill-tree nodes?
- Should `items.json` become the Required Now source for base items and uniques, or should base/unique files remain separate consumer contracts?
- Are idols a standalone family in `last-epoch-data`, or should they be treated as item types/subtypes plus affix eligibility?
- What minimum validation status/source-confidence should block patch-day readiness?
- Should `le-the-forge` fail startup on missing Required Now families, or only block specific routes/features with visible warnings?
- Which skill damage/tuning fields are extractable today, and which must remain manual until the compiler supports them?
- Can corruption scaling be extracted directly, or should it be versioned as a documented consumer approximation?
- Should DB seed state include a source dataset hash/version so the app can detect stale derived tables?
