"""Deterministic orchestration policy compatibility evaluation for v3.6 Phase 2."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_BLOCKED_BY_CONTINUITY_GAP,
    COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
    COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY,
    COMPATIBILITY_BLOCKED_BY_INTEGRITY_GAP,
    COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
    COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_CONTINUITY_GAP,
    COMPATIBILITY_CONTINUITY_PRESERVED,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP,
    COMPATIBILITY_EVALUATION_REQUIRES_MANUAL_REVIEW,
    COMPATIBILITY_EVALUATION_STABLE,
    COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    OrchestrationPolicyCompatibilityBlocker,
    OrchestrationPolicyCompatibilityEvaluationInput,
    OrchestrationPolicyCompatibilityEvaluationRecord,
    OrchestrationPolicyCompatibilityEvaluationResult,
    OrchestrationPolicyCompatibilityRelationship,
    export_compatibility_evaluation_result,
    hash_compatibility_evaluation_result,
    hash_compatibility_registry,
    hash_compatibility_relationship,
    serialize_compatibility_evaluation_result,
)
from .orchestration_policy_compatibility_registry import default_orchestration_policy_compatibility_registry


STRUCTURAL_BLOCKER_STATES: frozenset[str] = frozenset(
    {
        COMPATIBILITY_BLOCKED_BY_CONTINUITY_GAP,
        COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP,
        COMPATIBILITY_BLOCKED_BY_INTEGRITY_GAP,
        COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_GAP,
        COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
    }
)


def default_orchestration_policy_compatibility_evaluation_input() -> OrchestrationPolicyCompatibilityEvaluationInput:
    return OrchestrationPolicyCompatibilityEvaluationInput(
        compatibility_registry=default_orchestration_policy_compatibility_registry()
    )


def evaluate_orchestration_policy_compatibility_matrix(
    evaluation_input: OrchestrationPolicyCompatibilityEvaluationInput | None = None,
) -> OrchestrationPolicyCompatibilityEvaluationResult:
    source = evaluation_input or default_orchestration_policy_compatibility_evaluation_input()
    records = tuple(_evaluate_relationship(relationship, source) for relationship in source.compatibility_registry.relationships)
    blockers = tuple(sorted((blocker for record in records for blocker in record.blockers), key=_blocker_sort_key))
    registry_hash = hash_compatibility_registry(source.compatibility_registry)
    registry_hash_blocker = _registry_hash_blocker(source, registry_hash)
    if registry_hash_blocker is not None:
        blockers = tuple(sorted(blockers + (registry_hash_blocker,), key=_blocker_sort_key))
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _evaluation_status(blockers, manual_review)
    result = OrchestrationPolicyCompatibilityEvaluationResult(
        registry_id=source.compatibility_registry.registry_id,
        compatibility_evaluation_status=status,
        planning_only=True,
        non_production=True,
        relationship_records=records,
        registered_relationship_count=len(records),
        compatible_relationship_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_COMPATIBLE),
        incompatible_relationship_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_INCOMPATIBLE),
        prohibited_relationship_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_PROHIBITED),
        unsupported_relationship_count=sum(1 for record in records if record.compatibility_state == COMPATIBILITY_UNSUPPORTED),
        dependency_conflict_count=sum(record.dependency_conflict_count for record in records),
        governance_conflict_count=sum(record.governance_conflict_count for record in records),
        blocker_chain_count=sum(record.blocker_chain_count for record in records),
        blocker_count=len(blockers),
        multi_policy_compatibility_state=_multi_policy_state(source.selected_policy_ids, records),
        selected_policy_ids=tuple(sorted(source.selected_policy_ids)),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        blocker_summary=blockers,
        manual_review_summary=manual_review,
        deterministic_registry_hash=registry_hash,
        deterministic_compatibility_evaluation_hash="",
        deterministic_explanation_summary=_explanation(status, blockers),
    )
    return replace(result, deterministic_compatibility_evaluation_hash=hash_compatibility_evaluation_result(result))


def export_orchestration_policy_compatibility_evaluation_result(
    result: OrchestrationPolicyCompatibilityEvaluationResult,
) -> dict[str, object]:
    return export_compatibility_evaluation_result(result)


def serialize_orchestration_policy_compatibility_evaluation_result(
    result: OrchestrationPolicyCompatibilityEvaluationResult,
) -> str:
    return serialize_compatibility_evaluation_result(result)


def hash_orchestration_policy_compatibility_evaluation_result(
    result: OrchestrationPolicyCompatibilityEvaluationResult,
) -> str:
    return hash_compatibility_evaluation_result(result)


def _evaluate_relationship(
    relationship: OrchestrationPolicyCompatibilityRelationship,
    source: OrchestrationPolicyCompatibilityEvaluationInput,
) -> OrchestrationPolicyCompatibilityEvaluationRecord:
    relationship_id = relationship.identifier.relationship_id
    relationship_hash = hash_compatibility_relationship(relationship)
    blockers = _state_blockers(relationship)
    blockers.extend(_dependency_blockers(relationship))
    blockers.extend(_governance_conflict_blockers(relationship))
    blockers.extend(_provenance_blockers(relationship))
    blockers.extend(_reference_blockers(relationship_id, relationship.integrity_reference_ids, COMPATIBILITY_BLOCKED_BY_INTEGRITY_GAP))
    blockers.extend(_reference_blockers(relationship_id, relationship.explainability_reference_ids, COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_GAP))
    expected_hash = source.expected_relationship_hashes.get(relationship_id) if source.expected_relationship_hashes else None
    if expected_hash is not None and expected_hash != relationship_hash:
        blockers.append(
            OrchestrationPolicyCompatibilityBlocker(
                relationship_id=relationship_id,
                blocker_state=COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
                reason="compatibility relationship hash does not match expected deterministic hash",
                evidence_ids=(relationship_hash, expected_hash),
            )
        )
    return OrchestrationPolicyCompatibilityEvaluationRecord(
        relationship_id=relationship_id,
        policy_ids=tuple(sorted(relationship.policy_ids)),
        compatibility_state=relationship.compatibility_state,
        relationship_hash=relationship_hash,
        dependency_conflict_count=len(relationship.dependency_conflicts),
        governance_conflict_count=len(relationship.governance_conflicts),
        blocker_chain_count=len(relationship.blocker_chains),
        provenance_continuity_state=COMPATIBILITY_CONTINUITY_GAP if _provenance_blockers(relationship) else COMPATIBILITY_CONTINUITY_PRESERVED,
        governance_continuity_state=COMPATIBILITY_CONTINUITY_GAP if _governance_continuity_gap(relationship) else COMPATIBILITY_CONTINUITY_PRESERVED,
        integrity_continuity_state=COMPATIBILITY_CONTINUITY_GAP if not relationship.integrity_reference_ids else COMPATIBILITY_CONTINUITY_PRESERVED,
        explainability_continuity_state=COMPATIBILITY_CONTINUITY_GAP if not relationship.explainability_reference_ids else COMPATIBILITY_CONTINUITY_PRESERVED,
        blockers=tuple(sorted(blockers, key=_blocker_sort_key)),
    )


def _state_blockers(relationship: OrchestrationPolicyCompatibilityRelationship) -> list[OrchestrationPolicyCompatibilityBlocker]:
    blocker_state_by_compatibility = {
        COMPATIBILITY_INCOMPATIBLE: COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY,
        COMPATIBILITY_PROHIBITED: COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
        COMPATIBILITY_UNSUPPORTED: COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
        COMPATIBILITY_DEPENDENCY_BLOCKED: COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
        COMPATIBILITY_GOVERNANCE_BLOCKED: COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
    }
    blocker_state = blocker_state_by_compatibility.get(relationship.compatibility_state)
    if blocker_state is None:
        return []
    return [
        OrchestrationPolicyCompatibilityBlocker(
            relationship_id=relationship.identifier.relationship_id,
            blocker_state=blocker_state,
            reason=reason,
            evidence_ids=relationship.policy_ids,
        )
        for reason in sorted(relationship.blocker_reasons or (relationship.compatibility_state,))
    ]


def _dependency_blockers(relationship: OrchestrationPolicyCompatibilityRelationship) -> list[OrchestrationPolicyCompatibilityBlocker]:
    return [
        OrchestrationPolicyCompatibilityBlocker(
            relationship_id=relationship.identifier.relationship_id,
            blocker_state=COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
            reason=conflict.conflict_reason,
            evidence_ids=conflict.dependency_chain,
        )
        for conflict in relationship.dependency_conflicts
    ]


def _governance_conflict_blockers(relationship: OrchestrationPolicyCompatibilityRelationship) -> list[OrchestrationPolicyCompatibilityBlocker]:
    return [
        OrchestrationPolicyCompatibilityBlocker(
            relationship_id=relationship.identifier.relationship_id,
            blocker_state=COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
            reason=conflict,
            evidence_ids=relationship.policy_ids,
        )
        for conflict in relationship.governance_conflicts
    ]


def _provenance_blockers(relationship: OrchestrationPolicyCompatibilityRelationship) -> list[OrchestrationPolicyCompatibilityBlocker]:
    provenance = relationship.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    if not missing:
        return []
    return [
        OrchestrationPolicyCompatibilityBlocker(
            relationship_id=relationship.identifier.relationship_id,
            blocker_state=COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP,
            reason="compatibility provenance continuity gap",
            evidence_ids=tuple(sorted(missing)),
        )
    ]


def _reference_blockers(relationship_id: str, references: tuple[str, ...], blocker_state: str) -> list[OrchestrationPolicyCompatibilityBlocker]:
    if references:
        return []
    return [
        OrchestrationPolicyCompatibilityBlocker(
            relationship_id=relationship_id,
            blocker_state=blocker_state,
            reason="compatibility continuity reference is missing",
            evidence_ids=(blocker_state,),
        )
    ]


def _governance_continuity_gap(relationship: OrchestrationPolicyCompatibilityRelationship) -> bool:
    metadata = relationship.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "autonomy_enabled",
        "production_runtime_reads_enabled",
        "production_runtime_writes_enabled",
        "persistent_writes_enabled",
    )
    if any(metadata.get(key) is not True for key in required_true):
        return True
    if any(metadata.get(key) is not False for key in required_false):
        return True
    return any(
        (
            relationship.runtime_execution_enabled,
            relationship.orchestration_execution_enabled,
            relationship.routing_behavior_enabled,
            relationship.mutation_behavior_enabled,
            relationship.audit_log_writing_enabled,
            relationship.production_consumption_enabled,
            relationship.graph_execution_enabled,
            relationship.graph_traversal_behavior_enabled,
            relationship.scheduling_behavior_enabled,
            relationship.orchestration_dispatch_enabled,
            relationship.runtime_trace_capture_enabled,
            relationship.production_state_reads_enabled,
            relationship.live_replay_enabled,
            relationship.persistent_audit_storage_enabled,
            relationship.compatibility_execution_enabled,
        )
    )


def _registry_hash_blocker(source: OrchestrationPolicyCompatibilityEvaluationInput, registry_hash: str) -> OrchestrationPolicyCompatibilityBlocker | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationPolicyCompatibilityBlocker(
        relationship_id=source.compatibility_registry.registry_id,
        blocker_state=COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
        reason="compatibility registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _multi_policy_state(
    selected_policy_ids: tuple[str, ...],
    records: tuple[OrchestrationPolicyCompatibilityEvaluationRecord, ...],
) -> str:
    if len(selected_policy_ids) < 2:
        return COMPATIBILITY_COMPATIBLE
    selected = set(selected_policy_ids)
    matching = [record for record in records if set(record.policy_ids).issubset(selected)]
    priority = (
        COMPATIBILITY_PROHIBITED,
        COMPATIBILITY_UNSUPPORTED,
        COMPATIBILITY_DEPENDENCY_BLOCKED,
        COMPATIBILITY_GOVERNANCE_BLOCKED,
        COMPATIBILITY_INCOMPATIBLE,
        COMPATIBILITY_COMPATIBLE,
    )
    states = {record.compatibility_state for record in matching}
    for state in priority:
        if state in states:
            return state
    return COMPATIBILITY_COMPATIBLE


def _continuity_status(records: tuple[OrchestrationPolicyCompatibilityEvaluationRecord, ...], field: str) -> str:
    return COMPATIBILITY_CONTINUITY_PRESERVED if all(getattr(record, field) == COMPATIBILITY_CONTINUITY_PRESERVED for record in records) else COMPATIBILITY_CONTINUITY_GAP


def _evaluation_status(blockers: tuple[OrchestrationPolicyCompatibilityBlocker, ...], manual_review: tuple[str, ...]) -> str:
    if any(blocker.blocker_state in STRUCTURAL_BLOCKER_STATES for blocker in blockers):
        return COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP
    if manual_review:
        return COMPATIBILITY_EVALUATION_REQUIRES_MANUAL_REVIEW
    if blockers:
        return COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS
    return COMPATIBILITY_EVALUATION_STABLE


def _explanation(status: str, blockers: tuple[OrchestrationPolicyCompatibilityBlocker, ...]) -> str:
    if status == COMPATIBILITY_EVALUATION_STABLE:
        return "Compatibility evaluation is stable; all selected relationship evidence is compatible and planning-only."
    if status == COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS:
        return "Compatibility evaluation is stable with visible incompatible, prohibited, unsupported, dependency, and governance blockers."
    visible = tuple(sorted({f"{blocker.relationship_id}:{blocker.blocker_state}" for blocker in blockers}))
    return f"Compatibility evaluation classified as {status}; visible compatibility entries: {', '.join(visible)}."


def _blocker_sort_key(blocker: OrchestrationPolicyCompatibilityBlocker) -> tuple[str, str, str]:
    return (blocker.relationship_id, blocker.blocker_state, blocker.reason)
