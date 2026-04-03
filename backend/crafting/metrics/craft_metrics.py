from __future__ import annotations
from dataclasses import dataclass
import statistics

from crafting.simulation.monte_carlo_crafting import MCCraftResult


@dataclass
class CraftMetrics:
    success_probability: float
    mean_fp_cost: float
    std_fp_cost: float
    expected_failures: float    # expected fractures per 100 attempts
    fp_efficiency: float        # mean_fp_cost / max_fp_budget
    confidence_low: float       # 95% CI lower bound on success rate
    confidence_high: float      # 95% CI upper bound


def compute_craft_metrics(mc_result: MCCraftResult, max_fp_budget: int = 200) -> CraftMetrics:
    n = mc_result.n_runs
    p = mc_result.success_rate
    # Wilson score CI
    z = 1.96
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margin = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / (1 + z**2 / n)
    return CraftMetrics(
        success_probability=p,
        mean_fp_cost=mc_result.mean_fp_spent,
        std_fp_cost=mc_result.std_fp_spent,
        expected_failures=mc_result.fracture_rate * 100,
        fp_efficiency=mc_result.mean_fp_spent / max(max_fp_budget, 1),
        confidence_low=max(0.0, center - margin),
        confidence_high=min(1.0, center + margin),
    )
