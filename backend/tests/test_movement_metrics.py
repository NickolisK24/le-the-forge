"""L16 — MovementMetrics tests."""
import pytest
from metrics.movement_metrics import MovementMetrics


class TestRecording:
    def test_initial_state_empty(self):
        m = MovementMetrics()
        assert m.total_distance() == pytest.approx(0.0)
        assert m.kite_count() == 0

    def test_record_movement_accumulates(self):
        m = MovementMetrics()
        m.record_movement("e1", 3.0)
        m.record_movement("e1", 2.0)
        assert m.total_distance("e1") == pytest.approx(5.0)

    def test_record_movement_multiple_entities(self):
        m = MovementMetrics()
        m.record_movement("e1", 10.0)
        m.record_movement("e2", 5.0)
        assert m.total_distance() == pytest.approx(15.0)

    def test_record_time_in_range(self):
        m = MovementMetrics()
        m.record_time_in_range("player", "enemy_1", 2.0)
        m.record_time_in_range("player", "enemy_1", 1.0)
        assert m.time_in_range("player", "enemy_1") == pytest.approx(3.0)

    def test_record_time_out_of_range(self):
        m = MovementMetrics()
        m.record_time_out_of_range("player", "enemy_1", 4.0)
        assert m.time_out_of_range("player", "enemy_1") == pytest.approx(4.0)

    def test_record_reposition(self):
        m = MovementMetrics()
        m.record_reposition("player", 1.0)
        m.record_reposition("player", 3.0)
        assert m.reposition_count("player") == 2

    def test_reposition_count_all(self):
        m = MovementMetrics()
        m.record_reposition("a", 1.0)
        m.record_reposition("b", 2.0)
        assert m.reposition_count() == 2

    def test_record_kite_event(self):
        m = MovementMetrics()
        m.record_kite_event(1.0)
        m.record_kite_event(2.0)
        assert m.kite_count() == 2

    def test_record_behavior_change(self):
        m = MovementMetrics()
        m.record_behavior_change("e1", "idle", "aggressive", 0.5)
        s = m.summary()
        assert s["behavior_changes"] == 1


class TestEfficiency:
    def test_movement_efficiency(self):
        m = MovementMetrics()
        m.record_total_time(10.0)
        m.record_movement("e1", 50.0)
        assert m.movement_efficiency("e1") == pytest.approx(5.0)

    def test_efficiency_zero_when_no_time(self):
        m = MovementMetrics()
        m.record_movement("e1", 50.0)
        assert m.movement_efficiency("e1") == pytest.approx(0.0)

    def test_all_entities(self):
        m = MovementMetrics()
        m.record_movement("e1", 1.0)
        m.record_movement("e2", 2.0)
        assert set(m.all_entities()) == {"e1", "e2"}


class TestSummary:
    def test_summary_has_expected_keys(self):
        m = MovementMetrics()
        s = m.summary()
        assert "total_distance_all" in s
        assert "kite_events" in s
        assert "total_repositions" in s

    def test_reset_clears_all(self):
        m = MovementMetrics()
        m.record_movement("e1", 100.0)
        m.record_kite_event(1.0)
        m.reset()
        assert m.total_distance() == pytest.approx(0.0)
        assert m.kite_count() == 0
