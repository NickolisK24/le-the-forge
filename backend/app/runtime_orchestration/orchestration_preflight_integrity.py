"""Deterministic orchestration preflight integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_preflight_evaluator import evaluate_orchestration_preflight
from .orchestration_preflight_explainability import explain_orchestration_preflight
from .orchestration_preflight_models import (
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_EXPLAINABILITY_STABLE,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    PREFLIGHT_INTEGRITY_STABLE,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_STATES,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    OrchestrationPreflightEvaluationInput,
    OrchestrationPreflightIntegrityInput,
    OrchestrationPreflightIntegrityResult,
    OrchestrationPreflightIntegritySummary,
    OrchestrationPreflightRecord,
    OrchestrationPreflightRegistry,
    export_preflight_integrity_result,
    hash_preflight_integrity_result,
    hash_preflight_record,
    hash_preflight_registry,
    serialize_preflight_integrity_result,
    serialize_preflight_registry,
)
from .orchestration_preflight_registry import default_orchestration_preflight_registry


def default_orchestration_preflight_integrity_input() -> OrchestrationPreflightIntegrityInput:
    registry = default_orchestration_preflight_registry()
    evaluation = evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=registry)
    )
    explainability = explain_orchestration_preflight(registry, evaluation)
    return OrchestrationPreflightIntegrityInput(
        preflight_registry=registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
    )


def audit_orchestration_preflight_integrity(
    integrity_input: OrchestrationPreflightIntegrityInput | None = None,
) -> OrchestrationPreflightIntegrityResult:
    source = integrity_input or default_orchestration_preflight_integrity_input()
    registry_hash = hash_preflight_registry(source.preflight_registry)
    registry = _registry_integrity(source, registry_hash)
    preflight_hash = _preflight_hash_integrity(source.preflight_registry)
    provenance = _provenance_integrity(source.preflight_registry)
    explainability = _explainability_integrity(source)
    governance = _governance_integrity(source.preflight_registry)
    compatibility = _compatibility_integrity(source.preflight_registry)
    dependency = _dependency_integrity(source.preflight_registry)
    blocker = _blocker_integrity(source.preflight_registry)
    supported_domain = _supported_domain_integrity(source.preflight_registry)
    policy = _policy_integrity(source.preflight_registry)
    serialization = _serialization_integrity(source.preflight_registry)
    failures = _failure_summary(
        registry,
        preflight_hash,
        provenance,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
        policy,
        serialization,
    )
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _integrity_status(
        registry,
        preflight_hash,
        provenance,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
        policy,
    )
    result = OrchestrationPreflightIntegrityResult(
        registry_id=source.preflight_registry.registry_id,
        preflight_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        preflight_hash_integrity=preflight_hash,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        governance_integrity=governance,
        compatibility_integrity=compatibility,
        dependency_integrity=dependency,
        blocker_integrity=blocker,
        supported_domain_integrity=supported_domain,
        policy_integrity=policy,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_preflight_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_preflight_integrity_hash=hash_preflight_integrity_result(result))


def export_orchestration_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> dict[str, object]:
    return export_preflight_integrity_result(result)


def serialize_orchestration_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> str:
    return serialize_preflight_integrity_result(result)


def hash_orchestration_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> str:
    return hash_preflight_integrity_result(result)


def _registry_integrity(
    source: OrchestrationPreflightIntegrityInput,
    registry_hash: str,
) -> OrchestrationPreflightIntegritySummary:
    failures: list[str] = []
    if not source.preflight_registry.records:
        failures.append("preflight_registry_has_no_records")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("preflight_registry_hash_mismatch")
    if not source.preflight_registry.planning_only or not source.preflight_registry.non_production:
        failures.append("preflight_registry_boundary_not_planning_only_non_production")
    return OrchestrationPreflightIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _preflight_hash_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(f"{record.identifier.preflight_id}:{hash_preflight_record(record)}" for record in registry.records))
    ids = [record.identifier.preflight_id for record in registry.records]
    duplicates = sorted({preflight_id for preflight_id in ids if ids.count(preflight_id) > 1})
    failures = tuple(f"duplicate_preflight_id:{preflight_id}" for preflight_id in duplicates)
    failures += tuple(
        sorted(
            f"{record.identifier.preflight_id}:unrecognized_preflight_state"
            for record in registry.records
            if record.preflight_state not in PREFLIGHT_STATES
        )
    )
    return OrchestrationPreflightIntegritySummary("preflight_hash", references, failures)


def _provenance_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        provenance = record.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                provenance.intent_id,
                provenance.mapping_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{record.identifier.preflight_id}:source_provenance_gap")
        if not provenance.intent_id:
            failures.append(f"{record.identifier.preflight_id}:intent_provenance_gap")
        if not provenance.mapping_id:
            failures.append(f"{record.identifier.preflight_id}:mapping_provenance_gap")
        if not provenance.policy_ids:
            failures.append(f"{record.identifier.preflight_id}:policy_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{record.identifier.preflight_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{record.identifier.preflight_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{record.identifier.preflight_id}:governance_provenance_gap")
    return OrchestrationPreflightIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _explainability_integrity(source: OrchestrationPreflightIntegrityInput) -> OrchestrationPreflightIntegritySummary:
    references = (
        source.evaluation_result.deterministic_preflight_evaluation_hash,
        source.explainability_result.deterministic_preflight_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.preflight_explainability_status != PREFLIGHT_EXPLAINABILITY_STABLE:
        failures.append(f"preflight_explainability_status:{source.explainability_result.preflight_explainability_status}")
    if source.expected_evaluation_hash is not None and source.expected_evaluation_hash != source.evaluation_result.deterministic_preflight_evaluation_hash:
        failures.append("preflight_evaluation_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_preflight_explainability_hash:
        failures.append("preflight_explainability_hash_mismatch")
    return OrchestrationPreflightIntegritySummary("explainability", references, tuple(sorted(failures)))


def _governance_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(record.identifier.preflight_id for record in registry.records))
    failures: list[str] = []
    for record in registry.records:
        if not record.governance_boundaries:
            failures.append(f"{record.identifier.preflight_id}:missing_governance_boundary_visibility")
        if record.preflight_state == PREFLIGHT_GOVERNANCE_BLOCKED and not record.governance_boundaries:
            failures.append(f"{record.identifier.preflight_id}:missing_governance_blocker_visibility")
        if _governance_gap(record):
            failures.append(f"{record.identifier.preflight_id}:governance_boundary_gap")
    return OrchestrationPreflightIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(record.identifier.preflight_id for record in registry.records if record.compatibility_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.preflight_state == PREFLIGHT_COMPATIBILITY_BLOCKED and not record.compatibility_domains:
            failures.append(f"{record.identifier.preflight_id}:missing_compatibility_domain_visibility")
        if record.preflight_state in (PREFLIGHT_UNSUPPORTED, PREFLIGHT_PROHIBITED) and not record.compatibility_domains:
            failures.append(f"{record.identifier.preflight_id}:missing_blocked_compatibility_domain_visibility")
    return OrchestrationPreflightIntegritySummary("compatibility", references, tuple(sorted(failures)))


def _dependency_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(record.identifier.preflight_id for record in registry.records if record.dependency_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.preflight_state == PREFLIGHT_DEPENDENCY_BLOCKED and not record.dependency_domains:
            failures.append(f"{record.identifier.preflight_id}:missing_dependency_domain_visibility")
    return OrchestrationPreflightIntegritySummary("dependency", references, tuple(sorted(failures)))


def _blocker_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(record.identifier.preflight_id for record in registry.records if record.blocker_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.preflight_state != PREFLIGHT_SUPPORTED and not record.blocker_domains:
            failures.append(f"{record.identifier.preflight_id}:missing_blocker_domain_visibility")
    return OrchestrationPreflightIntegritySummary("blocker", references, tuple(sorted(failures)))


def _supported_domain_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted(record.identifier.preflight_id for record in registry.records if record.supported_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.preflight_id}:missing_supported_domain_visibility"
            for record in registry.records
            if record.preflight_state == PREFLIGHT_SUPPORTED and not record.supported_domains
        )
    )
    return OrchestrationPreflightIntegritySummary("supported_domain", references, failures)


def _policy_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    references = tuple(sorted({policy_id for record in registry.records for policy_id in record.policy_ids}))
    failures = tuple(
        sorted(
            f"{record.identifier.preflight_id}:missing_policy_reference_visibility"
            for record in registry.records
            if not record.policy_ids
        )
    )
    return OrchestrationPreflightIntegritySummary("policy", references, failures)


def _serialization_integrity(registry: OrchestrationPreflightRegistry) -> OrchestrationPreflightIntegritySummary:
    first = serialize_preflight_registry(registry)
    second = serialize_preflight_registry(registry)
    failures = () if first == second else ("preflight_registry_serialization_not_stable",)
    return OrchestrationPreflightIntegritySummary("deterministic_serialization", (hash_preflight_registry(registry),), failures)


def _governance_gap(record: OrchestrationPreflightRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "preflight_evaluation_only")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "recommendation_enabled",
        "optimization_enabled",
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
            record.runtime_execution_enabled,
            record.orchestration_execution_enabled,
            record.routing_behavior_enabled,
            record.mutation_behavior_enabled,
            record.production_consumption_enabled,
            record.background_processing_enabled,
            record.recommendation_behavior_enabled,
            record.optimization_behavior_enabled,
            record.autonomous_behavior_enabled,
            record.graph_execution_enabled,
            record.preflight_execution_enabled,
        )
    )


def _failure_summary(*summaries: OrchestrationPreflightIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationPreflightIntegritySummary,
    preflight_hash: OrchestrationPreflightIntegritySummary,
    provenance: OrchestrationPreflightIntegritySummary,
    explainability: OrchestrationPreflightIntegritySummary,
    governance: OrchestrationPreflightIntegritySummary,
    compatibility: OrchestrationPreflightIntegritySummary,
    dependency: OrchestrationPreflightIntegritySummary,
    blocker: OrchestrationPreflightIntegritySummary,
    supported_domain: OrchestrationPreflightIntegritySummary,
    policy: OrchestrationPreflightIntegritySummary,
) -> str:
    if registry.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP if "preflight_registry_hash_mismatch" in registry.failures else PREFLIGHT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if preflight_hash.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if policy.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_POLICY_GAP
    if explainability.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else PREFLIGHT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if governance.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    if dependency.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if blocker.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if supported_domain.failures:
        return PREFLIGHT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    return PREFLIGHT_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == PREFLIGHT_INTEGRITY_STABLE:
        return (
            "Preflight integrity is stable; registry, hashes, provenance, explainability, governance, "
            "compatibility, dependency, blocker, supported-domain, policy, and serialization continuity remain deterministic and non-executing."
        )
    return f"Preflight integrity classified as {status}; failures: {', '.join(failures)}."
