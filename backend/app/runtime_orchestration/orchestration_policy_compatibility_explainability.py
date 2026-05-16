"""Deterministic orchestration policy compatibility explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_compatibility_evaluator import evaluate_orchestration_policy_compatibility_matrix
from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_CONTINUITY_GAP,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    COMPATIBILITY_EXPLAINABILITY_STABLE,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    OrchestrationPolicyCompatibilityEvaluationInput,
    OrchestrationPolicyCompatibilityEvaluationResult,
    OrchestrationPolicyCompatibilityExplainabilityResult,
    OrchestrationPolicyCompatibilityExplanationRecord,
    OrchestrationPolicyCompatibilityRegistry,
    OrchestrationPolicyCompatibilityRelationship,
    export_compatibility_explainability_result,
    hash_compatibility_explainability_result,
    serialize_compatibility_explainability_result,
)
from .orchestration_policy_compatibility_registry import default_orchestration_policy_compatibility_registry


def explain_orchestration_policy_compatibility(
    compatibility_registry: OrchestrationPolicyCompatibilityRegistry | None = None,
    evaluation_result: OrchestrationPolicyCompatibilityEvaluationResult | None = None,
) -> OrchestrationPolicyCompatibilityExplainabilityResult:
    registry = compatibility_registry or default_orchestration_policy_compatibility_registry()
    evaluation = evaluation_result or evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=registry)
    )
    relationships_by_id = {relationship.identifier.relationship_id: relationship for relationship in registry.relationships}
    records = tuple(
        _explain_relationship(relationships_by_id[record.relationship_id], record)
        for record in sorted(evaluation.relationship_records, key=lambda item: item.relationship_id)
        if record.relationship_id in relationships_by_id
    )
    status = (
        COMPATIBILITY_EXPLAINABILITY_STABLE
        if all(_record_has_visibility(record) for record in records)
        else COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationPolicyCompatibilityExplainabilityResult(
        registry_id=registry.registry_id,
        compatibility_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        compatible_explanation_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_COMPATIBLE),
        incompatible_explanation_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_INCOMPATIBLE),
        prohibited_explanation_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_PROHIBITED),
        unsupported_explanation_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_UNSUPPORTED),
        dependency_conflict_visibility_count=sum(len(record.dependency_conflict_chain) for record in records),
        governance_conflict_visibility_count=sum(len(record.governance_conflict_chain) for record in records),
        continuity_conflict_visibility_count=sum(len(record.continuity_conflict_chain) for record in records),
        blocker_chain_visibility_count=sum(len(record.blocker_chain_visibility) for record in records),
        deterministic_compatibility_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_compatibility_explainability_hash=hash_compatibility_explainability_result(result))


def export_orchestration_policy_compatibility_explainability_result(
    result: OrchestrationPolicyCompatibilityExplainabilityResult,
) -> dict[str, object]:
    return export_compatibility_explainability_result(result)


def serialize_orchestration_policy_compatibility_explainability_result(
    result: OrchestrationPolicyCompatibilityExplainabilityResult,
) -> str:
    return serialize_compatibility_explainability_result(result)


def hash_orchestration_policy_compatibility_explainability_result(
    result: OrchestrationPolicyCompatibilityExplainabilityResult,
) -> str:
    return hash_compatibility_explainability_result(result)


def _explain_relationship(relationship: OrchestrationPolicyCompatibilityRelationship, evaluation_record) -> OrchestrationPolicyCompatibilityExplanationRecord:
    blocker_visibility = tuple(
        sorted(
            {f"{blocker.blocker_state}:{blocker.reason}" for blocker in evaluation_record.blockers}
            | {
                f"{chain.blocker_chain_id}:{','.join(sorted(chain.blocker_states))}"
                for chain in relationship.blocker_chains
            }
        )
    )
    continuity_conflicts = _continuity_conflicts(evaluation_record)
    return OrchestrationPolicyCompatibilityExplanationRecord(
        relationship_id=relationship.identifier.relationship_id,
        policy_ids=tuple(sorted(relationship.policy_ids)),
        compatibility_state=relationship.compatibility_state,
        explanation_status=COMPATIBILITY_EXPLAINABILITY_STABLE
        if _has_explanation(relationship, blocker_visibility, continuity_conflicts)
        else COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
        why_compatible=tuple(sorted(relationship.support_rationale)) if relationship.compatibility_state == COMPATIBILITY_COMPATIBLE else (),
        why_incompatible=tuple(sorted(relationship.blocker_reasons)) if relationship.compatibility_state == COMPATIBILITY_INCOMPATIBLE else (),
        why_prohibited=tuple(sorted(relationship.blocker_reasons)) if relationship.compatibility_state == COMPATIBILITY_PROHIBITED else (),
        why_unsupported=tuple(sorted(relationship.blocker_reasons)) if relationship.compatibility_state == COMPATIBILITY_UNSUPPORTED else (),
        dependency_conflict_chain=tuple(
            sorted(
                f"{conflict.conflict_id}:{'|'.join(sorted(conflict.dependency_chain))}"
                for conflict in relationship.dependency_conflicts
            )
        ),
        governance_conflict_chain=tuple(sorted(relationship.governance_conflicts)),
        continuity_conflict_chain=continuity_conflicts,
        blocker_chain_visibility=blocker_visibility,
        provenance_visibility=_provenance_visibility(relationship),
        integrity_visibility=tuple(sorted(relationship.integrity_reference_ids)),
    )


def _continuity_conflicts(evaluation_record) -> tuple[str, ...]:
    conflicts: list[str] = []
    for field in (
        "provenance_continuity_state",
        "governance_continuity_state",
        "integrity_continuity_state",
        "explainability_continuity_state",
    ):
        value = getattr(evaluation_record, field)
        if value == COMPATIBILITY_CONTINUITY_GAP:
            conflicts.append(f"{field}:{value}")
    return tuple(sorted(conflicts))


def _provenance_visibility(relationship: OrchestrationPolicyCompatibilityRelationship) -> tuple[str, ...]:
    provenance = relationship.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.upstream_policy_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _record_has_visibility(record: OrchestrationPolicyCompatibilityExplanationRecord) -> bool:
    return bool(
        record.why_compatible
        or record.why_incompatible
        or record.why_prohibited
        or record.why_unsupported
        or record.dependency_conflict_chain
        or record.governance_conflict_chain
        or record.continuity_conflict_chain
        or record.blocker_chain_visibility
    )


def _has_explanation(
    relationship: OrchestrationPolicyCompatibilityRelationship,
    blocker_visibility: tuple[str, ...],
    continuity_conflicts: tuple[str, ...],
) -> bool:
    return bool(
        relationship.support_rationale
        or relationship.blocker_reasons
        or relationship.dependency_conflicts
        or relationship.governance_conflicts
        or blocker_visibility
        or continuity_conflicts
    )


def _summary(status: str, records: tuple[OrchestrationPolicyCompatibilityExplanationRecord, ...]) -> str:
    if status == COMPATIBILITY_EXPLAINABILITY_STABLE:
        return (
            "Compatibility explainability is stable; compatible, incompatible, prohibited, unsupported, dependency, "
            "governance, blocker-chain, provenance, and integrity visibility are deterministic and planning-only."
        )
    missing = tuple(sorted(record.relationship_id for record in records if record.explanation_status != COMPATIBILITY_EXPLAINABILITY_STABLE))
    return f"Compatibility explainability has visibility gaps for: {', '.join(missing)}."
