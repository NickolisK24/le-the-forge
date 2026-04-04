"""K8 — Pierce logic tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile
from projectiles.pierce_logic import PierceLogic, PierceResult


def _proj(pierce: int = 0) -> Projectile:
    return Projectile(
        origin=Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=10.0,
        damage=50.0,
        skill_id="test",
        pierce_count=pierce,
    )


class TestEvaluate:
    def test_no_pierce_stops(self):
        pl = PierceLogic()
        p = _proj(pierce=0)
        result = pl.evaluate(p, "t1")
        assert result.pierced is False

    def test_one_pierce_continues(self):
        pl = PierceLogic()
        p = _proj(pierce=1)
        result = pl.evaluate(p, "t1")
        assert result.pierced is True

    def test_evaluate_does_not_mutate(self):
        pl = PierceLogic()
        p = _proj(pierce=2)
        pl.evaluate(p, "t1")
        assert p.pierce_count == 2  # unchanged

    def test_evaluate_remaining_decremented(self):
        pl = PierceLogic()
        p = _proj(pierce=3)
        result = pl.evaluate(p, "t1")
        assert result.pierce_remaining == 2


class TestApply:
    def test_apply_records_hit(self):
        pl = PierceLogic()
        p = _proj(pierce=1)
        pl.apply(p, "t1")
        assert p.has_hit("t1") is True

    def test_apply_decrements_pierce(self):
        pl = PierceLogic()
        p = _proj(pierce=2)
        pl.apply(p, "t1")
        assert p.pierce_count == 1

    def test_apply_deactivates_when_no_pierce(self):
        pl = PierceLogic()
        p = _proj(pierce=0)
        pl.apply(p, "t1")
        assert p.is_active is False

    def test_apply_with_pierce_stays_active(self):
        pl = PierceLogic()
        p = _proj(pierce=2)
        pl.apply(p, "t1")
        assert p.is_active is True


class TestCanHit:
    def test_active_unregistered_target_can_hit(self):
        p = _proj(pierce=1)
        assert PierceLogic.can_hit(p, "t1") is True

    def test_already_hit_target_cannot_hit(self):
        p = _proj(pierce=1)
        p.record_hit("t1")
        assert PierceLogic.can_hit(p, "t1") is False

    def test_inactive_projectile_cannot_hit(self):
        p = _proj()
        p.deactivate()
        assert PierceLogic.can_hit(p, "t1") is False

    def test_remaining_pierce_count(self):
        p = _proj(pierce=3)
        assert PierceLogic.remaining_pierce(p) == 3
