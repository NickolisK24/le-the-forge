from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class ProcResult:
    triggered: bool
    effect_id: str
    magnitude: float
    rng_value: float


class ProcResolver:
    """Resolves proc (chance-based effect) triggers."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def resolve(
        self,
        effect_id: str,
        chance: float,
        magnitude: float = 1.0,
    ) -> ProcResult:
        """Roll for a single proc and return the result."""
        rng_value = self._rng.random()
        triggered = rng_value < chance
        return ProcResult(
            triggered=triggered,
            effect_id=effect_id,
            magnitude=magnitude if triggered else 0.0,
            rng_value=rng_value,
        )

    def resolve_all(self, effects: list[dict]) -> list[ProcResult]:
        """Resolve a list of proc definitions.

        Each dict must have keys ``effect_id`` and ``chance``, and may
        optionally include ``magnitude`` (defaults to 1.0).
        """
        results: list[ProcResult] = []
        for effect in effects:
            effect_id: str = effect["effect_id"]
            chance: float = effect["chance"]
            magnitude: float = effect.get("magnitude", 1.0)
            results.append(self.resolve(effect_id, chance, magnitude))
        return results
