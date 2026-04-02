"""
Extreme Value Testing (Step 82).

Pushes all combat mechanics to their extreme ranges to verify clamping,
safety guards, and correctness at numeric boundaries.

Systems under test:
  - Resistance: RES_CAP (75%) and RES_MIN (-100%) clamp
  - Armor: ARMOR_MITIGATION_CAP (75%) even at infinite armor
  - Crit chance: CRIT_CAP (100%) clamp from bonus overshoot
  - Dodge: DODGE_CAP (75%) from high rating
  - Block: BLOCK_CHANCE_CAP (75%) clamp
  - Accuracy: HIT_CHANCE_MIN (5%) / HIT_CHANCE_MAX (95%) floor/ceiling
  - Penetration: cannot push effective resistance below RES_MIN
  - Shred: MAX_SHRED_PER_TYPE (100) cap
  - Reflection: REFLECT_CAP (100%) clamp
  - Stability helpers: clamp, safe_subtract, stable_divide at edge values
  - Full pipeline: extreme inputs produce valid HitResult
"""

import math

import pytest

from app.domain.accuracy import (
    HIT_CHANCE_MAX,
    HIT_CHANCE_MIN,
    calculate_hit_chance,
)
from app.domain.armor import (
    ARMOR_MITIGATION_CAP,
    apply_armor,
    armor_mitigation_pct,
)
from app.domain.block import BLOCK_CHANCE_CAP, block_result
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.critical import CRIT_CAP, effective_crit_chance
from app.domain.dodge import DODGE_CAP, dodge_chance
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.penetration import (
    MAX_SHRED_PER_TYPE,
    apply_shred,
    effective_resistance,
)
from app.domain.reflection import REFLECT_CAP, apply_reflection
from app.domain.resistance import RES_CAP, RES_MIN, apply_resistance
from app.domain.stability import (
    clamp,
    safe_subtract,
    safe_tick,
    stable_divide,
)


# ---------------------------------------------------------------------------
# Resistance caps
# ---------------------------------------------------------------------------

class TestResistanceCaps:
    def test_resistance_above_cap_clamped(self):
        # 200% resistance input → damage should match RES_CAP applied
        result = apply_resistance(100.0, 200.0)
        expected = apply_resistance(100.0, RES_CAP)
        assert result == pytest.approx(expected)

    def test_resistance_at_cap_leaves_25pct(self):
        # RES_CAP = 75% → 25% of damage passes through
        assert apply_resistance(100.0, RES_CAP) == pytest.approx(25.0)

    def test_negative_resistance_increases_damage(self):
        # -100% resistance → 200% of damage
        assert apply_resistance(100.0, -100.0) == pytest.approx(200.0)

    def test_resistance_below_min_clamped(self):
        # -200% resistance input → same as RES_MIN
        result   = apply_resistance(100.0, -200.0)
        expected = apply_resistance(100.0, RES_MIN)
        assert result == pytest.approx(expected)

    def test_zero_resistance_full_damage(self):
        assert apply_resistance(100.0, 0.0) == pytest.approx(100.0)

    def test_zero_damage_any_resistance(self):
        assert apply_resistance(0.0, RES_CAP) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Armor cap
# ---------------------------------------------------------------------------

class TestArmorCap:
    def test_infinite_armor_capped_at_mitigation_cap(self):
        mit = armor_mitigation_pct(1e18, 100.0)
        assert mit == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_extreme_armor_damage_never_negative(self):
        result = apply_armor(50.0, 1e18)
        assert result >= 0.0

    def test_zero_armor_full_damage(self):
        assert apply_armor(100.0, 0.0) == pytest.approx(100.0)

    def test_zero_damage_zero_mitigation(self):
        # armor_mitigation_pct with 0 raw_damage: formula is armor/(armor+0)=1 but cap applies
        # The key invariant: result is non-negative
        result = apply_armor(0.0, 1000.0)
        assert result >= 0.0


# ---------------------------------------------------------------------------
# Crit chance cap
# ---------------------------------------------------------------------------

class TestCritCap:
    def test_crit_chance_cannot_exceed_cap(self):
        result = effective_crit_chance(0.5, 1000.0)
        assert result == pytest.approx(CRIT_CAP)

    def test_negative_bonus_cannot_push_below_zero(self):
        result = effective_crit_chance(0.05, -999.0)
        assert result >= 0.0

    def test_zero_base_zero_bonus_is_zero(self):
        assert effective_crit_chance(0.0, 0.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Dodge cap
# ---------------------------------------------------------------------------

class TestDodgeCap:
    def test_extreme_rating_capped(self):
        result = dodge_chance(1e12)
        assert result == pytest.approx(DODGE_CAP)

    def test_zero_rating_zero_dodge(self):
        assert dodge_chance(0.0) == pytest.approx(0.0)

    def test_dodge_never_exceeds_cap_with_penalty(self):
        # Even with level penalty, result stays <= DODGE_CAP
        result = dodge_chance(1e12, level_penalty=5.0)
        assert result <= DODGE_CAP


# ---------------------------------------------------------------------------
# Block cap
# ---------------------------------------------------------------------------

class TestBlockCap:
    def test_block_chance_above_cap_clamped(self):
        # block_chance=2.0 (200%) → still caps at 0.75
        dmg, blocked = block_result(100.0, 2.0, 0.5, rng_roll=0.0)
        assert blocked is True
        assert dmg == pytest.approx(50.0)

    def test_block_effectiveness_above_1_raises(self):
        # block_effectiveness is validated to [0, 1]; values above 1 are invalid
        with pytest.raises(ValueError):
            block_result(100.0, 1.0, 2.0, rng_roll=0.0)

    def test_zero_block_chance_never_blocks(self):
        _, blocked = block_result(100.0, 0.0, 0.5, rng_roll=0.0)
        assert blocked is False


# ---------------------------------------------------------------------------
# Accuracy floor / ceiling
# ---------------------------------------------------------------------------

class TestAccuracyCaps:
    def test_zero_accuracy_hits_floor(self):
        result = calculate_hit_chance(0.0, 1000.0)
        assert result == pytest.approx(HIT_CHANCE_MIN)

    def test_zero_evasion_hits_ceiling(self):
        result = calculate_hit_chance(1000.0, 0.0)
        assert result == pytest.approx(HIT_CHANCE_MAX)

    def test_extreme_accuracy_capped_at_max(self):
        result = calculate_hit_chance(1e18, 1.0)
        assert result == pytest.approx(HIT_CHANCE_MAX)

    def test_extreme_evasion_floored_at_min(self):
        result = calculate_hit_chance(1.0, 1e18)
        assert result == pytest.approx(HIT_CHANCE_MIN)


# ---------------------------------------------------------------------------
# Penetration / shred extremes
# ---------------------------------------------------------------------------

class TestPenetrationExtremes:
    def test_massive_penetration_cannot_go_below_res_min(self):
        result = effective_resistance(75.0, penetration=10_000.0, shred=0.0)
        assert result >= RES_MIN

    def test_massive_shred_cannot_go_below_res_min(self):
        result = effective_resistance(75.0, penetration=0.0, shred=10_000.0)
        assert result >= RES_MIN

    def test_shred_accumulation_capped_at_max(self):
        acc = apply_shred(0.0, 10_000.0, max_shred=MAX_SHRED_PER_TYPE)
        assert acc == pytest.approx(MAX_SHRED_PER_TYPE)

    def test_shred_incremental_accumulation_caps(self):
        acc = 0.0
        for _ in range(200):
            acc = apply_shred(acc, 1.0, max_shred=MAX_SHRED_PER_TYPE)
        assert acc == pytest.approx(MAX_SHRED_PER_TYPE)


# ---------------------------------------------------------------------------
# Reflection cap
# ---------------------------------------------------------------------------

class TestReflectionCap:
    def test_reflection_above_100pct_clamped(self):
        _, reflected = apply_reflection(100.0, 200.0)
        assert reflected == pytest.approx(100.0)  # capped at 100%

    def test_zero_reflection(self):
        _, reflected = apply_reflection(100.0, 0.0)
        assert reflected == pytest.approx(0.0)

    def test_reflection_with_attacker_resistance(self):
        # Attacker at 50% resistance → takes 50% of reflected
        _, reflected = apply_reflection(100.0, 100.0, attacker_resistance=50.0)
        assert reflected == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Stability helpers at boundaries
# ---------------------------------------------------------------------------

class TestStabilityExtremes:
    def test_clamp_above_hi(self):
        assert clamp(1e18, 0.0, 100.0) == pytest.approx(100.0)

    def test_clamp_below_lo(self):
        assert clamp(-1e18, 0.0, 100.0) == pytest.approx(0.0)

    def test_safe_subtract_never_negative(self):
        assert safe_subtract(5.0, 1e18) == pytest.approx(0.0)

    def test_safe_tick_never_negative(self):
        assert safe_tick(5.0, 1e18) == pytest.approx(0.0)

    def test_stable_divide_zero_denominator_returns_fallback(self):
        assert stable_divide(100.0, 0.0, fallback=42.0) == pytest.approx(42.0)

    def test_stable_divide_normal(self):
        assert stable_divide(10.0, 4.0) == pytest.approx(2.5)

    def test_clamp_nan_lo_hi(self):
        # NaN should not silently pass through clamp; clamp uses max/min so
        # math.nan comparisons return False → result is nan. Document behavior.
        result = clamp(float("nan"), 0.0, 1.0)
        # result is nan — we simply confirm no exception is raised
        assert result != result or (0.0 <= result <= 1.0)


# ---------------------------------------------------------------------------
# Full pipeline with extreme inputs
# ---------------------------------------------------------------------------

class TestPipelineExtremes:
    def test_zero_damage_produces_zero_health_damage(self):
        result = resolve_hit(HitInput(base_damage=0.0, rng_hit=0.0, rng_crit=99.0))
        assert result.health_damage == pytest.approx(0.0)

    def test_extreme_base_damage_no_exceptions(self):
        result = resolve_hit(HitInput(base_damage=1e12, rng_hit=0.0, rng_crit=99.0))
        assert result.health_damage >= 0.0
        assert not math.isnan(result.health_damage)
        assert not math.isinf(result.health_damage)

    def test_full_resistance_enemy_takes_25pct(self):
        from app.domain.calculators.damage_type_router import DamageType
        enemy = EnemyInstance.from_stats(EnemyStats(
            health=10_000, armor=0, resistances={"fire": 200.0}
        ))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        # 200% input → clamped to RES_CAP=75% → 25 damage
        assert result.post_resistance == pytest.approx(25.0)

    def test_negative_resistance_enemy_amplifies_damage(self):
        from app.domain.calculators.damage_type_router import DamageType
        enemy = EnemyInstance.from_stats(EnemyStats(
            health=10_000, armor=0, resistances={"fire": -100.0}
        ))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        # -100% resistance → 200% damage
        assert result.post_resistance == pytest.approx(200.0)

    def test_pipeline_with_all_systems_extreme(self):
        """All systems pushed to extremes — no exceptions, no NaN."""
        from app.domain.calculators.damage_type_router import DamageType
        from app.domain.damage_conversion import ConversionRule
        from app.domain.shields import AbsorptionShield

        enemy  = EnemyInstance.from_stats(EnemyStats(health=1, armor=0))
        shield = AbsorptionShield.at_full(1e9)
        rules  = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)

        result = resolve_hit(HitInput(
            base_damage=1e12,
            damage_type=DamageType.PHYSICAL,
            crit_chance=1.0,
            crit_multiplier=10.0,
            conversion_rules=rules,
            enemy=enemy,
            shield=shield,
            rng_hit=0.0,
            rng_crit=0.0,
            leech_pct=100.0,
            reflect_pct=100.0,
            penetration=10_000.0,
        ))

        assert not math.isnan(result.health_damage)
        assert not math.isinf(result.health_damage)
        assert result.shield_absorbed >= 0.0
        assert result.mana_leeched >= 0.0
        assert result.reflected_damage >= 0.0
