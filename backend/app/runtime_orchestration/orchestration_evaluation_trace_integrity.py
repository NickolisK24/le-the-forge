"""Deterministic orchestration evaluation trace integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_trace_builder import build_orchestration_evaluation_trace
from .orchestration_evaluation_trace_explainability import explain_orchestration_evaluation_trace
from .orchestration_evaluation_trace_models import (
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_DEPENDENCY_BLOCKED,
    TRACE_EXPLAINABILITY_STABLE,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    TRACE_INTEGRITY_STABLE,
    TRACE_PROHIBITED,
    TRACE_STATES,
    TRACE_STEP_TYPES,
    TRACE_SUPPORTED,
    TRACE_UNSUPPORTED,
    OrchestrationEvaluationTraceBuildInput,
    OrchestrationEvaluationTraceIntegrityInput,
    OrchestrationEvaluationTraceIntegrityResult,
    OrchestrationEvaluationTraceIntegritySummary,
    OrchestrationEvaluationTraceRecord,
    OrchestrationEvaluationTraceRegistry,
    export_trace_integrity_result,
    hash_trace_integrity_result,
    hash_trace_record,
    hash_trace_registry,
    serialize_trace_integrity_result,
    serialize_trace_registry,
)
from .orchestration_evaluation_trace_registry import default_orchestration_evaluation_trace_registry


def default_orchestration_evaluation_trace_integrity_input() -> OrchestrationEvaluationTraceIntegrityInput:
    registry = default_orchestration_evaluation_trace_registry()
    build = build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=registry)
    )
    explainability = explain_orchestration_evaluation_trace(registry, build)
    return OrchestrationEvaluationTraceIntegrityInput(
        trace_registry=registry,
        build_result=build,
        explainability_result=explainability,
    )


def audit_orchestration_evaluation_trace_integrity(
    integrity_input: OrchestrationEvaluationTraceIntegrityInput | None = None,
) -> OrchestrationEvaluationTraceIntegrityResult:
    source = integrity_input or default_orchestration_evaluation_trace_integrity_input()
    registry_hash = hash_trace_registry(source.trace_registry)
    registry = _registry_integrity(source, registry_hash)
    trace_hash = _trace_hash_integrity(source.trace_registry)
    provenance = _provenance_integrity(source.trace_registry)
    trace_step = _trace_step_integrity(source.trace_registry)
    policy = _policy_integrity(source.trace_registry)
    explainability = _explainability_integrity(source)
    governance = _governance_integrity(source.trace_registry)
    compatibility = _compatibility_integrity(source.trace_registry)
    dependency = _dependency_integrity(source.trace_registry)
    blocker = _blocker_integrity(source.trace_registry)
    supported_domain = _supported_domain_integrity(source.trace_registry)
    serialization = _serialization_integrity(source.trace_registry)
    failures = _failure_summary(
        registry,
        trace_hash,
        provenance,
        trace_step,
        policy,
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
        trace_hash,
        provenance,
        trace_step,
        policy,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
    )
    result = OrchestrationEvaluationTraceIntegrityResult(
        registry_id=source.trace_registry.registry_id,
        trace_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        trace_hash_integrity=trace_hash,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        governance_integrity=governance,
        compatibility_integrity=compatibility,
        dependency_integrity=dependency,
        blocker_integrity=blocker,
        supported_domain_integrity=supported_domain,
        trace_step_integrity=trace_step,
        policy_integrity=policy,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_trace_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_trace_integrity_hash=hash_trace_integrity_result(result))


def export_orchestration_evaluation_trace_integrity_result(
    result: OrchestrationEvaluationTraceIntegrityResult,
) -> dict[str, object]:
    return export_trace_integrity_result(result)


def serialize_orchestration_evaluation_trace_integrity_result(
    result: OrchestrationEvaluationTraceIntegrityResult,
) -> str:
    return serialize_trace_integrity_result(result)


def hash_orchestration_evaluation_trace_integrity_result(
    result: OrchestrationEvaluationTraceIntegrityResult,
) -> str:
    return hash_trace_integrity_result(result)


def _registry_integrity(
    source: OrchestrationEvaluationTraceIntegrityInput,
    registry_hash: str,
) -> OrchestrationEvaluationTraceIntegritySummary:
    failures: list[str] = []
    if not source.trace_registry.records:
        failures.append("trace_registry_has_no_records")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("trace_registry_hash_mismatch")
    if not source.trace_registry.planning_only or not source.trace_registry.non_production:
        failures.append("trace_registry_boundary_not_planning_only_non_production")
    return OrchestrationEvaluationTraceIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _trace_hash_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(f"{record.identifier.trace_id}:{hash_trace_record(record)}" for record in registry.records))
    ids = [record.identifier.trace_id for record in registry.records]
    duplicates = sorted({trace_id for trace_id in ids if ids.count(trace_id) > 1})
    failures = tuple(f"duplicate_trace_id:{trace_id}" for trace_id in duplicates)
    failures += tuple(
        sorted(
            f"{record.identifier.trace_id}:unrecognized_trace_state"
            for record in registry.records
            if record.trace_state not in TRACE_STATES
        )
    )
    return OrchestrationEvaluationTraceIntegritySummary("trace_hash", references, failures)


def _provenance_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        provenance = record.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                provenance.preflight_id,
                provenance.intent_id,
                *provenance.policy_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{record.identifier.trace_id}:source_provenance_gap")
        if not provenance.preflight_id:
            failures.append(f"{record.identifier.trace_id}:preflight_provenance_gap")
        if not provenance.intent_id:
            failures.append(f"{record.identifier.trace_id}:intent_provenance_gap")
        if not provenance.policy_ids:
            failures.append(f"{record.identifier.trace_id}:policy_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{record.identifier.trace_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{record.identifier.trace_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{record.identifier.trace_id}:governance_provenance_gap")
    return OrchestrationEvaluationTraceIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _trace_step_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        references.extend(step.step_id for step in record.trace_steps)
        if not record.trace_steps:
            failures.append(f"{record.identifier.trace_id}:missing_trace_step_visibility")
        if not record.reasoning_chain:
            failures.append(f"{record.identifier.trace_id}:missing_reasoning_chain_visibility")
        sequence_ids = [step.sequence_id for step in record.trace_steps]
        duplicates = sorted({sequence_id for sequence_id in sequence_ids if sequence_ids.count(sequence_id) > 1})
        failures.extend(f"{record.identifier.trace_id}:duplicate_trace_step_sequence:{sequence_id}" for sequence_id in duplicates)
        failures.extend(
            sorted(
                f"{record.identifier.trace_id}:unrecognized_trace_step_type:{step.step_type}"
                for step in record.trace_steps
                if step.step_type not in TRACE_STEP_TYPES
            )
        )
    return OrchestrationEvaluationTraceIntegritySummary("trace_step", tuple(sorted(set(references))), tuple(sorted(failures)))


def _policy_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted({policy_id for record in registry.records for policy_id in record.policy_ids}))
    failures = tuple(
        sorted(
            f"{record.identifier.trace_id}:missing_policy_reference_visibility"
            for record in registry.records
            if not record.policy_ids
        )
    )
    return OrchestrationEvaluationTraceIntegritySummary("policy", references, failures)


def _explainability_integrity(source: OrchestrationEvaluationTraceIntegrityInput) -> OrchestrationEvaluationTraceIntegritySummary:
    references = (
        source.build_result.deterministic_trace_build_hash,
        source.explainability_result.deterministic_trace_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.trace_explainability_status != TRACE_EXPLAINABILITY_STABLE:
        failures.append(f"trace_explainability_status:{source.explainability_result.trace_explainability_status}")
    if source.expected_build_hash is not None and source.expected_build_hash != source.build_result.deterministic_trace_build_hash:
        failures.append("trace_build_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_trace_explainability_hash:
        failures.append("trace_explainability_hash_mismatch")
    return OrchestrationEvaluationTraceIntegritySummary("explainability", references, tuple(sorted(failures)))


def _governance_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(record.identifier.trace_id for record in registry.records))
    failures: list[str] = []
    for record in registry.records:
        if not record.governance_boundaries:
            failures.append(f"{record.identifier.trace_id}:missing_governance_boundary_visibility")
        if record.trace_state == TRACE_GOVERNANCE_BLOCKED and not record.governance_boundaries:
            failures.append(f"{record.identifier.trace_id}:missing_governance_blocker_visibility")
        if _governance_gap(record):
            failures.append(f"{record.identifier.trace_id}:governance_boundary_gap")
    return OrchestrationEvaluationTraceIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(record.identifier.trace_id for record in registry.records if record.compatibility_domains))
    failures: list[str] = []
    for record in registry.records:
        if record.trace_state == TRACE_COMPATIBILITY_BLOCKED and not record.compatibility_domains:
            failures.append(f"{record.identifier.trace_id}:missing_compatibility_domain_visibility")
        if record.trace_state in (TRACE_UNSUPPORTED, TRACE_PROHIBITED) and not record.compatibility_domains:
            failures.append(f"{record.identifier.trace_id}:missing_blocked_compatibility_domain_visibility")
    return OrchestrationEvaluationTraceIntegritySummary("compatibility", references, tuple(sorted(failures)))


def _dependency_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(record.identifier.trace_id for record in registry.records if record.dependency_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.trace_id}:missing_dependency_domain_visibility"
            for record in registry.records
            if record.trace_state == TRACE_DEPENDENCY_BLOCKED and not record.dependency_domains
        )
    )
    return OrchestrationEvaluationTraceIntegritySummary("dependency", references, failures)


def _blocker_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(record.identifier.trace_id for record in registry.records if record.blocker_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.trace_id}:missing_blocker_domain_visibility"
            for record in registry.records
            if record.trace_state != TRACE_SUPPORTED and not record.blocker_domains
        )
    )
    return OrchestrationEvaluationTraceIntegritySummary("blocker", references, failures)


def _supported_domain_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    references = tuple(sorted(record.identifier.trace_id for record in registry.records if record.supported_domains))
    failures = tuple(
        sorted(
            f"{record.identifier.trace_id}:missing_supported_domain_visibility"
            for record in registry.records
            if record.trace_state == TRACE_SUPPORTED and not record.supported_domains
        )
    )
    return OrchestrationEvaluationTraceIntegritySummary("supported_domain", references, failures)


def _serialization_integrity(registry: OrchestrationEvaluationTraceRegistry) -> OrchestrationEvaluationTraceIntegritySummary:
    first = serialize_trace_registry(registry)
    second = serialize_trace_registry(registry)
    failures = () if first == second else ("trace_registry_serialization_not_stable",)
    return OrchestrationEvaluationTraceIntegritySummary("deterministic_serialization", (hash_trace_registry(registry),), failures)


def _governance_gap(record: OrchestrationEvaluationTraceRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "evaluation_trace_modeling_only")
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
            record.trace_execution_enabled,
        )
    )


def _failure_summary(*summaries: OrchestrationEvaluationTraceIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationEvaluationTraceIntegritySummary,
    trace_hash: OrchestrationEvaluationTraceIntegritySummary,
    provenance: OrchestrationEvaluationTraceIntegritySummary,
    trace_step: OrchestrationEvaluationTraceIntegritySummary,
    policy: OrchestrationEvaluationTraceIntegritySummary,
    explainability: OrchestrationEvaluationTraceIntegritySummary,
    governance: OrchestrationEvaluationTraceIntegritySummary,
    compatibility: OrchestrationEvaluationTraceIntegritySummary,
    dependency: OrchestrationEvaluationTraceIntegritySummary,
    blocker: OrchestrationEvaluationTraceIntegritySummary,
    supported_domain: OrchestrationEvaluationTraceIntegritySummary,
) -> str:
    if registry.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP if "trace_registry_hash_mismatch" in registry.failures else TRACE_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if trace_hash.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if trace_step.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP
    if policy.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_POLICY_GAP
    if explainability.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else TRACE_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if governance.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    if dependency.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if blocker.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if supported_domain.failures:
        return TRACE_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    return TRACE_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == TRACE_INTEGRITY_STABLE:
        return (
            "Evaluation trace integrity is stable; registry, hashes, provenance, trace steps, policy references, "
            "explainability, governance, compatibility, dependency, blocker, supported-domain, and serialization "
            "continuity remain deterministic and non-executing."
        )
    return f"Evaluation trace integrity classified as {status}; failures: {', '.join(failures)}."
