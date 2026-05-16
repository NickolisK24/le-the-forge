"""Limited experimental runtime guard contract for v3.1 governance.

This module defines the guardrail contract for a future limited experimental
runtime path. It does not enable runtime manifest consumption or production
routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


LIMITED_EXPERIMENTAL_RUNTIME_GUARD_STATUSES = (
    "guard_contract_ready",
    "blocked_missing_promotion_readiness",
    "blocked_invalid_manifest_eligibility",
    "blocked_invalid_authorization_state",
    "blocked_runtime_consumption_enabled",
    "blocked_production_routing_authorized",
    "blocked_missing_non_production_manifest",
)
STABLE_LIMITED_RUNTIME_GUARD_TOKEN = "v3_1_phase_25_limited_experimental_runtime_guards_token"


def build_limited_experimental_runtime_guards(
    *,
    controlled_consumption_promotion_readiness: dict[str, Any] | list[dict[str, Any]],
    manifest_consumption_eligibility: dict[str, Any] | list[dict[str, Any]],
    admission_aware_manifest_serialization: dict[str, Any] | list[dict[str, Any]],
    production_non_consumption_assumptions: dict[str, Any] | None = None,
    run_id: str = "v3_1_phase_25_limited_experimental_runtime_guards",
) -> dict[str, Any]:
    """Build deterministic limited experimental runtime guard records."""

    readiness_records = _readiness_records(controlled_consumption_promotion_readiness)
    eligibility_records = _eligibility_records(manifest_consumption_eligibility)
    manifests = _serialized_manifests(admission_aware_manifest_serialization)
    assumptions = production_non_consumption_assumptions or {}
    runtime_enabled = _runtime_enabled(
        controlled_consumption_promotion_readiness,
        manifest_consumption_eligibility,
        admission_aware_manifest_serialization,
        assumptions,
    )
    production_routing_authorized = _production_routing_authorized(
        controlled_consumption_promotion_readiness,
        manifest_consumption_eligibility,
        admission_aware_manifest_serialization,
        assumptions,
    )
    eligibility_by_key = {_trace_key(record): record for record in eligibility_records if _trace_key(record)}
    manifests_by_key = {_trace_key(record): record for record in manifests if _trace_key(record)}
    guard_records = [
        _guard_record(
            readiness=record,
            eligibility=eligibility_by_key.get(_trace_key(record)),
            manifest=manifests_by_key.get(_trace_key(record)),
            runtime_enabled=runtime_enabled,
            production_routing_authorized=production_routing_authorized,
        )
        for record in sorted(readiness_records, key=_record_sort_key)
    ]
    if not guard_records:
        guard_records = [_missing_readiness_record(runtime_enabled=runtime_enabled, production_routing_authorized=production_routing_authorized)]

    counts = Counter(record["guard_contract_status"] for record in guard_records)
    blocker_reasons = Counter(reason for record in guard_records for reason in record["blockers"])
    envelope = {
        "schema_version": "v3_1.limited_experimental_runtime_guards.1",
        "run": {
            "run_id": run_id,
            "promotion_readiness_record_count": len(readiness_records),
            "manifest_eligibility_record_count": len(eligibility_records),
            "serialized_manifest_count": len(manifests),
            "controlled_consumption_promotion_readiness_hash": _source_hash(controlled_consumption_promotion_readiness),
            "manifest_consumption_eligibility_hash": _source_hash(manifest_consumption_eligibility),
            "admission_aware_manifest_serialization_hash": _source_hash(admission_aware_manifest_serialization),
        },
        "summary": {
            "records_evaluated": len(guard_records),
            "guard_contract_ready_count": counts["guard_contract_ready"],
            "blocked_count": len(guard_records) - counts["guard_contract_ready"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "guard_contract_status_counts": {
            status: counts[status]
            for status in LIMITED_EXPERIMENTAL_RUNTIME_GUARD_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "required_guard_conditions": {
            "promotion_readiness_required": "ready_for_limited_experimental_runtime_consideration",
            "manifest_eligibility_required": "eligible_for_controlled_test_consumption",
            "authorization_state_required": NON_PRODUCTION_AUTHORIZATION_STATE,
            "runtime_manifest_consumption_enabled_required": False,
            "production_routing_authorized_required": False,
            "serialized_manifest_must_be_non_production_authoritative": True,
        },
        "limited_experimental_runtime_guard_records": guard_records,
        "safety_confirmations": {
            "guard_readiness_enables_runtime_behavior": False,
            "guard_readiness_authorizes_production_routing": False,
            "guard_readiness_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_limited_experimental_runtime_guards",
            "observational_only": True,
            "guard_contract_only": True,
            "controlled_test_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_LIMITED_RUNTIME_GUARD_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _readiness_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("promotion_readiness_records", [])]


def _eligibility_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("eligibility_records", [])]


def _serialized_manifests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("serialized_manifests", [])]


def _guard_record(
    *,
    readiness: dict[str, Any],
    eligibility: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    runtime_enabled: bool,
    production_routing_authorized: bool,
) -> dict[str, Any]:
    blockers = _blockers(
        readiness=readiness,
        eligibility=eligibility,
        manifest=manifest,
        runtime_enabled=runtime_enabled,
        production_routing_authorized=production_routing_authorized,
    )
    status = blockers[0] if blockers else "guard_contract_ready"
    authorization_state = _authorization_state(readiness=readiness, eligibility=eligibility, manifest=manifest)
    seed = {
        "manifest_id": readiness.get("manifest_id"),
        "fixture_set_id": readiness.get("fixture_set_id"),
        "status": status,
        "token": STABLE_LIMITED_RUNTIME_GUARD_TOKEN,
    }
    return {
        "runtime_guard_contract_id": f"v3_1_limited_runtime_guard_{deterministic_hash(seed)[:16]}",
        "manifest_id": readiness.get("manifest_id"),
        "fixture_set_id": readiness.get("fixture_set_id"),
        "promotion_readiness_status": readiness.get("promotion_readiness_status"),
        "eligibility_status": (eligibility or {}).get("eligibility_status"),
        "authorization_state": authorization_state,
        "runtime_consumption_enabled": runtime_enabled,
        "production_routing_authorized": production_routing_authorized,
        "guard_contract_status": status,
        "blockers": blockers,
        "guard_readiness_enables_runtime_behavior": False,
        "guard_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "guard_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_readiness_record(*, runtime_enabled: bool, production_routing_authorized: bool) -> dict[str, Any]:
    seed = {"missing_readiness": True, "runtime_enabled": runtime_enabled, "production_routing_authorized": production_routing_authorized, "token": STABLE_LIMITED_RUNTIME_GUARD_TOKEN}
    blockers = ["blocked_missing_promotion_readiness"]
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if production_routing_authorized:
        blockers.append("blocked_production_routing_authorized")
    return {
        "runtime_guard_contract_id": f"v3_1_limited_runtime_guard_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "promotion_readiness_status": None,
        "eligibility_status": None,
        "authorization_state": None,
        "runtime_consumption_enabled": runtime_enabled,
        "production_routing_authorized": production_routing_authorized,
        "guard_contract_status": "blocked_missing_promotion_readiness",
        "blockers": blockers,
        "guard_readiness_enables_runtime_behavior": False,
        "guard_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "guard_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(
    *,
    readiness: dict[str, Any],
    eligibility: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    runtime_enabled: bool,
    production_routing_authorized: bool,
) -> list[str]:
    blockers: list[str] = []
    if readiness.get("promotion_readiness_status") != "ready_for_limited_experimental_runtime_consideration":
        blockers.append("blocked_missing_promotion_readiness")
    if eligibility is None or eligibility.get("eligibility_status") != "eligible_for_controlled_test_consumption":
        blockers.append("blocked_invalid_manifest_eligibility")
    if _authorization_state(readiness=readiness, eligibility=eligibility, manifest=manifest) != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if production_routing_authorized:
        blockers.append("blocked_production_routing_authorized")
    if not _manifest_is_non_production_authoritative(manifest):
        blockers.append("blocked_missing_non_production_manifest")
    return sorted(set(blockers), key=blockers.index)


def _authorization_state(
    *,
    readiness: dict[str, Any],
    eligibility: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
) -> str | None:
    states = [
        (eligibility or {}).get("authorization_state"),
        ((manifest or {}).get("authorization_status") or {}).get("authorization_state"),
    ]
    for state in states:
        if state:
            return state
    if readiness.get("promotion_readiness_status") == "ready_for_limited_experimental_runtime_consideration":
        return NON_PRODUCTION_AUTHORIZATION_STATE
    return None


def _manifest_is_non_production_authoritative(manifest: dict[str, Any] | None) -> bool:
    if not manifest:
        return False
    authorization = manifest.get("authorization_status") or {}
    return (
        manifest.get("non_production_authoritative") is True
        and authorization.get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
        and authorization.get("manifest_authorizes_production_routing") is False
        and authorization.get("manifest_is_production_authoritative") is False
        and authorization.get("manifest_is_production_approved") is False
    )


def _runtime_enabled(*values: Any) -> bool:
    for value in values:
        if not isinstance(value, dict):
            continue
        summary = value.get("summary") or {}
        safety = value.get("safety_confirmations") or {}
        if (
            value.get("runtime_manifest_consumption_enabled")
            or value.get("runtime_production_consumption_enabled")
            or summary.get("runtime_manifest_consumption_enabled")
            or summary.get("runtime_production_consumption_enabled")
            or summary.get("manifest_runtime_consumption_enabled")
            or safety.get("runtime_manifest_consumption_enabled")
            or safety.get("runtime_production_consumption_enabled")
        ):
            return True
    return False


def _production_routing_authorized(*values: Any) -> bool:
    for value in values:
        if not isinstance(value, dict):
            continue
        summary = value.get("summary") or {}
        safety = value.get("safety_confirmations") or {}
        if (
            value.get("production_default_routing_authorized")
            or summary.get("production_default_routing_authorized")
            or summary.get("production_routing_authorized")
            or safety.get("production_planner_routing_changed")
            or safety.get("guard_readiness_authorizes_production_routing")
        ):
            return True
    return False


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
    )


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
