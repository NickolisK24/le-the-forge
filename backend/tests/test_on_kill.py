"""
Tests for On-Kill Event System (Step 67).
"""

import pytest
from app.domain.on_kill import (
    OnKillContext,
    OnKillEffect,
    OnKillEffectType,
    OnKillRegistry,
)


def ctx(**kwargs) -> OnKillContext:
    return OnKillContext(**kwargs)


class TestOnKillEffect:
    def test_basic_construction(self):
        e = OnKillEffect(OnKillEffectType.RESTORE_MANA, value=30.0)
        assert e.effect_type is OnKillEffectType.RESTORE_MANA
        assert e.value == pytest.approx(30.0)
        assert e.chance_pct == pytest.approx(100.0)

    def test_invalid_chance_raises(self):
        with pytest.raises(ValueError, match="chance_pct"):
            OnKillEffect(OnKillEffectType.RESTORE_MANA, chance_pct=101.0)

    def test_negative_chance_raises(self):
        with pytest.raises(ValueError, match="chance_pct"):
            OnKillEffect(OnKillEffectType.RESTORE_MANA, chance_pct=-1.0)

    def test_zero_chance_allowed(self):
        e = OnKillEffect(OnKillEffectType.RESTORE_MANA, chance_pct=0.0)
        assert e.chance_pct == pytest.approx(0.0)

    def test_all_effect_types_constructible(self):
        for et in OnKillEffectType:
            e = OnKillEffect(et)
            assert e.effect_type is et


class TestOnKillContext:
    def test_defaults(self):
        c = OnKillContext()
        assert c.enemy_name == ""
        assert c.overkill_damage == pytest.approx(0.0)

    def test_with_values(self):
        c = OnKillContext(enemy_name="orc", enemy_max_health=500.0, overkill_damage=50.0)
        assert c.enemy_name == "orc"
        assert c.enemy_max_health == pytest.approx(500.0)
        assert c.overkill_damage == pytest.approx(50.0)


class TestOnKillRegistry:
    def test_empty_registry_returns_empty(self):
        reg = OnKillRegistry()
        assert reg.process_kill(ctx()) == []

    def test_100pct_chance_always_fires(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.RESTORE_MANA, value=20.0)
        reg.register(e)
        fired = reg.process_kill(ctx(), rng_roll=99.9)
        assert e in fired

    def test_0pct_chance_never_fires(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.RESTORE_MANA, chance_pct=0.0)
        reg.register(e)
        fired = reg.process_kill(ctx(), rng_roll=0.0)
        assert fired == []

    def test_roll_below_threshold_fires(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.GRANT_CHARGE, chance_pct=50.0)
        reg.register(e)
        assert e in reg.process_kill(ctx(), rng_roll=49.9)

    def test_roll_at_threshold_no_fire(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.GRANT_CHARGE, chance_pct=50.0)
        reg.register(e)
        assert reg.process_kill(ctx(), rng_roll=50.0) == []

    def test_none_roll_treated_as_zero(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.RESTORE_HEALTH, chance_pct=1.0)
        reg.register(e)
        assert e in reg.process_kill(ctx(), rng_roll=None)

    def test_multiple_effects_all_fire(self):
        reg = OnKillRegistry()
        e1 = OnKillEffect(OnKillEffectType.RESTORE_MANA,   value=20.0)
        e2 = OnKillEffect(OnKillEffectType.RESTORE_HEALTH, value=10.0)
        reg.register(e1)
        reg.register(e2)
        fired = reg.process_kill(ctx())
        assert e1 in fired
        assert e2 in fired

    def test_only_passing_effects_returned(self):
        reg = OnKillRegistry()
        always = OnKillEffect(OnKillEffectType.RESTORE_MANA,   chance_pct=100.0)
        never  = OnKillEffect(OnKillEffectType.RESTORE_HEALTH, chance_pct=0.0)
        reg.register(always)
        reg.register(never)
        fired = reg.process_kill(ctx())
        assert always in fired
        assert never not in fired

    def test_clear_removes_all_effects(self):
        reg = OnKillRegistry()
        reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA))
        reg.clear()
        assert reg.process_kill(ctx()) == []
        assert reg.effects == []

    def test_effects_property_snapshot(self):
        reg = OnKillRegistry()
        e = OnKillEffect(OnKillEffectType.GAIN_BUFF, value=20.0, duration=3.0)
        reg.register(e)
        snap = reg.effects
        assert e in snap
        # Mutating snapshot does not affect registry
        snap.clear()
        assert len(reg.effects) == 1

    def test_reset_cooldown_effect_fields(self):
        e = OnKillEffect(
            OnKillEffectType.RESET_COOLDOWN,
            skill_name="fireball",
            chance_pct=100.0,
        )
        assert e.skill_name == "fireball"
