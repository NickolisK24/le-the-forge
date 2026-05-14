# V2 Item Base Display Metadata

Phase 19 adds a display-only item/base metadata adapter backed by v2 trusted item bundles.
It does not use v2 item bases, implicits, or modifier values for planner calculations.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Item bases inspected: `542`
- Implicits loaded: `1182`
- Display-only eligible item bases: `542`
- Planner-calculable item bases: `0`
- Stable-calculable item bases: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Fields Exposed

- `canonical_id`
- `display_name`
- `domain`
- `item_category`
- `item_type`
- `subtype`
- `slot`
- `classification`
- `level_requirement`
- `class_restrictions`
- `mastery_restrictions`
- `implicit_count`
- `implicit_metadata`
- `source_path`
- `provenance_summary`
- `support_status`
- `trust_level`
- `warnings`
- `debug_summary`
- `display_only_eligible`
- `planner_calculable`
- `stable_calculable`
- `blocked_reasons`

## Fields Excluded From Calculation

- `base_stats`
- `modifier_rows`
- `value_range`
- `value_min`
- `value_max`
- `raw_value_min`
- `raw_value_max`
- `normalized_value_min`
- `normalized_value_max`

## Domains

| Domain | Item bases |
| --- | ---: |
| `accessory` | `154` |
| `armor` | `194` |
| `weapon` | `194` |

## Implicit Metadata Treatment

- Implicit records loaded: `1182`
- Implicit metadata records exposed: `1182`
- Modifier rows exposed: `false`
- Modifier values exposed as planner stats: `false`

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `display_only_metadata` | `542` |
| `implicit_values_not_planner_normalized` | `542` |
| `stable_calculable_false` | `542` |

## Runtime Behavior

- No production planner route was added.
- No frontend debug page was changed in this phase.
- No item, implicit, crafting, simulation, or stat calculation behavior was changed.
- No value scale was promoted.
- Display-only eligibility does not imply planner-calculable or stable-calculable eligibility.
