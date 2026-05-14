"""Read-only v2 unique and set item repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2UniqueSetBundleError(ValueError):
    """Raised when v2 unique/set bundles are missing or invalid."""


class V2UniqueSetRepository:
    """Read-only repository over generated v2 unique and set bundles."""

    def __init__(self, unique_bundle_path: str | Path, set_bundle_path: str | Path) -> None:
        self.unique_bundle_path = Path(unique_bundle_path)
        self.set_bundle_path = Path(set_bundle_path)
        self._unique_payload: dict[str, Any] | None = None
        self._set_payload: dict[str, Any] | None = None
        self._uniques: tuple[dict[str, Any], ...] = ()
        self._sets: tuple[dict[str, Any], ...] = ()
        self._set_items: tuple[dict[str, Any], ...] = ()
        self._set_bonuses: tuple[dict[str, Any], ...] = ()
        self._uniques_by_id: dict[str, dict[str, Any]] = {}
        self._sets_by_id: dict[str, dict[str, Any]] = {}
        self._set_items_by_group: dict[str, tuple[dict[str, Any], ...]] = {}
        self._set_bonuses_by_group: dict[str, tuple[dict[str, Any], ...]] = {}

    def load(self) -> "V2UniqueSetRepository":
        return self.load_payloads(
            _read_json(self.unique_bundle_path, "v2 unique bundle"),
            _read_json(self.set_bundle_path, "v2 set bundle"),
        )

    def load_payloads(self, unique_payload: dict[str, Any], set_payload: dict[str, Any]) -> "V2UniqueSetRepository":
        uniques = _records(unique_payload, "uniques", "v2 unique bundle")
        sets = _records(set_payload, "sets", "v2 set bundle")
        set_items = _records(set_payload, "set_items", "v2 set bundle")
        set_bonuses = _records(set_payload, "set_bonuses", "v2 set bundle")
        self._validate_uniques(uniques)
        self._validate_sets(sets, set_items, set_bonuses)
        self._unique_payload = deepcopy(unique_payload)
        self._set_payload = deepcopy(set_payload)
        self._uniques = tuple(deepcopy(record) for record in uniques)
        self._sets = tuple(deepcopy(record) for record in sets)
        self._set_items = tuple(deepcopy(record) for record in set_items)
        self._set_bonuses = tuple(deepcopy(record) for record in set_bonuses)
        self._uniques_by_id = {record["canonical_id"]: record for record in self._uniques}
        self._sets_by_id = {record["canonical_id"]: record for record in self._sets}
        self._set_items_by_group = _group_by(self._set_items, "set_group_id")
        self._set_bonuses_by_group = _group_by(self._set_bonuses, "set_group_id")
        return self

    def list_uniques(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._uniques, limit=limit, offset=offset)

    def get_unique(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._uniques_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_uniques(
        self,
        *,
        query: str = "",
        slot: str = "",
        item_type: str = "",
        class_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return _filter_item_like(self._uniques, query=query, slot=slot, item_type=item_type, class_id=class_id, limit=limit, offset=offset)

    def list_sets(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._sets, limit=limit, offset=offset)

    def get_set(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._sets_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def get_set_items(self, set_group_id: str) -> list[dict[str, Any]]:
        return [deepcopy(record) for record in self._set_items_by_group.get(set_group_id, ())]

    def get_set_bonuses(self, set_group_id: str) -> list[dict[str, Any]]:
        return [deepcopy(record) for record in self._set_bonuses_by_group.get(set_group_id, ())]

    def filter_set_items(
        self,
        *,
        query: str = "",
        slot: str = "",
        item_type: str = "",
        class_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return _filter_item_like(self._set_items, query=query, slot=slot, item_type=item_type, class_id=class_id, limit=limit, offset=offset)

    def count_uniques(self) -> int:
        return len(self._uniques)

    def count_sets(self) -> int:
        return len(self._sets)

    def count_set_items(self) -> int:
        return len(self._set_items)

    def count_set_bonuses(self) -> int:
        return len(self._set_bonuses)

    def debug_summary(self) -> dict[str, Any]:
        unique_summary = self._unique_payload.get("summary", {}) if self._unique_payload else {}
        set_summary = self._set_payload.get("summary", {}) if self._set_payload else {}
        return {
            "unique_bundle_path": str(self.unique_bundle_path),
            "set_bundle_path": str(self.set_bundle_path),
            "unique_count": self.count_uniques(),
            "set_group_count": self.count_sets(),
            "set_item_count": self.count_set_items(),
            "set_bonus_count": self.count_set_bonuses(),
            "unique_summary": deepcopy(unique_summary),
            "set_summary": deepcopy(set_summary),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate_uniques(records: list[Any]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            _validate_common(record, index, "Unique")
            canonical_id = record["canonical_id"]
            if canonical_id in seen:
                raise V2UniqueSetBundleError(f"Duplicate canonical_id in v2 unique bundle: {canonical_id}")
            seen.add(canonical_id)
            _validate_modifier_rows(record, "Unique")
            _validate_classification(record, "Unique")

    @staticmethod
    def _validate_sets(sets: list[Any], set_items: list[Any], set_bonuses: list[Any]) -> None:
        set_ids: set[str] = set()
        seen_items: set[str] = set()
        seen_bonuses: set[str] = set()
        for index, record in enumerate(sets):
            _validate_common(record, index, "Set")
            canonical_id = record["canonical_id"]
            if canonical_id in set_ids:
                raise V2UniqueSetBundleError(f"Duplicate canonical_id in v2 set bundle: {canonical_id}")
            if record.get("set_group_id") != canonical_id:
                raise V2UniqueSetBundleError(f"Set {canonical_id} has conflicting set_group_id.")
            set_ids.add(canonical_id)
        for index, record in enumerate(set_items):
            _validate_common(record, index, "Set item")
            canonical_id = record["canonical_id"]
            if canonical_id in seen_items:
                raise V2UniqueSetBundleError(f"Duplicate canonical_id in v2 set item bundle: {canonical_id}")
            seen_items.add(canonical_id)
            if record.get("set_group_id") not in set_ids:
                raise V2UniqueSetBundleError(f"Set item {canonical_id} references missing set group: {record.get('set_group_id')}")
            _validate_modifier_rows(record, "Set item")
            _validate_classification(record, "Set item")
        for index, record in enumerate(set_bonuses):
            _validate_common(record, index, "Set bonus")
            canonical_id = record["canonical_id"]
            if canonical_id in seen_bonuses:
                raise V2UniqueSetBundleError(f"Duplicate canonical_id in v2 set bonus bundle: {canonical_id}")
            seen_bonuses.add(canonical_id)
            if record.get("set_group_id") not in set_ids:
                raise V2UniqueSetBundleError(f"Set bonus {canonical_id} references missing set group: {record.get('set_group_id')}")
            _validate_modifier_rows(record, "Set bonus")
            _validate_classification(record, "Set bonus")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2UniqueSetBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2UniqueSetBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str, label: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict):
        raise V2UniqueSetBundleError(f"{label} records must be an object.")
    values = records.get(key)
    if not isinstance(values, list):
        raise V2UniqueSetBundleError(f"{label} records.{key} must be a list.")
    return values


def _validate_common(record: Any, index: int, label: str) -> None:
    if not isinstance(record, dict):
        raise V2UniqueSetBundleError(f"{label} record {index} must be an object.")
    canonical_id = record.get("canonical_id")
    try:
        validate_canonical_id(canonical_id)
    except ValueError as exc:
        raise V2UniqueSetBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
    if not record.get("display_name"):
        raise V2UniqueSetBundleError(f"{label} {canonical_id} is missing display_name.")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("source_path"):
        raise V2UniqueSetBundleError(f"{label} {canonical_id} is missing provenance.source_path.")
    try:
        status = SupportStatus(str(record.get("support_status")))
    except ValueError as exc:
        raise V2UniqueSetBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
    try:
        trust_level = TrustLevel(str(record.get("trust_level")))
    except ValueError as exc:
        raise V2UniqueSetBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
    if trust_level in {TrustLevel.GAME_EXTRACTED, TrustLevel.GENERATED_FROM_GAME_DATA}:
        if not provenance.get("source_id") and not record.get("source_id"):
            raise V2UniqueSetBundleError(f"{label} {canonical_id} is missing source reference.")
    if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
        raise V2UniqueSetBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 5.")


def _validate_modifier_rows(record: dict[str, Any], label: str) -> None:
    for modifier in record.get("modifier_rows") or []:
        if not isinstance(modifier, dict) or not modifier.get("provenance"):
            raise V2UniqueSetBundleError(f"{label} {record['canonical_id']} has modifier row without provenance.")
        if not modifier.get("support_status"):
            raise V2UniqueSetBundleError(f"{label} {record['canonical_id']} has modifier row without support_status.")
        if modifier.get("stable_calculable") is True:
            raise V2UniqueSetBundleError(f"{label} {record['canonical_id']} has stable-calculable modifier row.")


def _validate_classification(record: dict[str, Any], label: str) -> None:
    if record.get("special_mechanic_classification") not in {
        "trusted_modifier",
        "partial_modifier",
        "text_only_effect",
        "scripted_runtime_behavior",
        "unsupported_special_behavior",
        "unknown",
    }:
        raise V2UniqueSetBundleError(f"{label} {record['canonical_id']} has invalid special mechanic classification.")


def _filter_item_like(
    records: tuple[dict[str, Any], ...],
    *,
    query: str,
    slot: str,
    item_type: str,
    class_id: str,
    limit: int | None,
    offset: int,
) -> list[dict[str, Any]]:
    filtered = list(records)
    if query:
        needle = query.strip().lower()
        filtered = [
            record for record in filtered
            if needle in record["canonical_id"].lower()
            or needle in str(record.get("display_name", "")).lower()
            or needle in str(record.get("source_id", "")).lower()
        ]
    if slot:
        expected = slot.strip().lower()
        filtered = [record for record in filtered if str(record.get("slot", "")).lower() == expected]
    if item_type:
        expected = item_type.strip().lower()
        filtered = [record for record in filtered if str(record.get("item_type", "")).lower() == expected]
    if class_id:
        expected = class_id.strip().lower()
        filtered = [
            record for record in filtered
            if expected in {str(value).lower() for value in record.get("class_restrictions") or []}
        ]
    return _page(tuple(filtered), limit=limit, offset=offset)


def _group_by(records: tuple[dict[str, Any], ...], key: str) -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record.get(key)), []).append(record)
    return {group: tuple(values) for group, values in grouped.items()}


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
