# V3 Limited Mechanical Adapter Mode

Phase 10 introduces the first limited candidate execution path behind explicit dry-run and domain gates.
It is not production mechanical remap work and it does not change production planner behavior.

## Gate

- Default enabled: `false`
- Disabled response active: `false`
- Enabled only by explicit request: `true`
- Production consumer: `false`
- Allowed domains: `item_affix, passive_skill`

## Summary

- Executed rows: `8`
- Rejected rows: `2`
- Blocked rows: `21`
- Candidate aggregates: `8`
- Deterministic hash: `e677c553535939d66d86604819725419b2b72d1ae6d69a07fa3f2aab77c061cf`

## Execution Categories

| Category | Count |
| --- | ---: |
| `blocked_ambiguous_skill_identity` | `1` |
| `blocked_conditional_semantics` | `1` |
| `blocked_missing_candidate` | `2` |
| `blocked_missing_current` | `1` |
| `blocked_missing_provenance` | `2` |
| `blocked_scripted_mechanic` | `2` |
| `blocked_text_only_mechanic` | `2` |
| `blocked_triggered_semantics` | `1` |
| `blocked_unknown_operation` | `2` |
| `blocked_unresolved_skill_identity` | `1` |
| `blocked_unresolved_stat_identity` | `2` |
| `blocked_unsupported_mechanic` | `2` |
| `blocked_value_normalization` | `2` |
| `executed_accepted_dry_run_delta` | `2` |
| `executed_accepted_unchanged` | `6` |
| `rejected_unapproved_delta` | `2` |

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `candidate_delta_not_approved_for_dry_run` | `2` |
| `missing_candidate_output` | `2` |
| `missing_candidate_provenance` | `2` |
| `scripted_mechanic` | `2` |
| `text_only_mechanic` | `2` |
| `unknown_operation_semantics` | `2` |
| `unresolved_stat_identity` | `2` |
| `unsupported_mechanic` | `2` |
| `value_normalization_audit_only` | `2` |
| `ambiguous_skill_identity` | `1` |
| `conditional_semantics_unresolved` | `1` |
| `missing_current_output` | `1` |
| `triggered_semantics_unresolved` | `1` |
| `unresolved_skill_identity` | `1` |

## Execution Gates

- dry_run_enabled_required: `True`
- domain_gate_required: `True`
- allowed_domains: `['item_affix', 'passive_skill']`
- stable_calculable_required: `True`
- approved_normalization_required: `True`
- approved_operation_semantics_required: `True`
- approved_identity_resolution_required: `True`
- provenance_required: `True`
- accepted_dry_run_category_required: `True`
- unsupported_text_only_scripted_blocked: `True`
- production_consumption_allowed: `False`

## Safety Confirmations

- Production consumed: `false`
- Production enabled: `false`
- Production planner output changed: `false`
- Planner remap performed: `false`
- Live stat aggregation changed: `false`
- Candidate execution default enabled: `false`

## Current Limitations

- execution consumes only supplied comparison reports, not production planner runtime output
- only rows accepted by dry-run comparison are executable
- aggregates are deterministic candidate sums for audit, not live stat aggregation
- unsupported, text-only, scripted, unknown-operation, unresolved-identity, conditional, and triggered rows remain blocked
- combat, DPS, crafting, optimizer, simulation, and production stat remap behavior is not implemented

## Remaining Blockers Before Production Remap Gate Audit

- source-backed candidate adapter inventory for each supported domain
- golden baseline approval for limited candidate aggregates
- formal production remap gate review
- explicit rollback and kill-switch plan for any future production opt-in
- approved semantics for conditional, triggered, cooldown, duration, chance, and proc behavior
- approved identity bridge policy for passive and skill rows
