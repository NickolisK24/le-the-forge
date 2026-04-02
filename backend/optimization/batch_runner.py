"""
F5 — Batch Simulation Runner

Executes encounter simulations across multiple build variants.
Supports sequential (default) and parallel execution via ThreadPoolExecutor.

Each simulation is independent — a failed variant returns None rather than
crashing the whole batch.
"""

from __future__ import annotations
import concurrent.futures
from dataclasses import dataclass, field

from builds.build_definition   import BuildDefinition
from builds.build_stats_engine import BuildStatsEngine


@dataclass
class BatchProgress:
    """Tracks progress through a batch run."""
    total:     int
    completed: int = 0
    failed:    int = 0

    @property
    def fraction(self) -> float:
        return self.completed / self.total if self.total > 0 else 0.0


class BatchRunner:
    """
    Runs encounter simulations for a list of BuildDefinition variants.

    Parameters
    ----------
    encounter_kwargs:
        Dict of encounter parameters passed to run_encounter_simulation:
        enemy_template, fight_duration, tick_size, distribution.
    max_workers:
        Thread pool size for parallel execution.  Use 1 for sequential (default).
    """

    def __init__(
        self,
        encounter_kwargs: dict | None = None,
        max_workers: int = 1,
    ) -> None:
        self._enc_kwargs = encounter_kwargs or {
            "enemy_template": "STANDARD_BOSS",
            "fight_duration": 60.0,
            "tick_size":      0.1,
            "distribution":   "SINGLE",
        }
        self._max_workers = max_workers
        self._engine = BuildStatsEngine()

    def run_one(self, build: BuildDefinition) -> dict | None:
        """
        Simulate a single variant.  Returns the result dict or None on failure.
        """
        try:
            from app.services.simulation_service import run_encounter_simulation
            params = self._engine.to_encounter_params(build)
            return run_encounter_simulation(
                base_damage     = params["base_damage"],
                crit_chance     = params["crit_chance"],
                crit_multiplier = params["crit_multiplier"],
                **self._enc_kwargs,
            )
        except Exception:
            return None

    def run_batch(
        self,
        variants: list[BuildDefinition],
        progress: BatchProgress | None = None,
    ) -> list[tuple[BuildDefinition, dict | None]]:
        """
        Simulate all variants and return (build, result_or_None) pairs.

        Uses sequential execution when max_workers==1 (safe in all contexts).
        Uses a ThreadPoolExecutor for max_workers > 1 (faster but requires
        thread-safe game data access — safe after app context is initialised).
        """
        if progress is not None:
            progress.total = len(variants)

        results: list[tuple[BuildDefinition, dict | None]] = []

        if self._max_workers <= 1:
            # Sequential
            for v in variants:
                r = self.run_one(v)
                results.append((v, r))
                if progress is not None:
                    progress.completed += 1
                    if r is None:
                        progress.failed += 1
        else:
            # Parallel
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self._max_workers
            ) as executor:
                future_map = {executor.submit(self.run_one, v): v for v in variants}
                for future in concurrent.futures.as_completed(future_map):
                    v = future_map[future]
                    try:
                        r = future.result()
                    except Exception:
                        r = None
                    results.append((v, r))
                    if progress is not None:
                        progress.completed += 1
                        if r is None:
                            progress.failed += 1

        return results
