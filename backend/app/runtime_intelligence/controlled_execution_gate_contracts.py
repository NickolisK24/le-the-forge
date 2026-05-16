"""Planning-only controlled execution gate contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize


ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING = "eligible_for_controlled_execution_planning"
BLOCKED_PRODUCTION_EXECUTION_PROHIBITED = "blocked_production_execution_prohibited"
BLOCKED_MISSING_REPLAY_REQUIREMENT = "blocked_missing_replay_requirement"
BLOCKED_MISSING_ROLLBACK_REQUIREMENT = "blocked_missing_rollback_requirement"
BLOCKED_MISSING_SESSION_ISOLATION = "blocked_missing_session_isolation"
BLOCKED_MISSING_AUTHORIZATION = "blocked_missing_authorization"
BLOCKED_UNSUPPORTED_EXECUTION_SCOPE = "blocked_unsupported_execution_scope"
BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED = "blocked_runtime_decision_routing_prohibited"
BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED = "blocked_recommendation_logic_prohibited"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

AUTHORIZED_STATES = frozenset({"explicitly_authorized", "authorized_for_non_production_planning"})
NON_PRODUCTION_ENVIRONMENTS = frozenset({"local", "test", "ci", "non_production", "experimental"})
CONTROLLED_EXECUTION_SCOPES = frozenset(
    {
        "controlled_non_production",
        "isolated_experimental_planning",
        "replay_verified_planning",
    }
)
PRODUCTION_SCOPES = frozenset({"production", "production_runtime", "production_execution"})

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_PRODUCTION_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_MISSING_REPLAY_REQUIREMENT,
    BLOCKED_MISSING_ROLLBACK_REQUIREMENT,
    BLOCKED_MISSING_SESSION_ISOLATION,
    BLOCKED_UNSUPPORTED_EXECUTION_SCOPE,
    BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED,
    BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED,
    MANUAL_REVIEW_REQUIRED,
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ControlledExecutionGateContract:
    """Inputs required to classify future non-production execution planning eligibility."""

    execution_scope: str
    environment: str
    authorization_state: str
    replay_required: bool
    rollback_required: bool
    session_isolated: bool
    drift_escalation_required: bool
    decision_routing_requested: bool
    recommendation_requested: bool
    production_authoritative_requested: bool
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False


def build_controlled_execution_gate_contract(
    *,
    execution_scope: str,
    environment: str,
    authorization_state: str,
    replay_required: bool,
    rollback_required: bool,
    session_isolated: bool,
    drift_escalation_required: bool,
    decision_routing_requested: bool,
    recommendation_requested: bool,
    production_authoritative_requested: bool,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
) -> ControlledExecutionGateContract:
    return ControlledExecutionGateContract(
        execution_scope=execution_scope,
        environment=environment,
        authorization_state=authorization_state,
        replay_required=replay_required,
        rollback_required=rollback_required,
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


def evaluate_controlled_execution_gate_contract(contract: ControlledExecutionGateContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.environment == "production" or contract.execution_scope in PRODUCTION_SCOPES:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "production_execution_prohibited")
    if contract.production_authoritative_requested:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "production_authoritative_manifest_treatment_prohibited")
    if contract.runtime_manifest_consumption_enabled:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "default_runtime_manifest_consumption_prohibited")
    if contract.live_runtime_execution_enabled:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "live_runtime_execution_prohibited")
    if contract.live_replay_execution_enabled:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "live_replay_execution_prohibited")
    if contract.live_synthesis_execution_enabled:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "live_synthesis_execution_prohibited")
    if contract.autonomous_planner_mutation_enabled:
        add_blocker(BLOCKED_PRODUCTION_EXECUTION_PROHIBITED, "autonomous_planner_mutation_prohibited")
    if contract.authorization_state not in AUTHORIZED_STATES:
        add_blocker(BLOCKED_MISSING_AUTHORIZATION, "explicit_non_production_authorization_required")
    if not contract.replay_required:
        add_blocker(BLOCKED_MISSING_REPLAY_REQUIREMENT, "replay_requirement_missing")
    if not contract.rollback_required:
        add_blocker(BLOCKED_MISSING_ROLLBACK_REQUIREMENT, "rollback_requirement_missing")
    if not contract.session_isolated:
        add_blocker(BLOCKED_MISSING_SESSION_ISOLATION, "session_isolation_missing")
    if contract.execution_scope not in CONTROLLED_EXECUTION_SCOPES and contract.execution_scope not in PRODUCTION_SCOPES:
        add_blocker(BLOCKED_UNSUPPORTED_EXECUTION_SCOPE, "unsupported_execution_scope")
    if contract.environment not in NON_PRODUCTION_ENVIRONMENTS and contract.environment != "production":
        add_blocker(BLOCKED_UNSUPPORTED_EXECUTION_SCOPE, "unsupported_execution_environment")
    if contract.decision_routing_requested or contract.live_decision_routing_enabled:
        add_blocker(BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED, "runtime_decision_routing_prohibited")
    if contract.recommendation_requested:
        add_blocker(BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED, "recommendation_logic_prohibited")

    if not blockers and contract.drift_escalation_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_controlled_execution_gate_status(candidate_statuses)
    result = {
        "status": status,
        "eligible": status == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": asdict(contract),
        "prohibition_checks": {
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


def classify_controlled_execution_gate_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_UNSUPPORTED_EXECUTION_SCOPE


def summarize_controlled_execution_gate_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "eligible": result["eligible"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        "production_execution_enabled": result["prohibition_checks"]["production_execution_enabled"],
        "production_runtime_routing_authorized": result["prohibition_checks"]["production_runtime_routing_authorized"],
        "runtime_manifest_consumption_enabled": result["prohibition_checks"]["runtime_manifest_consumption_enabled"],
        "production_authoritative_manifest_treatment": result["prohibition_checks"]["production_authoritative_manifest_treatment"],
        "live_runtime_execution_enabled": result["prohibition_checks"]["live_runtime_execution_enabled"],
        "live_replay_execution_enabled": result["prohibition_checks"]["live_replay_execution_enabled"],
        "live_synthesis_execution_enabled": result["prohibition_checks"]["live_synthesis_execution_enabled"],
        "live_decision_routing_enabled": result["prohibition_checks"]["live_decision_routing_enabled"],
        "recommendation_logic_enabled": result["prohibition_checks"]["recommendation_logic_enabled"],
        "autonomous_planner_mutation_enabled": result["prohibition_checks"]["autonomous_planner_mutation_enabled"],
    }


def serialize_controlled_execution_gate_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_controlled_execution_gate_contract() -> ControlledExecutionGateContract:
    return build_controlled_execution_gate_contract(
        execution_scope="controlled_non_production",
        environment="non_production",
        authorization_state="explicitly_authorized",
        replay_required=True,
        rollback_required=True,
        session_isolated=True,
        drift_escalation_required=False,
        decision_routing_requested=False,
        recommendation_requested=False,
        production_authoritative_requested=False,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
