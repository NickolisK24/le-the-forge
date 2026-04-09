"""
Tests for the Enemy Defense Engine.

Verifies:
  - Higher resistance reduces damage
  - Higher armor reduces physical damage
  - Non-physical damage bypasses armor
  - Penetration reduces effective resistance
  - Training dummy takes full damage
  - Boss enemies mitigate significantly
  - Mitigation percentage is computed correctly
  - Effective DPS accounts for defenses
  - Debug trace captures defense pipeline
  - Convenience methods (from_profile, from_archetype) work
"""

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.domain.skill import SkillStatDef
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats
from app.skills.skill_execution import SkillExecutionEngine, SkillExecutionResult
from app.enemies.enemy_defense import EnemyDefenseEngine, DefensedDamageResult


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


def _physical_strike(**kw) -> SkillStatDef:
    defaults = {
        "base_damage": 100.0, "level_scaling": 0.0, "attack_speed": 1.0,
        "scaling_stats": ("physical_damage_pct", "melee_damage_pct"),
        "is_melee": True, "damage_types": (DamageType.PHYSICAL,),
        "data_version": "test",
    }
    defaults.update(kw)
    return SkillStatDef(**defaults)


def _mixed_skill() -> SkillStatDef:
    return SkillStatDef(
        base_damage=100.0, level_scaling=0.0, attack_speed=1.0,
        scaling_stats=("spell_damage_pct",), is_spell=True,
        damage_types=(DamageType.FIRE, DamageType.PHYSICAL),
        data_version="test",
    )


def _enemy(armor: int = 0, **resistances: float) -> EnemyInstance:
    return EnemyInstance.from_stats(EnemyStats(
        health=10000, armor=armor, resistances=resistances,
    ))


SKILL_ENGINE = SkillExecutionEngine()
DEFENSE_ENGINE = EnemyDefenseEngine()


def _exec_skill(skill=None, stats=None):
    return SKILL_ENGINE.execute(skill or _fireball(), stats or _stats(), level=1)


# ---------------------------------------------------------------------------
# Resistance
# ---------------------------------------------------------------------------

class TestResistance:
    def test_higher_resistance_reduces_damage(self):
        skill_result = _exec_skill()
        r_low = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=10.0))
        r_high = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=50.0))
        assert r_high.damage_dealt < r_low.damage_dealt

    def test_zero_resistance_full_damage(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=0.0))
        assert abs(result.damage_dealt - skill_result.average_hit) < 0.01

    def test_50_pct_resistance_halves_damage(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=50.0))
        expected = skill_result.average_hit * 0.5
        assert abs(result.damage_dealt - expected) < 0.5

    def test_resistance_only_applies_to_matching_type(self):
        """Fire resistance doesn't reduce cold damage."""
        cold_skill = SkillStatDef(
            base_damage=100.0, level_scaling=0.0, attack_speed=1.0,
            scaling_stats=("spell_damage_pct",), is_spell=True,
            damage_types=(DamageType.COLD,), data_version="test",
        )
        skill_result = SKILL_ENGINE.execute(cold_skill, _stats(), level=1)
        # Enemy has high fire res but zero cold res
        result = DEFENSE_ENGINE.apply_defenses(
            skill_result, _enemy(fire=75.0, cold=0.0),
        )
        assert abs(result.damage_dealt - skill_result.average_hit) < 0.01

    def test_resistance_reduction_tracked(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=40.0))
        assert result.resistance_reduction > 0


# ---------------------------------------------------------------------------
# Armor
# ---------------------------------------------------------------------------

class TestArmor:
    def test_higher_armor_reduces_physical_damage(self):
        skill_result = _exec_skill(_physical_strike())
        r_low = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(armor=200))
        r_high = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(armor=2000))
        assert r_high.damage_dealt < r_low.damage_dealt

    def test_armor_does_not_reduce_fire_damage(self):
        skill_result = _exec_skill(_fireball())
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(armor=5000))
        # No fire resistance → full damage regardless of armor
        assert abs(result.damage_dealt - skill_result.average_hit) < 0.01

    def test_armor_reduction_tracked(self):
        skill_result = _exec_skill(_physical_strike())
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(armor=500))
        assert result.armor_reduction > 0

    def test_zero_armor_no_physical_mitigation(self):
        skill_result = _exec_skill(_physical_strike())
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(armor=0))
        assert result.armor_reduction == 0.0


# ---------------------------------------------------------------------------
# Mixed damage types
# ---------------------------------------------------------------------------

class TestMixedDamage:
    def test_mixed_type_applies_both_defenses(self):
        """Fire+Physical skill: fire resisted, physical gets armor+res."""
        skill_result = SKILL_ENGINE.execute(_mixed_skill(), _stats(), level=1)
        enemy = _enemy(armor=500, fire=30.0, physical=20.0)
        result = DEFENSE_ENGINE.apply_defenses(skill_result, enemy)
        # Both resistance and armor should reduce damage
        assert result.damage_dealt < skill_result.average_hit
        assert result.resistance_reduction > 0
        assert result.armor_reduction > 0


# ---------------------------------------------------------------------------
# Penetration
# ---------------------------------------------------------------------------

class TestPenetration:
    def test_penetration_reduces_effective_resistance(self):
        skill_result = _exec_skill()
        enemy = _enemy(fire=50.0)
        r_no_pen = DEFENSE_ENGINE.apply_defenses(skill_result, enemy)
        r_with_pen = DEFENSE_ENGINE.apply_defenses(
            skill_result, enemy, penetration={"fire": 30.0},
        )
        assert r_with_pen.damage_dealt > r_no_pen.damage_dealt

    def test_full_penetration_negates_resistance(self):
        skill_result = _exec_skill()
        enemy = _enemy(fire=40.0)
        result = DEFENSE_ENGINE.apply_defenses(
            skill_result, enemy, penetration={"fire": 40.0},
        )
        # Penetration fully cancels resistance
        assert abs(result.damage_dealt - skill_result.average_hit) < 0.5


# ---------------------------------------------------------------------------
# Dodge (expected value)
# ---------------------------------------------------------------------------

class TestDodge:
    def test_dodge_chance_currently_zero(self):
        """EnemyStats has no dodge_rating, so dodge is always 0."""
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy())
        assert result.dodge_chance_pct == 0.0
        assert result.dodge_reduction == 0.0


# ---------------------------------------------------------------------------
# Archetypes
# ---------------------------------------------------------------------------

class TestArchetypes:
    def test_training_dummy_takes_full_damage(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses_from_archetype(
            skill_result, EnemyArchetype.TRAINING_DUMMY,
        )
        assert abs(result.damage_dealt - skill_result.average_hit) < 0.01
        assert result.mitigation_pct < 0.01

    def test_boss_mitigates_significantly(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses_from_archetype(
            skill_result, EnemyArchetype.BOSS,
        )
        assert result.mitigation_pct > 20.0  # bosses have 60% fire res

    def test_boss_harder_than_normal(self):
        skill_result = _exec_skill()
        r_normal = DEFENSE_ENGINE.apply_defenses_from_archetype(
            skill_result, EnemyArchetype.NORMAL,
        )
        r_boss = DEFENSE_ENGINE.apply_defenses_from_archetype(
            skill_result, EnemyArchetype.BOSS,
        )
        assert r_boss.damage_dealt < r_normal.damage_dealt


# ---------------------------------------------------------------------------
# Mitigation summary
# ---------------------------------------------------------------------------

class TestMitigationSummary:
    def test_mitigation_pct_correct(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=40.0))
        expected_pct = (result.damage_mitigated / result.damage_before) * 100
        assert abs(result.mitigation_pct - expected_pct) < 0.01

    def test_damage_conservation(self):
        """damage_dealt + damage_mitigated = damage_before."""
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=30.0))
        assert abs(
            result.damage_dealt + result.damage_mitigated - result.damage_before
        ) < 0.01


# ---------------------------------------------------------------------------
# Effective DPS
# ---------------------------------------------------------------------------

class TestEffectiveDPS:
    def test_effective_dps_lower_than_raw(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=40.0))
        assert result.effective_dps < skill_result.dps

    def test_training_dummy_dps_unchanged(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses_from_archetype(
            skill_result, EnemyArchetype.TRAINING_DUMMY,
        )
        assert abs(result.effective_dps - skill_result.dps) < 0.01


# ---------------------------------------------------------------------------
# Debug trace
# ---------------------------------------------------------------------------

class TestDebugTrace:
    def test_debug_captured(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(
            skill_result, _enemy(fire=30.0, armor=200), capture_debug=True,
        )
        assert result.debug is not None
        assert "damage_by_type_before" in result.debug
        assert "resistance_detail" in result.debug

    def test_debug_not_captured_by_default(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy())
        assert result.debug is None


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_to_dict_all_fields(self):
        skill_result = _exec_skill()
        result = DEFENSE_ENGINE.apply_defenses(skill_result, _enemy(fire=30.0))
        d = result.to_dict()
        assert "damage_dealt" in d
        assert "damage_mitigated" in d
        assert "mitigation_pct" in d
        assert "effective_dps" in d
        assert "per_type_damage" in d
