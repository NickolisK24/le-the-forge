from __future__ import annotations

import math
from dataclasses import dataclass

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class ComparisonResult:
    build_a_mean: float
    build_b_mean: float
    delta_mean: float
    delta_pct: float
    winner: str  # "A", "B", or "tie"
    a_is_better_pct: float  # fraction of runs where A > B (0.0–1.0)
    effect_size: float  # Cohen's d


class BuildComparison:
    """Compares two build simulation results."""

    def compare(
        self,
        results_a: list[RunResult],
        results_b: list[RunResult],
    ) -> ComparisonResult:
        """Compare two sets of simulation results and return a ComparisonResult."""
        damages_a = [r.total_damage for r in results_a]
        damages_b = [r.total_damage for r in results_b]

        n_a = len(damages_a)
        n_b = len(damages_b)

        mean_a = sum(damages_a) / n_a if n_a > 0 else 0.0
        mean_b = sum(damages_b) / n_b if n_b > 0 else 0.0

        delta_mean = mean_a - mean_b
        delta_pct = (delta_mean / mean_b * 100) if mean_b != 0.0 else 0.0

        if delta_pct > 1.0:
            winner = "A"
        elif delta_pct < -1.0:
            winner = "B"
        else:
            winner = "tie"

        # Fraction of paired comparisons where A > B
        n_pairs = min(n_a, n_b)
        if n_pairs > 0:
            a_better = sum(
                1 for va, vb in zip(damages_a[:n_pairs], damages_b[:n_pairs])
                if va > vb
            )
            a_is_better_pct = a_better / n_pairs
        else:
            a_is_better_pct = 0.0

        # Cohen's d with pooled std
        var_a = sum((d - mean_a) ** 2 for d in damages_a) / n_a if n_a > 0 else 0.0
        var_b = sum((d - mean_b) ** 2 for d in damages_b) / n_b if n_b > 0 else 0.0
        pooled_std = math.sqrt((var_a + var_b) / 2)
        effect_size = (mean_a - mean_b) / pooled_std if pooled_std != 0.0 else 0.0

        return ComparisonResult(
            build_a_mean=mean_a,
            build_b_mean=mean_b,
            delta_mean=delta_mean,
            delta_pct=delta_pct,
            winner=winner,
            a_is_better_pct=a_is_better_pct,
            effect_size=effect_size,
        )
