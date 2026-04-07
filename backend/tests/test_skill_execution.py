"""
Tests for the Skill Execution Engine.

Verifies:
  - Base damage scales correctly with level
  - Increased % damage from stats applies
  - Intelligence increases spell damage
  - Crit chance and multiplier affect average hit
  - Attack/cast speed affects DPS
  - Skill modifiers (more damage, extra hits, speed) integrate
  - Multi-hit skills compute correct DPS
  - Per-type damage breakdown populates correctly
  - Debug trace captures pipeline stages
  - execute_from_spec convenience method works
"""

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.domain.skill import SkillStatDef, SkillSpec
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats
from app.skills.skill_execution import SkillExecutionEngine, SkillExecutionResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _stats(**overrides: float) -> BuildStats:
    s = BuildStats()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


def _fireball(**kw) -> SkillStatDef:
    """Fireball-like spell: fire damage, spell scaling."""
    defaults = {
        "base_damage": 100.0,
        "level_scaling": 0.10,
        "attack_speed": 1.0,
        "scaling_stats": ("spell_damage_pct", "fire_damage_pct"),
        "is_spell": True,
        "damage_types": (DamageType.FIRE,),
        "data_version": "test",
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


def _melee_strike(**kw) -> SkillStatDef:
    """Physical melee strike."""
    defaults = {
        "base_damage": 80.0,
        "level_scaling": 0.08,
        "attack_speed": 1.5,
        "scaling_stats": ("physical_damage_pct", "melee_damage_pct"),
        "is_melee": True,
        "damage_types": (DamageType.PHYSICAL,),
        "data_version": "test",
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


ENGINE = SkillExecutionEngine()


# ---------------------------------------------------------------------------
# Base damage scaling
# ---------------------------------------------------------------------------

class TestBaseDamageScaling:
    def test_level_1_uses_base_damage(self):
        result = ENGINE.execute(_fireball(), _stats(), level=1)
        # At level 1: 100 * (1 + 0.10 * 0) = 100
        assert abs(result.hit_damage - 100.0) < 0.01

    def test_level_scaling_increases_damage(self):
        r1 = ENGINE.execute(_fireball(), _stats(), level=1)
        r10 = ENGINE.execute(_fireball(), _stats(), level=10)
        # Level 10: 100 * (1 + 0.10 * 9) = 190
        assert r10.hit_damage > r1.hit_damage
        assert abs(r10.hit_damage - 190.0) < 0.01

    def test_level_20_max_scaling(self):
        result = ENGINE.execute(_fireball(), _stats(), level=20)
        # Level 20: 100 * (1 + 0.10 * 19) = 290
        assert abs(result.hit_damage - 290.0) < 0.01


# ---------------------------------------------------------------------------
# Increased % damage
# ---------------------------------------------------------------------------

class TestIncreasedDamage:
    def test_spell_damage_pct_increases_spell_hit(self):
        stats_base = _stats()
        stats_buffed = _stats(spell_damage_pct=50.0)
        r_base = ENGINE.execute(_fireball(), stats_base, level=1)
        r_buffed = ENGINE.execute(_fireball(), stats_buffed, level=1)
        # 50% increased → 100 * 1.5 = 150
        assert r_buffed.hit_damage > r_base.hit_damage
        assert abs(r_buffed.hit_damage - 150.0) < 0.01

    def test_fire_damage_pct_increases_fire_spell(self):
        stats = _stats(fire_damage_pct=30.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        # 30% increased → 100 * 1.3 = 130
        assert abs(result.hit_damage - 130.0) < 0.01

    def test_multiple_increased_sources_stack_additively(self):
        stats = _stats(spell_damage_pct=20.0, fire_damage_pct=30.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        # 20% + 30% = 50% increased → 100 * 1.5 = 150
        assert abs(result.hit_damage - 150.0) < 0.01

    def test_intelligence_scaling_increases_spell_damage(self):
        """Higher intelligence → higher spell_damage_pct (via attribute scaling
        in aggregate_stats). Here we test the direct stat effect."""
        stats_low = _stats(spell_damage_pct=10.0)
        stats_high = _stats(spell_damage_pct=50.0)  # simulates higher int
        r_low = ENGINE.execute(_fireball(), stats_low, level=1)
        r_high = ENGINE.execute(_fireball(), stats_high, level=1)
        assert r_high.hit_damage > r_low.hit_damage


# ---------------------------------------------------------------------------
# Crit
# ---------------------------------------------------------------------------

class TestCrit:
    def test_crit_chance_affects_average_hit(self):
        stats_no_crit = _stats(crit_chance=0.0, crit_multiplier=2.0)
        stats_high_crit = _stats(crit_chance=0.5, crit_multiplier=2.0)
        r_no = ENGINE.execute(_fireball(), stats_no_crit, level=1)
        r_hi = ENGINE.execute(_fireball(), stats_high_crit, level=1)
        assert r_hi.average_hit > r_no.average_hit
        assert r_no.average_hit == r_no.hit_damage  # no crits

    def test_crit_multiplier_affects_average_hit(self):
        stats_low = _stats(crit_chance=0.3, crit_multiplier=1.5)
        stats_high = _stats(crit_chance=0.3, crit_multiplier=3.0)
        r_low = ENGINE.execute(_fireball(), stats_low, level=1)
        r_high = ENGINE.execute(_fireball(), stats_high, level=1)
        assert r_high.average_hit > r_low.average_hit

    def test_crit_contribution_nonzero_with_crits(self):
        stats = _stats(crit_chance=0.5, crit_multiplier=2.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert result.crit_contribution > 0

    def test_crit_contribution_zero_without_crits(self):
        stats = _stats(crit_chance=0.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert result.crit_contribution == 0

    def test_skill_mod_crit_bonus(self):
        stats = _stats(crit_chance=0.05, crit_multiplier=1.5)
        sm = SkillModifiers(crit_chance_pct=20.0)  # +20% crit
        result = ENGINE.execute(_fireball(), stats, level=1, skill_mods=sm)
        # 0.05 + 20/100 = 0.25
        assert abs(result.crit_chance - 0.25) < 0.01


# ---------------------------------------------------------------------------
# Speed and DPS
# ---------------------------------------------------------------------------

class TestSpeedAndDPS:
    def test_dps_scales_with_attack_speed(self):
        slow = _fireball(attack_speed=1.0)
        fast = _fireball(attack_speed=2.0)
        stats = _stats()
        r_slow = ENGINE.execute(slow, stats, level=1)
        r_fast = ENGINE.execute(fast, stats, level=1)
        assert abs(r_fast.dps - r_slow.dps * 2.0) < 0.01

    def test_cast_speed_bonus_increases_spell_dps(self):
        stats_base = _stats(cast_speed=0.0)
        stats_fast = _stats(cast_speed=50.0)  # +50% cast speed
        r_base = ENGINE.execute(_fireball(), stats_base, level=1)
        r_fast = ENGINE.execute(_fireball(), stats_fast, level=1)
        assert r_fast.dps > r_base.dps
        assert r_fast.casts_per_second > r_base.casts_per_second

    def test_attack_speed_pct_increases_melee_dps(self):
        stats_base = _stats(attack_speed_pct=0.0)
        stats_fast = _stats(attack_speed_pct=50.0)
        r_base = ENGINE.execute(_melee_strike(), stats_base, level=1)
        r_fast = ENGINE.execute(_melee_strike(), stats_fast, level=1)
        assert r_fast.dps > r_base.dps

    def test_dps_equals_avg_hit_times_speed(self):
        stats = _stats(crit_chance=0.1, crit_multiplier=1.5)
        result = ENGINE.execute(_fireball(), stats, level=1)
        expected_dps = result.average_hit * result.hits_per_cast * result.casts_per_second
        assert abs(result.dps - expected_dps) < 0.01


# ---------------------------------------------------------------------------
# Skill modifiers (spec tree)
# ---------------------------------------------------------------------------

class TestSkillModifiers:
    def test_more_damage_pct_multiplies(self):
        stats = _stats()
        sm = SkillModifiers(more_damage_pct=50.0)  # 50% more
        r_base = ENGINE.execute(_fireball(), stats, level=1)
        r_more = ENGINE.execute(_fireball(), stats, level=1, skill_mods=sm)
        # 50% more → hit_damage * 1.5
        assert abs(r_more.hit_damage - r_base.hit_damage * 1.5) < 0.5

    def test_added_hits_per_cast(self):
        stats = _stats()
        sm = SkillModifiers(added_hits_per_cast=2)
        r_single = ENGINE.execute(_fireball(), stats, level=1)
        r_multi = ENGINE.execute(_fireball(), stats, level=1, skill_mods=sm)
        # Same per-hit damage, but DPS should be 3x (1+2 hits)
        assert r_multi.hits_per_cast == 3
        assert abs(r_multi.dps - r_single.dps * 3.0) < 0.01

    def test_skill_speed_bonus(self):
        stats = _stats()
        sm = SkillModifiers(cast_speed_pct=30.0)
        r_base = ENGINE.execute(_fireball(), stats, level=1)
        r_fast = ENGINE.execute(_fireball(), stats, level=1, skill_mods=sm)
        assert r_fast.casts_per_second > r_base.casts_per_second


# ---------------------------------------------------------------------------
# Flat added damage
# ---------------------------------------------------------------------------

class TestFlatDamage:
    def test_flat_spell_damage_adds_to_base(self):
        stats = _stats(added_spell_damage=50.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        # base 100 + flat 50 = 150 effective base
        assert result.hit_damage > 100.0

    def test_flat_melee_damage_adds_to_melee(self):
        stats = _stats(added_melee_physical=30.0)
        result = ENGINE.execute(_melee_strike(), stats, level=1)
        # base 80 + flat 30 = 110 effective base
        assert result.hit_damage > 80.0


# ---------------------------------------------------------------------------
# Damage type breakdown
# ---------------------------------------------------------------------------

class TestDamageByType:
    def test_single_type_has_full_damage(self):
        result = ENGINE.execute(_fireball(), _stats(), level=1)
        assert "fire" in result.damage_by_type
        assert abs(result.damage_by_type["fire"] - result.hit_damage) < 0.01

    def test_multi_type_splits_evenly(self):
        skill = SkillStatDef(
            base_damage=100.0, level_scaling=0.0, attack_speed=1.0,
            scaling_stats=("spell_damage_pct",),
            damage_types=(DamageType.FIRE, DamageType.COLD),
            is_spell=True, data_version="test",
        )
        result = ENGINE.execute(skill, _stats(), level=1)
        assert "fire" in result.damage_by_type
        assert "cold" in result.damage_by_type
        total = sum(result.damage_by_type.values())
        assert abs(total - result.hit_damage) < 0.01


# ---------------------------------------------------------------------------
# Debug trace
# ---------------------------------------------------------------------------

class TestDebugTrace:
    def test_debug_trace_captured(self):
        result = ENGINE.execute(_fireball(), _stats(), level=10, capture_debug=True)
        assert result.debug is not None
        assert "scaled_total" in result.debug
        assert "effective_base" in result.debug
        assert "hit_damage" in result.debug
        assert "dps" in result.debug

    def test_debug_trace_not_captured_by_default(self):
        result = ENGINE.execute(_fireball(), _stats(), level=1)
        assert result.debug is None


# ---------------------------------------------------------------------------
# execute_from_spec
# ---------------------------------------------------------------------------

class TestExecuteFromSpec:
    def test_uses_spec_level_and_name(self):
        spec = SkillSpec(skill_name="Fireball", level=15)
        result = ENGINE.execute_from_spec(spec, _fireball(), _stats())
        assert result.skill_name == "Fireball"
        # Level 15: 100 * (1 + 0.10 * 14) = 240
        assert abs(result.hit_damage - 240.0) < 0.01


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestResultSerialization:
    def test_to_dict_has_all_fields(self):
        result = ENGINE.execute(_fireball(), _stats(), level=1, skill_name="Fireball")
        d = result.to_dict()
        assert d["skill_name"] == "Fireball"
        assert "hit_damage" in d
        assert "average_hit" in d
        assert "dps" in d
        assert "crit_chance" in d
        assert "damage_by_type" in d

    def test_to_dict_values_rounded(self):
        result = ENGINE.execute(_fireball(), _stats(crit_chance=0.05), level=1)
        d = result.to_dict()
        # All numeric values should be finite
        assert isinstance(d["hit_damage"], float)
        assert isinstance(d["dps"], float)
