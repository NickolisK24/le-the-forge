"""
Tests for mana resource integration into the combat simulation loop.

Verifies:
  - Skill requires mana to cast (skipped if OOM)
  - Mana regeneration enables casts over time
  - Higher mana cost reduces total casts and DPS
  - Zero-cost skills behave identically to pre-mana system
  - Mana never exceeds max
  - Mana tracking fields populated in SimulationResult
  - Determinism preserved with mana enabled
"""

import pytest

from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
from app.combat.combat_simulator import CombatSimulator
from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyArchetype, EnemyInstance
from app.domain.mana import ManaPool
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


def _skill(mana_cost: float = 0.0, attack_speed: float = 1.0, **kw) -> SkillStatDef:
    defaults = {
        "base_damage": 100.0, "level_scaling": 0.0,
        "attack_speed": attack_speed,
        "scaling_stats": ("spell_damage_pct",),
        "is_spell": True, "damage_types": (DamageType.FIRE,),
        "data_version": "test", "mana_cost": mana_cost,
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


def _entry(skill=None, name="Fireball", **kw):
    return SkillRotationEntry(
        skill_def=skill or _skill(),
        skill_name=name,
        skill_mods=kw.pop("skill_mods", SkillModifiers()),
        **kw,
    )


def _scenario(entries=None, duration=10.0, max_mana=0.0, mana_regen=0.0):
    return CombatScenario(
        duration_seconds=duration,
        enemy=EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY),
        rotation=tuple(entries or [_entry()]),
        max_mana=max_mana,
        mana_regen_rate=mana_regen,
    )


SIM = CombatSimulator()


# ---------------------------------------------------------------------------
# test_skill_requires_mana
# ---------------------------------------------------------------------------

class TestSkillRequiresMana:
    def test_no_mana_no_casts(self):
        """Skill cost > available mana → skill never casts, damage = 0."""
        skill = _skill(mana_cost=50.0)
        entry = _entry(skill=skill, name="Expensive")
        # max_mana=10, regen=0 → can never afford 50
        result = SIM.simulate(_scenario([entry], max_mana=10.0, mana_regen=0.0), _stats())
        assert result.total_casts == 0
        assert result.total_damage == 0.0

    def test_insufficient_mana_skips_cast(self):
        """Start with enough for one cast, no regen → only one cast."""
        skill = _skill(mana_cost=100.0)
        entry = _entry(skill=skill, name="BigSpell")
        # max_mana=100, regen=0 → exactly one cast possible
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=100.0, mana_regen=0.0),
            _stats(),
        )
        assert result.total_casts == 1
        assert result.casts_skipped_oom > 0

    def test_oom_does_not_trigger_cooldown(self):
        """When mana check fails, the skill should remain ready (no cooldown)."""
        skill = _skill(mana_cost=50.0, attack_speed=10.0)  # very fast
        entry = _entry(skill=skill, name="Fast")
        # max_mana=50, regen=25/s → can cast ~once every 2s
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=50.0, mana_regen=25.0),
            _stats(),
        )
        # Should cast multiple times (regen enables periodic casts)
        assert result.total_casts > 1
        # But fewer than unlimited (10s * 10/s = 100 without mana)
        assert result.total_casts < 100


# ---------------------------------------------------------------------------
# test_mana_regeneration_enables_cast
# ---------------------------------------------------------------------------

class TestManaRegeneration:
    def test_regen_enables_later_casts(self):
        """Low starting mana + regen → skill eventually casts."""
        skill = _skill(mana_cost=20.0)
        entry = _entry(skill=skill, name="Spell")
        # Start full at 50, regen=10/s → can sustain casting
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=50.0, mana_regen=10.0),
            _stats(),
        )
        assert result.total_casts > 1
        assert result.total_mana_regenerated > 0

    def test_high_regen_sustains_casting(self):
        """Very high regen should sustain near-unlimited casting."""
        skill = _skill(mana_cost=5.0)
        entry = _entry(skill=skill, name="Cheap")
        # 1000 regen/s easily sustains 5 cost at 1 cast/s
        r_mana = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=100.0, mana_regen=1000.0),
            _stats(),
        )
        r_free = SIM.simulate(
            _scenario([_entry(skill=_skill(mana_cost=0.0))], duration=10.0),
            _stats(),
        )
        # Should be very close to unlimited casting
        assert r_mana.total_casts >= r_free.total_casts - 1


# ---------------------------------------------------------------------------
# test_high_cost_skill_reduces_total_casts
# ---------------------------------------------------------------------------

class TestManaCostAffectsCasts:
    def test_higher_cost_fewer_casts(self):
        """Same skill, different mana costs → higher cost = fewer casts."""
        cheap = _entry(skill=_skill(mana_cost=5.0), name="Cheap")
        expensive = _entry(skill=_skill(mana_cost=40.0), name="Expensive")
        r_cheap = SIM.simulate(
            _scenario([cheap], duration=10.0, max_mana=100.0, mana_regen=10.0),
            _stats(),
        )
        r_expensive = SIM.simulate(
            _scenario([expensive], duration=10.0, max_mana=100.0, mana_regen=10.0),
            _stats(),
        )
        assert r_expensive.total_casts < r_cheap.total_casts

    def test_higher_cost_lower_dps(self):
        """Higher mana cost → fewer casts → lower DPS."""
        cheap = _entry(skill=_skill(mana_cost=5.0), name="Cheap")
        expensive = _entry(skill=_skill(mana_cost=40.0), name="Expensive")
        r_cheap = SIM.simulate(
            _scenario([cheap], duration=10.0, max_mana=100.0, mana_regen=10.0),
            _stats(),
        )
        r_expensive = SIM.simulate(
            _scenario([expensive], duration=10.0, max_mana=100.0, mana_regen=10.0),
            _stats(),
        )
        assert r_expensive.effective_dps < r_cheap.effective_dps


# ---------------------------------------------------------------------------
# test_zero_cost_skill_behaves_normally
# ---------------------------------------------------------------------------

class TestZeroCostBackwardCompat:
    def test_zero_cost_with_mana_pool(self):
        """mana_cost=0 → no mana consumed, same behavior as no-mana system."""
        free_skill = _skill(mana_cost=0.0)
        entry = _entry(skill=free_skill, name="Free")
        r_mana = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=100.0, mana_regen=5.0),
            _stats(),
        )
        r_no_mana = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=0.0),
            _stats(),
        )
        assert r_mana.total_casts == r_no_mana.total_casts
        assert abs(r_mana.total_damage - r_no_mana.total_damage) < 0.01

    def test_no_mana_pool_ignores_cost(self):
        """Without mana pool (max_mana=0), mana_cost is ignored."""
        skill = _skill(mana_cost=999.0)  # absurd cost
        entry = _entry(skill=skill, name="IgnoredCost")
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=0.0),
            _stats(),
        )
        assert result.total_casts > 0  # casts normally


# ---------------------------------------------------------------------------
# test_mana_never_exceeds_max
# ---------------------------------------------------------------------------

class TestManaPool:
    def test_mana_capped_at_max(self):
        """Even with high regen, ManaPool should never exceed max."""
        pool = ManaPool(max_mana=100.0, current_mana=99.0, mana_regeneration_rate=1000.0)
        restored = pool.regenerate(1.0)
        assert pool.current_mana == 100.0
        assert restored == 1.0  # only 1 mana was needed

    def test_scenario_creates_fresh_pool(self):
        """Each call to create_mana_pool() returns independent state."""
        scenario = _scenario(max_mana=100.0, mana_regen=10.0)
        pool1 = scenario.create_mana_pool()
        pool2 = scenario.create_mana_pool()
        pool1.spend(50.0)
        assert pool2.current_mana == 100.0  # independent

    def test_no_mana_pool_when_disabled(self):
        """max_mana=0 → create_mana_pool() returns None."""
        scenario = _scenario(max_mana=0.0)
        assert scenario.create_mana_pool() is None


# ---------------------------------------------------------------------------
# Mana tracking in SimulationResult
# ---------------------------------------------------------------------------

class TestManaTracking:
    def test_mana_spent_tracked(self):
        skill = _skill(mana_cost=10.0)
        entry = _entry(skill=skill)
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=200.0, mana_regen=50.0),
            _stats(),
        )
        assert result.total_mana_spent > 0
        assert result.total_mana_spent == result.total_casts * 10.0

    def test_mana_regenerated_tracked(self):
        skill = _skill(mana_cost=10.0)
        entry = _entry(skill=skill)
        result = SIM.simulate(
            _scenario([entry], duration=10.0, max_mana=200.0, mana_regen=50.0),
            _stats(),
        )
        assert result.total_mana_regenerated > 0

    def test_oom_skips_tracked(self):
        skill = _skill(mana_cost=100.0)
        entry = _entry(skill=skill)
        result = SIM.simulate(
            _scenario([entry], duration=5.0, max_mana=100.0, mana_regen=0.0),
            _stats(),
        )
        assert result.casts_skipped_oom > 0

    def test_to_dict_includes_mana_when_used(self):
        skill = _skill(mana_cost=10.0)
        entry = _entry(skill=skill)
        result = SIM.simulate(
            _scenario([entry], duration=5.0, max_mana=100.0, mana_regen=20.0),
            _stats(),
        )
        d = result.to_dict()
        assert "total_mana_spent" in d
        assert "total_mana_regenerated" in d

    def test_to_dict_omits_mana_when_unused(self):
        result = SIM.simulate(_scenario(duration=5.0), _stats())
        d = result.to_dict()
        assert "total_mana_spent" not in d


# ---------------------------------------------------------------------------
# Determinism with mana
# ---------------------------------------------------------------------------

class TestDeterminismWithMana:
    def test_same_inputs_same_output(self):
        skill = _skill(mana_cost=15.0)
        entry = _entry(skill=skill)
        scenario = _scenario([entry], duration=20.0, max_mana=100.0, mana_regen=10.0)
        stats = _stats(spell_damage_pct=30.0)
        r1 = SIM.simulate(scenario, stats)
        r2 = SIM.simulate(scenario, stats)
        assert r1.total_damage == r2.total_damage
        assert r1.total_casts == r2.total_casts
        assert r1.total_mana_spent == r2.total_mana_spent
        assert r1.casts_skipped_oom == r2.casts_skipped_oom
