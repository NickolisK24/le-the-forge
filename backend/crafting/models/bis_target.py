from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AffixRequirement:
    affix_id: str
    min_tier: int = 1
    target_tier: int = 7
    required: bool = True   # if False, "nice to have"


@dataclass
class BisTarget:
    item_class: str
    requirements: list[AffixRequirement] = field(default_factory=list)
    min_success_probability: float = 0.5  # stop if below this threshold
    max_fp_budget: int = 200

    @property
    def required_affixes(self) -> list[str]:
        return [r.affix_id for r in self.requirements if r.required]

    @property
    def target_tiers(self) -> dict[str, int]:
        return {r.affix_id: r.target_tier for r in self.requirements}

    def is_satisfied(self, state) -> bool:
        present = {a.affix_id: a.current_tier for a in state.affixes}
        for req in self.requirements:
            if req.required:
                if req.affix_id not in present:
                    return False
                if present[req.affix_id] < req.min_tier:
                    return False
        return True

    def satisfaction_rate(self, state) -> float:
        if not self.requirements:
            return 1.0
        satisfied = sum(1 for r in self.requirements
                        if any(a.affix_id == r.affix_id and a.current_tier >= r.min_tier
                               for a in state.affixes))
        return satisfied / len(self.requirements)
