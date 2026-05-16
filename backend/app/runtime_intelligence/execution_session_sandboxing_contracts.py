"""Planning-only execution session sandboxing contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_execution_gate_contract,
)
from .non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_non_production_execution_authorization_contract,
)


SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "sandbox_ready_for_controlled_execution_planning"
BLOCKED_MISSING_SESSION_ID = "blocked_missing_session_id"
BLOCKED_MISSING_SANDBOX_ID = "blocked_missing_sandbox_id"
BLOCKED_SESSION_NOT_ISOLATED = "blocked_session_not_isolated"
BLOCKED_CROSS_SESSION_STATE_ACCESS = "blocked_cross_session_state_access"
BLOCKED_PERSISTENT_MUTATION_REQUESTED = "blocked_persistent_mutation_requested"
BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED = "blocked_external_side_effect_requested"
BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED = "blocked_production_environment_prohibited"
BLOCKED_MISSING_AUTHORIZATION_LINK = "blocked_missing_authorization_link"
BLOCKED_MISSING_GATE_LINK = "blocked_missing_gate_link"
BLOCKED_SANDBOX_SCOPE_UNSUPPORTED = "blocked_sandbox_scope_unsupported"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

SUPPORTED_SANDBOX_SCOPES = frozenset(
    {
        "controlled_non_production",
        "isolated_experimental_planning",
        "replay_verified_planning",
    }
)
SUPPORTED_ENVIRONMENTS = frozenset({"local", "test", "ci", "non_production", "experimental"})

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED,
    BLOCKED_MISSING_SESSION_ID,
    BLOCKED_MISSING_SANDBOX_ID,
    BLOCKED_MISSING_AUTHORIZATION_LINK,
    BLOCKED_MISSING_GATE_LINK,
    BLOCKED_SESSION_NOT_ISOLATED,
    BLOCKED_CROSS_SESSION_STATE_ACCESS,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_SANDBOX_SCOPE_UNSUPPORTED,
    MANUAL_REVIEW_REQUIRED,
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ExecutionSessionSandboxContract:
    """Inputs required to validate isolated session sandbox planning boundaries."""

    session_id: str
    sandbox_id: str
    execution_scope: str
    environment: str
    isolated: bool
    authorization_id: str
    gate_contract_id: str
    cross_session_access_requested: bool
    persistent_mutation_requested: bool
    external_side_effect_requested: bool
    production_environment_requested: bool
    sandbox_scope_supported: bool
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    recommendation_logic_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_execution_session_sandbox_contract(
    *,
    session_id: str,
    sandbox_id: str,
    execution_scope: str,
    environment: str,
    isolated: bool,
    authorization_id: str,
    gate_contract_id: str,
    cross_session_access_requested: bool,
    persistent_mutation_requested: bool,
    external_side_effect_requested: bool,
    production_environment_requested: bool,
    sandbox_scope_supported: bool,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    recommendation_logic_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> ExecutionSessionSandboxContract:
    return ExecutionSessionSandboxContract(
        session_id=session_id,
        sandbox_id=sandbox_id,
        execution_scope=execution_scope,
        environment=environment,
        isolated=isolated,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        cross_session_access_requested=cross_session_access_requested,
        persistent_mutation_requested=persistent_mutation_requested,
        external_side_effect_requested=external_side_effect_requested,
        production_environment_requested=production_environment_requested,
        sandbox_scope_supported=sandbox_scope_supported,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_replay_execution_enabled=live_replay_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        recommendation_logic_enabled=recommendation_logic_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_execution_session_sandbox_contract(contract: ExecutionSessionSandboxContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.production_environment_requested or contract.environment == "production":
        add_blocker(BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED, "production_environment_prohibited")
    if contract.production_authoritative_manifest_treatment:
        add_blocker(BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED, "production_authoritative_manifest_treatment_prohibited")
    if not contract.session_id:
        add_blocker(BLOCKED_MISSING_SESSION_ID, "session_id_missing")
    if not contract.sandbox_id:
        add_blocker(BLOCKED_MISSING_SANDBOX_ID, "sandbox_id_missing")
    if not contract.authorization_id:
        add_blocker(BLOCKED_MISSING_AUTHORIZATION_LINK, "authorization_link_missing")
    if not contract.gate_contract_id:
        add_blocker(BLOCKED_MISSING_GATE_LINK, "phase1_gate_link_missing")
    if not contract.isolated:
        add_blocker(BLOCKED_SESSION_NOT_ISOLATED, "session_state_not_isolated")
    if contract.cross_session_access_requested:
        add_blocker(BLOCKED_CROSS_SESSION_STATE_ACCESS, "cross_session_state_access_prohibited")
    if contract.persistent_mutation_requested:
        add_blocker(BLOCKED_PERSISTENT_MUTATION_REQUESTED, "persistent_mutation_prohibited")
    if contract.external_side_effect_requested:
        add_blocker(BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED, "external_side_effect_prohibited")
    if (
        not contract.sandbox_scope_supported
        or contract.execution_scope not in SUPPORTED_SANDBOX_SCOPES
        or contract.environment not in SUPPORTED_ENVIRONMENTS
    ):
        add_blocker(BLOCKED_SANDBOX_SCOPE_UNSUPPORTED, "sandbox_scope_unsupported")

    gate_result = (
        evaluate_controlled_execution_gate_contract(contract.gate_contract)
        if contract.gate_contract is not None
        else None
    )
    authorization_result = (
        evaluate_non_production_execution_authorization_contract(contract.authorization_contract)
        if contract.authorization_contract is not None
        else None
    )
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_GATE_LINK, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MISSING_AUTHORIZATION_LINK, "phase2_authorization_not_valid")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_execution_session_sandbox_status(candidate_statuses)
    result = {
        "status": status,
        "sandbox_ready": status == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "sandbox_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "sandbox_does_not_bypass_authorization": True,
        },
        "prohibition_checks": {
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": contract.runtime_manifest_consumption_enabled,
            "production_authoritative_manifest_treatment": contract.production_authoritative_manifest_treatment,
            "live_runtime_execution_enabled": contract.live_runtime_execution_enabled,
            "live_replay_execution_enabled": contract.live_replay_execution_enabled,
            "live_synthesis_execution_enabled": contract.live_synthesis_execution_enabled,
            "live_decision_routing_enabled": contract.live_decision_routing_enabled,
            "recommendation_logic_enabled": contract.recommendation_logic_enabled,
            "autonomous_planner_mutation_enabled": contract.autonomous_planner_mutation_enabled,
            "persistent_mutation_enabled": False,
            "cross_session_state_sharing_enabled": False,
            "external_side_effects_enabled": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_execution_session_sandbox_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_SANDBOX_SCOPE_UNSUPPORTED


def summarize_execution_session_sandbox_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "sandbox_ready": result["sandbox_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "sandbox_does_not_bypass_gate": result["phase1_gate_compatibility"]["sandbox_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "sandbox_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["sandbox_does_not_bypass_authorization"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_execution_session_sandbox_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_execution_session_sandbox_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
) -> ExecutionSessionSandboxContract:
    return build_execution_session_sandbox_contract(
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        execution_scope="controlled_non_production",
        environment="non_production",
        isolated=True,
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        cross_session_access_requested=False,
        persistent_mutation_requested=False,
        external_side_effect_requested=False,
        production_environment_requested=False,
        sandbox_scope_supported=True,
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ExecutionSessionSandboxContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
