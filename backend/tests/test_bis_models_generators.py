"""
Tests for Phase Q BIS Search Engine – models and generators.
File 1 of 2. Target: 65+ tests.
"""
from __future__ import annotations

import pytest

from bis.models.item_slot import SlotType, ItemSlot, SlotPool, ALL_SLOTS
from bis.generator.item_candidate_generator import (
    ItemCandidate,
    ItemCandidateGenerator,
    BASE_ITEMS,
)
from bis.generator.affix_combination_generator import (
    AffixCombo,
    AffixCombinationGenerator,
    AVAILABLE_AFFIXES,
)
from bis.generator.tier_range_expander import TierAssignment, TierRangeExpander
from bis.pruning.candidate_pruner import CandidatePruner, PruneResult
from bis.validation.craft_feasibility import FeasibilityResult


# ===========================================================================
# SlotType
# ===========================================================================


class TestSlotTypeEnum:
    def test_helm_exists(self):
        assert SlotType.HELM.value == "helm"

    def test_chest_exists(self):
        assert SlotType.CHEST.value == "chest"

    def test_gloves_exists(self):
        assert SlotType.GLOVES.value == "gloves"

    def test_boots_exists(self):
        assert SlotType.BOOTS.value == "boots"

    def test_belt_exists(self):
        assert SlotType.BELT.value == "belt"

    def test_ring1_exists(self):
        assert SlotType.RING1.value == "ring1"

    def test_ring2_exists(self):
        assert SlotType.RING2.value == "ring2"

    def test_amulet_exists(self):
        assert SlotType.AMULET.value == "amulet"

    def test_weapon1_exists(self):
        assert SlotType.WEAPON1.value == "weapon1"

    def test_weapon2_exists(self):
        assert SlotType.WEAPON2.value == "weapon2"

    def test_offhand_exists(self):
        assert SlotType.OFFHAND.value == "offhand"

    def test_total_slot_count(self):
        assert len(SlotType) == 11

    def test_all_slots_list_length(self):
        assert len(ALL_SLOTS) == 11

    def test_all_slots_contains_helm(self):
        assert "helm" in ALL_SLOTS


# ===========================================================================
# ItemSlot
# ===========================================================================


class TestItemSlot:
    def test_default_is_enabled(self):
        slot = ItemSlot(SlotType.HELM)
        assert slot.is_enabled is True

    def test_default_max_affixes(self):
        slot = ItemSlot(SlotType.CHEST)
        assert slot.max_affixes == 4

    def test_slot_type_stored(self):
        slot = ItemSlot(SlotType.BOOTS)
        assert slot.slot_type == SlotType.BOOTS

    def test_allowed_item_classes_default_empty(self):
        slot = ItemSlot(SlotType.GLOVES)
        assert slot.allowed_item_classes == []

    def test_can_override_is_enabled(self):
        slot = ItemSlot(SlotType.RING1, is_enabled=False)
        assert slot.is_enabled is False

    def test_can_override_max_affixes(self):
        slot = ItemSlot(SlotType.AMULET, max_affixes=6)
        assert slot.max_affixes == 6


# ===========================================================================
# SlotPool
# ===========================================================================


class TestSlotPool:
    def test_all_slots_returns_11_slots(self):
        pool = SlotPool.all_slots()
        assert len(pool.slots) == 11

    def test_all_slots_all_enabled(self):
        pool = SlotPool.all_slots()
        assert all(s.is_enabled for s in pool.slots)

    def test_from_slot_types_count(self):
        pool = SlotPool.from_slot_types(["helm", "chest"])
        assert len(pool.slots) == 2

    def test_from_slot_types_correct_types(self):
        pool = SlotPool.from_slot_types(["helm", "chest"])
        values = [s.slot_type.value for s in pool.slots]
        assert "helm" in values
        assert "chest" in values

    def test_enabled_slots_full_pool(self):
        pool = SlotPool.all_slots()
        assert len(pool.enabled_slots()) == 11

    def test_enabled_slots_excludes_disabled(self):
        pool = SlotPool.all_slots()
        pool.disable("helm")
        assert len(pool.enabled_slots()) == 10

    def test_disable_helm(self):
        pool = SlotPool.all_slots()
        pool.disable("helm")
        helm = next(s for s in pool.slots if s.slot_type.value == "helm")
        assert helm.is_enabled is False

    def test_disable_does_not_affect_other_slots(self):
        pool = SlotPool.all_slots()
        pool.disable("helm")
        others = [s for s in pool.slots if s.slot_type.value != "helm"]
        assert all(s.is_enabled for s in others)

    def test_from_slot_types_single(self):
        pool = SlotPool.from_slot_types(["ring1"])
        assert len(pool.slots) == 1
        assert pool.slots[0].slot_type == SlotType.RING1


# ===========================================================================
# ItemCandidateGenerator
# ===========================================================================


class TestItemCandidateGenerator:
    def setup_method(self):
        self.gen = ItemCandidateGenerator()
        self.helm_slot = ItemSlot(SlotType.HELM)

    def test_generate_returns_list(self):
        result = self.gen.generate(self.helm_slot)
        assert isinstance(result, list)

    def test_generate_returns_item_candidates(self):
        result = self.gen.generate(self.helm_slot)
        assert all(isinstance(c, ItemCandidate) for c in result)

    def test_candidate_id_starts_with_slot_name(self):
        result = self.gen.generate(self.helm_slot)
        assert all(c.candidate_id.startswith("helm") for c in result)

    def test_candidate_slot_type_correct(self):
        result = self.gen.generate(self.helm_slot)
        assert all(c.slot_type == "helm" for c in result)

    def test_candidate_item_class_correct(self):
        result = self.gen.generate(self.helm_slot)
        assert all(c.item_class == "helm" for c in result)

    def test_forging_potential_positive(self):
        result = self.gen.generate(self.helm_slot)
        assert all(c.forging_potential > 0 for c in result)

    def test_limit_reduces_count(self):
        result = self.gen.generate(self.helm_slot, limit=1)
        assert len(result) == 1

    def test_limit_2_returns_2(self):
        result = self.gen.generate(self.helm_slot, limit=2)
        assert len(result) == 2

    def test_no_limit_returns_all_bases(self):
        n_bases = len(BASE_ITEMS["helm"])
        result = self.gen.generate(self.helm_slot)
        assert len(result) == n_bases

    def test_generate_all_returns_dict(self):
        pool = SlotPool.from_slot_types(["helm", "chest"])
        result = self.gen.generate_all(pool)
        assert isinstance(result, dict)

    def test_generate_all_keyed_by_slot_name(self):
        pool = SlotPool.from_slot_types(["helm", "chest"])
        result = self.gen.generate_all(pool)
        assert "helm" in result
        assert "chest" in result

    def test_generate_all_excludes_disabled(self):
        pool = SlotPool.from_slot_types(["helm", "chest"])
        pool.disable("helm")
        result = self.gen.generate_all(pool)
        assert "helm" not in result
        assert "chest" in result

    def test_generate_all_fp_positive(self):
        pool = SlotPool.from_slot_types(["helm"])
        result = self.gen.generate_all(pool)
        for candidates in result.values():
            assert all(c.forging_potential > 0 for c in candidates)

    def test_generate_chest(self):
        slot = ItemSlot(SlotType.CHEST)
        result = self.gen.generate(slot)
        assert len(result) > 0
        assert all(c.slot_type == "chest" for c in result)

    def test_generate_weapon1(self):
        slot = ItemSlot(SlotType.WEAPON1)
        result = self.gen.generate(slot)
        assert len(result) > 0


# ===========================================================================
# AffixCombinationGenerator
# ===========================================================================


class TestAffixCombinationGenerator:
    def setup_method(self):
        self.gen = AffixCombinationGenerator()

    def test_generate_n2_size(self):
        combos = self.gen.generate(2)
        assert all(c.size == 2 for c in combos)

    def test_generate_n2_affix_count(self):
        combos = self.gen.generate(2)
        assert all(len(c.affixes) == 2 for c in combos)

    def test_generate_n1_returns_combos(self):
        combos = self.gen.generate(1)
        assert len(combos) > 0

    def test_affix_combo_size_matches_len(self):
        combos = self.gen.generate(3)
        for c in combos:
            assert c.size == len(c.affixes)

    def test_required_affixes_always_included(self):
        combos = self.gen.generate(3, required=["max_life"])
        for c in combos:
            assert "max_life" in c.affixes

    def test_required_two_affixes_always_included(self):
        combos = self.gen.generate(3, required=["max_life", "armour"])
        for c in combos:
            assert "max_life" in c.affixes
            assert "armour" in c.affixes

    def test_excluded_affixes_never_appear(self):
        combos = self.gen.generate(2, excluded=["max_life"])
        for c in combos:
            assert "max_life" not in c.affixes

    def test_excluded_multiple_affixes(self):
        combos = self.gen.generate(2, excluded=["max_life", "armour"])
        for c in combos:
            assert "max_life" not in c.affixes
            assert "armour" not in c.affixes

    def test_generate_with_n_exceeding_pool_uses_available(self):
        tiny = AffixCombinationGenerator(available=["a", "b"])
        combos = tiny.generate(5)
        # pool only has 2 affixes, so combos will have ≤ 2 affixes
        assert all(len(c.affixes) <= 5 for c in combos)

    def test_generate_with_sizes_min1_max3_covers_all(self):
        combos = self.gen.generate_with_sizes(1, 3)
        sizes = {c.size for c in combos}
        assert 1 in sizes
        assert 2 in sizes
        assert 3 in sizes

    def test_generate_with_sizes_no_zero_size(self):
        combos = self.gen.generate_with_sizes(1, 3)
        assert all(c.size >= 1 for c in combos)

    def test_generate_with_sizes_required_in_all(self):
        combos = self.gen.generate_with_sizes(1, 3, required=["max_life"])
        for c in combos:
            assert "max_life" in c.affixes

    def test_affix_combo_is_dataclass(self):
        combo = AffixCombo(["max_life", "armour"], 2)
        assert combo.affixes == ["max_life", "armour"]
        assert combo.size == 2

    def test_custom_available_pool(self):
        gen = AffixCombinationGenerator(available=["x", "y", "z"])
        combos = gen.generate(2)
        for c in combos:
            assert all(a in ["x", "y", "z"] for a in c.affixes)


# ===========================================================================
# TierRangeExpander
# ===========================================================================


class TestTierRangeExpander:
    def setup_method(self):
        self.exp = TierRangeExpander()

    def test_expand_two_affixes_min1_max2_returns_4(self):
        result = self.exp.expand(["a", "b"], min_tier=1, max_tier=2)
        assert len(result) == 4  # (1,1),(1,2),(2,1),(2,2)

    def test_expand_one_affix_min1_max3_returns_3(self):
        result = self.exp.expand(["a"], min_tier=1, max_tier=3)
        assert len(result) == 3

    def test_expand_tier_assignment_type(self):
        result = self.exp.expand(["a"], min_tier=1, max_tier=2)
        assert all(isinstance(r, TierAssignment) for r in result)

    def test_expand_total_tier_sum_correct(self):
        result = self.exp.expand(["a", "b"], min_tier=1, max_tier=1)
        assert result[0].total_tier_sum == 2  # both tier 1

    def test_expand_with_target_tiers_caps(self):
        result = self.exp.expand(["a"], min_tier=1, max_tier=7, target_tiers={"a": 3})
        max_tier = max(r.affix_tiers["a"] for r in result)
        assert max_tier <= 3

    def test_expand_with_target_tiers_multiple(self):
        result = self.exp.expand(["a", "b"], min_tier=1, max_tier=7,
                                 target_tiers={"a": 2, "b": 3})
        for r in result:
            assert r.affix_tiers["a"] <= 2
            assert r.affix_tiers["b"] <= 3

    def test_expand_empty_affixes(self):
        result = self.exp.expand([], min_tier=1, max_tier=7)
        assert len(result) == 1
        assert result[0].affix_tiers == {}
        assert result[0].total_tier_sum == 0

    def test_expand_with_budget_filters(self):
        result = self.exp.expand_with_budget(["a", "b"], tier_budget=5)
        assert all(r.total_tier_sum <= 5 for r in result)

    def test_expand_with_budget_removes_over_budget(self):
        all_result = self.exp.expand(["a", "b"], min_tier=1, max_tier=7)
        budgeted = self.exp.expand_with_budget(["a", "b"], tier_budget=3)
        assert len(budgeted) < len(all_result)

    def test_top_assignment_all_at_max(self):
        ta = self.exp.top_assignment(["a", "b"], max_tier=7)
        assert ta.affix_tiers == {"a": 7, "b": 7}

    def test_top_assignment_total_sum(self):
        ta = self.exp.top_assignment(["a", "b", "c"], max_tier=5)
        assert ta.total_tier_sum == 15

    def test_tier_assignment_affix_tiers_dict(self):
        result = self.exp.expand(["a"], min_tier=2, max_tier=2)
        assert result[0].affix_tiers == {"a": 2}

    def test_expand_with_budget_tight_budget(self):
        result = self.exp.expand_with_budget(["a"], tier_budget=1, min_tier=1)
        assert all(r.total_tier_sum <= 1 for r in result)


# ===========================================================================
# CandidatePruner
# ===========================================================================


def _make_feasibility(candidate_id: str, feasible: bool, prob: float) -> FeasibilityResult:
    return FeasibilityResult(candidate_id, feasible, prob, 0.0, "test")


def _make_tier_assignment(tiers: dict) -> TierAssignment:
    return TierAssignment(tiers, sum(tiers.values()))


class TestCandidatePruner:
    def setup_method(self):
        self.pruner = CandidatePruner()

    def test_prune_by_feasibility_keeps_feasible(self):
        results = [
            _make_feasibility("a", True, 0.8),
            _make_feasibility("b", False, 0.0),
        ]
        pr = self.pruner.prune_by_feasibility(results)
        assert len(pr.kept) == 1
        assert pr.kept[0].candidate_id == "a"

    def test_prune_by_feasibility_removes_infeasible(self):
        results = [
            _make_feasibility("a", True, 0.8),
            _make_feasibility("b", False, 0.0),
        ]
        pr = self.pruner.prune_by_feasibility(results)
        assert len(pr.pruned) == 1
        assert pr.pruned[0].candidate_id == "b"

    def test_prune_by_feasibility_filters_by_min_prob(self):
        pruner = CandidatePruner(min_success_prob=0.5)
        results = [
            _make_feasibility("a", True, 0.9),
            _make_feasibility("b", True, 0.3),  # feasible but below threshold
        ]
        pr = pruner.prune_by_feasibility(results)
        assert len(pr.kept) == 1
        assert pr.kept[0].candidate_id == "a"

    def test_prune_by_feasibility_all_feasible(self):
        results = [_make_feasibility(f"c{i}", True, 1.0) for i in range(5)]
        pr = self.pruner.prune_by_feasibility(results)
        assert len(pr.kept) == 5
        assert len(pr.pruned) == 0

    def test_prune_by_feasibility_all_infeasible(self):
        results = [_make_feasibility(f"c{i}", False, 0.0) for i in range(3)]
        pr = self.pruner.prune_by_feasibility(results)
        assert len(pr.kept) == 0
        assert len(pr.pruned) == 3

    def test_prune_by_tier_keeps_above_min(self):
        pruner = CandidatePruner(min_tier_sum=5)
        assignments = [
            _make_tier_assignment({"a": 3, "b": 3}),  # sum=6 ✓
            _make_tier_assignment({"a": 1, "b": 2}),  # sum=3 ✗
        ]
        pr = pruner.prune_by_tier(assignments)
        assert len(pr.kept) == 1
        assert pr.kept[0].total_tier_sum == 6

    def test_prune_by_tier_removes_below_min(self):
        pruner = CandidatePruner(min_tier_sum=5)
        assignments = [
            _make_tier_assignment({"a": 3, "b": 3}),
            _make_tier_assignment({"a": 1, "b": 2}),
        ]
        pr = pruner.prune_by_tier(assignments)
        assert len(pr.pruned) == 1
        assert pr.pruned[0].total_tier_sum == 3

    def test_prune_dominated_keeps_top_half(self):
        candidates = [(f"c{i}", float(i)) for i in range(10)]
        pr = self.pruner.prune_dominated(candidates)
        assert len(pr.kept) == 5
        assert len(pr.pruned) == 5

    def test_prune_dominated_kept_are_highest_scores(self):
        candidates = [(f"c{i}", float(i)) for i in range(10)]
        pr = self.pruner.prune_dominated(candidates)
        # kept items are sorted descending, so they have the highest scores
        assert all(k == f"c{9 - i}" for i, k in enumerate(pr.kept))

    def test_prune_result_prune_rate_range(self):
        results = [
            _make_feasibility("a", True, 0.9),
            _make_feasibility("b", False, 0.0),
        ]
        pr = self.pruner.prune_by_feasibility(results)
        assert 0.0 <= pr.prune_rate <= 1.0

    def test_prune_rate_half(self):
        results = [
            _make_feasibility("a", True, 0.9),
            _make_feasibility("b", False, 0.0),
        ]
        pr = self.pruner.prune_by_feasibility(results)
        assert pr.prune_rate == pytest.approx(0.5)

    def test_prune_empty_list_kept_empty(self):
        pr = self.pruner.prune_by_feasibility([])
        assert pr.kept == []

    def test_prune_empty_list_pruned_empty(self):
        pr = self.pruner.prune_by_feasibility([])
        assert pr.pruned == []

    def test_prune_empty_list_rate_zero(self):
        pr = self.pruner.prune_by_feasibility([])
        assert pr.prune_rate == 0.0

    def test_prune_dominated_single_item(self):
        pr = self.pruner.prune_dominated([("c0", 1.0)])
        assert len(pr.kept) == 1
        assert len(pr.pruned) == 0

    def test_prune_dominated_empty(self):
        pr = self.pruner.prune_dominated([])
        assert pr.kept == []
        assert pr.pruned == []
        assert pr.prune_rate == 0.0

    def test_prune_result_is_dataclass(self):
        pr = PruneResult(kept=[1], pruned=[], prune_rate=0.0)
        assert pr.kept == [1]
        assert pr.pruned == []
        assert pr.prune_rate == 0.0
