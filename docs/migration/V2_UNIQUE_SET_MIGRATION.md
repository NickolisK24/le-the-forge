# v2 Unique and Set Migration

## Purpose

Phase 5 creates read-only canonical unique and set item bundles on top of the v2 contracts and the Phase 4 item base infrastructure. It preserves extracted modifier rows, set membership, base links where available, and text-only/special effect evidence without simulating unique or set mechanics.

This phase does not remap planner behavior, implement special runtime behavior, or mark unique/set records as stable planner inputs.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_unique_set_bundles.py --source-uniques D:\Forge\last-epoch-data\exports_json\uniques.json --source-set-bonuses D:\Forge\last-epoch-data\exports_json\set_bonuses.json --item-base-bundle docs\generated\v2_item_base_bundle.json --unique-output docs\generated\v2_unique_bundle.json --set-output docs\generated\v2_set_bundle.json --validation-output docs\generated\v2_unique_set_validation_report.json --unsupported-output docs\generated\v2_unique_set_unsupported_report.json --markdown-output docs\migration\V2_UNIQUE_SET_MIGRATION.md
```

## Summary

- Unique count: 409
- Set group count: 23
- Set item count: 59
- Set bonus count: 45
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 0
- Unsupported/text-only/special behavior records: 344
- Production consumed: false

## Unique Classification Counts

| Classification | Count |
| --- | ---: |
| partial_modifier | 385 |
| text_only_effect | 24 |

## Set Classification Counts

| Classification | Count |
| --- | ---: |
| partial_modifier | 103 |
| text_only_effect | 24 |

## Unsupported and Text-Only Findings

| Classification | Count |
| --- | ---: |
| partial_modifier | 296 |
| text_only_effect | 48 |

Tooltip and description text is retained as display/debug evidence only. It is not converted into calculated mechanics.

## Example Uniques

| Canonical ID | Display name | Item type | Classification | Modifier rows |
| --- | --- | --- | --- | ---: |
| `unique:0` | Calamity | helmet | partial_modifier | 3 |
| `unique:1` | Fractured Crown | helmet | partial_modifier | 4 |
| `unique:2` | Snowblind | helmet | partial_modifier | 8 |
| `unique:3` | Artor's Legacy | helmet | partial_modifier | 5 |
| `unique:4` | Decayed Skull | helmet | partial_modifier | 7 |
| `unique:6` | Boneclamor Barbute | helmet | partial_modifier | 5 |
| `unique:7` | The Kestrel | body_armor | partial_modifier | 5 |
| `unique:8` | Doublet of Onos Tull | body_armor | partial_modifier | 3 |
| `unique:9` | Prism Wraps | body_armor | partial_modifier | 4 |
| `unique:10` | Urzil's Pride | body_armor | partial_modifier | 4 |
| `unique:11` | Exsanguinous | body_armor | partial_modifier | 6 |
| `unique:12` | Yrun's Wisdom | body_armor | partial_modifier | 1 |
| `unique:13` | Titan Heart | body_armor | partial_modifier | 5 |
| `unique:14` | Valeroot | body_armor | partial_modifier | 6 |
| `unique:15` | Vipertail | belt | partial_modifier | 5 |

## Example Set Items

| Canonical ID | Display name | Set group | Classification | Modifier rows |
| --- | --- | --- | --- | ---: |
| `set_item:5` | Isadora's Revenge | `set:1` | partial_modifier | 4 |
| `set_item:16` | Isadora's Tomb Binding | `set:1` | partial_modifier | 4 |
| `set_item:26` | Isadora's Gravechill | `set:1` | partial_modifier | 2 |
| `set_item:57` | The Invoker's Frozen Heart | `set:2` | partial_modifier | 4 |
| `set_item:63` | The Invoker's Scorching Grasp | `set:2` | partial_modifier | 4 |
| `set_item:64` | The Invoker's Static Touch | `set:2` | partial_modifier | 4 |
| `set_item:77` | Apiarist's Smoker | `set:3` | partial_modifier | 6 |
| `set_item:78` | Apiarist's Suit | `set:3` | partial_modifier | 9 |
| `set_item:79` | Apiarist's Comb | `set:3` | partial_modifier | 5 |
| `set_item:85` | Sunforged Hammer | `set:4` | partial_modifier | 6 |
| `set_item:86` | Sunforged Cuirass | `set:4` | partial_modifier | 4 |
| `set_item:87` | Sunforged Greathelm | `set:4` | partial_modifier | 4 |
| `set_item:88` | Blade of the Forgotten Knight | `set:5` | partial_modifier | 6 |
| `set_item:89` | Defiance of the Forgotten Knight | `set:5` | partial_modifier | 6 |
| `set_item:90` | Locket of the Forgotten Knight | `set:5` | partial_modifier | 4 |

## Migration Implications

- Unique and set records are available for experimental lookup and debug inspection.
- Structured modifier rows remain `partial`; value-scale and modifier normalization are unresolved.
- Text-only and special behavior remains displayable but is not calculated.
- Existing planner and `/api/ref/uniques` behavior remain unchanged.

## Deferred

- Runtime simulation for unique and set special mechanics.
- Stable modifier normalization and value-scale policy.
- Planner, crafting, stat aggregation, and simulation consumption.
- Idol, passive, and skill infrastructure.

## Checkpoint 5

Checkpoint 5 is ready for review when generated bundles, validation reports, unsupported report, repository, routes, debug page, and focused tests pass.
