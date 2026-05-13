# V2 Affix Display Provenance

Phase 20 adds a display/provenance-only affix metadata adapter backed by v2 trusted affix bundles.
It does not use v2 affixes, tiers, or modifier values for planner calculations.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Affixes inspected: `1098`
- Display-only eligible affixes: `1098`
- Planner-calculable affixes: `0`
- Stable-calculable affixes: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Fields Exposed

- `canonical_id`
- `display_name`
- `domain`
- `affix_type`
- `prefix_suffix`
- `categories`
- `slot_restrictions`
- `item_type_restrictions`
- `class_restrictions`
- `mastery_restrictions`
- `tier_count`
- `modifier_reference_count`
- `modifier_reference_metadata`
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

- `tier_ranges`
- `normalized_fields`
- `raw_value_min`
- `raw_value_max`
- `normalized_value_min`
- `normalized_value_max`
- `min_value`
- `max_value`

## Domains

| Domain | Affixes |
| --- | ---: |
| `equipment` | `615` |
| `idol` | `483` |

## Prefix/Suffix

| Classification | Affixes |
| --- | ---: |
| `prefix` | `832` |
| `suffix` | `266` |

## Tier and Modifier Metadata Treatment

- Tier counts exposed: `true`
- Tier ranges exposed: `false`
- Modifier reference metadata records exposed: `1624`
- Modifier values exposed as planner stats: `false`

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `affix_values_not_planner_normalized` | `1098` |
| `display_only_metadata` | `1098` |
| `stable_calculable_false` | `1098` |

## Runtime Behavior

- No production planner route was added.
- No frontend debug page was changed in this phase.
- No affix, modifier, crafting, simulation, or stat calculation behavior was changed.
- No value scale was promoted.
- Display-only eligibility does not imply planner-calculable or stable-calculable eligibility.
