"""Read-only repository over Forge-safe affix records."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoader, ForgeSafeAffixRecord


class ForgeSafeAffixRepository:
    def __init__(self, export_path: str | Path) -> None:
        self.export_path = Path(export_path)
        self._records: list[ForgeSafeAffixRecord] | None = None
        self._by_id: dict[str, ForgeSafeAffixRecord] = {}

    def load(self, *, force: bool = False) -> list[ForgeSafeAffixRecord]:
        if self._records is None or force:
            self._records = ForgeSafeAffixLoader(self.export_path).load()
            self._by_id = {record.id: record for record in self._records}
        return list(self._records)

    def all(self) -> list[ForgeSafeAffixRecord]:
        return self.load()

    def get(self, affix_id: str) -> ForgeSafeAffixRecord | None:
        self.load()
        return self._by_id.get(str(affix_id))

    def summary(self) -> dict:
        records = self.load()
        source_types = Counter(r.source_type or "unknown" for r in records)
        item_types = Counter(item for r in records for item in r.item_types)
        return {
            "data_source": "forge_safe",
            "count": len(records),
            "source_types": dict(sorted(source_types.items())),
            "item_types": dict(sorted(item_types.items())),
            "export_path": str(self.export_path),
            "production_consumer": False,
        }
