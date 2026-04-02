"""
Encounter Performance Tests (Step 109).

Throughput benchmarks for the encounter simulation engine.
Thresholds are set conservatively (10-25× observed baseline) to
prevent flaky failures on slower CI machines while still catching
catastrophic regressions.

Baselines (developer machine):
  100 × short run  (10 s / 0.1 tick)  ≈ 0.19 s total  (~2 ms each)
  10  × long run   (300 s / 0.1 tick) ≈ 0.56 s total  (~56 ms each)
  20  × multi-target CLEAVE 10-enemy  ≈ 1.77 s total  (~88 ms each)
"""

import time

import pytest

from encounter.multi_target import HitDistribution, MultiHitConfig
from encounter.state_machine import EncounterConfig, EncounterMachine
from encounter.enemy import EncounterEnemy


def _hit(dist=HitDistribution.SINGLE):
    return MultiHitConfig(distribution=dist, rng_hit=0.0, rng_crit=99.0)


def _dummy(health: float = 1_000_000.0, name: str = "d") -> EncounterEnemy:
    return EncounterEnemy(
        max_health=health, current_health=health, armor=0.0, name=name
    )


class TestShortRunThroughput:
    """100 short fights must complete well within budget."""

    def test_100_short_runs_complete(self):
        """100 × 10-second fights (100 ticks each) finish in < 5 s."""
        start = time.perf_counter()
        for _ in range(100):
            cfg = EncounterConfig(
                enemies=[_dummy()],
                fight_duration=10.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(),
            )
            result = EncounterMachine(cfg).run()
            assert result.ticks_simulated >= 100
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"100 short runs took {elapsed:.2f}s (budget 5s)"

    def test_single_short_run_under_budget(self):
        """A single 10-second fight must finish in < 100 ms."""
        cfg = EncounterConfig(
            enemies=[_dummy()],
            fight_duration=10.0,
            tick_size=0.1,
            base_damage=100.0,
            hit_config=_hit(),
        )
        start = time.perf_counter()
        EncounterMachine(cfg).run()
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"Single short run took {elapsed*1000:.1f}ms (budget 100ms)"


class TestLongRunThroughput:
    """10 long fights must complete within budget."""

    def test_10_long_runs_complete(self):
        """10 × 300-second fights (3 000 ticks each) finish in < 10 s."""
        start = time.perf_counter()
        for _ in range(10):
            cfg = EncounterConfig(
                enemies=[_dummy(health=1_000_000_000.0)],
                fight_duration=300.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(),
            )
            result = EncounterMachine(cfg).run()
            assert result.ticks_simulated >= 3000
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"10 long runs took {elapsed:.2f}s (budget 10s)"

    def test_single_long_run_under_budget(self):
        """A single 300-second fight must finish in < 1 s."""
        cfg = EncounterConfig(
            enemies=[_dummy(health=1_000_000_000.0)],
            fight_duration=300.0,
            tick_size=0.1,
            base_damage=100.0,
            hit_config=_hit(),
        )
        start = time.perf_counter()
        EncounterMachine(cfg).run()
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Single long run took {elapsed*1000:.1f}ms (budget 1000ms)"


class TestMultiTargetThroughput:
    """Multi-target (CLEAVE) benchmarks with 10 enemies."""

    def test_20_cleave_runs_complete(self):
        """20 × 10-enemy CLEAVE fights (60 s) finish in < 15 s."""
        start = time.perf_counter()
        for _ in range(20):
            enemies = [_dummy(name=f"e{i}") for i in range(10)]
            cfg = EncounterConfig(
                enemies=enemies,
                fight_duration=60.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(HitDistribution.CLEAVE),
            )
            result = EncounterMachine(cfg).run()
            assert result.ticks_simulated == 600
        elapsed = time.perf_counter() - start
        assert elapsed < 15.0, f"20 CLEAVE runs took {elapsed:.2f}s (budget 15s)"

    def test_single_cleave_run_under_budget(self):
        """A single 10-enemy CLEAVE fight (60 s) must finish in < 1 s."""
        enemies = [_dummy(name=f"e{i}") for i in range(10)]
        cfg = EncounterConfig(
            enemies=enemies,
            fight_duration=60.0,
            tick_size=0.1,
            base_damage=100.0,
            hit_config=_hit(HitDistribution.CLEAVE),
        )
        start = time.perf_counter()
        EncounterMachine(cfg).run()
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Single CLEAVE run took {elapsed*1000:.1f}ms (budget 1000ms)"

    def test_cleave_scales_with_enemy_count(self):
        """CLEAVE with 20 enemies should still finish < 2× the 10-enemy budget."""
        enemies_10 = [_dummy(name=f"e{i}") for i in range(10)]
        enemies_20 = [_dummy(name=f"e{i}") for i in range(20)]

        def run(enemies):
            cfg = EncounterConfig(
                enemies=enemies,
                fight_duration=30.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(HitDistribution.CLEAVE),
            )
            t0 = time.perf_counter()
            EncounterMachine(cfg).run()
            return time.perf_counter() - t0

        t10 = run(enemies_10)
        t20 = run(enemies_20)
        # 20-enemy run should be no more than 3× slower than 10-enemy run
        assert t20 < t10 * 3 + 0.05, (
            f"20-enemy ({t20*1000:.1f}ms) > 3× 10-enemy ({t10*1000:.1f}ms)"
        )
