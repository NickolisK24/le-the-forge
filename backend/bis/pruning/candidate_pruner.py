from __future__ import annotations

from dataclasses import dataclass

from bis.validation.craft_feasibility import FeasibilityResult
from bis.generator.tier_range_expander import TierAssignment


@dataclass
class PruneResult:
    kept: list
    pruned: list
    prune_rate: float


class CandidatePruner:
    def __init__(
        self,
        min_fp: int = 0,
        max_fp: int = 200,
        min_tier_sum: int = 0,
        min_success_prob: float = 0.0,
    ):
        self.min_fp = min_fp
        self.max_fp = max_fp
        self.min_tier_sum = min_tier_sum
        self.min_success_prob = min_success_prob

    def prune_by_feasibility(
        self, results: list[FeasibilityResult]
    ) -> PruneResult:
        kept = [
            r
            for r in results
            if r.feasible and r.success_probability >= self.min_success_prob
        ]
        pruned = [r for r in results if r not in kept]
        total = len(results)
        return PruneResult(kept, pruned, len(pruned) / total if total else 0.0)

    def prune_by_tier(
        self, assignments: list[TierAssignment]
    ) -> PruneResult:
        kept = [a for a in assignments if a.total_tier_sum >= self.min_tier_sum]
        pruned = [a for a in assignments if a not in kept]
        total = len(assignments)
        return PruneResult(kept, pruned, len(pruned) / total if total else 0.0)

    def prune_dominated(
        self, scored_candidates: list[tuple]
    ) -> PruneResult:
        # scored_candidates: list of (candidate, score)
        # Prune any candidate dominated by another with same or fewer affixes but higher score.
        if not scored_candidates:
            return PruneResult([], [], 0.0)
        sorted_c = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
        kept = sorted_c[: max(1, len(sorted_c) // 2)]  # keep top half
        pruned = sorted_c[len(kept):]
        total = len(scored_candidates)
        return PruneResult(
            [c for c, _ in kept],
            [c for c, _ in pruned],
            len(pruned) / total if total else 0.0,
        )
