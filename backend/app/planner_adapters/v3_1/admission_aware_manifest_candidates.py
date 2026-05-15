"""Admission-aware approval manifest candidate refresh.

This layer refreshes manifest candidates from admission-aware readiness records.
It is governance-only and never makes candidates production-authoritative.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


ADMISSION_AWARE_MANIFEST_CANDIDATE_STATUSES = (
    "candidate_ready",
    "excluded_not_ready",
    "excluded_missing_admission_readiness",
    "excluded_invalid_readiness_state",
)
VALID_ADMISSION_AWARE_READINESS_STATES = frozenset(
    {
        "ready_for_approval_review",
        "blocked_missing_inputs",
        "blocked_policy_failure",
        "blocked_malformed_inputs",
        "blocked_duplicate_inputs",
        "blocked_insufficient_review",
        "blocked_missing_admission_aware_policy",
        "blocked_invalid_admission_policy_state",
    }
)
STABLE_ADMISSION_AWARE_MANIFEST_TOKEN = "v3_1_phase_14_admission_aware_manifest_candidates_token"


def build_admission_aware_manifest_candidates(
    *,
    admission_aware_readiness_gate: dict[str, Any],
    approval_manifest_candidates: dict[str, Any] | None = None,
    run_id: str = "v3_1_phase_14_admission_aware_manifest_candidates",
) -> dict[str, Any]:
    """Build deterministic refreshed manifest candidate records."""

    original_by_set = {
        str(row.get("fixture_set_id") or ""): deepcopy(row)
        for row in (approval_manifest_candidates or {}).get("manifest_candidates", [])
    }
    records = [
        _candidate_record(readiness_record=row, original_candidate=original_by_set.get(str(row.get("fixture_set_id") or "")))
        for row in sorted(
            admission_aware_readiness_gate.get("admission_aware_readiness_records", []),
            key=lambda item: str(item.get("fixture_set_id") or ""),
        )
    ]
    if not records and original_by_set:
        records = [
            _missing_readiness_record(original_candidate=row)
            for row in sorted(original_by_set.values(), key=lambda item: str(item.get("fixture_set_id") or ""))
        ]
    counts = Counter(row["candidate_status"] for row in records)
    exclusion_reasons = Counter(reason for row in records if row["candidate_status"] != "candidate_ready" for reason in row["reason_codes"])
    refresh = Counter(row["candidate_refresh_status"] for row in records)
    comparison = Counter(row["original_vs_admission_aware"] for row in records)
    envelope = {
        "schema_version": "v3_1.admission_aware_manifest_candidates.1",
        "run": {
            "run_id": run_id,
            "admission_aware_readiness_record_count": len(admission_aware_readiness_gate.get("admission_aware_readiness_records", [])),
            "original_candidate_record_count": len(original_by_set),
            "admission_aware_readiness_hash": admission_aware_readiness_gate.get("deterministic_hash"),
            "original_candidate_hash": (approval_manifest_candidates or {}).get("deterministic_hash"),
        },
        "summary": {
            "admission_aware_readiness_records_evaluated": len(records),
            "candidate_ready_count": counts["candidate_ready"],
            "excluded_count": len(records) - counts["candidate_ready"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "candidate_status_counts": {
            status: counts[status]
            for status in ADMISSION_AWARE_MANIFEST_CANDIDATE_STATUSES
        },
        "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        "candidate_refresh_summary": dict(sorted(refresh.items())),
        "original_vs_admission_aware_comparison": dict(sorted(comparison.items())),
        "manifest_candidates": records,
        "candidate_ready_manifest": [record for record in records if record["candidate_status"] == "candidate_ready"],
        "input_consumption": {
            "admission_aware_readiness_hash": admission_aware_readiness_gate.get("deterministic_hash"),
            "admission_aware_readiness_schema": admission_aware_readiness_gate.get("schema_version"),
            "original_candidate_hash": (approval_manifest_candidates or {}).get("deterministic_hash"),
            "original_candidate_schema": (approval_manifest_candidates or {}).get("schema_version"),
        },
        "safety_confirmations": {
            "candidate_ready_is_production_approval": False,
            "admission_aware_candidates_authorize_production_routing": False,
            "admission_aware_candidates_are_production_authoritative": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_admission_aware_manifest_candidates",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_ADMISSION_AWARE_MANIFEST_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _candidate_record(readiness_record: dict[str, Any], original_candidate: dict[str, Any] | None) -> dict[str, Any]:
    status, reasons = _candidate_status(readiness_record)
    fixture_set_id = str(readiness_record.get("fixture_set_id") or "")
    seed = {
        "fixture_set_id": fixture_set_id,
        "admission_aware_readiness_id": readiness_record.get("admission_aware_readiness_id"),
        "token": STABLE_ADMISSION_AWARE_MANIFEST_TOKEN,
    }
    original_status = (original_candidate or {}).get("candidate_status")
    return {
        "manifest_candidate_id": f"v3_1_admission_manifest_candidate_{deterministic_hash(seed)[:16]}",
        "fixture_set_id": readiness_record.get("fixture_set_id"),
        "candidate_status": status,
        "original_candidate_status": original_status,
        "candidate_refresh_status": _refresh_status(status=status, original_status=original_status),
        "original_vs_admission_aware": _comparison_status(status=status, original_status=original_status),
        "readiness_reclassification": readiness_record.get("readiness_reclassification"),
        "source_summary": {
            "set_key": readiness_record.get("set_key"),
            "associated_fixture_ids": list(readiness_record.get("associated_fixture_ids") or []),
        },
        "policy_summary": {
            "admission_aware_policy_status": readiness_record.get("admission_aware_policy_status"),
            "valid_policy_state": readiness_record.get("admission_aware_policy_status") == "policy_satisfied_for_review",
        },
        "readiness_summary": {
            "original_readiness_status": readiness_record.get("original_readiness_status"),
            "admission_aware_readiness_status": readiness_record.get("final_admission_aware_readiness_status")
            or readiness_record.get("admission_aware_readiness_status"),
            "remaining_blockers": list(readiness_record.get("remaining_blockers") or []),
            "original_block_reason_codes": list(readiness_record.get("original_block_reason_codes") or []),
        },
        "authorization_status": _non_production_authorization(),
        "non_production_authoritative": True,
        "reason_codes": reasons,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_readiness_record(original_candidate: dict[str, Any]) -> dict[str, Any]:
    fixture_set_id = str(original_candidate.get("fixture_set_id") or "")
    seed = {
        "fixture_set_id": fixture_set_id,
        "missing_admission_readiness": True,
        "token": STABLE_ADMISSION_AWARE_MANIFEST_TOKEN,
    }
    original_status = original_candidate.get("candidate_status")
    return {
        "manifest_candidate_id": f"v3_1_admission_manifest_candidate_{deterministic_hash(seed)[:16]}",
        "fixture_set_id": original_candidate.get("fixture_set_id"),
        "candidate_status": "excluded_missing_admission_readiness",
        "original_candidate_status": original_status,
        "candidate_refresh_status": "missing_admission_aware_readiness",
        "original_vs_admission_aware": "excluded_by_missing_admission_readiness",
        "readiness_reclassification": None,
        "source_summary": deepcopy(original_candidate.get("source_summary") or {}),
        "policy_summary": deepcopy(original_candidate.get("policy_summary") or {}),
        "readiness_summary": deepcopy(original_candidate.get("readiness_summary") or {}),
        "authorization_status": _non_production_authorization(),
        "non_production_authoritative": True,
        "reason_codes": ["missing_admission_aware_readiness_record"],
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _candidate_status(readiness_record: dict[str, Any]) -> tuple[str, list[str]]:
    readiness = readiness_record.get("final_admission_aware_readiness_status") or readiness_record.get("admission_aware_readiness_status")
    if not readiness:
        return "excluded_missing_admission_readiness", ["missing_admission_aware_readiness_status"]
    if readiness not in VALID_ADMISSION_AWARE_READINESS_STATES:
        return "excluded_invalid_readiness_state", [f"invalid_admission_aware_readiness_state_{readiness}"]
    if readiness != "ready_for_approval_review":
        return "excluded_not_ready", list(readiness_record.get("remaining_blockers") or [f"readiness_{readiness}"])
    return "candidate_ready", ["admission_aware_ready_for_approval_review"]


def _refresh_status(*, status: str, original_status: Any) -> str:
    if status == "candidate_ready" and original_status == "candidate_ready":
        return "remained_candidate_ready"
    if status == "candidate_ready":
        return "promoted_to_candidate_ready_for_review"
    if original_status == "candidate_ready":
        return "demoted_from_candidate_ready"
    return "remained_excluded"


def _comparison_status(*, status: str, original_status: Any) -> str:
    if original_status is None:
        return "new_admission_aware_candidate"
    if status == original_status:
        return "unchanged"
    return f"{original_status}_to_{status}"


def _non_production_authorization() -> dict[str, Any]:
    return {
        "candidate_is_production_approved": False,
        "candidate_authorizes_production_routing": False,
        "candidate_is_production_authoritative": False,
        "legacy_planner_ownership_preserved": True,
        "trusted_default_routing": False,
    }
