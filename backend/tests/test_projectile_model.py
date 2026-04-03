"""K3 — Projectile model tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile


def _proj(**kw) -> Projectile:
    defaults = dict(
        origin=Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=10.0,
        damage=50.0,
        skill_id="arrow",
    )
    defaults.update(kw)
    return Projectile(**defaults)


class TestConstruction:
    def test_starts_at_origin(self):
        p = _proj()
        assert p.position == Vector2(0, 0)

    def test_direction_normalized(self):
        p = _proj(direction=Vector2(3, 4))
        assert p.direction.magnitude() == pytest.approx(1.0)

    def test_zero_direction_raises(self):
        with pytest.raises(ValueError):
            _proj(direction=Vector2(0, 0))

    def test_negative_speed_raises(self):
        with pytest.raises(ValueError):
            _proj(speed=0.0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError):
            _proj(damage=-1.0)

    def test_negative_pierce_raises(self):
        with pytest.raises(ValueError):
            _proj(pierce_count=-1)

    def test_negative_max_range_raises(self):
        with pytest.raises(ValueError):
            _proj(max_range=-1.0)

    def test_default_active(self):
        assert _proj().is_active is True


class TestTravel:
    def test_advance_moves_position(self):
        p = _proj(speed=10.0)
        p.advance(1.0)
        assert p.position.x == pytest.approx(10.0)

    def test_advance_tracks_distance(self):
        p = _proj(speed=10.0)
        p.advance(0.5)
        assert p.distance_traveled == pytest.approx(5.0)

    def test_expires_at_max_range(self):
        p = _proj(speed=10.0, max_range=5.0)
        p.advance(0.5)  # 5 units — exactly at range
        assert p.is_active is False

    def test_advance_on_inactive_noop(self):
        p = _proj()
        p.deactivate()
        p.advance(1.0)
        assert p.distance_traveled == pytest.approx(0.0)

    def test_range_remaining(self):
        p = _proj(speed=10.0, max_range=20.0)
        p.advance(1.0)
        assert p.range_remaining() == pytest.approx(10.0)


class TestHitTracking:
    def test_record_hit_marks_target(self):
        p = _proj(pierce_count=1)
        p.record_hit("t1")
        assert p.has_hit("t1") is True

    def test_pierce_decrements(self):
        p = _proj(pierce_count=2)
        p.record_hit("t1")
        assert p.pierce_count == 1

    def test_deactivates_when_pierce_exhausted(self):
        p = _proj(pierce_count=0)
        p.record_hit("t1")
        assert p.is_active is False

    def test_to_dict_keys(self):
        d = _proj().to_dict()
        assert "projectile_id" in d and "position" in d and "is_active" in d
