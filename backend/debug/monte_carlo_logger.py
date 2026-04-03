from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from simulation.monte_carlo.monte_carlo_runner import RunResult


@dataclass
class MonteCarloLogEntry:
    event_type: str
    run_id: Optional[int]
    data: dict
    timestamp: float


class MonteCarloLogger:
    """Debug logger for Monte Carlo simulations."""

    def __init__(self, capacity: int = 500) -> None:
        self._entries: deque[MonteCarloLogEntry] = deque(maxlen=capacity)

    def log_run_start(self, run_id: int, seed: int) -> None:
        """Log the start of a single simulation run."""
        self._entries.append(
            MonteCarloLogEntry(
                event_type="run_start",
                run_id=run_id,
                data={"run_id": run_id, "seed": seed},
                timestamp=time.time(),
            )
        )

    def log_run_complete(self, run_id: int, result: RunResult) -> None:
        """Log the completion of a single simulation run."""
        self._entries.append(
            MonteCarloLogEntry(
                event_type="run_complete",
                run_id=run_id,
                data={
                    "run_id": result.run_id,
                    "seed": result.seed,
                    "total_damage": result.total_damage,
                    "crit_count": result.crit_count,
                    "proc_count": result.proc_count,
                    "elapsed_time": result.elapsed_time,
                },
                timestamp=time.time(),
            )
        )

    def log_batch_complete(
        self,
        n_runs: int,
        mean_damage: float,
        elapsed_seconds: float,
    ) -> None:
        """Log the completion of a batch of simulation runs."""
        self._entries.append(
            MonteCarloLogEntry(
                event_type="batch_complete",
                run_id=None,
                data={
                    "n_runs": n_runs,
                    "mean_damage": mean_damage,
                    "elapsed_seconds": elapsed_seconds,
                },
                timestamp=time.time(),
            )
        )

    def log_convergence(
        self,
        n_runs: int,
        cv: float,
        converged: bool,
    ) -> None:
        """Log a convergence check result."""
        self._entries.append(
            MonteCarloLogEntry(
                event_type="convergence",
                run_id=None,
                data={"n_runs": n_runs, "cv": cv, "converged": converged},
                timestamp=time.time(),
            )
        )

    def get_entries(
        self,
        event_type: Optional[str] = None,
    ) -> list[MonteCarloLogEntry]:
        """Return all log entries, optionally filtered by event_type."""
        if event_type is None:
            return list(self._entries)
        return [e for e in self._entries if e.event_type == event_type]

    def clear(self) -> None:
        """Remove all log entries."""
        self._entries.clear()

    def summary(self) -> dict:
        """Return a summary of entries by event type."""
        by_type: dict[str, int] = {}
        for entry in self._entries:
            by_type[entry.event_type] = by_type.get(entry.event_type, 0) + 1
        return {
            "total_entries": len(self._entries),
            "by_type": by_type,
        }
