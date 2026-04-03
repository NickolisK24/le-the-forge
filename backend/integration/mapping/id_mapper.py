from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class MappingEntry:
    external_id: str
    internal_id: str
    category: str        # "skill", "item", "passive"
    version_added: str = "1.0"


@dataclass
class MappingResult:
    external_id: str
    internal_id: str | None
    found: bool
    category: str
    fallback_used: bool = False


class IdMapper:
    def __init__(self):
        self._mappings: dict[str, dict[str, MappingEntry]] = {
            "skill": {}, "item": {}, "passive": {}
        }

    def register(self, entry: MappingEntry) -> None:
        """Register a single mapping entry."""
        self._mappings.setdefault(entry.category, {})[entry.external_id] = entry

    def register_bulk(self, entries: list[MappingEntry]) -> None:
        """Register multiple mapping entries at once."""
        for e in entries:
            self.register(e)

    def map(self, external_id: str, category: str) -> MappingResult:
        """Translate an external ID to an internal ID for the given category."""
        cat = self._mappings.get(category, {})
        entry = cat.get(external_id)
        if entry:
            return MappingResult(external_id, entry.internal_id, True, category)
        return MappingResult(external_id, None, False, category)

    def map_with_fallback(
        self, external_id: str, category: str, fallback_id: str
    ) -> MappingResult:
        """Translate an external ID; use fallback_id when no mapping is found."""
        result = self.map(external_id, category)
        if not result.found:
            return MappingResult(external_id, fallback_id, False, category, fallback_used=True)
        return result

    def map_all(self, ids: list[str], category: str) -> list[MappingResult]:
        """Translate a list of external IDs for the given category."""
        return [self.map(eid, category) for eid in ids]

    def unmapped_count(self, ids: list[str], category: str) -> int:
        """Return the number of IDs in the list that have no registered mapping."""
        return sum(1 for r in self.map_all(ids, category) if not r.found)

    def list_category(self, category: str) -> list[MappingEntry]:
        """Return all registered mapping entries for a category."""
        return list(self._mappings.get(category, {}).values())

    def clear_category(self, category: str) -> None:
        """Remove all mappings for the given category."""
        self._mappings[category] = {}
