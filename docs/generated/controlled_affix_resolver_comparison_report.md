# Controlled Affix Resolver Prototype Comparison Report

- comparison_status: warning
- production_safe: false
- saved_resolver_status: warning
- fresh_resolver_status: warning
- deterministic_output_agreement: true
- affix_910_duplicate_evidence_agreement: true

## Count Deltas

- total_normalized_affixes: saved=1227 fresh=1227 delta=0
- equipment_affixes: saved=1112 fresh=1112 delta=0
- idol_affixes: saved=115 fresh=115 delta=0
- total_embedded_tiers: saved=6959 fresh=6959 delta=0

## Phase Status Delta

- phase_1_source_shape: saved=warning fresh=warning agrees=True
- phase_2_identity_provenance: saved=warning fresh=warning agrees=True
- phase_3_eligibility: saved=warning fresh=warning agrees=True
- phase_4_tag_category: saved=warning fresh=warning agrees=True
- phase_5_saved_vs_fresh: saved=warning fresh=warning agrees=True

## Warning Category Delta

- phase_1_source_shape::ambiguous_name_collisions: saved=28 fresh=28 delta=0
- phase_1_source_shape::malformed_tier_ranges: saved=136 fresh=136 delta=0
- phase_1_source_shape::missing_stat_modifier_references: saved=115 fresh=115 delta=0
- phase_1_source_shape::unsupported_or_unresolved_fields: saved=1112 fresh=1112 delta=0
- phase_2_identity_provenance::ambiguous_display_name_collisions: saved=137 fresh=137 delta=0
- phase_3_eligibility::duplicate_or_ambiguous_eligibility_records: saved=1 fresh=1 delta=0
- phase_3_eligibility::unsupported_or_unresolved_eligibility_fields: saved=115 fresh=115 delta=0
- phase_4_tag_category::ambiguous_tag_category_mappings: saved=110 fresh=110 delta=0
- phase_4_tag_category::unknown_or_unsupported_tag_category_values: saved=148 fresh=148 delta=0
- phase_5_saved_vs_fresh::phases_with_warning_status: saved=4 fresh=4 delta=0

## Affix 910 Duplicate Evidence

- agrees: True
- saved: {'record_id': 910, 'section': 'equipment', 'record_path': 'equipment[910].canRollOn', 'raw_canRollOn': ['IDOL_4x1', 'IDOL_4x1'], 'normalized_canRollOn': ['IDOL_4X1', 'IDOL_4X1'], 'raw_duplicate_count': 2, 'duplicate_positions': [0, 1], 'diagnostic_unique_targets': ['IDOL_4X1'], 'diagnostic_unique_targets_label': 'diagnostic_only_not_source_mutation', 'policy_result': 'warning_only'}
- fresh: {'record_id': 910, 'section': 'equipment', 'record_path': 'equipment[910].canRollOn', 'raw_canRollOn': ['IDOL_4x1', 'IDOL_4x1'], 'normalized_canRollOn': ['IDOL_4X1', 'IDOL_4X1'], 'raw_duplicate_count': 2, 'duplicate_positions': [0, 1], 'diagnostic_unique_targets': ['IDOL_4X1'], 'diagnostic_unique_targets_label': 'diagnostic_only_not_source_mutation', 'policy_result': 'warning_only'}

## Safety Agreement

- production_safe_agreement: {'saved': False, 'fresh': False, 'agrees': True}
- non_production_inspection_allowed_agreement: {'saved': True, 'fresh': True, 'agrees': True}

## Errors

- none

## Warnings

- Resolver outputs remain warning-level and non-production.

## Recommendations

- Keep the resolver prototype diagnostic-only and non-production.
- Review count, warning, or deterministic-output drift before using the fresh output as a baseline.
- Do not generate affix bundle families or production consumers from this comparison.

## Safety Boundary

- This comparison is diagnostic-only and non-production.
- It compares saved resolver output with freshly generated resolver output.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not silently deduplicate affix 910.
- It does not claim production readiness.

