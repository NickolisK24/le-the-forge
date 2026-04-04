from dataclasses import dataclass, field
from collections import OrderedDict
import time


@dataclass
class SearchCacheEntry:
    key: str
    result: object
    created_at: float
    ttl: float  # 0 = never expires
    hit_count: int = 0


class SearchCache:
    def __init__(self, max_size: int = 500, default_ttl: float = 600.0):
        self._cache: OrderedDict[str, SearchCacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl

    def _is_expired(self, entry: SearchCacheEntry) -> bool:
        return entry.ttl > 0 and time.time() - entry.created_at > entry.ttl

    def get(self, key: str) -> object | None:
        entry = self._cache.get(key)
        if entry is None or self._is_expired(entry):
            return None
        entry.hit_count += 1
        return entry.result

    def set(self, key: str, result: object, ttl: float | None = None) -> None:
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._cache.popitem(last=False)
        self._cache[key] = SearchCacheEntry(
            key,
            result,
            time.time(),
            ttl if ttl is not None else self.default_ttl,
        )

    def invalidate(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> dict:
        entries = list(self._cache.values())
        expired = sum(1 for e in entries if self._is_expired(e))
        total_hits = sum(e.hit_count for e in entries)
        return {
            "size": len(entries),
            "max_size": self.max_size,
            "expired": expired,
            "total_hits": total_hits,
        }

    def __len__(self) -> int:
        return len(self._cache)
