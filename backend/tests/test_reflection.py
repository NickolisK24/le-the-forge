"""Tests for Damage Reflection System (Step 71)."""
import pytest
from app.domain.reflection import reflect_damage, apply_reflection, REFLECT_CAP


class TestReflectDamage:
    def test_zero_pct_no_reflection(self):
        assert reflect_damage(100.0, 0.0) == pytest.approx(0.0)

    def test_100pct_reflects_all(self):
        assert reflect_damage(100.0, 100.0) == pytest.approx(100.0)

    def test_50pct_reflects_half(self):
        assert reflect_damage(200.0, 50.0) == pytest.approx(100.0)

    def test_above_cap_clamped(self):
        assert reflect_damage(100.0, 150.0) == pytest.approx(100.0)

    def test_negative_pct_clamped_to_zero(self):
        assert reflect_damage(100.0, -20.0) == pytest.approx(0.0)

    def test_zero_incoming(self):
        assert reflect_damage(0.0, 50.0) == pytest.approx(0.0)

    def test_negative_incoming_raises(self):
        with pytest.raises(ValueError, match="incoming"):
            reflect_damage(-10.0, 50.0)

    def test_exact_cap_boundary(self):
        assert reflect_damage(80.0, REFLECT_CAP) == pytest.approx(80.0)


class TestApplyReflection:
    def test_defender_takes_full_damage(self):
        defender, _ = apply_reflection(100.0, 30.0)
        assert defender == pytest.approx(100.0)

    def test_attacker_takes_reflected_amount(self):
        _, attacker = apply_reflection(100.0, 30.0)
        assert attacker == pytest.approx(30.0)

    def test_attacker_resistance_reduces_reflected(self):
        # 50 reflected, 50% attacker res → 25 damage to attacker
        _, attacker = apply_reflection(100.0, 50.0, attacker_resistance=50.0)
        assert attacker == pytest.approx(25.0)

    def test_zero_reflection_zero_attacker_damage(self):
        _, attacker = apply_reflection(100.0, 0.0)
        assert attacker == pytest.approx(0.0)

    def test_both_values_returned_correctly(self):
        defender, attacker = apply_reflection(200.0, 25.0, attacker_resistance=0.0)
        assert defender == pytest.approx(200.0)
        assert attacker == pytest.approx(50.0)
