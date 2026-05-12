# Forge-Safe Stat Key Mapping Review

Generated: 2026-05-11

## Purpose

This read-only diagnostic groups legacy Forge `stat_key` values by the Forge-safe bundle modifier/property references observed in the saved legacy-vs-bundle comparison report. It does not route planner, crafting, stat aggregation, simulation, or `/api/ref/affixes` to the Forge-safe bundle.

## Source

Source comparison report: `docs\generated\forge_safe_legacy_affix_comparison.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_stat_key_mapping.py --comparison-path docs\generated\forge_safe_legacy_affix_comparison.json --output docs\generated\forge_safe_stat_key_mapping_report.json --markdown-output docs\migration\FORGE_SAFE_STAT_KEY_MAPPING_REVIEW.md
```

## Summary Counts

| Metric | Count |
| --- | ---: |
| matched_affix_count | 1098 |
| stat_key_difference_count | 1098 |
| legacy_stat_key_count | 1046 |
| unique_bundle_modifier_reference_count | 705 |
| one_to_one_mapping_count | 560 |
| one_to_many_mapping_count | 455 |
| missing_mapping_count | 0 |
| ambiguous_mapping_count | 31 |
| one_to_two_affix_count | 526 |

## Mapping Shape Breakdown

| Shape | Count | Migration meaning |
| --- | ---: | --- |
| one_to_one | 560 | Candidate for future adapter work after value/applicability validation. |
| one_to_many | 455 | Requires explicit adapter policy for split or compound modifier routing. |
| missing | 0 | Cannot map without deeper source validation. |
| ambiguous | 31 | Same legacy key reaches conflicting structural references. Requires audit. |

## Top One-To-Many Mappings

| Legacy stat_key | Affixes | References | Examples |
| --- | ---: | --- | --- |
| `_attack_and_cast_speed` | 1 | `INCREASED:AttackSpeed:None`, `INCREASED:CastSpeed:None` | 1004 |
| `abandoned_chitin_of_the_weaver_reforged` | 1 | `ADDED:Armour:None`, `ADDED:PlayerProperty:Lightning:Cold:Fire:Necrotic:Poison:Melee` | 949 |
| `abandoned_eyes_of_the_weaver_reforged` | 1 | `ADDED:PlayerProperty:Cold:Fire:Necrotic:Poison:Melee`, `ADDED:WardDecayThreshold:None` | 950 |
| `abyssal_champions` | 1 | `ADDED:AbilityProperty:Lightning:Void:Elemental:Spell`, `ADDED:Damage:Melee` | 773 |
| `acolyte_critical_strike_chance_for_skeletons_and_skeletal_mages` | 1 | `ADDED:AbilityProperty:Fire:Void:Necrotic:Poison`, `ADDED:AbilityProperty:Physical:Lightning:Necrotic:Spell` | 419 |
| `acolyte_idol_ward_per_second_and_increased_health` | 1 | `ADDED:WardRegen:None`, `INCREASED:Health:None` | 941 |
| `acolyte_increased_damage_with_rip_blood_and_blood_splatter` | 1 | `ADDED:AbilityProperty:Lightning:Fire:Elemental`, `ADDED:AbilityProperty:Physical:Fire:Elemental` | 418 |
| `acolyte_level_of_assemble_abomination` | 1 | `ADDED:LevelOfSkills:Cold:Void:Necrotic:Poison:Spell`, `INCREASED:Health:Minion` | 633 |
| `acolyte_level_of_aura_of_decay` | 1 | `ADDED:LevelOfSkills:Spell`, `ADDED:PoisonResistance:None` | 576 |
| `acolyte_level_of_bone_curse` | 1 | `ADDED:LevelOfSkills:Physical:Void:Necrotic:Poison:Spell`, `INCREASED:Damage:Spell` | 635 |
| `acolyte_level_of_chaos_bolts` | 1 | `ADDED:LevelOfSkills:Physical:Lightning:Fire:Poison:Elemental:Melee`, `INCREASED:Damage:Spell` | 734 |
| `acolyte_level_of_chthonic_fissure` | 1 | `ADDED:LevelOfSkills:Lightning:Void:Poison:Elemental:Melee`, `INCREASED:Damage:DoT` | 733 |
| `acolyte_level_of_death_seal` | 1 | `ADDED:LevelOfSkills:Lightning:Fire:Elemental:Spell`, `INCREASED:Damage:Spell` | 636 |
| `acolyte_level_of_drain_life` | 1 | `ADDED:LevelOfSkills:Physical:Cold:Void:Necrotic:Poison:Spell`, `INCREASED:Damage:Spell` | 632 |
| `acolyte_level_of_dread_shade` | 1 | `ADDED:LevelOfSkills:Physical:Lightning:Fire:Void:Elemental:Spell`, `ADDED:Mana:None` | 571 |
| `acolyte_level_of_flay` | 1 | `ADDED:IncreasedAreaForAreaSkills:None`, `ADDED:LevelOfSkills:Physical:Lightning:Cold:Fire:Necrotic:Spell:Melee` | 944 |
| `acolyte_level_of_ghostflame` | 1 | `ADDED:LevelOfSkills:Lightning:Cold:Fire:Poison:Elemental:Melee`, `INCREASED:Damage:DoT` | 735 |
| `acolyte_level_of_harvest` | 1 | `ADDED:LevelOfSkills:Physical:Fire:Void:Necrotic:Elemental`, `INCREASED:Damage:Melee` | 594 |
| `acolyte_level_of_hungering_souls` | 1 | `ADDED:LevelOfSkills:Physical:Fire:Void:Elemental`, `INCREASED:Damage:Spell` | 577 |
| `acolyte_level_of_infernal_shade` | 1 | `ADDED:LevelOfSkills:Lightning:Void:Necrotic:Poison:Spell`, `INCREASED:Damage:Spell` | 573 |

## Legacy Single stat_key To Two Bundle Modifiers

Total one-to-two affixes: 526

These affixes block a direct legacy `stat_key` adapter because one legacy stat key would need to route into two Forge-safe modifier references without an approved split policy.

| Legacy stat_key | Affix count | Example affix IDs |
| --- | ---: | --- |
| `max_mana` | 7 | 718, 759, 973, 977, 1009, 1014, 1021 |
| `minion_damage_pct` | 4 | 64, 102, 643, 945 |
| `cast_speed` | 3 | 976, 978, 1005 |
| `health_pct` | 3 | 996, 1010, 1019 |
| `max_health` | 2 | 29, 825 |
| `physical_res` | 2 | 1023, 1025 |
| `ward_regen` | 2 | 824, 1002 |
| `_attack_and_cast_speed` | 1 | 1004 |
| `_elemental_res` | 1 | 1024 |
| `abandoned_chitin_of_the_weaver_reforged` | 1 | 949 |
| `abandoned_eyes_of_the_weaver_reforged` | 1 | 950 |
| `abyssal_champions` | 1 | 773 |
| `acolyte_1_skeleton_and_increased_skeleton_damage` | 1 | 192 |
| `acolyte_critical_strike_chance_for_skeletons_and_skeletal_mages` | 1 | 419 |
| `acolyte_idol_ward_per_second_and_increased_health` | 1 | 941 |
| `acolyte_increased_damage_with_rip_blood_and_blood_splatter` | 1 | 418 |
| `acolyte_level_of_assemble_abomination` | 1 | 633 |
| `acolyte_level_of_aura_of_decay` | 1 | 576 |
| `acolyte_level_of_bone_curse` | 1 | 635 |
| `acolyte_level_of_chaos_bolts` | 1 | 734 |
| `acolyte_level_of_chthonic_fissure` | 1 | 733 |
| `acolyte_level_of_death_seal` | 1 | 636 |
| `acolyte_level_of_drain_life` | 1 | 632 |
| `acolyte_level_of_dread_shade` | 1 | 571 |
| `acolyte_level_of_flay` | 1 | 944 |

## Missing And Ambiguous Mappings

Missing mappings are legacy stat keys with no structural bundle modifier/property references in the comparison output. Ambiguous mappings are legacy stat keys that map to conflicting structural reference signatures across records.

- Missing mapping count: 0
- Ambiguous mapping count: 31

| Legacy stat_key | Affixes | References | Examples |
| --- | ---: | --- | --- |
| `max_mana` | 9 | `ADDED:LevelOfSkills:None`, `ADDED:Mana:None`, `ADDED:ManaSpentGainedAsWard:None`, `ADDED:PlayerProperty:Physical:Cold:Void:Poison:Melee`, ... | 34, 331, 718, 759, 973, 977 |
| `minion_damage_pct` | 5 | `ADDED:Damage:Bow:Minion`, `ADDED:Damage:Melee:Minion`, `ADDED:Damage:Spell:Minion`, `ADDED:IncreasedAreaForAreaSkills:Minion`, ... | 26, 64, 102, 643, 945 |
| `cast_speed` | 4 | `ADDED:PlayerProperty:Cold:Necrotic:Spell`, `INCREASED:CastSpeed:Minion`, `INCREASED:CastSpeed:None` | 4, 976, 978, 1005 |
| `crit_chance_pct` | 4 | `ADDED:CriticalChance:Melee`, `ADDED:CriticalChance:None`, `INCREASED:AttackSpeed:Bow`, `INCREASED:CriticalChance:None`, ... | 5, 62, 84, 672 |
| `health_pct` | 4 | `ADDED:PlayerProperty:Fire:Poison:Elemental`, `ADDED:WardRegen:None`, `INCREASED:Health:None`, `INCREASED:PlayerProperty:Lightning:Cold:Fire:Void:Necrotic:Elemental` | 52, 996, 1010, 1019 |
| `attack_speed_pct` | 3 | `ADDED:PlayerProperty:Physical:Lightning:Fire:Poison:Elemental:Spell`, `INCREASED:AttackSpeed:Bow`, `INCREASED:AttackSpeed:Melee` | 2, 432, 989 |
| `max_health` | 3 | `ADDED:Health:None`, `ADDED:HealthRegen:None`, `ADDED:StunAvoidance:None` | 25, 29, 825 |
| `physical_res` | 3 | `ADDED:PhysicalResistance:None`, `ADDED:PoisonResistance:None`, `ADDED:VoidResistance:None` | 45, 1023, 1025 |
| `ward_regen` | 3 | `ADDED:PlayerProperty:Physical:Cold:Poison`, `ADDED:WardDecayThreshold:None`, `ADDED:WardRegen:None` | 382, 824, 1002 |
| `_all_res` | 2 | `ADDED:AllResistances:Channelling`, `ADDED:AllResistances:None` | 46, 104 |
| `_elemental_res` | 2 | `ADDED:ElementalResistance:None`, `ADDED:NecroticResistance:None` | 80, 1024 |
| `area_pct` | 2 | `ADDED:IncreasedAreaForAreaSkills:Melee`, `ADDED:IncreasedAreaForAreaSkills:None` | 101, 671 |
| `armour` | 2 | `ADDED:Armour:None`, `INCREASED:Armour:None` | 1, 31 |
| `attunement` | 2 | `ADDED:Attunement:None`, `INCREASED:ManaRegen:None` | 504, 1015 |
| `block_chance` | 2 | `ADDED:BlockChance:None`, `ADDED:BlockEffectiveness:None` | 3, 426 |
| `cold_penetration` | 2 | `ADDED:Penetration:Cold`, `ADDED:Penetration:Cold:Minion` | 35, 721 |
| `cold_res` | 2 | `ADDED:ColdResistance:None`, `ADDED:VoidResistance:None` | 17, 1027 |
| `dexterity` | 2 | `ADDED:Dexterity:None`, `INCREASED:DodgeRating:None` | 503, 1017 |
| `dodge_rating` | 2 | `ADDED:DodgeRating:None`, `INCREASED:DodgeRating:None` | 8, 59 |
| `endurance` | 2 | `ADDED:Endurance:None`, `ADDED:MaximumHealthGainedAsEnduranceThreshold:None` | 92, 1020 |

## Migration Implications

Direct legacy `stat_key` mapping is not safe yet. The report has one-to-one candidates, but the comparison still shows universal stat-key differences and 526 one-to-two modifier splits. Adapter generation can only start with one-to-one mappings, and even those still need the separate slot/applicability and value-scale blockers resolved.

A future adapter can be partially generated from one-to-one mappings as a candidate table. One-to-many mappings require explicit routing policy. Missing and ambiguous mappings require deeper source validation before any production consumer can rely on them.

Recommended next step: create a reviewed adapter-candidate table for one-to-one mappings only, with tests proving it remains read-only and is not consumed by planner, crafting, stat aggregation, simulation, or `/api/ref/affixes`.
