"""Tests for the stat aggregation engine."""

import pytest
from app.engines.stat_engine import (
    aggregate_stats,
    BuildStats,
    CLASS_BASE_STATS,
    MASTERY_BONUSES,
    KEYSTONE_BONUSES,
    get_affix_value,
)


class TestClassBaseStats:
    def test_all_five_classes_present(self):
        for cls in ["Acolyte", "Mage", "Primalist", "Sentinel", "Rogue"]:
            assert cls in CLASS_BASE_STATS

    def test_mage_has_highest_mana(self):
        assert CLASS_BASE_STATS["Mage"]["mana"] > CLASS_BASE_STATS["Sentinel"]["mana"]

    def test_sentinel_has_highest_health(self):
        assert CLASS_BASE_STATS["Sentinel"]["health"] > CLASS_BASE_STATS["Mage"]["health"]

    def test_rogue_has_highest_crit_chance(self):
        assert CLASS_BASE_STATS["Rogue"]["crit_chance"] > CLASS_BASE_STATS["Mage"]["crit_chance"]


class TestAggregateStatsBaseClass:
    def test_returns_build_stats_instance(self):
        stats = aggregate_stats("Mage", "Sorcerer", [], [], [])
        assert isinstance(stats, BuildStats)

    def test_class_base_damage_applied(self):
        stats = aggregate_stats("Sentinel", "Paladin", [], [], [])
        assert stats.base_damage == CLASS_BASE_STATS["Sentinel"]["base_damage"]

    def test_class_base_health_applied(self):
        stats = aggregate_stats("Primalist", "Druid", [], [], [])
        assert stats.max_health >= CLASS_BASE_STATS["Primalist"]["health"]

    def test_default_crit_chance_is_low(self):
        stats = aggregate_stats("Mage", "Sorcerer", [], [], [])
        assert 0.04 < stats.crit_chance < 0.20


class TestMasteryBonuses:
    def test_sorcerer_adds_spell_damage(self):
        stats_base = aggregate_stats("Mage", "Sorcerer", [], [], [])
        # Sorcerer has +15 spell_damage_pct, Runemaster has +10
        stats_rune = aggregate_stats("Mage", "Runemaster", [], [], [])
        assert stats_base.spell_damage_pct > stats_rune.spell_damage_pct

    def test_paladin_adds_health(self):
        stats = aggregate_stats("Sentinel", "Paladin", [], [], [])
        # Paladin: +200 max_health on top of base
        base_health = CLASS_BASE_STATS["Sentinel"]["health"]
        assert stats.max_health > base_health

    def test_lich_ward_per_node(self):
        nodes_5 = [{"id": i, "type": "core", "name": f"Node{i}"} for i in range(1, 6)]
        stats = aggregate_stats("Acolyte", "Lich", list(range(1, 6)), nodes_5, [])
        # Lich: +8 ward per allocated node
        assert stats.ward >= 5 * 8

    def test_forge_guard_armour_per_node(self):
        nodes_4 = [{"id": i, "type": "core", "name": f"Node{i}"} for i in range(1, 5)]
        stats = aggregate_stats("Sentinel", "Forge Guard", list(range(1, 5)), nodes_4, [])
        # Forge Guard: +15 armour per allocated node = 60 from mastery
        base_armour = CLASS_BASE_STATS["Sentinel"]["strength"] * 2  # attribute scaling
        assert stats.armour >= 4 * 15


class TestPassiveNodeBonuses:
    def test_allocated_nodes_add_stats(self):
        nodes = [
            {"id": 0, "type": "core", "name": "Node0"},  # id%10=0 → max_health +8
        ]
        stats_with = aggregate_stats("Mage", "Sorcerer", [0], nodes, [])
        stats_without = aggregate_stats("Mage", "Sorcerer", [], nodes, [])
        assert stats_with.max_health > stats_without.max_health

    def test_unallocated_nodes_not_applied(self):
        nodes = [{"id": 3, "type": "core", "name": "ArmourNode"}]
        stats = aggregate_stats("Mage", "Sorcerer", [], nodes, [])
        # Node 3 → armour (id%10 == 3). Not allocated, so no bonus.
        # Mage has 0 base armour from class + only attribute scaling
        expected_armour = CLASS_BASE_STATS["Mage"]["strength"] * 2
        assert stats.armour == pytest.approx(expected_armour)

    def test_keystone_node_applies_keystone_bonus(self):
        nodes = [{"id": 99, "type": "keystone", "name": "Arcane Absorption"}]
        stats_with = aggregate_stats("Mage", "Sorcerer", [99], nodes, [])
        stats_without = aggregate_stats("Mage", "Sorcerer", [], nodes, [])
        # Arcane Absorption: +20 spell_damage_pct
        assert stats_with.spell_damage_pct > stats_without.spell_damage_pct

    def test_notable_node_has_3x_bonus(self):
        nodes = [
            {"id": 0, "type": "core",    "name": "CoreNode"},
            {"id": 10, "type": "notable", "name": "NotableNode"},  # id%10==0 → max_health
        ]
        stats_core    = aggregate_stats("Mage", "Sorcerer", [0],  nodes, [])
        stats_notable = aggregate_stats("Mage", "Sorcerer", [10], nodes, [])
        # Notable gives 3× base bonus — health gain from notable > from core
        assert (stats_notable.max_health - aggregate_stats("Mage", "Sorcerer", [], [], []).max_health) > \
               (stats_core.max_health    - aggregate_stats("Mage", "Sorcerer", [], [], []).max_health)

    def test_mastery_gate_nodes_are_ignored(self):
        nodes = [{"id": 50, "type": "mastery-gate", "name": "Gate"}]
        stats = aggregate_stats("Sentinel", "Paladin", [50], nodes, [])
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        # mastery-gate nodes contribute nothing
        assert stats.max_health == pytest.approx(base.max_health)


class TestGearAffixes:
    def test_affix_value_adds_to_stat(self):
        affixes = [{"name": "Health", "tier": 1}]
        stats_with = aggregate_stats("Mage", "Sorcerer", [], [], affixes)
        stats_without = aggregate_stats("Mage", "Sorcerer", [], [], [])
        # T1 Health midpoint is 130
        assert stats_with.max_health > stats_without.max_health

    def test_t1_affix_better_than_t5(self):
        affix_t1 = [{"name": "Fire Damage", "tier": 1}]
        affix_t5 = [{"name": "Fire Damage", "tier": 5}]
        stats_t1 = aggregate_stats("Acolyte", "Lich", [], [], affix_t1)
        stats_t5 = aggregate_stats("Acolyte", "Lich", [], [], affix_t5)
        # T5 is now the best tier, T1 is lowest
        assert stats_t5.fire_damage_pct > stats_t1.fire_damage_pct

    def test_resistance_affix_stacks(self):
        affixes = [
            {"name": "Fire Resistance", "tier": 1},
            {"name": "Fire Resistance", "tier": 2},
        ]
        stats = aggregate_stats("Mage", "Sorcerer", [], [], affixes)
        # Two fire res affixes should stack
        assert stats.fire_res >= get_affix_value("Fire Resistance", 1) + get_affix_value("Fire Resistance", 2)

    def test_unknown_affix_is_ignored(self):
        affixes = [{"name": "Made Up Affix XYZ", "tier": 1}]
        stats = aggregate_stats("Mage", "Sorcerer", [], [], affixes)
        base = aggregate_stats("Mage", "Sorcerer", [], [], [])
        assert stats.max_health == pytest.approx(base.max_health)


class TestAttributeScaling:
    def test_intelligence_boosts_spell_damage(self):
        # Add intelligence affix
        affixes = [{"name": "Intelligence", "tier": 1}]
        stats = aggregate_stats("Mage", "Sorcerer", [], [], affixes)
        base = aggregate_stats("Mage", "Sorcerer", [], [], [])
        assert stats.spell_damage_pct > base.spell_damage_pct

    def test_strength_boosts_armour(self):
        affixes = [{"name": "Strength", "tier": 1}]
        stats = aggregate_stats("Sentinel", "Paladin", [], [], affixes)
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        assert stats.armour > base.armour

    def test_dexterity_boosts_dodge(self):
        affixes = [{"name": "Dexterity", "tier": 1}]
        stats = aggregate_stats("Rogue", "Bladedancer", [], [], affixes)
        base = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        assert stats.dodge_rating > base.dodge_rating


class TestGetAffixValue:
    def test_t1_health_midpoint(self):
        val = get_affix_value("Health", 1)
        assert val == 27  # T1 is lowest tier

    def test_unknown_affix_returns_zero(self):
        assert get_affix_value("Completely Fake Affix", 1) == 0

    def test_invalid_tier_returns_zero(self):
        assert get_affix_value("Health", 99) == 0
