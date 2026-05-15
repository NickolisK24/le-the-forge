"""Deterministic approval manifest serialization.

Serialized approval manifests are governance artifacts derived from Phase 8
manifest candidates. They are explicitly non-authoritative for production
routing and do not replace legacy planner ownership.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


SERIALIZED_APPROVAL_MANIFEST_STATUSES = (
    "serialized_manifest",
    "excluded_not_ready",
    "excluded_missing_readiness",
    "excluded_invalid_policy_state",
)
STABLE_APPROVAL_MANIFEST_SERIALIZATION_TOKEN = "v3_1_phase_9_approval_manifest_serialization_token"
NON_PRODUCTION_AUTHORIZATION_STATE = "non_production_authoritative"


def serialize_approval_manifest_candidates(
    *,
    approval_manifest_candidates: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_9_approval_manifest_serialization",
) -> dict[str, Any]:
    """Serialize candidate-ready approval manifests in a deterministic envelope."""

    candidates = _candidate_records(approval_manifest_candidates)
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
    source_hash = approval_manifest_candidates.get("deterministic_hash") if isinstance(approval_manifest_candidates, dict) else None
    source_schema = approval_manifest_candidates.get("schema_version") if isinstance(approval_manifest_candidates, dict) else None

    envelope = {
        "schema_version": "v3_1.approval_manifest_serialization.1",
        "run": {
            "run_id": run_id,
            "candidate_record_count": len(records),
            "source_candidate_hash": source_hash,
        },
        "summary": {
            "total_candidates_evaluated": len(records),
            "serialized_manifest_count": len(serialized),
            "excluded_count": len(excluded),
            "production_affected_count": sum(1 for row in records if row["production_output_affected"]),
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "production_default_routing_authorized": False,
            "deterministic": True,
        },
        "serialization_status_counts": {
            status: counts[status]
            for status in SERIALIZED_APPROVAL_MANIFEST_STATUSES
        },
        "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        "serialized_manifests": serialized,
        "excluded_candidates": excluded,
        "input_consumption": {
            "approval_manifest_candidate_hash": source_hash,
            "approval_manifest_candidate_schema": source_schema,
        },
        "safety_confirmations": {
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "legacy_planner_ownership_preserved": True,
            "runtime_state_mutated": False,
            "serialized_manifests_authorize_production_routing": False,
            "serialized_manifests_are_production_approved": False,
            "all_manifests_non_production_authoritative": all(
                row.get("authorization_status", {}).get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
                for row in serialized
            ),
        },
        "metadata": {
            "source": "v3_1_approval_manifest_serialization",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_APPROVAL_MANIFEST_SERIALIZATION_TOKEN,
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
    fixture_set_id = str(candidate.get("fixture_set_id") or "")
    candidate_id = str(candidate.get("manifest_candidate_id") or "")
    manifest_id = f"v3_1_approval_manifest_{deterministic_hash({'fixture_set_id': fixture_set_id, 'candidate_id': candidate_id, 'token': STABLE_APPROVAL_MANIFEST_SERIALIZATION_TOKEN})[:16]}"

    if status != "serialized_manifest":
        return {
            "manifest_candidate_id": candidate.get("manifest_candidate_id"),
            "fixture_set_id": candidate.get("fixture_set_id"),
            "serialization_status": status,
            "reason_codes": reason_codes,
            "authorization_status": _authorization_status(),
            "production_output_affected": False,
            "metadata": {
                "observational_only": True,
                "production_consumer": False,
                "planner_remap_performed": False,
            },
        }

    manifest = {
        "manifest_id": manifest_id,
        "manifest_candidate_id": candidate.get("manifest_candidate_id"),
        "fixture_set_id": candidate.get("fixture_set_id"),
        "serialization_status": status,
        "source_summary": deepcopy(candidate.get("source_summary") or {}),
        "policy_summary": deepcopy(candidate.get("policy_summary") or {}),
        "readiness_summary": deepcopy(candidate.get("readiness_summary") or {}),
        "authorization_status": _authorization_status(),
        "non_production_authoritative": True,
        "reason_codes": reason_codes,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_APPROVAL_MANIFEST_SERIALIZATION_TOKEN,
        },
    }
    manifest["generated_hash"] = deterministic_hash({"serialized_manifest": manifest})
    return manifest


def _serialization_status(candidate: dict[str, Any]) -> tuple[str, list[str]]:
    status = candidate.get("candidate_status")
    if not status:
        return "excluded_missing_readiness", ["missing_candidate_status"]
    if status == "excluded_missing_readiness":
        return "excluded_missing_readiness", list(candidate.get("reason_codes") or ["missing_readiness_classification"])
    if status == "excluded_invalid_policy_state":
        return "excluded_invalid_policy_state", list(candidate.get("reason_codes") or ["invalid_policy_state"])
    if status != "candidate_ready":
        return "excluded_not_ready", list(candidate.get("reason_codes") or [f"candidate_status_{status}"])
    policy = (candidate.get("policy_summary") or {}).get("policy_outcome")
    if policy != "passes_policy":
        return "excluded_invalid_policy_state", [f"invalid_policy_state_{policy or 'missing'}"]
    return "serialized_manifest", ["candidate_ready_serialized_non_authoritative_manifest"]


def _authorization_status() -> dict[str, Any]:
    return {
        "authorization_state": NON_PRODUCTION_AUTHORIZATION_STATE,
        "manifest_authorizes_production_routing": False,
        "manifest_is_production_approved": False,
        "legacy_planner_ownership_preserved": True,
        "trusted_default_routing": False,
    }
