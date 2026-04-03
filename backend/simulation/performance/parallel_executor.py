from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Optional

from simulation.monte_carlo.monte_carlo_runner import MonteCarloRunner, RunConfig, RunResult


@dataclass
class ParallelConfig:
    n_workers: int = 4
    chunk_size: int = 250


class ParallelExecutor:
    """Parallel execution of Monte Carlo runs using ThreadPoolExecutor."""

    def __init__(self, parallel_config: Optional[ParallelConfig] = None) -> None:
        self._default_config = parallel_config or ParallelConfig()

    def execute(
        self,
        sim_fn: Callable,
        run_config: RunConfig,
        parallel_config: Optional[ParallelConfig] = None,
    ) -> list[RunResult]:
        """Execute all runs in parallel, splitting work into chunks."""
        cfg = parallel_config or self._default_config
        runner = MonteCarloRunner(run_config)

        # Build chunks of run_ids
        all_run_ids = list(range(run_config.n_runs))
        chunks: list[list[int]] = []
        for i in range(0, len(all_run_ids), cfg.chunk_size):
            chunks.append(all_run_ids[i : i + cfg.chunk_size])

        def run_chunk(run_ids: list[int]) -> list[RunResult]:
            return [runner.run_single(run_id, sim_fn) for run_id in run_ids]

        all_results: list[RunResult] = []
        with ThreadPoolExecutor(max_workers=cfg.n_workers) as executor:
            futures = {executor.submit(run_chunk, chunk): chunk for chunk in chunks}
            for future in as_completed(futures):
                all_results.extend(future.result())

        all_results.sort(key=lambda r: r.run_id)
        return all_results

    def execute_comparison(
        self,
        sim_fn_a: Callable,
        sim_fn_b: Callable,
        run_config: RunConfig,
    ) -> tuple[list[RunResult], list[RunResult]]:
        """Run both sim functions in parallel threads, returning their results."""
        runner_a = MonteCarloRunner(run_config)
        runner_b = MonteCarloRunner(run_config)

        results_a: list[RunResult] = []
        results_b: list[RunResult] = []

        def run_a() -> list[RunResult]:
            return runner_a.run_all(sim_fn_a)

        def run_b() -> list[RunResult]:
            return runner_b.run_all(sim_fn_b)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(run_a)
            future_b = executor.submit(run_b)
            results_a = future_a.result()
            results_b = future_b.result()

        return results_a, results_b
