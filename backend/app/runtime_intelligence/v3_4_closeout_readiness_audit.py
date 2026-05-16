"""Deterministic v3.4 closeout and v3.5 readiness audit."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize
from .controlled_execution_gate_contracts import ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
from .controlled_execution_readiness_audit import V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
from .controlled_experiment_isolation_contracts import EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .controlled_runtime_mutation_boundary_contracts import MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_audit_logging_contracts import AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_drift_escalation_contracts import DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .execution_session_sandboxing_contracts import SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .non_production_execution_authorization_contracts import AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
from .replay_safe_execution_scope_contracts import REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
from .rollback_execution_governance_contracts import ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING


V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING = "v3_4_closed_out_ready_for_v3_5_planning"
BLOCKED_MISSING_PHASE_1_CONTRACTS = "blocked_missing_phase_1_contracts"
BLOCKED_MISSING_PHASE_2_CONTRACTS = "blocked_missing_phase_2_contracts"
BLOCKED_MISSING_PHASE_3_CONTRACTS = "blocked_missing_phase_3_contracts"
BLOCKED_MISSING_PHASE_4_CONTRACTS = "blocked_missing_phase_4_contracts"
BLOCKED_MISSING_PHASE_5_CONTRACTS = "blocked_missing_phase_5_contracts"
BLOCKED_MISSING_PHASE_6_CONTRACTS = "blocked_missing_phase_6_contracts"
BLOCKED_MISSING_PHASE_7_CONTRACTS = "blocked_missing_phase_7_contracts"
BLOCKED_MISSING_PHASE_8_CONTRACTS = "blocked_missing_phase_8_contracts"
BLOCKED_MISSING_PHASE_9_CONTRACTS = "blocked_missing_phase_9_contracts"
BLOCKED_MISSING_PHASE_10_READINESS_AUDIT = "blocked_missing_phase_10_readiness_audit"
BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE = "blocked_governance_chain_incompatible"
BLOCKED_PRODUCTION_BEHAVIOR_DETECTED = "blocked_production_behavior_detected"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_MISSING_PHASE_1_CONTRACTS,
    BLOCKED_MISSING_PHASE_2_CONTRACTS,
    BLOCKED_MISSING_PHASE_3_CONTRACTS,
    BLOCKED_MISSING_PHASE_4_CONTRACTS,
    BLOCKED_MISSING_PHASE_5_CONTRACTS,
    BLOCKED_MISSING_PHASE_6_CONTRACTS,
    BLOCKED_MISSING_PHASE_7_CONTRACTS,
    BLOCKED_MISSING_PHASE_8_CONTRACTS,
    BLOCKED_MISSING_PHASE_9_CONTRACTS,
    BLOCKED_MISSING_PHASE_10_READINESS_AUDIT,
    BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    MANUAL_REVIEW_REQUIRED,
    V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
)

EXPECTED_PHASE_CLOSEOUT: tuple[dict[str, str], ...] = (
    {
        "phase_id": "phase_1_controlled_execution_gate",
        "status_field": "phase_1_status",
        "expected_status": ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_1_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_execution_gate_contracts_report.json",
        "report_status_key": "final_execution_gate_readiness_status",
    },
    {
        "phase_id": "phase_2_non_production_authorization",
        "status_field": "phase_2_status",
        "expected_status": AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_2_CONTRACTS,
        "report_path": "docs/generated/v3_4_non_production_execution_authorization_report.json",
        "report_status_key": "final_authorization_readiness_status",
    },
    {
        "phase_id": "phase_3_execution_session_sandboxing",
        "status_field": "phase_3_status",
        "expected_status": SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_3_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_session_sandboxing_report.json",
        "report_status_key": "final_sandbox_readiness_status",
    },
    {
        "phase_id": "phase_4_replay_safe_execution_scope",
        "status_field": "phase_4_status",
        "expected_status": REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_4_CONTRACTS,
        "report_path": "docs/generated/v3_4_replay_safe_execution_scopes_report.json",
        "report_status_key": "final_replay_scope_readiness_status",
    },
    {
        "phase_id": "phase_5_rollback_execution_governance",
        "status_field": "phase_5_status",
        "expected_status": ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_5_CONTRACTS,
        "report_path": "docs/generated/v3_4_rollback_execution_governance_report.json",
        "report_status_key": "final_rollback_governance_readiness_status",
    },
    {
        "phase_id": "phase_6_execution_drift_escalation",
        "status_field": "phase_6_status",
        "expected_status": DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_6_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_drift_escalation_report.json",
        "report_status_key": "final_drift_escalation_readiness_status",
    },
    {
        "phase_id": "phase_7_controlled_runtime_mutation_boundary",
        "status_field": "phase_7_status",
        "expected_status": MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_7_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_runtime_mutation_boundaries_report.json",
        "report_status_key": "final_mutation_boundary_readiness_status",
    },
    {
        "phase_id": "phase_8_controlled_experiment_isolation",
        "status_field": "phase_8_status",
        "expected_status": EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_8_CONTRACTS,
        "report_path": "docs/generated/v3_4_controlled_experiment_isolation_report.json",
        "report_status_key": "final_experiment_isolation_readiness_status",
    },
    {
        "phase_id": "phase_9_execution_audit_logging",
        "status_field": "phase_9_status",
        "expected_status": AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_9_CONTRACTS,
        "report_path": "docs/generated/v3_4_execution_audit_logging_report.json",
        "report_status_key": "final_audit_logging_readiness_status",
    },
    {
        "phase_id": "phase_10_controlled_execution_readiness_audit",
        "status_field": "phase_10_status",
        "expected_status": V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
        "missing_status": BLOCKED_MISSING_PHASE_10_READINESS_AUDIT,
        "report_path": "docs/generated/v3_4_controlled_execution_readiness_audit_report.json",
        "report_status_key": "final_v3_4_readiness_status",
    },
)


@dataclass(frozen=True)
class V34CloseoutReadinessAuditContract:
    closeout_audit_id: str
    phase_1_status: str
    phase_2_status: str
    phase_3_status: str
    phase_4_status: str
    phase_5_status: str
    phase_6_status: str
    phase_7_status: str
    phase_8_status: str
    phase_9_status: str
    phase_10_status: str
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


def build_v3_4_closeout_readiness_audit_contract(**kwargs: Any) -> V34CloseoutReadinessAuditContract:
    return V34CloseoutReadinessAuditContract(**kwargs)


def default_v3_4_closeout_readiness_audit_contract(
    phase_report_evidence: tuple[dict[str, Any], ...] = (),
) -> V34CloseoutReadinessAuditContract:
    return build_v3_4_closeout_readiness_audit_contract(
        closeout_audit_id="closeout-audit-v3-4-v3-5-readiness",
        phase_1_status=ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_2_status=AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_3_status=SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_4_status=REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_5_status=ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_6_status=DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_7_status=MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_8_status=EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_9_status=AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        phase_10_status=V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
        governance_chain_compatible=True,
        production_behavior_detected=False,
        manual_review_required=False,
        phase_report_evidence=phase_report_evidence,
    )


def load_v3_4_closeout_phase_reports(repo_root: Path | str | None = None) -> tuple[dict[str, Any], ...]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    evidence: list[dict[str, Any]] = []
    for phase in EXPECTED_PHASE_CLOSEOUT:
        path = root / phase["report_path"]
        if not path.exists():
            evidence.append(_missing_evidence(phase, "report_missing"))
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            evidence.append(_missing_evidence(phase, type(exc).__name__, missing=False))
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


def build_v3_4_closeout_readiness_audit_from_reports(
    repo_root: Path | str | None = None,
) -> V34CloseoutReadinessAuditContract:
    evidence = load_v3_4_closeout_phase_reports(repo_root)
    values = {phase["status_field"]: _status_from_evidence(evidence, phase) for phase in EXPECTED_PHASE_CLOSEOUT}
    return build_v3_4_closeout_readiness_audit_contract(
        closeout_audit_id="closeout-audit-v3-4-v3-5-readiness",
        governance_chain_compatible=all(row["status"] == row["expected_status"] for row in evidence),
        production_behavior_detected=any(bool(row.get("production_behavior_detected")) for row in evidence),
        manual_review_required=False,
        phase_report_evidence=evidence,
        **values,
    )


def evaluate_v3_4_closeout_readiness_audit(contract: V34CloseoutReadinessAuditContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    data = asdict(contract)
    for index, phase in enumerate(EXPECTED_PHASE_CLOSEOUT, start=1):
        if data[phase["status_field"]] != phase["expected_status"]:
            add_blocker(phase["missing_status"], f"phase_{index}_not_ready")
    if not contract.governance_chain_compatible:
        add_blocker(BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE, "governance_chain_incompatible")
    if contract.production_behavior_detected or _contract_production_behavior_detected(contract):
        add_blocker(BLOCKED_PRODUCTION_BEHAVIOR_DETECTED, "production_behavior_detected")
    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_v3_4_closeout_readiness(candidate_statuses)
    result = {
        "status": status,
        "v3_4_closed_out": status == V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
        "v3_5_planning_may_begin": status == V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
        "controlled_execution_authorized": False,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": asdict(contract),
        "phase_closeout": _phase_closeout(contract),
        "phase_report_evidence": list(contract.phase_report_evidence),
        "governance_chain_compatible": contract.governance_chain_compatible,
        "production_behavior_detected": contract.production_behavior_detected or _contract_production_behavior_detected(contract),
        "prohibition_checks": _prohibition_checks(contract),
        "audit_only": True,
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_v3_4_closeout_readiness(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE


def summarize_v3_4_closeout_readiness_audit(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "v3_4_closed_out": result["v3_4_closed_out"],
        "v3_5_planning_may_begin": result["v3_5_planning_may_begin"],
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


def serialize_v3_4_closeout_readiness_audit(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def _phase_closeout(contract: V34CloseoutReadinessAuditContract) -> list[dict[str, Any]]:
    data = asdict(contract)
    return [
        {
            "phase_id": phase["phase_id"],
            "status": data[phase["status_field"]],
            "expected_status": phase["expected_status"],
            "closed_out": data[phase["status_field"]] == phase["expected_status"],
        }
        for phase in EXPECTED_PHASE_CLOSEOUT
    ]


def _status_from_evidence(evidence: tuple[dict[str, Any], ...], phase: dict[str, str]) -> str:
    for row in evidence:
        if row["phase_id"] == phase["phase_id"]:
            return row["status"]
    return ""


def _missing_evidence(phase: dict[str, str], error: str, missing: bool = True) -> dict[str, Any]:
    return {
        "phase_id": phase["phase_id"],
        "report_path": phase["report_path"],
        "readable": False,
        "missing": missing,
        "status": "",
        "expected_status": phase["expected_status"],
        "production_behavior_detected": False,
        "error": error,
    }


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


def _contract_production_behavior_detected(contract: V34CloseoutReadinessAuditContract) -> bool:
    return any(_prohibition_checks(contract).values())


def _prohibition_checks(contract: V34CloseoutReadinessAuditContract) -> dict[str, bool]:
    return {
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
    }


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
