# V3 Passive And Skill Mechanical Comparison

Phase 9 adds a conservative passive/skill comparison adapter behind the v3 dry-run boundary.
It is comparison infrastructure only and does not calculate production passive or skill mechanics.

## Gate

- Default enabled: `false`
- Disabled response active: `false`
- Enabled only by explicit request: `true`
- Production consumer: `false`

## Summary

- Current rows: `17`
- Candidate rows: `16`
- Simple explainable candidate rows: `5`
- Accepted deltas: `4`
- Rejected deltas: `1`
- Blocked deltas: `12`
- Deterministic hash: `b967b7bd4d2251ef9234ee2d3962bbebce31c05ead1f046ad77f219c7f0cd0c3`

## Component Summary

| Component | Count |
| --- | ---: |
| `passive_node` | `2` |
| `skill_modifier` | `3` |
| `skill_node` | `11` |

## Delta Categories

| Category | Count |
| --- | ---: |
| `accepted_explicit_dry_run_delta` | `1` |
| `accepted_unchanged` | `3` |
| `blocked_ambiguous_skill_identity` | `1` |
| `blocked_conditional_semantics` | `1` |
| `blocked_missing_candidate` | `1` |
| `blocked_missing_provenance` | `1` |
| `blocked_scripted_mechanic` | `1` |
| `blocked_text_only_mechanic` | `1` |
| `blocked_triggered_semantics` | `1` |
| `blocked_unknown_operation` | `1` |
| `blocked_unresolved_skill_identity` | `1` |
| `blocked_unresolved_stat_identity` | `1` |
| `blocked_unsupported_mechanic` | `1` |
| `blocked_value_normalization` | `1` |
| `rejected_unapproved_delta` | `1` |

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `ambiguous_skill_identity` | `1` |
| `candidate_delta_not_approved_for_dry_run` | `1` |
| `conditional_semantics_unresolved` | `1` |
| `missing_candidate_output` | `1` |
| `missing_candidate_provenance` | `1` |
| `scripted_mechanic` | `1` |
| `text_only_mechanic` | `1` |
| `triggered_semantics_unresolved` | `1` |
| `unknown_operation_semantics` | `1` |
| `unresolved_skill_identity` | `1` |
| `unresolved_stat_identity` | `1` |
| `unsupported_mechanic` | `1` |
| `value_normalization_audit_only` | `1` |

## Safety Confirmations

- Production consumed: `false`
- Production enabled: `false`
- Production planner output changed: `false`
- Planner remap performed: `false`
- Skill identity bridge added: `false`
- Conditional semantics implemented: `false`
- Triggered semantics implemented: `false`
- Tooltip semantics inferred: `false`

## Current Limitations

- candidate rows are fixtures or future adapter output, not production planner execution
- passive and skill identity gaps remain blocking conditions
- conditional and triggered semantics are visible blockers, not implemented formulas
- cooldown, duration, chance, proc, scripted, text-only, combat, DPS, crafting, and simulation behavior remains blocked
- changed deltas require explicit dry-run approval and baseline snapshot evidence

## Remaining Blockers Before Limited Opt-In Mechanical Adapter Mode

- approved passive and skill identity bridge policy
- approved conditional and triggered operation semantics
- cooldown, duration, and chance formula contracts
- passive and skill mechanical golden baselines
- candidate passive and skill adapters backed by source data, not tooltip inference
- dry-run parity review across item, affix, passive, and skill domains
- explicit limited opt-in adapter gate review
