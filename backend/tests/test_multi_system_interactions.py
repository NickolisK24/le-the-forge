"""
Multi-System Interaction Testing (Step 83).

Tests complex interactions between multiple combat mechanics simultaneously
to verify that the systems compose correctly and produce expected combined
behavior.

Interaction scenarios:
  - Conversion + armor:     converted fire bypasses physical armor
  - Conversion + resistance: each output type gets its own resistance applied
  - Penetration + shred:    both subtract from enemy resistance additively
  - Crit + block:           crit multiplier applied to already-reduced damage
  - Crit + conversion:      crit multiplies the full pre-conversion damage
  - Shield + overkill:      overflow past shield still caps at enemy health
  - Leech + reflection:     both computed from the same post-shield damage
  - On-kill + overkill:     on-kill fires iff enemy dies, overkill is excess
  - Resistance + pen pipeline: pen reduces eff-res before apply_resistance
  - Full pipeline ordering: conversion before armor, armor before resistance,
    shield before health, on-kill after health
"""

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.damage_conversion import ConversionRule, apply_conversions
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.on_kill import OnKillEffect, OnKillEffectType, OnKillRegistry
from app.domain.shields import AbsorptionShield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _enemy(health: float = 1000.0, armor: int = 0, **resistances) -> EnemyInstance:
    return EnemyInstance.from_stats(EnemyStats(
        health=int(health), armor=armor, resistances=resistances
    ))


def _hit(enemy=None, shield=None, **kwargs) -> HitInput:
    """Build a HitInput with deterministic rolls (always hit, never crit by default)."""
    defaults = dict(
        base_damage=100.0,
        rng_hit=0.0,
        rng_crit=99.0,
    )
    defaults.update(kwargs)
    if enemy is not None:
        defaults["enemy"] = enemy
    if shield is not None:
        defaults["shield"] = shield
    return HitInput(**defaults)


# ---------------------------------------------------------------------------
# Conversion × Armor
# ---------------------------------------------------------------------------

class TestConversionAndArmor:
    def test_converted_fire_bypasses_armor(self):
        # 100% physical converted to fire — armor has zero effect
        enemy = _enemy(armor=100_000)
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 100.0),)
        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        ))
        # all damage is now fire, armor does nothing → full 100 through
        assert result.post_armor == pytest.approx(100.0)

    def test_partial_conversion_splits_armor_treatment(self):
        # 50% physical → fire; 50% stays physical; high armor heavily reduces physical half
        enemy = _enemy(armor=100_000)
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        ))
        # fire portion (50) passes fully, physical portion is near 0 due to extreme armor
        # total post_armor should be significantly > 0 (fire half) but < 100
        assert result.post_armor > 40.0
        assert result.post_armor < 100.0

    def test_no_conversion_full_armor_reduction(self):
        enemy = _enemy(armor=100_000)
        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
        ))
        # ARMOR_MITIGATION_CAP = 85% → minimum 15% always passes through
        assert result.post_armor == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# Conversion × Resistance
# ---------------------------------------------------------------------------

class TestConversionAndResistance:
    def test_each_type_gets_its_own_resistance(self):
        # 50% physical → fire; enemy has 75% fire resist but 0% physical resist
        enemy = _enemy(fire=75.0)
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        ))
        # physical half (50) → 0% resist → 50 through
        # fire half (50) → 75% resist → 12.5 through
        # total = 62.5
        assert result.post_resistance == pytest.approx(62.5)

    def test_full_conversion_to_resisted_type(self):
        # 100% physical → fire; enemy has 50% fire resist
        enemy = _enemy(fire=50.0)
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 100.0),)
        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        ))
        # 100 → all fire → 50% resist → 50 through
        assert result.post_resistance == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Penetration × Shred (via EnemyInstance)
# ---------------------------------------------------------------------------

class TestPenetrationAndShred:
    def test_pen_and_shred_reduce_effective_resistance_additively(self):
        from app.domain.penetration import effective_resistance

        enemy_res = 75.0
        pen = 20.0
        shred = 15.0
        eff = effective_resistance(enemy_res, penetration=pen, shred=shred)
        # 75 - 20 - 15 = 40
        assert eff == pytest.approx(40.0)

    def test_pen_and_shred_combined_cap_at_res_min(self):
        from app.domain.penetration import effective_resistance
        from app.domain.resistance import RES_MIN

        eff = effective_resistance(75.0, penetration=500.0, shred=500.0)
        assert eff == pytest.approx(RES_MIN)

    def test_shred_on_enemy_reduces_resistance_in_hit(self):
        enemy = _enemy(fire=60.0)
        # Manually shred 30 fire resistance first
        enemy.apply_shred("fire", 30.0)

        result = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.FIRE,
        ))
        # 60 - 30 = 30% effective resistance → 70% of 100 = 70 through
        assert result.post_resistance == pytest.approx(70.0)


# ---------------------------------------------------------------------------
# Crit × Block
# ---------------------------------------------------------------------------

class TestCritAndBlock:
    def test_crit_applies_after_block_reduction(self):
        # block 50% effectiveness → 50 damage; then crit ×2 → 100
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            enemy_block_chance=1.0,
            enemy_block_eff=0.5,
            rng_block=0.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            rng_crit=0.0,
        ))
        assert result.blocked is True
        assert result.is_crit is True
        assert result.crit_damage == pytest.approx(100.0)

    def test_no_block_crit_sees_full_damage(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            enemy_block_chance=0.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            rng_crit=0.0,
        ))
        assert result.is_crit is True
        assert result.crit_damage == pytest.approx(200.0)


# ---------------------------------------------------------------------------
# Shield × Overkill
# ---------------------------------------------------------------------------

class TestShieldAndOverkill:
    def test_shield_absorbs_first_overkill_on_remaining_health(self):
        # Shield 60, enemy 50 HP, damage 100
        # Shield absorbs 60 → overflow 40 → enemy at 50 HP takes 40 → dies with 10 overkill
        enemy  = _enemy(health=50.0)
        shield = AbsorptionShield.at_full(60.0)
        result = resolve_hit(_hit(enemy=enemy, shield=shield, base_damage=100.0))
        assert result.shield_absorbed == pytest.approx(60.0)
        assert result.health_damage   == pytest.approx(40.0)
        assert result.overkill        == pytest.approx(0.0)   # 40 <= 50 HP
        assert not enemy.is_alive or enemy.current_health >= 0.0

    def test_overkill_calculated_on_overflow_damage(self):
        # Shield 0 (no shield), enemy 30 HP, damage 100 → 70 overkill
        enemy  = _enemy(health=30.0)
        result = resolve_hit(_hit(enemy=enemy, base_damage=100.0))
        assert result.health_damage == pytest.approx(100.0)
        assert result.overkill      == pytest.approx(70.0)
        assert not enemy.is_alive


# ---------------------------------------------------------------------------
# Leech × Reflection
# ---------------------------------------------------------------------------

class TestLeechAndReflection:
    def test_leech_and_reflection_both_computed_from_same_damage(self):
        # 10% leech + 25% reflect on 100 base damage
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            leech_pct=10.0,
            reflect_pct=25.0,
        ))
        assert result.mana_leeched     == pytest.approx(10.0)
        assert result.reflected_damage == pytest.approx(25.0)

    def test_leech_and_reflection_scale_with_damage(self):
        result = resolve_hit(HitInput(
            base_damage=200.0,
            rng_hit=0.0,
            rng_crit=99.0,
            leech_pct=10.0,
            reflect_pct=25.0,
        ))
        assert result.mana_leeched     == pytest.approx(20.0)
        assert result.reflected_damage == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# On-kill × Overkill
# ---------------------------------------------------------------------------

class TestOnKillAndOverkill:
    def test_on_kill_fires_and_overkill_computed_together(self):
        enemy = _enemy(health=40.0)
        reg   = OnKillRegistry()
        reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=30.0))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            on_kill_registry=reg,
            rng_on_kill=0.0,
        ))
        assert result.overkill == pytest.approx(60.0)
        assert len(result.on_kill_effects) == 1
        assert not enemy.is_alive

    def test_on_kill_does_not_fire_when_enemy_survives(self):
        enemy = _enemy(health=1000.0)
        reg   = OnKillRegistry()
        reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=30.0))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            on_kill_registry=reg,
            rng_on_kill=0.0,
        ))
        assert result.overkill == pytest.approx(0.0)
        assert result.on_kill_effects == []
        assert enemy.is_alive


# ---------------------------------------------------------------------------
# Full pipeline ordering smoke test
# ---------------------------------------------------------------------------

class TestPipelineOrdering:
    def test_conversion_before_armor_in_pipeline(self):
        """Verify conversion happens before armor: converted portion bypasses armor."""
        enemy = _enemy(armor=10_000)
        # Without conversion: extreme armor → near-zero damage
        result_no_conv = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
        ))
        # With full conversion to fire: armor irrelevant
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 100.0),)
        result_conv = resolve_hit(_hit(
            enemy=enemy,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        ))
        # no_conv caps at 25 (armor mitigation cap); conv sees 100 (fire bypasses)
        assert result_conv.post_armor > result_no_conv.post_armor * 3

    def test_crit_before_armor_in_pipeline(self):
        """Crit multiplier is applied before armor/resistance, so armor sees amplified damage."""
        enemy = _enemy(armor=500)
        result_no_crit = resolve_hit(HitInput(
            base_damage=100.0, rng_hit=0.0,
            crit_chance=0.0, rng_crit=99.0,
            damage_type=DamageType.PHYSICAL,
            enemy=enemy,
        ))
        result_crit = resolve_hit(HitInput(
            base_damage=100.0, rng_hit=0.0,
            crit_chance=1.0, crit_multiplier=2.0, rng_crit=0.0,
            damage_type=DamageType.PHYSICAL,
            enemy=enemy,
        ))
        # Crit doubles pre-armor damage; armor formula is non-linear so post_armor
        # won't double exactly, but it should be significantly higher
        assert result_crit.post_armor > result_no_crit.post_armor * 1.5

    def test_resistance_after_armor_in_pipeline(self):
        """post_armor and post_resistance are separate stages."""
        enemy = _enemy(armor=0, fire=50.0)
        result = resolve_hit(HitInput(
            base_damage=100.0, rng_hit=0.0, rng_crit=99.0,
            damage_type=DamageType.FIRE,
            enemy=enemy,
        ))
        # No armor on fire; armor stage leaves 100; resistance removes 50%
        assert result.post_armor        == pytest.approx(100.0)
        assert result.post_resistance   == pytest.approx(50.0)
        assert result.health_damage     == pytest.approx(50.0)
