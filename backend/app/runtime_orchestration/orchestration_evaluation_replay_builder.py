"""Deterministic orchestration evaluation replay packet building."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_replay_models import (
    REPLAY_BLOCKER_EVIDENCE_VISIBLE,
    REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP,
    REPLAY_BUILD_STABLE,
    REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS,
    REPLAY_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    REPLAY_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    REPLAY_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    REPLAY_CLASSIFIED_AS_PROHIBITED,
    REPLAY_CLASSIFIED_AS_SUPPORTED,
    REPLAY_CLASSIFIED_AS_UNSUPPORTED,
    REPLAY_COMPATIBILITY_BLOCKED,
    REPLAY_COMPATIBILITY_EVIDENCE_VISIBLE,
    REPLAY_CONTINUITY_GAP,
    REPLAY_CONTINUITY_PRESERVED,
    REPLAY_DEPENDENCY_BLOCKED,
    REPLAY_DEPENDENCY_EVIDENCE_VISIBLE,
    REPLAY_EVIDENCE_GAP,
    REPLAY_EVIDENCE_TYPES,
    REPLAY_EXPLAINABILITY_EVIDENCE_VISIBLE,
    REPLAY_EXPLAINABILITY_GAP,
    REPLAY_GOVERNANCE_BLOCKED,
    REPLAY_GOVERNANCE_BOUNDARY_GAP,
    REPLAY_GOVERNANCE_EVIDENCE_VISIBLE,
    REPLAY_HASH_MISMATCH,
    REPLAY_INTEGRITY_EVIDENCE_VISIBLE,
    REPLAY_INTEGRITY_GAP,
    REPLAY_INTENT_EVIDENCE_VISIBLE,
    REPLAY_INTENT_GAP,
    REPLAY_POLICY_MAPPING_GAP,
    REPLAY_POLICY_MAPPING_VISIBLE,
    REPLAY_PREFLIGHT_EVIDENCE_VISIBLE,
    REPLAY_PROHIBITED,
    REPLAY_PROHIBITED_EVIDENCE_VISIBLE,
    REPLAY_PROVENANCE_EVIDENCE_VISIBLE,
    REPLAY_PROVENANCE_GAP,
    REPLAY_REASONING_CHAIN_VISIBLE,
    REPLAY_SUPPORTED,
    REPLAY_SUPPORTED_DOMAIN_VISIBLE,
    REPLAY_TRACE_EVIDENCE_VISIBLE,
    REPLAY_TRACE_GAP,
    REPLAY_UNSUPPORTED,
    REPLAY_UNSUPPORTED_EVIDENCE_VISIBLE,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayBuildRecord,
    OrchestrationEvaluationReplayBuildResult,
    OrchestrationEvaluationReplayFinding,
    OrchestrationEvaluationReplayPacket,
    export_replay_build_result,
    hash_replay_build_result,
    hash_replay_packet,
    hash_replay_registry,
    serialize_replay_build_result,
)
from .orchestration_evaluation_replay_registry import default_orchestration_evaluation_replay_registry


STRUCTURAL_REPLAY_FINDINGS: frozenset[str] = frozenset(
    {
        REPLAY_PROVENANCE_GAP,
        REPLAY_EXPLAINABILITY_GAP,
        REPLAY_INTEGRITY_GAP,
        REPLAY_HASH_MISMATCH,
        REPLAY_GOVERNANCE_BOUNDARY_GAP,
        REPLAY_EVIDENCE_GAP,
        REPLAY_INTENT_GAP,
        REPLAY_POLICY_MAPPING_GAP,
        REPLAY_TRACE_GAP,
    }
)


def default_orchestration_evaluation_replay_build_input() -> OrchestrationEvaluationReplayBuildInput:
    return OrchestrationEvaluationReplayBuildInput(
        replay_registry=default_orchestration_evaluation_replay_registry()
    )


def build_orchestration_evaluation_replay_packets(
    build_input: OrchestrationEvaluationReplayBuildInput | None = None,
) -> OrchestrationEvaluationReplayBuildResult:
    source = build_input or default_orchestration_evaluation_replay_build_input()
    registry_hash = hash_replay_registry(source.replay_registry)
    records = tuple(_build_record(packet, source) for packet in source.replay_registry.packets)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _build_status(records, findings)
    result = OrchestrationEvaluationReplayBuildResult(
        registry_id=source.replay_registry.registry_id,
        replay_build_status=status,
        planning_only=True,
        build_records=records,
        registered_replay_packet_count=len(records),
        governance_evidence_count=_packet_count(source.replay_registry.packets, "governance_evidence"),
        compatibility_evidence_count=_packet_count(source.replay_registry.packets, "compatibility_evidence"),
        dependency_evidence_count=_packet_count(source.replay_registry.packets, "dependency_evidence"),
        blocker_evidence_count=_packet_count(source.replay_registry.packets, "blocker_evidence"),
        unsupported_replay_count=_packet_count(source.replay_registry.packets, "unsupported_evidence"),
        prohibited_replay_count=_packet_count(source.replay_registry.packets, "prohibited_evidence"),
        preflight_evidence_count=_packet_count(source.replay_registry.packets, "preflight_evidence"),
        trace_evidence_count=_packet_count(source.replay_registry.packets, "trace_evidence"),
        intent_evidence_count=_packet_count(source.replay_registry.packets, "intent_evidence"),
        policy_mapping_evidence_count=_packet_count(source.replay_registry.packets, "policy_mapping_evidence"),
        reasoning_step_count=sum(len(packet.reasoning_chain) for packet in source.replay_registry.packets),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_replay_build_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_replay_build_hash=hash_replay_build_result(result))


def build_orchestration_evaluation_replay(
    build_input: OrchestrationEvaluationReplayBuildInput | None = None,
) -> OrchestrationEvaluationReplayBuildResult:
    return build_orchestration_evaluation_replay_packets(build_input)


def export_orchestration_evaluation_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> dict[str, object]:
    return export_replay_build_result(result)


def serialize_orchestration_evaluation_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> str:
    return serialize_replay_build_result(result)


def hash_orchestration_evaluation_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> str:
    return hash_replay_build_result(result)


def _build_record(
    packet: OrchestrationEvaluationReplayPacket,
    source: OrchestrationEvaluationReplayBuildInput,
) -> OrchestrationEvaluationReplayBuildRecord:
    packet_hash = hash_replay_packet(packet)
    findings = _packet_findings(packet)
    expected_hash = source.expected_packet_hashes.get(packet.identifier.packet_id) if source.expected_packet_hashes else None
    if expected_hash is not None and expected_hash != packet_hash:
        findings.append(
            OrchestrationEvaluationReplayFinding(
                packet_id=packet.identifier.packet_id,
                trace_id=packet.identifier.trace_id,
                classification=REPLAY_HASH_MISMATCH,
                reason="replay packet hash does not match expected deterministic hash",
                evidence_ids=(packet_hash, expected_hash),
            )
        )
    provenance_continuity = REPLAY_CONTINUITY_GAP if any(finding.classification == REPLAY_PROVENANCE_GAP for finding in findings) else REPLAY_CONTINUITY_PRESERVED
    explainability_continuity = REPLAY_CONTINUITY_GAP if any(finding.classification == REPLAY_EXPLAINABILITY_GAP for finding in findings) else REPLAY_CONTINUITY_PRESERVED
    integrity_continuity = REPLAY_CONTINUITY_GAP if any(finding.classification in (REPLAY_INTEGRITY_GAP, REPLAY_HASH_MISMATCH, REPLAY_EVIDENCE_GAP, REPLAY_TRACE_GAP) for finding in findings) else REPLAY_CONTINUITY_PRESERVED
    governance_continuity = REPLAY_CONTINUITY_GAP if any(finding.classification == REPLAY_GOVERNANCE_BOUNDARY_GAP for finding in findings) else REPLAY_CONTINUITY_PRESERVED
    return OrchestrationEvaluationReplayBuildRecord(
        packet_id=packet.identifier.packet_id,
        trace_id=packet.identifier.trace_id,
        replay_state=packet.replay_state,
        packet_hash=packet_hash,
        evidence_count=sum(len(getattr(packet, field)) for field in _evidence_fields()),
        intent_evidence_count=len(packet.intent_evidence),
        policy_mapping_evidence_count=len(packet.policy_mapping_evidence),
        governance_evidence_count=len(packet.governance_evidence),
        compatibility_evidence_count=len(packet.compatibility_evidence),
        dependency_evidence_count=len(packet.dependency_evidence),
        blocker_evidence_count=len(packet.blocker_evidence),
        unsupported_evidence_count=len(packet.unsupported_evidence),
        prohibited_evidence_count=len(packet.prohibited_evidence),
        preflight_evidence_count=len(packet.preflight_evidence),
        trace_evidence_count=len(packet.trace_evidence),
        reasoning_step_count=len(packet.reasoning_chain),
        provenance_continuity_state=provenance_continuity,
        explainability_continuity_state=explainability_continuity,
        integrity_continuity_state=integrity_continuity,
        governance_continuity_state=governance_continuity,
        findings=tuple(sorted(findings, key=_finding_sort_key)),
    )


def _packet_findings(packet: OrchestrationEvaluationReplayPacket) -> list[OrchestrationEvaluationReplayFinding]:
    findings = [_state_finding(packet)]
    for classification, values, reason in (
        (REPLAY_INTENT_EVIDENCE_VISIBLE, packet.intent_evidence, "intent evidence is packaged"),
        (REPLAY_POLICY_MAPPING_VISIBLE, packet.policy_mapping_evidence, "policy mapping evidence is packaged"),
        (REPLAY_GOVERNANCE_EVIDENCE_VISIBLE, packet.governance_evidence, "governance evidence is packaged"),
        (REPLAY_COMPATIBILITY_EVIDENCE_VISIBLE, packet.compatibility_evidence, "compatibility evidence is packaged"),
        (REPLAY_DEPENDENCY_EVIDENCE_VISIBLE, packet.dependency_evidence, "dependency evidence is packaged"),
        (REPLAY_BLOCKER_EVIDENCE_VISIBLE, packet.blocker_evidence, "blocker evidence is packaged"),
        (REPLAY_UNSUPPORTED_EVIDENCE_VISIBLE, packet.unsupported_evidence, "unsupported evidence is packaged"),
        (REPLAY_PROHIBITED_EVIDENCE_VISIBLE, packet.prohibited_evidence, "prohibited evidence is packaged"),
        (REPLAY_PREFLIGHT_EVIDENCE_VISIBLE, packet.preflight_evidence, "preflight evidence is packaged"),
        (REPLAY_TRACE_EVIDENCE_VISIBLE, packet.trace_evidence, "trace evidence is packaged"),
        (REPLAY_PROVENANCE_EVIDENCE_VISIBLE, packet.provenance_evidence, "provenance evidence is packaged"),
        (REPLAY_EXPLAINABILITY_EVIDENCE_VISIBLE, packet.explainability_evidence, "explainability evidence is packaged"),
        (REPLAY_INTEGRITY_EVIDENCE_VISIBLE, packet.integrity_evidence, "integrity evidence is packaged"),
        (REPLAY_SUPPORTED_DOMAIN_VISIBLE, packet.supported_domains, "supported domains are visible"),
    ):
        if values:
            findings.append(_finding(packet, classification, reason, _evidence_ids(values)))
    if packet.reasoning_chain:
        findings.append(_finding(packet, REPLAY_REASONING_CHAIN_VISIBLE, "reasoning chain is packaged", packet.reasoning_chain))
    findings.extend(_continuity_findings(packet))
    return findings


def _state_finding(packet: OrchestrationEvaluationReplayPacket) -> OrchestrationEvaluationReplayFinding:
    state_map = {
        REPLAY_SUPPORTED: (REPLAY_CLASSIFIED_AS_SUPPORTED, "replay packet preserves a supported theoretical evaluation state", packet.supported_domains),
        REPLAY_UNSUPPORTED: (REPLAY_CLASSIFIED_AS_UNSUPPORTED, "replay packet preserves an unsupported fail-visible evaluation state", packet.unsupported_domains),
        REPLAY_PROHIBITED: (REPLAY_CLASSIFIED_AS_PROHIBITED, "replay packet preserves a prohibited fail-visible evaluation state", packet.prohibited_domains),
        REPLAY_GOVERNANCE_BLOCKED: (REPLAY_CLASSIFIED_AS_GOVERNANCE_BLOCKED, "replay packet preserves a governance-blocked evaluation state", packet.governance_boundaries),
        REPLAY_COMPATIBILITY_BLOCKED: (REPLAY_CLASSIFIED_AS_COMPATIBILITY_BLOCKED, "replay packet preserves a compatibility-blocked evaluation state", packet.compatibility_domains),
        REPLAY_DEPENDENCY_BLOCKED: (REPLAY_CLASSIFIED_AS_DEPENDENCY_BLOCKED, "replay packet preserves a dependency-blocked evaluation state", packet.dependency_domains),
    }
    classification, reason, evidence = state_map.get(
        packet.replay_state,
        (REPLAY_GOVERNANCE_BOUNDARY_GAP, "replay packet state is not recognized", (packet.replay_state,)),
    )
    return _finding(packet, classification, reason, evidence)


def _continuity_findings(packet: OrchestrationEvaluationReplayPacket) -> list[OrchestrationEvaluationReplayFinding]:
    findings: list[OrchestrationEvaluationReplayFinding] = []
    missing_provenance = _missing_provenance(packet)
    if missing_provenance:
        findings.append(_finding(packet, REPLAY_PROVENANCE_GAP, "replay packet provenance continuity gap", missing_provenance))
    if not packet.intent_evidence:
        findings.append(_finding(packet, REPLAY_INTENT_GAP, "replay packet has no packaged intent evidence", (packet.identifier.packet_id,)))
    if not packet.policy_mapping_evidence:
        findings.append(_finding(packet, REPLAY_POLICY_MAPPING_GAP, "replay packet has no packaged policy mapping evidence", (packet.identifier.packet_id,)))
    if not packet.preflight_evidence:
        findings.append(_finding(packet, REPLAY_EVIDENCE_GAP, "replay packet has no packaged preflight evidence", (packet.identifier.packet_id,)))
    if not packet.trace_evidence:
        findings.append(_finding(packet, REPLAY_TRACE_GAP, "replay packet has no packaged trace evidence", (packet.identifier.packet_id,)))
    if not packet.reasoning_chain:
        findings.append(_finding(packet, REPLAY_EVIDENCE_GAP, "replay packet reasoning chain is missing", (packet.identifier.packet_id,)))
    if any(evidence.evidence_type not in REPLAY_EVIDENCE_TYPES for evidence in _all_evidence(packet)):
        findings.append(_finding(packet, REPLAY_EVIDENCE_GAP, "replay packet evidence type is not recognized", tuple(evidence.evidence_type for evidence in _all_evidence(packet))))
    if not packet.provenance_evidence:
        findings.append(_finding(packet, REPLAY_PROVENANCE_GAP, "replay packet provenance evidence is missing", (packet.identifier.packet_id,)))
    if not packet.explainability_evidence:
        findings.append(_finding(packet, REPLAY_EXPLAINABILITY_GAP, "replay packet explainability evidence is missing", (packet.identifier.packet_id,)))
    if not packet.integrity_evidence:
        findings.append(_finding(packet, REPLAY_INTEGRITY_GAP, "replay packet integrity evidence is missing", (packet.identifier.packet_id,)))
    if _governance_boundary_gap(packet):
        findings.append(_finding(packet, REPLAY_GOVERNANCE_BOUNDARY_GAP, "replay packet governance boundary is not planning-only", (packet.identifier.packet_id,)))
    return findings


def _finding(
    packet: OrchestrationEvaluationReplayPacket,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationEvaluationReplayFinding:
    return OrchestrationEvaluationReplayFinding(
        packet_id=packet.identifier.packet_id,
        trace_id=packet.identifier.trace_id,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(evidence_ids)),
    )


def _missing_provenance(packet: OrchestrationEvaluationReplayPacket) -> tuple[str, ...]:
    provenance = packet.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.packet_id:
        missing.append("packet_id")
    if not provenance.trace_id:
        missing.append("trace_id")
    if not provenance.preflight_id:
        missing.append("preflight_id")
    if not provenance.intent_id:
        missing.append("intent_id")
    if not provenance.mapping_id:
        missing.append("mapping_id")
    if not provenance.policy_ids:
        missing.append("policy_ids")
    if not provenance.trace_reference_ids:
        missing.append("trace_reference_ids")
    if not provenance.preflight_reference_ids:
        missing.append("preflight_reference_ids")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    return tuple(sorted(missing))


def _governance_boundary_gap(packet: OrchestrationEvaluationReplayPacket) -> bool:
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


def _registry_hash_finding(
    source: OrchestrationEvaluationReplayBuildInput,
    registry_hash: str,
) -> OrchestrationEvaluationReplayFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationEvaluationReplayFinding(
        packet_id=source.replay_registry.registry_id,
        trace_id=source.replay_registry.registry_id,
        classification=REPLAY_HASH_MISMATCH,
        reason="replay packet registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _packet_count(packets: tuple[OrchestrationEvaluationReplayPacket, ...], field: str) -> int:
    return sum(1 for packet in packets if getattr(packet, field))


def _continuity_status(records: tuple[OrchestrationEvaluationReplayBuildRecord, ...], field: str) -> str:
    return REPLAY_CONTINUITY_PRESERVED if all(getattr(record, field) == REPLAY_CONTINUITY_PRESERVED for record in records) else REPLAY_CONTINUITY_GAP


def _build_status(
    records: tuple[OrchestrationEvaluationReplayBuildRecord, ...],
    findings: tuple[OrchestrationEvaluationReplayFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_REPLAY_FINDINGS for finding in findings):
        return REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS
    return REPLAY_BUILD_STABLE


def _summary(status: str, findings: tuple[OrchestrationEvaluationReplayFinding, ...]) -> str:
    if status == REPLAY_BUILD_STABLE:
        return "Replay packet building is stable; no replay packets require fail-visible classification."
    if status == REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Replay packet building is stable with visible intent, policy mapping, governance, compatibility, "
            "dependency, blocker, unsupported, prohibited, preflight, trace, provenance, explainability, "
            "integrity, and reasoning-chain findings."
        )
    visible = tuple(sorted({f"{finding.packet_id}:{finding.classification}" for finding in findings}))
    return f"Replay packet building is {status}; visible replay entries: {', '.join(visible)}."


def _evidence_fields() -> tuple[str, ...]:
    return (
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


def _all_evidence(packet: OrchestrationEvaluationReplayPacket) -> tuple[object, ...]:
    return tuple(evidence for field in _evidence_fields() for evidence in getattr(packet, field))


def _evidence_ids(values: tuple[object, ...]) -> tuple[str, ...]:
    ids: list[str] = []
    for value in values:
        evidence_id = getattr(value, "evidence_id", None)
        ids.append(evidence_id if evidence_id is not None else str(value))
    return tuple(sorted(ids))


def _finding_sort_key(finding: OrchestrationEvaluationReplayFinding) -> tuple[str, str, str, str]:
    return (finding.packet_id, finding.trace_id, finding.classification, finding.reason)
