# v2 Passive Tree Migration

## Purpose

Phase 8 creates a read-only canonical passive tree bundle from extracted passive tree data. Existing local passive JSON is used only as a layout supplement for position and connection fields already used by the current passive viewer.

This phase does not replace production passive behavior, calculate passive effects, implement skill trees, or remap the planner.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_passive_tree_bundle.py --source-passives D:\Forge\last-epoch-data\exports_json\passive_trees.json --layout-passives data\classes\passives.json --class-mastery-bundle docs\generated\v2_class_mastery_bundle.json --output docs\generated\v2_passive_tree_bundle.json --validation-output docs\generated\v2_passive_tree_validation_report.json --unsupported-output docs\generated\v2_passive_unsupported_report.json --markdown-output docs\migration\V2_PASSIVE_TREE_MIGRATION.md
```

## Summary

- Passive tree count: 5
- Passive node count: 535
- Layout supplement matched nodes: 535
- Unsupported/text-only node count: 463
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 0
- Production consumed: false

## Passive Trees

| Tree ID | Display name | Owner class | Nodes |
| --- | --- | --- | ---: |
| `passive_tree:ac_1` | Acolyte Passive Tree | `class:acolyte` | 103 |
| `passive_tree:mg_1` | Mage Passive Tree | `class:mage` | 108 |
| `passive_tree:pr_1` | Primalist Passive Tree | `class:primalist` | 111 |
| `passive_tree:rg_1` | Rogue Passive Tree | `class:rogue` | 103 |
| `passive_tree:kn_1` | Sentinel Passive Tree | `class:sentinel` | 110 |

## Special Behavior Classification

| Classification | Count |
| --- | ---: |
| partial_modifier | 72 |
| scripted_runtime_behavior | 209 |
| unsupported_special_behavior | 254 |

## Class/Mastery Cross-Reference

| Class/mastery passive tree link | Resolved v2 passive tree | Status |
| --- | --- | --- |
| `passive_tree:ac_1` | `passive_tree:ac_1` | resolved |
| `passive_tree:kn_1` | `passive_tree:kn_1` | resolved |
| `passive_tree:mg_1` | `passive_tree:mg_1` | resolved |
| `passive_tree:pr_1` | `passive_tree:pr_1` | resolved |
| `passive_tree:rg_1` | `passive_tree:rg_1` | resolved |

## Unsupported and Text-Only Findings

Unsupported/text-only records are written to `docs/generated/v2_passive_unsupported_report.json`. These records preserve serialized evidence and text, but they are not treated as planner-calculable.

## Migration Implications

- Passive trees and nodes are available for experimental lookup and debug inspection.
- Modifier-like rows remain `partial`; value normalization and stat routing are unresolved.
- Tooltip and description text is display/debug evidence only.
- Existing passive API, planner behavior, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Skill tree infrastructure.
- Modifier normalization and value-scale policy.
- Planner remapping to v2 passive nodes.
- Stable calculation of passive effects.

## Recommended Next Step

Proceed to Phase 9 skill infrastructure after Checkpoint 8 review.
