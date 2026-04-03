"""G6 — RotationTimeline Engine tests"""
import pytest
from rotation.timeline_engine import build_timeline, CastEvent
from rotation.models.rotation_definition import RotationDefinition
from rotation.models.rotation_step import RotationStep
from skills.models.skill_definition import SkillDefinition


def _skill(sid, cast_time=0.0, cooldown=0.0, base_damage=100.0):
    return SkillDefinition(skill_id=sid, cast_time=cast_time, cooldown=cooldown,
                           base_damage=base_damage)


def _step(sid, **kw):
    return RotationStep(skill_id=sid, **kw)


def _rotation(steps, rotation_id="r", loop=True):
    return RotationDefinition(rotation_id=rotation_id, steps=steps, loop=loop)


def _registry(*skills):
    return {s.skill_id: s for s in skills}


class TestTimelineOrder:
    def test_single_instant_skill_fills_duration(self):
        rot = _rotation([_step("a")])
        reg = _registry(_skill("a", cooldown=1.0))
        events = build_timeline(rot, reg, duration=3.0)
        assert len(events) > 0
        for e in events:
            assert e.skill_id == "a"
            assert e.cast_at < 3.0

    def test_events_ordered_by_cast_at(self):
        rot = _rotation([_step("a"), _step("b")])
        reg = _registry(_skill("a", cooldown=1.0), _skill("b", cooldown=1.0))
        events = build_timeline(rot, reg, duration=6.0)
        times = [e.cast_at for e in events]
        assert times == sorted(times)

    def test_empty_rotation_returns_empty(self):
        rot = RotationDefinition(rotation_id="r")
        assert build_timeline(rot, {}, duration=10.0) == []

    def test_no_loop_stops_after_all_steps(self):
        rot = _rotation([_step("a"), _step("b")], loop=False)
        reg = _registry(_skill("a"), _skill("b"))
        events = build_timeline(rot, reg, duration=100.0)
        assert len(events) == 2
        assert events[0].skill_id == "a"
        assert events[1].skill_id == "b"

    def test_unknown_skill_skipped(self):
        rot = _rotation([_step("unknown"), _step("known")], loop=False)
        reg = _registry(_skill("known"))
        events = build_timeline(rot, reg, duration=5.0)
        assert all(e.skill_id == "known" for e in events)


class TestCooldownRespect:
    def test_cooldown_delays_next_cast(self):
        rot = _rotation([_step("a")])
        reg = _registry(_skill("a", cooldown=2.0))
        events = build_timeline(rot, reg, duration=5.0)
        cast_times = [e.cast_at for e in events]
        assert cast_times == pytest.approx([0.0, 2.0, 4.0])

    def test_cast_time_adds_to_resolves_at(self):
        rot = _rotation([_step("a")], loop=False)
        reg = _registry(_skill("a", cast_time=0.5))
        events = build_timeline(rot, reg, duration=5.0)
        assert events[0].cast_at == pytest.approx(0.0)
        assert events[0].resolves_at == pytest.approx(0.5)

    def test_step_index_set(self):
        rot = _rotation([_step("a"), _step("b")], loop=False)
        reg = _registry(_skill("a"), _skill("b"))
        events = build_timeline(rot, reg, duration=5.0)
        assert events[0].step_index == 0
        assert events[1].step_index == 1


class TestDelayAccuracy:
    def test_delay_after_cast_pushes_next(self):
        rot = _rotation([_step("a", delay_after_cast=1.0)], loop=False)
        reg = _registry(_skill("a", cast_time=0.5))
        events = build_timeline(rot, reg, duration=5.0)
        assert events[0].resolves_at == pytest.approx(0.5)
        assert len(events) == 1  # loop=False, single step

    def test_delay_separates_consecutive_casts(self):
        rot = _rotation([_step("a", delay_after_cast=1.0)])
        reg = _registry(_skill("a"))  # 0 cast/cooldown, 1s delay
        events = build_timeline(rot, reg, duration=3.0)
        cast_times = [e.cast_at for e in events]
        assert cast_times == pytest.approx([0.0, 1.0, 2.0])

    def test_gcd_respected(self):
        rot = _rotation([_step("a"), _step("b")])
        reg = _registry(_skill("a"), _skill("b"))
        # GCD of 1s: a at 0, b at 1, a at 2, ...
        events = build_timeline(rot, reg, duration=3.0, gcd=1.0)
        cast_times = [e.cast_at for e in events]
        for i in range(1, len(cast_times)):
            assert cast_times[i] - cast_times[i - 1] >= 1.0 - 1e-9
