"""
Tests for Final Combat Validation Suite (Step 80).

Validates the full hit pipeline: accuracy → dodge → block → crit →
conversion → armor → resistance → shield → health → overkill → leech
→ reflection → on-kill.
"""

import pytest
from app.domain.combat_validation import HitInput, HitResult, resolve_hit
from app.domain.calculators.damage_type_router import DamageType
from app.domain.damage_conversion import ConversionRule
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.domain.on_kill import OnKillEffect, OnKillEffectType, OnKillRegistry
from app.domain.shields import AbsorptionShield


def dummy_enemy(health: float = 1000.0) -> EnemyInstance:
    return EnemyInstance.from_stats(EnemyStats(health=int(health), armor=0))


# ---------------------------------------------------------------------------
# Miss / dodge / block early exits
# ---------------------------------------------------------------------------

class TestEarlyExits:
    def test_miss_returns_no_damage(self):
        # rng_hit=0.99 but hit chance always < 1 → miss if rng >= hit_chance
        result = resolve_hit(HitInput(base_damage=100.0, rng_hit=1.0))
        assert result.landed is False
        assert result.health_damage == pytest.approx(0.0)

    def test_dodge_returns_no_damage(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,       # always hits
            enemy_dodge_chance=1.0,
            rng_dodge=0.0,     # always dodges
        ))
        assert result.dodged is True
        assert result.health_damage == pytest.approx(0.0)

    def test_block_reduces_damage(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            enemy_block_chance=1.0,
            enemy_block_eff=0.5,
            rng_block=0.0,
            rng_crit=99.0,
        ))
        assert result.blocked is True
        # 50% block effectiveness → half damage through before other calcs
        assert result.crit_damage == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Crit
# ---------------------------------------------------------------------------

class TestCrit:
    def test_crit_doubles_damage(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            rng_hit=0.0,
            rng_crit=0.0,
        ))
        assert result.is_crit is True
        assert result.crit_damage == pytest.approx(200.0)

    def test_no_crit_damage_unchanged(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            crit_chance=0.0,
            rng_hit=0.0,
        ))
        assert result.is_crit is False
        assert result.crit_damage == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Resistance
# ---------------------------------------------------------------------------

class TestResistance:
    def test_50pct_fire_res_halves_damage(self):
        enemy = EnemyInstance.from_stats(EnemyStats(
            health=1000, armor=0,
            resistances={"fire": 50.0},
        ))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.post_resistance == pytest.approx(50.0)

    def test_zero_resistance_full_damage(self):
        enemy = dummy_enemy()
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.post_resistance == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Armor
# ---------------------------------------------------------------------------

class TestArmor:
    def test_armor_reduces_physical_damage(self):
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=1000))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.PHYSICAL,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.post_armor < 100.0

    def test_armor_does_not_affect_fire(self):
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=10000))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.post_armor == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Shield
# ---------------------------------------------------------------------------

class TestShield:
    def test_shield_absorbs_before_health(self):
        enemy  = dummy_enemy(1000.0)
        shield = AbsorptionShield.at_full(200.0)
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            shield=shield,
        ))
        assert result.shield_absorbed == pytest.approx(100.0)
        assert result.health_damage   == pytest.approx(0.0)
        assert enemy.current_health   == pytest.approx(1000.0)

    def test_shield_overflow_hits_health(self):
        enemy  = dummy_enemy(1000.0)
        shield = AbsorptionShield.at_full(50.0)
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            shield=shield,
        ))
        assert result.shield_absorbed == pytest.approx(50.0)
        assert result.health_damage   == pytest.approx(50.0)
        assert enemy.current_health   == pytest.approx(950.0)


# ---------------------------------------------------------------------------
# Overkill
# ---------------------------------------------------------------------------

class TestOverkill:
    def test_overkill_computed_correctly(self):
        enemy = dummy_enemy(50.0)
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.overkill == pytest.approx(50.0)
        assert not enemy.is_alive


# ---------------------------------------------------------------------------
# Leech
# ---------------------------------------------------------------------------

class TestLeech:
    def test_leech_pct_recorded(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            leech_pct=10.0,
        ))
        assert result.mana_leeched == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Reflection
# ---------------------------------------------------------------------------

class TestReflection:
    def test_reflected_damage_recorded(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            reflect_pct=25.0,
        ))
        assert result.reflected_damage == pytest.approx(25.0)


# ---------------------------------------------------------------------------
# On-kill
# ---------------------------------------------------------------------------

class TestOnKill:
    def test_on_kill_fires_when_enemy_dies(self):
        enemy = dummy_enemy(50.0)
        reg   = OnKillRegistry()
        reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=20.0))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            on_kill_registry=reg,
            rng_on_kill=0.0,
        ))
        assert len(result.on_kill_effects) == 1
        assert not enemy.is_alive

    def test_on_kill_does_not_fire_when_alive(self):
        enemy = dummy_enemy(1000.0)
        reg   = OnKillRegistry()
        reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=20.0))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
            on_kill_registry=reg,
            rng_on_kill=0.0,
        ))
        assert result.on_kill_effects == []
        assert enemy.is_alive


# ---------------------------------------------------------------------------
# Damage conversion integration
# ---------------------------------------------------------------------------

class TestConversionIntegration:
    def test_physical_converted_to_fire_bypasses_armor(self):
        # High armor enemy: physical with conversion → some goes to fire (no armor)
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=10000))
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        # With extreme armor: physical portion is near 0, fire portion = 50
        assert result.post_armor > 40.0   # at least the fire portion survived
