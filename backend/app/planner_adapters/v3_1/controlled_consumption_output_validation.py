"""Controlled consumption output validation for v3.1 governance.

Validation is test-only/governance-only. It verifies controlled-test output
traceability and production isolation without authorizing production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


CONTROLLED_CONSUMPTION_OUTPUT_VALIDATION_STATUSES = (
    "valid_controlled_test_output",
    "blocked_missing_consumption_record",
    "blocked_missing_manifest_trace",
    "blocked_missing_fixture_set_trace",
    "blocked_invalid_authorization_state",
    "blocked_runtime_consumption_enabled",
    "blocked_invalid_consumption_status",
)
STABLE_CONTROLLED_OUTPUT_VALIDATION_TOKEN = "v3_1_phase_18_controlled_consumption_output_validation_token"


def validate_controlled_consumption_output(
    *,
    controlled_test_consumption: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_18_controlled_consumption_output_validation",
) -> dict[str, Any]:
    """Validate controlled-test consumption records deterministically."""

    records = _consumption_records(controlled_test_consumption)
    runtime_enabled = _runtime_consumption_enabled(controlled_test_consumption)
    validation_records = [
        _validation_record(record=record, runtime_enabled=runtime_enabled)
        for record in sorted(records, key=_consumption_sort_key)
    ]
    if not validation_records:
        validation_records = [_missing_record(runtime_enabled=runtime_enabled)]
    counts = Counter(row["validation_status"] for row in validation_records)
    blocker_reasons = Counter(reason for row in validation_records for reason in row["blockers"])
    traceability = {
        "manifest_trace_count": sum(1 for row in validation_records if row["traceability_summary"]["manifest_trace_present"]),
        "fixture_set_trace_count": sum(1 for row in validation_records if row["traceability_summary"]["fixture_set_trace_present"]),
        "authorization_trace_count": sum(1 for row in validation_records if row["traceability_summary"]["authorization_state"] == NON_PRODUCTION_AUTHORIZATION_STATE),
    }
    source_hash = controlled_test_consumption.get("deterministic_hash") if isinstance(controlled_test_consumption, dict) else None
    source_schema = controlled_test_consumption.get("schema_version") if isinstance(controlled_test_consumption, dict) else None
    envelope = {
        "schema_version": "v3_1.controlled_consumption_output_validation.1",
        "run": {
            "run_id": run_id,
            "controlled_consumption_record_count": len(records),
            "controlled_test_consumption_hash": source_hash,
            "controlled_test_consumption_schema": source_schema,
        },
        "summary": {
            "records_evaluated": len(validation_records),
            "valid_count": counts["valid_controlled_test_output"],
            "blocked_count": len(validation_records) - counts["valid_controlled_test_output"],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "validation_status_counts": {
            status: counts[status]
            for status in CONTROLLED_CONSUMPTION_OUTPUT_VALIDATION_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "traceability_summary": traceability,
        "validation_records": validation_records,
        "safety_confirmations": {
            "validation_authorizes_production_routing": False,
            "validation_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_controlled_consumption_output_validation",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_CONTROLLED_OUTPUT_VALIDATION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _consumption_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("controlled_consumption_records", [])]


def _runtime_consumption_enabled(value: dict[str, Any] | list[dict[str, Any]]) -> bool:
    if not isinstance(value, dict):
        return False
    summary = value.get("summary") or {}
    safety = value.get("safety_confirmations") or {}
    return bool(summary.get("runtime_manifest_consumption_enabled") or summary.get("runtime_production_consumption_enabled") or safety.get("runtime_manifest_consumption_enabled") or safety.get("runtime_production_consumption_enabled"))


def _consumption_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
    )


def _validation_record(*, record: dict[str, Any], runtime_enabled: bool) -> dict[str, Any]:
    blockers = _blockers(record=record, runtime_enabled=runtime_enabled)
    status = blockers[0] if blockers else "valid_controlled_test_output"
    seed = {
        "manifest_id": record.get("manifest_id"),
        "fixture_set_id": record.get("fixture_set_id"),
        "status": status,
        "token": STABLE_CONTROLLED_OUTPUT_VALIDATION_TOKEN,
    }
    return {
        "validation_record_id": f"v3_1_controlled_output_validation_{deterministic_hash(seed)[:16]}",
        "manifest_id": record.get("manifest_id"),
        "fixture_set_id": record.get("fixture_set_id"),
        "controlled_consumption_status": record.get("controlled_consumption_status"),
        "validation_status": status,
        "blockers": blockers,
        "traceability_summary": _traceability_summary(record=record, runtime_enabled=runtime_enabled),
        "validation_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_record(*, runtime_enabled: bool) -> dict[str, Any]:
    seed = {"missing_consumption_record": True, "token": STABLE_CONTROLLED_OUTPUT_VALIDATION_TOKEN}
    blockers = ["blocked_missing_consumption_record"]
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    return {
        "validation_record_id": f"v3_1_controlled_output_validation_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "controlled_consumption_status": None,
        "validation_status": blockers[0],
        "blockers": blockers,
        "traceability_summary": {
            "manifest_trace_present": False,
            "fixture_set_trace_present": False,
            "authorization_state": None,
            "runtime_consumption_enabled": runtime_enabled,
            "not_production_consumption": False,
        },
        "validation_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(*, record: dict[str, Any], runtime_enabled: bool) -> list[str]:
    blockers: list[str] = []
    if not record.get("manifest_id"):
        blockers.append("blocked_missing_manifest_trace")
    if not record.get("fixture_set_id"):
        blockers.append("blocked_missing_fixture_set_trace")
    if record.get("authorization_state") != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if record.get("controlled_consumption_status") != "consumed_in_controlled_test":
        blockers.append("blocked_invalid_consumption_status")
    if record.get("controlled_consumption_authorizes_production_routing") is not False or record.get("not_production_consumption") is not True:
        blockers.append("blocked_invalid_authorization_state")
    return sorted(set(blockers), key=blockers.index)


def _traceability_summary(*, record: dict[str, Any], runtime_enabled: bool) -> dict[str, Any]:
    return {
        "manifest_trace_present": bool(record.get("manifest_id")),
        "fixture_set_trace_present": bool(record.get("fixture_set_id")),
        "authorization_state": record.get("authorization_state"),
        "runtime_consumption_enabled": runtime_enabled,
        "not_production_consumption": record.get("not_production_consumption") is True,
    }
