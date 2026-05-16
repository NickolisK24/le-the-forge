"""Deterministic orchestration intent-policy mapping integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_policy_explainability import explain_orchestration_intent_policy_mappings
from .orchestration_intent_policy_mapper import map_orchestration_intent_policies
from .orchestration_intent_policy_mapping_models import (
    MAPPING_EXPLAINABILITY_STABLE,
    MAPPING_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    MAPPING_INTEGRITY_STABLE,
    MAPPING_PROHIBITED,
    MAPPING_SUPPORTED,
    MAPPING_UNSUPPORTED,
    OrchestrationIntentPolicyMappingInput,
    OrchestrationIntentPolicyMappingIntegrityInput,
    OrchestrationIntentPolicyMappingIntegrityResult,
    OrchestrationIntentPolicyMappingIntegritySummary,
    OrchestrationIntentPolicyMappingRecord,
    OrchestrationIntentPolicyMappingRegistry,
    export_mapping_integrity_result,
    hash_mapping_integrity_result,
    hash_mapping_record,
    hash_mapping_registry,
    serialize_mapping_integrity_result,
    serialize_mapping_registry,
)
from .orchestration_intent_policy_mapping_registry import default_orchestration_intent_policy_mapping_registry


def default_orchestration_intent_policy_mapping_integrity_input() -> OrchestrationIntentPolicyMappingIntegrityInput:
    registry = default_orchestration_intent_policy_mapping_registry()
    mapping = map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=registry)
    )
    explainability = explain_orchestration_intent_policy_mappings(registry, mapping)
    return OrchestrationIntentPolicyMappingIntegrityInput(
        mapping_registry=registry,
        mapping_result=mapping,
        explainability_result=explainability,
    )


def audit_orchestration_intent_policy_mapping_integrity(
    integrity_input: OrchestrationIntentPolicyMappingIntegrityInput | None = None,
) -> OrchestrationIntentPolicyMappingIntegrityResult:
    source = integrity_input or default_orchestration_intent_policy_mapping_integrity_input()
    registry_hash = hash_mapping_registry(source.mapping_registry)
    registry = _registry_integrity(source, registry_hash)
    mapping_hash = _mapping_hash_integrity(source.mapping_registry)
    provenance = _provenance_integrity(source.mapping_registry)
    explainability = _explainability_integrity(source)
    governance = _governance_integrity(source.mapping_registry)
    compatibility = _compatibility_integrity(source.mapping_registry)
    dependency = _dependency_integrity(source.mapping_registry)
    blocker = _blocker_integrity(source.mapping_registry)
    supported_domain = _supported_domain_integrity(source.mapping_registry)
    policy = _policy_integrity(source.mapping_registry)
    serialization = _serialization_integrity(source.mapping_registry)
    failures = _failure_summary(
        registry,
        mapping_hash,
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
        mapping_hash,
        provenance,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
        policy,
    )
    result = OrchestrationIntentPolicyMappingIntegrityResult(
        registry_id=source.mapping_registry.registry_id,
        mapping_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        mapping_hash_integrity=mapping_hash,
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
        deterministic_mapping_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_mapping_integrity_hash=hash_mapping_integrity_result(result))


def export_orchestration_intent_policy_mapping_integrity_result(
    result: OrchestrationIntentPolicyMappingIntegrityResult,
) -> dict[str, object]:
    return export_mapping_integrity_result(result)


def serialize_orchestration_intent_policy_mapping_integrity_result(
    result: OrchestrationIntentPolicyMappingIntegrityResult,
) -> str:
    return serialize_mapping_integrity_result(result)


def hash_orchestration_intent_policy_mapping_integrity_result(
    result: OrchestrationIntentPolicyMappingIntegrityResult,
) -> str:
    return hash_mapping_integrity_result(result)


def _registry_integrity(
    source: OrchestrationIntentPolicyMappingIntegrityInput,
    registry_hash: str,
) -> OrchestrationIntentPolicyMappingIntegritySummary:
    failures: list[str] = []
    if not source.mapping_registry.records:
        failures.append("mapping_registry_has_no_records")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("mapping_registry_hash_mismatch")
    if not source.mapping_registry.planning_only or not source.mapping_registry.non_production:
        failures.append("mapping_registry_boundary_not_planning_only_non_production")
    return OrchestrationIntentPolicyMappingIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _mapping_hash_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(f"{record.identifier.mapping_id}:{hash_mapping_record(record)}" for record in registry.records))
    ids = [record.identifier.mapping_id for record in registry.records]
    duplicates = sorted({mapping_id for mapping_id in ids if ids.count(mapping_id) > 1})
    failures = tuple(f"duplicate_mapping_id:{mapping_id}" for mapping_id in duplicates)
    return OrchestrationIntentPolicyMappingIntegritySummary("mapping_hash", references, failures)


def _provenance_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        provenance = record.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                provenance.intent_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{record.identifier.mapping_id}:source_provenance_gap")
        if not provenance.intent_id:
            failures.append(f"{record.identifier.mapping_id}:intent_provenance_gap")
        if not provenance.policy_ids:
            failures.append(f"{record.identifier.mapping_id}:policy_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{record.identifier.mapping_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{record.identifier.mapping_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{record.identifier.mapping_id}:governance_provenance_gap")
    return OrchestrationIntentPolicyMappingIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _explainability_integrity(source: OrchestrationIntentPolicyMappingIntegrityInput) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = (
        source.mapping_result.deterministic_mapping_analysis_hash,
        source.explainability_result.deterministic_mapping_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.mapping_explainability_status != MAPPING_EXPLAINABILITY_STABLE:
        failures.append(f"mapping_explainability_status:{source.explainability_result.mapping_explainability_status}")
    if source.expected_mapping_analysis_hash is not None and source.expected_mapping_analysis_hash != source.mapping_result.deterministic_mapping_analysis_hash:
        failures.append("mapping_analysis_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_mapping_explainability_hash:
        failures.append("mapping_explainability_hash_mismatch")
    return OrchestrationIntentPolicyMappingIntegritySummary("explainability", references, tuple(sorted(failures)))


def _governance_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(record.identifier.mapping_id for record in registry.records))
    failures: list[str] = []
    for record in registry.records:
        if not record.governance_boundaries:
            failures.append(f"{record.identifier.mapping_id}:missing_governance_boundary_visibility")
        if _governance_gap(record):
            failures.append(f"{record.identifier.mapping_id}:governance_boundary_gap")
    return OrchestrationIntentPolicyMappingIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(record.identifier.mapping_id for record in registry.records if record.compatibility_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.identifier.intent_id == "v3_6.intent.compatibility-check" and not record.compatibility_domains:
            failures.append(f"{record.identifier.mapping_id}:missing_compatibility_domain_visibility")
        if record.mapping_state in (MAPPING_UNSUPPORTED, MAPPING_PROHIBITED) and not record.compatibility_domains:
            failures.append(f"{record.identifier.mapping_id}:missing_blocked_compatibility_domain_visibility")
    return OrchestrationIntentPolicyMappingIntegritySummary("compatibility", references, tuple(sorted(failures)))


def _dependency_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(record.identifier.mapping_id for record in registry.records if record.dependency_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.identifier.intent_id in ("v3_6.intent.dependency-analysis", "v3_6.intent.continuity-analysis") and not record.dependency_domains:
            failures.append(f"{record.identifier.mapping_id}:missing_dependency_domain_visibility")
    return OrchestrationIntentPolicyMappingIntegritySummary("dependency", references, tuple(sorted(failures)))


def _blocker_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(record.identifier.mapping_id for record in registry.records if record.blocker_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.mapping_state in (MAPPING_UNSUPPORTED, MAPPING_PROHIBITED) and not record.blocker_domains:
            failures.append(f"{record.identifier.mapping_id}:missing_blocker_domain_visibility")
    return OrchestrationIntentPolicyMappingIntegritySummary("blocker", references, tuple(sorted(failures)))


def _supported_domain_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted(record.identifier.mapping_id for record in registry.records if record.supported_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.mapping_id}:missing_supported_domain_visibility"
            for record in registry.records
            if record.mapping_state == MAPPING_SUPPORTED and not record.supported_domains
        )
    )
    return OrchestrationIntentPolicyMappingIntegritySummary("supported_domain", references, failures)


def _policy_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    references = tuple(sorted({policy_id for record in registry.records for policy_id in record.policy_ids}))
    failures = tuple(
        sorted(
            f"{record.identifier.mapping_id}:missing_policy_applicability"
            for record in registry.records
            if not record.policy_ids
        )
    )
    return OrchestrationIntentPolicyMappingIntegritySummary("policy", references, failures)


def _serialization_integrity(registry: OrchestrationIntentPolicyMappingRegistry) -> OrchestrationIntentPolicyMappingIntegritySummary:
    first = serialize_mapping_registry(registry)
    second = serialize_mapping_registry(registry)
    failures = () if first == second else ("mapping_registry_serialization_not_stable",)
    return OrchestrationIntentPolicyMappingIntegritySummary("deterministic_serialization", (hash_mapping_registry(registry),), failures)


def _governance_gap(record: OrchestrationIntentPolicyMappingRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "intent_policy_mapping_only")
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
            record.mapping_execution_enabled,
        )
    )


def _failure_summary(*summaries: OrchestrationIntentPolicyMappingIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationIntentPolicyMappingIntegritySummary,
    mapping_hash: OrchestrationIntentPolicyMappingIntegritySummary,
    provenance: OrchestrationIntentPolicyMappingIntegritySummary,
    explainability: OrchestrationIntentPolicyMappingIntegritySummary,
    governance: OrchestrationIntentPolicyMappingIntegritySummary,
    compatibility: OrchestrationIntentPolicyMappingIntegritySummary,
    dependency: OrchestrationIntentPolicyMappingIntegritySummary,
    blocker: OrchestrationIntentPolicyMappingIntegritySummary,
    supported_domain: OrchestrationIntentPolicyMappingIntegritySummary,
    policy: OrchestrationIntentPolicyMappingIntegritySummary,
) -> str:
    if registry.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP if "mapping_registry_hash_mismatch" in registry.failures else MAPPING_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if mapping_hash.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if policy.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_POLICY_GAP
    if explainability.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else MAPPING_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if governance.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    if dependency.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if blocker.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if supported_domain.failures:
        return MAPPING_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    return MAPPING_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == MAPPING_INTEGRITY_STABLE:
        return (
            "Intent-policy mapping integrity is stable; registry, hashes, provenance, explainability, governance, "
            "compatibility, dependency, blocker, supported-domain, policy, and serialization continuity remain deterministic and non-executing."
        )
    return f"Intent-policy mapping integrity classified as {status}; failures: {', '.join(failures)}."
