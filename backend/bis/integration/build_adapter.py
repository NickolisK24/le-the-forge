from __future__ import annotations

from dataclasses import dataclass, field

from crafting.models.craft_state import CraftState, AffixState
from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment


@dataclass
class BuildSnapshot:
    build_id: str
    slots: dict[str, CraftState]  # slot_type → CraftState
    total_affix_count: int
    total_tier_sum: int


class BuildAdapter:
    def candidate_to_state(
        self, candidate: ItemCandidate, assignment: TierAssignment
    ) -> CraftState:
        affixes = [
            AffixState(aid, tier, 7)
            for aid, tier in assignment.affix_tiers.items()
        ]
        return CraftState(
            item_id=candidate.candidate_id,
            item_name=candidate.base_name,
            item_class=candidate.item_class,
            forging_potential=candidate.forging_potential,
            instability=0,
            affixes=affixes,
        )

    def assemble_build(
        self,
        build_id: str,
        slot_items: dict[str, tuple[ItemCandidate, TierAssignment]],
    ) -> BuildSnapshot:
        slots: dict[str, CraftState] = {}
        total_affixes = 0
        total_tiers = 0
        for slot_type, (candidate, assignment) in slot_items.items():
            state = self.candidate_to_state(candidate, assignment)
            slots[slot_type] = state
            total_affixes += len(state.affixes)
            total_tiers += assignment.total_tier_sum
        return BuildSnapshot(build_id, slots, total_affixes, total_tiers)

    def extract_affixes(
        self, snapshot: BuildSnapshot
    ) -> dict[str, list[str]]:
        return {
            slot: [a.affix_id for a in state.affixes]
            for slot, state in snapshot.slots.items()
        }
