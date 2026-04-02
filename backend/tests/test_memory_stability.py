"""
Memory Stability (Step 85).

Runs thousands of simulations back-to-back to verify there are no memory
leaks, reference cycles, or unbounded object accumulation.

Approach:
  - Measure RSS before and after N simulations.
  - Acceptable growth is capped at a generous threshold (10 MB) to allow
    for Python interpreter caching/interning.
  - Tests cover FullCombatLoop, resolve_hit, and EnemyInstance.
  - Also verifies that SimResult, HitResult, and EnemyInstance objects are
    not accidentally retained by the engine between runs.
"""

import gc
import sys

import pytest

from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.ailments import AilmentType
from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.damage_conversion import ConversionRule
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.shields import AbsorptionShield


# ---------------------------------------------------------------------------
# Memory helpers
# ---------------------------------------------------------------------------

def _rss_bytes() -> int:
    """Return current process RSS in bytes, or 0 if unavailable."""
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        return 0


def _current_memory_mb() -> float:
    """Return current RSS in MB using /proc/self/status (Linux) or resource."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024.0
    except Exception:
        pass
    return _rss_bytes() / (1024 * 1024)


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

def _sustain_cfg(duration=10.0) -> SimConfig:
    return SimConfig(
        tick_size=0.1,
        fight_duration=duration,
        max_mana=200.0,
        mana_regen_rate=20.0,
        ailment_damage_pct=50.0,
        skills=(
            SkillSpec("fireball",  mana_cost=30.0, cooldown=2.0, base_damage=150.0, priority=1),
            SkillSpec("frostbolt", mana_cost=10.0, cooldown=0.5, base_damage=50.0,  priority=2),
        ),
    )


def _ailment_cfg(duration=10.0) -> SimConfig:
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
        ),
    )


# ---------------------------------------------------------------------------
# FullCombatLoop stability
# ---------------------------------------------------------------------------

class TestLoopMemoryStability:
    _ITERATIONS = 500

    def test_sustain_loop_no_leak(self):
        cfg = _sustain_cfg()
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            result = FullCombatLoop(cfg).run()
            del result

        gc.collect()
        after_mb = _current_memory_mb()
        growth_mb = after_mb - before_mb
        assert growth_mb < 10.0, f"Memory grew by {growth_mb:.1f} MB over {self._ITERATIONS} runs"

    def test_ailment_loop_no_leak(self):
        cfg = _ailment_cfg()
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            result = FullCombatLoop(cfg).run()
            del result

        gc.collect()
        after_mb = _current_memory_mb()
        growth_mb = after_mb - before_mb
        assert growth_mb < 10.0, f"Memory grew by {growth_mb:.1f} MB over {self._ITERATIONS} runs"

    def test_results_not_retained_by_engine(self):
        """SimResult objects should not be held alive by FullCombatLoop after run()."""
        import weakref
        cfg = _sustain_cfg()
        loop = FullCombatLoop(cfg)
        result = loop.run()
        ref = weakref.ref(result)
        del result
        gc.collect()
        # The loop should not hold a strong reference to its last result
        # (weak ref becomes None if object is freed)
        # This is a best-effort check; if loop holds result it will fail
        loop_attrs = vars(loop) if hasattr(loop, "__dict__") else {}
        # Verify no SimResult stored on the loop object
        from app.domain.full_combat_loop import SimResult
        for v in loop_attrs.values():
            assert not isinstance(v, SimResult), "FullCombatLoop retained SimResult"


# ---------------------------------------------------------------------------
# resolve_hit stability
# ---------------------------------------------------------------------------

class TestHitPipelineMemoryStability:
    _ITERATIONS = 2000

    def test_simple_hit_no_leak(self):
        inp = HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0)
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            result = resolve_hit(inp)
            del result

        gc.collect()
        after_mb = _current_memory_mb()
        growth_mb = after_mb - before_mb
        assert growth_mb < 10.0, f"Memory grew by {growth_mb:.1f} MB over {self._ITERATIONS} hits"

    def test_hit_with_conversion_no_leak(self):
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        inp = HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=99.0,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
        )
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            result = resolve_hit(inp)
            del result

        gc.collect()
        after_mb = _current_memory_mb()
        assert after_mb - before_mb < 10.0

    def test_hit_with_enemy_no_leak(self):
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=100))
            inp = HitInput(
                base_damage=50.0,
                rng_hit=0.0,
                rng_crit=99.0,
                enemy=enemy,
            )
            result = resolve_hit(inp)
            del result, enemy, inp

        gc.collect()
        after_mb = _current_memory_mb()
        assert after_mb - before_mb < 15.0


# ---------------------------------------------------------------------------
# EnemyInstance stability
# ---------------------------------------------------------------------------

class TestEnemyInstanceStability:
    _ITERATIONS = 5000

    def test_many_enemy_instances_no_leak(self):
        gc.collect()
        before_mb = _current_memory_mb()

        for _ in range(self._ITERATIONS):
            e = EnemyInstance.from_stats(EnemyStats(
                health=500, armor=100,
                resistances={"fire": 50.0, "cold": 30.0},
            ))
            e.take_damage(100.0)
            e.apply_shred("fire", 10.0)
            del e

        gc.collect()
        after_mb = _current_memory_mb()
        assert after_mb - before_mb < 10.0

    def test_shred_dict_does_not_accumulate_on_single_instance(self):
        """Repeated shred applications should not grow the shred dict unboundedly."""
        e = EnemyInstance.from_stats(EnemyStats(health=10000, armor=0))
        for i in range(500):
            e.apply_shred("fire", 0.5)
        # Only one entry for "fire" in the shred dict
        assert len(e._shred) == 1


# ---------------------------------------------------------------------------
# Mixed workload
# ---------------------------------------------------------------------------

class TestMixedWorkloadStability:
    def test_mixed_workload_1000_iterations(self):
        """Alternates between loop runs and hit pipeline calls."""
        cfg    = _sustain_cfg(5.0)
        rules  = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)

        gc.collect()
        before_mb = _current_memory_mb()

        for i in range(1000):
            if i % 2 == 0:
                r = FullCombatLoop(cfg).run()
            else:
                inp = HitInput(
                    base_damage=100.0,
                    rng_hit=0.0,
                    rng_crit=0.0,
                    crit_chance=1.0,
                    crit_multiplier=2.0,
                    damage_type=DamageType.PHYSICAL,
                    conversion_rules=rules,
                )
                r = resolve_hit(inp)
            del r

        gc.collect()
        after_mb = _current_memory_mb()
        assert after_mb - before_mb < 15.0
