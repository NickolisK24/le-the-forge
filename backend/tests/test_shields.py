"""Tests for Damage Absorption Shields (Step 72)."""
import pytest
from app.domain.shields import absorb, AbsorptionShield


class TestAbsorb:
    def test_damage_less_than_shield(self):
        remaining, overflow = absorb(100.0, 40.0)
        assert remaining == pytest.approx(60.0)
        assert overflow  == pytest.approx(0.0)

    def test_damage_exceeds_shield(self):
        remaining, overflow = absorb(50.0, 80.0)
        assert remaining == pytest.approx(0.0)
        assert overflow  == pytest.approx(30.0)

    def test_damage_equals_shield(self):
        remaining, overflow = absorb(100.0, 100.0)
        assert remaining == pytest.approx(0.0)
        assert overflow  == pytest.approx(0.0)

    def test_zero_shield_full_overflow(self):
        remaining, overflow = absorb(0.0, 50.0)
        assert remaining == pytest.approx(0.0)
        assert overflow  == pytest.approx(50.0)

    def test_zero_damage_no_change(self):
        remaining, overflow = absorb(100.0, 0.0)
        assert remaining == pytest.approx(100.0)
        assert overflow  == pytest.approx(0.0)

    def test_negative_shield_raises(self):
        with pytest.raises(ValueError, match="shield_hp"):
            absorb(-1.0, 50.0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError, match="incoming"):
            absorb(100.0, -10.0)


class TestAbsorptionShield:
    def test_at_full(self):
        s = AbsorptionShield.at_full(200.0)
        assert s.current_shield == pytest.approx(200.0)
        assert s.is_depleted is False

    def test_take_damage_within_shield(self):
        s = AbsorptionShield.at_full(100.0)
        overflow = s.take_damage(30.0)
        assert overflow == pytest.approx(0.0)
        assert s.current_shield == pytest.approx(70.0)

    def test_take_damage_overflow(self):
        s = AbsorptionShield.at_full(50.0)
        overflow = s.take_damage(80.0)
        assert overflow == pytest.approx(30.0)
        assert s.is_depleted is True

    def test_restore_caps_at_max(self):
        s = AbsorptionShield.at_full(100.0)
        s.take_damage(40.0)
        s.restore(200.0)
        assert s.current_shield == pytest.approx(100.0)

    def test_restore_negative_ignored(self):
        s = AbsorptionShield.at_full(100.0)
        s.take_damage(50.0)
        s.restore(-10.0)
        assert s.current_shield == pytest.approx(50.0)
