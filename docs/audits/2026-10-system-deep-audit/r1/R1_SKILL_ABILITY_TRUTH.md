# R1 Skill / Ability Truth (R1.9)

## Source population discovered

| Source class | Instances (1.4.6 manifest) | Classification | Notes |
| --- | --- | --- | --- |
| `Ability` (ScriptableObject) | 4,110 | REQUIRED_NOW | Player and monster abilities; this is the source-entity denominator |
| `AbilityManager` | 1 | REQUIRED_NOW | Ability registry used by `ability_manager_resolver.py` |
| `KnownAbilityList` | 1 | REQUIRED_NOW | Separates player-known abilities from monster ones (audit 04 §9). **No extractor.** |
| `AbilityPropertyList`, `PropertyList`, `PlayerPropertyList`, `TrackerPropertyList`, `ExtraStatData` | 1 each | REQUIRED_NOW | Property definitions; needed to resolve skill-node and affix stat ids. **Never extracted.** |
| `DamageStatsHolder` family (8 classes) | prefab components | REQUIRED_NOW | Damage values; partly read by `enrich_skill_damage_sources.py` |
| `AbilityMutator` subclasses (110) | prefab components | REQUIRED_FUTURE | Specialization mechanics |
| `RequiresTaggedStats` family (21) | prefab components | REQUIRED_FUTURE | Ailment, resource and heal application |
| 137 skill trees + 5 passive + WeaverTree | sharedassets1 | REQUIRED_NOW | Canonical tree exports (R1_PASSIVE_TRUTH.md) |

## Legacy `skills.json` (1.4.6, informational)

- **Coverage:** 184 records for 4,110 `Ability` instances. The player-skill subset cannot be separated without `KnownAbilityList`.
- **Fields present:** `damageSources`, `levelScaling`, `attributeScaling`, `tags` and `tagsDecoded`, `conversionDamageTagsDecoded`, `summonedActors`, `mutatorHints`, `sharedCooldownAbilityRefs`, cost and channel fields.
- **Defects:** 1 skill has an empty id ("Detonate Decoy"); 12 names repeat (variants).
- **Damage coverage:** `damageSourceStatus` is direct for 81, runtime/mutator-driven for 29 and none_found for 74.
- **Structure:** records are keyed by skill name, not by `Ability` path id. The extractor records which `Ability` it read, but the legacy export cannot be re-derived without raw.

## R1 extraction path (operator)

- `r1_operator_dumps.py typetrees` dumps every in-scope class: all 4,110 `Ability` objects, `AbilityManager`, `KnownAbilityList`, the property lists, and every mutator, unique and damage component class. Dumps are build-stamped.
- Canonical envelopes keep each record under its `path_id`, so authoritative skill data is keyed by source identity, not name.
- Class → skill and mastery → skill relationships (audit: 60 of 184 and 0 of 20) become measurable from `CharacterClass.knownAbilities` and `unlockableAbilities` and `KnownAbilityList` in the raw dumps. R1.12 then counts them in relationship coverage.

**Combat formulas are not certified in R1.** Semantic status is UNVERIFIED for every skill family.

## Status

- **Ability, AbilityManager and KnownAbilityList:** RAW_MISSING, with field survival BLOCKED_NO_RAW.
- **Canonical exports:** skill trees only, and they are QUARANTINED (integrity defects, unstamped raw).
- **Property-definition tables:** no extractor and no export. Without them, the tree stat property ids (0–25,206, beyond SP) cannot be resolved: 7,855 stat→property relationships stay unresolved.
