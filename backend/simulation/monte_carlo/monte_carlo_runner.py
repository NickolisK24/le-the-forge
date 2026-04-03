from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from simulation.random.random_seed_manager import RandomSeedManager


@dataclass
class RunConfig:
    n_runs: int = 1000
    base_seed: int = 42
    tick_size: float = 0.1
    duration: float = 10.0


@dataclass
class RunResult:
    run_id: int
    seed: int
    total_damage: float
    crit_count: int
    proc_count: int
    elapsed_time: float


class MonteCarloRunner:
    """Executes repeated simulation runs using a deterministic seed manager."""

    def __init__(self, config: RunConfig) -> None:
        self.config = config
        self._seed_manager = RandomSeedManager(base_seed=config.base_seed)

    def run_single(
        self,
        run_id: int,
        sim_fn: Callable[[random.Random, RunConfig], RunResult],
    ) -> RunResult:
        """Run a single simulation iteration and return its result."""
        seed = self._seed_manager.get_seed(run_id)
        rng = self._seed_manager.get_rng(run_id)
        result = sim_fn(rng, self.config)
        # Ensure run_id and seed on the result match what the runner used
        result.run_id = run_id
        result.seed = seed
        return result

    def run_all(
        self,
        sim_fn: Callable[[random.Random, RunConfig], RunResult],
    ) -> list[RunResult]:
        """Run all iterations specified in RunConfig and return every result."""
        return [
            self.run_single(run_id, sim_fn)
            for run_id in range(self.config.n_runs)
        ]
