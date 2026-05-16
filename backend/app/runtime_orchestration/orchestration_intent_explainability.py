"""Deterministic orchestration intent explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_classifier import classify_orchestration_intents
from .orchestration_intent_models import (
    INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    INTENT_EXPLAINABILITY_STABLE,
    INTENT_PROHIBITED,
    INTENT_SUPPORTED,
    INTENT_UNSUPPORTED,
    OrchestrationIntentClassificationInput,
    OrchestrationIntentClassificationRecord,
    OrchestrationIntentClassificationResult,
    OrchestrationIntentExplainabilityResult,
    OrchestrationIntentExplanationRecord,
    OrchestrationIntentRecord,
    OrchestrationIntentRegistry,
    export_intent_explainability_result,
    hash_intent_explainability_result,
    serialize_intent_explainability_result,
)
from .orchestration_intent_registry import default_orchestration_intent_registry


def explain_orchestration_intents(
    intent_registry: OrchestrationIntentRegistry | None = None,
    classification_result: OrchestrationIntentClassificationResult | None = None,
) -> OrchestrationIntentExplainabilityResult:
    registry = intent_registry or default_orchestration_intent_registry()
    classification = classification_result or classify_orchestration_intents(
        OrchestrationIntentClassificationInput(intent_registry=registry)
    )
    records_by_id = {record.identifier.intent_id: record for record in registry.records}
    classification_by_id = {record.intent_id: record for record in classification.classification_records}
    records = tuple(
        _explain_record(records_by_id[intent_id], classification_by_id[intent_id])
        for intent_id in sorted(records_by_id)
        if intent_id in classification_by_id
    )
    status = (
        INTENT_EXPLAINABILITY_STABLE
        if all(record.explanation_status == INTENT_EXPLAINABILITY_STABLE for record in records)
        else INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationIntentExplainabilityResult(
        registry_id=registry.registry_id,
        intent_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        supported_explanation_count=sum(1 for record in records if record.support_state == INTENT_SUPPORTED),
        unsupported_explanation_count=sum(1 for record in records if record.support_state == INTENT_UNSUPPORTED),
        prohibited_explanation_count=sum(1 for record in records if record.support_state == INTENT_PROHIBITED),
        governance_boundary_visibility_count=sum(len(record.governance_boundary_visibility) for record in records),
        compatibility_domain_visibility_count=sum(len(record.compatibility_domain_visibility) for record in records),
        dependency_domain_visibility_count=sum(len(record.dependency_domain_visibility) for record in records),
        blocker_domain_visibility_count=sum(len(record.blocker_domain_visibility) for record in records),
        unsupported_domain_visibility_count=sum(len(record.unsupported_domain_visibility) for record in records),
        prohibited_domain_visibility_count=sum(len(record.prohibited_domain_visibility) for record in records),
        deterministic_intent_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_intent_explainability_hash=hash_intent_explainability_result(result))


def export_orchestration_intent_explainability_result(
    result: OrchestrationIntentExplainabilityResult,
) -> dict[str, object]:
    return export_intent_explainability_result(result)


def serialize_orchestration_intent_explainability_result(
    result: OrchestrationIntentExplainabilityResult,
) -> str:
    return serialize_intent_explainability_result(result)


def hash_orchestration_intent_explainability_result(
    result: OrchestrationIntentExplainabilityResult,
) -> str:
    return hash_intent_explainability_result(result)


def _explain_record(
    record: OrchestrationIntentRecord,
    classification_record: OrchestrationIntentClassificationRecord,
) -> OrchestrationIntentExplanationRecord:
    classification_visibility = tuple(
        sorted(
            f"{finding.classification}:{finding.reason}"
            for finding in classification_record.findings
        )
    )
    explanation_status = (
        INTENT_EXPLAINABILITY_STABLE
        if _has_visibility(record, classification_record, classification_visibility)
        else INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationIntentExplanationRecord(
        intent_id=record.identifier.intent_id,
        intent_type=record.intent_type,
        support_state=record.support_state,
        explanation_status=explanation_status,
        intent_goal_visibility=(record.intent_goal,),
        policy_domain_visibility=tuple(sorted(record.policy_domains)),
        compatibility_domain_visibility=tuple(sorted(record.compatibility_domains)),
        governance_boundary_visibility=tuple(sorted(record.governance_boundaries)),
        dependency_domain_visibility=tuple(sorted(record.dependency_domains)),
        blocker_domain_visibility=tuple(sorted(record.blocker_domains)),
        unsupported_domain_visibility=tuple(sorted(record.unsupported_domains)),
        prohibited_domain_visibility=tuple(sorted(record.prohibited_domains)),
        supported_domain_visibility=tuple(sorted(record.supported_domains)),
        provenance_visibility=_provenance_visibility(record),
        classification_visibility=classification_visibility,
        integrity_visibility=tuple(sorted(record.integrity_reference_ids)),
    )


def _provenance_visibility(record: OrchestrationIntentRecord) -> tuple[str, ...]:
    provenance = record.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.upstream_policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.resolution_record_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_visibility(
    record: OrchestrationIntentRecord,
    classification_record: OrchestrationIntentClassificationRecord,
    classification_visibility: tuple[str, ...],
) -> bool:
    return bool(
        record.intent_goal
        and record.policy_domains
        and record.governance_boundaries
        and record.integrity_reference_ids
        and classification_visibility
        and classification_record.findings
    )


def _summary(
    status: str,
    records: tuple[OrchestrationIntentExplanationRecord, ...],
) -> str:
    if status == INTENT_EXPLAINABILITY_STABLE:
        return (
            "Intent explainability is stable; goals, policy domains, compatibility domains, governance boundaries, "
            "dependencies, blockers, unsupported domains, prohibited domains, provenance, and integrity references are visible."
        )
    missing = tuple(sorted(record.intent_id for record in records if record.explanation_status != INTENT_EXPLAINABILITY_STABLE))
    return f"Intent explainability has visibility gaps for: {', '.join(missing)}."
