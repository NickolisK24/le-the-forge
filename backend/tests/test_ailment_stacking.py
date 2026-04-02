"""
Tests for Ailment Stacking Logic (Step 3).

Validates:
  - STACK_LIMITS constants are correct per type
  - enforce_stack_limit trims oldest stacks at the cap
  - Stacks of other types are not affected by enforcement
  - apply_ailment_with_limit combines application + enforcement
  - calculate_total_ailment_damage sums DPS across all stacks
"""

import pytest
from app.domain.ailments import AilmentType, AilmentInstance, apply_ailment
from app.domain.ailment_stacking import (
    STACK_LIMITS,
    enforce_stack_limit,
    apply_ailment_with_limit,
    calculate_total_ailment_damage,
)


# ---------------------------------------------------------------------------
# STACK_LIMITS
# ---------------------------------------------------------------------------

class TestStackLimits:
    def test_bleed_limit(self):
        assert STACK_LIMITS[AilmentType.BLEED] == 8

    def test_poison_limit(self):
        assert STACK_LIMITS[AilmentType.POISON] == 8

    def test_ignite_limit(self):
        assert STACK_LIMITS[AilmentType.IGNITE] == 1

    def test_shock_limit(self):
        assert STACK_LIMITS[AilmentType.SHOCK] == 1

    def test_frostbite_limit(self):
        assert STACK_LIMITS[AilmentType.FROSTBITE] == 1

    def test_all_types_have_limits(self):
        for t in AilmentType:
            assert t in STACK_LIMITS, f"{t} missing from STACK_LIMITS"


# ---------------------------------------------------------------------------
# enforce_stack_limit
# ---------------------------------------------------------------------------

class TestEnforceStackLimit:
    def _make_bleeds(self, n: int, dmg_start: float = 10.0) -> list[AilmentInstance]:
        active: list[AilmentInstance] = []
        for i in range(n):
            active = apply_ailment(active, AilmentType.BLEED, dmg_start + i, 4.0)
        return active

    def test_within_limit_unchanged(self):
        active = self._make_bleeds(4)
        result = enforce_stack_limit(active, AilmentType.BLEED)
        assert len(result) == 4

    def test_at_limit_unchanged(self):
        active = self._make_bleeds(8)
        result = enforce_stack_limit(active, AilmentType.BLEED)
        assert len(result) == 8

    def test_over_limit_trimmed_to_limit(self):
        active = self._make_bleeds(10)
        result = enforce_stack_limit(active, AilmentType.BLEED)
        bleeds = [i for i in result if i.ailment_type is AilmentType.BLEED]
        assert len(bleeds) == 8

    def test_oldest_stacks_removed(self):
        # stacks applied in order with dmg 10, 11, ..., 17 (8 newest kept from 10 total)
        active = self._make_bleeds(10, dmg_start=10.0)
        result = enforce_stack_limit(active, AilmentType.BLEED)
        bleeds = [i for i in result if i.ailment_type is AilmentType.BLEED]
        dps_values = {i.damage_per_tick for i in bleeds}
        # oldest 2 stacks (dmg=10, dmg=11) should be removed; newest 8 kept (12..19)
        assert 10.0 not in dps_values
        assert 11.0 not in dps_values
        assert 19.0 in dps_values  # newest kept

    def test_other_types_untouched(self):
        active = self._make_bleeds(10)
        active = apply_ailment(active, AilmentType.IGNITE, 200.0, 3.0)
        result = enforce_stack_limit(active, AilmentType.BLEED)
        ignites = [i for i in result if i.ailment_type is AilmentType.IGNITE]
        assert len(ignites) == 1

    def test_ignite_single_stack_limit(self):
        active: list[AilmentInstance] = []
        for i in range(3):
            active = apply_ailment(active, AilmentType.IGNITE, 100.0 + i, 3.0)
        result = enforce_stack_limit(active, AilmentType.IGNITE)
        ignites = [i for i in result if i.ailment_type is AilmentType.IGNITE]
        assert len(ignites) == 1

    def test_ignite_keeps_most_recent(self):
        active: list[AilmentInstance] = []
        for dmg in [100.0, 150.0, 200.0]:
            active = apply_ailment(active, AilmentType.IGNITE, dmg, 3.0)
        result = enforce_stack_limit(active, AilmentType.IGNITE)
        ignites = [i for i in result if i.ailment_type is AilmentType.IGNITE]
        assert ignites[0].damage_per_tick == pytest.approx(200.0)

    def test_empty_list_stays_empty(self):
        assert enforce_stack_limit([], AilmentType.BLEED) == []

    def test_enforce_different_type_leaves_all_bleeds(self):
        active = self._make_bleeds(5)
        result = enforce_stack_limit(active, AilmentType.IGNITE)
        bleeds = [i for i in result if i.ailment_type is AilmentType.BLEED]
        assert len(bleeds) == 5


# ---------------------------------------------------------------------------
# apply_ailment_with_limit
# ---------------------------------------------------------------------------

class TestApplyAilmentWithLimit:
    def test_basic_application(self):
        result = apply_ailment_with_limit([], AilmentType.BLEED, 30.0, 4.0)
        assert len(result) == 1
        assert result[0].ailment_type is AilmentType.BLEED

    def test_respects_limit_on_apply(self):
        active: list[AilmentInstance] = []
        for _ in range(8):
            active = apply_ailment_with_limit(active, AilmentType.BLEED, 30.0, 4.0)
        # one more should still be 8
        active = apply_ailment_with_limit(active, AilmentType.BLEED, 30.0, 4.0)
        bleeds = [i for i in active if i.ailment_type is AilmentType.BLEED]
        assert len(bleeds) == 8

    def test_single_limit_types_keep_newest(self):
        active: list[AilmentInstance] = []
        active = apply_ailment_with_limit(active, AilmentType.IGNITE, 100.0, 3.0)
        active = apply_ailment_with_limit(active, AilmentType.IGNITE, 999.0, 3.0)
        ignites = [i for i in active if i.ailment_type is AilmentType.IGNITE]
        assert len(ignites) == 1
        assert ignites[0].damage_per_tick == pytest.approx(999.0)


# ---------------------------------------------------------------------------
# calculate_total_ailment_damage
# ---------------------------------------------------------------------------

class TestCalculateTotalAilmentDamage:
    def test_empty_list_returns_zero(self):
        assert calculate_total_ailment_damage([]) == pytest.approx(0.0)

    def test_single_stack(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        assert calculate_total_ailment_damage(active) == pytest.approx(50.0)

    def test_multiple_same_type(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        active = apply_ailment(active, AilmentType.BLEED, 30.0, 2.0)
        assert calculate_total_ailment_damage(active) == pytest.approx(80.0)

    def test_mixed_types_sum(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        active = apply_ailment(active, AilmentType.IGNITE, 200.0, 3.0)
        active = apply_ailment(active, AilmentType.POISON, 25.0, 6.0)
        assert calculate_total_ailment_damage(active) == pytest.approx(275.0)

    def test_after_stack_limit_enforced(self):
        active: list[AilmentInstance] = []
        for _ in range(9):
            active = apply_ailment_with_limit(active, AilmentType.BLEED, 10.0, 4.0)
        # 8 stacks × 10.0 dps = 80.0
        assert calculate_total_ailment_damage(active) == pytest.approx(80.0)

    def test_independent_of_duration(self):
        # DPS snapshot should not be affected by remaining duration
        a = apply_ailment([], AilmentType.BLEED, 50.0, 0.1)
        b = apply_ailment([], AilmentType.BLEED, 50.0, 100.0)
        assert calculate_total_ailment_damage(a) == calculate_total_ailment_damage(b)
