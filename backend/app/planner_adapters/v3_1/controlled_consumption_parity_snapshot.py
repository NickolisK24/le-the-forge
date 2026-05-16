"""Controlled consumption parity snapshot infrastructure for v3.1 governance.

Parity snapshots compare validated controlled-test consumption output against
planner-adjacent baseline snapshots. They are observational only and cannot
authorize production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


CONTROLLED_CONSUMPTION_PARITY_STATUSES = (
    "parity_confirmed",
    "blocked_missing_validated_output",
    "blocked_missing_baseline_snapshot",
    "blocked_identity_mismatch",
    "blocked_fixture_set_mismatch",
    "blocked_manifest_trace_mismatch",
    "blocked_invalid_authorization_state",
)
STABLE_CONTROLLED_CONSUMPTION_PARITY_TOKEN = "v3_1_phase_19_controlled_consumption_parity_snapshot_token"


def build_controlled_consumption_parity_snapshot(
    *,
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    planner_snapshot_baselines: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_19_controlled_consumption_parity_snapshot",
) -> dict[str, Any]:
    """Build deterministic parity records for controlled-test output."""

    validation_records = _validation_records(controlled_consumption_output_validation)
    baseline_snapshots = _baseline_snapshots(planner_snapshot_baselines)
    selected_baseline = _selected_baseline_snapshot(baseline_snapshots)

    parity_records = [
        _parity_record(record=record, baseline=selected_baseline)
        for record in sorted(validation_records, key=_validation_sort_key)
    ]
    if not parity_records:
        parity_records = [_missing_validated_output_record(baseline=selected_baseline)]

    counts = Counter(record["parity_status"] for record in parity_records)
    blocker_reasons = Counter(reason for record in parity_records for reason in record["blockers"])
    validation_hash = controlled_consumption_output_validation.get("deterministic_hash") if isinstance(controlled_consumption_output_validation, dict) else None
    baseline_hash = planner_snapshot_baselines.get("deterministic_hash") if isinstance(planner_snapshot_baselines, dict) else None
    envelope = {
        "schema_version": "v3_1.controlled_consumption_parity_snapshot.1",
        "run": {
            "run_id": run_id,
            "validated_output_record_count": len(validation_records),
            "planner_snapshot_count": len(baseline_snapshots),
            "controlled_consumption_output_validation_hash": validation_hash,
            "planner_snapshot_baselines_hash": baseline_hash,
        },
        "summary": {
            "records_evaluated": len(parity_records),
            "parity_confirmed_count": counts["parity_confirmed"],
            "blocked_count": len(parity_records) - counts["parity_confirmed"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "parity_status_counts": {
            status: counts[status]
            for status in CONTROLLED_CONSUMPTION_PARITY_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "baseline_comparison_summary": {
            "baseline_snapshots_available": len(baseline_snapshots),
            "baseline_candidate_count": sum(1 for snapshot in baseline_snapshots if snapshot.get("baseline_candidate") is True),
            "comparison_eligible_count": sum(1 for snapshot in baseline_snapshots if snapshot.get("comparison_eligible") is True),
            "selected_baseline_id": selected_baseline.get("snapshot_id") if selected_baseline else None,
            "validated_output_count": len(validation_records),
            "production_routing_authorized": False,
        },
        "parity_records": parity_records,
        "safety_confirmations": {
            "parity_authorizes_production_routing": False,
            "parity_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_controlled_consumption_parity_snapshot",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_CONTROLLED_CONSUMPTION_PARITY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _baseline_snapshots(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("snapshots", [])]


def _selected_baseline_snapshot(snapshots: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [
        snapshot
        for snapshot in snapshots
        if snapshot.get("baseline_candidate") is True
        or snapshot.get("baseline_readiness") == "baseline_candidate"
        or snapshot.get("comparison_eligible") is True
    ]
    if not eligible:
        return None
    return sorted(eligible, key=_baseline_sort_key)[0]


def _baseline_sort_key(snapshot: dict[str, Any]) -> tuple[int, str, str]:
    priority = 0 if snapshot.get("baseline_candidate") is True or snapshot.get("baseline_readiness") == "baseline_candidate" else 1
    return (
        priority,
        str(snapshot.get("stable_key") or ""),
        str(snapshot.get("snapshot_id") or ""),
    )


def _validation_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
        str(record.get("validation_record_id") or ""),
    )


def _parity_record(*, record: dict[str, Any], baseline: dict[str, Any] | None) -> dict[str, Any]:
    blockers = _blockers(record=record, baseline=baseline)
    status = blockers[0] if blockers else "parity_confirmed"
    seed = {
        "validation_record_id": record.get("validation_record_id"),
        "manifest_id": record.get("manifest_id"),
        "fixture_set_id": record.get("fixture_set_id"),
        "baseline_id": baseline.get("snapshot_id") if baseline else None,
        "status": status,
        "token": STABLE_CONTROLLED_CONSUMPTION_PARITY_TOKEN,
    }
    return {
        "parity_record_id": f"v3_1_controlled_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": record.get("manifest_id"),
        "fixture_set_id": record.get("fixture_set_id"),
        "baseline_id": baseline.get("snapshot_id") if baseline else None,
        "parity_status": status,
        "blockers": blockers,
        "comparison_summary": _comparison_summary(record=record, baseline=baseline),
        "parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_validated_output_record(*, baseline: dict[str, Any] | None) -> dict[str, Any]:
    seed = {
        "missing_validated_output": True,
        "baseline_id": baseline.get("snapshot_id") if baseline else None,
        "token": STABLE_CONTROLLED_CONSUMPTION_PARITY_TOKEN,
    }
    blockers = ["blocked_missing_validated_output"]
    if baseline is None:
        blockers.append("blocked_missing_baseline_snapshot")
    return {
        "parity_record_id": f"v3_1_controlled_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "baseline_id": baseline.get("snapshot_id") if baseline else None,
        "parity_status": "blocked_missing_validated_output",
        "blockers": blockers,
        "comparison_summary": {
            "validated_output_present": False,
            "baseline_snapshot_present": baseline is not None,
            "controlled_identity_present": False,
            "fixture_set_trace_present": False,
            "manifest_trace_present": False,
            "authorization_state": None,
            "baseline_candidate_snapshot": bool(baseline and baseline.get("baseline_candidate") is True),
            "production_routing_authorized": False,
        },
        "parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(*, record: dict[str, Any], baseline: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if record.get("validation_status") != "valid_controlled_test_output":
        blockers.append("blocked_missing_validated_output")
    if baseline is None:
        blockers.append("blocked_missing_baseline_snapshot")
    if (record.get("traceability_summary") or {}).get("authorization_state") != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    if not record.get("manifest_id"):
        blockers.append("blocked_manifest_trace_mismatch")
    if not record.get("fixture_set_id"):
        blockers.append("blocked_fixture_set_mismatch")
    if baseline is not None:
        if baseline.get("expected_validation_record_id") and baseline.get("expected_validation_record_id") != record.get("validation_record_id"):
            blockers.append("blocked_identity_mismatch")
        if baseline.get("expected_fixture_set_id") and baseline.get("expected_fixture_set_id") != record.get("fixture_set_id"):
            blockers.append("blocked_fixture_set_mismatch")
        if baseline.get("expected_manifest_id") and baseline.get("expected_manifest_id") != record.get("manifest_id"):
            blockers.append("blocked_manifest_trace_mismatch")
    return sorted(set(blockers), key=blockers.index)


def _comparison_summary(*, record: dict[str, Any], baseline: dict[str, Any] | None) -> dict[str, Any]:
    traceability = record.get("traceability_summary") or {}
    return {
        "validated_output_present": record.get("validation_status") == "valid_controlled_test_output",
        "baseline_snapshot_present": baseline is not None,
        "baseline_expected_identity_present": bool(baseline and (baseline.get("snapshot_id") or baseline.get("stable_key"))),
        "controlled_identity_present": bool(record.get("validation_record_id")),
        "fixture_set_trace_present": bool(record.get("fixture_set_id") and traceability.get("fixture_set_trace_present") is True),
        "manifest_trace_present": bool(record.get("manifest_id") and traceability.get("manifest_trace_present") is True),
        "authorization_state": traceability.get("authorization_state"),
        "baseline_candidate_snapshot": bool(baseline and baseline.get("baseline_candidate") is True),
        "baseline_readiness": baseline.get("baseline_readiness") if baseline else None,
        "baseline_stable_key": baseline.get("stable_key") if baseline else None,
        "production_routing_authorized": False,
    }
