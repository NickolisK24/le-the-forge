from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class ConfidenceInterval:
    mean: float
    lower: float
    upper: float
    confidence: float
    margin_of_error: float


class ConfidenceIntervalCalculator:
    """Computes statistical confidence intervals using a t-distribution approximation."""

    _Z_SCORES: dict[float, float] = {
        0.99: 2.576,
        0.95: 1.96,
    }
    _DEFAULT_Z: float = 1.645  # fallback (e.g. 0.90)

    def _z_score(self, confidence: float) -> float:
        return self._Z_SCORES.get(confidence, self._DEFAULT_Z)

    def compute(self, data: list[float], confidence: float = 0.95) -> ConfidenceInterval:
        """Compute a confidence interval for the provided data."""
        n = len(data)
        mean = statistics.mean(data) if data else 0.0

        if n > 1:
            std = statistics.stdev(data)
            z = self._z_score(confidence)
            margin = z * (std / math.sqrt(n))
        else:
            margin = 0.0

        return ConfidenceInterval(
            mean=mean,
            lower=mean - margin,
            upper=mean + margin,
            confidence=confidence,
            margin_of_error=margin,
        )

    def compute_for_results(
        self,
        results: list[RunResult],
        confidence: float = 0.95,
    ) -> ConfidenceInterval:
        """Extract total_damage from each RunResult and compute a confidence interval."""
        damages = [r.total_damage for r in results]
        return self.compute(damages, confidence)

    def is_converged(self, data: list[float], threshold: float = 0.05) -> bool:
        """Return True when the relative margin of error is below threshold.

        Convergence is defined as: (margin_of_error / mean) < threshold.
        Returns False when the mean is zero to avoid division-by-zero.
        """
        ci = self.compute(data)
        if ci.mean == 0.0:
            return False
        return (ci.margin_of_error / ci.mean) < threshold
