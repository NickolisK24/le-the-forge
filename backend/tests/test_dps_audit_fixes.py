"""
Tests for DPS audit fixes — skill data, skill tree wiring, affix scaling, armor shred.
"""

import pytest

from app.domain.skill_modifiers import SkillModifiers
from app.engines.combat_engine import calculate_dps, _get_skill_def
from app.engines.stat_engine import BuildStats, get_affix_value


def _rogue_stats(**overrides) -> BuildStats:
    """Create BuildStats with Rogue base values."""
    stats = BuildStats()
    stats.base_damage = 85
    stats.crit_chance = 0.07
    stats.crit_multiplier = 1.5
    stats.attack_speed = 1.3
    stats.dexterity = 18
    for k, v in overrides.items():
        setattr(stats, k, v)
    return stats


# ---------------------------------------------------------------------------
# Fix 1: Umbral Blades exists in game data
# ---------------------------------------------------------------------------

class TestUmbralBladesExists:
    def test_get_skill_def_returns_valid(self):
        sd = _get_skill_def("Umbral Blades")
        assert sd is not None
        assert sd.base_damage > 0
        assert sd.attack_speed > 0

    def test_is_throwing_skill(self):
        sd = _get_skill_def("Umbral Blades")
        assert sd.is_throwing is True
        assert sd.is_melee is False
        assert sd.is_spell is False

    def test_produces_nonzero_dps(self):
        result = calculate_dps(_rogue_stats(), "Umbral Blades", skill_level=20)
        assert result.dps > 0
        assert result.hit_damage > 0


# ---------------------------------------------------------------------------
# Fix 2: Skill tree nodes increase DPS
# ---------------------------------------------------------------------------

class TestSkillTreeWiring:
    def test_skill_modifiers_increase_dps(self):
        stats = _rogue_stats(physical_damage_pct=50.0)
        base = calculate_dps(stats, "Umbral Blades", skill_level=20)

        sm = SkillModifiers(more_damage_pct=50.0, crit_chance_pct=10.0)
        buffed = calculate_dps(stats, "Umbral Blades", skill_level=20, skill_modifiers=sm)

        assert buffed.dps > base.dps
        # 50% more damage should roughly multiply DPS by ~1.5
        assert buffed.dps > base.dps * 1.3

    def test_added_hits_per_cast_increases_dps(self):
        stats = _rogue_stats()
        base = calculate_dps(stats, "Umbral Blades", skill_level=20)

        sm = SkillModifiers(added_hits_per_cast=2)
        multi = calculate_dps(stats, "Umbral Blades", skill_level=20, skill_modifiers=sm)

        # Base has 3 hits, +2 = 5 hits → should be ~5/3 = 1.67x
        assert multi.dps > base.dps * 1.5

    def test_crit_multiplier_pct_increases_dps(self):
        stats = _rogue_stats(crit_chance=0.5)
        base = calculate_dps(stats, "Umbral Blades", skill_level=20)

        sm = SkillModifiers(crit_multiplier_pct=50.0)
        buffed = calculate_dps(stats, "Umbral Blades", skill_level=20, skill_modifiers=sm)

        assert buffed.dps > base.dps


# ---------------------------------------------------------------------------
# Fix 3: Class-aware passive modulo fallback
# ---------------------------------------------------------------------------

class TestPassiveClassAwareCycle:
    def test_rogue_passives_contribute_physical_damage(self):
        """Rogue passive cycle should contribute physical_damage_pct more often."""
        from app.engines.stat_engine import aggregate_stats
        # No passives
        stats_no_passives = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        # 20 passive nodes allocated (IDs 0-19)
        nodes = [{"id": i, "type": "minor", "name": f"node_{i}"} for i in range(20)]
        stats_with = aggregate_stats("Rogue", "Bladedancer", list(range(20)), nodes, [])
        # Rogue passives should add physical_damage_pct
        assert stats_with.physical_damage_pct > stats_no_passives.physical_damage_pct

    def test_rogue_passives_add_dexterity(self):
        from app.engines.stat_engine import aggregate_stats
        stats_no = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        nodes = [{"id": i, "type": "minor", "name": f"node_{i}"} for i in range(20)]
        stats_with = aggregate_stats("Rogue", "Bladedancer", list(range(20)), nodes, [])
        assert stats_with.dexterity > stats_no.dexterity

    def test_mage_passives_differ_from_rogue(self):
        from app.engines.stat_engine import aggregate_stats
        nodes = [{"id": i, "type": "minor", "name": f"node_{i}"} for i in range(20)]
        rogue = aggregate_stats("Rogue", "Bladedancer", list(range(20)), nodes, [])
        mage = aggregate_stats("Mage", "Sorcerer", list(range(20)), nodes, [])
        # Mage should have more spell_damage_pct, Rogue more physical_damage_pct
        assert mage.spell_damage_pct > rogue.spell_damage_pct
        assert rogue.physical_damage_pct > mage.physical_damage_pct


# ---------------------------------------------------------------------------
# Fix 4: Affix value normalization (100x correction)
# ---------------------------------------------------------------------------

class TestAffixValueScaling:
    def test_t5_melee_physical_in_correct_range(self):
        """T5 Added Melee Physical should be ~21-26, not 2100-2600."""
        val = get_affix_value("Added Melee Physical Damage", 5)
        assert 15 <= val <= 30, f"T5 melee phys = {val}, expected 15-30"

    def test_t7_melee_physical_in_correct_range(self):
        val = get_affix_value("Added Melee Physical Damage", 7)
        assert 40 <= val <= 70, f"T7 melee phys = {val}, expected 40-70"

    def test_t7_crit_multiplier_unchanged(self):
        """Crit multiplier is already in correct scale (45 = 45% crit multi)."""
        val = get_affix_value("Added Critical Strike Multiplier", 7)
        assert 40 <= val <= 50, f"T7 crit multi = {val}, expected 40-50"

    def test_t5_physical_penetration_unchanged(self):
        """Physical pen should remain at face value (8-9)."""
        val = get_affix_value("Physical Penetration", 5)
        assert 5 <= val <= 12, f"T5 phys pen = {val}, expected 5-12"

    def test_flat_damage_used_in_dps_correctly(self):
        """T5 melee physical should add ~23 to DPS, not 2350."""
        stats = _rogue_stats()
        # Pre-set the added_melee_physical as if gear applied it
        val = get_affix_value("Added Melee Physical Damage", 5)
        stats.added_melee_physical = val
        result = calculate_dps(stats, "Umbral Blades", skill_level=20)
        # With ~23 flat added damage, hit_damage should not exceed 200
        assert result.hit_damage < 500, f"Hit damage {result.hit_damage} too high (affix value probably still 100x)"


# ---------------------------------------------------------------------------
# Fix 5: Armor shred modeling
# ---------------------------------------------------------------------------

class TestArmorShredModeling:
    def test_armor_shred_increases_dps_vs_armored_enemy(self):
        from app.enemies.enemy_defense import EnemyDefenseEngine
        from app.domain.enemy import EnemyInstance, EnemyStats
        from app.skills.skill_execution import SkillExecutionEngine

        engine = SkillExecutionEngine()
        defense = EnemyDefenseEngine()
        skill_def = _get_skill_def("Umbral Blades")
        stats = _rogue_stats(physical_damage_pct=100.0)

        sr = engine.execute(skill_def, stats, level=20, skill_name="Umbral Blades")
        enemy = EnemyInstance.from_stats(EnemyStats(health=10000, armor=1000))

        # Without penetration
        r_no_pen = defense.apply_defenses(sr, enemy)
        # With penetration
        r_with_pen = defense.apply_defenses(sr, enemy, penetration={"physical": 15.0})

        assert r_with_pen.damage_dealt > r_no_pen.damage_dealt
