from dataclasses import dataclass, field

from bis.ranking.ranking_engine import RankedEntry, RankingEngine
from bis.scoring.build_score_engine import BuildScore


@dataclass
class TopNResult:
    entries: list[RankedEntry]
    total_evaluated: int
    top_n: int
    min_score_threshold: float
    score_range: tuple[float, float]  # (min, max) in top-N


class TopSelector:
    def __init__(self, ranking_engine: RankingEngine | None = None):
        self._ranker = ranking_engine or RankingEngine()

    def select(
        self,
        scores: list[BuildScore],
        n: int = 10,
        min_score: float = 0.0,
    ) -> TopNResult:
        filtered = [s for s in scores if s.total_score >= min_score]
        ranked = self._ranker.top_n(filtered, n)
        total = len(scores)
        if ranked:
            score_vals = [r.score.total_score for r in ranked]
            score_range = (min(score_vals), max(score_vals))
        else:
            score_range = (0.0, 0.0)
        return TopNResult(ranked, total, n, min_score, score_range)

    def select_per_slot(self, scores: list[BuildScore], slot: str, n: int = 5) -> TopNResult:
        ranked = self._ranker.rank_by_slot(scores, slot)[:n]
        if ranked:
            score_vals = [r.score.slot_scores.get(slot, 0.0) for r in ranked]
            score_range = (min(score_vals), max(score_vals))
        else:
            score_range = (0.0, 0.0)
        return TopNResult(ranked, len(scores), n, 0.0, score_range)
