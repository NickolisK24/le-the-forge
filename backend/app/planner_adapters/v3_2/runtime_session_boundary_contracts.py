"""Runtime session boundary contracts for v3.2 governance.

This module layers session lifecycle governance on top of v3.2 entrypoint and
isolation contracts. It is pure, deterministic, and does not enable runtime
manifest consumption or production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.planner_adapters.v3_1.approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash
from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import (
    EXPERIMENTAL_RUNTIME_ELIGIBLE,
    PRODUCTION_RUNTIME_PROHIBITED,
)
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED


RUNTIME_SESSION_BOUNDARY_SATISFIED = "runtime_session_boundary_satisfied"
RUNTIME_SESSION_BOUNDARY_BLOCKED = "runtime_session_boundary_blocked"
SESSION_INITIALIZATION_BLOCKED = "session_initialization_blocked"
SESSION_AUTHORIZATION_CONTEXT_MISSING = "session_authorization_context_missing"
SESSION_ISOLATION_CONTEXT_MISSING = "session_isolation_context_missing"
SESSION_OWNERSHIP_CROSSOVER_BLOCKED = "session_ownership_crossover_blocked"
SESSION_MUTATION_BLOCKED = "session_mutation_blocked"
SESSION_REUSE_BLOCKED = "session_reuse_blocked"
SESSION_LEAKAGE_BLOCKED = "session_leakage_blocked"
SESSION_TERMINATION_REQUIRED = "session_termination_required"
SESSION_ROLLBACK_CONTAINMENT_REQUIRED = "session_rollback_containment_required"

RUNTIME_SESSION_BOUNDARY_CONTRACT_STATUSES = (
    RUNTIME_SESSION_BOUNDARY_SATISFIED,
    RUNTIME_SESSION_BOUNDARY_BLOCKED,
    SESSION_INITIALIZATION_BLOCKED,
    SESSION_AUTHORIZATION_CONTEXT_MISSING,
    SESSION_ISOLATION_CONTEXT_MISSING,
    SESSION_OWNERSHIP_CROSSOVER_BLOCKED,
    SESSION_MUTATION_BLOCKED,
    SESSION_REUSE_BLOCKED,
    SESSION_LEAKAGE_BLOCKED,
    SESSION_TERMINATION_REQUIRED,
    SESSION_ROLLBACK_CONTAINMENT_REQUIRED,
)
STABLE_RUNTIME_SESSION_BOUNDARY_TOKEN = "v3_2_phase_3_runtime_session_boundary_contracts_token"


def build_runtime_session_boundary_contract(
    runtime_session_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_3_runtime_session_boundary_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime session boundary contracts."""

    requests = _session_requests(runtime_session_requests)
    entrypoints = _entrypoint_records(experimental_runtime_entrypoint_contracts)
    isolations = _isolation_records(runtime_isolation_contracts)
    entrypoint_by_key = {_trace_key(record): record for record in entrypoints if _trace_key(record)}
    isolation_by_key = {_trace_key(record): record for record in isolations if _trace_key(record)}
    contracts = [
        evaluate_runtime_session_boundary_contract(
            request,
            entrypoint_contract=entrypoint_by_key.get(_trace_key(request)),
            isolation_contract=isolation_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_runtime_session_boundary_contract({}, entrypoint_contract=None, isolation_contract=None)]
    return summarize_runtime_session_boundary_contract(
        contracts,
        run_id=run_id,
        runtime_session_requests_hash=_source_hash(runtime_session_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
    )


def evaluate_runtime_session_boundary_contract(
    runtime_session_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one session request against entrypoint and isolation contracts."""

    request = deepcopy(runtime_session_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    blockers = _blockers(request, entrypoint, isolation)
    status = classify_runtime_session_boundary_state(request, blockers=blockers)
    manifest_id = request.get("manifest_id") or (entrypoint or {}).get("manifest_id") or (isolation or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (entrypoint or {}).get("fixture_set_id") or (isolation or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "token": STABLE_RUNTIME_SESSION_BOUNDARY_TOKEN,
    }
    return {
        "runtime_session_boundary_contract_id": f"v3_2_runtime_session_boundary_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "entrypoint_contract_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "entrypoint_authorization_state": (entrypoint or {}).get("runtime_authorization_state"),
        "isolation_contract_status": (isolation or {}).get("runtime_isolation_status"),
        "session_initialization_state": request.get("session_initialization_state"),
        "session_authorization_context": request.get("session_authorization_context"),
        "session_isolation_context": request.get("session_isolation_context"),
        "session_lifecycle_state": request.get("session_lifecycle_state"),
        "session_ownership_state": request.get("session_ownership_state"),
        "session_mutation_prohibition_state": request.get("session_mutation_prohibition_state"),
        "session_reuse_prohibition_state": request.get("session_reuse_prohibition_state"),
        "session_leakage_prohibition_state": request.get("session_leakage_prohibition_state"),
        "session_termination_requirement_state": request.get("session_termination_requirement_state"),
        "rollback_containment_state": request.get("rollback_containment_state"),
        "session_blocker_state": "blocked" if blockers else "unblocked_for_contract_only",
        "session_trace_classification": _trace_classification(status),
        "runtime_session_boundary_status": status,
        "blockers": blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "session_boundary_authorizes_runtime_consumption": False,
        "session_boundary_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_session_boundary_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_runtime_session_activation_allowed": False,
            "implicit_session_reuse_allowed": False,
            "fallback_session_behavior_allowed": False,
        },
    }


def classify_runtime_session_boundary_state(
    runtime_session_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    """Classify session boundary state with explicit categories."""

    blocker_set = set(blockers if blockers is not None else _blockers(runtime_session_request or {}, None, None))
    if "session_authorization_context_missing" in blocker_set or "phase_1_entrypoint_authorization_missing" in blocker_set:
        return SESSION_AUTHORIZATION_CONTEXT_MISSING
    if "session_isolation_context_missing" in blocker_set or "phase_2_isolation_context_missing" in blocker_set:
        return SESSION_ISOLATION_CONTEXT_MISSING
    if "session_initialization_missing" in blocker_set or "explicit_experimental_opt_in_missing" in blocker_set:
        return SESSION_INITIALIZATION_BLOCKED
    if "session_ownership_crossover" in blocker_set:
        return SESSION_OWNERSHIP_CROSSOVER_BLOCKED
    if "session_mutation_requested" in blocker_set:
        return SESSION_MUTATION_BLOCKED
    if "session_reuse_not_scoped" in blocker_set:
        return SESSION_REUSE_BLOCKED
    if "session_state_leakage" in blocker_set:
        return SESSION_LEAKAGE_BLOCKED
    if "session_termination_missing" in blocker_set:
        return SESSION_TERMINATION_REQUIRED
    if "rollback_containment_missing" in blocker_set:
        return SESSION_ROLLBACK_CONTAINMENT_REQUIRED
    if blocker_set:
        return RUNTIME_SESSION_BOUNDARY_BLOCKED
    return RUNTIME_SESSION_BOUNDARY_SATISFIED


def summarize_runtime_session_boundary_contract(
    runtime_session_boundary_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_3_runtime_session_boundary_contracts",
    runtime_session_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
) -> dict[str, Any]:
    """Return a deterministic summary envelope for session boundary contracts."""

    contracts = [deepcopy(record) for record in sorted(runtime_session_boundary_contracts, key=_record_sort_key)]
    counts = Counter(record["runtime_session_boundary_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_session_boundary_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_session_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "isolation_contract_count": isolation_count,
            "runtime_session_requests_hash": runtime_session_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_session_boundary_satisfied_count": counts[RUNTIME_SESSION_BOUNDARY_SATISFIED],
            "runtime_session_boundary_blocked_count": len(contracts) - counts[RUNTIME_SESSION_BOUNDARY_SATISFIED],
            "session_initialization_blocked_count": counts[SESSION_INITIALIZATION_BLOCKED],
            "session_authorization_context_missing_count": counts[SESSION_AUTHORIZATION_CONTEXT_MISSING],
            "session_isolation_context_missing_count": counts[SESSION_ISOLATION_CONTEXT_MISSING],
            "session_ownership_crossover_blocked_count": counts[SESSION_OWNERSHIP_CROSSOVER_BLOCKED],
            "session_mutation_blocked_count": counts[SESSION_MUTATION_BLOCKED],
            "session_reuse_blocked_count": counts[SESSION_REUSE_BLOCKED],
            "session_leakage_blocked_count": counts[SESSION_LEAKAGE_BLOCKED],
            "session_termination_required_count": counts[SESSION_TERMINATION_REQUIRED],
            "session_rollback_containment_required_count": counts[SESSION_ROLLBACK_CONTAINMENT_REQUIRED],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_session_boundary_status_counts": {
            status: counts[status]
            for status in RUNTIME_SESSION_BOUNDARY_CONTRACT_STATUSES
        },
        "session_boundary_state_distribution": _distribution(contracts, "session_lifecycle_state"),
        "session_initialization_blocker_distribution": _distribution(contracts, "session_initialization_state"),
        "authorization_context_distribution": _distribution(contracts, "session_authorization_context"),
        "isolation_context_distribution": _distribution(contracts, "session_isolation_context"),
        "ownership_crossover_distribution": _distribution(contracts, "session_ownership_state"),
        "mutation_blocker_distribution": _distribution(contracts, "session_mutation_prohibition_state"),
        "reuse_blocker_distribution": _distribution(contracts, "session_reuse_prohibition_state"),
        "leakage_blocker_distribution": _distribution(contracts, "session_leakage_prohibition_state"),
        "termination_required_distribution": _distribution(contracts, "session_termination_requirement_state"),
        "rollback_containment_distribution": _distribution(contracts, "rollback_containment_state"),
        "blocker_distribution": dict(sorted(blocker_counts.items())),
        "phase_1_entrypoint_compatibility": {
            "entrypoint_contract_records": entrypoint_count,
            "requires_experimental_runtime_eligible": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_runtime_prohibited": True,
            "explicit_opt_in_preserved": True,
        },
        "phase_2_isolation_compatibility": {
            "isolation_contract_records": isolation_count,
            "requires_runtime_isolation_satisfied": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
            "runtime_isolation_preserved": True,
        },
        "runtime_disabled_path_verification": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "silent_runtime_session_activation_allowed": False,
            "implicit_session_reuse_allowed": False,
            "fallback_session_behavior_allowed": False,
        },
        "runtime_session_boundary_contracts": contracts,
        "safety_confirmations": {
            "session_boundary_enables_runtime_manifest_consumption": False,
            "session_boundary_authorizes_production_routing": False,
            "session_boundary_mutates_planner_ownership": False,
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
            "source": "v3_2_runtime_session_boundary_contracts",
            "governance_only": True,
            "runtime_session_boundary_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_RUNTIME_SESSION_BOUNDARY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if entrypoint is None:
        blockers.append("phase_1_entrypoint_authorization_missing")
    else:
        if entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
            blockers.append("phase_1_entrypoint_not_eligible")
        if entrypoint.get("runtime_authorization_state") != NON_PRODUCTION_AUTHORIZATION_STATE:
            blockers.append("phase_1_entrypoint_authorization_missing")
        if entrypoint.get("explicit_experimental_runtime_opt_in") is not True:
            blockers.append("explicit_experimental_opt_in_missing")
    if isolation is None:
        blockers.append("phase_2_isolation_context_missing")
    else:
        if isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
            blockers.append("phase_2_isolation_not_satisfied")
    if not request:
        blockers.append("session_initialization_missing")
        return blockers
    if request.get("session_initialization_state") != "session_initialization_explicit":
        blockers.append("session_initialization_missing")
    if request.get("explicit_experimental_runtime_opt_in") is not True:
        blockers.append("explicit_experimental_opt_in_missing")
    if request.get("session_authorization_context") != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("session_authorization_context_missing")
    if request.get("session_isolation_context") != "runtime_isolated":
        blockers.append("session_isolation_context_missing")
    if request.get("session_ownership_state") != "session_ownership_isolated" or request.get("session_ownership_crossover") is True:
        blockers.append("session_ownership_crossover")
    if request.get("session_mutation_prohibition_state") != "session_mutation_prohibited" or request.get("session_mutates_production_planner") is True:
        blockers.append("session_mutation_requested")
    if request.get("session_reuse_prohibition_state") != "session_reuse_prohibited":
        if not (
            request.get("session_reuse_prohibition_state") == "session_reuse_scoped_deterministic_non_production"
            and request.get("session_reuse_scope") == "single_fixture_set"
            and request.get("session_reuse_deterministic") is True
            and request.get("session_reuse_non_production") is True
        ):
            blockers.append("session_reuse_not_scoped")
    if request.get("session_leakage_prohibition_state") != "session_leakage_prohibited" or request.get("session_state_leakage_detected") is True:
        blockers.append("session_state_leakage")
    if request.get("session_termination_requirement_state") != "session_termination_required_and_explicit":
        blockers.append("session_termination_missing")
    if request.get("rollback_containment_state") != "rollback_contained":
        blockers.append("rollback_containment_missing")
    return sorted(set(blockers), key=blockers.index)


def _session_requests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_session_requests", [])]


def _entrypoint_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_entrypoint_contracts", [])]


def _isolation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_isolation_contracts", [])]


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


def _distribution(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(record.get(key) or "missing" for record in records).items()))


def _trace_classification(status: str) -> str:
    if status == RUNTIME_SESSION_BOUNDARY_SATISFIED:
        return "runtime_session_boundary_trace_satisfied"
    if status == SESSION_TERMINATION_REQUIRED:
        return "runtime_session_boundary_trace_termination_required"
    if status == SESSION_ROLLBACK_CONTAINMENT_REQUIRED:
        return "runtime_session_boundary_trace_rollback_required"
    return "runtime_session_boundary_trace_blocked"


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
