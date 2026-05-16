"""Planning-only controlled execution readiness audit for v3.4."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
from .controlled_experiment_isolation_contracts import EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .controlled_runtime_mutation_boundary_contracts import MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_audit_logging_contracts import AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_drift_escalation_contracts import DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_session_sandboxing_contracts import SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .non_production_execution_authorization_contracts import AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
from .replay_safe_execution_scope_contracts import REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .rollback_execution_governance_contracts import ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING


V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING = "v3_4_ready_for_future_controlled_execution_planning"
BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS = "blocked_missing_controlled_execution_gate_contracts"
BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS = "blocked_missing_non_production_authorization_contracts"
BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS = "blocked_missing_execution_session_sandboxing_contracts"
BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS = "blocked_missing_replay_safe_execution_scope_contracts"
BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS = "blocked_missing_rollback_execution_governance_contracts"
BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS = "blocked_missing_execution_drift_escalation_contracts"
BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS = "blocked_missing_controlled_runtime_mutation_boundary_contracts"
BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS = "blocked_missing_controlled_experiment_isolation_contracts"
BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS = "blocked_missing_execution_audit_logging_contracts"
BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN = "blocked_incompatible_governance_chain"
BLOCKED_PRODUCTION_BEHAVIOR_DETECTED = "blocked_production_behavior_detected"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS,
    BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS,
    BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS,
    BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS,
    BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    MANUAL_REVIEW_REQUIRED,
    V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
)

EXPECTED_PHASE_READINESS: tuple[dict[str, str], ...] = (
    {
        "phase_id": "phase_1_controlled_execution_gate",
        "status_field": "controlled_execution_gate_status",
        "expected_status": ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_execution_gate_contracts_report.json",
        "report_status_key": "final_execution_gate_readiness_status",
    },
    {
        "phase_id": "phase_2_non_production_authorization",
        "status_field": "non_production_authorization_status",
        "expected_status": AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS,
        "report_path": "docs/generated/v3_4_non_production_execution_authorization_report.json",
        "report_status_key": "final_authorization_readiness_status",
    },
    {
        "phase_id": "phase_3_execution_session_sandboxing",
        "status_field": "execution_session_sandboxing_status",
        "expected_status": SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_session_sandboxing_report.json",
        "report_status_key": "final_sandbox_readiness_status",
    },
    {
        "phase_id": "phase_4_replay_safe_execution_scope",
        "status_field": "replay_safe_execution_scope_status",
        "expected_status": REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS,
        "report_path": "docs/generated/v3_4_replay_safe_execution_scopes_report.json",
        "report_status_key": "final_replay_scope_readiness_status",
    },
    {
        "phase_id": "phase_5_rollback_execution_governance",
        "status_field": "rollback_execution_governance_status",
        "expected_status": ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS,
        "report_path": "docs/generated/v3_4_rollback_execution_governance_report.json",
        "report_status_key": "final_rollback_governance_readiness_status",
    },
    {
        "phase_id": "phase_6_execution_drift_escalation",
        "status_field": "execution_drift_escalation_status",
        "expected_status": DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_drift_escalation_report.json",
        "report_status_key": "final_drift_escalation_readiness_status",
    },
    {
        "phase_id": "phase_7_controlled_runtime_mutation_boundary",
        "status_field": "controlled_runtime_mutation_boundary_status",
        "expected_status": MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_runtime_mutation_boundaries_report.json",
        "report_status_key": "final_mutation_boundary_readiness_status",
    },
    {
        "phase_id": "phase_8_controlled_experiment_isolation",
        "status_field": "controlled_experiment_isolation_status",
        "expected_status": EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_experiment_isolation_report.json",
        "report_status_key": "final_experiment_isolation_readiness_status",
    },
    {
        "phase_id": "phase_9_execution_audit_logging",
        "status_field": "execution_audit_logging_status",
        "expected_status": AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_audit_logging_report.json",
        "report_status_key": "final_audit_logging_readiness_status",
    },
)


@dataclass(frozen=True)
class ControlledExecutionReadinessAuditContract:
    """Inputs required to audit the complete v3.4 controlled execution planning chain."""

    readiness_audit_id: str
    controlled_execution_gate_status: str
    non_production_authorization_status: str
    execution_session_sandboxing_status: str
    replay_safe_execution_scope_status: str
    rollback_execution_governance_status: str
    execution_drift_escalation_status: str
    controlled_runtime_mutation_boundary_status: str
    controlled_experiment_isolation_status: str
    execution_audit_logging_status: str
    governance_chain_compatible: bool
    production_behavior_detected: bool
    manual_review_required: bool
    phase_report_evidence: tuple[dict[str, Any], ...] = ()
    execution_enabled: bool = False
    controlled_execution_authorized: bool = False
    production_execution_enabled: bool = False
    production_runtime_routing_authorized: bool = False
    runtime_manifest_consumption_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False
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


def build_controlled_execution_readiness_audit_contract(
    *,
    readiness_audit_id: str,
    controlled_execution_gate_status: str,
    non_production_authorization_status: str,
    execution_session_sandboxing_status: str,
    replay_safe_execution_scope_status: str,
    rollback_execution_governance_status: str,
    execution_drift_escalation_status: str,
    controlled_runtime_mutation_boundary_status: str,
    controlled_experiment_isolation_status: str,
    execution_audit_logging_status: str,
    governance_chain_compatible: bool,
    production_behavior_detected: bool,
    manual_review_required: bool,
    phase_report_evidence: tuple[dict[str, Any], ...] = (),
    execution_enabled: bool = False,
    controlled_execution_authorized: bool = False,
    production_execution_enabled: bool = False,
    production_runtime_routing_authorized: bool = False,
    runtime_manifest_consumption_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
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
) -> ControlledExecutionReadinessAuditContract:
    return ControlledExecutionReadinessAuditContract(
        readiness_audit_id=readiness_audit_id,
        controlled_execution_gate_status=controlled_execution_gate_status,
        non_production_authorization_status=non_production_authorization_status,
        execution_session_sandboxing_status=execution_session_sandboxing_status,
        replay_safe_execution_scope_status=replay_safe_execution_scope_status,
        rollback_execution_governance_status=rollback_execution_governance_status,
        execution_drift_escalation_status=execution_drift_escalation_status,
        controlled_runtime_mutation_boundary_status=controlled_runtime_mutation_boundary_status,
        controlled_experiment_isolation_status=controlled_experiment_isolation_status,
        execution_audit_logging_status=execution_audit_logging_status,
        governance_chain_compatible=governance_chain_compatible,
        production_behavior_detected=production_behavior_detected,
        manual_review_required=manual_review_required,
        phase_report_evidence=tuple(phase_report_evidence),
        execution_enabled=execution_enabled,
        controlled_execution_authorized=controlled_execution_authorized,
        production_execution_enabled=production_execution_enabled,
        production_runtime_routing_authorized=production_runtime_routing_authorized,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
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
    )


def default_controlled_execution_readiness_audit_contract(
    phase_report_evidence: tuple[dict[str, Any], ...] = (),
) -> ControlledExecutionReadinessAuditContract:
    return build_controlled_execution_readiness_audit_contract(
        readiness_audit_id="readiness-audit-v3-4-phase-10",
        controlled_execution_gate_status=ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        non_production_authorization_status=AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        execution_session_sandboxing_status=SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        replay_safe_execution_scope_status=REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        rollback_execution_governance_status=ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        execution_drift_escalation_status=DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        controlled_runtime_mutation_boundary_status=MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        controlled_experiment_isolation_status=EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        execution_audit_logging_status=AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        governance_chain_compatible=True,
        production_behavior_detected=False,
        manual_review_required=False,
        phase_report_evidence=phase_report_evidence,
    )


def load_v3_4_phase_reports(repo_root: Path | str | None = None) -> tuple[dict[str, Any], ...]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    evidence: list[dict[str, Any]] = []
    for phase in EXPECTED_PHASE_READINESS:
        path = root / phase["report_path"]
        if not path.exists():
            evidence.append(
                {
                    "phase_id": phase["phase_id"],
                    "report_path": phase["report_path"],
                    "readable": False,
                    "missing": True,
                    "status": "",
                    "expected_status": phase["expected_status"],
                    "production_behavior_detected": False,
                    "error": "report_missing",
                }
            )
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            evidence.append(
                {
                    "phase_id": phase["phase_id"],
                    "report_path": phase["report_path"],
                    "readable": False,
                    "missing": False,
                    "status": "",
                    "expected_status": phase["expected_status"],
                    "production_behavior_detected": False,
                    "error": type(exc).__name__,
                }
            )
            continue
        evidence.append(
            {
                "phase_id": phase["phase_id"],
                "report_path": phase["report_path"],
                "readable": True,
                "missing": False,
                "status": str(report.get(phase["report_status_key"], "")),
                "expected_status": phase["expected_status"],
                "deterministic_hash_present": bool(report.get("deterministic_hash")),
                "production_behavior_detected": _report_production_behavior_detected(report),
            }
        )
    return tuple(evidence)


def build_controlled_execution_readiness_audit_from_reports(
    repo_root: Path | str | None = None,
) -> ControlledExecutionReadinessAuditContract:
    evidence = load_v3_4_phase_reports(repo_root)
    values = {phase["status_field"]: _status_from_evidence(evidence, phase) for phase in EXPECTED_PHASE_READINESS}
    governance_chain_compatible = all(row["status"] == row["expected_status"] for row in evidence)
    production_behavior_detected = any(bool(row.get("production_behavior_detected")) for row in evidence)
    return build_controlled_execution_readiness_audit_contract(
        readiness_audit_id="readiness-audit-v3-4-phase-10",
        governance_chain_compatible=governance_chain_compatible,
        production_behavior_detected=production_behavior_detected,
        manual_review_required=False,
        phase_report_evidence=evidence,
        **values,
    )


def evaluate_controlled_execution_readiness_audit(
    contract: ControlledExecutionReadinessAuditContract,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.controlled_execution_gate_status != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS, "phase1_controlled_execution_gate_not_ready")
    if contract.non_production_authorization_status != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS, "phase2_non_production_authorization_not_ready")
    if contract.execution_session_sandboxing_status != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS, "phase3_execution_session_sandboxing_not_ready")
    if contract.replay_safe_execution_scope_status != REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS, "phase4_replay_safe_execution_scope_not_ready")
    if contract.rollback_execution_governance_status != ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS, "phase5_rollback_execution_governance_not_ready")
    if contract.execution_drift_escalation_status != DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS, "phase6_execution_drift_escalation_not_ready")
    if contract.controlled_runtime_mutation_boundary_status != MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS, "phase7_controlled_runtime_mutation_boundary_not_ready")
    if contract.controlled_experiment_isolation_status != EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS, "phase8_controlled_experiment_isolation_not_ready")
    if contract.execution_audit_logging_status != AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS, "phase9_execution_audit_logging_not_ready")
    if not contract.governance_chain_compatible:
        add_blocker(BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN, "governance_chain_incompatible")
    if contract.production_behavior_detected or _contract_production_behavior_detected(contract):
        add_blocker(BLOCKED_PRODUCTION_BEHAVIOR_DETECTED, "production_behavior_detected")
    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_v3_4_controlled_execution_readiness(candidate_statuses)
    result = {
        "status": status,
        "ready_for_future_controlled_execution_planning": status == V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
        "controlled_execution_authorized": False,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase_readiness": _phase_readiness(contract),
        "phase_report_evidence": list(contract.phase_report_evidence),
        "governance_chain_compatible": contract.governance_chain_compatible,
        "production_behavior_detected": contract.production_behavior_detected or _contract_production_behavior_detected(contract),
        "prohibition_checks": {
            "execution_enabled": contract.execution_enabled,
            "controlled_execution_authorized": False,
            "production_execution_enabled": contract.production_execution_enabled,
            "production_runtime_routing_authorized": contract.production_runtime_routing_authorized,
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
        },
        "audit_only": True,
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_v3_4_controlled_execution_readiness(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN


def summarize_controlled_execution_readiness_audit(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "ready_for_future_controlled_execution_planning": result["ready_for_future_controlled_execution_planning"],
        "controlled_execution_authorized": result["controlled_execution_authorized"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "governance_chain_compatible": result["governance_chain_compatible"],
        "production_behavior_detected": result["production_behavior_detected"],
        "deterministic_hash": result["deterministic_hash"],
        "audit_only": result["audit_only"],
        "planning_only": result["planning_only"],
        **result["prohibition_checks"],
    }


def serialize_controlled_execution_readiness_audit(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def _status_from_evidence(evidence: tuple[dict[str, Any], ...], phase: dict[str, str]) -> str:
    for row in evidence:
        if row["phase_id"] == phase["phase_id"]:
            return row["status"]
    return ""


def _phase_readiness(contract: ControlledExecutionReadinessAuditContract) -> list[dict[str, Any]]:
    readiness = []
    data = asdict(contract)
    for phase in EXPECTED_PHASE_READINESS:
        actual = data[phase["status_field"]]
        readiness.append(
            {
                "phase_id": phase["phase_id"],
                "status": actual,
                "expected_status": phase["expected_status"],
                "ready": actual == phase["expected_status"],
            }
        )
    return readiness


def _report_production_behavior_detected(report: dict[str, Any]) -> bool:
    prohibited_true_keys = (
        "execution_enabled",
        "controlled_execution_authorized",
        "production_execution_enabled",
        "production_runtime_routing_authorized",
        "runtime_manifest_consumption_enabled",
        "production_authoritative_manifest_treatment",
        "live_runtime_execution_enabled",
        "live_replay_execution_enabled",
        "live_rollback_execution_enabled",
        "live_synthesis_execution_enabled",
        "live_decision_routing_enabled",
        "recommendation_logic_enabled",
        "autonomous_planner_mutation_enabled",
        "persistent_mutation_enabled",
        "state_writes_enabled",
        "external_side_effects_enabled",
        "experiment_execution_enabled",
        "audit_log_writing_enabled",
        "production_state_access_enabled",
        "production_mutation_enabled",
        "mutation_execution_enabled",
    )
    return any(report.get(key) is True for key in prohibited_true_keys)


def _contract_production_behavior_detected(contract: ControlledExecutionReadinessAuditContract) -> bool:
    return any(
        (
            contract.execution_enabled,
            contract.controlled_execution_authorized,
            contract.production_execution_enabled,
            contract.production_runtime_routing_authorized,
            contract.runtime_manifest_consumption_enabled,
            contract.production_authoritative_manifest_treatment,
            contract.live_runtime_execution_enabled,
            contract.live_replay_execution_enabled,
            contract.live_rollback_execution_enabled,
            contract.live_synthesis_execution_enabled,
            contract.live_decision_routing_enabled,
            contract.recommendation_logic_enabled,
            contract.autonomous_planner_mutation_enabled,
            contract.persistent_mutation_enabled,
            contract.state_writes_enabled,
            contract.external_side_effects_enabled,
            contract.experiment_execution_enabled,
            contract.audit_log_writing_enabled,
            contract.production_state_access_enabled,
        )
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ControlledExecutionReadinessAuditContract) -> dict[str, Any]:
    return asdict(contract)


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
