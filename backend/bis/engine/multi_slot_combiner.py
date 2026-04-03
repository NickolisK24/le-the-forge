from __future__ import annotations

from dataclasses import dataclass, field
import itertools

from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment
from bis.integration.build_adapter import BuildAdapter, BuildSnapshot


@dataclass
class CombinationBatch:
    combinations: list[BuildSnapshot]
    total_evaluated: int
    slots_covered: list[str]


class MultiSlotCombiner:
    def __init__(self) -> None:
        self._adapter = BuildAdapter()

    def combine(
        self,
        slot_candidates: dict[str, list[tuple[ItemCandidate, TierAssignment]]],
        max_combinations: int = 1000,
    ) -> CombinationBatch:
        # slot_candidates: {slot_type: [(candidate, assignment), ...]}
        slot_names = list(slot_candidates.keys())
        option_lists = [slot_candidates[s] for s in slot_names]

        combinations: list[BuildSnapshot] = []
        total = 0
        for combo in itertools.product(*option_lists):
            if total >= max_combinations:
                break
            slot_map = {slot_names[i]: combo[i] for i in range(len(slot_names))}
            build_id = f"build_{total:05d}"
            snapshot = self._adapter.assemble_build(build_id, slot_map)
            combinations.append(snapshot)
            total += 1

        return CombinationBatch(combinations, total, slot_names)

    def combine_greedy(
        self,
        slot_candidates: dict[str, list[tuple[ItemCandidate, TierAssignment]]],
    ) -> BuildSnapshot:
        # Pick best (first) candidate per slot
        slot_map = {
            slot: candidates[0]
            for slot, candidates in slot_candidates.items()
            if candidates
        }
        return self._adapter.assemble_build("greedy_best", slot_map)
