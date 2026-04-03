"""Phase Q — BIS Search Engine performance tests.

All tests are marked @pytest.mark.slow and can be skipped with:
    pytest -m "not slow"
"""

from __future__ import annotations

import time
import threading

import pytest

from bis.models.item_slot import SlotPool, ItemSlot, SlotType
from bis.generator.item_candidate_generator import ItemCandidateGenerator, ItemCandidate
from bis.generator.affix_combination_generator import AffixCombinationGenerator
from bis.generator.tier_range_expander import TierRangeExpander, TierAssignment
from bis.integration.build_adapter import BuildAdapter, BuildSnapshot
from bis.scoring.build_score_engine import BuildScoreEngine, BuildScore
from bis.ranking.ranking_engine import RankingEngine
from bis.ranking.top_selector import TopSelector
from bis.engine.incremental_search import IncrementalSearchEngine
from bis.cache.search_cache import SearchCache
from bis.metrics.search_metrics import SearchMetricsCollector
from bis.engine.parallel_manager import ParallelManager, ParallelTask


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_score(build_id: str, total: float) -> BuildScore:
    return BuildScore(build_id, total, total, total, total, {"helm": total})


def _single_pool() -> SlotPool:
    return SlotPool.from_slot_types(["helm"])


def _two_slot_pool() -> SlotPool:
    return SlotPool.from_slot_types(["helm", "boots"])


# ---------------------------------------------------------------------------
# Generator performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestGeneratorPerformance:
    def test_item_candidate_generate_1000(self):
        gen = ItemCandidateGenerator()
        slot = ItemSlot(SlotType.HELM)
        t0 = time.perf_counter()
        candidates = gen.generate(slot, limit=1000)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
        assert len(candidates) > 0

    def test_affix_combo_generate_with_sizes(self):
        gen = AffixCombinationGenerator()
        t0 = time.perf_counter()
        combos = gen.generate_with_sizes(2, 4)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5
        assert len(combos) > 0

    def test_tier_range_expander_four_affixes(self):
        expander = TierRangeExpander()
        affixes = ["fire_res", "cold_res", "lightning_res", "life"]
        t0 = time.perf_counter()
        assignments = expander.expand(affixes)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5
        assert len(assignments) > 0

    def test_tier_range_top_assignment_fast(self):
        expander = TierRangeExpander()
        t0 = time.perf_counter()
        for _ in range(1000):
            expander.top_assignment(["fire_res", "cold_res"])
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0


# ---------------------------------------------------------------------------
# Search performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestSearchPerformance:
    def test_single_slot_search_completes_under_5s(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=10)
        t0 = time.perf_counter()
        result = engine.search(_single_pool(), [], {}, top_n=5)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0
        assert result.total_evaluated > 0

    def test_two_slot_search_completes_under_10s(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        t0 = time.perf_counter()
        result = engine.search(_two_slot_pool(), [], {}, top_n=3, max_candidates=50)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0
        assert result.total_evaluated > 0

    def test_search_with_max_candidates_100_under_3s(self):
        engine = IncrementalSearchEngine(n_runs_per_eval=5)
        t0 = time.perf_counter()
        result = engine.search(_single_pool(), [], {}, max_candidates=100)
        elapsed = time.perf_counter() - t0
        assert elapsed < 3.0


# ---------------------------------------------------------------------------
# Scoring performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestScoringPerformance:
    def test_rank_500_entries_under_0_5s(self):
        scores = [_make_score(f"b{i}", i / 500) for i in range(500)]
        ranker = RankingEngine()
        t0 = time.perf_counter()
        ranked = ranker.rank(scores)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5
        assert len(ranked) == 500

    def test_top_selector_1000_entries_under_0_1s(self):
        scores = [_make_score(f"b{i}", i / 1000) for i in range(1000)]
        sel = TopSelector()
        t0 = time.perf_counter()
        result = sel.select(scores, n=10)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.1
        assert len(result.entries) == 10

    def test_filter_by_score_500_entries_fast(self):
        scores = [_make_score(f"b{i}", i / 500) for i in range(500)]
        ranker = RankingEngine()
        ranked = ranker.rank(scores)
        t0 = time.perf_counter()
        filtered = ranker.filter_by_score(ranked, 0.5)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.1


# ---------------------------------------------------------------------------
# Cache performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestCachePerformance:
    def test_store_and_retrieve_1000_entries_under_0_5s(self):
        cache = SearchCache(max_size=2000)
        t0 = time.perf_counter()
        for i in range(1000):
            cache.set(f"k{i}", {"val": i})
        for i in range(1000):
            assert cache.get(f"k{i}") is not None
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_1000_cache_hits_under_0_1s(self):
        cache = SearchCache(max_size=100)
        cache.set("hot_key", {"data": "result"})
        t0 = time.perf_counter()
        for _ in range(1000):
            cache.get("hot_key")
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.1

    def test_eviction_under_load(self):
        cache = SearchCache(max_size=100)
        t0 = time.perf_counter()
        for i in range(10000):
            cache.set(f"k{i}", i)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0
        assert len(cache) <= 100


# ---------------------------------------------------------------------------
# ParallelManager performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestParallelManagerPerformance:
    def test_20_tasks_sleep_0_01_under_2s(self):
        mgr = ParallelManager(max_workers=8)
        tasks = [ParallelTask(f"t{i}", lambda: time.sleep(0.01)) for i in range(20)]
        t0 = time.perf_counter()
        results = mgr.run(tasks)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0
        assert len(results) == 20

    def test_50_trivial_tasks_under_3s(self):
        mgr = ParallelManager(max_workers=8)
        tasks = [ParallelTask(f"t{i}", lambda x=i: x * 2) for i in range(50)]
        t0 = time.perf_counter()
        results = mgr.run(tasks)
        elapsed = time.perf_counter() - t0
        assert elapsed < 3.0
        assert all(r.error is None for r in results)


# ---------------------------------------------------------------------------
# Metrics performance
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestMetricsPerformance:
    def test_10000_record_evaluated_under_0_5s(self):
        col = SearchMetricsCollector()
        t0 = time.perf_counter()
        for _ in range(10000):
            col.record_evaluated(1)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5
        assert col.collect().total_candidates_evaluated == 10000

    def test_mixed_operations_10000_under_1s(self):
        col = SearchMetricsCollector()
        t0 = time.perf_counter()
        for i in range(10000):
            if i % 3 == 0:
                col.record_evaluated()
            elif i % 3 == 1:
                col.record_pruned()
            else:
                col.record_cache_hit()
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
