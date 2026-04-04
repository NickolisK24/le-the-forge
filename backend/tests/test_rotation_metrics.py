"""G10 — RotationMetrics tests"""
import pytest
from rotation.metrics import compute_metrics, RotationMetrics
from rotation.rotation_executor import CastResult


def _cast(skill_id, cast_at, resolves_at, damage=100.0, step_index=0):
    return CastResult(skill_id=skill_id, cast_at=cast_at,
                      resolves_at=resolves_at, damage=damage, step_index=step_index)


class TestIdleDetection:
    def test_empty_results(self):
        m = compute_metrics([], duration=10.0)
        assert m.total_casts == 0
        assert m.total_damage == 0.0
        assert m.idle_time == 10.0
        assert m.efficiency == 0.0

    def test_full_uptime_instant_casts(self):
        # Instant casts (0 duration) → 0 active time → all idle
        results = [_cast("a", 0.0, 0.0), _cast("a", 1.0, 1.0)]
        m = compute_metrics(results, duration=2.0)
        assert m.idle_time == pytest.approx(2.0)
        assert m.uptime_fraction == pytest.approx(0.0)

    def test_cast_time_reduces_idle(self):
        # 1s cast from 0→1, then 1s cast from 1→2
        results = [_cast("a", 0.0, 1.0), _cast("a", 1.0, 2.0)]
        m = compute_metrics(results, duration=2.0)
        assert m.idle_time == pytest.approx(0.0)
        assert m.uptime_fraction == pytest.approx(1.0)


class TestEfficiencyCalculation:
    def test_efficiency_equals_uptime(self):
        results = [_cast("a", 0.0, 0.5)]
        m = compute_metrics(results, duration=1.0)
        assert m.efficiency == pytest.approx(m.uptime_fraction)

    def test_efficiency_zero_no_casts(self):
        assert compute_metrics([], 10.0).efficiency == 0.0

    def test_total_damage_summed(self):
        results = [_cast("a", 0.0, 0.0, damage=200.0), _cast("b", 1.0, 1.0, damage=150.0)]
        m = compute_metrics(results, duration=2.0)
        assert m.total_damage == pytest.approx(350.0)

    def test_cast_counts(self):
        results = [_cast("a", 0.0, 0.0), _cast("b", 1.0, 1.0), _cast("a", 2.0, 2.0)]
        m = compute_metrics(results, duration=3.0)
        assert m.cast_counts == {"a": 2, "b": 1}

    def test_damage_by_skill(self):
        results = [_cast("a", 0.0, 0.0, 100.0), _cast("a", 1.0, 1.0, 150.0), _cast("b", 2.0, 2.0, 50.0)]
        m = compute_metrics(results, duration=3.0)
        assert m.damage_by_skill["a"] == pytest.approx(250.0)
        assert m.damage_by_skill["b"] == pytest.approx(50.0)

    def test_dps_computed(self):
        results = [_cast("a", 0.0, 2.0, 200.0)]
        m = compute_metrics(results, duration=10.0)
        assert m.dps == pytest.approx(200.0 / 2.0)

    def test_avg_cast_interval(self):
        results = [_cast("a", 0.0, 0.0), _cast("a", 2.0, 2.0), _cast("a", 4.0, 4.0)]
        m = compute_metrics(results, duration=5.0)
        assert m.avg_cast_interval == pytest.approx(2.0)

    def test_single_cast_interval_zero(self):
        results = [_cast("a", 0.0, 0.0)]
        m = compute_metrics(results, duration=5.0)
        assert m.avg_cast_interval == 0.0
