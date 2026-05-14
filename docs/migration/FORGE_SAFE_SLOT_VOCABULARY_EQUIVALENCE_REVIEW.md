# Forge-Safe Slot Vocabulary Equivalence Review

Generated: 2026-05-11

## Purpose

This read-only diagnostic compares legacy slot/applicability vocabulary to Forge-safe bundle item/applicability vocabulary for one-to-one adapter candidate affixes only. It does not address value-scale differences and does not enable any runtime adapter.

## Sources

- Adapter candidates: `docs\generated\forge_safe_adapter_candidates.json`
- Comparison report: `docs\generated\forge_safe_legacy_affix_comparison.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_slot_vocabulary_equivalence.py --adapter-candidates docs\generated\forge_safe_adapter_candidates.json --comparison-report docs\generated\forge_safe_legacy_affix_comparison.json --output docs\generated\forge_safe_slot_vocabulary_equivalence.json --markdown-output docs\migration\FORGE_SAFE_SLOT_VOCABULARY_EQUIVALENCE_REVIEW.md
```

## Summary Counts

| Metric | Count |
| --- | ---: |
| candidate_count | 560 |
| candidate_affix_count | 560 |
| legacy_slot_value_count | 35 |
| bundle_item_value_count | 35 |
| one_to_one_slot_mapping_count | 1 |
| one_to_many_slot_mapping_count | 0 |
| ambiguous_slot_mapping_count | 34 |
| missing_slot_mapping_count | 0 |
| pure_vocabulary_candidate_count | 559 |
| slot_blocked_candidate_count | 1 |
| needs_manual_review_count | 0 |
| production_consumed | False |

## Top Legacy Slot Values

| Legacy slot | Candidate affix references |
| --- | ---: |
| `helm` | 128 |
| `chest` | 126 |
| `idol_1x4` | 93 |
| `idol_4x1` | 91 |
| `idol_2x2` | 91 |
| `idol_3x1` | 89 |
| `idol_1x3` | 86 |
| `axe_2h` | 33 |
| `spear` | 32 |
| `sword_1h` | 32 |
| `sword_2h` | 32 |
| `axe_1h` | 31 |
| `mace_2h` | 30 |
| `dagger` | 29 |
| `staff` | 29 |
| `mace_1h` | 28 |
| `sceptre` | 28 |
| `amulet` | 28 |
| `quiver` | 26 |
| `bow` | 24 |

## Top Bundle Item Values

| Bundle item value | Candidate affix references |
| --- | ---: |
| `HELMET` | 128 |
| `BODY_ARMOR` | 126 |
| `IDOL_1x4` | 93 |
| `IDOL_4x1` | 91 |
| `IDOL_2x2` | 91 |
| `IDOL_3x1` | 89 |
| `IDOL_1x3` | 86 |
| `TWO_HANDED_AXE` | 33 |
| `ONE_HANDED_SWORD` | 32 |
| `TWO_HANDED_SPEAR` | 32 |
| `TWO_HANDED_SWORD` | 32 |
| `ONE_HANDED_AXE` | 31 |
| `TWO_HANDED_MACE` | 30 |
| `ONE_HANDED_DAGGER` | 29 |
| `TWO_HANDED_STAFF` | 29 |
| `ONE_HANDED_MACES` | 28 |
| `ONE_HANDED_SCEPTRE` | 28 |
| `AMULET` | 28 |
| `QUIVER` | 26 |
| `BOW` | 24 |

## Mapping Shape Breakdown

| Shape | Count |
| --- | ---: |
| one_to_one | 1 |
| one_to_many | 0 |
| ambiguous | 34 |
| missing | 0 |

## Candidate Slot Status Breakdown

| Status | Count |
| --- | ---: |
| pure_vocabulary_difference | 559 |
| blocked_by_slot_applicability | 1 |
| needs_manual_review | 0 |

## Pure Vocabulary Difference Examples

| Legacy stat_key | Affixes | Legacy slots | Bundle items | Examples |
| --- | ---: | --- | --- | --- |
| `_all_attributes` | 1 | `axe_2h`, `mace_2h`, `spear`, `sword_2h` | `TWO_HANDED_AXE`, `TWO_HANDED_MACE`, `TWO_HANDED_SPEAR`, `TWO_HANDED_SWORD` | 50 |
| `acolyte_1_skeleton_and_increased_skeleton_damage` | 1 | `chest` | `BODY_ARMOR` | 192 |
| `acolyte_added_spell_damage_for_curses` | 1 | `helm` | `HELMET` | 749 |
| `acolyte_additional_projectile_chance_with_chaos_bolts` | 1 | `helm` | `HELMET` | 747 |
| `acolyte_chance_to_apply_damned_on_hit` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 421 |
| `acolyte_chance_to_cast_marrow_shards_when_you_cast_transplant` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 435 |
| `acolyte_chance_to_gain_20_ward_on_kill_with_hungering_souls` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 415 |
| `acolyte_damage_leeched_as_health_while_transformed` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 422 |
| `acolyte_increased_projectile_speed_with_marrow_shards_and_bone_nova` | 1 | `chest` | `BODY_ARMOR` | 417 |
| `acolyte_increased_skeletal_mage_damage` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 410 |
| `acolyte_increased_spirit_frequency_with_chthonic_fissure` | 1 | `chest` | `BODY_ARMOR` | 748 |
| `acolyte_leech_with_harvest` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 412 |
| `acolyte_mana_gained_on_harvest_use` | 1 | `chest` | `BODY_ARMOR` | 411 |
| `acolyte_minion_freeze_rate` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 384 |
| `acolyte_minion_reflect` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 413 |
| `acolyte_necrotic_damage_while_transformed` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 402 |
| `acolyte_physical_damage_while_transformed` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 401 |
| `acolyte_physical_spell_critical_strike_chance` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 424 |
| `acolyte_reduced_health_cost_of_spells` | 1 | `helm` | `HELMET` | 423 |
| `acolyte_spell_damage_per_skeletal_mage` | 1 | `chest`, `helm` | `BODY_ARMOR`, `HELMET` | 420 |

## Blocked Slot Applicability Examples

| Legacy stat_key | Affixes | Legacy slots | Bundle items | Examples |
| --- | ---: | --- | --- | --- |
| `health_on_kill` | 2 | `axe_1h`, `axe_2h`, `bow`, `dagger`, `mace_1h`, `mace_2h`, `quiver`, `sceptre` | `BOW`, `ONE_HANDED_AXE`, `ONE_HANDED_DAGGER`, `ONE_HANDED_MACES`, `ONE_HANDED_SCEPTRE`, `ONE_HANDED_SWORD`, `QUIVER`, `TWO_HANDED_AXE` | 20, 44 |

## Migration Implications

Slot vocabulary normalization is tractable for candidates classified as pure vocabulary differences because each candidate has a consistent legacy applicability set and a consistent bundle applicability set. This is still review evidence only; it does not prove gameplay correctness and does not resolve value-scale blockers.

Candidates classified as blocked need slot policy/design work before adapter prototyping. Value-scale normalization remains a separate audit after slot vocabulary policy is settled.

Recommended next step: document a slot vocabulary policy for the pure vocabulary candidate groups and explicitly list blocked slot-applicability cases that need design decisions before value-scale normalization work starts.
