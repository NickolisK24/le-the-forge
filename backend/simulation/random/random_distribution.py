from __future__ import annotations

import math
import random


class RandomDistribution:
    """Probability distribution samplers backed by a single Random instance."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def uniform(self, low: float, high: float) -> float:
        """Sample from a uniform distribution over [low, high]."""
        return self._rng.uniform(low, high)

    def normal(self, mean: float, std_dev: float) -> float:
        """Sample from a normal distribution using the Box-Muller method (via gauss)."""
        return self._rng.gauss(mean, std_dev)

    def bernoulli(self, p: float) -> bool:
        """Return True with probability p."""
        return self._rng.random() < p

    def exponential(self, rate: float) -> float:
        """Sample from an exponential distribution with the given rate (lambda).

        Clamps u away from 1.0 to avoid log(0).
        """
        u = self._rng.random()
        # Clamp so that (1 - u) is never exactly 0
        u = min(u, 1.0 - 1e-15)
        return -math.log(1.0 - u) / rate

    def triangular(self, low: float, high: float, mode: float) -> float:
        """Sample from a triangular distribution."""
        return self._rng.triangular(low, high, mode)

    def choice(self, items: list, weights: list | None = None) -> object:
        """Return a single randomly chosen element, optionally weighted."""
        return self._rng.choices(items, weights=weights)[0]
