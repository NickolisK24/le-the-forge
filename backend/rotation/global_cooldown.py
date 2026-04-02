"""
G5 — Global Cooldown (GCD) System

A single shared lock that prevents any skill from being cast while active.

Usage
-----
    gcd = GlobalCooldown(base_gcd=1.0)
    gcd.trigger(current_time=0.0)
    gcd.is_locked(0.5)   # True
    gcd.is_locked(1.0)   # False
    gcd.time_remaining(0.5)  # 0.5
"""

from __future__ import annotations

_GCD_MIN = 0.0
_GCD_MAX = 10.0


class GlobalCooldown:
    """
    Shared cast-lock applied after every skill cast.

    Parameters
    ----------
    base_gcd:
        Duration (seconds) of the global cooldown window. Must be in [0, 10].
        0 = no GCD (every skill is always eligible).
    """

    def __init__(self, base_gcd: float = 1.0) -> None:
        if not (_GCD_MIN <= base_gcd <= _GCD_MAX):
            raise ValueError(
                f"base_gcd must be in [{_GCD_MIN}, {_GCD_MAX}], got {base_gcd}"
            )
        self.base_gcd = base_gcd
        self._locked_until: float = 0.0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def trigger(self, current_time: float) -> None:
        """Activate the GCD starting at `current_time`."""
        self._locked_until = current_time + self.base_gcd

    def unlock(self) -> None:
        """Immediately clear the GCD lock."""
        self._locked_until = 0.0

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def is_locked(self, current_time: float) -> bool:
        """Return True if the GCD is still active at `current_time`."""
        return current_time < self._locked_until

    def time_remaining(self, current_time: float) -> float:
        """Return seconds until the GCD expires (0.0 if not locked)."""
        return max(0.0, self._locked_until - current_time)

    def locked_until(self) -> float:
        """Absolute simulation time at which the GCD expires."""
        return self._locked_until
