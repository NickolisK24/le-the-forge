"""Planning-only non-production execution authorization contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    build_controlled_execution_gate_contract,
    evaluate_controlled_execution_gate_contract,
)


AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING = "authorized_for_controlled_execution_planning"
BLOCKED_MISSING_AUTHORIZATION = "blocked_missing_authorization"
BLOCKED_INVALID_AUTHORIZATION_SCOPE = "blocked_invalid_authorization_scope"
BLOCKED_EXPIRED_AUTHORIZATION = "blocked_expired_authorization"
BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED = "blocked_production_authorization_prohibited"
BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH = "blocked_authorization_environment_mismatch"
BLOCKED_AUTHORIZATION_SESSION_MISMATCH = "blocked_authorization_session_mismatch"
BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING = "blocked_authorization_replay_requirement_missing"
BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING = "blocked_authorization_rollback_requirement_missing"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

AUTHORIZED_STATES = frozenset({"authorized", "explicitly_authorized", "authorized_for_non_production_planning"})
VALID_AUTHORIZATION_SCOPES = frozenset(
    {
        "controlled_non_production",
        "isolated_experimental_planning",
        "replay_verified_planning",
    }
)
VALID_ENVIRONMENTS = frozenset({"local", "test", "ci", "non_production", "experimental"})
ACTIVE_EXPIRATION_STATES = frozenset({"active", "not_expired"})

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED,
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_INVALID_AUTHORIZATION_SCOPE,
    BLOCKED_EXPIRED_AUTHORIZATION,
    BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH,
    BLOCKED_AUTHORIZATION_SESSION_MISMATCH,
    BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING,
    BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING,
    MANUAL_REVIEW_REQUIRED,
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class NonProductionExecutionAuthorizationContract:
    """Inputs required to authorize future controlled non-production execution planning."""

    authorization_id: str
    authorization_scope: str
    environment: str
    session_id: str
    authorized_by: str
    authorization_state: str
    replay_required: bool
    rollback_required: bool
    production_authorization_requested: bool
    expiration_state: str
    manual_review_required: bool
    requested_environment: str
    requested_session_id: str
    session_isolated: bool = True
    drift_escalation_required: bool = False
    decision_routing_requested: bool = False
    recommendation_requested: bool = False
    production_authoritative_requested: bool = False
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False


def build_non_production_execution_authorization_contract(
    *,
    authorization_id: str,
    authorization_scope: str,
    environment: str,
    session_id: str,
    authorized_by: str,
    authorization_state: str,
    replay_required: bool,
    rollback_required: bool,
    production_authorization_requested: bool,
    expiration_state: str,
    manual_review_required: bool,
    requested_environment: str | None = None,
    requested_session_id: str | None = None,
    session_isolated: bool = True,
    drift_escalation_required: bool = False,
    decision_routing_requested: bool = False,
    recommendation_requested: bool = False,
    production_authoritative_requested: bool = False,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
) -> NonProductionExecutionAuthorizationContract:
    return NonProductionExecutionAuthorizationContract(
        authorization_id=authorization_id,
        authorization_scope=authorization_scope,
        environment=environment,
        session_id=session_id,
        authorized_by=authorized_by,
        authorization_state=authorization_state,
        replay_required=replay_required,
        rollback_required=rollback_required,
        production_authorization_requested=production_authorization_requested,
        expiration_state=expiration_state,
        manual_review_required=manual_review_required,
        requested_environment=requested_environment or environment,
        requested_session_id=requested_session_id or session_id,
        session_isolated=session_isolated,
        drift_escalation_required=drift_escalation_required,
        decision_routing_requested=decision_routing_requested,
        recommendation_requested=recommendation_requested,
        production_authoritative_requested=production_authoritative_requested,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_replay_execution_enabled=live_replay_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
    )


def evaluate_non_production_execution_authorization_contract(
    contract: NonProductionExecutionAuthorizationContract,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.production_authorization_requested or contract.environment == "production":
        add_blocker(BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED, "production_authorization_prohibited")
    if contract.production_authoritative_requested:
        add_blocker(BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED, "production_authoritative_manifest_treatment_prohibited")
    if (
        not contract.authorization_id
        or not contract.authorized_by
        or contract.authorization_state not in AUTHORIZED_STATES
    ):
        add_blocker(BLOCKED_MISSING_AUTHORIZATION, "explicit_non_production_authorization_missing")
    if contract.authorization_scope not in VALID_AUTHORIZATION_SCOPES:
        add_blocker(BLOCKED_INVALID_AUTHORIZATION_SCOPE, "authorization_scope_not_supported")
    if contract.expiration_state not in ACTIVE_EXPIRATION_STATES:
        add_blocker(BLOCKED_EXPIRED_AUTHORIZATION, "authorization_expired")
    if contract.environment not in VALID_ENVIRONMENTS or contract.requested_environment != contract.environment:
        add_blocker(BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH, "authorization_environment_mismatch")
    if not contract.session_id or contract.requested_session_id != contract.session_id:
        add_blocker(BLOCKED_AUTHORIZATION_SESSION_MISMATCH, "authorization_session_mismatch")
    if not contract.replay_required:
        add_blocker(BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING, "authorization_replay_requirement_missing")
    if not contract.rollback_required:
        add_blocker(BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING, "authorization_rollback_requirement_missing")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_non_production_execution_authorization_status(candidate_statuses)
    phase1_gate = build_phase1_compatible_gate_contract(contract, status)
    phase1_result = evaluate_controlled_execution_gate_contract(phase1_gate)
    result = {
        "status": status,
        "authorized": status == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": asdict(contract),
        "phase1_gate_compatibility": {
            "gate_status": phase1_result["status"],
            "gate_eligible": phase1_result["status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
            "authorization_does_not_bypass_gate": True,
        },
        "prohibition_checks": {
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": contract.runtime_manifest_consumption_enabled,
            "production_authoritative_manifest_treatment": contract.production_authoritative_requested,
            "live_runtime_execution_enabled": contract.live_runtime_execution_enabled,
            "live_replay_execution_enabled": contract.live_replay_execution_enabled,
            "live_synthesis_execution_enabled": contract.live_synthesis_execution_enabled,
            "live_decision_routing_enabled": contract.live_decision_routing_enabled,
            "recommendation_logic_enabled": contract.recommendation_requested,
            "autonomous_planner_mutation_enabled": contract.autonomous_planner_mutation_enabled,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def build_phase1_compatible_gate_contract(
    contract: NonProductionExecutionAuthorizationContract,
    authorization_status: str,
):
    return build_controlled_execution_gate_contract(
        execution_scope=contract.authorization_scope,
        environment=contract.requested_environment,
        authorization_state=(
            "explicitly_authorized"
            if authorization_status == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
            else "missing"
        ),
        replay_required=contract.replay_required,
        rollback_required=contract.rollback_required,
        session_isolated=contract.session_isolated,
        drift_escalation_required=contract.drift_escalation_required,
        decision_routing_requested=contract.decision_routing_requested,
        recommendation_requested=contract.recommendation_requested,
        production_authoritative_requested=contract.production_authoritative_requested,
        runtime_manifest_consumption_enabled=contract.runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=contract.live_runtime_execution_enabled,
        live_replay_execution_enabled=contract.live_replay_execution_enabled,
        live_synthesis_execution_enabled=contract.live_synthesis_execution_enabled,
        live_decision_routing_enabled=contract.live_decision_routing_enabled,
        autonomous_planner_mutation_enabled=contract.autonomous_planner_mutation_enabled,
    )


def classify_non_production_execution_authorization_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_MISSING_AUTHORIZATION


def summarize_non_production_execution_authorization_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "authorized": result["authorized"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "phase1_gate_eligible": result["phase1_gate_compatibility"]["gate_eligible"],
        "authorization_does_not_bypass_gate": result["phase1_gate_compatibility"]["authorization_does_not_bypass_gate"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_non_production_execution_authorization_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_non_production_execution_authorization_contract() -> NonProductionExecutionAuthorizationContract:
    return build_non_production_execution_authorization_contract(
        authorization_id="auth-v3-4-phase-2-non-production",
        authorization_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-2",
        authorized_by="runtime-governance",
        authorization_state="explicitly_authorized",
        replay_required=True,
        rollback_required=True,
        production_authorization_requested=False,
        expiration_state="active",
        manual_review_required=False,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
