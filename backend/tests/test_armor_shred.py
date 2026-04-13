"""
Tests for armor shred modeling in the DPS calculation path.
"""

import pytest

from app.domain.armor_shred import (
    ARMOR_PER_STACK,
    STACK_DURATION,
    armor_shred_amount,
    steady_state_stacks,
)
from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.enemies.enemy_defense import EnemyDefenseEngine
from app.engines.combat_engine import _get_skill_def
from app.engines.stat_engine import BuildStats
from app.skills.skill_execution import SkillExecutionEngine


def _stats(**overrides) -> BuildStats:
    s = BuildStats()
    s.base_damage = 85
    s.crit_chance = 0.07
    s.crit_multiplier = 1.5
    s.attack_speed = 1.3
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# Steady-state stack calculation
# ---------------------------------------------------------------------------

class TestSteadyStateStacks:
    def test_zero_shred_chance_zero_stacks(self):
        assert steady_state_stacks(0.0, 2.0) == 0.0

    def test_zero_hits_per_second_zero_stacks(self):
        assert steady_state_stacks(85.0, 0.0) == 0.0

    def test_high_shred_fast_attack_no_cap(self):
        # 85% chance, 3 hits/sec, 5 hit_count = 0.85*3*5*4 = 51 stacks (no cap per 1.4.3)
        stacks = steady_state_stacks(85.0, 3.0, hit_count=5)
        assert abs(stacks - 51.0) < 0.01

    def test_low_shred_partial_stacks(self):
        # 20% chance, 1 hit/sec, 1 hit = 0.20*1*1*4 = 0.8 stacks
        stacks = steady_state_stacks(20.0, 1.0, hit_count=1)
        assert abs(stacks - 0.8) < 0.01

    def test_moderate_shred_moderate_stacks(self):
        # 50% chance, 2 hits/sec, 1 hit = 0.50*2*1*4 = 4 stacks
        stacks = steady_state_stacks(50.0, 2.0, hit_count=1)
        assert abs(stacks - 4.0) < 0.01

    def test_over_100_percent_clamped(self):
        # 175% chance → clamped to 100%
        stacks = steady_state_stacks(175.0, 1.0, hit_count=1)
        assert abs(stacks - 4.0) < 0.01  # 1.0*1*1*4 = 4


# ---------------------------------------------------------------------------
# Armor shred amount
# ---------------------------------------------------------------------------

class TestArmorShredAmount:
    def test_amount_is_stacks_times_per_stack(self):
        amount = armor_shred_amount(50.0, 2.0, hit_count=1)
        stacks = steady_state_stacks(50.0, 2.0, hit_count=1)
        assert abs(amount - stacks * ARMOR_PER_STACK) < 0.01

    def test_zero_shred_zero_amount(self):
        assert armor_shred_amount(0.0, 2.0) == 0.0

    def test_high_rate_uncapped_amount(self):
        # 100% chance × 10 hits/s × 5 hit_count × 4s duration = 200 stacks (no cap)
        amount = armor_shred_amount(100.0, 10.0, hit_count=5)
        assert amount == 200 * ARMOR_PER_STACK  # 200 * 100 = 20000

    def test_effective_armor_never_negative(self):
        amount = armor_shred_amount(100.0, 10.0, hit_count=5)
        enemy_armor = 1000
        effective = max(0, enemy_armor - amount)
        assert effective == 0  # 1000 - 20000 = 0 (clamped)


# ---------------------------------------------------------------------------
# EnemyDefenseEngine with armor shred
# ---------------------------------------------------------------------------

class TestDefenseWithArmorShred:
    def test_shred_reduces_physical_mitigation(self):
        engine = SkillExecutionEngine()
        defense = EnemyDefenseEngine()
        skill_def = _get_skill_def("Umbral Blades")
        stats = _stats(physical_damage_pct=100.0)
        sr = engine.execute(skill_def, stats, level=20)

        enemy = EnemyInstance.from_stats(EnemyStats(health=10000, armor=1000))

        r_no_shred = defense.apply_defenses(sr, enemy, armor_shred=0.0)
        r_with_shred = defense.apply_defenses(sr, enemy, armor_shred=500.0)

        assert r_with_shred.damage_dealt > r_no_shred.damage_dealt

    def test_full_shred_removes_armor(self):
        defense = EnemyDefenseEngine()
        engine = SkillExecutionEngine()
        skill_def = _get_skill_def("Umbral Blades")
        stats = _stats(physical_damage_pct=100.0)
        sr = engine.execute(skill_def, stats, level=20)

        enemy = EnemyInstance.from_stats(EnemyStats(health=10000, armor=1000))
        dummy = EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY)

        r_full_shred = defense.apply_defenses(sr, enemy, armor_shred=2000.0)
        r_dummy = defense.apply_defenses(sr, dummy)

        # Full shred on 1000 armor = 0 effective armor ≈ training dummy
        assert abs(r_full_shred.damage_dealt - r_dummy.damage_dealt) < 1.0

    def test_shred_stacks_with_penetration(self):
        defense = EnemyDefenseEngine()
        engine = SkillExecutionEngine()
        skill_def = _get_skill_def("Umbral Blades")
        stats = _stats(physical_damage_pct=100.0)
        sr = engine.execute(skill_def, stats, level=20)

        enemy = EnemyInstance.from_stats(EnemyStats(
            health=10000, armor=1000,
            resistances={"physical": 30.0},
        ))

        r_nothing = defense.apply_defenses(sr, enemy)
        r_pen_only = defense.apply_defenses(sr, enemy, penetration={"physical": 15.0})
        r_shred_only = defense.apply_defenses(sr, enemy, armor_shred=500.0)
        r_both = defense.apply_defenses(sr, enemy, penetration={"physical": 15.0}, armor_shred=500.0)

        # Both > either alone > nothing
        assert r_both.damage_dealt > r_pen_only.damage_dealt
        assert r_both.damage_dealt > r_shred_only.damage_dealt
        assert r_pen_only.damage_dealt > r_nothing.damage_dealt
        assert r_shred_only.damage_dealt > r_nothing.damage_dealt


# ---------------------------------------------------------------------------
# DPS impact verification
# ---------------------------------------------------------------------------

class TestDPSImpact:
    def test_t5_shred_increases_dps_20_to_50_pct(self):
        """T5 armor shred with Umbral Blades vs BOSS (1000 armor) = 20-50% improvement."""
        from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
        from app.combat.combat_simulator import CombatSimulator

        skill_def = _get_skill_def("Umbral Blades")
        stats_no_shred = _stats(physical_damage_pct=100.0)
        stats_with_shred = _stats(physical_damage_pct=100.0, armour_shred_chance=85.0)

        entry = SkillRotationEntry(skill_def=skill_def, skill_name="Umbral Blades", level=20)
        enemy = EnemyInstance.from_archetype(EnemyArchetype.BOSS)

        scenario = CombatScenario(
            duration_seconds=10.0,
            enemy=enemy,
            rotation=(entry,),
        )

        sim = CombatSimulator()
        r_no = sim.simulate(scenario, stats_no_shred)
        r_yes = sim.simulate(scenario, stats_with_shred)

        improvement = (r_yes.effective_dps / r_no.effective_dps - 1.0) * 100
        assert 80 <= improvement <= 120, f"Improvement was {improvement:.1f}%, expected ~100%"

    def test_no_shred_vs_training_dummy_same(self):
        """Armor shred has no effect against training dummy (0 armor)."""
        from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
        from app.combat.combat_simulator import CombatSimulator

        skill_def = _get_skill_def("Umbral Blades")
        stats_no = _stats()
        stats_yes = _stats(armour_shred_chance=85.0)

        entry = SkillRotationEntry(skill_def=skill_def, skill_name="Umbral Blades", level=20)
        dummy = EnemyInstance.from_archetype(EnemyArchetype.TRAINING_DUMMY)

        scenario = CombatScenario(duration_seconds=10.0, enemy=dummy, rotation=(entry,))

        sim = CombatSimulator()
        r_no = sim.simulate(scenario, stats_no)
        r_yes = sim.simulate(scenario, stats_yes)

        assert abs(r_no.effective_dps - r_yes.effective_dps) < 0.5
