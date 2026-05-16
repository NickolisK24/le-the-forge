"""Deterministic orchestration preflight explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_preflight_evaluator import evaluate_orchestration_preflight
from .orchestration_preflight_models import (
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    PREFLIGHT_EXPLAINABILITY_STABLE,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    OrchestrationPreflightEvaluationInput,
    OrchestrationPreflightEvaluationRecord,
    OrchestrationPreflightEvaluationResult,
    OrchestrationPreflightExplainabilityResult,
    OrchestrationPreflightExplanationRecord,
    OrchestrationPreflightRecord,
    OrchestrationPreflightRegistry,
    export_preflight_explainability_result,
    hash_preflight_explainability_result,
    serialize_preflight_explainability_result,
)
from .orchestration_preflight_registry import default_orchestration_preflight_registry


def explain_orchestration_preflight(
    preflight_registry: OrchestrationPreflightRegistry | None = None,
    evaluation_result: OrchestrationPreflightEvaluationResult | None = None,
) -> OrchestrationPreflightExplainabilityResult:
    registry = preflight_registry or default_orchestration_preflight_registry()
    evaluation = evaluation_result or evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=registry)
    )
    records_by_id = {record.identifier.preflight_id: record for record in registry.records}
    evaluation_by_id = {record.preflight_id: record for record in evaluation.evaluation_records}
    records = tuple(
        _explain_record(records_by_id[preflight_id], evaluation_by_id[preflight_id])
        for preflight_id in sorted(records_by_id)
        if preflight_id in evaluation_by_id
    )
    status = (
        PREFLIGHT_EXPLAINABILITY_STABLE
        if all(record.explanation_status == PREFLIGHT_EXPLAINABILITY_STABLE for record in records)
        else PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationPreflightExplainabilityResult(
        registry_id=registry.registry_id,
        preflight_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        supported_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_SUPPORTED),
        unsupported_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_UNSUPPORTED),
        prohibited_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_PROHIBITED),
        governance_blocked_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_GOVERNANCE_BLOCKED),
        compatibility_blocked_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_COMPATIBILITY_BLOCKED),
        dependency_blocked_explanation_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_DEPENDENCY_BLOCKED),
        policy_visibility_count=sum(len(record.policy_visibility) for record in records),
        governance_boundary_visibility_count=sum(len(record.governance_boundary_visibility) for record in records),
        compatibility_domain_visibility_count=sum(len(record.compatibility_domain_visibility) for record in records),
        dependency_domain_visibility_count=sum(len(record.dependency_domain_visibility) for record in records),
        blocker_domain_visibility_count=sum(len(record.blocker_domain_visibility) for record in records),
        unsupported_domain_visibility_count=sum(len(record.unsupported_domain_visibility) for record in records),
        prohibited_domain_visibility_count=sum(len(record.prohibited_domain_visibility) for record in records),
        deterministic_preflight_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_preflight_explainability_hash=hash_preflight_explainability_result(result))


def export_orchestration_preflight_explainability_result(
    result: OrchestrationPreflightExplainabilityResult,
) -> dict[str, object]:
    return export_preflight_explainability_result(result)


def serialize_orchestration_preflight_explainability_result(
    result: OrchestrationPreflightExplainabilityResult,
) -> str:
    return serialize_preflight_explainability_result(result)


def hash_orchestration_preflight_explainability_result(
    result: OrchestrationPreflightExplainabilityResult,
) -> str:
    return hash_preflight_explainability_result(result)


def _explain_record(
    record: OrchestrationPreflightRecord,
    evaluation_record: OrchestrationPreflightEvaluationRecord,
) -> OrchestrationPreflightExplanationRecord:
    evaluation_visibility = tuple(
        sorted(
            f"{finding.classification}:{finding.reason}"
            for finding in evaluation_record.findings
        )
    )
    explanation_status = (
        PREFLIGHT_EXPLAINABILITY_STABLE
        if _has_visibility(record, evaluation_record, evaluation_visibility)
        else PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationPreflightExplanationRecord(
        preflight_id=record.identifier.preflight_id,
        intent_id=record.identifier.intent_id,
        preflight_state=record.preflight_state,
        explanation_status=explanation_status,
        theoretical_supportability_visibility=(f"theoretically_supportable:{record.theoretically_supportable}",),
        policy_visibility=tuple(sorted(record.policy_ids)),
        governance_boundary_visibility=tuple(sorted(record.governance_boundaries)),
        compatibility_domain_visibility=tuple(sorted(record.compatibility_domains)),
        dependency_domain_visibility=tuple(sorted(record.dependency_domains)),
        blocker_domain_visibility=tuple(sorted(record.blocker_domains)),
        unsupported_domain_visibility=tuple(sorted(record.unsupported_domains)),
        prohibited_domain_visibility=tuple(sorted(record.prohibited_domains)),
        supported_domain_visibility=tuple(sorted(record.supported_domains)),
        preflight_rationale_visibility=tuple(sorted(record.preflight_rationale)),
        provenance_visibility=_provenance_visibility(record),
        evaluation_visibility=evaluation_visibility,
        integrity_visibility=tuple(sorted(record.integrity_reference_ids)),
    )


def _provenance_visibility(record: OrchestrationPreflightRecord) -> tuple[str, ...]:
    provenance = record.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                provenance.intent_id,
                provenance.mapping_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_visibility(
    record: OrchestrationPreflightRecord,
    evaluation_record: OrchestrationPreflightEvaluationRecord,
    evaluation_visibility: tuple[str, ...],
) -> bool:
    return bool(
        record.policy_ids
        and record.preflight_rationale
        and record.governance_boundaries
        and record.integrity_reference_ids
        and evaluation_visibility
        and evaluation_record.findings
    )


def _summary(
    status: str,
    records: tuple[OrchestrationPreflightExplanationRecord, ...],
) -> str:
    if status == PREFLIGHT_EXPLAINABILITY_STABLE:
        return (
            "Preflight explainability is stable; theoretical supportability, policy references, governance "
            "boundaries, compatibility domains, dependencies, blockers, unsupported domains, prohibited domains, "
            "provenance, rationale, and integrity references are visible."
        )
    missing = tuple(sorted(record.preflight_id for record in records if record.explanation_status != PREFLIGHT_EXPLAINABILITY_STABLE))
    return f"Preflight explainability has visibility gaps for: {', '.join(missing)}."
