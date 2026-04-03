from __future__ import annotations

from dataclasses import dataclass, field

from bis.integration.build_adapter import BuildSnapshot


@dataclass
class BuildScore:
    build_id: str
    total_score: float        # 0.0–1.0
    tier_score: float         # average tier across all affixes / 7
    coverage_score: float     # fraction of target affixes present
    fp_score: float           # average FP efficiency across slots
    slot_scores: dict[str, float] = field(default_factory=dict)


class BuildScoreEngine:
    def score(
        self,
        snapshot: BuildSnapshot,
        target_affixes: list[str],
        target_tiers: dict[str, int],
        weights: dict[str, float] | None = None,
    ) -> BuildScore:
        weights = weights or {"tier": 0.5, "coverage": 0.4, "fp": 0.1}

        all_affixes: dict[str, int] = {
            a.affix_id: a.current_tier
            for state in snapshot.slots.values()
            for a in state.affixes
        }

        # Coverage: fraction of target affixes present
        coverage = sum(1 for a in target_affixes if a in all_affixes) / max(
            len(target_affixes), 1
        )

        # Tier score: for target affixes that are present, how close to target tier
        tier_scores: list[float] = []
        for aid in target_affixes:
            if aid in all_affixes:
                t = all_affixes[aid]
                target_t = target_tiers.get(aid, 7)
                tier_scores.append(min(t / target_t, 1.0))
        tier_score = sum(tier_scores) / max(len(target_affixes), 1)

        # FP score: average remaining FP / initial FP (rough proxy: fp/100)
        fp_vals = [
            min(s.forging_potential / 100, 1.0) for s in snapshot.slots.values()
        ]
        fp_score = sum(fp_vals) / max(len(fp_vals), 1) if fp_vals else 0.0

        # Per-slot scores
        slot_scores: dict[str, float] = {}
        for slot, state in snapshot.slots.items():
            slot_affixes = {a.affix_id: a.current_tier for a in state.affixes}
            slot_target = [a for a in target_affixes if a in slot_affixes]
            if slot_target:
                slot_scores[slot] = sum(
                    slot_affixes[a] / target_tiers.get(a, 7) for a in slot_target
                ) / len(slot_target)
            else:
                slot_scores[slot] = 0.0

        total = (
            weights.get("tier", 0.5) * tier_score
            + weights.get("coverage", 0.4) * coverage
            + weights.get("fp", 0.1) * fp_score
        )

        return BuildScore(
            snapshot.build_id,
            round(total, 4),
            round(tier_score, 4),
            round(coverage, 4),
            round(fp_score, 4),
            slot_scores,
        )
