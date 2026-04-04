from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass
class FPCostResult:
    base_cost: int
    actual_cost: int
    remaining: int
    exhausted: bool


class ForgingPotentialEngine:
    # FP costs vary by action type
    FP_COSTS = {
        "add_affix": (3, 6),        # (min, max) inclusive
        "upgrade_affix": (2, 4),
        "remove_affix": (4, 7),
        "reroll_affix": (3, 8),
        "glyph": (1, 3),
        "rune": (2, 5),
    }

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def roll_cost(self, action_type: str) -> int:
        # Returns random cost in range for action_type; default (2,5) if unknown
        lo, hi = self.FP_COSTS.get(action_type, (2, 5))
        return self._rng.randint(lo, hi)

    def apply_cost(self, state, action_type: str) -> FPCostResult:
        # Mutates state.forging_potential; returns FPCostResult
        # Import CraftState inline to avoid circular
        cost = self.roll_cost(action_type)
        state.forging_potential = max(0, state.forging_potential - cost)
        exhausted = state.forging_potential == 0
        return FPCostResult(cost, cost, state.forging_potential, exhausted)

    def detect_exhaustion(self, state) -> bool:
        return state.forging_potential <= 0

    def estimate_remaining_crafts(self, state, action_type: str = "upgrade_affix") -> float:
        lo, hi = self.FP_COSTS.get(action_type, (2, 5))
        avg_cost = (lo + hi) / 2
        return state.forging_potential / avg_cost if avg_cost > 0 else 0.0
