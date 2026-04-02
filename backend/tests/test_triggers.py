"""
Tests for Conditional Trigger System (Step 55).

Validates:
  - evaluate_triggers returns only matching triggers
  - ON_CRIT requires is_crit=True in context
  - ON_LOW_MANA requires mana_pct < threshold
  - ON_HIT / ON_CAST / ON_KILL fire on any context
  - TriggerCondition guards (is_crit, min_hit_damage, mana_below_pct)
  - Chance roll: rng_roll <= chance_pct fires, > chance_pct does not
  - Multiple triggers evaluated independently
  - TriggerContext.mana_pct computed correctly
"""

import pytest
from app.domain.triggers import (
    Trigger,
    TriggerCondition,
    TriggerContext,
    TriggerEffect,
    TriggerType,
    evaluate_triggers,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_trigger(
    trigger_type: TriggerType = TriggerType.ON_HIT,
    effect: TriggerEffect = TriggerEffect.APPLY_BLEED,
    *,
    is_crit: bool = False,
    min_hit_damage: float = 0.0,
    mana_below_pct: float = 100.0,
    chance_pct: float = 100.0,
    effect_value: float = 0.0,
    source: str = "",
) -> Trigger:
    cond = TriggerCondition(
        is_crit=is_crit,
        min_hit_damage=min_hit_damage,
        mana_below_pct=mana_below_pct,
        chance_pct=chance_pct,
    )
    return Trigger(
        trigger_type=trigger_type,
        effect=effect,
        condition=cond,
        effect_value=effect_value,
        source=source,
    )


def hit_ctx(
    *,
    is_crit: bool = False,
    hit_damage: float = 100.0,
    current_mana: float = 100.0,
    max_mana: float = 100.0,
) -> TriggerContext:
    return TriggerContext(
        is_crit=is_crit,
        hit_damage=hit_damage,
        current_mana=current_mana,
        max_mana=max_mana,
    )


# ---------------------------------------------------------------------------
# TriggerContext
# ---------------------------------------------------------------------------

class TestTriggerContext:
    def test_mana_pct_full(self):
        ctx = TriggerContext(current_mana=100.0, max_mana=100.0)
        assert ctx.mana_pct == pytest.approx(100.0)

    def test_mana_pct_half(self):
        ctx = TriggerContext(current_mana=50.0, max_mana=100.0)
        assert ctx.mana_pct == pytest.approx(50.0)

    def test_mana_pct_empty(self):
        ctx = TriggerContext(current_mana=0.0, max_mana=200.0)
        assert ctx.mana_pct == pytest.approx(0.0)

    def test_mana_pct_fraction(self):
        ctx = TriggerContext(current_mana=25.0, max_mana=200.0)
        assert ctx.mana_pct == pytest.approx(12.5)

    def test_default_max_mana_nonzero(self):
        ctx = TriggerContext()
        assert ctx.mana_pct == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Event matching — ON_CRIT
# ---------------------------------------------------------------------------

class TestOnCritEventMatch:
    def test_on_crit_fires_on_crit(self):
        t = make_trigger(TriggerType.ON_CRIT)
        ctx = hit_ctx(is_crit=True)
        assert t in evaluate_triggers([t], ctx)

    def test_on_crit_does_not_fire_on_normal_hit(self):
        t = make_trigger(TriggerType.ON_CRIT)
        ctx = hit_ctx(is_crit=False)
        assert evaluate_triggers([t], ctx) == []


# ---------------------------------------------------------------------------
# Event matching — ON_HIT
# ---------------------------------------------------------------------------

class TestOnHitEventMatch:
    def test_on_hit_fires_on_normal_hit(self):
        t = make_trigger(TriggerType.ON_HIT)
        ctx = hit_ctx(is_crit=False)
        assert t in evaluate_triggers([t], ctx)

    def test_on_hit_fires_on_crit_too(self):
        t = make_trigger(TriggerType.ON_HIT)
        ctx = hit_ctx(is_crit=True)
        assert t in evaluate_triggers([t], ctx)


# ---------------------------------------------------------------------------
# Event matching — ON_CAST / ON_KILL
# ---------------------------------------------------------------------------

class TestOnCastOnKill:
    def test_on_cast_fires(self):
        t = make_trigger(TriggerType.ON_CAST, TriggerEffect.GAIN_BUFF)
        ctx = TriggerContext()
        assert t in evaluate_triggers([t], ctx)

    def test_on_kill_fires(self):
        t = make_trigger(TriggerType.ON_KILL, TriggerEffect.RESTORE_MANA)
        ctx = TriggerContext()
        assert t in evaluate_triggers([t], ctx)


# ---------------------------------------------------------------------------
# Event matching — ON_LOW_MANA
# ---------------------------------------------------------------------------

class TestOnLowManaEventMatch:
    def test_on_low_mana_fires_below_threshold(self):
        t = make_trigger(TriggerType.ON_LOW_MANA, mana_below_pct=30.0)
        ctx = hit_ctx(current_mana=20.0, max_mana=100.0)   # 20% < 30%
        assert t in evaluate_triggers([t], ctx)

    def test_on_low_mana_does_not_fire_at_threshold(self):
        t = make_trigger(TriggerType.ON_LOW_MANA, mana_below_pct=30.0)
        ctx = hit_ctx(current_mana=30.0, max_mana=100.0)   # 30% == 30%
        assert evaluate_triggers([t], ctx) == []

    def test_on_low_mana_does_not_fire_above_threshold(self):
        t = make_trigger(TriggerType.ON_LOW_MANA, mana_below_pct=30.0)
        ctx = hit_ctx(current_mana=50.0, max_mana=100.0)   # 50% > 30%
        assert evaluate_triggers([t], ctx) == []


# ---------------------------------------------------------------------------
# Condition guards — is_crit
# ---------------------------------------------------------------------------

class TestConditionIsCrit:
    def test_is_crit_guard_blocks_normal_hit(self):
        t = make_trigger(TriggerType.ON_HIT, is_crit=True)
        ctx = hit_ctx(is_crit=False)
        assert evaluate_triggers([t], ctx) == []

    def test_is_crit_guard_passes_on_crit(self):
        t = make_trigger(TriggerType.ON_HIT, is_crit=True)
        ctx = hit_ctx(is_crit=True)
        assert t in evaluate_triggers([t], ctx)

    def test_no_is_crit_guard_fires_on_normal_hit(self):
        t = make_trigger(TriggerType.ON_HIT, is_crit=False)
        ctx = hit_ctx(is_crit=False)
        assert t in evaluate_triggers([t], ctx)


# ---------------------------------------------------------------------------
# Condition guards — min_hit_damage
# ---------------------------------------------------------------------------

class TestConditionMinHitDamage:
    def test_hit_meets_minimum_fires(self):
        t = make_trigger(TriggerType.ON_HIT, min_hit_damage=50.0)
        ctx = hit_ctx(hit_damage=100.0)
        assert t in evaluate_triggers([t], ctx)

    def test_hit_exactly_at_minimum_fires(self):
        t = make_trigger(TriggerType.ON_HIT, min_hit_damage=100.0)
        ctx = hit_ctx(hit_damage=100.0)
        assert t in evaluate_triggers([t], ctx)

    def test_hit_below_minimum_blocked(self):
        t = make_trigger(TriggerType.ON_HIT, min_hit_damage=100.0)
        ctx = hit_ctx(hit_damage=99.9)
        assert evaluate_triggers([t], ctx) == []

    def test_zero_minimum_always_passes(self):
        t = make_trigger(TriggerType.ON_HIT, min_hit_damage=0.0)
        ctx = hit_ctx(hit_damage=0.0)
        assert t in evaluate_triggers([t], ctx)


# ---------------------------------------------------------------------------
# Condition guards — mana_below_pct
# ---------------------------------------------------------------------------

class TestConditionManaBelowPct:
    def test_mana_below_threshold_fires(self):
        t = make_trigger(TriggerType.ON_HIT, mana_below_pct=50.0)
        ctx = hit_ctx(current_mana=40.0, max_mana=100.0)  # 40% < 50%
        assert t in evaluate_triggers([t], ctx)

    def test_mana_at_threshold_blocked(self):
        t = make_trigger(TriggerType.ON_HIT, mana_below_pct=50.0)
        ctx = hit_ctx(current_mana=50.0, max_mana=100.0)  # 50% == 50%
        assert evaluate_triggers([t], ctx) == []

    def test_mana_above_threshold_blocked(self):
        t = make_trigger(TriggerType.ON_HIT, mana_below_pct=50.0)
        ctx = hit_ctx(current_mana=80.0, max_mana=100.0)  # 80% > 50%
        assert evaluate_triggers([t], ctx) == []

    def test_default_100_pct_never_blocks(self):
        # mana_below_pct=100 means "no restriction" — fires even at full mana
        t = make_trigger(TriggerType.ON_HIT, mana_below_pct=100.0)
        ctx = hit_ctx(current_mana=100.0, max_mana=100.0)
        assert t in evaluate_triggers([t], ctx)

    def test_mana_just_below_100_fires_with_default(self):
        t = make_trigger(TriggerType.ON_HIT, mana_below_pct=100.0)
        ctx = hit_ctx(current_mana=99.9, max_mana=100.0)
        assert t in evaluate_triggers([t], ctx)


# ---------------------------------------------------------------------------
# Chance roll
# ---------------------------------------------------------------------------

class TestChanceRoll:
    def test_100_pct_always_fires(self):
        t = make_trigger(TriggerType.ON_HIT, chance_pct=100.0)
        ctx = hit_ctx()
        assert t in evaluate_triggers([t], ctx, rng_roll=99.9)

    def test_roll_at_threshold_fires(self):
        t = make_trigger(TriggerType.ON_HIT, chance_pct=50.0)
        ctx = hit_ctx()
        assert t in evaluate_triggers([t], ctx, rng_roll=50.0)

    def test_roll_just_above_blocked(self):
        t = make_trigger(TriggerType.ON_HIT, chance_pct=50.0)
        ctx = hit_ctx()
        assert evaluate_triggers([t], ctx, rng_roll=50.1) == []

    def test_roll_zero_always_fires(self):
        t = make_trigger(TriggerType.ON_HIT, chance_pct=1.0)
        ctx = hit_ctx()
        assert t in evaluate_triggers([t], ctx, rng_roll=0.0)

    def test_no_rng_roll_treats_as_zero(self):
        # When rng_roll is None, implementation uses 0.0 — always fires
        t = make_trigger(TriggerType.ON_HIT, chance_pct=1.0)
        ctx = hit_ctx()
        assert t in evaluate_triggers([t], ctx, rng_roll=None)


# ---------------------------------------------------------------------------
# Multiple triggers
# ---------------------------------------------------------------------------

class TestMultipleTriggers:
    def test_all_matching_triggers_returned(self):
        t1 = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_BLEED)
        t2 = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_POISON)
        ctx = hit_ctx()
        result = evaluate_triggers([t1, t2], ctx)
        assert t1 in result
        assert t2 in result

    def test_only_matching_triggers_returned(self):
        t_hit  = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_BLEED)
        t_crit = make_trigger(TriggerType.ON_CRIT, TriggerEffect.APPLY_IGNITE)
        ctx = hit_ctx(is_crit=False)
        result = evaluate_triggers([t_hit, t_crit], ctx)
        assert t_hit in result
        assert t_crit not in result

    def test_empty_triggers_returns_empty(self):
        ctx = hit_ctx()
        assert evaluate_triggers([], ctx) == []

    def test_order_preserved(self):
        t1 = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_BLEED, source="a")
        t2 = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_POISON, source="b")
        t3 = make_trigger(TriggerType.ON_HIT, TriggerEffect.APPLY_SHOCK, source="c")
        ctx = hit_ctx()
        result = evaluate_triggers([t1, t2, t3], ctx)
        assert result == [t1, t2, t3]


# ---------------------------------------------------------------------------
# Combined guards
# ---------------------------------------------------------------------------

class TestCombinedGuards:
    def test_crit_hit_with_min_damage_both_pass(self):
        t = make_trigger(
            TriggerType.ON_HIT,
            is_crit=True,
            min_hit_damage=50.0,
            chance_pct=100.0,
        )
        ctx = hit_ctx(is_crit=True, hit_damage=100.0)
        assert t in evaluate_triggers([t], ctx)

    def test_crit_guard_fails_even_if_damage_passes(self):
        t = make_trigger(TriggerType.ON_HIT, is_crit=True, min_hit_damage=50.0)
        ctx = hit_ctx(is_crit=False, hit_damage=100.0)
        assert evaluate_triggers([t], ctx) == []

    def test_damage_guard_fails_even_if_crit_passes(self):
        t = make_trigger(TriggerType.ON_HIT, is_crit=True, min_hit_damage=200.0)
        ctx = hit_ctx(is_crit=True, hit_damage=100.0)
        assert evaluate_triggers([t], ctx) == []

    def test_all_guards_pass_with_chance_fail(self):
        t = make_trigger(
            TriggerType.ON_HIT,
            is_crit=True,
            min_hit_damage=50.0,
            chance_pct=30.0,
        )
        ctx = hit_ctx(is_crit=True, hit_damage=100.0)
        assert evaluate_triggers([t], ctx, rng_roll=50.0) == []
