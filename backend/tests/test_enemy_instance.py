"""
Tests for Enemy Profile System — EnemyInstance (Step 65).
"""

import pytest
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.domain.resistance import RES_CAP


def normal_instance() -> EnemyInstance:
    return EnemyInstance.from_archetype(EnemyArchetype.NORMAL)

def dummy_instance() -> EnemyInstance:
    return EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY)


class TestEnemyInstanceConstruction:
    def test_from_archetype_normal(self):
        e = normal_instance()
        assert e.current_health == pytest.approx(1000.0)
        assert e.is_alive is True

    def test_from_archetype_boss(self):
        e = EnemyInstance.from_archetype(EnemyArchetype.BOSS)
        assert e.current_health == pytest.approx(10000.0)

    def test_from_stats(self):
        stats = EnemyStats(health=500, armor=100, resistances={"fire": 30.0})
        e = EnemyInstance.from_stats(stats)
        assert e.max_health == pytest.approx(500.0)
        assert e.armor == 100

    def test_health_pct_starts_at_100(self):
        e = normal_instance()
        assert e.health_pct == pytest.approx(100.0)


class TestTakeDamage:
    def test_reduces_current_health(self):
        e = normal_instance()
        e.take_damage(200.0)
        assert e.current_health == pytest.approx(800.0)

    def test_returns_actual_damage_dealt(self):
        e = normal_instance()
        actual = e.take_damage(300.0)
        assert actual == pytest.approx(300.0)

    def test_overkill_capped_at_health(self):
        e = normal_instance()
        actual = e.take_damage(5000.0)
        assert actual == pytest.approx(1000.0)
        assert e.current_health == pytest.approx(0.0)

    def test_dead_enemy_takes_no_damage(self):
        e = normal_instance()
        e.take_damage(1000.0)
        assert e.is_alive is False
        actual = e.take_damage(500.0)
        assert actual == pytest.approx(0.0)
        assert e.current_health == pytest.approx(0.0)

    def test_zero_damage_no_change(self):
        e = normal_instance()
        e.take_damage(0.0)
        assert e.current_health == pytest.approx(1000.0)

    def test_negative_damage_raises(self):
        e = normal_instance()
        with pytest.raises(ValueError, match="damage amount"):
            e.take_damage(-10.0)

    def test_health_pct_updates(self):
        e = normal_instance()
        e.take_damage(500.0)
        assert e.health_pct == pytest.approx(50.0)

    def test_exactly_lethal_damage(self):
        e = normal_instance()
        e.take_damage(1000.0)
        assert e.is_alive is False
        assert e.current_health == pytest.approx(0.0)


class TestEffectiveResistance:
    def test_base_resistance_without_modifiers(self):
        e = normal_instance()
        res = e.effective_resistance("fire")
        assert res == pytest.approx(25.0)   # NORMAL has 25% fire res

    def test_zero_resistance_for_dummy(self):
        e = dummy_instance()
        assert e.effective_resistance("fire") == pytest.approx(0.0)

    def test_penetration_reduces_effective_res(self):
        e = normal_instance()
        res = e.effective_resistance("fire", penetration=10.0)
        assert res == pytest.approx(15.0)

    def test_resistance_capped_at_res_cap(self):
        stats = EnemyStats(health=100, armor=0, resistances={"fire": 90.0})
        e = EnemyInstance.from_stats(stats)
        assert e.effective_resistance("fire") == pytest.approx(RES_CAP)

    def test_unknown_damage_type_returns_zero(self):
        e = normal_instance()
        assert e.effective_resistance("chaos") == pytest.approx(0.0)


class TestApplyShred:
    def test_shred_reduces_effective_resistance(self):
        e = normal_instance()
        e.apply_shred("fire", 15.0)
        assert e.effective_resistance("fire") == pytest.approx(10.0)

    def test_shred_accumulates(self):
        e = normal_instance()
        e.apply_shred("fire", 10.0)
        e.apply_shred("fire", 10.0)
        assert e.effective_resistance("fire") == pytest.approx(5.0)

    def test_shred_capped_at_max(self):
        e = normal_instance()
        e.apply_shred("fire", 200.0)  # capped at 100 by apply_shred
        # 25 base - 100 shred → clamped to -100 (RES_MIN)
        assert e.effective_resistance("fire") == pytest.approx(-75.0)

    def test_current_shred_query(self):
        e = normal_instance()
        e.apply_shred("cold", 20.0)
        assert e.current_shred("cold") == pytest.approx(20.0)

    def test_no_shred_returns_zero(self):
        e = normal_instance()
        assert e.current_shred("void") == pytest.approx(0.0)

    def test_shred_on_different_types_independent(self):
        e = normal_instance()
        e.apply_shred("fire", 20.0)
        assert e.effective_resistance("cold") == pytest.approx(25.0)
