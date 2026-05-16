"""Dry-run result stability audit for v3.1 governance.

The audit compares repeated limited experimental runtime dry-run snapshots and
keeps the result observational only. It does not enable runtime consumption or
production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


DRY_RUN_RESULT_STABILITY_STATUSES = (
    "dry_run_stable",
    "blocked_missing_dry_run_record",
    "blocked_snapshot_count_insufficient",
    "blocked_manifest_identity_drift",
    "blocked_fixture_set_identity_drift",
    "blocked_guard_status_drift",
    "blocked_readiness_status_drift",
    "blocked_authorization_state_drift",
    "blocked_dry_run_status_drift",
)
STABLE_DRY_RUN_RESULT_STABILITY_TOKEN = "v3_1_phase_27_dry_run_result_stability_token"
_DRIFT_FIELD_TO_BLOCKER = {
    "manifest_id": "blocked_manifest_identity_drift",
    "fixture_set_id": "blocked_fixture_set_identity_drift",
    "guard_status": "blocked_guard_status_drift",
    "promotion_readiness_status": "blocked_readiness_status_drift",
    "authorization_state": "blocked_authorization_state_drift",
    "dry_run_status": "blocked_dry_run_status_drift",
}


def audit_dry_run_result_stability(
    dry_run_snapshots: list[dict[str, Any] | list[dict[str, Any]]],
    *,
    run_id: str = "v3_1_phase_27_dry_run_result_stability",
) -> dict[str, Any]:
    """Compare repeated dry-run snapshots and expose deterministic drift records."""

    normalized_snapshots = [_dry_run_records(snapshot) for snapshot in dry_run_snapshots]
    snapshot_count = len(normalized_snapshots)
    keys = sorted(
        {
            key
            for snapshot in normalized_snapshots
            for record in snapshot
            for key in [_comparison_key(record)]
            if key is not None
        },
        key=lambda item: (item[0], item[1], item[2]),
    )
    if not keys:
        keys = [(None, None, None)]

    records = [
        _stability_record(
            key=key,
            snapshots=normalized_snapshots,
            snapshot_count=snapshot_count,
        )
        for key in keys
    ]
    counts = Counter(record["stability_status"] for record in records)
    drift_reasons = Counter(reason for record in records for reason in record["blockers"])
    envelope = {
        "schema_version": "v3_1.dry_run_result_stability.1",
        "run": {
            "run_id": run_id,
            "snapshot_count": snapshot_count,
            "snapshot_record_counts": [len(snapshot) for snapshot in normalized_snapshots],
            "snapshot_hashes": [_source_hash(snapshot) for snapshot in dry_run_snapshots],
        },
        "summary": {
            "records_evaluated": len(records),
            "stable_count": counts["dry_run_stable"],
            "blocked_count": len(records) - counts["dry_run_stable"],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "stability_status_counts": {
            status: counts[status]
            for status in DRY_RUN_RESULT_STABILITY_STATUSES
        },
        "drift_reason_counts": dict(sorted(drift_reasons.items())),
        "compared_snapshot_summary": {
            "compared_snapshot_count": snapshot_count,
            "snapshot_count_sufficient": snapshot_count >= 2,
            "records_per_snapshot": [len(snapshot) for snapshot in normalized_snapshots],
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
        },
        "dry_run_result_stability_records": records,
        "safety_confirmations": {
            "stability_authorizes_production_routing": False,
            "stability_enables_runtime_manifest_consumption": False,
            "stability_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_dry_run_result_stability",
            "observational_only": True,
            "dry_run_governance_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_DRY_RUN_RESULT_STABILITY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _stability_record(
    *,
    key: tuple[str | None, str | None, str | None],
    snapshots: list[list[dict[str, Any]]],
    snapshot_count: int,
) -> dict[str, Any]:
    _, manifest_id, fixture_set_id = key
    matches = [_find_record(snapshot, key) for snapshot in snapshots]
    present = [record for record in matches if record is not None]
    drift_fields = _drift_fields(present)
    blockers: list[str] = []
    if snapshot_count < 2:
        blockers.append("blocked_snapshot_count_insufficient")
    if not present or len(present) != snapshot_count:
        blockers.append("blocked_missing_dry_run_record")
    for field in drift_fields:
        blockers.append(_DRIFT_FIELD_TO_BLOCKER[field])
    blockers = sorted(set(blockers), key=blockers.index)
    status = blockers[0] if blockers else "dry_run_stable"
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "token": STABLE_DRY_RUN_RESULT_STABILITY_TOKEN,
    }
    reference = present[0] if present else {}
    return {
        "dry_run_stability_id": f"v3_1_dry_run_stability_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id or reference.get("manifest_id"),
        "fixture_set_id": fixture_set_id or reference.get("fixture_set_id"),
        "compared_snapshot_count": snapshot_count,
        "stability_status": status,
        "drift_fields": drift_fields,
        "blockers": blockers,
        "field_values": {
            field: _stable_values(present, field)
            for field in _DRIFT_FIELD_TO_BLOCKER
        },
        "stability_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "dry_run_governance_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
            "stability_does_not_authorize_production_routing": True,
        },
    }


def _dry_run_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [
        deepcopy(record)
        for record in value.get("limited_experimental_runtime_dry_run_records", [])
    ]


def _comparison_key(record: dict[str, Any]) -> tuple[str, str, str] | None:
    record_id = record.get("limited_runtime_dry_run_id")
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if record_id is None and manifest_id is None and fixture_set_id is None:
        return None
    if record_id is not None:
        return (str(record_id), "", "")
    return (str(record_id or ""), str(manifest_id or ""), str(fixture_set_id or ""))


def _find_record(snapshot: list[dict[str, Any]], key: tuple[str | None, str | None, str | None]) -> dict[str, Any] | None:
    for record in snapshot:
        if _comparison_key(record) == key:
            return record
    record_id, _, _ = key
    if record_id:
        for record in snapshot:
            if str(record.get("limited_runtime_dry_run_id") or "") == record_id:
                return record
    return None


def _drift_fields(records: list[dict[str, Any]]) -> list[str]:
    drifted: list[str] = []
    if len(records) < 2:
        return drifted
    for field in _DRIFT_FIELD_TO_BLOCKER:
        if len({record.get(field) for record in records}) > 1:
            drifted.append(field)
    return drifted


def _stable_values(records: list[dict[str, Any]], field: str) -> list[Any]:
    return [record.get(field) for record in records]


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
