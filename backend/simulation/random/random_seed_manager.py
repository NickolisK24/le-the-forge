from __future__ import annotations

import random


class RandomSeedManager:
    """Manages reproducible random seeds for Monte Carlo runs."""

    def __init__(self, base_seed: int = 42) -> None:
        self._base_seed = base_seed

    def get_seed(self, run_id: int) -> int:
        """Return a deterministic seed derived from base_seed and run_id."""
        return (self._base_seed ^ (run_id * 2654435761)) & 0xFFFFFFFF

    def get_rng(self, run_id: int) -> random.Random:
        """Return a seeded Random instance for the given run_id."""
        rng = random.Random()
        rng.seed(self.get_seed(run_id))
        return rng

    def reset(self, new_base_seed: int) -> None:
        """Replace the base seed."""
        self._base_seed = new_base_seed
