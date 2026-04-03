"""
Unit tests for VisualCache, ReportGenerator, and ComparisonDatasetBuilder.
Target: 45+ tests
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from visualization.cache.visual_cache import CacheEntry, VisualCache
from visualization.reports.report_generator import Report, ReportGenerator, ReportSection
from visualization.comparison.comparison_dataset_builder import (
    BuildMetricSnapshot,
    ComparisonDataset,
    ComparisonDatasetBuilder,
)
from visualization.metrics.metric_summary import (
    BuffUptimeSummary,
    DpsBreakdown,
    MetricSummary,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snapshot(
    build_id: str = "b1",
    label: str = "Build 1",
    total_damage: float = 10_000.0,
    dps: float = 1_000.0,
    crit_rate: float = 0.3,
    buff_uptime_pct: float = 0.8,
    kill_time: float | None = 30.0,
    reliability_score: float = 0.9,
) -> BuildMetricSnapshot:
    return BuildMetricSnapshot(
        build_id=build_id,
        label=label,
        total_damage=total_damage,
        dps=dps,
        crit_rate=crit_rate,
        buff_uptime_pct=buff_uptime_pct,
        kill_time=kill_time,
        reliability_score=reliability_score,
    )


def _make_metric_summary(
    duration: float = 10.0,
    damage_by_source: dict | None = None,
    buff_uptimes: dict | None = None,
    kill_times: list | None = None,
) -> MetricSummary:
    """
    Builds a MetricSummary whose attributes the report_generator reads via
    getattr(..., "damage_by_source", {}) (a dict), getattr(..., "buff_uptimes", {})
    (a dict), and getattr(..., "kill_times", []) (a list).

    MetricSummary is a dataclass, so we inject the non-standard attributes
    dynamically.
    """
    summary = MetricSummary(
        duration=duration,
        total_damage=0.0,
        overall_dps=0.0,
        dps_breakdown=[],
        buff_uptimes=[],
        kill_times=kill_times or [],
        peak_dps=0.0,
        mean_dps=0.0,
    )
    # The report_generator uses getattr(summary, "damage_by_source", {}).items()
    # so we attach the dict attribute directly.
    summary.damage_by_source = damage_by_source or {}  # type: ignore[attr-defined]
    # Similarly for buff_uptimes (dict, not list)
    summary.buff_uptimes = buff_uptimes or {}  # type: ignore[attr-defined]
    return summary


# ===========================================================================
# VisualCache
# ===========================================================================

class TestVisualCacheMissAndHit:
    def test_get_missing_key_returns_none(self):
        cache = VisualCache()
        assert cache.get("nonexistent") is None

    def test_set_then_get_returns_data(self):
        cache = VisualCache()
        cache.set("k1", {"x": 1})
        assert cache.get("k1") == {"x": 1}

    def test_set_then_get_returns_exact_object(self):
        cache = VisualCache()
        obj = [1, 2, 3]
        cache.set("list_key", obj)
        assert cache.get("list_key") is obj

    def test_get_after_different_key_set_still_none(self):
        cache = VisualCache()
        cache.set("k1", "data1")
        assert cache.get("k2") is None

    def test_overwrite_existing_key(self):
        cache = VisualCache()
        cache.set("k", "first")
        cache.set("k", "second")
        assert cache.get("k") == "second"


class TestVisualCacheTTL:
    def test_ttl_expiry_returns_none(self):
        cache = VisualCache()
        # Set created_at in the past so ttl has already elapsed
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "data", ttl=1.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1002.0  # 2 seconds later — expired
            result = cache.get("k")
        assert result is None

    def test_ttl_not_expired_returns_data(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "data", ttl=10.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1005.0  # 5 seconds later — still valid
            result = cache.get("k")
        assert result == "data"

    def test_ttl_zero_never_expires(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "forever", ttl=0.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 9_999_999.0
            result = cache.get("k")
        assert result == "forever"

    def test_ttl_boundary_exact_expiry(self):
        """An entry is expired when time elapsed is strictly greater than ttl."""
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "val", ttl=5.0)

        # At exactly ttl seconds elapsed, time.time() - created_at == 5.0,
        # which is NOT > 5.0, so it should still be valid.
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1005.0
            assert cache.get("k") == "val"

        # One microsecond past TTL — should now be expired.
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1005.0001
            assert cache.get("k") is None


class TestVisualCacheEviction:
    def test_max_size_2_evicts_oldest_on_third_insert(self):
        cache = VisualCache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None  # oldest evicted
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_len_respects_max_size(self):
        cache = VisualCache(max_size=3)
        for i in range(5):
            cache.set(f"k{i}", i)
        assert len(cache) == 3

    def test_reinserting_existing_key_does_not_grow_beyond_max(self):
        cache = VisualCache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("a", 99)  # re-insert — should not evict b
        assert cache.get("a") == 99
        assert cache.get("b") == 2
        assert len(cache) == 2


class TestVisualCacheHitCount:
    def test_hit_count_increments_on_successful_get(self):
        cache = VisualCache()
        cache.set("k", "v")
        cache.get("k")
        cache.get("k")
        entry = cache._cache["k"]
        assert entry.hit_count == 2

    def test_hit_count_does_not_increment_on_miss(self):
        cache = VisualCache()
        cache.set("k", "v")
        cache.get("missing")
        entry = cache._cache["k"]
        assert entry.hit_count == 0

    def test_hit_count_does_not_increment_on_expired_entry(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "v", ttl=1.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1002.0
            cache.get("k")  # expired — should NOT increment

        entry = cache._cache["k"]
        assert entry.hit_count == 0


class TestVisualCacheInvalidate:
    def test_invalidate_existing_key_returns_true(self):
        cache = VisualCache()
        cache.set("k", "v")
        assert cache.invalidate("k") is True

    def test_invalidate_existing_key_removes_it(self):
        cache = VisualCache()
        cache.set("k", "v")
        cache.invalidate("k")
        assert cache.get("k") is None

    def test_invalidate_missing_key_returns_false(self):
        cache = VisualCache()
        assert cache.invalidate("no_such_key") is False


class TestVisualCacheClear:
    def test_clear_empties_cache(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_get_after_clear_returns_none(self):
        cache = VisualCache()
        cache.set("k", "v")
        cache.clear()
        assert cache.get("k") is None

    def test_can_insert_after_clear(self):
        cache = VisualCache()
        cache.set("k", "v1")
        cache.clear()
        cache.set("k", "v2")
        assert cache.get("k") == "v2"


class TestVisualCacheEvictExpired:
    def test_evict_expired_removes_expired_entries(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("expired_1", "x", ttl=1.0)
            cache.set("expired_2", "y", ttl=1.0)
            cache.set("fresh", "z", ttl=100.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1002.0
            count = cache.evict_expired()
            fresh_val = cache.get("fresh")

        assert count == 2
        assert fresh_val is not None

    def test_evict_expired_returns_zero_when_nothing_expired(self):
        cache = VisualCache()
        cache.set("k", "v", ttl=100.0)
        assert cache.evict_expired() == 0

    def test_evict_expired_ttl_zero_not_evicted(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("k", "v", ttl=0.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 9_999_999.0
            count = cache.evict_expired()

        assert count == 0


class TestVisualCacheStats:
    def test_stats_has_required_keys(self):
        cache = VisualCache()
        s = cache.stats()
        for key in ("size", "max_size", "total_hits", "expired_keys"):
            assert key in s

    def test_stats_total_hits_accumulates(self):
        cache = VisualCache()
        cache.set("k", "v")
        cache.get("k")
        cache.get("k")
        assert cache.stats()["total_hits"] == 2

    def test_stats_expired_keys_count(self):
        cache = VisualCache()
        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1000.0
            cache.set("expired", "x", ttl=1.0)
            cache.set("fresh", "y", ttl=1000.0)

        with patch("visualization.cache.visual_cache.time") as mock_time:
            mock_time.time.return_value = 1002.0
            s = cache.stats()

        assert s["expired_keys"] == 1

    def test_stats_size_reflects_current_count(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.stats()["size"] == 2


class TestVisualCacheLen:
    def test_len_empty(self):
        cache = VisualCache()
        assert len(cache) == 0

    def test_len_after_inserts(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2

    def test_len_after_invalidate(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.invalidate("a")
        assert len(cache) == 1


# ===========================================================================
# ReportGenerator
# ===========================================================================

class TestReportGeneratorCreateReport:
    def test_create_report_has_title(self):
        gen = ReportGenerator()
        report = gen.create_report("My Report")
        assert report.title == "My Report"

    def test_create_report_has_generated_at(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        assert report.generated_at > 0

    def test_create_report_sections_empty(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        assert report.sections == []

    def test_create_report_default_metadata_empty(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        assert report.metadata == {}

    def test_create_report_custom_metadata(self):
        gen = ReportGenerator()
        report = gen.create_report("R", metadata={"author": "tester"})
        assert report.metadata["author"] == "tester"


class TestReportGeneratorAddSection:
    def test_add_section_increases_count(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "Section 1", [{"a": 1}])
        assert len(report.sections) == 1

    def test_add_two_sections(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S1", [])
        gen.add_section(report, "S2", [])
        assert len(report.sections) == 2

    def test_add_section_title_stored(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "My Section", [])
        assert report.sections[0].title == "My Section"

    def test_add_section_data_stored(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        rows = [{"key": "val"}]
        gen.add_section(report, "S", rows)
        assert report.sections[0].data == rows

    def test_add_section_summary_default_empty(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S", [])
        assert report.sections[0].summary == {}


class TestReportGeneratorToJson:
    def test_to_json_is_valid_json(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        raw = gen.to_json(report)
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_to_json_has_title_key(self):
        gen = ReportGenerator()
        report = gen.create_report("My Title")
        parsed = json.loads(gen.to_json(report))
        assert parsed["title"] == "My Title"

    def test_to_json_contains_sections(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S1", [{"x": 1}])
        parsed = json.loads(gen.to_json(report))
        assert len(parsed["sections"]) == 1

    def test_to_json_generated_at_present(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        parsed = json.loads(gen.to_json(report))
        assert "generated_at" in parsed


class TestReportGeneratorToCsv:
    def test_to_csv_no_sections_returns_empty_string(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        assert gen.to_csv(report) == ""

    def test_to_csv_empty_section_data_returns_empty_string(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "Empty", [])
        assert gen.to_csv(report) == ""

    def test_to_csv_contains_header_row(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S", [{"name": "Alice", "score": 100}])
        csv_out = gen.to_csv(report)
        assert "name" in csv_out
        assert "score" in csv_out

    def test_to_csv_contains_data_values(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S", [{"col": "hello"}])
        csv_out = gen.to_csv(report)
        assert "hello" in csv_out

    def test_to_csv_first_section_by_default(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S0", [{"a": "first"}])
        gen.add_section(report, "S1", [{"b": "second"}])
        csv_out = gen.to_csv(report)
        assert "first" in csv_out
        assert "second" not in csv_out


class TestReportGeneratorToPdfData:
    def test_to_pdf_data_has_title_key(self):
        gen = ReportGenerator()
        report = gen.create_report("PDF Title")
        pdf = gen.to_pdf_data(report)
        assert pdf["title"] == "PDF Title"

    def test_to_pdf_data_has_sections_key(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        pdf = gen.to_pdf_data(report)
        assert "sections" in pdf

    def test_to_pdf_data_sections_count_matches(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        gen.add_section(report, "S1", [])
        gen.add_section(report, "S2", [])
        pdf = gen.to_pdf_data(report)
        assert len(pdf["sections"]) == 2

    def test_to_pdf_data_has_generated_at(self):
        gen = ReportGenerator()
        report = gen.create_report("R")
        pdf = gen.to_pdf_data(report)
        assert "generated_at" in pdf


class TestReportGeneratorFromMetricSummary:
    def _make_dps_source(
        self,
        total_damage: float = 5000.0,
        dps: float = 500.0,
        hit_count: int = 10,
        crit_count: int = 3,
        crit_rate: float = 0.3,
    ) -> DpsBreakdown:
        return DpsBreakdown(
            source="fireball",
            total_damage=total_damage,
            dps=dps,
            hit_count=hit_count,
            crit_count=crit_count,
            crit_rate=crit_rate,
        )

    def _make_buff_source(
        self,
        buff_name: str = "haste",
        total_uptime: float = 8.0,
        uptime_pct: float = 0.8,
        application_count: int = 2,
    ) -> BuffUptimeSummary:
        return BuffUptimeSummary(
            buff_name=buff_name,
            total_uptime=total_uptime,
            uptime_pct=uptime_pct,
            application_count=application_count,
        )

    def test_from_metric_summary_produces_exactly_3_sections(self):
        gen = ReportGenerator()
        summary = _make_metric_summary()
        report = gen.from_metric_summary(summary)
        assert len(report.sections) == 3

    def test_from_metric_summary_section_names(self):
        gen = ReportGenerator()
        summary = _make_metric_summary()
        report = gen.from_metric_summary(summary)
        titles = [s.title for s in report.sections]
        assert "DPS Breakdown" in titles
        assert "Buff Uptimes" in titles
        assert "Kill Times" in titles

    def test_from_metric_summary_dps_section_rows(self):
        gen = ReportGenerator()
        dps_src = self._make_dps_source()
        summary = _make_metric_summary(
            damage_by_source={"fireball": dps_src}
        )
        report = gen.from_metric_summary(summary)
        dps_section = next(s for s in report.sections if s.title == "DPS Breakdown")
        assert len(dps_section.data) == 1
        assert dps_section.data[0]["source"] == "fireball"
        assert dps_section.data[0]["total_damage"] == 5000.0

    def test_from_metric_summary_buff_section_rows(self):
        gen = ReportGenerator()
        buff_src = self._make_buff_source()
        summary = _make_metric_summary(
            buff_uptimes={"haste": buff_src}
        )
        report = gen.from_metric_summary(summary)
        buff_section = next(s for s in report.sections if s.title == "Buff Uptimes")
        assert len(buff_section.data) == 1
        assert buff_section.data[0]["buff_name"] == "haste"
        assert buff_section.data[0]["uptime_pct"] == pytest.approx(0.8)

    def test_from_metric_summary_kill_times_section_rows(self):
        gen = ReportGenerator()
        summary = _make_metric_summary(kill_times=[12.5, 15.0])
        report = gen.from_metric_summary(summary)
        kill_section = next(s for s in report.sections if s.title == "Kill Times")
        assert len(kill_section.data) == 2
        times = [row["kill_time"] for row in kill_section.data]
        assert 12.5 in times
        assert 15.0 in times

    def test_from_metric_summary_title_contains_build_label(self):
        gen = ReportGenerator()
        summary = _make_metric_summary()
        report = gen.from_metric_summary(summary, build_label="Alpha")
        assert "Alpha" in report.title

    def test_from_metric_summary_no_damage_sources_empty_dps_section(self):
        gen = ReportGenerator()
        summary = _make_metric_summary(damage_by_source={})
        report = gen.from_metric_summary(summary)
        dps_section = next(s for s in report.sections if s.title == "DPS Breakdown")
        assert dps_section.data == []

    def test_from_metric_summary_dps_row_has_crit_rate(self):
        gen = ReportGenerator()
        dps_src = self._make_dps_source(crit_rate=0.45)
        summary = _make_metric_summary(damage_by_source={"skill": dps_src})
        report = gen.from_metric_summary(summary)
        dps_section = next(s for s in report.sections if s.title == "DPS Breakdown")
        assert dps_section.data[0]["crit_rate"] == pytest.approx(0.45)


# ===========================================================================
# ComparisonDatasetBuilder
# ===========================================================================

class TestComparisonDatasetBuilderBasic:
    def test_add_build_and_build_comparison_differential(self):
        builder = ComparisonDatasetBuilder()
        s1 = _snapshot(build_id="A", dps=1000.0)
        s2 = _snapshot(build_id="B", dps=1200.0)
        builder.add_build(s1)
        builder.add_build(s2)
        dataset = builder.build_comparison()
        assert dataset.differential["dps"] == pytest.approx(200.0)

    def test_differential_total_damage(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", total_damage=10_000.0))
        builder.add_build(_snapshot(build_id="B", total_damage=12_000.0))
        dataset = builder.build_comparison()
        assert dataset.differential["total_damage"] == pytest.approx(2_000.0)

    def test_differential_negative_when_b_lower(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", dps=1500.0))
        builder.add_build(_snapshot(build_id="B", dps=1000.0))
        dataset = builder.build_comparison()
        assert dataset.differential["dps"] == pytest.approx(-500.0)

    def test_builds_list_preserved(self):
        builder = ComparisonDatasetBuilder()
        s1 = _snapshot(build_id="A")
        s2 = _snapshot(build_id="B")
        builder.add_build(s1)
        builder.add_build(s2)
        dataset = builder.build_comparison()
        assert len(dataset.builds) == 2

    def test_metric_names_list_present(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot("A"))
        builder.add_build(_snapshot("B"))
        dataset = builder.build_comparison()
        assert "dps" in dataset.metric_names
        assert "total_damage" in dataset.metric_names


class TestComparisonDatasetBuilderWinnerByMetric:
    def test_winner_by_metric_dps_correct(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", dps=800.0))
        builder.add_build(_snapshot(build_id="B", dps=1000.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["dps"] == "B"

    def test_winner_by_metric_dps_a_wins(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", dps=2000.0))
        builder.add_build(_snapshot(build_id="B", dps=500.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["dps"] == "A"

    def test_winner_by_metric_kill_time_lower_wins(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", kill_time=30.0))
        builder.add_build(_snapshot(build_id="B", kill_time=20.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["kill_time"] == "B"

    def test_winner_by_metric_kill_time_none_b_has_kill(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", kill_time=None))
        builder.add_build(_snapshot(build_id="B", kill_time=25.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["kill_time"] == "B"

    def test_winner_by_metric_kill_time_none_a_has_kill(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", kill_time=25.0))
        builder.add_build(_snapshot(build_id="B", kill_time=None))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["kill_time"] == "A"

    def test_winner_by_metric_kill_time_both_none_a_wins(self):
        """When both builds have no kill, tie-breaks to build A (first)."""
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot(build_id="A", kill_time=None))
        builder.add_build(_snapshot(build_id="B", kill_time=None))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["kill_time"] == "A"

    def test_winner_by_metric_all_metrics_present(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot("A"))
        builder.add_build(_snapshot("B"))
        dataset = builder.build_comparison()
        for metric in ("total_damage", "dps", "crit_rate", "buff_uptime_pct",
                       "reliability_score", "kill_time"):
            assert metric in dataset.winner_by_metric


class TestComparisonDatasetBuilderErrors:
    def test_fewer_than_2_builds_raises_value_error(self):
        builder = ComparisonDatasetBuilder()
        with pytest.raises(ValueError, match="[Aa]t least 2"):
            builder.build_comparison()

    def test_exactly_1_build_raises_value_error(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot())
        with pytest.raises(ValueError):
            builder.build_comparison()


class TestComparisonDatasetBuilderReset:
    def test_reset_clears_builds(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot("A"))
        builder.add_build(_snapshot("B"))
        builder.reset()
        with pytest.raises(ValueError):
            builder.build_comparison()

    def test_can_add_builds_after_reset(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(_snapshot("A"))
        builder.reset()
        builder.add_build(_snapshot("X"))
        builder.add_build(_snapshot("Y"))
        dataset = builder.build_comparison()
        assert len(dataset.builds) == 2


class TestComparisonDatasetBuilderFromMetricSummaries:
    def _make_summary_tuple(
        self,
        build_id: str,
        label: str,
        dps_val: float = 1000.0,
        kill_time: float | None = 30.0,
    ):
        dps_src = DpsBreakdown(
            source="skill",
            total_damage=dps_val * 10,
            dps=dps_val,
            hit_count=10,
            crit_count=3,
            crit_rate=0.3,
        )
        buff_src = BuffUptimeSummary(
            buff_name="haste",
            total_uptime=8.0,
            uptime_pct=0.8,
            application_count=2,
        )
        summary = MetricSummary(
            duration=10.0,
            total_damage=dps_val * 10,
            overall_dps=dps_val,
            dps_breakdown=[dps_src],
            buff_uptimes=[buff_src],
            kill_times=[kill_time] if kill_time is not None else [],
            peak_dps=dps_val * 1.5,
            mean_dps=dps_val * 0.9,
        )
        # Attach dict-style attributes that comparison builder reads via getattr
        summary.damage_by_source = {"skill": dps_src}  # type: ignore[attr-defined]
        summary.buff_uptimes = {"haste": buff_src}  # type: ignore[attr-defined]
        return (build_id, label, summary)

    def test_from_metric_summaries_returns_comparison_dataset(self):
        builder = ComparisonDatasetBuilder()
        summaries = [
            self._make_summary_tuple("A", "Build A"),
            self._make_summary_tuple("B", "Build B"),
        ]
        dataset = builder.from_metric_summaries(summaries)
        assert isinstance(dataset, ComparisonDataset)

    def test_from_metric_summaries_correct_differential(self):
        builder = ComparisonDatasetBuilder()
        summaries = [
            self._make_summary_tuple("A", "Build A", dps_val=1000.0),
            self._make_summary_tuple("B", "Build B", dps_val=1200.0),
        ]
        dataset = builder.from_metric_summaries(summaries)
        # dps differential = 1200 - 1000 = 200
        assert dataset.differential["dps"] == pytest.approx(200.0)

    def test_from_metric_summaries_two_builds(self):
        builder = ComparisonDatasetBuilder()
        summaries = [
            self._make_summary_tuple("A", "Build A"),
            self._make_summary_tuple("B", "Build B"),
        ]
        dataset = builder.from_metric_summaries(summaries)
        assert len(dataset.builds) == 2

    def test_from_metric_summaries_resets_between_calls(self):
        """Calling from_metric_summaries twice should not accumulate old builds."""
        builder = ComparisonDatasetBuilder()
        summaries = [
            self._make_summary_tuple("A", "Build A"),
            self._make_summary_tuple("B", "Build B"),
        ]
        builder.from_metric_summaries(summaries)
        dataset2 = builder.from_metric_summaries(summaries)
        assert len(dataset2.builds) == 2
