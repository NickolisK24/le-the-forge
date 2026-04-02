"""Tests for Area Damage Falloff (Step 76)."""
import pytest
from app.domain.aoe_falloff import linear_falloff, apply_aoe_damage


class TestLinearFalloff:
    def test_within_inner_radius_full_damage(self):
        assert linear_falloff(3.0, inner_radius=5.0, outer_radius=10.0) == pytest.approx(1.0)

    def test_at_inner_radius_full_damage(self):
        assert linear_falloff(5.0, inner_radius=5.0, outer_radius=10.0) == pytest.approx(1.0)

    def test_at_outer_radius_min_damage(self):
        assert linear_falloff(10.0, inner_radius=5.0, outer_radius=10.0, min_pct=20.0) == pytest.approx(0.2)

    def test_beyond_outer_radius_min_damage(self):
        assert linear_falloff(20.0, inner_radius=5.0, outer_radius=10.0, min_pct=20.0) == pytest.approx(0.2)

    def test_midpoint_linear(self):
        # midpoint = 7.5; t=0.5 → 1.0 - 0.5*(1.0-0.2) = 0.6
        assert linear_falloff(7.5, inner_radius=5.0, outer_radius=10.0, min_pct=20.0) == pytest.approx(0.6)

    def test_default_min_pct_zero(self):
        assert linear_falloff(10.0, inner_radius=5.0, outer_radius=10.0) == pytest.approx(0.0)

    def test_invalid_outer_radius_raises(self):
        with pytest.raises(ValueError):
            linear_falloff(5.0, inner_radius=10.0, outer_radius=5.0)

    def test_negative_distance_raises(self):
        with pytest.raises(ValueError):
            linear_falloff(-1.0, inner_radius=0.0, outer_radius=5.0)


class TestApplyAoeDamage:
    def test_within_radius_full_damage(self):
        assert apply_aoe_damage(100.0, 2.0, inner_radius=5.0, outer_radius=10.0) == pytest.approx(100.0)

    def test_beyond_outer_zero_min(self):
        assert apply_aoe_damage(100.0, 15.0, inner_radius=5.0, outer_radius=10.0) == pytest.approx(0.0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError):
            apply_aoe_damage(-10.0, 3.0, inner_radius=1.0, outer_radius=5.0)
