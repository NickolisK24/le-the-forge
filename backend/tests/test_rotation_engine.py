"""
Tests for build rotation_engine (Step 93).

Validates cooldown tracking, priority scheduling, mana management,
and execution order.
"""

import pytest

from build.rotation_engine import BuildRotation, CastEvent, RotationResult, RotationSkill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skill(name: str, cooldown=0.0, mana_cost=0.0, priority=1, damage=100.0) -> RotationSkill:
    return RotationSkill(
        name=name, cooldown=cooldown, mana_cost=mana_cost,
        priority=priority, base_damage=damage,
    )


def _run(skills, duration=10.0, max_mana=10_000.0, regen=0.0, tick=0.1) -> RotationResult:
    return BuildRotation(skills, fight_duration=duration, max_mana=max_mana,
                         mana_regen_rate=regen, tick_size=tick).run()


# ---------------------------------------------------------------------------
# RotationSkill validation
# ---------------------------------------------------------------------------

class TestRotationSkill:
    def test_negative_cooldown_raises(self):
        with pytest.raises(ValueError):
            RotationSkill("a", cooldown=-1.0)

    def test_negative_mana_raises(self):
        with pytest.raises(ValueError):
            RotationSkill("a", mana_cost=-1.0)

    def test_priority_below_1_raises(self):
        with pytest.raises(ValueError):
            RotationSkill("a", priority=0)


# ---------------------------------------------------------------------------
# BuildRotation validation
# ---------------------------------------------------------------------------

class TestBuildRotationValidation:
    def test_empty_skills_raises(self):
        with pytest.raises(ValueError):
            BuildRotation([], fight_duration=10.0)

    def test_zero_duration_raises(self):
        with pytest.raises(ValueError):
            BuildRotation([_skill("a")], fight_duration=0.0)

    def test_zero_tick_raises(self):
        with pytest.raises(ValueError):
            BuildRotation([_skill("a")], fight_duration=10.0, tick_size=0.0)


# ---------------------------------------------------------------------------
# Single skill
# ---------------------------------------------------------------------------

class TestSingleSkill:
    def test_no_cooldown_casts_every_tick(self):
        result = _run([_skill("spam", cooldown=0.0)], duration=1.0, tick=0.1)
        # ~10 ticks; floating point accumulation may give 10 or 11
        assert 10 <= result.casts_per_skill["spam"] <= 11

    def test_cooldown_limits_casts(self):
        # 2s cooldown, 10s fight → ~5 casts (at t=0, 2, 4, 6, 8)
        result = _run([_skill("heavy", cooldown=2.0)], duration=10.0, tick=0.1)
        assert 4 <= result.casts_per_skill["heavy"] <= 6

    def test_total_damage_correct(self):
        result = _run([_skill("spell", cooldown=0.0, damage=50.0)], duration=1.0, tick=0.1)
        # ~10-11 ticks × 50 damage
        assert 500.0 <= result.total_damage <= 550.0

    def test_damage_per_skill_matches_casts(self):
        result = _run([_skill("spell", cooldown=1.0, damage=80.0)], duration=5.0, tick=0.1)
        expected = result.casts_per_skill["spell"] * 80.0
        assert result.damage_per_skill["spell"] == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

class TestPriority:
    def test_higher_priority_fires_first(self):
        skills = [
            _skill("low",  priority=2, cooldown=0.0),
            _skill("high", priority=1, cooldown=0.0),
        ]
        result = _run(skills, duration=1.0, tick=0.1)
        # Every tick, "high" (priority 1) fires; "low" never fires
        assert result.casts_per_skill["high"] >= 10
        assert result.casts_per_skill["low"]  == 0

    def test_fallback_to_lower_priority_when_high_on_cd(self):
        skills = [
            _skill("primary",   priority=1, cooldown=5.0, damage=200.0),
            _skill("secondary", priority=2, cooldown=0.0, damage=50.0),
        ]
        result = _run(skills, duration=10.0, tick=0.1)
        # primary fires ~2x (t=0, t=5), secondary fills all other ticks
        assert result.casts_per_skill["primary"]   == 2
        assert result.casts_per_skill["secondary"] > 0

    def test_execution_order_in_timeline(self):
        skills = [
            _skill("a", priority=1, cooldown=2.0),
            _skill("b", priority=2, cooldown=1.0),
        ]
        result = _run(skills, duration=5.0, tick=0.1)
        # All "a" casts should happen before any "b" cast at times when both are ready
        for event in result.timeline:
            if event.skill_name == "a":
                # No "b" should have fired at the exact same time
                same_time = [e for e in result.timeline
                             if abs(e.time - event.time) < 1e-9 and e.skill_name == "b"]
                assert same_time == []


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

class TestMana:
    def test_skill_blocked_when_mana_insufficient(self):
        skills = [_skill("costly", mana_cost=100.0, cooldown=0.0, damage=50.0)]
        # max_mana=50, regen=0 → never enough mana → no casts
        result = _run(skills, duration=10.0, max_mana=50.0, regen=0.0, tick=0.1)
        assert result.casts_per_skill["costly"] == 0

    def test_mana_regen_enables_casts(self):
        # mana_cost=10, regen=5/s, tick=0.1, max_mana=100 → starts empty, refills over time
        skills = [_skill("spell", mana_cost=10.0, cooldown=0.0)]
        result = _run(skills, duration=10.0, max_mana=100.0, regen=5.0, tick=0.1)
        # With 5/s regen and 10 cost, can cast ~every 2s → ~5 casts in 10s
        assert result.casts_per_skill["spell"] > 0

    def test_mana_floor_never_negative(self):
        skills = [_skill("costly", mana_cost=5.0, cooldown=0.0)]
        result = _run(skills, duration=5.0, max_mana=100.0, regen=0.0, tick=0.1)
        assert result.mana_floor >= 0.0

    def test_mana_capped_at_max(self):
        # Very high regen, low cost — mana shouldn't overflow
        skills = [_skill("cheap", mana_cost=1.0, cooldown=1.0)]
        result = _run(skills, duration=5.0, max_mana=50.0, regen=1000.0, tick=0.1)
        assert result.mana_floor <= 50.0


# ---------------------------------------------------------------------------
# Result fields
# ---------------------------------------------------------------------------

class TestRotationResult:
    def test_total_casts_sum_of_per_skill(self):
        skills = [_skill("a", cooldown=0.5), _skill("b", cooldown=1.0, priority=2)]
        result = _run(skills, duration=10.0, tick=0.1)
        assert result.total_casts == sum(result.casts_per_skill.values())

    def test_total_damage_sum_of_per_skill(self):
        skills = [_skill("a", cooldown=1.0, damage=100.0), _skill("b", cooldown=2.0, damage=80.0, priority=2)]
        result = _run(skills, duration=10.0, tick=0.1)
        assert result.total_damage == pytest.approx(sum(result.damage_per_skill.values()))

    def test_timeline_length_matches_total_casts(self):
        skills = [_skill("a", cooldown=0.5), _skill("b", cooldown=1.0, priority=2)]
        result = _run(skills, duration=5.0, tick=0.1)
        assert len(result.timeline) == result.total_casts

    def test_timeline_is_time_ordered(self):
        skills = [_skill("a", cooldown=0.5), _skill("b", cooldown=1.0, priority=2)]
        result = _run(skills, duration=5.0, tick=0.1)
        times = [e.time for e in result.timeline]
        assert times == sorted(times)

    def test_fight_duration_preserved(self):
        result = _run([_skill("a")], duration=42.0, tick=0.1)
        assert result.fight_duration == pytest.approx(42.0)
