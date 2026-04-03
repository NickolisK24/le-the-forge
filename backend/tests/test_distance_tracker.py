"""L13 — DistanceTracker tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.distance.distance_tracker import DistanceTracker, DistanceEvent


class TestTracking:
    def test_track_pair_and_update(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        positions = {"a": Vector2(0, 0), "b": Vector2(3, 4)}
        tracker.update(positions, now=0.0)
        assert tracker.current_distance("a", "b") == pytest.approx(5.0)

    def test_symmetric_key_lookup(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        positions = {"a": Vector2(0, 0), "b": Vector2(5, 0)}
        tracker.update(positions, now=0.0)
        # Both orderings should work
        assert tracker.current_distance("a", "b") == pytest.approx(5.0)
        assert tracker.current_distance("b", "a") == pytest.approx(5.0)

    def test_no_distance_before_update(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        assert tracker.current_distance("a", "b") is None

    def test_missing_position_skipped(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        positions = {"a": Vector2(0, 0)}  # b missing
        events = tracker.update(positions, now=0.0)
        assert tracker.current_distance("a", "b") is None
        assert events == []

    def test_untrack_pair(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        tracker.untrack_pair("a", "b")
        assert ("a", "b") not in tracker.tracked_pairs() and ("b", "a") not in tracker.tracked_pairs()


class TestRangeEvents:
    def test_enter_range_event(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=10.0)
        events = tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=1.0)
        assert any(e.event_type == "enter_range" for e in events)

    def test_leave_range_event(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=10.0)
        tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=0.0)
        # Now move b far away
        events = tracker.update({"a": Vector2(0, 0), "b": Vector2(20, 0)}, now=1.0)
        assert any(e.event_type == "leave_range" for e in events)

    def test_no_event_when_still_in_range(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=10.0)
        tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=0.0)
        events = tracker.update({"a": Vector2(0, 0), "b": Vector2(6, 0)}, now=1.0)
        assert not any(e.event_type in ("enter_range", "leave_range") for e in events)

    def test_is_in_range_true(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=10.0)
        tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=0.0)
        assert tracker.is_in_range("a", "b") is True

    def test_is_in_range_false(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=3.0)
        tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=0.0)
        assert tracker.is_in_range("a", "b") is False

    def test_no_threshold_no_events(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b", threshold=None)
        events = tracker.update({"a": Vector2(0, 0), "b": Vector2(5, 0)}, now=0.0)
        assert events == []


class TestHistory:
    def test_history_accumulates(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        for t in range(5):
            tracker.update({"a": Vector2(0, 0), "b": Vector2(t, 0)}, now=float(t))
        history = tracker.distance_history("a", "b")
        assert len(history) == 5

    def test_history_entries_have_time_and_distance(self):
        tracker = DistanceTracker()
        tracker.track_pair("a", "b")
        tracker.update({"a": Vector2(0, 0), "b": Vector2(3, 4)}, now=2.0)
        history = tracker.distance_history("a", "b")
        t, d = history[0]
        assert t == pytest.approx(2.0)
        assert d == pytest.approx(5.0)
