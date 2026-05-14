"""Repository for controlled Forge-safe affix bundle consumption.

The bundle repository is a read-only lookup layer over the validated
last-epoch-data Forge-safe affix bundle. It preserves affix/modifier
relationships for experimental inspection without replacing production
planner, crafting, simulation, or existing affix behavior.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from data.loaders.forge_safe_affix_bundle_loader import (
    ForgeSafeAffixBundle,
    ForgeSafeAffixBundleLoader,
)

__all__ = [
    "ForgeSafeAffixBundleRepository",
    "ForgeSafeAffixBundleRepositoryNotLoadedError",
]


class ForgeSafeAffixBundleRepositoryNotLoadedError(RuntimeError):
    """Raised when repository methods are used before load()."""


class ForgeSafeAffixBundleRepository:
    """Read-only repository over a validated Forge-safe affix bundle."""

    def __init__(
        self,
        export_path: str | Path | None = None,
        *,
        loader: ForgeSafeAffixBundleLoader | None = None,
    ) -> None:
        self._export_path = Path(export_path) if export_path is not None else None
        self._loader = loader or ForgeSafeAffixBundleLoader()
        self._bundle: ForgeSafeAffixBundle | None = None
        self._affixes: tuple[dict[str, Any], ...] = ()
        self._modifiers: tuple[dict[str, Any], ...] = ()
        self._modifiers_by_affix_identity: dict[str, tuple[dict[str, Any], ...]] = {}
        self._affix_by_id: dict[str, dict[str, Any]] = {}
        self._affix_by_identity: dict[str, dict[str, Any]] = {}

    def load(self, export_path: str | Path | None = None) -> "ForgeSafeAffixBundleRepository":
        """Load and index the configured Forge-safe affix bundle."""

        if export_path is not None:
            self._export_path = Path(export_path)
        if self._export_path is None:
            raise ValueError("ForgeSafeAffixBundleRepository requires an explicit export path.")

        loaded = self._loader.load(self._export_path)
        affixes = tuple(deepcopy(record) for record in loaded.affixes)
        modifiers = tuple(deepcopy(record) for record in loaded.modifiers)
        modifier_index = {
            identity: tuple(deepcopy(modifier) for modifier in values)
            for identity, values in loaded.modifiers_by_affix_identity.items()
        }

        self._bundle = loaded
        self._affixes = affixes
        self._modifiers = modifiers
        self._modifiers_by_affix_identity = modifier_index
        self._affix_by_id = {str(record["affix_id"]): record for record in affixes}
        self._affix_by_identity = {
            _source_affix_identity(record): record
            for record in affixes
        }
        return self

    def is_loaded(self) -> bool:
        return self._bundle is not None

    def count_affixes(self) -> int:
        return len(self._affixes) if self.is_loaded() else 0

    def count_modifiers(self) -> int:
        return len(self._modifiers) if self.is_loaded() else 0

    def list_affixes(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        """Return affix records in bundle order."""

        self._require_loaded()
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in self._affixes[start:end]]

    def get_affix(self, affix_id: int | str) -> dict[str, Any] | None:
        """Return one affix by source affix ID, or None when missing."""

        self._require_loaded()
        record = self._affix_by_id.get(str(affix_id))
        return deepcopy(record) if record is not None else None

    def get_affix_with_modifiers(self, affix_id: int | str) -> dict[str, Any] | None:
        """Return an affix plus its validated modifiers."""

        self._require_loaded()
        record = self._affix_by_id.get(str(affix_id))
        if record is None:
            return None
        identity = _source_affix_identity(record)
        modifiers = self._modifiers_by_affix_identity.get(identity, ())
        return {
            "affix": deepcopy(record),
            "modifiers": [deepcopy(modifier) for modifier in modifiers],
            "modifier_count": len(modifiers),
        }

    def get_by_source_affix_identity(self, source_affix_identity: str) -> dict[str, Any] | None:
        """Return one affix by canonical source affix identity."""

        self._require_loaded()
        record = self._affix_by_identity.get(source_affix_identity)
        return deepcopy(record) if record is not None else None

    def get_modifiers_for_affix(self, source_affix_identity: str) -> list[dict[str, Any]]:
        """Return validated modifier records for a source affix identity."""

        self._require_loaded()
        return [
            deepcopy(modifier)
            for modifier in self._modifiers_by_affix_identity.get(source_affix_identity, ())
        ]

    def search_affixes(self, query: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Search affixes by ID, name, display name, or source identity."""

        self._require_loaded()
        needle = query.strip().lower()
        if not needle:
            return []
        matches = [
            record for record in self._affixes
            if _record_matches_search(record, needle)
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def filter_by_source_type(self, source_type: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Filter records by source_type."""

        self._require_loaded()
        expected = source_type.strip().lower()
        matches = [
            record for record in self._affixes
            if str(record.get("source_type", "")).lower() == expected
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def filter_by_item_type(self, item_type: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Filter records by item_type or eligible_item_types."""

        self._require_loaded()
        expected = item_type.strip().lower()
        matches = [
            record for record in self._affixes
            if _record_matches_item_type(record, expected)
        ]
        return [deepcopy(record) for record in matches[: max(0, limit)]]

    def get_summary(self) -> dict[str, Any]:
        """Return bundle metadata preserved by the repository."""

        self._require_loaded()
        assert self._bundle is not None
        summary = deepcopy(self._bundle.summary)
        cross_reference = deepcopy(self._bundle.cross_reference_validation)
        return {
            "source_path": str(self._bundle.source_path),
            "loaded_affix_count": self.count_affixes(),
            "loaded_modifier_count": self.count_modifiers(),
            "warning_count": len(self._bundle.warnings),
            "warnings": list(self._bundle.warnings),
            "schema_version": self._bundle.schema_version,
            "export_policy": self._bundle.export_policy,
            "export_status": summary.get("export_status"),
            "total_affix_records_seen": summary.get("total_affix_records_seen"),
            "total_modifier_records_seen": summary.get("total_modifier_records_seen"),
            "excluded_affix_records": summary.get("excluded_record_count"),
            "summary": summary,
            "cross_reference_validation": cross_reference,
        }

    def _require_loaded(self) -> None:
        if not self.is_loaded():
            raise ForgeSafeAffixBundleRepositoryNotLoadedError(
                "ForgeSafeAffixBundleRepository is not loaded. Call load() first."
            )


def _source_affix_identity(record: dict[str, Any]) -> str:
    provenance = record.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_affix_identity"):
        return str(provenance["source_affix_identity"])
    return ""


def _record_matches_search(record: dict[str, Any], needle: str) -> bool:
    values = [
        record.get("affix_id"),
        record.get("affix_name"),
        record.get("display_name"),
        _source_affix_identity(record),
    ]
    return any(needle in str(value).lower() for value in values if value is not None)


def _record_matches_item_type(record: dict[str, Any], expected: str) -> bool:
    item_type = str(record.get("item_type", "")).lower()
    if item_type == expected:
        return True
    eligible = record.get("eligible_item_types") or []
    return any(str(value).lower() == expected for value in eligible)
