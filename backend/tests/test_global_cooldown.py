"""G5 — GlobalCooldown tests"""
import pytest
from rotation.global_cooldown import GlobalCooldown


class TestGCDActivation:
    def test_not_locked_before_trigger(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        assert not gcd.is_locked(0.0)

    def test_locked_immediately_after_trigger(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert gcd.is_locked(0.0)

    def test_locked_mid_window(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert gcd.is_locked(0.5)

    def test_unlocked_at_expiry(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert not gcd.is_locked(1.0)

    def test_unlocked_after_expiry(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert not gcd.is_locked(5.0)

    def test_trigger_mid_session(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(5.0)
        assert gcd.is_locked(5.5)
        assert not gcd.is_locked(6.0)


class TestGCDLockPrevention:
    def test_time_remaining_during_lock(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert abs(gcd.time_remaining(0.4) - 0.6) < 1e-9

    def test_time_remaining_after_expiry(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)
        assert gcd.time_remaining(2.0) == 0.0

    def test_unlock_clears_immediately(self):
        gcd = GlobalCooldown(base_gcd=2.0)
        gcd.trigger(0.0)
        assert gcd.is_locked(0.5)
        gcd.unlock()
        assert not gcd.is_locked(0.5)

    def test_zero_gcd_never_locks(self):
        gcd = GlobalCooldown(base_gcd=0.0)
        gcd.trigger(0.0)
        assert not gcd.is_locked(0.0)


class TestGCDTimingAccuracy:
    def test_locked_until_value(self):
        gcd = GlobalCooldown(base_gcd=1.5)
        gcd.trigger(2.0)
        assert abs(gcd.locked_until() - 3.5) < 1e-9

    def test_retriggering_extends_lock(self):
        gcd = GlobalCooldown(base_gcd=1.0)
        gcd.trigger(0.0)   # locked until 1.0
        gcd.trigger(0.5)   # re-triggered at 0.5 → locked until 1.5
        assert gcd.is_locked(1.2)
        assert not gcd.is_locked(1.5)

    def test_invalid_base_gcd_raises(self):
        with pytest.raises(ValueError):
            GlobalCooldown(base_gcd=-0.1)

    def test_max_gcd_boundary(self):
        gcd = GlobalCooldown(base_gcd=10.0)
        gcd.trigger(0.0)
        assert gcd.is_locked(9.9)
        assert not gcd.is_locked(10.0)
