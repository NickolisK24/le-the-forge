"""Tests for multi-target combat engine (Step 101)."""

import pytest
from encounter.enemy import EncounterEnemy
from encounter.multi_target import HitDistribution, MultiHitConfig, MultiTargetEngine


def _enemy(health=1000.0, name="e"):
    return EncounterEnemy(max_health=health, current_health=health,
                          armor=0.0, name=name)

def _dead():
    e = _enemy(health=100.0, name="dead")
    e.apply_damage(100.0)
    return e

def _cfg(dist, **kw):
    return MultiHitConfig(distribution=dist, rng_hit=0.0, rng_crit=99.0, **kw)


class TestSingle:
    def test_only_primary_hit(self):
        enemies = [_enemy(name="a"), _enemy(name="b")]
        eng = MultiTargetEngine()
        results = eng.apply_hit(enemies, 100.0, _cfg(HitDistribution.SINGLE), primary_idx=0)
        assert results[0] is not None
        assert results[1] is None
        assert enemies[0].current_health == pytest.approx(900.0)
        assert enemies[1].current_health == pytest.approx(1000.0)

    def test_empty_returns_empty(self):
        assert MultiTargetEngine().apply_hit([], 100.0) == []

    def test_dead_primary_skipped(self):
        d = _dead()
        e = _enemy(name="b")
        results = MultiTargetEngine().apply_hit([d, e], 100.0,
                  _cfg(HitDistribution.SINGLE), primary_idx=0)
        assert results[0] is None


class TestCleave:
    def test_all_alive_hit(self):
        enemies = [_enemy(name="a"), _enemy(name="b"), _enemy(name="c")]
        eng = MultiTargetEngine()
        eng.apply_hit(enemies, 100.0, _cfg(HitDistribution.CLEAVE))
        for e in enemies:
            assert e.current_health == pytest.approx(900.0)

    def test_dead_enemy_skipped(self):
        alive = _enemy(name="a")
        dead  = _dead()
        results = MultiTargetEngine().apply_hit([alive, dead], 100.0,
                                                 _cfg(HitDistribution.CLEAVE))
        assert results[0] is not None
        assert results[1] is None

    def test_total_damage_correct(self):
        enemies = [_enemy(name="a"), _enemy(name="b")]
        eng = MultiTargetEngine()
        results = eng.apply_hit(enemies, 100.0, _cfg(HitDistribution.CLEAVE))
        assert MultiTargetEngine.total_damage(results) == pytest.approx(200.0)


class TestSplit:
    def test_damage_divided_equally(self):
        enemies = [_enemy(name="a"), _enemy(name="b")]
        eng = MultiTargetEngine()
        eng.apply_hit(enemies, 100.0, _cfg(HitDistribution.SPLIT))
        for e in enemies:
            assert e.current_health == pytest.approx(950.0)

    def test_single_target_split_full_damage(self):
        e = _enemy(name="a")
        MultiTargetEngine().apply_hit([e], 100.0, _cfg(HitDistribution.SPLIT))
        assert e.current_health == pytest.approx(900.0)

    def test_total_damage_same_as_base(self):
        enemies = [_enemy(name=f"e{i}") for i in range(4)]
        results = MultiTargetEngine().apply_hit(enemies, 100.0,
                                                 _cfg(HitDistribution.SPLIT))
        assert MultiTargetEngine.total_damage(results) == pytest.approx(100.0)


class TestChain:
    def test_primary_takes_full_damage(self):
        enemies = [_enemy(name="a"), _enemy(name="b")]
        MultiTargetEngine().apply_hit(enemies, 100.0,
            _cfg(HitDistribution.CHAIN, chain_falloff_pct=50.0))
        assert enemies[0].current_health == pytest.approx(900.0)
        assert enemies[1].current_health == pytest.approx(950.0)

    def test_chain_falloff_reduces_damage(self):
        enemies = [_enemy(name=f"e{i}") for i in range(3)]
        MultiTargetEngine().apply_hit(enemies, 100.0,
            _cfg(HitDistribution.CHAIN, chain_falloff_pct=50.0))
        # e0=100, e1=50, e2=25
        assert enemies[0].current_health == pytest.approx(900.0)
        assert enemies[1].current_health == pytest.approx(950.0)
        assert enemies[2].current_health == pytest.approx(975.0)

    def test_results_length_matches_enemies(self):
        enemies = [_enemy(name=f"e{i}") for i in range(3)]
        results = MultiTargetEngine().apply_hit(enemies, 100.0,
                    _cfg(HitDistribution.CHAIN))
        assert len(results) == 3


class TestMiss:
    def test_miss_deals_no_damage(self):
        e = _enemy(name="a")
        cfg = MultiHitConfig(distribution=HitDistribution.SINGLE,
                              rng_hit=1.0)  # always miss
        results = MultiTargetEngine().apply_hit([e], 100.0, cfg)
        assert results[0].hit_result.landed is False
        assert e.current_health == pytest.approx(1000.0)
