# Controlled Affix Resolver Prototype Report

- resolver: controlled_affix_resolver_prototype
- scope: non_production_read_only_cli_report
- source: generated_diagnostic_artifacts
- production_safe: false
- non_production_inspection_allowed: true
- phase5_migration_gate_status: warning

## Summary

- total_normalized_affixes: 1227
- equipment_affixes: 1112
- idol_affixes: 115
- total_embedded_tiers: 6959
- warning_categories: 10
- warning_count: 1904
- affix_910_duplicate_evidence_preserved: True
- phase5_migration_gate_status: warning

## Phase Status Summary

- phase_1_source_shape: validation_status=warning migration_gate_status=n/a production_safe=false warnings=1391 errors=0
- phase_2_identity_provenance: validation_status=warning migration_gate_status=n/a production_safe=false warnings=137 errors=0
- phase_3_eligibility: validation_status=warning migration_gate_status=n/a production_safe=false warnings=116 errors=0
- phase_4_tag_category: validation_status=warning migration_gate_status=n/a production_safe=false warnings=258 errors=0
- phase_5_saved_vs_fresh: validation_status=warning migration_gate_status=warning production_safe=false warnings=2 errors=0

## Normalized Inspection Objects

- Full record count is emitted in JSON. Markdown shows representative objects only to keep the report readable.
- equipment:0: section=equipment source_affix_id=0 warnings=1 production_safe=false
- equipment:1: section=equipment source_affix_id=1 warnings=1 production_safe=false
- equipment:2: section=equipment source_affix_id=2 warnings=1 production_safe=false
- equipment:3: section=equipment source_affix_id=3 warnings=1 production_safe=false
- equipment:4: section=equipment source_affix_id=4 warnings=1 production_safe=false
- equipment:5: section=equipment source_affix_id=5 warnings=1 production_safe=false
- equipment:6: section=equipment source_affix_id=6 warnings=1 production_safe=false
- equipment:7: section=equipment source_affix_id=7 warnings=1 production_safe=false
- ... 1219 additional inspection objects omitted from markdown.

## Warning Categories

- phase=phase_1_source_shape, category=ambiguous_name_collisions, count=28
- phase=phase_1_source_shape, category=malformed_tier_ranges, count=136
- phase=phase_1_source_shape, category=missing_stat_modifier_references, count=115
- phase=phase_1_source_shape, category=unsupported_or_unresolved_fields, count=1112
- phase=phase_2_identity_provenance, category=ambiguous_display_name_collisions, count=137
- phase=phase_3_eligibility, category=duplicate_or_ambiguous_eligibility_records, count=1
- phase=phase_3_eligibility, category=unsupported_or_unresolved_eligibility_fields, count=115
- phase=phase_4_tag_category, category=unknown_or_unsupported_tag_category_values, count=148
- phase=phase_4_tag_category, category=ambiguous_tag_category_mappings, count=110
- phase=phase_5_saved_vs_fresh, category=phases_with_warning_status, count=4

## Affix 910 Duplicate Evidence

- record_id: 910
- section: equipment
- record_path: equipment[910].canRollOn
- raw_canRollOn: ['IDOL_4x1', 'IDOL_4x1']
- normalized_canRollOn: ['IDOL_4X1', 'IDOL_4X1']
- raw_duplicate_count: 2
- duplicate_positions: [0, 1]
- diagnostic_unique_targets: ['IDOL_4X1']
- diagnostic_unique_targets_label: diagnostic_only_not_source_mutation
- policy_result: warning_only
- origin_assessment: unresolved/unknown before exports_json/affixes.json
- message: Eligibility target 'IDOL_4X1' appears 2 times for this affix. Classification: exact_duplicate_in_current_export; origin assessment: unresolved/unknown before exports_json/affixes.json; policy result: warning_only.

## Errors

- none

## Warnings

- phase_1_source_shape remains warning-level and non-production.
- phase_1_source_shape contains 1391 diagnostic warnings.
- phase_2_identity_provenance remains warning-level and non-production.
- phase_2_identity_provenance contains 137 diagnostic warnings.
- phase_3_eligibility remains warning-level and non-production.
- phase_3_eligibility contains 116 diagnostic warnings.
- phase_4_tag_category remains warning-level and non-production.
- phase_4_tag_category contains 258 diagnostic warnings.
- phase_5_saved_vs_fresh remains warning-level and non-production.
- phase_5_saved_vs_fresh contains 2 diagnostic warnings.
- Warning categories are preserved; this is not production readiness.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.
- Do not use this resolver prototype as a production affix model.
- Do not treat normalized inspection objects as gameplay stat data.

## Safety Boundary

- This resolver is a prototype for inspection-only diagnostics.
- It does not consume production bundle data directly.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not silently deduplicate affix 910.
- It does not claim production readiness.

