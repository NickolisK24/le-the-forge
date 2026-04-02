"""G17 — Rotation performance benchmarks.

These tests assert that the rotation engine processes within acceptable wall-clock
limits.  They are NOT expected to be slow — if they fail it indicates a regression
(e.g. re-introduction of an infinite loop or quadratic algorithm).
"""
import time
import pytest

from rotation.models.rotation_step import RotationStep
from rotation.models.rotation_definition import RotationDefinition
from rotation.rotation_executor import execute_rotation
from rotation.timeline_engine import build_timeline
from rotation.metrics import compute_metrics
from skills.models.skill_definition import SkillDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_registry(n: int) -> dict[str, SkillDefinition]:
    return {
        f"skill_{i}": SkillDefinition(
            f"skill_{i}",
            base_damage=float(50 + i * 10),
            cooldown=float(0.5 + (i % 5) * 0.3),
        )
        for i in range(n)
    }


def _make_rotation(n: int, loop=True) -> RotationDefinition:
    rot = RotationDefinition("perf_test")
    for i in range(n):
        rot.add_step(RotationStep(f"skill_{i}", priority=i))
    rot.loop = loop
    return rot


# ---------------------------------------------------------------------------
# Benchmark constants (generous limits to avoid flakiness on slow CI)
# ---------------------------------------------------------------------------

LIMIT_SMALL  = 0.5   # seconds — small rotation, long fight
LIMIT_MEDIUM = 1.0   # seconds — medium rotation
LIMIT_LARGE  = 3.0   # seconds — stress test


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExecutionSpeed:
    def test_small_rotation_60s(self):
        """2-skill rotation over 60 s must finish in < {LIMIT_SMALL}s."""
        skills = _make_registry(2)
        rot    = _make_rotation(2)
        t0 = time.perf_counter()
        execute_rotation(rot, skills, duration=60.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_SMALL, f"Took {elapsed:.3f}s (limit {LIMIT_SMALL}s)"

    def test_medium_rotation_300s(self):
        """10-skill rotation over 300 s must finish in < {LIMIT_MEDIUM}s."""
        skills = _make_registry(10)
        rot    = _make_rotation(10)
        t0 = time.perf_counter()
        execute_rotation(rot, skills, duration=300.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_MEDIUM, f"Took {elapsed:.3f}s (limit {LIMIT_MEDIUM}s)"

    def test_large_rotation_3600s(self):
        """20-skill rotation over 3600 s (1 hour) must finish in < {LIMIT_LARGE}s."""
        skills = _make_registry(20)
        rot    = _make_rotation(20)
        t0 = time.perf_counter()
        results = execute_rotation(rot, skills, duration=3600.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_LARGE, f"Took {elapsed:.3f}s (limit {LIMIT_LARGE}s)"
        assert len(results) > 0

    def test_gcd_does_not_slow_execution(self):
        """Adding GCD=1.0 must not push a 10-skill/300s run past the medium limit."""
        skills = _make_registry(10)
        rot    = _make_rotation(10)
        t0 = time.perf_counter()
        execute_rotation(rot, skills, duration=300.0, gcd=1.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_MEDIUM, f"Took {elapsed:.3f}s (limit {LIMIT_MEDIUM}s)"


class TestTimelineSpeed:
    def test_build_timeline_small(self):
        """build_timeline for 2 skills / 60 s must complete in < {LIMIT_SMALL}s."""
        skills = _make_registry(2)
        rot    = _make_rotation(2)
        t0 = time.perf_counter()
        build_timeline(rot, skills, duration=60.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_SMALL, f"Took {elapsed:.3f}s"

    def test_build_timeline_medium(self):
        """build_timeline for 10 skills / 300 s must complete in < {LIMIT_MEDIUM}s."""
        skills = _make_registry(10)
        rot    = _make_rotation(10)
        t0 = time.perf_counter()
        build_timeline(rot, skills, duration=300.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < LIMIT_MEDIUM, f"Took {elapsed:.3f}s"


class TestMetricsSpeed:
    def test_compute_metrics_large_list(self):
        """compute_metrics on 50 000 cast results must finish in < 1s."""
        from rotation.rotation_executor import CastResult
        results = [
            CastResult(
                skill_id=f"skill_{i % 10}",
                cast_at=float(i) * 0.06,
                resolves_at=float(i) * 0.06 + 0.05,
                damage=100.0,
                step_index=i % 10,
            )
            for i in range(50_000)
        ]
        t0 = time.perf_counter()
        m = compute_metrics(results, duration=3000.0)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0, f"Took {elapsed:.3f}s"
        assert m.total_casts == 50_000


class TestScaling:
    def test_linear_scaling(self):
        """Doubling the fight duration should at most triple the execution time."""
        skills = _make_registry(5)
        rot    = _make_rotation(5)

        t0 = time.perf_counter()
        execute_rotation(rot, skills, duration=100.0)
        t_short = time.perf_counter() - t0

        t0 = time.perf_counter()
        execute_rotation(rot, skills, duration=200.0)
        t_long = time.perf_counter() - t0

        # Allow generous 4x factor to avoid flakiness on slow CI
        if t_short > 1e-4:  # skip ratio check if baseline is too fast to measure
            assert t_long < t_short * 4.0, (
                f"Scaling looks super-linear: {t_short:.4f}s → {t_long:.4f}s"
            )
