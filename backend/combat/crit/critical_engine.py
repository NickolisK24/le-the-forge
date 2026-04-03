from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class CritResult:
    is_crit: bool
    damage_multiplier: float
    rng_value: float


class CriticalEngine:
    """Simulates critical strike outcomes."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def roll(self, crit_chance: float, crit_multiplier: float = 2.0) -> CritResult:
        """Roll for a critical strike and return the result."""
        rng_value = self._rng.random()
        is_crit = rng_value < crit_chance
        damage_multiplier = crit_multiplier if is_crit else 1.0
        return CritResult(
            is_crit=is_crit,
            damage_multiplier=damage_multiplier,
            rng_value=rng_value,
        )

    def apply(
        self,
        base_damage: float,
        crit_chance: float,
        crit_multiplier: float = 2.0,
    ) -> tuple[float, CritResult]:
        """Apply a crit roll to base_damage and return (final_damage, CritResult)."""
        result = self.roll(crit_chance, crit_multiplier)
        return base_damage * result.damage_multiplier, result

    def expected_multiplier(
        self,
        crit_chance: float,
        crit_multiplier: float = 2.0,
    ) -> float:
        """Return the theoretical expected damage multiplier (no RNG involved)."""
        return 1.0 + crit_chance * (crit_multiplier - 1.0)
