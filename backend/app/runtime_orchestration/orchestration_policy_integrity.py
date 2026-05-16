"""Deterministic orchestration policy integrity auditing for v3.6."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_evaluator import evaluate_orchestration_policy_compatibility
from .orchestration_policy_explainability import explain_orchestration_policy_evaluation
from .orchestration_policy_models import (
    POLICY_CONTINUITY_GAP,
    POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP,
    POLICY_EXPLAINABILITY_STABLE,
    POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_INTEGRITY_BLOCKED_BY_POLICY_HASH_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    POLICY_INTEGRITY_REQUIRES_MANUAL_REVIEW,
    POLICY_INTEGRITY_STABLE,
    OrchestrationPolicyIntegrityInput,
    OrchestrationPolicyIntegrityResult,
    OrchestrationPolicyIntegritySummary,
    OrchestrationPolicyRegistry,
    export_policy_integrity_result,
    hash_policy_definition,
    hash_policy_integrity_result,
    hash_policy_registry,
    serialize_policy_integrity_result,
    serialize_policy_registry,
)
from .orchestration_policy_registry import default_orchestration_policy_registry


def default_orchestration_policy_integrity_input() -> OrchestrationPolicyIntegrityInput:
    registry = default_orchestration_policy_registry()
    evaluation = evaluate_orchestration_policy_compatibility()
    explainability = explain_orchestration_policy_evaluation(registry, evaluation)
    return OrchestrationPolicyIntegrityInput(
        registry=registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
    )


def audit_orchestration_policy_integrity(
    integrity_input: OrchestrationPolicyIntegrityInput | None = None,
) -> OrchestrationPolicyIntegrityResult:
    source = integrity_input or default_orchestration_policy_integrity_input()
    registry_hash = hash_policy_registry(source.registry)
    registry = _registry_integrity(source, registry_hash)
    policy_hash = _policy_hash_integrity(source.registry)
    provenance = _provenance_integrity(source.registry)
    dependency = _dependency_integrity(source)
    governance = _governance_integrity(source)
    explainability = _explainability_integrity(source)
    evaluation = _evaluation_integrity(source)
    serialization = _serialization_integrity(source.registry)
    blocker_visibility = _blocker_visibility_integrity(source)
    failures = _failure_summary(
        registry,
        policy_hash,
        provenance,
        dependency,
        governance,
        explainability,
        evaluation,
        serialization,
        blocker_visibility,
    )
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _integrity_status(
        registry,
        policy_hash,
        provenance,
        dependency,
        governance,
        explainability,
        evaluation,
        manual_review,
    )
    result = OrchestrationPolicyIntegrityResult(
        registry_id=source.registry.registry_id,
        policy_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        policy_hash_integrity=policy_hash,
        provenance_integrity=provenance,
        dependency_integrity=dependency,
        governance_integrity=governance,
        explainability_integrity=explainability,
        evaluation_integrity=evaluation,
        deterministic_serialization_integrity=serialization,
        blocker_visibility_integrity=blocker_visibility,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_policy_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_policy_integrity_hash=hash_policy_integrity_result(result))


def export_orchestration_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> dict[str, object]:
    return export_policy_integrity_result(result)


def serialize_orchestration_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> str:
    return serialize_policy_integrity_result(result)


def hash_orchestration_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> str:
    return hash_policy_integrity_result(result)


def _registry_integrity(source: OrchestrationPolicyIntegrityInput, registry_hash: str) -> OrchestrationPolicyIntegritySummary:
    failures: list[str] = []
    if not source.registry.policies:
        failures.append("registry_has_no_policies")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("registry_hash_mismatch")
    if not source.registry.planning_only or not source.registry.non_production:
        failures.append("registry_boundary_not_planning_only_non_production")
    return OrchestrationPolicyIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _policy_hash_integrity(registry: OrchestrationPolicyRegistry) -> OrchestrationPolicyIntegritySummary:
    references = tuple(sorted(f"{policy.identifier.policy_id}:{hash_policy_definition(policy)}" for policy in registry.policies))
    ids = [policy.identifier.policy_id for policy in registry.policies]
    duplicates = sorted({policy_id for policy_id in ids if ids.count(policy_id) > 1})
    failures = tuple(f"duplicate_policy_id:{policy_id}" for policy_id in duplicates)
    return OrchestrationPolicyIntegritySummary("policy_hash", references, failures)


def _provenance_integrity(registry: OrchestrationPolicyRegistry) -> OrchestrationPolicyIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for policy in registry.policies:
        provenance = policy.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{policy.identifier.policy_id}:source_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{policy.identifier.policy_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{policy.identifier.policy_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{policy.identifier.policy_id}:governance_provenance_gap")
    return OrchestrationPolicyIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _dependency_integrity(source: OrchestrationPolicyIntegrityInput) -> OrchestrationPolicyIntegritySummary:
    references = tuple(sorted(record.policy_id for record in source.evaluation_result.policy_records))
    failures = tuple(
        sorted(
            f"{record.policy_id}:{record.dependency_state}"
            for record in source.evaluation_result.policy_records
            if record.dependency_state != "policy_dependency_satisfied"
        )
    )
    return OrchestrationPolicyIntegritySummary("dependency", references, failures)


def _governance_integrity(source: OrchestrationPolicyIntegrityInput) -> OrchestrationPolicyIntegritySummary:
    references = tuple(sorted(source.evaluation_result.supported_policy_ids + source.evaluation_result.prohibited_policy_ids + source.evaluation_result.unsupported_policy_ids))
    failures: list[str] = []
    if source.evaluation_result.governance_continuity_status == POLICY_CONTINUITY_GAP:
        failures.append("governance_continuity_gap")
    for field in (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "routing_behavior_enabled",
        "mutation_behavior_enabled",
        "production_consumption_enabled",
        "policy_execution_enabled",
    ):
        if getattr(source.evaluation_result, field):
            failures.append(f"{field}:enabled")
    return OrchestrationPolicyIntegritySummary("governance", references, tuple(sorted(failures)))


def _explainability_integrity(source: OrchestrationPolicyIntegrityInput) -> OrchestrationPolicyIntegritySummary:
    references = (source.explainability_result.deterministic_explainability_hash,)
    failures: list[str] = []
    if source.explainability_result.explainability_status != POLICY_EXPLAINABILITY_STABLE:
        failures.append(f"explainability_status:{source.explainability_result.explainability_status}")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_explainability_hash:
        failures.append("explainability_hash_mismatch")
    return OrchestrationPolicyIntegritySummary("explainability", references, tuple(sorted(failures)))


def _evaluation_integrity(source: OrchestrationPolicyIntegrityInput) -> OrchestrationPolicyIntegritySummary:
    references = (source.evaluation_result.deterministic_policy_evaluation_hash,)
    failures: list[str] = []
    if source.evaluation_result.policy_evaluation_status == POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP:
        failures.append(f"evaluation_status:{source.evaluation_result.policy_evaluation_status}")
    if source.expected_evaluation_hash is not None and source.expected_evaluation_hash != source.evaluation_result.deterministic_policy_evaluation_hash:
        failures.append("evaluation_hash_mismatch")
    return OrchestrationPolicyIntegritySummary("evaluation", references, tuple(sorted(failures)))


def _serialization_integrity(registry: OrchestrationPolicyRegistry) -> OrchestrationPolicyIntegritySummary:
    first = serialize_policy_registry(registry)
    second = serialize_policy_registry(registry)
    failures = () if first == second else ("registry_serialization_not_stable",)
    return OrchestrationPolicyIntegritySummary("deterministic_serialization", (hash_policy_registry(registry),), failures)


def _blocker_visibility_integrity(source: OrchestrationPolicyIntegrityInput) -> OrchestrationPolicyIntegritySummary:
    blockers = source.evaluation_result.blocker_summary
    references = tuple(sorted({f"{blocker.policy_id}:{blocker.blocker_state}" for blocker in blockers}))
    failures = () if len(blockers) == source.evaluation_result.blocker_count else ("blocker_count_mismatch",)
    return OrchestrationPolicyIntegritySummary("blocker_visibility", references, failures)


def _failure_summary(*summaries: OrchestrationPolicyIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationPolicyIntegritySummary,
    policy_hash: OrchestrationPolicyIntegritySummary,
    provenance: OrchestrationPolicyIntegritySummary,
    dependency: OrchestrationPolicyIntegritySummary,
    governance: OrchestrationPolicyIntegritySummary,
    explainability: OrchestrationPolicyIntegritySummary,
    evaluation: OrchestrationPolicyIntegritySummary,
    manual_review: tuple[str, ...],
) -> str:
    if registry.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH if "registry_hash_mismatch" in registry.failures else POLICY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if policy_hash.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_POLICY_HASH_GAP
    if provenance.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if dependency.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if governance.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if explainability.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH if "explainability_hash_mismatch" in explainability.failures else POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if evaluation.failures:
        return POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH if "evaluation_hash_mismatch" in evaluation.failures else POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if manual_review:
        return POLICY_INTEGRITY_REQUIRES_MANUAL_REVIEW
    return POLICY_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == POLICY_INTEGRITY_STABLE:
        return (
            "Policy integrity is stable; registry, policy hashes, provenance, dependency, governance, explainability, "
            "evaluation, serialization, and blocker visibility remain deterministic and non-executing."
        )
    return f"Policy integrity classified as {status}; failures: {', '.join(failures)}."
