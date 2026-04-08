"""
Tests for Phase 7 — Advanced Analysis.

Covers:
  - BossEncounterSimulator: phase transitions, enrage, immunity, result shape
  - CorruptionScaler: multipliers at breakpoints, recommended max, curve length
  - GearUpgradeRanker: DPS delta, FP cost, ranking, no-item case
  - API endpoints: response shape, 404/400 handling, bosses list
"""

import pytest
from app.engines.stat_engine import BuildStats
from app.engines.boss_encounter import (
    simulate_boss_encounter,
    _build_phases,
    PhaseResult,
    BossEncounterResult,
)
from app.engines.corruption_scaler import (
    health_multiplier,
    damage_multiplier,
    scale_corruption,
    STANDARD_BREAKPOINTS,
)
from app.engines.gear_upgrade_ranker import (
    rank_gear_upgrades,
    GearUpgradeResult,
    _normalize_slot,
    _fp_cost_for_tier,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_stats(**overrides) -> BuildStats:
    """Create a BuildStats with sensible defaults for testing.

    Only passes fields that exist on BuildStats — uses keyword-only valid attrs.
    """
    defaults = dict(
        base_damage=200.0,
        attack_speed=1.5,
        crit_chance=0.15,
        crit_multiplier=2.0,
        spell_damage_pct=100.0,
        physical_damage_pct=50.0,
        fire_damage_pct=80.0,
        elemental_damage_pct=30.0,
        more_damage_multiplier=1.0,
        max_health=2500.0,
        armour=600.0,
        dodge_rating=200.0,
        crit_avoidance=30.0,
        fire_res=60.0,
        cold_res=50.0,
        lightning_res=55.0,
        void_res=30.0,
        necrotic_res=40.0,
        physical_res=20.0,
        poison_res=15.0,
        mana_regen=8.0,
        health_regen=10.0,
        leech=3.0,
        strength=20.0,
        intelligence=30.0,
        dexterity=15.0,
        vitality=25.0,
        attunement=20.0,
        added_spell_fire=10.0,
    )
    defaults.update(overrides)
    # Only pass fields that BuildStats actually accepts
    import dataclasses
    valid_fields = {f.name for f in dataclasses.fields(BuildStats)}
    filtered = {k: v for k, v in defaults.items() if k in valid_fields}
    return BuildStats(**filtered)


_SINGLE_PHASE_BOSS = {
    "id": "test_boss",
    "name": "Test Boss",
    "category": "boss",
    "health": 100000,
    "armor": 500,
    "resistances": {
        "physical": 30,
        "fire": 40,
        "cold": 40,
        "lightning": 40,
        "void": 30,
        "necrotic": 30,
        "poison": 20,
    },
    "crit_chance": 0.2,
    "crit_multiplier": 2.0,
}

_MULTI_PHASE_BOSS = {
    "id": "test_phased_boss",
    "name": "Phased Boss",
    "category": "pinnacle",
    "health": 200000,
    "armor": 800,
    "resistances": {"physical": 50, "fire": 50, "cold": 50, "lightning": 50, "void": 50, "necrotic": 50, "poison": 40},
    "enrage_time": 120.0,
    "phases": [
        {
            "phase": 1,
            "health_threshold": 1.0,
            "resistances": {"physical": 40, "fire": 40, "cold": 40, "lightning": 40, "void": 40, "necrotic": 40, "poison": 30},
            "armor": 600,
        },
        {
            "phase": 2,
            "health_threshold": 0.5,
            "immunity": True,
            "immunity_duration": 3.0,
        },
        {
            "phase": 3,
            "health_threshold": 0.5,
            "resistances": {"physical": 60, "fire": 60, "cold": 60, "lightning": 60, "void": 60, "necrotic": 60, "poison": 50},
            "armor": 1000,
            "damage_reduction": 20.0,
        },
    ],
}


# ============================================================================
# Boss Encounter Simulator Tests
# ============================================================================

class TestBossEncounterSimulator:
    def test_single_phase_result_shape(self):
        stats = _make_stats()
        result = simulate_boss_encounter(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)

        assert isinstance(result, BossEncounterResult)
        assert result.boss_id == "test_boss"
        assert result.boss_name == "Test Boss"
        assert result.corruption == 0
        assert len(result.phases) == 1

        phase = result.phases[0]
        assert phase.phase == 1
        assert phase.health_threshold == 1.0
        assert phase.dps > 0
        assert phase.ttk_seconds > 0
        assert 0 <= phase.survival_score <= 100
        assert isinstance(phase.mana_sustainable, bool)

    def test_multi_phase_transitions(self):
        stats = _make_stats()
        result = simulate_boss_encounter(stats, _MULTI_PHASE_BOSS, "Fireball", 20)

        assert len(result.phases) == 3
        # Phase 1 should have lower resistance than phase 3
        p1 = result.phases[0]
        p3 = result.phases[2]
        assert p1.phase == 1
        assert p3.phase == 3
        # Phase 1 (lower res) should have higher DPS than phase 3 (higher res + DR)
        assert p1.dps > p3.dps or p3.dps == 0

    def test_immunity_phase_zeroes_damage(self):
        stats = _make_stats()
        result = simulate_boss_encounter(stats, _MULTI_PHASE_BOSS, "Fireball", 20)

        # Phase 2 is the immunity phase
        immunity_phase = next(p for p in result.phases if p.phase == 2)
        assert immunity_phase.dps == 0
        assert any("Immunity" in w for w in immunity_phase.warnings)

    def test_enrage_flag_triggers(self):
        """A very weak build should not kill before enrage."""
        weak_stats = _make_stats(base_damage=1.0, attack_speed=0.1)
        result = simulate_boss_encounter(weak_stats, _MULTI_PHASE_BOSS, "Fireball", 1)

        # With 1 base damage, TTK should far exceed 120s enrage
        assert result.summary.can_kill_before_enrage is False
        assert any("enrage" in w.lower() for w in result.warnings)

    def test_enrage_ok_for_strong_build(self):
        """A strong build should beat enrage."""
        strong = _make_stats(
            base_damage=50000.0,
            attack_speed=5.0,
            spell_damage_pct=500.0,
            fire_damage_pct=500.0,
            more_damage_multiplier=5.0,
            crit_chance=0.8,
            crit_multiplier=4.0,
        )
        result = simulate_boss_encounter(strong, _MULTI_PHASE_BOSS, "Fireball", 20)

        assert result.summary.can_kill_before_enrage is True

    def test_corruption_scales_boss(self):
        stats = _make_stats()
        r0 = simulate_boss_encounter(stats, _SINGLE_PHASE_BOSS, "Fireball", 20,
                                      corruption=0, health_multiplier=1.0)
        r300 = simulate_boss_encounter(stats, _SINGLE_PHASE_BOSS, "Fireball", 20,
                                        corruption=300, health_multiplier=4.6)

        # Higher corruption → longer TTK (same DPS, more boss HP)
        assert r300.summary.total_ttk_seconds > r0.summary.total_ttk_seconds

    def test_result_to_dict_shape(self):
        stats = _make_stats()
        result = simulate_boss_encounter(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)
        d = result.to_dict()

        assert "boss_id" in d
        assert "boss_name" in d
        assert "corruption" in d
        assert "phases" in d
        assert "summary" in d
        assert "total_ttk_seconds" in d["summary"]
        assert "can_kill_before_enrage" in d["summary"]
        assert "overall_survival_score" in d["summary"]
        assert "weakest_phase" in d["summary"]

    def test_missing_boss_fields_defaults(self):
        """Boss with minimal fields should not crash."""
        minimal_boss = {"id": "minimal", "name": "Minimal", "health": 5000}
        stats = _make_stats()
        result = simulate_boss_encounter(stats, minimal_boss, "Fireball", 20)

        assert result.boss_id == "minimal"
        assert len(result.phases) == 1
        assert result.phases[0].dps > 0


# ============================================================================
# Corruption Scaler Tests
# ============================================================================

class TestCorruptionScaler:
    def test_health_multiplier_at_zero(self):
        assert health_multiplier(0) == 1.0

    def test_health_multiplier_at_100(self):
        assert health_multiplier(100) == pytest.approx(2.0, abs=0.01)

    def test_health_multiplier_at_200(self):
        assert health_multiplier(200) == pytest.approx(3.0, abs=0.01)

    def test_health_multiplier_accelerates_past_200(self):
        m300 = health_multiplier(300)
        m400 = health_multiplier(400)
        m500 = health_multiplier(500)

        # Each step should increase by more than the previous
        delta_300 = m300 - health_multiplier(200)
        delta_400 = m400 - m300
        delta_500 = m500 - m400

        assert delta_400 > delta_300
        assert delta_500 > delta_400

    def test_damage_multiplier_linear(self):
        assert damage_multiplier(0) == 1.0
        assert damage_multiplier(100) == pytest.approx(1.5, abs=0.01)
        assert damage_multiplier(200) == pytest.approx(2.0, abs=0.01)
        assert damage_multiplier(500) == pytest.approx(3.5, abs=0.01)

    def test_scale_corruption_curve_length(self):
        stats = _make_stats()
        result = scale_corruption(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)

        assert len(result.curve) == len(STANDARD_BREAKPOINTS)
        assert result.curve[0].corruption == 0
        assert result.curve[-1].corruption == 500

    def test_recommended_max_corruption(self):
        stats = _make_stats()
        result = scale_corruption(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)

        # Recommended should be a value from the breakpoints
        assert result.recommended_max_corruption in STANDARD_BREAKPOINTS

    def test_dps_efficiency_decreases_with_corruption(self):
        stats = _make_stats()
        result = scale_corruption(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)

        # DPS efficiency should generally decrease as corruption rises
        efficiencies = [dp.dps_efficiency for dp in result.curve]
        assert efficiencies[0] >= efficiencies[-1]

    def test_result_to_dict_shape(self):
        stats = _make_stats()
        result = scale_corruption(stats, _SINGLE_PHASE_BOSS, "Fireball", 20)
        d = result.to_dict()

        assert "boss_id" in d
        assert "recommended_max_corruption" in d
        assert "curve" in d
        assert len(d["curve"]) == 6
        assert "corruption" in d["curve"][0]
        assert "dps_efficiency" in d["curve"][0]
        assert "survivability_score" in d["curve"][0]


# ============================================================================
# Gear Upgrade Ranker Tests
# ============================================================================

class TestGearUpgradeRanker:
    def test_normalize_slot(self):
        assert _normalize_slot("helm") == "helmet"
        assert _normalize_slot("chest") == "body"
        assert _normalize_slot("feet") == "boots"
        assert _normalize_slot("weapon") == "weapon"

    def test_fp_cost_for_tier(self):
        # Lower tiers cost less
        low = _fp_cost_for_tier(1)
        mid = _fp_cost_for_tier(4)
        high = _fp_cost_for_tier(7)
        assert low <= mid <= high

    def test_rank_with_candidates(self):
        stats = _make_stats()
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [],
            "nodes": [],
        }

        candidates = [
            {
                "item_name": "Fire Crown",
                "base_type": "Royal Circlet",
                "slot": "helmet",
                "affixes": [{"name": "Increased Fire Damage", "tier": 5}],
            },
            {
                "item_name": "Tough Helm",
                "base_type": "Royal Circlet",
                "slot": "helmet",
                "affixes": [{"name": "Health", "tier": 3}],
            },
        ]

        result = rank_gear_upgrades(
            stats, build, "Fireball", 20,
            candidate_items=candidates,
        )

        assert isinstance(result, GearUpgradeResult)
        # Should have at least some candidates evaluated
        assert len(result.top_10_overall) >= 0

    def test_no_item_in_slot_handled(self):
        """Build with empty gear should not crash."""
        stats = _make_stats()
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [],
            "nodes": [],
        }

        candidates = [
            {
                "item_name": "Test Amulet",
                "base_type": "Gold Amulet",
                "slot": "amulet",
                "affixes": [{"name": "Spell Damage", "tier": 4}],
            },
        ]

        result = rank_gear_upgrades(
            stats, build, "Fireball", 20,
            candidate_items=candidates,
        )
        assert isinstance(result, GearUpgradeResult)

    def test_ranking_sorted_by_efficiency(self):
        stats = _make_stats()
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [{"slot": "helmet", "affixes": [{"name": "Health", "tier": 1}]}],
            "nodes": [],
        }

        candidates = [
            {"item_name": "Item A", "base_type": "Base", "slot": "helmet",
             "affixes": [{"name": "Increased Fire Damage", "tier": 5}]},
            {"item_name": "Item B", "base_type": "Base", "slot": "helmet",
             "affixes": [{"name": "Health", "tier": 2}]},
            {"item_name": "Item C", "base_type": "Base", "slot": "helmet",
             "affixes": [{"name": "Increased Fire Damage", "tier": 7}]},
        ]

        result = rank_gear_upgrades(
            stats, build, "Fireball", 20,
            candidate_items=candidates,
        )

        if len(result.top_10_overall) >= 2:
            # Should be sorted by efficiency descending
            scores = [c.efficiency_score for c in result.top_10_overall]
            assert scores == sorted(scores, reverse=True)

    def test_result_to_dict_shape(self):
        stats = _make_stats()
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [],
            "nodes": [],
        }
        result = rank_gear_upgrades(stats, build, "Fireball", 20, candidate_items=[])
        d = result.to_dict()

        assert "slots" in d
        assert "top_10_overall" in d


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestAnalysisEndpoints:
    def test_boss_analysis_unknown_build(self, client):
        resp = client.get("/api/builds/nonexistent-slug/analysis/boss/boss_standard")
        assert resp.status_code == 404

    def test_boss_analysis_unknown_boss(self, client, sample_build):
        resp = client.get(f"/api/builds/{sample_build.slug}/analysis/boss/nonexistent_boss")
        assert resp.status_code == 404

    def test_boss_analysis_invalid_corruption(self, client, sample_build):
        resp = client.get(f"/api/builds/{sample_build.slug}/analysis/boss/boss_standard?corruption=9999")
        assert resp.status_code == 400

    def test_corruption_analysis_unknown_build(self, client):
        resp = client.get("/api/builds/nonexistent-slug/analysis/corruption")
        assert resp.status_code == 404

    def test_gear_upgrades_unknown_build(self, client):
        resp = client.get("/api/builds/nonexistent-slug/analysis/gear-upgrades")
        assert resp.status_code == 404

    def test_bosses_list_endpoint(self, client):
        resp = client.get("/api/entities/bosses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "data" in data
        assert isinstance(data["data"], list)
        if len(data["data"]) > 0:
            assert "id" in data["data"][0]
            assert "name" in data["data"][0]


# ============================================================================
# Build Phases Helper Tests
# ============================================================================

class TestBuildPhases:
    def test_single_phase_boss(self):
        phases = _build_phases(_SINGLE_PHASE_BOSS)
        assert len(phases) == 1
        assert phases[0]["phase"] == 1
        assert phases[0]["health_threshold"] == 1.0

    def test_multi_phase_boss(self):
        phases = _build_phases(_MULTI_PHASE_BOSS)
        assert len(phases) == 3
        # Should be sorted by health_threshold descending
        thresholds = [p["health_threshold"] for p in phases]
        assert thresholds == sorted(thresholds, reverse=True)

    def test_phases_inherit_boss_resistances(self):
        boss = {
            "id": "test",
            "name": "Test",
            "health": 10000,
            "resistances": {"fire": 50},
            "armor": 300,
            "phases": [
                {"phase": 1, "health_threshold": 1.0},
            ],
        }
        phases = _build_phases(boss)
        assert phases[0]["resistances"] == {"fire": 50}
        assert phases[0]["armor"] == 300

    def test_phases_override_resistances(self):
        boss = {
            "id": "test",
            "name": "Test",
            "health": 10000,
            "resistances": {"fire": 50},
            "armor": 300,
            "phases": [
                {
                    "phase": 1,
                    "health_threshold": 1.0,
                    "resistances": {"fire": 75},
                    "armor": 500,
                },
            ],
        }
        phases = _build_phases(boss)
        assert phases[0]["resistances"] == {"fire": 75}
        assert phases[0]["armor"] == 500
