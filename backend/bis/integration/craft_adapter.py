from dataclasses import dataclass, field

from bis.generator.item_candidate_generator import ItemCandidate
from bis.generator.tier_range_expander import TierAssignment
from bis.validation.craft_feasibility import CraftFeasibilityValidator, FeasibilityResult


@dataclass
class CraftAdapterResult:
    candidate_id: str
    assignment: TierAssignment
    feasibility: FeasibilityResult
    adjusted_tiers: dict[str, int]  # tiers adjusted down if infeasible


class CraftAdapter:
    def __init__(self, n_runs: int = 50, min_prob: float = 0.1):
        self._validator = CraftFeasibilityValidator(n_runs=n_runs, min_success_prob=min_prob)

    def evaluate(self, candidate: ItemCandidate, assignment: TierAssignment) -> CraftAdapterResult:
        feasibility = self._validator.validate(candidate, assignment)
        adjusted = dict(assignment.affix_tiers)
        if not feasibility.feasible:
            # Reduce all tiers by 1 as fallback
            adjusted = {k: max(1, v - 1) for k, v in adjusted.items()}
        return CraftAdapterResult(candidate.candidate_id, assignment, feasibility, adjusted)

    def evaluate_batch(
        self,
        candidates_assignments: list[tuple[ItemCandidate, TierAssignment]],
    ) -> list[CraftAdapterResult]:
        return [self.evaluate(c, a) for c, a in candidates_assignments]

    def filter_feasible(self, results: list[CraftAdapterResult]) -> list[CraftAdapterResult]:
        return [r for r in results if r.feasibility.feasible]
