"""
Tests for ailment system integration into the skill execution and combat pipelines.

Verifies:
  - Ailment application chance produces ailment DPS
  - Bleed, Ignite, Poison each produce steady-state DPS
  - Zero chance produces zero ailment DPS
  - Ailment DPS adds to total_dps
  - Combat simulator aggregates ailment DPS
  - Ailment damage scaling responds to BuildStats bonuses
"""

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyArchetype, EnemyInstance
from app.domain.skill import SkillStatDef
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats
from app.skills.skill_execution import SkillExecutionEngine, SkillExecutionResult
from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
from app.combat.combat_simulator import CombatSimulator


# ---------------------------------------------------------------------------
# Helpers
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


ENGINE = SkillExecutionEngine()
SIM = CombatSimulator()


# ---------------------------------------------------------------------------
# Ailment DPS in SkillExecutionResult
# ---------------------------------------------------------------------------

class TestAilmentInSkillExecution:
    def test_ignite_chance_produces_ignite_dps(self):
        stats = _stats(ignite_chance_pct=50.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert "ignite" in result.ailment_dps
        assert result.ailment_dps["ignite"] > 0

    def test_bleed_chance_produces_bleed_dps(self):
        stats = _stats(bleed_chance_pct=40.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert "bleed" in result.ailment_dps
        assert result.ailment_dps["bleed"] > 0

    def test_poison_chance_produces_poison_dps(self):
        stats = _stats(poison_chance_pct=60.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert "poison" in result.ailment_dps
        assert result.ailment_dps["poison"] > 0

    def test_zero_chance_no_ailment_dps(self):
        stats = _stats()  # all chances are 0
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert result.ailment_dps == {}

    def test_ailment_dps_adds_to_total(self):
        stats = _stats(ignite_chance_pct=100.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert result.total_dps > result.dps
        expected = result.dps + sum(result.ailment_dps.values())
        assert abs(result.total_dps - expected) < 0.01

    def test_multiple_ailments_stack(self):
        stats = _stats(ignite_chance_pct=50.0, bleed_chance_pct=30.0, poison_chance_pct=40.0)
        result = ENGINE.execute(_fireball(), stats, level=1)
        assert len(result.ailment_dps) == 3
        assert result.total_dps > result.dps

    def test_higher_chance_higher_dps(self):
        r_low = ENGINE.execute(_fireball(), _stats(ignite_chance_pct=20.0), level=1)
        r_high = ENGINE.execute(_fireball(), _stats(ignite_chance_pct=80.0), level=1)
        assert r_high.ailment_dps["ignite"] > r_low.ailment_dps["ignite"]


# ---------------------------------------------------------------------------
# Ailment damage scaling
# ---------------------------------------------------------------------------

class TestAilmentScaling:
    def test_ignite_damage_pct_increases_ignite_dps(self):
        base = _stats(ignite_chance_pct=100.0)
        buffed = _stats(ignite_chance_pct=100.0, ignite_damage_pct=50.0)
        r_base = ENGINE.execute(_fireball(), base, level=1)
        r_buff = ENGINE.execute(_fireball(), buffed, level=1)
        assert r_buff.ailment_dps["ignite"] > r_base.ailment_dps["ignite"]

    def test_ailment_damage_pct_affects_all(self):
        base = _stats(bleed_chance_pct=100.0)
        buffed = _stats(bleed_chance_pct=100.0, ailment_damage_pct=30.0)
        r_base = ENGINE.execute(_fireball(), base, level=1)
        r_buff = ENGINE.execute(_fireball(), buffed, level=1)
        assert r_buff.ailment_dps["bleed"] > r_base.ailment_dps["bleed"]


# ---------------------------------------------------------------------------
# Ailment DPS in CombatSimulator
# ---------------------------------------------------------------------------

class TestAilmentInCombatSim:
    def test_combat_sim_includes_ailment_dps(self):
        stats = _stats(ignite_chance_pct=50.0)
        entry = SkillRotationEntry(skill_def=_fireball(), skill_name="FB")
        scenario = CombatScenario(
            duration_seconds=10.0,
            enemy=EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY),
            rotation=(entry,),
        )
        result = SIM.simulate(scenario, stats)
        assert "ignite" in result.ailment_dps
        assert result.ailment_dps["ignite"] > 0
        assert result.total_dps_with_ailments > result.effective_dps

    def test_no_ailment_chance_empty_in_sim(self):
        entry = SkillRotationEntry(skill_def=_fireball(), skill_name="FB")
        scenario = CombatScenario(
            duration_seconds=10.0,
            enemy=EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY),
            rotation=(entry,),
        )
        result = SIM.simulate(scenario, _stats())
        assert result.ailment_dps == {}

    def test_to_dict_includes_ailment_when_present(self):
        stats = _stats(poison_chance_pct=50.0)
        entry = SkillRotationEntry(skill_def=_fireball(), skill_name="FB")
        scenario = CombatScenario(
            duration_seconds=5.0,
            enemy=EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY),
            rotation=(entry,),
        )
        result = SIM.simulate(scenario, stats)
        d = result.to_dict()
        assert "ailment_dps" in d

    def test_to_dict_omits_ailment_when_absent(self):
        entry = SkillRotationEntry(skill_def=_fireball(), skill_name="FB")
        scenario = CombatScenario(
            duration_seconds=5.0,
            enemy=EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY),
            rotation=(entry,),
        )
        result = SIM.simulate(scenario, _stats())
        d = result.to_dict()
        assert "ailment_dps" not in d
