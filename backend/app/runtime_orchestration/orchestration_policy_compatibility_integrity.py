"""Deterministic orchestration policy compatibility integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_compatibility_evaluator import evaluate_orchestration_policy_compatibility_matrix
from .orchestration_policy_compatibility_explainability import explain_orchestration_policy_compatibility
from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_EXPLAINABILITY_STABLE,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_CLASSIFICATION_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    COMPATIBILITY_INTEGRITY_REQUIRES_MANUAL_REVIEW,
    COMPATIBILITY_INTEGRITY_STABLE,
    COMPATIBILITY_STATES,
    OrchestrationPolicyCompatibilityEvaluationInput,
    OrchestrationPolicyCompatibilityIntegrityInput,
    OrchestrationPolicyCompatibilityIntegrityResult,
    OrchestrationPolicyCompatibilityIntegritySummary,
    OrchestrationPolicyCompatibilityRegistry,
    export_compatibility_integrity_result,
    hash_compatibility_integrity_result,
    hash_compatibility_registry,
    hash_compatibility_relationship,
    serialize_compatibility_integrity_result,
    serialize_compatibility_registry,
)
from .orchestration_policy_compatibility_registry import default_orchestration_policy_compatibility_registry


def default_orchestration_policy_compatibility_integrity_input() -> OrchestrationPolicyCompatibilityIntegrityInput:
    registry = default_orchestration_policy_compatibility_registry()
    evaluation = evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=registry)
    )
    explainability = explain_orchestration_policy_compatibility(registry, evaluation)
    return OrchestrationPolicyCompatibilityIntegrityInput(
        compatibility_registry=registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
    )


def audit_orchestration_policy_compatibility_integrity(
    integrity_input: OrchestrationPolicyCompatibilityIntegrityInput | None = None,
) -> OrchestrationPolicyCompatibilityIntegrityResult:
    source = integrity_input or default_orchestration_policy_compatibility_integrity_input()
    registry_hash = hash_compatibility_registry(source.compatibility_registry)
    registry = _registry_integrity(source, registry_hash)
    compatibility_hash = _compatibility_hash_integrity(source.compatibility_registry)
    provenance = _provenance_integrity(source.compatibility_registry)
    dependency = _dependency_integrity(source)
    governance = _governance_integrity(source)
    explainability = _explainability_integrity(source)
    classification = _classification_integrity(source)
    blocker_chain = _blocker_chain_integrity(source)
    serialization = _serialization_integrity(source.compatibility_registry)
    failures = _failure_summary(
        registry,
        compatibility_hash,
        provenance,
        dependency,
        governance,
        explainability,
        classification,
        blocker_chain,
        serialization,
    )
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _integrity_status(
        registry,
        compatibility_hash,
        provenance,
        dependency,
        governance,
        explainability,
        classification,
        blocker_chain,
        manual_review,
    )
    result = OrchestrationPolicyCompatibilityIntegrityResult(
        registry_id=source.compatibility_registry.registry_id,
        compatibility_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        compatibility_hash_integrity=compatibility_hash,
        provenance_integrity=provenance,
        dependency_integrity=dependency,
        governance_integrity=governance,
        explainability_integrity=explainability,
        classification_integrity=classification,
        blocker_chain_integrity=blocker_chain,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_compatibility_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_compatibility_integrity_hash=hash_compatibility_integrity_result(result))


def export_orchestration_policy_compatibility_integrity_result(
    result: OrchestrationPolicyCompatibilityIntegrityResult,
) -> dict[str, object]:
    return export_compatibility_integrity_result(result)


def serialize_orchestration_policy_compatibility_integrity_result(
    result: OrchestrationPolicyCompatibilityIntegrityResult,
) -> str:
    return serialize_compatibility_integrity_result(result)


def hash_orchestration_policy_compatibility_integrity_result(
    result: OrchestrationPolicyCompatibilityIntegrityResult,
) -> str:
    return hash_compatibility_integrity_result(result)


def _registry_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput, registry_hash: str) -> OrchestrationPolicyCompatibilityIntegritySummary:
    failures: list[str] = []
    if not source.compatibility_registry.relationships:
        failures.append("compatibility_registry_has_no_relationships")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("compatibility_registry_hash_mismatch")
    if not source.compatibility_registry.planning_only or not source.compatibility_registry.non_production:
        failures.append("compatibility_registry_boundary_not_planning_only_non_production")
    return OrchestrationPolicyCompatibilityIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _compatibility_hash_integrity(registry: OrchestrationPolicyCompatibilityRegistry) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = tuple(sorted(f"{relationship.identifier.relationship_id}:{hash_compatibility_relationship(relationship)}" for relationship in registry.relationships))
    ids = [relationship.identifier.relationship_id for relationship in registry.relationships]
    duplicates = sorted({relationship_id for relationship_id in ids if ids.count(relationship_id) > 1})
    failures = tuple(f"duplicate_compatibility_relationship_id:{relationship_id}" for relationship_id in duplicates)
    return OrchestrationPolicyCompatibilityIntegritySummary("compatibility_hash", references, failures)


def _provenance_integrity(registry: OrchestrationPolicyCompatibilityRegistry) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for relationship in registry.relationships:
        provenance = relationship.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.upstream_policy_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{relationship.identifier.relationship_id}:source_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{relationship.identifier.relationship_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{relationship.identifier.relationship_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{relationship.identifier.relationship_id}:governance_provenance_gap")
    return OrchestrationPolicyCompatibilityIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _dependency_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = tuple(sorted(record.relationship_id for record in source.evaluation_result.relationship_records))
    failures = tuple(
        sorted(
            f"{record.relationship_id}:missing_dependency_conflict_visibility"
            for record in source.evaluation_result.relationship_records
            if record.compatibility_state == "compatibility_dependency_blocked" and record.dependency_conflict_count == 0
        )
    )
    return OrchestrationPolicyCompatibilityIntegritySummary("dependency", references, failures)


def _governance_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = tuple(sorted(record.relationship_id for record in source.evaluation_result.relationship_records))
    failures: list[str] = []
    for record in source.evaluation_result.relationship_records:
        if record.compatibility_state == "compatibility_governance_blocked" and record.governance_conflict_count == 0:
            failures.append(f"{record.relationship_id}:missing_governance_conflict_visibility")
        if record.governance_continuity_state == "compatibility_continuity_gap":
            failures.append(f"{record.relationship_id}:governance_continuity_gap")
    for field in (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "routing_behavior_enabled",
        "mutation_behavior_enabled",
        "production_consumption_enabled",
        "compatibility_execution_enabled",
    ):
        if getattr(source.evaluation_result, field):
            failures.append(f"{field}:enabled")
    return OrchestrationPolicyCompatibilityIntegritySummary("governance", references, tuple(sorted(failures)))


def _explainability_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = (source.explainability_result.deterministic_compatibility_explainability_hash,)
    failures: list[str] = []
    if source.explainability_result.compatibility_explainability_status != COMPATIBILITY_EXPLAINABILITY_STABLE:
        failures.append(f"compatibility_explainability_status:{source.explainability_result.compatibility_explainability_status}")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_compatibility_explainability_hash:
        failures.append("compatibility_explainability_hash_mismatch")
    if source.expected_evaluation_hash is not None and source.expected_evaluation_hash != source.evaluation_result.deterministic_compatibility_evaluation_hash:
        failures.append("compatibility_evaluation_hash_mismatch")
    return OrchestrationPolicyCompatibilityIntegritySummary("explainability", references, tuple(sorted(failures)))


def _classification_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = tuple(sorted(f"{record.relationship_id}:{record.compatibility_state}" for record in source.evaluation_result.relationship_records))
    failures = tuple(
        sorted(
            f"{record.relationship_id}:unknown_compatibility_state:{record.compatibility_state}"
            for record in source.evaluation_result.relationship_records
            if record.compatibility_state not in COMPATIBILITY_STATES
        )
    )
    return OrchestrationPolicyCompatibilityIntegritySummary("classification", references, failures)


def _blocker_chain_integrity(source: OrchestrationPolicyCompatibilityIntegrityInput) -> OrchestrationPolicyCompatibilityIntegritySummary:
    references = tuple(sorted(f"{blocker.relationship_id}:{blocker.blocker_state}" for blocker in source.evaluation_result.blocker_summary))
    failures = () if len(source.evaluation_result.blocker_summary) == source.evaluation_result.blocker_count else ("compatibility_blocker_count_mismatch",)
    return OrchestrationPolicyCompatibilityIntegritySummary("blocker_chain", references, failures)


def _serialization_integrity(registry: OrchestrationPolicyCompatibilityRegistry) -> OrchestrationPolicyCompatibilityIntegritySummary:
    first = serialize_compatibility_registry(registry)
    second = serialize_compatibility_registry(registry)
    failures = () if first == second else ("compatibility_registry_serialization_not_stable",)
    return OrchestrationPolicyCompatibilityIntegritySummary("deterministic_serialization", (hash_compatibility_registry(registry),), failures)


def _failure_summary(*summaries: OrchestrationPolicyCompatibilityIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationPolicyCompatibilityIntegritySummary,
    compatibility_hash: OrchestrationPolicyCompatibilityIntegritySummary,
    provenance: OrchestrationPolicyCompatibilityIntegritySummary,
    dependency: OrchestrationPolicyCompatibilityIntegritySummary,
    governance: OrchestrationPolicyCompatibilityIntegritySummary,
    explainability: OrchestrationPolicyCompatibilityIntegritySummary,
    classification: OrchestrationPolicyCompatibilityIntegritySummary,
    blocker_chain: OrchestrationPolicyCompatibilityIntegritySummary,
    manual_review: tuple[str, ...],
) -> str:
    if registry.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP if "compatibility_registry_hash_mismatch" in registry.failures else COMPATIBILITY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if compatibility_hash.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if dependency.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if governance.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if explainability.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if classification.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_CLASSIFICATION_GAP
    if blocker_chain.failures:
        return COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if manual_review:
        return COMPATIBILITY_INTEGRITY_REQUIRES_MANUAL_REVIEW
    return COMPATIBILITY_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == COMPATIBILITY_INTEGRITY_STABLE:
        return (
            "Compatibility integrity is stable; registry, hashes, provenance, dependency, governance, explainability, "
            "classification, blocker-chain, and serialization continuity remain deterministic and non-executing."
        )
    return f"Compatibility integrity classified as {status}; failures: {', '.join(failures)}."
