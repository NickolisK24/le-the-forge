# V3 Item And Affix Mechanical Comparison

Phase 8 adds the first item/affix domain adapter behind the v3 dry-run comparison boundary.
It is read-only, opt-in, and non-production-consuming.
It does not replace production planner math or implement final combat/stat formulas.

## Gate

- Default enabled: `false`
- Disabled response active: `false`
- Enabled only by explicit request: `true`
- Production consumer: `false`

## Summary

- Current rows: `13`
- Candidate rows: `13`
- Mechanically explainable candidate rows: `6`
- Accepted deltas: `4`
- Rejected deltas: `1`
- Blocked deltas: `9`
- Deterministic hash: `8f2e427896126d7fc7dbea6e8e59ea58eb686429f872fc78fca8113f6993031f`

## Component Summary

| Component | Count |
| --- | ---: |
| `affix` | `11` |
| `implicit` | `1` |
| `item_base` | `1` |

## Delta Categories

| Category | Count |
| --- | ---: |
| `accepted_explicit_dry_run_delta` | `1` |
| `accepted_unchanged` | `3` |
| `blocked_missing_candidate` | `1` |
| `blocked_missing_current` | `1` |
| `blocked_missing_provenance` | `1` |
| `blocked_scripted_mechanic` | `1` |
| `blocked_text_only_mechanic` | `1` |
| `blocked_unknown_operation` | `1` |
| `blocked_unresolved_stat_identity` | `1` |
| `blocked_unsupported_mechanic` | `1` |
| `blocked_value_normalization` | `1` |
| `rejected_unapproved_delta` | `1` |

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `candidate_delta_not_approved_for_dry_run` | `1` |
| `missing_candidate_output` | `1` |
| `missing_candidate_provenance` | `1` |
| `missing_current_output` | `1` |
| `scripted_mechanic` | `1` |
| `text_only_mechanic` | `1` |
| `unknown_operation_semantics` | `1` |
| `unresolved_stat_identity` | `1` |
| `unsupported_mechanic` | `1` |
| `value_normalization_audit_only` | `1` |

## Safety Confirmations

- Production consumed: `false`
- Production enabled: `false`
- Production planner output changed: `false`
- Planner remap performed: `false`
- Runtime stat aggregation changed: `false`
- Unique/set logic added: `false`
- Tooltip semantics inferred: `false`

## Current Limitations

- only item bases, implicits, and standard affix rows are represented
- candidate rows are fixtures or future adapter output, not production planner execution
- unique, set, scripted, text-only, conditional, proc, skill-specific, combat, DPS, and crafting behavior remains blocked
- value normalization must already be approved per row; unknown or audit-only values remain blocked
- changed deltas require explicit dry-run approval and baseline snapshot evidence

## Remaining Blockers Before Passive/Skill Comparison

- passive and skill identity bridge policy
- passive and skill mechanical golden baselines
- unsupported scripted passive and skill behavior policy
- operation semantics for conditional, triggered, cooldown, duration, and chance effects
- candidate passive and skill row adapters behind the dry-run boundary
