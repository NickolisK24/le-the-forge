"""Planning-only execution drift escalation contracts for v3.4."""

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
from .rollback_execution_governance_contracts import (
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_rollback_execution_governance_contract,
)


DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "drift_escalation_ready_for_controlled_execution_planning"
BLOCKED_MISSING_DRIFT_AUDIT_ID = "blocked_missing_drift_audit_id"
BLOCKED_DRIFT_CHECK_NOT_REQUIRED = "blocked_drift_check_not_required"
BLOCKED_DRIFT_AUDIT_MISSING = "blocked_drift_audit_missing"
BLOCKED_DRIFT_BASELINE_MISSING = "blocked_drift_baseline_missing"
BLOCKED_DRIFT_DETECTION_MISSING = "blocked_drift_detection_missing"
BLOCKED_UNRESOLVED_DRIFT_DETECTED = "blocked_unresolved_drift_detected"
BLOCKED_DRIFT_SEVERITY_UNSUPPORTED = "blocked_drift_severity_unsupported"
BLOCKED_DRIFT_ENVIRONMENT_MISMATCH = "blocked_drift_environment_mismatch"
BLOCKED_DRIFT_SESSION_MISMATCH = "blocked_drift_session_mismatch"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

DEFAULT_SUPPORTED_DRIFT_SEVERITIES = ("none", "low", "moderate", "high", "critical")

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_DRIFT_AUDIT_ID,
    BLOCKED_DRIFT_CHECK_NOT_REQUIRED,
    BLOCKED_DRIFT_AUDIT_MISSING,
    BLOCKED_DRIFT_BASELINE_MISSING,
    BLOCKED_DRIFT_DETECTION_MISSING,
    BLOCKED_UNRESOLVED_DRIFT_DETECTED,
    BLOCKED_DRIFT_SEVERITY_UNSUPPORTED,
    BLOCKED_DRIFT_ENVIRONMENT_MISMATCH,
    BLOCKED_DRIFT_SESSION_MISMATCH,
    MANUAL_REVIEW_REQUIRED,
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ExecutionDriftEscalationContract:
    """Inputs required to validate drift escalation for future controlled planning."""

    drift_audit_id: str
    execution_scope: str
    environment: str
    session_id: str
    sandbox_id: str
    authorization_id: str
    gate_contract_id: str
    replay_scope_id: str
    rollback_plan_id: str
    drift_check_required: bool
    drift_audit_present: bool
    drift_baseline_present: bool
    drift_detection_present: bool
    unresolved_drift_detected: bool
    drift_severity: str
    supported_drift_severities: tuple[str, ...]
    expected_environment: str
    expected_session_id: str
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    sandbox_contract: Any | None = None
    replay_scope_contract: Any | None = None
    rollback_contract: Any | None = None
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_replay_execution_enabled: bool = False
    live_rollback_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    recommendation_logic_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_execution_drift_escalation_contract(
    *,
    drift_audit_id: str,
    execution_scope: str,
    environment: str,
    session_id: str,
    sandbox_id: str,
    authorization_id: str,
    gate_contract_id: str,
    replay_scope_id: str,
    rollback_plan_id: str,
    drift_check_required: bool,
    drift_audit_present: bool,
    drift_baseline_present: bool,
    drift_detection_present: bool,
    unresolved_drift_detected: bool,
    drift_severity: str,
    supported_drift_severities: tuple[str, ...] = DEFAULT_SUPPORTED_DRIFT_SEVERITIES,
    expected_environment: str,
    expected_session_id: str,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_replay_execution_enabled: bool = False,
    live_rollback_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    recommendation_logic_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> ExecutionDriftEscalationContract:
    return ExecutionDriftEscalationContract(
        drift_audit_id=drift_audit_id,
        execution_scope=execution_scope,
        environment=environment,
        session_id=session_id,
        sandbox_id=sandbox_id,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        replay_scope_id=replay_scope_id,
        rollback_plan_id=rollback_plan_id,
        drift_check_required=drift_check_required,
        drift_audit_present=drift_audit_present,
        drift_baseline_present=drift_baseline_present,
        drift_detection_present=drift_detection_present,
        unresolved_drift_detected=unresolved_drift_detected,
        drift_severity=drift_severity,
        supported_drift_severities=tuple(supported_drift_severities),
        expected_environment=expected_environment,
        expected_session_id=expected_session_id,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_replay_execution_enabled=live_replay_execution_enabled,
        live_rollback_execution_enabled=live_rollback_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        recommendation_logic_enabled=recommendation_logic_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_execution_drift_escalation_contract(contract: ExecutionDriftEscalationContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if not contract.drift_audit_id:
        add_blocker(BLOCKED_MISSING_DRIFT_AUDIT_ID, "drift_audit_id_missing")
    if not contract.drift_check_required:
        add_blocker(BLOCKED_DRIFT_CHECK_NOT_REQUIRED, "drift_check_requirement_missing")
    if not contract.drift_audit_present:
        add_blocker(BLOCKED_DRIFT_AUDIT_MISSING, "drift_audit_missing")
    if not contract.drift_baseline_present:
        add_blocker(BLOCKED_DRIFT_BASELINE_MISSING, "drift_baseline_missing")
    if not contract.drift_detection_present:
        add_blocker(BLOCKED_DRIFT_DETECTION_MISSING, "drift_detection_missing")
    if contract.unresolved_drift_detected:
        add_blocker(BLOCKED_UNRESOLVED_DRIFT_DETECTED, "unresolved_drift_detected")
    if contract.drift_severity not in contract.supported_drift_severities:
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "drift_severity_unsupported")
    if contract.environment != contract.expected_environment:
        add_blocker(BLOCKED_DRIFT_ENVIRONMENT_MISMATCH, "drift_environment_mismatch")
    if contract.session_id != contract.expected_session_id:
        add_blocker(BLOCKED_DRIFT_SESSION_MISMATCH, "drift_session_mismatch")

    gate_result = evaluate_controlled_execution_gate_contract(contract.gate_contract) if contract.gate_contract is not None else None
    authorization_result = (
        evaluate_non_production_execution_authorization_contract(contract.authorization_contract)
        if contract.authorization_contract is not None
        else None
    )
    sandbox_result = evaluate_execution_session_sandbox_contract(contract.sandbox_contract) if contract.sandbox_contract is not None else None
    replay_result = evaluate_replay_safe_execution_scope_contract(contract.replay_scope_contract) if contract.replay_scope_contract is not None else None
    rollback_result = evaluate_rollback_execution_governance_contract(contract.rollback_contract) if contract.rollback_contract is not None else None
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "phase2_authorization_not_valid")
    if (
        sandbox_result is not None
        and sandbox_result["status"] != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "phase3_sandbox_not_ready")
    if (
        replay_result is not None
        and replay_result["status"] != REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "phase4_replay_scope_not_ready")
    if (
        rollback_result is not None
        and rollback_result["status"] != ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_DRIFT_SEVERITY_UNSUPPORTED, "phase5_rollback_governance_not_ready")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_execution_drift_escalation_status(candidate_statuses)
    result = {
        "status": status,
        "drift_escalation_ready": status == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "drift_escalation_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "drift_escalation_does_not_bypass_authorization": True,
        },
        "phase3_sandbox_compatibility": {
            "sandbox_linked": bool(contract.sandbox_id),
            "sandbox_status": sandbox_result["status"] if sandbox_result else "not_evaluated",
            "drift_escalation_does_not_bypass_sandbox": True,
        },
        "phase4_replay_scope_compatibility": {
            "replay_scope_linked": bool(contract.replay_scope_id),
            "replay_scope_status": replay_result["status"] if replay_result else "not_evaluated",
            "drift_escalation_does_not_bypass_replay_scope": True,
        },
        "phase5_rollback_governance_compatibility": {
            "rollback_plan_linked": bool(contract.rollback_plan_id),
            "rollback_governance_status": rollback_result["status"] if rollback_result else "not_evaluated",
            "drift_escalation_does_not_bypass_rollback_governance": True,
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
            "automatic_drift_resolution_enabled": False,
            "drift_severity_downgrade_enabled": False,
            "unresolved_drift_allowed": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_execution_drift_escalation_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_DRIFT_SEVERITY_UNSUPPORTED


def summarize_execution_drift_escalation_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "drift_escalation_ready": result["drift_escalation_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "drift_escalation_does_not_bypass_gate": result["phase1_gate_compatibility"]["drift_escalation_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "drift_escalation_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["drift_escalation_does_not_bypass_authorization"],
        "phase3_sandbox_status": result["phase3_sandbox_compatibility"]["sandbox_status"],
        "drift_escalation_does_not_bypass_sandbox": result["phase3_sandbox_compatibility"]["drift_escalation_does_not_bypass_sandbox"],
        "phase4_replay_scope_status": result["phase4_replay_scope_compatibility"]["replay_scope_status"],
        "drift_escalation_does_not_bypass_replay_scope": result["phase4_replay_scope_compatibility"]["drift_escalation_does_not_bypass_replay_scope"],
        "phase5_rollback_governance_status": result["phase5_rollback_governance_compatibility"]["rollback_governance_status"],
        "drift_escalation_does_not_bypass_rollback_governance": result["phase5_rollback_governance_compatibility"]["drift_escalation_does_not_bypass_rollback_governance"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_execution_drift_escalation_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_execution_drift_escalation_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
) -> ExecutionDriftEscalationContract:
    return build_execution_drift_escalation_contract(
        drift_audit_id="drift-audit-v3-4-phase-6",
        execution_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        replay_scope_id="replay-scope-v3-4-phase-4",
        rollback_plan_id="rollback-plan-v3-4-phase-5",
        drift_check_required=True,
        drift_audit_present=True,
        drift_baseline_present=True,
        drift_detection_present=True,
        unresolved_drift_detected=False,
        drift_severity="none",
        supported_drift_severities=DEFAULT_SUPPORTED_DRIFT_SEVERITIES,
        expected_environment="non_production",
        expected_session_id="session-v3-4-phase-3",
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ExecutionDriftEscalationContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    data["sandbox_contract"] = "linked" if contract.sandbox_contract is not None else None
    data["replay_scope_contract"] = "linked" if contract.replay_scope_contract is not None else None
    data["rollback_contract"] = "linked" if contract.rollback_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
