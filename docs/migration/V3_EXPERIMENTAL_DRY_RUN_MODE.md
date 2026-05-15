# V3 Experimental Mechanical Dry-Run Mode

Phase 7 introduces the first safety layer for future mechanical comparison.
It compares supplied current-planner snapshots with supplied v3 candidate snapshots.
It does not execute production planner code, normalize values, or implement final mechanics.

## Gate

- Default enabled: `false`
- Disabled response active: `false`
- Enabled response active only when explicitly requested: `true`
- Read-only: `true`
- Production consumer: `false`

## Comparison Summary

- Current output count: `11`
- Candidate output count: `11`
- Accepted deltas: `2`
- Rejected deltas: `1`
- Blocked deltas: `9`
- Deterministic hash: `d07a91ccd056b9f8bfd6037d23598f4d56f85d7a381662116443198c0f618064`

## Delta Categories

| Category | Count |
| --- | ---: |
| `accepted_explicit_dry_run_delta` | `1` |
| `accepted_unchanged` | `1` |
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
- Mechanical calculations performed: `false`
- Value normalization promoted: `false`
- Unsupported mechanics promoted: `false`

## Rollback And Debug Visibility

- The dry-run result includes a deterministic hash, delta category counts, blocked reasons, comparison rows, and safety confirmations.
- Rollback does not require planner changes because this layer is not production-consumed.

## Current Limitations

- candidate outputs are supplied fixtures or future adapter outputs, not production planner execution
- accepted changed deltas require explicit dry-run approval and baseline snapshot evidence
- unsupported, text-only, scripted, unknown-operation, unresolved-identity, and audit-only value rows remain blocked
- no final combat, stat, crafting, DPS, or simulation formulas are implemented

## Remaining Blockers Before Mechanical Remap

- approved value normalization contracts
- approved operation semantics
- resolved stat identities for target domains
- approved skill identity bridge policy
- mechanical golden baselines
- candidate adapter implementation behind this comparison boundary
- explicit production remap gate review
