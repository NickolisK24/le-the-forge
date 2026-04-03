from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass
class FractureResult:
    fractured: bool
    fracture_type: str | None    # "minor", "damaging", "destructive"
    affix_lost: str | None       # affix_id lost if damaging/destructive
    item_destroyed: bool


class FractureEngine:
    # If fracture occurs, determine type by roll:
    FRACTURE_TYPE_WEIGHTS = {"minor": 50, "damaging": 35, "destructive": 15}

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def roll_fracture(self, chance: float) -> bool:
        return self._rng.random() < chance

    def determine_type(self) -> str:
        choices = list(self.FRACTURE_TYPE_WEIGHTS.keys())
        weights = list(self.FRACTURE_TYPE_WEIGHTS.values())
        return self._rng.choices(choices, weights=weights)[0]

    def apply(self, state, chance: float) -> FractureResult:
        if not self.roll_fracture(chance):
            return FractureResult(False, None, None, False)
        ftype = self.determine_type()
        state.is_fractured = True
        state.fracture_type = ftype
        affix_lost = None
        destroyed = False
        if ftype == "damaging" and state.affixes:
            # Remove a random non-locked affix
            unlocked = [a for a in state.affixes if not a.locked]
            if unlocked:
                victim = self._rng.choice(unlocked)
                state.affixes.remove(victim)
                affix_lost = victim.affix_id
        elif ftype == "destructive":
            destroyed = True
            state.affixes = []
            state.forging_potential = 0
        return FractureResult(True, ftype, affix_lost, destroyed)
