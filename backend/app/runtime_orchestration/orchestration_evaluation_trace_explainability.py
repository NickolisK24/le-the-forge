"""Deterministic orchestration evaluation trace explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_trace_builder import build_orchestration_evaluation_trace
from .orchestration_evaluation_trace_models import (
    TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    TRACE_EXPLAINABILITY_STABLE,
    TRACE_STEP_BLOCKER,
    TRACE_STEP_COMPATIBILITY,
    TRACE_STEP_DEPENDENCY,
    TRACE_STEP_GOVERNANCE,
    TRACE_STEP_PROHIBITED_DOMAIN,
    TRACE_STEP_UNSUPPORTED_DOMAIN,
    OrchestrationEvaluationTraceBuildInput,
    OrchestrationEvaluationTraceBuildRecord,
    OrchestrationEvaluationTraceBuildResult,
    OrchestrationEvaluationTraceExplainabilityResult,
    OrchestrationEvaluationTraceExplanationRecord,
    OrchestrationEvaluationTraceRecord,
    OrchestrationEvaluationTraceRegistry,
    export_trace_explainability_result,
    hash_trace_explainability_result,
    serialize_trace_explainability_result,
)
from .orchestration_evaluation_trace_registry import default_orchestration_evaluation_trace_registry


def explain_orchestration_evaluation_trace(
    trace_registry: OrchestrationEvaluationTraceRegistry | None = None,
    build_result: OrchestrationEvaluationTraceBuildResult | None = None,
) -> OrchestrationEvaluationTraceExplainabilityResult:
    registry = trace_registry or default_orchestration_evaluation_trace_registry()
    build = build_result or build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=registry)
    )
    records_by_id = {record.identifier.trace_id: record for record in registry.records}
    build_by_id = {record.trace_id: record for record in build.build_records}
    records = tuple(
        _explain_record(records_by_id[trace_id], build_by_id[trace_id])
        for trace_id in sorted(records_by_id)
        if trace_id in build_by_id
    )
    status = (
        TRACE_EXPLAINABILITY_STABLE
        if all(record.explanation_status == TRACE_EXPLAINABILITY_STABLE for record in records)
        else TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationEvaluationTraceExplainabilityResult(
        registry_id=registry.registry_id,
        trace_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        governance_explanation_count=_explanation_count(registry.records, TRACE_STEP_GOVERNANCE),
        compatibility_explanation_count=_explanation_count(registry.records, TRACE_STEP_COMPATIBILITY),
        dependency_explanation_count=_explanation_count(registry.records, TRACE_STEP_DEPENDENCY),
        blocker_explanation_count=_explanation_count(registry.records, TRACE_STEP_BLOCKER),
        unsupported_explanation_count=_explanation_count(registry.records, TRACE_STEP_UNSUPPORTED_DOMAIN),
        prohibited_explanation_count=_explanation_count(registry.records, TRACE_STEP_PROHIBITED_DOMAIN),
        trace_step_visibility_count=sum(len(record.trace_step_visibility) for record in records),
        reasoning_chain_visibility_count=sum(len(record.reasoning_chain_visibility) for record in records),
        deterministic_trace_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_trace_explainability_hash=hash_trace_explainability_result(result))


def export_orchestration_evaluation_trace_explainability_result(
    result: OrchestrationEvaluationTraceExplainabilityResult,
) -> dict[str, object]:
    return export_trace_explainability_result(result)


def serialize_orchestration_evaluation_trace_explainability_result(
    result: OrchestrationEvaluationTraceExplainabilityResult,
) -> str:
    return serialize_trace_explainability_result(result)


def hash_orchestration_evaluation_trace_explainability_result(
    result: OrchestrationEvaluationTraceExplainabilityResult,
) -> str:
    return hash_trace_explainability_result(result)


def _explain_record(
    record: OrchestrationEvaluationTraceRecord,
    build_record: OrchestrationEvaluationTraceBuildRecord,
) -> OrchestrationEvaluationTraceExplanationRecord:
    build_visibility = tuple(
        sorted(
            f"{finding.classification}:{finding.reason}"
            for finding in build_record.findings
        )
    )
    explanation_status = (
        TRACE_EXPLAINABILITY_STABLE
        if _has_visibility(record, build_record, build_visibility)
        else TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationEvaluationTraceExplanationRecord(
        trace_id=record.identifier.trace_id,
        preflight_id=record.identifier.preflight_id,
        trace_state=record.trace_state,
        explanation_status=explanation_status,
        reasoning_chain_visibility=tuple(sorted(record.reasoning_chain)),
        trace_step_visibility=tuple(
            sorted(
                f"{step.sequence_id:02d}:{step.step_type}:{step.description}"
                for step in record.trace_steps
            )
        ),
        governance_boundary_visibility=tuple(sorted(record.governance_boundaries)),
        compatibility_domain_visibility=tuple(sorted(record.compatibility_domains)),
        dependency_domain_visibility=tuple(sorted(record.dependency_domains)),
        blocker_domain_visibility=tuple(sorted(record.blocker_domains)),
        unsupported_domain_visibility=tuple(sorted(record.unsupported_domains)),
        prohibited_domain_visibility=tuple(sorted(record.prohibited_domains)),
        supported_domain_visibility=tuple(sorted(record.supported_domains)),
        provenance_visibility=_provenance_visibility(record),
        build_visibility=build_visibility,
        integrity_visibility=tuple(sorted(record.integrity_reference_ids)),
    )


def _provenance_visibility(record: OrchestrationEvaluationTraceRecord) -> tuple[str, ...]:
    provenance = record.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                provenance.preflight_id,
                provenance.intent_id,
                *provenance.policy_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_visibility(
    record: OrchestrationEvaluationTraceRecord,
    build_record: OrchestrationEvaluationTraceBuildRecord,
    build_visibility: tuple[str, ...],
) -> bool:
    return bool(
        record.trace_steps
        and record.reasoning_chain
        and record.policy_ids
        and record.governance_boundaries
        and record.explainability_reference_ids
        and record.integrity_reference_ids
        and build_record.findings
        and build_visibility
    )


def _explanation_count(
    records: tuple[OrchestrationEvaluationTraceRecord, ...],
    step_type: str,
) -> int:
    return sum(1 for record in records if any(step.step_type == step_type for step in record.trace_steps))


def _summary(
    status: str,
    records: tuple[OrchestrationEvaluationTraceExplanationRecord, ...],
) -> str:
    if status == TRACE_EXPLAINABILITY_STABLE:
        return (
            "Evaluation trace explainability is stable; reasoning chains, trace steps, governance boundaries, "
            "compatibility domains, dependencies, blockers, unsupported domains, prohibited domains, "
            "provenance, build findings, and integrity references are visible."
        )
    missing = tuple(sorted(record.trace_id for record in records if record.explanation_status != TRACE_EXPLAINABILITY_STABLE))
    return f"Evaluation trace explainability has visibility gaps for: {', '.join(missing)}."
