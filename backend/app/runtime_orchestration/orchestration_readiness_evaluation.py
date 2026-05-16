"""Planning-only orchestration readiness evaluation contracts for v3.5 Phase 2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .governance_consumption_contracts import GovernanceConsumptionContract, default_governance_consumption_contract
from .orchestration_readiness_report_models import (
    OrchestrationReadinessBlocker,
    OrchestrationReadinessResult,
    export_readiness_result,
    serialize_readiness_result,
)
from .orchestration_readiness_status import (
    BLOCKED_BY_AUTHORIZATION_FAILURE,
    BLOCKED_BY_COMPATIBILITY_FAILURE,
    BLOCKED_BY_ENVIRONMENT_FAILURE,
    BLOCKED_BY_GOVERNANCE_DEPENDENCY,
    BLOCKED_BY_REPLAY_LINEAGE_GAP,
    BLOCKED_BY_ROLLBACK_LINEAGE_GAP,
    MANUAL_REVIEW_REQUIRED,
    PROHIBITED_ORCHESTRATION_REQUEST,
    READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
    UNSUPPORTED_ORCHESTRATION_REQUEST,
    classify_readiness_status,
)


@dataclass(frozen=True)
class OrchestrationReadinessEvaluationInput:
    contract: GovernanceConsumptionContract
    required_governance_dependency_ids: tuple[str, ...]
    required_replay_requirements: tuple[str, ...]
    required_rollback_requirements: tuple[str, ...]
    required_compatibility_requirements: tuple[str, ...]
    expected_environment: str
    allowed_orchestration_domains: tuple[str, ...]
    prohibited_orchestration_domains: tuple[str, ...]
    manual_review_required: bool = False
    manual_review_reasons: tuple[str, ...] = ()


def default_orchestration_readiness_evaluation_input() -> OrchestrationReadinessEvaluationInput:
    contract = default_governance_consumption_contract()
    return OrchestrationReadinessEvaluationInput(
        contract=contract,
        required_governance_dependency_ids=contract.governance_dependency_ids,
        required_replay_requirements=("replay_lineage_id",),
        required_rollback_requirements=("rollback_lineage_id",),
        required_compatibility_requirements=contract.compatibility_requirements,
        expected_environment="non_production",
        allowed_orchestration_domains=contract.boundary_model.allowed_orchestration_domains,
        prohibited_orchestration_domains=contract.boundary_model.prohibited_orchestration_domains,
    )


def evaluate_orchestration_readiness(
    evaluation_input: OrchestrationReadinessEvaluationInput | None = None,
) -> OrchestrationReadinessResult:
    source = evaluation_input or default_orchestration_readiness_evaluation_input()
    contract = source.contract
    blockers: list[OrchestrationReadinessBlocker] = []
    candidate_statuses: list[str] = []

    missing_governance_dependencies = tuple(
        sorted(set(source.required_governance_dependency_ids) - set(contract.governance_dependency_ids))
    )
    missing_replay_requirements = _missing_replay_requirements(source)
    missing_rollback_requirements = _missing_rollback_requirements(source)
    compatibility_failures = _compatibility_failures(source)
    environment_failures = _environment_failures(source)
    unsupported_states = tuple(sorted(set(contract.unsupported_orchestration_states)))
    prohibited_domains = _prohibited_domains(source)
    manual_review_reasons = tuple(sorted(set(source.manual_review_reasons))) if source.manual_review_required else ()

    if not contract.orchestration_request_id or not contract.orchestration_scope_id:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_GOVERNANCE_DEPENDENCY,
            "orchestration_identity_missing",
            "governance_dependency",
            10,
            "orchestration request identity and scope identity must be explicit",
        )
    for dependency_id in missing_governance_dependencies:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_GOVERNANCE_DEPENDENCY,
            f"missing_governance_dependency:{dependency_id}",
            "governance_dependency",
            20,
            "required governance dependency is missing",
        )
    if contract.authorization_required and contract.authorization_state != "authorized_for_planning":
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_AUTHORIZATION_FAILURE,
            "authorization_not_satisfied",
            "authorization_failure",
            30,
            "non-production planning authorization must be explicit",
        )
    for requirement in missing_replay_requirements:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_REPLAY_LINEAGE_GAP,
            f"missing_replay_requirement:{requirement}",
            "replay_lineage_gap",
            40,
            "required replay lineage must remain fail-visible",
        )
    for requirement in missing_rollback_requirements:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_ROLLBACK_LINEAGE_GAP,
            f"missing_rollback_requirement:{requirement}",
            "rollback_lineage_gap",
            50,
            "required rollback lineage must remain fail-visible",
        )
    for failure in compatibility_failures:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_COMPATIBILITY_FAILURE,
            f"compatibility_failure:{failure}",
            "compatibility_failure",
            60,
            "compatibility evidence must be deterministic and explicit",
        )
    for failure in environment_failures:
        _add_blocker(
            blockers,
            candidate_statuses,
            BLOCKED_BY_ENVIRONMENT_FAILURE,
            f"environment_failure:{failure}",
            "environment_failure",
            70,
            "environment requirements must preserve non-production isolation",
        )
    for state in unsupported_states:
        _add_blocker(
            blockers,
            candidate_statuses,
            UNSUPPORTED_ORCHESTRATION_REQUEST,
            f"unsupported_state:{state}",
            "unsupported_state",
            80,
            "unsupported orchestration states must remain explicit",
        )
    for domain in prohibited_domains:
        _add_blocker(
            blockers,
            candidate_statuses,
            PROHIBITED_ORCHESTRATION_REQUEST,
            f"prohibited_domain:{domain}",
            "prohibited_domain",
            5,
            "prohibited orchestration domains must not be downgraded",
        )
    if _prohibited_behavior_detected(contract):
        _add_blocker(
            blockers,
            candidate_statuses,
            PROHIBITED_ORCHESTRATION_REQUEST,
            "prohibited_execution_or_consumption_behavior_detected",
            "prohibited_behavior",
            6,
            "execution, routing, mutation, write, side-effect, or production consumption behavior is prohibited",
        )
    for reason in manual_review_reasons:
        _add_blocker(
            blockers,
            candidate_statuses,
            MANUAL_REVIEW_REQUIRED,
            f"manual_review:{reason}",
            "manual_review",
            90,
            "manual review requirement must remain explicit",
        )

    status = classify_readiness_status(candidate_statuses)
    return OrchestrationReadinessResult(
        readiness_status=status,
        planning_ready=status == READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
        planning_only=True,
        blockers=tuple(blockers),
        unsupported_states=unsupported_states,
        prohibited_domains=prohibited_domains,
        missing_governance_dependencies=missing_governance_dependencies,
        missing_replay_requirements=missing_replay_requirements,
        missing_rollback_requirements=missing_rollback_requirements,
        compatibility_failures=compatibility_failures,
        environment_failures=environment_failures,
        manual_review_reasons=manual_review_reasons,
        deterministic_explanation_summary=_explanation_summary(status, blockers),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        audit_log_writing_enabled=False,
        production_consumption_enabled=False,
    )


def export_orchestration_readiness_result(
    result: OrchestrationReadinessResult,
) -> dict[str, Any]:
    return export_readiness_result(result)


def serialize_orchestration_readiness_result(result: OrchestrationReadinessResult) -> str:
    return serialize_readiness_result(result)


def hash_orchestration_readiness_input(source: OrchestrationReadinessEvaluationInput) -> str:
    return deterministic_hash(
        {
            "contract": source.contract,
            "required_governance_dependency_ids": source.required_governance_dependency_ids,
            "required_replay_requirements": source.required_replay_requirements,
            "required_rollback_requirements": source.required_rollback_requirements,
            "required_compatibility_requirements": source.required_compatibility_requirements,
            "expected_environment": source.expected_environment,
            "allowed_orchestration_domains": source.allowed_orchestration_domains,
            "prohibited_orchestration_domains": source.prohibited_orchestration_domains,
            "manual_review_required": source.manual_review_required,
            "manual_review_reasons": source.manual_review_reasons,
        }
    )


def _missing_replay_requirements(source: OrchestrationReadinessEvaluationInput) -> tuple[str, ...]:
    missing: list[str] = []
    if "replay_lineage_id" in source.required_replay_requirements:
        if not source.contract.replay_lineage_required or not source.contract.replay_lineage_id:
            missing.append("replay_lineage_id")
    return tuple(sorted(missing))


def _missing_rollback_requirements(source: OrchestrationReadinessEvaluationInput) -> tuple[str, ...]:
    missing: list[str] = []
    if "rollback_lineage_id" in source.required_rollback_requirements:
        if not source.contract.rollback_lineage_required or not source.contract.rollback_lineage_id:
            missing.append("rollback_lineage_id")
    return tuple(sorted(missing))


def _compatibility_failures(source: OrchestrationReadinessEvaluationInput) -> tuple[str, ...]:
    failures: list[str] = []
    missing = set(source.required_compatibility_requirements) - set(source.contract.compatibility_requirements)
    failures.extend(f"missing:{item}" for item in sorted(missing))
    if not source.contract.compatibility_verified:
        failures.append("compatibility_not_verified")
    return tuple(sorted(failures))


def _environment_failures(source: OrchestrationReadinessEvaluationInput) -> tuple[str, ...]:
    failures: list[str] = []
    if source.contract.environment != source.expected_environment:
        failures.append("environment_mismatch")
    if source.contract.environment != "non_production":
        failures.append("non_production_environment_required")
    if not source.contract.environment_isolated:
        failures.append("environment_not_isolated")
    if source.contract.orchestration_scope not in source.contract.boundary_model.isolated_orchestration_scopes:
        failures.append("scope_not_isolated")
    return tuple(sorted(set(failures)))


def _prohibited_domains(source: OrchestrationReadinessEvaluationInput) -> tuple[str, ...]:
    domains: list[str] = []
    if source.contract.requested_orchestration_domain in source.prohibited_orchestration_domains:
        domains.append(source.contract.requested_orchestration_domain)
    if source.contract.requested_orchestration_domain not in source.allowed_orchestration_domains:
        domains.append(source.contract.requested_orchestration_domain)
    return tuple(sorted(set(domains)))


def _prohibited_behavior_detected(contract: GovernanceConsumptionContract) -> bool:
    return any(
        (
            contract.runtime_execution_enabled,
            contract.orchestration_execution_enabled,
            contract.autonomous_orchestration_enabled,
            contract.recommendation_system_enabled,
            contract.decision_routing_enabled,
            contract.production_routing_enabled,
            contract.persistent_mutation_enabled,
            contract.state_writes_enabled,
            contract.audit_log_writes_enabled,
            contract.external_side_effects_enabled,
            contract.production_authoritative_manifests_enabled,
            contract.production_runtime_consumption_enabled,
            contract.experiment_execution_enabled,
            contract.self_modifying_orchestration_enabled,
            contract.hidden_fallback_logic_enabled,
        )
    )


def _add_blocker(
    blockers: list[OrchestrationReadinessBlocker],
    candidate_statuses: list[str],
    status: str,
    blocker_id: str,
    category: str,
    rank: int,
    explanation: str,
) -> None:
    candidate_statuses.append(status)
    blockers.append(
        OrchestrationReadinessBlocker(
            blocker_id=blocker_id,
            readiness_status=status,
            blocker_category=category,
            deterministic_rank=rank,
            fail_visible=True,
            audit_safe=True,
            explanation=explanation,
        )
    )


def _explanation_summary(status: str, blockers: list[OrchestrationReadinessBlocker]) -> str:
    if not blockers:
        return (
            "Readiness is planning-only and satisfied for future orchestration planning; "
            "no execution, routing, mutation, audit writing, or production consumption is authorized."
        )
    blocker_ids = ", ".join(row.blocker_id for row in sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))
    return f"Readiness classified as {status}; fail-visible blockers: {blocker_ids}."
