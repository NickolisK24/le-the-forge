"""
Tests for EnemyStats and EnemyArchetype (Step 1 — Enemy Archetype System).

Validates:
  - Default stats load correctly for each archetype
  - Resistance cap (75%) applied via capped_resistances
  - Boss archetypes scale above Elite which scales above Normal
"""

import pytest
from app.domain.enemy import EnemyStats, EnemyArchetype
from app.constants.defense import RES_CAP


# ---------------------------------------------------------------------------
# EnemyStats
# ---------------------------------------------------------------------------

class TestEnemyStats:
    def test_defaults_are_zero(self):
        s = EnemyStats()
        assert s.health == 0
        assert s.armor == 0
        assert s.resistances == {}
        assert s.status_effects == ()

    def test_is_frozen(self):
        s = EnemyStats(health=100)
        with pytest.raises((AttributeError, TypeError)):
            s.health = 999  # type: ignore[misc]

    def test_capped_resistances_within_cap(self):
        s = EnemyStats(resistances={"fire": 50.0, "cold": 30.0})
        capped = s.capped_resistances
        assert capped["fire"] == 50.0
        assert capped["cold"] == 30.0

    def test_capped_resistances_above_cap(self):
        s = EnemyStats(resistances={"fire": 90.0, "void": 100.0})
        capped = s.capped_resistances
        assert capped["fire"] == float(RES_CAP)
        assert capped["void"] == float(RES_CAP)

    def test_capped_resistances_at_exactly_cap(self):
        s = EnemyStats(resistances={"fire": float(RES_CAP)})
        assert s.capped_resistances["fire"] == float(RES_CAP)

    def test_capped_resistances_empty(self):
        assert EnemyStats().capped_resistances == {}

    def test_status_effects_tuple(self):
        s = EnemyStats(status_effects=("stunned", "burning"))
        assert "stunned" in s.status_effects
        assert "burning" in s.status_effects


# ---------------------------------------------------------------------------
# EnemyArchetype — default stats
# ---------------------------------------------------------------------------

class TestEnemyArchetypeDefaults:
    def test_training_dummy_is_zero(self):
        s = EnemyArchetype.TRAINING_DUMMY.base_stats()
        assert s.health == 0
        assert s.armor == 0
        assert s.resistances == {}
        assert s.status_effects == ()

    def test_normal_has_positive_health_and_armor(self):
        s = EnemyArchetype.NORMAL.base_stats()
        assert s.health > 0
        assert s.armor > 0

    def test_elite_has_positive_health_and_armor(self):
        s = EnemyArchetype.ELITE.base_stats()
        assert s.health > 0
        assert s.armor > 0

    def test_boss_has_positive_health_and_armor(self):
        s = EnemyArchetype.BOSS.base_stats()
        assert s.health > 0
        assert s.armor > 0

    def test_all_archetypes_return_enemy_stats(self):
        for archetype in EnemyArchetype:
            assert isinstance(archetype.base_stats(), EnemyStats)


# ---------------------------------------------------------------------------
# EnemyArchetype — resistance caps
# ---------------------------------------------------------------------------

class TestEnemyArchetypeResistanceCaps:
    def test_normal_resistances_within_cap(self):
        s = EnemyArchetype.NORMAL.base_stats()
        for res in s.resistances.values():
            assert res <= RES_CAP

    def test_elite_resistances_within_cap(self):
        s = EnemyArchetype.ELITE.base_stats()
        for res in s.resistances.values():
            assert res <= RES_CAP

    def test_boss_resistances_within_cap(self):
        s = EnemyArchetype.BOSS.base_stats()
        for res in s.resistances.values():
            assert res <= RES_CAP

    def test_capped_resistances_never_exceed_cap(self):
        s = EnemyStats(resistances={"fire": 200.0, "cold": -10.0})
        for val in s.capped_resistances.values():
            assert val <= RES_CAP


# ---------------------------------------------------------------------------
# EnemyArchetype — boss scales above elite scales above normal
# ---------------------------------------------------------------------------

class TestEnemyArchetypeScaling:
    def test_boss_health_greater_than_elite(self):
        assert EnemyArchetype.BOSS.base_stats().health > EnemyArchetype.ELITE.base_stats().health

    def test_elite_health_greater_than_normal(self):
        assert EnemyArchetype.ELITE.base_stats().health > EnemyArchetype.NORMAL.base_stats().health

    def test_normal_health_greater_than_dummy(self):
        assert EnemyArchetype.NORMAL.base_stats().health > EnemyArchetype.TRAINING_DUMMY.base_stats().health

    def test_boss_armor_greater_than_elite(self):
        assert EnemyArchetype.BOSS.base_stats().armor > EnemyArchetype.ELITE.base_stats().armor

    def test_elite_armor_greater_than_normal(self):
        assert EnemyArchetype.ELITE.base_stats().armor > EnemyArchetype.NORMAL.base_stats().armor

    def test_boss_fire_resistance_greater_than_normal(self):
        boss   = EnemyArchetype.BOSS.base_stats().resistances.get("fire", 0.0)
        normal = EnemyArchetype.NORMAL.base_stats().resistances.get("fire", 0.0)
        assert boss > normal
