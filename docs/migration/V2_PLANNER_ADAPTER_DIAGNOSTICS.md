# V2 Planner Adapter Diagnostics

Phase 17 adds read-only diagnostics for the v2 planner-safe adapter boundary.
The diagnostics explain what the adapter can inspect, what it would block, and which future remap phases remain non-calculating.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Planner-calculable records: `0`
- Stable-calculable records: `0`
- Blocked records: `19398`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Adapter-Visible Versus Planner-Calculable

- Adapter-visible records: `19398`
- Planner-calculable records: `0`
- Domains checked: `9`

## Display-Only Candidates

- `item/base display metadata`: `ready_for_adapter_later` (needs non-calculating API adapter tests)
- `affix display and provenance`: `ready_for_adapter_later` (must stay display-only until value policy is proven)
- `class/mastery metadata`: `ready_for_adapter_later` (metadata can be inspected; planner skill ownership remains partially unresolved)

## Blocked Mechanical Data

- `affix modifier math`: `blocked_by_value_normalization` (source_units_value_scale, unstable_support_status)
- `item implicit modifier math`: `blocked_by_value_normalization` (source_units_value_scale, unstable_support_status)
- `unique and set mechanics`: `blocked_by_unsupported_mechanics` (unsupported/text-only report remains intentionally visible)
- `idol base and idol affix math`: `blocked_by_value_normalization` (source_units_value_scale, IDOL_ALTAR warnings remain display-only)
- `skill ownership`: `blocked_by_identity_resolution` (unresolved_refs=2, ambiguous_refs=1)
- `passive node behavior`: `blocked_by_unsupported_mechanics` (scripted and unsupported passive records remain non-calculable)
- `skill and skill tree behavior`: `blocked_by_unsupported_mechanics` (scripted and unsupported skill records remain non-calculable)
- `stat/modifier adapter math`: `blocked_by_value_normalization` (unknown_value_scale=13150, source_units_value_scale=6248)
- `crafting engine`: `blocked_by_behavioral_risk` (production behavior depends on legacy craft engine and FP constants)
- `simulation/combat engine`: `blocked_by_behavioral_risk` (production behavior depends on legacy stat fields and combat formulas)
- `production reference routes`: `manual_only_currently` (routes expose legacy DB/static data and must not switch without compatibility tests)
- `frontend planner API clients`: `blocked_by_missing_tests` (needs adapter dry-run and UI compatibility tests before remap)

## Top Blocked Reasons

| Reason | Count |
| --- | ---: |
| `not_stable_calculable` | `19398` |
| `unstable_support_status` | `19398` |
| `unknown_value_scale` | `13150` |
| `unresolved_skill_identity` | `11924` |
| `unknown_operation` | `11606` |
| `scripted_behavior` | `7495` |
| `source_units_value_scale` | `6248` |
| `unsupported_behavior` | `5276` |
| `unresolved_stat_identity` | `4714` |
| `text_only_behavior` | `265` |

## Future Remap Phase Status

1. **Read-only planner diagnostics using v2 adapter** - `diagnostic_or_display_only_candidate`
2. **Non-calculating metadata remap** - `diagnostic_or_display_only_candidate`
3. **Item/base display metadata remap** - `diagnostic_or_display_only_candidate`
4. **Affix display and provenance remap** - `diagnostic_or_display_only_candidate`
5. **Passive/skill identity-only remap where safe** - `diagnostic_or_display_only_candidate`
6. **Stat/modifier adapter dry-run comparison** - `blocked_until_safety_gates_pass`
7. **Golden baseline test creation** - `blocked_until_safety_gates_pass`
8. **Limited opt-in experimental planner adapter mode** - `blocked_until_safety_gates_pass`
9. **Production remap after stable-calculable gates pass** - `blocked_until_safety_gates_pass`

## Runtime Behavior

- No production planner route was added.
- No production planner, crafting, simulation, or stat output was changed.
- No value scale was promoted.
- No unresolved skill identity was bridged.
- The optional diagnostics route was skipped; this phase is module/script/report only.
