from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class BisLogEntry:
    event_type: str  # "search_start", "search_complete", "candidate_evaluated",
                     # "cache_hit", "prune", "error"
    search_id: str | None
    data: dict
    timestamp: float = field(default_factory=time.time)


class BisSearchLogger:
    def __init__(self, capacity: int = 2000):
        self._entries: deque[BisLogEntry] = deque(maxlen=capacity)

    def log_search_start(self, search_id: str, target_affixes: list[str], n_slots: int) -> None:
        self._append("search_start", search_id, {"affixes": target_affixes, "n_slots": n_slots})

    def log_search_complete(
        self,
        search_id: str,
        total_evaluated: int,
        best_score: float,
        duration_s: float,
    ) -> None:
        self._append(
            "search_complete",
            search_id,
            {"evaluated": total_evaluated, "best_score": best_score, "duration_s": duration_s},
        )

    def log_candidate_evaluated(self, search_id: str, candidate_id: str, score: float) -> None:
        self._append(
            "candidate_evaluated",
            search_id,
            {"candidate_id": candidate_id, "score": score},
        )

    def log_cache_hit(self, search_id: str, key: str) -> None:
        self._append("cache_hit", search_id, {"key": key})

    def log_prune(self, search_id: str, pruned_count: int, reason: str) -> None:
        self._append("prune", search_id, {"pruned_count": pruned_count, "reason": reason})

    def log_error(self, search_id: str | None, error: str) -> None:
        self._append("error", search_id, {"error": error})

    def _append(self, event_type: str, search_id: str | None, data: dict) -> None:
        self._entries.append(BisLogEntry(event_type, search_id, data))

    def get_entries(
        self,
        event_type: str | None = None,
        search_id: str | None = None,
    ) -> list[BisLogEntry]:
        entries = list(self._entries)
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        if search_id:
            entries = [e for e in entries if e.search_id == search_id]
        return entries

    def summary(self) -> dict:
        entries = list(self._entries)
        by_type: dict[str, int] = {}
        for e in entries:
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        searches = by_type.get("search_complete", 0)
        evaluated = sum(
            e.data.get("evaluated", 0)
            for e in entries
            if e.event_type == "search_complete"
        )
        return {
            "total_entries": len(entries),
            "by_type": by_type,
            "searches_completed": searches,
            "total_evaluated": evaluated,
        }

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
