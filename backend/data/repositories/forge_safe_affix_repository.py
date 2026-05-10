"""Repository for controlled Forge-safe canonical affix consumption.

This repository is an internal lookup layer over the validated Forge-safe
affix export. It is not wired into planner, crafting, simulation, API, or
production affix behavior by default.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from data.loaders.forge_safe_affixes_loader import (
    ForgeSafeAffixExport,
    ForgeSafeAffixLoader,
)

__all__ = [
    "ForgeSafeAffixRepository",
    "ForgeSafeAffixRepositoryNotLoadedError",
]


class ForgeSafeAffixRepositoryNotLoadedError(RuntimeError):
    """Raised when repository methods are used before load()."""


class ForgeSafeAffixRepository:
    """Read-only repository over a validated Forge-safe affix export."""

    def __init__(
        self,
        export_path: str | Path | None = None,
        *,
        loader: ForgeSafeAffixLoader | None = None,
    ) -> None:
        self._export_path = Path(export_path) if export_path is not None else None
        self._loader = loader or ForgeSafeAffixLoader()
        self._export: ForgeSafeAffixExport | None = None
        self._records: tuple[dict[str, Any], ...] = ()
        self._by_affix_id: dict[str, dict[str, Any]] = {}

    def load(self, export_path: str | Path | None = None) -> "ForgeSafeAffixRepository":
        """Load and index the configured Forge-safe affix export."""

        if export_path is not None:
            self._export_path = Path(export_path)
        if self._export_path is None:
            raise ValueError("ForgeSafeAffixRepository requires an explicit export path.")

        loaded = self._loader.load(self._export_path)
        records = tuple(deepcopy(record) for record in loaded.records)
        self._export = loaded
        self._records = records
        self._by_affix_id = {str(record["affix_id"]): record for record in records}
        return self

    def is_loaded(self) -> bool:
        return self._export is not None

    def count(self) -> int:
        return len(self._records) if self.is_loaded() else 0

    def list_affixes(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        """Return affix records in export order."""

        self._require_loaded()
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in self._records[start:end]]

    def get_by_affix_id(self, affix_id: int | str) -> dict[str, Any] | None:
        """Return one affix by source affix ID, or None when missing."""

        self._require_loaded()
        record = self._by_affix_id.get(str(affix_id))
        return deepcopy(record) if record is not None else None

    def search(self, query: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Search by affix ID, affix_name, or display_name."""

        self._require_loaded()
        needle = query.strip().lower()
        if not needle:
            return []
        matches = [
            record for record in self._records
            if _record_matches_search(record, needle)
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def filter_by_source_type(self, source_type: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Filter records by source_type."""

        self._require_loaded()
        expected = source_type.strip().lower()
        matches = [
            record for record in self._records
            if str(record.get("source_type", "")).lower() == expected
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def filter_by_item_type(self, item_type: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Filter records by item_type or eligible_item_types."""

        self._require_loaded()
        expected = item_type.strip().lower()
        matches = [
            record for record in self._records
            if _record_matches_item_type(record, expected)
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def get_summary(self) -> dict[str, Any]:
        """Return loader/export metadata preserved by the repository."""

        self._require_loaded()
        assert self._export is not None
        summary = deepcopy(self._export.summary)
        return {
            "source_path": str(self._export.source_path),
            "loaded_record_count": self.count(),
            "warning_count": len(self._export.warnings),
            "warnings": list(self._export.warnings),
            "export_policy": self._export.export_policy,
            "export_status": summary.get("export_status"),
            "total_affix_records_seen": summary.get("total_affix_records_seen"),
            "excluded_affix_records": summary.get("excluded_affix_records"),
            "summary": summary,
        }

    def _require_loaded(self) -> None:
        if not self.is_loaded():
            raise ForgeSafeAffixRepositoryNotLoadedError(
                "ForgeSafeAffixRepository is not loaded. Call load() first."
            )


def _record_matches_search(record: dict[str, Any], needle: str) -> bool:
    values = [
        record.get("affix_id"),
        record.get("affix_name"),
        record.get("display_name"),
    ]
    return any(needle in str(value).lower() for value in values if value is not None)


def _record_matches_item_type(record: dict[str, Any], expected: str) -> bool:
    item_type = str(record.get("item_type", "")).lower()
    if item_type == expected:
        return True
    eligible = record.get("eligible_item_types") or []
    return any(str(value).lower() == expected for value in eligible)
