"""
Tests for Phase Q BIS Search Engine: MetricWeights, RankingEngine, TopSelector,
BisResult, SearchCache, SearchMetricsCollector.

Run from backend/:
    python -m pytest tests/test_bis_ranking_cache.py -v --tb=short
"""

import time
from unittest.mock import patch

import pytest

from bis.scoring.metric_weights import (
    MetricWeights,
    BALANCED,
    TIER_FOCUSED,
    COVERAGE_FOCUSED,
)
from bis.ranking.ranking_engine import RankedEntry, RankingEngine
from bis.ranking.top_selector import TopNResult, TopSelector
from bis.models.bis_result import BisResult
from bis.cache.search_cache import SearchCache, SearchCacheEntry
from bis.metrics.search_metrics import SearchMetrics, SearchMetricsCollector
from bis.scoring.build_score_engine import BuildScore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_score(build_id: str, total: float) -> BuildScore:
    return BuildScore(build_id, total, 0.5, 0.5, 0.5, {})


def make_score_with_slots(build_id: str, total: float, slot_scores: dict) -> BuildScore:
    return BuildScore(build_id, total, 0.5, 0.5, 0.5, slot_scores)


def make_ranked(build_id: str, total: float, rank: int = 1) -> RankedEntry:
    return RankedEntry(rank, build_id, make_score(build_id, total), 100.0)


# ===========================================================================
# MetricWeights tests (12 tests)
# ===========================================================================

class TestMetricWeightsValidate:
    def test_default_validates_true(self):
        w = MetricWeights()
        assert w.validate() is True

    def test_sum_exactly_one_is_valid(self):
        w = MetricWeights(0.25, 0.25, 0.25, 0.25)
        assert w.validate() is True

    def test_sum_not_one_is_invalid(self):
        w = MetricWeights(0.5, 0.5, 0.5, 0.5)
        assert w.validate() is False

    def test_sum_less_than_one_is_invalid(self):
        w = MetricWeights(0.1, 0.1, 0.1, 0.1)
        assert w.validate() is False

    def test_zero_weights_invalid(self):
        w = MetricWeights(0.0, 0.0, 0.0, 0.0)
        assert w.validate() is False


class TestMetricWeightsNormalize:
    def test_normalize_sums_to_one(self):
        w = MetricWeights(1.0, 1.0, 1.0, 1.0)
        n = w.normalize()
        total = n.tier_weight + n.coverage_weight + n.fp_efficiency_weight + n.feasibility_weight
        assert abs(total - 1.0) < 1e-6

    def test_normalize_already_valid_unchanged(self):
        w = MetricWeights(0.4, 0.3, 0.15, 0.15)
        n = w.normalize()
        assert abs(n.tier_weight - 0.4) < 1e-6

    def test_normalize_zero_returns_default(self):
        w = MetricWeights(0.0, 0.0, 0.0, 0.0)
        n = w.normalize()
        # Should return default MetricWeights() which sums to 1
        assert n.validate() is True

    def test_normalize_returns_metric_weights_instance(self):
        w = MetricWeights(2.0, 1.0, 0.5, 0.5)
        n = w.normalize()
        assert isinstance(n, MetricWeights)


class TestMetricWeightsToDict:
    def test_to_dict_has_correct_keys(self):
        w = MetricWeights()
        d = w.to_dict()
        assert set(d.keys()) == {"tier", "coverage", "fp", "feasibility"}

    def test_to_dict_values_match_weights(self):
        w = MetricWeights(0.4, 0.3, 0.15, 0.15)
        d = w.to_dict()
        assert d["tier"] == 0.4
        assert d["coverage"] == 0.3
        assert d["fp"] == 0.15
        assert d["feasibility"] == 0.15

    def test_to_dict_returns_dict(self):
        w = MetricWeights()
        assert isinstance(w.to_dict(), dict)


class TestPresetWeights:
    def test_balanced_is_valid(self):
        assert BALANCED.validate() is True

    def test_tier_focused_is_valid(self):
        assert TIER_FOCUSED.validate() is True

    def test_coverage_focused_is_valid(self):
        assert COVERAGE_FOCUSED.validate() is True

    def test_tier_focused_has_highest_tier_weight(self):
        assert TIER_FOCUSED.tier_weight > BALANCED.tier_weight

    def test_coverage_focused_has_highest_coverage_weight(self):
        assert COVERAGE_FOCUSED.coverage_weight > BALANCED.coverage_weight


# ===========================================================================
# RankingEngine tests (12 tests)
# ===========================================================================

class TestRankingEngineRank:
    def setup_method(self):
        self.engine = RankingEngine()

    def test_rank_sorted_descending_by_total_score(self):
        scores = [make_score("a", 0.3), make_score("b", 0.8), make_score("c", 0.5)]
        ranked = self.engine.rank(scores)
        assert ranked[0].score.total_score >= ranked[1].score.total_score
        assert ranked[1].score.total_score >= ranked[2].score.total_score

    def test_rank_first_entry_has_rank_one(self):
        scores = [make_score("a", 0.5), make_score("b", 0.9)]
        ranked = self.engine.rank(scores)
        assert ranked[0].rank == 1

    def test_rank_all_entries_have_sequential_ranks(self):
        scores = [make_score(str(i), i * 0.1) for i in range(5)]
        ranked = self.engine.rank(scores)
        for idx, entry in enumerate(ranked):
            assert entry.rank == idx + 1

    def test_rank_empty_returns_empty_list(self):
        assert self.engine.rank([]) == []

    def test_rank_single_entry_rank_one(self):
        scores = [make_score("only", 0.7)]
        ranked = self.engine.rank(scores)
        assert len(ranked) == 1
        assert ranked[0].rank == 1

    def test_rank_single_entry_percentile_100(self):
        scores = [make_score("only", 0.7)]
        ranked = self.engine.rank(scores)
        assert ranked[0].percentile == 100.0

    def test_rank_returns_ranked_entry_objects(self):
        scores = [make_score("a", 0.5)]
        ranked = self.engine.rank(scores)
        assert isinstance(ranked[0], RankedEntry)

    def test_rank_percentile_between_0_and_100(self):
        scores = [make_score(str(i), i * 0.1) for i in range(1, 6)]
        ranked = self.engine.rank(scores)
        for entry in ranked:
            assert 0.0 <= entry.percentile <= 100.0

    def test_rank_top_has_highest_percentile(self):
        scores = [make_score("a", 0.3), make_score("b", 0.9), make_score("c", 0.6)]
        ranked = self.engine.rank(scores)
        assert ranked[0].percentile >= ranked[-1].percentile


class TestRankingEngineTopN:
    def setup_method(self):
        self.engine = RankingEngine()

    def test_top_n_returns_n_entries(self):
        scores = [make_score(str(i), i * 0.1) for i in range(10)]
        result = self.engine.top_n(scores, 5)
        assert len(result) == 5

    def test_top_n_fewer_than_n_returns_all(self):
        scores = [make_score("a", 0.5), make_score("b", 0.3)]
        result = self.engine.top_n(scores, 10)
        assert len(result) == 2

    def test_top_n_first_is_best(self):
        scores = [make_score("low", 0.1), make_score("high", 0.9)]
        result = self.engine.top_n(scores, 1)
        assert result[0].score.total_score == 0.9


class TestRankingEngineFilterByScore:
    def setup_method(self):
        self.engine = RankingEngine()

    def test_filter_removes_entries_below_threshold(self):
        scores = [make_score("a", 0.3), make_score("b", 0.8), make_score("c", 0.5)]
        ranked = self.engine.rank(scores)
        filtered = self.engine.filter_by_score(ranked, 0.5)
        assert all(r.score.total_score >= 0.5 for r in filtered)

    def test_filter_zero_threshold_returns_all(self):
        scores = [make_score(str(i), i * 0.1) for i in range(5)]
        ranked = self.engine.rank(scores)
        filtered = self.engine.filter_by_score(ranked, 0.0)
        assert len(filtered) == 5

    def test_filter_threshold_above_all_returns_empty(self):
        scores = [make_score("a", 0.3)]
        ranked = self.engine.rank(scores)
        filtered = self.engine.filter_by_score(ranked, 0.9)
        assert filtered == []


class TestRankingEngineRankBySlot:
    def setup_method(self):
        self.engine = RankingEngine()

    def test_rank_by_slot_sorted_by_slot_score(self):
        scores = [
            make_score_with_slots("a", 0.5, {"helm": 0.2}),
            make_score_with_slots("b", 0.3, {"helm": 0.9}),
            make_score_with_slots("c", 0.7, {"helm": 0.5}),
        ]
        ranked = self.engine.rank_by_slot(scores, "helm")
        helm_scores = [r.score.slot_scores.get("helm", 0.0) for r in ranked]
        assert helm_scores == sorted(helm_scores, reverse=True)

    def test_rank_by_slot_first_entry_rank_one(self):
        scores = [make_score_with_slots("a", 0.5, {"boots": 0.7})]
        ranked = self.engine.rank_by_slot(scores, "boots")
        assert ranked[0].rank == 1

    def test_rank_by_slot_missing_slot_defaults_to_zero(self):
        scores = [make_score("a", 0.5), make_score("b", 0.8)]
        ranked = self.engine.rank_by_slot(scores, "nonexistent_slot")
        assert len(ranked) == 2


# ===========================================================================
# TopSelector tests (12 tests)
# ===========================================================================

class TestTopSelectorSelect:
    def setup_method(self):
        self.selector = TopSelector()

    def test_select_returns_top_n_result(self):
        scores = [make_score(str(i), i * 0.1) for i in range(10)]
        result = self.selector.select(scores, n=5)
        assert isinstance(result, TopNResult)

    def test_select_result_has_correct_n(self):
        scores = [make_score(str(i), i * 0.1) for i in range(10)]
        result = self.selector.select(scores, n=5)
        assert result.top_n == 5

    def test_select_entries_limited_to_n(self):
        scores = [make_score(str(i), i * 0.1) for i in range(10)]
        result = self.selector.select(scores, n=3)
        assert len(result.entries) == 3

    def test_select_score_range_min_le_max(self):
        scores = [make_score(str(i), i * 0.1) for i in range(1, 6)]
        result = self.selector.select(scores, n=5)
        assert result.score_range[0] <= result.score_range[1]

    def test_select_score_range_max_is_best_entry(self):
        scores = [make_score("a", 0.3), make_score("b", 0.8), make_score("c", 0.5)]
        result = self.selector.select(scores, n=3)
        assert result.score_range[1] == 0.8

    def test_select_score_range_zero_when_empty(self):
        result = self.selector.select([], n=5)
        assert result.score_range == (0.0, 0.0)

    def test_select_total_evaluated_equals_input_length(self):
        scores = [make_score(str(i), i * 0.1) for i in range(7)]
        result = self.selector.select(scores, n=3)
        assert result.total_evaluated == 7

    def test_select_min_score_excludes_low_scores(self):
        scores = [make_score("a", 0.1), make_score("b", 0.5), make_score("c", 0.9)]
        result = self.selector.select(scores, n=5, min_score=0.4)
        for entry in result.entries:
            assert entry.score.total_score >= 0.4

    def test_select_min_score_all_filtered_empty_entries(self):
        scores = [make_score("a", 0.1), make_score("b", 0.2)]
        result = self.selector.select(scores, n=5, min_score=0.9)
        assert result.entries == []

    def test_select_returns_fewer_when_not_enough(self):
        scores = [make_score("a", 0.5)]
        result = self.selector.select(scores, n=10)
        assert len(result.entries) == 1


class TestTopSelectorSelectPerSlot:
    def setup_method(self):
        self.selector = TopSelector()

    def test_select_per_slot_returns_top_n_result(self):
        scores = [make_score_with_slots(str(i), 0.5, {"helm": i * 0.1}) for i in range(5)]
        result = self.selector.select_per_slot(scores, "helm", n=3)
        assert isinstance(result, TopNResult)

    def test_select_per_slot_limits_entries(self):
        scores = [make_score_with_slots(str(i), 0.5, {"helm": i * 0.1}) for i in range(10)]
        result = self.selector.select_per_slot(scores, "helm", n=4)
        assert len(result.entries) <= 4

    def test_select_per_slot_total_evaluated_correct(self):
        scores = [make_score_with_slots(str(i), 0.5, {"helm": 0.5}) for i in range(6)]
        result = self.selector.select_per_slot(scores, "helm")
        assert result.total_evaluated == 6


# ===========================================================================
# BisResult tests (10 tests)
# ===========================================================================

class TestBisResult:
    def _make_result(self, entries, search_id="s1"):
        return BisResult(
            search_id=search_id,
            top_entries=entries,
            total_evaluated=len(entries),
            search_duration_s=0.5,
            target_affixes=["affix_a"],
            target_tiers={"affix_a": 5},
        )

    def test_best_returns_first_entry(self):
        entries = [make_ranked("a", 0.9, 1), make_ranked("b", 0.5, 2)]
        result = self._make_result(entries)
        assert result.best is entries[0]

    def test_best_none_when_empty(self):
        result = self._make_result([])
        assert result.best is None

    def test_best_score_correct_value(self):
        entries = [make_ranked("a", 0.85, 1)]
        result = self._make_result(entries)
        assert result.best_score == 0.85

    def test_best_score_zero_when_empty(self):
        result = self._make_result([])
        assert result.best_score == 0.0

    def test_summary_has_all_required_keys(self):
        entries = [make_ranked("a", 0.7, 1)]
        result = self._make_result(entries)
        s = result.summary()
        for key in ("search_id", "total_evaluated", "results_count", "best_score", "duration_s", "target_affixes"):
            assert key in s

    def test_summary_best_score_matches_best(self):
        entries = [make_ranked("a", 0.75, 1)]
        result = self._make_result(entries)
        s = result.summary()
        assert s["best_score"] == result.best_score

    def test_summary_results_count_matches_entries(self):
        entries = [make_ranked(str(i), 0.5, i + 1) for i in range(3)]
        result = self._make_result(entries)
        assert result.summary()["results_count"] == 3

    def test_summary_search_id_matches(self):
        result = self._make_result([], search_id="mysearch")
        assert result.summary()["search_id"] == "mysearch"

    def test_summary_total_evaluated_correct(self):
        result = BisResult(
            search_id="x",
            top_entries=[],
            total_evaluated=42,
            search_duration_s=1.0,
            target_affixes=[],
            target_tiers={},
        )
        assert result.summary()["total_evaluated"] == 42

    def test_created_at_is_float(self):
        result = self._make_result([])
        assert isinstance(result.created_at, float)


# ===========================================================================
# SearchCache tests (15 tests)
# ===========================================================================

class TestSearchCacheGet:
    def test_get_returns_none_for_missing_key(self):
        cache = SearchCache()
        assert cache.get("nonexistent") is None

    def test_set_then_get_returns_data(self):
        cache = SearchCache()
        cache.set("key1", {"data": 42})
        assert cache.get("key1") == {"data": 42}

    def test_get_increments_hit_count(self):
        cache = SearchCache()
        cache.set("k", "value")
        cache.get("k")
        cache.get("k")
        entry = cache._cache["k"]
        assert entry.hit_count == 2

    def test_ttl_expiry_returns_none(self):
        cache = SearchCache(default_ttl=1.0)
        cache.set("k", "value", ttl=1.0)
        with patch("bis.cache.search_cache.time.time", return_value=time.time() + 1000):
            assert cache.get("k") is None

    def test_zero_ttl_never_expires(self):
        cache = SearchCache()
        cache.set("k", "value", ttl=0.0)
        with patch("bis.cache.search_cache.time.time", return_value=time.time() + 99999):
            assert cache.get("k") == "value"


class TestSearchCacheEviction:
    def test_eviction_at_max_size(self):
        cache = SearchCache(max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # should evict "a"
        assert len(cache) == 3

    def test_eviction_removes_oldest_entry(self):
        cache = SearchCache(max_size=2)
        cache.set("first", "x")
        cache.set("second", "y")
        cache.set("third", "z")  # evicts "first"
        assert cache.get("first") is None
        assert cache.get("third") == "z"

    def test_update_existing_key_no_eviction(self):
        cache = SearchCache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("a", 99)  # update existing, should not evict
        assert len(cache) == 2


class TestSearchCacheInvalidate:
    def test_invalidate_returns_true_if_existed(self):
        cache = SearchCache()
        cache.set("key", "val")
        assert cache.invalidate("key") is True

    def test_invalidate_returns_false_if_not_existed(self):
        cache = SearchCache()
        assert cache.invalidate("missing") is False

    def test_invalidate_removes_entry(self):
        cache = SearchCache()
        cache.set("key", "val")
        cache.invalidate("key")
        assert cache.get("key") is None


class TestSearchCacheClearStats:
    def test_clear_empties_cache(self):
        cache = SearchCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_stats_returns_correct_size(self):
        cache = SearchCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.stats()["size"] == 2

    def test_stats_expired_count(self):
        cache = SearchCache()
        cache.set("k", "v", ttl=1.0)
        with patch("bis.cache.search_cache.time.time", return_value=time.time() + 1000):
            stats = cache.stats()
        assert stats["expired"] == 1

    def test_stats_total_hits_accumulates(self):
        cache = SearchCache()
        cache.set("k", "v")
        cache.get("k")
        cache.get("k")
        cache.get("k")
        assert cache.stats()["total_hits"] == 3

    def test_len_correct(self):
        cache = SearchCache()
        cache.set("x", 1)
        cache.set("y", 2)
        assert len(cache) == 2


# ===========================================================================
# SearchMetricsCollector tests (15 tests)
# ===========================================================================

class TestSearchMetricsCollectorBasics:
    def test_start_stop_sets_timing(self):
        collector = SearchMetricsCollector()
        collector.start()
        time.sleep(0.01)
        collector.stop()
        metrics = collector.collect()
        assert metrics.search_duration_s > 0

    def test_record_evaluated_increments(self):
        collector = SearchMetricsCollector()
        collector.record_evaluated(5)
        metrics = collector.collect()
        assert metrics.total_candidates_evaluated == 5

    def test_record_evaluated_multiple_times(self):
        collector = SearchMetricsCollector()
        collector.record_evaluated(3)
        collector.record_evaluated(7)
        metrics = collector.collect()
        assert metrics.total_candidates_evaluated == 10

    def test_record_pruned_increments(self):
        collector = SearchMetricsCollector()
        collector.record_pruned(4)
        metrics = collector.collect()
        assert metrics.total_pruned == 4

    def test_record_cache_hit_increments(self):
        collector = SearchMetricsCollector()
        collector.record_cache_hit()
        collector.record_cache_hit()
        metrics = collector.collect()
        assert metrics.cache_hits == 2

    def test_record_cache_miss_increments(self):
        collector = SearchMetricsCollector()
        collector.record_cache_miss()
        metrics = collector.collect()
        assert metrics.cache_misses == 1


class TestSearchMetricsCollectorRates:
    def test_candidates_per_second_positive_after_evaluation(self):
        collector = SearchMetricsCollector()
        collector.start()
        time.sleep(0.01)
        collector.record_evaluated(100)
        collector.stop()
        metrics = collector.collect()
        assert metrics.candidates_per_second > 0

    def test_prune_rate_correct_formula(self):
        collector = SearchMetricsCollector()
        collector.record_evaluated(6)
        collector.record_pruned(4)
        metrics = collector.collect()
        expected = 4 / (6 + 4)
        assert abs(metrics.prune_rate - expected) < 1e-6

    def test_prune_rate_zero_when_no_pruning(self):
        collector = SearchMetricsCollector()
        collector.record_evaluated(5)
        metrics = collector.collect()
        assert metrics.prune_rate == 0.0

    def test_cache_hit_rate_correct_formula(self):
        collector = SearchMetricsCollector()
        collector.record_cache_hit()
        collector.record_cache_hit()
        collector.record_cache_miss()
        metrics = collector.collect()
        expected = 2 / 3
        assert abs(metrics.cache_hit_rate - expected) < 1e-6

    def test_cache_hit_rate_zero_when_no_cache_activity(self):
        collector = SearchMetricsCollector()
        metrics = collector.collect()
        assert metrics.cache_hit_rate == 0.0

    def test_cache_hit_rate_one_when_all_hits(self):
        collector = SearchMetricsCollector()
        collector.record_cache_hit()
        collector.record_cache_hit()
        metrics = collector.collect()
        assert metrics.cache_hit_rate == 1.0

    def test_prune_rate_one_when_all_pruned(self):
        collector = SearchMetricsCollector()
        collector.record_pruned(10)
        metrics = collector.collect()
        assert metrics.prune_rate == 1.0


class TestSearchMetricsCollectorReset:
    def test_reset_zeroes_evaluated(self):
        collector = SearchMetricsCollector()
        collector.record_evaluated(10)
        collector.reset()
        metrics = collector.collect()
        assert metrics.total_candidates_evaluated == 0

    def test_reset_zeroes_pruned(self):
        collector = SearchMetricsCollector()
        collector.record_pruned(5)
        collector.reset()
        metrics = collector.collect()
        assert metrics.total_pruned == 0

    def test_reset_zeroes_cache_hits(self):
        collector = SearchMetricsCollector()
        collector.record_cache_hit()
        collector.reset()
        metrics = collector.collect()
        assert metrics.cache_hits == 0

    def test_reset_zeroes_cache_misses(self):
        collector = SearchMetricsCollector()
        collector.record_cache_miss()
        collector.reset()
        metrics = collector.collect()
        assert metrics.cache_misses == 0

    def test_collect_returns_search_metrics_instance(self):
        collector = SearchMetricsCollector()
        assert isinstance(collector.collect(), SearchMetrics)
