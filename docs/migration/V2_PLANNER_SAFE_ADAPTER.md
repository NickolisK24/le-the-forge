# V2 Planner-Safe Adapter

## Purpose

This document defines the initial planner-safe adapter boundary for future v2 trusted-data consumption.

The adapter is read-only and conservative. It can inspect normalized v2 modifier rows and explain why records are blocked from planner-facing calculation, but it does not switch production planner behavior to v2 data.

## Summary

- Domains inspected: `9`
- Modifiers inspected: `19398`
- Eligible planner-calculable records: `0`
- Blocked records: `19398`
- Stable-calculable count: `0`
- Production consumed: `false`
- Value normalization status: `audit_only`
- Skill identity bridge status: `unbridged`

## Safety Gates

- `trusted_or_explicitly_supported_support_status`
- `known_canonical_id`
- `valid_provenance`
- `non_unsupported_mechanics`
- `non_text_only_behavior`
- `non_scripted_behavior`
- `planner_normalized_value_scale`
- `resolved_stat_identity`
- `resolved_source_identity`
- `backend_policy_stable_calculable`

## Blocked Reasons

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

## Domain Coverage

| Domain | Inspected | Eligible | Blocked | Stable |
| --- | ---: | ---: | ---: | ---: |
| `affix` | `1624` | `0` | `1624` | `0` |
| `idol_affix_modifier` | `647` | `0` | `647` | `0` |
| `item_implicit` | `1182` | `0` | `1182` | `0` |
| `passive_node_modifier` | `1660` | `0` | `1660` | `0` |
| `set_bonus_modifier` | `27` | `0` | `27` | `0` |
| `set_item_modifier` | `287` | `0` | `287` | `0` |
| `skill_node_modifier` | `10843` | `0` | `10843` | `0` |
| `skill_structured_value` | `1081` | `0` | `1081` | `0` |
| `unique_modifier` | `2047` | `0` | `2047` | `0` |

## Runtime Behavior

- Production planner behavior was not changed.
- Crafting, simulation, and stat aggregation behavior were not changed.
- No v2 records are exposed as planner-calculable in this phase.
- Unresolved skill identity references remain unbridged.
- Value normalization remains audit-only.

## Optional Route Status

No planner adapter debug route was added in this phase. The adapter boundary is available to backend code and generated reporting only.

## Recommended Next Step

Use this adapter report to choose the first small planner-safe prototype only after value normalization and stable eligibility policies produce nonzero planner-safe records.
