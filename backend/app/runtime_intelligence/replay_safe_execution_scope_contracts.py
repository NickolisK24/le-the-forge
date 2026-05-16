"""Planning-only replay-safe execution scope contracts for v3.4."""

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


REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING = "replay_scope_ready_for_controlled_execution_planning"
BLOCKED_MISSING_REPLAY_SCOPE_ID = "blocked_missing_replay_scope_id"
BLOCKED_MISSING_REPLAY_IDENTITY = "blocked_missing_replay_identity"
BLOCKED_REPLAY_NOT_REQUIRED = "blocked_replay_not_required"
BLOCKED_REPLAY_CAPTURE_DISABLED = "blocked_replay_capture_disabled"
BLOCKED_REPLAY_MANIFEST_MISSING = "blocked_replay_manifest_missing"
BLOCKED_REPLAY_MANIFEST_UNTRUSTED = "blocked_replay_manifest_untrusted"
BLOCKED_REPLAY_LINEAGE_MISSING = "blocked_replay_lineage_missing"
BLOCKED_REPLAY_SCOPE_UNSUPPORTED = "blocked_replay_scope_unsupported"
BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED = "blocked_live_replay_execution_prohibited"
BLOCKED_REPLAY_ENVIRONMENT_MISMATCH = "blocked_replay_environment_mismatch"
BLOCKED_REPLAY_SESSION_MISMATCH = "blocked_replay_session_mismatch"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

SUPPORTED_REPLAY_SCOPES = frozenset(
    {
        "controlled_non_production",
        "isolated_experimental_planning",
        "replay_verified_planning",
    }
)
SUPPORTED_REPLAY_ENVIRONMENTS = frozenset({"local", "test", "ci", "non_production", "experimental"})

STATUS_PRIORITY: tuple[str, ...] = (
    BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_REPLAY_SCOPE_ID,
    BLOCKED_MISSING_REPLAY_IDENTITY,
    BLOCKED_REPLAY_NOT_REQUIRED,
    BLOCKED_REPLAY_CAPTURE_DISABLED,
    BLOCKED_REPLAY_MANIFEST_MISSING,
    BLOCKED_REPLAY_MANIFEST_UNTRUSTED,
    BLOCKED_REPLAY_LINEAGE_MISSING,
    BLOCKED_REPLAY_SCOPE_UNSUPPORTED,
    BLOCKED_REPLAY_ENVIRONMENT_MISMATCH,
    BLOCKED_REPLAY_SESSION_MISMATCH,
    MANUAL_REVIEW_REQUIRED,
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)


@dataclass(frozen=True)
class ReplaySafeExecutionScopeContract:
    """Inputs required to validate replay-safe future execution planning scopes."""

    replay_scope_id: str
    replay_identity: str
    execution_scope: str
    environment: str
    session_id: str
    sandbox_id: str
    authorization_id: str
    gate_contract_id: str
    replay_required: bool
    replay_capture_enabled: bool
    replay_manifest_present: bool
    replay_manifest_trusted: bool
    replay_lineage_present: bool
    live_replay_execution_requested: bool
    replay_scope_supported: bool
    expected_environment: str
    expected_session_id: str
    manual_review_required: bool
    gate_contract: Any | None = None
    authorization_contract: Any | None = None
    sandbox_contract: Any | None = None
    runtime_manifest_consumption_enabled: bool = False
    live_runtime_execution_enabled: bool = False
    live_synthesis_execution_enabled: bool = False
    live_decision_routing_enabled: bool = False
    recommendation_logic_enabled: bool = False
    autonomous_planner_mutation_enabled: bool = False
    production_authoritative_manifest_treatment: bool = False


def build_replay_safe_execution_scope_contract(
    *,
    replay_scope_id: str,
    replay_identity: str,
    execution_scope: str,
    environment: str,
    session_id: str,
    sandbox_id: str,
    authorization_id: str,
    gate_contract_id: str,
    replay_required: bool,
    replay_capture_enabled: bool,
    replay_manifest_present: bool,
    replay_manifest_trusted: bool,
    replay_lineage_present: bool,
    live_replay_execution_requested: bool,
    replay_scope_supported: bool,
    expected_environment: str,
    expected_session_id: str,
    manual_review_required: bool,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
    runtime_manifest_consumption_enabled: bool = False,
    live_runtime_execution_enabled: bool = False,
    live_synthesis_execution_enabled: bool = False,
    live_decision_routing_enabled: bool = False,
    recommendation_logic_enabled: bool = False,
    autonomous_planner_mutation_enabled: bool = False,
    production_authoritative_manifest_treatment: bool = False,
) -> ReplaySafeExecutionScopeContract:
    return ReplaySafeExecutionScopeContract(
        replay_scope_id=replay_scope_id,
        replay_identity=replay_identity,
        execution_scope=execution_scope,
        environment=environment,
        session_id=session_id,
        sandbox_id=sandbox_id,
        authorization_id=authorization_id,
        gate_contract_id=gate_contract_id,
        replay_required=replay_required,
        replay_capture_enabled=replay_capture_enabled,
        replay_manifest_present=replay_manifest_present,
        replay_manifest_trusted=replay_manifest_trusted,
        replay_lineage_present=replay_lineage_present,
        live_replay_execution_requested=live_replay_execution_requested,
        replay_scope_supported=replay_scope_supported,
        expected_environment=expected_environment,
        expected_session_id=expected_session_id,
        manual_review_required=manual_review_required,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
        runtime_manifest_consumption_enabled=runtime_manifest_consumption_enabled,
        live_runtime_execution_enabled=live_runtime_execution_enabled,
        live_synthesis_execution_enabled=live_synthesis_execution_enabled,
        live_decision_routing_enabled=live_decision_routing_enabled,
        recommendation_logic_enabled=recommendation_logic_enabled,
        autonomous_planner_mutation_enabled=autonomous_planner_mutation_enabled,
        production_authoritative_manifest_treatment=production_authoritative_manifest_treatment,
    )


def evaluate_replay_safe_execution_scope_contract(contract: ReplaySafeExecutionScopeContract) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    candidate_statuses: list[str] = []

    def add_blocker(status: str, blocker_id: str) -> None:
        candidate_statuses.append(status)
        blockers.append({"status": status, "blocker_id": blocker_id})

    if contract.live_replay_execution_requested:
        add_blocker(BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED, "live_replay_execution_prohibited")
    if not contract.replay_scope_id:
        add_blocker(BLOCKED_MISSING_REPLAY_SCOPE_ID, "replay_scope_id_missing")
    if not contract.replay_identity:
        add_blocker(BLOCKED_MISSING_REPLAY_IDENTITY, "replay_identity_missing")
    if not contract.replay_required:
        add_blocker(BLOCKED_REPLAY_NOT_REQUIRED, "replay_requirement_missing")
    if not contract.replay_capture_enabled:
        add_blocker(BLOCKED_REPLAY_CAPTURE_DISABLED, "replay_capture_disabled")
    if not contract.replay_manifest_present:
        add_blocker(BLOCKED_REPLAY_MANIFEST_MISSING, "replay_manifest_missing")
    if contract.replay_manifest_present and not contract.replay_manifest_trusted:
        add_blocker(BLOCKED_REPLAY_MANIFEST_UNTRUSTED, "replay_manifest_untrusted")
    if not contract.replay_lineage_present:
        add_blocker(BLOCKED_REPLAY_LINEAGE_MISSING, "replay_lineage_missing")
    if (
        not contract.replay_scope_supported
        or contract.execution_scope not in SUPPORTED_REPLAY_SCOPES
        or contract.environment not in SUPPORTED_REPLAY_ENVIRONMENTS
    ):
        add_blocker(BLOCKED_REPLAY_SCOPE_UNSUPPORTED, "replay_scope_unsupported")
    if contract.environment != contract.expected_environment:
        add_blocker(BLOCKED_REPLAY_ENVIRONMENT_MISMATCH, "replay_environment_mismatch")
    if contract.session_id != contract.expected_session_id:
        add_blocker(BLOCKED_REPLAY_SESSION_MISMATCH, "replay_session_mismatch")

    gate_result = evaluate_controlled_execution_gate_contract(contract.gate_contract) if contract.gate_contract is not None else None
    authorization_result = (
        evaluate_non_production_execution_authorization_contract(contract.authorization_contract)
        if contract.authorization_contract is not None
        else None
    )
    sandbox_result = evaluate_execution_session_sandbox_contract(contract.sandbox_contract) if contract.sandbox_contract is not None else None
    if gate_result is not None and gate_result["status"] != ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING:
        add_blocker(BLOCKED_REPLAY_SCOPE_UNSUPPORTED, "phase1_gate_not_eligible")
    if (
        authorization_result is not None
        and authorization_result["status"] != AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_REPLAY_SCOPE_UNSUPPORTED, "phase2_authorization_not_valid")
    if (
        sandbox_result is not None
        and sandbox_result["status"] != SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    ):
        add_blocker(BLOCKED_REPLAY_SCOPE_UNSUPPORTED, "phase3_sandbox_not_ready")

    if not blockers and contract.manual_review_required:
        candidate_statuses.append(MANUAL_REVIEW_REQUIRED)

    status = classify_replay_safe_execution_scope_status(candidate_statuses)
    result = {
        "status": status,
        "replay_scope_ready": status == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        "manual_review_required": status == MANUAL_REVIEW_REQUIRED,
        "blockers": _order_blockers(blockers),
        "contract": _serializable_contract(contract),
        "phase1_gate_compatibility": {
            "gate_contract_linked": bool(contract.gate_contract_id),
            "gate_status": gate_result["status"] if gate_result else "not_evaluated",
            "replay_scope_does_not_bypass_gate": True,
        },
        "phase2_authorization_compatibility": {
            "authorization_linked": bool(contract.authorization_id),
            "authorization_status": authorization_result["status"] if authorization_result else "not_evaluated",
            "replay_scope_does_not_bypass_authorization": True,
        },
        "phase3_sandbox_compatibility": {
            "sandbox_linked": bool(contract.sandbox_id),
            "sandbox_status": sandbox_result["status"] if sandbox_result else "not_evaluated",
            "replay_scope_does_not_bypass_sandbox": True,
        },
        "prohibition_checks": {
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": contract.runtime_manifest_consumption_enabled,
            "production_authoritative_manifest_treatment": contract.production_authoritative_manifest_treatment,
            "live_runtime_execution_enabled": contract.live_runtime_execution_enabled,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": contract.live_synthesis_execution_enabled,
            "live_decision_routing_enabled": contract.live_decision_routing_enabled,
            "recommendation_logic_enabled": contract.recommendation_logic_enabled,
            "autonomous_planner_mutation_enabled": contract.autonomous_planner_mutation_enabled,
            "replay_manifest_execution_enabled": False,
            "replay_manifest_production_authoritative": False,
        },
        "planning_only": True,
    }
    result["deterministic_hash"] = deterministic_hash(_without_hash(result))
    return result


def classify_replay_safe_execution_scope_status(candidate_statuses: list[str] | tuple[str, ...]) -> str:
    if not candidate_statuses:
        return REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_REPLAY_SCOPE_UNSUPPORTED


def summarize_replay_safe_execution_scope_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "replay_scope_ready": result["replay_scope_ready"],
        "manual_review_required": result["manual_review_required"],
        "blocker_count": len(result["blockers"]),
        "phase1_gate_status": result["phase1_gate_compatibility"]["gate_status"],
        "replay_scope_does_not_bypass_gate": result["phase1_gate_compatibility"]["replay_scope_does_not_bypass_gate"],
        "phase2_authorization_status": result["phase2_authorization_compatibility"]["authorization_status"],
        "replay_scope_does_not_bypass_authorization": result["phase2_authorization_compatibility"]["replay_scope_does_not_bypass_authorization"],
        "phase3_sandbox_status": result["phase3_sandbox_compatibility"]["sandbox_status"],
        "replay_scope_does_not_bypass_sandbox": result["phase3_sandbox_compatibility"]["replay_scope_does_not_bypass_sandbox"],
        "planning_only": result["planning_only"],
        "deterministic_hash": result["deterministic_hash"],
        **result["prohibition_checks"],
    }


def serialize_replay_safe_execution_scope_result(result: dict[str, Any]) -> str:
    return stable_serialize(result)


def default_replay_safe_execution_scope_contract(
    *,
    gate_contract: Any | None = None,
    authorization_contract: Any | None = None,
    sandbox_contract: Any | None = None,
) -> ReplaySafeExecutionScopeContract:
    return build_replay_safe_execution_scope_contract(
        replay_scope_id="replay-scope-v3-4-phase-4",
        replay_identity="replay-identity-v3-4-phase-4",
        execution_scope="controlled_non_production",
        environment="non_production",
        session_id="session-v3-4-phase-3",
        sandbox_id="sandbox-v3-4-phase-3",
        authorization_id="auth-v3-4-phase-2-non-production",
        gate_contract_id="gate-v3-4-phase-1-controlled-execution",
        replay_required=True,
        replay_capture_enabled=True,
        replay_manifest_present=True,
        replay_manifest_trusted=True,
        replay_lineage_present=True,
        live_replay_execution_requested=False,
        replay_scope_supported=True,
        expected_environment="non_production",
        expected_session_id="session-v3-4-phase-3",
        manual_review_required=False,
        gate_contract=gate_contract,
        authorization_contract=authorization_contract,
        sandbox_contract=sandbox_contract,
    )


def _order_blockers(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {status: index for index, status in enumerate(STATUS_PRIORITY)}
    return sorted(blockers, key=lambda row: (priority[row["status"]], row["blocker_id"]))


def _serializable_contract(contract: ReplaySafeExecutionScopeContract) -> dict[str, Any]:
    data = asdict(contract)
    data["gate_contract"] = "linked" if contract.gate_contract is not None else None
    data["authorization_contract"] = "linked" if contract.authorization_contract is not None else None
    data["sandbox_contract"] = "linked" if contract.sandbox_contract is not None else None
    return data


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = dict(payload)
    stable.pop("deterministic_hash", None)
    return stable
