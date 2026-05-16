"""Deterministic orchestration evaluation replay packet registry for v3.6 Phase 8."""

from __future__ import annotations

from typing import Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .orchestration_evaluation_replay_models import (
    REPLAY_CLASSIFICATION_BLOCKER,
    REPLAY_CLASSIFICATION_COMPATIBILITY,
    REPLAY_CLASSIFICATION_DEPENDENCY,
    REPLAY_CLASSIFICATION_EXPLAINABILITY,
    REPLAY_CLASSIFICATION_GOVERNANCE,
    REPLAY_CLASSIFICATION_INTEGRITY,
    REPLAY_CLASSIFICATION_PREFLIGHT,
    REPLAY_CLASSIFICATION_PROHIBITED,
    REPLAY_CLASSIFICATION_PROVENANCE,
    REPLAY_CLASSIFICATION_TRACE,
    REPLAY_CLASSIFICATION_UNSUPPORTED,
    REPLAY_COMPATIBILITY_BLOCKED,
    REPLAY_DEPENDENCY_BLOCKED,
    REPLAY_EVIDENCE_BLOCKER,
    REPLAY_EVIDENCE_COMPATIBILITY,
    REPLAY_EVIDENCE_DEPENDENCY,
    REPLAY_EVIDENCE_EXPLAINABILITY,
    REPLAY_EVIDENCE_GOVERNANCE,
    REPLAY_EVIDENCE_INTENT,
    REPLAY_EVIDENCE_INTEGRITY,
    REPLAY_EVIDENCE_POLICY_MAPPING,
    REPLAY_EVIDENCE_PREFLIGHT,
    REPLAY_EVIDENCE_PROHIBITED,
    REPLAY_EVIDENCE_PROVENANCE,
    REPLAY_EVIDENCE_TRACE,
    REPLAY_EVIDENCE_UNSUPPORTED,
    REPLAY_GOVERNANCE_BLOCKED,
    REPLAY_PROHIBITED,
    REPLAY_SUPPORTED,
    REPLAY_UNSUPPORTED,
    OrchestrationEvaluationReplayEvidence,
    OrchestrationEvaluationReplayIdentifier,
    OrchestrationEvaluationReplayPacket,
    OrchestrationEvaluationReplayProvenance,
    OrchestrationEvaluationReplayRegistry,
    export_replay_registry,
    hash_replay_registry,
    serialize_replay_registry,
)
from .orchestration_evaluation_trace_models import (
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_DEPENDENCY_BLOCKED,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_PROHIBITED,
    TRACE_SUPPORTED,
    TRACE_UNSUPPORTED,
    OrchestrationEvaluationTraceRecord,
    hash_trace_record,
)
from .orchestration_evaluation_trace_registry import default_orchestration_evaluation_trace_registry
from .orchestration_intent_models import hash_intent_record
from .orchestration_intent_policy_mapping_models import hash_mapping_record
from .orchestration_intent_policy_mapping_registry import (
    default_orchestration_intent_policy_mapping_registry,
    get_registered_mapping_record_for_intent,
)
from .orchestration_intent_registry import (
    default_orchestration_intent_registry,
    get_registered_intent_record,
)
from .orchestration_policy_compatibility_models import hash_compatibility_relationship
from .orchestration_policy_compatibility_registry import (
    default_orchestration_policy_compatibility_registry,
    get_registered_compatibility_relationship,
)
from .orchestration_preflight_models import hash_preflight_record
from .orchestration_preflight_registry import (
    default_orchestration_preflight_registry,
    get_registered_preflight_record,
)


DEFAULT_REPLAY_REGISTRY_ID = "v3_6_orchestration_evaluation_replay_registry"
DEFAULT_REPLAY_SCHEMA_VERSION = "v3_6.orchestration_evaluation_replay_registry.1"


def default_orchestration_evaluation_replay_registry() -> OrchestrationEvaluationReplayRegistry:
    return build_orchestration_evaluation_replay_registry(default_orchestration_evaluation_replay_packets())


def build_orchestration_evaluation_replay_registry(
    packets: Iterable[OrchestrationEvaluationReplayPacket],
    registry_id: str = DEFAULT_REPLAY_REGISTRY_ID,
) -> OrchestrationEvaluationReplayRegistry:
    ordered = tuple(sorted(packets, key=lambda item: item.identifier.packet_id))
    packet_ids = [packet.identifier.packet_id for packet in ordered]
    if len(packet_ids) != len(set(packet_ids)):
        duplicates = sorted({packet_id for packet_id in packet_ids if packet_ids.count(packet_id) > 1})
        raise ValueError(f"Duplicate orchestration evaluation replay packet ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationEvaluationReplayRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_REPLAY_SCHEMA_VERSION,
        packets=ordered,
        registry_metadata={
            "phase": "v3.6.phase_8",
            "purpose": "deterministic_orchestration_evaluation_replay_packets",
            "planning_only": True,
            "non_production": True,
            "replay_packet_modeling_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "recommendation_behavior_enabled": False,
            "optimization_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
            "persistent_write_enabled": False,
        },
    )


def default_orchestration_evaluation_replay_packets() -> tuple[OrchestrationEvaluationReplayPacket, ...]:
    trace_registry = default_orchestration_evaluation_trace_registry()
    preflight_registry = default_orchestration_preflight_registry()
    intent_registry = default_orchestration_intent_registry()
    mapping_registry = default_orchestration_intent_policy_mapping_registry()
    compatibility_registry = default_orchestration_policy_compatibility_registry()
    return tuple(
        _replay_packet(
            trace=trace,
            preflight=get_registered_preflight_record(preflight_registry, trace.identifier.preflight_id),
            intent=get_registered_intent_record(intent_registry, trace.identifier.intent_id),
            mapping=get_registered_mapping_record_for_intent(mapping_registry, trace.identifier.intent_id),
            compatibility_registry=compatibility_registry,
        )
        for trace in trace_registry.records
    )


def registered_replay_packet_ids(registry: OrchestrationEvaluationReplayRegistry) -> tuple[str, ...]:
    return tuple(sorted(packet.identifier.packet_id for packet in registry.packets))


def get_registered_replay_packet(
    registry: OrchestrationEvaluationReplayRegistry,
    packet_id: str,
) -> OrchestrationEvaluationReplayPacket | None:
    for packet in registry.packets:
        if packet.identifier.packet_id == packet_id:
            return packet
    return None


def get_registered_replay_packet_for_trace(
    registry: OrchestrationEvaluationReplayRegistry,
    trace_id: str,
) -> OrchestrationEvaluationReplayPacket | None:
    for packet in registry.packets:
        if packet.identifier.trace_id == trace_id:
            return packet
    return None


def export_default_orchestration_evaluation_replay_registry() -> dict[str, object]:
    return export_replay_registry(default_orchestration_evaluation_replay_registry())


def serialize_default_orchestration_evaluation_replay_registry() -> str:
    return serialize_replay_registry(default_orchestration_evaluation_replay_registry())


def hash_default_orchestration_evaluation_replay_registry() -> str:
    return hash_replay_registry(default_orchestration_evaluation_replay_registry())


def _replay_packet(
    trace: OrchestrationEvaluationTraceRecord,
    preflight,
    intent,
    mapping,
    compatibility_registry,
) -> OrchestrationEvaluationReplayPacket:
    packet_id = trace.identifier.trace_id.replace("v3_6.trace.", "v3_6.replay.")
    mapping_id = mapping.identifier.mapping_id if mapping is not None else f"{trace.identifier.intent_id}.mapping_gap"
    compatibility_relationship_ids = (
        preflight.provenance.compatibility_relationship_ids
        if preflight is not None
        else ()
    )
    return OrchestrationEvaluationReplayPacket(
        identifier=OrchestrationEvaluationReplayIdentifier(
            packet_id=packet_id,
            trace_id=trace.identifier.trace_id,
            preflight_id=trace.identifier.preflight_id,
            intent_id=trace.identifier.intent_id,
            mapping_id=mapping_id,
            namespace="v3_6.orchestration_evaluation_replay",
            version="1",
        ),
        replay_state=_replay_state(trace.trace_state),
        replay_classifications=_replay_classifications(trace),
        intent_evidence=_intent_evidence(packet_id, intent),
        policy_mapping_evidence=_mapping_evidence(packet_id, mapping),
        governance_evidence=_domain_evidence(packet_id, REPLAY_EVIDENCE_GOVERNANCE, "governance", trace.governance_boundaries),
        compatibility_evidence=_compatibility_evidence(packet_id, trace, compatibility_relationship_ids, compatibility_registry),
        dependency_evidence=_domain_evidence(packet_id, REPLAY_EVIDENCE_DEPENDENCY, "dependency", trace.dependency_domains),
        blocker_evidence=_domain_evidence(packet_id, REPLAY_EVIDENCE_BLOCKER, "blocker", trace.blocker_domains),
        unsupported_evidence=_domain_evidence(packet_id, REPLAY_EVIDENCE_UNSUPPORTED, "unsupported", trace.unsupported_domains),
        prohibited_evidence=_domain_evidence(packet_id, REPLAY_EVIDENCE_PROHIBITED, "prohibited", trace.prohibited_domains),
        preflight_evidence=_preflight_evidence(packet_id, preflight),
        trace_evidence=_trace_evidence(packet_id, trace),
        provenance_evidence=_provenance_evidence(packet_id, trace, preflight, mapping),
        explainability_evidence=_reference_evidence(packet_id, REPLAY_EVIDENCE_EXPLAINABILITY, "explainability", trace.explainability_reference_ids),
        integrity_evidence=_reference_evidence(packet_id, REPLAY_EVIDENCE_INTEGRITY, "integrity", trace.integrity_reference_ids),
        reasoning_chain=trace.reasoning_chain,
        policy_ids=trace.policy_ids,
        governance_boundaries=trace.governance_boundaries,
        compatibility_domains=trace.compatibility_domains,
        dependency_domains=trace.dependency_domains,
        blocker_domains=trace.blocker_domains,
        unsupported_domains=trace.unsupported_domains,
        prohibited_domains=trace.prohibited_domains,
        supported_domains=trace.supported_domains,
        provenance=OrchestrationEvaluationReplayProvenance(
            source_phase="v3.6_phase_8_deterministic_orchestration_evaluation_replay_packets",
            source_artifact="backend/app/runtime_orchestration/orchestration_evaluation_replay_registry.py",
            packet_id=packet_id,
            trace_id=trace.identifier.trace_id,
            preflight_id=trace.identifier.preflight_id,
            intent_id=trace.identifier.intent_id,
            mapping_id=mapping_id,
            policy_ids=trace.policy_ids,
            compatibility_relationship_ids=compatibility_relationship_ids,
            trace_reference_ids=(trace.identifier.trace_id, *trace.integrity_reference_ids),
            preflight_reference_ids=(trace.identifier.preflight_id,),
            replay_reference_ids=(f"{packet_id}.replay",),
            rollback_reference_ids=(f"{packet_id}.rollback",),
            governance_reference_ids=(
                "v3_6_trace_integrity_stable",
                "v3_6_replay_governance_first",
                "v3_6_replay_planning_only",
            ),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "replay_packet_modeling_only": True,
            "evidence_packaging_only": True,
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
    )


def _replay_state(trace_state: str) -> str:
    if trace_state == TRACE_SUPPORTED:
        return REPLAY_SUPPORTED
    if trace_state == TRACE_UNSUPPORTED:
        return REPLAY_UNSUPPORTED
    if trace_state == TRACE_PROHIBITED:
        return REPLAY_PROHIBITED
    if trace_state == TRACE_GOVERNANCE_BLOCKED:
        return REPLAY_GOVERNANCE_BLOCKED
    if trace_state == TRACE_COMPATIBILITY_BLOCKED:
        return REPLAY_COMPATIBILITY_BLOCKED
    if trace_state == TRACE_DEPENDENCY_BLOCKED:
        return REPLAY_DEPENDENCY_BLOCKED
    return REPLAY_UNSUPPORTED


def _replay_classifications(trace: OrchestrationEvaluationTraceRecord) -> tuple[str, ...]:
    classifications = {
        REPLAY_CLASSIFICATION_GOVERNANCE,
        REPLAY_CLASSIFICATION_PREFLIGHT,
        REPLAY_CLASSIFICATION_TRACE,
        REPLAY_CLASSIFICATION_PROVENANCE,
        REPLAY_CLASSIFICATION_EXPLAINABILITY,
        REPLAY_CLASSIFICATION_INTEGRITY,
    }
    if trace.compatibility_domains:
        classifications.add(REPLAY_CLASSIFICATION_COMPATIBILITY)
    if trace.dependency_domains:
        classifications.add(REPLAY_CLASSIFICATION_DEPENDENCY)
    if trace.blocker_domains:
        classifications.add(REPLAY_CLASSIFICATION_BLOCKER)
    if trace.unsupported_domains:
        classifications.add(REPLAY_CLASSIFICATION_UNSUPPORTED)
    if trace.prohibited_domains:
        classifications.add(REPLAY_CLASSIFICATION_PROHIBITED)
    return tuple(sorted(classifications))


def _intent_evidence(packet_id: str, intent) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if intent is None:
        return ()
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_INTENT,
            intent.identifier.intent_id,
            hash_intent_record(intent),
            "deterministically package orchestration intent state",
            (
                intent.identifier.intent_id,
                *intent.policy_domains,
                *intent.governance_boundaries,
            ),
        ),
    )


def _mapping_evidence(packet_id: str, mapping) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if mapping is None:
        return ()
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_POLICY_MAPPING,
            mapping.identifier.mapping_id,
            hash_mapping_record(mapping),
            "deterministically package intent policy mapping state",
            (
                mapping.identifier.intent_id,
                *mapping.policy_ids,
                *mapping.governance_boundaries,
                *mapping.compatibility_domains,
            ),
        ),
    )


def _preflight_evidence(packet_id: str, preflight) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if preflight is None:
        return ()
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_PREFLIGHT,
            preflight.identifier.preflight_id,
            hash_preflight_record(preflight),
            "deterministically package preflight evaluation state",
            (
                preflight.preflight_state,
                *preflight.policy_ids,
                *preflight.preflight_rationale,
            ),
        ),
    )


def _trace_evidence(
    packet_id: str,
    trace: OrchestrationEvaluationTraceRecord,
) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_TRACE,
            trace.identifier.trace_id,
            hash_trace_record(trace),
            "deterministically package evaluation trace state",
            (
                trace.trace_state,
                *tuple(step.step_id for step in trace.trace_steps),
            ),
        ),
    )


def _compatibility_evidence(
    packet_id: str,
    trace: OrchestrationEvaluationTraceRecord,
    relationship_ids: tuple[str, ...],
    compatibility_registry,
) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if not trace.compatibility_domains:
        return ()
    relationship_hashes = []
    for relationship_id in relationship_ids:
        relationship = get_registered_compatibility_relationship(compatibility_registry, relationship_id)
        if relationship is not None:
            relationship_hashes.append(f"{relationship_id}:{hash_compatibility_relationship(relationship)}")
        else:
            relationship_hashes.append(f"{relationship_id}:missing_relationship")
    source_hash = deterministic_hash(
        {
            "compatibility_domains": trace.compatibility_domains,
            "compatibility_relationship_hashes": tuple(sorted(relationship_hashes)),
        }
    )
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_COMPATIBILITY,
            "compatibility_evidence_bundle",
            source_hash,
            "deterministically package compatibility evidence",
            (*trace.compatibility_domains, *relationship_ids),
        ),
    )


def _domain_evidence(
    packet_id: str,
    evidence_type: str,
    domain_name: str,
    values: tuple[str, ...],
) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if not values:
        return ()
    return (
        _evidence(
            packet_id,
            evidence_type,
            f"{domain_name}_domain_bundle",
            deterministic_hash({"domain": domain_name, "values": tuple(sorted(values))}),
            f"deterministically package {domain_name} evidence",
            values,
        ),
    )


def _reference_evidence(
    packet_id: str,
    evidence_type: str,
    reference_name: str,
    values: tuple[str, ...],
) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    if not values:
        return ()
    return (
        _evidence(
            packet_id,
            evidence_type,
            f"{reference_name}_reference_bundle",
            deterministic_hash({"reference": reference_name, "values": tuple(sorted(values))}),
            f"deterministically package {reference_name} evidence",
            values,
        ),
    )


def _provenance_evidence(packet_id: str, trace: OrchestrationEvaluationTraceRecord, preflight, mapping) -> tuple[OrchestrationEvaluationReplayEvidence, ...]:
    values = (
        trace.provenance.source_phase,
        trace.provenance.source_artifact,
        trace.provenance.preflight_id,
        trace.provenance.intent_id,
        *(preflight.provenance.replay_reference_ids if preflight is not None else ()),
        *(preflight.provenance.rollback_reference_ids if preflight is not None else ()),
        *(mapping.provenance.replay_reference_ids if mapping is not None else ()),
        *(mapping.provenance.rollback_reference_ids if mapping is not None else ()),
        *trace.provenance.replay_reference_ids,
        *trace.provenance.rollback_reference_ids,
    )
    return (
        _evidence(
            packet_id,
            REPLAY_EVIDENCE_PROVENANCE,
            "replay_provenance_bundle",
            deterministic_hash({"provenance": tuple(sorted(values))}),
            "deterministically package provenance continuity evidence",
            values,
        ),
    )


def _evidence(
    packet_id: str,
    evidence_type: str,
    source_id: str,
    source_hash: str,
    description: str,
    reference_ids: tuple[str, ...],
) -> OrchestrationEvaluationReplayEvidence:
    suffix = evidence_type.replace("_packet", "")
    return OrchestrationEvaluationReplayEvidence(
        evidence_id=f"{packet_id}.{suffix}",
        evidence_type=evidence_type,
        source_id=source_id,
        source_hash=source_hash,
        description=description,
        reference_ids=tuple(sorted(reference_ids)),
    )
