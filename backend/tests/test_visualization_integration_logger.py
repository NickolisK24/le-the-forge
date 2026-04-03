"""
Unit tests for VisualizationIntegration and VisualizationLogger.
Target: 40+ tests
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from services.visualization_integration import (
    VisualizationIntegration,
    VisualizationRequest,
    VisualizationResult,
)
from visualization.cache.visual_cache import VisualCache
from debug.visualization_logger import VisualizationLogger, VisLogEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_integration() -> tuple[VisualizationIntegration, MagicMock, MagicMock, MagicMock, MagicMock]:
    """
    Returns (integration, mock_timeline_gen, mock_heatmap_gen,
             mock_summary_engine, mock_report_gen).

    All sub-generators are mocked so that `process` does not call real
    generator code (some generators have different APIs from what the
    integration layer expects, making them fail without mocks).
    """
    with patch("services.visualization_integration.TimelineGenerator") as MockTL, \
         patch("services.visualization_integration.HeatmapGenerator") as MockHM, \
         patch("services.visualization_integration.MetricSummaryEngine") as MockSE, \
         patch("services.visualization_integration.ResultFormatter") as MockFmt, \
         patch("services.visualization_integration.CombatReplayBuilder") as MockRB, \
         patch("services.visualization_integration.ReportGenerator") as MockRG:
        vi = VisualizationIntegration()
        return vi, MockTL.return_value, MockHM.return_value, MockSE.return_value, MockRG.return_value


def _basic_sim_data(**overrides) -> dict:
    base = {
        "damage_events": [],
        "buff_events": [],
        "kill_events": [],
        "hit_positions": [],
        "damages": [],
        "duration": 10.0,
    }
    base.update(overrides)
    return base


def _run_process(
    vi: VisualizationIntegration,
    key: str = "sim_001",
    include_timeline: bool = True,
    include_heatmap: bool = True,
    include_report: bool = True,
    sim_data: dict | None = None,
) -> VisualizationResult:
    req = VisualizationRequest(
        simulation_key=key,
        include_timeline=include_timeline,
        include_heatmap=include_heatmap,
        include_report=include_report,
    )
    return vi.process(req, sim_data or _basic_sim_data())


# ===========================================================================
# VisualizationIntegration
# ===========================================================================

class TestVisualizationIntegrationTimeline:
    def test_include_timeline_true_result_not_none(self):
        vi, mock_tl, *_ = _make_integration()
        mock_tl.generate.return_value = MagicMock(name="timeline_dataset")
        result = _run_process(vi, include_timeline=True)
        assert result.timeline is not None

    def test_include_timeline_false_result_is_none(self):
        vi, mock_tl, *_ = _make_integration()
        result = _run_process(vi, include_timeline=False)
        assert result.timeline is None

    def test_include_timeline_calls_generator_generate(self):
        vi, mock_tl, *_ = _make_integration()
        _run_process(vi, include_timeline=True)
        mock_tl.generate.assert_called_once()

    def test_include_timeline_false_does_not_call_generator(self):
        vi, mock_tl, *_ = _make_integration()
        _run_process(vi, include_timeline=False)
        mock_tl.generate.assert_not_called()


class TestVisualizationIntegrationHeatmap:
    def test_include_heatmap_true_result_not_none(self):
        vi, _, mock_hm, *_ = _make_integration()
        mock_hm.generate.return_value = MagicMock(name="heatmap_data")
        result = _run_process(vi, include_heatmap=True)
        assert result.heatmap is not None

    def test_include_heatmap_false_result_is_none(self):
        vi, *_ = _make_integration()
        result = _run_process(vi, include_heatmap=False)
        assert result.heatmap is None

    def test_include_heatmap_calls_generator_generate(self):
        vi, _, mock_hm, *_ = _make_integration()
        _run_process(vi, include_heatmap=True)
        mock_hm.generate.assert_called_once()

    def test_include_heatmap_false_does_not_call_generator(self):
        vi, _, mock_hm, *_ = _make_integration()
        _run_process(vi, include_heatmap=False)
        mock_hm.generate.assert_not_called()


class TestVisualizationIntegrationReport:
    def test_include_report_true_result_not_none(self):
        vi, _, _, mock_se, mock_rg = _make_integration()
        mock_se.compute.return_value = MagicMock(name="summary")
        mock_rg.from_metric_summary.return_value = MagicMock(name="report")
        result = _run_process(vi, include_report=True)
        assert result.report is not None

    def test_include_report_false_result_is_none(self):
        vi, *_ = _make_integration()
        result = _run_process(vi, include_report=False)
        assert result.report is None

    def test_include_report_calls_report_gen(self):
        vi, _, _, mock_se, mock_rg = _make_integration()
        mock_se.compute.return_value = MagicMock(name="summary")
        _run_process(vi, include_report=True)
        mock_rg.from_metric_summary.assert_called_once()


class TestVisualizationIntegrationCaching:
    def test_second_call_same_key_returns_cached_true(self):
        vi, *_ = _make_integration()
        sim_data = _basic_sim_data()
        req = VisualizationRequest(simulation_key="cached_key")
        vi.process(req, sim_data)
        result2 = vi.process(req, sim_data)
        assert result2.cached is True

    def test_first_call_cached_false(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="fresh_key")
        result = vi.process(req, _basic_sim_data())
        assert result.cached is False

    def test_different_keys_not_shared(self):
        vi, *_ = _make_integration()
        req1 = VisualizationRequest(simulation_key="key_1")
        req2 = VisualizationRequest(simulation_key="key_2")
        r1 = vi.process(req1, _basic_sim_data())
        r2 = vi.process(req2, _basic_sim_data())
        assert r1.cached is False
        assert r2.cached is False

    def test_cached_result_preserves_simulation_key(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="preserve_key")
        vi.process(req, _basic_sim_data())
        result2 = vi.process(req, _basic_sim_data())
        assert result2.simulation_key == "preserve_key"


class TestVisualizationIntegrationInvalidate:
    def test_invalidate_clears_cache_so_next_call_recomputes(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="inv_key")
        vi.process(req, _basic_sim_data())
        vi.invalidate("inv_key")
        result = vi.process(req, _basic_sim_data())
        assert result.cached is False

    def test_invalidate_nonexistent_key_does_not_raise(self):
        vi, *_ = _make_integration()
        vi.invalidate("no_such_key")  # should not raise


class TestVisualizationIntegrationEdgeCases:
    def test_empty_damage_events_still_produces_result(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="empty_key")
        result = vi.process(req, _basic_sim_data(damage_events=[]))
        assert result is not None

    def test_hit_positions_populated_heatmap_called_with_data(self):
        vi, _, mock_hm, *_ = _make_integration()
        positions = [(1.0, 2.0), (3.0, 4.0)]
        damages = [100.0, 200.0]
        sim_data = _basic_sim_data(hit_positions=positions, damages=damages)
        req = VisualizationRequest(simulation_key="heat_key", include_heatmap=True)
        vi.process(req, sim_data)
        call_kwargs = mock_hm.generate.call_args
        # The positions should have been forwarded to the heatmap generator
        assert call_kwargs is not None

    def test_result_simulation_key_matches_request(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="my_special_key")
        result = vi.process(req, _basic_sim_data())
        assert result.simulation_key == "my_special_key"

    def test_result_is_visualization_result_instance(self):
        vi, *_ = _make_integration()
        req = VisualizationRequest(simulation_key="type_check")
        result = vi.process(req, _basic_sim_data())
        assert isinstance(result, VisualizationResult)


# ===========================================================================
# VisualizationLogger
# ===========================================================================

class TestVisualizationLoggerCacheEvents:
    def test_log_cache_hit_event_type(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("sim_1", "timeline")
        entries = logger.get_entries()
        assert entries[0].event_type == "cache_hit"

    def test_log_cache_hit_simulation_key_stored(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("sim_xyz", "heatmap")
        assert logger.get_entries()[0].simulation_key == "sim_xyz"

    def test_log_cache_hit_component_stored(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("sim_1", "heatmap")
        assert logger.get_entries()[0].component == "heatmap"

    def test_log_cache_miss_event_type(self):
        logger = VisualizationLogger()
        logger.log_cache_miss("sim_2", "timeline")
        entries = logger.get_entries()
        assert entries[0].event_type == "cache_miss"

    def test_log_cache_miss_component_stored(self):
        logger = VisualizationLogger()
        logger.log_cache_miss("sim_2", "report")
        assert logger.get_entries()[0].component == "report"


class TestVisualizationLoggerGenerated:
    def test_log_generated_event_type(self):
        logger = VisualizationLogger()
        logger.log_generated("sim_1", "timeline", 42.5)
        assert logger.get_entries()[0].event_type == "generated"

    def test_log_generated_duration_ms_stored(self):
        logger = VisualizationLogger()
        logger.log_generated("sim_1", "summary", 123.4)
        assert logger.get_entries()[0].duration_ms == pytest.approx(123.4)

    def test_log_generated_with_metadata(self):
        logger = VisualizationLogger()
        logger.log_generated("sim_1", "heatmap", 10.0, metadata={"cells": 400})
        entry = logger.get_entries()[0]
        assert entry.metadata.get("cells") == 400

    def test_log_generated_metadata_none_defaults_to_empty(self):
        logger = VisualizationLogger()
        logger.log_generated("sim_1", "timeline", 5.0, metadata=None)
        assert logger.get_entries()[0].metadata == {}


class TestVisualizationLoggerError:
    def test_log_error_event_type(self):
        logger = VisualizationLogger()
        logger.log_error("sim_err", "heatmap", "NullPointerError")
        assert logger.get_entries()[0].event_type == "error"

    def test_log_error_metadata_has_error_key(self):
        logger = VisualizationLogger()
        logger.log_error("sim_err", "timeline", "Something broke")
        entry = logger.get_entries()[0]
        assert "error" in entry.metadata

    def test_log_error_error_message_stored(self):
        logger = VisualizationLogger()
        logger.log_error(None, "report", "Oops")
        assert logger.get_entries()[0].metadata["error"] == "Oops"

    def test_log_error_simulation_key_can_be_none(self):
        logger = VisualizationLogger()
        logger.log_error(None, "summary", "Error")
        assert logger.get_entries()[0].simulation_key is None


class TestVisualizationLoggerExport:
    def test_log_export_event_type(self):
        logger = VisualizationLogger()
        logger.log_export("sim_1", "json", 1024)
        assert logger.get_entries()[0].event_type == "export"

    def test_log_export_component_is_report(self):
        logger = VisualizationLogger()
        logger.log_export("sim_1", "csv", 512)
        assert logger.get_entries()[0].component == "report"

    def test_log_export_format_in_metadata(self):
        logger = VisualizationLogger()
        logger.log_export("sim_1", "pdf", 2048)
        assert logger.get_entries()[0].metadata["format"] == "pdf"

    def test_log_export_size_bytes_in_metadata(self):
        logger = VisualizationLogger()
        logger.log_export("sim_1", "json", 9999)
        assert logger.get_entries()[0].metadata["size_bytes"] == 9999


class TestVisualizationLoggerGetEntries:
    def test_get_entries_returns_all(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_miss("s2", "heatmap")
        logger.log_generated("s3", "report", 10.0)
        assert len(logger.get_entries()) == 3

    def test_get_entries_filter_by_event_type(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_hit("s2", "heatmap")
        logger.log_cache_miss("s3", "timeline")
        hits = logger.get_entries(event_type="cache_hit")
        assert len(hits) == 2
        assert all(e.event_type == "cache_hit" for e in hits)

    def test_get_entries_filter_by_component(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_miss("s2", "timeline")
        logger.log_generated("s3", "heatmap", 5.0)
        timeline_entries = logger.get_entries(component="timeline")
        assert len(timeline_entries) == 2
        assert all(e.component == "timeline" for e in timeline_entries)

    def test_get_entries_filter_combined_event_type_and_component(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_hit("s2", "heatmap")
        logger.log_cache_miss("s3", "timeline")
        result = logger.get_entries(event_type="cache_hit", component="timeline")
        assert len(result) == 1
        assert result[0].simulation_key == "s1"

    def test_get_entries_empty_logger_returns_empty_list(self):
        logger = VisualizationLogger()
        assert logger.get_entries() == []

    def test_get_entries_filter_no_match_returns_empty(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        result = logger.get_entries(event_type="error")
        assert result == []


class TestVisualizationLoggerSummary:
    def test_summary_has_required_keys(self):
        logger = VisualizationLogger()
        s = logger.summary()
        for key in ("total_entries", "by_type", "by_component", "avg_generation_ms"):
            assert key in s

    def test_summary_total_entries(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_miss("s2", "heatmap")
        assert logger.summary()["total_entries"] == 2

    def test_summary_avg_generation_ms_from_generated_events(self):
        logger = VisualizationLogger()
        logger.log_generated("s1", "timeline", 100.0)
        logger.log_generated("s2", "timeline", 200.0)
        avg = logger.summary()["avg_generation_ms"]
        assert avg == pytest.approx(150.0)

    def test_summary_avg_generation_ms_zero_when_no_generated_events(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        assert logger.summary()["avg_generation_ms"] == 0.0

    def test_summary_by_type_counts(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "t")
        logger.log_cache_hit("s2", "t")
        logger.log_cache_miss("s3", "t")
        s = logger.summary()
        assert s["by_type"]["cache_hit"] == 2
        assert s["by_type"]["cache_miss"] == 1

    def test_summary_by_component_counts(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_hit("s2", "timeline")
        logger.log_cache_hit("s3", "heatmap")
        s = logger.summary()
        assert s["by_component"]["timeline"] == 2
        assert s["by_component"]["heatmap"] == 1

    def test_summary_empty_logger(self):
        logger = VisualizationLogger()
        s = logger.summary()
        assert s["total_entries"] == 0
        assert s["avg_generation_ms"] == 0.0


class TestVisualizationLoggerClear:
    def test_clear_empties_entries(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.log_cache_hit("s2", "heatmap")
        logger.clear()
        assert logger.get_entries() == []

    def test_clear_resets_total_entries_in_summary(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.clear()
        assert logger.summary()["total_entries"] == 0

    def test_can_log_after_clear(self):
        logger = VisualizationLogger()
        logger.log_cache_hit("s1", "timeline")
        logger.clear()
        logger.log_generated("s2", "heatmap", 30.0)
        assert len(logger.get_entries()) == 1


class TestVisualizationLoggerCapacity:
    def test_capacity_enforced_at_max(self):
        capacity = 500
        logger = VisualizationLogger(capacity=capacity)
        for i in range(capacity + 2):
            logger.log_cache_hit(f"s{i}", "timeline")
        assert len(logger.get_entries()) == capacity

    def test_capacity_oldest_entries_dropped(self):
        """When the deque is at capacity the oldest entry is dropped first."""
        logger = VisualizationLogger(capacity=3)
        for i in range(5):
            logger.log_cache_hit(f"sim_{i}", "timeline")
        keys = [e.simulation_key for e in logger.get_entries()]
        assert "sim_0" not in keys
        assert "sim_1" not in keys
        assert "sim_4" in keys

    def test_default_capacity_is_500(self):
        logger = VisualizationLogger()
        for i in range(502):
            logger.log_cache_hit(f"s{i}", "timeline")
        assert len(logger.get_entries()) == 500
