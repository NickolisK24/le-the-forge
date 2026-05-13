# V2 Stat Modifier Dry Run

Phase 22 adds a dry-run comparison layer for v2 stat/modifier adapter data.
It does not use v2 stat or modifier data for production planner calculations.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Stat registry entries: `2070`
- Modifier rows: `19398`
- Adapter-visible modifier rows: `19398`
- Planner-calculable modifier rows: `0`
- Stable-calculable modifier rows: `0`
- Blocked modifier rows: `19398`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Value Scale Distribution

| Value scale | Count |
| --- | ---: |
| `source_units` | `6248` |
| `unknown` | `13150` |

## Operation Distribution

| Operation | Count |
| --- | ---: |
| `chance` | `69` |
| `cooldown` | `429` |
| `cost` | `440` |
| `duration` | `949` |
| `flat` | `4627` |
| `increased` | `1112` |
| `less` | `1` |
| `more` | `165` |
| `unknown` | `11606` |

## Comparison Categories

| Category | Count |
| --- | ---: |
| `blocked_by_value_normalization` | `19398` |

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

## Current Planner Expectation Gaps

- v2 values are still source_units or unknown, while planner math requires normalized values
- v2 operation identity is unknown for many passive and skill rows
- v2 stat identity still includes stat:unknown and raw serialized stat IDs
- v2 scripted, unsupported, and text-only mechanics are intentionally blocked
- skill-derived modifier rows retain unresolved or ambiguous source identity gaps
- golden output baselines do not yet exist for mechanical remap

## Golden Baseline Requirements

- known item affix stat output
- known passive node stat output
- known skill node stat output
- known unique/set unsupported behavior exclusions
- value scale examples for each normalization family
- operation examples for flat, increased, more, and conditional behavior
- old planner output versus v2 adapter dry-run comparison snapshots

## Runtime Behavior

- No production planner route was added.
- No stat or modifier calculation behavior was changed.
- No crafting, simulation, or stat aggregation behavior was changed.
- No value scale was promoted.
- No unresolved skill identity reference was bridged.
- Dry-run visibility does not imply planner-calculable or stable-calculable eligibility.
