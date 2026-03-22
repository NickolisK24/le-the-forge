"""Tests for the optimization / upgrade advisor engine."""

import pytest
from app.engines.stat_engine import aggregate_stats, BuildStats
from app.engines.optimization_engine import get_stat_upgrades, StatUpgrade, STAT_TEST_INCREMENTS


def _mage_stats() -> BuildStats:
    return aggregate_stats("Mage", "Sorcerer", [], [], [])


def _sentinel_stats() -> BuildStats:
    return aggregate_stats("Sentinel", "Paladin", [], [], [])


class TestGetStatUpgrades:
    def test_returns_list_of_stat_upgrades(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20)
        assert isinstance(upgrades, list)
        assert all(isinstance(u, StatUpgrade) for u in upgrades)

    def test_returns_top_n_results(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=5)
        assert len(upgrades) <= 5

    def test_default_top_n_is_5(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20)
        assert len(upgrades) <= 5

    def test_custom_top_n(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=3)
        assert len(upgrades) == 3

    def test_sorted_by_dps_gain_descending(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=10)
        gains = [u.dps_gain_pct for u in upgrades]
        assert gains == sorted(gains, reverse=True)

    def test_spell_damage_is_top_upgrade_for_mage(self):
        """Sorcerer/Fireball should rank spell damage highly."""
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=5)
        top_stats = [u.stat for u in upgrades[:3]]
        # Spell damage, crit multiplier, or crit chance should be in top 3
        spell_stats = {"spell_damage_pct", "crit_multiplier_pct", "crit_chance_pct", "cast_speed"}
        assert any(s in spell_stats for s in top_stats)

    def test_physical_damage_ranks_high_for_sentinel(self):
        upgrades = get_stat_upgrades(_sentinel_stats(), "Rive", 20, top_n=5)
        top_stats = [u.stat for u in upgrades[:3]]
        physical_stats = {"physical_damage_pct", "crit_multiplier_pct", "crit_chance_pct", "attack_speed_pct"}
        assert any(s in physical_stats for s in top_stats)

    def test_unknown_skill_returns_zero_dps_gains(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fake Skill XYZ", 20, top_n=5)
        # With 0 base DPS, all DPS gains are 0
        for u in upgrades:
            assert u.dps_gain_pct == 0.0

    def test_ehp_gain_present_for_health_upgrade(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=len(STAT_TEST_INCREMENTS))
        health_upgrades = [u for u in upgrades if u.stat == "max_health"]
        assert len(health_upgrades) > 0
        assert health_upgrades[0].ehp_gain_pct > 0

    def test_dps_gain_pct_is_float(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20)
        for u in upgrades:
            assert isinstance(u.dps_gain_pct, float)

    def test_to_dict_has_required_keys(self):
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=1)
        assert len(upgrades) >= 1
        d = upgrades[0].to_dict()
        for key in ["stat", "label", "dps_gain_pct", "ehp_gain_pct"]:
            assert key in d

    def test_crit_multiplier_ranks_high_for_crit_build(self):
        """A build with high crit chance should rank crit multiplier highly."""
        crit_stats = aggregate_stats("Mage", "Sorcerer", [], [],
                                     [{"name": "Increased Critical Strike Chance", "tier": 5}] * 3)
        upgrades = get_stat_upgrades(crit_stats, "Fireball", 20, top_n=10)
        top_stats = [u.stat for u in upgrades[:6]]
        assert "crit_multiplier_pct" in top_stats

    def test_no_negative_dps_in_relevant_stats(self):
        """Damage stat upgrades should always improve DPS, never hurt it."""
        upgrades = get_stat_upgrades(_mage_stats(), "Fireball", 20, top_n=len(STAT_TEST_INCREMENTS))
        damage_keys = {"spell_damage_pct", "crit_multiplier_pct", "crit_chance_pct",
                       "cast_speed", "fire_damage_pct"}
        for u in upgrades:
            if u.stat in damage_keys:
                assert u.dps_gain_pct >= 0, f"{u.stat} gave negative DPS gain"
