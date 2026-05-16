"""Runtime safety and rollback contracts for v3.2 governance.

This layer evaluates explicit safety and rollback readiness on top of v3.2
entrypoint, isolation, and session boundary contracts. It is governance-only
and does not enable runtime manifest consumption or production routing.
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
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED


RUNTIME_SAFETY_SATISFIED = "runtime_safety_satisfied"
RUNTIME_SAFETY_BLOCKED = "runtime_safety_blocked"
RUNTIME_ROLLBACK_READY = "runtime_rollback_ready"
RUNTIME_ROLLBACK_BLOCKED = "runtime_rollback_blocked"
ROLLBACK_CONTAINMENT_REQUIRED = "rollback_containment_required"
ROLLBACK_TRIGGER_MISSING = "rollback_trigger_missing"
ROLLBACK_REVERSIBILITY_MISSING = "rollback_reversibility_missing"
UNSAFE_SIDE_EFFECT_BLOCKED = "unsafe_side_effect_blocked"
PRODUCTION_IMPACT_BLOCKED = "production_impact_blocked"
ENTRYPOINT_COMPATIBILITY_MISSING = "entrypoint_compatibility_missing"
ISOLATION_COMPATIBILITY_MISSING = "isolation_compatibility_missing"
SESSION_BOUNDARY_COMPATIBILITY_MISSING = "session_boundary_compatibility_missing"

RUNTIME_SAFETY_STATUSES = (
    RUNTIME_SAFETY_SATISFIED,
    RUNTIME_SAFETY_BLOCKED,
    UNSAFE_SIDE_EFFECT_BLOCKED,
    PRODUCTION_IMPACT_BLOCKED,
    ENTRYPOINT_COMPATIBILITY_MISSING,
    ISOLATION_COMPATIBILITY_MISSING,
    SESSION_BOUNDARY_COMPATIBILITY_MISSING,
)
RUNTIME_ROLLBACK_STATUSES = (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_ROLLBACK_BLOCKED,
    ROLLBACK_CONTAINMENT_REQUIRED,
    ROLLBACK_TRIGGER_MISSING,
    ROLLBACK_REVERSIBILITY_MISSING,
)
STABLE_RUNTIME_SAFETY_ROLLBACK_TOKEN = "v3_2_phase_4_runtime_safety_rollback_contracts_token"


def build_runtime_safety_rollback_contract(
    runtime_safety_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_4_runtime_safety_rollback_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime safety and rollback contracts."""

    requests = _records(runtime_safety_requests, "runtime_safety_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    entrypoint_by_key = {_trace_key(record): record for record in entrypoints if _trace_key(record)}
    isolation_by_key = {_trace_key(record): record for record in isolations if _trace_key(record)}
    session_by_key = {_trace_key(record): record for record in sessions if _trace_key(record)}
    contracts = [
        evaluate_runtime_safety_rollback_contract(
            request,
            entrypoint_contract=entrypoint_by_key.get(_trace_key(request)),
            isolation_contract=isolation_by_key.get(_trace_key(request)),
            session_boundary_contract=session_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_runtime_safety_rollback_contract({}, entrypoint_contract=None, isolation_contract=None, session_boundary_contract=None)]
    return summarize_runtime_safety_rollback_contract(
        contracts,
        run_id=run_id,
        runtime_safety_requests_hash=_source_hash(runtime_safety_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        runtime_session_boundary_contracts_hash=_source_hash(runtime_session_boundary_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
    )


def evaluate_runtime_safety_rollback_contract(
    runtime_safety_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one safety and rollback request."""

    request = deepcopy(runtime_safety_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    session = deepcopy(session_boundary_contract) if session_boundary_contract else None
    safety_blockers = _safety_blockers(request, entrypoint, isolation, session)
    rollback_blockers = _rollback_blockers(request)
    safety_status = classify_runtime_safety_state(request, blockers=safety_blockers)
    rollback_status = classify_runtime_rollback_state(request, blockers=rollback_blockers)
    manifest_id = request.get("manifest_id") or (entrypoint or {}).get("manifest_id") or (isolation or {}).get("manifest_id") or (session or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (entrypoint or {}).get("fixture_set_id") or (isolation or {}).get("fixture_set_id") or (session or {}).get("fixture_set_id")
    seed = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "safety": safety_status, "rollback": rollback_status, "token": STABLE_RUNTIME_SAFETY_ROLLBACK_TOKEN}
    return {
        "runtime_safety_rollback_contract_id": f"v3_2_runtime_safety_rollback_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "entrypoint_contract_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "isolation_contract_status": (isolation or {}).get("runtime_isolation_status"),
        "session_boundary_contract_status": (session or {}).get("runtime_session_boundary_status"),
        "runtime_safety_state": request.get("runtime_safety_state"),
        "rollback_readiness_state": request.get("rollback_readiness_state"),
        "rollback_containment_state": request.get("rollback_containment_state"),
        "rollback_trigger_state": request.get("rollback_trigger_state"),
        "rollback_reversibility_state": request.get("rollback_reversibility_state"),
        "unsafe_side_effect_prohibition_state": request.get("unsafe_side_effect_prohibition_state"),
        "production_impact_prohibition_state": request.get("production_impact_prohibition_state"),
        "session_rollback_compatibility_state": request.get("session_rollback_compatibility_state"),
        "isolation_rollback_compatibility_state": request.get("isolation_rollback_compatibility_state"),
        "entrypoint_rollback_compatibility_state": request.get("entrypoint_rollback_compatibility_state"),
        "runtime_safety_status": safety_status,
        "runtime_rollback_status": rollback_status,
        "safety_blockers": safety_blockers,
        "rollback_blockers": rollback_blockers,
        "safety_blocker_state": "blocked" if safety_blockers else "unblocked_for_contract_only",
        "rollback_blocker_state": "blocked" if rollback_blockers else "ready_for_contract_only",
        "safety_trace_classification": _safety_trace(safety_status),
        "rollback_trace_classification": _rollback_trace(rollback_status),
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "safety_contract_authorizes_runtime_consumption": False,
        "safety_contract_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_safety_rollback_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_runtime_safety_approval_allowed": False,
            "implicit_rollback_readiness_allowed": False,
            "fallback_rollback_logic_allowed": False,
            "irreversible_side_effects_allowed": False,
        },
    }


def classify_runtime_safety_state(runtime_safety_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _safety_blockers(runtime_safety_request or {}, None, None, None))
    if "entrypoint_compatibility_missing" in blocker_set:
        return ENTRYPOINT_COMPATIBILITY_MISSING
    if "isolation_compatibility_missing" in blocker_set:
        return ISOLATION_COMPATIBILITY_MISSING
    if "session_boundary_compatibility_missing" in blocker_set:
        return SESSION_BOUNDARY_COMPATIBILITY_MISSING
    if "unsafe_side_effect" in blocker_set:
        return UNSAFE_SIDE_EFFECT_BLOCKED
    if "production_impact" in blocker_set:
        return PRODUCTION_IMPACT_BLOCKED
    if blocker_set:
        return RUNTIME_SAFETY_BLOCKED
    return RUNTIME_SAFETY_SATISFIED


def classify_runtime_rollback_state(runtime_safety_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _rollback_blockers(runtime_safety_request or {}))
    if "rollback_containment_missing" in blocker_set:
        return ROLLBACK_CONTAINMENT_REQUIRED
    if "rollback_trigger_missing" in blocker_set:
        return ROLLBACK_TRIGGER_MISSING
    if "rollback_reversibility_missing" in blocker_set:
        return ROLLBACK_REVERSIBILITY_MISSING
    if blocker_set:
        return RUNTIME_ROLLBACK_BLOCKED
    return RUNTIME_ROLLBACK_READY


def summarize_runtime_safety_rollback_contract(
    runtime_safety_rollback_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_4_runtime_safety_rollback_contracts",
    runtime_safety_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    runtime_session_boundary_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(runtime_safety_rollback_contracts, key=_record_sort_key)]
    safety_counts = Counter(record["runtime_safety_status"] for record in contracts)
    rollback_counts = Counter(record["runtime_rollback_status"] for record in contracts)
    safety_blockers = Counter(blocker for record in contracts for blocker in record["safety_blockers"])
    rollback_blockers = Counter(blocker for record in contracts for blocker in record["rollback_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_safety_rollback_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_safety_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "isolation_contract_count": isolation_count,
            "session_boundary_contract_count": session_count,
            "runtime_safety_requests_hash": runtime_safety_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
            "runtime_session_boundary_contracts_hash": runtime_session_boundary_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_safety_satisfied_count": safety_counts[RUNTIME_SAFETY_SATISFIED],
            "runtime_safety_blocked_count": len(contracts) - safety_counts[RUNTIME_SAFETY_SATISFIED],
            "runtime_rollback_ready_count": rollback_counts[RUNTIME_ROLLBACK_READY],
            "runtime_rollback_blocked_count": len(contracts) - rollback_counts[RUNTIME_ROLLBACK_READY],
            "unsafe_side_effect_blocked_count": safety_counts[UNSAFE_SIDE_EFFECT_BLOCKED],
            "production_impact_blocked_count": safety_counts[PRODUCTION_IMPACT_BLOCKED],
            "rollback_containment_required_count": rollback_counts[ROLLBACK_CONTAINMENT_REQUIRED],
            "rollback_trigger_missing_count": rollback_counts[ROLLBACK_TRIGGER_MISSING],
            "rollback_reversibility_missing_count": rollback_counts[ROLLBACK_REVERSIBILITY_MISSING],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_safety_status_counts": {status: safety_counts[status] for status in RUNTIME_SAFETY_STATUSES},
        "runtime_rollback_status_counts": {status: rollback_counts[status] for status in RUNTIME_ROLLBACK_STATUSES},
        "runtime_safety_state_distribution": _distribution(contracts, "runtime_safety_state"),
        "rollback_readiness_state_distribution": _distribution(contracts, "rollback_readiness_state"),
        "rollback_containment_distribution": _distribution(contracts, "rollback_containment_state"),
        "rollback_trigger_distribution": _distribution(contracts, "rollback_trigger_state"),
        "rollback_reversibility_distribution": _distribution(contracts, "rollback_reversibility_state"),
        "unsafe_side_effect_blocker_distribution": _distribution(contracts, "unsafe_side_effect_prohibition_state"),
        "production_impact_blocker_distribution": _distribution(contracts, "production_impact_prohibition_state"),
        "safety_blocker_distribution": dict(sorted(safety_blockers.items())),
        "rollback_blocker_distribution": dict(sorted(rollback_blockers.items())),
        "phase_1_entrypoint_compatibility": {"entrypoint_contract_records": entrypoint_count, "requires_experimental_runtime_eligible": True, "production_runtime_prohibited": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_2_isolation_compatibility": {"isolation_contract_records": isolation_count, "requires_runtime_isolation_satisfied": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_3_session_boundary_compatibility": {"session_boundary_contract_records": session_count, "requires_session_boundary_satisfied": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "silent_runtime_safety_approval_allowed": False, "implicit_rollback_readiness_allowed": False, "fallback_rollback_logic_allowed": False},
        "runtime_safety_rollback_contracts": contracts,
        "safety_confirmations": {"safety_contract_enables_runtime_manifest_consumption": False, "safety_contract_authorizes_production_routing": False, "safety_contract_allows_irreversible_side_effects": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_runtime_safety_rollback_contracts", "governance_only": True, "runtime_safety_rollback_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_RUNTIME_SAFETY_ROLLBACK_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _safety_blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None, session: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("entrypoint_compatibility_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("isolation_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("session_boundary_compatibility_missing")
    if not request or request.get("runtime_safety_state") != "runtime_safety_explicitly_satisfied":
        blockers.append("runtime_safety_not_satisfied")
    if request.get("unsafe_side_effect_prohibition_state") != "unsafe_side_effects_prohibited" or request.get("unsafe_side_effect_detected") is True:
        blockers.append("unsafe_side_effect")
    if request.get("production_impact_prohibition_state") != "production_impact_prohibited" or request.get("production_impact_detected") is True:
        blockers.append("production_impact")
    return sorted(set(blockers), key=blockers.index)


def _rollback_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request or request.get("rollback_readiness_state") != "rollback_readiness_explicitly_ready":
        blockers.append("rollback_readiness_not_satisfied")
    if request.get("rollback_containment_state") != "rollback_contained":
        blockers.append("rollback_containment_missing")
    if request.get("rollback_trigger_state") != "rollback_trigger_explicit":
        blockers.append("rollback_trigger_missing")
    if request.get("rollback_reversibility_state") != "rollback_reversible":
        blockers.append("rollback_reversibility_missing")
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


def _safety_trace(status: str) -> str:
    return "runtime_safety_trace_satisfied" if status == RUNTIME_SAFETY_SATISFIED else "runtime_safety_trace_blocked"


def _rollback_trace(status: str) -> str:
    return "runtime_rollback_trace_ready" if status == RUNTIME_ROLLBACK_READY else "runtime_rollback_trace_blocked"


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
