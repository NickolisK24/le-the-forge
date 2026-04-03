"""L18 — MovementLogger tests."""
import pytest
from spatial.models.vector2 import Vector2
from debug.movement_logger import MovementLogger


class TestLogging:
    def test_initial_empty(self):
        log = MovementLogger()
        assert log.count == 0

    def test_log_move(self):
        log = MovementLogger()
        log.log_move("e1", Vector2(0, 0), Vector2(1, 0), distance=1.0, behavior="linear")
        assert log.count == 1
        assert log.entries()[0]["event_type"] == "move"

    def test_log_behavior_change(self):
        log = MovementLogger()
        log.log_behavior_change("e1", "idle", "aggressive", time=0.5)
        e = log.entries()[0]
        assert e["event_type"] == "behavior_change"
        assert e["payload"]["old_behavior"] == "idle"

    def test_log_kite_event(self):
        log = MovementLogger()
        log.log_kite_event(Vector2(0, 0), 3.5, time=1.0)
        e = log.entries()[0]
        assert e["event_type"] == "kite"
        assert "closest_enemy_dist" in e["payload"]

    def test_log_range_event(self):
        log = MovementLogger()
        log.log_range_event("enter_range", "player", "enemy_1", 4.5, time=2.0)
        e = log.entries()[0]
        assert e["event_type"] == "enter_range"
        assert e["payload"]["entity_a"] == "player"

    def test_log_stop(self):
        log = MovementLogger()
        log.log_stop("e1", Vector2(3, 4), time=5.0)
        assert log.entries()[0]["event_type"] == "stop"

    def test_entries_by_type(self):
        log = MovementLogger()
        log.log_kite_event(Vector2(0, 0), 2.0)
        log.log_kite_event(Vector2(1, 0), 3.0)
        log.log_stop("e1", Vector2(0, 0))
        kites = log.entries_by_type("kite")
        assert len(kites) == 2

    def test_clear(self):
        log = MovementLogger()
        log.log_stop("e1", Vector2(0, 0))
        log.clear()
        assert log.count == 0


class TestRingBuffer:
    def test_capacity_enforced(self):
        log = MovementLogger(capacity=3)
        for i in range(5):
            log.log_stop(f"e{i}", Vector2(i, 0))
        assert log.count == 3

    def test_oldest_evicted(self):
        log = MovementLogger(capacity=2)
        log.log_stop("first", Vector2(0, 0))
        log.log_stop("second", Vector2(1, 0))
        log.log_stop("third", Vector2(2, 0))
        entries = log.entries()
        entity_ids = [e["payload"]["entity_id"] for e in entries]
        assert "first" not in entity_ids
        assert "third" in entity_ids

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError):
            MovementLogger(capacity=0)

    def test_capacity_property(self):
        log = MovementLogger(capacity=100)
        assert log.capacity == 100
