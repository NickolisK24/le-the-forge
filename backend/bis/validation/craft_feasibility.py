from __future__ import annotations

from dataclasses import dataclass, field

from crafting.models.craft_state import CraftState, AffixState
from crafting.simulation.monte_carlo_crafting import MonteCarloCraftSimulator, MCCraftConfig
from crafting.models.craft_action import CraftAction, ActionType
from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment


@dataclass
class FeasibilityResult:
    candidate_id: str
    feasible: bool
    success_probability: float
    mean_fp_cost: float
    reason: str


class CraftFeasibilityValidator:
    def __init__(self, n_runs: int = 100, min_success_prob: float = 0.1):
        self.n_runs = n_runs
        self.min_success_prob = min_success_prob

    def _make_state(self, candidate: ItemCandidate) -> CraftState:
        return CraftState(
            item_id=candidate.candidate_id,
            item_name=candidate.base_name,
            item_class=candidate.item_class,
            forging_potential=candidate.forging_potential,
            instability=0,
        )

    def _make_actions(
        self, affixes: list[str], tiers: dict[str, int]
    ) -> list[CraftAction]:
        actions: list[CraftAction] = []
        for aid in affixes:
            actions.append(CraftAction(ActionType.ADD_AFFIX, new_affix_id=aid))
            target_t = tiers.get(aid, 1)
            for _ in range(target_t - 1):
                actions.append(CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id=aid))
        return actions

    def validate(
        self, candidate: ItemCandidate, assignment: TierAssignment
    ) -> FeasibilityResult:
        state = self._make_state(candidate)
        actions = self._make_actions(
            list(assignment.affix_tiers.keys()), assignment.affix_tiers
        )
        if not actions:
            return FeasibilityResult(
                candidate.candidate_id, True, 1.0, 0.0, "no actions needed"
            )
        config = MCCraftConfig(n_runs=self.n_runs, base_seed=42)
        mc = MonteCarloCraftSimulator(config)
        result = mc.run(state, actions)
        feasible = result.success_rate >= self.min_success_prob
        return FeasibilityResult(
            candidate.candidate_id,
            feasible,
            result.success_rate,
            result.mean_fp_spent,
            "ok"
            if feasible
            else (
                f"success_rate {result.success_rate:.2f} < threshold {self.min_success_prob}"
            ),
        )

    def validate_batch(
        self, candidates: list[ItemCandidate], assignment: TierAssignment
    ) -> list[FeasibilityResult]:
        return [self.validate(c, assignment) for c in candidates]
