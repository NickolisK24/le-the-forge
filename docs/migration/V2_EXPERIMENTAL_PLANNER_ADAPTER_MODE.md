# V2 Experimental Planner Adapter Mode

Phase 24 adds a limited opt-in experimental planner adapter mode.
The mode exposes diagnostic, display, dry-run, and baseline readiness context only.

## Gate

- Gate mechanism: `explicit_enabled_argument`
- Default enabled: `false`
- Disabled response active: `false`
- Enabled response active: `true`
- Optional route added: `false`

## Included Summaries

- `adapter_eligibility`
- `planner_adapter_diagnostics`
- `planner_metadata`
- `item_base_display_metadata`
- `affix_display_provenance`
- `passive_skill_identity`
- `stat_modifier_dry_run`
- `golden_baseline_readiness`

## Safety State

- Production consumed: `false`
- Production planner output changed: `false`
- Planner remap performed: `false`
- Mechanical calculations performed: `false`
- Planner-calculable count: `0`
- Stable-calculable count: `0`
- Blocked modifier count: `19398`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Baseline Readiness

- Safe-now baseline fixtures: `7`
- Blocked baseline fixtures: `6`
- Display-only candidates: `3`
- Blocked mechanical categories: `12`

## Top Blocked Reasons

| Reason | Count |
| --- | ---: |
| `not_stable_calculable` | `77592` |
| `unstable_support_status` | `77592` |
| `unknown_value_scale` | `52600` |
| `unresolved_skill_identity` | `47696` |
| `unknown_operation` | `46424` |
| `scripted_behavior` | `29980` |
| `source_units_value_scale` | `24992` |
| `unsupported_behavior` | `21104` |
| `unresolved_stat_identity` | `18856` |
| `stable_calculable_false` | `6419` |
| `identity_only_metadata` | `4779` |
| `passive_skill_effects_not_planner_calculable` | `4779` |

## Runtime Behavior

- No production planner route was added.
- No stat or modifier calculation behavior was changed.
- No crafting, simulation, or stat aggregation behavior was changed.
- No value scale was promoted.
- No unresolved skill identity reference was bridged.
- The experimental mode remains disabled unless explicitly requested.
