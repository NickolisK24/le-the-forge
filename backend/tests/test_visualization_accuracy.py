"""Visualization accuracy tests for Phase N.

Verifies that visual output values are mathematically correct:
ResultFormatter normalisation and aggregation, timeline tick sums,
buff uptime pairing, heatmap cell weights, MetricSummary DPS/crit
calculations, ReplayBuilder frame ordering, and VisualCache counters.
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from visualization.formatters.result_formatter import ResultFormatter
from visualization.timeline.timeline_generator import TimelineGenerator, TimelineEvent, TimelineDataset
from visualization.heatmaps.heatmap_generator import HeatmapGenerator
from visualization.replay.combat_replay_builder import (
    CombatReplayBuilder,
    ReplayEntity,
    ReplayProjectile,
)
from visualization.metrics.metric_summary import MetricSummaryEngine
from visualization.cache.visual_cache import VisualCache, CacheEntry


# ===========================================================================
# 1. ResultFormatter accuracy
# ===========================================================================

class TestResultFormatterAccuracy:
    """Mathematical correctness of normalize() and aggregate_by_bucket()."""

    def test_normalize_standard_case(self):
        formatter = ResultFormatter()
        result = formatter.normalize([0.0, 5.0, 10.0])
        assert result[0] == pytest.approx(0.0)
        assert result[1] == pytest.approx(0.5)
        assert result[2] == pytest.approx(1.0)

    def test_normalize_returns_list(self):
        formatter = ResultFormatter()
        result = formatter.normalize([0.0, 5.0, 10.0])
        assert isinstance(result, list)

    def test_normalize_all_same_values_noop(self):
        formatter = ResultFormatter()
        result = formatter.normalize([3.0, 3.0, 3.0])
        # hi == lo so the original list is returned unchanged
        assert result == [3.0, 3.0, 3.0]

    def test_normalize_all_same_values_length_preserved(self):
        formatter = ResultFormatter()
        result = formatter.normalize([7.0, 7.0, 7.0, 7.0])
        assert len(result) == 4

    def test_normalize_single_element(self):
        formatter = ResultFormatter()
        result = formatter.normalize([42.0])
        assert result == [42.0]

    def test_normalize_negative_values(self):
        formatter = ResultFormatter()
        result = formatter.normalize([-10.0, 0.0, 10.0])
        assert result[0] == pytest.approx(0.0)
        assert result[1] == pytest.approx(0.5)
        assert result[2] == pytest.approx(1.0)

    def test_aggregate_by_bucket_two_buckets(self):
        formatter = ResultFormatter()
        # timestamps: 0.0, 0.5 → bucket 0; 1.0, 1.5 → bucket 1
        centers, avgs = formatter.aggregate_by_bucket(
            [0.0, 0.5, 1.0, 1.5],
            [10.0, 20.0, 30.0, 40.0],
            bucket_size=1.0,
        )
        assert len(centers) == 2
        assert centers[0] == pytest.approx(0.5)   # (0 + 0.5) * 1.0
        assert centers[1] == pytest.approx(1.5)   # (1 + 0.5) * 1.0
        assert avgs[0] == pytest.approx(15.0)     # (10 + 20) / 2
        assert avgs[1] == pytest.approx(35.0)     # (30 + 40) / 2

    def test_aggregate_by_bucket_center_calculation(self):
        formatter = ResultFormatter()
        centers, _ = formatter.aggregate_by_bucket(
            [0.0, 0.9], [1.0, 2.0], bucket_size=1.0
        )
        # Both in bucket 0 → center = 0.5
        assert len(centers) == 1
        assert centers[0] == pytest.approx(0.5)

    def test_aggregate_by_bucket_average_calculation(self):
        formatter = ResultFormatter()
        _, avgs = formatter.aggregate_by_bucket(
            [2.0, 2.5, 2.9], [10.0, 20.0, 30.0], bucket_size=1.0
        )
        # All in bucket 2 → avg = (10+20+30)/3 = 20.0
        assert len(avgs) == 1
        assert avgs[0] == pytest.approx(20.0)

    def test_aggregate_by_bucket_single_point(self):
        formatter = ResultFormatter()
        centers, avgs = formatter.aggregate_by_bucket([3.0], [99.0], bucket_size=1.0)
        assert len(centers) == 1
        assert avgs[0] == pytest.approx(99.0)

    def test_aggregate_by_bucket_sorted_output(self):
        formatter = ResultFormatter()
        centers, avgs = formatter.aggregate_by_bucket(
            [5.0, 1.0, 3.0], [50.0, 10.0, 30.0], bucket_size=1.0
        )
        # Each in its own bucket; centers should be sorted ascending
        assert centers == sorted(centers)

    def test_normalize_min_is_zero_max_is_one(self):
        formatter = ResultFormatter()
        data = [2.0, 5.0, 8.0, 11.0]
        result = formatter.normalize(data)
        assert min(result) == pytest.approx(0.0)
        assert max(result) == pytest.approx(1.0)


# ===========================================================================
# 2. Timeline accuracy
# ===========================================================================

class TestTimelineAccuracy:
    """Damage tick sums and buff uptime pairing are mathematically correct."""

    def test_damage_events_sum_correctly_per_tick(self):
        # Three events at t=0.0, 0.0, 1.0 with tick_size=1.0
        # Tick 0 → 100+200=300; Tick 1 → 50
        events = [
            {"time": 0.0, "source": "skill_a", "amount": 100.0},
            {"time": 0.0, "source": "skill_a", "amount": 200.0},
            {"time": 1.0, "source": "skill_a", "amount": 50.0},
        ]
        gen = TimelineGenerator(tick_size=1.0)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        assert len(series.y) == 2
        assert series.y[0] == pytest.approx(300.0)
        assert series.y[1] == pytest.approx(50.0)

    def test_chart_series_total_matches_sum_of_events(self):
        amounts = [10.0, 20.0, 30.0, 40.0, 50.0]
        events = [{"time": float(i), "source": "s", "amount": a} for i, a in enumerate(amounts)]
        gen = TimelineGenerator(tick_size=1.0)
        dataset = gen.generate_damage_timeline(events)
        series = gen.to_chart_series(dataset, "damage")
        assert sum(series.y) == pytest.approx(sum(amounts))

    def test_buff_applied_expired_pairing_uptime_seconds(self):
        # applied at t=1.0, expired at t=3.0 → uptime = 2.0 s
        engine = MetricSummaryEngine()
        buff_events = [
            {"time": 1.0, "buff_name": "power", "event": "applied"},
            {"time": 3.0, "buff_name": "power", "event": "expired"},
        ]
        uptimes = engine.compute_buff_uptimes(buff_events, duration=10.0)
        assert len(uptimes) == 1
        assert uptimes[0].total_uptime == pytest.approx(2.0)

    def test_buff_uptime_pct_calculation(self):
        engine = MetricSummaryEngine()
        buff_events = [
            {"time": 0.0, "buff_name": "haste", "event": "applied"},
            {"time": 5.0, "buff_name": "haste", "event": "expired"},
        ]
        uptimes = engine.compute_buff_uptimes(buff_events, duration=10.0)
        assert uptimes[0].uptime_pct == pytest.approx(0.5)

    def test_buff_still_active_at_duration_end(self):
        # applied at t=2, never expired → uptime = duration - apply_time
        engine = MetricSummaryEngine()
        buff_events = [
            {"time": 2.0, "buff_name": "barrier", "event": "applied"},
        ]
        uptimes = engine.compute_buff_uptimes(buff_events, duration=10.0)
        assert uptimes[0].total_uptime == pytest.approx(8.0)

    def test_multiple_applications_counted(self):
        engine = MetricSummaryEngine()
        buff_events = [
            {"time": 0.0, "buff_name": "buff", "event": "applied"},
            {"time": 2.0, "buff_name": "buff", "event": "expired"},
            {"time": 5.0, "buff_name": "buff", "event": "applied"},
            {"time": 7.0, "buff_name": "buff", "event": "expired"},
        ]
        uptimes = engine.compute_buff_uptimes(buff_events, duration=10.0)
        assert uptimes[0].application_count == 2
        assert uptimes[0].total_uptime == pytest.approx(4.0)

    def test_timeline_event_sorting_by_time(self):
        events = [
            {"time": 3.0, "source": "s", "amount": 30.0},
            {"time": 1.0, "source": "s", "amount": 10.0},
            {"time": 2.0, "source": "s", "amount": 20.0},
        ]
        gen = TimelineGenerator(tick_size=1.0)
        dataset = gen.generate_damage_timeline(events)
        times = [e.time for e in dataset.events]
        assert times == sorted(times)

    def test_timeline_duration_equals_last_event_time(self):
        events = [
            {"time": 1.0, "source": "s", "amount": 10.0},
            {"time": 9.5, "source": "s", "amount": 20.0},
        ]
        gen = TimelineGenerator(tick_size=0.5)
        dataset = gen.generate_damage_timeline(events)
        assert dataset.duration == pytest.approx(9.5)


# ===========================================================================
# 3. Heatmap accuracy
# ===========================================================================

class TestHeatmapAccuracy:
    """Cell weight accumulation and normalization."""

    def test_4x4_three_points_at_origin_cell_value(self):
        # All points at (0,0); with only identical points x_range=y_range=0,
        # so _world_to_cell always returns (0,0). Weight with 1.0 each.
        gen = HeatmapGenerator(rows=4, cols=4)
        points = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        heatmap = gen.generate(points, weights=[1.0, 1.0, 1.0])
        # All weight in cell (0,0)
        assert heatmap.grid[0][0] == pytest.approx(3.0)

    def test_4x4_three_points_other_cells_zero(self):
        gen = HeatmapGenerator(rows=4, cols=4)
        points = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        heatmap = gen.generate(points, weights=[1.0, 1.0, 1.0])
        for r in range(4):
            for c in range(4):
                if not (r == 0 and c == 0):
                    assert heatmap.grid[r][c] == pytest.approx(0.0)

    def test_normalized_max_cell_is_1(self):
        gen = HeatmapGenerator(rows=4, cols=4)
        points = [(0.0, 0.0)] * 5
        heatmap = gen.generate(points)
        max_normalized = max(c.normalized for c in heatmap.cells)
        assert max_normalized == pytest.approx(1.0)

    def test_normalized_non_max_cells_are_zero_for_identical_positions(self):
        gen = HeatmapGenerator(rows=4, cols=4)
        points = [(0.0, 0.0)] * 5
        heatmap = gen.generate(points)
        for cell in heatmap.cells:
            if not (cell.row == 0 and cell.col == 0):
                assert cell.normalized == pytest.approx(0.0)

    def test_max_value_equals_total_weight_at_single_point(self):
        gen = HeatmapGenerator(rows=5, cols=5)
        points = [(0.0, 0.0)] * 7
        heatmap = gen.generate(points, weights=[1.0] * 7)
        assert heatmap.max_value == pytest.approx(7.0)

    def test_weighted_points_accumulate_correctly(self):
        gen = HeatmapGenerator(rows=5, cols=5)
        # Two points at (0,0) with weights 3 and 5 → total 8
        points = [(0.0, 0.0), (0.0, 0.0)]
        heatmap = gen.generate(points, weights=[3.0, 5.0])
        assert heatmap.grid[0][0] == pytest.approx(8.0)

    def test_heatmap_total_weight_conserved(self):
        gen = HeatmapGenerator(rows=10, cols=10)
        points = [(float(i % 5), float(i % 3)) for i in range(20)]
        weights = [2.0] * 20
        heatmap = gen.generate(points, weights)
        total = sum(heatmap.grid[r][c] for r in range(heatmap.rows) for c in range(heatmap.cols))
        assert total == pytest.approx(40.0)

    def test_empty_heatmap_max_value_zero(self):
        gen = HeatmapGenerator(rows=5, cols=5)
        heatmap = gen.generate([])
        assert heatmap.max_value == pytest.approx(0.0)


# ===========================================================================
# 4. MetricSummary accuracy
# ===========================================================================

class TestMetricSummaryAccuracy:
    """DPS, crit rate, peak_dps, mean_dps, buff uptime calculations."""

    def test_crit_rate_two_crits_out_of_ten(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": float(i), "source": "skill_a", "amount": 100.0, "is_crit": i < 2}
            for i in range(10)
        ]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        skill_a = next(b for b in breakdown if b.source == "skill_a")
        assert skill_a.crit_rate == pytest.approx(0.2)

    def test_crit_count_two_crits_out_of_ten(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": float(i), "source": "skill_a", "amount": 100.0, "is_crit": i < 2}
            for i in range(10)
        ]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        skill_a = next(b for b in breakdown if b.source == "skill_a")
        assert skill_a.crit_count == 2

    def test_dps_equals_total_damage_divided_by_duration(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": float(i), "source": "fire", "amount": 50.0, "is_crit": False}
            for i in range(20)
        ]
        duration = 10.0
        breakdown = engine.compute_dps_breakdown(events, duration=duration)
        fire = next(b for b in breakdown if b.source == "fire")
        expected_dps = fire.total_damage / duration
        assert fire.dps == pytest.approx(expected_dps, rel=1e-6)

    def test_total_damage_sum(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": float(i), "source": "skill_a", "amount": 123.456, "is_crit": False}
            for i in range(5)
        ]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        skill_a = next(b for b in breakdown if b.source == "skill_a")
        assert skill_a.total_damage == pytest.approx(5 * 123.456)

    def test_peak_dps_all_damage_in_one_tick(self):
        engine = MetricSummaryEngine()
        tick_size = 0.5
        # All events at t=0.0 so they land in tick 0
        events = [
            {"time": 0.0, "source": "s", "amount": 100.0, "is_crit": False}
            for _ in range(5)
        ]
        summary = engine.summarize(events, [], [], duration=10.0, tick_size=tick_size)
        # Total in tick = 500.0; peak_dps = 500 / 0.5 = 1000
        assert summary.peak_dps == pytest.approx(500.0 / tick_size, rel=1e-6)

    def test_mean_dps_single_tick_equals_peak_dps(self):
        engine = MetricSummaryEngine()
        events = [{"time": 0.0, "source": "s", "amount": 200.0, "is_crit": False}]
        summary = engine.summarize(events, [], [], duration=10.0, tick_size=1.0)
        assert summary.mean_dps == pytest.approx(summary.peak_dps, rel=1e-6)

    def test_overall_dps_matches_manual(self):
        engine = MetricSummaryEngine()
        events = [
            {"time": float(i), "source": "s", "amount": 250.0, "is_crit": False}
            for i in range(4)
        ]
        summary = engine.summarize(events, [], [], duration=10.0, tick_size=1.0)
        assert summary.overall_dps == pytest.approx(1000.0 / 10.0, rel=1e-6)

    def test_buff_uptime_pct_half_duration(self):
        engine = MetricSummaryEngine()
        buff_events = [
            {"time": 0.0, "buff_name": "shield", "event": "applied"},
            {"time": 5.0, "buff_name": "shield", "event": "expired"},
        ]
        uptimes = engine.compute_buff_uptimes(buff_events, duration=10.0)
        assert uptimes[0].uptime_pct == pytest.approx(0.5)

    def test_kill_times_sorted(self):
        engine = MetricSummaryEngine()
        kill_events = [{"time": 9.0}, {"time": 3.0}, {"time": 6.0}]
        kill_times = engine.compute_kill_times(kill_events)
        assert kill_times == sorted(kill_times)

    def test_kill_times_values_correct(self):
        engine = MetricSummaryEngine()
        kill_events = [{"time": 2.5}, {"time": 7.0}]
        kill_times = engine.compute_kill_times(kill_events)
        assert kill_times == pytest.approx([2.5, 7.0])

    def test_zero_duration_dps_is_zero(self):
        engine = MetricSummaryEngine()
        events = [{"time": 0.0, "source": "s", "amount": 100.0, "is_crit": False}]
        breakdown = engine.compute_dps_breakdown(events, duration=0.0)
        assert breakdown[0].dps == pytest.approx(0.0)

    def test_no_crits_crit_rate_zero(self):
        engine = MetricSummaryEngine()
        events = [{"time": float(i), "source": "s", "amount": 50.0, "is_crit": False} for i in range(5)]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        assert breakdown[0].crit_rate == pytest.approx(0.0)

    def test_all_crits_crit_rate_one(self):
        engine = MetricSummaryEngine()
        events = [{"time": float(i), "source": "s", "amount": 50.0, "is_crit": True} for i in range(5)]
        breakdown = engine.compute_dps_breakdown(events, duration=10.0)
        assert breakdown[0].crit_rate == pytest.approx(1.0)


# ===========================================================================
# 5. ReplayBuilder accuracy
# ===========================================================================

class TestReplayBuilderAccuracy:
    """Frame indices, time-based lookup, entity data preservation."""

    def _entity(self, eid: str, x: float = 0.0, y: float = 0.0) -> ReplayEntity:
        return ReplayEntity(entity_id=eid, position=(x, y), health=100.0, is_alive=True)

    def test_frame_indices_sequential_from_zero(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in range(6):
            builder.add_frame(time=float(t), entities=[self._entity("e")])
        replay = builder.build()
        indices = [f.frame_index for f in replay.frames]
        assert indices == list(range(6))

    def test_get_frame_at_time_returns_closest_frame(self):
        builder = CombatReplayBuilder(tick_size=0.5)
        builder.add_frame(time=1.0, entities=[self._entity("a")])
        builder.add_frame(time=2.0, entities=[self._entity("b")])
        # t=1.05 is closer to 1.0 than 2.0
        frame = builder.get_frame_at_time(1.05)
        assert frame is not None
        assert frame.time == pytest.approx(1.0)

    def test_get_frame_at_time_exact_match(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=3.0, entities=[self._entity("e")])
        frame = builder.get_frame_at_time(3.0)
        assert frame is not None
        assert frame.time == pytest.approx(3.0)

    def test_get_frame_at_time_returns_far_frame_when_only_one(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=5.0, entities=[self._entity("e")])
        frame = builder.get_frame_at_time(0.0)
        assert frame is not None
        assert frame.time == pytest.approx(5.0)

    def test_entities_in_frame_match_passed_entities(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        entities = [self._entity("hero", 1.0, 2.0), self._entity("enemy", 3.0, 4.0)]
        builder.add_frame(time=0.0, entities=entities)
        replay = builder.build()
        frame_entities = replay.frames[0].entities
        entity_ids = [e.entity_id for e in frame_entities]
        assert "hero" in entity_ids
        assert "enemy" in entity_ids

    def test_entity_position_preserved(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=0.0, entities=[self._entity("hero", 7.5, 3.2)])
        replay = builder.build()
        hero = replay.frames[0].entities[0]
        assert hero.position == pytest.approx((7.5, 3.2))

    def test_frames_sorted_by_time_in_build(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=3.0, entities=[self._entity("e")])
        builder.add_frame(time=1.0, entities=[self._entity("e")])
        builder.add_frame(time=2.0, entities=[self._entity("e")])
        replay = builder.build()
        times = [f.time for f in replay.frames]
        assert times == sorted(times)

    def test_get_frame_by_index(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in range(5):
            builder.add_frame(time=float(t), entities=[self._entity("e")])
        frame = builder.get_frame(2)
        assert frame is not None
        assert frame.frame_index == 2

    def test_get_frame_none_for_missing_index(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        builder.add_frame(time=0.0, entities=[self._entity("e")])
        assert builder.get_frame(99) is None

    def test_total_frames_count(self):
        builder = CombatReplayBuilder(tick_size=0.1)
        for t in range(7):
            builder.add_frame(time=float(t), entities=[self._entity("e")])
        replay = builder.build()
        assert replay.total_frames == 7


# ===========================================================================
# 6. Cache accuracy
# ===========================================================================

class TestCacheAccuracy:
    """hit_count increments and expired_keys detection."""

    def test_hit_count_starts_at_zero(self):
        cache = VisualCache()
        cache.set("key", "value")
        entry = cache._cache["key"]
        assert entry.hit_count == 0

    def test_hit_count_increments_on_each_get(self):
        cache = VisualCache()
        cache.set("key", "value")
        cache.get("key")
        cache.get("key")
        cache.get("key")
        entry = cache._cache["key"]
        assert entry.hit_count == 3

    def test_hit_count_not_incremented_on_miss(self):
        cache = VisualCache()
        cache.set("key", "value")
        cache.get("nonexistent")
        entry = cache._cache["key"]
        assert entry.hit_count == 0

    def test_total_hits_in_stats(self):
        cache = VisualCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")
        cache.get("a")
        cache.get("b")
        stats = cache.stats()
        assert stats["total_hits"] == 3

    def test_expired_keys_count_in_stats(self):
        cache = VisualCache(default_ttl=10.0)
        cache.set("fresh", "value", ttl=10.0)
        cache.set("stale", "value", ttl=10.0)

        # Mock time.time to make "stale" appear expired
        original_created_at = cache._cache["stale"].created_at
        cache._cache["stale"].created_at = original_created_at - 20.0  # 20s ago, ttl=10 → expired

        stats = cache.stats()
        assert stats["expired_keys"] >= 1

    def test_expired_entry_returns_none(self):
        cache = VisualCache(default_ttl=10.0)
        cache.set("key", "value", ttl=10.0)
        # Backdating the creation time by more than TTL
        cache._cache["key"].created_at -= 20.0
        assert cache.get("key") is None

    def test_evict_expired_removes_stale_entries(self):
        cache = VisualCache(default_ttl=10.0)
        cache.set("a", 1, ttl=10.0)
        cache.set("b", 2, ttl=10.0)
        cache._cache["a"].created_at -= 20.0  # expired
        removed = cache.evict_expired()
        assert removed == 1
        assert cache.get("b") == 2

    def test_zero_ttl_never_expires(self):
        cache = VisualCache()
        cache.set("key", "immortal", ttl=0.0)
        # Even backdating the creation time should not expire it
        cache._cache["key"].created_at -= 1_000_000.0
        assert cache.get("key") == "immortal"

    def test_hit_count_tracks_multiple_keys_independently(self):
        cache = VisualCache()
        cache.set("x", 1)
        cache.set("y", 2)
        cache.get("x")
        cache.get("x")
        cache.get("y")
        assert cache._cache["x"].hit_count == 2
        assert cache._cache["y"].hit_count == 1
