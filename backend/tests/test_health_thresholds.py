"""H10 — Health Threshold Logic tests."""
import pytest
from state.health_thresholds import HealthThreshold, HealthThresholdTracker


class TestThresholdDetection:
    def test_fires_when_below(self):
        fired = []
        t = HealthThreshold(0.5, "below", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.4)
        assert len(fired) == 1
        assert fired[0] == pytest.approx(0.4)

    def test_does_not_fire_when_above(self):
        fired = []
        t = HealthThreshold(0.5, "below", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.7)
        assert fired == []

    def test_fires_only_once(self):
        fired = []
        t = HealthThreshold(0.5, "below", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.4)
        tracker.update(0.3)
        assert len(fired) == 1


class TestTransitionBoundaries:
    def test_exactly_at_threshold_below(self):
        fired = []
        t = HealthThreshold(0.5, "below", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.5)   # 0.5 <= 0.5 → fires
        assert len(fired) == 1

    def test_above_fires_when_equal(self):
        fired = []
        t = HealthThreshold(0.8, "above", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.8)
        assert len(fired) == 1


class TestEdgeCases:
    def test_invalid_pct_raises(self):
        tracker = HealthThresholdTracker()
        with pytest.raises(ValueError):
            tracker.update(1.1)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            HealthThreshold(1.5, "below")

    def test_reset_allows_refire(self):
        fired = []
        t = HealthThreshold(0.5, "below", callback=lambda th, act: fired.append(act))
        tracker = HealthThresholdTracker()
        tracker.add_threshold(t)
        tracker.update(0.4)
        tracker.reset()
        tracker.update(0.3)
        assert len(fired) == 2
