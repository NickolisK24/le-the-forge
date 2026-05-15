"""Admission-aware readiness gate re-evaluation for v3.1 governance.

This module re-evaluates readiness records after source admission and
admission-aware policy evaluation. It remains observational and never approves
production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


ADMISSION_AWARE_READINESS_STATUSES = (
    "ready_for_approval_review",
    "blocked_missing_inputs",
    "blocked_policy_failure",
    "blocked_malformed_inputs",
    "blocked_duplicate_inputs",
    "blocked_insufficient_review",
    "blocked_missing_admission_aware_policy",
    "blocked_invalid_admission_policy_state",
)
STABLE_ADMISSION_AWARE_READINESS_TOKEN = "v3_1_phase_13_admission_aware_readiness_gate_token"
VALID_ADMISSION_POLICY_STATES = frozenset(
    {
        "policy_satisfied_for_review",
        "blocked_source_not_admitted",
        "blocked_policy_failure",
        "blocked_missing_admission_record",
        "blocked_missing_fixture_input",
        "blocked_invalid_review_state",
    }
)


def build_admission_aware_readiness_gate(
    *,
    fixture_set_readiness_gate: dict[str, Any],
    admission_aware_policy_evaluation: dict[str, Any],
    reviewed_fixture_inputs: dict[str, Any],
    persisted_fixture_sets: dict[str, Any],
    run_id: str = "v3_1_phase_13_admission_aware_readiness_gate",
) -> dict[str, Any]:
    """Build deterministic admission-aware readiness records."""

    policy_by_set = {
        str(row.get("fixture_set_id") or ""): deepcopy(row)
        for row in admission_aware_policy_evaluation.get("admission_aware_policy_records", [])
    }
    fixture_set_by_id = {
        str(row.get("fixture_set_id") or ""): deepcopy(row)
        for row in persisted_fixture_sets.get("fixture_sets", [])
    }
    input_by_id = _reviewed_inputs_by_id(reviewed_fixture_inputs.get("normalized_fixture_inputs", []))
    records = [
        _admission_aware_record(
            readiness_record=row,
            admission_policy=policy_by_set.get(str(row.get("fixture_set_id") or "")),
            fixture_set=fixture_set_by_id.get(str(row.get("fixture_set_id") or "")),
            input_by_id=input_by_id,
        )
        for row in sorted(fixture_set_readiness_gate.get("readiness_records", []), key=lambda item: str(item.get("fixture_set_id") or ""))
    ]
    counts = Counter(row["admission_aware_readiness_status"] for row in records)
    blocker_reasons = Counter(reason for row in records for reason in row["remaining_blockers"])
    reclassification = Counter(row["readiness_reclassification"] for row in records)
    envelope = {
        "schema_version": "v3_1.admission_aware_readiness_gate.1",
        "run": {
            "run_id": run_id,
            "record_count": len(records),
            "fixture_set_readiness_gate_hash": fixture_set_readiness_gate.get("deterministic_hash"),
            "admission_aware_policy_evaluation_hash": admission_aware_policy_evaluation.get("deterministic_hash"),
            "reviewed_fixture_inputs_hash": reviewed_fixture_inputs.get("deterministic_hash"),
            "persisted_fixture_sets_hash": persisted_fixture_sets.get("deterministic_hash"),
        },
        "summary": {
            "records_evaluated": len(records),
            "ready_for_approval_review_count": counts["ready_for_approval_review"],
            "blocked_count": len(records) - counts["ready_for_approval_review"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "admission_aware_readiness_counts": {
            status: counts[status]
            for status in ADMISSION_AWARE_READINESS_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "readiness_reclassification_summary": dict(sorted(reclassification.items())),
        "remaining_blocker_summary": [
            {"reason": reason, "count": count}
            for reason, count in sorted(blocker_reasons.items(), key=lambda item: (-item[1], item[0]))
        ],
        "admission_aware_readiness_records": records,
        "safety_confirmations": {
            "ready_for_approval_review_is_production_approval": False,
            "admission_aware_readiness_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
            "remaining_blockers_hidden": False,
        },
        "metadata": {
            "source": "v3_1_admission_aware_readiness_gate",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_ADMISSION_AWARE_READINESS_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _admission_aware_record(
    *,
    readiness_record: dict[str, Any],
    admission_policy: dict[str, Any] | None,
    fixture_set: dict[str, Any] | None,
    input_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    original_status = readiness_record.get("readiness_classification")
    original_blockers = list(readiness_record.get("block_reason_codes") or [])
    admission_policy_status = admission_policy.get("admission_aware_policy_status") if admission_policy else None
    fixture_set_id = readiness_record.get("fixture_set_id")
    final_status, remaining_blockers, reclassification = _final_status(
        readiness_record=readiness_record,
        admission_policy=admission_policy,
        fixture_set=fixture_set,
        input_by_id=input_by_id,
        original_blockers=original_blockers,
    )
    seed = {
        "fixture_set_id": fixture_set_id,
        "original_status": original_status,
        "admission_policy_status": admission_policy_status,
        "final_status": final_status,
        "token": STABLE_ADMISSION_AWARE_READINESS_TOKEN,
    }
    return {
        "admission_aware_readiness_id": f"v3_1_admission_readiness_{deterministic_hash(seed)[:16]}",
        "fixture_set_id": fixture_set_id,
        "set_key": readiness_record.get("set_key") or (fixture_set or {}).get("set_key"),
        "original_readiness_status": original_status,
        "original_block_reason_codes": original_blockers,
        "admission_aware_policy_status": admission_policy_status,
        "final_admission_aware_readiness_status": final_status,
        "admission_aware_readiness_status": final_status,
        "remaining_blockers": remaining_blockers,
        "readiness_reclassification": reclassification,
        "associated_fixture_ids": list(readiness_record.get("associated_fixture_ids") or (fixture_set or {}).get("associated_fixture_ids") or []),
        "non_production_authorization": {
            "ready_for_approval_review_is_production_approval": False,
            "readiness_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "trusted_default_routing": False,
        },
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _final_status(
    *,
    readiness_record: dict[str, Any],
    admission_policy: dict[str, Any] | None,
    fixture_set: dict[str, Any] | None,
    input_by_id: dict[str, dict[str, Any]],
    original_blockers: list[str],
) -> tuple[str, list[str], str]:
    non_policy_status = _explicit_non_policy_status(readiness_record.get("readiness_classification"))
    if non_policy_status:
        return non_policy_status, original_blockers or [non_policy_status], "non_policy_readiness_blocker_preserved"

    input_status = _input_status_blocker(readiness_record=readiness_record, fixture_set=fixture_set, input_by_id=input_by_id)
    if input_status:
        return input_status[0], input_status[1], "non_policy_input_blocker_preserved"

    if admission_policy is None:
        return "blocked_missing_admission_aware_policy", ["missing_admission_aware_policy_record"], "missing_admission_aware_policy"

    admission_status = admission_policy.get("admission_aware_policy_status")
    if admission_status not in VALID_ADMISSION_POLICY_STATES:
        return "blocked_invalid_admission_policy_state", [f"invalid_admission_policy_state_{admission_status or 'missing'}"], "invalid_admission_policy_state"
    if admission_status != "policy_satisfied_for_review":
        blockers = list(admission_policy.get("remaining_blockers") or [f"admission_policy_{admission_status}"])
        return "blocked_policy_failure", blockers, "admission_policy_blocker_preserved"

    remaining_non_policy = [reason for reason in original_blockers if not str(reason).startswith("policy_")]
    if remaining_non_policy:
        return _status_from_reason(remaining_non_policy[0]), sorted(set(remaining_non_policy)), "non_policy_readiness_blocker_preserved"

    if readiness_record.get("readiness_classification") == "ready_for_approval_review":
        return "ready_for_approval_review", [], "already_ready"
    return "ready_for_approval_review", [], "policy_blocker_cleared_by_admission_aware_policy"


def _explicit_non_policy_status(status: Any) -> str | None:
    if status in {
        "blocked_missing_inputs",
        "blocked_malformed_inputs",
        "blocked_duplicate_inputs",
        "blocked_insufficient_review",
    }:
        return str(status)
    return None


def _input_status_blocker(
    *,
    readiness_record: dict[str, Any],
    fixture_set: dict[str, Any] | None,
    input_by_id: dict[str, dict[str, Any]],
) -> tuple[str, list[str]] | None:
    fixture_ids = list(readiness_record.get("associated_fixture_ids") or (fixture_set or {}).get("associated_fixture_ids") or [])
    if not fixture_ids:
        return "blocked_missing_inputs", ["missing_fixture_set_membership"]
    statuses = Counter()
    for fixture_id in fixture_ids:
        row = input_by_id.get(_normalize_id(str(fixture_id)))
        if row is None:
            statuses["missing_source"] += 1
        else:
            statuses[str(row.get("status") or "missing_source")] += 1
    if statuses["missing_source"]:
        return "blocked_missing_inputs", ["missing_reviewed_fixture_input"]
    if statuses["malformed"]:
        return "blocked_malformed_inputs", ["malformed_reviewed_fixture_input"]
    if statuses["duplicate"]:
        return "blocked_duplicate_inputs", ["duplicate_reviewed_fixture_input"]
    return None


def _status_from_reason(reason: str) -> str:
    if "missing" in reason:
        return "blocked_missing_inputs"
    if "malformed" in reason:
        return "blocked_malformed_inputs"
    if "duplicate" in reason:
        return "blocked_duplicate_inputs"
    if "policy" in reason:
        return "blocked_policy_failure"
    return "blocked_insufficient_review"


def _reviewed_inputs_by_id(inputs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in sorted(inputs, key=lambda item: str(item.get("normalized_fixture_id") or "")):
        normalized_id = _normalize_id(str(row.get("normalized_fixture_id") or ""))
        source_fixture_id = _normalize_id(str(row.get("source_fixture_id") or ""))
        if normalized_id:
            result[normalized_id] = deepcopy(row)
        if source_fixture_id:
            result[source_fixture_id] = deepcopy(row)
    return result


def _normalize_id(value: str) -> str:
    return "_".join(value.strip().lower().replace("\\", "/").replace(":", "_").split())
