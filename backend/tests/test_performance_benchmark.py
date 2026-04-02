"""
Performance Benchmark (Step 86).

Establishes runtime efficiency baselines for all major simulation paths.
Tests must complete within generous wall-clock time bounds so the suite
stays fast on any reasonable CI machine.

Baselines:
  - 100× 10s sustain loop (tick=0.1s, 2 skills) in < 5s
  - 100× 10s ailment loop in < 5s
  - 10 000 resolve_hit calls in < 2s
  - 1 × 1800s coarse loop (tick=0.5s) in < 3s
  - 1 × 600s fine loop (tick=0.1s, 2 skills) in < 3s
  - 10 000 EnemyInstance alloc + shred + take_damage in < 2s
"""

import time

import pytest

from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.ailments import AilmentType
from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.damage_conversion import ConversionRule
from app.domain.enemy import EnemyInstance, EnemyStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _elapsed(fn) -> float:
    """Return wall-clock seconds for fn()."""
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


def _sustain_cfg(duration: float, tick: float = 0.1) -> SimConfig:
    return SimConfig(
        tick_size=tick,
        fight_duration=duration,
        max_mana=200.0,
        mana_regen_rate=20.0,
        ailment_damage_pct=50.0,
        skills=(
            SkillSpec("fireball",  mana_cost=30.0, cooldown=2.0, base_damage=150.0, priority=1),
            SkillSpec("frostbolt", mana_cost=10.0, cooldown=0.5, base_damage=50.0,  priority=2),
        ),
    )


def _ailment_cfg(duration: float) -> SimConfig:
    return SimConfig(
        tick_size=0.1,
        fight_duration=duration,
        max_mana=300.0,
        mana_regen_rate=15.0,
        ailment_damage_pct=75.0,
        ailment_duration_pct=50.0,
        skills=(
            SkillSpec(
                name="bleed",
                mana_cost=15.0,
                cooldown=1.0,
                base_damage=0.0,
                ailment_type=AilmentType.BLEED,
                ailment_base_dmg=30.0,
                ailment_duration=5.0,
                priority=1,
            ),
            SkillSpec(
                name="poison",
                mana_cost=10.0,
                cooldown=0.5,
                base_damage=0.0,
                ailment_type=AilmentType.POISON,
                ailment_base_dmg=20.0,
                ailment_duration=4.0,
                priority=2,
            ),
        ),
    )


# ---------------------------------------------------------------------------
# FullCombatLoop benchmarks
# ---------------------------------------------------------------------------

class TestLoopPerformance:
    def test_100x_10s_sustain_under_5s(self):
        cfg = _sustain_cfg(10.0)
        elapsed = _elapsed(lambda: [FullCombatLoop(cfg).run() for _ in range(100)])
        assert elapsed < 5.0, f"100× sustain loop took {elapsed:.2f}s (limit 5s)"

    def test_100x_10s_ailment_under_5s(self):
        cfg = _ailment_cfg(10.0)
        elapsed = _elapsed(lambda: [FullCombatLoop(cfg).run() for _ in range(100)])
        assert elapsed < 5.0, f"100× ailment loop took {elapsed:.2f}s (limit 5s)"

    def test_1x_600s_fine_tick_under_3s(self):
        cfg = _sustain_cfg(600.0, tick=0.1)
        elapsed = _elapsed(lambda: FullCombatLoop(cfg).run())
        assert elapsed < 3.0, f"600s/0.1 loop took {elapsed:.2f}s (limit 3s)"

    def test_1x_1800s_coarse_tick_under_3s(self):
        cfg = _sustain_cfg(1800.0, tick=0.5)
        elapsed = _elapsed(lambda: FullCombatLoop(cfg).run())
        assert elapsed < 3.0, f"1800s/0.5 loop took {elapsed:.2f}s (limit 3s)"

    def test_throughput_ticks_per_second(self):
        """Log ticks-per-second; no hard limit but prints for CI visibility."""
        cfg = _sustain_cfg(300.0, tick=0.1)
        t0 = time.perf_counter()
        result = FullCombatLoop(cfg).run()
        elapsed = time.perf_counter() - t0
        tps = result.ticks_simulated / elapsed
        # Require at least 5000 ticks/second on any reasonable machine
        assert tps >= 5_000, f"Throughput too low: {tps:.0f} ticks/s"


# ---------------------------------------------------------------------------
# resolve_hit benchmarks
# ---------------------------------------------------------------------------

class TestHitPipelinePerformance:
    def test_10k_basic_hits_under_2s(self):
        inp = HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0)
        elapsed = _elapsed(lambda: [resolve_hit(inp) for _ in range(10_000)])
        assert elapsed < 2.0, f"10 000 basic hits took {elapsed:.2f}s (limit 2s)"

    def test_10k_hits_with_conversion_under_2s(self):
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        inp = HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=0.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        )
        elapsed = _elapsed(lambda: [resolve_hit(inp) for _ in range(10_000)])
        assert elapsed < 2.0, f"10 000 conversion hits took {elapsed:.2f}s (limit 2s)"

    def test_10k_hits_miss_path_under_1s(self):
        inp = HitInput(base_damage=100.0, rng_hit=1.0)
        elapsed = _elapsed(lambda: [resolve_hit(inp) for _ in range(10_000)])
        assert elapsed < 1.0, f"10 000 miss-path hits took {elapsed:.2f}s (limit 1s)"


# ---------------------------------------------------------------------------
# EnemyInstance benchmarks
# ---------------------------------------------------------------------------

class TestEnemyInstancePerformance:
    def test_10k_alloc_and_ops_under_2s(self):
        def _workload():
            for _ in range(10_000):
                e = EnemyInstance.from_stats(EnemyStats(
                    health=1000, armor=200, resistances={"fire": 50.0}
                ))
                e.apply_shred("fire", 10.0)
                e.take_damage(100.0)

        elapsed = _elapsed(_workload)
        assert elapsed < 2.0, f"10 000 EnemyInstance ops took {elapsed:.2f}s (limit 2s)"


# ---------------------------------------------------------------------------
# Combined throughput
# ---------------------------------------------------------------------------

class TestCombinedThroughput:
    def test_full_suite_under_10s(self):
        """All major paths combined: confirms total benchmark suite is fast."""
        cfg = _sustain_cfg(10.0)
        inp = HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0)
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        inp_conv = HitInput(
            base_damage=100.0,
            damage_type=DamageType.PHYSICAL,
            rng_hit=0.0,
            rng_crit=99.0,
            conversion_rules=rules,
        )

        t0 = time.perf_counter()
        for _ in range(50):
            FullCombatLoop(cfg).run()
        for _ in range(5_000):
            resolve_hit(inp)
        for _ in range(5_000):
            resolve_hit(inp_conv)
        elapsed = time.perf_counter() - t0

        assert elapsed < 10.0, f"Combined throughput test took {elapsed:.2f}s (limit 10s)"
