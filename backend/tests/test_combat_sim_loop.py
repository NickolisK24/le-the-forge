"""
Tests for the Combat Simulator time-based loop.

Verifies:
  - Longer duration increases total damage
  - More frequent skill usage increases DPS
  - Enemy defenses reduce final damage
  - Multi-skill rotation works correctly
  - Skill priority ordering is respected
  - Timeline events are captured
  - Determinism: same inputs → same outputs
  - Damage conservation and DPS math
"""

import pytest

from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
from app.combat.combat_simulator import CombatSimulator, SimulationResult
from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.domain.skill import SkillStatDef
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

def _stats(**overrides: float) -> BuildStats:
    s = BuildStats()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def _fireball(**kw) -> SkillStatDef:
    defaults = {
        "base_damage": 100.0, "level_scaling": 0.0, "attack_speed": 1.0,
        "scaling_stats": ("spell_damage_pct", "fire_damage_pct"),
        "is_spell": True, "damage_types": (DamageType.FIRE,),
        "data_version": "test",
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


def _ice_bolt(**kw) -> SkillStatDef:
    defaults = {
        "base_damage": 80.0, "level_scaling": 0.0, "attack_speed": 1.5,
        "scaling_stats": ("spell_damage_pct", "cold_damage_pct"),
        "is_spell": True, "damage_types": (DamageType.COLD,),
        "data_version": "test",
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


def _entry(skill=None, name="Fireball", level=1, priority=1, cooldown=0.0, mods=None):
    return SkillRotationEntry(
        skill_def=skill or _fireball(),
        skill_name=name,
        level=level,
        priority=priority,
        cooldown=cooldown,
        skill_mods=mods or SkillModifiers(),
    )


def _scenario(entries=None, duration=10.0, archetype=EnemyArchetype.TRAINING_DUMMY):
    return CombatScenario(
        duration_seconds=duration,
        enemy=EnemyInstance.from_archetype(archetype),
        rotation=tuple(entries or [_entry()]),
    )


SIM = CombatSimulator()


# ---------------------------------------------------------------------------
# Duration scaling
# ---------------------------------------------------------------------------

class TestDurationScaling:
    def test_longer_duration_more_total_damage(self):
        stats = _stats()
        r_short = SIM.simulate(_scenario(duration=5.0), stats)
        r_long = SIM.simulate(_scenario(duration=20.0), stats)
        assert r_long.total_damage > r_short.total_damage

    def test_dps_stable_across_durations(self):
        stats = _stats()
        r10 = SIM.simulate(_scenario(duration=10.0), stats)
        r30 = SIM.simulate(_scenario(duration=30.0), stats)
        assert abs(r10.effective_dps - r30.effective_dps) / max(r30.effective_dps, 1) < 0.10

    def test_total_damage_proportional_to_duration(self):
        stats = _stats()
        r10 = SIM.simulate(_scenario(duration=10.0), stats)
        r20 = SIM.simulate(_scenario(duration=20.0), stats)
        ratio = r20.total_damage / r10.total_damage
        assert 1.8 < ratio < 2.2


# ---------------------------------------------------------------------------
# Skill frequency
# ---------------------------------------------------------------------------

class TestSkillFrequency:
    def test_faster_skill_more_casts(self):
        slow = _entry(skill=_fireball(attack_speed=0.5), name="Slow")
        fast = _entry(skill=_fireball(attack_speed=2.0), name="Fast")
        r_slow = SIM.simulate(_scenario([slow], duration=10.0), _stats())
        r_fast = SIM.simulate(_scenario([fast], duration=10.0), _stats())
        assert r_fast.total_casts > r_slow.total_casts

    def test_cooldown_limits_cast_rate(self):
        fast_skill = _fireball(attack_speed=10.0)
        entry = _entry(skill=fast_skill, cooldown=2.0)
        result = SIM.simulate(_scenario([entry], duration=10.0), _stats())
        assert result.total_casts <= 6


# ---------------------------------------------------------------------------
# Enemy defenses
# ---------------------------------------------------------------------------

class TestEnemyDefenses:
    def test_defenses_reduce_total_damage(self):
        stats = _stats()
        r_dummy = SIM.simulate(_scenario(archetype=EnemyArchetype.TRAINING_DUMMY), stats)
        r_boss = SIM.simulate(_scenario(archetype=EnemyArchetype.BOSS), stats)
        assert r_boss.total_damage < r_dummy.total_damage

    def test_training_dummy_raw_equals_effective(self):
        result = SIM.simulate(_scenario(archetype=EnemyArchetype.TRAINING_DUMMY), _stats())
        assert abs(result.effective_dps - result.raw_dps) < 0.5

    def test_boss_effective_dps_lower_than_raw(self):
        result = SIM.simulate(_scenario(archetype=EnemyArchetype.BOSS), _stats())
        assert result.effective_dps < result.raw_dps


# ---------------------------------------------------------------------------
# Multi-skill rotation
# ---------------------------------------------------------------------------

class TestMultiSkillRotation:
    def test_both_skills_used(self):
        fb = _entry(skill=_fireball(), name="Fireball", priority=1)
        ib = _entry(skill=_ice_bolt(), name="Ice Bolt", priority=2)
        result = SIM.simulate(_scenario([fb, ib], duration=10.0), _stats())
        assert result.skill_usage.get("Fireball", 0) > 0
        assert result.skill_usage.get("Ice Bolt", 0) > 0

    def test_per_skill_damage_tracked(self):
        fb = _entry(skill=_fireball(), name="Fireball")
        ib = _entry(skill=_ice_bolt(), name="Ice Bolt")
        result = SIM.simulate(_scenario([fb, ib], duration=10.0), _stats())
        assert result.skill_damage.get("Fireball", 0) > 0
        assert result.skill_damage.get("Ice Bolt", 0) > 0

    def test_skill_damage_sums_to_total(self):
        fb = _entry(skill=_fireball(), name="Fireball")
        ib = _entry(skill=_ice_bolt(), name="Ice Bolt")
        result = SIM.simulate(_scenario([fb, ib], duration=10.0), _stats())
        summed = sum(result.skill_damage.values())
        assert abs(summed - result.total_damage) < 0.01


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------

class TestPriority:
    def test_higher_priority_casts_first(self):
        fb = _entry(skill=_fireball(), name="Primary", priority=1, cooldown=1.0)
        ib = _entry(skill=_ice_bolt(), name="Secondary", priority=2, cooldown=1.0)
        result = SIM.simulate(
            _scenario([ib, fb], duration=5.0),
            _stats(),
            capture_timeline=True,
        )
        assert result.timeline[0].skill_name == "Primary"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_inputs_same_output(self):
        scenario = _scenario(duration=15.0)
        stats = _stats(spell_damage_pct=30.0)
        r1 = SIM.simulate(scenario, stats)
        r2 = SIM.simulate(scenario, stats)
        assert r1.total_damage == r2.total_damage
        assert r1.total_casts == r2.total_casts
        assert r1.effective_dps == r2.effective_dps


# ---------------------------------------------------------------------------
# Timeline capture
# ---------------------------------------------------------------------------

class TestTimeline:
    def test_timeline_captured_when_enabled(self):
        result = SIM.simulate(_scenario(duration=5.0), _stats(), capture_timeline=True)
        assert len(result.timeline) > 0

    def test_timeline_empty_when_disabled(self):
        result = SIM.simulate(_scenario(duration=5.0), _stats(), capture_timeline=False)
        assert len(result.timeline) == 0

    def test_timeline_events_chronological(self):
        result = SIM.simulate(_scenario(duration=10.0), _stats(), capture_timeline=True)
        times = [e.time for e in result.timeline]
        assert times == sorted(times)


# ---------------------------------------------------------------------------
# DPS math
# ---------------------------------------------------------------------------

class TestDPSMath:
    def test_effective_dps_is_total_over_duration(self):
        result = SIM.simulate(_scenario(duration=10.0), _stats())
        expected = result.total_damage / result.fight_duration
        assert abs(result.effective_dps - expected) < 0.01

    def test_total_casts_equals_sum_of_skill_usage(self):
        fb = _entry(skill=_fireball(), name="Fireball")
        ib = _entry(skill=_ice_bolt(), name="Ice Bolt")
        result = SIM.simulate(_scenario([fb, ib], duration=10.0), _stats())
        assert result.total_casts == sum(result.skill_usage.values())


# ---------------------------------------------------------------------------
# Stat scaling
# ---------------------------------------------------------------------------

class TestStatScaling:
    def test_higher_spell_damage_more_dps(self):
        r_low = SIM.simulate(_scenario(duration=10.0), _stats(spell_damage_pct=0.0))
        r_high = SIM.simulate(_scenario(duration=10.0), _stats(spell_damage_pct=100.0))
        assert r_high.effective_dps > r_low.effective_dps

    def test_crit_chance_increases_dps(self):
        r_no = SIM.simulate(_scenario(duration=10.0), _stats(crit_chance=0.0, crit_multiplier=2.0))
        r_hi = SIM.simulate(_scenario(duration=10.0), _stats(crit_chance=0.5, crit_multiplier=2.0))
        assert r_hi.effective_dps > r_no.effective_dps


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_result_to_dict(self):
        result = SIM.simulate(_scenario(duration=5.0), _stats())
        d = result.to_dict()
        for key in ("total_damage", "effective_dps", "fight_duration",
                     "total_casts", "skill_usage", "skill_damage", "raw_dps"):
            assert key in d


# ---------------------------------------------------------------------------
# Scenario validation
# ---------------------------------------------------------------------------

class TestScenarioValidation:
    def test_zero_duration_raises(self):
        with pytest.raises(ValueError, match="duration"):
            _scenario(duration=0.0)

    def test_empty_rotation_raises(self):
        with pytest.raises(ValueError, match="rotation"):
            CombatScenario(duration_seconds=10.0, rotation=())

    def test_quick_factory(self):
        scenario = CombatScenario.quick(_fireball(), duration=5.0, skill_name="FB")
        result = SIM.simulate(scenario, _stats())
        assert result.total_casts > 0
        assert result.total_damage > 0
