from __future__ import annotations

import time
from collections import OrderedDict
from typing import Optional

from simulation.monte_carlo.monte_carlo_runner import RunConfig, RunResult


class ResultStore:
    """In-memory store for simulation results with LRU-style eviction."""

    def __init__(self, max_entries: int = 100) -> None:
        self._max_entries = max_entries
        self._store: OrderedDict[str, dict] = OrderedDict()

    def save(self, key: str, results: list[RunResult], config: RunConfig) -> None:
        """Save results and config under key, evicting the oldest entry if at capacity."""
        # If key already exists, remove it first so insertion order is updated
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self._max_entries:
            # Evict oldest entry (first in insertion order)
            self._store.popitem(last=False)

        self._store[key] = {
            "results": results,
            "config": config,
            "timestamp": time.time(),
        }

    def load(self, key: str) -> Optional[tuple[list[RunResult], RunConfig]]:
        """Return (results, config) for key, or None if not found."""
        entry = self._store.get(key)
        if entry is None:
            return None
        return entry["results"], entry["config"]

    def list_keys(self) -> list[str]:
        """Return all stored keys in insertion order."""
        return list(self._store.keys())

    def delete(self, key: str) -> bool:
        """Delete the entry for key. Returns True if it existed, False otherwise."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
