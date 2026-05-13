# v2 Class and Mastery Migration

## Purpose

Phase 7 creates a read-only canonical class/mastery bundle from the extracted class registry. The bundle is used for diagnostics, validation, and future class/mastery references only.

This phase does not implement passive trees, skill trees, planner remapping, or stable-calculable class behavior.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_class_mastery_bundle.py --source-classes D:\Forge\last-epoch-data\exports_json\classes.json --affix-bundle docs\generated\v2_affix_bundle.json --item-base-bundle docs\generated\v2_item_base_bundle.json --unique-bundle docs\generated\v2_unique_bundle.json --set-bundle docs\generated\v2_set_bundle.json --idol-bundle docs\generated\v2_idol_bundle.json --idol-affix-bundle docs\generated\v2_idol_affix_bundle.json --output docs\generated\v2_class_mastery_bundle.json --validation-output docs\generated\v2_class_mastery_validation_report.json --markdown-output docs\migration\V2_CLASS_MASTERY_MIGRATION.md
```

## Summary

- Class count: 5
- Mastery count: 15
- Restriction labels found in existing v2 bundles: 3
- Restriction labels mapped to class/mastery records: 3
- Restriction labels unmapped: 0
- Manual bridge count: 0
- Stable-calculable count: 0
- Validation errors: 0
- Validation warnings: 0
- Production consumed: false

## Classes

| Canonical ID | Display name | Masteries | Existing restriction labels |
| --- | --- | ---: | --- |
| `class:primalist` | Primalist | 3 | Primalist |
| `class:mage` | Mage | 3 | Mage |
| `class:sentinel` | Sentinel | 3 | None |
| `class:acolyte` | Acolyte | 3 | Acolyte |
| `class:rogue` | Rogue | 3 | None |

## Masteries

| Canonical ID | Display name | Parent class | Existing restriction labels |
| --- | --- | --- | --- |
| `mastery:primalist:beastmaster` | Beastmaster | `class:primalist` | None |
| `mastery:primalist:shaman` | Shaman | `class:primalist` | None |
| `mastery:primalist:druid` | Druid | `class:primalist` | None |
| `mastery:mage:sorcerer` | Sorcerer | `class:mage` | None |
| `mastery:mage:spellblade` | Spellblade | `class:mage` | None |
| `mastery:mage:runemaster` | Runemaster | `class:mage` | None |
| `mastery:sentinel:void_knight` | Void Knight | `class:sentinel` | None |
| `mastery:sentinel:forge_guard` | Forge Guard | `class:sentinel` | None |
| `mastery:sentinel:paladin` | Paladin | `class:sentinel` | None |
| `mastery:acolyte:necromancer` | Necromancer | `class:acolyte` | None |
| `mastery:acolyte:lich` | Lich | `class:acolyte` | None |
| `mastery:acolyte:warlock` | Warlock | `class:acolyte` | None |
| `mastery:rogue:bladedancer` | Bladedancer | `class:rogue` | None |
| `mastery:rogue:marksman` | Marksman | `class:rogue` | None |
| `mastery:rogue:falconer` | Falconer | `class:rogue` | None |

## Cross-Reference Findings

| Restriction label | Count | Class mapping | Mastery mapping |
| --- | ---: | --- | --- |
| Acolyte | 46 | `class:acolyte` | `` |
| Mage | 46 | `class:mage` | `` |
| Primalist | 48 | `class:primalist` | `` |

Existing generated v2 affix, item, unique/set, and idol bundles were scanned for class/mastery restriction labels. The scan reports mappings only; it does not rewrite prior bundles.

## Manual Bridge Findings

Manual bridge records: 0

The extracted class registry provided class and mastery records for this phase, so no manual bridge was needed. If later phases add temporary bridge records, they must use `trust_level: manual_bridge` and explain the source gap in provenance.

## Migration Implications

- Classes and masteries are available for experimental lookup and debug inspection.
- Records remain `partial` because passives, skills, and modifier normalization are not complete.
- Restriction labels from prior v2 bundles can now be audited against canonical class/mastery records.
- Existing planner, crafting, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Passive tree generation and validation.
- Skill tree generation and validation.
- Planner remapping to canonical class/mastery IDs.
- Stable planner eligibility for class/mastery-linked effects.

## Recommended Next Step

Proceed to Phase 8 passive infrastructure after Checkpoint 7 review.
