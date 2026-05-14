# Controlled Affix Per-Affix Diagnostic Records

- diagnostic: controlled_affix_per_affix_diagnostic_records
- scope: non_production_read_only_per_affix_records
- production_safe: false
- diagnostic_only: true
- non_production_inspection_allowed: true
- phase5_migration_gate_status: warning

## Summary

- total_records: 1227
- equipment_records: 1112
- idol_records: 115
- embedded_tier_count: 6959
- warning_category_count: 17
- records_with_warnings: 1227
- affix_910_duplicate_evidence_preserved: True

## Phase Status Summary

- phase_1_source_shape: warning
- phase_2_identity_provenance: warning
- phase_3_eligibility: warning
- phase_4_tag_category: warning
- phase_5_saved_vs_fresh: warning

## Warning Category Summary

- phase=phase_1_source_shape, category=affix_record.extra_typetree_fields, count=1112
- phase=phase_1_source_shape, category=affix_record.idol_stat_modifier_reference_unmodeled, count=115
- phase=phase_1_source_shape, category=affix_tier.inverted_numeric_range, count=136
- phase=phase_1_source_shape, category=ambiguous_name_collisions, count=28
- phase=phase_1_source_shape, category=malformed_tier_ranges, count=136
- phase=phase_1_source_shape, category=missing_stat_modifier_references, count=115
- phase=phase_1_source_shape, category=unsupported_or_unresolved_fields, count=1112
- phase=phase_2_identity_provenance, category=ambiguous_display_name_collisions, count=137
- phase=phase_3_eligibility, category=affix_eligibility.duplicate_target, count=1
- phase=phase_3_eligibility, category=affix_eligibility.idol_context_unresolved, count=115
- phase=phase_3_eligibility, category=duplicate_or_ambiguous_eligibility_records, count=1
- phase=phase_3_eligibility, category=unsupported_or_unresolved_eligibility_fields, count=115
- phase=phase_4_tag_category, category=affix_tags.ambiguous_mapping, count=110
- phase=phase_4_tag_category, category=affix_tags.unknown_or_unsupported_value, count=148
- phase=phase_4_tag_category, category=ambiguous_tag_category_mappings, count=110
- phase=phase_4_tag_category, category=unknown_or_unsupported_tag_category_values, count=148
- phase=phase_5_saved_vs_fresh, category=phases_with_warning_status, count=4

## Affix 910 Evidence Summary

- record_identity: equipment:910
- raw_duplicate_evidence: {'record_id': 910, 'section': 'equipment', 'record_path': 'equipment[910].canRollOn', 'raw_canRollOn': ['IDOL_4x1', 'IDOL_4x1'], 'normalized_canRollOn': ['IDOL_4X1', 'IDOL_4X1'], 'raw_duplicate_count': 2, 'duplicate_positions': [0, 1], 'diagnostic_unique_targets': ['IDOL_4X1'], 'diagnostic_unique_targets_label': 'diagnostic_only_not_source_mutation', 'policy_result': 'warning_only', 'origin_assessment': 'unresolved/unknown before exports_json/affixes.json', 'message': "Eligibility target 'IDOL_4X1' appears 2 times for this affix. Classification: exact_duplicate_in_current_export; origin assessment: unresolved/unknown before exports_json/affixes.json; policy result: warning_only."}
- record_contains_raw_duplicate_evidence: True
- diagnostic_normalized_views: [{'view': 'eligibility_unique_targets', 'values': ['IDOL_4X1'], 'label': 'diagnostic_only_not_source_mutation', 'source_mutation': False}]
- source_mutation: False

## Representative Records

- Full per-affix records are emitted in JSON. Markdown shows representative records only.
- equipment:0: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:1: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:2: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:3: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:4: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:5: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:6: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- equipment:7: classification=equipment warnings=1 production_safe=false diagnostic_only=true
- ... 1219 additional records omitted from markdown.

## Errors

- none

## Warnings

- Per-affix records remain non-production and production_safe=false.
- Per-affix warning metadata is attached for inspection only.
- Warning categories are preserved; this is not production readiness.
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
- Do not use this per-affix diagnostic artifact as production affix data.
- Do not treat diagnostic normalized views as source mutation.

## Safety Boundary

- This artifact is diagnostic-only and non-production.
- It is generated from controlled resolver output over approved diagnostic artifacts.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not silently deduplicate affix 910.
- It does not claim production readiness.

