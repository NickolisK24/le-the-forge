# V2 Passive Skill Identity Remap

Phase 21 adds an identity/provenance-only passive and skill metadata adapter backed by v2 trusted bundles.
It does not use v2 passive or skill effects for planner calculations.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Passive identity records inspected: `540`
- Skill identity records inspected: `4239`
- Identity-only eligible records: `4779`
- Planner-calculable records: `0`
- Stable-calculable records: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Skill Identity Audit

- Total class/mastery skill refs: `63`
- Safe top-level matches: `60`
- Unresolved refs: `2`
- Ambiguous refs: `1`
- Bridge safe: `false`
- Recommended mapping strategy: `top_level_source_identity_partial_unresolved`

## Fields Exposed

- `canonical_id`
- `display_name`
- `domain`
- `owner_class_ids`
- `owner_mastery_ids`
- `tree_id`
- `skill_id`
- `source_id`
- `source_path`
- `source_tree_id`
- `source_skill_id`
- `source_ability_path_id`
- `identity_match_status`
- `ownership_status`
- `provenance_summary`
- `support_status`
- `trust_level`
- `warnings`
- `debug_summary`
- `identity_only_eligible`
- `planner_calculable`
- `stable_calculable`
- `blocked_reasons`

## Fields Excluded From Calculation

- `modifier_rows`
- `modifier_references`
- `effect_hint_classifications`
- `text_effects`
- `tooltip_text`
- `description_text`
- `damage_types`
- `skill_tags`
- `scaling_tags`
- `cast_data`
- `cooldown`
- `cost`
- `raw_value_min`
- `raw_value_max`
- `normalized_value_min`
- `normalized_value_max`

## Passive Domains

| Domain | Records |
| --- | ---: |
| `passive_tree` | `5` |
| `passive_node` | `535` |

## Skill Domains

| Domain | Records |
| --- | ---: |
| `skill` | `184` |
| `skill_tree` | `136` |
| `skill_node` | `3919` |

## Passive / Skill Tree Metadata Treatment

- Passive tree links exposed: `true`
- Skill tree links exposed: `true`
- Passive node effects exposed as planner stats: `false`
- Skill node effects exposed as planner stats: `false`
- Tooltip text used for mechanics: `false`

## Blocked Reasons

| Reason | Count |
| --- | ---: |
| `identity_only_metadata` | `4779` |
| `passive_skill_effects_not_planner_calculable` | `4779` |
| `stable_calculable_false` | `4779` |
| `value_normalization_audit_only` | `4779` |
| `skill_identity_bridge_unresolved` | `4239` |
| `skill_identity_ambiguous` | `4` |

## Runtime Behavior

- No production planner route was added.
- No frontend debug page was changed in this phase.
- No passive, skill, crafting, simulation, or stat calculation behavior was changed.
- No value scale was promoted.
- No unresolved or ambiguous skill identity reference was bridged.
- Identity-only eligibility does not imply planner-calculable or stable-calculable eligibility.
