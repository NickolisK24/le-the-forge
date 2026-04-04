"""L15 — KitingEngine tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.kiting.kiting_engine import KitingEngine, KiteResult


class TestConstruction:
    def test_invalid_min_range_raises(self):
        with pytest.raises(ValueError):
            KitingEngine(min_range=-1.0)

    def test_invalid_max_range_raises(self):
        with pytest.raises(ValueError):
            KitingEngine(min_range=5.0, max_range=3.0)

    def test_invalid_kite_speed_raises(self):
        with pytest.raises(ValueError):
            KitingEngine(kite_speed=0.0)


class TestEvaluate:
    def test_retreat_when_enemy_too_close(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        result = engine.evaluate(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(2, 0)],  # 2 < min_range=5
        )
        assert result.kite_action == "retreat"
        assert result.is_kiting is True
        # Velocity should point away from enemy at +2x → negative x direction
        assert result.recommended_velocity.x < 0

    def test_advance_when_all_enemies_far(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        result = engine.evaluate(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(20, 0)],  # 20 > max_range=15
        )
        assert result.kite_action == "advance"
        assert result.is_kiting is False

    def test_hold_when_in_safe_band(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        result = engine.evaluate(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(10, 0)],  # 10 in [5, 15]
        )
        assert result.kite_action == "hold"
        assert result.recommended_velocity == Vector2.zero()

    def test_strafe_when_configured(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, strafe_speed=3.0)
        result = engine.evaluate(Vector2(0, 0), [Vector2(10, 0)])
        assert result.kite_action == "strafe"
        assert result.recommended_velocity.magnitude() == pytest.approx(3.0)

    def test_no_enemies_returns_hold(self):
        engine = KitingEngine()
        result = engine.evaluate(Vector2(0, 0), [])
        assert result.kite_action == "hold"
        assert result.closest_enemy_dist == float("inf")

    def test_retreat_velocity_magnitude(self):
        engine = KitingEngine(kite_speed=7.0)
        result = engine.evaluate(Vector2(0, 0), [Vector2(2, 0)])
        assert result.recommended_velocity.magnitude() == pytest.approx(7.0)

    def test_multiple_enemies_reacts_to_nearest(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        result = engine.evaluate(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(20, 0), Vector2(2, 0), Vector2(30, 0)],
        )
        # Nearest enemy at dist 2 → retreat
        assert result.kite_action == "retreat"
        assert result.closest_enemy_dist == pytest.approx(2.0)


class TestUpdatePlayerPosition:
    def test_returns_new_position_and_result(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        new_pos, result = engine.update_player_position(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(2, 0)],
            delta=0.1,
        )
        assert isinstance(new_pos, Vector2)
        assert isinstance(result, KiteResult)

    def test_retreat_moves_player_away(self):
        engine = KitingEngine(min_range=5.0, max_range=15.0, kite_speed=7.0)
        new_pos, _ = engine.update_player_position(
            player_pos=Vector2(0, 0),
            enemy_positions=[Vector2(3, 0)],
            delta=1.0,
        )
        # Player should have moved in -x direction (away from enemy)
        assert new_pos.distance_to(Vector2(3, 0)) > 3.0
