# Forge-Safe Adapter Candidate Validation Review

Generated: 2026-05-11

## Purpose

This read-only diagnostic validates the one-to-one adapter candidates against existing value-scale and slot-applicability evidence from the real legacy-vs-bundle comparison report. It does not build or enable a runtime adapter.

## Sources

- Adapter candidates: `docs\generated\forge_safe_adapter_candidates.json`
- Comparison report: `docs\generated\forge_safe_legacy_affix_comparison.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_adapter_candidate_validation.py --adapter-candidates docs\generated\forge_safe_adapter_candidates.json --comparison-report docs\generated\forge_safe_legacy_affix_comparison.json --output docs\generated\forge_safe_adapter_candidate_validation.json --markdown-output docs\migration\FORGE_SAFE_ADAPTER_CANDIDATE_VALIDATION_REVIEW.md
```

## Summary Counts

| Metric | Count |
| --- | ---: |
| candidate_count | 560 |
| approved_for_test_adapter_candidate_count | 0 |
| blocked_by_value_scale_count | 0 |
| blocked_by_slot_applicability_count | 0 |
| blocked_by_both_count | 560 |
| needs_manual_review_count | 0 |
| production_consumed | False |

## Validation Rules

- `approved_for_test_adapter_candidate`: no slot or tier/value blockers in all comparison evidence for the candidate.
- `blocked_by_value_scale`: tier/value differences exist and equivalence is not proven.
- `blocked_by_slot_applicability`: slot/applicability differences exist and equivalence is not proven.
- `blocked_by_both`: both value-scale and slot-applicability blockers exist.
- `needs_manual_review`: comparison evidence is absent, incomplete, or outside the explicit slot/tier policy.

The classifier does not infer safety from names, tooltips, casing, or likely vocabulary conversions.

## Status Breakdown

| Status | Count |
| --- | ---: |
| approved_for_test_adapter_candidate | 0 |
| blocked_by_value_scale | 0 |
| blocked_by_slot_applicability | 0 |
| blocked_by_both | 560 |
| needs_manual_review | 0 |

## Top Blocked Candidates By Affix Count

| Legacy stat_key | Status | Affixes | Difference types | Examples |
| --- | --- | ---: | --- | --- |
| `health_on_kill` | blocked_by_both | 2 | slot, stat_key, tier | 20, 44 |
| `_all_attributes` | blocked_by_both | 1 | slot, stat_key, tier | 50 |
| `acolyte_1_skeleton_and_increased_skeleton_damage` | blocked_by_both | 1 | modifier_count, slot, stat_key, tier | 192 |
| `acolyte_added_spell_damage_for_curses` | blocked_by_both | 1 | slot, stat_key, tier | 749 |
| `acolyte_additional_projectile_chance_with_chaos_bolts` | blocked_by_both | 1 | slot, stat_key, tier | 747 |
| `acolyte_chance_to_apply_damned_on_hit` | blocked_by_both | 1 | slot, stat_key, tier | 421 |
| `acolyte_chance_to_cast_marrow_shards_when_you_cast_transplant` | blocked_by_both | 1 | slot, stat_key, tier | 435 |
| `acolyte_chance_to_gain_20_ward_on_kill_with_hungering_souls` | blocked_by_both | 1 | slot, stat_key, tier | 415 |
| `acolyte_damage_leeched_as_health_while_transformed` | blocked_by_both | 1 | slot, stat_key, tier | 422 |
| `acolyte_increased_projectile_speed_with_marrow_shards_and_bone_nova` | blocked_by_both | 1 | slot, stat_key, structure, tier | 417 |
| `acolyte_increased_skeletal_mage_damage` | blocked_by_both | 1 | slot, stat_key, tier | 410 |
| `acolyte_increased_spirit_frequency_with_chthonic_fissure` | blocked_by_both | 1 | slot, stat_key, tier | 748 |
| `acolyte_leech_with_harvest` | blocked_by_both | 1 | slot, stat_key, tier | 412 |
| `acolyte_mana_gained_on_harvest_use` | blocked_by_both | 1 | slot, stat_key, tier | 411 |
| `acolyte_minion_freeze_rate` | blocked_by_both | 1 | slot, stat_key, tier | 384 |
| `acolyte_minion_reflect` | blocked_by_both | 1 | slot, stat_key, tier | 413 |
| `acolyte_necrotic_damage_while_transformed` | blocked_by_both | 1 | slot, stat_key, tier | 402 |
| `acolyte_physical_damage_while_transformed` | blocked_by_both | 1 | slot, stat_key, tier | 401 |
| `acolyte_physical_spell_critical_strike_chance` | blocked_by_both | 1 | slot, stat_key, tier | 424 |
| `acolyte_reduced_health_cost_of_spells` | blocked_by_both | 1 | slot, stat_key, tier | 423 |
| `acolyte_spell_damage_per_skeletal_mage` | blocked_by_both | 1 | slot, stat_key, tier | 420 |
| `acolyte_volatile_zombie_damage_and_explosion_area` | blocked_by_both | 1 | modifier_count, slot, stat_key, structure, tier | 650 |
| `acolyte_volatile_zombie_speed_and_damage` | blocked_by_both | 1 | modifier_count, slot, stat_key, tier | 649 |
| `added_bow_cold_damage` | blocked_by_both | 1 | slot, stat_key, tier | 670 |
| `added_bow_fire` | blocked_by_both | 1 | slot, stat_key, tier | 434 |

## Blocker Summary

- Value-scale blocked candidates: 560
- Slot-applicability blocked candidates: 560
- Approved candidates for future test-only adapter subset: 0

Because existing comparison evidence reports slot and tier/value differences for the matched affixes, one-to-one stat-key shape is not enough to approve candidates for direct use.

## Migration Implications

The 560 one-to-one candidates cannot be safely used directly. No production planner, crafting, stat aggregation, simulation, registry, or `/api/ref/affixes` behavior consumes this report.

The immediate blocker category is shared by slot vocabulary and value-scale evidence. Slot-vocabulary normalization should be addressed first if the goal is to establish item applicability equivalence without touching numerical gameplay values; value-scale normalization should follow as a separate audited policy.

Recommended next step: produce a read-only slot-vocabulary equivalence report for the candidate affixes, then separately audit value-scale normalization before any feature-flagged adapter prototype is designed.
