from __future__ import annotations

from dataclasses import dataclass
import itertools


@dataclass
class TierAssignment:
    affix_tiers: dict[str, int]  # affix_id → tier
    total_tier_sum: int


class TierRangeExpander:
    def expand(
        self,
        affixes: list[str],
        min_tier: int = 1,
        max_tier: int = 7,
        target_tiers: dict[str, int] | None = None,
    ) -> list[TierAssignment]:
        # For each affix, tier range is [min_tier, target_tiers.get(id, max_tier)]
        ranges: list[range] = []
        for a in affixes:
            top = target_tiers.get(a, max_tier) if target_tiers else max_tier
            ranges.append(range(min_tier, top + 1))
        assignments: list[TierAssignment] = []
        for combo in itertools.product(*ranges):
            d = dict(zip(affixes, combo))
            assignments.append(TierAssignment(d, sum(combo)))
        return assignments

    def expand_with_budget(
        self,
        affixes: list[str],
        tier_budget: int,
        min_tier: int = 1,
    ) -> list[TierAssignment]:
        # Only return assignments where total_tier_sum <= tier_budget
        return [
            a
            for a in self.expand(affixes, min_tier, 7)
            if a.total_tier_sum <= tier_budget
        ]

    def top_assignment(
        self, affixes: list[str], max_tier: int = 7
    ) -> TierAssignment:
        # Returns assignment with all affixes at max_tier
        d = {a: max_tier for a in affixes}
        return TierAssignment(d, max_tier * len(affixes))
