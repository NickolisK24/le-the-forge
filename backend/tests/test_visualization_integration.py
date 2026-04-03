"""Integration tests for Phase N visualization pipeline.

Tests exercise multiple visualization components working together:
timeline → formatter, heatmap → blur, replay → dict roundtrip,
MetricSummary → Report, VisualizationIntegration full pipeline,
ComparisonDatasetBuilder, and various edge cases.
"""

from __future__ import annotations

import json
import random
from unittest.mock import MagicMock, patch

import pytest

from visualization.formatters.result_formatter import ResultFormatter, FormattedDataset
from visualization.timeline.timeline_generator import TimelineGenerator, TimelineDataset
from visualization.heatmaps.heatmap_generator import HeatmapGenerator
from visualization.replay.combat_replay_builder import (
    CombatReplayBuilder,
    ReplayEntity,
    ReplayProjectile,
)
from visualization.metrics.metric_summary import MetricSummaryEngine, MetricSummary, DpsBreakdown, BuffUptimeSummary
from visualization.reports.report_generator import ReportGenerator, Report
from visualization.cache.visual_cache import VisualCache
from visualization.comparison.comparison_dataset_builder import (
    ComparisonDatasetBuilder,
    BuildMetricSnapshot,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_damage_events(n: int, source: str = "skill_a", base_time: float = 0.0) -> list[dict]:
    return [
        {"time": base_time + i * 0.5, "source": source, "amount": 100.0, "is_crit": False}
        for i in range(n)
    ]


def _make_buff_events(buff_name: str = "power_buff") -> list[dict]:
    return [
        {"time": 1.0, "buff_name": buff_name, "event": "applied", "duration": 2.0},
        {"time": 3.0, "buff_name": buff_name, "event": "expired", "duration": 0.0},
    ]


def _make_kill_events(times: list[float]) -> list[dict]:
    return [{"time": t, "target": f"enemy_{i}"} for i, t in enumerate(times)]


def _make_metric_summary(
    total_damage: float = 1000.0,
    duration: float = 10.0,
    source: str = "skill_a",
    hit_count: int = 10,
    crit_count: int = 2,
) -> MetricSummary:
    breakdown = DpsBreakdown(
        source=source,
        total_damage=total_damage,
        dps=total_damage / duration,
        hit_count=hit_count,
        crit_count=crit_count,
        crit_rate=crit_count / hit_count if hit_count else 0.0,
    )
    buff_uptime = BuffUptimeSummary(
        buff_name="power_buff",
        total_uptime=5.0,
        uptime_pct=0.5,
        application_count=1,
    )
    return MetricSummary(
        duration=duration,
        total_damage=total_damage,
        overall_dps=total_damage / duration,
        dps_breakdown=[breakdown],
        buff_uptimes=[buff_uptime],
        kill_times=[5.0],
        peak_dps=total_damage / duration,
        mean_dps=total_damage / duration,
    )


# ===========================================================================
# 1. Timeline → Formatter pipeline
# ===========================================================================

class TestTimelineFormatterPipeline:
    """Timeline generation feeding directly into ResultFormatter."""

    def test_damage_timeline_50_events_chart_series_label(self):
        events = _make_damage_events(50)
        gen = TimelineGenerator(tick_size=0.5)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        assert series.label == "damage"

    def test_damage_timeline_50_events_chart_series_non_empty(self):
        events = _make_damage_events(50)
        gen = TimelineGenerator(tick_size=0.5)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        assert len(series.x) > 0
        assert len(series.y) > 0
        assert len(series.x) == len(series.y)

    def test_formatter_format_time_series_from_chart_series(self):
        events = _make_damage_events(20)
        gen = TimelineGenerator(tick_size=0.5)
        dataset = gen.generate_damage_timeline(events)
        chart_series = gen.to_chart_series(dataset, "damage")
        formatter = ResultFormatter()
        formatted = formatter.format_time_series(
            chart_series.x, chart_series.y, label="damage_output", unit="dmg"
        )
        assert formatted.label == "damage_output"
        assert len(formatted.x) == len(chart_series.x)
        assert len(formatted.y) == len(chart_series.y)

    def test_formatter_format_time_series_values_match(self):
        events = _make_damage_events(10)
        gen = TimelineGenerator(tick_size=1.0)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        formatter = ResultFormatter()
        formatted = formatter.format_time_series(series.x, series.y, "test")
        assert formatted.x == series.x
        assert formatted.y == series.y

    def test_resample_then_chart_series_aggregates_values(self):
        # Two events at t=0.1 and t=0.2 — after resample to tick=1.0 they land in same bucket
        events = [
            {"time": 0.1, "source": "skill_a", "amount": 50.0},
            {"time": 0.2, "source": "skill_a", "amount": 70.0},
        ]
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_damage_timeline(events)
        resampled = gen.resample(dataset, new_tick_size=1.0)
        series = gen.to_chart_series(resampled, "damage")
        # Both events should land in tick bucket 0 → sum = 120.0
        assert len(series.y) >= 1
        assert series.y[0] == pytest.approx(120.0)

    def test_resample_preserves_duration(self):
        events = _make_damage_events(10)
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_damage_timeline(events)
        resampled = gen.resample(dataset, new_tick_size=1.0)
        assert resampled.duration == dataset.duration

    def test_resample_changes_tick_size(self):
        events = _make_damage_events(10)
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_damage_timeline(events)
        resampled = gen.resample(dataset, new_tick_size=0.5)
        assert resampled.tick_size == pytest.approx(0.5)

    def test_format_multi_series_pipeline(self):
        formatter = ResultFormatter()
        dataset = formatter.format_multi_series(
            {"damage": ([0.0, 1.0, 2.0], [100.0, 200.0, 150.0]),
             "heal": ([0.0, 1.0, 2.0], [50.0, 60.0, 70.0])},
            title="Combat Overview",
        )
        assert dataset.title == "Combat Overview"
        assert len(dataset.series) == 2

    def test_to_dict_from_pipeline(self):
        formatter = ResultFormatter()
        ds = formatter.format_multi_series(
            {"atk": ([0.0, 1.0], [10.0, 20.0])},
            title="T",
        )
        d = formatter.to_dict(ds)
        assert d["title"] == "T"
        assert len(d["series"]) == 1
        assert d["series"][0]["label"] == "atk"


# ===========================================================================
# 2. Heatmap → Blur pipeline
# ===========================================================================

class TestHeatmapBlurPipeline:
    """Heatmap generation followed by gaussian blur."""

    def test_100_random_points_blur_output_shape_preserved(self):
        rng = random.Random(42)
        points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(100)]
        gen = HeatmapGenerator(rows=10, cols=10)
        heatmap = gen.generate(points)
        blurred = gen.apply_gaussian_blur(heatmap, sigma=1.0)
        assert blurred.rows == heatmap.rows
        assert blurred.cols == heatmap.cols
        assert len(blurred.grid) == heatmap.rows
        assert len(blurred.grid[0]) == heatmap.cols

    def test_100_random_points_blur_no_normalized_exceeds_1(self):
        rng = random.Random(99)
        points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(100)]
        gen = HeatmapGenerator(rows=10, cols=10)
        heatmap = gen.generate(points)
        blurred = gen.apply_gaussian_blur(heatmap, sigma=1.0)
        for cell in blurred.cells:
            assert cell.normalized <= 1.0 + 1e-9

    def test_blur_max_value_positive_after_nonzero_input(self):
        points = [(5.0, 5.0)] * 10
        gen = HeatmapGenerator(rows=5, cols=5)
        heatmap = gen.generate(points)
        blurred = gen.apply_gaussian_blur(heatmap, sigma=1.0)
        assert blurred.max_value > 0.0

    def test_blur_cell_count_preserved(self):
        points = [(float(i), float(i)) for i in range(20)]
        gen = HeatmapGenerator(rows=8, cols=8)
        heatmap = gen.generate(points)
        blurred = gen.apply_gaussian_blur(heatmap, sigma=1.0)
        assert len(blurred.cells) == heatmap.rows * heatmap.cols

    def test_blur_all_normalized_between_0_and_1(self):
        rng = random.Random(7)
        points = [(rng.uniform(-50, 50), rng.uniform(-50, 50)) for _ in range(50)]
        gen = HeatmapGenerator(rows=12, cols=12)
        heatmap = gen.generate(points)
        blurred = gen.apply_gaussian_blur(heatmap, sigma=1.0)
        for cell in blurred.cells:
            assert 0.0 <= cell.normalized <= 1.0 + 1e-9

    def test_generate_damage_density_then_blur(self):
        positions = [(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
        damages = [100.0, 200.0, 300.0]
        gen = HeatmapGenerator(rows=5, cols=5)
        heatmap = gen.generate_damage_density(positions, damages)
        blurred = gen.apply_gaussian_blur(heatmap)
        assert blurred.rows == 5
        assert blurred.cols == 5


# ===========================================================================
# 3. Replay → Dict roundtrip
# ===========================================================================

class TestReplayDictRoundtrip:
    """Build replay frames, serialize to dict, verify structure."""

    def _make_entities(self, count: int = 2) -> list[ReplayEntity]:
        return [
            ReplayEntity(
                entity_id=f"entity_{i}",
                position=(float(i), float(i * 2)),
                health=100.0 - i * 10,
                is_alive=True,
            )
            for i in range(count)
        ]

    def test_5_frames_dict_frame_count(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in range(5):
            builder.add_frame(time=float(t), entities=self._make_entities())
        replay = builder.build()
        d = builder.to_dict(replay)
        assert d["total_frames"] == 5
        assert len(d["frames"]) == 5

    def test_entity_positions_serialized_as_lists(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=0.0, entities=self._make_entities(3))
        replay = builder.build()
        d = builder.to_dict(replay)
        for frame in d["frames"]:
            for entity in frame["entities"]:
                assert isinstance(entity["position"], list), (
                    f"position should be list, got {type(entity['position'])}"
                )

    def test_entity_positions_not_tuples(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        entities = [ReplayEntity("e0", (3.5, 7.2), 100.0, True)]
        builder.add_frame(time=0.0, entities=entities)
        replay = builder.build()
        d = builder.to_dict(replay)
        pos = d["frames"][0]["entities"][0]["position"]
        assert not isinstance(pos, tuple)
        assert pos == [3.5, 7.2]

    def test_frame_indices_sequential(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in range(5):
            builder.add_frame(time=float(t), entities=self._make_entities(1))
        replay = builder.build()
        d = builder.to_dict(replay)
        indices = [f["frame_index"] for f in d["frames"]]
        assert indices == list(range(5))

    def test_entity_ids_in_replay_data(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        entities = [
            ReplayEntity("hero", (0.0, 0.0), 100.0, True),
            ReplayEntity("enemy", (5.0, 5.0), 80.0, True),
        ]
        builder.add_frame(time=0.0, entities=entities)
        replay = builder.build()
        assert "hero" in replay.entity_ids
        assert "enemy" in replay.entity_ids

    def test_duration_set_correctly(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in [0.0, 1.0, 5.0, 10.0]:
            builder.add_frame(time=t, entities=self._make_entities(1))
        replay = builder.build()
        assert replay.duration == pytest.approx(10.0)


# ===========================================================================
# 4. MetricSummary → Report pipeline
# ===========================================================================

class TestMetricSummaryReportPipeline:
    """MetricSummaryEngine output feeding into ReportGenerator."""

    def test_report_has_three_sections(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary)
        assert len(report.sections) == 3

    def test_report_section_titles(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary)
        titles = [s.title for s in report.sections]
        assert "DPS Breakdown" in titles
        assert "Buff Uptimes" in titles
        assert "Kill Times" in titles

    def test_kill_times_section_has_correct_count(self):
        summary = _make_metric_summary()
        summary.kill_times = [2.5, 7.0, 9.1]
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary, build_label="TestBuild")
        # Find Kill Times section
        kill_section = next(s for s in report.sections if s.title == "Kill Times")
        assert len(kill_section.data) == 3

    def test_report_build_label_in_title(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary, build_label="MyBuild")
        assert "MyBuild" in report.title

    def test_report_generated_at_positive(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary)
        assert report.generated_at > 0.0

    def test_metric_summary_engine_compute_dps_breakdown_source_rows(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": 0.0, "source": "skill_a", "amount": 200.0, "is_crit": False},
            {"time": 1.0, "source": "skill_b", "amount": 300.0, "is_crit": True},
            {"time": 2.0, "source": "skill_a", "amount": 100.0, "is_crit": False},
        ]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        sources = {b.source for b in breakdown}
        assert "skill_a" in sources
        assert "skill_b" in sources

    def test_metric_summary_engine_dps_breakdown_totals(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": 0.0, "source": "fire", "amount": 500.0, "is_crit": False},
            {"time": 1.0, "source": "fire", "amount": 500.0, "is_crit": False},
        ]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        fire = next(b for b in breakdown if b.source == "fire")
        assert fire.total_damage == pytest.approx(1000.0)
        assert fire.dps == pytest.approx(100.0)


# ===========================================================================
# 5. ComparisonDatasetBuilder integration
# ===========================================================================

class TestComparisonDatasetBuilderIntegration:
    """Two MetricSummary objects compared via ComparisonDatasetBuilder."""

    def _snapshot(self, build_id: str, dps: float, total_damage: float) -> BuildMetricSnapshot:
        return BuildMetricSnapshot(
            build_id=build_id,
            label=build_id,
            total_damage=total_damage,
            dps=dps,
            crit_rate=0.2,
            buff_uptime_pct=0.5,
            kill_time=5.0,
            reliability_score=1.0,
        )

    def test_winner_by_metric_dps_correct_build(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("build_a", dps=100.0, total_damage=1000.0))
        builder.add_build(self._snapshot("build_b", dps=150.0, total_damage=1500.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["dps"] == "build_b"

    def test_winner_by_metric_lower_dps_loses(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("build_a", dps=200.0, total_damage=2000.0))
        builder.add_build(self._snapshot("build_b", dps=50.0, total_damage=500.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["dps"] == "build_a"

    def test_differential_dps_computed(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=1000.0))
        builder.add_build(self._snapshot("b", dps=120.0, total_damage=1200.0))
        dataset = builder.build_comparison()
        assert dataset.differential["dps"] == pytest.approx(20.0)

    def test_two_builds_in_dataset(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=1000.0))
        builder.add_build(self._snapshot("b", dps=200.0, total_damage=2000.0))
        dataset = builder.build_comparison()
        assert len(dataset.builds) == 2

    def test_metric_names_contains_dps(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=1000.0))
        builder.add_build(self._snapshot("b", dps=200.0, total_damage=2000.0))
        dataset = builder.build_comparison()
        assert "dps" in dataset.metric_names

    def test_single_build_raises(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=1000.0))
        with pytest.raises(ValueError):
            builder.build_comparison()

    def test_reset_clears_builds(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=1000.0))
        builder.reset()
        builder.add_build(self._snapshot("x", dps=50.0, total_damage=500.0))
        builder.add_build(self._snapshot("y", dps=60.0, total_damage=600.0))
        dataset = builder.build_comparison()
        build_ids = {b.build_id for b in dataset.builds}
        assert "a" not in build_ids
        assert "x" in build_ids

    def test_winner_by_metric_total_damage(self):
        builder = ComparisonDatasetBuilder()
        builder.add_build(self._snapshot("a", dps=100.0, total_damage=3000.0))
        builder.add_build(self._snapshot("b", dps=100.0, total_damage=1000.0))
        dataset = builder.build_comparison()
        assert dataset.winner_by_metric["total_damage"] == "a"


# ===========================================================================
# 6. Edge cases
# ===========================================================================

class TestEdgeCases:
    """Edge cases: empty inputs, single events, degenerate data."""

    def test_empty_damage_events_timeline_returns_empty_dataset(self):
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_damage_timeline([])
        assert len(dataset.events) == 0
        assert dataset.duration == pytest.approx(0.0)

    def test_empty_damage_events_chart_series_empty(self):
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_damage_timeline([])
        series = gen.to_chart_series(dataset, "damage")
        assert series.x == []
        assert series.y == []

    def test_single_event_timeline_produces_single_bucket_series(self):
        events = [{"time": 2.0, "source": "skill_a", "amount": 500.0}]
        gen = TimelineGenerator(tick_size=1.0)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        assert len(series.x) == 1
        assert len(series.y) == 1
        assert series.y[0] == pytest.approx(500.0)

    def test_heatmap_empty_points_returns_zero_grid(self):
        gen = HeatmapGenerator(rows=5, cols=5)
        heatmap = gen.generate([])
        assert heatmap.max_value == pytest.approx(0.0)
        for row in heatmap.grid:
            for val in row:
                assert val == pytest.approx(0.0)

    def test_heatmap_identical_positions_max_value_positive(self):
        points = [(5.0, 5.0)] * 20
        gen = HeatmapGenerator(rows=10, cols=10)
        heatmap = gen.generate(points)
        assert heatmap.max_value > 0.0

    def test_heatmap_identical_positions_one_hot_cell(self):
        points = [(5.0, 5.0)] * 10
        gen = HeatmapGenerator(rows=10, cols=10)
        heatmap = gen.generate(points)
        # All weight goes to one cell — exactly one cell should be 1.0 normalized
        hot_cells = [c for c in heatmap.cells if c.normalized == pytest.approx(1.0)]
        assert len(hot_cells) == 1

    def test_replay_zero_frames_build_returns_empty_replay(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        replay = builder.build()
        assert replay.total_frames == 0
        assert len(replay.frames) == 0
        assert replay.duration == pytest.approx(0.0)

    def test_normalize_empty_list_returns_empty(self):
        formatter = ResultFormatter()
        assert formatter.normalize([]) == []

    def test_aggregate_by_bucket_empty_timestamps_returns_empty(self):
        formatter = ResultFormatter()
        centers, avgs = formatter.aggregate_by_bucket([], [], bucket_size=1.0)
        assert centers == []
        assert avgs == []

    def test_aggregate_by_bucket_zero_bucket_size_returns_empty(self):
        formatter = ResultFormatter()
        centers, avgs = formatter.aggregate_by_bucket([1.0, 2.0], [10.0, 20.0], bucket_size=0.0)
        assert centers == []
        assert avgs == []

    def test_buff_timeline_empty_returns_empty_dataset(self):
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_buff_timeline([])
        assert len(dataset.events) == 0

    def test_movement_timeline_empty_returns_empty_dataset(self):
        gen = TimelineGenerator(tick_size=0.1)
        dataset = gen.generate_movement_timeline([])
        assert len(dataset.events) == 0


# ===========================================================================
# 7. Report export pipeline
# ===========================================================================

class TestReportExportPipeline:
    """from_metric_summary → to_json / to_csv / to_pdf_data."""

    def test_to_json_succeeds(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary, build_label="Export")
        json_str = gen.to_json(report)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_to_json_contains_title(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary, build_label="Export")
        parsed = json.loads(gen.to_json(report))
        assert "title" in parsed
        assert "Export" in parsed["title"]

    def test_to_json_contains_sections(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary)
        parsed = json.loads(gen.to_json(report))
        assert "sections" in parsed
        assert len(parsed["sections"]) == 3

    def test_to_csv_section_0_succeeds(self):
        """CSV export of section 0 (DPS Breakdown)."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_section(report, "DPS Breakdown", [
            {"source": "fire", "total_damage": 1000.0, "dps": 100.0,
             "hit_count": 10, "crit_count": 2, "crit_rate": 0.2},
        ])
        csv_str = gen.to_csv(report, section_index=0)
        assert len(csv_str) > 0

    def test_to_csv_has_correct_headers(self):
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_section(report, "DPS Breakdown", [
            {"source": "fire", "total_damage": 1000.0, "dps": 100.0,
             "hit_count": 10, "crit_count": 2, "crit_rate": 0.2},
        ])
        csv_str = gen.to_csv(report, section_index=0)
        first_line = csv_str.splitlines()[0]
        assert "source" in first_line
        assert "total_damage" in first_line
        assert "dps" in first_line

    def test_to_csv_empty_section_returns_empty_string(self):
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_section(report, "Empty", [])
        assert gen.to_csv(report, section_index=0) == ""

    def test_to_csv_no_sections_returns_empty_string(self):
        gen = ReportGenerator()
        report = gen.create_report("Test")
        assert gen.to_csv(report) == ""

    def test_to_pdf_data_has_expected_keys(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary, build_label="PdfTest")
        pdf_data = gen.to_pdf_data(report)
        assert "title" in pdf_data
        assert "generated_at" in pdf_data
        assert "sections" in pdf_data

    def test_to_pdf_data_sections_list(self):
        summary = _make_metric_summary()
        gen = ReportGenerator()
        report = gen.from_metric_summary(summary)
        pdf_data = gen.to_pdf_data(report)
        assert isinstance(pdf_data["sections"], list)
        assert len(pdf_data["sections"]) == 3

    def test_to_pdf_data_section_keys(self):
        gen = ReportGenerator()
        report = gen.create_report("PDF")
        gen.add_section(report, "Test Section", [{"a": 1}], summary={"note": "x"})
        pdf_data = gen.to_pdf_data(report)
        section = pdf_data["sections"][0]
        assert "title" in section
        assert "data" in section
        assert "summary" in section


# ===========================================================================
# 8. VisualizationIntegration / VisualCache integration
# ===========================================================================

class TestVisualCacheIntegration:
    """VisualCache used directly in integration-style tests."""

    def test_cache_stores_and_retrieves(self):
        cache = VisualCache()
        cache.set("key1", {"data": 42})
        result = cache.get("key1")
        assert result == {"data": 42}

    def test_cache_miss_returns_none(self):
        cache = VisualCache()
        assert cache.get("nonexistent") is None

    def test_cache_invalidate_returns_true(self):
        cache = VisualCache()
        cache.set("k", "value")
        assert cache.invalidate("k") is True

    def test_cache_invalidate_missing_key_returns_false(self):
        cache = VisualCache()
        assert cache.invalidate("not_there") is False

    def test_cache_after_invalidate_returns_none(self):
        cache = VisualCache()
        cache.set("k", "value")
        cache.invalidate("k")
        assert cache.get("k") is None

    def test_cache_set_overwrite(self):
        cache = VisualCache()
        cache.set("k", "first")
        cache.set("k", "second")
        assert cache.get("k") == "second"

    def test_cache_clear_removes_all(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_cache_stats_size(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        stats = cache.stats()
        assert stats["size"] == 2

    def test_cache_stats_max_size(self):
        cache = VisualCache(max_size=50)
        stats = cache.stats()
        assert stats["max_size"] == 50

    def test_cache_evicts_oldest_at_capacity(self):
        cache = VisualCache(max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("d") == 4
