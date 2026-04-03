from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from simulation.monte_carlo.monte_carlo_runner import MonteCarloRunner, RunConfig, RunResult
from simulation.aggregation.result_aggregator import AggregatedResult, ResultAggregator
from simulation.statistics.confidence_intervals import ConfidenceInterval, ConfidenceIntervalCalculator
from simulation.statistics.reliability_score import ReliabilityReport, ReliabilityScorer
from simulation.storage.result_store import ResultStore
from simulation.random.random_distribution import RandomDistribution
from metrics.statistical_metrics import StatisticalMetrics, compute_for_results


@dataclass
class MonteCarloConfig:
    n_runs: int = 1000
    base_seed: int = 42
    duration: float = 10.0
    tick_size: float = 0.1
    crit_chance: float = 0.2
    crit_multiplier: float = 2.0
    base_damage: float = 100.0
    proc_chance: float = 0.1
    proc_magnitude: float = 50.0


@dataclass
class MonteCarloSimulationResult:
    config: MonteCarloConfig
    aggregated: AggregatedResult
    confidence_interval: ConfidenceInterval
    reliability: ReliabilityReport
    metrics: StatisticalMetrics
    distribution: list[dict]


class MonteCarloIntegration:
    """High-level service integrating all Monte Carlo components."""

    def __init__(self, store: Optional[ResultStore] = None) -> None:
        self._store = store

    def run(
        self,
        config: MonteCarloConfig,
        key: Optional[str] = None,
    ) -> MonteCarloSimulationResult:
        """Run a full Monte Carlo simulation and return aggregated results."""
        run_config = RunConfig(
            n_runs=config.n_runs,
            base_seed=config.base_seed,
            tick_size=config.tick_size,
            duration=config.duration,
        )

        # Capture config in closure
        _config = config

        def sim_fn(rng: random.Random, run_cfg: RunConfig) -> RunResult:
            dist = RandomDistribution(rng)
            n_hits = int(run_cfg.duration / run_cfg.tick_size)
            crits = sum(
                1 for _ in range(n_hits) if dist.bernoulli(_config.crit_chance)
            )
            procs = sum(
                1 for _ in range(n_hits) if dist.bernoulli(_config.proc_chance)
            )
            damage = (
                n_hits * _config.base_damage
                * (1 + crits / n_hits * (_config.crit_multiplier - 1))
                + procs * _config.proc_magnitude
            )
            # run_id and seed will be set by MonteCarloRunner.run_single
            return RunResult(
                run_id=0,
                seed=0,
                total_damage=damage,
                crit_count=crits,
                proc_count=procs,
                elapsed_time=run_cfg.duration,
            )

        runner = MonteCarloRunner(run_config)
        results = runner.run_all(sim_fn)

        aggregator = ResultAggregator()
        aggregated = aggregator.aggregate(results)
        distribution = aggregator.damage_distribution(results)

        ci_calculator = ConfidenceIntervalCalculator()
        confidence_interval = ci_calculator.compute_for_results(results)

        reliability_scorer = ReliabilityScorer()
        reliability = reliability_scorer.score(results)

        metrics = compute_for_results(results)

        if key is not None and self._store is not None:
            self._store.save(key, results, run_config)

        return MonteCarloSimulationResult(
            config=config,
            aggregated=aggregated,
            confidence_interval=confidence_interval,
            reliability=reliability,
            metrics=metrics,
            distribution=distribution,
        )
