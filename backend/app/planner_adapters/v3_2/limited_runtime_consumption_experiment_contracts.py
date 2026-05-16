"""Limited runtime consumption experiment contracts for v3.2 governance.

This layer evaluates explicit non-production experiment eligibility on top of
the v3.2 runtime governance chain. It does not enable default runtime manifest
consumption, production routing, or production-authoritative manifests.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash
from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import (
    EXPERIMENTAL_RUNTIME_ELIGIBLE,
    PRODUCTION_RUNTIME_PROHIBITED,
)
from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import RUNTIME_DETERMINISM_SATISFIED
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import RUNTIME_DIFF_AUDIT_SATISFIED
from app.planner_adapters.v3_2.runtime_drift_detection_contracts import (
    RUNTIME_DRIFT_DETECTION_SATISFIED,
    RUNTIME_DRIFT_NOT_DETECTED,
)
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_replayability_contracts import RUNTIME_REPLAYABILITY_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED
from app.planner_adapters.v3_2.runtime_traceability_contracts import RUNTIME_TRACEABILITY_SATISFIED


LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE = "limited_runtime_experiment_eligible"
LIMITED_RUNTIME_EXPERIMENT_BLOCKED = "limited_runtime_experiment_blocked"
EXPERIMENT_AUTHORIZATION_MISSING = "experiment_authorization_missing"
EXPERIMENT_INTENT_MISSING = "experiment_intent_missing"
EXPERIMENT_SCOPE_MISSING = "experiment_scope_missing"
EXPERIMENT_SCOPE_UNSAFE = "experiment_scope_unsafe"
EXPERIMENT_CONSUMPTION_MODE_INVALID = "experiment_consumption_mode_invalid"
EXPERIMENT_MANIFEST_AUTHORITY_INVALID = "experiment_manifest_authority_invalid"
EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED = "experiment_production_routing_prohibited"
EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED = "experiment_default_manifest_consumption_prohibited"
EXPERIMENT_ISOLATION_COMPATIBILITY_MISSING = "experiment_isolation_compatibility_missing"
EXPERIMENT_SESSION_COMPATIBILITY_MISSING = "experiment_session_compatibility_missing"
EXPERIMENT_SAFETY_ROLLBACK_COMPATIBILITY_MISSING = "experiment_safety_rollback_compatibility_missing"
EXPERIMENT_DIFF_AUDIT_COMPATIBILITY_MISSING = "experiment_diff_audit_compatibility_missing"
EXPERIMENT_DETERMINISM_COMPATIBILITY_MISSING = "experiment_determinism_compatibility_missing"
EXPERIMENT_TRACEABILITY_COMPATIBILITY_MISSING = "experiment_traceability_compatibility_missing"
EXPERIMENT_REPLAYABILITY_COMPATIBILITY_MISSING = "experiment_replayability_compatibility_missing"
EXPERIMENT_DRIFT_DETECTION_COMPATIBILITY_MISSING = "experiment_drift_detection_compatibility_missing"
EXPERIMENT_ROLLBACK_READINESS_MISSING = "experiment_rollback_readiness_missing"

LIMITED_RUNTIME_EXPERIMENT_STATUSES = (
    LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE,
    LIMITED_RUNTIME_EXPERIMENT_BLOCKED,
    EXPERIMENT_AUTHORIZATION_MISSING,
    EXPERIMENT_INTENT_MISSING,
    EXPERIMENT_SCOPE_MISSING,
    EXPERIMENT_SCOPE_UNSAFE,
    EXPERIMENT_CONSUMPTION_MODE_INVALID,
    EXPERIMENT_MANIFEST_AUTHORITY_INVALID,
    EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED,
    EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED,
    EXPERIMENT_ISOLATION_COMPATIBILITY_MISSING,
    EXPERIMENT_SESSION_COMPATIBILITY_MISSING,
    EXPERIMENT_SAFETY_ROLLBACK_COMPATIBILITY_MISSING,
    EXPERIMENT_DIFF_AUDIT_COMPATIBILITY_MISSING,
    EXPERIMENT_DETERMINISM_COMPATIBILITY_MISSING,
    EXPERIMENT_TRACEABILITY_COMPATIBILITY_MISSING,
    EXPERIMENT_REPLAYABILITY_COMPATIBILITY_MISSING,
    EXPERIMENT_DRIFT_DETECTION_COMPATIBILITY_MISSING,
    EXPERIMENT_ROLLBACK_READINESS_MISSING,
)
LIMITED_RUNTIME_CONSUMPTION_MODE_STATUSES = (
    LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE,
    EXPERIMENT_CONSUMPTION_MODE_INVALID,
    EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED,
    EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED,
)
STABLE_LIMITED_RUNTIME_EXPERIMENT_TOKEN = "v3_2_phase_10_limited_runtime_consumption_experiment_contracts_token"


def build_limited_runtime_consumption_experiment_contract(
    limited_runtime_experiment_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_determinism_validation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_traceability_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_replayability_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_drift_detection_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_10_limited_runtime_consumption_experiment_contracts",
) -> dict[str, Any]:
    requests = _records(limited_runtime_experiment_requests, "limited_runtime_experiment_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    traceability_records = _records(runtime_traceability_contracts, "runtime_traceability_contracts")
    replayability_records = _records(runtime_replayability_contracts, "runtime_replayability_contracts")
    drift_records = _records(runtime_drift_detection_contracts, "runtime_drift_detection_contracts")
    maps = {
        "entrypoint": _by_key(entrypoints),
        "isolation": _by_key(isolations),
        "session": _by_key(sessions),
        "safety": _by_key(safety_records),
        "diff": _by_key(diff_records),
        "determinism": _by_key(determinism_records),
        "traceability": _by_key(traceability_records),
        "replayability": _by_key(replayability_records),
        "drift": _by_key(drift_records),
    }
    contracts = [
        evaluate_limited_runtime_consumption_experiment_contract(
            request,
            entrypoint_contract=maps["entrypoint"].get(_trace_key(request)),
            isolation_contract=maps["isolation"].get(_trace_key(request)),
            session_boundary_contract=maps["session"].get(_trace_key(request)),
            safety_rollback_contract=maps["safety"].get(_trace_key(request)),
            diff_audit_contract=maps["diff"].get(_trace_key(request)),
            determinism_validation_contract=maps["determinism"].get(_trace_key(request)),
            traceability_contract=maps["traceability"].get(_trace_key(request)),
            replayability_contract=maps["replayability"].get(_trace_key(request)),
            drift_detection_contract=maps["drift"].get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_limited_runtime_consumption_experiment_contract({}, entrypoint_contract=None, isolation_contract=None, session_boundary_contract=None, safety_rollback_contract=None, diff_audit_contract=None, determinism_validation_contract=None, traceability_contract=None, replayability_contract=None, drift_detection_contract=None)]
    return summarize_limited_runtime_consumption_experiment_contract(
        contracts,
        run_id=run_id,
        limited_runtime_experiment_requests_hash=_source_hash(limited_runtime_experiment_requests),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
        safety_rollback_count=len(safety_records),
        diff_audit_count=len(diff_records),
        determinism_count=len(determinism_records),
        traceability_count=len(traceability_records),
        replayability_count=len(replayability_records),
        drift_detection_count=len(drift_records),
    )


def evaluate_limited_runtime_consumption_experiment_contract(
    limited_runtime_experiment_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
    determinism_validation_contract: dict[str, Any] | None,
    traceability_contract: dict[str, Any] | None,
    replayability_contract: dict[str, Any] | None,
    drift_detection_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    request = deepcopy(limited_runtime_experiment_request)
    blockers = _experiment_blockers(request, entrypoint_contract, isolation_contract, session_boundary_contract, safety_rollback_contract, diff_audit_contract, determinism_validation_contract, traceability_contract, replayability_contract, drift_detection_contract)
    status = classify_limited_runtime_consumption_experiment_state(request, blockers=blockers)
    mode_status = classify_limited_runtime_consumption_mode_state(request, blockers=blockers)
    manifest_id = request.get("manifest_id") or (drift_detection_contract or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (drift_detection_contract or {}).get("fixture_set_id")
    seed = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "status": status, "mode": mode_status, "token": STABLE_LIMITED_RUNTIME_EXPERIMENT_TOKEN}
    return {
        "limited_runtime_experiment_contract_id": f"v3_2_limited_runtime_experiment_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "experiment_authorization_state": request.get("experiment_authorization_state"),
        "experiment_intent_state": request.get("experiment_intent_state"),
        "experiment_scope_state": request.get("experiment_scope_state"),
        "experiment_eligibility_state": request.get("experiment_eligibility_state"),
        "experiment_consumption_mode_state": request.get("experiment_consumption_mode_state"),
        "experiment_manifest_authority_state": request.get("experiment_manifest_authority_state"),
        "experiment_production_prohibition_state": request.get("experiment_production_prohibition_state"),
        "runtime_manifest_consumption_enabled_by_default": request.get("runtime_manifest_consumption_enabled_by_default", False),
        "production_routing_authorized_by_experiment": request.get("production_routing_authorized_by_experiment", False),
        "entrypoint_contract_status": (entrypoint_contract or {}).get("runtime_entrypoint_status"),
        "isolation_contract_status": (isolation_contract or {}).get("runtime_isolation_status"),
        "session_boundary_contract_status": (session_boundary_contract or {}).get("runtime_session_boundary_status"),
        "safety_contract_status": (safety_rollback_contract or {}).get("runtime_safety_status"),
        "rollback_contract_status": (safety_rollback_contract or {}).get("runtime_rollback_status"),
        "diff_audit_contract_status": (diff_audit_contract or {}).get("runtime_diff_audit_status"),
        "determinism_contract_status": (determinism_validation_contract or {}).get("runtime_determinism_status"),
        "traceability_contract_status": (traceability_contract or {}).get("runtime_traceability_status"),
        "replayability_contract_status": (replayability_contract or {}).get("runtime_replayability_status"),
        "drift_detection_contract_status": (drift_detection_contract or {}).get("runtime_drift_detection_status"),
        "limited_runtime_experiment_status": status,
        "limited_runtime_consumption_mode_status": mode_status,
        "experiment_blocker_state": "blocked" if blockers else "unblocked_for_experiment_review_only",
        "experiment_blockers": blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "production_authoritative_manifest_treatment": False,
        "limited_runtime_experiment_authorizes_runtime_consumption": False,
        "limited_runtime_experiment_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {"governance_only": True, "limited_runtime_consumption_experiment_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_authoritative_manifest_treatment_prohibited": True, "production_consumer": False, "planner_remap_performed": False, "silent_experiment_eligibility_allowed": False, "implicit_runtime_consumption_allowed": False, "fallback_experiment_logic_allowed": False},
    }


def classify_limited_runtime_consumption_experiment_state(limited_runtime_experiment_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _experiment_blockers(limited_runtime_experiment_request or {}, None, None, None, None, None, None, None, None, None))
    for blocker, status in _STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return LIMITED_RUNTIME_EXPERIMENT_BLOCKED
    return LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE


def classify_limited_runtime_consumption_mode_state(limited_runtime_experiment_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _experiment_blockers(limited_runtime_experiment_request or {}, None, None, None, None, None, None, None, None, None))
    if "experiment_production_routing_prohibited" in blocker_set:
        return EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED
    if "experiment_default_manifest_consumption_prohibited" in blocker_set:
        return EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED
    if "experiment_consumption_mode_invalid" in blocker_set:
        return EXPERIMENT_CONSUMPTION_MODE_INVALID
    return LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE


def summarize_limited_runtime_consumption_experiment_contract(
    limited_runtime_experiment_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_10_limited_runtime_consumption_experiment_contracts",
    limited_runtime_experiment_requests_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
    safety_rollback_count: int | None = None,
    diff_audit_count: int | None = None,
    determinism_count: int | None = None,
    traceability_count: int | None = None,
    replayability_count: int | None = None,
    drift_detection_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(limited_runtime_experiment_contracts, key=_record_sort_key)]
    status_counts = Counter(record["limited_runtime_experiment_status"] for record in contracts)
    mode_counts = Counter(record["limited_runtime_consumption_mode_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["experiment_blockers"])
    envelope = {
        "schema_version": "v3_2.limited_runtime_consumption_experiment_contracts.1",
        "run": {"run_id": run_id, "limited_runtime_experiment_request_count": len(contracts) if request_count is None else request_count, "entrypoint_contract_count": entrypoint_count, "runtime_isolation_contract_count": isolation_count, "runtime_session_boundary_contract_count": session_count, "runtime_safety_rollback_contract_count": safety_rollback_count, "runtime_diff_audit_contract_count": diff_audit_count, "runtime_determinism_validation_contract_count": determinism_count, "runtime_traceability_contract_count": traceability_count, "runtime_replayability_contract_count": replayability_count, "runtime_drift_detection_contract_count": drift_detection_count, "limited_runtime_experiment_requests_hash": limited_runtime_experiment_requests_hash},
        "summary": {"records_evaluated": len(contracts), "limited_runtime_experiment_eligible_count": status_counts[LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE], "limited_runtime_experiment_blocked_count": len(contracts) - status_counts[LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE], "experiment_authorization_missing_count": status_counts[EXPERIMENT_AUTHORIZATION_MISSING], "experiment_scope_unsafe_count": status_counts[EXPERIMENT_SCOPE_UNSAFE], "experiment_consumption_mode_invalid_count": status_counts[EXPERIMENT_CONSUMPTION_MODE_INVALID], "experiment_manifest_authority_invalid_count": status_counts[EXPERIMENT_MANIFEST_AUTHORITY_INVALID], "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_routing_authorized": False, "production_default_routing_authorized": False, "production_authoritative_manifest_treatment": False, "production_output_affected": False, "production_behavior_changed": False, "deterministic": True},
        "limited_runtime_experiment_status_counts": {status: status_counts[status] for status in LIMITED_RUNTIME_EXPERIMENT_STATUSES},
        "limited_runtime_consumption_mode_status_counts": {status: mode_counts[status] for status in LIMITED_RUNTIME_CONSUMPTION_MODE_STATUSES},
        "experiment_authorization_distribution": _distribution(contracts, "experiment_authorization_state"),
        "experiment_intent_distribution": _distribution(contracts, "experiment_intent_state"),
        "experiment_scope_distribution": _distribution(contracts, "experiment_scope_state"),
        "experiment_eligibility_distribution": _distribution(contracts, "experiment_eligibility_state"),
        "experiment_consumption_mode_distribution": _distribution(contracts, "experiment_consumption_mode_state"),
        "experiment_manifest_authority_distribution": _distribution(contracts, "experiment_manifest_authority_state"),
        "experiment_production_prohibition_distribution": _distribution(contracts, "experiment_production_prohibition_state"),
        "isolation_compatibility_distribution": _distribution(contracts, "isolation_contract_status"),
        "session_compatibility_distribution": _distribution(contracts, "session_boundary_contract_status"),
        "safety_rollback_compatibility_distribution": _distribution(contracts, "safety_contract_status"),
        "diff_audit_compatibility_distribution": _distribution(contracts, "diff_audit_contract_status"),
        "determinism_compatibility_distribution": _distribution(contracts, "determinism_contract_status"),
        "traceability_compatibility_distribution": _distribution(contracts, "traceability_contract_status"),
        "replayability_compatibility_distribution": _distribution(contracts, "replayability_contract_status"),
        "drift_detection_compatibility_distribution": _distribution(contracts, "drift_detection_contract_status"),
        "rollback_readiness_distribution": _distribution(contracts, "rollback_contract_status"),
        "experiment_blocker_distribution": dict(sorted(blocker_counts.items())),
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "default_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False, "silent_experiment_eligibility_allowed": False, "implicit_runtime_consumption_allowed": False, "fallback_experiment_logic_allowed": False},
        "limited_runtime_experiment_contracts": contracts,
        "safety_confirmations": {"limited_runtime_experiment_enables_runtime_manifest_consumption": False, "limited_runtime_experiment_authorizes_production_routing": False, "limited_runtime_experiment_treats_manifest_as_production_authoritative": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_limited_runtime_consumption_experiment_contracts", "governance_only": True, "limited_runtime_consumption_experiment_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_authoritative_manifest_treatment_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_LIMITED_RUNTIME_EXPERIMENT_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


_STATUS_PRIORITY = (
    ("experiment_authorization_missing", EXPERIMENT_AUTHORIZATION_MISSING),
    ("experiment_intent_missing", EXPERIMENT_INTENT_MISSING),
    ("experiment_scope_missing", EXPERIMENT_SCOPE_MISSING),
    ("experiment_scope_unsafe", EXPERIMENT_SCOPE_UNSAFE),
    ("experiment_consumption_mode_invalid", EXPERIMENT_CONSUMPTION_MODE_INVALID),
    ("experiment_manifest_authority_invalid", EXPERIMENT_MANIFEST_AUTHORITY_INVALID),
    ("experiment_production_routing_prohibited", EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED),
    ("experiment_default_manifest_consumption_prohibited", EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED),
    ("experiment_isolation_compatibility_missing", EXPERIMENT_ISOLATION_COMPATIBILITY_MISSING),
    ("experiment_session_compatibility_missing", EXPERIMENT_SESSION_COMPATIBILITY_MISSING),
    ("experiment_safety_rollback_compatibility_missing", EXPERIMENT_SAFETY_ROLLBACK_COMPATIBILITY_MISSING),
    ("experiment_rollback_readiness_missing", EXPERIMENT_ROLLBACK_READINESS_MISSING),
    ("experiment_diff_audit_compatibility_missing", EXPERIMENT_DIFF_AUDIT_COMPATIBILITY_MISSING),
    ("experiment_determinism_compatibility_missing", EXPERIMENT_DETERMINISM_COMPATIBILITY_MISSING),
    ("experiment_traceability_compatibility_missing", EXPERIMENT_TRACEABILITY_COMPATIBILITY_MISSING),
    ("experiment_replayability_compatibility_missing", EXPERIMENT_REPLAYABILITY_COMPATIBILITY_MISSING),
    ("experiment_drift_detection_compatibility_missing", EXPERIMENT_DRIFT_DETECTION_COMPATIBILITY_MISSING),
)


def _experiment_blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None, session: dict[str, Any] | None, safety: dict[str, Any] | None, diff: dict[str, Any] | None, determinism: dict[str, Any] | None, traceability: dict[str, Any] | None, replayability: dict[str, Any] | None, drift: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if request.get("experiment_authorization_state") != "experiment_authorized":
        blockers.append("experiment_authorization_missing")
    if request.get("experiment_intent_state") != "limited_runtime_consumption_experiment_intent_explicit":
        blockers.append("experiment_intent_missing")
    if request.get("experiment_scope_state") in {None, "missing"}:
        blockers.append("experiment_scope_missing")
    elif request.get("experiment_scope_state") != "non_production_isolated_reversible_limited_scope":
        blockers.append("experiment_scope_unsafe")
    if request.get("experiment_consumption_mode_state") != "experimental_only_consumption_mode":
        blockers.append("experiment_consumption_mode_invalid")
    if request.get("experiment_manifest_authority_state") != "non_production_authoritative":
        blockers.append("experiment_manifest_authority_invalid")
    if request.get("production_routing_authorized_by_experiment") is True:
        blockers.append("experiment_production_routing_prohibited")
    if request.get("runtime_manifest_consumption_enabled_by_default") is True:
        blockers.append("experiment_default_manifest_consumption_prohibited")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("experiment_isolation_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("experiment_session_compatibility_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED:
        blockers.append("experiment_safety_rollback_compatibility_missing")
    if safety is None or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("experiment_rollback_readiness_missing")
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("experiment_diff_audit_compatibility_missing")
    if determinism is None or determinism.get("runtime_determinism_status") != RUNTIME_DETERMINISM_SATISFIED:
        blockers.append("experiment_determinism_compatibility_missing")
    if traceability is None or traceability.get("runtime_traceability_status") != RUNTIME_TRACEABILITY_SATISFIED:
        blockers.append("experiment_traceability_compatibility_missing")
    if replayability is None or replayability.get("runtime_replayability_status") != RUNTIME_REPLAYABILITY_SATISFIED:
        blockers.append("experiment_replayability_compatibility_missing")
    if drift is None or drift.get("runtime_drift_detection_status") not in {RUNTIME_DRIFT_DETECTION_SATISFIED, RUNTIME_DRIFT_NOT_DETECTED}:
        blockers.append("experiment_drift_detection_compatibility_missing")
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("experiment_authorization_missing")
    return sorted(set(blockers), key=blockers.index)


def _records(value: dict[str, Any] | list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get(key, [])]


def _by_key(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {_trace_key(record): record for record in records if _trace_key(record)}


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("fixture_set_id") or ""), str(record.get("manifest_id") or ""))


def _distribution(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(record.get(key) or "missing" for record in records).items()))


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
