"""Read-only v2 canonical affix repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id
from app.data_contracts.validation import is_stable_calculable


class V2AffixBundleError(ValueError):
    """Raised when the v2 affix bundle is missing or invalid."""


class V2AffixRepository:
    """Read-only repository over the generated v2 canonical affix bundle."""

    def __init__(self, bundle_path: str | Path) -> None:
        self.bundle_path = Path(bundle_path)
        self._payload: dict[str, Any] | None = None
        self._records: tuple[dict[str, Any], ...] = ()
        self._by_id: dict[str, dict[str, Any]] = {}

    def load(self) -> "V2AffixRepository":
        if not self.bundle_path.exists():
            raise FileNotFoundError(f"v2 affix bundle not found: {self.bundle_path}")
        try:
            payload = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise V2AffixBundleError(f"Invalid JSON in v2 affix bundle {self.bundle_path}: {exc}") from exc
        self.load_payload(payload)
        return self

    def load_payload(self, payload: dict[str, Any]) -> "V2AffixRepository":
        if not isinstance(payload, dict):
            raise V2AffixBundleError("v2 affix bundle must be a JSON object.")
        records = payload.get("records")
        if not isinstance(records, dict):
            raise V2AffixBundleError("v2 affix bundle records must be an object.")
        affixes = records.get("affixes")
        if not isinstance(affixes, list):
            raise V2AffixBundleError("v2 affix bundle records.affixes must be a list.")
        if not affixes:
            raise V2AffixBundleError("v2 affix bundle records.affixes must not be empty.")
        self._validate_records(affixes)
        self._payload = deepcopy(payload)
        self._records = tuple(deepcopy(record) for record in affixes)
        self._by_id = {record["canonical_id"]: record for record in self._records}
        return self

    def list_affixes(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in self._records[start:end]]

    def get_affix(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_affixes(
        self,
        *,
        query: str = "",
        slot: str = "",
        item_type: str = "",
        class_id: str = "",
        support_status: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._records)
        if query:
            needle = query.strip().lower()
            records = [
                record for record in records
                if needle in record["canonical_id"].lower()
                or needle in str(record.get("display_name", "")).lower()
                or needle in str(record.get("source_id", "")).lower()
            ]
        if slot:
            expected = slot.strip().lower()
            records = [
                record for record in records
                if expected in {str(value).lower() for value in record.get("slot_restrictions") or []}
            ]
        if item_type:
            expected = item_type.strip().lower()
            records = [
                record for record in records
                if expected in {str(value).lower() for value in record.get("item_type_restrictions") or []}
            ]
        if class_id:
            expected = class_id.strip().lower()
            records = [
                record for record in records
                if expected in {str(value).lower() for value in record.get("class_restrictions") or []}
            ]
        if support_status:
            expected = support_status.strip().lower()
            records = [
                record for record in records
                if str(record.get("support_status", "")).lower() == expected
            ]
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in records[start:end]]

    def count(self) -> int:
        return len(self._records)

    def debug_summary(self) -> dict[str, Any]:
        payload_summary = self._payload.get("summary", {}) if self._payload else {}
        status_counts: dict[str, int] = {}
        domain_counts: dict[str, int] = {}
        modifier_counts: dict[str, int] = {}
        for record in self._records:
            status = str(record.get("support_status", "unknown"))
            domain = str(record.get("affix_domain", "unknown"))
            modifier_count = str(len(record.get("modifier_references") or []))
            status_counts[status] = status_counts.get(status, 0) + 1
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            modifier_counts[modifier_count] = modifier_counts.get(modifier_count, 0) + 1
        return {
            "source_path": str(self.bundle_path),
            "affix_count": self.count(),
            "summary": deepcopy(payload_summary),
            "support_status_counts": status_counts,
            "affix_domain_counts": domain_counts,
            "modifier_reference_count_distribution": modifier_counts,
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate_records(records: list[Any]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise V2AffixBundleError(f"Affix record {index} must be an object.")
            canonical_id = record.get("canonical_id")
            try:
                validate_canonical_id(canonical_id)
            except ValueError as exc:
                raise V2AffixBundleError(f"Affix record {index} has invalid canonical_id: {exc}") from exc
            if canonical_id in seen:
                raise V2AffixBundleError(f"Duplicate canonical_id in v2 affix bundle: {canonical_id}")
            seen.add(canonical_id)
            if not record.get("display_name"):
                raise V2AffixBundleError(f"Affix record {canonical_id} is missing display_name.")
            provenance = record.get("provenance")
            if not isinstance(provenance, dict) or not provenance.get("source_path"):
                raise V2AffixBundleError(f"Affix record {canonical_id} is missing provenance.source_path.")
            try:
                status = SupportStatus(str(record.get("support_status")))
            except ValueError as exc:
                raise V2AffixBundleError(f"Affix record {canonical_id} has invalid support_status.") from exc
            try:
                trust_level = TrustLevel(str(record.get("trust_level")))
            except ValueError as exc:
                raise V2AffixBundleError(f"Affix record {canonical_id} has invalid trust_level.") from exc
            if trust_level in {TrustLevel.GAME_EXTRACTED, TrustLevel.GENERATED_FROM_GAME_DATA}:
                if not provenance.get("source_id") and not record.get("source_id"):
                    raise V2AffixBundleError(f"Affix record {canonical_id} is missing source reference.")
            tier_ranges = record.get("tier_ranges")
            if status in {SupportStatus.TRUSTED, SupportStatus.PARTIAL}:
                if not isinstance(tier_ranges, list) or not tier_ranges:
                    raise V2AffixBundleError(f"Affix record {canonical_id} is missing tier_ranges.")
            if not isinstance(record.get("slot_restrictions"), list):
                raise V2AffixBundleError(f"Affix record {canonical_id} has invalid slot_restrictions.")
            if not isinstance(record.get("item_type_restrictions"), list):
                raise V2AffixBundleError(f"Affix record {canonical_id} has invalid item_type_restrictions.")
            if record.get("affix_domain") not in {"equipment", "idol", "unknown"}:
                raise V2AffixBundleError(f"Affix record {canonical_id} has invalid affix_domain.")
            if record.get("affix_domain") == "equipment" and record.get("source_type") == "idol":
                raise V2AffixBundleError(f"Affix record {canonical_id} mixes equipment and idol domains.")
            if is_stable_calculable(status, trust_level) and record.get("stable_calculable") is not True:
                raise V2AffixBundleError(f"Affix record {canonical_id} has inconsistent stable_calculable flag.")
            if record.get("stable_calculable") is True and status != SupportStatus.TRUSTED:
                raise V2AffixBundleError(f"Affix record {canonical_id} is stable_calculable without trusted status.")
