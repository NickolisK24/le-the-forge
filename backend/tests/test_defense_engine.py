"""Tests for the defense / EHP engine."""

import pytest
from app.engines.stat_engine import aggregate_stats, BuildStats
from app.engines.defense_engine import calculate_defense, DefenseResult, RES_CAP


def _base_sentinel() -> BuildStats:
    return aggregate_stats("Sentinel", "Paladin", [], [], [])


def _base_mage() -> BuildStats:
    return aggregate_stats("Mage", "Sorcerer", [], [], [])


class TestCalculateDefense:
    def test_returns_defense_result(self):
        result = calculate_defense(_base_sentinel())
        assert isinstance(result, DefenseResult)

    def test_effective_hp_gte_max_health(self):
        """EHP must always be >= raw health."""
        result = calculate_defense(_base_sentinel())
        assert result.effective_hp >= result.max_health

    def test_zero_mitigation_ehp_equals_health(self):
        """With 0 armour and 0 resistances, EHP = health."""
        stats = BuildStats()
        stats.max_health = 1000
        result = calculate_defense(stats)
        assert result.effective_hp == 1000

    def test_high_armour_increases_ehp(self):
        base = _base_sentinel()
        armoured = aggregate_stats("Sentinel", "Paladin", [], [],
                                   [{"name": "Increased Armor", "tier": 1}])
        base_r = calculate_defense(base)
        arm_r  = calculate_defense(armoured)
        assert arm_r.effective_hp > base_r.effective_hp

    def test_high_resistance_increases_ehp(self):
        base = _base_sentinel()
        capped = aggregate_stats("Sentinel", "Paladin", [], [],
                                  [{"name": "Fire Resistance", "tier": 1}])
        base_r = calculate_defense(base)
        cap_r  = calculate_defense(capped)
        assert cap_r.effective_hp >= base_r.effective_hp

    def test_resistance_capped_at_75(self):
        stats = BuildStats()
        stats.max_health = 1000
        stats.fire_res = 200  # way above cap
        result = calculate_defense(stats)
        assert result.fire_res == RES_CAP

    def test_resistances_capped_individually(self):
        stats = BuildStats()
        stats.max_health = 1000
        stats.fire_res = 100
        stats.cold_res = 10
        result = calculate_defense(stats)
        assert result.fire_res == RES_CAP
        assert result.cold_res == 10

    def test_armour_reduction_formula(self):
        """ArmorReduction = Armor / (Armor + 1000)"""
        stats = BuildStats()
        stats.max_health = 1000
        stats.armour = 1000  # 1000/(1000+1000) = 50%
        result = calculate_defense(stats)
        assert result.armor_reduction_pct == 50

    def test_survivability_score_range(self):
        result = calculate_defense(_base_sentinel())
        assert 0 <= result.survivability_score <= 100

    def test_low_resistances_produce_weaknesses(self):
        """New build with no resistances should flag weaknesses."""
        stats = BuildStats()
        stats.max_health = 1500
        result = calculate_defense(stats)
        assert len(result.weaknesses) > 0

    def test_low_health_is_weakness(self):
        stats = BuildStats()
        stats.max_health = 500
        result = calculate_defense(stats)
        assert any("health" in w.lower() for w in result.weaknesses)

    def test_low_armour_is_weakness(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.armour = 100  # below 500 threshold
        result = calculate_defense(stats)
        assert any("armour" in w.lower() for w in result.weaknesses)

    def test_capped_fire_res_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.fire_res = 75
        result = calculate_defense(stats)
        assert any("fire" in s.lower() for s in result.strengths)

    def test_large_health_is_strength(self):
        stats = BuildStats()
        stats.max_health = 3000
        result = calculate_defense(stats)
        assert any("health" in s.lower() for s in result.strengths)

    def test_high_ward_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.ward = 300
        result = calculate_defense(stats)
        assert any("ward" in s.lower() for s in result.strengths)

    def test_to_dict_has_all_keys(self):
        result = calculate_defense(_base_sentinel())
        d = result.to_dict()
        for key in ["max_health", "effective_hp", "armor_reduction_pct", "avg_resistance",
                    "fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res",
                    "dodge_chance_pct", "ward_regen_per_second", "ward_decay_per_second",
                    "net_ward_per_second", "survivability_score", "weaknesses", "strengths",
                    "physical_res", "poison_res", "block_chance_pct", "block_mitigation_pct",
                    "endurance_pct", "endurance_threshold_pct", "crit_avoidance_pct",
                    "glancing_blow_pct", "stun_avoidance_pct", "ward_buffer", "total_ehp",
                    "leech_pct", "health_on_kill", "sustain_score"]:
            assert key in d, f"Missing key: {key}"


class TestDodgeChance:
    def test_zero_dodge_rating_gives_zero_chance(self):
        stats = BuildStats()
        stats.max_health = 1000
        result = calculate_defense(stats)
        assert result.dodge_chance_pct == 0.0

    def test_dodge_formula(self):
        """DodgeChancePct = dodge_rating / (dodge_rating + 1000) * 100"""
        stats = BuildStats()
        stats.max_health = 1000
        stats.dodge_rating = 1000  # 1000/(1000+1000)*100 = 50%
        result = calculate_defense(stats)
        assert result.dodge_chance_pct == 50.0

    def test_high_dodge_becomes_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.dodge_rating = 250  # ~20% dodge
        result = calculate_defense(stats)
        assert any("dodge" in s.lower() for s in result.strengths)

    def test_dodge_never_exceeds_100(self):
        stats = BuildStats()
        stats.max_health = 1000
        stats.dodge_rating = 1_000_000
        result = calculate_defense(stats)
        assert result.dodge_chance_pct < 100.0


class TestWardSustainability:
    def test_zero_ward_has_no_decay(self):
        stats = BuildStats()
        stats.max_health = 1000
        result = calculate_defense(stats)
        assert result.ward_decay_per_second == 0.0
        assert result.net_ward_per_second == 0.0

    def test_ward_decays_at_base_rate(self):
        """With 0 retention, decay = ward * 0.25/s"""
        stats = BuildStats()
        stats.max_health = 1000
        stats.ward = 400
        result = calculate_defense(stats)
        assert result.ward_decay_per_second == 100.0  # 400 * 0.25

    def test_ward_retention_reduces_decay(self):
        """25% retention → decay rate = max(0, 0.25 - 0.25) = 0"""
        stats = BuildStats()
        stats.max_health = 1000
        stats.ward = 400
        stats.ward_retention_pct = 25.0
        result = calculate_defense(stats)
        assert result.ward_decay_per_second == 0.0

    def test_ward_regen_contributes_positively(self):
        stats = BuildStats()
        stats.max_health = 1000
        stats.ward = 0
        stats.ward_regen = 10.0
        result = calculate_defense(stats)
        assert result.ward_regen_per_second == 10.0
        assert result.net_ward_per_second == 10.0

    def test_positive_net_ward_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.ward = 0
        stats.ward_regen = 20.0
        result = calculate_defense(stats)
        assert any("sustaining" in s.lower() or "ward" in s.lower() for s in result.strengths)

    def test_ward_decay_warning_flagged_as_weakness(self):
        """Ward decaying with non-trivial ward pool should warn."""
        stats = BuildStats()
        stats.max_health = 2000
        stats.ward = 300  # non-trivial ward
        stats.ward_retention_pct = 0.0
        stats.ward_regen = 0.0
        result = calculate_defense(stats)
        assert any("ward" in w.lower() for w in result.weaknesses)


class TestBlockMechanics:
    def test_block_chance_increases_ehp(self):
        base = BuildStats()
        base.max_health = 2000
        blocked = BuildStats()
        blocked.max_health = 2000
        blocked.block_chance = 40
        blocked.block_effectiveness = 500
        assert calculate_defense(blocked).effective_hp > calculate_defense(base).effective_hp

    def test_block_chance_capped_at_100(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.block_chance = 150  # over cap
        stats.block_effectiveness = 500
        result = calculate_defense(stats)
        assert result.block_chance_pct == 100.0

    def test_block_mitigation_formula(self):
        """BlockMitigation = effectiveness / (effectiveness + 1000)"""
        stats = BuildStats()
        stats.max_health = 2000
        stats.block_effectiveness = 1000
        result = calculate_defense(stats)
        assert result.block_mitigation_pct == 50.0

    def test_block_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.block_chance = 40
        result = calculate_defense(stats)
        assert any("block" in s.lower() for s in result.strengths)


class TestEnduranceMechanics:
    def test_endurance_increases_ehp(self):
        base = BuildStats()
        base.max_health = 2000
        endured = BuildStats()
        endured.max_health = 2000
        endured.endurance = 40
        endured.endurance_threshold = 60
        assert calculate_defense(endured).effective_hp > calculate_defense(base).effective_hp

    def test_endurance_capped_at_60(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.endurance = 80  # over LE cap
        result = calculate_defense(stats)
        assert result.endurance_pct == 60.0

    def test_endurance_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.endurance = 30
        result = calculate_defense(stats)
        assert any("endurance" in s.lower() for s in result.strengths)


class TestCritAvoidanceAndGlancingBlow:
    def test_crit_avoidance_increases_ehp(self):
        base = BuildStats()
        base.max_health = 2000
        avoided = BuildStats()
        avoided.max_health = 2000
        avoided.crit_avoidance = 80
        assert calculate_defense(avoided).effective_hp > calculate_defense(base).effective_hp

    def test_glancing_blow_increases_ehp(self):
        base = BuildStats()
        base.max_health = 2000
        glancing = BuildStats()
        glancing.max_health = 2000
        glancing.glancing_blow = 40
        assert calculate_defense(glancing).effective_hp > calculate_defense(base).effective_hp

    def test_crit_avoidance_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.crit_avoidance = 60
        result = calculate_defense(stats)
        assert any("crit avoidance" in s.lower() for s in result.strengths)


class TestWardBuffer:
    def test_ward_adds_to_total_ehp(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.ward = 500
        result = calculate_defense(stats)
        assert result.ward_buffer == 500
        assert result.total_ehp > result.effective_hp

    def test_total_ehp_includes_ward(self):
        stats = BuildStats()
        stats.max_health = 2000
        result = calculate_defense(stats)
        assert result.total_ehp == result.effective_hp + result.ward_buffer


class TestPhysicalPoisonResistance:
    def test_physical_res_in_result(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.physical_res = 30
        result = calculate_defense(stats)
        assert result.physical_res == 30

    def test_poison_res_in_result(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.poison_res = 45
        result = calculate_defense(stats)
        assert result.poison_res == 45

    def test_physical_res_affects_avg_resistance(self):
        base = BuildStats()
        base.max_health = 2000
        with_phys = BuildStats()
        with_phys.max_health = 2000
        with_phys.physical_res = 50
        assert calculate_defense(with_phys).avg_resistance > calculate_defense(base).avg_resistance


class TestSustainMetrics:
    def test_leech_in_result(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.leech = 5
        result = calculate_defense(stats)
        assert result.leech_pct == 5.0

    def test_health_on_kill_in_result(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.health_on_kill = 20
        result = calculate_defense(stats)
        assert result.health_on_kill == 20.0

    def test_sustain_score_increases_with_leech(self):
        base = BuildStats()
        base.max_health = 2000
        sustained = BuildStats()
        sustained.max_health = 2000
        sustained.leech = 8
        assert calculate_defense(sustained).sustain_score > calculate_defense(base).sustain_score

    def test_no_sustain_is_weakness(self):
        stats = BuildStats()
        stats.max_health = 2000
        result = calculate_defense(stats)
        assert any("sustain" in w.lower() for w in result.weaknesses)

    def test_leech_is_strength(self):
        stats = BuildStats()
        stats.max_health = 2000
        stats.leech = 5
        result = calculate_defense(stats)
        assert any("leech" in s.lower() for s in result.strengths)
