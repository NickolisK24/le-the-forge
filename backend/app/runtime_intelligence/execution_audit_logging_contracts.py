"""Planning-only execution audit logging contracts for v3.4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_execution_gate_contract,
)
from .controlled_experiment_isolation_contracts import (
    EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_experiment_isolation_contract,
)
from .controlled_runtime_mutation_boundary_contracts import (
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    evaluate_controlled_runtime_mutation_boundary_contract,
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


AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "audit_logging_ready_for_controlled_execution_planning"
BLOCKED_MISSING_AUDIT_RECORD_ID = "blocked_missing_audit_record_id"
BLOCKED_AUDIT_EVENT_TYPE_MISSING = "blocked_audit_event_type_missing"
BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED = "blocked_audit_event_type_unsupported"
BLOCKED_AUDIT_HASH_MISSING = "blocked_audit_hash_missing"
BLOCKED_AUDIT_LINEAGE_MISSING = "blocked_audit_lineage_missing"
BLOCKED_AUDIT_TIMESTAMP_MISSING = "blocked_audit_timestamp_missing"
BLOCKED_AUDIT_ACTOR_MISSING = "blocked_audit_actor_missing"
BLOCKED_AUDIT_ENVIRONMENT_MISMATCH = "blocked_audit_environment_mismatch"
BLOCKED_AUDIT_SESSION_MISMATCH = "blocked_audit_session_mismatch"
BLOCKED_AUDIT_WRITE_REQUESTED = "blocked_audit_write_requested"
BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK = "blocked_missing_experiment_isolation_link"
BLOCKED_MISSING_MUTATION_BOUNDARY_LINK = "blocked_missing_mutation_boundary_link"
BLOCKED_MISSING_DRIFT_ESCALATION_LINK = "blocked_missing_drift_escalation_link"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

DEFAULT_SUPPORTED_AUDIT_EVENT_TYPES = (
    "controlled_execution_planning_audit",
    "governance_linkage_audit",
    "non_production_boundary_audit",
    "fail_visible_blocker_audit",
)

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_AUDIT_RECORD_ID,
    BLOCKED_AUDIT_EVENT_TYPE_MISSING,
    BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED,
    BLOCKED_AUDIT_HASH_MISSING,
    BLOCKED_AUDIT_LINEAGE_MISSING,
    BLOCKED_AUDIT_TIMESTAMP_MISSING,
    BLOCKED_AUDIT_ACTOR_MISSING,
    BLOCKED_AUDIT_ENVIRONMENT_MISMATCH,
    BLOCKED_AUDIT_SESSION_MISMATCH,
    BLOCKED_AUDIT_WRITE_REQUESTED,
    BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK,
    BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    MANUAL_REVIEW_REQUIRED,
    AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ExecutionAuditLoggingContract:
    """Inputs required to validate audit logging requirements for future controlled planning."""

    audit_record_id: str
    audit_event_type: str
    execution_scope: str
    environment: str
    session_id: str
    sandbox_id: str
    authorization_id: str
    gate_contract_id: str
    replay_scope_id: str
    rollback_plan_id: str
    drift_audit_id: str
    mutation_boundary_id: str
    experiment_id: str
    audit_hash_present: bool
    audit_lineage_present: bool
    audit_timestamp_present: bool
    audit_actor_present: bool
    audit_write_requested: bool
    supported_audit_event_types: tuple[str, ...]
    expected_environment: str
    expected_session_id: str
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    sandbox_contract: Any | None = None
    replay_scope_contract: Any | None = None
    rollback_contract: Any | None = None
    drift_escalation_contract: Any | None = None
    mutation_boundary_contract: Any | None = None
    experiment_isolation_contract: Any | None = None
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
    experiment_execution_enabled: bool = False
    audit_log_writing_enabled: bool = False
    production_state_access_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_execution_audit_logging_contract(
    *,
    audit_record_id: str,
    audit_event_type: str,
    execution_scope: str,
    environment: str,
    session_id: str,
    sandbox_id: str,
    authorization_id: str,
    gate_contract_id: str,
    replay_scope_id: str,
    rollback_plan_id: str,
    drift_audit_id: str,
    mutation_boundary_id: str,
    experiment_id: str,
    audit_hash_present: bool,
    audit_lineage_present: bool,
    audit_timestamp_present: bool,
    audit_actor_present: bool,
    audit_write_requested: bool,
    supported_audit_event_types: tuple[str, ...] = DEFAULT_SUPPORTED_AUDIT_EVENT_TYPES,
    expected_environment: str,
    expected_session_id: str,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
    drift_escalation_contract: Any | None = None,
    mutation_boundary_contract: Any | None = None,
    experiment_isolation_contract: Any | None = None,
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
    experiment_execution_enabled: bool = False,
    audit_log_writing_enabled: bool = False,
    production_state_access_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> ExecutionAuditLoggingContract:
    return ExecutionAuditLoggingContract(
        audit_record_id=audit_record_id,
        audit_event_type=audit_event_type,
        execution_scope=execution_scope,
        environment=environment,
        session_id=session_id,
        sandbox_id=sandbox_id,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        replay_scope_id=replay_scope_id,
        rollback_plan_id=rollback_plan_id,
        drift_audit_id=drift_audit_id,
        mutation_boundary_id=mutation_boundary_id,
        experiment_id=experiment_id,
        audit_hash_present=audit_hash_present,
        audit_lineage_present=audit_lineage_present,
        audit_timestamp_present=audit_timestamp_present,
        audit_actor_present=audit_actor_present,
        audit_write_requested=audit_write_requested,
        supported_audit_event_types=tuple(supported_audit_event_types),
        expected_environment=expected_environment,
        expected_session_id=expected_session_id,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
        drift_escalation_contract=drift_escalation_contract,
        mutation_boundary_contract=mutation_boundary_contract,
        experiment_isolation_contract=experiment_isolation_contract,
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
        experiment_execution_enabled=experiment_execution_enabled,
        audit_log_writing_enabled=audit_log_writing_enabled,
        production_state_access_enabled=production_state_access_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_execution_audit_logging_contract(contract: ExecutionAuditLoggingContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if not contract.audit_record_id:
        add_blocker(BLOCKED_MISSING_AUDIT_RECORD_ID, "audit_record_id_missing")
    if not contract.audit_event_type:
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_MISSING, "audit_event_type_missing")
    if contract.audit_event_type not in contract.supported_audit_event_types:
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "audit_event_type_unsupported")
    if not contract.audit_hash_present:
        add_blocker(BLOCKED_AUDIT_HASH_MISSING, "audit_hash_missing")
    if not contract.audit_lineage_present:
        add_blocker(BLOCKED_AUDIT_LINEAGE_MISSING, "audit_lineage_missing")
    if not contract.audit_timestamp_present:
        add_blocker(BLOCKED_AUDIT_TIMESTAMP_MISSING, "audit_timestamp_missing")
    if not contract.audit_actor_present:
        add_blocker(BLOCKED_AUDIT_ACTOR_MISSING, "audit_actor_missing")
    if contract.environment != contract.expected_environment:
        add_blocker(BLOCKED_AUDIT_ENVIRONMENT_MISMATCH, "audit_environment_mismatch")
    if contract.session_id != contract.expected_session_id:
        add_blocker(BLOCKED_AUDIT_SESSION_MISMATCH, "audit_session_mismatch")
    if contract.audit_write_requested:
        add_blocker(BLOCKED_AUDIT_WRITE_REQUESTED, "audit_write_requested")
    if not contract.experiment_id:
        add_blocker(BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK, "experiment_isolation_link_missing")
    if not contract.mutation_boundary_id:
        add_blocker(BLOCKED_MISSING_MUTATION_BOUNDARY_LINK, "mutation_boundary_link_missing")
    if not contract.drift_audit_id:
        add_blocker(BLOCKED_MISSING_DRIFT_ESCALATION_LINK, "drift_escalation_link_missing")

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
    mutation_result = (
        evaluate_controlled_runtime_mutation_boundary_contract(contract.mutation_boundary_contract)
        if contract.mutation_boundary_contract is not None
        else None
    )
    experiment_result = (
        evaluate_controlled_experiment_isolation_contract(contract.experiment_isolation_contract)
        if contract.experiment_isolation_contract is not None
        else None
    )
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase2_authorization_not_valid")
    if (
        sandbox_result is not None
        and sandbox_result["status"] != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase3_sandbox_not_ready")
    if (
        replay_result is not None
        and replay_result["status"] != REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase4_replay_scope_not_ready")
    if (
        rollback_result is not None
        and rollback_result["status"] != ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase5_rollback_governance_not_ready")
    if (
        drift_result is not None
        and drift_result["status"] != DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase6_drift_escalation_not_ready")
    if (
        mutation_result is not None
        and mutation_result["status"] != MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase7_mutation_boundary_not_ready")
    if (
        experiment_result is not None
        and experiment_result["status"] != EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED, "phase8_experiment_isolation_not_ready")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_execution_audit_logging_status(candidate_statuses)
    result = {
        "status": status,
        "audit_logging_ready": status == AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "audit_logging_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "audit_logging_does_not_bypass_authorization": True,
        },
        "phase3_sandbox_compatibility": {
            "sandbox_linked": bool(contract.sandbox_id),
            "sandbox_status": sandbox_result["status"] if sandbox_result else "not_evaluated",
            "audit_logging_does_not_bypass_sandbox": True,
        },
        "phase4_replay_scope_compatibility": {
            "replay_scope_linked": bool(contract.replay_scope_id),
            "replay_scope_status": replay_result["status"] if replay_result else "not_evaluated",
            "audit_logging_does_not_bypass_replay_scope": True,
        },
        "phase5_rollback_governance_compatibility": {
            "rollback_plan_linked": bool(contract.rollback_plan_id),
            "rollback_governance_status": rollback_result["status"] if rollback_result else "not_evaluated",
            "audit_logging_does_not_bypass_rollback_governance": True,
        },
        "phase6_drift_escalation_compatibility": {
            "drift_audit_linked": bool(contract.drift_audit_id),
            "drift_escalation_status": drift_result["status"] if drift_result else "not_evaluated",
            "audit_logging_does_not_bypass_drift_escalation": True,
        },
        "phase7_mutation_boundary_compatibility": {
            "mutation_boundary_linked": bool(contract.mutation_boundary_id),
            "mutation_boundary_status": mutation_result["status"] if mutation_result else "not_evaluated",
            "audit_logging_does_not_bypass_mutation_boundary": True,
        },
        "phase8_experiment_isolation_compatibility": {
            "experiment_isolation_linked": bool(contract.experiment_id),
            "experiment_isolation_status": experiment_result["status"] if experiment_result else "not_evaluated",
            "audit_logging_does_not_bypass_experiment_isolation": True,
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
            "experiment_execution_enabled": contract.experiment_execution_enabled,
            "audit_log_writing_enabled": contract.audit_log_writing_enabled,
            "production_state_access_enabled": contract.production_state_access_enabled,
            "production_mutation_enabled": False,
            "mutation_execution_enabled": False,
            "cross_experiment_state_access_enabled": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_execution_audit_logging_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED


def summarize_execution_audit_logging_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "audit_logging_ready": result["audit_logging_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "audit_logging_does_not_bypass_gate": result["phase1_gate_compatibility"]["audit_logging_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "audit_logging_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["audit_logging_does_not_bypass_authorization"],
        "phase3_sandbox_status": result["phase3_sandbox_compatibility"]["sandbox_status"],
        "audit_logging_does_not_bypass_sandbox": result["phase3_sandbox_compatibility"]["audit_logging_does_not_bypass_sandbox"],
        "phase4_replay_scope_status": result["phase4_replay_scope_compatibility"]["replay_scope_status"],
        "audit_logging_does_not_bypass_replay_scope": result["phase4_replay_scope_compatibility"]["audit_logging_does_not_bypass_replay_scope"],
        "phase5_rollback_governance_status": result["phase5_rollback_governance_compatibility"]["rollback_governance_status"],
        "audit_logging_does_not_bypass_rollback_governance": result["phase5_rollback_governance_compatibility"]["audit_logging_does_not_bypass_rollback_governance"],
        "phase6_drift_escalation_status": result["phase6_drift_escalation_compatibility"]["drift_escalation_status"],
        "audit_logging_does_not_bypass_drift_escalation": result["phase6_drift_escalation_compatibility"]["audit_logging_does_not_bypass_drift_escalation"],
        "phase7_mutation_boundary_status": result["phase7_mutation_boundary_compatibility"]["mutation_boundary_status"],
        "audit_logging_does_not_bypass_mutation_boundary": result["phase7_mutation_boundary_compatibility"]["audit_logging_does_not_bypass_mutation_boundary"],
        "phase8_experiment_isolation_status": result["phase8_experiment_isolation_compatibility"]["experiment_isolation_status"],
        "audit_logging_does_not_bypass_experiment_isolation": result["phase8_experiment_isolation_compatibility"]["audit_logging_does_not_bypass_experiment_isolation"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_execution_audit_logging_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_execution_audit_logging_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    replay_scope_contract: Any | None = None,
    rollback_contract: Any | None = None,
    drift_escalation_contract: Any | None = None,
    mutation_boundary_contract: Any | None = None,
    experiment_isolation_contract: Any | None = None,
) -> ExecutionAuditLoggingContract:
    return build_execution_audit_logging_contract(
        audit_record_id="audit-record-v3-4-phase-9",
        audit_event_type="controlled_execution_planning_audit",
        execution_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        replay_scope_id="replay-scope-v3-4-phase-4",
        rollback_plan_id="rollback-plan-v3-4-phase-5",
        drift_audit_id="drift-audit-v3-4-phase-6",
        mutation_boundary_id="mutation-boundary-v3-4-phase-7",
        experiment_id="experiment-v3-4-phase-8",
        audit_hash_present=True,
        audit_lineage_present=True,
        audit_timestamp_present=True,
        audit_actor_present=True,
        audit_write_requested=False,
        supported_audit_event_types=DEFAULT_SUPPORTED_AUDIT_EVENT_TYPES,
        expected_environment="non_production",
        expected_session_id="session-v3-4-phase-3",
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        replay_scope_contract=replay_scope_contract,
        rollback_contract=rollback_contract,
        drift_escalation_contract=drift_escalation_contract,
        mutation_boundary_contract=mutation_boundary_contract,
        experiment_isolation_contract=experiment_isolation_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ExecutionAuditLoggingContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    data["sandbox_contract"] = "linked" if contract.sandbox_contract is not None else None
    data["replay_scope_contract"] = "linked" if contract.replay_scope_contract is not None else None
    data["rollback_contract"] = "linked" if contract.rollback_contract is not None else None
    data["drift_escalation_contract"] = "linked" if contract.drift_escalation_contract is not None else None
    data["mutation_boundary_contract"] = "linked" if contract.mutation_boundary_contract is not None else None
    data["experiment_isolation_contract"] = "linked" if contract.experiment_isolation_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
