"""Experimental runtime entrypoint contracts for v3.2 governance.

This module defines the runtime-adjacent authorization boundary for future
limited experimental runtime work. It is pure, deterministic, and does not
enable runtime manifest consumption or production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.planner_adapters.v3_1.approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash


EXPERIMENTAL_RUNTIME_ELIGIBLE = "experimental_runtime_eligible"
EXPERIMENTAL_RUNTIME_BLOCKED = "experimental_runtime_blocked"
PRODUCTION_RUNTIME_PROHIBITED = "production_runtime_prohibited"
RUNTIME_DISABLED_BY_POLICY = "runtime_disabled_by_policy"
RUNTIME_DISABLED_BY_AUTHORIZATION = "runtime_disabled_by_authorization"
RUNTIME_DISABLED_BY_ISOLATION_FAILURE = "runtime_disabled_by_isolation_failure"
RUNTIME_ROLLBACK_REQUIRED = "runtime_rollback_required"

RUNTIME_ENTRYPOINT_CONTRACT_STATUSES = (
    EXPERIMENTAL_RUNTIME_ELIGIBLE,
    EXPERIMENTAL_RUNTIME_BLOCKED,
    PRODUCTION_RUNTIME_PROHIBITED,
    RUNTIME_DISABLED_BY_POLICY,
    RUNTIME_DISABLED_BY_AUTHORIZATION,
    RUNTIME_DISABLED_BY_ISOLATION_FAILURE,
    RUNTIME_ROLLBACK_REQUIRED,
)
STABLE_RUNTIME_ENTRYPOINT_CONTRACT_TOKEN = "v3_2_phase_1_experimental_runtime_entrypoint_contracts_token"
_REQUIRED_CLOSEOUT_STATUS = "ready_for_future_limited_experimental_runtime_phase"
_REQUIRED_ISOLATION_STATE = "runtime_isolated"
_EXPERIMENTAL_RUNTIME_MODE = "limited_experimental_runtime"
_PRODUCTION_RUNTIME_MODE = "production_runtime"


def build_runtime_entrypoint_contract(
    runtime_entry_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_readiness_closeout: dict[str, Any] | list[dict[str, Any]] | None = None,
    run_id: str = "v3_2_phase_1_experimental_runtime_entrypoint_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime entrypoint contracts from explicit requests."""

    requests = _entry_requests(runtime_entry_requests)
    closeout_records = _closeout_records(experimental_runtime_readiness_closeout or {})
    closeout_by_key = {_trace_key(record): record for record in closeout_records if _trace_key(record)}
    contracts = [
        evaluate_runtime_entrypoint_contract(
            request,
            closeout_record=closeout_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_runtime_entrypoint_contract({}, closeout_record=None)]

    status_counts = Counter(record["runtime_entrypoint_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["blockers"])
    authorization_counts = Counter(record["runtime_authorization_state"] or "missing" for record in contracts)
    isolation_counts = Counter(record["runtime_isolation_state"] or "missing" for record in contracts)
    envelope = {
        "schema_version": "v3_2.experimental_runtime_entrypoint_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_entry_request_count": len(requests),
            "closeout_record_count": len(closeout_records),
            "runtime_entry_requests_hash": _source_hash(runtime_entry_requests),
            "experimental_runtime_readiness_closeout_hash": _source_hash(experimental_runtime_readiness_closeout or {}),
        },
        "summary": {
            "records_evaluated": len(contracts),
            "experimental_runtime_eligible_count": status_counts[EXPERIMENTAL_RUNTIME_ELIGIBLE],
            "experimental_runtime_blocked_count": len(contracts) - status_counts[EXPERIMENTAL_RUNTIME_ELIGIBLE],
            "production_runtime_prohibited_count": status_counts[PRODUCTION_RUNTIME_PROHIBITED],
            "runtime_disabled_by_policy_count": status_counts[RUNTIME_DISABLED_BY_POLICY],
            "runtime_disabled_by_authorization_count": status_counts[RUNTIME_DISABLED_BY_AUTHORIZATION],
            "runtime_disabled_by_isolation_failure_count": status_counts[RUNTIME_DISABLED_BY_ISOLATION_FAILURE],
            "runtime_rollback_required_count": status_counts[RUNTIME_ROLLBACK_REQUIRED],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_entrypoint_status_counts": {
            status: status_counts[status]
            for status in RUNTIME_ENTRYPOINT_CONTRACT_STATUSES
        },
        "authorization_state_distribution": dict(sorted(authorization_counts.items())),
        "isolation_state_distribution": dict(sorted(isolation_counts.items())),
        "blocker_distribution": dict(sorted(blocker_counts.items())),
        "runtime_disabled_path_verification": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "silent_runtime_activation_allowed": False,
            "fallback_authorization_allowed": False,
        },
        "runtime_entrypoint_contracts": contracts,
        "safety_confirmations": {
            "entrypoint_contract_enables_runtime_manifest_consumption": False,
            "entrypoint_contract_authorizes_production_routing": False,
            "entrypoint_contract_authorizes_production_manifests": False,
            "production_runtime_routing_prohibited": True,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_2_experimental_runtime_entrypoint_contracts",
            "governance_only": True,
            "runtime_adjacent_boundary": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_RUNTIME_ENTRYPOINT_CONTRACT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def evaluate_runtime_entrypoint_contract(
    runtime_entry_request: dict[str, Any],
    *,
    closeout_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate one runtime entrypoint request against explicit authorization gates."""

    request = deepcopy(runtime_entry_request)
    closeout = deepcopy(closeout_record) if closeout_record else None
    blockers = _blockers(request, closeout)
    status = classify_runtime_entrypoint_state(request, blockers=blockers)
    manifest_id = request.get("manifest_id") or (closeout or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (closeout or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "token": STABLE_RUNTIME_ENTRYPOINT_CONTRACT_TOKEN,
    }
    runtime_activation_intent = request.get("runtime_activation_intent") or "none"
    return {
        "runtime_entrypoint_contract_id": f"v3_2_runtime_entrypoint_contract_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_authorization_state": request.get("runtime_authorization_state"),
        "runtime_eligibility_state": EXPERIMENTAL_RUNTIME_ELIGIBLE if status == EXPERIMENTAL_RUNTIME_ELIGIBLE else EXPERIMENTAL_RUNTIME_BLOCKED,
        "runtime_blocker_state": "blocked" if blockers else "unblocked_for_contract_only",
        "runtime_isolation_state": request.get("runtime_isolation_state"),
        "runtime_consumption_prohibition_state": "runtime_manifest_consumption_disabled",
        "runtime_activation_intent": runtime_activation_intent,
        "runtime_rollback_eligibility": request.get("runtime_rollback_eligibility"),
        "runtime_trace_classification": _trace_classification(status),
        "runtime_mode": request.get("runtime_mode") or _EXPERIMENTAL_RUNTIME_MODE,
        "explicit_experimental_runtime_opt_in": request.get("explicit_experimental_runtime_opt_in") is True,
        "closeout_readiness_status": (closeout or {}).get("closeout_readiness_status"),
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "runtime_entrypoint_status": status,
        "blockers": blockers,
        "entrypoint_contract_authorizes_runtime_consumption": False,
        "entrypoint_contract_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_adjacent_boundary": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_runtime_activation_allowed": False,
            "fallback_authorization_allowed": False,
        },
    }


def classify_runtime_entrypoint_state(
    runtime_entry_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    """Classify a runtime entrypoint request without collapsing explicit states."""

    request = runtime_entry_request or {}
    blocker_set = set(blockers if blockers is not None else _blockers(request, None))
    if "production_runtime_requested" in blocker_set:
        return PRODUCTION_RUNTIME_PROHIBITED
    if "rollback_required" in blocker_set or "rollback_not_eligible" in blocker_set:
        return RUNTIME_ROLLBACK_REQUIRED
    if "runtime_isolation_missing" in blocker_set or "runtime_isolation_failed" in blocker_set:
        return RUNTIME_DISABLED_BY_ISOLATION_FAILURE
    if "runtime_authorization_missing" in blocker_set or "runtime_authorization_invalid" in blocker_set:
        return RUNTIME_DISABLED_BY_AUTHORIZATION
    if (
        "explicit_experimental_opt_in_missing" in blocker_set
        or "runtime_policy_disabled" in blocker_set
        or "runtime_manifest_consumption_requested" in blocker_set
    ):
        return RUNTIME_DISABLED_BY_POLICY
    if blocker_set:
        return EXPERIMENTAL_RUNTIME_BLOCKED
    return EXPERIMENTAL_RUNTIME_ELIGIBLE


def _blockers(request: dict[str, Any], closeout: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    runtime_mode = request.get("runtime_mode") or _EXPERIMENTAL_RUNTIME_MODE
    if runtime_mode == _PRODUCTION_RUNTIME_MODE:
        blockers.append("production_runtime_requested")
    if request.get("runtime_manifest_consumption_enabled") is True or request.get("runtime_production_consumption_enabled") is True:
        blockers.append("runtime_manifest_consumption_requested")
    if request.get("runtime_policy_allows_entrypoint") is not True:
        blockers.append("runtime_policy_disabled")
    if request.get("explicit_experimental_runtime_opt_in") is not True:
        blockers.append("explicit_experimental_opt_in_missing")
    authorization = request.get("runtime_authorization_state")
    if not authorization:
        blockers.append("runtime_authorization_missing")
    elif authorization != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("runtime_authorization_invalid")
    isolation = request.get("runtime_isolation_state")
    if not isolation:
        blockers.append("runtime_isolation_missing")
    elif isolation != _REQUIRED_ISOLATION_STATE:
        blockers.append("runtime_isolation_failed")
    if request.get("runtime_rollback_required") is True:
        blockers.append("rollback_required")
    if request.get("runtime_rollback_eligibility") is not True:
        blockers.append("rollback_not_eligible")
    if closeout is None:
        blockers.append("missing_runtime_readiness_closeout")
    elif closeout.get("closeout_readiness_status") != _REQUIRED_CLOSEOUT_STATUS:
        blockers.append("runtime_readiness_closeout_not_ready")
    return sorted(set(blockers), key=blockers.index)


def _entry_requests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_entry_requests", [])]


def _closeout_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("closeout_records", [])]


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


def _trace_classification(status: str) -> str:
    if status == EXPERIMENTAL_RUNTIME_ELIGIBLE:
        return "runtime_entry_contract_trace_ready"
    if status == PRODUCTION_RUNTIME_PROHIBITED:
        return "runtime_entry_contract_trace_prohibited"
    if status == RUNTIME_ROLLBACK_REQUIRED:
        return "runtime_entry_contract_trace_rollback_required"
    return "runtime_entry_contract_trace_blocked"


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
