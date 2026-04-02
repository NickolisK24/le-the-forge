"""Tests for encounter timeline engine (Step 99)."""

import pytest
from encounter.timeline import EncounterTimeline, EventType, TimelineEvent


def _event(t, etype=EventType.CUSTOM, end=-1.0, **payload):
    return TimelineEvent(event_type=etype, start_time=t, end_time=end,
                         payload=payload)


class TestTimelineEvent:
    def test_negative_start_raises(self):
        with pytest.raises(ValueError):
            TimelineEvent(EventType.CUSTOM, start_time=-1.0)

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError):
            TimelineEvent(EventType.CUSTOM, start_time=5.0, end_time=3.0)

    def test_instantaneous(self):
        e = _event(1.0)
        assert e.is_instantaneous is True
        assert e.duration == pytest.approx(0.0)

    def test_duration(self):
        e = _event(2.0, end=5.0)
        assert e.duration == pytest.approx(3.0)


class TestEncounterTimeline:
    def test_empty_advance_returns_empty(self):
        tl = EncounterTimeline()
        assert tl.advance(10.0) == []

    def test_event_fires_at_correct_time(self):
        tl = EncounterTimeline([_event(5.0)])
        assert tl.advance(4.9) == []
        fired = tl.advance(5.0)
        assert len(fired) == 1

    def test_event_fires_only_once(self):
        tl = EncounterTimeline([_event(5.0)])
        tl.advance(5.0)
        assert tl.advance(10.0) == []

    def test_multiple_events_ordered(self):
        tl = EncounterTimeline([_event(10.0), _event(5.0), _event(1.0)])
        fired = tl.advance(10.0)
        assert len(fired) == 3
        times = [e.start_time for e in fired]
        assert times == sorted(times)

    def test_events_fire_in_batches(self):
        tl = EncounterTimeline([_event(1.0), _event(2.0), _event(3.0)])
        assert len(tl.advance(2.0)) == 2
        assert len(tl.advance(3.0)) == 1

    def test_backward_time_raises(self):
        tl = EncounterTimeline([_event(5.0)])
        tl.advance(5.0)
        with pytest.raises(ValueError):
            tl.advance(3.0)

    def test_add_event_maintains_order(self):
        tl = EncounterTimeline([_event(3.0)])
        tl.add_event(_event(1.0))
        tl.add_event(_event(2.0))
        fired = tl.advance(3.0)
        times = [e.start_time for e in fired]
        assert times == [1.0, 2.0, 3.0]

    def test_pending_events(self):
        tl = EncounterTimeline([_event(1.0), _event(2.0), _event(3.0)])
        tl.advance(1.0)
        assert len(tl.pending_events()) == 2

    def test_reset_unfires_all(self):
        tl = EncounterTimeline([_event(1.0), _event(2.0)])
        tl.advance(2.0)
        tl.reset()
        assert len(tl.advance(2.0)) == 2

    def test_event_type_preserved(self):
        tl = EncounterTimeline([_event(1.0, etype=EventType.SPAWN)])
        fired = tl.advance(1.0)
        assert fired[0].event_type == EventType.SPAWN

    def test_payload_preserved(self):
        e = TimelineEvent(EventType.CUSTOM, 1.0, payload={"count": 3})
        tl = EncounterTimeline([e])
        fired = tl.advance(1.0)
        assert fired[0].payload["count"] == 3

    def test_current_time_tracks(self):
        tl = EncounterTimeline()
        tl.advance(5.5)
        assert tl.current_time == pytest.approx(5.5)
