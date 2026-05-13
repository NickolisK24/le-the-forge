"""Read-only v2 class/mastery repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2ClassMasteryBundleError(ValueError):
    """Raised when the v2 class/mastery bundle is missing or invalid."""


class V2ClassMasteryRepository:
    """Read-only repository over the generated v2 class/mastery bundle."""

    def __init__(self, bundle_path: str | Path) -> None:
        self.bundle_path = Path(bundle_path)
        self._payload: dict[str, Any] | None = None
        self._classes: tuple[dict[str, Any], ...] = ()
        self._masteries: tuple[dict[str, Any], ...] = ()
        self._classes_by_id: dict[str, dict[str, Any]] = {}
        self._masteries_by_id: dict[str, dict[str, Any]] = {}

    def load(self) -> "V2ClassMasteryRepository":
        return self.load_payload(_read_json(self.bundle_path, "v2 class/mastery bundle"))

    def load_payload(self, payload: dict[str, Any]) -> "V2ClassMasteryRepository":
        classes = _records(payload, "classes")
        masteries = _records(payload, "masteries")
        self._validate(classes, masteries)
        self._payload = deepcopy(payload)
        self._classes = tuple(deepcopy(record) for record in classes)
        self._masteries = tuple(deepcopy(record) for record in masteries)
        self._classes_by_id = {record["canonical_id"]: record for record in self._classes}
        self._masteries_by_id = {record["canonical_id"]: record for record in self._masteries}
        return self

    def list_classes(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._classes, limit=limit, offset=offset)

    def get_class(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._classes_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_classes(self, *, query: str = "", limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        records = list(self._classes)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        return _page(tuple(records), limit=limit, offset=offset)

    def list_masteries(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._masteries, limit=limit, offset=offset)

    def get_mastery(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._masteries_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def get_masteries_by_class(self, class_id: str, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        records = tuple(record for record in self._masteries if record.get("class_id") == class_id)
        return _page(records, limit=limit, offset=offset)

    def filter_masteries(
        self,
        *,
        query: str = "",
        class_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._masteries)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        if class_id:
            expected = class_id.strip().lower()
            records = [record for record in records if str(record.get("class_id", "")).lower() == expected]
        return _page(tuple(records), limit=limit, offset=offset)

    def count_classes(self) -> int:
        return len(self._classes)

    def count_masteries(self) -> int:
        return len(self._masteries)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "bundle_path": str(self.bundle_path),
            "class_count": self.count_classes(),
            "mastery_count": self.count_masteries(),
            "summary": deepcopy(self._payload.get("summary", {}) if self._payload else {}),
            "cross_reference": deepcopy(self._payload.get("cross_reference", {}) if self._payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate(classes: list[Any], masteries: list[Any]) -> None:
        class_ids = _validate_common(classes, "Class")
        mastery_ids = _validate_common(masteries, "Mastery")
        for record in classes:
            canonical_id = record["canonical_id"]
            if not isinstance(record.get("mastery_ids"), list):
                raise V2ClassMasteryBundleError(f"Class {canonical_id} has invalid mastery_ids.")
            for mastery_id in record.get("mastery_ids") or []:
                if mastery_id not in mastery_ids:
                    raise V2ClassMasteryBundleError(f"Class {canonical_id} links missing mastery {mastery_id}.")
        for record in masteries:
            canonical_id = record["canonical_id"]
            if record.get("class_id") not in class_ids:
                raise V2ClassMasteryBundleError(f"Mastery {canonical_id} links missing class {record.get('class_id')}.")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2ClassMasteryBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2ClassMasteryBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict) or not isinstance(records.get(key), list):
        raise V2ClassMasteryBundleError(f"v2 class/mastery bundle records.{key} must be a list.")
    return records[key]


def _validate_common(records: list[Any], label: str) -> set[str]:
    seen: set[str] = set()
    ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise V2ClassMasteryBundleError(f"{label} record {index} must be an object.")
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            raise V2ClassMasteryBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
        if canonical_id in seen:
            raise V2ClassMasteryBundleError(f"Duplicate canonical_id in v2 class/mastery bundle: {canonical_id}")
        seen.add(canonical_id)
        ids.add(canonical_id)
        if not record.get("display_name"):
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} is missing display_name.")
        provenance = record.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("source_path") or not provenance.get("source_id"):
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} is missing provenance.")
        try:
            status = SupportStatus(str(record.get("support_status")))
        except ValueError as exc:
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
        try:
            trust = TrustLevel(str(record.get("trust_level")))
        except ValueError as exc:
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
        if record.get("manual_bridge") is True and trust != TrustLevel.MANUAL_BRIDGE:
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} is a manual bridge without trust_level manual_bridge.")
        if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
            raise V2ClassMasteryBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 7.")
    return ids


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
