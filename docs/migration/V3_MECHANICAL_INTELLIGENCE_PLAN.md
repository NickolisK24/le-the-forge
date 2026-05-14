# V3 Mechanical Intelligence Plan

This audit defines the v3 scope and order of work. It is planning-only.
It does not implement mechanics, normalize values, bridge skill identities, or change planner output.

## Readiness Decision

- V3 planning ready: `true`
- V3 mechanical implementation ready: `false`
- Production planner remap ready: `false`
- Recommended next phase: `v3_value_normalization_contract_design`

## Scope

V3 should deliver deterministic, explainable mechanical intelligence only after policy, identity, value, operation, baseline, and dry-run gates are satisfied.

## Non-Goals

- Do not implement value normalization in this phase.
- Do not implement stat or modifier calculations in this phase.
- Do not wire v2 data into production planner math.
- Do not infer tooltip mechanics.
- Do not bridge unresolved skill identities.
- Do not promote records to stable-calculable.

## Mechanical Domains

| Domain | Classification | Severity |
| --- | --- | --- |
| `value_normalization` | `ready_for_policy_design` | `critical` |
| `operation_semantics` | `blocked_by_value_normalization` | `critical` |
| `stat_identity_resolution` | `ready_for_policy_design` | `critical` |
| `modifier_application_semantics` | `blocked_by_operation_semantics` | `critical` |
| `item_affix_stat_output` | `blocked_by_missing_golden_baseline` | `high` |
| `passive_node_stat_output` | `blocked_by_unsupported_mechanics` | `high` |
| `skill_node_stat_output` | `blocked_by_skill_identity` | `high` |
| `unique_set_unsupported_behavior_exclusions` | `blocked_by_unsupported_mechanics` | `high` |
| `idol_mechanic_treatment` | `blocked_by_value_normalization` | `medium` |
| `skill_identity_bridge_policy` | `ready_for_policy_design` | `critical` |
| `deterministic_stat_resolution_adapter` | `blocked_by_missing_golden_baseline` | `critical` |
| `experimental_mechanical_dry_run_comparison` | `blocked_by_missing_golden_baseline` | `critical` |
| `production_planner_remap_gates` | `blocked_by_behavioral_risk` | `critical` |

## Ordered Phase Sequence

| Order | Phase | Description |
| ---: | --- | --- |
| `1` | `v3_value_normalization_contract_design` | Design value normalization contracts and source-unit policy. |
| `2` | `v3_operation_semantics_taxonomy` | Define operation taxonomy and unsupported operation handling. |
| `3` | `v3_stat_identity_resolution_policy` | Define stat identity resolution policy and target-domain scope. |
| `4` | `v3_skill_identity_bridge_policy` | Define evidence requirements for skill identity bridges. |
| `5` | `v3_golden_mechanical_baseline_creation` | Create existing-production golden baselines before mechanical changes. |
| `6` | `v3_deterministic_stat_resolution_adapter_design` | Design deterministic adapter behavior and explanations. |
| `7` | `v3_experimental_mechanical_dry_run_mode` | Add opt-in dry-run comparison without changing production output. |
| `8` | `v3_item_affix_mechanical_comparison` | Compare item and affix mechanical output under approved gates. |
| `9` | `v3_passive_skill_mechanical_comparison` | Compare passive and skill output under approved identity and unsupported policies. |
| `10` | `v3_limited_opt_in_mechanical_adapter_mode` | Expose limited opt-in mechanical adapter mode after dry-run evidence. |
| `11` | `v3_production_planner_remap_gate_audit` | Audit production remap gates and rollback/debug path. |
| `12` | `v3_production_remap_after_stable_gates` | Production remap only after all stable-calculable gates pass. |

## Production Remap Gates

- stable-calculable count greater than zero only through proven policy
- value normalization contracts approved
- operation semantics approved
- stat identities resolved for target domain
- skill identity bridge policy approved
- unsupported/scripted mechanics excluded
- golden baselines passing
- old planner versus v3 dry-run comparison passing
- production non-consumption guard intentionally updated only when remap is approved
- rollback and debug path exists

## Required Golden Baseline Strategy

- `known_item_affix_stat_output`: Existing planner output for representative item affix stat math.
- `known_passive_node_stat_output`: Existing planner output for representative passive node stat math.
- `known_skill_node_stat_output`: Existing planner output for representative skill node stat math.
- `unique_set_unsupported_exclusions`: Assertions that unsupported unique/set mechanics remain excluded from stable math.
- `value_scale_normalization_examples`: Golden examples proving source-unit to planner-normalized conversion families.
- `operation_examples`: Golden examples for flat, increased, more, and conditional operation handling.
- `planner_output_vs_v2_dry_run_snapshots`: Snapshot comparisons between current planner output and v2 adapter dry-run explanations.

## Known Risks

- `unknown_value_scales`: Unknown values remain blocked from mechanical use.
- `source_units_without_contracts`: Source-unit values remain blocked until conversion contracts are approved.
- `unknown_operations`: Unknown operations remain blocked.
- `unresolved_stat_identities`: Unresolved stat identities remain blocked.
- `unresolved_skill_identities`: Unresolved or ambiguous skill identities remain unbridged.
- `scripted_text_only_unsupported_mechanics`: Scripted, text-only, and unsupported mechanics remain excluded by default.

## Safety State

- Production consumed: `false`
- Planner-calculable count: `0`
- Stable-calculable count: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`
- Runtime behavior changed: `false`

## Recommended Next Phase

`v3_value_normalization_contract_design` should define value families, source-unit handling, unknown value policy, approval criteria, and fixtures without changing production planner behavior.
