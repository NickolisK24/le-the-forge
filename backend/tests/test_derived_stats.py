"""
Tests for the derived stat registry and pipeline integration.

Verifies:
  - Individual derived stat functions produce correct values
  - Registry executes in dependency order
  - Debug snapshots capture inputs/outputs
  - Pipeline Layer 7 runs and affects final BuildStats
  - Vitality → health_regen, armour → mitigation, intelligence → mana_regen
"""

import pytest

from app.engines.stat_engine import BuildStats
from app.stats.derived_stats import (
    DERIVED_STAT_REGISTRY,
    DerivedStatEntry,
    DerivedStatSnapshot,
    apply_derived_stat_registry,
    compute_armor_mitigation,
    compute_dodge_chance,
    compute_effective_health,
    compute_health,
    compute_mana_regen,
    _REFERENCE_HIT,
    _validate_no_circular_deps,
)
from app.domain.armor import ARMOR_K, ARMOR_MITIGATION_CAP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stats(**overrides: float) -> BuildStats:
    """Create a BuildStats with specific field overrides."""
    s = BuildStats()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# Individual derived stat functions
# ---------------------------------------------------------------------------

class TestComputeHealth:
    def test_vitality_increases_health_regen(self):
        stats = _stats(vitality=20.0, health_regen=0.0)
        compute_health(stats)
        assert stats.health_regen == 10.0  # 20 * 0.5

    def test_zero_vitality_no_change(self):
        stats = _stats(vitality=0.0, health_regen=5.0)
        compute_health(stats)
        assert stats.health_regen == 5.0  # unchanged

    def test_additive_on_existing_regen(self):
        stats = _stats(vitality=10.0, health_regen=3.0)
        compute_health(stats)
        assert stats.health_regen == 8.0  # 3 + 10*0.5


class TestComputeArmorMitigation:
    def test_zero_armour_no_mitigation(self):
        stats = _stats(armour=0.0)
        compute_armor_mitigation(stats)
        assert not hasattr(stats, "_armor_mitigation_pct")

    def test_positive_armour_produces_mitigation(self):
        stats = _stats(armour=500.0)
        compute_armor_mitigation(stats)
        # 500 / (500 + 10*100) = 500/1500 = 0.333... → 33.33%
        expected = (500.0 / (500.0 + ARMOR_K * _REFERENCE_HIT)) * 100.0
        assert abs(stats._armor_mitigation_pct - expected) < 0.01

    def test_high_armour_capped(self):
        stats = _stats(armour=100000.0)
        compute_armor_mitigation(stats)
        assert stats._armor_mitigation_pct <= ARMOR_MITIGATION_CAP * 100.0

    def test_formula_matches_armor_module(self):
        from app.domain.armor import armor_mitigation_pct
        armour = 1200.0
        stats = _stats(armour=armour)
        compute_armor_mitigation(stats)
        expected = armor_mitigation_pct(armour, _REFERENCE_HIT) * 100.0
        assert abs(stats._armor_mitigation_pct - expected) < 0.001


class TestComputeManaRegen:
    def test_intelligence_increases_mana_regen(self):
        stats = _stats(intelligence=30.0, mana_regen=0.0)
        compute_mana_regen(stats)
        assert stats.mana_regen == 3.0  # 30 * 0.1

    def test_additive_on_existing(self):
        stats = _stats(intelligence=20.0, mana_regen=2.0)
        compute_mana_regen(stats)
        assert stats.mana_regen == 4.0  # 2 + 20*0.1


class TestComputeEffectiveHealth:
    def test_no_armour_ehp_equals_health(self):
        stats = _stats(max_health=1000.0, armour=0.0)
        compute_effective_health(stats)
        assert stats._effective_health == 1000.0

    def test_armour_increases_ehp(self):
        stats = _stats(max_health=1000.0, armour=500.0)
        compute_effective_health(stats)
        assert stats._effective_health > 1000.0

    def test_high_armour_significant_ehp(self):
        stats = _stats(max_health=1000.0, armour=2000.0)
        compute_effective_health(stats)
        # 2000 / (2000 + 1000) = 0.667 → ehp = 1000 / 0.333 ≈ 3000
        assert stats._effective_health > 2500.0


class TestComputeDodgeChance:
    def test_zero_rating_no_dodge(self):
        stats = _stats(dodge_rating=0.0)
        compute_dodge_chance(stats)
        assert not hasattr(stats, "_dodge_chance_pct")

    def test_positive_rating_produces_chance(self):
        stats = _stats(dodge_rating=500.0)
        compute_dodge_chance(stats)
        # 500 / (500 + 1000) = 33.33%
        expected = (500.0 / 1500.0) * 100.0
        assert abs(stats._dodge_chance_pct - expected) < 0.01

    def test_diminishing_returns(self):
        stats_low = _stats(dodge_rating=200.0)
        stats_high = _stats(dodge_rating=2000.0)
        compute_dodge_chance(stats_low)
        compute_dodge_chance(stats_high)
        # High rating should have less than 10x the low rating's chance
        ratio = stats_high._dodge_chance_pct / stats_low._dodge_chance_pct
        assert ratio < 5.0


# ---------------------------------------------------------------------------
# Registry structure and ordering
# ---------------------------------------------------------------------------

class TestDerivedStatRegistry:
    def test_registry_not_empty(self):
        assert len(DERIVED_STAT_REGISTRY) >= 5

    def test_registry_sorted_by_order(self):
        orders = [e.order for e in DERIVED_STAT_REGISTRY]
        assert orders == sorted(orders)

    def test_no_circular_deps(self):
        warnings = _validate_no_circular_deps(DERIVED_STAT_REGISTRY)
        assert warnings == []

    def test_all_entries_have_names(self):
        for entry in DERIVED_STAT_REGISTRY:
            assert entry.name
            assert entry.compute is not None
            assert len(entry.reads) > 0
            assert len(entry.writes) > 0


# ---------------------------------------------------------------------------
# Registry execution
# ---------------------------------------------------------------------------

class TestApplyDerivedStatRegistry:
    def test_all_functions_execute(self):
        stats = _stats(vitality=10.0, intelligence=20.0, armour=500.0, dodge_rating=300.0, max_health=500.0)
        apply_derived_stat_registry(stats)
        # health_regen should have vitality contribution
        assert stats.health_regen >= 5.0  # 10 * 0.5
        # mana_regen should have intelligence contribution
        assert stats.mana_regen >= 2.0  # 20 * 0.1
        # armor mitigation should exist
        assert hasattr(stats, "_armor_mitigation_pct")
        assert stats._armor_mitigation_pct > 0
        # effective health should exist
        assert hasattr(stats, "_effective_health")
        assert stats._effective_health > 500.0
        # dodge chance should exist
        assert hasattr(stats, "_dodge_chance_pct")

    def test_capture_returns_snapshots(self):
        stats = _stats(vitality=10.0, intelligence=15.0, armour=200.0, dodge_rating=100.0, max_health=300.0)
        snapshots = apply_derived_stat_registry(stats, capture=True)
        assert len(snapshots) == len(DERIVED_STAT_REGISTRY)
        for snap in snapshots:
            assert isinstance(snap, DerivedStatSnapshot)
            assert snap.name
            assert isinstance(snap.inputs, dict)
            assert isinstance(snap.outputs, dict)

    def test_snapshot_records_correct_inputs(self):
        stats = _stats(vitality=25.0, health_regen=0.0)
        snapshots = apply_derived_stat_registry(stats, capture=True)
        health_snap = next(s for s in snapshots if s.name == "health_regen_from_vitality")
        assert health_snap.inputs["vitality"] == 25.0

    def test_no_capture_returns_empty(self):
        stats = _stats()
        snapshots = apply_derived_stat_registry(stats, capture=False)
        assert snapshots == []


# ---------------------------------------------------------------------------
# Pipeline integration (Layer 7)
# ---------------------------------------------------------------------------

class TestPipelineLayer7Integration:
    def test_vitality_affects_health_regen_in_pipeline(self):
        """High-vitality build should have more max_health than low-vitality."""
        # updated: verified in-game data — all classes now share near-equal
        # base Vitality (0 or 1). Vitality also no longer directly scales
        # health_regen; it grants +6 HP, +1 ET, +1% poison/necrotic
        # resistance. Use explicit Vitality affix to drive VIT differences
        # and assert on max_health (the actual verified scaling target).
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result_high_vit = resolve_final_stats({
            "character_class": "Sentinel",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [{"stat_key": "vitality", "value": 20}],
        })
        result_low_vit = resolve_final_stats({
            "character_class": "Sentinel",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [],
        })
        assert result_high_vit.stats.max_health > result_low_vit.stats.max_health

    def test_armour_affects_armor_mitigation_in_pipeline(self):
        """Sentinel with armor affix should have armor mitigation."""
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats({
            "character_class": "Sentinel",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [{"stat_key": "armour", "value": 500}],
        })
        assert hasattr(result.stats, "_armor_mitigation_pct")
        assert result.stats._armor_mitigation_pct > 0

    def test_intelligence_affects_mana_regen_in_pipeline(self):
        """Mage (high int) should have more mana_regen than Primalist (low int)."""
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result_mage = resolve_final_stats({
            "character_class": "Mage",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [],
        })
        result_prim = resolve_final_stats({
            "character_class": "Primalist",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [],
        })
        assert result_mage.stats.mana_regen > result_prim.stats.mana_regen

    def test_layer7_snapshot_captured(self):
        """With capture_snapshots=True, Layer 7 snapshot should exist."""
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats(
            {"character_class": "Sentinel", "mastery": "", "passive_tree": [], "gear_affixes": []},
            capture_snapshots=True,
        )
        assert "7_registry_derived" in result.layer_snapshots
        layer7 = result.layer_snapshots["7_registry_derived"]
        assert "_derived_entries" in layer7
        entries = layer7["_derived_entries"]
        assert len(entries) >= 5
        assert all("name" in e for e in entries)

    def test_resolution_order_includes_layer7(self):
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats({
            "character_class": "Sentinel", "mastery": "",
            "passive_tree": [], "gear_affixes": [],
        })
        assert "7_registry_derived" in result.resolution_order
