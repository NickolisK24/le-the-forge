"""
Tests for Status Effect Interaction System (Step 7).

Validates:
  - evaluate_status_interactions returns correct results per interaction rule
  - Shock increases all damage (target=None)
  - Frostbite increases cold damage (target=FROSTBITE)
  - Ignite+Shock synergy adds multiplicative bonus
  - apply_interaction_multiplier combines additive and multiplicative bonuses
"""

import pytest
from app.domain.ailments import AilmentType, AilmentInstance, apply_ailment
from app.domain.status_interactions import (
    SHOCK_DAMAGE_BONUS_PER_STACK,
    FROSTBITE_COLD_DAMAGE_BONUS,
    IGNITE_SHOCK_MULTIPLIER_BONUS,
    InteractionResult,
    evaluate_status_interactions,
    apply_interaction_multiplier,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inst(ailment_type: AilmentType, stack_count: int = 1) -> AilmentInstance:
    return AilmentInstance(
        ailment_type=ailment_type,
        damage_per_tick=10.0,
        duration=5.0,
        stack_count=stack_count,
    )


# ---------------------------------------------------------------------------
# InteractionResult
# ---------------------------------------------------------------------------

class TestInteractionResult:
    def test_is_frozen(self):
        r = InteractionResult(
            source=AilmentType.SHOCK,
            target=None,
            bonus_percent=20.0,
            multiplier=1.0,
            description="test",
        )
        with pytest.raises((AttributeError, TypeError)):
            r.bonus_percent = 99.0  # type: ignore[misc]

    def test_target_can_be_none(self):
        r = InteractionResult(
            source=AilmentType.SHOCK,
            target=None,
            bonus_percent=20.0,
            multiplier=1.0,
            description="",
        )
        assert r.target is None


# ---------------------------------------------------------------------------
# evaluate_status_interactions — no interactions
# ---------------------------------------------------------------------------

class TestEvaluateNoInteraction:
    def test_empty_active_returns_empty(self):
        assert evaluate_status_interactions([]) == []

    def test_bleed_only_no_interactions(self):
        active = [_inst(AilmentType.BLEED)]
        assert evaluate_status_interactions(active) == []

    def test_poison_only_no_interactions(self):
        active = [_inst(AilmentType.POISON)]
        assert evaluate_status_interactions(active) == []

    def test_ignite_only_no_interaction(self):
        # Ignite alone does not trigger synergy (needs shock too)
        active = [_inst(AilmentType.IGNITE)]
        results = evaluate_status_interactions(active)
        assert all(r.source is not AilmentType.SHOCK for r in results)


# ---------------------------------------------------------------------------
# evaluate_status_interactions — shock
# ---------------------------------------------------------------------------

class TestShockInteraction:
    def test_one_shock_stack(self):
        active = [_inst(AilmentType.SHOCK, stack_count=1)]
        results = evaluate_status_interactions(active)
        shock_results = [r for r in results if r.source is AilmentType.SHOCK and r.target is None]
        assert len(shock_results) == 1
        assert shock_results[0].bonus_percent == pytest.approx(SHOCK_DAMAGE_BONUS_PER_STACK)

    def test_multiple_shock_stacks_scale_linearly(self):
        active = [_inst(AilmentType.SHOCK, stack_count=3)]
        results = evaluate_status_interactions(active)
        shock_results = [r for r in results if r.source is AilmentType.SHOCK and r.target is None]
        assert shock_results[0].bonus_percent == pytest.approx(3 * SHOCK_DAMAGE_BONUS_PER_STACK)

    def test_shock_target_is_none(self):
        active = [_inst(AilmentType.SHOCK)]
        results = evaluate_status_interactions(active)
        shock_results = [r for r in results if r.source is AilmentType.SHOCK and r.target is None]
        assert shock_results[0].target is None

    def test_shock_multiplier_is_one(self):
        active = [_inst(AilmentType.SHOCK)]
        results = evaluate_status_interactions(active)
        shock_results = [r for r in results if r.source is AilmentType.SHOCK and r.target is None]
        assert shock_results[0].multiplier == pytest.approx(1.0)

    def test_shock_description_mentions_stacks(self):
        active = [_inst(AilmentType.SHOCK, stack_count=2)]
        results = evaluate_status_interactions(active)
        shock_results = [r for r in results if r.source is AilmentType.SHOCK and r.target is None]
        assert "2" in shock_results[0].description


# ---------------------------------------------------------------------------
# evaluate_status_interactions — frostbite
# ---------------------------------------------------------------------------

class TestFrostbiteInteraction:
    def test_frostbite_present(self):
        active = [_inst(AilmentType.FROSTBITE)]
        results = evaluate_status_interactions(active)
        frost_results = [r for r in results if r.source is AilmentType.FROSTBITE]
        assert len(frost_results) == 1

    def test_frostbite_target_is_frostbite(self):
        active = [_inst(AilmentType.FROSTBITE)]
        results = evaluate_status_interactions(active)
        frost_results = [r for r in results if r.source is AilmentType.FROSTBITE]
        assert frost_results[0].target is AilmentType.FROSTBITE

    def test_frostbite_bonus_per_stack(self):
        active = [_inst(AilmentType.FROSTBITE, stack_count=2)]
        results = evaluate_status_interactions(active)
        frost_results = [r for r in results if r.source is AilmentType.FROSTBITE]
        assert frost_results[0].bonus_percent == pytest.approx(2 * FROSTBITE_COLD_DAMAGE_BONUS)


# ---------------------------------------------------------------------------
# evaluate_status_interactions — ignite + shock synergy
# ---------------------------------------------------------------------------

class TestIgniteShockSynergy:
    def test_synergy_requires_both(self):
        # Shock alone: no ignite synergy
        active = [_inst(AilmentType.SHOCK)]
        results = evaluate_status_interactions(active)
        synergy = [r for r in results if r.target is AilmentType.IGNITE]
        assert len(synergy) == 0

    def test_synergy_triggers_with_both(self):
        active = [_inst(AilmentType.SHOCK), _inst(AilmentType.IGNITE)]
        results = evaluate_status_interactions(active)
        synergy = [r for r in results if r.target is AilmentType.IGNITE]
        assert len(synergy) == 1

    def test_synergy_multiplier_one_shock_stack(self):
        active = [_inst(AilmentType.SHOCK, stack_count=1), _inst(AilmentType.IGNITE)]
        results = evaluate_status_interactions(active)
        synergy = [r for r in results if r.target is AilmentType.IGNITE]
        expected = 1.0 + 1 * IGNITE_SHOCK_MULTIPLIER_BONUS
        assert synergy[0].multiplier == pytest.approx(expected)

    def test_synergy_multiplier_scales_with_shock_stacks(self):
        active = [_inst(AilmentType.SHOCK, stack_count=3), _inst(AilmentType.IGNITE)]
        results = evaluate_status_interactions(active)
        synergy = [r for r in results if r.target is AilmentType.IGNITE]
        expected = 1.0 + 3 * IGNITE_SHOCK_MULTIPLIER_BONUS
        assert synergy[0].multiplier == pytest.approx(expected)


# ---------------------------------------------------------------------------
# apply_interaction_multiplier
# ---------------------------------------------------------------------------

class TestApplyInteractionMultiplier:
    def test_no_interactions_returns_base(self):
        active = [_inst(AilmentType.BLEED)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.BLEED)
        assert result == pytest.approx(100.0)

    def test_shock_boosts_bleed(self):
        # 1 shock = SHOCK_DAMAGE_BONUS_PER_STACK% additive
        active = [_inst(AilmentType.SHOCK, stack_count=1), _inst(AilmentType.BLEED)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.BLEED)
        expected = 100.0 * (1.0 + SHOCK_DAMAGE_BONUS_PER_STACK / 100.0)
        assert result == pytest.approx(expected)

    def test_shock_boosts_ignite(self):
        active = [_inst(AilmentType.SHOCK, stack_count=1), _inst(AilmentType.IGNITE)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.IGNITE)
        # Shock additive bonus (target=None) + ignite synergy multiplier
        additive = 1.0 + SHOCK_DAMAGE_BONUS_PER_STACK / 100.0
        mult = 1.0 + IGNITE_SHOCK_MULTIPLIER_BONUS
        expected = 100.0 * additive * mult
        assert result == pytest.approx(expected)

    def test_frostbite_boosts_frostbite_damage(self):
        active = [_inst(AilmentType.FROSTBITE, stack_count=1)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.FROSTBITE)
        expected = 100.0 * (1.0 + FROSTBITE_COLD_DAMAGE_BONUS / 100.0)
        assert result == pytest.approx(expected)

    def test_frostbite_does_not_boost_bleed(self):
        active = [_inst(AilmentType.FROSTBITE)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.BLEED)
        assert result == pytest.approx(100.0)

    def test_empty_active_returns_base(self):
        result = apply_interaction_multiplier(200.0, [], AilmentType.IGNITE)
        assert result == pytest.approx(200.0)

    def test_zero_base_damage(self):
        active = [_inst(AilmentType.SHOCK, stack_count=3)]
        result = apply_interaction_multiplier(0.0, active, AilmentType.BLEED)
        assert result == pytest.approx(0.0)

    def test_multiple_shock_stacks_compound(self):
        active = [_inst(AilmentType.SHOCK, stack_count=2)]
        result = apply_interaction_multiplier(100.0, active, AilmentType.BLEED)
        expected = 100.0 * (1.0 + 2 * SHOCK_DAMAGE_BONUS_PER_STACK / 100.0)
        assert result == pytest.approx(expected)
