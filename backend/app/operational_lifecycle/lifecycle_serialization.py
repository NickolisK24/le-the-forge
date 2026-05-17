"""Deterministic serialization helpers for v4.0 patch lifecycle foundations.

Serialization is evidence serialization only. It does not omit unsupported,
prohibited, unknown, or warning states, and it does not correct lifecycle
records.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .lifecycle_models import (
    LifecycleLineageRecord,
    LifecycleProvenanceRecord,
    LifecycleState,
    LifecycleVisibilityRecord,
    PatchIdentity,
    PatchLifecycleFoundation,
    PatchOperationalMetadata,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_for_lifecycle_serialization(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_for_lifecycle_serialization(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_for_lifecycle_serialization(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, (tuple, list)):
        return [canonicalize_for_lifecycle_serialization(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_for_lifecycle_serialization(payload),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def export_patch_identity(identity: PatchIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_lifecycle_state(state: LifecycleState) -> dict[str, Any]:
    return asdict(state)


def export_lifecycle_provenance_record(record: LifecycleProvenanceRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("continuity_references", "source_evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lifecycle_lineage_record(record: LifecycleLineageRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in (
        "prior_bundle_references",
        "successor_references",
        "continuity_references",
        "rollback_references",
        "provenance_continuity_references",
        "trusted_bundle_references",
        "refresh_chain_references",
        "fail_visible_lineage_gap_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lifecycle_visibility_record(record: LifecycleVisibilityRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in (
        "fail_visible_findings",
        "unsupported_state_visibility",
        "prohibited_state_visibility",
        "unknown_state_visibility",
        "integrity_warning_visibility",
        "lifecycle_continuity_visibility",
        "lineage_gap_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_patch_operational_metadata(metadata: PatchOperationalMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in ("lifecycle_state_references", "visibility_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_patch_lifecycle_foundation(foundation: PatchLifecycleFoundation) -> dict[str, Any]:
    data = asdict(foundation)
    data["patch_identity"] = export_patch_identity(foundation.patch_identity)
    data["lifecycle_states"] = [
        export_lifecycle_state(state)
        for state in sorted(foundation.lifecycle_states, key=lambda item: (item.deterministic_order, item.state_id))
    ]
    data["provenance_records"] = [
        export_lifecycle_provenance_record(record)
        for record in sorted(foundation.provenance_records, key=lambda item: item.provenance_reference_id)
    ]
    data["lineage_records"] = [
        export_lifecycle_lineage_record(record)
        for record in sorted(foundation.lineage_records, key=lambda item: (item.deterministic_order, item.lineage_reference_id))
    ]
    data["visibility_records"] = [
        export_lifecycle_visibility_record(record)
        for record in sorted(
            foundation.visibility_records,
            key=lambda item: (item.deterministic_order, item.visibility_reference_id),
        )
    ]
    data["operational_metadata"] = export_patch_operational_metadata(foundation.operational_metadata)
    return data


def serialize_patch_identity(identity: PatchIdentity) -> str:
    return stable_serialize(export_patch_identity(identity))


def serialize_lifecycle_state(state: LifecycleState) -> str:
    return stable_serialize(export_lifecycle_state(state))


def serialize_lifecycle_lineage_record(record: LifecycleLineageRecord) -> str:
    return stable_serialize(export_lifecycle_lineage_record(record))


def serialize_lifecycle_visibility_record(record: LifecycleVisibilityRecord) -> str:
    return stable_serialize(export_lifecycle_visibility_record(record))


def serialize_lifecycle_provenance_record(record: LifecycleProvenanceRecord) -> str:
    return stable_serialize(export_lifecycle_provenance_record(record))


def serialize_patch_lifecycle_foundation(foundation: PatchLifecycleFoundation) -> str:
    return stable_serialize(export_patch_lifecycle_foundation(foundation))
