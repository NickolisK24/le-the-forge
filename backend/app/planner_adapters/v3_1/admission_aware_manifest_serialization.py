"""Admission-aware manifest serialization for v3.1 governance.

This module serializes admission-aware candidate-ready records into
non-production-authoritative manifests. It does not approve fixture sets or
authorize production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


ADMISSION_AWARE_SERIALIZED_MANIFEST_STATUSES = (
    "serialized_manifest",
    "excluded_not_ready",
    "excluded_missing_candidate_status",
    "excluded_invalid_candidate_state",
)
STABLE_ADMISSION_AWARE_SERIALIZATION_TOKEN = "v3_1_phase_15_admission_aware_manifest_serialization_token"


def serialize_admission_aware_manifest_candidates(
    *,
    admission_aware_manifest_candidates: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_15_admission_aware_manifest_serialization",
) -> dict[str, Any]:
    """Serialize admission-aware candidate-ready records in deterministic order."""

    candidates = _candidate_records(admission_aware_manifest_candidates)
    records = [_serialization_record(candidate) for candidate in sorted(candidates, key=_candidate_sort_key)]
    counts = Counter(row["serialization_status"] for row in records)
    exclusion_reasons = Counter(
        reason
        for row in records
        if row["serialization_status"] != "serialized_manifest"
        for reason in row["reason_codes"]
    )
    serialized = [row for row in records if row["serialization_status"] == "serialized_manifest"]
    excluded = [row for row in records if row["serialization_status"] != "serialized_manifest"]
    source_hash = admission_aware_manifest_candidates.get("deterministic_hash") if isinstance(admission_aware_manifest_candidates, dict) else None
    source_schema = admission_aware_manifest_candidates.get("schema_version") if isinstance(admission_aware_manifest_candidates, dict) else None
    comparison = Counter(row["candidate_summary"].get("original_vs_admission_aware") for row in serialized)
    envelope = {
        "schema_version": "v3_1.admission_aware_manifest_serialization.1",
        "run": {
            "run_id": run_id,
            "candidate_record_count": len(records),
            "source_candidate_hash": source_hash,
        },
        "summary": {
            "admission_aware_candidates_evaluated": len(records),
            "serialized_manifest_count": len(serialized),
            "excluded_count": len(excluded),
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "serialization_status_counts": {
            status: counts[status]
            for status in ADMISSION_AWARE_SERIALIZED_MANIFEST_STATUSES
        },
        "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        "original_vs_admission_aware_comparison": dict(sorted(comparison.items())),
        "serialized_manifests": serialized,
        "excluded_candidates": excluded,
        "input_consumption": {
            "admission_aware_manifest_candidate_hash": source_hash,
            "admission_aware_manifest_candidate_schema": source_schema,
        },
        "safety_confirmations": {
            "serialized_manifests_are_production_approval": False,
            "admission_aware_manifests_authorize_production_routing": False,
            "admission_aware_manifests_are_production_authoritative": False,
            "all_manifests_non_production_authoritative": all(
                row.get("authorization_status", {}).get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
                and row.get("non_production_authoritative") is True
                for row in serialized
            ),
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_admission_aware_manifest_serialization",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_ADMISSION_AWARE_SERIALIZATION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _candidate_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("manifest_candidates", [])]


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[str, str]:
    return (
        str(candidate.get("fixture_set_id") or ""),
        str(candidate.get("manifest_candidate_id") or ""),
    )


def _serialization_record(candidate: dict[str, Any]) -> dict[str, Any]:
    status, reason_codes = _serialization_status(candidate)
    if status != "serialized_manifest":
        return {
            "manifest_candidate_id": candidate.get("manifest_candidate_id"),
            "fixture_set_id": candidate.get("fixture_set_id"),
            "serialization_status": status,
            "candidate_summary": _candidate_summary(candidate),
            "authorization_status": _authorization_status(),
            "reason_codes": reason_codes,
            "production_output_affected": False,
            "metadata": {
                "observational_only": True,
                "production_consumer": False,
                "planner_remap_performed": False,
            },
        }

    fixture_set_id = str(candidate.get("fixture_set_id") or "")
    candidate_id = str(candidate.get("manifest_candidate_id") or "")
    manifest_id = f"v3_1_admission_manifest_{deterministic_hash({'fixture_set_id': fixture_set_id, 'candidate_id': candidate_id, 'token': STABLE_ADMISSION_AWARE_SERIALIZATION_TOKEN})[:16]}"
    manifest = {
        "manifest_id": manifest_id,
        "manifest_candidate_id": candidate.get("manifest_candidate_id"),
        "fixture_set_id": candidate.get("fixture_set_id"),
        "serialization_status": status,
        "source_summary": deepcopy(candidate.get("source_summary") or {}),
        "policy_summary": deepcopy(candidate.get("policy_summary") or {}),
        "readiness_summary": deepcopy(candidate.get("readiness_summary") or {}),
        "candidate_summary": _candidate_summary(candidate),
        "authorization_status": _authorization_status(),
        "non_production_authoritative": True,
        "reason_codes": reason_codes,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_ADMISSION_AWARE_SERIALIZATION_TOKEN,
        },
    }
    manifest["generated_hash"] = deterministic_hash({"admission_aware_serialized_manifest": manifest})
    return manifest


def _serialization_status(candidate: dict[str, Any]) -> tuple[str, list[str]]:
    status = candidate.get("candidate_status")
    if not status:
        return "excluded_missing_candidate_status", ["missing_candidate_status"]
    if status == "candidate_ready":
        return "serialized_manifest", ["admission_aware_candidate_ready_serialized_non_authoritative_manifest"]
    if status in {"excluded_not_ready", "excluded_missing_admission_readiness", "excluded_invalid_readiness_state"}:
        return "excluded_not_ready", list(candidate.get("reason_codes") or [f"candidate_status_{status}"])
    return "excluded_invalid_candidate_state", [f"invalid_candidate_state_{status}"]


def _candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_status": candidate.get("candidate_status"),
        "original_candidate_status": candidate.get("original_candidate_status"),
        "candidate_refresh_status": candidate.get("candidate_refresh_status"),
        "original_vs_admission_aware": candidate.get("original_vs_admission_aware"),
        "readiness_reclassification": candidate.get("readiness_reclassification"),
        "candidate_is_non_production_authoritative": bool(candidate.get("non_production_authoritative", True)),
    }


def _authorization_status() -> dict[str, Any]:
    return {
        "authorization_state": NON_PRODUCTION_AUTHORIZATION_STATE,
        "manifest_authorizes_production_routing": False,
        "manifest_is_production_approved": False,
        "manifest_is_production_authoritative": False,
        "legacy_planner_ownership_preserved": True,
        "trusted_default_routing": False,
    }
