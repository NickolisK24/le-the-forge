"""G7 — PriorityResolver tests"""
from rotation.priority_resolver import resolve_next, next_ready_time
from rotation.models.rotation_step import RotationStep
from rotation.cooldown_tracker import CooldownTracker
from rotation.global_cooldown import GlobalCooldown


def _step(sid, priority=0):
    return RotationStep(skill_id=sid, priority=priority)


def _fresh():
    return CooldownTracker(), GlobalCooldown(base_gcd=0.0)


class TestPriorityFallback:
    def test_returns_none_when_empty(self):
        t, g = _fresh()
        assert resolve_next([], t, g, 0.0) is None

    def test_returns_none_when_all_on_cd(self):
        t, g = _fresh()
        t.start("a", 0.0, 5.0)
        result = resolve_next([_step("a")], t, g, 0.0)
        assert result is None

    def test_returns_none_when_gcd_locked(self):
        t, g = CooldownTracker(), GlobalCooldown(base_gcd=1.0)
        g.trigger(0.0)
        result = resolve_next([_step("a")], t, g, 0.5)
        assert result is None

    def test_single_ready_skill(self):
        t, g = _fresh()
        steps = [_step("a")]
        idx, step = resolve_next(steps, t, g, 0.0)
        assert step.skill_id == "a"
        assert idx == 0


class TestSkillSelectionLogic:
    def test_lower_priority_wins(self):
        t, g = _fresh()
        steps = [_step("high", priority=5), _step("low", priority=1)]
        _, step = resolve_next(steps, t, g, 0.0)
        assert step.skill_id == "low"

    def test_tie_broken_by_earlier_index(self):
        t, g = _fresh()
        steps = [_step("first", priority=0), _step("second", priority=0)]
        idx, step = resolve_next(steps, t, g, 0.0)
        assert step.skill_id == "first"
        assert idx == 0

    def test_skips_skill_on_cooldown(self):
        t, g = _fresh()
        t.start("preferred", 0.0, 5.0)
        steps = [_step("preferred", priority=0), _step("fallback", priority=1)]
        _, step = resolve_next(steps, t, g, 0.0)
        assert step.skill_id == "fallback"

    def test_all_ready_picks_best_priority(self):
        t, g = _fresh()
        steps = [_step("c", priority=3), _step("a", priority=1), _step("b", priority=2)]
        _, step = resolve_next(steps, t, g, 0.0)
        assert step.skill_id == "a"

    def test_returns_original_index(self):
        t, g = _fresh()
        steps = [_step("a"), _step("b", priority=-1)]
        idx, step = resolve_next(steps, t, g, 0.0)
        assert idx == 1  # "b" is at index 1 but has lower priority value


class TestNextReadyTime:
    def test_returns_current_if_ready(self):
        t, g = _fresh()
        steps = [_step("a")]
        assert next_ready_time(steps, t, g, 2.0) == 2.0

    def test_returns_cooldown_end(self):
        t, g = _fresh()
        t.start("a", 0.0, 3.0)
        steps = [_step("a")]
        assert abs(next_ready_time(steps, t, g, 0.0) - 3.0) < 1e-9

    def test_gcd_adds_to_wait(self):
        t, g = CooldownTracker(), GlobalCooldown(base_gcd=1.0)
        g.trigger(0.0)
        steps = [_step("a")]
        t_ready = next_ready_time(steps, t, g, 0.0)
        assert abs(t_ready - 1.0) < 1e-9
