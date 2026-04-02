"""Tests for enemy damage resolution bridge (Step 97)."""

import pytest

from app.domain.calculators.damage_type_router import DamageType
from encounter.enemy import EncounterEnemy
from encounter.enemy_damage_pipeline import EncounterHitResult, resolve_hit_against_enemy


def _enemy(health=1000.0, armor=0.0, shield=0.0, **res) -> EncounterEnemy:
    return EncounterEnemy(
        max_health=health, current_health=health,
        armor=armor, resistances=res,
        shield=shield, max_shield=shield,
    )


class TestBasicHit:
    def test_hit_reduces_enemy_health(self):
        e = _enemy(health=1000.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert result.hit_result.landed is True
        assert e.current_health == pytest.approx(900.0)
        assert result.health_dealt == pytest.approx(100.0)

    def test_miss_does_no_damage(self):
        e = _enemy(health=1000.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=1.0)
        assert result.hit_result.landed is False
        assert e.current_health == pytest.approx(1000.0)
        assert result.health_dealt == pytest.approx(0.0)

    def test_enemy_alive_after_partial_damage(self):
        e = _enemy(health=1000.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert result.enemy_alive is True


class TestArmorMitigation:
    def test_armor_reduces_physical_damage(self):
        e = _enemy(health=1000.0, armor=10000)
        result = resolve_hit_against_enemy(
            e, 100.0,
            damage_type=DamageType.PHYSICAL,
            rng_hit=0.0, rng_crit=99.0,
        )
        # High armor -> near-minimum (ARMOR_MITIGATION_CAP=75%) -> ~25 through
        assert result.health_dealt < 30.0

    def test_zero_armor_full_damage(self):
        e = _enemy(health=1000.0, armor=0)
        result = resolve_hit_against_enemy(
            e, 100.0,
            damage_type=DamageType.PHYSICAL,
            rng_hit=0.0, rng_crit=99.0,
        )
        assert result.health_dealt == pytest.approx(100.0)


class TestResistanceApplication:
    def test_fire_resistance_reduces_damage(self):
        e = _enemy(health=1000.0, fire=50.0)
        result = resolve_hit_against_enemy(
            e, 100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0, rng_crit=99.0,
        )
        # 50% resist -> 50 damage
        assert result.health_dealt == pytest.approx(50.0)

    def test_negative_resistance_amplifies_damage(self):
        e = _enemy(health=1000.0, fire=-100.0)
        result = resolve_hit_against_enemy(
            e, 100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0, rng_crit=99.0,
        )
        # -100% resist -> 200 damage
        assert result.health_dealt == pytest.approx(200.0)

    def test_penetration_reduces_effective_resistance(self):
        e = _enemy(health=1000.0, fire=75.0)
        result = resolve_hit_against_enemy(
            e, 100.0,
            damage_type=DamageType.FIRE,
            penetration=25.0,
            rng_hit=0.0, rng_crit=99.0,
        )
        # 75 - 25 = 50% effective -> 50 damage
        assert result.health_dealt == pytest.approx(50.0)


class TestShieldAbsorption:
    def test_shield_absorbs_before_health(self):
        e = _enemy(health=1000.0, shield=200.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert e.shield         == pytest.approx(100.0)
        assert e.current_health == pytest.approx(1000.0)

    def test_shield_overflow_hits_health(self):
        e = _enemy(health=1000.0, shield=50.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert e.shield         == pytest.approx(0.0)
        assert e.current_health == pytest.approx(950.0)

    def test_shield_synced_after_hit(self):
        e = _enemy(health=1000.0, shield=300.0)
        resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert e.shield == pytest.approx(200.0)


class TestOverkillAndDeath:
    def test_overkill_tracked_on_enemy(self):
        e = _enemy(health=50.0)
        result = resolve_hit_against_enemy(e, 100.0, rng_hit=0.0, rng_crit=99.0)
        assert result.enemy_alive is False
        assert result.overkill == pytest.approx(50.0)

    def test_enemy_dead_after_lethal_hit(self):
        e = _enemy(health=10.0)
        resolve_hit_against_enemy(e, 1000.0, rng_hit=0.0, rng_crit=99.0)
        assert e.is_alive is False


class TestCritHit:
    def test_crit_doubles_damage(self):
        e = _enemy(health=10000.0)
        result = resolve_hit_against_enemy(
            e, 100.0,
            crit_chance=1.0, crit_multiplier=2.0,
            rng_hit=0.0, rng_crit=0.0,
        )
        assert result.hit_result.is_crit is True
        assert result.health_dealt == pytest.approx(200.0)
