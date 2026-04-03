from __future__ import annotations

import statistics
from dataclasses import dataclass

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class AggregatedResult:
    n_runs: int
    mean_damage: float
    std_damage: float
    min_damage: float
    max_damage: float
    median_damage: float
    mean_crits: float
    mean_procs: float
    percentile_5: float
    percentile_95: float


class ResultAggregator:
    """Aggregates Monte Carlo run results into summary statistics."""

    def aggregate(self, results: list[RunResult]) -> AggregatedResult:
        """Compute summary statistics over all run results."""
        damages = [r.total_damage for r in results]
        crits = [r.crit_count for r in results]
        procs = [r.proc_count for r in results]

        n = len(damages)
        sorted_damages = sorted(damages)

        def _percentile(sorted_data: list[float], pct: float) -> float:
            """Return the value at the given percentile (0–100) using nearest-rank."""
            if not sorted_data:
                return 0.0
            index = max(0, int(pct / 100.0 * len(sorted_data)) - 1)
            index = min(index, len(sorted_data) - 1)
            return sorted_data[index]

        return AggregatedResult(
            n_runs=n,
            mean_damage=statistics.mean(damages) if damages else 0.0,
            std_damage=statistics.stdev(damages) if n > 1 else 0.0,
            min_damage=min(damages) if damages else 0.0,
            max_damage=max(damages) if damages else 0.0,
            median_damage=statistics.median(damages) if damages else 0.0,
            mean_crits=statistics.mean(crits) if crits else 0.0,
            mean_procs=statistics.mean(procs) if procs else 0.0,
            percentile_5=_percentile(sorted_damages, 5),
            percentile_95=_percentile(sorted_damages, 95),
        )

    def damage_distribution(
        self,
        results: list[RunResult],
        bins: int = 20,
    ) -> list[dict]:
        """Bucket total_damage values into equal-width bins.

        Returns a list of dicts with keys:
            bin_start, bin_end, count, frequency
        """
        damages = [r.total_damage for r in results]
        if not damages:
            return []

        min_d = min(damages)
        max_d = max(damages)

        # Avoid zero-width bins when all values are identical
        if max_d == min_d:
            return [
                {
                    "bin_start": min_d,
                    "bin_end": max_d,
                    "count": len(damages),
                    "frequency": 1.0,
                }
            ]

        bin_width = (max_d - min_d) / bins
        counts = [0] * bins

        for d in damages:
            idx = int((d - min_d) / bin_width)
            # Clamp the last value into the final bin
            idx = min(idx, bins - 1)
            counts[idx] += 1

        total = len(damages)
        distribution: list[dict] = []
        for i, count in enumerate(counts):
            distribution.append(
                {
                    "bin_start": min_d + i * bin_width,
                    "bin_end": min_d + (i + 1) * bin_width,
                    "count": count,
                    "frequency": count / total,
                }
            )
        return distribution
