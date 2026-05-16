"""Planning-only rollback execution governance contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_execution_gate_contract,
)
from .execution_session_sandboxing_contracts import (
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_execution_session_sandbox_contract,
)
from .non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_non_production_execution_authorization_contract,
)
from .replay_safe_execution_scope_contracts import (
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_replay_safe_execution_scope_contract,
)


ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "rollback_governance_ready_for_controlled_execution_planning"
BLOCKED_MISSING_ROLLBACK_PLAN_ID = "blocked_missing_rollback_plan_id"
BLOCKED_ROLLBACK_NOT_REQUIRED = "blocked_rollback_not_required"
BLOCKED_ROLLBACK_PLAN_MISSING = "blocked_rollback_plan_missing"
BLOCKED_ROLLBACK_LINEAGE_MISSING = "blocked_rollback_lineage_missing"
BLOCKED_ROLLBACK_TARGET_MISSING = "blocked_rollback_target_missing"
BLOCKED_ROLLBACK_VALIDATION_MISSING = "blocked_rollback_validation_missing"
BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH = "blocked_rollback_environment_mismatch"
BLOCKED_ROLLBACK_SESSION_MISMATCH = "blocked_rollback_session_mismatch"
BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED = "blocked_rollback_scope_unsupported"
BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED = "blocked_live_rollback_execution_prohibited"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

SUPPORTED_ROLLBACK_SCOPES = frozenset(
    {
        "controlled_non_production",
        "isolated_experimental_planning",
        "replay_verified_planning",
    }
)
SUPPORTED_ROLLBACK_ENVIRONMENTS = frozenset({"local", "test", "ci", "non_production", "experimental"})

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_ROLLBACK_PLAN_ID,
    BLOCKED_ROLLBACK_NOT_REQUIRED,
    BLOCKED_ROLLBACK_PLAN_MISSING,
    BLOCKED_ROLLBACK_LINEAGE_MISSING,
    BLOCKED_ROLLBACK_TARGET_MISSING,
    BLOCKED_ROLLBACK_VALIDATION_MISSING,
    BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH,
    BLOCKED_ROLLBACK_SESSION_MISMATCH,
    BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED,
    MANUAL_REVIEW_REQUIRED,
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class RollbackExecutionGovernanceContract:
    """Inputs required to validate rollback governance for future controlled planning."""

    rollback_plan_id: str
    execution_scope: str
    environment: str
    session_id: str
    sandbox_id: str
    authorization_id: str
    gate_contract_id: str
    replay_scope_id: str
    rollback_required: bool
    rollback_plan_present: bool
    rollback_lineage_present: bool
    rollback_target_present: bool
    rollback_validation_present: bool
    rollback_scope_supported: bool
    live_rollback_execution_requested: bool
    expected_environment: str
    expected_session_id: str
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    sandbox_contract: Any | None = None
    replay_scope_contract: Any | None = None
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    recommendation_logic_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_rollback_execution_governance_contract(
    *,
    rollback_plan_id: str,
    execution_scope: str,
    environment: str,
    session_id: str,
    sandbox_id: str,
    authorization_id: str,
    gate_contract_id: str,
    replay_scope_id: str,
    rollback_required: bool,
    rollback_plan_present: bool,
    rollback_lineage_present: bool,
    rollback_target_present: bool,
    rollback_validation_present: bool,
    rollback_scope_supported: bool,
    live_rollback_execution_requested: bool,
    expected_environment: str,
    expected_session_id: str,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    recommendation_logic_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> RollbackExecutionGovernanceContract:
    return RollbackExecutionGovernanceContract(
        rollback_plan_id=rollback_plan_id,
        execution_scope=execution_scope,
        environment=environment,
        session_id=session_id,
        sandbox_id=sandbox_id,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        replay_scope_id=replay_scope_id,
        rollback_required=rollback_required,
        rollback_plan_present=rollback_plan_present,
        rollback_lineage_present=rollback_lineage_present,
        rollback_target_present=rollback_target_present,
        rollback_validation_present=rollback_validation_present,
        rollback_scope_supported=rollback_scope_supported,
        live_rollback_execution_requested=live_rollback_execution_requested,
        expected_environment=expected_environment,
        expected_session_id=expected_session_id,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_replay_execution_enabled=live_replay_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        recommendation_logic_enabled=recommendation_logic_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_rollback_execution_governance_contract(contract: RollbackExecutionGovernanceContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.live_rollback_execution_requested:
        add_blocker(BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED, "live_rollback_execution_prohibited")
    if not contract.rollback_plan_id:
        add_blocker(BLOCKED_MISSING_ROLLBACK_PLAN_ID, "rollback_plan_id_missing")
    if not contract.rollback_required:
        add_blocker(BLOCKED_ROLLBACK_NOT_REQUIRED, "rollback_requirement_missing")
    if not contract.rollback_plan_present:
        add_blocker(BLOCKED_ROLLBACK_PLAN_MISSING, "rollback_plan_missing")
    if not contract.rollback_lineage_present:
        add_blocker(BLOCKED_ROLLBACK_LINEAGE_MISSING, "rollback_lineage_missing")
    if not contract.rollback_target_present:
        add_blocker(BLOCKED_ROLLBACK_TARGET_MISSING, "rollback_target_missing")
    if not contract.rollback_validation_present:
        add_blocker(BLOCKED_ROLLBACK_VALIDATION_MISSING, "rollback_validation_missing")
    if contract.environment != contract.expected_environment:
        add_blocker(BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH, "rollback_environment_mismatch")
    if contract.session_id != contract.expected_session_id:
        add_blocker(BLOCKED_ROLLBACK_SESSION_MISMATCH, "rollback_session_mismatch")
    if (
        not contract.rollback_scope_supported
        or contract.execution_scope not in SUPPORTED_ROLLBACK_SCOPES
        or contract.environment not in SUPPORTED_ROLLBACK_ENVIRONMENTS
    ):
        add_blocker(BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED, "rollback_scope_unsupported")

    gate_result = evaluate_controlled_execution_gate_contract(contract.gate_contract) if contract.gate_contract is not None else None
    authorization_result = (
        evaluate_non_production_execution_authorization_contract(contract.authorization_contract)
        if contract.authorization_contract is not None
        else None
    )
    sandbox_result = evaluate_execution_session_sandbox_contract(contract.sandbox_contract) if contract.sandbox_contract is not None else None
    replay_result = evaluate_replay_safe_execution_scope_contract(contract.replay_scope_contract) if contract.replay_scope_contract is not None else None
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED, "phase2_authorization_not_valid")
    if (
        sandbox_result is not None
        and sandbox_result["status"] != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED, "phase3_sandbox_not_ready")
    if (
        replay_result is not None
        and replay_result["status"] != REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED, "phase4_replay_scope_not_ready")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_rollback_execution_governance_status(candidate_statuses)
    result = {
        "status": status,
        "rollback_governance_ready": status == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "rollback_governance_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "rollback_governance_does_not_bypass_authorization": True,
        },
        "phase3_sandbox_compatibility": {
            "sandbox_linked": bool(contract.sandbox_id),
            "sandbox_status": sandbox_result["status"] if sandbox_result else "not_evaluated",
            "rollback_governance_does_not_bypass_sandbox": True,
        },
        "phase4_replay_scope_compatibility": {
            "replay_scope_linked": bool(contract.replay_scope_id),
            "replay_scope_status": replay_result["status"] if replay_result else "not_evaluated",
            "rollback_governance_does_not_bypass_replay_scope": True,
        },
        "prohibition_checks": {
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": contract.runtime_manifest_consumption_enabled,
            "production_authoritative_manifest_treatment": contract.production_authoritative_manifest_treatment,
            "live_runtime_execution_enabled": contract.live_runtime_execution_enabled,
            "live_replay_execution_enabled": contract.live_replay_execution_enabled,
            "live_rollback_execution_enabled": False,
            "live_synthesis_execution_enabled": contract.live_synthesis_execution_enabled,
            "live_decision_routing_enabled": contract.live_decision_routing_enabled,
            "recommendation_logic_enabled": contract.recommendation_logic_enabled,
            "autonomous_planner_mutation_enabled": contract.autonomous_planner_mutation_enabled,
            "rollback_plan_execution_enabled": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_rollback_execution_governance_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED


def summarize_rollback_execution_governance_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "rollback_governance_ready": result["rollback_governance_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "rollback_governance_does_not_bypass_gate": result["phase1_gate_compatibility"]["rollback_governance_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "rollback_governance_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["rollback_governance_does_not_bypass_authorization"],
        "phase3_sandbox_status": result["phase3_sandbox_compatibility"]["sandbox_status"],
        "rollback_governance_does_not_bypass_sandbox": result["phase3_sandbox_compatibility"]["rollback_governance_does_not_bypass_sandbox"],
        "phase4_replay_scope_status": result["phase4_replay_scope_compatibility"]["replay_scope_status"],
        "rollback_governance_does_not_bypass_replay_scope": result["phase4_replay_scope_compatibility"]["rollback_governance_does_not_bypass_replay_scope"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_rollback_execution_governance_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_rollback_execution_governance_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
) -> RollbackExecutionGovernanceContract:
    return build_rollback_execution_governance_contract(
        rollback_plan_id="rollback-plan-v3-4-phase-5",
        execution_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        replay_scope_id="replay-scope-v3-4-phase-4",
        rollback_required=True,
        rollback_plan_present=True,
        rollback_lineage_present=True,
        rollback_target_present=True,
        rollback_validation_present=True,
        rollback_scope_supported=True,
        live_rollback_execution_requested=False,
        expected_environment="non_production",
        expected_session_id="session-v3-4-phase-3",
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: RollbackExecutionGovernanceContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    data["sandbox_contract"] = "linked" if contract.sandbox_contract is not None else None
    data["replay_scope_contract"] = "linked" if contract.replay_scope_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
