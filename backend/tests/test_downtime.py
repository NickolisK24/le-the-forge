"""Tests for downtime simulation system (Step 102)."""

import pytest
from encounter.downtime import DowntimeTracker, DowntimeWindow


def _win(start, end, name="dt"):
    return DowntimeWindow(name=name, start_time=start, end_time=end)


class TestDowntimeWindow:
    def test_end_before_start_raises(self):
        with pytest.raises(ValueError):
            _win(5.0, 3.0)

    def test_equal_start_end_raises(self):
        with pytest.raises(ValueError):
            _win(5.0, 5.0)

    def test_duration(self):
        assert _win(2.0, 5.0).duration == pytest.approx(3.0)

    def test_is_active_inside(self):
        assert _win(2.0, 5.0).is_active(3.0) is True

    def test_is_active_at_start(self):
        assert _win(2.0, 5.0).is_active(2.0) is True

    def test_is_active_at_end_exclusive(self):
        assert _win(2.0, 5.0).is_active(5.0) is False

    def test_is_active_outside(self):
        assert _win(2.0, 5.0).is_active(1.0) is False


class TestDowntimeTracker:
    def test_no_windows_no_downtime(self):
        assert DowntimeTracker().is_downtime(5.0) is False

    def test_inside_window(self):
        t = DowntimeTracker()
        t.add_window(_win(10.0, 15.0))
        assert t.is_downtime(12.0) is True

    def test_outside_window(self):
        t = DowntimeTracker()
        t.add_window(_win(10.0, 15.0))
        assert t.is_downtime(16.0) is False

    def test_multiple_windows(self):
        t = DowntimeTracker()
        t.add_window(_win(5.0, 8.0))
        t.add_window(_win(20.0, 25.0))
        assert t.is_downtime(6.0)  is True
        assert t.is_downtime(10.0) is False
        assert t.is_downtime(22.0) is True

    def test_active_window_returns_correct(self):
        t = DowntimeTracker()
        w = _win(5.0, 10.0, name="move")
        t.add_window(w)
        assert t.active_window(7.0) is w

    def test_active_window_none_outside(self):
        t = DowntimeTracker()
        t.add_window(_win(5.0, 10.0))
        assert t.active_window(11.0) is None

    def test_total_downtime_single(self):
        t = DowntimeTracker()
        t.add_window(_win(5.0, 8.0))
        assert t.total_downtime() == pytest.approx(3.0)

    def test_total_downtime_non_overlapping(self):
        t = DowntimeTracker()
        t.add_window(_win(1.0, 3.0))
        t.add_window(_win(5.0, 8.0))
        assert t.total_downtime() == pytest.approx(5.0)

    def test_total_downtime_overlapping_merged(self):
        t = DowntimeTracker()
        t.add_window(_win(1.0, 5.0))
        t.add_window(_win(3.0, 7.0))
        assert t.total_downtime() == pytest.approx(6.0)

    def test_uptime_fraction(self):
        t = DowntimeTracker()
        t.add_window(_win(0.0, 30.0))
        assert t.uptime_fraction(100.0) == pytest.approx(0.70)

    def test_uptime_no_downtime(self):
        assert DowntimeTracker().uptime_fraction(60.0) == pytest.approx(1.0)

    def test_clear(self):
        t = DowntimeTracker()
        t.add_window(_win(1.0, 2.0))
        t.clear()
        assert t.window_count() == 0
        assert t.is_downtime(1.5) is False
