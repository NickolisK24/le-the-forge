"""Deterministic orchestration intent-policy mapping explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_policy_mapper import map_orchestration_intent_policies
from .orchestration_intent_policy_mapping_models import (
    MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    MAPPING_EXPLAINABILITY_STABLE,
    MAPPING_PROHIBITED,
    MAPPING_SUPPORTED,
    MAPPING_UNSUPPORTED,
    OrchestrationIntentPolicyMappingAnalysisRecord,
    OrchestrationIntentPolicyMappingInput,
    OrchestrationIntentPolicyMappingRecord,
    OrchestrationIntentPolicyMappingRegistry,
    OrchestrationIntentPolicyMappingResult,
    OrchestrationIntentPolicyMappingExplainabilityResult,
    OrchestrationIntentPolicyMappingExplanationRecord,
    export_mapping_explainability_result,
    hash_mapping_explainability_result,
    serialize_mapping_explainability_result,
)
from .orchestration_intent_policy_mapping_registry import default_orchestration_intent_policy_mapping_registry


def explain_orchestration_intent_policy_mappings(
    mapping_registry: OrchestrationIntentPolicyMappingRegistry | None = None,
    mapping_result: OrchestrationIntentPolicyMappingResult | None = None,
) -> OrchestrationIntentPolicyMappingExplainabilityResult:
    registry = mapping_registry or default_orchestration_intent_policy_mapping_registry()
    analysis = mapping_result or map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=registry)
    )
    records_by_id = {record.identifier.mapping_id: record for record in registry.records}
    analysis_by_id = {record.mapping_id: record for record in analysis.analysis_records}
    records = tuple(
        _explain_record(records_by_id[mapping_id], analysis_by_id[mapping_id])
        for mapping_id in sorted(records_by_id)
        if mapping_id in analysis_by_id
    )
    status = (
        MAPPING_EXPLAINABILITY_STABLE
        if all(record.explanation_status == MAPPING_EXPLAINABILITY_STABLE for record in records)
        else MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationIntentPolicyMappingExplainabilityResult(
        registry_id=registry.registry_id,
        mapping_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        supported_explanation_count=sum(1 for record in records if record.mapping_state == MAPPING_SUPPORTED),
        unsupported_explanation_count=sum(1 for record in records if record.mapping_state == MAPPING_UNSUPPORTED),
        prohibited_explanation_count=sum(1 for record in records if record.mapping_state == MAPPING_PROHIBITED),
        policy_applicability_visibility_count=sum(len(record.policy_applicability_visibility) for record in records),
        governance_boundary_visibility_count=sum(len(record.governance_boundary_visibility) for record in records),
        compatibility_domain_visibility_count=sum(len(record.compatibility_domain_visibility) for record in records),
        dependency_domain_visibility_count=sum(len(record.dependency_domain_visibility) for record in records),
        blocker_domain_visibility_count=sum(len(record.blocker_domain_visibility) for record in records),
        unsupported_domain_visibility_count=sum(len(record.unsupported_domain_visibility) for record in records),
        prohibited_domain_visibility_count=sum(len(record.prohibited_domain_visibility) for record in records),
        deterministic_mapping_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_mapping_explainability_hash=hash_mapping_explainability_result(result))


def export_orchestration_intent_policy_mapping_explainability_result(
    result: OrchestrationIntentPolicyMappingExplainabilityResult,
) -> dict[str, object]:
    return export_mapping_explainability_result(result)


def serialize_orchestration_intent_policy_mapping_explainability_result(
    result: OrchestrationIntentPolicyMappingExplainabilityResult,
) -> str:
    return serialize_mapping_explainability_result(result)


def hash_orchestration_intent_policy_mapping_explainability_result(
    result: OrchestrationIntentPolicyMappingExplainabilityResult,
) -> str:
    return hash_mapping_explainability_result(result)


def _explain_record(
    record: OrchestrationIntentPolicyMappingRecord,
    analysis_record: OrchestrationIntentPolicyMappingAnalysisRecord,
) -> OrchestrationIntentPolicyMappingExplanationRecord:
    analysis_visibility = tuple(
        sorted(
            f"{finding.classification}:{finding.reason}"
            for finding in analysis_record.findings
        )
    )
    explanation_status = (
        MAPPING_EXPLAINABILITY_STABLE
        if _has_visibility(record, analysis_record, analysis_visibility)
        else MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationIntentPolicyMappingExplanationRecord(
        mapping_id=record.identifier.mapping_id,
        intent_id=record.identifier.intent_id,
        mapping_state=record.mapping_state,
        explanation_status=explanation_status,
        policy_applicability_visibility=tuple(sorted(record.policy_ids)),
        governance_boundary_visibility=tuple(sorted(record.governance_boundaries)),
        compatibility_domain_visibility=tuple(sorted(record.compatibility_domains)),
        dependency_domain_visibility=tuple(sorted(record.dependency_domains)),
        blocker_domain_visibility=tuple(sorted(record.blocker_domains)),
        unsupported_domain_visibility=tuple(sorted(record.unsupported_domains)),
        prohibited_domain_visibility=tuple(sorted(record.prohibited_domains)),
        supported_domain_visibility=tuple(sorted(record.supported_domains)),
        mapping_rationale_visibility=tuple(sorted(record.mapping_rationale)),
        provenance_visibility=_provenance_visibility(record),
        analysis_visibility=analysis_visibility,
        integrity_visibility=tuple(sorted(record.integrity_reference_ids)),
    )


def _provenance_visibility(record: OrchestrationIntentPolicyMappingRecord) -> tuple[str, ...]:
    provenance = record.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                provenance.intent_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_visibility(
    record: OrchestrationIntentPolicyMappingRecord,
    analysis_record: OrchestrationIntentPolicyMappingAnalysisRecord,
    analysis_visibility: tuple[str, ...],
) -> bool:
    return bool(
        record.policy_ids
        and record.mapping_rationale
        and record.governance_boundaries
        and record.integrity_reference_ids
        and analysis_visibility
        and analysis_record.findings
    )


def _summary(
    status: str,
    records: tuple[OrchestrationIntentPolicyMappingExplanationRecord, ...],
) -> str:
    if status == MAPPING_EXPLAINABILITY_STABLE:
        return (
            "Intent-policy mapping explainability is stable; policy applicability, governance boundaries, "
            "compatibility domains, dependencies, blockers, unsupported domains, prohibited domains, "
            "provenance, rationale, and integrity references are visible."
        )
    missing = tuple(sorted(record.mapping_id for record in records if record.explanation_status != MAPPING_EXPLAINABILITY_STABLE))
    return f"Intent-policy mapping explainability has visibility gaps for: {', '.join(missing)}."
