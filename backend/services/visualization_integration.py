from __future__ import annotations

from dataclasses import dataclass, field

from visualization.formatters.result_formatter import FormattedDataset, ResultFormatter
from visualization.timeline.timeline_generator import TimelineDataset, TimelineGenerator
from visualization.heatmaps.heatmap_generator import HeatmapData, HeatmapGenerator
from visualization.replay.combat_replay_builder import ReplayData, CombatReplayBuilder
from visualization.metrics.metric_summary import MetricSummary, MetricSummaryEngine
from visualization.reports.report_generator import Report, ReportGenerator
from visualization.cache.visual_cache import VisualCache


@dataclass
class VisualizationRequest:
    simulation_key: str
    include_timeline: bool = True
    include_heatmap: bool = True
    include_replay: bool = False
    include_report: bool = True
    tick_size: float = 0.1
    heatmap_rows: int = 20
    heatmap_cols: int = 20


@dataclass
class VisualizationResult:
    simulation_key: str
    timeline: TimelineDataset | None
    heatmap: HeatmapData | None
    replay: ReplayData | None
    summary: MetricSummary | None
    report: Report | None
    formatted_dataset: FormattedDataset | None
    cached: bool = False


class VisualizationIntegration:
    def __init__(self, cache: VisualCache | None = None) -> None:
        self._cache = cache or VisualCache()
        self._formatter = ResultFormatter()
        self._timeline_gen = TimelineGenerator()
        self._heatmap_gen = HeatmapGenerator()
        self._replay_builder = CombatReplayBuilder()
        self._summary_engine = MetricSummaryEngine()
        self._report_gen = ReportGenerator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        request: VisualizationRequest,
        simulation_data: dict,
    ) -> VisualizationResult:
        """
        Build all requested visualization artifacts for *simulation_data*.

        Expected keys in *simulation_data*:
            damage_events   – list of damage event dicts
            buff_events     – list of buff event dicts
            kill_events     – list of kill event dicts
            hit_positions   – list of (x, y) tuples / coordinate dicts
            damages         – parallel list of damage values for each hit_position
            duration        – total simulation duration in seconds

        Results are cached under *request.simulation_key*.  A cached result
        is returned unchanged on subsequent calls with the same key.
        """
        cached_result: VisualizationResult | None = self._cache.get(request.simulation_key)
        if cached_result is not None:
            # Return a shallow copy with the cached flag set
            return VisualizationResult(
                simulation_key=cached_result.simulation_key,
                timeline=cached_result.timeline,
                heatmap=cached_result.heatmap,
                replay=cached_result.replay,
                summary=cached_result.summary,
                report=cached_result.report,
                formatted_dataset=cached_result.formatted_dataset,
                cached=True,
            )

        damage_events: list = simulation_data.get("damage_events", [])
        buff_events: list = simulation_data.get("buff_events", [])
        kill_events: list = simulation_data.get("kill_events", [])
        hit_positions: list = simulation_data.get("hit_positions", [])
        damages: list = simulation_data.get("damages", [])
        duration: float = float(simulation_data.get("duration", 0.0))

        # --- Timeline ---
        timeline: TimelineDataset | None = None
        if request.include_timeline:
            timeline = self._timeline_gen.generate(
                damage_events=damage_events,
                buff_events=buff_events,
                kill_events=kill_events,
                tick_size=request.tick_size,
                duration=duration,
            )

        # --- Heatmap ---
        heatmap: HeatmapData | None = None
        if request.include_heatmap:
            heatmap = self._heatmap_gen.generate(
                positions=hit_positions,
                damages=damages,
                rows=request.heatmap_rows,
                cols=request.heatmap_cols,
            )

        # --- Replay (requires full frame data — not available here) ---
        replay: ReplayData | None = None

        # --- Metric summary ---
        summary: MetricSummary | None = None
        formatted_dataset: FormattedDataset | None = None
        report: Report | None = None

        # Build summary regardless so the report can use it
        summary = self._summary_engine.compute(
            damage_events=damage_events,
            buff_events=buff_events,
            kill_events=kill_events,
            duration=duration,
        )

        # Formatted dataset (always computed alongside summary)
        formatted_dataset = self._formatter.format(
            damage_events=damage_events,
            buff_events=buff_events,
            kill_events=kill_events,
            duration=duration,
        )

        # --- Report ---
        if request.include_report and summary is not None:
            report = self._report_gen.from_metric_summary(summary)

        result = VisualizationResult(
            simulation_key=request.simulation_key,
            timeline=timeline,
            heatmap=heatmap,
            replay=replay,
            summary=summary,
            report=report,
            formatted_dataset=formatted_dataset,
            cached=False,
        )

        self._cache.set(request.simulation_key, result)
        return result

    def invalidate(self, simulation_key: str) -> None:
        """Remove a cached result for the given simulation key."""
        self._cache.invalidate(simulation_key)
