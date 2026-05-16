"""Runtime diff auditing contracts for v3.2 governance.

This layer evaluates explicit before/after runtime-state auditability on top of
the v3.2 isolation, session boundary, and safety rollback contracts. It is
governance-only and does not enable runtime manifest consumption or production
routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash
from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import PRODUCTION_RUNTIME_PROHIBITED
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED


RUNTIME_DIFF_AUDIT_SATISFIED = "runtime_diff_audit_satisfied"
RUNTIME_DIFF_AUDIT_BLOCKED = "runtime_diff_audit_blocked"
RUNTIME_MUTATION_DETECTED = "runtime_mutation_detected"
RUNTIME_MUTATION_PROHIBITED = "runtime_mutation_prohibited"
RUNTIME_DRIFT_DETECTED = "runtime_drift_detected"
RUNTIME_DRIFT_BLOCKED = "runtime_drift_blocked"
RUNTIME_TRANSITION_UNAUDITED = "runtime_transition_unaudited"
RUNTIME_SNAPSHOT_MISSING = "runtime_snapshot_missing"
ROLLBACK_AUDIT_COMPATIBILITY_MISSING = "rollback_audit_compatibility_missing"
ISOLATION_AUDIT_COMPATIBILITY_MISSING = "isolation_audit_compatibility_missing"
SESSION_AUDIT_COMPATIBILITY_MISSING = "session_audit_compatibility_missing"

RUNTIME_DIFF_AUDIT_STATUSES = (
    RUNTIME_DIFF_AUDIT_SATISFIED,
    RUNTIME_DIFF_AUDIT_BLOCKED,
    RUNTIME_MUTATION_DETECTED,
    RUNTIME_MUTATION_PROHIBITED,
    RUNTIME_TRANSITION_UNAUDITED,
    RUNTIME_SNAPSHOT_MISSING,
    ROLLBACK_AUDIT_COMPATIBILITY_MISSING,
    ISOLATION_AUDIT_COMPATIBILITY_MISSING,
    SESSION_AUDIT_COMPATIBILITY_MISSING,
)
RUNTIME_DRIFT_STATUSES = (
    RUNTIME_DIFF_AUDIT_SATISFIED,
    RUNTIME_DRIFT_DETECTED,
    RUNTIME_DRIFT_BLOCKED,
    RUNTIME_SNAPSHOT_MISSING,
    RUNTIME_TRANSITION_UNAUDITED,
)
STABLE_RUNTIME_DIFF_AUDIT_TOKEN = "v3_2_phase_5_runtime_diff_auditing_contracts_token"


def build_runtime_diff_audit_contract(
    runtime_diff_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_5_runtime_diff_auditing_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime diff audit contracts from explicit inputs."""

    requests = _records(runtime_diff_requests, "runtime_diff_requests")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    isolation_records = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    session_records = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_by_key = {_trace_key(record): record for record in safety_records if _trace_key(record)}
    isolation_by_key = {_trace_key(record): record for record in isolation_records if _trace_key(record)}
    session_by_key = {_trace_key(record): record for record in session_records if _trace_key(record)}
    contracts = [
        evaluate_runtime_diff_audit_contract(
            request,
            safety_rollback_contract=safety_by_key.get(_trace_key(request)),
            isolation_contract=isolation_by_key.get(_trace_key(request)),
            session_boundary_contract=session_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [
            evaluate_runtime_diff_audit_contract(
                {},
                safety_rollback_contract=None,
                isolation_contract=None,
                session_boundary_contract=None,
            )
        ]
    return summarize_runtime_diff_audit_contract(
        contracts,
        run_id=run_id,
        runtime_diff_requests_hash=_source_hash(runtime_diff_requests),
        runtime_safety_rollback_contracts_hash=_source_hash(runtime_safety_rollback_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        runtime_session_boundary_contracts_hash=_source_hash(runtime_session_boundary_contracts),
        request_count=len(requests),
        safety_rollback_count=len(safety_records),
        isolation_count=len(isolation_records),
        session_count=len(session_records),
    )


def evaluate_runtime_diff_audit_contract(
    runtime_diff_request: dict[str, Any],
    *,
    safety_rollback_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one runtime diff audit request against prior governance layers."""

    request = deepcopy(runtime_diff_request)
    safety = deepcopy(safety_rollback_contract) if safety_rollback_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    session = deepcopy(session_boundary_contract) if session_boundary_contract else None
    mutation_blockers = _mutation_blockers(request, safety, isolation, session)
    drift_blockers = _drift_blockers(request)
    diff_status = classify_runtime_diff_state(request, blockers=mutation_blockers)
    drift_status = classify_runtime_drift_state(request, blockers=drift_blockers)
    manifest_id = request.get("manifest_id") or (safety or {}).get("manifest_id") or (isolation or {}).get("manifest_id") or (session or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (safety or {}).get("fixture_set_id") or (isolation or {}).get("fixture_set_id") or (session or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "diff": diff_status,
        "drift": drift_status,
        "token": STABLE_RUNTIME_DIFF_AUDIT_TOKEN,
    }
    return {
        "runtime_diff_audit_contract_id": f"v3_2_runtime_diff_audit_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_safety_status": (safety or {}).get("runtime_safety_status"),
        "runtime_rollback_status": (safety or {}).get("runtime_rollback_status"),
        "runtime_isolation_status": (isolation or {}).get("runtime_isolation_status"),
        "runtime_session_boundary_status": (session or {}).get("runtime_session_boundary_status"),
        "runtime_pre_state_snapshot": deepcopy(request.get("runtime_pre_state_snapshot")),
        "runtime_post_state_snapshot": deepcopy(request.get("runtime_post_state_snapshot")),
        "runtime_pre_state_snapshot_hash": _snapshot_signature(request.get("runtime_pre_state_snapshot")),
        "runtime_post_state_snapshot_hash": _snapshot_signature(request.get("runtime_post_state_snapshot")),
        "runtime_mutation_classification": request.get("runtime_mutation_classification"),
        "runtime_drift_classification": request.get("runtime_drift_classification"),
        "runtime_transition_trace": request.get("runtime_transition_trace"),
        "runtime_diff_visibility_state": request.get("runtime_diff_visibility_state"),
        "runtime_auditability_state": request.get("runtime_auditability_state"),
        "runtime_rollback_audit_compatibility": request.get("runtime_rollback_audit_compatibility_state"),
        "runtime_isolation_audit_compatibility": request.get("runtime_isolation_audit_compatibility_state"),
        "runtime_session_audit_compatibility": request.get("runtime_session_audit_compatibility_state"),
        "runtime_mutation_blocker_state": "blocked" if mutation_blockers else "unblocked_for_contract_only",
        "runtime_drift_blocker_state": "blocked" if drift_blockers else "unblocked_for_contract_only",
        "runtime_diff_audit_status": diff_status,
        "runtime_drift_status": drift_status,
        "runtime_audit_trace_classification": _audit_trace(diff_status, drift_status),
        "mutation_blockers": mutation_blockers,
        "drift_blockers": drift_blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_diff_audit_authorizes_runtime_consumption": False,
        "runtime_diff_audit_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_diff_audit_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_runtime_mutations_allowed": False,
            "hidden_runtime_transitions_allowed": False,
            "implicit_runtime_transition_approval_allowed": False,
            "fallback_diff_auditing_allowed": False,
        },
    }


def classify_runtime_diff_state(runtime_diff_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    """Classify runtime diff audit state with explicit non-boolean categories."""

    blocker_set = set(blockers if blockers is not None else _mutation_blockers(runtime_diff_request or {}, None, None, None))
    if "runtime_snapshot_missing" in blocker_set:
        return RUNTIME_SNAPSHOT_MISSING
    if "rollback_audit_compatibility_missing" in blocker_set:
        return ROLLBACK_AUDIT_COMPATIBILITY_MISSING
    if "isolation_audit_compatibility_missing" in blocker_set:
        return ISOLATION_AUDIT_COMPATIBILITY_MISSING
    if "session_audit_compatibility_missing" in blocker_set:
        return SESSION_AUDIT_COMPATIBILITY_MISSING
    if "runtime_transition_unaudited" in blocker_set:
        return RUNTIME_TRANSITION_UNAUDITED
    if "runtime_mutation_prohibited" in blocker_set:
        return RUNTIME_MUTATION_PROHIBITED
    if "runtime_mutation_detected" in blocker_set:
        return RUNTIME_MUTATION_DETECTED
    if blocker_set:
        return RUNTIME_DIFF_AUDIT_BLOCKED
    return RUNTIME_DIFF_AUDIT_SATISFIED


def classify_runtime_drift_state(runtime_diff_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    """Classify runtime drift state with explicit non-boolean categories."""

    blocker_set = set(blockers if blockers is not None else _drift_blockers(runtime_diff_request or {}))
    if "runtime_snapshot_missing" in blocker_set:
        return RUNTIME_SNAPSHOT_MISSING
    if "runtime_transition_unaudited" in blocker_set:
        return RUNTIME_TRANSITION_UNAUDITED
    if "runtime_drift_blocked" in blocker_set:
        return RUNTIME_DRIFT_BLOCKED
    if "runtime_drift_detected" in blocker_set:
        return RUNTIME_DRIFT_DETECTED
    if blocker_set:
        return RUNTIME_DRIFT_BLOCKED
    return RUNTIME_DIFF_AUDIT_SATISFIED


def summarize_runtime_diff_audit_contract(
    runtime_diff_audit_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_5_runtime_diff_auditing_contracts",
    runtime_diff_requests_hash: str | None = None,
    runtime_safety_rollback_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    runtime_session_boundary_contracts_hash: str | None = None,
    request_count: int | None = None,
    safety_rollback_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
) -> dict[str, Any]:
    """Return a deterministic summary envelope for runtime diff audit contracts."""

    contracts = [deepcopy(record) for record in sorted(runtime_diff_audit_contracts, key=_record_sort_key)]
    diff_counts = Counter(record["runtime_diff_audit_status"] for record in contracts)
    drift_counts = Counter(record["runtime_drift_status"] for record in contracts)
    mutation_blockers = Counter(blocker for record in contracts for blocker in record["mutation_blockers"])
    drift_blockers = Counter(blocker for record in contracts for blocker in record["drift_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_diff_auditing_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_diff_request_count": len(contracts) if request_count is None else request_count,
            "runtime_safety_rollback_contract_count": safety_rollback_count,
            "runtime_isolation_contract_count": isolation_count,
            "runtime_session_boundary_contract_count": session_count,
            "runtime_diff_requests_hash": runtime_diff_requests_hash,
            "runtime_safety_rollback_contracts_hash": runtime_safety_rollback_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
            "runtime_session_boundary_contracts_hash": runtime_session_boundary_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_diff_audit_satisfied_count": diff_counts[RUNTIME_DIFF_AUDIT_SATISFIED],
            "runtime_diff_audit_blocked_count": len(contracts) - diff_counts[RUNTIME_DIFF_AUDIT_SATISFIED],
            "runtime_mutation_detected_count": diff_counts[RUNTIME_MUTATION_DETECTED],
            "runtime_mutation_prohibited_count": diff_counts[RUNTIME_MUTATION_PROHIBITED],
            "runtime_drift_detected_count": drift_counts[RUNTIME_DRIFT_DETECTED],
            "runtime_drift_blocked_count": drift_counts[RUNTIME_DRIFT_BLOCKED],
            "runtime_transition_unaudited_count": diff_counts[RUNTIME_TRANSITION_UNAUDITED],
            "runtime_snapshot_missing_count": diff_counts[RUNTIME_SNAPSHOT_MISSING],
            "rollback_audit_compatibility_missing_count": diff_counts[ROLLBACK_AUDIT_COMPATIBILITY_MISSING],
            "isolation_audit_compatibility_missing_count": diff_counts[ISOLATION_AUDIT_COMPATIBILITY_MISSING],
            "session_audit_compatibility_missing_count": diff_counts[SESSION_AUDIT_COMPATIBILITY_MISSING],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_diff_audit_status_counts": {status: diff_counts[status] for status in RUNTIME_DIFF_AUDIT_STATUSES},
        "runtime_drift_status_counts": {status: drift_counts[status] for status in RUNTIME_DRIFT_STATUSES},
        "runtime_mutation_distribution": _distribution(contracts, "runtime_mutation_classification"),
        "runtime_drift_distribution": _distribution(contracts, "runtime_drift_classification"),
        "runtime_transition_audit_distribution": _distribution(contracts, "runtime_transition_trace"),
        "runtime_snapshot_availability_distribution": _snapshot_distribution(contracts),
        "rollback_audit_compatibility_distribution": _distribution(contracts, "runtime_rollback_audit_compatibility"),
        "isolation_audit_compatibility_distribution": _distribution(contracts, "runtime_isolation_audit_compatibility"),
        "session_audit_compatibility_distribution": _distribution(contracts, "runtime_session_audit_compatibility"),
        "runtime_mutation_blocker_distribution": dict(sorted(mutation_blockers.items())),
        "runtime_drift_blocker_distribution": dict(sorted(drift_blockers.items())),
        "phase_2_isolation_audit_compatibility": {
            "isolation_contract_records": isolation_count,
            "requires_runtime_isolation_satisfied": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
        },
        "phase_3_session_audit_compatibility": {
            "session_boundary_contract_records": session_count,
            "requires_session_boundary_satisfied": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
        },
        "phase_4_rollback_audit_compatibility": {
            "runtime_safety_rollback_contract_records": safety_rollback_count,
            "requires_runtime_safety_satisfied": True,
            "requires_runtime_rollback_ready": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
        },
        "runtime_disabled_path_verification": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "silent_runtime_mutations_allowed": False,
            "hidden_runtime_transitions_allowed": False,
            "implicit_runtime_transition_approval_allowed": False,
            "fallback_diff_auditing_allowed": False,
        },
        "runtime_diff_audit_contracts": contracts,
        "safety_confirmations": {
            "runtime_diff_audit_enables_runtime_manifest_consumption": False,
            "runtime_diff_audit_authorizes_production_routing": False,
            "runtime_diff_audit_allows_hidden_runtime_mutations": False,
            "runtime_diff_audit_allows_hidden_runtime_transitions": False,
            "production_runtime_routing_prohibited": True,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
        },
        "metadata": {
            "source": "v3_2_runtime_diff_auditing_contracts",
            "governance_only": True,
            "runtime_diff_audit_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_RUNTIME_DIFF_AUDIT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _mutation_blockers(
    request: dict[str, Any],
    safety: dict[str, Any] | None,
    isolation: dict[str, Any] | None,
    session: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if request.get("runtime_pre_state_snapshot") is None or request.get("runtime_post_state_snapshot") is None:
        blockers.append("runtime_snapshot_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("rollback_audit_compatibility_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("isolation_audit_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("session_audit_compatibility_missing")
    if request.get("runtime_transition_trace") != "runtime_transition_audited":
        blockers.append("runtime_transition_unaudited")
    if request.get("runtime_diff_visibility_state") != "runtime_diff_visible" or request.get("runtime_auditability_state") != "runtime_auditable":
        blockers.append("runtime_transition_unaudited")
    if request.get("runtime_mutation_classification") == RUNTIME_MUTATION_PROHIBITED:
        blockers.append("runtime_mutation_prohibited")
    elif request.get("runtime_mutation_classification") == RUNTIME_MUTATION_DETECTED:
        blockers.append("runtime_mutation_detected")
    return sorted(set(blockers), key=blockers.index)


def _drift_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if request.get("runtime_pre_state_snapshot") is None or request.get("runtime_post_state_snapshot") is None:
        blockers.append("runtime_snapshot_missing")
    if request.get("runtime_transition_trace") != "runtime_transition_audited":
        blockers.append("runtime_transition_unaudited")
    if request.get("runtime_drift_classification") == RUNTIME_DRIFT_BLOCKED:
        blockers.append("runtime_drift_blocked")
    elif request.get("runtime_drift_classification") == RUNTIME_DRIFT_DETECTED:
        blockers.append("runtime_drift_detected")
    elif not _snapshots_match(request.get("runtime_pre_state_snapshot"), request.get("runtime_post_state_snapshot")):
        blockers.append("runtime_drift_detected")
    return sorted(set(blockers), key=blockers.index)


def _records(value: dict[str, Any] | list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get(key, [])]


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


def _snapshot_distribution(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for record in records:
        if record.get("runtime_pre_state_snapshot") is None and record.get("runtime_post_state_snapshot") is None:
            counts["pre_and_post_missing"] += 1
        elif record.get("runtime_pre_state_snapshot") is None:
            counts["pre_missing"] += 1
        elif record.get("runtime_post_state_snapshot") is None:
            counts["post_missing"] += 1
        else:
            counts["pre_and_post_available"] += 1
    return dict(sorted(counts.items()))


def _snapshots_match(pre_state: Any, post_state: Any) -> bool:
    if pre_state is None or post_state is None:
        return False
    return _snapshot_signature(pre_state) == _snapshot_signature(post_state)


def _snapshot_signature(snapshot: Any) -> str | None:
    if snapshot is None:
        return None
    return deterministic_hash(snapshot)


def _audit_trace(diff_status: str, drift_status: str) -> str:
    if diff_status == RUNTIME_DIFF_AUDIT_SATISFIED and drift_status == RUNTIME_DIFF_AUDIT_SATISFIED:
        return "runtime_diff_audit_trace_satisfied"
    return "runtime_diff_audit_trace_blocked"


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
