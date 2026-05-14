# V3 Operation Semantics Taxonomy

This document defines the operation semantics taxonomy contract.
It does not implement operation calculations, stat math, value normalization, or planner output changes.

## Current Operation Distribution

- `chance`: `69`
- `cooldown`: `429`
- `cost`: `440`
- `duration`: `949`
- `flat`: `4627`
- `increased`: `1112`
- `less`: `1`
- `more`: `165`
- `unknown`: `11606`

## Operation Families

| Operation | Classification | Count | Promotion |
| --- | --- | ---: | --- |
| `flat` | `candidate_needs_evidence` | `4627` | `candidate_needs_evidence` |
| `increased` | `candidate_needs_evidence` | `1112` | `candidate_needs_evidence` |
| `more` | `candidate_needs_evidence` | `165` | `candidate_needs_evidence` |
| `duration` | `candidate_needs_evidence` | `949` | `candidate_needs_evidence` |
| `cost` | `candidate_needs_evidence` | `440` | `candidate_needs_evidence` |
| `cooldown` | `candidate_needs_evidence` | `429` | `candidate_needs_evidence` |
| `chance` | `candidate_needs_evidence` | `69` | `candidate_needs_evidence` |
| `threshold` | `blocked_by_conditional_behavior` | `0` | `blocked_by_conditional_behavior` |
| `conditional` | `blocked_by_conditional_behavior` | `0` | `blocked_by_conditional_behavior` |
| `conversion` | `audit_only` | `0` | `audit_only` |
| `unknown` | `blocked_by_unknown_operation` | `11606` | `blocked_by_unknown_operation` |

## Semantic Contract Fields

- `operation_id`
- `operation_label`
- `source_operation_values`
- `planner_semantic_meaning`
- `allowed_domains`
- `stat_identity_dependency`
- `value_normalization_dependency`
- `stacking_semantics`
- `polarity_semantics`
- `rounding_policy_dependency`
- `conditional_requirements`
- `exclusion_rules`
- `source_examples`
- `golden_baseline_refs`
- `validation_status`
- `promotion_status`
- `blocked_reasons`
- `provenance`

## Allowed Promotion States

- `audit_only`
- `blocked_by_conditional_behavior`
- `blocked_by_missing_baseline`
- `blocked_by_stat_identity`
- `blocked_by_unknown_operation`
- `blocked_by_unsupported_behavior`
- `blocked_by_value_normalization`
- `candidate_needs_evidence`
- `planner_semantics_experimental`
- `planner_semantics_stable`

## Evidence Requirements

- `source_operation_examples`: Representative source rows for each operation label.
- `expected_planner_interpretation`: Plain semantic meaning approved before calculation use.
- `resolved_stat_identity`: Canonical target stat identities for the operation domain.
- `normalized_or_scale_independent_value`: Value scale normalized or explicitly proven scale-independent.
- `stacking_behavior`: Known stacking and ordering behavior.
- `polarity_behavior`: Known positive, negative, inverse, and reduction semantics.
- `conditional_behavior_policy`: Conditional behavior either excluded or modeled with proof.
- `golden_baseline_coverage`: Representative old planner and operation-specific baselines.
- `dry_run_comparison_result`: Candidate output compared without production consumption.
- `provenance_patch_traceability`: Source path, bundle provenance, and patch/export version.

## Disallowed Assumptions

- Do not infer operation semantics from tooltip text.
- Do not treat structural operation labels as planner-safe semantics.
- Do not assume flat, increased, and more share stacking behavior.
- Do not treat unknown operations as no-op or flat operations.
- Do not model conditional behavior without explicit policy and baselines.
- Do not promote operations while value normalization remains audit-only.
- Do not bridge unresolved skill identities to make operation semantics pass.

## Future Sequence

| Order | Step |
| ---: | --- |
| `1` | Classify source operation labels. |
| `2` | Identify one narrow operation candidate. |
| `3` | Confirm stat identity requirements. |
| `4` | Confirm value normalization dependency. |
| `5` | Define stacking and polarity semantics. |
| `6` | Create operation golden baseline. |
| `7` | Run dry-run comparison. |
| `8` | Mark experimental only after evidence passes. |
| `9` | Promote stable only after repeated validation. |

## Safety Confirmations

- Operation semantics implemented: `false`
- Modifier calculations changed: `false`
- Values normalized: `false`
- Stable-calculable promoted: `false`
- Planner-calculable promoted: `false`
- Production consumed: `false`
- Unknown operations blocked: `true`
- Value normalization: `audit_only`
- Unresolved stat identities blocked: `true`
- Unsupported/scripted behavior excluded: `true`

## Recommended Next Phase

`v3_stat_identity_resolution_policy`
