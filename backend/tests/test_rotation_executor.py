"""G8 — RotationExecutor tests"""
import pytest
from rotation.rotation_executor import execute_rotation, CastResult
from rotation.models.rotation_definition import RotationDefinition
from rotation.models.rotation_step import RotationStep
from skills.models.skill_definition import SkillDefinition


def _skill(sid, base_damage=100.0, cast_time=0.0, cooldown=0.0):
    return SkillDefinition(skill_id=sid, base_damage=base_damage,
                           cast_time=cast_time, cooldown=cooldown)


def _step(sid, priority=0, delay=0.0, repeat=1):
    return RotationStep(skill_id=sid, priority=priority,
                        delay_after_cast=delay, repeat_count=repeat)


def _rot(*steps, loop=True):
    return RotationDefinition(rotation_id="r", steps=list(steps), loop=loop)


def _reg(*skills):
    return {s.skill_id: s for s in skills}


class TestRotationAccuracy:
    def test_empty_rotation_returns_empty(self):
        assert execute_rotation(RotationDefinition(rotation_id="r"), {}, 10.0) == []

    def test_all_unknown_skills_returns_empty(self):
        rot = _rot(_step("ghost"))
        assert execute_rotation(rot, {}, 10.0) == []

    def test_single_instant_skill_no_cooldown(self):
        """With no cooldown and no delay, instant skill loops at time 0,0,0..."""
        rot = _rot(_step("a", delay=1.0))
        reg = _reg(_skill("a"))
        results = execute_rotation(rot, reg, duration=3.0)
        cast_times = [r.cast_at for r in results]
        assert cast_times == pytest.approx([0.0, 1.0, 2.0])

    def test_damage_matches_skill_base_damage(self):
        rot = _rot(_step("a"))
        reg = _reg(_skill("a", base_damage=250.0, cooldown=1.0))
        results = execute_rotation(rot, reg, duration=3.0)
        for r in results:
            assert r.damage == 250.0

    def test_results_are_ordered_by_cast_at(self):
        rot = _rot(_step("a"), _step("b"))
        reg = _reg(_skill("a", cooldown=1.0), _skill("b", cooldown=1.0))
        results = execute_rotation(rot, reg, duration=5.0)
        times = [r.cast_at for r in results]
        assert times == sorted(times)


class TestSkillDamageSequencing:
    def test_priority_selects_lower_value_first(self):
        rot = _rot(_step("slow", priority=1, delay=1.0),
                   _step("fast", priority=0, delay=1.0))
        reg = _reg(_skill("slow"), _skill("fast"))
        results = execute_rotation(rot, reg, duration=4.0)
        skill_ids = [r.skill_id for r in results]
        # "fast" (priority 0) always wins
        assert all(sid == "fast" for sid in skill_ids)

    def test_skill_on_cooldown_falls_back_to_next(self):
        """fast is on 3s CD; while waiting, slow (priority 1) should fire."""
        rot = _rot(_step("fast", priority=0, delay=0.0),
                   _step("slow", priority=1, delay=0.0))
        reg = _reg(_skill("fast", cooldown=3.0), _skill("slow", cooldown=0.0))
        results = execute_rotation(rot, reg, duration=4.0)
        # After fast at t=0 (CD until t=3), slow fires at t=0,1,2 then fast at t=3
        skill_ids = [r.skill_id for r in results]
        assert skill_ids[0] == "fast"
        assert "slow" in skill_ids  # slow fills the gap

    def test_cast_time_delays_resolves_at(self):
        rot = _rot(_step("a"))
        reg = _reg(_skill("a", cast_time=0.5, cooldown=1.0))
        results = execute_rotation(rot, reg, duration=2.0)
        assert results[0].resolves_at == pytest.approx(0.5)

    def test_gcd_separates_casts(self):
        rot = _rot(_step("a"), _step("b"))
        reg = _reg(_skill("a"), _skill("b"))
        results = execute_rotation(rot, reg, duration=5.0, gcd=1.0)
        for i in range(1, len(results)):
            gap = results[i].cast_at - results[i - 1].cast_at
            assert gap >= 1.0 - 1e-9
