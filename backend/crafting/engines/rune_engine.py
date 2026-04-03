from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import random


class RuneType(Enum):
    REMOVAL = "removal"       # removes one affix
    REFINEMENT = "refinement"  # upgrades one affix tier
    SHAPING = "shaping"       # locks one affix
    DISCOVERY = "discovery"   # adds a new random affix


@dataclass
class RuneResult:
    rune_type: str
    applied: bool
    affected_affix: str | None
    message: str


class RuneEngine:
    MAX_AFFIXES = 4

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def apply_removal(self, state) -> RuneResult:
        unlocked = [a for a in state.affixes if not a.locked]
        if not unlocked:
            return RuneResult("removal", False, None, "no removable affixes")
        target = self._rng.choice(unlocked)
        state.affixes.remove(target)
        return RuneResult("removal", True, target.affix_id, f"removed {target.affix_id}")

    def apply_refinement(self, state) -> RuneResult:
        upgradeable = [a for a in state.affixes if a.current_tier < a.max_tier]
        if not upgradeable:
            return RuneResult("refinement", False, None, "no upgradeable affixes")
        target = self._rng.choice(upgradeable)
        target.current_tier += 1
        return RuneResult("refinement", True, target.affix_id, f"upgraded {target.affix_id} to T{target.current_tier}")

    def apply_shaping(self, state) -> RuneResult:
        unlocked = [a for a in state.affixes if not a.locked]
        if not unlocked:
            return RuneResult("shaping", False, None, "no lockable affixes")
        target = self._rng.choice(unlocked)
        target.locked = True
        return RuneResult("shaping", True, target.affix_id, f"locked {target.affix_id}")

    def apply_discovery(self, state, available_affix_ids: list[str]) -> RuneResult:
        if len(state.affixes) >= self.MAX_AFFIXES:
            return RuneResult("discovery", False, None, "item is full")
        existing = {a.affix_id for a in state.affixes}
        candidates = [aid for aid in available_affix_ids if aid not in existing]
        if not candidates:
            return RuneResult("discovery", False, None, "no available affixes")
        new_id = self._rng.choice(candidates)
        from crafting.models.craft_state import AffixState
        state.affixes.append(AffixState(new_id, 1, 7))
        return RuneResult("discovery", True, new_id, f"added {new_id} at T1")

    def apply(self, rune_type: str | RuneType, state, available_affix_ids: list[str] | None = None) -> RuneResult:
        if isinstance(rune_type, RuneType):
            rune_type = rune_type.value
        if rune_type == RuneType.REMOVAL.value:
            return self.apply_removal(state)
        elif rune_type == RuneType.REFINEMENT.value:
            return self.apply_refinement(state)
        elif rune_type == RuneType.SHAPING.value:
            return self.apply_shaping(state)
        elif rune_type == RuneType.DISCOVERY.value:
            return self.apply_discovery(state, available_affix_ids or [])
        return RuneResult(rune_type, False, None, "unknown rune type")
