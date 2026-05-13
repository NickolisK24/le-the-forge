# V2 Planner Metadata Remap

Phase 18 adds a non-calculating planner metadata layer.
It exposes v2 identity, support, provenance, warnings, debug status, and adapter blocked reasons without feeding v2 values into planner math.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Metadata records inspected: `19398`
- Display-only eligible records: `19398`
- Planner-calculable records: `0`
- Stable-calculable records: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Fields Exposed

- `canonical_id`
- `display_name`
- `domain`
- `source_id`
- `source_path`
- `support_status`
- `trust_level`
- `provenance_summary`
- `warnings`
- `debug_summary`
- `adapter_blocked_reasons`
- `planner_calculable`
- `stable_calculable`
- `display_only_eligible`

## Calculation Fields Explicitly Excluded

- `raw_value_min`
- `raw_value_max`
- `normalized_value_min`
- `normalized_value_max`

## Domain Summary

| Domain | Inspected | Display-only | Planner-calculable | Stable |
| --- | ---: | ---: | ---: | ---: |
| `affix` | `1624` | `1624` | `0` | `0` |
| `idol_affix_modifier` | `647` | `647` | `0` | `0` |
| `item_implicit` | `1182` | `1182` | `0` | `0` |
| `passive_node_modifier` | `1660` | `1660` | `0` | `0` |
| `set_bonus_modifier` | `27` | `27` | `0` | `0` |
| `set_item_modifier` | `287` | `287` | `0` | `0` |
| `skill_node_modifier` | `10843` | `10843` | `0` | `0` |
| `skill_structured_value` | `1081` | `1081` | `0` | `0` |
| `unique_modifier` | `2047` | `2047` | `0` | `0` |

## Display-Only Candidates

- `item/base display metadata`: needs non-calculating API adapter tests
- `affix display and provenance`: must stay display-only until value policy is proven
- `class/mastery metadata`: metadata can be inspected; planner skill ownership remains partially unresolved

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

## Runtime Behavior

- No production planner route was added.
- No planner, crafting, simulation, or stat output was changed.
- No value scale was promoted.
- No unresolved skill identity was bridged.
- Display-only eligibility does not imply planner-calculable or stable-calculable eligibility.
