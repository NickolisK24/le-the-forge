"""I11 — Multi-Target Timeline Sync tests."""
import pytest
from targets.target_templates import mob_swarm, single_boss
from state.multi_target_state import MultiTargetState
from state.multi_target_timeline_sync import MultiTargetTimelineSynchronizer


class TestTickAlignment:
    def test_elapsed_advances(self):
        state = MultiTargetState(manager=mob_swarm(3, 1e9))  # won't die
        sync = MultiTargetTimelineSynchronizer(tick_size=0.5)
        sync.run(state, duration=2.0)
        assert state.elapsed_time == pytest.approx(2.0)

    def test_records_count(self):
        state = MultiTargetState(manager=mob_swarm(2, 1e9))
        sync = MultiTargetTimelineSynchronizer(tick_size=1.0)
        records = sync.run(state, duration=3.0)
        assert len(records) == 3

    def test_no_records_when_disabled(self):
        state = MultiTargetState(manager=mob_swarm(2, 1e9))
        sync = MultiTargetTimelineSynchronizer(record_snapshots=False)
        records = sync.run(state, duration=1.0)
        assert records == []


class TestMultiTargetStateAccuracy:
    def test_stops_early_when_cleared(self):
        # Single target with tiny HP; deal massive damage → should clear quickly
        state = MultiTargetState(manager=single_boss(1.0))
        state.apply_damage("boss", 1.0)   # kill immediately
        sync = MultiTargetTimelineSynchronizer(tick_size=0.1)
        records = sync.run(state, duration=10.0)
        # Should stop after clearing (very few ticks)
        assert state.elapsed_time < 5.0

    def test_invalid_tick_size_raises(self):
        with pytest.raises(ValueError):
            MultiTargetTimelineSynchronizer(tick_size=0.0)

    def test_invalid_duration_raises(self):
        state = MultiTargetState(manager=single_boss())
        sync = MultiTargetTimelineSynchronizer()
        with pytest.raises(ValueError):
            sync.run(state, duration=0.0)


class TestExactTickCounting:
    def test_exactly_10_ticks_for_1s_at_0_1(self):
        """tick_size=0.1, duration=1.0 must produce exactly 10 ticks (no float drift)."""
        state = MultiTargetState(manager=mob_swarm(1, 1e9))
        sync = MultiTargetTimelineSynchronizer(tick_size=0.1)
        records = sync.run(state, duration=1.0)
        assert len(records) == 10

    def test_elapsed_time_exact_after_run(self):
        state = MultiTargetState(manager=mob_swarm(1, 1e9))
        sync = MultiTargetTimelineSynchronizer(tick_size=0.1)
        sync.run(state, duration=1.0)
        assert abs(state.elapsed_time - 1.0) < 1e-9
