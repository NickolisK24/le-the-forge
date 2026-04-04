from dataclasses import dataclass, field

from bis.scoring.build_score_engine import BuildScore


@dataclass
class RankedEntry:
    rank: int
    build_id: str
    score: BuildScore
    percentile: float  # 0.0–100.0


class RankingEngine:
    def rank(self, scores: list[BuildScore]) -> list[RankedEntry]:
        sorted_scores = sorted(scores, key=lambda s: s.total_score, reverse=True)
        n = len(sorted_scores)
        entries = []
        for i, s in enumerate(sorted_scores):
            percentile = (1 - i / n) * 100 if n > 1 else 100.0
            entries.append(RankedEntry(i + 1, s.build_id, s, round(percentile, 1)))
        return entries

    def top_n(self, scores: list[BuildScore], n: int) -> list[RankedEntry]:
        return self.rank(scores)[:n]

    def filter_by_score(self, ranked: list[RankedEntry], min_score: float) -> list[RankedEntry]:
        return [r for r in ranked if r.score.total_score >= min_score]

    def rank_by_slot(self, scores: list[BuildScore], slot: str) -> list[RankedEntry]:
        slot_scores = sorted(scores, key=lambda s: s.slot_scores.get(slot, 0.0), reverse=True)
        n = len(slot_scores)
        return [
            RankedEntry(i + 1, s.build_id, s, (1 - i / n) * 100 if n > 1 else 100.0)
            for i, s in enumerate(slot_scores)
        ]
