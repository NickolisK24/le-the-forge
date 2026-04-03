from __future__ import annotations

from dataclasses import dataclass

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class ReliabilityReport:
    score: float
    is_reliable: bool
    cv: float
    n_runs: int
    recommendation: str


class ReliabilityScorer:
    """Scores how reliable/stable a Monte Carlo simulation is."""

    def score(self, results: list[RunResult]) -> ReliabilityReport:
        """Compute a reliability score based on the coefficient of variation."""
        damages = [r.total_damage for r in results]
        n = len(damages)

        if n == 0:
            return ReliabilityReport(
                score=0.0,
                is_reliable=False,
                cv=0.0,
                n_runs=0,
                recommendation="increase runs",
            )

        mean = sum(damages) / n
        variance = sum((d - mean) ** 2 for d in damages) / n if n > 1 else 0.0
        std = variance ** 0.5

        cv = std / mean if mean != 0.0 else 0.0
        raw_score = max(0.0, 1.0 - cv)
        score = min(1.0, raw_score)

        if n < 100:
            recommendation = "increase runs"
        elif cv > 0.5:
            recommendation = "high variance"
        elif score >= 0.8:
            recommendation = "reliable"
        else:
            recommendation = "marginally reliable"

        return ReliabilityReport(
            score=score,
            is_reliable=score >= 0.8,
            cv=cv,
            n_runs=n,
            recommendation=recommendation,
        )
