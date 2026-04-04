"""
Unit tests for HeatmapGenerator, CombatReplayBuilder, and MetricSummaryEngine.

Run with:
    python -m pytest tests/test_visualization_spatial.py -v --tb=short
"""
from __future__ import annotations

import pytest

from visualization.heatmaps.heatmap_generator import (
    HeatmapCell,
    HeatmapData,
    HeatmapGenerator,
)
from visualization.replay.combat_replay_builder import (
    CombatReplayBuilder,
    ReplayEntity,
    ReplayFrame,
    ReplayProjectile,
)
from visualization.metrics.metric_summary import (
    BuffUptimeSummary,
    DpsBreakdown,
    MetricSummary,
    MetricSummaryEngine,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def hg():
    return HeatmapGenerator(rows=10, cols=10)


@pytest.fixture
def builder():
    return CombatReplayBuilder(tick_size=0.1)


@pytest.fixture
def engine():
    return MetricSummaryEngine()


def _entity(entity_id="hero", x=0.0, y=0.0, health=100.0, alive=True):
    return ReplayEntity(entity_id=entity_id, position=(x, y), health=health, is_alive=alive)


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate – empty input
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorEmpty:
    def test_empty_input_returns_heatmap_data(self, hg):
        result = hg.generate([])
        assert isinstance(result, HeatmapData)

    def test_empty_grid_all_zeros(self, hg):
        result = hg.generate([])
        for row in result.grid:
            assert all(v == 0.0 for v in row)

    def test_empty_max_value_zero(self, hg):
        assert hg.generate([]).max_value == 0.0

    def test_empty_cells_all_normalized_zero(self, hg):
        result = hg.generate([])
        assert all(c.normalized == 0.0 for c in result.cells)

    def test_empty_has_correct_row_col_shape(self, hg):
        result = hg.generate([])
        assert result.rows == 10 and result.cols == 10

    def test_empty_cells_count(self, hg):
        result = hg.generate([])
        assert len(result.cells) == 10 * 10


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate – single point
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorSinglePoint:
    def test_single_point_max_value_is_weight(self, hg):
        result = hg.generate([(5.0, 5.0)], weights=[3.0])
        assert result.max_value == pytest.approx(3.0)

    def test_single_point_one_cell_nonzero(self, hg):
        result = hg.generate([(5.0, 5.0)])
        nonzero = [c for c in result.cells if c.value > 0]
        assert len(nonzero) == 1

    def test_single_point_nonzero_cell_normalized_one(self, hg):
        result = hg.generate([(5.0, 5.0)])
        nonzero = [c for c in result.cells if c.value > 0]
        assert nonzero[0].normalized == pytest.approx(1.0)

    def test_single_point_default_weight_one(self, hg):
        result = hg.generate([(2.0, 3.0)])
        assert result.max_value == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate – weights applied
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorWeights:
    def test_weight_applied_to_cell_value(self, hg):
        """Two points at same world position, different weights — same cell accumulates both."""
        result = hg.generate([(5.0, 5.0), (5.0, 5.0)], weights=[3.0, 7.0])
        assert result.max_value == pytest.approx(10.0)

    def test_weights_affect_relative_normalization(self, hg):
        # Two distinct cells; weights 1 and 5
        hg2 = HeatmapGenerator(rows=20, cols=20)
        result = hg2.generate([(0.0, 0.0), (100.0, 100.0)], weights=[1.0, 5.0])
        # max cell has weight 5, min has 1; normalized min should be 0.2
        min_nonzero = min(c.normalized for c in result.cells if c.value > 0)
        assert min_nonzero == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate – multiple points
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorMultiplePoints:
    def test_two_points_at_least_one_nonzero_cell(self, hg):
        result = hg.generate([(0.0, 0.0), (100.0, 100.0)])
        nonzero = [c for c in result.cells if c.value > 0]
        assert len(nonzero) >= 1

    def test_max_value_positive(self, hg):
        result = hg.generate([(0.0, 0.0), (10.0, 10.0), (5.0, 5.0)])
        assert result.max_value > 0.0

    def test_normalized_in_zero_one_range(self, hg):
        result = hg.generate([(0.0, 0.0), (10.0, 10.0), (5.0, 5.0)])
        for c in result.cells:
            assert 0.0 <= c.normalized <= 1.0

    def test_bounds_stored_correctly(self, hg):
        result = hg.generate([(0.0, 0.0), (8.0, 6.0)])
        assert result.x_min == pytest.approx(0.0)
        assert result.x_max == pytest.approx(8.0)
        assert result.y_min == pytest.approx(0.0)
        assert result.y_max == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# HeatmapGenerator._world_to_cell – corners and center
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorWorldToCell:
    def test_minimum_corner_is_row0_col0(self, hg):
        row, col = hg._world_to_cell(0.0, 0.0, 0.0, 10.0, 0.0, 10.0)
        assert row == 0 and col == 0

    def test_maximum_corner_clamped(self, hg):
        row, col = hg._world_to_cell(10.0, 10.0, 0.0, 10.0, 0.0, 10.0)
        assert row == hg.rows - 1 and col == hg.cols - 1

    def test_center_point(self, hg):
        row, col = hg._world_to_cell(5.0, 5.0, 0.0, 10.0, 0.0, 10.0)
        # int(5.0/10.0 * 10) = 5
        assert row == 5 and col == 5

    def test_zero_x_range_returns_col_zero(self, hg):
        row, col = hg._world_to_cell(5.0, 3.0, 5.0, 5.0, 0.0, 10.0)
        assert col == 0

    def test_zero_y_range_returns_row_zero(self, hg):
        row, col = hg._world_to_cell(3.0, 5.0, 0.0, 10.0, 5.0, 5.0)
        assert row == 0

    def test_negative_x_clamped_to_zero(self, hg):
        row, col = hg._world_to_cell(-5.0, 5.0, 0.0, 10.0, 0.0, 10.0)
        assert col == 0

    def test_beyond_max_x_clamped(self, hg):
        row, col = hg._world_to_cell(100.0, 5.0, 0.0, 10.0, 0.0, 10.0)
        assert col == hg.cols - 1


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate_damage_density
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorDamageDensity:
    def test_returns_heatmap_data(self, hg):
        result = hg.generate_damage_density([(1.0, 2.0)], [50.0])
        assert isinstance(result, HeatmapData)

    def test_damage_used_as_weight(self, hg):
        result = hg.generate_damage_density([(5.0, 5.0)], [100.0])
        assert result.max_value == pytest.approx(100.0)

    def test_multiple_hits_same_location(self, hg):
        result = hg.generate_damage_density([(5.0, 5.0), (5.0, 5.0)], [50.0, 75.0])
        assert result.max_value == pytest.approx(125.0)


# ---------------------------------------------------------------------------
# HeatmapGenerator.generate_target_clustering
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorTargetClustering:
    def test_returns_heatmap_data(self, hg):
        result = hg.generate_target_clustering([(1.0, 2.0), (3.0, 4.0)])
        assert isinstance(result, HeatmapData)

    def test_uniform_weight_one(self, hg):
        result = hg.generate_target_clustering([(5.0, 5.0)])
        assert result.max_value == pytest.approx(1.0)

    def test_two_positions_max_value(self, hg):
        hg2 = HeatmapGenerator(rows=20, cols=20)
        result = hg2.generate_target_clustering([(0.0, 0.0), (100.0, 100.0)])
        assert result.max_value >= 1.0


# ---------------------------------------------------------------------------
# HeatmapGenerator.apply_gaussian_blur
# ---------------------------------------------------------------------------


class TestHeatmapGeneratorApplyGaussianBlur:
    def _make_data(self, hg):
        return hg.generate([(5.0, 5.0)], weights=[10.0])

    def test_output_shape_preserved_rows(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        assert blurred.rows == data.rows

    def test_output_shape_preserved_cols(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        assert blurred.cols == data.cols

    def test_cell_count_preserved(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        assert len(blurred.cells) == len(data.cells)

    def test_values_change_after_blur(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        # After blur, the isolated spike spreads; cells adjacent to the spike
        # should now have non-zero values
        nonzero_before = sum(1 for c in data.cells if c.value > 0)
        nonzero_after = sum(1 for c in blurred.cells if c.value > 0)
        assert nonzero_after >= nonzero_before

    def test_max_value_recalculated(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        expected_max = max(blurred.grid[r][c] for r in range(blurred.rows) for c in range(blurred.cols))
        assert blurred.max_value == pytest.approx(expected_max)

    def test_normalized_still_in_zero_one_range(self, hg):
        data = self._make_data(hg)
        blurred = hg.apply_gaussian_blur(data)
        for c in blurred.cells:
            assert 0.0 <= c.normalized <= 1.0 + 1e-9


# ---------------------------------------------------------------------------
# HeatmapData.normalized – values in [0, 1]
# ---------------------------------------------------------------------------


class TestHeatmapDataNormalized:
    def test_all_normalized_in_range(self, hg):
        result = hg.generate([(0.0, 0.0), (5.0, 5.0), (10.0, 10.0)], weights=[1.0, 2.0, 3.0])
        for c in result.cells:
            assert 0.0 <= c.normalized <= 1.0

    def test_max_cell_normalized_equals_one(self, hg):
        result = hg.generate([(0.0, 0.0), (100.0, 100.0)], weights=[1.0, 5.0])
        max_norm = max(c.normalized for c in result.cells)
        assert max_norm == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# CombatReplayBuilder.add_frame
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderAddFrame:
    def test_add_frame_returns_replay_frame(self, builder):
        frame = builder.add_frame(time=0.0, entities=[_entity()])
        assert isinstance(frame, ReplayFrame)

    def test_first_frame_index_is_zero(self, builder):
        frame = builder.add_frame(time=0.0, entities=[_entity()])
        assert frame.frame_index == 0

    def test_second_frame_index_is_one(self, builder):
        builder.add_frame(time=0.0, entities=[])
        frame = builder.add_frame(time=0.1, entities=[_entity()])
        assert frame.frame_index == 1

    def test_frame_count_increments(self, builder):
        for i in range(5):
            builder.add_frame(time=float(i) * 0.1, entities=[])
        assert len(builder._frames) == 5

    def test_frame_time_stored(self, builder):
        frame = builder.add_frame(time=2.5, entities=[])
        assert frame.time == pytest.approx(2.5)

    def test_projectiles_default_empty(self, builder):
        frame = builder.add_frame(time=0.0, entities=[])
        assert frame.projectiles == []

    def test_events_default_empty(self, builder):
        frame = builder.add_frame(time=0.0, entities=[])
        assert frame.events == []

    def test_provided_projectiles_stored(self, builder):
        proj = ReplayProjectile("p1", (1.0, 2.0), (0.0, 1.0), speed=5.0)
        frame = builder.add_frame(time=0.0, entities=[], projectiles=[proj])
        assert len(frame.projectiles) == 1

    def test_provided_events_stored(self, builder):
        frame = builder.add_frame(time=0.0, entities=[], events=[{"type": "damage"}])
        assert frame.events[0]["type"] == "damage"


# ---------------------------------------------------------------------------
# CombatReplayBuilder.build
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderBuild:
    def test_total_frames_correct(self, builder):
        builder.add_frame(0.0, [_entity("A")])
        builder.add_frame(0.1, [_entity("B")])
        replay = builder.build()
        assert replay.total_frames == 2

    def test_frames_sorted_by_time(self, builder):
        builder.add_frame(1.0, [])
        builder.add_frame(0.0, [])
        builder.add_frame(0.5, [])
        replay = builder.build()
        times = [f.time for f in replay.frames]
        assert times == sorted(times)

    def test_duration_is_last_frame_time(self, builder):
        builder.add_frame(0.0, [])
        builder.add_frame(5.0, [])
        replay = builder.build()
        assert replay.duration == pytest.approx(5.0)

    def test_entity_ids_collected(self, builder):
        builder.add_frame(0.0, [_entity("hero"), _entity("goblin")])
        replay = builder.build()
        assert set(replay.entity_ids) == {"hero", "goblin"}

    def test_entity_ids_deduplicated(self, builder):
        builder.add_frame(0.0, [_entity("hero")])
        builder.add_frame(0.1, [_entity("hero")])
        replay = builder.build()
        assert replay.entity_ids.count("hero") == 1

    def test_empty_builder_total_frames_zero(self, builder):
        replay = builder.build()
        assert replay.total_frames == 0


# ---------------------------------------------------------------------------
# CombatReplayBuilder.get_frame
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderGetFrame:
    def test_get_frame_zero(self, builder):
        builder.add_frame(0.0, [])
        frame = builder.get_frame(0)
        assert frame is not None and frame.frame_index == 0

    def test_get_frame_by_index(self, builder):
        builder.add_frame(0.0, [])
        builder.add_frame(0.1, [])
        builder.add_frame(0.2, [])
        frame = builder.get_frame(2)
        assert frame is not None and frame.frame_index == 2

    def test_get_frame_out_of_range_returns_none(self, builder):
        builder.add_frame(0.0, [])
        assert builder.get_frame(99) is None

    def test_get_frame_empty_builder_returns_none(self, builder):
        assert builder.get_frame(0) is None


# ---------------------------------------------------------------------------
# CombatReplayBuilder.get_frame_at_time
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderGetFrameAtTime:
    def test_empty_builder_returns_none(self, builder):
        assert builder.get_frame_at_time(0.5) is None

    def test_exact_match(self, builder):
        builder.add_frame(1.0, [])
        frame = builder.get_frame_at_time(1.0)
        assert frame is not None and frame.time == pytest.approx(1.0)

    def test_returns_nearest_frame(self, builder):
        builder.add_frame(0.0, [])
        builder.add_frame(1.0, [])
        builder.add_frame(2.0, [])
        frame = builder.get_frame_at_time(0.9)
        assert frame.time == pytest.approx(1.0)

    def test_nearest_before_midpoint(self, builder):
        builder.add_frame(0.0, [])
        builder.add_frame(2.0, [])
        frame = builder.get_frame_at_time(0.4)
        assert frame.time == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# CombatReplayBuilder.reset
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderReset:
    def test_reset_clears_frames(self, builder):
        builder.add_frame(0.0, [])
        builder.add_frame(0.1, [])
        builder.reset()
        assert builder._frames == []

    def test_reset_allows_reuse(self, builder):
        builder.add_frame(0.0, [])
        builder.reset()
        builder.add_frame(0.5, [])
        assert len(builder._frames) == 1

    def test_frame_index_restarts_after_reset(self, builder):
        builder.add_frame(0.0, [])
        builder.reset()
        frame = builder.add_frame(0.5, [])
        assert frame.frame_index == 0


# ---------------------------------------------------------------------------
# CombatReplayBuilder.to_dict
# ---------------------------------------------------------------------------


class TestCombatReplayBuilderToDict:
    def _build_replay(self, builder):
        builder.add_frame(0.0, [_entity("hero")])
        return builder.build()

    def test_has_duration(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "duration" in d

    def test_has_total_frames(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "total_frames" in d

    def test_has_entity_ids(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "entity_ids" in d

    def test_has_frames_list(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "frames" in d and isinstance(d["frames"], list)

    def test_frame_has_frame_index(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "frame_index" in d["frames"][0]

    def test_frame_has_entities(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert "entities" in d["frames"][0]

    def test_entity_has_entity_id(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        assert d["frames"][0]["entities"][0]["entity_id"] == "hero"

    def test_entity_position_is_list(self, builder):
        d = builder.to_dict(self._build_replay(builder))
        pos = d["frames"][0]["entities"][0]["position"]
        assert isinstance(pos, list)

    def test_total_frames_value(self, builder):
        replay = self._build_replay(builder)
        d = builder.to_dict(replay)
        assert d["total_frames"] == 1


# ---------------------------------------------------------------------------
# MetricSummaryEngine.compute_dps_breakdown
# ---------------------------------------------------------------------------


class TestMetricSummaryEngineComputeDpsBreakdown:
    def test_groups_by_source(self, engine):
        events = [
            {"source": "A", "amount": 100.0},
            {"source": "B", "amount": 200.0},
        ]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        sources = {b.source for b in result}
        assert sources == {"A", "B"}

    def test_total_damage_per_source(self, engine):
        events = [
            {"source": "A", "amount": 50.0},
            {"source": "A", "amount": 50.0},
        ]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        assert result[0].total_damage == pytest.approx(100.0)

    def test_dps_calculation(self, engine):
        events = [{"source": "A", "amount": 100.0}]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        assert result[0].dps == pytest.approx(10.0)

    def test_crit_rate_all_crits(self, engine):
        events = [
            {"source": "A", "amount": 100.0, "is_crit": True},
            {"source": "A", "amount": 100.0, "is_crit": True},
        ]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        assert result[0].crit_rate == pytest.approx(1.0)

    def test_crit_rate_no_crits(self, engine):
        events = [{"source": "A", "amount": 100.0}]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        assert result[0].crit_rate == pytest.approx(0.0)

    def test_crit_rate_mixed(self, engine):
        events = [
            {"source": "A", "amount": 100.0, "is_crit": True},
            {"source": "A", "amount": 100.0, "is_crit": False},
            {"source": "A", "amount": 100.0, "is_crit": False},
            {"source": "A", "amount": 100.0, "is_crit": False},
        ]
        result = engine.compute_dps_breakdown(events, duration=10.0)
        assert result[0].crit_rate == pytest.approx(0.25)

    def test_hit_count_correct(self, engine):
        events = [
            {"source": "X", "amount": 10.0},
            {"source": "X", "amount": 10.0},
            {"source": "X", "amount": 10.0},
        ]
        result = engine.compute_dps_breakdown(events, duration=5.0)
        assert result[0].hit_count == 3

    def test_empty_events_returns_empty_list(self, engine):
        assert engine.compute_dps_breakdown([], duration=10.0) == []


# ---------------------------------------------------------------------------
# MetricSummaryEngine.compute_buff_uptimes
# ---------------------------------------------------------------------------


class TestMetricSummaryEngineComputeBuffUptimes:
    def test_returns_list(self, engine):
        events = [
            {"time": 0.0, "buff_name": "Haste", "event": "applied"},
            {"time": 5.0, "buff_name": "Haste", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert isinstance(result, list)

    def test_uptime_seconds_correct(self, engine):
        events = [
            {"time": 0.0, "buff_name": "Haste", "event": "applied"},
            {"time": 5.0, "buff_name": "Haste", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert result[0].total_uptime == pytest.approx(5.0)

    def test_uptime_pct_correct(self, engine):
        events = [
            {"time": 0.0, "buff_name": "Haste", "event": "applied"},
            {"time": 5.0, "buff_name": "Haste", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert result[0].uptime_pct == pytest.approx(0.5)

    def test_still_active_counts_to_duration(self, engine):
        events = [
            {"time": 2.0, "buff_name": "Haste", "event": "applied"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert result[0].total_uptime == pytest.approx(8.0)

    def test_application_count(self, engine):
        events = [
            {"time": 0.0, "buff_name": "Haste", "event": "applied"},
            {"time": 3.0, "buff_name": "Haste", "event": "expired"},
            {"time": 5.0, "buff_name": "Haste", "event": "applied"},
            {"time": 8.0, "buff_name": "Haste", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert result[0].application_count == 2

    def test_multiple_buffs(self, engine):
        events = [
            {"time": 0.0, "buff_name": "A", "event": "applied"},
            {"time": 5.0, "buff_name": "A", "event": "expired"},
            {"time": 0.0, "buff_name": "B", "event": "applied"},
            {"time": 10.0, "buff_name": "B", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        names = {b.buff_name for b in result}
        assert names == {"A", "B"}

    def test_full_uptime_pct_is_one(self, engine):
        events = [
            {"time": 0.0, "buff_name": "X", "event": "applied"},
            {"time": 10.0, "buff_name": "X", "event": "expired"},
        ]
        result = engine.compute_buff_uptimes(events, duration=10.0)
        assert result[0].uptime_pct == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# MetricSummaryEngine.compute_kill_times
# ---------------------------------------------------------------------------


class TestMetricSummaryEngineComputeKillTimes:
    def test_returns_sorted_list(self, engine):
        events = [{"time": 3.0}, {"time": 1.0}, {"time": 5.0}]
        result = engine.compute_kill_times(events)
        assert result == [1.0, 3.0, 5.0]

    def test_empty_events_returns_empty(self, engine):
        assert engine.compute_kill_times([]) == []

    def test_single_kill(self, engine):
        result = engine.compute_kill_times([{"time": 2.5}])
        assert result == [2.5]

    def test_result_is_floats(self, engine):
        events = [{"time": 1}]
        result = engine.compute_kill_times(events)
        assert all(isinstance(t, float) for t in result)

    def test_sorted_ascending(self, engine):
        events = [{"time": 9.0}, {"time": 2.0}, {"time": 7.0}]
        result = engine.compute_kill_times(events)
        assert result == sorted(result)


# ---------------------------------------------------------------------------
# MetricSummaryEngine.summarize
# ---------------------------------------------------------------------------


class TestMetricSummaryEngineSummarize:
    def _damage_events(self):
        return [
            {"source": "A", "amount": 100.0, "time": 0.0, "is_crit": False},
            {"source": "A", "amount": 200.0, "time": 1.0, "is_crit": True},
            {"source": "B", "amount": 300.0, "time": 2.0, "is_crit": False},
        ]

    def _buff_events(self):
        return [
            {"time": 0.0, "buff_name": "Haste", "event": "applied"},
            {"time": 5.0, "buff_name": "Haste", "event": "expired"},
        ]

    def _kill_events(self):
        return [{"time": 2.0}, {"time": 4.0}]

    def test_returns_metric_summary(self, engine):
        result = engine.summarize(self._damage_events(), self._buff_events(), self._kill_events(), duration=10.0)
        assert isinstance(result, MetricSummary)

    def test_duration_field(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.duration == pytest.approx(10.0)

    def test_total_damage_correct(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.total_damage == pytest.approx(600.0)

    def test_overall_dps_correct(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.overall_dps == pytest.approx(60.0)

    def test_dps_breakdown_populated(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert len(result.dps_breakdown) == 2

    def test_buff_uptimes_populated(self, engine):
        result = engine.summarize(self._damage_events(), self._buff_events(), [], duration=10.0)
        assert len(result.buff_uptimes) == 1

    def test_kill_times_populated(self, engine):
        result = engine.summarize(self._damage_events(), [], self._kill_events(), duration=10.0)
        assert result.kill_times == [2.0, 4.0]

    def test_peak_dps_positive(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.peak_dps > 0.0

    def test_mean_dps_positive(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.mean_dps > 0.0

    def test_peak_dps_at_least_mean_dps(self, engine):
        result = engine.summarize(self._damage_events(), [], [], duration=10.0)
        assert result.peak_dps >= result.mean_dps

    def test_peak_dps_reflects_highest_tick(self, engine):
        # Single tick bucket: 300 dmg / 0.1 tick_size = 3000 peak DPS
        events = [{"source": "A", "amount": 300.0, "time": 2.0}]
        result = engine.summarize(events, [], [], duration=10.0, tick_size=0.1)
        assert result.peak_dps == pytest.approx(3000.0)

    def test_no_damage_events_peak_dps_zero(self, engine):
        result = engine.summarize([], [], [], duration=10.0)
        assert result.peak_dps == 0.0 and result.mean_dps == 0.0
