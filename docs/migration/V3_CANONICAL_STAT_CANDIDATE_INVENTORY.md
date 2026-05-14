# V3 Canonical Stat Candidate Inventory

This document ranks future canonical stat identity candidates for investigation only.
It does not promote stat identities, normalize values, implement operation semantics, or change planner output.

## Summary

- Total stat registry entries: `2070`
- Total modifier rows: `19398`
- Unresolved stat identity count: `4714`
- Ambiguous mapping stat count: `253`
- Ambiguous mapping modifier count: `7064`
- Candidate-needs-evidence stat count: `1816`
- Candidate-needs-evidence modifier count: `7620`

## Candidate Status Distribution

- `candidate_blocked_by_ambiguity`: `253`
- `candidate_blocked_by_behavioral_context`: `52`
- `candidate_blocked_by_operation_semantics`: `5`
- `candidate_blocked_by_skill_identity_bridge`: `389`
- `candidate_blocked_by_value_normalization`: `444`
- `excluded_unsupported_behavior`: `926`
- `unknown_needs_review`: `1`

## Ranking Criteria

- clear source identity
- low ambiguity
- simple operation families
- simple value scale requirements
- many modifier examples
- low unsupported behavior risk
- no skill identity bridge requirement
- likely golden baseline feasibility

## Recommended Future Pilot Candidates

| Candidate | Domain | Modifiers | Status | Blocking Reasons |
| --- | --- | ---: | --- | --- |
| `stat:added_attunement_none` | `affix` | `5` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_intelligence_none` | `affix` | `5` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:increased_castspeed_none` | `affix` | `5` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_dexterity_none` | `affix` | `4` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_increasedareaforareaskills_none` | `affix` | `4` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_criticalmultiplier_bow` | `item_implicit` | `3` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_strength_none` | `affix` | `3` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_healthleech_none` | `affix` | `2` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_increasedleechrate_none` | `affix` | `2` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |
| `stat:added_morefreezerateperstackofchill_none` | `affix` | `2` | `candidate_blocked_by_value_normalization` | `missing_golden_baseline, value_normalization_audit_only` |

## Explicit Exclusions And Blockers

| Candidate | Status | Reason |
| --- | --- | --- |
| `stat:added_armour` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:increased_movespeed` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_ailmentchance` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_intelligence` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_mana` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:increased_damage_minion` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_health` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:increased_manaregen` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_increasedailmentduration` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_blockchance` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:added_blockeffectiveness` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |
| `stat:increased_attackspeed_melee` | `excluded_unsupported_behavior` | `missing_golden_baseline, unsupported_unique_set_behavior` |

## Evidence Gaps

- confirmed canonical stat ID
- confirmed source stat ID/path
- stable source examples
- modifier examples
- known operation semantics
- known value scale or explicit no-normalization-needed decision
- unsupported behavior exclusions
- golden baseline references
- dry-run comparison evidence
- repeat validation evidence
- patch/version provenance

## Production Remap Blockers

- planner-calculable count remains 0
- stable-calculable count remains 0
- production consumed remains false
- value normalization remains audit_only
- operation semantics remain taxonomy-only
- ambiguous mappings remain blocked
- unresolved stat identities remain blocked
- skill identity bridge remains unbridged
- golden mechanical baselines are missing

## Safety Confirmations

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
