# v2 Item Base Migration

## Purpose

Phase 4 creates read-only canonical item base and implicit bundles on top of the v2 data contracts. The generated data preserves extracted item subtype, requirement, slot, and implicit modifier evidence without remapping planner behavior.

This phase does not implement unique, set, idol, passive, skill, crafting, or planner migration.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_item_bundles.py --source-items D:\Forge\last-epoch-data\exports_json\items.json --base-output docs\generated\v2_item_base_bundle.json --implicit-output docs\generated\v2_item_implicit_bundle.json --validation-output docs\generated\v2_item_validation_report.json --markdown-output docs\migration\V2_ITEM_BASE_MIGRATION.md
```

## Summary

- Item base count: 542
- Implicit count: 1182
- Base type count: 25
- Excluded non-Phase-4 base type count: 17
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 0
- Production consumed: false

## Support Status Counts

| Support status | Count |
| --- | ---: |
| `partial` | 542 |

## Item Classification Counts

| Classification | Count |
| --- | ---: |
| `accessory` | 154 |
| `armor` | 194 |
| `weapon` | 194 |

## Implicit Modifier Count Distribution

| Modifier rows | Implicit count |
| --- | ---: |
| `1` | 1182 |

## Example Item Bases

| Canonical ID | Display name | Item type | Level requirement | Implicits |
| --- | --- | --- | ---: | ---: |
| `item_base:equippable:0:0` | Refuge Helmet | helmet | 0 | 1 |
| `item_base:equippable:0:1` | Jewelled Circlet | helmet | 7 | 3 |
| `item_base:equippable:0:2` | Iron Casque | helmet | 10 | 1 |
| `item_base:equippable:0:3` | Wolf Helmet | helmet | 20 | 2 |
| `item_base:equippable:0:4` | Dome Cap | helmet | 24 | 1 |
| `item_base:equippable:0:5` | Bronze Casque | helmet | 39 | 1 |
| `item_base:equippable:0:6` | Gladiator Helmet | helmet | 65 | 1 |
| `item_base:equippable:0:7` | Forest Helmet | helmet | 35 | 1 |
| `item_base:equippable:0:8` | Outcast Cage | helmet | 0 | 1 |
| `item_base:equippable:0:9` | Bone Mask | helmet | 3 | 2 |
| `item_base:equippable:0:10` | Skull Cage | helmet | 6 | 2 |
| `item_base:equippable:0:11` | Death Mask | helmet | 13 | 1 |
| `item_base:equippable:0:12` | Fiend Cowl | helmet | 29 | 2 |
| `item_base:equippable:0:13` | Burial Mask | helmet | 51 | 2 |
| `item_base:equippable:0:14` | Profane Crown | helmet | 60 | 3 |
| `item_base:equippable:0:15` | Revenant Mask | helmet | 66 | 3 |
| `item_base:equippable:0:16` | Copper Circlet | helmet | 0 | 1 |
| `item_base:equippable:0:17` | Adept Helm | helmet | 3 | 1 |
| `item_base:equippable:0:18` | Keeper Helm | helmet | 6 | 2 |
| `item_base:equippable:0:19` | Temple Veil | helmet | 22 | 2 |

## Migration Implications

- Item base and implicit records are available for experimental lookup and debug inspection.
- Records remain `partial` and non-stable because value-scale policy and planner compatibility have not been reviewed.
- Implicit records are linked back to item base IDs for future compatibility checks.
- Existing `/api/ref/base-items` and planner behavior remain unchanged.

## Deferred

- Unique and set item infrastructure.
- Idol-specific infrastructure.
- Planner remapping and implicit stat aggregation.
- Value-scale normalization policy.

## Checkpoint 4

Checkpoint 4 is ready for review when the generated item bundles, validation report, repository, experimental routes, debug view, and focused tests pass.
