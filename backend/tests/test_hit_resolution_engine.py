"""K7 — Hit resolution engine tests."""
import random
import pytest
from spatial.models.vector2 import Vector2
from spatial.aoe.aoe_shapes import CircleShape
from combat.hit_resolution_engine import HitResolutionEngine, HitResult, AoeHitResult
from targets.models.target_entity import TargetEntity


def _target(tid: str = "t1", hp: float = 100.0) -> TargetEntity:
    return TargetEntity(target_id=tid, max_health=hp)


class TestProjectileHit:
    def test_applies_damage(self):
        eng = HitResolutionEngine()
        t = _target(hp=100.0)
        result = eng.resolve_projectile_hit(30.0, t, Vector2(0, 0))
        assert result.damage_dealt == pytest.approx(30.0)
        assert t.current_health == pytest.approx(70.0)

    def test_overkill_computed(self):
        eng = HitResolutionEngine()
        t = _target(hp=10.0)
        result = eng.resolve_projectile_hit(50.0, t, Vector2(0, 0))
        assert result.overkill == pytest.approx(40.0)

    def test_killed_flag(self):
        eng = HitResolutionEngine()
        t = _target(hp=1.0)
        result = eng.resolve_projectile_hit(100.0, t, Vector2(0, 0))
        assert result.killed is True

    def test_no_crit_by_default(self):
        eng = HitResolutionEngine(rng=random.Random(999))
        t = _target(hp=1000.0)
        result = eng.resolve_projectile_hit(10.0, t, Vector2(0, 0), crit_chance=0.0)
        assert result.is_critical is False

    def test_guaranteed_crit(self):
        eng = HitResolutionEngine(rng=random.Random(0))
        t = _target(hp=10000.0)
        result = eng.resolve_projectile_hit(100.0, t, Vector2(0, 0), crit_chance=1.0, crit_multiplier=2.0)
        assert result.is_critical is True
        assert result.raw_damage == pytest.approx(200.0)

    def test_invalid_crit_chance_raises(self):
        eng = HitResolutionEngine()
        t = _target()
        with pytest.raises(ValueError):
            eng.resolve_projectile_hit(10.0, t, Vector2(0, 0), crit_chance=1.5)

    def test_invalid_crit_multiplier_raises(self):
        eng = HitResolutionEngine()
        t = _target()
        with pytest.raises(ValueError):
            eng.resolve_projectile_hit(10.0, t, Vector2(0, 0), crit_multiplier=0.5)

    def test_position_stored(self):
        eng = HitResolutionEngine()
        pos = Vector2(3.0, 7.0)
        result = eng.resolve_projectile_hit(10.0, _target(), pos)
        assert result.position == pos


class TestAoeResolution:
    def test_hits_targets_inside_circle(self):
        eng = HitResolutionEngine()
        shape = CircleShape(center=Vector2(0, 0), radius=5.0)
        targets = [
            (_target("in1"), Vector2(2, 0)),
            (_target("in2"), Vector2(0, 3)),
            (_target("out"), Vector2(8, 0)),
        ]
        result = eng.resolve_aoe(shape, targets, base_damage=50.0)
        assert result.targets_hit == 2
        hit_ids = {h.target_id for h in result.hits}
        assert "in1" in hit_ids and "in2" in hit_ids
        assert "out" not in hit_ids

    def test_skips_dead_targets(self):
        eng = HitResolutionEngine()
        shape = CircleShape(center=Vector2(0, 0), radius=5.0)
        dead = _target("dead", hp=1.0)
        dead.apply_damage(1.0)
        targets = [(dead, Vector2(0, 0))]
        result = eng.resolve_aoe(shape, targets, base_damage=50.0)
        assert result.targets_hit == 0

    def test_total_damage_sum(self):
        eng = HitResolutionEngine()
        shape = CircleShape(center=Vector2(0, 0), radius=10.0)
        targets = [(_target(f"t{i}", hp=1000.0), Vector2(i, 0)) for i in range(3)]
        result = eng.resolve_aoe(shape, targets, base_damage=100.0, falloff=0.0)
        assert result.total_damage == pytest.approx(300.0)

    def test_falloff_reduces_damage_at_edge(self):
        eng = HitResolutionEngine()
        shape = CircleShape(center=Vector2(0, 0), radius=10.0)
        # target at distance 5 with falloff=0.1 → factor = 1 - 0.1*5 = 0.5 → 50 damage
        t = _target(hp=1000.0)
        result = eng.resolve_aoe(shape, [(t, Vector2(5, 0))], base_damage=100.0, falloff=0.1)
        assert result.total_damage == pytest.approx(50.0)
