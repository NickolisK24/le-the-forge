# Full Repository Audit

## 1. Product Purpose

The Forge is a deterministic Last Epoch build analysis and simulation platform. The product is intended to help players inspect build legality, stat truth, combat performance, survivability, crafting outcomes, and upgrade priorities while making uncertainty visible.

Current user-facing features appear across:

- Build planning and reports: `frontend/src/components/features/build/BuildPlannerPage.tsx`, `frontend/src/components/features/builds/ReportPage.tsx`, `backend/app/routes/builds.py`, `backend/app/routes/report.py`.
- Simulation and stat analysis: `frontend/src/pages/simulation/SimulationPage.tsx`, `frontend/src/components/features/build/SimulationDashboard.tsx`, `backend/app/routes/simulate.py`, `backend/app/services/simulation_service.py`.
- Crafting: `frontend/src/components/features/craft/CraftSimulatorPage.tsx`, `frontend/src/pages/crafting/CraftingPage.tsx`, `backend/app/routes/craft.py`, `backend/app/services/craft_service.py`.
- Optimizer and BIS search: `frontend/src/components/features/optimizer/OptimizerPage.tsx`, `frontend/src/pages/bis/BisSearchPage.tsx`, `backend/app/routes/optimize.py`, `backend/app/routes/bis_search.py`.
- Import from external planners: `frontend/src/components/import/ImportPanel.tsx`, `backend/app/routes/import_route.py`, `backend/app/services/importers/lastepochtools_importer.py`, `backend/app/services/importers/maxroll_importer.py`.
- Passive and skill tree work: `frontend/src/pages/PassiveTreePage.tsx`, `frontend/src/components/PassiveTree/`, `frontend/src/components/features/build/SkillTreePanel.tsx`, `backend/app/routes/passives.py`, `backend/app/routes/skills.py`.

`docs/FORGE_SYSTEM_PILLARS.md` defines the product direction around legality, stat truth, combat insight, survivability insight, upgrade guidance, and transparency. It also defines the intended feature status model:

- Authoritative: should be reserved for validated, canonical-ready data and deterministic logic.
- Advisory: useful but backed by partial, approximate, or lower-confidence data.
- Experimental: sandbox or early systems with incomplete mechanics.

Current verified or relatively strong areas include the deterministic stat pipeline, seeded Monte Carlo behavior, craft RNG determinism, EHP/resistance capping, and portions of build import, as described in `docs/KNOWN_LIMITATIONS.md`. Current advisory or incomplete areas include skill base damage approximations, enemy armour/resistance profiles, ailment verification, Maxroll import confidence, passive stat coverage gaps, minion DPS, conditional DPS integration, and armour shred accumulation.

## 2. Repository Structure

Top-level repository structure:

- `backend/`: Flask backend, calculation engines, services, routes, tests, migrations, scripts, and diagnostic modules.
- `frontend/`: React 18, TypeScript, Vite, Tailwind frontend.
- `data/`: production-facing static game data used by the current Forge app.
- `docs/`: architecture docs, limitations, data bundle docs, migration diagnostics, and generated reports.
- `scripts/`: workspace checks, data sync utilities, image/icon tooling, passive tree utilities, and cross-repo smoke tests.
- `electron/`: optional desktop wrapper scaffold.
- `.github/workflows/`: CI configuration.

Backend structure:

- App factory and extension wiring: `backend/app/__init__.py`.
- Routes: `backend/app/routes/`.
- Services: `backend/app/services/`.
- Importers: `backend/app/services/importers/`.
- Calculation engines: `backend/app/engines/`.
- Domain/data registries: `backend/app/domain/`, `backend/data/registries/`, `backend/app/game_data/`.
- Constants and hardcoded mappings: `backend/app/constants/`.
- Developer diagnostics: `backend/app/game_data/`, `backend/scripts/`.
- Tests: `backend/tests/`.

Frontend structure:

- App routes: `frontend/src/App.tsx`.
- Pages: `frontend/src/pages/`.
- Feature components: `frontend/src/components/features/`.
- Shared UI/components: `frontend/src/components/ui/`, `frontend/src/components/layout/`, `frontend/src/components/navigation/`.
- API clients: `frontend/src/lib/api.ts`, `frontend/src/services/`.
- State: `frontend/src/store/`.
- Logic utilities: `frontend/src/logic/`.
- Frontend static tree/data helpers: `frontend/src/data/`.
- Frontend tests: `frontend/src/__tests__/`.

Data/static files:

- Item data: `data/items/`.
- Class and skill data: `data/classes/`.
- Combat data: `data/combat/`.
- Enemy data: `data/entities/`.
- Localization: `data/localization/`.
- Progression/world data: `data/progression/`, `data/world/`.
- Backend package-local game data: `backend/app/game_data/skills.json`, `backend/app/game_data/classes.json`, `backend/app/game_data/constants.json`.

Generated diagnostics:

- `docs/generated/bundle_item_adapter_map_report.md`
- `docs/generated/le_tools_import_context_fixture_report.md`
- `docs/generated/le_tools_importer_fixture_context_report.md`
- `docs/generated/le_tools_offline_buildinfo_context_report.md`
- `docs/generated/le_tools_import_stage_context_report.md`
- `docs/generated/le_tools_import_context_sidecar_report.md`
- `docs/generated/le_tools_import_context_sidecar_validation_report.md`
- `docs/generated/le_tools_import_context_sidecar_saved_fixture_validation_report.md`

## 3. Backend Architecture

The backend is a Flask application built by `backend/app/__init__.py`. It initializes SQLAlchemy, Flask-Migrate, JWT, CORS, rate limiting, logging, security headers, and the game data pipeline. It registers blueprints for auth, builds, imports, crafting, references, passives, simulation, optimization, rotations, conditional simulation, multi-target simulation, admin, jobs, version, BIS, skills, entities, comparisons, meta, reports, health, and views.

Important backend route files include:

- `backend/app/routes/import_route.py`
- `backend/app/routes/simulate.py`
- `backend/app/routes/craft.py`
- `backend/app/routes/optimize.py`
- `backend/app/routes/bis_search.py`
- `backend/app/routes/passives.py`
- `backend/app/routes/skills.py`
- `backend/app/routes/entities.py`
- `backend/app/routes/builds.py`
- `backend/app/routes/health.py`

Services coordinate application behavior:

- Build analysis and persistence: `backend/app/services/build_service.py`, `backend/app/services/build_analysis_service.py`, `backend/app/services/build_report_service.py`.
- Simulation orchestration: `backend/app/services/simulation_service.py`.
- Crafting: `backend/app/services/craft_service.py`.
- Passive and skill resolution: `backend/app/services/passive_stat_resolver.py`, `backend/app/services/skill_tree_resolver.py`.
- Encounter/multi-target orchestration: `backend/app/services/state_encounter_integration.py`, `backend/app/services/multi_target_encounter.py`.
- Meta analytics: `backend/app/services/meta_analytics_service.py`.
- Discord/import failure notification: `backend/app/services/discord_notifier.py`.

Importers live under `backend/app/services/importers/`:

- `base_importer.py`
- `importer_factory.py`
- `lastepochtools_importer.py`
- `maxroll_importer.py`

Calculation engines live under `backend/app/engines/`. `docs/engine_architecture.md` describes these as pure calculation modules with no database access, HTTP requests, or side effects. Important modules include:

- Stat pipeline: `backend/app/engines/stat_engine.py`, `backend/app/engines/stat_resolution_pipeline.py`.
- Combat: `backend/app/engines/combat_engine.py`, `backend/app/engines/combat_simulator.py`.
- Defense: `backend/app/engines/defense_engine.py`.
- Crafting: `backend/app/engines/craft_engine.py`, `backend/app/engines/craft_simulator.py`, `backend/app/engines/fp_engine.py`.
- Optimization and ranking: `backend/app/engines/optimization_engine.py`, `backend/app/engines/build_optimizer.py`, `backend/app/engines/sensitivity_analyzer.py`, `backend/app/engines/efficiency_scorer.py`, `backend/app/engines/upgrade_ranker.py`, `backend/app/engines/gear_upgrade_ranker.py`.
- Encounters and corruption: `backend/app/engines/boss_encounter.py`, `backend/app/engines/corruption_scaler.py`.
- Items and affixes: `backend/app/engines/item_engine.py`, `backend/app/engines/base_engine.py`, `backend/app/engines/affix_engine.py`.

Game data loading uses `backend/app/game_data/pipeline.py` as the app startup pipeline. It loads from `data/` and package-local `backend/app/game_data/*.json`, then stores data on `app.extensions["game_data"]`. It also initializes registries in `backend/app/__init__.py`:

- `app.domain.registries.skill_registry.SkillRegistry`
- `app.domain.registries.affix_registry.AffixRegistry`
- `app.domain.registries.enemy_registry.EnemyRegistry`

Known hardcoded/static data exists in:

- `backend/app/constants/base_type_id_to_item_type_id.py`
- `backend/app/constants/item_type_ids.py`
- `backend/app/constants/item_type_to_slot.py`
- `backend/app/constants/game_type_to_item_type_id.py`
- `backend/app/constants/sub_type_id_to_item_type_id.py`
- `backend/app/constants/classes.py`
- `backend/app/constants/combat.py`
- `backend/app/constants/crafting.py`
- Skill fallback definitions mentioned in `docs/engine_architecture.md` around `backend/app/engines/combat_engine.py`.

## 4. Frontend Architecture

The frontend is a React/Vite application. Routing is centralized in `frontend/src/App.tsx` with `BrowserRouter`, `Routes`, React Query, auth bootstrap, and development-only debug routes.

Production-facing routes include:

- `/`: `frontend/src/pages/DashboardPage.tsx`
- `/home`: `frontend/src/components/features/HomePage.tsx`
- `/builds`: `frontend/src/components/features/builds/BuildsPage.tsx`
- `/build`: `frontend/src/components/features/build/BuildPlannerPage.tsx`
- `/workspace/*`: `frontend/src/components/features/build-workspace/UnifiedBuildPage.tsx`
- `/craft`, `/crafting`, `/crafting-workspace`
- `/affixes`
- `/passives`
- `/compare`
- `/report/:slug`
- `/meta`
- `/encounter`
- `/optimizer`
- `/rotation`
- `/conditional`
- `/multi-target`
- `/data-manager`
- `/monte-carlo`
- `/classes`
- `/bis-search`
- `/profile`

Development-only debug routes in `frontend/src/App.tsx` are conditionally registered when `import.meta.env.DEV` is true:

- `/movement-debug`
- `/viz-debug`
- `/craft-debug`
- `/debug`
- `/data-flow`

State and API patterns:

- Zustand state is used in `frontend/src/store/`, including `frontend/src/store/buildWorkspace.ts`.
- TanStack Query is configured in `frontend/src/App.tsx`.
- Backend API access is centralized in `frontend/src/lib/api.ts` and feature clients under `frontend/src/services/`.
- Build import/export logic exists under `frontend/src/logic/importBuild.ts`, `frontend/src/logic/exportBuild.ts`, and `frontend/src/services/sharing/`.

Major component areas include:

- Build UI: `frontend/src/components/features/build/`, `frontend/src/pages/build/`.
- Crafting UI: `frontend/src/components/crafting/`, `frontend/src/components/features/craft/`, `frontend/src/pages/crafting/`.
- BIS/optimizer UI: `frontend/src/components/bis/`, `frontend/src/components/features/optimizer/`, `frontend/src/pages/bis/`.
- Passive tree UI: `frontend/src/components/PassiveTree/`, `frontend/src/components/passives/`.
- Diagnostics/debug UI: `frontend/src/components/diagnostics/`, `frontend/src/pages/debug/`.
- Import UI: `frontend/src/components/import/ImportPanel.tsx`.

No bundle item type/base item migration is wired into frontend behavior.

## 5. Data Architecture

The current application data source is still local Forge static data, not the `last-epoch-data` bundle.

Current production-facing static data lives under `data/`:

- `data/items/item_types.json`: 25 current Forge item type records.
- `data/items/base_items.json`: 20 top-level grouped item type buckets and 115 flattened base item records per the bundle diff diagnostic.
- `data/items/affixes.json`: 1163 affix records.
- `data/items/uniques.json`: 403 unique item records by non-meta key count.
- `data/entities/enemy_profiles.json`: 8 enemy profiles.
- `data/classes/passives.json`: 541 passive nodes.
- `data/classes/skills_metadata.json`: 161 non-meta skill metadata entries by current JSON key count.
- `data/version.json`: current data version metadata.

The startup pipeline in `backend/app/game_data/pipeline.py` loads affixes, enemies, skills, classes, skills metadata, uniques, rarities, damage types, implicit stats, blessings, and the Weaver tree. It treats missing optional files as warnings in some cases, but malformed JSON can raise startup failures.

Data classifications:

- Static/production-facing: `data/items/*.json`, `data/classes/*.json`, `data/entities/*.json`, `data/combat/*.json`, `data/progression/*.json`, `data/world/*.json`.
- Backend constants and mappings: `backend/app/constants/*.py`.
- Package-local fallback/engine data: `backend/app/game_data/skills.json`, `backend/app/game_data/classes.json`, `backend/app/game_data/constants.json`.
- Diagnostic-only bundle and importer artifacts: `backend/app/game_data/bundle_*.py`, `backend/app/game_data/le_tools_import_*`, `backend/tests/fixtures/bundle_item_type_*.json`, `backend/tests/fixtures/le_tools_*`, `docs/generated/*.md`.
- Generated or report-only diagnostics: `docs/generated/`.

HYBRID risk remains high in item data because current Forge production paths combine static JSON, backend constants, import-derived IDs, and diagnostic bundle mappings. The bundle `item_types` and `base_items` are not production sources yet.

## 6. Bundle / last-epoch-data Integration

The bundle integration is read-only and diagnostic-only.

Compatibility reader:

- Module: `backend/app/game_data/bundle_compat.py`
- CLI: `backend/scripts/check_data_bundle.py`
- Tests: `backend/tests/test_data_bundle_compat.py`
- Docs: `docs/DATA_BUNDLE_COMPATIBILITY.md`

The reader inspects `metadata.json`, `manifest.json`, `validation_status.json`, and optional reports under `D:\Forge\last-epoch-data\data_bundle`. It classifies status as `compatible`, `compatible_with_warnings`, or `incompatible`. It does not load production family data into Forge loaders.

Cross-repo smoke test:

- Script: `scripts/smoke_data_bundle_handoff.ps1`
- Docs: `docs/DATA_BUNDLE_COMPATIBILITY.md`

Item bundle diff diagnostic:

- Module: `backend/app/game_data/bundle_item_diff.py`
- CLI: `backend/scripts/diff_bundle_items.py`
- Tests: `backend/tests/test_bundle_item_diff.py`
- Docs: `docs/BUNDLE_ITEM_DIFF_DIAGNOSTIC.md`

Adapter report and mapping diagnostics:

- Module: `backend/app/game_data/bundle_item_adapter_report.py`
- CLI: `backend/scripts/report_bundle_item_adapter_map.py`
- Tests: `backend/tests/test_bundle_item_adapter_report.py`
- Report: `docs/generated/bundle_item_adapter_map_report.md`
- Planning doc: `docs/BUNDLE_ITEM_ADAPTER_MAP_PROPOSAL.md`

Reviewed mapping and translation fixtures:

- Review fixture: `backend/tests/fixtures/bundle_item_type_mapping_review.json`
- Review loader: `backend/app/game_data/bundle_item_mapping_review.py`
- Tests: `backend/tests/test_bundle_item_mapping_review.py`
- Needs-adapter review: `docs/BUNDLE_ITEM_NEEDS_ADAPTER_REVIEW.md`
- Translation fixture: `backend/tests/fixtures/bundle_item_type_adapter_translations.json`
- Translation loader: `backend/app/game_data/bundle_item_adapter_translations.py`
- Tests: `backend/tests/test_bundle_item_adapter_translations.py`

Dry-run resolver and context coverage:

- Resolver: `backend/app/game_data/bundle_item_type_dry_run_resolver.py`
- Resolver CLI: `backend/scripts/dry_run_bundle_item_type_resolver.py`
- Resolver tests: `backend/tests/test_bundle_item_type_dry_run_resolver.py`
- Context report: `backend/app/game_data/bundle_item_type_context_report.py`
- Context CLI: `backend/scripts/report_bundle_item_type_context.py`
- Context tests: `backend/tests/test_bundle_item_type_context_report.py`
- Usage audit: `docs/BUNDLE_ITEM_TYPE_CONTEXT_USAGE_AUDIT.md`

Current bundle facts from generated diagnostics:

- Bundle `item_types`: 50 records.
- Bundle `base_items`: 1508 records.
- Forge static item types: 25 records in `data/items/item_types.json`.
- Forge backend item type IDs: 30.
- Forge `base_type_id` mappings: 34.
- Forge base items: 115 flattened records.
- Base item name overlap: 17 normalized names.
- Precise base item comparison is blocked because `data/items/base_items.json` lacks `base_type_id` and `subtype_id`.

Current mapping review state:

- accepted: 19
- needs_adapter: 15
- needs_review: 9
- deferred: 8
- unsafe: 0
- `production_safe`: false globally and per mapping.

No production loader consumes bundle item type or base item IDs.

## 7. Importer Systems

LE Tools importer:

- Production importer: `backend/app/services/importers/lastepochtools_importer.py`.
- Import route: `backend/app/routes/import_route.py`.
- Tests: `backend/tests/test_importers.py`, `backend/tests/test_build_import.py`.

The LE Tools importer parses embedded `window["buildInfo"]` payloads and maps class, mastery, passives, skill trees, HUD slots, and equipment. Its docstring states relevant equipment fields include `baseTypeID` and affixes. It reads or derives item context from fields such as `id`, `baseTypeID`, `baseType`, and `base_type_id`, and emits mapped gear with `base_type_id`.

Maxroll importer:

- Production importer: `backend/app/services/importers/maxroll_importer.py`.
- Current confidence is lower per `docs/KNOWN_LIMITATIONS.md`; Maxroll import is not exhaustively validated against live URLs.

Developer-only LE Tools import context diagnostics:

- Context report: `backend/app/game_data/le_tools_import_context_report.py`
- CLI: `backend/scripts/report_le_tools_import_context.py`
- Tests: `backend/tests/test_le_tools_import_context_report.py`
- Docs: `docs/LE_TOOLS_IMPORT_CONTEXT_DRY_RUN.md`
- Representative parsed fixture: `backend/tests/fixtures/le_tools_parsed_gear_context_sample.json`
- Generated fixture report: `docs/generated/le_tools_import_context_fixture_report.md`

Importer fixture and offline context diagnostics:

- Fixture audit: `docs/LE_TOOLS_IMPORTER_FIXTURE_CONTEXT_AUDIT.md`
- Generated fixture audit report: `docs/generated/le_tools_importer_fixture_context_report.md`
- Offline buildInfo fixture: `backend/tests/fixtures/le_tools_offline_buildinfo_equipment_sample.json`
- Stage context fixture: `backend/tests/fixtures/le_tools_offline_buildinfo_stage_context_sample.json`
- Stage report module: `backend/app/game_data/le_tools_import_stage_context_report.py`
- Stage report CLI: `backend/scripts/report_le_tools_import_stage_context.py`
- Stage tests: `backend/tests/test_le_tools_importer_stage_context.py`
- Generated stage report: `docs/generated/le_tools_import_stage_context_report.md`

Sidecar diagnostics:

- Design: `docs/LE_TOOLS_IMPORT_CONTEXT_SIDECAR_DESIGN.md`
- Builder: `backend/app/game_data/le_tools_import_context_sidecar.py`
- Builder CLI: `backend/scripts/build_le_tools_import_context_sidecar.py`
- Builder tests: `backend/tests/test_le_tools_import_context_sidecar.py`
- Saved sidecar fixture: `backend/tests/fixtures/le_tools_import_context_sidecar_current.json`
- Validator: `backend/app/game_data/le_tools_import_context_sidecar_validator.py`
- Validator CLI: `backend/scripts/validate_le_tools_import_context_sidecar.py`
- Validator tests: `backend/tests/test_le_tools_import_context_sidecar_validator.py`
- Generated reports:
  - `docs/generated/le_tools_import_context_sidecar_report.md`
  - `docs/generated/le_tools_import_context_sidecar_validation_report.md`
  - `docs/generated/le_tools_import_context_sidecar_saved_fixture_validation_report.md`

Current importer context findings:

- Current synthetic/offline sidecar has 12 items.
- Raw/source stage has `base_type_id` for 9 records.
- Mapped output preserves `base_type_id` for 9 records.
- Mapped output does not expose item type context for 12 records.
- 11 records require test-only raw/mapped pairing in diagnostics.
- Resolver results: 8 resolved, 2 `needs_context`, 1 `needs_review`, 1 `unresolved`.
- `production_safe` remains false globally and per item.

Boundaries:

- Production importer output was not changed.
- Import routes were not changed.
- Diagnostics consume copied or saved fixture data.
- No live LET URL shape is proven by the synthetic/offline fixtures.

## 8. Simulation and Calculation Systems

The simulation/calculation architecture is documented in `docs/engine_architecture.md` and `docs/simulation_design.md`.

Deterministic or strongly tested systems:

- 8-layer stat pipeline: `backend/app/engines/stat_resolution_pipeline.py`, `backend/app/engines/stat_engine.py`.
- DPS and combat calculations: `backend/app/engines/combat_engine.py`, `backend/app/engines/combat_simulator.py`.
- Defense/EHP: `backend/app/engines/defense_engine.py`.
- Craft RNG determinism: `backend/app/engines/craft_engine.py`, `backend/app/engines/craft_simulator.py`, `backend/app/engines/fp_engine.py`.
- Optimization/sensitivity: `backend/app/engines/optimization_engine.py`, `backend/app/engines/sensitivity_analyzer.py`, `backend/app/engines/build_optimizer.py`.
- Boss/corruption: `backend/app/engines/boss_encounter.py`, `backend/app/engines/corruption_scaler.py`.

Approximate or incomplete systems called out in `docs/KNOWN_LIMITATIONS.md`:

- 34 skill base damage values are calibrated estimates.
- Ailment DPS formulas need live reconciliation.
- Enemy armour/resistance profiles in `data/entities/enemy_profiles.json` are community-sourced approximations.
- Maxroll build import is not exhaustively validated.
- Passive stat resolution still preserves many entries in `special_effects`.
- Minion DPS is not modeled.
- Conditional stat bonuses are not fully wired into DPS.
- Armour-shred accumulation over fight duration is not modeled.

Hardcoded/fallback risks:

- `docs/engine_architecture.md` notes hardcoded `SKILL_STATS` fallback in `backend/app/engines/combat_engine.py`.
- Item type and slot mappings exist in `backend/app/constants/*.py`.
- Current static base item records in `data/items/base_items.json` lack source composite IDs needed for canonical bundle matching.

## 9. Tests and Validation

Backend tests are extensive under `backend/tests/`. Areas include:

- Architecture/determinism: `test_architecture.py`, `test_architecture_determinism.py`, `test_determinism_lock.py`.
- Simulation/combat: `test_combat_engine.py`, `test_combat_regression.py`, `test_full_combat_loop.py`, `test_simulation_determinism.py`.
- Stat pipeline: `test_stat_engine.py`, `test_stat_resolution_pipeline.py`, `test_stat_pipeline_extended.py`.
- Crafting: `test_craft_engine.py`, `test_craft_simulator.py`, `test_crafting_*`.
- Optimization/BIS: `test_optimization_*`, `test_bis_*`.
- Importers: `test_importers.py`, `test_build_import.py`.
- Game data: `test_game_data_*`, `test_raw_data_loader.py`, `test_versioned_loader.py`.
- Bundle diagnostics: `test_data_bundle_compat.py`, `test_bundle_item_diff.py`, `test_bundle_item_adapter_report.py`, `test_bundle_item_mapping_review.py`, `test_bundle_item_adapter_translations.py`, `test_bundle_item_type_dry_run_resolver.py`, `test_bundle_item_type_context_report.py`.
- LE Tools context diagnostics: `test_le_tools_import_context_report.py`, `test_le_tools_importer_fixture_context.py`, `test_le_tools_importer_stage_context.py`, `test_le_tools_import_context_sidecar.py`, `test_le_tools_import_context_sidecar_validator.py`.

Frontend tests live under `frontend/src/__tests__/` and cover store behavior, routes/layout, design system, hooks, components, phase UI workflows, pages, and feature components.

Safe focused backend diagnostic check previously used:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe -m pytest tests\test_le_tools_import_context_sidecar_validator.py tests\test_le_tools_import_context_sidecar.py tests\test_le_tools_importer_stage_context.py tests\test_le_tools_importer_fixture_context.py tests\test_importers.py tests\test_le_tools_import_context_report.py tests\test_bundle_item_type_context_report.py tests\test_bundle_item_type_dry_run_resolver.py tests\test_bundle_item_adapter_translations.py tests\test_bundle_item_mapping_review.py tests\test_bundle_item_adapter_report.py tests\test_bundle_item_diff.py tests\test_data_bundle_compat.py -q
```

Previous focused result for this diagnostic suite was 123 passed and 1 skipped.

Other useful checks:

```powershell
cd D:\Forge\le-the-forge
powershell -ExecutionPolicy Bypass -File .\scripts\check_forge_workspace.ps1
```

```powershell
cd D:\Forge\le-the-forge\backend
FLASK_APP=wsgi.py PYTHONPATH=. flask validate-data
```

```powershell
cd D:\Forge\le-the-forge\frontend
npx tsc --noEmit
```

Known caution from prior broader import testing: `tests/test_build_import.py` has had unrelated `TestBaseItemDecoding` failures in some local runs when unique item lookup loaded `{}` or failed to decode `uniques.json`. Importer warnings have also appeared around “Working outside of application context” for skill ID map loading and `charmap` decode errors for `uniques.json`. Treat those as existing environment/data loading risks unless reproduced and triaged directly.

No tests were run for this audit document because this task changed documentation only.

## 10. Current Completed Migration Milestones

Completed or documented milestones in `le-the-forge`:

1. Forge system pillars: `docs/FORGE_SYSTEM_PILLARS.md`.
2. Workspace health check: `scripts/check_forge_workspace.ps1`, `docs/WORKSPACE_HEALTHCHECK.md`.
3. Bundle compatibility reader: `backend/app/game_data/bundle_compat.py`, `backend/scripts/check_data_bundle.py`, `backend/tests/test_data_bundle_compat.py`, `docs/DATA_BUNDLE_COMPATIBILITY.md`.
4. Cross-repo handoff smoke test: `scripts/smoke_data_bundle_handoff.ps1`.
5. Item bundle diff diagnostic: `backend/app/game_data/bundle_item_diff.py`, `backend/scripts/diff_bundle_items.py`, `backend/tests/test_bundle_item_diff.py`, `docs/BUNDLE_ITEM_DIFF_DIAGNOSTIC.md`.
6. Adapter mapping report: `backend/app/game_data/bundle_item_adapter_report.py`, `backend/scripts/report_bundle_item_adapter_map.py`, `backend/tests/test_bundle_item_adapter_report.py`, `docs/generated/bundle_item_adapter_map_report.md`.
7. Mapping assumption tests: `backend/tests/test_bundle_item_adapter_report.py`.
8. Reviewed mapping fixture: `backend/tests/fixtures/bundle_item_type_mapping_review.json`, `backend/app/game_data/bundle_item_mapping_review.py`, `backend/tests/test_bundle_item_mapping_review.py`.
9. Needs-adapter review: `docs/BUNDLE_ITEM_NEEDS_ADAPTER_REVIEW.md`.
10. Adapter translation fixture: `backend/tests/fixtures/bundle_item_type_adapter_translations.json`, `backend/app/game_data/bundle_item_adapter_translations.py`, `backend/tests/test_bundle_item_adapter_translations.py`.
11. Dry-run resolver: `backend/app/game_data/bundle_item_type_dry_run_resolver.py`, `backend/scripts/dry_run_bundle_item_type_resolver.py`, `backend/tests/test_bundle_item_type_dry_run_resolver.py`.
12. Context coverage report: `backend/app/game_data/bundle_item_type_context_report.py`, `backend/scripts/report_bundle_item_type_context.py`, `backend/tests/test_bundle_item_type_context_report.py`.
13. LET import context dry-run: `backend/app/game_data/le_tools_import_context_report.py`, `backend/scripts/report_le_tools_import_context.py`, `backend/tests/test_le_tools_import_context_report.py`, `docs/LE_TOOLS_IMPORT_CONTEXT_DRY_RUN.md`.
14. Parsed gear fixture: `backend/tests/fixtures/le_tools_parsed_gear_context_sample.json`, `docs/generated/le_tools_import_context_fixture_report.md`.
15. Importer fixture context audit: `docs/LE_TOOLS_IMPORTER_FIXTURE_CONTEXT_AUDIT.md`, `docs/generated/le_tools_importer_fixture_context_report.md`.
16. Offline buildInfo fixture: `backend/tests/fixtures/le_tools_offline_buildinfo_equipment_sample.json`, `backend/tests/test_le_tools_importer_fixture_context.py`, `docs/generated/le_tools_offline_buildinfo_context_report.md`.
17. Stage context report: `backend/tests/fixtures/le_tools_offline_buildinfo_stage_context_sample.json`, `backend/app/game_data/le_tools_import_stage_context_report.py`, `backend/scripts/report_le_tools_import_stage_context.py`, `backend/tests/test_le_tools_importer_stage_context.py`, `docs/generated/le_tools_import_stage_context_report.md`.
18. Sidecar design: `docs/LE_TOOLS_IMPORT_CONTEXT_SIDECAR_DESIGN.md`.
19. Sidecar builder: `backend/app/game_data/le_tools_import_context_sidecar.py`, `backend/scripts/build_le_tools_import_context_sidecar.py`, `backend/tests/test_le_tools_import_context_sidecar.py`, `docs/generated/le_tools_import_context_sidecar_report.md`.
20. Sidecar validator: `backend/app/game_data/le_tools_import_context_sidecar_validator.py`, `backend/scripts/validate_le_tools_import_context_sidecar.py`, `backend/tests/test_le_tools_import_context_sidecar_validator.py`, `docs/generated/le_tools_import_context_sidecar_validation_report.md`.
21. Saved sidecar fixture validation: `backend/tests/fixtures/le_tools_import_context_sidecar_current.json`, `docs/generated/le_tools_import_context_sidecar_saved_fixture_validation_report.md`.

These milestones are diagnostic and developer-only. They do not activate production bundle consumption.

## 11. Current Safety Boundary

The current safety boundary is:

- No production loaders consume bundle `item_types` or `base_items`.
- No frontend or backend API behavior depends on bundle item type IDs.
- No simulation math depends on the bundle.
- No production importer output shape has been changed for sidecar diagnostics.
- `production_safe` remains false in mapping fixtures, adapter translations, resolver output, sidecars, and validators.
- Bundle compatibility status is expected to remain `compatible_with_warnings`, not fully compatible.
- Diagnostics are developer-only modules, scripts, fixtures, and docs.
- Synthetic/offline LE Tools fixtures do not prove live LET payload shape.
- Current mapped importer output preserves `base_type_id` but does not expose item type context.
- Base item migration is blocked for production use because current Forge base items lack `base_type_id` and `subtype_id`.

This means the migration work is still pre-consumer. It has established inspection, mapping, dry-run, context, and validation infrastructure, but not a production or non-production consumer that uses bundle IDs as application data.

## 12. Risks and Gaps

Highest data migration risks:

- Collapsed Forge item type groups require `base_type_id`: `axe`, `mace`, `sword`, and `idol_1x1`.
- `spear` remains `needs_review` and is not accepted.
- `subtype_id` alone is unsafe because subtype IDs are scoped under base type.
- Name-only base item matching is unsafe.
- `data/items/base_items.json` lacks composite source IDs, blocking authoritative bundle `base_items` migration.
- Bundle-only and non-equipment item types remain deferred or need review.
- Current Forge constants may be partial or stale.
- Current production consumers may depend on simplified item categories.

Importer risks:

- Synthetic/offline fixtures prove diagnostic behavior, not live LET payload shape.
- Mapped importer output preserves `base_type_id` but omits item type context.
- Test-only pairing is currently required in sidecar diagnostics.
- Maxroll import confidence remains lower than LE Tools import confidence.

Simulation/data accuracy risks:

- Skill base damage estimates remain for 34 skills.
- Enemy armour/resistance profiles are approximate.
- Ailment DPS needs live verification.
- Minion DPS is not modeled.
- Conditional stats are not fully wired into DPS.
- Armour shred does not accumulate over fight duration.
- Passive stat resolution still preserves unresolved mechanics in `special_effects`.

Repository/process risks:

- There is a large amount of diagnostic code under `backend/app/game_data/`; it must remain isolated from production imports.
- `docs/generated/` artifacts are useful but should not be mistaken for canonical data.
- Some local import tests can expose environment/data decoding issues unrelated to bundle diagnostics.
- The root `last-epoch-data/` directory inside this repo tree should not be confused with the sibling `D:\Forge\last-epoch-data` source repo used for bundle generation.

## 13. Recommended Next Steps

Recommended roadmap:

1. Immediate milestone summary: create a concise migration checkpoint document that summarizes the completed item type diagnostic chain, the current `production_safe=false` boundary, and the exact blocker list for a non-production consumer.
2. Next diagnostic step: validate or capture a real offline LET payload shape if available, without network calls and without changing importer output. The current synthetic/offline fixtures are useful but not proof of live LET field shape.
3. First non-production consumer candidate: a developer-only CLI/report that reads a copied LE Tools sidecar or saved fixture and reports canonical bundle item type IDs as diagnostics only. It should not be imported by production loaders or routes.
4. Before production migration: add source IDs to the relevant Forge item/base item records or introduce a validated adapter layer that requires `base_type_id`, preserves fallback visibility, and has tests for collapsed groups, `spear`, non-equipment deferrals, subtype scoping, and name-only rejection.
5. Only after non-production diagnostics are stable: consider a dev-only backend comparison route or admin report if an existing developer-only diagnostics pattern is preferred. Do not expose it to users or simulation.

What not to do yet:

- Do not replace production item loaders.
- Do not migrate `base_items` by name.
- Do not use `subtype_id` alone.
- Do not treat `spear` as accepted.
- Do not mark mappings or sidecars `production_safe=true`.
- Do not expose sidecar data in public API responses.
- Do not wire bundle IDs into simulation, import routes, or frontend item UI.
- Do not claim synthetic/offline LET fixtures prove live LET payload correctness.

