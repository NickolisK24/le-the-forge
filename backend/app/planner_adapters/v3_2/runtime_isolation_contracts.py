"""Runtime isolation contracts for v3.2 limited experimental runtime governance.

This module layers isolation governance on top of v3.2 Phase 1 entrypoint
contracts. It is pure and deterministic, and it does not enable runtime
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


RUNTIME_ISOLATION_SATISFIED = "runtime_isolation_satisfied"
RUNTIME_ISOLATION_BLOCKED = "runtime_isolation_blocked"
PRODUCTION_ROUTING_CROSSOVER_BLOCKED = "production_routing_crossover_blocked"
MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED = "manifest_consumption_crossover_blocked"
PLANNER_OWNERSHIP_CROSSOVER_BLOCKED = "planner_ownership_crossover_blocked"
RUNTIME_MUTATION_BLOCKED = "runtime_mutation_blocked"
SIDE_EFFECT_BOUNDARY_BLOCKED = "side_effect_boundary_blocked"
ROLLBACK_CONTAINMENT_REQUIRED = "rollback_containment_required"

RUNTIME_ISOLATION_CONTRACT_STATUSES = (
    RUNTIME_ISOLATION_SATISFIED,
    RUNTIME_ISOLATION_BLOCKED,
    PRODUCTION_ROUTING_CROSSOVER_BLOCKED,
    MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED,
    PLANNER_OWNERSHIP_CROSSOVER_BLOCKED,
    RUNTIME_MUTATION_BLOCKED,
    SIDE_EFFECT_BOUNDARY_BLOCKED,
    ROLLBACK_CONTAINMENT_REQUIRED,
)
STABLE_RUNTIME_ISOLATION_CONTRACT_TOKEN = "v3_2_phase_2_runtime_isolation_contracts_token"


def build_runtime_isolation_contract(
    runtime_isolation_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_2_runtime_isolation_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime isolation contracts from explicit inputs."""

    requests = _isolation_requests(runtime_isolation_requests)
    entrypoints = _entrypoint_records(experimental_runtime_entrypoint_contracts)
    entrypoint_by_key = {_trace_key(record): record for record in entrypoints if _trace_key(record)}
    contracts = [
        evaluate_runtime_isolation_contract(
            request,
            entrypoint_contract=entrypoint_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_runtime_isolation_contract({}, entrypoint_contract=None)]
    return summarize_runtime_isolation_contract(
        contracts,
        run_id=run_id,
        runtime_isolation_requests_hash=_source_hash(runtime_isolation_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
    )


def evaluate_runtime_isolation_contract(
    runtime_isolation_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one isolation request against a Phase 1 entrypoint contract."""

    request = deepcopy(runtime_isolation_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    blockers = _blockers(request, entrypoint)
    status = classify_runtime_isolation_state(request, blockers=blockers)
    manifest_id = request.get("manifest_id") or (entrypoint or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (entrypoint or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "token": STABLE_RUNTIME_ISOLATION_CONTRACT_TOKEN,
    }
    return {
        "runtime_isolation_contract_id": f"v3_2_runtime_isolation_contract_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "entrypoint_contract_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "entrypoint_authorization_state": (entrypoint or {}).get("runtime_authorization_state"),
        "entrypoint_production_runtime_classification": (entrypoint or {}).get("production_runtime_classification", PRODUCTION_RUNTIME_PROHIBITED),
        "runtime_isolation_boundary_state": request.get("runtime_isolation_boundary_state"),
        "production_routing_separation_state": request.get("production_routing_separation_state"),
        "manifest_consumption_separation_state": request.get("manifest_consumption_separation_state"),
        "planner_ownership_separation_state": request.get("planner_ownership_separation_state"),
        "runtime_mutation_prohibition_state": request.get("runtime_mutation_prohibition_state"),
        "experimental_only_execution_scope": request.get("experimental_only_execution_scope"),
        "runtime_side_effect_prohibition_state": request.get("runtime_side_effect_prohibition_state"),
        "rollback_containment_state": request.get("rollback_containment_state"),
        "isolation_blocker_state": "blocked" if blockers else "unblocked_for_contract_only",
        "isolation_trace_classification": _trace_classification(status),
        "runtime_isolation_status": status,
        "blockers": blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "isolation_contract_authorizes_runtime_consumption": False,
        "isolation_contract_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_isolation_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_runtime_activation_allowed": False,
            "fallback_isolation_allowed": False,
            "implicit_manifest_consumption_allowed": False,
        },
    }


def classify_runtime_isolation_state(
    runtime_isolation_request: dict[str, Any],
    *,
    blockers: list[str] | None = None,
) -> str:
    """Classify isolation state with explicit non-boolean categories."""

    blocker_set = set(blockers if blockers is not None else _blockers(runtime_isolation_request or {}, None))
    if "production_routing_crossover" in blocker_set or "production_routing_authorized" in blocker_set:
        return PRODUCTION_ROUTING_CROSSOVER_BLOCKED
    if "manifest_consumption_crossover" in blocker_set or "implicit_manifest_consumption" in blocker_set:
        return MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED
    if "planner_ownership_crossover" in blocker_set:
        return PLANNER_OWNERSHIP_CROSSOVER_BLOCKED
    if "runtime_mutation_requested" in blocker_set:
        return RUNTIME_MUTATION_BLOCKED
    if "side_effect_boundary_failed" in blocker_set:
        return SIDE_EFFECT_BOUNDARY_BLOCKED
    if "rollback_containment_missing" in blocker_set or "rollback_containment_required" in blocker_set:
        return ROLLBACK_CONTAINMENT_REQUIRED
    if blocker_set:
        return RUNTIME_ISOLATION_BLOCKED
    return RUNTIME_ISOLATION_SATISFIED


def summarize_runtime_isolation_contract(
    runtime_isolation_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_2_runtime_isolation_contracts",
    runtime_isolation_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
) -> dict[str, Any]:
    """Return a deterministic summary envelope for isolation contracts."""

    contracts = [deepcopy(record) for record in sorted(runtime_isolation_contracts, key=_record_sort_key)]
    counts = Counter(record["runtime_isolation_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["blockers"])
    boundary_counts = Counter(record.get("runtime_isolation_boundary_state") or "missing" for record in contracts)
    routing_counts = Counter(record.get("production_routing_separation_state") or "missing" for record in contracts)
    manifest_counts = Counter(record.get("manifest_consumption_separation_state") or "missing" for record in contracts)
    planner_counts = Counter(record.get("planner_ownership_separation_state") or "missing" for record in contracts)
    mutation_counts = Counter(record.get("runtime_mutation_prohibition_state") or "missing" for record in contracts)
    side_effect_counts = Counter(record.get("runtime_side_effect_prohibition_state") or "missing" for record in contracts)
    rollback_counts = Counter(record.get("rollback_containment_state") or "missing" for record in contracts)
    envelope = {
        "schema_version": "v3_2.runtime_isolation_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_isolation_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "runtime_isolation_requests_hash": runtime_isolation_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_isolation_satisfied_count": counts[RUNTIME_ISOLATION_SATISFIED],
            "runtime_isolation_blocked_count": len(contracts) - counts[RUNTIME_ISOLATION_SATISFIED],
            "production_routing_crossover_blocked_count": counts[PRODUCTION_ROUTING_CROSSOVER_BLOCKED],
            "manifest_consumption_crossover_blocked_count": counts[MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED],
            "planner_ownership_crossover_blocked_count": counts[PLANNER_OWNERSHIP_CROSSOVER_BLOCKED],
            "runtime_mutation_blocked_count": counts[RUNTIME_MUTATION_BLOCKED],
            "side_effect_boundary_blocked_count": counts[SIDE_EFFECT_BOUNDARY_BLOCKED],
            "rollback_containment_required_count": counts[ROLLBACK_CONTAINMENT_REQUIRED],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_isolation_status_counts": {
            status: counts[status]
            for status in RUNTIME_ISOLATION_CONTRACT_STATUSES
        },
        "isolation_state_distribution": dict(sorted(boundary_counts.items())),
        "production_routing_crossover_distribution": dict(sorted(routing_counts.items())),
        "manifest_consumption_crossover_distribution": dict(sorted(manifest_counts.items())),
        "planner_ownership_crossover_distribution": dict(sorted(planner_counts.items())),
        "runtime_mutation_blocker_distribution": dict(sorted(mutation_counts.items())),
        "side_effect_blocker_distribution": dict(sorted(side_effect_counts.items())),
        "rollback_containment_distribution": dict(sorted(rollback_counts.items())),
        "blocker_distribution": dict(sorted(blocker_counts.items())),
        "phase_1_entrypoint_compatibility": {
            "entrypoint_contract_records": entrypoint_count,
            "requires_experimental_runtime_eligible": True,
            "runtime_manifest_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_runtime_prohibited": True,
            "explicit_opt_in_preserved": True,
            "runtime_disabled_states_remain_visible": True,
            "rollback_required_states_remain_visible": True,
        },
        "runtime_disabled_path_verification": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "silent_runtime_activation_allowed": False,
            "implicit_manifest_consumption_allowed": False,
            "fallback_isolation_allowed": False,
        },
        "runtime_isolation_contracts": contracts,
        "safety_confirmations": {
            "isolation_contract_enables_runtime_manifest_consumption": False,
            "isolation_contract_authorizes_production_routing": False,
            "isolation_contract_mutates_planner_ownership": False,
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
            "source": "v3_2_runtime_isolation_contracts",
            "governance_only": True,
            "runtime_isolation_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_RUNTIME_ISOLATION_CONTRACT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if entrypoint is None:
        blockers.append("missing_phase_1_entrypoint_authorization_context")
    else:
        if entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
            blockers.append("phase_1_entrypoint_not_eligible")
        if entrypoint.get("runtime_manifest_consumption_enabled") is True:
            blockers.append("runtime_manifest_consumption_enabled")
        if entrypoint.get("production_routing_authorized") is True:
            blockers.append("production_routing_authorized")
        if entrypoint.get("production_runtime_classification") != PRODUCTION_RUNTIME_PROHIBITED:
            blockers.append("production_runtime_not_prohibited")
        if entrypoint.get("explicit_experimental_runtime_opt_in") is not True:
            blockers.append("explicit_experimental_opt_in_missing")
        if entrypoint.get("runtime_authorization_state") != NON_PRODUCTION_AUTHORIZATION_STATE:
            blockers.append("runtime_authorization_invalid")
    if not request:
        blockers.append("missing_isolation_inputs")
        return blockers
    if request.get("runtime_isolation_boundary_state") != "isolation_boundary_satisfied":
        blockers.append("isolation_boundary_missing")
    if request.get("production_routing_separation_state") != "production_routing_separated" or request.get("production_routing_crossover") is True:
        blockers.append("production_routing_crossover")
    if _manifest_consumption_blocked(request):
        blockers.append("manifest_consumption_crossover")
    if request.get("planner_ownership_separation_state") != "planner_ownership_separated" or request.get("planner_ownership_mutation_requested") is True:
        blockers.append("planner_ownership_crossover")
    if request.get("runtime_mutation_prohibition_state") != "runtime_mutation_prohibited" or request.get("runtime_mutation_requested") is True:
        blockers.append("runtime_mutation_requested")
    if _side_effect_blocked(request):
        blockers.append("side_effect_boundary_failed")
    if request.get("rollback_containment_state") != "rollback_contained":
        blockers.append("rollback_containment_missing")
    if request.get("experimental_only_execution_scope") != "experimental_only":
        blockers.append("experimental_only_scope_missing")
    return sorted(set(blockers), key=blockers.index)


def _manifest_consumption_blocked(request: dict[str, Any]) -> bool:
    if request.get("manifest_consumption_separation_state") != "manifest_consumption_separated":
        return True
    if request.get("manifest_consumption_crossover") is True:
        return not (
            request.get("manifest_consumption_scope") == "experimental_only"
            and request.get("manifest_authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
            and request.get("implicit_manifest_consumption") is False
        )
    return request.get("implicit_manifest_consumption") is True


def _side_effect_blocked(request: dict[str, Any]) -> bool:
    if request.get("runtime_side_effect_prohibition_state") == "side_effects_prohibited":
        return False
    return not (
        request.get("runtime_side_effect_prohibition_state") == "side_effects_isolated_reversible_non_production"
        and request.get("side_effects_isolated") is True
        and request.get("side_effects_reversible") is True
        and request.get("side_effects_non_production") is True
    )


def _isolation_requests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_isolation_requests", [])]


def _entrypoint_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get("runtime_entrypoint_contracts", [])]


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
    if status == RUNTIME_ISOLATION_SATISFIED:
        return "runtime_isolation_trace_satisfied"
    if status == ROLLBACK_CONTAINMENT_REQUIRED:
        return "runtime_isolation_trace_rollback_required"
    if status == PRODUCTION_ROUTING_CROSSOVER_BLOCKED:
        return "runtime_isolation_trace_production_crossover_blocked"
    return "runtime_isolation_trace_blocked"


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
