# EpochForge v2 Source Inventory

## Purpose

This Phase 1 report inventories current data sources, mappings, fixtures, fallback paths, and generated diagnostics that may affect the trusted data rebuild. It is read-only and does not define v2 contracts.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_source_inventory.py --output docs\generated\v2_source_inventory.json --markdown-output docs\migration\V2_SOURCE_INVENTORY.md
```

## Summary

- Source count: 890
- Runtime-adjacent source count: 389
- Replace or remap count: 369
- Generated on: 2026-05-12
- Checkpoint: checkpoint_1

## Data Category Counts

| Data category | Count |
| --- | ---: |
| affixes | 133 |
| backend_mappings | 9 |
| classes_masteries | 38 |
| debug_demo_data | 39 |
| fallback_data | 1 |
| fixtures | 22 |
| frontend_mappings | 1 |
| generated_files | 35 |
| implicits | 1 |
| item_bases | 3 |
| items | 120 |
| passive_trees | 21 |
| planner_constants | 7 |
| sets | 10 |
| skill_trees | 5 |
| skills | 16 |
| static_json_files | 60 |
| stats_modifiers | 16 |
| tests_with_runtime_assumptions | 344 |
| uniques | 9 |

## Source Kind Counts

| Source kind | Count |
| --- | ---: |
| debug_demo | 39 |
| extracted | 55 |
| fallback | 1 |
| fixture | 22 |
| generated | 35 |
| manual | 66 |
| static_json | 18 |
| unknown | 654 |

## Current Trust Status Counts

| Trust status | Count |
| --- | ---: |
| partial | 90 |
| text_only | 14 |
| unknown | 724 |
| unsupported | 62 |

## Migration Priority Counts

| Priority | Count |
| --- | ---: |
| critical | 346 |
| high | 77 |
| low | 62 |
| medium | 405 |

## High-Priority Inventory Slice

| Source path | Data category | Source kind | Trust status | Priority | v2 disposition | Replace/remap |
| --- | --- | --- | --- | --- | --- | --- |
| backend/app/constants/cache.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/app/constants/crafting.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/app/domain/build_state.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/domain/calculators/affix_calculator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/domain/calculators/stat_calculator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/domain/item.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/domain/registries/affix_registry.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/affix_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/craft_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/craft_simulator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/item_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/stat_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/engines/stat_resolution_pipeline.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/__init__.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/affix_diagnostic_consumer.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/bundle_compat.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/controlled_affix_per_affix_diagnostic.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/controlled_affix_resolver_comparison.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/controlled_affix_resolver_prototype.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/controlled_modifier_resolver_comparison.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/controlled_modifier_resolver_prototype.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/game_data_loader.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/malformed_tier_value_shape_validator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/missing_modifier_reference_mapping_validator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/modifier_unresolved_category_triage.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/game_data/pipeline.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/routes/affixes.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/routes/craft.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/routes/skills.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/services/affix_catalog_service.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/services/craft_service.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/app/services/forge_safe_affix_comparison_service.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/bis/generator/affix_combination_generator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/bis/generator/item_candidate_generator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/bis/integration/craft_adapter.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/bis/models/item_slot.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/bis/validation/craft_feasibility.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/builds/build_stats_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/engines/craft_execution_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/engines/forging_potential_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/engines/fracture_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/engines/glyph_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/engines/rune_engine.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/models/affix_tier.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/models/bis_target.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/models/craft_action.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/models/craft_state.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/optimization/craft_optimizer.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/optimization/path_generator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/optimization/scoring.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/simulation/monte_carlo_crafting.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/crafting/simulation/sequence_simulator.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/loaders/forge_safe_affix_bundle_loader.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/loaders/forge_safe_affixes_loader.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/mappers/data_mapper.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/models/affix_model.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/models/item_model.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/repositories/forge_safe_affix_bundle_repository.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/repositories/forge_safe_affix_repository.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/schemas/game_data_schema.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/data/versioning/versioned_loader.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/migrations/versions/21bc975a3016_add_affixes_before_to_craftstep_for_.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/migrations/versions/8d9b7a5c2e11_add_affix_metadata_columns.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/migrations/versions/93e06c1a641f_widen_affix_defs_name_column_to_256.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/migrations/versions/b4c1f0f6d2aa_widen_affix_def_columns.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/migrations/versions/e07407b85e20_widen_affix_defs_stat_key_and_class_.py | affixes | unknown | unknown | critical | temporary_until_remapped | True |
| backend/scripts/compare_controlled_affix_resolver_prototype.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/compare_forge_safe_affixes.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/inspect_forge_safe_affixes.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_affix_diagnostic_consumer.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_controlled_affix_per_affix_diagnostic.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_controlled_affix_resolver_prototype.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_controlled_modifier_resolver_comparison.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_controlled_modifier_resolver_prototype.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_adapter_candidate_validation.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_adapter_candidates.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_legacy_affix_comparison.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_slot_vocabulary_equivalence.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_slot_vocabulary_policy.py | affixes | manual | unknown | critical | temporary_until_remapped | True |
| backend/scripts/report_forge_safe_stat_key_mapping.py | affixes | manual | unknown | critical | temporary_until_remapped | True |

## Important Findings

- The repo contains both extracted/static JSON and manual mapping/constants paths. v2 needs explicit provenance before any runtime path treats them as trusted.
- Existing generated diagnostics are valuable audit records, but they are not runtime sources.
- Fixtures, samples, fallback records, and debug/demo paths are widespread enough that tests may currently encode behavior that should remain test-only.
- Planner, crafting, stat, and simulation paths depend on manual constants and mapping layers that need contract review before replacement.

## Remaining Risks

- Consumer detection is path and token based; it should be treated as an inventory aid, not a dependency graph.
- Trust status is conservative. Unknown and partial sources need source-specific validation in later phases.
- This report does not approve any data contract, gameplay calculation, adapter, or runtime behavior change.

## Checkpoint 1

Checkpoint 1 is ready for review when the JSON report validates, this markdown report is reviewed, and no Phase 2 contract work has started.
