"""Deterministic orchestration evaluation replay packet integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_replay_builder import build_orchestration_evaluation_replay_packets
from .orchestration_evaluation_replay_explainability import explain_orchestration_evaluation_replay_packets
from .orchestration_evaluation_replay_models import (
    REPLAY_COMPATIBILITY_BLOCKED,
    REPLAY_DEPENDENCY_BLOCKED,
    REPLAY_EVIDENCE_TYPES,
    REPLAY_EXPLAINABILITY_STABLE,
    REPLAY_GOVERNANCE_BLOCKED,
    REPLAY_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_INTENT_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_POLICY_MAPPING_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_TRACE_GAP,
    REPLAY_INTEGRITY_STABLE,
    REPLAY_PROHIBITED,
    REPLAY_STATES,
    REPLAY_SUPPORTED,
    REPLAY_UNSUPPORTED,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
    OrchestrationEvaluationReplayIntegrityResult,
    OrchestrationEvaluationReplayIntegritySummary,
    OrchestrationEvaluationReplayPacket,
    OrchestrationEvaluationReplayRegistry,
    export_replay_integrity_result,
    hash_replay_integrity_result,
    hash_replay_packet,
    hash_replay_registry,
    serialize_replay_integrity_result,
    serialize_replay_registry,
)
from .orchestration_evaluation_replay_registry import default_orchestration_evaluation_replay_registry


def default_orchestration_evaluation_replay_integrity_input() -> OrchestrationEvaluationReplayIntegrityInput:
    registry = default_orchestration_evaluation_replay_registry()
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=registry)
    )
    explainability = explain_orchestration_evaluation_replay_packets(registry, build)
    return OrchestrationEvaluationReplayIntegrityInput(
        replay_registry=registry,
        build_result=build,
        explainability_result=explainability,
    )


def audit_orchestration_evaluation_replay_integrity(
    integrity_input: OrchestrationEvaluationReplayIntegrityInput | None = None,
) -> OrchestrationEvaluationReplayIntegrityResult:
    source = integrity_input or default_orchestration_evaluation_replay_integrity_input()
    registry_hash = hash_replay_registry(source.replay_registry)
    registry = _registry_integrity(source, registry_hash)
    replay_hash = _replay_hash_integrity(source.replay_registry)
    provenance = _provenance_integrity(source.replay_registry)
    evidence = _evidence_integrity(source.replay_registry)
    intent = _intent_integrity(source.replay_registry)
    policy_mapping = _policy_mapping_integrity(source.replay_registry)
    trace = _trace_integrity(source.replay_registry)
    explainability = _explainability_integrity(source)
    governance = _governance_integrity(source.replay_registry)
    compatibility = _compatibility_integrity(source.replay_registry)
    dependency = _dependency_integrity(source.replay_registry)
    blocker = _blocker_integrity(source.replay_registry)
    supported_domain = _supported_domain_integrity(source.replay_registry)
    serialization = _serialization_integrity(source.replay_registry)
    failures = _failure_summary(
        registry,
        replay_hash,
        provenance,
        evidence,
        intent,
        policy_mapping,
        trace,
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
        replay_hash,
        provenance,
        evidence,
        intent,
        policy_mapping,
        trace,
        explainability,
        governance,
        compatibility,
        dependency,
        blocker,
        supported_domain,
    )
    result = OrchestrationEvaluationReplayIntegrityResult(
        registry_id=source.replay_registry.registry_id,
        replay_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        replay_hash_integrity=replay_hash,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        governance_integrity=governance,
        compatibility_integrity=compatibility,
        dependency_integrity=dependency,
        blocker_integrity=blocker,
        supported_domain_integrity=supported_domain,
        evidence_integrity=evidence,
        intent_integrity=intent,
        policy_mapping_integrity=policy_mapping,
        trace_integrity=trace,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_replay_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_replay_integrity_hash=hash_replay_integrity_result(result))


def export_orchestration_evaluation_replay_integrity_result(
    result: OrchestrationEvaluationReplayIntegrityResult,
) -> dict[str, object]:
    return export_replay_integrity_result(result)


def serialize_orchestration_evaluation_replay_integrity_result(
    result: OrchestrationEvaluationReplayIntegrityResult,
) -> str:
    return serialize_replay_integrity_result(result)


def hash_orchestration_evaluation_replay_integrity_result(
    result: OrchestrationEvaluationReplayIntegrityResult,
) -> str:
    return hash_replay_integrity_result(result)


def _registry_integrity(
    source: OrchestrationEvaluationReplayIntegrityInput,
    registry_hash: str,
) -> OrchestrationEvaluationReplayIntegritySummary:
    failures: list[str] = []
    if not source.replay_registry.packets:
        failures.append("replay_registry_has_no_packets")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("replay_registry_hash_mismatch")
    if not source.replay_registry.planning_only or not source.replay_registry.non_production:
        failures.append("replay_registry_boundary_not_planning_only_non_production")
    return OrchestrationEvaluationReplayIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _replay_hash_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(f"{packet.identifier.packet_id}:{hash_replay_packet(packet)}" for packet in registry.packets))
    ids = [packet.identifier.packet_id for packet in registry.packets]
    duplicates = sorted({packet_id for packet_id in ids if ids.count(packet_id) > 1})
    failures = tuple(f"duplicate_replay_packet_id:{packet_id}" for packet_id in duplicates)
    failures += tuple(
        sorted(
            f"{packet.identifier.packet_id}:unrecognized_replay_state"
            for packet in registry.packets
            if packet.replay_state not in REPLAY_STATES
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("replay_hash", references, failures)


def _provenance_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for packet in registry.packets:
        provenance = packet.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                provenance.packet_id,
                provenance.trace_id,
                provenance.preflight_id,
                provenance.intent_id,
                provenance.mapping_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.trace_reference_ids,
                *provenance.preflight_reference_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{packet.identifier.packet_id}:source_provenance_gap")
        if not provenance.packet_id:
            failures.append(f"{packet.identifier.packet_id}:packet_provenance_gap")
        if not provenance.trace_id:
            failures.append(f"{packet.identifier.packet_id}:trace_provenance_gap")
        if not provenance.preflight_id:
            failures.append(f"{packet.identifier.packet_id}:preflight_provenance_gap")
        if not provenance.intent_id:
            failures.append(f"{packet.identifier.packet_id}:intent_provenance_gap")
        if not provenance.mapping_id:
            failures.append(f"{packet.identifier.packet_id}:mapping_provenance_gap")
        if not provenance.policy_ids:
            failures.append(f"{packet.identifier.packet_id}:policy_provenance_gap")
        if not provenance.trace_reference_ids:
            failures.append(f"{packet.identifier.packet_id}:trace_reference_gap")
        if not provenance.preflight_reference_ids:
            failures.append(f"{packet.identifier.packet_id}:preflight_reference_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{packet.identifier.packet_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{packet.identifier.packet_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{packet.identifier.packet_id}:governance_provenance_gap")
    return OrchestrationEvaluationReplayIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _evidence_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for packet in registry.packets:
        evidence_items = _all_evidence(packet)
        references.extend(evidence.evidence_id for evidence in evidence_items)
        if not packet.preflight_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_preflight_evidence")
        if not packet.trace_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_trace_evidence")
        if not packet.provenance_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_provenance_evidence")
        if not packet.explainability_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_explainability_evidence")
        if not packet.integrity_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_integrity_evidence")
        if not packet.reasoning_chain:
            failures.append(f"{packet.identifier.packet_id}:missing_reasoning_chain_visibility")
        failures.extend(
            sorted(
                f"{packet.identifier.packet_id}:unrecognized_evidence_type:{evidence.evidence_type}"
                for evidence in evidence_items
                if evidence.evidence_type not in REPLAY_EVIDENCE_TYPES
            )
        )
    return OrchestrationEvaluationReplayIntegritySummary("evidence", tuple(sorted(set(references))), tuple(sorted(failures)))


def _intent_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(evidence.source_id for packet in registry.packets for evidence in packet.intent_evidence))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_intent_evidence"
            for packet in registry.packets
            if not packet.intent_evidence or not packet.identifier.intent_id
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("intent", references, failures)


def _policy_mapping_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(evidence.source_id for packet in registry.packets for evidence in packet.policy_mapping_evidence))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_policy_mapping_evidence"
            for packet in registry.packets
            if not packet.policy_mapping_evidence or not packet.identifier.mapping_id
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("policy_mapping", references, failures)


def _trace_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(evidence.source_id for packet in registry.packets for evidence in packet.trace_evidence))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_trace_evidence"
            for packet in registry.packets
            if not packet.trace_evidence or not packet.identifier.trace_id
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("trace", references, failures)


def _explainability_integrity(source: OrchestrationEvaluationReplayIntegrityInput) -> OrchestrationEvaluationReplayIntegritySummary:
    references = (
        source.build_result.deterministic_replay_build_hash,
        source.explainability_result.deterministic_replay_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.replay_explainability_status != REPLAY_EXPLAINABILITY_STABLE:
        failures.append(f"replay_explainability_status:{source.explainability_result.replay_explainability_status}")
    if source.expected_build_hash is not None and source.expected_build_hash != source.build_result.deterministic_replay_build_hash:
        failures.append("replay_build_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_replay_explainability_hash:
        failures.append("replay_explainability_hash_mismatch")
    return OrchestrationEvaluationReplayIntegritySummary("explainability", references, tuple(sorted(failures)))


def _governance_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(packet.identifier.packet_id for packet in registry.packets))
    failures: list[str] = []
    for packet in registry.packets:
        if not packet.governance_boundaries or not packet.governance_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_governance_boundary_visibility")
        if packet.replay_state == REPLAY_GOVERNANCE_BLOCKED and not packet.governance_boundaries:
            failures.append(f"{packet.identifier.packet_id}:missing_governance_blocker_visibility")
        if _governance_gap(packet):
            failures.append(f"{packet.identifier.packet_id}:governance_boundary_gap")
    return OrchestrationEvaluationReplayIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(packet.identifier.packet_id for packet in registry.packets if packet.compatibility_evidence))
    failures: list[str] = []
    for packet in registry.packets:
        if packet.replay_state == REPLAY_COMPATIBILITY_BLOCKED and not packet.compatibility_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_compatibility_evidence")
        if packet.replay_state in (REPLAY_UNSUPPORTED, REPLAY_PROHIBITED) and not packet.compatibility_evidence:
            failures.append(f"{packet.identifier.packet_id}:missing_blocked_compatibility_evidence")
    return OrchestrationEvaluationReplayIntegritySummary("compatibility", references, tuple(sorted(failures)))


def _dependency_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(packet.identifier.packet_id for packet in registry.packets if packet.dependency_evidence))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_dependency_evidence"
            for packet in registry.packets
            if packet.replay_state == REPLAY_DEPENDENCY_BLOCKED and not packet.dependency_evidence
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("dependency", references, failures)


def _blocker_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(packet.identifier.packet_id for packet in registry.packets if packet.blocker_evidence))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_blocker_evidence"
            for packet in registry.packets
            if packet.replay_state != REPLAY_SUPPORTED and not packet.blocker_evidence
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("blocker", references, failures)


def _supported_domain_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    references = tuple(sorted(packet.identifier.packet_id for packet in registry.packets if packet.supported_domains))
    failures = tuple(
        sorted(
            f"{packet.identifier.packet_id}:missing_supported_domain_visibility"
            for packet in registry.packets
            if packet.replay_state == REPLAY_SUPPORTED and not packet.supported_domains
        )
    )
    return OrchestrationEvaluationReplayIntegritySummary("supported_domain", references, failures)


def _serialization_integrity(registry: OrchestrationEvaluationReplayRegistry) -> OrchestrationEvaluationReplayIntegritySummary:
    first = serialize_replay_registry(registry)
    second = serialize_replay_registry(registry)
    failures = () if first == second else ("replay_registry_serialization_not_stable",)
    return OrchestrationEvaluationReplayIntegritySummary("deterministic_serialization", (hash_replay_registry(registry),), failures)


def _governance_gap(packet: OrchestrationEvaluationReplayPacket) -> bool:
    metadata = packet.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "replay_packet_modeling_only", "evidence_packaging_only")
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
            packet.runtime_execution_enabled,
            packet.orchestration_execution_enabled,
            packet.routing_behavior_enabled,
            packet.mutation_behavior_enabled,
            packet.production_consumption_enabled,
            packet.background_processing_enabled,
            packet.recommendation_behavior_enabled,
            packet.optimization_behavior_enabled,
            packet.autonomous_behavior_enabled,
            packet.graph_execution_enabled,
            packet.replay_execution_enabled,
            packet.persistent_write_enabled,
        )
    )


def _failure_summary(*summaries: OrchestrationEvaluationReplayIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationEvaluationReplayIntegritySummary,
    replay_hash: OrchestrationEvaluationReplayIntegritySummary,
    provenance: OrchestrationEvaluationReplayIntegritySummary,
    evidence: OrchestrationEvaluationReplayIntegritySummary,
    intent: OrchestrationEvaluationReplayIntegritySummary,
    policy_mapping: OrchestrationEvaluationReplayIntegritySummary,
    trace: OrchestrationEvaluationReplayIntegritySummary,
    explainability: OrchestrationEvaluationReplayIntegritySummary,
    governance: OrchestrationEvaluationReplayIntegritySummary,
    compatibility: OrchestrationEvaluationReplayIntegritySummary,
    dependency: OrchestrationEvaluationReplayIntegritySummary,
    blocker: OrchestrationEvaluationReplayIntegritySummary,
    supported_domain: OrchestrationEvaluationReplayIntegritySummary,
) -> str:
    if registry.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP if "replay_registry_hash_mismatch" in registry.failures else REPLAY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if replay_hash.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if evidence.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP
    if intent.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_INTENT_GAP
    if policy_mapping.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_POLICY_MAPPING_GAP
    if trace.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_TRACE_GAP
    if explainability.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else REPLAY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if governance.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    if dependency.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    if blocker.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if supported_domain.failures:
        return REPLAY_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    return REPLAY_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == REPLAY_INTEGRITY_STABLE:
        return (
            "Replay packet integrity is stable; registry, hashes, provenance, evidence, intent, policy mapping, "
            "trace, explainability, governance, compatibility, dependency, blocker, supported-domain, and "
            "serialization continuity remain deterministic and non-executing."
        )
    return f"Replay packet integrity classified as {status}; failures: {', '.join(failures)}."


def _all_evidence(packet: OrchestrationEvaluationReplayPacket) -> tuple[object, ...]:
    fields = (
        "intent_evidence",
        "policy_mapping_evidence",
        "governance_evidence",
        "compatibility_evidence",
        "dependency_evidence",
        "blocker_evidence",
        "unsupported_evidence",
        "prohibited_evidence",
        "preflight_evidence",
        "trace_evidence",
        "provenance_evidence",
        "explainability_evidence",
        "integrity_evidence",
    )
    return tuple(evidence for field in fields for evidence in getattr(packet, field))
