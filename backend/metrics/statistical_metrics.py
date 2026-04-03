from __future__ import annotations

from dataclasses import dataclass

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class StatisticalMetrics:
    mean: float
    median: float
    std: float
    variance: float
    cv: float
    skewness: float
    kurtosis: float
    percentile_25: float
    percentile_75: float
    iqr: float


def _percentile(sorted_data: list[float], pct: float) -> float:
    """Return the value at the given percentile (0–100) using nearest-rank."""
    n = len(sorted_data)
    if n == 0:
        return 0.0
    index = max(0, int(pct / 100.0 * n) - 1)
    index = min(index, n - 1)
    return sorted_data[index]


def compute_metrics(data: list[float]) -> StatisticalMetrics:
    """Compute statistical metrics over a list of float values."""
    n = len(data)
    if n == 0:
        return StatisticalMetrics(
            mean=0.0, median=0.0, std=0.0, variance=0.0, cv=0.0,
            skewness=0.0, kurtosis=0.0,
            percentile_25=0.0, percentile_75=0.0, iqr=0.0,
        )

    mean = sum(data) / n

    sorted_data = sorted(data)
    if n % 2 == 1:
        median = sorted_data[n // 2]
    else:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0

    variance = sum((x - mean) ** 2 for x in data) / n
    std = variance ** 0.5

    cv = std / mean if mean != 0.0 else 0.0

    if std == 0.0:
        skewness = 0.0
        kurtosis = 0.0
    else:
        # Pearson's 2nd coefficient of skewness
        skewness = (mean - median) / std * 3
        # Excess kurtosis
        kurtosis = sum((x - mean) ** 4 for x in data) / (n * std ** 4) - 3

    percentile_25 = _percentile(sorted_data, 25)
    percentile_75 = _percentile(sorted_data, 75)
    iqr = percentile_75 - percentile_25

    return StatisticalMetrics(
        mean=mean,
        median=median,
        std=std,
        variance=variance,
        cv=cv,
        skewness=skewness,
        kurtosis=kurtosis,
        percentile_25=percentile_25,
        percentile_75=percentile_75,
        iqr=iqr,
    )


def compute_for_results(results: list[RunResult]) -> StatisticalMetrics:
    """Extract total_damage from each RunResult and compute statistical metrics."""
    damages = [r.total_damage for r in results]
    return compute_metrics(damages)
