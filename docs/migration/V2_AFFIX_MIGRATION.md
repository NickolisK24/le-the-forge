# v2 Affix Migration

## Purpose

Phase 3 creates a read-only canonical affix bundle on top of the v2 data contracts. The bundle preserves deterministic Forge-safe affix/modifier relationships and exposes validation diagnostics for later repository, API, debug, and planner work.

This phase does not remap planner, crafting, stat aggregation, simulation, item, passive, skill, idol, unique, or set behavior.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_affix_bundle.py --source-bundle D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json --output docs\generated\v2_affix_bundle.json --validation-output docs\generated\v2_affix_validation_report.json --markdown-output docs\migration\V2_AFFIX_MIGRATION.md
```

## Summary

- Affix count: 1098
- Stable-calculable count: 0
- Records with warnings: 1098
- Validation errors: 0
- Validation warnings: 0
- Production consumed: false

## Support Status Counts

| Support status | Count |
| --- | ---: |
| `partial` | 1098 |

## Affix Domain Counts

| Domain | Count |
| --- | ---: |
| `equipment` | 615 |
| `idol` | 483 |

## Prefix/Suffix Counts

| Classification | Count |
| --- | ---: |
| `prefix` | 832 |
| `suffix` | 266 |

## Modifier Reference Count Distribution

| Modifier references | Affix count |
| --- | ---: |
| `1` | 572 |
| `2` | 526 |

## Example Canonical Affixes

| Canonical ID | Display name | Domain | Prefix/suffix | Modifier references |
| --- | --- | --- | --- | ---: |
| `affix:equipment:0` | Void Penetration | equipment | prefix | 1 |
| `affix:equipment:1` | Armor | equipment | suffix | 1 |
| `affix:equipment:2` | Increased Melee Attack Speed | equipment | prefix | 1 |
| `affix:equipment:3` | Added Block Chance | equipment | prefix | 1 |
| `affix:equipment:4` | Increased Cast Speed | equipment | prefix | 1 |
| `affix:equipment:5` | Increased Critical Strike Chance | equipment | prefix | 1 |
| `affix:equipment:6` | Added Critical Strike Multiplier | equipment | prefix | 1 |
| `affix:equipment:7` | Void Resistance | equipment | suffix | 1 |
| `affix:equipment:8` | Added Dodge Rating | equipment | suffix | 1 |
| `affix:equipment:9` | Increased Elemental Damage | equipment | prefix | 1 |
| `affix:equipment:10` | Necrotic Resistance | equipment | suffix | 1 |
| `affix:equipment:11` | Freeze Rate Multiplier | equipment | suffix | 1 |
| `affix:equipment:12` | Increased Fire Damage | equipment | prefix | 1 |
| `affix:equipment:13` | Fire Resistance | equipment | suffix | 1 |
| `affix:equipment:15` | Increased Void Damage | equipment | prefix | 1 |
| `affix:equipment:16` | Increased Cold Damage | equipment | prefix | 1 |
| `affix:equipment:17` | Cold Resistance | equipment | suffix | 1 |
| `affix:equipment:18` | Increased Necrotic Damage | equipment | prefix | 1 |
| `affix:equipment:19` | Poison Resistance | equipment | suffix | 1 |
| `affix:equipment:20` | Health On Kill | equipment | suffix | 1 |

## Value and Polarity Policy

Tier values are preserved in source units. No planner value-scale normalization is applied in this phase. Polarity is preserved from source values without inference.

## Migration Implications

- The generated bundle is appropriate for experimental inspection and validation.
- Records are `partial`, not `trusted`, because value-scale normalization and planner eligibility remain unresolved.
- Equipment/idol domain separation is explicit in the bundle.
- Stable planner consumption remains blocked.

## Deferred

- Full planner remap.
- Value-scale normalization policy.
- Item/passive/skill/idol/unique/set infrastructure.
- Stable API contracts outside experimental routes.

## Checkpoint 3

Checkpoint 3 is ready for review when the generated bundle, validation report, repository, experimental routes, debug page, and focused tests pass.
