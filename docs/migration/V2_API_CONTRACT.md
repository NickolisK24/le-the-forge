# V2 API Contract

## Purpose

This document finalizes the experimental v2 API response contract for trusted-data debug and future integration work. It standardizes envelopes, metadata, support summaries, provenance, debug sections, and error shape without enabling production planner consumption.

## Summary

- Experimental v2 routes: `38`
- Standardized routes: `38`
- Repository domains: `10`
- Metadata coverage: `38`
- Support summary coverage: `38`
- Provenance coverage: `38`
- Error contract coverage: `38`
- Production consumed: `false`

## Standard Envelope

Every `/experimental/v2/*` JSON response is wrapped with:

- `data`
- `meta`
- `support_summary`
- `warnings`
- `provenance`
- `debug`

Existing top-level route fields such as `records`, `record`, and `debug_summary` are preserved for frontend debug compatibility.

## Error Contract

Experimental v2 errors expose:

```json
{
  "error": {
    "code": "",
    "message": "",
    "details": {}
  },
  "meta": {},
  "debug": {}
}
```

## Route Coverage

| Domain | Route | Envelope | Error Contract |
| --- | --- | --- | --- |
| `affixes` | `/experimental/v2/affixes` | `true` | `true` |
| `affixes` | `/experimental/v2/affixes/<affix_id>` | `true` | `true` |
| `affixes` | `/experimental/v2/affixes/debug` | `true` | `true` |
| `classes_masteries` | `/experimental/v2/classes` | `true` | `true` |
| `classes_masteries` | `/experimental/v2/classes/<class_id>` | `true` | `true` |
| `classes_masteries` | `/experimental/v2/masteries` | `true` | `true` |
| `classes_masteries` | `/experimental/v2/masteries/<mastery_id>` | `true` | `true` |
| `classes_masteries` | `/experimental/v2/classes/debug` | `true` | `true` |
| `idols` | `/experimental/v2/idols` | `true` | `true` |
| `idols` | `/experimental/v2/idols/<idol_id>` | `true` | `true` |
| `idols` | `/experimental/v2/idols/affixes` | `true` | `true` |
| `idols` | `/experimental/v2/idols/affixes/<affix_id>` | `true` | `true` |
| `idols` | `/experimental/v2/idols/debug` | `true` | `true` |
| `items` | `/experimental/v2/items/bases` | `true` | `true` |
| `items` | `/experimental/v2/items/bases/<item_base_id>` | `true` | `true` |
| `items` | `/experimental/v2/items/implicits` | `true` | `true` |
| `items` | `/experimental/v2/items/debug` | `true` | `true` |
| `modifiers` | `/experimental/v2/modifiers` | `true` | `true` |
| `modifiers` | `/experimental/v2/modifiers/<modifier_id>` | `true` | `true` |
| `modifiers` | `/experimental/v2/modifiers/debug` | `true` | `true` |
| `passives` | `/experimental/v2/passives` | `true` | `true` |
| `passives` | `/experimental/v2/passives/<tree_id>` | `true` | `true` |
| `passives` | `/experimental/v2/passives/<tree_id>/nodes/<node_id>` | `true` | `true` |
| `passives` | `/experimental/v2/passives/debug` | `true` | `true` |
| `skills` | `/experimental/v2/skills` | `true` | `true` |
| `skills` | `/experimental/v2/skills/<skill_id>` | `true` | `true` |
| `skills` | `/experimental/v2/skills/<skill_id>/tree` | `true` | `true` |
| `skills` | `/experimental/v2/skills/trees/<tree_id>` | `true` | `true` |
| `skills` | `/experimental/v2/skills/trees/<tree_id>/nodes/<node_id>` | `true` | `true` |
| `skills` | `/experimental/v2/skills/debug` | `true` | `true` |
| `stats` | `/experimental/v2/stats` | `true` | `true` |
| `stats` | `/experimental/v2/stats/<stat_id>` | `true` | `true` |
| `unique_sets` | `/experimental/v2/uniques` | `true` | `true` |
| `unique_sets` | `/experimental/v2/uniques/<unique_id>` | `true` | `true` |
| `unique_sets` | `/experimental/v2/sets` | `true` | `true` |
| `unique_sets` | `/experimental/v2/sets/<set_id>` | `true` | `true` |
| `unique_sets` | `/experimental/v2/uniques/debug` | `true` | `true` |
| `unique_sets` | `/experimental/v2/sets/debug` | `true` | `true` |
| `value_policy` | `(report-only domain)` | `false` | `false` |

## Safety Rules

- Routes remain experimental and read-only.
- Production planner, crafting, stat aggregation, simulation, and production reference routes do not consume v2 data.
- Stable-calculable status remains governed by Phase 10 safety rules.
- Value normalization policy remains audit-only.
- Unresolved skill identity references remain unbridged.

## Remaining Inconsistencies

No remaining route-contract inconsistencies are reported for Phase 12. Planner consumption remains intentionally deferred.
