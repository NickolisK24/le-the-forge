from __future__ import annotations

from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable
import time


@dataclass
class ParallelTask:
    task_id: str
    fn: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


@dataclass
class ParallelResult:
    task_id: str
    result: object
    duration_ms: float
    error: str | None = None


class ParallelManager:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def run(self, tasks: list[ParallelTask]) -> list[ParallelResult]:
        results: list[ParallelResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map: dict = {}
            for task in tasks:
                f = executor.submit(task.fn, *task.args, **task.kwargs)
                future_map[f] = task
            for future in as_completed(future_map):
                task = future_map[future]
                t0 = time.time()
                try:
                    result = future.result()
                    results.append(
                        ParallelResult(task.task_id, result, (time.time() - t0) * 1000)
                    )
                except Exception as e:
                    results.append(
                        ParallelResult(
                            task.task_id, None, (time.time() - t0) * 1000, str(e)
                        )
                    )
        return results

    def run_batch(
        self, fn: Callable, items: list, chunk_size: int = 10
    ) -> list[ParallelResult]:
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        tasks = [
            ParallelTask(f"chunk_{i}", fn, (chunk,)) for i, chunk in enumerate(chunks)
        ]
        return self.run(tasks)
