"""
Mana Resource System (Step 54).

Models the mana resource: current/max pool, regeneration over time,
and skill cost gating.

  ManaPool    — mutable mana state (current, max, regen rate)
  can_afford  — pure function; checks cost without mutating
  spend_mana  — deducts cost; raises InsufficientManaError if unaffordable
  regenerate  — advances time and restores mana at the regen rate
"""

from __future__ import annotations

from dataclasses import dataclass


class InsufficientManaError(Exception):
    """Raised when a skill cast would exceed available mana."""


@dataclass
class ManaPool:
    """
    Mutable mana state for one character.

    max_mana             — hard maximum; current_mana cannot exceed this
    current_mana         — mana currently available
    mana_regeneration_rate — mana restored per second (flat, before modifiers)
    """
    max_mana:              float
    current_mana:          float
    mana_regeneration_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.max_mana <= 0:
            raise ValueError(f"max_mana must be > 0, got {self.max_mana}")
        if self.current_mana < 0:
            raise ValueError(f"current_mana must be >= 0, got {self.current_mana}")
        if self.current_mana > self.max_mana:
            raise ValueError(
                f"current_mana ({self.current_mana}) cannot exceed max_mana ({self.max_mana})"
            )
        if self.mana_regeneration_rate < 0:
            raise ValueError(
                f"mana_regeneration_rate must be >= 0, got {self.mana_regeneration_rate}"
            )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def can_afford(self, cost: float) -> bool:
        """Return True if current_mana >= cost."""
        return self.current_mana >= cost

    @property
    def is_full(self) -> bool:
        return self.current_mana >= self.max_mana

    @property
    def is_empty(self) -> bool:
        return self.current_mana <= 0.0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def spend(self, cost: float) -> None:
        """
        Deduct ``cost`` from current_mana.

        Raises InsufficientManaError if current_mana < cost.
        Raises ValueError if cost < 0.
        """
        if cost < 0:
            raise ValueError(f"cost must be >= 0, got {cost}")
        if not self.can_afford(cost):
            raise InsufficientManaError(
                f"Need {cost:.1f} mana but only {self.current_mana:.1f} available"
            )
        self.current_mana = max(0.0, self.current_mana - cost)

    def regenerate(self, delta: float) -> float:
        """
        Restore mana at mana_regeneration_rate over ``delta`` seconds.

        Returns the amount of mana actually restored (may be less than the
        theoretical maximum if the pool was already near full).
        Raises ValueError if delta < 0.
        """
        if delta < 0:
            raise ValueError(f"delta must be >= 0, got {delta}")
        restored = min(
            self.mana_regeneration_rate * delta,
            self.max_mana - self.current_mana,
        )
        self.current_mana += restored
        return restored

    def restore_full(self) -> None:
        """Instantly fill mana to max (e.g. for fight start resets)."""
        self.current_mana = self.max_mana
