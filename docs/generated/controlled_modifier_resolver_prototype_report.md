# Controlled Modifier Resolver Prototype Report

- resolver: controlled_modifier_resolver_prototype
- scope: non_production_read_only_cli_report
- source: generated_diagnostic_artifacts
- diagnostic_only: true
- production_safe: false
- non_production_inspection_allowed: true
- phase5_migration_gate_status: warning

## Summary

- total_modifier_references: 6959
- resolved_modifier_objects: 5596
- unresolved_modifier_objects: 115
- malformed_modifier_objects: 136
- unsupported_modifier_objects: 1112
- warning_categories: 9
- deterministic_output_status: stable
- non_production_inspection_allowed: True
- affix_910_duplicate_evidence_preserved: True

## Phase Status Summary

- phase_1_source_shape: validation_status=warning migration_gate_status=n/a production_safe=false warnings=1391 errors=0
- phase_2_identity_provenance: validation_status=warning migration_gate_status=n/a production_safe=false warnings=137 errors=0
- phase_3_eligibility: validation_status=warning migration_gate_status=n/a production_safe=false warnings=116 errors=0
- phase_4_tag_category: validation_status=warning migration_gate_status=n/a production_safe=false warnings=258 errors=0
- phase_5_saved_vs_fresh: validation_status=warning migration_gate_status=warning production_safe=false warnings=2 errors=0

## Modifier Inspection Objects

- modifier_reference_group:resolved_structural: state=resolved references=5596 production_safe=false
- modifier_reference_group:unresolved: state=unresolved references=115 production_safe=false
- modifier_reference_group:malformed: state=malformed references=136 production_safe=false
- modifier_reference_group:unsupported: state=unsupported references=1112 production_safe=false

## Warning Categories

- phase=modifier_resolution_policy, category=unresolved_modifier_references, count=115
- phase=modifier_resolution_policy, category=malformed_modifier_structures, count=136
- phase=modifier_resolution_policy, category=unsupported_modifier_structures, count=1112
- phase=phase_1_source_shape, category=ambiguous_name_collisions, count=28
- phase=phase_2_identity_provenance, category=ambiguous_display_name_collisions, count=137
- phase=phase_3_eligibility, category=duplicate_or_ambiguous_eligibility_records, count=1
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
- Unresolved, malformed, and unsupported modifier evidence remains visible and excluded from resolved semantics.
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
- Do not use this modifier resolver prototype as a gameplay stat model.
- Do not infer additive, increased, more, conditional, ailment, minion, skill, class, or stacking semantics.
- Do not treat aggregate inspection objects as per-reference gameplay rows.

## Safety Boundary

- This resolver is a prototype for inspection-only diagnostics.
- It does not consume production bundle data directly.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not guess unsupported modifier semantics.
- It does not resolve malformed or unresolved modifier structures.
- It does not claim gameplay correctness or production readiness.

