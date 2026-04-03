from dataclasses import dataclass, field
import time


@dataclass
class SearchMetrics:
    total_candidates_evaluated: int
    total_pruned: int
    cache_hits: int
    cache_misses: int
    search_duration_s: float
    candidates_per_second: float
    prune_rate: float
    cache_hit_rate: float


class SearchMetricsCollector:
    def __init__(self):
        self._evaluated: int = 0
        self._pruned: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._start_time: float | None = None
        self._end_time: float | None = None

    def start(self) -> None:
        self._start_time = time.time()

    def stop(self) -> None:
        self._end_time = time.time()

    def record_evaluated(self, n: int = 1) -> None:
        self._evaluated += n

    def record_pruned(self, n: int = 1) -> None:
        self._pruned += n

    def record_cache_hit(self) -> None:
        self._cache_hits += 1

    def record_cache_miss(self) -> None:
        self._cache_misses += 1

    def collect(self) -> SearchMetrics:
        duration = (self._end_time or time.time()) - (self._start_time or time.time())
        total_cache = self._cache_hits + self._cache_misses
        return SearchMetrics(
            total_candidates_evaluated=self._evaluated,
            total_pruned=self._pruned,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            search_duration_s=duration,
            candidates_per_second=self._evaluated / duration if duration > 0 else 0.0,
            prune_rate=self._pruned / max(self._evaluated + self._pruned, 1),
            cache_hit_rate=self._cache_hits / total_cache if total_cache > 0 else 0.0,
        )

    def reset(self) -> None:
        self.__init__()
