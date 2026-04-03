"""G4 — CooldownTracker tests"""
from rotation.cooldown_tracker import CooldownTracker


class TestCooldownStart:
    def test_skill_not_started_is_ready(self):
        t = CooldownTracker()
        assert t.is_ready("fireball", 0.0)

    def test_skill_on_cooldown_not_ready(self):
        t = CooldownTracker()
        t.start("fireball", current_time=0.0, duration=3.0)
        assert not t.is_ready("fireball", 1.0)

    def test_zero_duration_no_op(self):
        t = CooldownTracker()
        t.start("fireball", current_time=0.0, duration=0.0)
        assert t.is_ready("fireball", 0.0)

    def test_negative_duration_no_op(self):
        t = CooldownTracker()
        t.start("fireball", current_time=0.0, duration=-1.0)
        assert t.is_ready("fireball", 0.0)

    def test_start_overwrites_previous(self):
        t = CooldownTracker()
        t.start("x", 0.0, 2.0)
        t.start("x", 1.0, 5.0)   # resets from t=1, ready at t=6
        assert not t.is_ready("x", 5.0)
        assert t.is_ready("x", 6.0)


class TestCooldownExpiration:
    def test_ready_exactly_at_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 3.0)
        assert t.is_ready("x", 3.0)

    def test_not_ready_just_before_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 3.0)
        assert not t.is_ready("x", 2.999)

    def test_ready_after_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 3.0)
        assert t.is_ready("x", 10.0)

    def test_time_remaining_before_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 4.0)
        assert abs(t.time_remaining("x", 1.0) - 3.0) < 1e-9

    def test_time_remaining_at_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 4.0)
        assert t.time_remaining("x", 4.0) == 0.0

    def test_time_remaining_after_expiry(self):
        t = CooldownTracker()
        t.start("x", 0.0, 4.0)
        assert t.time_remaining("x", 10.0) == 0.0

    def test_time_remaining_unknown_skill(self):
        t = CooldownTracker()
        assert t.time_remaining("ghost", 5.0) == 0.0


class TestMultipleCooldowns:
    def test_independent_skills(self):
        t = CooldownTracker()
        t.start("a", 0.0, 2.0)
        t.start("b", 0.0, 5.0)
        assert t.is_ready("a", 2.0)
        assert not t.is_ready("b", 2.0)

    def test_ready_skills_filter(self):
        t = CooldownTracker()
        t.start("a", 0.0, 2.0)
        t.start("b", 0.0, 5.0)
        ready = t.ready_skills(["a", "b", "c"], current_time=2.0)
        assert set(ready) == {"a", "c"}

    def test_reset_single(self):
        t = CooldownTracker()
        t.start("a", 0.0, 10.0)
        t.reset("a")
        assert t.is_ready("a", 0.0)

    def test_reset_all(self):
        t = CooldownTracker()
        t.start("a", 0.0, 10.0)
        t.start("b", 0.0, 10.0)
        t.reset_all()
        assert t.is_ready("a", 0.0)
        assert t.is_ready("b", 0.0)
