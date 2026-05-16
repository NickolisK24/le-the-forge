"""Planning-only governance dependency resolution contracts for v3.5 Phase 3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .governance_dependency_models import (
    GovernanceDependencyContract,
    default_governance_dependency_contract,
    export_governance_dependency_lineage,
)
from .governance_dependency_report_models import (
    GovernanceDependencyBlocker,
    GovernanceDependencyResolutionResult,
    export_dependency_resolution_result,
    serialize_dependency_resolution_result,
)
from .governance_dependency_status import (
    DEPENDENCY_BLOCKED,
    DEPENDENCY_ENVIRONMENT_MISMATCH,
    DEPENDENCY_INCOMPATIBLE,
    DEPENDENCY_LINEAGE_GAP,
    DEPENDENCY_MISSING,
    DEPENDENCY_PROHIBITED,
    DEPENDENCY_REQUIRES_MANUAL_REVIEW,
    DEPENDENCY_SATISFIED,
    DEPENDENCY_UNSUPPORTED,
    classify_dependency_status,
)


@dataclass(frozen=True)
class GovernanceDependencyResolutionInput:
    contract: GovernanceDependencyContract
    prohibited_dependency_domains: tuple[str, ...]
    required_lineage_categories: tuple[str, ...]
    expected_target_scope_id: str
    expected_source_contract_id: str


def default_governance_dependency_resolution_input() -> GovernanceDependencyResolutionInput:
    contract = default_governance_dependency_contract()
    return GovernanceDependencyResolutionInput(
        contract=contract,
        prohibited_dependency_domains=(
            "runtime_execution",
            "orchestration_execution",
            "production_routing",
            "state_write",
            "audit_log_write",
            "external_dependency_fetch",
            "automatic_remediation",
        ),
        required_lineage_categories=("replay", "rollback", "compatibility", "environment"),
        expected_target_scope_id=contract.target_scope_id,
        expected_source_contract_id=contract.source_contract_id,
    )


def resolve_governance_dependency(
    resolution_input: GovernanceDependencyResolutionInput | None = None,
) -> GovernanceDependencyResolutionResult:
    source = resolution_input or default_governance_dependency_resolution_input()
    contract = source.contract
    blockers: list[GovernanceDependencyBlocker] = []
    candidate_statuses: list[str] = []

    satisfied_evidence = tuple(sorted(set(contract.required_evidence_ids) & set(contract.provided_evidence_ids)))
    missing_evidence = tuple(sorted(set(contract.required_evidence_ids) - set(contract.provided_evidence_ids)))
    compatibility_failures = _compatibility_failures(contract)
    environment_mismatches = _environment_mismatches(source)
    lineage_gaps = _lineage_gaps(source)
    unsupported_reasons = _unsupported_reasons(contract)
    prohibited_reasons = _prohibited_reasons(source)
    manual_review_reasons = tuple(sorted(set(contract.manual_review_reasons)))

    if not contract.dependency_id or not contract.source_contract_id or not contract.target_scope_id:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_MISSING,
            "dependency_identity_missing",
            "dependency_identity",
            10,
            "dependency identity, source contract, and target scope must be explicit",
        )
    for evidence_id in missing_evidence:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_MISSING,
            f"missing_evidence:{evidence_id}",
            "missing_evidence",
            20,
            "required dependency evidence is missing",
        )
    for reason in sorted(set(contract.blocker_reasons)):
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_BLOCKED,
            f"blocked:{reason}",
            "blocked_dependency",
            30,
            "dependency blocker must remain fail-visible",
        )
    for reason in unsupported_reasons:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_UNSUPPORTED,
            f"unsupported:{reason}",
            "unsupported_dependency",
            40,
            "unsupported dependency state must remain explicit",
        )
    for reason in prohibited_reasons:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_PROHIBITED,
            f"prohibited:{reason}",
            "prohibited_dependency",
            5,
            "prohibited dependency request must not be downgraded",
        )
    for reason in manual_review_reasons:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_REQUIRES_MANUAL_REVIEW,
            f"manual_review:{reason}",
            "manual_review",
            80,
            "manual review requirement must remain explicit",
        )
    for failure in compatibility_failures:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_INCOMPATIBLE,
            f"compatibility_failure:{failure}",
            "compatibility_failure",
            50,
            "compatibility dependency failure must remain visible",
        )
    for mismatch in environment_mismatches:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_ENVIRONMENT_MISMATCH,
            f"environment_mismatch:{mismatch}",
            "environment_mismatch",
            60,
            "environment dependency mismatch must preserve non-production isolation",
        )
    for gap in lineage_gaps:
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_LINEAGE_GAP,
            f"lineage_gap:{gap}",
            "lineage_gap",
            70,
            "dependency lineage gap must remain explicit and non-executable",
        )
    if _prohibited_behavior_detected(contract):
        _add_blocker(
            blockers,
            candidate_statuses,
            DEPENDENCY_PROHIBITED,
            "prohibited:execution_fetch_mutation_or_remediation_behavior_detected",
            "prohibited_behavior",
            6,
            "execution, routing, mutation, writing, production consumption, external fetching, and remediation are prohibited",
        )

    status = classify_dependency_status(candidate_statuses)
    return GovernanceDependencyResolutionResult(
        dependency_id=contract.dependency_id,
        dependency_status=status,
        planning_only=True,
        satisfied_evidence=satisfied_evidence,
        missing_evidence=missing_evidence,
        blockers=tuple(blockers),
        unsupported_reasons=unsupported_reasons,
        prohibited_reasons=prohibited_reasons,
        manual_review_reasons=manual_review_reasons,
        compatibility_failures=compatibility_failures,
        environment_mismatches=environment_mismatches,
        lineage_gaps=lineage_gaps,
        lineage_propagation=_lineage_propagation(contract),
        deterministic_explanation_summary=_explanation_summary(status, blockers),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        audit_log_writing_enabled=False,
        production_consumption_enabled=False,
        external_dependency_fetching_enabled=False,
        automatic_remediation_enabled=False,
        contract=contract,
    )


def export_governance_dependency_resolution_result(
    result: GovernanceDependencyResolutionResult,
) -> dict[str, Any]:
    return export_dependency_resolution_result(result)


def serialize_governance_dependency_resolution_result(result: GovernanceDependencyResolutionResult) -> str:
    return serialize_dependency_resolution_result(result)


def hash_governance_dependency_resolution_input(source: GovernanceDependencyResolutionInput) -> str:
    return deterministic_hash(
        {
            "contract": source.contract,
            "prohibited_dependency_domains": source.prohibited_dependency_domains,
            "required_lineage_categories": source.required_lineage_categories,
            "expected_target_scope_id": source.expected_target_scope_id,
            "expected_source_contract_id": source.expected_source_contract_id,
        }
    )


def _compatibility_failures(contract: GovernanceDependencyContract) -> tuple[str, ...]:
    failures: list[str] = []
    missing = set(contract.compatibility_requirements) - set(contract.compatibility_evidence_ids)
    failures.extend(f"missing:{item}" for item in sorted(missing))
    if not contract.compatibility_verified:
        failures.append("compatibility_not_verified")
    return tuple(sorted(failures))


def _environment_mismatches(source: GovernanceDependencyResolutionInput) -> tuple[str, ...]:
    contract = source.contract
    mismatches: list[str] = []
    missing = set(contract.environment_requirements) - set(contract.environment_evidence_ids)
    mismatches.extend(f"missing:{item}" for item in sorted(missing))
    if not contract.environment_verified:
        mismatches.append("environment_not_verified")
    if contract.target_scope_id != source.expected_target_scope_id:
        mismatches.append("target_scope_mismatch")
    if contract.source_contract_id != source.expected_source_contract_id:
        mismatches.append("source_contract_mismatch")
    return tuple(sorted(set(mismatches)))


def _lineage_gaps(source: GovernanceDependencyResolutionInput) -> tuple[str, ...]:
    lineage = source.contract.lineage
    gaps: list[str] = []
    if not lineage.source_governance_contract_id:
        gaps.append("source_governance_contract_id")
    if not lineage.target_orchestration_scope_id:
        gaps.append("target_orchestration_scope_id")
    if "replay" in source.required_lineage_categories and not lineage.replay_lineage_references:
        gaps.append("replay_lineage_references")
    if "rollback" in source.required_lineage_categories and not lineage.rollback_lineage_references:
        gaps.append("rollback_lineage_references")
    if "compatibility" in source.required_lineage_categories and not lineage.compatibility_lineage_references:
        gaps.append("compatibility_lineage_references")
    if "environment" in source.required_lineage_categories and not lineage.environment_lineage_references:
        gaps.append("environment_lineage_references")
    return tuple(sorted(gaps))


def _unsupported_reasons(contract: GovernanceDependencyContract) -> tuple[str, ...]:
    reasons = set(contract.unsupported_reasons)
    if not contract.dependency_supported:
        reasons.add("dependency_not_supported")
    return tuple(sorted(reasons))


def _prohibited_reasons(source: GovernanceDependencyResolutionInput) -> tuple[str, ...]:
    contract = source.contract
    reasons = set(contract.prohibited_reasons)
    if contract.dependency_prohibited:
        reasons.add("dependency_marked_prohibited")
    if contract.dependency_domain in source.prohibited_dependency_domains:
        reasons.add(f"prohibited_domain:{contract.dependency_domain}")
    return tuple(sorted(reasons))


def _lineage_propagation(contract: GovernanceDependencyContract) -> dict[str, Any]:
    lineage = export_governance_dependency_lineage(contract.lineage)
    return {
        "source_governance_contract_id": lineage["source_governance_contract_id"],
        "target_orchestration_scope_id": lineage["target_orchestration_scope_id"],
        "upstream_dependency_ids": lineage["upstream_dependency_ids"],
        "downstream_dependency_ids": lineage["downstream_dependency_ids"],
        "replay_lineage_references": lineage["replay_lineage_references"],
        "rollback_lineage_references": lineage["rollback_lineage_references"],
        "compatibility_lineage_references": lineage["compatibility_lineage_references"],
        "environment_lineage_references": lineage["environment_lineage_references"],
        "non_executable": True,
        "external_graph_lookup_enabled": False,
        "automatic_repair_enabled": False,
    }


def _prohibited_behavior_detected(contract: GovernanceDependencyContract) -> bool:
    return any(
        (
            contract.external_dependency_fetching_enabled,
            contract.automatic_remediation_enabled,
            contract.runtime_execution_enabled,
            contract.orchestration_execution_enabled,
            contract.routing_behavior_enabled,
            contract.mutation_behavior_enabled,
            contract.audit_log_writing_enabled,
            contract.production_consumption_enabled,
        )
    )


def _add_blocker(
    blockers: list[GovernanceDependencyBlocker],
    candidate_statuses: list[str],
    status: str,
    blocker_id: str,
    category: str,
    rank: int,
    explanation: str,
) -> None:
    candidate_statuses.append(status)
    blockers.append(
        GovernanceDependencyBlocker(
            blocker_id=blocker_id,
            dependency_status=status,
            blocker_category=category,
            deterministic_rank=rank,
            fail_visible=True,
            audit_safe=True,
            explanation=explanation,
        )
    )


def _explanation_summary(status: str, blockers: list[GovernanceDependencyBlocker]) -> str:
    if not blockers:
        return (
            "Dependency is satisfied for planning-only governance resolution; no execution, routing, "
            "mutation, audit writing, production consumption, external fetching, or automatic remediation is authorized."
        )
    blocker_ids = ", ".join(row.blocker_id for row in sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))
    return f"Dependency classified as {status}; fail-visible blockers: {blocker_ids}."
