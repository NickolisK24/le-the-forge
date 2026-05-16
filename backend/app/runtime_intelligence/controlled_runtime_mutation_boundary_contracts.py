"""Planning-only controlled runtime mutation boundary contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_execution_gate_contract,
)
from .execution_drift_escalation_contracts import (
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_execution_drift_escalation_contract,
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
from .rollback_execution_governance_contracts import (
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_rollback_execution_governance_contract,
)


MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "mutation_boundary_ready_for_controlled_execution_planning"
BLOCKED_MISSING_MUTATION_BOUNDARY_ID = "blocked_missing_mutation_boundary_id"
BLOCKED_MUTATION_SCOPE_MISSING = "blocked_mutation_scope_missing"
BLOCKED_MUTATION_SCOPE_UNSUPPORTED = "blocked_mutation_scope_unsupported"
BLOCKED_PERSISTENT_MUTATION_REQUESTED = "blocked_persistent_mutation_requested"
BLOCKED_PRODUCTION_MUTATION_REQUESTED = "blocked_production_mutation_requested"
BLOCKED_AUTONOMOUS_MUTATION_REQUESTED = "blocked_autonomous_mutation_requested"
BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED = "blocked_external_side_effect_requested"
BLOCKED_STATE_WRITE_REQUESTED = "blocked_state_write_requested"
BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK = "blocked_missing_rollback_governance_link"
BLOCKED_MISSING_DRIFT_ESCALATION_LINK = "blocked_missing_drift_escalation_link"
BLOCKED_MUTATION_ENVIRONMENT_MISMATCH = "blocked_mutation_environment_mismatch"
BLOCKED_MUTATION_SESSION_MISMATCH = "blocked_mutation_session_mismatch"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

SUPPORTED_MUTATION_SCOPES = frozenset(
    {
        "read_only_boundary_validation",
        "ephemeral_non_persistent_planning",
        "no_write_sandbox_probe",
    }
)

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_MUTATION_BOUNDARY_ID,
    BLOCKED_MUTATION_SCOPE_MISSING,
    BLOCKED_MUTATION_SCOPE_UNSUPPORTED,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_PRODUCTION_MUTATION_REQUESTED,
    BLOCKED_AUTONOMOUS_MUTATION_REQUESTED,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_STATE_WRITE_REQUESTED,
    BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MUTATION_ENVIRONMENT_MISMATCH,
    BLOCKED_MUTATION_SESSION_MISMATCH,
    MANUAL_REVIEW_REQUIRED,
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ControlledRuntimeMutationBoundaryContract:
    """Inputs required to validate mutation boundaries for future controlled planning."""

    mutation_boundary_id: str
    mutation_scope: str
    execution_scope: str
    environment: str
    session_id: str
    sandbox_id: str
    authorization_id: str
    gate_contract_id: str
    replay_scope_id: str
    rollback_plan_id: str
    drift_audit_id: str
    mutation_scope_supported: bool
    persistent_mutation_requested: bool
    production_mutation_requested: bool
    autonomous_mutation_requested: bool
    external_side_effect_requested: bool
    state_write_requested: bool
    expected_environment: str
    expected_session_id: str
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    sandbox_contract: Any | None = None
    replay_scope_contract: Any | None = None
    rollback_contract: Any | None = None
    drift_escalation_contract: Any | None = None
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_rollback_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    recommendation_logic_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False
    persistent_mutation_enabled: bool = False
    state_writes_enabled: bool = False
    external_side_effects_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_controlled_runtime_mutation_boundary_contract(
    *,
    mutation_boundary_id: str,
    mutation_scope: str,
    execution_scope: str,
    environment: str,
    session_id: str,
    sandbox_id: str,
    authorization_id: str,
    gate_contract_id: str,
    replay_scope_id: str,
    rollback_plan_id: str,
    drift_audit_id: str,
    mutation_scope_supported: bool,
    persistent_mutation_requested: bool,
    production_mutation_requested: bool,
    autonomous_mutation_requested: bool,
    external_side_effect_requested: bool,
    state_write_requested: bool,
    expected_environment: str,
    expected_session_id: str,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
    drift_escalation_contract: Any | None = None,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_rollback_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    recommendation_logic_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
    persistent_mutation_enabled: bool = False,
    state_writes_enabled: bool = False,
    external_side_effects_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> ControlledRuntimeMutationBoundaryContract:
    return ControlledRuntimeMutationBoundaryContract(
        mutation_boundary_id=mutation_boundary_id,
        mutation_scope=mutation_scope,
        execution_scope=execution_scope,
        environment=environment,
        session_id=session_id,
        sandbox_id=sandbox_id,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        replay_scope_id=replay_scope_id,
        rollback_plan_id=rollback_plan_id,
        drift_audit_id=drift_audit_id,
        mutation_scope_supported=mutation_scope_supported,
        persistent_mutation_requested=persistent_mutation_requested,
        production_mutation_requested=production_mutation_requested,
        autonomous_mutation_requested=autonomous_mutation_requested,
        external_side_effect_requested=external_side_effect_requested,
        state_write_requested=state_write_requested,
        expected_environment=expected_environment,
        expected_session_id=expected_session_id,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
        drift_escalation_contract=drift_escalation_contract,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_replay_execution_enabled=live_replay_execution_enabled,
        live_rollback_execution_enabled=live_rollback_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        recommendation_logic_enabled=recommendation_logic_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
        persistent_mutation_enabled=persistent_mutation_enabled,
        state_writes_enabled=state_writes_enabled,
        external_side_effects_enabled=external_side_effects_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_controlled_runtime_mutation_boundary_contract(
    contract: ControlledRuntimeMutationBoundaryContract,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if not contract.mutation_boundary_id:
        add_blocker(BLOCKED_MISSING_MUTATION_BOUNDARY_ID, "mutation_boundary_id_missing")
    if not contract.mutation_scope:
        add_blocker(BLOCKED_MUTATION_SCOPE_MISSING, "mutation_scope_missing")
    if not contract.mutation_scope_supported or contract.mutation_scope not in SUPPORTED_MUTATION_SCOPES:
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "mutation_scope_unsupported")
    if contract.persistent_mutation_requested:
        add_blocker(BLOCKED_PERSISTENT_MUTATION_REQUESTED, "persistent_mutation_requested")
    if contract.production_mutation_requested:
        add_blocker(BLOCKED_PRODUCTION_MUTATION_REQUESTED, "production_mutation_requested")
    if contract.autonomous_mutation_requested:
        add_blocker(BLOCKED_AUTONOMOUS_MUTATION_REQUESTED, "autonomous_mutation_requested")
    if contract.external_side_effect_requested:
        add_blocker(BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED, "external_side_effect_requested")
    if contract.state_write_requested:
        add_blocker(BLOCKED_STATE_WRITE_REQUESTED, "state_write_requested")
    if not contract.rollback_plan_id:
        add_blocker(BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK, "rollback_governance_link_missing")
    if not contract.drift_audit_id:
        add_blocker(BLOCKED_MISSING_DRIFT_ESCALATION_LINK, "drift_escalation_link_missing")
    if contract.environment != contract.expected_environment:
        add_blocker(BLOCKED_MUTATION_ENVIRONMENT_MISMATCH, "mutation_environment_mismatch")
    if contract.session_id != contract.expected_session_id:
        add_blocker(BLOCKED_MUTATION_SESSION_MISMATCH, "mutation_session_mismatch")

    gate_result = evaluate_controlled_execution_gate_contract(contract.gate_contract) if contract.gate_contract is not None else None
    authorization_result = (
        evaluate_non_production_execution_authorization_contract(contract.authorization_contract)
        if contract.authorization_contract is not None
        else None
    )
    sandbox_result = evaluate_execution_session_sandbox_contract(contract.sandbox_contract) if contract.sandbox_contract is not None else None
    replay_result = evaluate_replay_safe_execution_scope_contract(contract.replay_scope_contract) if contract.replay_scope_contract is not None else None
    rollback_result = evaluate_rollback_execution_governance_contract(contract.rollback_contract) if contract.rollback_contract is not None else None
    drift_result = (
        evaluate_execution_drift_escalation_contract(contract.drift_escalation_contract)
        if contract.drift_escalation_contract is not None
        else None
    )
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase2_authorization_not_valid")
    if (
        sandbox_result is not None
        and sandbox_result["status"] != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase3_sandbox_not_ready")
    if (
        replay_result is not None
        and replay_result["status"] != REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase4_replay_scope_not_ready")
    if (
        rollback_result is not None
        and rollback_result["status"] != ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase5_rollback_governance_not_ready")
    if (
        drift_result is not None
        and drift_result["status"] != DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_MUTATION_SCOPE_UNSUPPORTED, "phase6_drift_escalation_not_ready")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_controlled_runtime_mutation_boundary_status(candidate_statuses)
    result = {
        "status": status,
        "mutation_boundary_ready": status == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_authorization": True,
        },
        "phase3_sandbox_compatibility": {
            "sandbox_linked": bool(contract.sandbox_id),
            "sandbox_status": sandbox_result["status"] if sandbox_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_sandbox": True,
        },
        "phase4_replay_scope_compatibility": {
            "replay_scope_linked": bool(contract.replay_scope_id),
            "replay_scope_status": replay_result["status"] if replay_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_replay_scope": True,
        },
        "phase5_rollback_governance_compatibility": {
            "rollback_plan_linked": bool(contract.rollback_plan_id),
            "rollback_governance_status": rollback_result["status"] if rollback_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_rollback_governance": True,
        },
        "phase6_drift_escalation_compatibility": {
            "drift_audit_linked": bool(contract.drift_audit_id),
            "drift_escalation_status": drift_result["status"] if drift_result else "not_evaluated",
            "mutation_boundary_does_not_bypass_drift_escalation": True,
        },
        "prohibition_checks": {
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": contract.runtime_manifest_consumption_enabled,
            "production_authoritative_manifest_treatment": contract.production_authoritative_manifest_treatment,
            "live_runtime_execution_enabled": contract.live_runtime_execution_enabled,
            "live_replay_execution_enabled": contract.live_replay_execution_enabled,
            "live_rollback_execution_enabled": contract.live_rollback_execution_enabled,
            "live_synthesis_execution_enabled": contract.live_synthesis_execution_enabled,
            "live_decision_routing_enabled": contract.live_decision_routing_enabled,
            "recommendation_logic_enabled": contract.recommendation_logic_enabled,
            "autonomous_planner_mutation_enabled": contract.autonomous_planner_mutation_enabled,
            "persistent_mutation_enabled": contract.persistent_mutation_enabled,
            "state_writes_enabled": contract.state_writes_enabled,
            "external_side_effects_enabled": contract.external_side_effects_enabled,
            "production_mutation_enabled": False,
            "mutation_execution_enabled": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_controlled_runtime_mutation_boundary_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_MUTATION_SCOPE_UNSUPPORTED


def summarize_controlled_runtime_mutation_boundary_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "mutation_boundary_ready": result["mutation_boundary_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "mutation_boundary_does_not_bypass_gate": result["phase1_gate_compatibility"]["mutation_boundary_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "mutation_boundary_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["mutation_boundary_does_not_bypass_authorization"],
        "phase3_sandbox_status": result["phase3_sandbox_compatibility"]["sandbox_status"],
        "mutation_boundary_does_not_bypass_sandbox": result["phase3_sandbox_compatibility"]["mutation_boundary_does_not_bypass_sandbox"],
        "phase4_replay_scope_status": result["phase4_replay_scope_compatibility"]["replay_scope_status"],
        "mutation_boundary_does_not_bypass_replay_scope": result["phase4_replay_scope_compatibility"]["mutation_boundary_does_not_bypass_replay_scope"],
        "phase5_rollback_governance_status": result["phase5_rollback_governance_compatibility"]["rollback_governance_status"],
        "mutation_boundary_does_not_bypass_rollback_governance": result["phase5_rollback_governance_compatibility"]["mutation_boundary_does_not_bypass_rollback_governance"],
        "phase6_drift_escalation_status": result["phase6_drift_escalation_compatibility"]["drift_escalation_status"],
        "mutation_boundary_does_not_bypass_drift_escalation": result["phase6_drift_escalation_compatibility"]["mutation_boundary_does_not_bypass_drift_escalation"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_controlled_runtime_mutation_boundary_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_controlled_runtime_mutation_boundary_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
    drift_escalation_contract: Any | None = None,
) -> ControlledRuntimeMutationBoundaryContract:
    return build_controlled_runtime_mutation_boundary_contract(
        mutation_boundary_id="mutation-boundary-v3-4-phase-7",
        mutation_scope="read_only_boundary_validation",
        execution_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        replay_scope_id="replay-scope-v3-4-phase-4",
        rollback_plan_id="rollback-plan-v3-4-phase-5",
        drift_audit_id="drift-audit-v3-4-phase-6",
        mutation_scope_supported=True,
        persistent_mutation_requested=False,
        production_mutation_requested=False,
        autonomous_mutation_requested=False,
        external_side_effect_requested=False,
        state_write_requested=False,
        expected_environment="non_production",
        expected_session_id="session-v3-4-phase-3",
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
        drift_escalation_contract=drift_escalation_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ControlledRuntimeMutationBoundaryContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    data["sandbox_contract"] = "linked" if contract.sandbox_contract is not None else None
    data["replay_scope_contract"] = "linked" if contract.replay_scope_contract is not None else None
    data["rollback_contract"] = "linked" if contract.rollback_contract is not None else None
    data["drift_escalation_contract"] = "linked" if contract.drift_escalation_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
