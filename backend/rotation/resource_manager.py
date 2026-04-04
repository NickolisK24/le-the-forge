"""
G9 — Resource Management System

Tracks a single resource pool (mana, rage, energy, etc.) over simulation time.

Rules
-----
- Pool has a current value in [0, maximum].
- Spending fails (returns False) if current < cost.
- Regeneration accrues per second; caller drives time by calling tick().
- Skills are blocked when they can't afford their cost.
"""

from __future__ import annotations


class ResourceManager:
    """
    Manages a single numeric resource pool.

    Parameters
    ----------
    maximum:       Pool cap.
    initial:       Starting value (defaults to maximum).
    regen_per_sec: Passive regeneration rate (units/second).
    """

    def __init__(
        self,
        maximum:       float,
        initial:       float | None = None,
        regen_per_sec: float        = 0.0,
    ) -> None:
        if maximum <= 0:
            raise ValueError(f"maximum must be > 0, got {maximum}")
        if regen_per_sec < 0:
            raise ValueError(f"regen_per_sec must be >= 0, got {regen_per_sec}")
        self._maximum = float(maximum)
        self._current = float(initial if initial is not None else maximum)
        self._regen   = float(regen_per_sec)
        self._current = max(0.0, min(self._maximum, self._current))

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current(self) -> float:
        return self._current

    @property
    def maximum(self) -> float:
        return self._maximum

    @property
    def regen_per_sec(self) -> float:
        return self._regen

    @property
    def is_empty(self) -> bool:
        return self._current <= 0.0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def tick(self, elapsed: float) -> None:
        """Advance time by `elapsed` seconds, applying passive regeneration."""
        if elapsed < 0:
            raise ValueError(f"elapsed must be >= 0, got {elapsed}")
        self._current = min(self._maximum, self._current + self._regen * elapsed)

    def spend(self, cost: float) -> bool:
        """
        Attempt to spend `cost` from the pool.

        Returns True if successful, False if insufficient resource.
        Does not mutate on failure.
        """
        if cost < 0:
            raise ValueError(f"cost must be >= 0, got {cost}")
        if self._current < cost:
            return False
        self._current -= cost
        return True

    def restore(self, amount: float) -> None:
        """Directly add `amount` to the pool (capped at maximum)."""
        if amount < 0:
            raise ValueError(f"amount must be >= 0, got {amount}")
        self._current = min(self._maximum, self._current + amount)

    def can_afford(self, cost: float) -> bool:
        """Return True if the pool has at least `cost` available."""
        return self._current >= cost
