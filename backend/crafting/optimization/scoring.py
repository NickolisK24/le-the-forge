from __future__ import annotations
from dataclasses import dataclass

from crafting.models.craft_state import CraftState


@dataclass
class CraftScore:
    total: float          # 0.0–1.0 composite
    tier_score: float     # fraction of target tiers achieved
    completion_score: float  # fraction of target affixes present
    fp_efficiency: float  # 1 - fp_spent / max_fp
    penalty: float        # fracture/destruction penalty


class CraftScorer:
    def score(self, state: CraftState, target_affixes: list[str],
              target_tiers: dict[str, int], initial_fp: int,
              fractured_penalty: float = 0.5) -> CraftScore:
        # completion: how many target affixes are present
        present = {a.affix_id for a in state.affixes}
        completion = sum(1 for aid in target_affixes if aid in present) / max(len(target_affixes), 1)

        # tier score: for present affixes, how close to target tier
        tier_scores = []
        for a in state.affixes:
            if a.affix_id in target_affixes:
                target_t = target_tiers.get(a.affix_id, a.max_tier)
                tier_scores.append(min(a.current_tier / target_t, 1.0))
        tier_score = sum(tier_scores) / max(len(target_affixes), 1)

        # FP efficiency
        fp_efficiency = state.forging_potential / max(initial_fp, 1)

        # penalty
        penalty = fractured_penalty if state.is_fractured else 0.0

        total = (completion * 0.4 + tier_score * 0.4 + fp_efficiency * 0.2) * (1 - penalty)
        return CraftScore(round(total, 4), round(tier_score, 4), round(completion, 4),
                          round(fp_efficiency, 4), penalty)

    def score_sequence(self, sequence_result, target_affixes, target_tiers, initial_fp) -> CraftScore:
        return self.score(sequence_result.final_state, target_affixes, target_tiers, initial_fp)
