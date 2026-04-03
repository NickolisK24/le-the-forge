"""L12 — MovementTimelineSynchronizer integration tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.linear_behavior import LinearBehavior
from movement.behaviors.aggressive_behavior import AggressiveBehavior
from movement.behaviors.random_behavior import RandomBehavior
from movement.timeline.movement_sync import MovementTimelineSynchronizer, MovementRecord


def _state(eid: str, pos: Vector2, target: Vector2 = None, max_speed: float = 10.0) -> MovementState:
    s = MovementState(entity_id=eid, position=pos, max_speed=max_speed)
    if target:
        s.set_target(target)
    return s


class TestTickCounting:
    def test_invalid_tick_size_raises(self):
        with pytest.raises(ValueError):
            MovementTimelineSynchronizer(tick_size=0.0)

    def test_invalid_duration_raises(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        with pytest.raises(ValueError):
            sync.run({}, {}, duration=0.0)

    def test_exact_tick_count_no_float_drift(self):
        """10 ticks of 0.1s = exactly 1.0s — must produce exactly 10 records per entity."""
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        s = _state("e1", Vector2(0, 0), target=Vector2(100, 0))
        b = LinearBehavior(speed=5.0)
        records = sync.run({"e1": s}, {"e1": b}, duration=1.0)
        entity_records = [r for r in records if r.entity_id == "e1"]
        assert len(entity_records) == 10

    def test_no_records_when_disabled(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1, record_snapshots=False)
        s = _state("e1", Vector2(0, 0))
        b = LinearBehavior()
        records = sync.run({"e1": s}, {"e1": b}, duration=1.0)
        assert records == []

    def test_timestamps_correct(self):
        sync = MovementTimelineSynchronizer(tick_size=0.5)
        s = _state("e1", Vector2(0, 0), target=Vector2(100, 0))
        b = LinearBehavior(speed=5.0)
        records = sync.run({"e1": s}, {"e1": b}, duration=1.0)
        times = [r.time for r in records if r.entity_id == "e1"]
        assert times[0] == pytest.approx(0.5)
        assert times[1] == pytest.approx(1.0)


class TestMovementApplication:
    def test_entity_moves_toward_target(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        s = _state("e1", Vector2(0, 0), target=Vector2(10, 0))
        b = LinearBehavior(speed=5.0)
        sync.run({"e1": s}, {"e1": b}, duration=1.0)
        assert s.position.x > 0

    def test_multiple_entities_independent(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        states = {
            "a": _state("a", Vector2(0, 0), target=Vector2(10, 0)),
            "b": _state("b", Vector2(0, 0), target=Vector2(-10, 0)),
        }
        behaviors = {
            "a": LinearBehavior(speed=5.0),
            "b": LinearBehavior(speed=5.0),
        }
        sync.run(states, behaviors, duration=1.0)
        assert states["a"].position.x > 0
        assert states["b"].position.x < 0

    def test_distance_moved_recorded(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        s = _state("e1", Vector2(0, 0), target=Vector2(100, 0))
        b = LinearBehavior(speed=5.0)
        sync.run({"e1": s}, {"e1": b}, duration=1.0)
        assert s.distance_moved > 0

    def test_record_has_expected_fields(self):
        sync = MovementTimelineSynchronizer(tick_size=0.5)
        s = _state("e1", Vector2(0, 0), target=Vector2(5, 0))
        b = LinearBehavior(speed=3.0)
        records = sync.run({"e1": s}, {"e1": b}, duration=0.5)
        r = records[0]
        assert hasattr(r, "time") and hasattr(r, "entity_id")
        assert hasattr(r, "position") and hasattr(r, "behavior_type")


class TestAvoidance:
    def test_avoidance_enabled_no_crash(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1, avoidance_radius=1.0)
        states = {
            "a": _state("a", Vector2(0, 0)),
            "b": _state("b", Vector2(0.3, 0)),  # close — will trigger avoidance
        }
        behaviors = {
            "a": RandomBehavior(speed=2.0, seed=1),
            "b": RandomBehavior(speed=2.0, seed=2),
        }
        records = sync.run(states, behaviors, duration=1.0)
        assert len(records) > 0

    def test_avoidance_pushes_apart(self):
        sync = MovementTimelineSynchronizer(tick_size=0.05, avoidance_radius=2.0)
        # Two entities starting at same position
        states = {
            "a": _state("a", Vector2(0, 0)),
            "b": _state("b", Vector2(0.1, 0)),
        }
        behaviors = {"a": LinearBehavior(), "b": LinearBehavior()}
        sync.run(states, behaviors, duration=0.5)
        dist = states["a"].position.distance_to(states["b"].position)
        assert dist > 0


class TestContextPropagation:
    def test_aggressive_uses_player_position_from_context(self):
        sync = MovementTimelineSynchronizer(tick_size=0.1)
        s = _state("enemy", Vector2(0, 0))
        b = AggressiveBehavior(speed=5.0)
        ctx = {"enemy": {"player_position": Vector2(10, 0)}}
        sync.run({"enemy": s}, {"enemy": b}, contexts=ctx, duration=1.0)
        assert s.position.x > 0
