"""Deterministic orchestration intent integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_classifier import classify_orchestration_intents
from .orchestration_intent_explainability import explain_orchestration_intents
from .orchestration_intent_models import (
    INTENT_COMPATIBILITY_CHECK,
    INTENT_CONTINUITY_ANALYSIS,
    INTENT_DEPENDENCY_ANALYSIS,
    INTENT_EXPLAINABILITY_STABLE,
    INTENT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_HASH_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    INTENT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    INTENT_INTEGRITY_STABLE,
    INTENT_PROHIBITED,
    INTENT_SUPPORTED,
    INTENT_UNSUPPORTED,
    OrchestrationIntentClassificationInput,
    OrchestrationIntentIntegrityInput,
    OrchestrationIntentIntegrityResult,
    OrchestrationIntentIntegritySummary,
    OrchestrationIntentRecord,
    OrchestrationIntentRegistry,
    export_intent_integrity_result,
    hash_intent_integrity_result,
    hash_intent_record,
    hash_intent_registry,
    serialize_intent_integrity_result,
    serialize_intent_registry,
)
from .orchestration_intent_registry import default_orchestration_intent_registry


def default_orchestration_intent_integrity_input() -> OrchestrationIntentIntegrityInput:
    registry = default_orchestration_intent_registry()
    classification = classify_orchestration_intents(
        OrchestrationIntentClassificationInput(intent_registry=registry)
    )
    explainability = explain_orchestration_intents(registry, classification)
    return OrchestrationIntentIntegrityInput(
        intent_registry=registry,
        classification_result=classification,
        explainability_result=explainability,
    )


def audit_orchestration_intent_integrity(
    integrity_input: OrchestrationIntentIntegrityInput | None = None,
) -> OrchestrationIntentIntegrityResult:
    source = integrity_input or default_orchestration_intent_integrity_input()
    registry_hash = hash_intent_registry(source.intent_registry)
    registry = _registry_integrity(source, registry_hash)
    intent_hash = _intent_hash_integrity(source.intent_registry)
    provenance = _provenance_integrity(source.intent_registry)
    explainability = _explainability_integrity(source)
    governance = _governance_integrity(source.intent_registry)
    compatibility = _compatibility_integrity(source.intent_registry)
    dependency = _dependency_integrity(source.intent_registry)
    blocker = _blocker_integrity(source.intent_registry)
    supported_domain = _supported_domain_integrity(source.intent_registry)
    serialization = _serialization_integrity(source.intent_registry)
    failures = _failure_summary(
        registry,
        intent_hash,
        provenance,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
        serialization,
    )
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _integrity_status(
        registry,
        intent_hash,
        provenance,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
    )
    result = OrchestrationIntentIntegrityResult(
        registry_id=source.intent_registry.registry_id,
        intent_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        intent_hash_integrity=intent_hash,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        governance_integrity=governance,
        compatibility_integrity=compatibility,
        dependency_integrity=dependency,
        blocker_integrity=blocker,
        supported_domain_integrity=supported_domain,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_intent_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_intent_integrity_hash=hash_intent_integrity_result(result))


def export_orchestration_intent_integrity_result(
    result: OrchestrationIntentIntegrityResult,
) -> dict[str, object]:
    return export_intent_integrity_result(result)


def serialize_orchestration_intent_integrity_result(
    result: OrchestrationIntentIntegrityResult,
) -> str:
    return serialize_intent_integrity_result(result)


def hash_orchestration_intent_integrity_result(
    result: OrchestrationIntentIntegrityResult,
) -> str:
    return hash_intent_integrity_result(result)


def _registry_integrity(
    source: OrchestrationIntentIntegrityInput,
    registry_hash: str,
) -> OrchestrationIntentIntegritySummary:
    failures: list[str] = []
    if not source.intent_registry.records:
        failures.append("intent_registry_has_no_records")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("intent_registry_hash_mismatch")
    if not source.intent_registry.planning_only or not source.intent_registry.non_production:
        failures.append("intent_registry_boundary_not_planning_only_non_production")
    return OrchestrationIntentIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _intent_hash_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(f"{record.identifier.intent_id}:{hash_intent_record(record)}" for record in registry.records))
    ids = [record.identifier.intent_id for record in registry.records]
    duplicates = sorted({intent_id for intent_id in ids if ids.count(intent_id) > 1})
    failures = tuple(f"duplicate_intent_id:{intent_id}" for intent_id in duplicates)
    return OrchestrationIntentIntegritySummary("intent_hash", references, failures)


def _provenance_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        provenance = record.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.upstream_policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.resolution_record_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{record.identifier.intent_id}:source_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{record.identifier.intent_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{record.identifier.intent_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{record.identifier.intent_id}:governance_provenance_gap")
    return OrchestrationIntentIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _explainability_integrity(source: OrchestrationIntentIntegrityInput) -> OrchestrationIntentIntegritySummary:
    references = (
        source.classification_result.deterministic_intent_classification_hash,
        source.explainability_result.deterministic_intent_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.intent_explainability_status != INTENT_EXPLAINABILITY_STABLE:
        failures.append(f"intent_explainability_status:{source.explainability_result.intent_explainability_status}")
    if source.expected_classification_hash is not None and source.expected_classification_hash != source.classification_result.deterministic_intent_classification_hash:
        failures.append("intent_classification_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_intent_explainability_hash:
        failures.append("intent_explainability_hash_mismatch")
    return OrchestrationIntentIntegritySummary("explainability", references, tuple(sorted(failures)))


def _governance_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(record.identifier.intent_id for record in registry.records))
    failures: list[str] = []
    for record in registry.records:
        if not record.governance_boundaries:
            failures.append(f"{record.identifier.intent_id}:missing_governance_boundary_visibility")
        if _governance_gap(record):
            failures.append(f"{record.identifier.intent_id}:governance_boundary_gap")
    return OrchestrationIntentIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(record.identifier.intent_id for record in registry.records if record.compatibility_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.intent_type == INTENT_COMPATIBILITY_CHECK and not record.compatibility_domains:
            failures.append(f"{record.identifier.intent_id}:missing_compatibility_domain_visibility")
        if record.support_state in (INTENT_UNSUPPORTED, INTENT_PROHIBITED) and not record.compatibility_domains:
            failures.append(f"{record.identifier.intent_id}:missing_blocked_compatibility_domain_visibility")
    return OrchestrationIntentIntegritySummary("compatibility", references, tuple(sorted(failures)))


def _dependency_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(record.identifier.intent_id for record in registry.records if record.dependency_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.intent_type in (INTENT_DEPENDENCY_ANALYSIS, INTENT_CONTINUITY_ANALYSIS) and not record.dependency_domains:
            failures.append(f"{record.identifier.intent_id}:missing_dependency_domain_visibility")
    return OrchestrationIntentIntegritySummary("dependency", references, tuple(sorted(failures)))


def _blocker_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(record.identifier.intent_id for record in registry.records if record.blocker_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.support_state in (INTENT_UNSUPPORTED, INTENT_PROHIBITED) and not record.blocker_domains:
            failures.append(f"{record.identifier.intent_id}:missing_blocker_domain_visibility")
    return OrchestrationIntentIntegritySummary("blocker", references, tuple(sorted(failures)))


def _supported_domain_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    references = tuple(sorted(record.identifier.intent_id for record in registry.records if record.supported_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.intent_id}:missing_supported_domain_visibility"
            for record in registry.records
            if record.support_state == INTENT_SUPPORTED and not record.supported_domains
        )
    )
    return OrchestrationIntentIntegritySummary("supported_domain", references, failures)


def _serialization_integrity(registry: OrchestrationIntentRegistry) -> OrchestrationIntentIntegritySummary:
    first = serialize_intent_registry(registry)
    second = serialize_intent_registry(registry)
    failures = () if first == second else ("intent_registry_serialization_not_stable",)
    return OrchestrationIntentIntegritySummary("deterministic_serialization", (hash_intent_registry(registry),), failures)


def _governance_gap(record: OrchestrationIntentRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "intent_modeling_only")
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
        )
    )


def _failure_summary(*summaries: OrchestrationIntentIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationIntentIntegritySummary,
    intent_hash: OrchestrationIntentIntegritySummary,
    provenance: OrchestrationIntentIntegritySummary,
    explainability: OrchestrationIntentIntegritySummary,
    governance: OrchestrationIntentIntegritySummary,
    compatibility: OrchestrationIntentIntegritySummary,
    dependency: OrchestrationIntentIntegritySummary,
    blocker: OrchestrationIntentIntegritySummary,
    supported_domain: OrchestrationIntentIntegritySummary,
) -> str:
    if registry.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_HASH_GAP if "intent_registry_hash_mismatch" in registry.failures else INTENT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if intent_hash.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if explainability.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else INTENT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if governance.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    if dependency.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if blocker.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if supported_domain.failures:
        return INTENT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    return INTENT_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == INTENT_INTEGRITY_STABLE:
        return (
            "Intent integrity is stable; registry, hashes, provenance, explainability, governance, compatibility, "
            "dependency, blocker, supported-domain, and serialization continuity remain deterministic and non-executing."
        )
    return f"Intent integrity classified as {status}; failures: {', '.join(failures)}."
