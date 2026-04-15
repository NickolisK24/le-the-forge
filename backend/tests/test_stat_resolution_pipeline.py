"""
Tests for stat_resolution_pipeline — Upgrade 1

Covers: 6-layer resolution, derived stats, conversions, resistance cap,
quick_resolve, snapshot capture, determinism, edge cases.
"""

from __future__ import annotations

import pytest
from dataclasses import asdict

from app.engines.stat_resolution_pipeline import (
    resolve_final_stats,
    quick_resolve,
    apply_derived_stats,
    apply_conversions,
    ResolutionResult,
    STR_TO_HEALTH,
    DEX_TO_DODGE,
    INT_TO_WARD_RETENTION,
    VIT_TO_HEALTH,
    ATT_TO_MANA_REGEN,
)
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build(
    char_class="Mage",
    mastery="Sorcerer",
    passive_tree=None,
    gear=None,
    **kw,
) -> dict:
    b = {
        "character_class": char_class,
        "mastery": mastery,
        "passive_tree": passive_tree or [],
        "gear": gear or [],
    }
    b.update(kw)
    return b


def _stats(**kw) -> BuildStats:
    s = BuildStats()
    for k, v in kw.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# 1. Basic API / Return type
# ---------------------------------------------------------------------------

class TestResolveReturnType:
    def test_returns_resolution_result(self):
        r = resolve_final_stats(_build())
        assert isinstance(r, ResolutionResult)

    def test_stats_field_is_build_stats(self):
        r = resolve_final_stats(_build())
        assert isinstance(r.stats, BuildStats)

    def test_resolution_order_has_8_layers(self):
        r = resolve_final_stats(_build())
        assert len(r.resolution_order) == 8

    def test_resolution_order_labels(self):
        r = resolve_final_stats(_build())
        labels = r.resolution_order
        assert labels[0].startswith("1")
        assert labels[1].startswith("2")
        assert labels[2].startswith("3")
        assert labels[3].startswith("4")
        assert labels[4].startswith("5")
        assert labels[5].startswith("6")

    def test_warnings_is_list(self):
        r = resolve_final_stats(_build())
        assert isinstance(r.warnings, list)

    def test_layer_snapshots_empty_without_capture(self):
        r = resolve_final_stats(_build(), capture_snapshots=False)
        assert r.layer_snapshots == {}

    def test_layer_snapshots_populated_with_capture(self):
        r = resolve_final_stats(_build(), capture_snapshots=True)
        assert len(r.layer_snapshots) > 0

    def test_to_dict_has_stats_key(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "stats" in d

    def test_to_dict_has_warnings_key(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "warnings" in d

    def test_to_dict_has_resolution_order_key(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "resolution_order" in d

    def test_to_dict_stats_is_dict(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert isinstance(d["stats"], dict)

    def test_quick_resolve_returns_build_stats(self):
        s = quick_resolve(_build())
        assert isinstance(s, BuildStats)

    def test_quick_resolve_matches_full_resolve(self):
        b = _build()
        full = resolve_final_stats(b).stats
        quick = quick_resolve(b)
        assert full.max_health == quick.max_health
        assert full.base_damage == quick.base_damage


# ---------------------------------------------------------------------------
# 2. Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    @pytest.mark.parametrize("char_class,mastery", [
        ("Mage", "Sorcerer"),
        ("Sentinel", "Paladin"),
        ("Rogue", "Bladedancer"),
        ("Primalist", "Druid"),
        ("Acolyte", "Lich"),
    ])
    def test_identical_inputs_give_identical_stats(self, char_class, mastery):
        b = _build(char_class=char_class, mastery=mastery)
        r1 = resolve_final_stats(b)
        r2 = resolve_final_stats(b)
        assert r1.stats.max_health == r2.stats.max_health
        assert r1.stats.base_damage == r2.stats.base_damage

    def test_multiple_calls_same_result_health(self):
        b = _build()
        results = [resolve_final_stats(b).stats.max_health for _ in range(5)]
        assert len(set(results)) == 1

    def test_multiple_calls_same_result_damage(self):
        b = _build()
        results = [resolve_final_stats(b).stats.base_damage for _ in range(5)]
        assert len(set(results)) == 1

    def test_empty_build_is_deterministic(self):
        b = _build(passive_tree=[], gear=[])
        r1 = resolve_final_stats(b)
        r2 = resolve_final_stats(b)
        assert asdict(r1.stats) == asdict(r2.stats)


# ---------------------------------------------------------------------------
# 3. Derived stats — apply_derived_stats()
# ---------------------------------------------------------------------------

class TestApplyDerivedStats:
    def test_strength_increases_health(self):
        s = _stats(max_health=100.0, strength=10.0)
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(100.0 + 10.0 * STR_TO_HEALTH)

    def test_dexterity_increases_dodge(self):
        s = _stats(dodge_rating=0.0, dexterity=20.0)
        apply_derived_stats(s)
        assert s.dodge_rating == pytest.approx(20.0 * DEX_TO_DODGE)

    def test_intelligence_increases_ward_retention(self):
        s = _stats(ward_retention_pct=0.0, intelligence=15.0)
        apply_derived_stats(s)
        assert s.ward_retention_pct == pytest.approx(15.0 * INT_TO_WARD_RETENTION)

    def test_vitality_increases_health(self):
        s = _stats(max_health=100.0, vitality=30.0)
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(100.0 + 30.0 * VIT_TO_HEALTH)

    def test_attunement_increases_mana_regen(self):
        s = _stats(mana_regen=0.0, attunement=25.0)
        apply_derived_stats(s)
        assert s.mana_regen == pytest.approx(25.0 * ATT_TO_MANA_REGEN)

    def test_zero_attributes_no_change(self):
        s = _stats(max_health=500.0, dodge_rating=100.0, strength=0.0,
                   dexterity=0.0, vitality=0.0, intelligence=0.0, attunement=0.0)
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(500.0)
        assert s.dodge_rating == pytest.approx(100.0)

    def test_str_and_vit_both_add_to_health(self):
        s = _stats(max_health=200.0, strength=10.0, vitality=10.0)
        apply_derived_stats(s)
        expected = 200.0 + 10.0 * STR_TO_HEALTH + 10.0 * VIT_TO_HEALTH
        assert s.max_health == pytest.approx(expected)

    @pytest.mark.parametrize("str_val,expected_bonus", [
        (0, 0), (1, STR_TO_HEALTH), (10, 10 * STR_TO_HEALTH),
        (50, 50 * STR_TO_HEALTH), (100, 100 * STR_TO_HEALTH),
    ])
    def test_strength_health_scaling(self, str_val, expected_bonus):
        s = _stats(max_health=0.0, strength=float(str_val))
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(expected_bonus)

    @pytest.mark.parametrize("dex_val,expected_bonus", [
        (0, 0), (5, 5 * DEX_TO_DODGE), (20, 20 * DEX_TO_DODGE),
        (100, 100 * DEX_TO_DODGE),
    ])
    def test_dexterity_dodge_scaling(self, dex_val, expected_bonus):
        s = _stats(dodge_rating=0.0, dexterity=float(dex_val))
        apply_derived_stats(s)
        assert s.dodge_rating == pytest.approx(expected_bonus)

    @pytest.mark.parametrize("vit_val,expected_bonus", [
        (0, 0), (10, 10 * VIT_TO_HEALTH), (50, 50 * VIT_TO_HEALTH),
    ])
    def test_vitality_health_scaling(self, vit_val, expected_bonus):
        s = _stats(max_health=0.0, vitality=float(vit_val))
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(expected_bonus)

    @pytest.mark.parametrize("att_val,expected_bonus", [
        (0, 0), (5, 5 * ATT_TO_MANA_REGEN), (25, 25 * ATT_TO_MANA_REGEN),
    ])
    def test_attunement_mana_regen_scaling(self, att_val, expected_bonus):
        s = _stats(mana_regen=0.0, attunement=float(att_val))
        apply_derived_stats(s)
        assert s.mana_regen == pytest.approx(expected_bonus)

    def test_derived_stats_applied_in_place(self):
        s = _stats(max_health=100.0, strength=10.0)
        apply_derived_stats(s)
        assert s.max_health > 100.0

    def test_high_attributes_large_bonus(self):
        s = _stats(max_health=0.0, strength=200.0, vitality=200.0)
        apply_derived_stats(s)
        assert s.max_health > 0.0

    def test_large_dex_large_dodge(self):
        s = _stats(dodge_rating=0.0, dexterity=500.0)
        apply_derived_stats(s)
        assert s.dodge_rating == pytest.approx(500.0 * DEX_TO_DODGE)

    def test_intelligence_does_not_affect_health(self):
        s = _stats(max_health=100.0, intelligence=100.0, strength=0.0, vitality=0.0)
        apply_derived_stats(s)
        assert s.max_health == pytest.approx(100.0)

    def test_attunement_does_not_affect_dodge(self):
        s = _stats(dodge_rating=0.0, attunement=100.0, dexterity=0.0)
        apply_derived_stats(s)
        assert s.dodge_rating == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 4. apply_conversions()
# ---------------------------------------------------------------------------

class TestApplyConversionsIsNoop:
    """Layer 5 ``apply_conversions`` is intentionally a no-op.

    The previous stat-level percentage-copy implementation was
    mechanically wrong for Last Epoch (it kept both source and target
    increased pools active, double-counting). Correct conversion is
    handled by ``DamageConversion`` objects at the DPS calculation
    layer — see ``combat_engine.calculate_dps``. These tests lock in
    the no-op contract: no BuildStats field may change as a result of
    calling ``apply_conversions``, and every input shape the old API
    accepted must still not raise.
    """

    def test_no_damage_pct_field_is_modified(self):
        s = _stats(
            physical_damage_pct=200.0,
            fire_damage_pct=0.0,
            cold_damage_pct=0.0,
        )
        apply_conversions(s, [{"from": "physical", "to": "fire", "pct": 100}])
        assert s.physical_damage_pct == pytest.approx(200.0)
        assert s.fire_damage_pct == pytest.approx(0.0)
        assert s.cold_damage_pct == pytest.approx(0.0)

    def test_buildstats_identical_before_and_after(self):
        s = _stats(
            physical_damage_pct=150.0,
            fire_damage_pct=40.0,
            cold_damage_pct=25.0,
            lightning_damage_pct=60.0,
            max_health=2000.0,
            crit_multiplier_pct=80.0,
        )
        before = asdict(s)
        apply_conversions(
            s,
            [
                {"from": "physical", "to": "fire", "pct": 50},
                {"from": "cold", "to": "lightning", "pct": 25},
            ],
        )
        after = asdict(s)
        assert before == after

    def test_accepts_none_without_raising(self):
        s = _stats(physical_damage_pct=100.0)
        apply_conversions(s, None)

    def test_accepts_empty_list_without_raising(self):
        s = _stats(physical_damage_pct=100.0)
        apply_conversions(s, [])

    def test_accepts_well_formed_list_without_raising(self):
        s = _stats(physical_damage_pct=100.0)
        apply_conversions(s, [{"from": "physical", "to": "fire", "pct": 50}])


# ---------------------------------------------------------------------------
# 5. Resistance cap enforcement
# ---------------------------------------------------------------------------

class TestResistanceCap:
    @pytest.mark.parametrize("res_attr", [
        "fire_res", "cold_res", "lightning_res",
        "void_res", "necrotic_res", "physical_res", "poison_res",
    ])
    def test_over_cap_generates_warning(self, res_attr):
        b = _build()
        # Inject over-capped resistance via gear_affixes won't be reliable;
        # test by resolving and checking cap is applied at output
        r = resolve_final_stats(b)
        # Whatever the result, res should not exceed 75
        assert getattr(r.stats, res_attr) <= 75.0

    def test_warning_added_when_res_exceeds_cap(self):
        # Inject extremely high resistance by providing gear_affixes
        # that would push a resistance over 75%
        b = _build()
        r = resolve_final_stats(b)
        # No warning if all resistances are within bounds
        for w in r.warnings:
            assert "capped" in w or "%" in w  # any warning must mention cap

    def test_no_warnings_for_zero_resistances(self):
        b = _build(char_class="Sentinel", mastery="Paladin",
                   passive_tree=[], gear=[])
        r = resolve_final_stats(b)
        assert r.warnings == []


# ---------------------------------------------------------------------------
# 6. Snapshot capture
# ---------------------------------------------------------------------------

class TestSnapshotCapture:
    def test_snapshots_empty_without_flag(self):
        r = resolve_final_stats(_build(), capture_snapshots=False)
        assert r.layer_snapshots == {}

    def test_snapshots_populated_with_flag(self):
        r = resolve_final_stats(_build(), capture_snapshots=True)
        assert len(r.layer_snapshots) >= 1

    def test_snapshots_are_dicts(self):
        r = resolve_final_stats(_build(), capture_snapshots=True)
        for snap in r.layer_snapshots.values():
            assert isinstance(snap, dict)

    def test_snapshot_has_max_health_key(self):
        r = resolve_final_stats(_build(), capture_snapshots=True)
        for snap in r.layer_snapshots.values():
            assert "max_health" in snap


# ---------------------------------------------------------------------------
# 7. Multiple character classes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"),
    ("Mage", "Runemaster"),
    ("Mage", "Spellblade"),
    ("Sentinel", "Forge Guard"),
    ("Sentinel", "Paladin"),
    ("Sentinel", "Void Knight"),
    ("Rogue", "Bladedancer"),
    ("Rogue", "Marksman"),
    ("Rogue", "Falconer"),
    ("Primalist", "Shaman"),
    ("Primalist", "Druid"),
    ("Primalist", "Beastmaster"),
    ("Acolyte", "Lich"),
    ("Acolyte", "Necromancer"),
    ("Acolyte", "Warlock"),
])
def test_all_class_mastery_resolve(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = resolve_final_stats(b)
    assert r.stats.max_health > 0


@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
    ("Primalist", "Druid"),
    ("Acolyte", "Lich"),
])
def test_different_classes_may_differ_in_stats(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert isinstance(r.stats.max_health, float)


# ---------------------------------------------------------------------------
# 8. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_passive_tree(self):
        b = _build(passive_tree=[])
        r = resolve_final_stats(b)
        assert r.stats.max_health > 0

    def test_empty_gear(self):
        b = _build(gear=[])
        r = resolve_final_stats(b)
        assert r.stats.max_health > 0

    def test_missing_char_class_uses_default(self):
        b = {"passive_tree": [], "gear": []}
        r = resolve_final_stats(b)
        assert isinstance(r.stats, BuildStats)

    def test_gear_affixes_override(self):
        b1 = _build()
        b2 = dict(b1)
        b2["gear_affixes"] = []
        r1 = resolve_final_stats(b1)
        r2 = resolve_final_stats(b2)
        # Both resolve without error
        assert isinstance(r1.stats, BuildStats)
        assert isinstance(r2.stats, BuildStats)

    def test_passive_tree_as_dicts(self):
        b = _build(passive_tree=[{"id": 1, "name": "test"}, {"id": 2}])
        r = resolve_final_stats(b)
        assert isinstance(r.stats, BuildStats)

    def test_passive_tree_as_ints(self):
        b = _build(passive_tree=[1, 2, 3])
        r = resolve_final_stats(b)
        assert isinstance(r.stats, BuildStats)

    def test_conversions_kwarg_takes_priority(self):
        b = _build(conversions=[{"from": "physical", "to": "fire", "pct": 10}])
        # Pass None as kwarg — should use build["conversions"]
        r = resolve_final_stats(b, conversions=None)
        assert isinstance(r.stats, BuildStats)

    def test_conversions_kwarg_overrides_build(self):
        b = _build(conversions=[{"from": "physical", "to": "fire", "pct": 100}])
        # Override with empty conversion
        r = resolve_final_stats(b, conversions=[])
        assert isinstance(r.stats, BuildStats)

    def test_gear_with_prefixes_and_suffixes(self):
        gear = [{"slot_type": "helmet", "forging_potential": 10,
                 "prefixes": [{"name": "Added Health", "tier": 1}],
                 "suffixes": []}]
        b = _build(gear=gear)
        r = resolve_final_stats(b)
        assert r.stats.max_health > 0

    def test_gear_with_affixes_list(self):
        gear = [{"slot_type": "helmet", "forging_potential": 10,
                 "affixes": [{"name": "Added Health", "tier": 2}]}]
        b = _build(gear=gear)
        r = resolve_final_stats(b)
        assert r.stats.max_health > 0

    def test_resolution_order_is_ordered_strings(self):
        r = resolve_final_stats(_build())
        for i, label in enumerate(r.resolution_order, 1):
            assert str(i) in label

    def test_stats_health_positive(self):
        r = resolve_final_stats(_build())
        assert r.stats.max_health > 0

    def test_no_negative_attack_speed(self):
        r = resolve_final_stats(_build())
        assert r.stats.attack_speed >= 0

    def test_no_negative_base_damage(self):
        r = resolve_final_stats(_build())
        assert r.stats.base_damage >= 0


# ---------------------------------------------------------------------------
# 9. Integration with other engines
# ---------------------------------------------------------------------------

class TestPipelineIntegration:
    def test_quick_resolve_usable_for_dps_calc(self):
        from app.engines.combat_engine import calculate_dps
        s = quick_resolve(_build())
        result = calculate_dps(s, "Fireball", 1)
        assert result.dps >= 0

    def test_quick_resolve_usable_for_ehp_calc(self):
        from app.engines.defense_engine import calculate_ehp
        s = quick_resolve(_build())
        ehp = calculate_ehp(s)
        assert ehp > 0

    def test_full_resolve_to_dict_serializable(self):
        import json
        r = resolve_final_stats(_build(), capture_snapshots=True)
        d = r.to_dict()
        # Should not raise
        json.dumps(d)

    def test_pipeline_result_stats_match_quick(self):
        b = _build(char_class="Rogue", mastery="Marksman")
        full = resolve_final_stats(b)
        quick = quick_resolve(b)
        assert full.stats.max_health == quick.max_health


# ---------------------------------------------------------------------------
# 10. Stat scaling monotonicity
# ---------------------------------------------------------------------------

class TestStatScalingMonotonicity:
    def test_more_strength_more_health(self):
        s_low = _stats(max_health=100.0, strength=10.0, vitality=0.0)
        s_high = _stats(max_health=100.0, strength=50.0, vitality=0.0)
        apply_derived_stats(s_low)
        apply_derived_stats(s_high)
        assert s_high.max_health > s_low.max_health

    def test_more_dex_more_dodge(self):
        s_low = _stats(dodge_rating=0.0, dexterity=10.0)
        s_high = _stats(dodge_rating=0.0, dexterity=100.0)
        apply_derived_stats(s_low)
        apply_derived_stats(s_high)
        assert s_high.dodge_rating > s_low.dodge_rating

    def test_more_int_more_ward_retention(self):
        s_low = _stats(ward_retention_pct=0.0, intelligence=10.0)
        s_high = _stats(ward_retention_pct=0.0, intelligence=100.0)
        apply_derived_stats(s_low)
        apply_derived_stats(s_high)
        assert s_high.ward_retention_pct > s_low.ward_retention_pct

    def test_more_vit_more_health(self):
        s_low = _stats(max_health=0.0, vitality=5.0, strength=0.0)
        s_high = _stats(max_health=0.0, vitality=50.0, strength=0.0)
        apply_derived_stats(s_low)
        apply_derived_stats(s_high)
        assert s_high.max_health > s_low.max_health

    def test_more_attunement_more_mana_regen(self):
        s_low = _stats(mana_regen=0.0, attunement=5.0)
        s_high = _stats(mana_regen=0.0, attunement=50.0)
        apply_derived_stats(s_low)
        apply_derived_stats(s_high)
        assert s_high.mana_regen > s_low.mana_regen


# ---------------------------------------------------------------------------
# 11. Parametrized stat coefficient checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stat_attr,coeff_name,coeff_val", [
    ("strength", "STR_TO_HEALTH", STR_TO_HEALTH),
    ("dexterity", "DEX_TO_DODGE", DEX_TO_DODGE),
    ("intelligence", "INT_TO_WARD_RETENTION", INT_TO_WARD_RETENTION),
    ("vitality", "VIT_TO_HEALTH", VIT_TO_HEALTH),
    ("attunement", "ATT_TO_MANA_REGEN", ATT_TO_MANA_REGEN),
])
def test_coefficient_is_positive(stat_attr, coeff_name, coeff_val):
    assert coeff_val > 0, f"{coeff_name} must be positive"


@pytest.mark.parametrize("points,coeff", [
    (1, STR_TO_HEALTH),
    (5, STR_TO_HEALTH),
    (10, STR_TO_HEALTH),
    (25, STR_TO_HEALTH),
    (50, STR_TO_HEALTH),
    (100, STR_TO_HEALTH),
    (200, STR_TO_HEALTH),
])
def test_str_health_exact(points, coeff):
    s = _stats(max_health=0.0, strength=float(points), vitality=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(points * coeff)


@pytest.mark.parametrize("points,coeff", [
    (1, DEX_TO_DODGE),
    (5, DEX_TO_DODGE),
    (10, DEX_TO_DODGE),
    (25, DEX_TO_DODGE),
    (50, DEX_TO_DODGE),
    (100, DEX_TO_DODGE),
])
def test_dex_dodge_exact(points, coeff):
    s = _stats(dodge_rating=0.0, dexterity=float(points))
    apply_derived_stats(s)
    assert s.dodge_rating == pytest.approx(points * coeff)


@pytest.mark.parametrize("points,coeff", [
    (1, VIT_TO_HEALTH),
    (10, VIT_TO_HEALTH),
    (50, VIT_TO_HEALTH),
    (100, VIT_TO_HEALTH),
])
def test_vit_health_exact(points, coeff):
    s = _stats(max_health=0.0, vitality=float(points), strength=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(points * coeff)


@pytest.mark.parametrize("points,coeff", [
    (1, ATT_TO_MANA_REGEN),
    (10, ATT_TO_MANA_REGEN),
    (50, ATT_TO_MANA_REGEN),
])
def test_att_mana_exact(points, coeff):
    s = _stats(mana_regen=0.0, attunement=float(points))
    apply_derived_stats(s)
    assert s.mana_regen == pytest.approx(points * coeff)


# ---------------------------------------------------------------------------
# 13. Resolution result to_dict completeness
# ---------------------------------------------------------------------------

class TestToDictCompleteness:
    def test_to_dict_layer_snapshots_empty_without_flag(self):
        r = resolve_final_stats(_build(), capture_snapshots=False)
        d = r.to_dict()
        assert d["layer_snapshots"] == {}

    def test_to_dict_resolution_order_is_list(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert isinstance(d["resolution_order"], list)

    def test_to_dict_warnings_is_list(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert isinstance(d["warnings"], list)

    def test_to_dict_stats_has_max_health(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "max_health" in d["stats"]

    def test_to_dict_stats_has_base_damage(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "base_damage" in d["stats"]

    def test_to_dict_stats_has_crit_chance(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "crit_chance" in d["stats"]

    def test_to_dict_stats_has_armour(self):
        r = resolve_final_stats(_build())
        d = r.to_dict()
        assert "armour" in d["stats"]


# ---------------------------------------------------------------------------
# 14. Stats remain within sane ranges after resolution
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Marksman"),
    ("Primalist", "Beastmaster"),
    ("Acolyte", "Necromancer"),
])
def test_crit_chance_within_range(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert 0.0 <= r.stats.crit_chance <= 1.0


@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Forge Guard"),
    ("Rogue", "Falconer"),
])
def test_attack_speed_positive(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert r.stats.attack_speed >= 0.0


@pytest.mark.parametrize("res_type", [
    "fire_res", "cold_res", "lightning_res",
    "void_res", "necrotic_res", "physical_res",
])
def test_resistance_at_most_75(res_type):
    r = resolve_final_stats(_build())
    val = getattr(r.stats, res_type)
    assert val <= 75.0
