"""
Tests for Phase Q BIS Search Engine: BisSearchLogger, IncrementalSearchEngine,
CraftAdapter, CraftFeasibilityValidator.

Run from backend/:
    python -m pytest tests/test_bis_search_logger_search.py -v --tb=short
"""

import pytest

from debug.bis_search_logger import BisSearchLogger, BisLogEntry
from bis.engine.incremental_search import IncrementalSearchEngine, SearchStage
from bis.models.bis_result import BisResult
from bis.integration.craft_adapter import CraftAdapter, CraftAdapterResult
from bis.validation.craft_feasibility import CraftFeasibilityValidator, FeasibilityResult
from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment
from bis.models.item_slot import SlotPool, SlotType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_candidate(candidate_id: str = "helm_iron_helm") -> ItemCandidate:
    return ItemCandidate(
        candidate_id=candidate_id,
        item_class="helm",
        slot_type="helm",
        base_name="Iron Helm",
        forging_potential=60,
    )


def make_assignment(affixes: list[str] | None = None, tiers: dict | None = None) -> TierAssignment:
    if affixes is None:
        affixes = ["phys_dmg", "crit_chance"]
    if tiers is None:
        tiers = {a: 3 for a in affixes}
    return TierAssignment(tiers, sum(tiers.values()))


def make_slot_pool_small() -> SlotPool:
    return SlotPool.from_slot_types(["helm"])


# ===========================================================================
# BisSearchLogger tests (22 tests)
# ===========================================================================

class TestBisSearchLoggerLogMethods:
    def setup_method(self):
        self.logger = BisSearchLogger()

    def test_log_search_start_stores_entry(self):
        self.logger.log_search_start("s1", ["affix_a"], 3)
        entries = self.logger.get_entries()
        assert len(entries) == 1

    def test_log_search_start_event_type(self):
        self.logger.log_search_start("s1", ["affix_a"], 3)
        entries = self.logger.get_entries()
        assert entries[0].event_type == "search_start"

    def test_log_search_start_search_id(self):
        self.logger.log_search_start("s99", ["a"], 2)
        entry = self.logger.get_entries()[0]
        assert entry.search_id == "s99"

    def test_log_search_complete_stored_with_correct_fields(self):
        self.logger.log_search_complete("s1", 100, 0.85, 0.5)
        entry = self.logger.get_entries()[0]
        assert entry.event_type == "search_complete"
        assert entry.data["evaluated"] == 100
        assert entry.data["best_score"] == 0.85
        assert entry.data["duration_s"] == 0.5

    def test_log_search_complete_search_id(self):
        self.logger.log_search_complete("sid", 10, 0.5, 0.1)
        entry = self.logger.get_entries()[0]
        assert entry.search_id == "sid"

    def test_log_candidate_evaluated_stored_with_candidate_id_and_score(self):
        self.logger.log_candidate_evaluated("s1", "cand_001", 0.72)
        entry = self.logger.get_entries()[0]
        assert entry.event_type == "candidate_evaluated"
        assert entry.data["candidate_id"] == "cand_001"
        assert entry.data["score"] == 0.72

    def test_log_cache_hit_stored_with_key(self):
        self.logger.log_cache_hit("s1", "cache_key_abc")
        entry = self.logger.get_entries()[0]
        assert entry.event_type == "cache_hit"
        assert entry.data["key"] == "cache_key_abc"

    def test_log_prune_stored_with_pruned_count_and_reason(self):
        self.logger.log_prune("s1", 50, "low_score")
        entry = self.logger.get_entries()[0]
        assert entry.event_type == "prune"
        assert entry.data["pruned_count"] == 50
        assert entry.data["reason"] == "low_score"

    def test_log_error_stored_with_error_message(self):
        self.logger.log_error("s1", "something went wrong")
        entry = self.logger.get_entries()[0]
        assert entry.event_type == "error"
        assert entry.data["error"] == "something went wrong"

    def test_log_error_with_none_search_id(self):
        self.logger.log_error(None, "orphan error")
        entry = self.logger.get_entries()[0]
        assert entry.search_id is None

    def test_entries_are_bis_log_entry_instances(self):
        self.logger.log_search_start("s1", [], 0)
        entry = self.logger.get_entries()[0]
        assert isinstance(entry, BisLogEntry)


class TestBisSearchLoggerGetEntries:
    def setup_method(self):
        self.logger = BisSearchLogger()
        self.logger.log_search_start("s1", ["a"], 1)
        self.logger.log_prune("s1", 10, "low")
        self.logger.log_prune("s2", 5, "tier")
        self.logger.log_search_complete("s1", 50, 0.9, 0.3)
        self.logger.log_candidate_evaluated("s2", "c1", 0.4)

    def test_get_entries_returns_all(self):
        assert len(self.logger.get_entries()) == 5

    def test_get_entries_filter_by_event_type(self):
        pruned = self.logger.get_entries(event_type="prune")
        assert len(pruned) == 2
        assert all(e.event_type == "prune" for e in pruned)

    def test_get_entries_filter_by_search_id(self):
        s1_entries = self.logger.get_entries(search_id="s1")
        assert all(e.search_id == "s1" for e in s1_entries)

    def test_get_entries_filter_by_both(self):
        result = self.logger.get_entries(event_type="prune", search_id="s1")
        assert len(result) == 1
        assert result[0].search_id == "s1"
        assert result[0].event_type == "prune"

    def test_get_entries_unknown_type_returns_empty(self):
        result = self.logger.get_entries(event_type="nonexistent")
        assert result == []


class TestBisSearchLoggerSummary:
    def test_summary_total_entries(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 0)
        logger.log_search_complete("s1", 10, 0.5, 0.1)
        s = logger.summary()
        assert s["total_entries"] == 2

    def test_summary_by_type_counts(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 0)
        logger.log_search_start("s2", [], 0)
        s = logger.summary()
        assert s["by_type"]["search_start"] == 2

    def test_summary_searches_completed(self):
        logger = BisSearchLogger()
        logger.log_search_complete("s1", 5, 0.5, 0.1)
        logger.log_search_complete("s2", 10, 0.8, 0.2)
        s = logger.summary()
        assert s["searches_completed"] == 2

    def test_summary_total_evaluated(self):
        logger = BisSearchLogger()
        logger.log_search_complete("s1", 25, 0.5, 0.1)
        logger.log_search_complete("s2", 75, 0.8, 0.2)
        s = logger.summary()
        assert s["total_evaluated"] == 100

    def test_summary_empty_logger(self):
        logger = BisSearchLogger()
        s = logger.summary()
        assert s["total_entries"] == 0
        assert s["searches_completed"] == 0
        assert s["total_evaluated"] == 0


class TestBisSearchLoggerClearCapacityLen:
    def test_clear_empties_logger(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 0)
        logger.clear()
        assert len(logger) == 0

    def test_len_correct(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 0)
        logger.log_cache_hit("s1", "k")
        assert len(logger) == 2

    def test_capacity_enforced(self):
        logger = BisSearchLogger(capacity=3)
        for i in range(10):
            logger.log_search_start(f"s{i}", [], 0)
        assert len(logger) == 3

    def test_capacity_keeps_most_recent(self):
        logger = BisSearchLogger(capacity=2)
        logger.log_search_start("s1", [], 0)
        logger.log_search_start("s2", [], 0)
        logger.log_search_start("s3", [], 0)
        entries = logger.get_entries()
        search_ids = [e.search_id for e in entries]
        assert "s3" in search_ids
        assert "s1" not in search_ids


# ===========================================================================
# IncrementalSearchEngine tests (14 tests)
# ===========================================================================

class TestIncrementalSearchEngine:
    def setup_method(self):
        self.engine = IncrementalSearchEngine(n_runs_per_eval=10)
        self.slot_pool = make_slot_pool_small()
        self.target_affixes = ["phys_dmg", "crit_chance"]
        self.target_tiers = {"phys_dmg": 5, "crit_chance": 3}

    def _run_search(self, top_n=5, max_candidates=50):
        return self.engine.search(
            self.slot_pool,
            self.target_affixes,
            self.target_tiers,
            top_n=top_n,
            max_candidates=max_candidates,
        )

    def test_search_returns_bis_result(self):
        result = self._run_search()
        assert isinstance(result, BisResult)

    def test_search_total_evaluated_positive(self):
        result = self._run_search()
        assert result.total_evaluated > 0

    def test_search_duration_positive(self):
        result = self._run_search()
        assert result.search_duration_s > 0

    def test_search_best_score_in_range(self):
        result = self._run_search()
        assert 0.0 <= result.best_score <= 1.0

    def test_search_top_entries_non_empty(self):
        result = self._run_search()
        assert len(result.top_entries) > 0

    def test_search_top_n_limits_entries(self):
        result = self._run_search(top_n=2, max_candidates=50)
        assert len(result.top_entries) <= 2

    def test_search_max_candidates_limits_evaluation(self):
        result_small = self._run_search(max_candidates=1)
        result_large = self._run_search(max_candidates=100)
        assert result_small.total_evaluated <= result_large.total_evaluated

    def test_search_target_affixes_stored(self):
        result = self._run_search()
        assert result.target_affixes == self.target_affixes

    def test_get_stages_returns_list_after_search(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        engine.search(self.slot_pool, self.target_affixes, self.target_tiers, max_candidates=50)
        stages = engine.get_stages()
        assert isinstance(stages, list)

    def test_get_stages_non_empty_after_search(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        engine.search(self.slot_pool, self.target_affixes, self.target_tiers, max_candidates=50)
        stages = engine.get_stages()
        assert len(stages) > 0

    def test_search_stage_elapsed_s_positive(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        engine.search(self.slot_pool, self.target_affixes, self.target_tiers, max_candidates=50)
        stages = engine.get_stages()
        assert all(s.elapsed_s > 0 for s in stages)

    def test_search_stage_is_search_stage_instance(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        engine.search(self.slot_pool, self.target_affixes, self.target_tiers, max_candidates=50)
        stages = engine.get_stages()
        assert all(isinstance(s, SearchStage) for s in stages)

    def test_search_no_affixes_returns_bis_result(self):
        result = self.engine.search(
            self.slot_pool, [], {}, top_n=5, max_candidates=20
        )
        assert isinstance(result, BisResult)

    def test_search_stage_candidates_evaluated_nonnegative(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        engine.search(self.slot_pool, self.target_affixes, self.target_tiers, max_candidates=50)
        stages = engine.get_stages()
        assert all(s.candidates_evaluated >= 0 for s in stages)


# ===========================================================================
# CraftAdapter tests (12 tests)
# ===========================================================================

class TestCraftAdapter:
    def setup_method(self):
        self.adapter = CraftAdapter(n_runs=10, min_prob=0.0)

    def test_evaluate_returns_craft_adapter_result(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.adapter.evaluate(candidate, assignment)
        assert isinstance(result, CraftAdapterResult)

    def test_evaluate_feasibility_populated(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.adapter.evaluate(candidate, assignment)
        assert isinstance(result.feasibility, FeasibilityResult)

    def test_evaluate_adjusted_tiers_present(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 3})
        result = self.adapter.evaluate(candidate, assignment)
        assert isinstance(result.adjusted_tiers, dict)

    def test_evaluate_adjusted_tiers_has_same_keys_as_assignment(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg", "crit_chance"], {"phys_dmg": 3, "crit_chance": 2})
        result = self.adapter.evaluate(candidate, assignment)
        assert set(result.adjusted_tiers.keys()) == set(assignment.affix_tiers.keys())

    def test_evaluate_feasible_result_keeps_original_tiers(self):
        # With min_prob=0.0, all results are feasible; tiers should match assignment
        adapter = CraftAdapter(n_runs=10, min_prob=0.0)
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 3})
        result = adapter.evaluate(candidate, assignment)
        if result.feasibility.feasible:
            assert result.adjusted_tiers == assignment.affix_tiers

    def test_evaluate_infeasible_result_adjusts_tiers_down(self):
        # Force infeasible by using extremely high min_prob
        adapter = CraftAdapter(n_runs=10, min_prob=1.1)
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 4})
        result = adapter.evaluate(candidate, assignment)
        if not result.feasibility.feasible:
            for affix, tier in result.adjusted_tiers.items():
                original = assignment.affix_tiers[affix]
                assert tier == max(1, original - 1)

    def test_evaluate_candidate_id_stored(self):
        candidate = make_candidate("my_helm")
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.adapter.evaluate(candidate, assignment)
        assert result.candidate_id == "my_helm"

    def test_filter_feasible_keeps_only_feasible(self):
        candidate = make_candidate()
        assignment = make_assignment([], {})
        results = [self.adapter.evaluate(candidate, assignment)]
        feasible = self.adapter.filter_feasible(results)
        assert all(r.feasibility.feasible for r in feasible)

    def test_evaluate_batch_processes_all_items(self):
        pairs = [
            (make_candidate(f"cand_{i}"), make_assignment([], {}))
            for i in range(3)
        ]
        results = self.adapter.evaluate_batch(pairs)
        assert len(results) == 3

    def test_evaluate_batch_returns_list_of_craft_adapter_results(self):
        pairs = [(make_candidate(), make_assignment([], {}))]
        results = self.adapter.evaluate_batch(pairs)
        assert isinstance(results[0], CraftAdapterResult)

    def test_evaluate_no_affixes_feasible(self):
        candidate = make_candidate()
        assignment = make_assignment([], {})
        result = self.adapter.evaluate(candidate, assignment)
        assert result.feasibility.feasible is True

    def test_evaluate_adjusted_tiers_min_is_one(self):
        adapter = CraftAdapter(n_runs=10, min_prob=1.1)  # force infeasible
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 1})
        result = adapter.evaluate(candidate, assignment)
        if not result.feasibility.feasible:
            assert result.adjusted_tiers["phys_dmg"] >= 1


# ===========================================================================
# CraftFeasibilityValidator tests (12 tests)
# ===========================================================================

class TestCraftFeasibilityValidator:
    def setup_method(self):
        self.validator = CraftFeasibilityValidator(n_runs=10, min_success_prob=0.0)

    def test_validate_returns_feasibility_result(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.validator.validate(candidate, assignment)
        assert isinstance(result, FeasibilityResult)

    def test_validate_candidate_id_correct(self):
        candidate = make_candidate("unique_id_456")
        assignment = make_assignment([], {})
        result = self.validator.validate(candidate, assignment)
        assert result.candidate_id == "unique_id_456"

    def test_validate_success_probability_in_range(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.validator.validate(candidate, assignment)
        assert 0.0 <= result.success_probability <= 1.0

    def test_validate_no_affixes_feasible_true(self):
        candidate = make_candidate()
        assignment = make_assignment([], {})
        result = self.validator.validate(candidate, assignment)
        assert result.feasible is True

    def test_validate_no_affixes_success_prob_one(self):
        candidate = make_candidate()
        assignment = make_assignment([], {})
        result = self.validator.validate(candidate, assignment)
        assert result.success_probability == 1.0

    def test_validate_with_zero_min_prob_feasible(self):
        # min_success_prob=0.0 means any success rate is feasible
        validator = CraftFeasibilityValidator(n_runs=10, min_success_prob=0.0)
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 3})
        result = validator.validate(candidate, assignment)
        assert result.feasible is True

    def test_validate_high_min_prob_may_be_infeasible(self):
        validator = CraftFeasibilityValidator(n_runs=10, min_success_prob=1.1)
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg", "crit_chance"], {"phys_dmg": 5, "crit_chance": 5})
        result = validator.validate(candidate, assignment)
        assert result.feasible is False

    def test_validate_result_has_mean_fp_cost(self):
        candidate = make_candidate()
        assignment = make_assignment(["phys_dmg"], {"phys_dmg": 2})
        result = self.validator.validate(candidate, assignment)
        assert hasattr(result, "mean_fp_cost")
        assert result.mean_fp_cost >= 0.0

    def test_validate_result_has_reason(self):
        candidate = make_candidate()
        assignment = make_assignment([], {})
        result = self.validator.validate(candidate, assignment)
        assert isinstance(result.reason, str)
        assert len(result.reason) > 0

    def test_validate_batch_returns_one_per_candidate(self):
        candidates = [make_candidate(f"c{i}") for i in range(4)]
        assignment = make_assignment([], {})
        results = self.validator.validate_batch(candidates, assignment)
        assert len(results) == 4

    def test_validate_batch_returns_feasibility_result_instances(self):
        candidates = [make_candidate("x")]
        assignment = make_assignment([], {})
        results = self.validator.validate_batch(candidates, assignment)
        assert isinstance(results[0], FeasibilityResult)

    def test_validate_batch_candidate_ids_match(self):
        candidates = [make_candidate(f"bid_{i}") for i in range(3)]
        assignment = make_assignment([], {})
        results = self.validator.validate_batch(candidates, assignment)
        result_ids = {r.candidate_id for r in results}
        expected_ids = {c.candidate_id for c in candidates}
        assert result_ids == expected_ids
