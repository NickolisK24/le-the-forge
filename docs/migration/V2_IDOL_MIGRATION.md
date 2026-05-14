# v2 Idol Migration

## Purpose

Phase 6 creates read-only canonical idol and idol-affix bundles. Idol bases are generated from extracted item subtype data, while idol affixes are generated from the Phase 3 v2 affix bundle and re-namespaced so they remain separate from equipment affixes.

This phase does not remap planner behavior or implement idol slot behavior.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_idol_bundles.py --source-items D:\Forge\last-epoch-data\exports_json\items.json --source-affix-bundle docs\generated\v2_affix_bundle.json --idol-output docs\generated\v2_idol_bundle.json --idol-affix-output docs\generated\v2_idol_affix_bundle.json --validation-output docs\generated\v2_idol_validation_report.json --markdown-output docs\migration\V2_IDOL_MIGRATION.md
```

## Summary

- Idol count: 71
- Idol affix count: 483
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 20
- Production consumed: false

## Idol Shape Counts

| Shape | Count |
| --- | ---: |
| idol_1x1_eterra | 3 |
| idol_1x1_lagon | 2 |
| idol_1x2 | 2 |
| idol_1x3 | 15 |
| idol_1x4 | 10 |
| idol_2x1 | 2 |
| idol_2x2 | 12 |
| idol_3x1 | 15 |
| idol_4x1 | 10 |

## Idol Class Restriction Counts

| Class | Count |
| --- | ---: |
| Acolyte | 12 |
| Any | 35 |
| Mage | 12 |
| Primalist | 12 |

## Idol Affix Prefix/Suffix Counts

| Classification | Count |
| --- | ---: |
| prefix | 290 |
| suffix | 193 |

## Example Idol Bases

| Canonical ID | Display name | Shape | Dimensions | Class |
| --- | --- | --- | --- | --- |
| `idol:25:0` | Small Eterran Idol | idol_1x1_eterra | 1x1 | Any |
| `idol:25:1` | Small Orobyss Idol | idol_1x1_eterra | 1x1 | Any |
| `idol:25:2` | Small Weaver Idol | idol_1x1_eterra | 1x1 | Any |
| `idol:26:0` | Minor Lagonian Idol | idol_1x1_lagon | 1x1 | Any |
| `idol:26:1` | Minor Weaver Idol | idol_1x1_lagon | 1x1 | Any |
| `idol:27:0` | Humble Eterran Idol | idol_2x1 | 2x1 | Any |
| `idol:27:1` | Humble Weaver Idol | idol_2x1 | 2x1 | Any |
| `idol:28:0` | Stout Lagonian Idol | idol_1x2 | 1x2 | Any |
| `idol:28:1` | Stout Weaver Idol | idol_1x2 | 1x2 | Any |
| `idol:29:0` | Grand Heorot Idol | idol_3x1 | 3x1 | Primalist |
| `idol:29:1` | Grand Glass Idol | idol_3x1 | 3x1 | Mage |
| `idol:29:2` | Grand Solar Idol | idol_3x1 | 3x1 | Acolyte |
| `idol:29:3` | Grand Bone Idol | idol_3x1 | 3x1 | Any |
| `idol:29:4` | Grand Majasan Idol | idol_3x1 | 3x1 | Any |
| `idol:29:5` | Heretical Grand Heorot Idol | idol_3x1 | 3x1 | Primalist |
| `idol:29:6` | Heretical Grand Glass Idol | idol_3x1 | 3x1 | Mage |
| `idol:29:7` | Heretical Grand Solar Idol | idol_3x1 | 3x1 | Acolyte |
| `idol:29:8` | Heretical Grand Bone Idol | idol_3x1 | 3x1 | Any |
| `idol:29:9` | Heretical Grand Majasan Idol | idol_3x1 | 3x1 | Any |
| `idol:29:10` | Grand Primal Omen Idol | idol_3x1 | 3x1 | Primalist |

## Example Idol Affixes

| Canonical ID | Display name | Prefix/Suffix | Tiers | Idol restrictions |
| --- | --- | --- | ---: | --- |
| `idol_affix:105` | Idol Health | suffix | 1 | IDOL_1x1_LAGON, IDOL_1x3, IDOL_1x4 |
| `idol_affix:106` | Health on Kill | prefix | 1 | IDOL_2x1, IDOL_2x2 |
| `idol_affix:107` | Idol Increased Health | prefix | 1 | IDOL_1x2 |
| `idol_affix:108` | Health Regeneration | prefix | 1 | IDOL_1x1_ETERRA, IDOL_3x1 |
| `idol_affix:109` | Idol Mana | prefix | 1 | IDOL_1x1_LAGON, IDOL_3x1 |
| `idol_affix:110` | Armor | prefix | 1 | IDOL_1x1_LAGON, IDOL_4x1 |
| `idol_affix:111` | Idol Fire Resistance | suffix | 1 | IDOL_1x1_LAGON, IDOL_1x2, IDOL_1x3 |
| `idol_affix:112` | Idol Cold Resistance | suffix | 1 | IDOL_1x1_LAGON, IDOL_1x2, IDOL_1x3 |
| `idol_affix:113` | Idol Lightning Resistance | suffix | 1 | IDOL_1x1_LAGON, IDOL_1x2, IDOL_1x3 |
| `idol_affix:114` | Idol Necrotic Resistance | suffix | 1 | IDOL_1x1_ETERRA, IDOL_2x1, IDOL_3x1 |
| `idol_affix:115` | Idol Void Resistance | suffix | 1 | IDOL_1x1_ETERRA, IDOL_2x1, IDOL_3x1 |
| `idol_affix:116` | Idol Poison Resistance | suffix | 1 | IDOL_1x1_ETERRA, IDOL_2x1, IDOL_3x1 |
| `idol_affix:117` | Idol Elemental Resistance | suffix | 1 | IDOL_1x1_LAGON, IDOL_1x2, IDOL_1x3 |
| `idol_affix:118` | Idol Dodge Rating | prefix | 1 | IDOL_1x1_ETERRA, IDOL_1x3 |
| `idol_affix:119` | Idol Increased Damage Over Time | prefix | 1 | IDOL_1x1_ETERRA, IDOL_3x1 |
| `idol_affix:120` | Idol Chance To Gain 30 Ward When Hit | prefix | 1 | IDOL_1x2, IDOL_4x1 |
| `idol_affix:121` | Idol Increased Stun Chance | prefix | 1 | IDOL_1x1_ETERRA, IDOL_2x2 |
| `idol_affix:122` | Ward On Potion Use | prefix | 1 | IDOL_1x1_LAGON, IDOL_1x3 |
| `idol_affix:123` | Idol Potion Health Converted To Ward | prefix | 1 | IDOL_1x2, IDOL_1x4 |
| `idol_affix:124` | Idol Vitality | prefix | 1 | IDOL_2x1, IDOL_4x1 |

## Migration Implications

- Idols and idol affixes are available for experimental lookup and debug inspection.
- Idol affixes are intentionally separate from equipment affixes.
- Records remain `partial` because value-scale and modifier normalization are unresolved.
- Existing planner and idol slot behavior remain unchanged.

## Deferred

- Planner idol slot behavior.
- Modifier/value normalization.
- Stable stat aggregation from idol affixes.
- Class/mastery, passive, and skill infrastructure.

## Checkpoint 6

Checkpoint 6 is ready for review when generated bundles, validation report, repository, routes, debug page, and focused tests pass.
