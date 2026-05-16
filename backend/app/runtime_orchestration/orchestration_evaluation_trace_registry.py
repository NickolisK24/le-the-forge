"""Deterministic orchestration evaluation trace registry for v3.6 Phase 7."""

from __future__ import annotations

from typing import Iterable

from .orchestration_preflight_models import (
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    OrchestrationPreflightRecord,
)
from .orchestration_preflight_registry import default_orchestration_preflight_registry
from .orchestration_evaluation_trace_models import (
    TRACE_CLASSIFICATION_BLOCKER,
    TRACE_CLASSIFICATION_COMPATIBILITY,
    TRACE_CLASSIFICATION_DEPENDENCY,
    TRACE_CLASSIFICATION_EXPLAINABILITY,
    TRACE_CLASSIFICATION_GOVERNANCE,
    TRACE_CLASSIFICATION_INTEGRITY,
    TRACE_CLASSIFICATION_PROHIBITED,
    TRACE_CLASSIFICATION_PROVENANCE,
    TRACE_CLASSIFICATION_UNSUPPORTED,
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_DEPENDENCY_BLOCKED,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_PROHIBITED,
    TRACE_STEP_BLOCKER,
    TRACE_STEP_COMPATIBILITY,
    TRACE_STEP_DEPENDENCY,
    TRACE_STEP_EXPLAINABILITY,
    TRACE_STEP_GOVERNANCE,
    TRACE_STEP_INTEGRITY,
    TRACE_STEP_PROHIBITED_DOMAIN,
    TRACE_STEP_PROVENANCE,
    TRACE_STEP_SUPPORTABILITY,
    TRACE_STEP_UNSUPPORTED_DOMAIN,
    TRACE_SUPPORTED,
    TRACE_UNSUPPORTED,
    OrchestrationEvaluationTraceIdentifier,
    OrchestrationEvaluationTraceProvenance,
    OrchestrationEvaluationTraceRecord,
    OrchestrationEvaluationTraceRegistry,
    OrchestrationEvaluationTraceStep,
    export_trace_registry,
    hash_trace_registry,
    serialize_trace_registry,
)


DEFAULT_TRACE_REGISTRY_ID = "v3_6_orchestration_evaluation_trace_registry"
DEFAULT_TRACE_SCHEMA_VERSION = "v3_6.orchestration_evaluation_trace_registry.1"


def default_orchestration_evaluation_trace_registry() -> OrchestrationEvaluationTraceRegistry:
    return build_orchestration_evaluation_trace_registry(default_orchestration_evaluation_trace_records())


def build_orchestration_evaluation_trace_registry(
    records: Iterable[OrchestrationEvaluationTraceRecord],
    registry_id: str = DEFAULT_TRACE_REGISTRY_ID,
) -> OrchestrationEvaluationTraceRegistry:
    ordered = tuple(sorted(records, key=lambda item: item.identifier.trace_id))
    trace_ids = [record.identifier.trace_id for record in ordered]
    if len(trace_ids) != len(set(trace_ids)):
        duplicates = sorted({trace_id for trace_id in trace_ids if trace_ids.count(trace_id) > 1})
        raise ValueError(f"Duplicate orchestration evaluation trace ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationEvaluationTraceRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_TRACE_SCHEMA_VERSION,
        records=ordered,
        registry_metadata={
            "phase": "v3.6.phase_7",
            "purpose": "deterministic_orchestration_evaluation_trace_modeling",
            "planning_only": True,
            "non_production": True,
            "evaluation_trace_modeling_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "recommendation_behavior_enabled": False,
            "optimization_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_evaluation_trace_records() -> tuple[OrchestrationEvaluationTraceRecord, ...]:
    preflight_registry = default_orchestration_preflight_registry()
    return tuple(_trace_record(preflight) for preflight in preflight_registry.records)


def registered_trace_ids(registry: OrchestrationEvaluationTraceRegistry) -> tuple[str, ...]:
    return tuple(sorted(record.identifier.trace_id for record in registry.records))


def get_registered_trace_record(
    registry: OrchestrationEvaluationTraceRegistry,
    trace_id: str,
) -> OrchestrationEvaluationTraceRecord | None:
    for record in registry.records:
        if record.identifier.trace_id == trace_id:
            return record
    return None


def get_registered_trace_record_for_preflight(
    registry: OrchestrationEvaluationTraceRegistry,
    preflight_id: str,
) -> OrchestrationEvaluationTraceRecord | None:
    for record in registry.records:
        if record.identifier.preflight_id == preflight_id:
            return record
    return None


def export_default_orchestration_evaluation_trace_registry() -> dict[str, object]:
    return export_trace_registry(default_orchestration_evaluation_trace_registry())


def serialize_default_orchestration_evaluation_trace_registry() -> str:
    return serialize_trace_registry(default_orchestration_evaluation_trace_registry())


def hash_default_orchestration_evaluation_trace_registry() -> str:
    return hash_trace_registry(default_orchestration_evaluation_trace_registry())


def _trace_record(preflight: OrchestrationPreflightRecord) -> OrchestrationEvaluationTraceRecord:
    trace_id = preflight.identifier.preflight_id.replace("v3_6.preflight.", "v3_6.trace.")
    trace_state = _trace_state(preflight.preflight_state)
    steps = _trace_steps(trace_id, preflight)
    reasoning_chain = tuple(
        f"{step.sequence_id:02d}:{step.description}"
        for step in sorted(steps, key=lambda item: (item.sequence_id, item.step_id))
    )
    return OrchestrationEvaluationTraceRecord(
        identifier=OrchestrationEvaluationTraceIdentifier(
            trace_id=trace_id,
            preflight_id=preflight.identifier.preflight_id,
            intent_id=preflight.identifier.intent_id,
            namespace="v3_6.orchestration_evaluation_trace",
            version="1",
        ),
        trace_state=trace_state,
        preflight_state=preflight.preflight_state,
        trace_classifications=_trace_classifications(preflight),
        trace_steps=steps,
        reasoning_chain=reasoning_chain,
        policy_ids=preflight.policy_ids,
        governance_boundaries=preflight.governance_boundaries,
        compatibility_domains=preflight.compatibility_domains,
        dependency_domains=preflight.dependency_domains,
        blocker_domains=preflight.blocker_domains,
        unsupported_domains=preflight.unsupported_domains,
        prohibited_domains=preflight.prohibited_domains,
        supported_domains=preflight.supported_domains,
        provenance=OrchestrationEvaluationTraceProvenance(
            source_phase="v3.6_phase_7_deterministic_orchestration_evaluation_trace_modeling",
            source_artifact="backend/app/runtime_orchestration/orchestration_evaluation_trace_registry.py",
            preflight_id=preflight.identifier.preflight_id,
            intent_id=preflight.identifier.intent_id,
            policy_ids=preflight.policy_ids,
            replay_reference_ids=(f"{trace_id}.replay",),
            rollback_reference_ids=(f"{trace_id}.rollback",),
            governance_reference_ids=(
                "v3_6_preflight_integrity_stable",
                "v3_6_trace_governance_first",
                "v3_6_trace_planning_only",
            ),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "evaluation_trace_modeling_only": True,
            "execution_enabled": False,
            "routing_enabled": False,
            "mutation_enabled": False,
            "recommendation_enabled": False,
            "optimization_enabled": False,
            "autonomy_enabled": False,
            "production_runtime_reads_enabled": False,
            "production_runtime_writes_enabled": False,
            "persistent_writes_enabled": False,
        },
        explainability_reference_ids=(f"{trace_id}.explainability",),
        integrity_reference_ids=(f"{trace_id}.integrity",),
    )


def _trace_state(preflight_state: str) -> str:
    if preflight_state == PREFLIGHT_SUPPORTED:
        return TRACE_SUPPORTED
    if preflight_state == PREFLIGHT_UNSUPPORTED:
        return TRACE_UNSUPPORTED
    if preflight_state == PREFLIGHT_PROHIBITED:
        return TRACE_PROHIBITED
    if preflight_state == PREFLIGHT_GOVERNANCE_BLOCKED:
        return TRACE_GOVERNANCE_BLOCKED
    if preflight_state == PREFLIGHT_COMPATIBILITY_BLOCKED:
        return TRACE_COMPATIBILITY_BLOCKED
    if preflight_state == PREFLIGHT_DEPENDENCY_BLOCKED:
        return TRACE_DEPENDENCY_BLOCKED
    return TRACE_UNSUPPORTED


def _trace_classifications(preflight: OrchestrationPreflightRecord) -> tuple[str, ...]:
    classifications = {
        TRACE_CLASSIFICATION_GOVERNANCE,
        TRACE_CLASSIFICATION_PROVENANCE,
        TRACE_CLASSIFICATION_EXPLAINABILITY,
        TRACE_CLASSIFICATION_INTEGRITY,
    }
    if preflight.compatibility_domains:
        classifications.add(TRACE_CLASSIFICATION_COMPATIBILITY)
    if preflight.dependency_domains:
        classifications.add(TRACE_CLASSIFICATION_DEPENDENCY)
    if preflight.blocker_domains:
        classifications.add(TRACE_CLASSIFICATION_BLOCKER)
    if preflight.unsupported_domains:
        classifications.add(TRACE_CLASSIFICATION_UNSUPPORTED)
    if preflight.prohibited_domains:
        classifications.add(TRACE_CLASSIFICATION_PROHIBITED)
    return tuple(sorted(classifications))


def _trace_steps(trace_id: str, preflight: OrchestrationPreflightRecord) -> tuple[OrchestrationEvaluationTraceStep, ...]:
    steps = [
        _step(
            trace_id,
            1,
            TRACE_STEP_SUPPORTABILITY,
            f"deterministically classify preflight state {preflight.preflight_state}",
            (preflight.preflight_state, str(preflight.theoretically_supportable)),
        ),
        _step(
            trace_id,
            2,
            TRACE_STEP_GOVERNANCE,
            "deterministically expose governance boundaries",
            preflight.governance_boundaries,
        ),
    ]
    next_sequence = 3
    for step_type, values, description in (
        (TRACE_STEP_COMPATIBILITY, preflight.compatibility_domains, "deterministically expose compatibility domains"),
        (TRACE_STEP_DEPENDENCY, preflight.dependency_domains, "deterministically expose dependency domains"),
        (TRACE_STEP_BLOCKER, preflight.blocker_domains, "deterministically expose blocker-chain domains"),
        (TRACE_STEP_UNSUPPORTED_DOMAIN, preflight.unsupported_domains, "deterministically expose unsupported domains"),
        (TRACE_STEP_PROHIBITED_DOMAIN, preflight.prohibited_domains, "deterministically expose prohibited domains"),
    ):
        if values:
            steps.append(_step(trace_id, next_sequence, step_type, description, values))
            next_sequence += 1
    steps.extend(
        (
            _step(
                trace_id,
                next_sequence,
                TRACE_STEP_PROVENANCE,
                "deterministically expose replay and rollback provenance",
                (*preflight.provenance.replay_reference_ids, *preflight.provenance.rollback_reference_ids),
            ),
            _step(
                trace_id,
                next_sequence + 1,
                TRACE_STEP_EXPLAINABILITY,
                "deterministically expose explainability references",
                preflight.explainability_reference_ids,
            ),
            _step(
                trace_id,
                next_sequence + 2,
                TRACE_STEP_INTEGRITY,
                "deterministically expose integrity references",
                preflight.integrity_reference_ids,
            ),
        )
    )
    return tuple(steps)


def _step(
    trace_id: str,
    sequence_id: int,
    step_type: str,
    description: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationEvaluationTraceStep:
    return OrchestrationEvaluationTraceStep(
        step_id=f"{trace_id}.step.{sequence_id:02d}.{step_type}",
        step_type=step_type,
        sequence_id=sequence_id,
        description=description,
        evidence_ids=tuple(sorted(evidence_ids)),
    )
