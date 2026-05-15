"""Manifest consumption eligibility gate for v3.1 governance.

Eligibility here means a non-production-authoritative manifest is structurally
eligible for future controlled test consumption only. It never authorizes
runtime routing or production planner ownership changes.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


MANIFEST_CONSUMPTION_ELIGIBILITY_STATUSES = (
    "eligible_for_controlled_test_consumption",
    "blocked_missing_manifest",
    "blocked_invalid_authorization_state",
    "blocked_missing_identity",
    "blocked_missing_hash",
    "blocked_missing_source_summary",
    "blocked_missing_policy_summary",
    "blocked_missing_readiness_summary",
    "blocked_missing_candidate_summary",
    "blocked_unstable_manifest_hash",
)
STABLE_MANIFEST_CONSUMPTION_ELIGIBILITY_TOKEN = "v3_1_phase_16_manifest_consumption_eligibility_token"


def evaluate_manifest_consumption_eligibility(
    *,
    admission_aware_manifest_serialization: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_16_manifest_consumption_eligibility",
) -> dict[str, Any]:
    """Evaluate manifests for controlled-test-consumption eligibility."""

    manifests = _manifest_records(admission_aware_manifest_serialization)
    records = [_eligibility_record(manifest) for manifest in sorted(manifests, key=_manifest_sort_key)]
    if not records:
        records = [_missing_manifest_record()]
    counts = Counter(row["eligibility_status"] for row in records)
    blocker_reasons = Counter(reason for row in records for reason in row["blockers"])
    source_hash = admission_aware_manifest_serialization.get("deterministic_hash") if isinstance(admission_aware_manifest_serialization, dict) else None
    source_schema = admission_aware_manifest_serialization.get("schema_version") if isinstance(admission_aware_manifest_serialization, dict) else None
    envelope = {
        "schema_version": "v3_1.manifest_consumption_eligibility.1",
        "run": {
            "run_id": run_id,
            "manifest_count": len(manifests),
            "source_serialization_hash": source_hash,
            "source_serialization_schema": source_schema,
        },
        "summary": {
            "manifests_evaluated": len(records),
            "eligible_count": counts["eligible_for_controlled_test_consumption"],
            "blocked_count": len(records) - counts["eligible_for_controlled_test_consumption"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "manifest_runtime_consumption_enabled": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "eligibility_status_counts": {
            status: counts[status]
            for status in MANIFEST_CONSUMPTION_ELIGIBILITY_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "eligibility_summary": {
            "eligible_for_controlled_test_consumption_only": counts["eligible_for_controlled_test_consumption"],
            "blocked_from_controlled_test_consumption": len(records) - counts["eligible_for_controlled_test_consumption"],
            "production_routing_authorized": False,
            "runtime_consumption_enabled": False,
        },
        "eligibility_records": records,
        "safety_confirmations": {
            "eligibility_authorizes_production_routing": False,
            "eligibility_enables_runtime_consumption": False,
            "eligible_manifests_are_production_approved": False,
            "eligible_manifests_are_production_authoritative": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_manifest_consumption_eligibility",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "controlled_test_consumption_only": True,
            "stable_generation_token": STABLE_MANIFEST_CONSUMPTION_ELIGIBILITY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _manifest_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("serialized_manifests", [])]


def _manifest_sort_key(manifest: dict[str, Any]) -> tuple[str, str]:
    return (
        str(manifest.get("fixture_set_id") or ""),
        str(manifest.get("manifest_id") or ""),
    )


def _eligibility_record(manifest: dict[str, Any]) -> dict[str, Any]:
    audit = _required_field_audit(manifest)
    blockers = _blockers(manifest=manifest, audit=audit)
    status = blockers[0] if blockers else "eligible_for_controlled_test_consumption"
    manifest_id = manifest.get("manifest_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": manifest.get("fixture_set_id"),
        "status": status,
        "token": STABLE_MANIFEST_CONSUMPTION_ELIGIBILITY_TOKEN,
    }
    return {
        "eligibility_record_id": f"v3_1_manifest_eligibility_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": manifest.get("fixture_set_id"),
        "authorization_state": (manifest.get("authorization_status") or {}).get("authorization_state"),
        "eligibility_status": status,
        "blockers": blockers,
        "required_field_audit": audit,
        "generated_hash": manifest.get("generated_hash"),
        "controlled_test_consumption_only": True,
        "eligibility_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_manifest_record() -> dict[str, Any]:
    seed = {
        "missing_manifest": True,
        "token": STABLE_MANIFEST_CONSUMPTION_ELIGIBILITY_TOKEN,
    }
    return {
        "eligibility_record_id": f"v3_1_manifest_eligibility_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "authorization_state": None,
        "eligibility_status": "blocked_missing_manifest",
        "blockers": ["blocked_missing_manifest"],
        "required_field_audit": {
            "manifest_present": False,
            "identity_present": False,
            "generated_hash_present": False,
            "generated_hash_stable": False,
            "source_summary_present": False,
            "policy_summary_present": False,
            "readiness_summary_present": False,
            "candidate_summary_present": False,
            "non_production_authoritative": False,
        },
        "generated_hash": None,
        "controlled_test_consumption_only": True,
        "eligibility_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(*, manifest: dict[str, Any], audit: dict[str, bool]) -> list[str]:
    ordered_checks = [
        ("blocked_invalid_authorization_state", not audit["non_production_authoritative"]),
        ("blocked_missing_identity", not audit["identity_present"]),
        ("blocked_missing_hash", not audit["generated_hash_present"]),
        ("blocked_missing_source_summary", not audit["source_summary_present"]),
        ("blocked_missing_policy_summary", not audit["policy_summary_present"]),
        ("blocked_missing_readiness_summary", not audit["readiness_summary_present"]),
        ("blocked_missing_candidate_summary", not audit["candidate_summary_present"]),
        ("blocked_unstable_manifest_hash", audit["generated_hash_present"] and not audit["generated_hash_stable"]),
    ]
    return [reason for reason, blocked in ordered_checks if blocked]


def _required_field_audit(manifest: dict[str, Any]) -> dict[str, bool]:
    return {
        "manifest_present": True,
        "identity_present": bool(manifest.get("manifest_id") and manifest.get("fixture_set_id")),
        "generated_hash_present": bool(manifest.get("generated_hash")),
        "generated_hash_stable": _generated_hash_is_stable(manifest),
        "source_summary_present": bool(manifest.get("source_summary")),
        "policy_summary_present": bool(manifest.get("policy_summary")),
        "readiness_summary_present": bool(manifest.get("readiness_summary")),
        "candidate_summary_present": bool(manifest.get("candidate_summary")),
        "non_production_authoritative": _is_non_production_authoritative(manifest),
    }


def _is_non_production_authoritative(manifest: dict[str, Any]) -> bool:
    authorization = manifest.get("authorization_status") or {}
    return (
        manifest.get("non_production_authoritative") is True
        and authorization.get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
        and authorization.get("manifest_authorizes_production_routing") is False
        and authorization.get("manifest_is_production_approved") is False
        and authorization.get("manifest_is_production_authoritative") is False
    )


def _generated_hash_is_stable(manifest: dict[str, Any]) -> bool:
    current_hash = manifest.get("generated_hash")
    if not current_hash:
        return False
    payload = deepcopy(manifest)
    payload.pop("generated_hash", None)
    expected = deterministic_hash({"admission_aware_serialized_manifest": payload})
    return current_hash == expected
