from dataclasses import dataclass, field
import time

from bis.models.item_slot import SlotPool
from bis.generator.item_candidate_generator import ItemCandidateGenerator
from bis.generator.tier_range_expander import TierRangeExpander, TierAssignment
from bis.integration.build_adapter import BuildAdapter, BuildSnapshot
from bis.scoring.build_score_engine import BuildScoreEngine, BuildScore
from bis.ranking.top_selector import TopSelector
from bis.models.bis_result import BisResult


@dataclass
class SearchStage:
    stage_id: int
    candidates_evaluated: int
    best_score: float
    elapsed_s: float


class IncrementalSearchEngine:
    def __init__(self, n_runs_per_eval: int = 50):
        self.n_runs_per_eval = n_runs_per_eval
        self._generator = ItemCandidateGenerator()
        self._tier_expander = TierRangeExpander()
        self._adapter = BuildAdapter()
        self._scorer = BuildScoreEngine()
        self._selector = TopSelector()
        self._stages: list[SearchStage] = []

    def search(
        self,
        slot_pool: SlotPool,
        target_affixes: list[str],
        target_tiers: dict[str, int],
        top_n: int = 10,
        max_candidates: int = 500,
    ) -> BisResult:
        t0 = time.time()
        search_id = f"search_{int(t0)}"

        all_scores: list[BuildScore] = []
        evaluated = 0

        for slot in slot_pool.enabled_slots():
            candidates = self._generator.generate(slot, limit=3)
            top_assignment = self._tier_expander.top_assignment(target_affixes[:4])

            for candidate in candidates:
                if evaluated >= max_candidates:
                    break
                snapshot = self._adapter.candidate_to_state(candidate, top_assignment)
                build_snap = BuildSnapshot(
                    build_id=f"snap_{evaluated:04d}",
                    slots={slot.slot_type.value: snapshot},
                    total_affix_count=len(snapshot.affixes),
                    total_tier_sum=top_assignment.total_tier_sum,
                )
                score = self._scorer.score(build_snap, target_affixes, target_tiers)
                all_scores.append(score)
                evaluated += 1

            self._stages.append(
                SearchStage(
                    len(self._stages),
                    evaluated,
                    max((s.total_score for s in all_scores), default=0.0),
                    time.time() - t0,
                )
            )

        result = self._selector.select(all_scores, top_n)
        return BisResult(
            search_id,
            result.entries,
            evaluated,
            time.time() - t0,
            target_affixes,
            target_tiers,
        )

    def get_stages(self) -> list[SearchStage]:
        return list(self._stages)
