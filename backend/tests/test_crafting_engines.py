"""
Tests for Phase P crafting engines:
  - ForgingPotentialEngine  (forging_potential_engine.py)
  - InstabilityEngine       (instability_engine.py)
  - FractureEngine          (fracture_engine.py)
  - GlyphEngine             (glyph_engine.py)
  - RuneEngine              (rune_engine.py)
"""
from __future__ import annotations

import random
import pytest

from crafting.models.craft_state import AffixState, CraftState
from crafting.engines.forging_potential_engine import ForgingPotentialEngine, FPCostResult
from crafting.engines.instability_engine import InstabilityEngine
from crafting.engines.fracture_engine import FractureEngine, FractureResult
from crafting.engines.glyph_engine import GlyphEngine, GlyphType
from crafting.engines.rune_engine import RuneEngine, RuneType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state(
    fp: int = 50,
    instability: int = 0,
    affixes=None,
    is_fractured: bool = False,
    metadata: dict | None = None,
) -> CraftState:
    return CraftState(
        item_id="item-001",
        item_name="Iron Helm",
        item_class="helm",
        forging_potential=fp,
        instability=instability,
        affixes=affixes if affixes is not None else [],
        is_fractured=is_fractured,
        metadata=metadata if metadata is not None else {},
    )


def make_affix(affix_id: str, current_tier: int = 1, max_tier: int = 7,
               locked: bool = False) -> AffixState:
    return AffixState(affix_id=affix_id, current_tier=current_tier,
                      max_tier=max_tier, locked=locked)


# ---------------------------------------------------------------------------
# ForgingPotentialEngine
# ---------------------------------------------------------------------------

class TestForgingPotentialEngine:
    def test_roll_cost_add_affix_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["add_affix"]
        for _ in range(50):
            c = eng.roll_cost("add_affix")
            assert lo <= c <= hi

    def test_roll_cost_upgrade_affix_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["upgrade_affix"]
        for _ in range(50):
            c = eng.roll_cost("upgrade_affix")
            assert lo <= c <= hi

    def test_roll_cost_remove_affix_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["remove_affix"]
        for _ in range(50):
            c = eng.roll_cost("remove_affix")
            assert lo <= c <= hi

    def test_roll_cost_reroll_affix_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["reroll_affix"]
        for _ in range(50):
            c = eng.roll_cost("reroll_affix")
            assert lo <= c <= hi

    def test_roll_cost_glyph_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["glyph"]
        for _ in range(50):
            c = eng.roll_cost("glyph")
            assert lo <= c <= hi

    def test_roll_cost_rune_in_range(self):
        eng = ForgingPotentialEngine()
        lo, hi = ForgingPotentialEngine.FP_COSTS["rune"]
        for _ in range(50):
            c = eng.roll_cost("rune")
            assert lo <= c <= hi

    def test_roll_cost_unknown_action_uses_default(self):
        eng = ForgingPotentialEngine()
        for _ in range(30):
            c = eng.roll_cost("unknown_action_xyz")
            assert 2 <= c <= 5

    def test_apply_cost_reduces_fp(self):
        eng = ForgingPotentialEngine(rng=random.Random(0))
        state = make_state(fp=50)
        result = eng.apply_cost(state, "upgrade_affix")
        assert state.forging_potential < 50
        assert result.remaining == state.forging_potential

    def test_apply_cost_result_remaining_correct(self):
        eng = ForgingPotentialEngine(rng=random.Random(42))
        state = make_state(fp=20)
        before = state.forging_potential
        result = eng.apply_cost(state, "glyph")
        assert result.remaining == state.forging_potential
        assert result.actual_cost == before - state.forging_potential

    def test_apply_cost_fp_cannot_go_below_zero(self):
        eng = ForgingPotentialEngine(rng=random.Random(0))
        state = make_state(fp=1)
        # rune costs 2-5, so fp=1 must clamp to 0
        result = eng.apply_cost(state, "rune")
        assert state.forging_potential == 0
        assert result.remaining == 0

    def test_apply_cost_exhausted_flag_when_zero(self):
        eng = ForgingPotentialEngine(rng=random.Random(0))
        state = make_state(fp=1)
        result = eng.apply_cost(state, "rune")
        # fp hits 0, so exhausted=True
        assert result.exhausted is True

    def test_apply_cost_not_exhausted_when_fp_remains(self):
        eng = ForgingPotentialEngine(rng=random.Random(0))
        state = make_state(fp=100)
        result = eng.apply_cost(state, "upgrade_affix")
        assert result.exhausted is False

    def test_detect_exhaustion_true_when_zero(self):
        eng = ForgingPotentialEngine()
        state = make_state(fp=0)
        assert eng.detect_exhaustion(state) is True

    def test_detect_exhaustion_false_when_positive(self):
        eng = ForgingPotentialEngine()
        state = make_state(fp=10)
        assert eng.detect_exhaustion(state) is False

    def test_estimate_remaining_crafts_positive(self):
        eng = ForgingPotentialEngine()
        state = make_state(fp=30)
        est = eng.estimate_remaining_crafts(state, "upgrade_affix")
        assert est > 0

    def test_estimate_remaining_crafts_decreases_as_fp_decreases(self):
        eng = ForgingPotentialEngine()
        state_high = make_state(fp=60)
        state_low = make_state(fp=20)
        assert eng.estimate_remaining_crafts(state_high) > eng.estimate_remaining_crafts(state_low)

    def test_estimate_remaining_crafts_zero_fp(self):
        eng = ForgingPotentialEngine()
        state = make_state(fp=0)
        assert eng.estimate_remaining_crafts(state) == 0.0

    def test_deterministic_with_seeded_rng(self):
        rng_a = random.Random(123)
        rng_b = random.Random(123)
        eng_a = ForgingPotentialEngine(rng=rng_a)
        eng_b = ForgingPotentialEngine(rng=rng_b)
        costs_a = [eng_a.roll_cost("add_affix") for _ in range(10)]
        costs_b = [eng_b.roll_cost("add_affix") for _ in range(10)]
        assert costs_a == costs_b


# ---------------------------------------------------------------------------
# InstabilityEngine
# ---------------------------------------------------------------------------

class TestInstabilityEngine:
    THRESHOLD = InstabilityEngine.FRACTURE_THRESHOLD
    BASE = InstabilityEngine.BASE_INCREASE

    def test_compute_increase_modifier_two_returns_double_base(self):
        eng = InstabilityEngine()
        result = eng.compute_increase(modifier=2.0)
        assert result == round(self.BASE * 2.0)

    def test_compute_increase_default_modifier(self):
        eng = InstabilityEngine()
        result = eng.compute_increase()
        assert result == self.BASE

    def test_compute_increase_custom_base(self):
        eng = InstabilityEngine()
        result = eng.compute_increase(base=20, modifier=1.5)
        assert result == max(1, round(20 * 1.5))

    def test_compute_increase_minimum_one(self):
        eng = InstabilityEngine()
        # modifier=0 → round(BASE*0)=0 → clamped to 1
        result = eng.compute_increase(modifier=0.0)
        assert result >= 1

    def test_apply_increases_instability(self):
        eng = InstabilityEngine()
        state = make_state(instability=0)
        result = eng.apply(state)
        assert state.instability > 0
        assert result.added > 0

    def test_apply_instability_clamped_to_threshold(self):
        eng = InstabilityEngine()
        state = make_state(instability=self.THRESHOLD - 1)
        eng.apply(state)
        assert state.instability <= self.THRESHOLD

    def test_apply_instability_already_at_threshold(self):
        eng = InstabilityEngine()
        state = make_state(instability=self.THRESHOLD)
        eng.apply(state)
        assert state.instability == self.THRESHOLD

    def test_apply_result_total_matches_state(self):
        eng = InstabilityEngine()
        state = make_state(instability=20)
        result = eng.apply(state)
        assert result.total == state.instability

    def test_fracture_chance_zero_at_zero_instability(self):
        eng = InstabilityEngine()
        assert eng.fracture_chance(0) == 0.0

    def test_fracture_chance_one_at_threshold(self):
        eng = InstabilityEngine()
        assert eng.fracture_chance(self.THRESHOLD) == 1.0

    def test_fracture_chance_linear_midpoint(self):
        eng = InstabilityEngine()
        mid = self.THRESHOLD // 2
        assert pytest.approx(eng.fracture_chance(mid), rel=1e-6) == 0.5

    def test_fracture_chance_linear_quarter(self):
        eng = InstabilityEngine()
        quarter = self.THRESHOLD // 4
        assert pytest.approx(eng.fracture_chance(quarter), rel=1e-6) == 0.25

    def test_fracture_chance_clamped_above_threshold(self):
        eng = InstabilityEngine()
        assert eng.fracture_chance(self.THRESHOLD + 50) == 1.0

    def test_reset_sets_instability_zero(self):
        eng = InstabilityEngine()
        state = make_state(instability=80)
        eng.reset(state)
        assert state.instability == 0

    def test_apply_with_modifier_uses_modified_increase(self):
        eng = InstabilityEngine()
        state_a = make_state(instability=0)
        state_b = make_state(instability=0)
        eng.apply(state_a, modifier=1.0)
        eng.apply(state_b, modifier=2.0)
        assert state_b.instability >= state_a.instability


# ---------------------------------------------------------------------------
# FractureEngine
# ---------------------------------------------------------------------------

class TestFractureEngine:
    def test_roll_fracture_chance_one_always_true(self):
        eng = FractureEngine(rng=random.Random(0))
        for _ in range(20):
            assert eng.roll_fracture(1.0) is True

    def test_roll_fracture_chance_zero_always_false(self):
        eng = FractureEngine(rng=random.Random(0))
        for _ in range(20):
            assert eng.roll_fracture(0.0) is False

    def test_roll_fracture_probabilistic(self):
        eng = FractureEngine(rng=random.Random(7))
        results = [eng.roll_fracture(0.5) for _ in range(200)]
        # With 200 trials at 50%, expect some True and some False
        assert any(results)
        assert not all(results)

    def test_apply_chance_zero_no_fracture(self):
        eng = FractureEngine(rng=random.Random(0))
        state = make_state(fp=50, affixes=[make_affix("flat_life")])
        result = eng.apply(state, 0.0)
        assert result.fractured is False
        assert state.is_fractured is False
        assert state.affixes  # unchanged

    def test_apply_chance_one_fractured_true(self):
        eng = FractureEngine(rng=random.Random(0))
        state = make_state(fp=50)
        result = eng.apply(state, 1.0)
        assert result.fractured is True
        assert state.is_fractured is True

    def test_apply_destructive_clears_affixes(self):
        # Force destructive outcome by using a seeded rng that picks "destructive"
        # We loop until we get one to ensure we test the path
        found = False
        for seed in range(500):
            rng = random.Random(seed)
            eng = FractureEngine(rng=rng)
            state = make_state(fp=50, affixes=[make_affix("flat_life"), make_affix("fire_res")])
            result = eng.apply(state, 1.0)
            if result.fracture_type == "destructive":
                assert state.affixes == []
                assert state.forging_potential == 0
                assert result.item_destroyed is True
                found = True
                break
        assert found, "Could not trigger destructive fracture in 500 seeds"

    def test_apply_damaging_removes_one_unlocked_affix(self):
        found = False
        for seed in range(500):
            rng = random.Random(seed)
            eng = FractureEngine(rng=rng)
            state = make_state(fp=50, affixes=[make_affix("flat_life"), make_affix("fire_res")])
            original_count = len(state.affixes)
            result = eng.apply(state, 1.0)
            if result.fracture_type == "damaging":
                assert len(state.affixes) == original_count - 1
                assert result.affix_lost is not None
                found = True
                break
        assert found, "Could not trigger damaging fracture in 500 seeds"

    def test_apply_minor_affixes_unchanged(self):
        found = False
        for seed in range(500):
            rng = random.Random(seed)
            eng = FractureEngine(rng=rng)
            state = make_state(fp=50, affixes=[make_affix("flat_life"), make_affix("fire_res")])
            result = eng.apply(state, 1.0)
            if result.fracture_type == "minor":
                assert len(state.affixes) == 2
                assert state.is_fractured is True
                assert result.item_destroyed is False
                found = True
                break
        assert found, "Could not trigger minor fracture in 500 seeds"

    def test_apply_chance_zero_result_fractured_false(self):
        eng = FractureEngine(rng=random.Random(0))
        state = make_state()
        result = eng.apply(state, 0.0)
        assert result.fractured is False
        assert result.fracture_type is None
        assert result.item_destroyed is False

    def test_seeded_rng_deterministic_fracture_type(self):
        types_a = []
        types_b = []
        for _ in range(10):
            eng_a = FractureEngine(rng=random.Random(99))
            eng_b = FractureEngine(rng=random.Random(99))
            types_a.append(eng_a.determine_type())
            types_b.append(eng_b.determine_type())
        assert types_a == types_b

    def test_damaging_fracture_does_not_remove_locked_affix_when_all_locked(self):
        # When all affixes locked, damaging fracture removes nothing
        found = False
        for seed in range(500):
            rng = random.Random(seed)
            eng = FractureEngine(rng=rng)
            state = make_state(fp=50, affixes=[make_affix("flat_life", locked=True)])
            result = eng.apply(state, 1.0)
            if result.fracture_type == "damaging":
                # No unlocked affixes → none removed
                assert len(state.affixes) == 1
                assert result.affix_lost is None
                found = True
                break
        assert found, "Could not trigger damaging fracture in 500 seeds"


# ---------------------------------------------------------------------------
# GlyphEngine
# ---------------------------------------------------------------------------

class TestGlyphEngine:
    def test_apply_stability_sets_metadata(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply_stability(state)
        assert state.metadata["instability_modifier"] == 0.5
        assert result.instability_modifier == pytest.approx(0.5)

    def test_apply_stability_result_applied_true(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply_stability(state)
        assert result.applied is True

    def test_apply_stability_glyph_type_string(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply_stability(state)
        assert result.glyph_type == "stability"

    def test_apply_hope_sets_metadata(self):
        eng = GlyphEngine(rng=random.Random(0))
        state = make_state()
        eng.apply_hope(state)
        assert "fp_preserved" in state.metadata

    def test_apply_hope_fp_saved_in_result(self):
        # With seed=0, random() < 0.5 determines fp_saved
        rng = random.Random(0)
        val = rng.random()  # peek at value
        eng = GlyphEngine(rng=random.Random(0))
        state = make_state()
        result = eng.apply_hope(state)
        expected = val < 0.5
        assert result.fp_saved == expected

    def test_apply_hope_metadata_matches_result(self):
        eng = GlyphEngine(rng=random.Random(42))
        state = make_state()
        result = eng.apply_hope(state)
        assert state.metadata["fp_preserved"] == result.fp_saved

    def test_apply_chaos_randomizes_tier(self):
        eng = GlyphEngine(rng=random.Random(0))
        affix = make_affix("flat_life", current_tier=5)
        state = make_state(affixes=[affix])
        result = eng.apply_chaos(state)
        assert result.applied is True
        assert result.affix_changed == "flat_life"
        # Tier should be in [1, max_tier]
        assert 1 <= state.affixes[0].current_tier <= 7

    def test_apply_chaos_no_affixes_returns_not_applied(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply_chaos(state)
        assert result.applied is False
        assert result.affix_changed is None

    def test_apply_dispatches_stability(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply("stability", state)
        assert result.glyph_type == "stability"
        assert state.metadata.get("instability_modifier") == 0.5

    def test_apply_dispatches_hope(self):
        eng = GlyphEngine(rng=random.Random(1))
        state = make_state()
        result = eng.apply("hope", state)
        assert result.glyph_type == "hope"
        assert "fp_preserved" in state.metadata

    def test_apply_dispatches_chaos(self):
        eng = GlyphEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply("chaos", state)
        assert result.glyph_type == "chaos"

    def test_apply_dispatches_via_enum(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply(GlyphType.STABILITY, state)
        assert result.glyph_type == "stability"

    def test_apply_dispatches_hope_via_enum(self):
        eng = GlyphEngine(rng=random.Random(1))
        state = make_state()
        result = eng.apply(GlyphType.HOPE, state)
        assert result.glyph_type == "hope"

    def test_apply_dispatches_chaos_via_enum(self):
        eng = GlyphEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("fire_res")])
        result = eng.apply(GlyphType.CHAOS, state)
        assert result.glyph_type == "chaos"

    def test_apply_unknown_glyph_not_applied(self):
        eng = GlyphEngine()
        state = make_state()
        result = eng.apply("totally_unknown_glyph", state)
        assert result.applied is False


# ---------------------------------------------------------------------------
# RuneEngine
# ---------------------------------------------------------------------------

class TestRuneEngine:
    def test_apply_removal_removes_one_unlocked_affix(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life"), make_affix("fire_res")])
        result = eng.apply_removal(state)
        assert result.applied is True
        assert len(state.affixes) == 1
        assert result.affected_affix is not None

    def test_apply_removal_no_unlocked_affixes_not_applied(self):
        eng = RuneEngine()
        state = make_state(affixes=[make_affix("flat_life", locked=True)])
        result = eng.apply_removal(state)
        assert result.applied is False

    def test_apply_removal_empty_affixes_not_applied(self):
        eng = RuneEngine()
        state = make_state()
        result = eng.apply_removal(state)
        assert result.applied is False

    def test_apply_removal_does_not_remove_locked_affix(self):
        eng = RuneEngine(rng=random.Random(0))
        locked = make_affix("locked_affix", locked=True)
        unlocked = make_affix("unlocked_affix", locked=False)
        state = make_state(affixes=[locked, unlocked])
        result = eng.apply_removal(state)
        assert result.applied is True
        assert result.affected_affix == "unlocked_affix"
        # locked affix still present
        assert any(a.affix_id == "locked_affix" for a in state.affixes)

    def test_apply_refinement_upgrades_one_affix_tier(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life", current_tier=3)])
        result = eng.apply_refinement(state)
        assert result.applied is True
        assert state.affixes[0].current_tier == 4

    def test_apply_refinement_all_maxed_not_applied(self):
        eng = RuneEngine()
        state = make_state(affixes=[make_affix("flat_life", current_tier=7, max_tier=7)])
        result = eng.apply_refinement(state)
        assert result.applied is False

    def test_apply_refinement_empty_affixes_not_applied(self):
        eng = RuneEngine()
        state = make_state()
        result = eng.apply_refinement(state)
        assert result.applied is False

    def test_apply_shaping_locks_one_affix(self):
        eng = RuneEngine(rng=random.Random(0))
        affix = make_affix("flat_life", locked=False)
        state = make_state(affixes=[affix])
        result = eng.apply_shaping(state)
        assert result.applied is True
        assert state.affixes[0].locked is True
        assert result.affected_affix == "flat_life"

    def test_apply_shaping_all_locked_not_applied(self):
        eng = RuneEngine()
        state = make_state(affixes=[make_affix("flat_life", locked=True)])
        result = eng.apply_shaping(state)
        assert result.applied is False

    def test_apply_shaping_empty_affixes_not_applied(self):
        eng = RuneEngine()
        state = make_state()
        result = eng.apply_shaping(state)
        assert result.applied is False

    def test_apply_discovery_adds_new_affix(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply_discovery(state, ["fire_res", "cold_res", "flat_mana"])
        assert result.applied is True
        assert len(state.affixes) == 2
        assert result.affected_affix in ("fire_res", "cold_res", "flat_mana")

    def test_apply_discovery_full_item_not_applied(self):
        eng = RuneEngine()
        affixes = [make_affix(f"affix_{i}") for i in range(4)]
        state = make_state(affixes=affixes)
        result = eng.apply_discovery(state, ["new_affix"])
        assert result.applied is False

    def test_apply_discovery_all_already_on_item_not_applied(self):
        eng = RuneEngine()
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply_discovery(state, ["flat_life"])
        assert result.applied is False

    def test_apply_discovery_no_available_not_applied(self):
        eng = RuneEngine()
        state = make_state()
        result = eng.apply_discovery(state, [])
        assert result.applied is False

    def test_apply_discovery_new_affix_at_tier_one(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state()
        eng.apply_discovery(state, ["fire_res"])
        assert state.affixes[0].current_tier == 1

    def test_apply_dispatches_removal(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply("removal", state)
        assert result.rune_type == "removal"

    def test_apply_dispatches_refinement(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life", current_tier=3)])
        result = eng.apply("refinement", state)
        assert result.rune_type == "refinement"

    def test_apply_dispatches_shaping(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply("shaping", state)
        assert result.rune_type == "shaping"

    def test_apply_dispatches_discovery(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state()
        result = eng.apply("discovery", state, available_affix_ids=["fire_res"])
        assert result.rune_type == "discovery"

    def test_apply_dispatches_via_enum_removal(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life")])
        result = eng.apply(RuneType.REMOVAL, state)
        assert result.rune_type == "removal"

    def test_apply_dispatches_via_enum_refinement(self):
        eng = RuneEngine(rng=random.Random(0))
        state = make_state(affixes=[make_affix("flat_life", current_tier=2)])
        result = eng.apply(RuneType.REFINEMENT, state)
        assert result.rune_type == "refinement"

    def test_apply_unknown_rune_not_applied(self):
        eng = RuneEngine()
        state = make_state()
        result = eng.apply("totally_unknown_rune", state)
        assert result.applied is False
