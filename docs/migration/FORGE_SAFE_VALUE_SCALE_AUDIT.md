# Forge-Safe Value Scale Audit

Generated: 2026-05-11

## Purpose

This read-only audit checks value-scale and tier evidence for the slot-policy-approved Forge-safe adapter candidates. It excludes slot-blocked candidates such as `health_on_kill` and does not build or enable a runtime adapter.

## Sources

- Slot policy: `docs\generated\forge_safe_slot_vocabulary_policy.json`
- Comparison report: `docs\generated\forge_safe_legacy_affix_comparison.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_value_scale_audit.py --slot-policy docs\generated\forge_safe_slot_vocabulary_policy.json --comparison-report docs\generated\forge_safe_legacy_affix_comparison.json --output docs\generated\forge_safe_value_scale_audit.json --markdown-output docs\migration\FORGE_SAFE_VALUE_SCALE_AUDIT.md
```

## Summary Counts

| Metric | Count |
| --- | ---: |
| slot_policy_approved_candidate_count | 559 |
| audited_candidate_count | 559 |
| excluded_slot_blocked_candidate_count | 1 |
| structurally_equivalent_count | 0 |
| consistent_scale_factor_count | 0 |
| polarity_difference_count | 0 |
| min_max_shape_difference_count | 0 |
| tier_count_difference_count | 0 |
| malformed_or_missing_values_count | 559 |
| needs_manual_review_count | 0 |
| future_test_adapter_candidate_count | 0 |
| production_consumed | False |

## Excluded Candidates

`health_on_kill` is excluded because the slot vocabulary policy keeps it blocked by inconsistent applicability evidence.

## Value Status Breakdown

| Status | Count |
| --- | ---: |
| structurally_equivalent | 0 |
| consistent_scale_factor | 0 |
| polarity_difference | 0 |
| min_max_shape_difference | 0 |
| tier_count_difference | 0 |
| malformed_or_missing_values | 559 |
| needs_manual_review | 0 |

## Scale Factor Breakdown

No deterministic scale factors were proven.

## Future Test Adapter Candidates

No candidates in this category.

## Top Blocked Candidates By Affix Count

| Legacy stat_key | Status | Affixes | Scale factor | Examples |
| --- | --- | ---: | --- | --- |
| `_all_attributes` | malformed_or_missing_values | 1 |  | 50 |
| `acolyte_1_skeleton_and_increased_skeleton_damage` | malformed_or_missing_values | 1 |  | 192 |
| `acolyte_added_spell_damage_for_curses` | malformed_or_missing_values | 1 |  | 749 |
| `acolyte_additional_projectile_chance_with_chaos_bolts` | malformed_or_missing_values | 1 |  | 747 |
| `acolyte_chance_to_apply_damned_on_hit` | malformed_or_missing_values | 1 |  | 421 |
| `acolyte_chance_to_cast_marrow_shards_when_you_cast_transplant` | malformed_or_missing_values | 1 |  | 435 |
| `acolyte_chance_to_gain_20_ward_on_kill_with_hungering_souls` | malformed_or_missing_values | 1 |  | 415 |
| `acolyte_damage_leeched_as_health_while_transformed` | malformed_or_missing_values | 1 |  | 422 |
| `acolyte_increased_projectile_speed_with_marrow_shards_and_bone_nova` | malformed_or_missing_values | 1 |  | 417 |
| `acolyte_increased_skeletal_mage_damage` | malformed_or_missing_values | 1 |  | 410 |
| `acolyte_increased_spirit_frequency_with_chthonic_fissure` | malformed_or_missing_values | 1 |  | 748 |
| `acolyte_leech_with_harvest` | malformed_or_missing_values | 1 |  | 412 |
| `acolyte_mana_gained_on_harvest_use` | malformed_or_missing_values | 1 |  | 411 |
| `acolyte_minion_freeze_rate` | malformed_or_missing_values | 1 |  | 384 |
| `acolyte_minion_reflect` | malformed_or_missing_values | 1 |  | 413 |
| `acolyte_necrotic_damage_while_transformed` | malformed_or_missing_values | 1 |  | 402 |
| `acolyte_physical_damage_while_transformed` | malformed_or_missing_values | 1 |  | 401 |
| `acolyte_physical_spell_critical_strike_chance` | malformed_or_missing_values | 1 |  | 424 |
| `acolyte_reduced_health_cost_of_spells` | malformed_or_missing_values | 1 |  | 423 |
| `acolyte_spell_damage_per_skeletal_mage` | malformed_or_missing_values | 1 |  | 420 |
| `acolyte_volatile_zombie_damage_and_explosion_area` | malformed_or_missing_values | 1 |  | 650 |
| `acolyte_volatile_zombie_speed_and_damage` | malformed_or_missing_values | 1 |  | 649 |
| `added_bow_cold_damage` | malformed_or_missing_values | 1 |  | 670 |
| `added_bow_fire` | malformed_or_missing_values | 1 |  | 434 |
| `added_bow_lightning_damage` | malformed_or_missing_values | 1 |  | 669 |

## Migration Implications

The current comparison report does not include tier min/max arrays, so value-scale equivalence cannot be proven for the slot-policy-approved candidates. This is evidence to write a value normalization policy/report that preserves full tier min/max data before any adapter prototype.

Recommended next task: extend or regenerate diagnostics to preserve tier min/max evidence, then document a value normalization policy before any test-only adapter subset design.
