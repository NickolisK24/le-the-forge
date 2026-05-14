# Phase 6 Affix Diagnostic Consumer Report

- diagnostic: phase_6_affix_diagnostic_consumer
- consumer_scope: non_production_read_only
- production_safe: false
- non_production_inspection_allowed: true
- phase5_migration_gate_status: warning

## Summary

- total_affixes: 1227
- equipment_affixes: 1112
- idol_affixes: 115
- total_embedded_tiers: 6959
- phase5_migration_gate_status: warning
- remaining_warning_categories: 10
- affix_910_duplicate_evidence_present: True
- tag_category_warnings_present: True

## Phase Statuses

- phase_1_source_shape: validation_status=warning migration_gate_status=n/a production_safe=false errors=0 warnings=1391
- phase_2_identity_provenance: validation_status=warning migration_gate_status=n/a production_safe=false errors=0 warnings=137
- phase_3_eligibility: validation_status=warning migration_gate_status=n/a production_safe=false errors=0 warnings=116
- phase_4_tag_category: validation_status=warning migration_gate_status=n/a production_safe=false errors=0 warnings=258
- phase_5_saved_vs_fresh: validation_status=warning migration_gate_status=warning production_safe=false errors=0 warnings=2

## Remaining Warning Categories

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

## Affix 910 Duplicate Eligibility Evidence

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

## Tag/Category Warning State

- validation_status: warning
- warning_count: 258
- unknown_or_unsupported_tag_category_values: 148
- ambiguous_tag_category_mappings: 110
- duplicate_tag_category_records: 0
- name_only_tag_category_records: 0
- subtype_id_only_tag_category_records: 0
- phase3_eligibility_status_from_phase3_report: warning
- phase3_relationship_note: Phase 4 remains a separate tag/category gate and does not resolve eligibility.

## Errors

- none

## Warnings

- phase_1_source_shape contains 1391 diagnostic warnings.
- phase_1_source_shape remains warning-level and non-production.
- phase_2_identity_provenance contains 137 diagnostic warnings.
- phase_2_identity_provenance remains warning-level and non-production.
- phase_3_eligibility contains 116 diagnostic warnings.
- phase_3_eligibility remains warning-level and non-production.
- phase_4_tag_category contains 258 diagnostic warnings.
- phase_4_tag_category remains warning-level and non-production.
- phase_5_saved_vs_fresh contains 2 diagnostic warnings.
- phase_5_saved_vs_fresh remains warning-level and non-production.
- Warning categories remain visible; do not treat this consumer as production readiness.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.

## Recommendations

- Phase 6 inspection may remain read-only and non-production.
- Keep this consumer limited to generated diagnostic artifacts.
- Do not generate affix bundle families or production Forge consumers from this report.
- Preserve affix 910 raw duplicate evidence in all downstream diagnostics.

## Safety Boundary

- This report consumes generated diagnostic artifacts only.
- It is read-only, non-production, and inspection-only.
- It does not consume production bundle data.
- It does not modify importers, loaders, generated output, APIs, frontend behavior, runtime behavior, crafting, or simulation.
- It does not silently deduplicate affix 910.
- It does not claim production readiness.
