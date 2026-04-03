"""K15 — Spatial debug logger tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile
from debug.spatial_logger import SpatialLogger, SpatialLogEntry


def _proj() -> Projectile:
    return Projectile(
        origin=Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=10.0,
        damage=50.0,
        skill_id="arrow",
    )


class TestLogging:
    def test_initial_empty(self):
        logger = SpatialLogger()
        assert logger.count == 0
        assert logger.entries() == []

    def test_log_spawn(self):
        logger = SpatialLogger()
        logger.log_projectile_spawn(_proj(), time=0.0)
        assert logger.count == 1
        assert logger.entries()[0]["event_type"] == "spawn"

    def test_log_hit(self):
        logger = SpatialLogger()
        logger.log_hit("enemy_1", damage=75.0, position=Vector2(3, 0), is_critical=True, time=0.5)
        e = logger.entries()[0]
        assert e["event_type"] == "hit"
        assert e["payload"]["target_id"] == "enemy_1"
        assert e["payload"]["is_critical"] is True

    def test_log_miss(self):
        logger = SpatialLogger()
        logger.log_miss("proj_1", position=Vector2(5, 0))
        assert logger.entries()[0]["event_type"] == "miss"

    def test_log_kill(self):
        logger = SpatialLogger()
        logger.log_target_killed("boss", time=2.3)
        e = logger.entries()[0]
        assert e["event_type"] == "kill"
        assert e["payload"]["target_id"] == "boss"

    def test_log_aoe(self):
        logger = SpatialLogger()
        logger.log_aoe({"shape": "circle"}, targets_hit=3, total_damage=300.0, time=1.0)
        e = logger.entries()[0]
        assert e["event_type"] == "aoe"
        assert e["payload"]["targets_hit"] == 3

    def test_log_expire(self):
        logger = SpatialLogger()
        logger.log_expire("proj_x", distance_traveled=42.5, time=1.5)
        e = logger.entries()[0]
        assert e["event_type"] == "expire"

    def test_entries_by_type(self):
        logger = SpatialLogger()
        logger.log_projectile_spawn(_proj())
        logger.log_hit("t1", 50.0, Vector2(1, 0))
        logger.log_hit("t2", 50.0, Vector2(2, 0))
        hits = logger.entries_by_type("hit")
        assert len(hits) == 2

    def test_clear(self):
        logger = SpatialLogger()
        logger.log_projectile_spawn(_proj())
        logger.clear()
        assert logger.count == 0


class TestRingBuffer:
    def test_capacity_enforced(self):
        logger = SpatialLogger(capacity=3)
        for i in range(5):
            logger.log_miss(f"p{i}", Vector2(i, 0))
        assert logger.count == 3

    def test_oldest_entry_dropped(self):
        logger = SpatialLogger(capacity=2)
        logger.log_miss("first", Vector2(0, 0))
        logger.log_miss("second", Vector2(1, 0))
        logger.log_miss("third", Vector2(2, 0))
        entries = logger.entries()
        # "first" should have been dropped
        payloads = [e["payload"]["projectile_id"] for e in entries]
        assert "first" not in payloads
        assert "third" in payloads

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError):
            SpatialLogger(capacity=0)
