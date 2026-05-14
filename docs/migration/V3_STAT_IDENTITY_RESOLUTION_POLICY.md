# V3 Stat Identity Resolution Policy

This document defines the stat identity resolution policy.
It does not implement stat identity resolution, stat math, value normalization, or planner output changes.

## Current Stat Identity Landscape

- Stat registry entries: `2070`
- Modifier rows: `19398`
- Unresolved stat identity count: `4714`
- Modifier rows affected by unresolved stat identity: `4714`

## Identity Classification Summary

| Identity State | Stat Count | Modifier Count |
| --- | ---: | ---: |
| `blocked_by_ambiguous_mapping` | `253` | `7064` |
| `blocked_by_unknown_stat` | `1` | `4714` |
| `canonical_candidate_needs_evidence` | `1816` | `7620` |

## Policy Fields

- `stat_identity_id`
- `canonical_stat_id`
- `source_stat_id`
- `source_label`
- `domain`
- `identity_state`
- `match_method`
- `confidence_level`
- `source_examples`
- `modifier_examples`
- `operation_dependencies`
- `value_scale_dependencies`
- `golden_baseline_refs`
- `unsupported_behavior_exclusions`
- `validation_status`
- `promotion_status`
- `blocked_reasons`
- `provenance`

## Identity States

- `audit_only`
- `blocked_by_ambiguous_mapping`
- `blocked_by_behavioral_context`
- `blocked_by_missing_baseline`
- `blocked_by_missing_source_id`
- `blocked_by_operation_semantics`
- `blocked_by_unknown_stat`
- `blocked_by_value_normalization`
- `canonical_candidate_needs_evidence`
- `planner_identity_experimental`
- `planner_identity_stable`
- `source_known`
- `unknown_needs_review`

Current records are not allowed to use `planner_identity_experimental` or `planner_identity_stable` in this phase.

## Evidence Requirements

- `source_stat_id_path`: Source stat ID and source path are present and version-traceable.
- `canonical_stat_id`: Canonical target stat ID is explicit and reversible.
- `stable_source_examples`: Representative source examples are stable across exports.
- `modifier_examples`: Representative modifier examples reference the candidate identity.
- `known_operation_semantics`: Operation semantics are approved for the candidate domain.
- `known_value_scale_or_unnecessary`: Value scale is approved or explicitly irrelevant to identity use.
- `unsupported_scripted_behavior_exclusions`: Unsupported, scripted, and text-only mechanics are excluded or modeled.
- `golden_baseline_coverage`: Existing behavior and candidate identity behavior have golden coverage.
- `patch_version_provenance`: Patch, export, and provenance traceability is recorded.
- `dry_run_comparison_evidence`: Dry-run comparison proves no production planner consumption.
- `repeat_validation_evidence`: Repeated validation confirms the mapping remains stable.

## Disallowed Assumptions

- Do not infer stat identity from tooltip text.
- Do not guess semantic identity from labels alone.
- Do not infer planner behavior without approved operation semantics.
- Do not infer planner behavior without value normalization evidence.
- Do not assume scripted or runtime mechanics from structural names.
- Do not assume unsupported unique or set mechanics are calculable.
- Do not bridge skill identities to make stat identity promotion pass.
- Do not apply cross-domain identity mappings without domain-specific evidence.

## Classification Philosophy

Stat identities are versioned evidence claims, not permanent truths.
Mappings must remain reversible when future patches invalidate assumptions.
The ordering is trusted, validated, explainable, patch-resilient, then intelligent.

## Dependencies

- Operation semantics: `blocked`
- Unknown operations: `11606`
- Value normalization: `audit_only`
- Unknown value scales: `13150`
- Source-units value scales: `6248`

## Production Remap Blockers

- `planner_calculable_zero`: planner-calculable modifier count remains 0
- `stable_calculable_zero`: stable-calculable modifier count remains 0
- `unresolved_stat_identities`: 4714 modifier rows remain affected by unresolved stat identity
- `operation_semantics_unapproved`: operation semantics remain taxonomy-only
- `value_normalization_audit_only`: value normalization remains audit-only
- `missing_golden_baselines`: mechanical stat identity baselines are not implemented

## Future Sequence

| Order | Step |
| ---: | --- |
| `1` | Inventory source stat identity forms. |
| `2` | Classify identity states. |
| `3` | Select narrow canonical candidate. |
| `4` | Collect source examples. |
| `5` | Collect modifier examples. |
| `6` | Verify operation semantics. |
| `7` | Verify value normalization. |
| `8` | Establish golden baseline. |
| `9` | Run dry-run comparison. |
| `10` | Mark experimental only. |
| `11` | Repeat validation. |
| `12` | Promote stable only after sustained evidence. |

## Safety Confirmations

- Stat identities promoted: `false`
- Stat calculations changed: `false`
- Values normalized: `false`
- Operation semantics implemented: `false`
- Planner-calculable promoted: `false`
- Stable-calculable promoted: `false`
- Production consumed: `false`
- Production planner changed: `false`
- Unresolved stat identities blocked: `true`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Recommended Next Phase

`v3_skill_identity_bridge_policy`
