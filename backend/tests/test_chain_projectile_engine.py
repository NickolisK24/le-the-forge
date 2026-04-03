"""K10 — Spatial chain projectile engine tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.chain_engine import SpatialChainEngine, SpatialChainResult
from targets.models.target_entity import TargetEntity


def _target(tid: str, hp: float = 1000.0) -> TargetEntity:
    return TargetEntity(target_id=tid, max_health=hp)


class TestBasicChain:
    def test_single_target_no_bounces(self):
        eng = SpatialChainEngine()
        primary = _target("boss")
        result = eng.execute(
            base_damage=100.0,
            primary=primary,
            primary_position=Vector2(0, 0),
            targets_with_positions=[(primary, Vector2(0, 0))],
            max_bounces=0,
        )
        assert result.hops_executed == 1
        assert result.total_damage == pytest.approx(100.0)

    def test_two_targets_one_bounce(self):
        eng = SpatialChainEngine()
        t1 = _target("t1")
        t2 = _target("t2")
        result = eng.execute(
            base_damage=100.0,
            primary=t1,
            primary_position=Vector2(0, 0),
            targets_with_positions=[(t1, Vector2(0, 0)), (t2, Vector2(2, 0))],
            max_bounces=1,
            decay=0.7,
        )
        assert result.hops_executed == 2
        assert result.bounces[1].target_id == "t2"
        assert result.bounces[1].damage_dealt == pytest.approx(70.0)

    def test_chain_applies_decay(self):
        eng = SpatialChainEngine()
        t1, t2, t3 = _target("t1"), _target("t2"), _target("t3")
        result = eng.execute(
            base_damage=100.0,
            primary=t1,
            primary_position=Vector2(0, 0),
            targets_with_positions=[
                (t1, Vector2(0, 0)),
                (t2, Vector2(1, 0)),
                (t3, Vector2(2, 0)),
            ],
            max_bounces=2,
            decay=0.5,
        )
        assert result.bounces[0].damage_dealt == pytest.approx(100.0)
        assert result.bounces[1].damage_dealt == pytest.approx(50.0)
        assert result.bounces[2].damage_dealt == pytest.approx(25.0)

    def test_chain_bounces_to_nearest(self):
        eng = SpatialChainEngine()
        primary = _target("primary")
        near = _target("near")
        far = _target("far")
        result = eng.execute(
            base_damage=100.0,
            primary=primary,
            primary_position=Vector2(0, 0),
            targets_with_positions=[
                (primary, Vector2(0, 0)),
                (near, Vector2(1, 0)),
                (far, Vector2(10, 0)),
            ],
            max_bounces=1,
        )
        assert result.bounces[1].target_id == "near"

    def test_max_chain_range_limits_bounces(self):
        eng = SpatialChainEngine()
        t1 = _target("t1")
        t2 = _target("t2")
        result = eng.execute(
            base_damage=100.0,
            primary=t1,
            primary_position=Vector2(0, 0),
            targets_with_positions=[(t1, Vector2(0, 0)), (t2, Vector2(20, 0))],
            max_bounces=1,
            max_chain_range=5.0,
        )
        # t2 is out of range
        assert result.hops_executed == 1

    def test_no_rehit_same_target(self):
        eng = SpatialChainEngine()
        t1 = _target("t1")
        result = eng.execute(
            base_damage=100.0,
            primary=t1,
            primary_position=Vector2(0, 0),
            targets_with_positions=[(t1, Vector2(0, 0))],
            max_bounces=2,
        )
        # Only 1 hop — no other targets to bounce to
        assert result.hops_executed == 1

    def test_invalid_max_bounces_raises(self):
        eng = SpatialChainEngine()
        t = _target("t1")
        with pytest.raises(ValueError):
            eng.execute(100.0, t, Vector2(0, 0), [(t, Vector2(0, 0))], max_bounces=-1)

    def test_invalid_decay_raises(self):
        eng = SpatialChainEngine()
        t = _target("t1")
        with pytest.raises(ValueError):
            eng.execute(100.0, t, Vector2(0, 0), [(t, Vector2(0, 0))], decay=0.0)

    def test_damage_applied_to_targets(self):
        eng = SpatialChainEngine()
        t1 = _target("t1", hp=1000.0)
        t2 = _target("t2", hp=1000.0)
        eng.execute(
            base_damage=200.0,
            primary=t1,
            primary_position=Vector2(0, 0),
            targets_with_positions=[(t1, Vector2(0, 0)), (t2, Vector2(1, 0))],
            max_bounces=1,
            decay=0.5,
        )
        assert t1.current_health == pytest.approx(800.0)
        assert t2.current_health == pytest.approx(900.0)
