# V2 Stat and Modifier Normalization

## Purpose

This report defines the read-only Phase 10 normalization layer for stat-like identifiers and modifier-like rows across generated v2 data bundles. It does not remap planner, crafting, stat aggregation, or simulation behavior.

## Generation command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_stat_modifier_normalization.py --stat-output docs\generated\v2_stat_registry.json --modifier-output docs\generated\v2_modifier_registry.json --validation-output docs\generated\v2_modifier_validation_report.json --blocked-reasons-output docs\generated\v2_modifier_blocked_reasons_report.json --markdown-output docs\migration\V2_STAT_MODIFIER_NORMALIZATION.md
```

## Summary

- Stat registry entries: `2070`
- Modifier registry entries: `19398`
- Stable-calculable modifiers: `0`
- Validation errors: `0`
- Validation warnings: `0`
- Unresolved skill references retained as identity gaps: `2`
- Ambiguous skill references retained as identity gaps: `1`

## Value Scale Policy

Planner-safe value normalization is not inferred in this phase. Source values are preserved as `source_units` unless a source row already proves planner-normalized values. `source_units` and `unknown` value scales are display/debug-only and block stable planner eligibility.

## Operation Breakdown

- `chance`: `69`
- `cooldown`: `429`
- `cost`: `440`
- `duration`: `949`
- `flat`: `4627`
- `increased`: `1112`
- `less`: `1`
- `more`: `165`
- `unknown`: `11606`

## Value Scale Breakdown

- `source_units`: `6248`
- `unknown`: `13150`

## Top Blocked Reasons

- `support_status_not_trusted`: `19398`
- `value_scale_not_planner_normalized`: `19398`
- `special_behavior_not_calculable`: `13036`
- `source_identity_not_resolved`: `11924`
- `operation_unknown`: `11606`
- `stat_id_unknown`: `4714`

## Skill Identity Handling

Phase 10 preserves the Phase 9.5 identity result. Safely resolved class/mastery skill identity can be reported, but unresolved and ambiguous class/mastery skill references remain blocked from stable planner eligibility. No bridge is inferred from display names or nested evidence.

## Migration Implications

The modifier registry is suitable for debugging, review, and policy development. It is not a planner input yet because value scale normalization remains unresolved and most source records are still partial, scripted, unsupported, or text-only.

## Recommended Next Step

Define a value normalization policy for the most common source-unit modifier families before any test-only planner adapter consumes normalized rows.
