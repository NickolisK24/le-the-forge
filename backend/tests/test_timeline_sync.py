"""H12 — Timeline State Synchronization tests."""
import pytest
from state.state_engine import SimulationState
from state.timeline_sync import TimelineSynchronizer
from status.models.status_effect import StatusEffect
from status.status_manager import StatusManager


def _state():
    return SimulationState(
        player_health=1000.0, player_max_health=1000.0,
        target_health=1000.0, target_max_health=1000.0,
    )


class TestStateAlignment:
    def test_elapsed_time_advances(self):
        sync = TimelineSynchronizer(tick_size=0.1)
        state = _state()
        records = sync.run(state, duration=1.0)
        assert abs(state.elapsed_time - 1.0) < 1e-6

    def test_records_count(self):
        sync = TimelineSynchronizer(tick_size=0.1)
        records = sync.run(_state(), duration=1.0)
        assert len(records) == 10

    def test_no_records_when_disabled(self):
        sync = TimelineSynchronizer(tick_size=0.1, record_snapshots=False)
        records = sync.run(_state(), duration=1.0)
        assert records == []


class TestEventTimingAccuracy:
    def test_status_expires_within_sync(self):
        shock = StatusEffect("shock", duration=0.5)
        mgr = StatusManager()
        mgr.register(shock)
        state = _state()
        mgr.apply("shock", now=0.0)
        state.apply_status("shock", 1)

        sync = TimelineSynchronizer(tick_size=0.1)
        records = sync.run(state, duration=1.0, status_mgr=mgr)

        # After 1 second, shock (duration=0.5) should have expired
        assert mgr.stack_count("shock") == 0

    def test_tick_timestamps_accurate(self):
        sync = TimelineSynchronizer(tick_size=0.5)
        state = _state()
        records = sync.run(state, duration=1.0)
        assert len(records) == 2
        assert abs(records[0].time - 0.5) < 1e-6
        assert abs(records[1].time - 1.0) < 1e-6

    def test_invalid_tick_size_raises(self):
        with pytest.raises(ValueError):
            TimelineSynchronizer(tick_size=0.0)

    def test_invalid_duration_raises(self):
        sync = TimelineSynchronizer()
        with pytest.raises(ValueError):
            sync.run(_state(), duration=0.0)


class TestExactTickCounting:
    def test_exactly_10_ticks_for_1s_at_0_1(self):
        """tick_size=0.1, duration=1.0 must produce exactly 10 ticks (no float drift)."""
        sync = TimelineSynchronizer(tick_size=0.1)
        records = sync.run(_state(), duration=1.0)
        assert len(records) == 10

    def test_elapsed_time_exact_after_run(self):
        sync = TimelineSynchronizer(tick_size=0.1)
        state = _state()
        sync.run(state, duration=1.0)
        assert abs(state.elapsed_time - 1.0) < 1e-9
