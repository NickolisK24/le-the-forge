"""I1 — Target Entity tests."""
import pytest
from targets.models.target_entity import TargetEntity


def _t(**kw) -> TargetEntity:
    defaults = dict(target_id="t1", max_health=1000.0)
    defaults.update(kw)
    return TargetEntity(**defaults)


class TestTargetCreation:
    def test_default_full_health(self):
        t = _t()
        assert t.current_health == 1000.0
        assert t.is_alive is True

    def test_explicit_health(self):
        t = TargetEntity("t1", max_health=1000.0, current_health=400.0)
        assert t.current_health == 400.0

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            TargetEntity("", max_health=100.0)

    def test_zero_max_health_raises(self):
        with pytest.raises(ValueError):
            TargetEntity("t1", max_health=0.0)

    def test_negative_health_raises(self):
        with pytest.raises(ValueError):
            TargetEntity("t1", max_health=100.0, current_health=-1.0)

    def test_health_above_max_raises(self):
        with pytest.raises(ValueError):
            TargetEntity("t1", max_health=100.0, current_health=200.0)


class TestDamageApplication:
    def test_damage_reduces_health(self):
        t = _t()
        actual = t.apply_damage(300.0)
        assert actual == 300.0
        assert t.current_health == 700.0

    def test_damage_floors_at_zero(self):
        t = _t()
        actual = t.apply_damage(9999.0)
        assert t.current_health == 0.0
        assert actual == 1000.0  # capped to remaining HP

    def test_negative_damage_raises(self):
        t = _t()
        with pytest.raises(ValueError):
            t.apply_damage(-1.0)


class TestDeathTransition:
    def test_alive_until_hp_zero(self):
        t = _t()
        t.apply_damage(999.9)
        assert t.is_alive is True

    def test_dead_at_zero(self):
        t = _t()
        t.apply_damage(1000.0)
        assert t.is_alive is False

    def test_health_pct_at_death(self):
        t = _t()
        t.apply_damage(1000.0)
        assert t.health_pct == 0.0


class TestStatusContainer:
    def test_add_status(self):
        t = _t()
        t.add_status("shock")
        assert t.has_status("shock") is True

    def test_remove_status(self):
        t = _t()
        t.add_status("shock")
        t.remove_status("shock")
        assert t.has_status("shock") is False

    def test_duplicate_status_not_added_twice(self):
        t = _t()
        t.add_status("shock")
        t.add_status("shock")
        assert t.status_list.count("shock") == 1

    def test_serialization_round_trip(self):
        t = TargetEntity("t1", max_health=500.0, current_health=300.0, position_index=2)
        t.add_status("ignite")
        t2 = TargetEntity.from_dict(t.to_dict())
        assert t2.target_id == "t1"
        assert t2.current_health == 300.0
        assert "ignite" in t2.status_list


class TestPositionIndexValidation:
    def test_default_position_index_zero(self):
        t = _t()
        assert t.position_index == 0

    def test_positive_position_index_accepted(self):
        t = _t(position_index=5)
        assert t.position_index == 5

    def test_negative_position_index_raises(self):
        with pytest.raises(ValueError, match="position_index"):
            _t(position_index=-1)

    def test_zero_position_index_accepted(self):
        t = _t(position_index=0)
        assert t.position_index == 0
