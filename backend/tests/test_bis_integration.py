"""Phase Q — BIS Search Engine integration tests."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from bis.models.item_slot import SlotPool, SlotType, ItemSlot
from bis.generator.item_candidate_generator import ItemCandidateGenerator, ItemCandidate
from bis.generator.tier_range_expander import TierRangeExpander, TierAssignment
from bis.integration.build_adapter import BuildAdapter, BuildSnapshot
from bis.scoring.build_score_engine import BuildScoreEngine, BuildScore
from bis.ranking.ranking_engine import RankingEngine
from bis.ranking.top_selector import TopSelector
from bis.models.bis_result import BisResult
from bis.engine.incremental_search import IncrementalSearchEngine, SearchStage
from bis.cache.search_cache import SearchCache
from bis.metrics.search_metrics import SearchMetricsCollector
from bis.integration.craft_adapter import CraftAdapter
from bis.validation.craft_feasibility import CraftFeasibilityValidator, FeasibilityResult
from bis.engine.parallel_manager import ParallelManager, ParallelTask
from debug.bis_search_logger import BisSearchLogger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_score(build_id: str, total: float, slot: str = "helm") -> BuildScore:
    return BuildScore(
        build_id=build_id,
        total_score=total,
        tier_score=total,
        coverage_score=total,
        fp_score=total,
        slot_scores={slot: total},
    )


def _single_slot_pool() -> SlotPool:
    return SlotPool.from_slot_types(["helm"])


def _two_slot_pool() -> SlotPool:
    return SlotPool.from_slot_types(["helm", "boots"])


def _make_candidate(cid="c1", fp=80) -> ItemCandidate:
    return ItemCandidate(
        candidate_id=cid,
        item_class="helm",
        slot_type="helm",
        base_name="Iron Helm",
        forging_potential=fp,
    )


def _make_assignment(affix: str = "fire_res", tier: int = 3) -> TierAssignment:
    return TierAssignment({affix: tier}, tier)


# ---------------------------------------------------------------------------
# IncrementalSearchEngine integration
# ---------------------------------------------------------------------------

class TestIncrementalSearchIntegration:
    def test_single_slot_returns_bis_result(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, top_n=3, max_candidates=10)
        assert isinstance(result, BisResult)

    def test_total_evaluated_positive(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, top_n=3, max_candidates=10)
        assert result.total_evaluated > 0

    def test_search_duration_non_negative(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, top_n=3, max_candidates=10)
        assert result.search_duration_s >= 0

    def test_top_entries_bounded_by_n(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, top_n=2, max_candidates=10)
        assert len(result.top_entries) <= 2

    def test_stages_populated(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        engine.search(_single_slot_pool(), [], {}, top_n=3, max_candidates=9)
        assert len(engine._stages) > 0

    def test_stages_have_required_fields(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        engine.search(_single_slot_pool(), [], {}, top_n=3, max_candidates=9)
        stage = engine._stages[0]
        assert hasattr(stage, "stage_id")
        assert hasattr(stage, "candidates_evaluated")
        assert hasattr(stage, "best_score")
        assert hasattr(stage, "elapsed_s")

    def test_two_slot_search_completes(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_two_slot_pool(), [], {}, top_n=3, max_candidates=15)
        assert isinstance(result, BisResult)
        assert result.total_evaluated > 0

    def test_max_candidates_respected(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, max_candidates=2)
        assert result.total_evaluated <= 2

    def test_bis_result_has_search_id(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {})
        assert result.search_id.startswith("search_")

    def test_summary_keys(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {})
        s = result.summary()
        for key in ("search_id", "total_evaluated", "results_count", "best_score", "duration_s"):
            assert key in s

    def test_best_is_highest_scored_entry(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        result = engine.search(_single_slot_pool(), [], {}, top_n=5, max_candidates=9)
        if len(result.top_entries) >= 2:
            assert result.top_entries[0].score.total_score >= result.top_entries[1].score.total_score

    def test_no_slots_gives_empty_result(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        pool = SlotPool([])
        result = engine.search(pool, [], {}, top_n=3)
        assert result.total_evaluated == 0


# ---------------------------------------------------------------------------
# SearchCache integration
# ---------------------------------------------------------------------------

class TestSearchCacheIntegration:
    def test_cache_miss_returns_none(self):
        cache = SearchCache(max_size=10)
        assert cache.get("missing_key") is None

    def test_cache_hit_after_set(self):
        cache = SearchCache(max_size=10)
        obj = {"data": 42}
        cache.set("key1", obj)
        assert cache.get("key1") is obj

    def test_zero_ttl_never_expires(self):
        cache = SearchCache(max_size=10, default_ttl=0)
        cache.set("k", "val")
        assert cache.get("k") == "val"

    def test_capacity_eviction(self):
        cache = SearchCache(max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # evicts "a" (LRU/FIFO)
        assert cache.get("a") is None
        assert cache.get("d") == 4

    def test_stats_has_size_key(self):
        cache = SearchCache(max_size=10)
        cache.set("k", "v")
        s = cache.stats()
        assert "size" in s
        assert s["size"] == 1

    def test_invalidate_removes_entry(self):
        cache = SearchCache(max_size=10)
        cache.set("k", "v")
        assert cache.invalidate("k") is True
        assert cache.get("k") is None

    def test_invalidate_missing_returns_false(self):
        cache = SearchCache(max_size=10)
        assert cache.invalidate("nope") is False

    def test_ttl_expiry(self):
        cache = SearchCache(max_size=10)
        cache.set("k", "v", ttl=1.0)
        with patch("bis.cache.search_cache.time.time", return_value=time.time() + 10):
            assert cache.get("k") is None

    def test_clear_empties_cache(self):
        cache = SearchCache(max_size=10)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_len_reflects_stored_items(self):
        cache = SearchCache(max_size=10)
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2


# ---------------------------------------------------------------------------
# ParallelManager integration
# ---------------------------------------------------------------------------

class TestParallelManagerIntegration:
    def test_five_tasks_all_succeed(self):
        mgr = ParallelManager(max_workers=4)
        tasks = [ParallelTask(f"t{i}", lambda x=i: x * 2) for i in range(5)]
        results = mgr.run(tasks)
        assert len(results) == 5
        assert all(r.error is None for r in results)

    def test_failed_task_recorded_not_raised(self):
        def boom():
            raise ValueError("fail")
        mgr = ParallelManager(max_workers=2)
        tasks = [ParallelTask("bad", boom)]
        results = mgr.run(tasks)
        assert len(results) == 1
        assert results[0].error is not None

    def test_duration_ms_non_negative(self):
        mgr = ParallelManager(max_workers=2)
        tasks = [ParallelTask("t0", lambda: 42)]
        results = mgr.run(tasks)
        assert results[0].duration_ms >= 0

    def test_run_batch_chunks_items(self):
        mgr = ParallelManager(max_workers=2)
        items = list(range(25))
        results = mgr.run_batch(lambda chunk: sum(chunk), items, chunk_size=10)
        assert len(results) == 3  # ceil(25/10) = 3 chunks

    def test_task_result_stored(self):
        mgr = ParallelManager(max_workers=2)
        tasks = [ParallelTask("t", lambda: 99)]
        results = mgr.run(tasks)
        assert results[0].result == 99


# ---------------------------------------------------------------------------
# BuildScoreEngine + RankingEngine integration
# ---------------------------------------------------------------------------

class TestScoringRankingIntegration:
    def _make_scores(self, n: int) -> list[BuildScore]:
        return [_make_score(f"b{i}", (i + 1) / n) for i in range(n)]

    def test_rank1_highest_score(self):
        scores = self._make_scores(5)
        ranked = RankingEngine().rank(scores)
        assert ranked[0].rank == 1
        assert ranked[0].score.total_score == max(s.total_score for s in scores)

    def test_entries_sorted_descending(self):
        scores = self._make_scores(5)
        ranked = RankingEngine().rank(scores)
        for i in range(len(ranked) - 1):
            assert ranked[i].score.total_score >= ranked[i + 1].score.total_score

    def test_percentile_rank1_is_100(self):
        scores = self._make_scores(1)
        ranked = RankingEngine().rank(scores)
        assert ranked[0].percentile == 100.0

    def test_filter_by_score_zero_returns_all(self):
        scores = self._make_scores(5)
        ranker = RankingEngine()
        ranked = ranker.rank(scores)
        filtered = ranker.filter_by_score(ranked, 0.0)
        assert len(filtered) == len(ranked)

    def test_rank_by_slot_returns_all_entries(self):
        scores = self._make_scores(5)
        by_slot = RankingEngine().rank_by_slot(scores, "helm")
        assert len(by_slot) == 5

    def test_top_selector_limits_n(self):
        scores = self._make_scores(10)
        result = TopSelector().select(scores, n=3)
        assert len(result.entries) == 3

    def test_top_selector_score_range_hi_gte_lo(self):
        scores = self._make_scores(5)
        result = TopSelector().select(scores, n=5)
        lo, hi = result.score_range
        assert hi >= lo

    def test_top_selector_total_evaluated(self):
        scores = self._make_scores(7)
        result = TopSelector().select(scores, n=3)
        assert result.total_evaluated == 7


# ---------------------------------------------------------------------------
# SearchMetricsCollector integration
# ---------------------------------------------------------------------------

class TestSearchMetricsIntegration:
    def test_start_stop_records_duration(self):
        col = SearchMetricsCollector()
        col.start()
        time.sleep(0.01)
        col.stop()
        m = col.collect()
        assert m.search_duration_s >= 0.01

    def test_record_evaluated_accumulates(self):
        col = SearchMetricsCollector()
        col.record_evaluated(10)
        col.record_evaluated(5)
        assert col.collect().total_candidates_evaluated == 15

    def test_record_pruned_accumulates(self):
        col = SearchMetricsCollector()
        col.record_pruned(3)
        col.record_pruned(7)
        assert col.collect().total_pruned == 10

    def test_cache_hit_miss_counts(self):
        col = SearchMetricsCollector()
        col.record_cache_hit()
        col.record_cache_hit()
        col.record_cache_miss()
        m = col.collect()
        assert m.cache_hits == 2
        assert m.cache_misses == 1

    def test_cache_hit_rate_half(self):
        col = SearchMetricsCollector()
        col.record_cache_hit()
        col.record_cache_miss()
        assert abs(col.collect().cache_hit_rate - 0.5) < 1e-9

    def test_reset_zeros_counters(self):
        col = SearchMetricsCollector()
        col.record_evaluated(100)
        col.record_pruned(50)
        col.reset()
        m = col.collect()
        assert m.total_candidates_evaluated == 0
        assert m.total_pruned == 0


# ---------------------------------------------------------------------------
# BisSearchLogger integration
# ---------------------------------------------------------------------------

class TestBisSearchLoggerIntegration:
    def test_log_and_retrieve_five_entries(self):
        logger = BisSearchLogger()
        for i in range(5):
            logger.log_candidate_evaluated(f"s{i}", f"c{i}", 0.5)
        assert len(logger.get_entries()) == 5

    def test_filter_by_event_type(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 1)
        logger.log_candidate_evaluated("s1", "c1", 0.9)
        starts = logger.get_entries(event_type="search_start")
        assert len(starts) == 1
        assert starts[0].event_type == "search_start"

    def test_filter_by_search_id(self):
        logger = BisSearchLogger()
        logger.log_candidate_evaluated("s1", "c1", 0.5)
        logger.log_candidate_evaluated("s2", "c2", 0.7)
        results = logger.get_entries(search_id="s1")
        assert all(e.search_id == "s1" for e in results)

    def test_summary_returns_dict(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 1)
        logger.log_search_complete("s1", 10, 0.8, 0.5)
        s = logger.summary()
        assert isinstance(s, dict)
        assert len(s) > 0

    def test_clear_resets_entries(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 1)
        logger.clear()
        assert len(logger.get_entries()) == 0

    def test_capacity_overflow_drops_oldest(self):
        logger = BisSearchLogger(capacity=5)
        for i in range(10):
            logger.log_candidate_evaluated("s", f"c{i}", 0.1 * i)
        entries = logger.get_entries()
        assert len(entries) == 5
        ids = [e.data["candidate_id"] for e in entries]
        assert "c9" in ids

    def test_len_returns_count(self):
        logger = BisSearchLogger()
        logger.log_search_start("s1", [], 1)
        logger.log_search_start("s2", [], 2)
        assert len(logger) == 2


# ---------------------------------------------------------------------------
# CraftFeasibilityValidator + CraftAdapter integration
# ---------------------------------------------------------------------------

class TestCraftFeasibilityIntegration:
    def test_validate_returns_feasibility_result(self):
        validator = CraftFeasibilityValidator(n_runs=5, min_success_prob=0.0)
        result = validator.validate(_make_candidate(), _make_assignment())
        assert isinstance(result, FeasibilityResult)

    def test_zero_min_prob_is_feasible(self):
        validator = CraftFeasibilityValidator(n_runs=5, min_success_prob=0.0)
        result = validator.validate(_make_candidate(), _make_assignment())
        assert result.feasible is True

    def test_impossible_min_prob_not_feasible(self):
        validator = CraftFeasibilityValidator(n_runs=5, min_success_prob=1.1)
        result = validator.validate(_make_candidate(), _make_assignment())
        assert result.feasible is False

    def test_batch_validate_returns_correct_count(self):
        validator = CraftFeasibilityValidator(n_runs=5, min_success_prob=0.0)
        candidates = [_make_candidate(f"c{i}", 60 + i * 10) for i in range(3)]
        results = validator.validate_batch(candidates, _make_assignment())
        assert len(results) == 3

    def test_craft_adapter_evaluate_returns_result(self):
        from bis.integration.craft_adapter import CraftAdapterResult
        adapter = CraftAdapter(n_runs=5, min_prob=0.0)
        result = adapter.evaluate(_make_candidate(), _make_assignment())
        assert isinstance(result, CraftAdapterResult)
        assert result.candidate_id == "c1"

    def test_craft_adapter_filter_feasible(self):
        adapter = CraftAdapter(n_runs=5, min_prob=0.0)
        pairs = [(_make_candidate(f"c{i}"), _make_assignment()) for i in range(3)]
        results = adapter.evaluate_batch(pairs)
        feasible = adapter.filter_feasible(results)
        assert all(r.feasibility.feasible for r in feasible)

    def test_craft_adapter_infeasible_reduces_tiers(self):
        adapter = CraftAdapter(n_runs=5, min_prob=1.1)
        result = adapter.evaluate(_make_candidate(), _make_assignment("fire_res", 3))
        assert result.adjusted_tiers.get("fire_res", 3) <= 3
