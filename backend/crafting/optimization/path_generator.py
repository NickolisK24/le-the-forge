from __future__ import annotations
from dataclasses import dataclass, field
import random

from crafting.models.craft_state import CraftState, AffixState
from crafting.models.craft_action import CraftAction, ActionType


@dataclass
class PathCandidate:
    actions: list[CraftAction]
    strategy: str   # "greedy", "randomized", "heuristic"
    estimated_fp: int
    priority: float  # higher = better candidate


class PathGenerator:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def greedy(self, state: CraftState, target_affixes: list[str],
               target_tiers: dict[str, int]) -> PathCandidate:
        # Greedy: upgrade lowest-tier needed affix first, add missing affixes
        actions = []
        for affix_id in target_affixes:
            existing = next((a for a in state.affixes if a.affix_id == affix_id), None)
            if existing is None:
                actions.append(CraftAction(ActionType.ADD_AFFIX, new_affix_id=affix_id))
            else:
                target_t = target_tiers.get(affix_id, existing.max_tier)
                for _ in range(target_t - existing.current_tier):
                    actions.append(CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id=affix_id))
        est_fp = len(actions) * 4  # rough estimate using avg cost
        return PathCandidate(actions, "greedy", est_fp, 1.0 / (est_fp + 1))

    def randomized(self, state: CraftState, target_affixes: list[str],
                   target_tiers: dict[str, int], n_variants: int = 5) -> list[PathCandidate]:
        # Shuffles action order n_variants times
        base = self.greedy(state, target_affixes, target_tiers)
        candidates = [base]
        for _ in range(n_variants - 1):
            shuffled = list(base.actions)
            self._rng.shuffle(shuffled)
            candidates.append(PathCandidate(shuffled, "randomized", base.estimated_fp,
                                            base.priority * self._rng.uniform(0.8, 1.2)))
        return candidates

    def heuristic(self, state: CraftState, target_affixes: list[str],
                  target_tiers: dict[str, int]) -> PathCandidate:
        # Heuristic: add missing affixes first (lowest weight cost), then upgrade from lowest tier up
        actions = []
        missing = [aid for aid in target_affixes if not any(a.affix_id == aid for a in state.affixes)]
        for aid in missing:
            actions.append(CraftAction(ActionType.ADD_AFFIX, new_affix_id=aid))
        # sort upgrades by tier gap ascending
        upgrades = []
        for a in state.affixes:
            if a.affix_id in target_affixes:
                target_t = target_tiers.get(a.affix_id, a.max_tier)
                gap = target_t - a.current_tier
                for _ in range(gap):
                    upgrades.append((a.current_tier, CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id=a.affix_id)))
        upgrades.sort(key=lambda x: x[0])
        actions.extend(act for _, act in upgrades)
        est_fp = len(actions) * 4
        return PathCandidate(actions, "heuristic", est_fp, 1.0 / (est_fp + 1) * 1.1)
