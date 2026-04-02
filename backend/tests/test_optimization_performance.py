"""
F15 — Optimization Performance Tests

Benchmarks for the optimization pipeline:
  - 100 variants < 10 seconds
  - 500 variants < 60 seconds

These tests use TRAINING_DUMMY with a large tick (1.0s) to minimize simulation
time per variant, isolating the optimization overhead rather than encounter math.
"""

import time
import pytest

# Mark the whole module as slow so it can be skipped in fast CI runs:
#   pytest -m "not slow"
pytestmark = pytest.mark.slow

from builds.build_definition import BuildDefinition
from optimization.models.optimization_config import OptimizationConfig
from optimization.optimization_service import optimize


# A minimal build: no gear, no passives, no buffs — fast to compile
BASE_BUILD = BuildDefinition.from_dict({
    "character_class": "Mage",
    "mastery":         "Spellblade",
    "skill_id":        "Rip Blood",
    "skill_level":     20,
})

# Fast encounter: Training Dummy + coarse tick so simulation is quick
FAST_ENCOUNTER = {
    "enemy_template": "TRAINING_DUMMY",
    "fight_duration": 10.0,
    "tick_size":      1.0,   # only 10 ticks → very fast
    "distribution":   "SINGLE",
}


def _time_optimize(n_variants: int, depth: int = 1, seed: int = 42) -> float:
    config = OptimizationConfig(
        target_metric  = "dps",
        max_variants   = n_variants,
        mutation_depth = depth,
        random_seed    = seed,
    )
    t0 = time.perf_counter()
    optimize(
        base_build       = BASE_BUILD,
        config           = config,
        encounter_kwargs = FAST_ENCOUNTER,
        top_n            = 10,
    )
    return time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------

class TestOptimizationPerformance:
    def test_100_variants_under_10_seconds(self):
        elapsed = _time_optimize(100)
        assert elapsed < 10.0, (
            f"100 variants took {elapsed:.2f}s — expected < 10s. "
            "Simulation overhead may be higher than anticipated."
        )

    def test_500_variants_under_60_seconds(self):
        elapsed = _time_optimize(500)
        assert elapsed < 60.0, (
            f"500 variants took {elapsed:.2f}s — expected < 60s."
        )

    def test_single_variant_is_fast(self):
        """Smoke test: a single variant should complete in well under 1 second."""
        elapsed = _time_optimize(1)
        assert elapsed < 1.0, f"Single variant took {elapsed:.2f}s — unexpectedly slow"

    def test_variant_count_scales_roughly_linearly(self):
        """
        Time for 100 variants should be < 5× time for 20 variants.
        This guards against accidental O(n²) complexity.
        """
        t20  = _time_optimize(20,  seed=1)
        t100 = _time_optimize(100, seed=1)
        # 5× looser bound to avoid flakiness on slow CI machines
        assert t100 < t20 * 5 + 1.0, (
            f"t20={t20:.2f}s, t100={t100:.2f}s — scaling looks non-linear"
        )
