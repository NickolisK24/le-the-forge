# Forge-Safe Adapter Candidates Review

Generated: 2026-05-11

## Purpose

This read-only artifact lists only deterministic one-to-one legacy `stat_key` mappings as adapter candidates for future review. It is not a runtime adapter and is not consumed by planner, crafting, stat aggregation, simulation, or `/api/ref/affixes`.

## Source

Source mapping report: `docs\generated\forge_safe_stat_key_mapping_report.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_adapter_candidates.py --mapping-report docs\generated\forge_safe_stat_key_mapping_report.json --output docs\generated\forge_safe_adapter_candidates.json --markdown-output docs\migration\FORGE_SAFE_ADAPTER_CANDIDATES_REVIEW.md
```

## Summary Counts

| Metric | Count |
| --- | ---: |
| source_legacy_stat_key_count | 1046 |
| candidate_count | 560 |
| excluded_one_to_many_count | 455 |
| excluded_ambiguous_count | 31 |
| excluded_missing_count | 0 |
| production_consumed | false |

## Candidate Rule

A candidate must have `mapping_shape == one_to_one` in the stat-key mapping report and exactly one structural Forge-safe bundle modifier/property reference. The candidate keeps the legacy `stat_key`, the bundle `property_path`, modifier IDs, affix count, examples, migration risk, and explicit `not_consumed` status.

## Explicit Exclusions

- One-to-many mappings excluded: 455
- Ambiguous mappings excluded: 31
- Missing mappings excluded: 0

One-to-many mappings are excluded because direct stat-key routing would need a split or compound modifier policy. Ambiguous mappings are excluded because one legacy key reaches conflicting structural references. Missing mappings are excluded because there is no deterministic bundle reference to review.

## Candidate Examples

| Legacy stat_key | Property path | Affixes | Examples |
| --- | --- | ---: | --- |
| `_all_attributes` | `ADDED:AllAttributes:None` | 1 | 50 |
| `acolyte_1_skeleton_and_increased_skeleton_damage` | `ADDED:AbilityProperty:Fire:Void:Necrotic:Poison` | 1 | 192 |
| `acolyte_added_spell_damage_for_curses` | `ADDED:Damage:Spell:Curse` | 1 | 749 |
| `acolyte_additional_projectile_chance_with_chaos_bolts` | `ADDED:AbilityProperty:Physical:Lightning:Fire:Poison:Elemental:Melee` | 1 | 747 |
| `acolyte_chance_to_apply_damned_on_hit` | `ADDED:AilmentChance:None` | 1 | 421 |
| `acolyte_chance_to_cast_marrow_shards_when_you_cast_transplant` | `ADDED:AbilityProperty:Physical:Cold:Fire:Void:Necrotic:Poison:Elemental` | 1 | 435 |
| `acolyte_chance_to_gain_20_ward_on_kill_with_hungering_souls` | `ADDED:AbilityProperty:Physical:Fire:Void:Elemental` | 1 | 415 |
| `acolyte_damage_leeched_as_health_while_transformed` | `ADDED:HealthLeech:Transform` | 1 | 422 |
| `acolyte_increased_projectile_speed_with_marrow_shards_and_bone_nova` | `MORE:GlobalConditionalDamage:DoT` | 1 | 417 |
| `acolyte_increased_skeletal_mage_damage` | `ADDED:AbilityProperty:Physical:Lightning:Necrotic:Spell` | 1 | 410 |
| `acolyte_increased_spirit_frequency_with_chthonic_fissure` | `ADDED:AbilityProperty:Lightning:Void:Poison:Elemental:Melee` | 1 | 748 |
| `acolyte_leech_with_harvest` | `ADDED:AbilityProperty:Physical:Fire:Void:Necrotic:Elemental` | 1 | 412 |
| `acolyte_mana_gained_on_harvest_use` | `ADDED:AbilityProperty:Physical:Fire:Void:Necrotic:Elemental` | 1 | 411 |
| `acolyte_minion_freeze_rate` | `ADDED:FreezeRateMultiplier:Minion` | 1 | 384 |
| `acolyte_minion_reflect` | `ADDED:PercentReflect:Minion` | 1 | 413 |
| `acolyte_necrotic_damage_while_transformed` | `INCREASED:Damage:Necrotic:Transform` | 1 | 402 |
| `acolyte_physical_damage_while_transformed` | `INCREASED:Damage:Physical:Transform` | 1 | 401 |
| `acolyte_physical_spell_critical_strike_chance` | `INCREASED:CriticalChance:Physical:Spell` | 1 | 424 |
| `acolyte_reduced_health_cost_of_spells` | `ADDED:AbilityProperty:Physical:Cold:Fire:Void:Necrotic:Poison:Elemental` | 1 | 423 |
| `acolyte_spell_damage_per_skeletal_mage` | `ADDED:AbilityProperty:Physical:Lightning:Necrotic:Spell` | 1 | 420 |
| `acolyte_volatile_zombie_damage_and_explosion_area` | `ADDED:AbilityProperty:Fire:Void:Elemental:Spell` | 1 | 650 |
| `acolyte_volatile_zombie_speed_and_damage` | `ADDED:AbilityProperty:Fire:Void:Elemental:Spell` | 1 | 649 |
| `added_bow_cold_damage` | `ADDED:Damage:Cold:Bow` | 1 | 670 |
| `added_bow_fire` | `ADDED:Damage:Fire:Bow` | 1 | 434 |
| `added_bow_lightning_damage` | `ADDED:Damage:Lightning:Bow` | 1 | 669 |

## Excluded One-To-Many Examples

| Legacy stat_key | Shape | Affixes | Reference count | Examples |
| --- | --- | ---: | ---: | --- |
| `_attack_and_cast_speed` | one_to_many | 1 | 2 | 1004 |
| `abandoned_chitin_of_the_weaver_reforged` | one_to_many | 1 | 2 | 949 |
| `abandoned_eyes_of_the_weaver_reforged` | one_to_many | 1 | 2 | 950 |
| `abyssal_champions` | one_to_many | 1 | 2 | 773 |
| `acolyte_critical_strike_chance_for_skeletons_and_skeletal_mages` | one_to_many | 1 | 2 | 419 |
| `acolyte_idol_ward_per_second_and_increased_health` | one_to_many | 1 | 2 | 941 |
| `acolyte_increased_damage_with_rip_blood_and_blood_splatter` | one_to_many | 1 | 2 | 418 |
| `acolyte_level_of_assemble_abomination` | one_to_many | 1 | 2 | 633 |
| `acolyte_level_of_aura_of_decay` | one_to_many | 1 | 2 | 576 |
| `acolyte_level_of_bone_curse` | one_to_many | 1 | 2 | 635 |
| `acolyte_level_of_chaos_bolts` | one_to_many | 1 | 2 | 734 |
| `acolyte_level_of_chthonic_fissure` | one_to_many | 1 | 2 | 733 |
| `acolyte_level_of_death_seal` | one_to_many | 1 | 2 | 636 |
| `acolyte_level_of_drain_life` | one_to_many | 1 | 2 | 632 |
| `acolyte_level_of_dread_shade` | one_to_many | 1 | 2 | 571 |

## Excluded Ambiguous Examples

| Legacy stat_key | Shape | Affixes | Reference count | Examples |
| --- | --- | ---: | ---: | --- |
| `_all_res` | ambiguous | 2 | 2 | 46, 104 |
| `_elemental_res` | ambiguous | 2 | 2 | 80, 1024 |
| `area_pct` | ambiguous | 2 | 2 | 101, 671 |
| `armour` | ambiguous | 2 | 2 | 1, 31 |
| `attack_speed_pct` | ambiguous | 3 | 3 | 2, 432, 989 |
| `attunement` | ambiguous | 2 | 2 | 504, 1015 |
| `block_chance` | ambiguous | 2 | 2 | 3, 426 |
| `cast_speed` | ambiguous | 4 | 3 | 4, 976, 978, 1005 |
| `cold_penetration` | ambiguous | 2 | 2 | 35, 721 |
| `cold_res` | ambiguous | 2 | 2 | 17, 1027 |
| `crit_chance_pct` | ambiguous | 4 | 5 | 5, 62, 84, 672 |
| `dexterity` | ambiguous | 2 | 2 | 503, 1017 |
| `dodge_rating` | ambiguous | 2 | 2 | 8, 59 |
| `endurance` | ambiguous | 2 | 2 | 92, 1020 |
| `fire_penetration` | ambiguous | 2 | 2 | 32, 720 |

## Production Non-Consumption

The JSON artifact is marked `read_only=true`, `candidate_only=true`, `production_safe=false`, `production_consumer=false`, and `consumption_status=not_consumed`. It is generated under `docs/generated` for review only and is not imported by production services or routes.

## Migration Implications

These candidates are safe for review, not safe for production consumption. One-to-one mapping shape alone does not prove gameplay correctness, value-scale compatibility, slot applicability equivalence, or simulation behavior.

A future adapter must be introduced behind a separate feature flag and tested against planner, crafting, stat aggregation, and simulation baselines. One-to-many and ambiguous mappings require separate policy and design work before they can become candidates.

Recommended next step: review the candidate list against value-scale and slot-applicability blockers, then design a feature-flagged adapter prototype that consumes only an explicitly approved subset in tests.
