"""
Tests for Phase Q BIS Search Engine – engine, scoring, adapter, and parallel components.
File 2 of 2. Target: 60+ tests.
"""
from __future__ import annotations

import pytest

from crafting.models.craft_state import CraftState, AffixState
from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment
from bis.integration.build_adapter import BuildAdapter, BuildSnapshot
from bis.engine.multi_slot_combiner import MultiSlotCombiner, CombinationBatch
from bis.engine.parallel_manager import ParallelManager, ParallelTask, ParallelResult
from bis.scoring.build_score_engine import BuildScoreEngine, BuildScore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_candidate(slot: str = "helm", fp: int = 80) -> ItemCandidate:
    return ItemCandidate(
        candidate_id=f"{slot}_iron",
        item_class=slot,
        slot_type=slot,
        base_name="Iron Item",
        forging_potential=fp,
    )


def _make_assignment(tiers: dict[str, int]) -> TierAssignment:
    return TierAssignment(tiers, sum(tiers.values()))


def _make_craft_state(
    slot: str = "helm",
    fp: int = 80,
    affixes: list[AffixState] | None = None,
    is_fractured: bool = False,
) -> CraftState:
    return CraftState(
        item_id=f"{slot}_iron",
        item_name="Iron Item",
        item_class=slot,
        forging_potential=fp,
        instability=0,
        affixes=affixes or [],
        is_fractured=is_fractured,
    )


def _make_snapshot(
    build_id: str = "build_001",
    slots: dict | None = None,
    total_affix_count: int = 0,
    total_tier_sum: int = 0,
) -> BuildSnapshot:
    return BuildSnapshot(
        build_id=build_id,
        slots=slots or {},
        total_affix_count=total_affix_count,
        total_tier_sum=total_tier_sum,
    )


# ===========================================================================
# BuildAdapter
# ===========================================================================


class TestBuildAdapter:
    def setup_method(self):
        self.adapter = BuildAdapter()

    def test_candidate_to_state_returns_craft_state(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5, "armour": 3})
        state = self.adapter.candidate_to_state(candidate, assignment)
        assert isinstance(state, CraftState)

    def test_candidate_to_state_item_id(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5})
        state = self.adapter.candidate_to_state(candidate, assignment)
        assert state.item_id == candidate.candidate_id

    def test_candidate_to_state_affixes_match_assignment(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5, "armour": 3})
        state = self.adapter.candidate_to_state(candidate, assignment)
        affix_ids = {a.affix_id for a in state.affixes}
        assert affix_ids == {"max_life", "armour"}

    def test_candidate_to_state_affix_tiers_match(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5, "armour": 3})
        state = self.adapter.candidate_to_state(candidate, assignment)
        tier_map = {a.affix_id: a.current_tier for a in state.affixes}
        assert tier_map["max_life"] == 5
        assert tier_map["armour"] == 3

    def test_candidate_to_state_forging_potential(self):
        candidate = _make_candidate("helm", 90)
        assignment = _make_assignment({})
        state = self.adapter.candidate_to_state(candidate, assignment)
        assert state.forging_potential == 90

    def test_candidate_to_state_item_class(self):
        candidate = _make_candidate("chest", 70)
        assignment = _make_assignment({"max_life": 4})
        state = self.adapter.candidate_to_state(candidate, assignment)
        assert state.item_class == "chest"

    def test_assemble_build_returns_snapshot(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5})
        snapshot = self.adapter.assemble_build(
            "b001", {"helm": (candidate, assignment)}
        )
        assert isinstance(snapshot, BuildSnapshot)

    def test_assemble_build_correct_total_affix_count(self):
        c_helm = _make_candidate("helm", 80)
        a_helm = _make_assignment({"max_life": 5, "armour": 3})
        c_chest = _make_candidate("chest", 70)
        a_chest = _make_assignment({"resistances": 4})
        snapshot = self.adapter.assemble_build(
            "b001",
            {"helm": (c_helm, a_helm), "chest": (c_chest, a_chest)},
        )
        assert snapshot.total_affix_count == 3  # 2 helm + 1 chest

    def test_assemble_build_correct_total_tier_sum(self):
        c_helm = _make_candidate("helm", 80)
        a_helm = _make_assignment({"max_life": 5, "armour": 3})  # sum = 8
        c_chest = _make_candidate("chest", 70)
        a_chest = _make_assignment({"resistances": 4})  # sum = 4
        snapshot = self.adapter.assemble_build(
            "b001",
            {"helm": (c_helm, a_helm), "chest": (c_chest, a_chest)},
        )
        assert snapshot.total_tier_sum == 12

    def test_assemble_build_slots_populated(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({"max_life": 5})
        snapshot = self.adapter.assemble_build(
            "b001", {"helm": (candidate, assignment)}
        )
        assert "helm" in snapshot.slots

    def test_assemble_build_build_id(self):
        candidate = _make_candidate("helm", 80)
        assignment = _make_assignment({})
        snapshot = self.adapter.assemble_build("my_build", {"helm": (candidate, assignment)})
        assert snapshot.build_id == "my_build"

    def test_extract_affixes_returns_dict(self):
        state = _make_craft_state(
            "helm", affixes=[AffixState("max_life", 5, 7), AffixState("armour", 3, 7)]
        )
        snapshot = _make_snapshot("b001", slots={"helm": state}, total_affix_count=2)
        result = self.adapter.extract_affixes(snapshot)
        assert isinstance(result, dict)

    def test_extract_affixes_slot_key(self):
        state = _make_craft_state(
            "helm", affixes=[AffixState("max_life", 5, 7)]
        )
        snapshot = _make_snapshot("b001", slots={"helm": state})
        result = self.adapter.extract_affixes(snapshot)
        assert "helm" in result

    def test_extract_affixes_affix_ids_correct(self):
        state = _make_craft_state(
            "helm", affixes=[AffixState("max_life", 5, 7), AffixState("armour", 3, 7)]
        )
        snapshot = _make_snapshot("b001", slots={"helm": state})
        result = self.adapter.extract_affixes(snapshot)
        assert set(result["helm"]) == {"max_life", "armour"}

    def test_extract_affixes_empty_slots(self):
        snapshot = _make_snapshot("b001", slots={})
        result = self.adapter.extract_affixes(snapshot)
        assert result == {}

    def test_assemble_build_empty_slots(self):
        snapshot = self.adapter.assemble_build("empty_build", {})
        assert snapshot.total_affix_count == 0
        assert snapshot.total_tier_sum == 0
        assert snapshot.slots == {}


# ===========================================================================
# MultiSlotCombiner
# ===========================================================================


def _slot_opts(slot: str, n: int) -> list[tuple[ItemCandidate, TierAssignment]]:
    return [
        (_make_candidate(slot, 80 + i * 5), _make_assignment({"max_life": i + 1}))
        for i in range(n)
    ]


class TestMultiSlotCombiner:
    def setup_method(self):
        self.combiner = MultiSlotCombiner()

    def test_combine_2x2_gives_4_combos(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 2),
            "chest": _slot_opts("chest", 2),
        }
        batch = self.combiner.combine(slot_candidates)
        assert len(batch.combinations) == 4

    def test_combine_returns_batch(self):
        slot_candidates = {"helm": _slot_opts("helm", 2)}
        batch = self.combiner.combine(slot_candidates)
        assert isinstance(batch, CombinationBatch)

    def test_combine_snapshots_are_build_snapshots(self):
        slot_candidates = {"helm": _slot_opts("helm", 2)}
        batch = self.combiner.combine(slot_candidates)
        assert all(isinstance(s, BuildSnapshot) for s in batch.combinations)

    def test_combine_respects_max_combinations(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 5),
            "chest": _slot_opts("chest", 5),
        }
        batch = self.combiner.combine(slot_candidates, max_combinations=3)
        assert len(batch.combinations) <= 3

    def test_combine_total_evaluated_correct(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 2),
            "chest": _slot_opts("chest", 2),
        }
        batch = self.combiner.combine(slot_candidates)
        assert batch.total_evaluated == 4

    def test_combine_slots_covered_lists_all(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 2),
            "chest": _slot_opts("chest", 2),
        }
        batch = self.combiner.combine(slot_candidates)
        assert set(batch.slots_covered) == {"helm", "chest"}

    def test_combine_greedy_returns_snapshot(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 3),
            "chest": _slot_opts("chest", 3),
        }
        snapshot = self.combiner.combine_greedy(slot_candidates)
        assert isinstance(snapshot, BuildSnapshot)

    def test_combine_greedy_picks_one_per_slot(self):
        slot_candidates = {
            "helm": _slot_opts("helm", 3),
            "chest": _slot_opts("chest", 3),
        }
        snapshot = self.combiner.combine_greedy(slot_candidates)
        assert len(snapshot.slots) == 2

    def test_combine_greedy_build_id(self):
        slot_candidates = {"helm": _slot_opts("helm", 2)}
        snapshot = self.combiner.combine_greedy(slot_candidates)
        assert snapshot.build_id == "greedy_best"

    def test_combine_empty_candidates_one_empty_combo(self):
        # itertools.product() of zero sequences yields exactly one empty tuple,
        # so MultiSlotCombiner returns a single BuildSnapshot with no slots.
        batch = self.combiner.combine({})
        assert len(batch.combinations) == 1
        assert batch.combinations[0].slots == {}

    def test_combine_batch_slots_covered_type(self):
        slot_candidates = {"helm": _slot_opts("helm", 1)}
        batch = self.combiner.combine(slot_candidates)
        assert isinstance(batch.slots_covered, list)

    def test_combine_1x1_gives_1_combo(self):
        slot_candidates = {"helm": _slot_opts("helm", 1)}
        batch = self.combiner.combine(slot_candidates)
        assert len(batch.combinations) == 1


# ===========================================================================
# ParallelManager
# ===========================================================================


class TestParallelManager:
    def setup_method(self):
        self.pm = ParallelManager(max_workers=4)

    def _make_tasks(self, n: int) -> list[ParallelTask]:
        return [
            ParallelTask(f"task_{i}", lambda x: x * 2, args=(i,))
            for i in range(n)
        ]

    def test_run_3_tasks_returns_3_results(self):
        tasks = self._make_tasks(3)
        results = self.pm.run(tasks)
        assert len(results) == 3

    def test_results_have_matching_task_ids(self):
        tasks = self._make_tasks(3)
        results = self.pm.run(tasks)
        result_ids = {r.task_id for r in results}
        assert result_ids == {"task_0", "task_1", "task_2"}

    def test_successful_tasks_have_error_none(self):
        tasks = self._make_tasks(3)
        results = self.pm.run(tasks)
        assert all(r.error is None for r in results)

    def test_all_results_have_duration_ms_non_negative(self):
        tasks = self._make_tasks(3)
        results = self.pm.run(tasks)
        assert all(r.duration_ms >= 0 for r in results)

    def test_failed_task_has_error_set(self):
        def failing_fn():
            raise ValueError("intentional failure")

        tasks = [ParallelTask("bad_task", failing_fn)]
        results = self.pm.run(tasks)
        assert len(results) == 1
        assert results[0].error is not None
        assert "intentional failure" in results[0].error

    def test_failed_task_result_is_none(self):
        def failing_fn():
            raise RuntimeError("boom")

        tasks = [ParallelTask("bad_task", failing_fn)]
        results = self.pm.run(tasks)
        assert results[0].result is None

    def test_failed_task_duration_non_negative(self):
        def failing_fn():
            raise RuntimeError("boom")

        tasks = [ParallelTask("bad_task", failing_fn)]
        results = self.pm.run(tasks)
        assert results[0].duration_ms >= 0

    def test_mixed_tasks_correct_count(self):
        def ok_fn():
            return 42

        def bad_fn():
            raise ValueError("err")

        tasks = [
            ParallelTask("ok", ok_fn),
            ParallelTask("bad", bad_fn),
        ]
        results = self.pm.run(tasks)
        assert len(results) == 2

    def test_run_batch_splits_correctly(self):
        items = list(range(25))
        results = self.pm.run_batch(lambda chunk: len(chunk), items, chunk_size=10)
        assert len(results) == 3  # 10, 10, 5 → 3 chunks

    def test_run_batch_task_ids_named_chunks(self):
        items = list(range(20))
        results = self.pm.run_batch(lambda chunk: chunk, items, chunk_size=10)
        task_ids = {r.task_id for r in results}
        assert "chunk_0" in task_ids
        assert "chunk_1" in task_ids

    def test_run_batch_correct_number_of_results(self):
        items = list(range(5))
        results = self.pm.run_batch(lambda chunk: chunk, items, chunk_size=5)
        assert len(results) == 1  # one chunk of 5

    def test_run_zero_tasks(self):
        results = self.pm.run([])
        assert results == []

    def test_parallel_result_is_dataclass(self):
        pr = ParallelResult("t1", 42, 10.0, None)
        assert pr.task_id == "t1"
        assert pr.result == 42
        assert pr.duration_ms == 10.0
        assert pr.error is None


# ===========================================================================
# BuildScoreEngine
# ===========================================================================


def _snapshot_with_affixes(
    build_id: str,
    slot: str,
    affix_tiers: dict[str, int],
    fp: int = 100,
) -> BuildSnapshot:
    affixes = [AffixState(aid, tier, 7) for aid, tier in affix_tiers.items()]
    state = CraftState(
        item_id=f"{slot}_item",
        item_name="Test Item",
        item_class=slot,
        forging_potential=fp,
        instability=0,
        affixes=affixes,
    )
    return BuildSnapshot(
        build_id=build_id,
        slots={slot: state},
        total_affix_count=len(affixes),
        total_tier_sum=sum(affix_tiers.values()),
    )


class TestBuildScoreEngine:
    def setup_method(self):
        self.engine = BuildScoreEngine()

    def test_score_returns_build_score(self):
        snapshot = _snapshot_with_affixes("b1", "helm", {"max_life": 7})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert isinstance(score, BuildScore)

    def test_perfect_coverage_max_tiers_near_1(self):
        snapshot = _snapshot_with_affixes("b1", "helm", {"max_life": 7}, fp=100)
        score = self.engine.score(
            snapshot,
            ["max_life"],
            {"max_life": 7},
            weights={"tier": 0.5, "coverage": 0.4, "fp": 0.1},
        )
        assert score.total_score == pytest.approx(1.0, abs=0.01)

    def test_no_target_affixes_present_coverage_zero(self):
        snapshot = _snapshot_with_affixes("b2", "helm", {"armour": 5})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.coverage_score == pytest.approx(0.0)

    def test_no_target_affixes_present_tier_score_zero(self):
        snapshot = _snapshot_with_affixes("b2", "helm", {"armour": 5})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.tier_score == pytest.approx(0.0)

    def test_fp_score_clamped_at_1(self):
        # fp=100 → fp/100=1.0
        snapshot = _snapshot_with_affixes("b3", "helm", {"max_life": 7}, fp=100)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.fp_score <= 1.0

    def test_fp_score_proportional(self):
        snapshot = _snapshot_with_affixes("b4", "helm", {"max_life": 7}, fp=50)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.fp_score == pytest.approx(0.5, abs=0.01)

    def test_fp_score_is_fp_over_100(self):
        snapshot = _snapshot_with_affixes("b5", "helm", {"max_life": 7}, fp=80)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.fp_score == pytest.approx(0.8, abs=0.01)

    def test_tier_weight_only_equals_tier_score(self):
        snapshot = _snapshot_with_affixes("b6", "helm", {"max_life": 7}, fp=80)
        score = self.engine.score(
            snapshot,
            ["max_life"],
            {"max_life": 7},
            weights={"tier": 1.0, "coverage": 0.0, "fp": 0.0},
        )
        assert score.total_score == pytest.approx(score.tier_score, abs=1e-6)

    def test_coverage_weight_only_equals_coverage(self):
        snapshot = _snapshot_with_affixes("b7", "helm", {"max_life": 7})
        score = self.engine.score(
            snapshot,
            ["max_life"],
            {"max_life": 7},
            weights={"tier": 0.0, "coverage": 1.0, "fp": 0.0},
        )
        assert score.total_score == pytest.approx(score.coverage_score, abs=1e-6)

    def test_slot_scores_populated(self):
        snapshot = _snapshot_with_affixes("b8", "helm", {"max_life": 7})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert "helm" in score.slot_scores

    def test_slot_scores_non_negative(self):
        snapshot = _snapshot_with_affixes("b9", "helm", {"max_life": 7})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert all(v >= 0.0 for v in score.slot_scores.values())

    def test_build_id_matches_snapshot(self):
        snapshot = _snapshot_with_affixes("my_build", "helm", {"max_life": 7})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.build_id == "my_build"

    def test_fractured_item_fp_0_reduces_fp_score(self):
        # fractured items: set fp=0 to simulate worst-case fractured
        state = CraftState(
            item_id="helm_frac",
            item_name="Fractured Helm",
            item_class="helm",
            forging_potential=0,
            instability=0,
            affixes=[AffixState("max_life", 7, 7)],
            is_fractured=True,
        )
        snapshot = BuildSnapshot("frac_build", {"helm": state}, 1, 7)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.fp_score == pytest.approx(0.0, abs=0.01)

    def test_partial_coverage_score(self):
        snapshot = _snapshot_with_affixes("b10", "helm", {"max_life": 7})
        # target = 2 affixes, only 1 present
        score = self.engine.score(
            snapshot, ["max_life", "armour"], {"max_life": 7, "armour": 7}
        )
        assert score.coverage_score == pytest.approx(0.5, abs=0.01)

    def test_total_score_in_range(self):
        snapshot = _snapshot_with_affixes("b11", "helm", {"max_life": 5})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert 0.0 <= score.total_score <= 1.0

    def test_empty_slots_coverage_zero(self):
        snapshot = BuildSnapshot("empty", {}, 0, 0)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.coverage_score == pytest.approx(0.0)

    def test_empty_slots_fp_score_zero(self):
        snapshot = BuildSnapshot("empty", {}, 0, 0)
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.fp_score == pytest.approx(0.0)

    def test_slot_scores_zero_when_no_target_affixes(self):
        # slot has armour, but target is max_life → slot score = 0
        snapshot = _snapshot_with_affixes("b12", "helm", {"armour": 5})
        score = self.engine.score(snapshot, ["max_life"], {"max_life": 7})
        assert score.slot_scores.get("helm", 0.0) == pytest.approx(0.0)

    def test_build_score_is_dataclass(self):
        bs = BuildScore("b", 0.5, 0.5, 0.5, 0.5, {"helm": 0.5})
        assert bs.build_id == "b"
        assert bs.total_score == 0.5
