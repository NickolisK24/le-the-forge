from dataclasses import dataclass, field
import time

from bis.ranking.ranking_engine import RankedEntry
from bis.scoring.build_score_engine import BuildScore


@dataclass
class BisResult:
    search_id: str
    top_entries: list[RankedEntry]
    total_evaluated: int
    search_duration_s: float
    target_affixes: list[str]
    target_tiers: dict[str, int]
    created_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def best(self) -> RankedEntry | None:
        return self.top_entries[0] if self.top_entries else None

    @property
    def best_score(self) -> float:
        return self.best.score.total_score if self.best else 0.0

    def summary(self) -> dict:
        return {
            "search_id": self.search_id,
            "total_evaluated": self.total_evaluated,
            "results_count": len(self.top_entries),
            "best_score": self.best_score,
            "duration_s": round(self.search_duration_s, 3),
            "target_affixes": self.target_affixes,
        }
