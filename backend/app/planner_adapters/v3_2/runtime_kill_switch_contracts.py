"""Runtime kill-switch contracts for v3.2 governance.

This layer defines deterministic emergency shutdown governance for limited
experimental runtime planning. It does not enable runtime manifest consumption,
production routing, or production-authoritative manifest treatment.
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
from app.planner_adapters.v3_2.limited_runtime_consumption_experiment_contracts import (
    LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE,
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


RUNTIME_KILL_SWITCH_SATISFIED = "runtime_kill_switch_satisfied"
RUNTIME_KILL_SWITCH_BLOCKED = "runtime_kill_switch_blocked"
RUNTIME_KILL_SWITCH_ACTIVE = "runtime_kill_switch_active"
RUNTIME_KILL_SWITCH_INACTIVE = "runtime_kill_switch_inactive"
RUNTIME_KILL_SWITCH_POLICY_MISSING = "runtime_kill_switch_policy_missing"
RUNTIME_KILL_SWITCH_SCOPE_MISSING = "runtime_kill_switch_scope_missing"
RUNTIME_KILL_SWITCH_REASON_MISSING = "runtime_kill_switch_reason_missing"
RUNTIME_SHUTDOWN_REQUIRED = "runtime_shutdown_required"
RUNTIME_SHUTDOWN_COMPLETE = "runtime_shutdown_complete"
RUNTIME_SHUTDOWN_INCOMPLETE = "runtime_shutdown_incomplete"
RUNTIME_OVERRIDE_NOT_REQUESTED = "runtime_override_not_requested"
RUNTIME_OVERRIDE_REQUESTED = "runtime_override_requested"
RUNTIME_OVERRIDE_UNAUTHORIZED = "runtime_override_unauthorized"
RUNTIME_OVERRIDE_UNSAFE = "runtime_override_unsafe"
RUNTIME_OVERRIDE_BLOCKED = "runtime_override_blocked"
RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY = (
    "runtime_override_allowed_for_non_production_recovery_only"
)
RUNTIME_EXPERIMENT_COMPATIBILITY_MISSING = "runtime_experiment_compatibility_missing"
RUNTIME_DRIFT_COMPATIBILITY_MISSING = "runtime_drift_compatibility_missing"
RUNTIME_REPLAYABILITY_COMPATIBILITY_MISSING = "runtime_replayability_compatibility_missing"
RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING = "runtime_traceability_compatibility_missing"
RUNTIME_DETERMINISM_COMPATIBILITY_MISSING = "runtime_determinism_compatibility_missing"
RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING = "runtime_diff_audit_compatibility_missing"
RUNTIME_ROLLBACK_COMPATIBILITY_MISSING = "runtime_rollback_compatibility_missing"
RUNTIME_SESSION_COMPATIBILITY_MISSING = "runtime_session_compatibility_missing"
RUNTIME_ISOLATION_COMPATIBILITY_MISSING = "runtime_isolation_compatibility_missing"
RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING = "runtime_entrypoint_compatibility_missing"

RUNTIME_KILL_SWITCH_STATUSES = (
    RUNTIME_KILL_SWITCH_SATISFIED,
    RUNTIME_KILL_SWITCH_BLOCKED,
    RUNTIME_KILL_SWITCH_ACTIVE,
    RUNTIME_KILL_SWITCH_INACTIVE,
    RUNTIME_KILL_SWITCH_POLICY_MISSING,
    RUNTIME_KILL_SWITCH_SCOPE_MISSING,
    RUNTIME_KILL_SWITCH_REASON_MISSING,
    RUNTIME_SHUTDOWN_REQUIRED,
    RUNTIME_SHUTDOWN_INCOMPLETE,
    RUNTIME_OVERRIDE_UNAUTHORIZED,
    RUNTIME_OVERRIDE_UNSAFE,
    RUNTIME_OVERRIDE_BLOCKED,
    RUNTIME_EXPERIMENT_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_COMPATIBILITY_MISSING,
    RUNTIME_REPLAYABILITY_COMPATIBILITY_MISSING,
    RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING,
)
RUNTIME_SHUTDOWN_STATUSES = (
    RUNTIME_SHUTDOWN_COMPLETE,
    RUNTIME_SHUTDOWN_REQUIRED,
    RUNTIME_SHUTDOWN_INCOMPLETE,
)
RUNTIME_KILL_SWITCH_OVERRIDE_STATUSES = (
    RUNTIME_OVERRIDE_NOT_REQUESTED,
    RUNTIME_OVERRIDE_REQUESTED,
    RUNTIME_OVERRIDE_UNAUTHORIZED,
    RUNTIME_OVERRIDE_UNSAFE,
    RUNTIME_OVERRIDE_BLOCKED,
    RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY,
)
STABLE_RUNTIME_KILL_SWITCH_TOKEN = "v3_2_phase_11_runtime_kill_switch_contracts_token"


def build_runtime_kill_switch_contract(
    runtime_kill_switch_requests: dict[str, Any] | list[dict[str, Any]],
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
    limited_runtime_experiment_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_11_runtime_kill_switch_contracts",
) -> dict[str, Any]:
    requests = _records(runtime_kill_switch_requests, "runtime_kill_switch_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    traceability_records = _records(runtime_traceability_contracts, "runtime_traceability_contracts")
    replayability_records = _records(runtime_replayability_contracts, "runtime_replayability_contracts")
    drift_records = _records(runtime_drift_detection_contracts, "runtime_drift_detection_contracts")
    experiment_records = _records(limited_runtime_experiment_contracts, "limited_runtime_experiment_contracts")
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
        "experiment": _by_key(experiment_records),
    }
    contracts = [
        evaluate_runtime_kill_switch_contract(
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
            limited_runtime_experiment_contract=maps["experiment"].get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [
            evaluate_runtime_kill_switch_contract(
                {},
                entrypoint_contract=None,
                isolation_contract=None,
                session_boundary_contract=None,
                safety_rollback_contract=None,
                diff_audit_contract=None,
                determinism_validation_contract=None,
                traceability_contract=None,
                replayability_contract=None,
                drift_detection_contract=None,
                limited_runtime_experiment_contract=None,
            )
        ]
    return summarize_runtime_kill_switch_contract(
        contracts,
        run_id=run_id,
        runtime_kill_switch_requests_hash=_source_hash(runtime_kill_switch_requests),
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
        limited_runtime_experiment_count=len(experiment_records),
    )


def evaluate_runtime_kill_switch_contract(
    runtime_kill_switch_request: dict[str, Any],
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
    limited_runtime_experiment_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    request = deepcopy(runtime_kill_switch_request)
    blockers, override_blockers = _kill_switch_blockers(
        request,
        entrypoint_contract,
        isolation_contract,
        session_boundary_contract,
        safety_rollback_contract,
        diff_audit_contract,
        determinism_validation_contract,
        traceability_contract,
        replayability_contract,
        drift_detection_contract,
        limited_runtime_experiment_contract,
    )
    status = classify_runtime_kill_switch_state(request, blockers=blockers)
    shutdown_status = classify_runtime_shutdown_state(request, blockers=blockers)
    override_status = classify_runtime_kill_switch_override_state(
        request,
        blockers=override_blockers,
    )
    manifest_id = request.get("manifest_id") or (limited_runtime_experiment_contract or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (limited_runtime_experiment_contract or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "shutdown_status": shutdown_status,
        "override_status": override_status,
        "token": STABLE_RUNTIME_KILL_SWITCH_TOKEN,
    }
    return {
        "runtime_kill_switch_contract_id": f"v3_2_runtime_kill_switch_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "kill_switch_policy_state": request.get("kill_switch_policy_state"),
        "kill_switch_activation_state": request.get("kill_switch_activation_state"),
        "kill_switch_scope_state": request.get("kill_switch_scope_state"),
        "kill_switch_reason_state": request.get("kill_switch_reason_state"),
        "kill_switch_shutdown_state": request.get("kill_switch_shutdown_state"),
        "kill_switch_override_intent_state": request.get("kill_switch_override_intent_state"),
        "kill_switch_override_authorization_state": request.get("kill_switch_override_authorization_state"),
        "kill_switch_override_safety_state": request.get("kill_switch_override_safety_state"),
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
        "limited_runtime_experiment_status": (limited_runtime_experiment_contract or {}).get("limited_runtime_experiment_status"),
        "runtime_kill_switch_status": status,
        "runtime_shutdown_status": shutdown_status,
        "runtime_kill_switch_override_status": override_status,
        "kill_switch_blocker_state": "blocked" if blockers else "unblocked_for_kill_switch_governance_only",
        "kill_switch_blockers": blockers,
        "override_blockers": override_blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_manifest_consumption_enabled_by_default": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "production_authoritative_manifest_treatment": False,
        "runtime_experiment_continuation_authorized": False,
        "runtime_kill_switch_contract_authorizes_runtime_consumption": False,
        "runtime_kill_switch_contract_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_kill_switch_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_kill_switch_failures_allowed": False,
            "implicit_experiment_continuation_allowed": False,
            "fallback_kill_switch_logic_allowed": False,
            "override_allowed_only_for_non_production_recovery": override_status
            == RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY,
        },
    }


def classify_runtime_kill_switch_state(
    runtime_kill_switch_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    blocker_set = set(blockers if blockers is not None else _kill_switch_blockers(runtime_kill_switch_request or {}, None, None, None, None, None, None, None, None, None, None)[0])
    for blocker, status in _STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return RUNTIME_KILL_SWITCH_BLOCKED
    if (runtime_kill_switch_request or {}).get("kill_switch_activation_state") == "runtime_kill_switch_inactive":
        return RUNTIME_KILL_SWITCH_SATISFIED
    return RUNTIME_KILL_SWITCH_BLOCKED


def classify_runtime_shutdown_state(
    runtime_kill_switch_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    blocker_set = set(blockers or [])
    if "runtime_shutdown_incomplete" in blocker_set:
        return RUNTIME_SHUTDOWN_INCOMPLETE
    if (runtime_kill_switch_request or {}).get("kill_switch_shutdown_state") == RUNTIME_SHUTDOWN_REQUIRED:
        return RUNTIME_SHUTDOWN_REQUIRED
    if "runtime_shutdown_required" in blocker_set:
        return RUNTIME_SHUTDOWN_REQUIRED
    return RUNTIME_SHUTDOWN_COMPLETE


def classify_runtime_kill_switch_override_state(
    runtime_kill_switch_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    request = runtime_kill_switch_request or {}
    blocker_set = set(blockers or [])
    if "runtime_override_unauthorized" in blocker_set:
        return RUNTIME_OVERRIDE_UNAUTHORIZED
    if "runtime_override_unsafe" in blocker_set:
        return RUNTIME_OVERRIDE_UNSAFE
    if blocker_set:
        return RUNTIME_OVERRIDE_BLOCKED
    if request.get("kill_switch_override_intent_state") == "runtime_override_requested":
        if (
            request.get("kill_switch_override_authorization_state")
            == "override_authorized_for_non_production_recovery"
            and request.get("kill_switch_override_safety_state")
            == "override_safe_for_non_production_recovery"
        ):
            return RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY
        return RUNTIME_OVERRIDE_REQUESTED
    return RUNTIME_OVERRIDE_NOT_REQUESTED


def summarize_runtime_kill_switch_contract(
    runtime_kill_switch_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_11_runtime_kill_switch_contracts",
    runtime_kill_switch_requests_hash: str | None = None,
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
    limited_runtime_experiment_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(runtime_kill_switch_contracts, key=_record_sort_key)]
    status_counts = Counter(record["runtime_kill_switch_status"] for record in contracts)
    shutdown_counts = Counter(record["runtime_shutdown_status"] for record in contracts)
    override_counts = Counter(record["runtime_kill_switch_override_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["kill_switch_blockers"])
    override_blocker_counts = Counter(blocker for record in contracts for blocker in record["override_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_kill_switch_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_kill_switch_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "runtime_isolation_contract_count": isolation_count,
            "runtime_session_boundary_contract_count": session_count,
            "runtime_safety_rollback_contract_count": safety_rollback_count,
            "runtime_diff_audit_contract_count": diff_audit_count,
            "runtime_determinism_validation_contract_count": determinism_count,
            "runtime_traceability_contract_count": traceability_count,
            "runtime_replayability_contract_count": replayability_count,
            "runtime_drift_detection_contract_count": drift_detection_count,
            "limited_runtime_experiment_contract_count": limited_runtime_experiment_count,
            "runtime_kill_switch_requests_hash": runtime_kill_switch_requests_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_kill_switch_satisfied_count": status_counts[RUNTIME_KILL_SWITCH_SATISFIED],
            "runtime_kill_switch_blocked_count": len(contracts) - status_counts[RUNTIME_KILL_SWITCH_SATISFIED],
            "runtime_kill_switch_active_count": status_counts[RUNTIME_KILL_SWITCH_ACTIVE],
            "runtime_shutdown_complete_count": shutdown_counts[RUNTIME_SHUTDOWN_COMPLETE],
            "runtime_shutdown_required_count": shutdown_counts[RUNTIME_SHUTDOWN_REQUIRED],
            "runtime_shutdown_incomplete_count": shutdown_counts[RUNTIME_SHUTDOWN_INCOMPLETE],
            "runtime_override_allowed_non_production_recovery_count": override_counts[
                RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY
            ],
            "runtime_override_blocked_count": override_counts[RUNTIME_OVERRIDE_UNAUTHORIZED]
            + override_counts[RUNTIME_OVERRIDE_UNSAFE]
            + override_counts[RUNTIME_OVERRIDE_BLOCKED],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_authoritative_manifest_treatment": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_kill_switch_status_counts": {status: status_counts[status] for status in RUNTIME_KILL_SWITCH_STATUSES},
        "runtime_shutdown_status_counts": {status: shutdown_counts[status] for status in RUNTIME_SHUTDOWN_STATUSES},
        "runtime_kill_switch_override_status_counts": {
            status: override_counts[status] for status in RUNTIME_KILL_SWITCH_OVERRIDE_STATUSES
        },
        "kill_switch_policy_distribution": _distribution(contracts, "kill_switch_policy_state"),
        "kill_switch_activation_distribution": _distribution(contracts, "kill_switch_activation_state"),
        "kill_switch_scope_distribution": _distribution(contracts, "kill_switch_scope_state"),
        "kill_switch_reason_distribution": _distribution(contracts, "kill_switch_reason_state"),
        "shutdown_state_distribution": _distribution(contracts, "kill_switch_shutdown_state"),
        "override_intent_distribution": _distribution(contracts, "kill_switch_override_intent_state"),
        "override_authorization_distribution": _distribution(contracts, "kill_switch_override_authorization_state"),
        "override_safety_distribution": _distribution(contracts, "kill_switch_override_safety_state"),
        "experiment_compatibility_distribution": _distribution(contracts, "limited_runtime_experiment_status"),
        "drift_compatibility_distribution": _distribution(contracts, "drift_detection_contract_status"),
        "replayability_compatibility_distribution": _distribution(contracts, "replayability_contract_status"),
        "traceability_compatibility_distribution": _distribution(contracts, "traceability_contract_status"),
        "determinism_compatibility_distribution": _distribution(contracts, "determinism_contract_status"),
        "diff_audit_compatibility_distribution": _distribution(contracts, "diff_audit_contract_status"),
        "rollback_compatibility_distribution": _distribution(contracts, "rollback_contract_status"),
        "session_compatibility_distribution": _distribution(contracts, "session_boundary_contract_status"),
        "isolation_compatibility_distribution": _distribution(contracts, "isolation_contract_status"),
        "entrypoint_compatibility_distribution": _distribution(contracts, "entrypoint_contract_status"),
        "kill_switch_blocker_distribution": dict(sorted(blocker_counts.items())),
        "override_blocker_distribution": dict(sorted(override_blocker_counts.items())),
        "runtime_disabled_path_verification": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "default_manifest_consumption_enabled": False,
            "production_authoritative_manifest_treatment": False,
            "silent_kill_switch_failures_allowed": False,
            "implicit_experiment_continuation_allowed": False,
            "fallback_kill_switch_logic_allowed": False,
        },
        "runtime_kill_switch_contracts": contracts,
        "safety_confirmations": {
            "runtime_kill_switch_contract_enables_runtime_manifest_consumption": False,
            "runtime_kill_switch_contract_authorizes_production_routing": False,
            "runtime_kill_switch_contract_treats_manifest_as_production_authoritative": False,
            "production_runtime_routing_prohibited": True,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
        },
        "metadata": {
            "source": "v3_2_runtime_kill_switch_contracts",
            "governance_only": True,
            "runtime_kill_switch_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_RUNTIME_KILL_SWITCH_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


_STATUS_PRIORITY = (
    ("runtime_kill_switch_policy_missing", RUNTIME_KILL_SWITCH_POLICY_MISSING),
    ("runtime_kill_switch_scope_missing", RUNTIME_KILL_SWITCH_SCOPE_MISSING),
    ("runtime_kill_switch_reason_missing", RUNTIME_KILL_SWITCH_REASON_MISSING),
    ("runtime_shutdown_incomplete", RUNTIME_SHUTDOWN_INCOMPLETE),
    ("runtime_override_unauthorized", RUNTIME_OVERRIDE_UNAUTHORIZED),
    ("runtime_override_unsafe", RUNTIME_OVERRIDE_UNSAFE),
    ("runtime_kill_switch_active", RUNTIME_KILL_SWITCH_ACTIVE),
    ("runtime_shutdown_required", RUNTIME_SHUTDOWN_REQUIRED),
    ("runtime_experiment_compatibility_missing", RUNTIME_EXPERIMENT_COMPATIBILITY_MISSING),
    ("runtime_drift_compatibility_missing", RUNTIME_DRIFT_COMPATIBILITY_MISSING),
    ("runtime_replayability_compatibility_missing", RUNTIME_REPLAYABILITY_COMPATIBILITY_MISSING),
    ("runtime_traceability_compatibility_missing", RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING),
    ("runtime_determinism_compatibility_missing", RUNTIME_DETERMINISM_COMPATIBILITY_MISSING),
    ("runtime_diff_audit_compatibility_missing", RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING),
    ("runtime_rollback_compatibility_missing", RUNTIME_ROLLBACK_COMPATIBILITY_MISSING),
    ("runtime_session_compatibility_missing", RUNTIME_SESSION_COMPATIBILITY_MISSING),
    ("runtime_isolation_compatibility_missing", RUNTIME_ISOLATION_COMPATIBILITY_MISSING),
    ("runtime_entrypoint_compatibility_missing", RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING),
)


def _kill_switch_blockers(
    request: dict[str, Any],
    entrypoint: dict[str, Any] | None,
    isolation: dict[str, Any] | None,
    session: dict[str, Any] | None,
    safety: dict[str, Any] | None,
    diff: dict[str, Any] | None,
    determinism: dict[str, Any] | None,
    traceability: dict[str, Any] | None,
    replayability: dict[str, Any] | None,
    drift: dict[str, Any] | None,
    experiment: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    override_blockers: list[str] = []
    if request.get("kill_switch_policy_state") != "kill_switch_policy_present":
        blockers.append("runtime_kill_switch_policy_missing")
    if request.get("kill_switch_scope_state") != "kill_switch_scope_limited_runtime_experiment":
        blockers.append("runtime_kill_switch_scope_missing")
    active = request.get("kill_switch_activation_state") == "runtime_kill_switch_active"
    if active:
        if request.get("kill_switch_reason_state") in {None, "missing", "kill_switch_reason_not_required"}:
            blockers.append("runtime_kill_switch_reason_missing")
        blockers.append("runtime_kill_switch_active")
        if request.get("kill_switch_shutdown_state") == "runtime_shutdown_incomplete":
            blockers.append("runtime_shutdown_incomplete")
        else:
            blockers.append("runtime_shutdown_required")
    elif request.get("kill_switch_activation_state") != "runtime_kill_switch_inactive":
        blockers.append("runtime_kill_switch_policy_missing")
    if request.get("kill_switch_shutdown_state") == "runtime_shutdown_incomplete":
        blockers.append("runtime_shutdown_incomplete")
    if request.get("kill_switch_override_intent_state") == "runtime_override_requested":
        if request.get("kill_switch_override_authorization_state") != "override_authorized_for_non_production_recovery":
            override_blockers.append("runtime_override_unauthorized")
        if request.get("kill_switch_override_safety_state") != "override_safe_for_non_production_recovery":
            override_blockers.append("runtime_override_unsafe")
    blockers.extend(override_blockers)
    if experiment is None or experiment.get("limited_runtime_experiment_status") != LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE:
        blockers.append("runtime_experiment_compatibility_missing")
    if drift is None or drift.get("runtime_drift_detection_status") not in {RUNTIME_DRIFT_DETECTION_SATISFIED, RUNTIME_DRIFT_NOT_DETECTED}:
        blockers.append("runtime_drift_compatibility_missing")
    if replayability is None or replayability.get("runtime_replayability_status") != RUNTIME_REPLAYABILITY_SATISFIED:
        blockers.append("runtime_replayability_compatibility_missing")
    if traceability is None or traceability.get("runtime_traceability_status") != RUNTIME_TRACEABILITY_SATISFIED:
        blockers.append("runtime_traceability_compatibility_missing")
    if determinism is None or determinism.get("runtime_determinism_status") != RUNTIME_DETERMINISM_SATISFIED:
        blockers.append("runtime_determinism_compatibility_missing")
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("runtime_diff_audit_compatibility_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED:
        blockers.append("runtime_rollback_compatibility_missing")
    if safety is None or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("runtime_rollback_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("runtime_session_compatibility_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("runtime_isolation_compatibility_missing")
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("runtime_entrypoint_compatibility_missing")
    return sorted(set(blockers), key=blockers.index), sorted(set(override_blockers), key=override_blockers.index)


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
