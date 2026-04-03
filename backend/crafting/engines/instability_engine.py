from __future__ import annotations
from dataclasses import dataclass


@dataclass
class InstabilityResult:
    added: int
    total: int
    fracture_chance: float  # 0.0–1.0


class InstabilityEngine:
    BASE_INCREASE = 10      # instability added per normal craft
    MODIFIER_SCALE = 1.0    # multiplier from glyphs etc.
    FRACTURE_THRESHOLD = 100  # instability >= this: 100% fracture

    def compute_increase(self, base: int = None, modifier: float = 1.0) -> int:
        base = base if base is not None else self.BASE_INCREASE
        return max(1, round(base * modifier))

    def apply(self, state, modifier: float = 1.0) -> InstabilityResult:
        increase = self.compute_increase(modifier=modifier)
        state.instability = min(state.instability + increase, self.FRACTURE_THRESHOLD)
        chance = self.fracture_chance(state.instability)
        return InstabilityResult(increase, state.instability, chance)

    def fracture_chance(self, instability: int) -> float:
        # Linear: 0 instability = 0%, 100 instability = 100%
        return min(1.0, max(0.0, instability / self.FRACTURE_THRESHOLD))

    def reset(self, state) -> None:
        state.instability = 0
