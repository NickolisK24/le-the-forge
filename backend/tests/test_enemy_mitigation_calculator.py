"""
Tests for enemy_mitigation_calculator — armor and resistance mitigation formulas.

Covers:
  armor_mitigation(armor, area_level, *, physical)
  effective_resistance(enemy, damage_type, penetration)
  damage_multiplier(enemy, damage_types, pen_map, area_level)
  weighted_damage_multiplier(enemy, damage_by_type, pen_map, area_level)
"""

from __future__ import annotations

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.constants.defense import (
    ARMOR_MITIGATION_CAP,
    ARMOR_NON_PHYSICAL_EFFECTIVENESS,
)
from app.domain.calculators.enemy_mitigation_calculator import (
    RES_CAP,
    armor_mitigation,
    damage_multiplier,
    effective_resistance,
    weighted_damage_multiplier,
)
from app.domain.enemy import EnemyProfile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _enemy(
    armor: int = 0,
    resistances: dict[str, float] | None = None,
) -> EnemyProfile:
    return EnemyProfile(
        id="test_enemy",
        name="Test Enemy",
        category="normal",
        data_version="test",
        health=1000,
        armor=armor,
        resistances=dict(resistances or {}),
    )


# ---------------------------------------------------------------------------
# armor_mitigation
# ---------------------------------------------------------------------------

class TestArmorMitigation:
    def test_zero_armor_returns_zero(self):
        assert armor_mitigation(0, 100, physical=True) == 0.0

    def test_negative_armor_returns_zero(self):
        assert armor_mitigation(-500, 100, physical=True) == 0.0

    def test_physical_1000_armor_area_100_is_half(self):
        # 1000 / (1000 + 10×100) = 0.5
        assert armor_mitigation(1000, 100, physical=True) == pytest.approx(0.5)

    def test_physical_extreme_armor_caps_at_85_pct(self):
        # Huge armor hits the 85% physical cap.
        assert armor_mitigation(10_000, 100, physical=True) == pytest.approx(0.85)
        assert armor_mitigation(1_000_000, 100, physical=True) == pytest.approx(0.85)

    def test_non_physical_less_effective_than_physical(self):
        phys = armor_mitigation(1000, 100, physical=True)
        elem = armor_mitigation(1000, 100, physical=False)
        assert elem < phys

    def test_non_physical_cap_applies_effectiveness_factor(self):
        # Non-physical cap = ARMOR_MITIGATION_CAP × ARMOR_NON_PHYSICAL_EFFECTIVENESS
        expected = ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS
        assert armor_mitigation(10_000_000, 100, physical=False) == pytest.approx(expected)

    def test_area_level_affects_formula(self):
        # Larger divisor (higher area_level) → lower mitigation for same armor.
        # At armor=1000: area=100 → 0.5, area=200 → 0.333
        low_area = armor_mitigation(1000, 58, physical=True)
        high_area = armor_mitigation(1000, 100, physical=True)
        assert low_area != high_area  # proves area_level actually affects the formula

    def test_area_level_zero_returns_cap(self):
        # Guard clause: area_level <= 0 returns the appropriate cap
        assert armor_mitigation(1000, 0, physical=True) == pytest.approx(ARMOR_MITIGATION_CAP)
        assert armor_mitigation(1000, 0, physical=False) == pytest.approx(
            ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS
        )


# ---------------------------------------------------------------------------
# effective_resistance
# ---------------------------------------------------------------------------

class TestEffectiveResistance:
    def test_zero_resistance_returns_zero(self):
        enemy = _enemy(resistances={"fire": 0.0})
        assert effective_resistance(enemy, "fire", penetration=0.0) == 0.0

    def test_resistance_capped_at_75(self):
        # Raw 100% resistance must be clamped to RES_CAP before any pen.
        enemy = _enemy(resistances={"fire": 100.0})
        assert RES_CAP == pytest.approx(75.0)
        assert effective_resistance(enemy, "fire", penetration=0.0) == pytest.approx(75.0)

    def test_penetration_subtracts_from_capped_resistance(self):
        # 75% capped - 30% pen = 45%
        enemy = _enemy(resistances={"fire": 90.0})  # raw 90 caps to 75
        assert effective_resistance(enemy, "fire", penetration=30.0) == pytest.approx(45.0)

    def test_penetration_cannot_push_below_zero(self):
        # 50% res - 80% pen = 0% (not -30)
        enemy = _enemy(resistances={"cold": 50.0})
        assert effective_resistance(enemy, "cold", penetration=80.0) == 0.0

    def test_missing_damage_type_returns_zero(self):
        enemy = _enemy(resistances={"fire": 50.0})
        assert effective_resistance(enemy, "lightning", penetration=0.0) == 0.0


# ---------------------------------------------------------------------------
# damage_multiplier
# ---------------------------------------------------------------------------

class TestDamageMultiplier:
    def test_empty_damage_types_falls_back_to_armor_only(self):
        enemy = _enemy(armor=1000)
        # Armor-only physical path: 1 - armor_mit(armor, area)
        expected = 1.0 - armor_mitigation(1000, 100, physical=True)
        assert damage_multiplier(enemy, set(), None, 100) == pytest.approx(expected)

    def test_physical_damage_uses_full_armor_effectiveness(self):
        enemy = _enemy(armor=1000)
        # No resistance entry → 0 res; just armor factor with physical armor.
        expected_armor = 1.0 - armor_mitigation(1000, 100, physical=True)
        got = damage_multiplier(enemy, {"physical"}, None, 100)
        assert got == pytest.approx(expected_armor)

    def test_non_physical_uses_reduced_armor_effectiveness(self):
        enemy = _enemy(armor=1000)
        phys = damage_multiplier(enemy, {"physical"}, None, 100)
        elem = damage_multiplier(enemy, {"fire"}, None, 100)
        # Non-physical armor mitigation is lower, so the post-armor multiplier
        # (1 - mit) is higher — more damage passes through.
        assert elem > phys

    def test_multiple_damage_types_use_average_resistance(self):
        enemy = _enemy(
            armor=0,
            resistances={"fire": 60.0, "cold": 20.0},
        )
        # No armor, no pen — armor factor is 1.0.
        # avg res = (60 + 20) / 2 = 40 → multiplier = 0.60
        got = damage_multiplier(enemy, {"fire", "cold"}, None, 100)
        assert got == pytest.approx(0.60)

    def test_pen_map_reduces_each_types_resistance(self):
        enemy = _enemy(armor=0, resistances={"fire": 60.0, "cold": 40.0})
        pen_map = {"fire": 30.0, "cold": 10.0}
        # effective fire = 60 - 30 = 30; effective cold = 40 - 10 = 30.
        # avg = 30 → multiplier = 0.70
        got = damage_multiplier(enemy, {"fire", "cold"}, pen_map, 100)
        assert got == pytest.approx(0.70)


# ---------------------------------------------------------------------------
# weighted_damage_multiplier
# ---------------------------------------------------------------------------

class TestWeightedDamageMultiplier:
    def test_empty_damage_by_type_falls_back_to_armor_only(self):
        enemy = _enemy(armor=1000)
        expected = 1.0 - armor_mitigation(1000, 100, physical=True)
        assert weighted_damage_multiplier(enemy, {}, None, 100) == pytest.approx(expected)

    def test_zero_total_damage_falls_back_to_armor_only(self):
        enemy = _enemy(armor=1000)
        expected = 1.0 - armor_mitigation(1000, 100, physical=True)
        got = weighted_damage_multiplier(
            enemy, {DamageType.FIRE: 0.0, DamageType.COLD: 0.0}, None, 100
        )
        assert got == pytest.approx(expected)

    def test_proportional_weighting_favors_dominant_type(self):
        # 90% fire / 10% physical — fire resistance should dominate the result.
        enemy = _enemy(armor=0, resistances={"fire": 60.0, "physical": 0.0})
        damage_by_type = {DamageType.FIRE: 90.0, DamageType.PHYSICAL: 10.0}
        got = weighted_damage_multiplier(enemy, damage_by_type, None, 100)
        # armor_factor = 1 (armor=0), res_factor = 0.9*(1-0.60) + 0.1*(1-0.0) = 0.46
        assert got == pytest.approx(0.46)

        # Flip the weights: 10% fire / 90% physical — physical res (0) dominates.
        damage_by_type_flipped = {DamageType.FIRE: 10.0, DamageType.PHYSICAL: 90.0}
        got_flipped = weighted_damage_multiplier(
            enemy, damage_by_type_flipped, None, 100
        )
        # res_factor = 0.1*(1-0.60) + 0.9*(1-0.0) = 0.94
        assert got_flipped == pytest.approx(0.94)
        assert got_flipped > got

    def test_all_zero_resistances_equals_pure_armor_mitigation(self):
        enemy = _enemy(armor=1000, resistances={"fire": 0.0, "cold": 0.0})
        damage_by_type = {DamageType.FIRE: 50.0, DamageType.COLD: 50.0}
        got = weighted_damage_multiplier(enemy, damage_by_type, None, 100)
        # No physical type → non-physical armor effectiveness applies.
        expected = 1.0 - armor_mitigation(1000, 100, physical=False)
        assert got == pytest.approx(expected)

    def test_physical_in_mix_uses_full_armor_effectiveness(self):
        enemy = _enemy(armor=1000, resistances={"fire": 0.0, "physical": 0.0})
        damage_by_type = {DamageType.PHYSICAL: 50.0, DamageType.FIRE: 50.0}
        got = weighted_damage_multiplier(enemy, damage_by_type, None, 100)
        expected = 1.0 - armor_mitigation(1000, 100, physical=True)
        assert got == pytest.approx(expected)
