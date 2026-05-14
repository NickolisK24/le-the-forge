# V3 Value Normalization Contract

This document defines the design contract for future value normalization.
It does not convert values, promote records, or change planner output.

## Current Blocker State

- Modifier rows: `19398`
- Blocked modifier rows: `19398`
- Planner-calculable count: `0`
- Stable-calculable count: `0`
- Value normalization: `audit_only`
- Source-unit values: `6248`
- Unknown values: `13150`
- Unknown operations: `11606`
- Unresolved stat identities: `4714`

## Required Contract Fields

- `family_id`
- `source_scale`
- `target_scale`
- `domain`
- `operation_type`
- `stat_identity_status`
- `value_transform_rule`
- `unit_semantics`
- `polarity_semantics`
- `rounding_policy`
- `stacking_policy_dependency`
- `applicability_scope`
- `source_examples`
- `golden_baseline_refs`
- `validation_status`
- `promotion_status`
- `blocked_reasons`
- `provenance`

## Allowed Promotion States

- `audit_only`
- `blocked_by_behavioral_risk`
- `blocked_by_missing_baseline`
- `blocked_by_operation_semantics`
- `blocked_by_source_units`
- `blocked_by_stat_identity`
- `blocked_by_unknown_scale`
- `candidate_needs_evidence`
- `planner_normalized_experimental`
- `planner_normalized_stable`

## Evidence Requirements

- `source_examples`: Representative source records for the family.
- `known_raw_value_examples`: Raw min/max values from trusted source data.
- `expected_normalized_value_examples`: Expected planner values approved by policy and baseline evidence.
- `operation_semantics`: Approved operation meaning, stacking, and scope.
- `resolved_stat_identity`: Canonical stat identity resolved for the target domain.
- `golden_baseline_test`: Existing planner output or explicit mechanical baseline.
- `old_planner_comparison`: Dry-run comparison against current planner output where applicable.
- `unsupported_exclusion`: Proof that scripted and unsupported mechanics remain excluded.
- `provenance_source`: Traceable source path and generated bundle provenance.
- `patch_version_traceability`: Patch/export version associated with the evidence.

## Family Classifications

| Family | Classification | Count |
| --- | --- | ---: |
| `all_unknown_value_scales` | `blocked_by_unknown_scale` | `13150` |
| `all_source_units_value_scales` | `blocked_by_source_units` | `6248` |
| `unknown_operations` | `blocked_by_operation_semantics` | `11606` |
| `unresolved_stat_identities` | `blocked_by_stat_identity` | `4714` |
| `unique_modifier|flat|added_playerproperty` | `candidate_needs_evidence` | `326` |
| `unique_modifier|flat|added_abilityproperty` | `candidate_needs_evidence` | `313` |
| `item_implicit|flat|added_damage` | `candidate_needs_evidence` | `259` |
| `affix|increased|increased_damage` | `candidate_needs_evidence` | `231` |
| `affix|flat|added_abilityproperty` | `candidate_needs_evidence` | `216` |
| `affix|flat|added_playerproperty` | `candidate_needs_evidence` | `205` |
| `item_implicit|flat|added_armour` | `candidate_needs_evidence` | `175` |
| `affix|flat|added_levelofskills` | `candidate_needs_evidence` | `135` |
| `skill_node_modifier|unknown|unknown` | `blocked_by_unknown_scale` | `4460` |
| `skill_node_modifier|unknown|54` | `blocked_by_unknown_scale` | `1320` |
| `skill_structured_value|duration|duration_cast` | `blocked_by_behavioral_risk` | `744` |
| `skill_node_modifier|unknown|damage` | `blocked_by_unknown_scale` | `323` |

## Disallowed Assumptions

- Do not infer value scale from display text.
- Do not infer value scale from tooltip text.
- Do not treat source_units as planner-normalized.
- Do not treat unknown values as zero or identity values.
- Do not assume percent-like operations use the same transform family.
- Do not promote a family without operation semantics and stat identity evidence.
- Do not bridge unresolved skill identities to make value normalization pass.

## Future Sequence

| Order | Step |
| ---: | --- |
| `1` | Define operation semantics taxonomy. |
| `2` | Define stat identity resolution policy. |
| `3` | Select one narrow value family candidate. |
| `4` | Gather raw source examples. |
| `5` | Define transform rule. |
| `6` | Create golden baseline. |
| `7` | Run dry-run comparison. |
| `8` | Mark experimental only after evidence passes. |
| `9` | Promote stable only after repeated validation. |

## Safety Confirmations

- Values normalized: `false`
- Stable-calculable promoted: `false`
- Planner-calculable promoted: `false`
- Production consumed: `false`
- Value normalization status: `audit_only`
- Unknown values blocked: `true`
- Source-unit values blocked: `true`
- Unknown operations blocked: `true`
- Unresolved stat identities blocked: `true`

## Recommended Next Phase

`v3_operation_semantics_taxonomy`
