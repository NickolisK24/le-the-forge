# V3 Golden Baseline Readiness Audit

This document defines golden baseline readiness requirements only.
It does not create fixtures, execute baselines, promote candidates, normalize values, or change planner output.

## Summary

- Total candidate count from Phase 5: `2070`
- Recommended pilot candidates reviewed: `10`
- Explicitly excluded candidates reviewed: `20`
- Planner-calculable count: `0`
- Stable-calculable count: `0`

## Candidate Readiness Distribution

- `blocked_by_unsupported_behavior`: `20`
- `blocked_by_value_normalization`: `10`

## Recommended Pilot Candidates Reviewed

| Candidate | Readiness | Status From Phase 5 | Required Case Types |
| --- | --- | --- | --- |
| `stat:added_attunement_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `class_attribute_source, item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_intelligence_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `class_attribute_source, item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:increased_castspeed_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_increased_stat` |
| `stat:added_dexterity_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `class_attribute_source, item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_increasedareaforareaskills_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_criticalmultiplier_bow` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_strength_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `class_attribute_source, item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_healthleech_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_increasedleechrate_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |
| `stat:added_morefreezerateperstackofchill_none` | `blocked_by_value_normalization` | `candidate_blocked_by_value_normalization` | `item_affix_source_only, multiple_modifiers_same_stat, single_modifier_flat_stat` |

## Required Future Baseline Case Types

- `single_modifier_flat_stat`
- `single_modifier_increased_stat`
- `multiple_modifiers_same_stat`
- `mixed_operation_same_stat`
- `item_affix_source_only`
- `passive_source_only`
- `skill_tree_source_only`
- `idol_source_only`
- `class_attribute_source`
- `resistance_source`
- `negative_or_cost_modifier`
- `conditional_modifier_exclusion`
- `unsupported_behavior_exclusion`

## Proposed Future Fixture Schema

- `baseline_id`
- `candidate_id`
- `canonical_stat_id`
- `source_record_refs`
- `input_modifiers`
- `expected_normalized_values`
- `expected_operation_semantics`
- `expected_final_stat_delta`
- `excluded_behavior_notes`
- `patch_version`
- `provenance`
- `validation_status`

## Explicit Exclusions

- unique/set scripted mechanics
- tooltip-only mechanics
- conditional runtime effects
- conversion mechanics
- threshold mechanics
- minion inheritance
- skill-specific behavior without skill bridge
- ambiguous source mappings
- unknown operation semantics
- unknown/source-unit value scales
- unsupported behavior

## Repeat Validation Policy

- `minimum_repeated_runs`: `3`
- `requires_distinct_exports_or_patch_snapshots`: `true`
- `requires_old_planner_comparison`: `true`
- `requires_dry_run_comparison`: `true`
- `requires_no_unexplained_delta`: `true`
- `requires_reversible_promotion_record`: `true`

## Production Remap Blockers

- planner-calculable count remains 0
- stable-calculable count remains 0
- production consumed remains false
- value normalization remains audit_only
- operation semantics remain taxonomy-only
- stat identity policy remains audit-only
- skill identity bridge remains unbridged
- golden baselines are not created
- repeat validation has not run

## Safety Confirmations

- Golden baselines created: `false`
- Stat identities promoted: `false`
- Canonical candidates promoted: `false`
- Stat calculations changed: `false`
- Values normalized: `false`
- Operation semantics implemented: `false`
- Planner-calculable promoted: `false`
- Stable-calculable promoted: `false`
- Production consumed: `false`
- Production planner changed: `false`
- Unresolved stat identities blocked: `true`
- Ambiguous mappings blocked: `true`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Recommended Next Phase

`v3_skill_identity_bridge_policy`
