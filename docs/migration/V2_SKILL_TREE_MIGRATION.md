# v2 Skill Tree Migration

## Purpose

Phase 9 creates read-only canonical skill and skill tree bundles from extracted skill data. Skill tree layout is supplemented from existing frontend raw layout data when available.

This phase does not replace production skill behavior, calculate skill effects, normalize modifiers, or remap the planner.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_skill_tree_bundle.py --source-skills D:\Forge\last-epoch-data\exports_json\skills_with_trees.json --layout-skills frontend\src\data\raw\skill-tree-layout.json --class-mastery-bundle docs\generated\v2_class_mastery_bundle.json --skill-output docs\generated\v2_skill_bundle.json --skill-tree-output docs\generated\v2_skill_tree_bundle.json --validation-output docs\generated\v2_skill_validation_report.json --unsupported-output docs\generated\v2_skill_unsupported_report.json --markdown-output docs\migration\V2_SKILL_TREE_MIGRATION.md
```

## Summary

- Skill count: 184
- Skill tree count: 136
- Skill node count: 3919
- Layout supplement matched nodes: 3919
- Unsupported/text-only skill records: 127
- Unsupported/text-only node records: 3888
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 64
- Production consumed: false

## Skill Behavior Classification

| Classification | Count |
| --- | ---: |
| partial_modifier | 57 |
| scripted_runtime_behavior | 83 |
| text_only_effect | 44 |

## Skill Node Behavior Classification

| Classification | Count |
| --- | ---: |
| partial_modifier | 31 |
| scripted_runtime_behavior | 2342 |
| text_only_effect | 105 |
| unknown | 30 |
| unsupported_special_behavior | 1411 |

## Sample Skill Trees

| Tree ID | Display name | Skill ID | Nodes |
| --- | --- | --- | ---: |
| `skill_tree:ab0lh` | Abyssal Echoes Skill Tree | `skill:ab0lh` | 31 |
| `skill_tree:aacfl` | Acid Flask Skill Tree | `skill:aacfl` | 29 |
| `skill_tree:aa989` | Aerial Assault Skill Tree | `skill:aa989` | 32 |
| `skill_tree:an0my` | Anomaly Skill Tree | `skill:an0my` | 30 |
| `skill_tree:arcas` | Arcane Ascendance Skill Tree | `skill:arcas` | 24 |
| `skill_tree:aa710` | Assemble Abomination Skill Tree | `skill:aa710` | 31 |
| `skill_tree:ad0ry` | Aura Of Decay Skill Tree | `skill:ad0ry` | 30 |
| `skill_tree:av75ch` | Avalanche Skill Tree | `skill:av75ch` | 28 |
| `skill_tree:ba1574` | Ballista Skill Tree | `skill:ba1574` | 30 |
| `skill_tree:bh2` | Black Hole Skill Tree | `skill:bh2` | 28 |
| `skill_tree:bl5st` | Bladestorm Skill Tree | `skill:bl5st` | 29 |
| `skill_tree:bc53` | Bone Curse Skill Tree | `skill:bc53` | 32 |
| `skill_tree:ch4bo` | Chaos Bolts Skill Skill Tree | `skill:ch4bo` | 28 |
| `skill_tree:ch0fs` | Chthonic Fissure Skill Tree | `skill:ch0fs` | 31 |
| `skill_tree:cstri` | Cinder Strike Skill Tree | `skill:cstri` | 28 |

## Class/Mastery Cross-Reference

- Class/mastery linked skill source IDs: 63
- Resolved links: 0
- Unresolved links: 63
- Manual bridge count: 0

The current skill export does not expose the same source path IDs used by class/mastery records, so these links are reported instead of inferred.

## Unsupported and Text-Only Findings

Unsupported/text-only records are written to `docs/generated/v2_skill_unsupported_report.json`. These records preserve serialized evidence and text, but they are not treated as planner-calculable.

## Migration Implications

- Skills, skill trees, and skill nodes are available for experimental lookup and debug inspection.
- Modifier-like rows remain `partial`; value normalization and stat routing are unresolved.
- Tooltip and description text is display/debug evidence only.
- Existing skill API, planner behavior, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Modifier normalization and value-scale policy.
- Planner remapping to v2 skills and skill tree nodes.
- Stable calculation of skill effects.
- Class/mastery skill ownership bridging unless a future source exposes stable IDs.

## Recommended Next Step

Proceed to modifier/stat normalization planning after Checkpoint 9 review.
