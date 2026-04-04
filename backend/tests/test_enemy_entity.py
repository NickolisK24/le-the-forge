"""Tests for encounter enemy entity (Step 96)."""

import pytest

from app.domain.enemy import EnemyArchetype, EnemyStats
from encounter.enemy import EncounterEnemy


def _enemy(health=100.0, armor=0.0, shield=0.0, **res) -> EncounterEnemy:
    return EncounterEnemy(
        max_health=health, current_health=health,
        armor=armor, resistances=res,
        shield=shield, max_shield=shield,
    )


class TestConstruction:
    def test_basic(self):
        e = _enemy(health=500.0, armor=100.0)
        assert e.max_health     == pytest.approx(500.0)
        assert e.current_health == pytest.approx(500.0)
        assert e.armor          == pytest.approx(100.0)

    def test_zero_health_raises(self):
        with pytest.raises(ValueError):
            _enemy(health=0.0)

    def test_negative_health_raises(self):
        with pytest.raises(ValueError):
            _enemy(health=-1.0)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError):
            EncounterEnemy(max_health=100.0, current_health=100.0, armor=-1.0)

    def test_negative_shield_raises(self):
        with pytest.raises(ValueError):
            _enemy(shield=-5.0)

    def test_from_stats(self):
        stats = EnemyStats(health=1000, armor=200, resistances={"fire": 30.0})
        e = EncounterEnemy.from_stats(stats, name="golem")
        assert e.max_health     == pytest.approx(1000.0)
        assert e.armor          == pytest.approx(200.0)
        assert e.resistances["fire"] == pytest.approx(30.0)
        assert e.name           == "golem"

    def test_from_archetype_boss(self):
        e = EncounterEnemy.from_archetype(EnemyArchetype.BOSS)
        assert e.max_health     == pytest.approx(10000.0)
        assert e.armor          == pytest.approx(1000.0)

    def test_from_archetype_with_shield(self):
        e = EncounterEnemy.from_archetype(EnemyArchetype.ELITE, shield=500.0)
        assert e.shield     == pytest.approx(500.0)
        assert e.max_shield == pytest.approx(500.0)


class TestApplyDamage:
    def test_reduces_health(self):
        e = _enemy(health=100.0)
        e.apply_damage(30.0)
        assert e.current_health == pytest.approx(70.0)

    def test_kills_enemy(self):
        e = _enemy(health=100.0)
        e.apply_damage(100.0)
        assert not e.is_alive
        assert e.current_health == pytest.approx(0.0)

    def test_overkill_tracked(self):
        e = _enemy(health=50.0)
        e.apply_damage(100.0)
        assert e.overkill == pytest.approx(50.0)

    def test_dead_enemy_takes_no_damage(self):
        e = _enemy(health=50.0)
        e.apply_damage(50.0)
        result = e.apply_damage(50.0)
        assert result == pytest.approx(0.0)
        assert e.current_health == pytest.approx(0.0)

    def test_negative_damage_raises(self):
        e = _enemy()
        with pytest.raises(ValueError):
            e.apply_damage(-1.0)

    def test_shield_absorbs_first(self):
        e = _enemy(health=100.0, shield=40.0)
        e.apply_damage(30.0)
        assert e.shield         == pytest.approx(10.0)
        assert e.current_health == pytest.approx(100.0)

    def test_shield_overflow_hits_health(self):
        e = _enemy(health=100.0, shield=20.0)
        e.apply_damage(50.0)
        assert e.shield         == pytest.approx(0.0)
        assert e.current_health == pytest.approx(70.0)

    def test_zero_damage_no_change(self):
        e = _enemy(health=100.0)
        e.apply_damage(0.0)
        assert e.current_health == pytest.approx(100.0)


class TestApplyShieldDamage:
    def test_shield_absorbed(self):
        e = _enemy(shield=50.0)
        absorbed, overflow = e.apply_shield_damage(30.0)
        assert absorbed  == pytest.approx(30.0)
        assert overflow  == pytest.approx(0.0)
        assert e.shield  == pytest.approx(20.0)

    def test_shield_overflow(self):
        e = _enemy(shield=20.0)
        absorbed, overflow = e.apply_shield_damage(50.0)
        assert absorbed == pytest.approx(20.0)
        assert overflow == pytest.approx(30.0)
        assert e.shield == pytest.approx(0.0)

    def test_no_shield_all_overflow(self):
        e = _enemy(health=100.0)
        absorbed, overflow = e.apply_shield_damage(40.0)
        assert absorbed == pytest.approx(0.0)
        assert overflow == pytest.approx(40.0)

    def test_health_not_affected(self):
        e = _enemy(health=100.0, shield=50.0)
        e.apply_shield_damage(100.0)
        assert e.current_health == pytest.approx(100.0)


class TestStateQueries:
    def test_is_alive_true(self):
        assert _enemy(health=100.0).is_alive is True

    def test_is_alive_false_after_death(self):
        e = _enemy(health=100.0)
        e.apply_damage(100.0)
        assert e.is_alive is False

    def test_health_pct_full(self):
        assert _enemy(health=100.0).health_pct == pytest.approx(100.0)

    def test_health_pct_half(self):
        e = _enemy(health=100.0)
        e.apply_damage(50.0)
        assert e.health_pct == pytest.approx(50.0)

    def test_shield_pct_full(self):
        e = _enemy(shield=100.0)
        assert e.shield_pct == pytest.approx(100.0)

    def test_shield_pct_no_shield(self):
        assert _enemy().shield_pct == pytest.approx(0.0)


class TestReset:
    def test_reset_restores_health(self):
        e = _enemy(health=100.0)
        e.apply_damage(80.0)
        e.reset()
        assert e.current_health == pytest.approx(100.0)

    def test_reset_restores_shield(self):
        e = _enemy(health=100.0, shield=50.0)
        e.apply_damage(80.0)
        e.reset()
        assert e.shield == pytest.approx(50.0)

    def test_reset_clears_overkill(self):
        e = _enemy(health=50.0)
        e.apply_damage(200.0)
        e.reset()
        assert e.overkill       == pytest.approx(0.0)
        assert e.current_health == pytest.approx(50.0)
        assert e.is_alive is True
