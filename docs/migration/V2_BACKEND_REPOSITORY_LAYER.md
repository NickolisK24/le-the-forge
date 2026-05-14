# V2 Backend Repository Layer

## Purpose

This report consolidates the read-only v2 backend repository layer after Phases 3 through 10.5. It documents generated artifact dependencies, loader validation, method coverage, experimental route coverage, and production-consumption safety.

This phase does not remap planner behavior and does not make partial, unsupported, unknown, or source-unit records stable-calculable.

## Summary

- Repository domains: `10`
- Loaded repositories/artifacts: `10`
- Missing artifacts: `0`
- Invalid repositories: `0`
- Missing required methods: `0`
- Experimental routes documented: `38`
- Production consumed: `false`

## Repository Coverage

| Domain | Status | Artifacts | Missing Methods | Experimental Routes |
| --- | --- | ---: | ---: | ---: |
| `affixes` | `ok` | `1` | `0` | `3` |
| `classes_masteries` | `ok` | `1` | `0` | `5` |
| `idols` | `ok` | `2` | `0` | `5` |
| `items` | `ok` | `2` | `0` | `4` |
| `modifiers` | `ok` | `1` | `0` | `3` |
| `passives` | `ok` | `1` | `0` | `4` |
| `skills` | `ok` | `2` | `0` | `6` |
| `stats` | `ok` | `1` | `0` | `2` |
| `unique_sets` | `ok` | `2` | `0` | `6` |
| `value_policy` | `ok` | `1` | `0` | `0` |

## Missing Artifacts

No missing generated artifacts were found.

## Route Coverage

- `affixes`: `/experimental/v2/affixes`, `/experimental/v2/affixes/<affix_id>`, `/experimental/v2/affixes/debug`
- `classes_masteries`: `/experimental/v2/classes`, `/experimental/v2/classes/<class_id>`, `/experimental/v2/masteries`, `/experimental/v2/masteries/<mastery_id>`, `/experimental/v2/classes/debug`
- `idols`: `/experimental/v2/idols`, `/experimental/v2/idols/<idol_id>`, `/experimental/v2/idols/affixes`, `/experimental/v2/idols/affixes/<affix_id>`, `/experimental/v2/idols/debug`
- `items`: `/experimental/v2/items/bases`, `/experimental/v2/items/bases/<item_base_id>`, `/experimental/v2/items/implicits`, `/experimental/v2/items/debug`
- `modifiers`: `/experimental/v2/modifiers`, `/experimental/v2/modifiers/<modifier_id>`, `/experimental/v2/modifiers/debug`
- `passives`: `/experimental/v2/passives`, `/experimental/v2/passives/<tree_id>`, `/experimental/v2/passives/<tree_id>/nodes/<node_id>`, `/experimental/v2/passives/debug`
- `skills`: `/experimental/v2/skills`, `/experimental/v2/skills/<skill_id>`, `/experimental/v2/skills/<skill_id>/tree`, `/experimental/v2/skills/trees/<tree_id>`, `/experimental/v2/skills/trees/<tree_id>/nodes/<node_id>`, `/experimental/v2/skills/debug`
- `stats`: `/experimental/v2/stats`, `/experimental/v2/stats/<stat_id>`
- `unique_sets`: `/experimental/v2/uniques`, `/experimental/v2/uniques/<unique_id>`, `/experimental/v2/sets`, `/experimental/v2/sets/<set_id>`, `/experimental/v2/uniques/debug`, `/experimental/v2/sets/debug`
- `value_policy`: no experimental route; audit/report-only domain.

## Safety Notes

- All v2 repositories remain read-only.
- Production planner, crafting, stat aggregation, simulation, and production reference routes do not consume this registry.
- The value normalization policy remains audit-only.
- Remaining skill identity gaps remain unbridged and must not be treated as resolved.

## Recommended Next Step

Proceed to API contract finalization only after this repository layer is reviewed. Planner remapping should remain deferred until value-scale normalization and stable eligibility policy have stronger evidence.
