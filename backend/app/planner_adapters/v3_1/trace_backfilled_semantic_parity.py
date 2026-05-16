"""Trace-backfilled semantic parity refresh for v3.1 governance.

This layer refreshes controlled-consumption semantic parity using deterministic
baseline trace backfill records. It only confirms parity when trace-backed
expectations match validated controlled output evidence.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


TRACE_BACKFILLED_SEMANTIC_PARITY_STATUSES = (
    "semantic_parity_confirmed",
    "semantic_parity_partial",
    "blocked_missing_semantic_parity_record",
    "blocked_missing_backfilled_expectation",
    "blocked_trace_conflict",
    "blocked_invalid_authorization_state",
    "blocked_missing_controlled_output",
)
STABLE_TRACE_BACKFILLED_SEMANTIC_PARITY_TOKEN = "v3_1_phase_23_trace_backfilled_semantic_parity_token"


def build_trace_backfilled_semantic_parity(
    *,
    controlled_consumption_semantic_parity: dict[str, Any] | list[dict[str, Any]],
    baseline_trace_expectation_backfill: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_23_trace_backfilled_semantic_parity",
) -> dict[str, Any]:
    """Refresh semantic parity using backfilled trace expectations."""

    semantic_records = _semantic_records(controlled_consumption_semantic_parity)
    backfill_records = _backfill_records(baseline_trace_expectation_backfill)
    validation_records = _validation_records(controlled_consumption_output_validation)
    backfill_by_baseline = {
        str(record.get("baseline_id")): record
        for record in backfill_records
        if record.get("baseline_id")
    }
    validation_by_key = {_trace_key(record): record for record in validation_records if _trace_key(record)}
    refreshed_records = [
        _refresh_record(
            semantic_record=record,
            backfill_record=backfill_by_baseline.get(str(record.get("baseline_id") or "")),
            validation_record=validation_by_key.get(_trace_key(record)),
        )
        for record in sorted(semantic_records, key=_semantic_sort_key)
    ]
    if not refreshed_records:
        refreshed_records = [_missing_semantic_parity_record()]

    counts = Counter(record["final_semantic_parity_status"] for record in refreshed_records)
    blocker_reasons = Counter(reason for record in refreshed_records for reason in record["blockers"])
    remaining_unavailable = Counter(field for record in refreshed_records for field in record["remaining_unavailable_fields"])
    mismatches = Counter(field for record in refreshed_records for field in record["mismatched_fields"])
    semantic_hash = controlled_consumption_semantic_parity.get("deterministic_hash") if isinstance(controlled_consumption_semantic_parity, dict) else None
    backfill_hash = baseline_trace_expectation_backfill.get("deterministic_hash") if isinstance(baseline_trace_expectation_backfill, dict) else None
    validation_hash = controlled_consumption_output_validation.get("deterministic_hash") if isinstance(controlled_consumption_output_validation, dict) else None
    envelope = {
        "schema_version": "v3_1.trace_backfilled_semantic_parity.1",
        "run": {
            "run_id": run_id,
            "semantic_parity_record_count": len(semantic_records),
            "trace_backfill_record_count": len(backfill_records),
            "validated_output_record_count": len(validation_records),
            "controlled_consumption_semantic_parity_hash": semantic_hash,
            "baseline_trace_expectation_backfill_hash": backfill_hash,
            "controlled_consumption_output_validation_hash": validation_hash,
        },
        "summary": {
            "records_evaluated": len(refreshed_records),
            "semantic_parity_confirmed_count": counts["semantic_parity_confirmed"],
            "semantic_parity_partial_count": counts["semantic_parity_partial"],
            "blocked_count": len(refreshed_records) - counts["semantic_parity_confirmed"] - counts["semantic_parity_partial"],
            "promoted_from_partial_count": sum(1 for record in refreshed_records if record["promoted_from_partial"] is True),
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "trace_backfilled_semantic_parity_status_counts": {
            status: counts[status]
            for status in TRACE_BACKFILLED_SEMANTIC_PARITY_STATUSES
        },
        "remaining_unavailable_field_counts": dict(sorted(remaining_unavailable.items())),
        "mismatched_field_counts": dict(sorted(mismatches.items())),
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "trace_backfilled_semantic_parity_records": refreshed_records,
        "safety_confirmations": {
            "semantic_parity_authorizes_production_routing": False,
            "semantic_parity_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_trace_backfilled_semantic_parity",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_TRACE_BACKFILLED_SEMANTIC_PARITY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _semantic_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("semantic_parity_records", [])]


def _backfill_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("baseline_trace_backfill_records", [])]


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _refresh_record(
    *,
    semantic_record: dict[str, Any],
    backfill_record: dict[str, Any] | None,
    validation_record: dict[str, Any] | None,
) -> dict[str, Any]:
    compared_fields, mismatched_fields = _compare_trace_fields(
        backfill_record=backfill_record,
        validation_record=validation_record,
    )
    blockers = _blockers(
        semantic_record=semantic_record,
        backfill_record=backfill_record,
        validation_record=validation_record,
        mismatched_fields=mismatched_fields,
    )
    if backfill_record is not None:
        remaining_unavailable = list(backfill_record.get("remaining_unavailable_fields") or [])
    else:
        remaining_unavailable = list(semantic_record.get("unavailable_fields") or [])
    status = _status(
        blockers=blockers,
        backfill_record=backfill_record,
        remaining_unavailable=remaining_unavailable,
        original_status=semantic_record.get("semantic_parity_status"),
    )
    seed = {
        "semantic_parity_record_id": semantic_record.get("semantic_parity_record_id"),
        "baseline_id": semantic_record.get("baseline_id"),
        "manifest_id": semantic_record.get("manifest_id"),
        "fixture_set_id": semantic_record.get("fixture_set_id"),
        "status": status,
        "token": STABLE_TRACE_BACKFILLED_SEMANTIC_PARITY_TOKEN,
    }
    original_status = semantic_record.get("semantic_parity_status")
    return {
        "trace_backfilled_semantic_parity_id": f"v3_1_trace_backfilled_semantic_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": semantic_record.get("manifest_id"),
        "fixture_set_id": semantic_record.get("fixture_set_id"),
        "baseline_id": semantic_record.get("baseline_id"),
        "original_semantic_parity_status": original_status,
        "backfill_status": (backfill_record or {}).get("trace_backfill_status"),
        "final_semantic_parity_status": status,
        "compared_trace_fields": compared_fields,
        "remaining_unavailable_fields": remaining_unavailable,
        "mismatched_fields": mismatched_fields,
        "blockers": blockers,
        "promoted_from_partial": original_status == "semantic_parity_partial" and status == "semantic_parity_confirmed",
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_semantic_parity_record() -> dict[str, Any]:
    seed = {"missing_semantic_parity": True, "token": STABLE_TRACE_BACKFILLED_SEMANTIC_PARITY_TOKEN}
    return {
        "trace_backfilled_semantic_parity_id": f"v3_1_trace_backfilled_semantic_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "baseline_id": None,
        "original_semantic_parity_status": None,
        "backfill_status": None,
        "final_semantic_parity_status": "blocked_missing_semantic_parity_record",
        "compared_trace_fields": [],
        "remaining_unavailable_fields": [],
        "mismatched_fields": [],
        "blockers": ["blocked_missing_semantic_parity_record"],
        "promoted_from_partial": False,
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _compare_trace_fields(
    *,
    backfill_record: dict[str, Any] | None,
    validation_record: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    if not backfill_record or not validation_record:
        return [], []
    compared: list[dict[str, Any]] = []
    mismatched: list[str] = []
    checks = (
        ("manifest_id", (backfill_record.get("backfilled_manifest_trace_fields") or {}).get("manifest_id"), validation_record.get("manifest_id")),
        ("fixture_set_id", (backfill_record.get("backfilled_fixture_trace_fields") or {}).get("fixture_set_id"), validation_record.get("fixture_set_id")),
    )
    for field, expected, actual in checks:
        if expected is None:
            continue
        matches = expected == actual
        compared.append({"field": field, "expected": expected, "actual": actual, "matches": matches})
        if not matches:
            mismatched.append(field)
    return compared, mismatched


def _blockers(
    *,
    semantic_record: dict[str, Any],
    backfill_record: dict[str, Any] | None,
    validation_record: dict[str, Any] | None,
    mismatched_fields: list[str],
) -> list[str]:
    blockers: list[str] = []
    if not semantic_record.get("semantic_parity_record_id"):
        blockers.append("blocked_missing_semantic_parity_record")
    if backfill_record is None:
        blockers.append("blocked_missing_backfilled_expectation")
    if validation_record is None:
        blockers.append("blocked_missing_controlled_output")
    if (backfill_record or {}).get("trace_conflicts"):
        blockers.append("blocked_trace_conflict")
    if mismatched_fields:
        blockers.append("blocked_trace_conflict")
    if _authorization_state(validation_record) != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    return sorted(set(blockers), key=blockers.index)


def _status(
    *,
    blockers: list[str],
    backfill_record: dict[str, Any] | None,
    remaining_unavailable: list[str],
    original_status: str | None,
) -> str:
    if blockers:
        return blockers[0]
    if original_status == "semantic_parity_confirmed":
        return "semantic_parity_confirmed"
    if (backfill_record or {}).get("trace_backfill_status") == "trace_expectations_backfilled" and not remaining_unavailable:
        return "semantic_parity_confirmed"
    return "semantic_parity_partial"


def _authorization_state(record: dict[str, Any] | None) -> str | None:
    if not record:
        return None
    return (record.get("traceability_summary") or {}).get("authorization_state")


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _semantic_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
        str(record.get("baseline_id") or ""),
    )
