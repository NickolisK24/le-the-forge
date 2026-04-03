"""I13 — Multi-Target Metrics tests."""
import pytest
from metrics.multi_target_metrics import MultiTargetMetrics


class TestKillCountingAccuracy:
    def test_no_kills_initially(self):
        m = MultiTargetMetrics()
        assert m.total_kills == 0

    def test_kills_counted(self):
        m = MultiTargetMetrics()
        m.record_kill("t1", 2.0)
        m.record_kill("t2", 4.0)
        assert m.total_kills == 2

    def test_damage_accumulated(self):
        m = MultiTargetMetrics()
        m.record_hit("t1", 300.0)
        m.record_hit("t1", 200.0)
        assert m.damage_per_target()["t1"] == pytest.approx(500.0)


class TestTimeTrackingCorrectness:
    def test_time_to_clear_is_last_kill(self):
        m = MultiTargetMetrics()
        m.record_kill("t1", 2.0)
        m.record_kill("t2", 5.0)
        assert m.time_to_clear() == pytest.approx(5.0)

    def test_time_to_clear_none_if_no_kills(self):
        m = MultiTargetMetrics()
        assert m.time_to_clear() is None

    def test_kill_times_dict(self):
        m = MultiTargetMetrics()
        m.record_kill("t1", 3.0)
        assert m.kill_times()["t1"] == pytest.approx(3.0)


class TestOverkillDetection:
    def test_overkill_tracked(self):
        m = MultiTargetMetrics()
        m.record_hit("t1", 900.0, overkill=400.0)
        assert m.overkill_waste()["t1"] == pytest.approx(400.0)

    def test_summary_has_all_keys(self):
        m = MultiTargetMetrics()
        m.record_hit("t1", 100.0)
        m.record_kill("t1", 1.0)
        s = m.summary()
        assert "total_kills" in s
        assert "time_to_clear" in s
        assert "damage_per_target" in s
        assert "overkill_waste" in s
        assert "kill_times" in s
