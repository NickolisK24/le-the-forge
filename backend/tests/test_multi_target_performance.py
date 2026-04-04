"""
I18 — Multi-Target Performance Benchmarks

Targets:
  - 10-target simulation < 0.5s
  - 50-target simulation < 2s
  - Linear scaling validation
"""
import time
import pytest
from targets.target_templates import mob_swarm
from state.multi_target_state import MultiTargetState
from app.services.multi_target_encounter import MultiTargetEncounterEngine


def _run(count: int, hp: float = 1e6, base_damage: float = 10_000.0,
         distribution: str = "full_aoe", max_duration: float = 60.0) -> float:
    state = MultiTargetState(manager=mob_swarm(count, hp))
    t0 = time.perf_counter()
    MultiTargetEncounterEngine().run(
        state, base_damage=base_damage, distribution=distribution,
        max_duration=max_duration, tick_size=0.1,
    )
    return time.perf_counter() - t0


class TestTenTargetSimulation:
    def test_10_targets_under_half_second(self):
        elapsed = _run(10)
        assert elapsed < 0.5, f"10-target sim took {elapsed:.3f}s (limit 0.5s)"


class TestFiftyTargetSimulation:
    def test_50_targets_under_two_seconds(self):
        elapsed = _run(50)
        assert elapsed < 2.0, f"50-target sim took {elapsed:.3f}s (limit 2.0s)"


class TestLinearScaling:
    def test_50_targets_no_more_than_10x_slower_than_10(self):
        t10 = _run(10)
        t50 = _run(50)
        ratio = t50 / max(t10, 1e-6)
        assert ratio < 10.0, (
            f"50-target ({t50:.3f}s) is {ratio:.1f}× slower than "
            f"10-target ({t10:.3f}s); expected < 10×"
        )
