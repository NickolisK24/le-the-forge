"""L14 — MovementTargeting tests."""
import math
import pytest
from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity
from combat.movement_targeting import MovementTargeting


def _t(tid: str, hp: float = 1000.0) -> TargetEntity:
    return TargetEntity(target_id=tid, max_health=hp)


class TestNearestFarthest:
    def test_nearest_to_player(self):
        mt = MovementTargeting()
        targets = [
            (_t("near"), Vector2(1, 0)),
            (_t("mid"),  Vector2(5, 0)),
            (_t("far"),  Vector2(20, 0)),
        ]
        result = mt.nearest_to_player(Vector2(0, 0), targets)
        assert result.primary.target_id == "near"

    def test_farthest_from_player(self):
        mt = MovementTargeting()
        targets = [
            (_t("near"), Vector2(1, 0)),
            (_t("far"),  Vector2(20, 0)),
        ]
        result = mt.farthest_from_player(Vector2(0, 0), targets)
        assert result.primary.target_id == "far"

    def test_no_targets_returns_none(self):
        result = MovementTargeting.nearest_to_player(Vector2(0, 0), [])
        assert result.primary is None

    def test_dead_target_not_selected_nearest(self):
        dead = _t("dead", hp=1.0)
        dead.apply_damage(1.0)
        alive = _t("alive")
        targets = [(dead, Vector2(0.1, 0)), (alive, Vector2(5, 0))]
        result = MovementTargeting.nearest_to_player(Vector2(0, 0), targets)
        assert result.primary.target_id == "alive"


class TestTargetsInRange:
    def test_finds_targets_in_range(self):
        targets = [
            (_t("in"), Vector2(3, 0)),
            (_t("out"), Vector2(15, 0)),
        ]
        result = MovementTargeting.targets_in_range(Vector2(0, 0), 10.0, targets)
        assert result.count == 1
        assert result.primary.target_id == "in"

    def test_zero_radius_raises(self):
        with pytest.raises(ValueError):
            MovementTargeting.targets_in_range(Vector2(0, 0), 0.0, [])

    def test_all_targets_in_large_radius(self):
        targets = [(_t(f"t{i}"), Vector2(i, 0)) for i in range(5)]
        result = MovementTargeting.targets_in_range(Vector2(0, 0), 100.0, targets)
        assert result.count == 5


class TestTargetsInCone:
    def test_targets_in_cone(self):
        targets = [
            (_t("in"),  Vector2(5, 0)),    # directly in front
            (_t("out"), Vector2(0, 5)),    # 90° off — outside 30° half-angle
        ]
        result = MovementTargeting.targets_in_cone(
            Vector2(0, 0), Vector2(1, 0), math.pi / 6, 10.0, targets
        )
        assert result.count == 1
        assert result.primary.target_id == "in"

    def test_invalid_half_angle_raises(self):
        with pytest.raises(ValueError):
            MovementTargeting.targets_in_cone(Vector2(0, 0), Vector2(1, 0), 0.0, 10.0, [])

    def test_beyond_range_excluded(self):
        targets = [(_t("far"), Vector2(100, 0))]
        result = MovementTargeting.targets_in_cone(
            Vector2(0, 0), Vector2(1, 0), math.pi / 4, 10.0, targets
        )
        assert result.count == 0


class TestMostIsolated:
    def test_isolated_target_selected(self):
        cluster = [(_t(f"c{i}"), Vector2(i * 0.1, 0)) for i in range(5)]
        isolated = (_t("lone"), Vector2(100, 100))
        result = MovementTargeting.most_isolated(cluster + [isolated], isolation_radius=5.0)
        assert result.primary.target_id == "lone"

    def test_no_targets_returns_none(self):
        result = MovementTargeting.most_isolated([])
        assert result.primary is None


class TestClosestN:
    def test_returns_n_targets(self):
        targets = [(_t(f"t{i}"), Vector2(i, 0)) for i in range(10)]
        result = MovementTargeting.closest_n(Vector2(0, 0), targets, n=3)
        assert result.count == 3

    def test_returns_nearest_first(self):
        targets = [(_t("near"), Vector2(1, 0)), (_t("far"), Vector2(10, 0))]
        result = MovementTargeting.closest_n(Vector2(0, 0), targets, n=1)
        assert result.primary.target_id == "near"

    def test_zero_n_raises(self):
        with pytest.raises(ValueError):
            MovementTargeting.closest_n(Vector2(0, 0), [], n=0)
