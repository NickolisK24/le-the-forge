"""H11 — Time Window Conditions tests."""
import pytest
from conditions.time_window import TimeWindow, TimeWindowTracker


class TestWindowActivation:
    def test_active_within_window(self):
        w = TimeWindow("opener", start=0.0, end=10.0)
        assert w.is_active(5.0) is True

    def test_inactive_before_start(self):
        w = TimeWindow("burn", start=5.0, end=15.0)
        assert w.is_active(3.0) is False

    def test_open_ended_window_never_expires(self):
        w = TimeWindow("endgame", start=10.0)
        assert w.is_active(9999.0) is True


class TestWindowExpiration:
    def test_inactive_at_end_boundary(self):
        w = TimeWindow("opener", start=0.0, end=10.0)
        assert w.is_active(10.0) is False  # half-open [0, 10)

    def test_inactive_past_end(self):
        w = TimeWindow("opener", start=0.0, end=10.0)
        assert w.is_active(11.0) is False

    def test_duration_property(self):
        w = TimeWindow("burn", start=5.0, end=15.0)
        assert w.duration == pytest.approx(10.0)

    def test_open_ended_duration_is_none(self):
        w = TimeWindow("forever", start=0.0)
        assert w.duration is None


class TestOverlappingWindows:
    def test_two_overlapping_windows(self):
        tracker = TimeWindowTracker()
        tracker.register(TimeWindow("a", start=0.0, end=10.0))
        tracker.register(TimeWindow("b", start=5.0, end=15.0))
        active = tracker.active_windows(7.0)
        assert set(active) == {"a", "b"}

    def test_non_overlapping(self):
        tracker = TimeWindowTracker()
        tracker.register(TimeWindow("a", start=0.0,  end=5.0))
        tracker.register(TimeWindow("b", start=10.0, end=15.0))
        assert tracker.active_windows(7.0) == []


class TestValidation:
    def test_negative_start_raises(self):
        with pytest.raises(ValueError):
            TimeWindow("x", start=-1.0)

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError):
            TimeWindow("x", start=5.0, end=3.0)

    def test_end_equals_start_raises(self):
        with pytest.raises(ValueError):
            TimeWindow("x", start=5.0, end=5.0)
