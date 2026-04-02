"""
Tests for Skill Cooldown System (Step 52).

Validates:
  - SkillCooldown: is_ready, trigger, tick, validation
  - CooldownManager: register, can_cast, trigger, tick, remaining
  - Cooldown blocks casting; resets correctly after expiry
"""

import pytest
from app.domain.cooldown import SkillCooldown, CooldownManager


# ---------------------------------------------------------------------------
# SkillCooldown
# ---------------------------------------------------------------------------

class TestSkillCooldown:
    def test_default_is_ready(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        assert cd.is_ready is True

    def test_zero_cooldown_always_ready(self):
        cd = SkillCooldown("instant", cooldown_duration=0.0)
        cd.trigger()
        assert cd.is_ready is True

    def test_trigger_starts_cooldown(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        cd.trigger()
        assert cd.cooldown_remaining == pytest.approx(3.0)
        assert cd.is_ready is False

    def test_tick_reduces_remaining(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        cd.trigger()
        cd.tick(1.0)
        assert cd.cooldown_remaining == pytest.approx(2.0)

    def test_tick_clamps_at_zero(self):
        cd = SkillCooldown("fireball", cooldown_duration=1.0)
        cd.trigger()
        cd.tick(5.0)
        assert cd.cooldown_remaining == pytest.approx(0.0)
        assert cd.is_ready is True

    def test_tick_to_exactly_zero_is_ready(self):
        cd = SkillCooldown("fireball", cooldown_duration=2.0)
        cd.trigger()
        cd.tick(2.0)
        assert cd.is_ready is True

    def test_multiple_ticks_accumulate(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        cd.trigger()
        cd.tick(1.0)
        cd.tick(1.0)
        cd.tick(1.0)
        assert cd.is_ready is True

    def test_trigger_resets_cooldown(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        cd.trigger()
        cd.tick(3.0)
        cd.trigger()
        assert cd.cooldown_remaining == pytest.approx(3.0)

    def test_negative_cooldown_duration_raises(self):
        with pytest.raises(ValueError, match="cooldown_duration"):
            SkillCooldown("fireball", cooldown_duration=-1.0)

    def test_negative_cooldown_remaining_raises(self):
        with pytest.raises(ValueError, match="cooldown_remaining"):
            SkillCooldown("fireball", cooldown_duration=3.0, cooldown_remaining=-0.5)

    def test_negative_tick_delta_raises(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0)
        with pytest.raises(ValueError, match="delta"):
            cd.tick(-1.0)

    def test_fields_accessible(self):
        cd = SkillCooldown("fireball", cooldown_duration=3.0, cooldown_remaining=1.5)
        assert cd.skill_name == "fireball"
        assert cd.cooldown_duration == pytest.approx(3.0)
        assert cd.cooldown_remaining == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# CooldownManager
# ---------------------------------------------------------------------------

class TestCooldownManager:
    def test_unregistered_skill_raises_key_error(self):
        mgr = CooldownManager()
        with pytest.raises(KeyError):
            mgr.can_cast("fireball")

    def test_registered_skill_initially_ready(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        assert mgr.can_cast("fireball") is True

    def test_trigger_puts_skill_on_cooldown(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.trigger("fireball")
        assert mgr.can_cast("fireball") is False

    def test_trigger_on_cooldown_raises(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.trigger("fireball")
        with pytest.raises(RuntimeError, match="fireball"):
            mgr.trigger("fireball")

    def test_tick_reduces_all_cooldowns(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.register("frostbolt", 2.0)
        mgr.trigger("fireball")
        mgr.trigger("frostbolt")
        mgr.tick(1.0)
        assert mgr.remaining("fireball") == pytest.approx(2.0)
        assert mgr.remaining("frostbolt") == pytest.approx(1.0)

    def test_skill_ready_after_full_cooldown(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.trigger("fireball")
        mgr.tick(3.0)
        assert mgr.can_cast("fireball") is True

    def test_remaining_zero_when_ready(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        assert mgr.remaining("fireball") == pytest.approx(0.0)

    def test_zero_cooldown_always_castable(self):
        mgr = CooldownManager()
        mgr.register("instant_cast", 0.0)
        mgr.trigger("instant_cast")
        assert mgr.can_cast("instant_cast") is True

    def test_all_cooldowns_snapshot(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.register("frostbolt", 2.0)
        mgr.trigger("fireball")
        snap = mgr.all_cooldowns
        assert snap["fireball"] == pytest.approx(3.0)
        assert snap["frostbolt"] == pytest.approx(0.0)

    def test_multiple_casts_after_cooldown(self):
        mgr = CooldownManager()
        mgr.register("fireball", 2.0)
        mgr.trigger("fireball")
        mgr.tick(2.0)
        mgr.trigger("fireball")   # second cast — should not raise
        assert mgr.remaining("fireball") == pytest.approx(2.0)

    def test_independent_skills_do_not_interfere(self):
        mgr = CooldownManager()
        mgr.register("fireball", 3.0)
        mgr.register("frostbolt", 1.0)
        mgr.trigger("fireball")
        mgr.tick(1.0)
        # frostbolt was never triggered so remains ready
        assert mgr.can_cast("frostbolt") is True
        assert mgr.can_cast("fireball") is False
