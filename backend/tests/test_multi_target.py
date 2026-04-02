"""
Tests for Multi-Enemy Simulation (Step 66).
"""

import pytest
from app.domain.multi_target import HitMode, TargetGroup
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats


def make_enemy(health: float = 1000.0) -> EnemyInstance:
    return EnemyInstance.from_stats(EnemyStats(health=int(health), armor=0))


def make_group(*healths: float) -> TargetGroup:
    return TargetGroup([make_enemy(h) for h in healths])


class TestTargetGroupConstruction:
    def test_single_enemy(self):
        g = TargetGroup([make_enemy()])
        assert g.count == 1

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            TargetGroup([])

    def test_living_all_alive(self):
        g = make_group(100.0, 200.0)
        assert len(g.living) == 2

    def test_all_dead_false_when_alive(self):
        g = make_group(100.0)
        assert g.all_dead is False


class TestHitModeSingle:
    def test_only_first_alive_hit(self):
        g = make_group(500.0, 500.0)
        results = g.apply_hit(100.0, HitMode.SINGLE)
        assert results[0] == pytest.approx(100.0)
        assert results[1] == pytest.approx(0.0)

    def test_skips_dead_primary(self):
        g = make_group(100.0, 500.0)
        g.enemies[0].take_damage(100.0)   # kill first
        results = g.apply_hit(50.0, HitMode.SINGLE)
        assert results[0] == pytest.approx(0.0)
        assert results[1] == pytest.approx(50.0)

    def test_no_living_targets(self):
        g = make_group(100.0)
        g.enemies[0].take_damage(100.0)
        results = g.apply_hit(50.0, HitMode.SINGLE)
        assert results == [pytest.approx(0.0)]

    def test_default_mode_is_single(self):
        g = make_group(500.0, 500.0)
        results = g.apply_hit(100.0)
        assert results[0] == pytest.approx(100.0)
        assert results[1] == pytest.approx(0.0)


class TestHitModeCleave:
    def test_all_targets_take_full_damage(self):
        g = make_group(500.0, 500.0, 500.0)
        results = g.apply_hit(100.0, HitMode.CLEAVE)
        assert all(r == pytest.approx(100.0) for r in results)

    def test_dead_enemy_takes_zero(self):
        g = make_group(100.0, 500.0)
        g.enemies[0].take_damage(100.0)
        results = g.apply_hit(50.0, HitMode.CLEAVE)
        assert results[0] == pytest.approx(0.0)
        assert results[1] == pytest.approx(50.0)

    def test_total_damage_equals_per_enemy_sum(self):
        g = make_group(300.0, 300.0)
        results = g.apply_hit(100.0, HitMode.CLEAVE)
        assert g.total_damage_dealt(results) == pytest.approx(200.0)


class TestHitModeSplit:
    def test_two_enemies_split_equally(self):
        g = make_group(500.0, 500.0)
        results = g.apply_hit(100.0, HitMode.SPLIT)
        assert results[0] == pytest.approx(50.0)
        assert results[1] == pytest.approx(50.0)

    def test_three_enemies_split_equally(self):
        g = make_group(500.0, 500.0, 500.0)
        results = g.apply_hit(90.0, HitMode.SPLIT)
        assert all(r == pytest.approx(30.0) for r in results)

    def test_split_excludes_dead_from_divisor(self):
        # 3 enemies, 1 dead → split among 2 living
        g = make_group(500.0, 500.0, 500.0)
        g.enemies[2].take_damage(500.0)
        results = g.apply_hit(100.0, HitMode.SPLIT)
        assert results[0] == pytest.approx(50.0)
        assert results[1] == pytest.approx(50.0)
        assert results[2] == pytest.approx(0.0)

    def test_single_living_enemy_gets_full_damage(self):
        g = make_group(500.0, 100.0)
        g.enemies[1].take_damage(100.0)
        results = g.apply_hit(80.0, HitMode.SPLIT)
        assert results[0] == pytest.approx(80.0)
        assert results[1] == pytest.approx(0.0)

    def test_all_dead_split_returns_zeros(self):
        g = make_group(100.0)
        g.enemies[0].take_damage(100.0)
        results = g.apply_hit(50.0, HitMode.SPLIT)
        assert results == [pytest.approx(0.0)]


class TestHitModeChain:
    def test_each_living_enemy_takes_full_damage(self):
        g = make_group(500.0, 500.0, 500.0)
        results = g.apply_hit(100.0, HitMode.CHAIN)
        assert all(r == pytest.approx(100.0) for r in results)

    def test_dead_enemy_skipped_in_chain(self):
        g = make_group(100.0, 500.0)
        g.enemies[0].take_damage(100.0)
        results = g.apply_hit(50.0, HitMode.CHAIN)
        assert results[0] == pytest.approx(0.0)
        assert results[1] == pytest.approx(50.0)

    def test_chain_total_higher_than_split(self):
        g = make_group(500.0, 500.0)
        chain = sum(g.apply_hit(100.0, HitMode.CHAIN))
        g2 = make_group(500.0, 500.0)
        split = sum(g2.apply_hit(100.0, HitMode.SPLIT))
        assert chain > split  # 200 vs 100


class TestNegativeDamageRaises:
    def test_all_modes_reject_negative_damage(self):
        g = make_group(500.0)
        for mode in HitMode:
            with pytest.raises(ValueError, match="damage"):
                g.apply_hit(-10.0, mode)


class TestLivingAndAllDead:
    def test_living_updates_after_kill(self):
        g = make_group(100.0, 200.0)
        g.apply_hit(100.0, HitMode.SINGLE)
        assert len(g.living) == 1

    def test_all_dead_after_cleave(self):
        g = make_group(50.0, 50.0)
        g.apply_hit(100.0, HitMode.CLEAVE)
        assert g.all_dead is True
