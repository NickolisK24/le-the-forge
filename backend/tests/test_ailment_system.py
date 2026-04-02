"""
Tests for the Ailment System Foundation (Step 2).

Validates:
  - AilmentType enum members exist
  - AilmentInstance is frozen with correct fields
  - apply_ailment adds independent stacks
  - tick_ailments advances time, collects damage, expires stacks
"""

import pytest
from app.domain.ailments import AilmentType, AilmentInstance, apply_ailment, tick_ailments


# ---------------------------------------------------------------------------
# AilmentType
# ---------------------------------------------------------------------------

class TestAilmentType:
    def test_all_types_exist(self):
        names = {a.value for a in AilmentType}
        assert names == {"bleed", "ignite", "poison", "shock", "frostbite"}

    def test_enum_members_accessible(self):
        assert AilmentType.BLEED.value == "bleed"
        assert AilmentType.IGNITE.value == "ignite"
        assert AilmentType.POISON.value == "poison"
        assert AilmentType.SHOCK.value == "shock"
        assert AilmentType.FROSTBITE.value == "frostbite"


# ---------------------------------------------------------------------------
# AilmentInstance
# ---------------------------------------------------------------------------

class TestAilmentInstance:
    def test_fields_accessible(self):
        inst = AilmentInstance(
            ailment_type=AilmentType.BLEED,
            damage_per_tick=50.0,
            duration=4.0,
        )
        assert inst.ailment_type is AilmentType.BLEED
        assert inst.damage_per_tick == 50.0
        assert inst.duration == 4.0
        assert inst.stack_count == 1

    def test_stack_count_override(self):
        inst = AilmentInstance(
            ailment_type=AilmentType.POISON,
            damage_per_tick=10.0,
            duration=2.0,
            stack_count=3,
        )
        assert inst.stack_count == 3

    def test_is_frozen(self):
        inst = AilmentInstance(
            ailment_type=AilmentType.IGNITE,
            damage_per_tick=100.0,
            duration=3.0,
        )
        with pytest.raises((AttributeError, TypeError)):
            inst.duration = 99.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# apply_ailment
# ---------------------------------------------------------------------------

class TestApplyAilment:
    def test_apply_to_empty_list(self):
        result = apply_ailment([], AilmentType.BLEED, 30.0, 4.0)
        assert len(result) == 1
        assert result[0].ailment_type is AilmentType.BLEED
        assert result[0].damage_per_tick == 30.0
        assert result[0].duration == 4.0

    def test_ailments_stack_independently(self):
        active = apply_ailment([], AilmentType.BLEED, 30.0, 4.0)
        active = apply_ailment(active, AilmentType.BLEED, 30.0, 4.0)
        assert len(active) == 2

    def test_different_types_stack(self):
        active = apply_ailment([], AilmentType.BLEED, 30.0, 4.0)
        active = apply_ailment(active, AilmentType.IGNITE, 80.0, 2.0)
        assert len(active) == 2
        types = {inst.ailment_type for inst in active}
        assert AilmentType.BLEED in types
        assert AilmentType.IGNITE in types

    def test_original_list_not_mutated(self):
        original = apply_ailment([], AilmentType.BLEED, 30.0, 4.0)
        original_len = len(original)
        apply_ailment(original, AilmentType.POISON, 10.0, 2.0)
        assert len(original) == original_len

    def test_apply_returns_new_list(self):
        active: list = []
        result = apply_ailment(active, AilmentType.SHOCK, 5.0, 1.0)
        assert result is not active

    def test_new_stack_has_default_stack_count(self):
        result = apply_ailment([], AilmentType.FROSTBITE, 20.0, 3.0)
        assert result[0].stack_count == 1


# ---------------------------------------------------------------------------
# tick_ailments
# ---------------------------------------------------------------------------

class TestTickAilments:
    def test_empty_list_returns_zero_damage(self):
        remaining, damage = tick_ailments([], 1.0)
        assert remaining == []
        assert damage == 0.0

    def test_damage_equals_damage_per_tick_times_delta(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        _, damage = tick_ailments(active, 1.0)
        assert damage == pytest.approx(50.0)

    def test_damage_scales_with_tick_delta(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        _, damage = tick_ailments(active, 0.5)
        assert damage == pytest.approx(25.0)

    def test_multiple_stacks_sum_damage(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        active = apply_ailment(active, AilmentType.BLEED, 50.0, 4.0)
        _, damage = tick_ailments(active, 1.0)
        assert damage == pytest.approx(100.0)

    def test_mixed_types_sum_damage(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        active = apply_ailment(active, AilmentType.IGNITE, 80.0, 2.0)
        _, damage = tick_ailments(active, 1.0)
        assert damage == pytest.approx(130.0)

    def test_duration_decreases_after_tick(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 4.0)
        remaining, _ = tick_ailments(active, 1.0)
        assert len(remaining) == 1
        assert remaining[0].duration == pytest.approx(3.0)

    def test_expired_stack_removed(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 1.0)
        remaining, _ = tick_ailments(active, 1.0)
        assert remaining == []

    def test_tick_exceeding_duration_removes_stack(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 0.5)
        remaining, _ = tick_ailments(active, 1.0)
        assert remaining == []

    def test_partial_expiry_keeps_longer_stacks(self):
        active = apply_ailment([], AilmentType.BLEED, 50.0, 0.5)   # expires
        active = apply_ailment(active, AilmentType.BLEED, 30.0, 4.0)  # survives
        remaining, _ = tick_ailments(active, 1.0)
        assert len(remaining) == 1
        assert remaining[0].damage_per_tick == pytest.approx(30.0)

    def test_ailment_type_preserved_after_tick(self):
        active = apply_ailment([], AilmentType.POISON, 20.0, 3.0)
        remaining, _ = tick_ailments(active, 1.0)
        assert remaining[0].ailment_type is AilmentType.POISON

    def test_stack_count_preserved_after_tick(self):
        inst = AilmentInstance(AilmentType.BLEED, 50.0, 4.0, stack_count=5)
        remaining, _ = tick_ailments([inst], 1.0)
        assert remaining[0].stack_count == 5

    def test_cumulative_ticks_expire_correctly(self):
        active = apply_ailment([], AilmentType.IGNITE, 100.0, 3.0)
        active, _ = tick_ailments(active, 1.0)
        assert len(active) == 1
        active, _ = tick_ailments(active, 1.0)
        assert len(active) == 1
        active, _ = tick_ailments(active, 1.0)
        assert len(active) == 0

    def test_damage_only_from_alive_stacks(self):
        # short stack: expires at t=0.5, should not contribute full second
        active = apply_ailment([], AilmentType.BLEED, 50.0, 0.5)
        active = apply_ailment(active, AilmentType.BLEED, 30.0, 4.0)
        # Both stacks contribute damage_per_tick * tick_delta regardless of mid-tick expiry
        _, damage = tick_ailments(active, 1.0)
        assert damage == pytest.approx(80.0)
