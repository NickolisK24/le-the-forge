"""Deterministic governance consumption orchestration contracts for v3.5 planning."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_blocker_models import (
    OrchestrationBlockerModel,
    default_orchestration_blockers,
    export_orchestration_blockers,
    hash_orchestration_blockers,
)
from .orchestration_boundary_models import (
    OrchestrationBoundaryModel,
    default_orchestration_boundary_model,
    export_orchestration_boundary,
    hash_orchestration_boundary,
)
from .orchestration_visibility_models import (
    OrchestrationVisibilityModel,
    default_orchestration_visibility_model,
    export_orchestration_visibility,
    hash_orchestration_visibility,
)


GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING = (
    "governance_consumption_ready_for_orchestration_planning"
)
BLOCKED_MISSING_ORCHESTRATION_IDENTITY = "blocked_missing_orchestration_identity"
BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT = "blocked_missing_authorization_requirement"
BLOCKED_MISSING_GOVERNANCE_DEPENDENCY = "blocked_missing_governance_dependency"
BLOCKED_MISSING_REPLAY_LINEAGE = "blocked_missing_replay_lineage"
BLOCKED_MISSING_ROLLBACK_LINEAGE = "blocked_missing_rollback_lineage"
BLOCKED_COMPATIBILITY_REQUIREMENT = "blocked_compatibility_requirement"
BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE = "blocked_unsupported_orchestration_state"
BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN = "blocked_prohibited_orchestration_domain"
BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT = "blocked_environment_isolation_requirement"
BLOCKED_EXECUTION_BEHAVIOR_DETECTED = "blocked_execution_behavior_detected"

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_ORCHESTRATION_IDENTITY,
    BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT,
    BLOCKED_MISSING_GOVERNANCE_DEPENDENCY,
    BLOCKED_MISSING_REPLAY_LINEAGE,
    BLOCKED_MISSING_ROLLBACK_LINEAGE,
    BLOCKED_COMPATIBILITY_REQUIREMENT,
    BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE,
    BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN,
    BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT,
    BLOCKED_EXECUTION_BEHAVIOR_DETECTED,
    GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
)


@dataclass(frozen=True)
class GovernanceConsumptionContract:
    orchestration_request_id: str
    orchestration_scope_id: str
    orchestration_scope: str
    environment: str
    authorization_required: bool
    authorization_state: str
    governance_dependency_ids: tuple[str, ...]
    replay_lineage_required: bool
    replay_lineage_id: str
    rollback_lineage_required: bool
    rollback_lineage_id: str
    compatibility_requirements: tuple[str, ...]
    compatibility_verified: bool
    environment_isolated: bool
    unsupported_orchestration_states: tuple[str, ...]
    requested_orchestration_domain: str
    boundary_model: OrchestrationBoundaryModel
    visibility_model: OrchestrationVisibilityModel
    blocker_models: tuple[OrchestrationBlockerModel, ...]
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    recommendation_system_enabled: bool = False
    decision_routing_enabled: bool = False
    production_routing_enabled: bool = False
    persistent_mutation_enabled: bool = False
    state_writes_enabled: bool = False
    audit_log_writes_enabled: bool = False
    external_side_effects_enabled: bool = False
    production_authoritative_manifests_enabled: bool = False
    production_runtime_consumption_enabled: bool = False
    experiment_execution_enabled: bool = False
    self_modifying_orchestration_enabled: bool = False
    hidden_fallback_logic_enabled: bool = False


def build_governance_consumption_contract(
    *,
    orchestration_request_id: str,
    orchestration_scope_id: str,
    orchestration_scope: str,
    environment: str,
    authorization_required: bool,
    authorization_state: str,
    governance_dependency_ids: tuple[str, ...],
    replay_lineage_required: bool,
    replay_lineage_id: str,
    rollback_lineage_required: bool,
    rollback_lineage_id: str,
    compatibility_requirements: tuple[str, ...],
    compatibility_verified: bool,
    environment_isolated: bool,
    unsupported_orchestration_states: tuple[str, ...],
    requested_orchestration_domain: str,
    boundary_model: OrchestrationBoundaryModel | None = None,
    visibility_model: OrchestrationVisibilityModel | None = None,
    blocker_models: tuple[OrchestrationBlockerModel, ...] | None = None,
    **prohibition_flags: bool,
) -> GovernanceConsumptionContract:
    return GovernanceConsumptionContract(
        orchestration_request_id=orchestration_request_id,
        orchestration_scope_id=orchestration_scope_id,
        orchestration_scope=orchestration_scope,
        environment=environment,
        authorization_required=authorization_required,
        authorization_state=authorization_state,
        governance_dependency_ids=tuple(governance_dependency_ids),
        replay_lineage_required=replay_lineage_required,
        replay_lineage_id=replay_lineage_id,
        rollback_lineage_required=rollback_lineage_required,
        rollback_lineage_id=rollback_lineage_id,
        compatibility_requirements=tuple(compatibility_requirements),
        compatibility_verified=compatibility_verified,
        environment_isolated=environment_isolated,
        unsupported_orchestration_states=tuple(unsupported_orchestration_states),
        requested_orchestration_domain=requested_orchestration_domain,
        boundary_model=boundary_model or default_orchestration_boundary_model(),
        visibility_model=visibility_model or default_orchestration_visibility_model(),
        blocker_models=blocker_models or default_orchestration_blockers(),
        **prohibition_flags,
    )


def default_governance_consumption_contract() -> GovernanceConsumptionContract:
    return build_governance_consumption_contract(
        orchestration_request_id="orchestration-request-v3-5-phase-1",
        orchestration_scope_id="orchestration-scope-v3-5-governance-consumption",
        orchestration_scope="non_production_governance_planning",
        environment="non_production",
        authorization_required=True,
        authorization_state="authorized_for_planning",
        governance_dependency_ids=(
            "v3_4_controlled_execution_gate",
            "v3_4_non_production_authorization",
            "v3_4_execution_session_sandboxing",
            "v3_4_replay_safe_execution_scope",
            "v3_4_rollback_execution_governance",
            "v3_4_execution_drift_escalation",
            "v3_4_runtime_mutation_boundary",
            "v3_4_experiment_isolation",
            "v3_4_execution_audit_logging",
            "v3_4_controlled_execution_readiness_audit",
            "v3_4_closeout_and_v3_5_readiness",
        ),
        replay_lineage_required=True,
        replay_lineage_id="replay-lineage-v3-5-governance-consumption",
        rollback_lineage_required=True,
        rollback_lineage_id="rollback-lineage-v3-5-governance-consumption",
        compatibility_requirements=(
            "v3_4_governance_chain_compatible",
            "non_production_environment_isolated",
            "planning_only_contract_surface",
        ),
        compatibility_verified=True,
        environment_isolated=True,
        unsupported_orchestration_states=(),
        requested_orchestration_domain="governance_consumption_planning",
    )


def evaluate_governance_consumption_contract(contract: GovernanceConsumptionContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidates: list[str] = []

    def add(status: str, blocker_id: str) -> None:
        candidates.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if not contract.orchestration_request_id or not contract.orchestration_scope_id:
        add(BLOCKED_MISSING_ORCHESTRATION_IDENTITY, "orchestration_identity_missing")
    if contract.authorization_required and contract.authorization_state != "authorized_for_planning":
        add(BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT, "authorization_requirement_not_satisfied")
    if not contract.governance_dependency_ids:
        add(BLOCKED_MISSING_GOVERNANCE_DEPENDENCY, "governance_dependency_missing")
    if contract.replay_lineage_required and not contract.replay_lineage_id:
        add(BLOCKED_MISSING_REPLAY_LINEAGE, "replay_lineage_missing")
    if contract.rollback_lineage_required and not contract.rollback_lineage_id:
        add(BLOCKED_MISSING_ROLLBACK_LINEAGE, "rollback_lineage_missing")
    if not contract.compatibility_requirements or not contract.compatibility_verified:
        add(BLOCKED_COMPATIBILITY_REQUIREMENT, "compatibility_requirement_not_satisfied")
    if contract.unsupported_orchestration_states:
        add(BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE, "unsupported_orchestration_state_visible")
    if contract.requested_orchestration_domain in contract.boundary_model.prohibited_orchestration_domains:
        add(BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN, "prohibited_orchestration_domain_requested")
    if contract.requested_orchestration_domain not in contract.boundary_model.allowed_orchestration_domains:
        add(BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN, "orchestration_domain_not_allowed")
    if not contract.environment_isolated or contract.environment != "non_production":
        add(BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT, "environment_isolation_not_satisfied")
    if _execution_behavior_detected(contract):
        add(BLOCKED_EXECUTION_BEHAVIOR_DETECTED, "execution_behavior_detected")

    status = classify_governance_consumption_status(candidates)
    result = {
        "status": status,
        "planning_ready": status == GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
        "planning_only": True,
        "execution_enabled": False,
        "orchestration_execution_enabled": False,
        "blockers": _order_blockers(blockers),
        "contract": _export_contract(contract),
        "boundary": export_orchestration_boundary(contract.boundary_model),
        "visibility": export_orchestration_visibility(contract.visibility_model),
        "blocker_models": export_orchestration_blockers(contract.blocker_models),
        "guarantees": {
            "deterministic_outputs": True,
            "stable_serialization": True,
            "replay_safe_contract_generation": bool(contract.replay_lineage_required and contract.replay_lineage_id),
            "rollback_safe_contract_generation": bool(contract.rollback_lineage_required and contract.rollback_lineage_id),
            "explicit_provenance": True,
            "explicit_unsupported_states": bool(contract.boundary_model.unsupported_orchestration_states),
            "compatibility_safe_evolution": bool(contract.compatibility_requirements),
            "governance_chain_explainability": bool(contract.visibility_model.governance_dependency_visible),
            "auditability": bool(contract.visibility_model.auditability_required),
        },
        "prohibitions": _prohibition_checks(contract),
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_governance_consumption_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_COMPATIBILITY_REQUIREMENT


def summarize_governance_consumption_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "planning_ready": result["planning_ready"],
        "planning_only": result["planning_only"],
        "execution_enabled": result["execution_enabled"],
        "orchestration_execution_enabled": result["orchestration_execution_enabled"],
        "blocker_count": len(result["blockers"]),
        "deterministic_hash": result["deterministic_hash"],
        **result["guarantees"],
        **result["prohibitions"],
    }


def serialize_governance_consumption_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def hash_governance_consumption_contract(contract: GovernanceConsumptionContract) -> str:
    return deterministic_hash(_export_contract(contract))


def _export_contract(contract: GovernanceConsumptionContract) -> dict[str, Any]:
    data = asdict(contract)
    data["boundary_model"] = export_orchestration_boundary(contract.boundary_model)
    data["visibility_model"] = export_orchestration_visibility(contract.visibility_model)
    data["blocker_models"] = export_orchestration_blockers(contract.blocker_models)
    data["boundary_hash"] = hash_orchestration_boundary(contract.boundary_model)
    data["visibility_hash"] = hash_orchestration_visibility(contract.visibility_model)
    data["blocker_hash"] = hash_orchestration_blockers(contract.blocker_models)
    return data


def _prohibition_checks(contract: GovernanceConsumptionContract) -> dict[str, bool]:
    return {
        "runtime_execution_enabled": contract.runtime_execution_enabled,
        "orchestration_execution_enabled": contract.orchestration_execution_enabled,
        "autonomous_orchestration_enabled": contract.autonomous_orchestration_enabled,
        "recommendation_system_enabled": contract.recommendation_system_enabled,
        "decision_routing_enabled": contract.decision_routing_enabled,
        "production_routing_enabled": contract.production_routing_enabled,
        "persistent_mutation_enabled": contract.persistent_mutation_enabled,
        "state_writes_enabled": contract.state_writes_enabled,
        "audit_log_writes_enabled": contract.audit_log_writes_enabled,
        "external_side_effects_enabled": contract.external_side_effects_enabled,
        "production_authoritative_manifests_enabled": contract.production_authoritative_manifests_enabled,
        "production_runtime_consumption_enabled": contract.production_runtime_consumption_enabled,
        "experiment_execution_enabled": contract.experiment_execution_enabled,
        "self_modifying_orchestration_enabled": contract.self_modifying_orchestration_enabled,
        "hidden_fallback_logic_enabled": contract.hidden_fallback_logic_enabled,
    }


def _execution_behavior_detected(contract: GovernanceConsumptionContract) -> bool:
    return any(_prohibition_checks(contract).values())


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
