from __future__ import annotations

from dataclasses import dataclass, field

from visualization.metrics.metric_summary import MetricSummary, MetricSummaryEngine


@dataclass
class BuildMetricSnapshot:
    build_id: str
    label: str
    total_damage: float
    dps: float
    crit_rate: float
    buff_uptime_pct: float   # average across all buffs
    kill_time: float | None  # first kill time or None
    reliability_score: float  # 0.0-1.0


@dataclass
class ComparisonDataset:
    builds: list[BuildMetricSnapshot]
    metric_names: list[str]   # ["total_damage", "dps", "crit_rate", ...]
    differential: dict[str, float]  # build_b_metric - build_a_metric for each metric
    winner_by_metric: dict[str, str]  # metric_name -> build_id of winner


_NUMERIC_METRICS: list[str] = [
    "total_damage",
    "dps",
    "crit_rate",
    "buff_uptime_pct",
    "reliability_score",
]

_KILL_TIME_METRIC = "kill_time"


class ComparisonDatasetBuilder:
    def __init__(self) -> None:
        self._builds: list[BuildMetricSnapshot] = []

    def add_build(self, snapshot: BuildMetricSnapshot) -> None:
        """Append a build snapshot to the internal list."""
        self._builds.append(snapshot)

    def build_comparison(self) -> ComparisonDataset:
        """
        Build a ComparisonDataset from the accumulated snapshots.

        Requires at least 2 builds. Uses the first two for differential
        and per-metric winner calculations. Kill time winner is the build
        with the *lower* value (faster kill); None values are treated as
        losing to a non-None value.
        """
        if len(self._builds) < 2:
            raise ValueError(
                "At least 2 builds are required to build a comparison; "
                f"got {len(self._builds)}."
            )

        a = self._builds[0]
        b = self._builds[1]

        metric_names = _NUMERIC_METRICS + [_KILL_TIME_METRIC]

        differential: dict[str, float] = {}
        winner_by_metric: dict[str, str] = {}

        # Numeric metrics — higher is better
        for metric in _NUMERIC_METRICS:
            val_a: float = getattr(a, metric)
            val_b: float = getattr(b, metric)
            differential[metric] = val_b - val_a
            winner_by_metric[metric] = b.build_id if val_b >= val_a else a.build_id

        # Kill time — lower is better; None means no kill recorded
        kt_a: float | None = a.kill_time
        kt_b: float | None = b.kill_time

        if kt_a is None and kt_b is None:
            diff_kt = 0.0
            winner_kt = a.build_id  # arbitrary tie-break to first build
        elif kt_a is None:
            diff_kt = 0.0  # b has a kill, a does not — b wins
            winner_kt = b.build_id
        elif kt_b is None:
            diff_kt = 0.0  # a has a kill, b does not — a wins
            winner_kt = a.build_id
        else:
            diff_kt = kt_b - kt_a  # negative means b killed faster
            winner_kt = b.build_id if kt_b <= kt_a else a.build_id

        differential[_KILL_TIME_METRIC] = diff_kt
        winner_by_metric[_KILL_TIME_METRIC] = winner_kt

        return ComparisonDataset(
            builds=list(self._builds),
            metric_names=metric_names,
            differential=differential,
            winner_by_metric=winner_by_metric,
        )

    def from_metric_summaries(
        self,
        summaries: list[tuple[str, str, MetricSummary]],
    ) -> ComparisonDataset:
        """
        Construct a ComparisonDataset from a list of (build_id, label, MetricSummary)
        tuples. Each MetricSummary is converted to a BuildMetricSnapshot
        (reliability_score defaults to 1.0 as a placeholder).
        """
        self.reset()

        for build_id, label, summary in summaries:
            # Total damage: sum across all damage sources
            total_damage: float = sum(
                getattr(src, "total_damage", 0.0)
                for src in getattr(summary, "damage_by_source", {}).values()
            )

            # DPS: sum across all damage sources
            dps: float = sum(
                getattr(src, "dps", 0.0)
                for src in getattr(summary, "damage_by_source", {}).values()
            )

            # Crit rate: weighted average across sources by hit count
            total_hits = 0
            total_crits = 0
            for src in getattr(summary, "damage_by_source", {}).values():
                total_hits += getattr(src, "hit_count", 0)
                total_crits += getattr(src, "crit_count", 0)
            crit_rate = (total_crits / total_hits) if total_hits > 0 else 0.0

            # Buff uptime: average uptime_pct across all tracked buffs
            buff_uptimes = getattr(summary, "buff_uptimes", {})
            if buff_uptimes:
                uptime_values = [
                    getattr(b, "uptime_pct", 0.0) for b in buff_uptimes.values()
                ]
                buff_uptime_pct = sum(uptime_values) / len(uptime_values)
            else:
                buff_uptime_pct = 0.0

            # Kill time: first entry from kill_times list
            kill_times: list[float] = getattr(summary, "kill_times", [])
            kill_time: float | None = kill_times[0] if kill_times else None

            snapshot = BuildMetricSnapshot(
                build_id=build_id,
                label=label,
                total_damage=total_damage,
                dps=dps,
                crit_rate=crit_rate,
                buff_uptime_pct=buff_uptime_pct,
                kill_time=kill_time,
                reliability_score=1.0,
            )
            self.add_build(snapshot)

        return self.build_comparison()

    def reset(self) -> None:
        """Clear all accumulated build snapshots."""
        self._builds: list[BuildMetricSnapshot] = []
