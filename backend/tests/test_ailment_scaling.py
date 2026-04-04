"""
Tests for Stat-Driven Ailment Scaling (Step 51).

Validates:
  - scale_ailment_damage returns base unchanged when no stats set
  - Each specific stat field scales the correct ailment type(s)
  - Generic stats (dot_damage_pct, ailment_damage_pct) apply to all types
  - Additive stacking: multiple stats sum before multiplying
  - Shock and Frostbite fall back to the generic stat pool
"""

import pytest
from app.domain.ailments import AilmentType
from app.domain.ailment_scaling import scale_ailment_damage
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stats(**kwargs) -> BuildStats:
    return BuildStats(**kwargs)


# ---------------------------------------------------------------------------
# Baseline — no stats set
# ---------------------------------------------------------------------------

class TestAilmentScalingBaseline:
    def test_bleed_no_stats_unchanged(self):
        s = _stats()
        assert scale_ailment_damage(100.0, AilmentType.BLEED, s) == pytest.approx(100.0)

    def test_ignite_no_stats_unchanged(self):
        s = _stats()
        assert scale_ailment_damage(100.0, AilmentType.IGNITE, s) == pytest.approx(100.0)

    def test_poison_no_stats_unchanged(self):
        s = _stats()
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(100.0)

    def test_shock_no_stats_unchanged(self):
        s = _stats()
        assert scale_ailment_damage(50.0, AilmentType.SHOCK, s) == pytest.approx(50.0)

    def test_frostbite_no_stats_unchanged(self):
        s = _stats()
        assert scale_ailment_damage(50.0, AilmentType.FROSTBITE, s) == pytest.approx(50.0)

    def test_zero_base_stays_zero(self):
        s = _stats(bleed_damage_pct=100.0)
        assert scale_ailment_damage(0.0, AilmentType.BLEED, s) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Specific ailment stats
# ---------------------------------------------------------------------------

class TestSpecificAilmentStats:
    def test_bleed_damage_pct_scales_bleed(self):
        # +100% bleed → ×2
        s = _stats(bleed_damage_pct=100.0)
        assert scale_ailment_damage(50.0, AilmentType.BLEED, s) == pytest.approx(100.0)

    def test_bleed_damage_pct_does_not_scale_ignite(self):
        s = _stats(bleed_damage_pct=100.0)
        assert scale_ailment_damage(50.0, AilmentType.IGNITE, s) == pytest.approx(50.0)

    def test_bleed_damage_pct_does_not_scale_poison(self):
        s = _stats(bleed_damage_pct=100.0)
        assert scale_ailment_damage(50.0, AilmentType.POISON, s) == pytest.approx(50.0)

    def test_ignite_damage_pct_scales_ignite(self):
        s = _stats(ignite_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.IGNITE, s) == pytest.approx(150.0)

    def test_ignite_damage_pct_does_not_scale_bleed(self):
        s = _stats(ignite_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.BLEED, s) == pytest.approx(100.0)

    def test_poison_dot_damage_pct_scales_poison(self):
        s = _stats(poison_dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(150.0)

    def test_physical_damage_pct_scales_bleed(self):
        # Bleed is physical DoT — physical_damage_pct applies
        s = _stats(physical_damage_pct=25.0)
        assert scale_ailment_damage(80.0, AilmentType.BLEED, s) == pytest.approx(100.0)

    def test_fire_damage_pct_scales_ignite(self):
        # Ignite is fire DoT — fire_damage_pct applies
        s = _stats(fire_damage_pct=25.0)
        assert scale_ailment_damage(80.0, AilmentType.IGNITE, s) == pytest.approx(100.0)

    def test_fire_damage_pct_does_not_scale_bleed(self):
        s = _stats(fire_damage_pct=100.0)
        assert scale_ailment_damage(50.0, AilmentType.BLEED, s) == pytest.approx(50.0)

    def test_poison_damage_pct_scales_poison(self):
        s = _stats(poison_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(150.0)


# ---------------------------------------------------------------------------
# Generic stats — apply to all ailment types
# ---------------------------------------------------------------------------

class TestGenericAilmentStats:
    def test_dot_damage_pct_scales_bleed(self):
        s = _stats(dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.BLEED, s) == pytest.approx(150.0)

    def test_dot_damage_pct_scales_ignite(self):
        s = _stats(dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.IGNITE, s) == pytest.approx(150.0)

    def test_dot_damage_pct_scales_poison(self):
        s = _stats(dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(150.0)

    def test_dot_damage_pct_scales_shock(self):
        s = _stats(dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.SHOCK, s) == pytest.approx(150.0)

    def test_dot_damage_pct_scales_frostbite(self):
        s = _stats(dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.FROSTBITE, s) == pytest.approx(150.0)

    def test_ailment_damage_pct_scales_bleed(self):
        s = _stats(ailment_damage_pct=25.0)
        assert scale_ailment_damage(100.0, AilmentType.BLEED, s) == pytest.approx(125.0)

    def test_ailment_damage_pct_scales_ignite(self):
        s = _stats(ailment_damage_pct=25.0)
        assert scale_ailment_damage(100.0, AilmentType.IGNITE, s) == pytest.approx(125.0)

    def test_ailment_damage_pct_scales_poison(self):
        s = _stats(ailment_damage_pct=25.0)
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(125.0)

    def test_ailment_damage_pct_scales_shock(self):
        s = _stats(ailment_damage_pct=25.0)
        assert scale_ailment_damage(100.0, AilmentType.SHOCK, s) == pytest.approx(125.0)

    def test_ailment_damage_pct_scales_frostbite(self):
        s = _stats(ailment_damage_pct=25.0)
        assert scale_ailment_damage(100.0, AilmentType.FROSTBITE, s) == pytest.approx(125.0)


# ---------------------------------------------------------------------------
# Additive stacking — multiple stats sum before multiplying
# ---------------------------------------------------------------------------

class TestAdditiveStacking:
    def test_bleed_multiple_sources_additive(self):
        # physical_damage_pct=20, dot_damage_pct=30, bleed_damage_pct=50
        # total = 100% → ×2
        s = _stats(physical_damage_pct=20.0, dot_damage_pct=30.0, bleed_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.BLEED, s) == pytest.approx(200.0)

    def test_ignite_multiple_sources_additive(self):
        # fire_damage_pct=25, ailment_damage_pct=25, ignite_damage_pct=50 → total=100%
        s = _stats(fire_damage_pct=25.0, ailment_damage_pct=25.0, ignite_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.IGNITE, s) == pytest.approx(200.0)

    def test_poison_multiple_sources_additive(self):
        # poison_damage_pct=50, dot_damage_pct=50 → total=100%
        s = _stats(poison_damage_pct=50.0, dot_damage_pct=50.0)
        assert scale_ailment_damage(100.0, AilmentType.POISON, s) == pytest.approx(200.0)

    def test_stacking_is_not_multiplicative(self):
        # If it were multiplicative: 100 × 1.5 × 1.5 = 225
        # If additive: 100 × (1 + 1.0) = 200
        s = _stats(dot_damage_pct=50.0, ailment_damage_pct=50.0)
        result = scale_ailment_damage(100.0, AilmentType.BLEED, s)
        assert result == pytest.approx(200.0)   # additive, not 225

    def test_all_bleed_stats_combined(self):
        # physical=10, dot=20, ailment=30, bleed=40 → total=100%
        s = _stats(
            physical_damage_pct=10.0, dot_damage_pct=20.0,
            ailment_damage_pct=30.0,  bleed_damage_pct=40.0,
        )
        assert scale_ailment_damage(50.0, AilmentType.BLEED, s) == pytest.approx(100.0)
