from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    key: str
    data: object
    created_at: float
    ttl: float          # seconds; 0 = never expires
    hit_count: int = 0


class VisualCache:
    def __init__(self, max_size: int = 200, default_ttl: float = 300.0) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Return True when the entry has exceeded its TTL."""
        if entry.ttl == 0:
            return False
        return time.time() - entry.created_at > entry.ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> object | None:
        """
        Return the cached data for *key*, or None if the key is missing or
        the entry has expired. Increments hit_count on a valid hit.
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        if self._is_expired(entry):
            return None
        entry.hit_count += 1
        return entry.data

    def set(self, key: str, data: object, ttl: float | None = None) -> None:
        """
        Store *data* under *key*.

        If the cache is already at capacity the oldest entry is evicted first.
        Uses *default_ttl* when *ttl* is not provided.
        """
        effective_ttl = self.default_ttl if ttl is None else ttl

        # If the key already exists, remove it so it will be re-inserted at the end
        # (most-recently-used position in the OrderedDict).
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            # Evict the oldest (first) entry
            self._cache.popitem(last=False)

        self._cache[key] = CacheEntry(
            key=key,
            data=data,
            created_at=time.time(),
            ttl=effective_ttl,
        )

    def invalidate(self, key: str) -> bool:
        """Remove *key* from the cache. Returns True if it existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._cache.clear()

    def stats(self) -> dict:
        """
        Return cache statistics::

            {
                "size": int,
                "max_size": int,
                "total_hits": int,
                "expired_keys": int,   # entries that have expired but not yet evicted
            }
        """
        total_hits = 0
        expired_keys = 0
        for entry in self._cache.values():
            total_hits += entry.hit_count
            if self._is_expired(entry):
                expired_keys += 1
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "expired_keys": expired_keys,
        }

    def evict_expired(self) -> int:
        """Remove all expired entries and return the count removed."""
        expired = [k for k, v in self._cache.items() if self._is_expired(v)]
        for key in expired:
            del self._cache[key]
        return len(expired)

    def __len__(self) -> int:
        return len(self._cache)
