# Controlled Modifier Resolver Prototype Comparison Report

- comparison_status: warning
- diagnostic_only: true
- production_safe: false
- saved_resolver_output_status: warning
- fresh_resolver_output_status: warning
- deterministic_output_agreement: true
- affix_910_duplicate_evidence_agreement: true

## Count Deltas

- total_modifier_references: saved=6959 fresh=6959 delta=0
- resolved_modifier_objects: saved=5596 fresh=5596 delta=0
- unresolved_modifier_objects: saved=115 fresh=115 delta=0
- malformed_modifier_objects: saved=136 fresh=136 delta=0
- unsupported_modifier_objects: saved=1112 fresh=1112 delta=0

## Warning Category Delta

- modifier_resolution_policy::malformed_modifier_structures: saved=136 fresh=136 delta=0
- modifier_resolution_policy::unresolved_modifier_references: saved=115 fresh=115 delta=0
- modifier_resolution_policy::unsupported_modifier_structures: saved=1112 fresh=1112 delta=0
- phase_1_source_shape::ambiguous_name_collisions: saved=28 fresh=28 delta=0
- phase_2_identity_provenance::ambiguous_display_name_collisions: saved=137 fresh=137 delta=0
- phase_3_eligibility::duplicate_or_ambiguous_eligibility_records: saved=1 fresh=1 delta=0
- phase_4_tag_category::ambiguous_tag_category_mappings: saved=110 fresh=110 delta=0
- phase_4_tag_category::unknown_or_unsupported_tag_category_values: saved=148 fresh=148 delta=0
- phase_5_saved_vs_fresh::phases_with_warning_status: saved=4 fresh=4 delta=0

## Safety Agreement

- provenance_coverage_agreement: {'saved': {'total_modifier_objects': 4, 'with_provenance': 4, 'missing_provenance': 0}, 'fresh': {'total_modifier_objects': 4, 'with_provenance': 4, 'missing_provenance': 0}, 'agrees': True}
- production_safe_agreement: {'saved': False, 'fresh': False, 'agrees': True}
- diagnostic_only_agreement: {'saved': True, 'fresh': True, 'agrees': True}

## Affix 910 Duplicate Evidence

- agrees: True
- saved: {'record_id': 910, 'section': 'equipment', 'record_path': 'equipment[910].canRollOn', 'raw_canRollOn': ['IDOL_4x1', 'IDOL_4x1'], 'normalized_canRollOn': ['IDOL_4X1', 'IDOL_4X1'], 'raw_duplicate_count': 2, 'duplicate_positions': [0, 1], 'diagnostic_unique_targets': ['IDOL_4X1'], 'diagnostic_unique_targets_label': 'diagnostic_only_not_source_mutation', 'policy_result': 'warning_only'}
- fresh: {'record_id': 910, 'section': 'equipment', 'record_path': 'equipment[910].canRollOn', 'raw_canRollOn': ['IDOL_4x1', 'IDOL_4x1'], 'normalized_canRollOn': ['IDOL_4X1', 'IDOL_4X1'], 'raw_duplicate_count': 2, 'duplicate_positions': [0, 1], 'diagnostic_unique_targets': ['IDOL_4X1'], 'diagnostic_unique_targets_label': 'diagnostic_only_not_source_mutation', 'policy_result': 'warning_only'}

## Errors

- none

## Warnings

- Unresolved, malformed, or unsupported modifier evidence remains visible; comparison is warning-level.
- Modifier resolver outputs remain warning-level and non-production.

## Recommendations

- Keep the modifier resolver prototype diagnostic-only and non-production.
- Review count, warning, or deterministic-output drift before using fresh output as a new baseline.
- Do not generate affix bundle families or production consumers from this comparison.

## Safety Boundary

- This comparison is diagnostic-only and non-production.
- It compares saved modifier resolver output with freshly generated modifier resolver output.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not infer gameplay semantics.
- It does not claim gameplay correctness or production readiness.

