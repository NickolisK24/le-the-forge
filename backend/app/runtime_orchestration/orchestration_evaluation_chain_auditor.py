"""Deterministic v3.6 orchestration evaluation chain integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_chain_models import (
    CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP,
    CHAIN_AUDIT_STABLE,
    CHAIN_BLOCKER_VISIBILITY_GAP,
    CHAIN_CONTINUITY_GAP,
    CHAIN_CONTINUITY_PRESERVED,
    CHAIN_EXPLAINABILITY_GAP,
    CHAIN_GOVERNANCE_VISIBILITY_GAP,
    CHAIN_HASH_MISMATCH,
    CHAIN_INTEGRITY_GAP,
    CHAIN_INVALID,
    CHAIN_LINK_BLOCKER,
    CHAIN_LINK_COMPATIBILITY,
    CHAIN_LINK_EXPLAINABILITY,
    CHAIN_LINK_GOVERNANCE,
    CHAIN_LINK_INTEGRITY,
    CHAIN_LINK_INTENT,
    CHAIN_LINK_MAPPING,
    CHAIN_LINK_MISSING,
    CHAIN_LINK_POLICY,
    CHAIN_LINK_PREFLIGHT,
    CHAIN_LINK_PROVENANCE,
    CHAIN_LINK_REPLAY,
    CHAIN_LINK_REPLAY_SAFETY,
    CHAIN_LINK_RESOLUTION,
    CHAIN_LINK_ROLLBACK_SAFETY,
    CHAIN_LINK_TRACE,
    CHAIN_LINK_VALID,
    CHAIN_NON_EXECUTION_GAP,
    CHAIN_PROHIBITED_VISIBILITY_GAP,
    CHAIN_PROVENANCE_GAP,
    CHAIN_REPLAY_SAFETY_GAP,
    CHAIN_ROLLBACK_SAFETY_GAP,
    CHAIN_SOURCE_EVIDENCE_GAP,
    CHAIN_UNSUPPORTED_VISIBILITY_GAP,
    CHAIN_VALID,
    OrchestrationEvaluationChainAuditInput,
    OrchestrationEvaluationChainAuditRecord,
    OrchestrationEvaluationChainAuditResult,
    OrchestrationEvaluationChainFinding,
    OrchestrationEvaluationChainIdentifier,
    export_chain_audit_result,
    hash_chain_audit_record,
    hash_chain_audit_result,
    serialize_chain_audit_result,
)
from .orchestration_evaluation_replay_builder import build_orchestration_evaluation_replay_packets
from .orchestration_evaluation_replay_explainability import explain_orchestration_evaluation_replay_packets
from .orchestration_evaluation_replay_integrity import audit_orchestration_evaluation_replay_integrity
from .orchestration_evaluation_replay_models import (
    REPLAY_EXPLAINABILITY_STABLE,
    REPLAY_INTEGRITY_STABLE,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
    hash_replay_packet,
    hash_replay_registry,
)
from .orchestration_evaluation_replay_registry import default_orchestration_evaluation_replay_registry
from .orchestration_evaluation_trace_models import hash_trace_record, hash_trace_registry
from .orchestration_evaluation_trace_registry import (
    default_orchestration_evaluation_trace_registry,
    get_registered_trace_record,
)
from .orchestration_intent_models import hash_intent_record, hash_intent_registry
from .orchestration_intent_policy_mapping_models import hash_mapping_record, hash_mapping_registry
from .orchestration_intent_policy_mapping_registry import (
    default_orchestration_intent_policy_mapping_registry,
    get_registered_mapping_record,
)
from .orchestration_intent_registry import (
    default_orchestration_intent_registry,
    get_registered_intent_record,
)
from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_COMPATIBLE,
    hash_compatibility_registry,
    hash_compatibility_relationship,
)
from .orchestration_policy_compatibility_registry import (
    default_orchestration_policy_compatibility_registry,
    get_registered_compatibility_relationship,
)
from .orchestration_policy_models import hash_policy_definition, hash_policy_registry
from .orchestration_policy_registry import (
    default_orchestration_policy_registry,
    get_registered_policy,
)
from .orchestration_policy_resolution_models import hash_resolution_record, hash_resolution_registry
from .orchestration_policy_resolution_registry import (
    default_orchestration_policy_resolution_registry,
    get_registered_resolution_record_for_relationship,
)
from .orchestration_preflight_models import hash_preflight_record, hash_preflight_registry
from .orchestration_preflight_registry import (
    default_orchestration_preflight_registry,
    get_registered_preflight_record,
)


DEFAULT_CHAIN_AUDIT_ID = "v3_6_orchestration_evaluation_chain_integrity_audit"


def default_orchestration_evaluation_chain_audit_input() -> OrchestrationEvaluationChainAuditInput:
    replay_registry = default_orchestration_evaluation_replay_registry()
    replay_build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=replay_registry)
    )
    replay_explainability = explain_orchestration_evaluation_replay_packets(
        replay_registry,
        replay_build,
    )
    replay_integrity = audit_orchestration_evaluation_replay_integrity(
        OrchestrationEvaluationReplayIntegrityInput(
            replay_registry=replay_registry,
            build_result=replay_build,
            explainability_result=replay_explainability,
        )
    )
    return OrchestrationEvaluationChainAuditInput(
        policy_registry=default_orchestration_policy_registry(),
        compatibility_registry=default_orchestration_policy_compatibility_registry(),
        resolution_registry=default_orchestration_policy_resolution_registry(),
        intent_registry=default_orchestration_intent_registry(),
        mapping_registry=default_orchestration_intent_policy_mapping_registry(),
        preflight_registry=default_orchestration_preflight_registry(),
        trace_registry=default_orchestration_evaluation_trace_registry(),
        replay_registry=replay_registry,
        replay_build_result=replay_build,
        replay_explainability_result=replay_explainability,
        replay_integrity_result=replay_integrity,
    )


def audit_orchestration_evaluation_chain_integrity(
    audit_input: OrchestrationEvaluationChainAuditInput | None = None,
) -> OrchestrationEvaluationChainAuditResult:
    source = audit_input or default_orchestration_evaluation_chain_audit_input()
    source_hashes = _source_hashes(source)
    records = tuple(
        sorted(
            (_audit_packet(packet, source, source_hashes) for packet in source.replay_registry.packets),
            key=lambda item: item.identifier.chain_id,
        )
    )
    source_findings = _source_hash_findings(source, source_hashes)
    findings = tuple(
        sorted(
            tuple(
                finding
                for record in records
                for finding in record.findings
                if finding.classification != CHAIN_LINK_VALID
            )
            + source_findings,
            key=_finding_sort_key,
        )
    )
    status = CHAIN_AUDIT_STABLE if not findings else CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    result = OrchestrationEvaluationChainAuditResult(
        audit_id=DEFAULT_CHAIN_AUDIT_ID,
        chain_audit_status=status,
        planning_only=True,
        audit_records=records,
        audited_chain_count=len(records),
        valid_chain_count=sum(1 for record in records if record.chain_state == CHAIN_VALID),
        invalid_chain_count=sum(1 for record in records if record.chain_state == CHAIN_INVALID),
        policy_continuity_status=_continuity_status(records, CHAIN_LINK_POLICY),
        compatibility_continuity_status=_continuity_status(records, CHAIN_LINK_COMPATIBILITY),
        resolution_continuity_status=_continuity_status(records, CHAIN_LINK_RESOLUTION),
        intent_continuity_status=_continuity_status(records, CHAIN_LINK_INTENT),
        mapping_continuity_status=_continuity_status(records, CHAIN_LINK_MAPPING),
        preflight_continuity_status=_continuity_status(records, CHAIN_LINK_PREFLIGHT),
        trace_continuity_status=_continuity_status(records, CHAIN_LINK_TRACE),
        replay_continuity_status=_continuity_status(records, CHAIN_LINK_REPLAY),
        blocker_chain_continuity_status=_continuity_status(records, CHAIN_LINK_BLOCKER),
        governance_boundary_continuity_status=_continuity_status(records, CHAIN_LINK_GOVERNANCE),
        provenance_continuity_status=_continuity_status(records, CHAIN_LINK_PROVENANCE),
        explainability_continuity_status=_continuity_status(records, CHAIN_LINK_EXPLAINABILITY),
        integrity_continuity_status=_continuity_status(records, CHAIN_LINK_INTEGRITY),
        replay_safety_status=_continuity_status(records, CHAIN_LINK_REPLAY_SAFETY),
        rollback_safety_status=_continuity_status(records, CHAIN_LINK_ROLLBACK_SAFETY),
        finding_summary=findings,
        deterministic_source_hashes=source_hashes,
        deterministic_chain_audit_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_chain_audit_hash=hash_chain_audit_result(result))


def audit_orchestration_evaluation_chain(
    audit_input: OrchestrationEvaluationChainAuditInput | None = None,
) -> OrchestrationEvaluationChainAuditResult:
    return audit_orchestration_evaluation_chain_integrity(audit_input)


def export_orchestration_evaluation_chain_audit_result(
    result: OrchestrationEvaluationChainAuditResult,
) -> dict[str, object]:
    return export_chain_audit_result(result)


def serialize_orchestration_evaluation_chain_audit_result(
    result: OrchestrationEvaluationChainAuditResult,
) -> str:
    return serialize_chain_audit_result(result)


def hash_orchestration_evaluation_chain_audit_result(
    result: OrchestrationEvaluationChainAuditResult,
) -> str:
    return hash_chain_audit_result(result)


def _audit_packet(
    packet,
    source: OrchestrationEvaluationChainAuditInput,
    source_hashes: dict[str, str],
) -> OrchestrationEvaluationChainAuditRecord:
    chain_id = packet.identifier.packet_id.replace("v3_6.replay.", "v3_6.chain.")
    trace = get_registered_trace_record(source.trace_registry, packet.identifier.trace_id)
    preflight = get_registered_preflight_record(source.preflight_registry, packet.identifier.preflight_id)
    mapping = get_registered_mapping_record(source.mapping_registry, packet.identifier.mapping_id)
    intent = get_registered_intent_record(source.intent_registry, packet.identifier.intent_id)
    policies = tuple(
        policy
        for policy_id in packet.policy_ids
        for policy in (get_registered_policy(source.policy_registry, policy_id),)
        if policy is not None
    )
    compatibility_relationships = tuple(
        relationship
        for relationship_id in packet.provenance.compatibility_relationship_ids
        for relationship in (
            get_registered_compatibility_relationship(source.compatibility_registry, relationship_id),
        )
        if relationship is not None
    )
    resolutions = tuple(
        resolution
        for relationship_id in packet.provenance.compatibility_relationship_ids
        for resolution in (
            get_registered_resolution_record_for_relationship(source.resolution_registry, relationship_id),
        )
        if resolution is not None
    )
    link_continuity: dict[str, str] = {}
    findings: list[OrchestrationEvaluationChainFinding] = []

    def valid(link_type: str, reason: str, evidence_ids: tuple[str, ...]) -> None:
        link_continuity[link_type] = CHAIN_CONTINUITY_PRESERVED
        findings.append(_finding(chain_id, link_type, CHAIN_LINK_VALID, reason, evidence_ids))

    def gap(link_type: str, classification: str, reason: str, evidence_ids: tuple[str, ...]) -> None:
        link_continuity[link_type] = CHAIN_CONTINUITY_GAP
        findings.append(_finding(chain_id, link_type, classification, reason, evidence_ids))

    _audit_policy(packet, policies, valid, gap)
    _audit_compatibility(packet, compatibility_relationships, valid, gap)
    _audit_resolution(packet, compatibility_relationships, resolutions, valid, gap)
    _audit_intent(packet, intent, mapping, valid, gap)
    _audit_mapping(packet, mapping, intent, preflight, valid, gap)
    _audit_preflight(packet, preflight, trace, valid, gap)
    _audit_trace(packet, trace, valid, gap)
    _audit_replay(packet, source, valid, gap)
    _audit_blockers(packet, valid, gap)
    _audit_governance(packet, valid, gap)
    _audit_provenance(packet, valid, gap)
    _audit_explainability(packet, source, valid, gap)
    _audit_integrity(packet, source, valid, gap)
    _audit_replay_safety(packet, source, valid, gap)
    _audit_rollback_safety(packet, valid, gap)

    record_hashes = _record_hashes(
        packet,
        trace,
        preflight,
        mapping,
        intent,
        policies,
        compatibility_relationships,
        resolutions,
    )
    all_hashes = dict(sorted({**source_hashes, **record_hashes}.items()))
    state = CHAIN_VALID if all(finding.classification == CHAIN_LINK_VALID for finding in findings) else CHAIN_INVALID
    record = _record(
        chain_id=chain_id,
        packet=packet,
        state=state,
        source_hashes=all_hashes,
        link_continuity=link_continuity,
        findings=tuple(sorted(findings, key=_finding_sort_key)),
        resolutions=resolutions,
    )
    expected_hash = (
        source.expected_chain_hashes.get(chain_id)
        if source.expected_chain_hashes is not None
        else None
    )
    if expected_hash is not None and expected_hash != hash_chain_audit_record(record):
        findings.append(
            _finding(
                chain_id,
                CHAIN_LINK_INTEGRITY,
                CHAIN_HASH_MISMATCH,
                "evaluation chain audit record hash does not match expected deterministic hash",
                (hash_chain_audit_record(record), expected_hash),
            )
        )
        link_continuity[CHAIN_LINK_INTEGRITY] = CHAIN_CONTINUITY_GAP
        record = _record(
            chain_id=chain_id,
            packet=packet,
            state=CHAIN_INVALID,
            source_hashes=all_hashes,
            link_continuity=link_continuity,
            findings=tuple(sorted(findings, key=_finding_sort_key)),
            resolutions=resolutions,
        )
    return record


def _audit_policy(packet, policies, valid, gap) -> None:
    policy_ids = tuple(sorted(policy.identifier.policy_id for policy in policies))
    missing = tuple(sorted(set(packet.policy_ids) - set(policy_ids)))
    if packet.policy_ids and not missing:
        valid(CHAIN_LINK_POLICY, "all replay packet policy ids resolve to policy records", packet.policy_ids)
    else:
        gap(CHAIN_LINK_POLICY, CHAIN_LINK_MISSING, "policy chain has missing policy records", missing or (packet.identifier.packet_id,))


def _audit_compatibility(packet, relationships, valid, gap) -> None:
    expected = tuple(sorted(packet.provenance.compatibility_relationship_ids))
    actual = tuple(sorted(relationship.identifier.relationship_id for relationship in relationships))
    missing = tuple(sorted(set(expected) - set(actual)))
    if expected and not missing and (packet.compatibility_evidence or not packet.compatibility_domains):
        valid(CHAIN_LINK_COMPATIBILITY, "compatibility relationships are represented in replay evidence", expected)
    elif not expected and not packet.compatibility_domains:
        valid(CHAIN_LINK_COMPATIBILITY, "compatibility relationship is not required for this replay packet", (packet.identifier.packet_id,))
    else:
        gap(CHAIN_LINK_COMPATIBILITY, CHAIN_LINK_MISSING, "compatibility chain has missing relationship evidence", missing or expected or packet.compatibility_domains)


def _audit_resolution(packet, relationships, resolutions, valid, gap) -> None:
    expected = tuple(sorted(packet.provenance.compatibility_relationship_ids))
    actual = tuple(sorted(resolution.identifier.relationship_id for resolution in resolutions))
    missing = tuple(sorted(set(expected) - set(actual)))
    compatible_without_resolution = (
        expected
        and missing
        and len(resolutions) < len(expected)
        and all(
            relationship.compatibility_state == COMPATIBILITY_COMPATIBLE
            for relationship in relationships
            if relationship.identifier.relationship_id in missing
        )
    )
    if expected and not missing:
        valid(CHAIN_LINK_RESOLUTION, "compatibility relationships resolve to resolution audit records", tuple(sorted(resolution.identifier.resolution_id for resolution in resolutions)))
    elif expected and compatible_without_resolution:
        valid(CHAIN_LINK_RESOLUTION, "compatible relationships do not require blocked-state resolution records", expected)
    elif not expected and not packet.compatibility_domains:
        valid(CHAIN_LINK_RESOLUTION, "resolution record is not required for this replay packet", (packet.identifier.packet_id,))
    else:
        gap(CHAIN_LINK_RESOLUTION, CHAIN_LINK_MISSING, "resolution chain has missing resolution records", missing or expected or packet.compatibility_domains)


def _audit_intent(packet, intent, mapping, valid, gap) -> None:
    if intent is not None and intent.identifier.intent_id == packet.identifier.intent_id and packet.intent_evidence:
        valid(CHAIN_LINK_INTENT, "replay packet resolves to its intent evidence", (intent.identifier.intent_id,))
    else:
        gap(CHAIN_LINK_INTENT, CHAIN_LINK_MISSING, "intent chain has missing intent evidence", (packet.identifier.intent_id,))
    if mapping is not None and intent is not None and mapping.identifier.intent_id != intent.identifier.intent_id:
        gap(CHAIN_LINK_INTENT, CHAIN_SOURCE_EVIDENCE_GAP, "mapping intent does not match intent record", (mapping.identifier.mapping_id, intent.identifier.intent_id))


def _audit_mapping(packet, mapping, intent, preflight, valid, gap) -> None:
    intent_matches = intent is not None and mapping is not None and mapping.identifier.intent_id == intent.identifier.intent_id
    preflight_matches = preflight is not None and mapping is not None and preflight.identifier.mapping_id == mapping.identifier.mapping_id
    policy_matches = mapping is not None and set(packet.policy_ids).issubset(set(mapping.policy_ids))
    if mapping is not None and intent_matches and preflight_matches and policy_matches and packet.policy_mapping_evidence:
        valid(CHAIN_LINK_MAPPING, "intent-policy mapping links intent, policy, and preflight evidence", (mapping.identifier.mapping_id,))
    else:
        gap(CHAIN_LINK_MAPPING, CHAIN_LINK_MISSING, "mapping chain has missing or discontinuous mapping evidence", (packet.identifier.mapping_id,))


def _audit_preflight(packet, preflight, trace, valid, gap) -> None:
    trace_matches = trace is not None and preflight is not None and trace.identifier.preflight_id == preflight.identifier.preflight_id
    intent_matches = preflight is not None and preflight.identifier.intent_id == packet.identifier.intent_id
    if preflight is not None and trace_matches and intent_matches and packet.preflight_evidence:
        valid(CHAIN_LINK_PREFLIGHT, "preflight record links mapping and trace evidence", (preflight.identifier.preflight_id,))
    else:
        gap(CHAIN_LINK_PREFLIGHT, CHAIN_LINK_MISSING, "preflight chain has missing or discontinuous preflight evidence", (packet.identifier.preflight_id,))


def _audit_trace(packet, trace, valid, gap) -> None:
    if trace is not None and trace.identifier.trace_id == packet.identifier.trace_id and packet.trace_evidence:
        valid(CHAIN_LINK_TRACE, "trace evidence resolves to the replay packet trace", (trace.identifier.trace_id,))
    else:
        gap(CHAIN_LINK_TRACE, CHAIN_LINK_MISSING, "trace chain has missing trace evidence", (packet.identifier.trace_id,))


def _audit_replay(packet, source, valid, gap) -> None:
    build_record = next(
        (record for record in source.replay_build_result.build_records if record.packet_id == packet.identifier.packet_id),
        None,
    )
    if build_record is not None and build_record.trace_id == packet.identifier.trace_id:
        valid(CHAIN_LINK_REPLAY, "replay packet is represented by replay build evidence", (packet.identifier.packet_id,))
    else:
        gap(CHAIN_LINK_REPLAY, CHAIN_LINK_MISSING, "replay chain has missing replay build evidence", (packet.identifier.packet_id,))


def _audit_blockers(packet, valid, gap) -> None:
    failures: list[str] = []
    if packet.blocker_domains and not packet.blocker_evidence:
        failures.append("missing_blocker_evidence")
    if packet.unsupported_domains and not packet.unsupported_evidence:
        failures.append("missing_unsupported_evidence")
    if packet.prohibited_domains and not packet.prohibited_evidence:
        failures.append("missing_prohibited_evidence")
    if failures:
        gap(CHAIN_LINK_BLOCKER, CHAIN_BLOCKER_VISIBILITY_GAP, "blocker or unsupported/prohibited visibility is missing", tuple(sorted(failures)))
    else:
        valid(CHAIN_LINK_BLOCKER, "blocker, unsupported, and prohibited visibility is preserved", _visibility(packet))


def _audit_governance(packet, valid, gap) -> None:
    if packet.governance_boundaries and packet.governance_evidence and not _execution_enabled(packet):
        valid(CHAIN_LINK_GOVERNANCE, "governance boundaries remain visible and non-executing", packet.governance_boundaries)
    else:
        classification = CHAIN_NON_EXECUTION_GAP if _execution_enabled(packet) else CHAIN_GOVERNANCE_VISIBILITY_GAP
        gap(CHAIN_LINK_GOVERNANCE, classification, "governance boundary visibility or non-execution guarantee is missing", (packet.identifier.packet_id,))


def _audit_provenance(packet, valid, gap) -> None:
    provenance = packet.provenance
    evidence = (
        provenance.source_phase,
        provenance.source_artifact,
        provenance.packet_id,
        provenance.trace_id,
        provenance.preflight_id,
        provenance.intent_id,
        provenance.mapping_id,
        *provenance.replay_reference_ids,
        *provenance.rollback_reference_ids,
        *provenance.governance_reference_ids,
    )
    if all(evidence) and packet.provenance_evidence:
        valid(CHAIN_LINK_PROVENANCE, "provenance chain is preserved from intent through replay packet", tuple(sorted(evidence)))
    else:
        gap(CHAIN_LINK_PROVENANCE, CHAIN_PROVENANCE_GAP, "provenance chain has missing evidence", (packet.identifier.packet_id,))


def _audit_explainability(packet, source, valid, gap) -> None:
    explanation = next(
        (
            record
            for record in source.replay_explainability_result.explanation_records
            if record.packet_id == packet.identifier.packet_id
        ),
        None,
    )
    if (
        explanation is not None
        and packet.explainability_evidence
    ):
        valid(CHAIN_LINK_EXPLAINABILITY, "explainability evidence is preserved for the chain", (packet.identifier.packet_id,))
    else:
        gap(CHAIN_LINK_EXPLAINABILITY, CHAIN_EXPLAINABILITY_GAP, "explainability chain has missing visibility", (packet.identifier.packet_id,))


def _audit_integrity(packet, source, valid, gap) -> None:
    if packet.integrity_evidence and packet.identifier.packet_id:
        valid(CHAIN_LINK_INTEGRITY, "integrity evidence is preserved for the chain", (packet.identifier.packet_id,))
    else:
        gap(CHAIN_LINK_INTEGRITY, CHAIN_INTEGRITY_GAP, "integrity chain has missing or blocked evidence", (packet.identifier.packet_id,))


def _audit_replay_safety(packet, source, valid, gap) -> None:
    if (
        packet.provenance.replay_reference_ids
        and not packet.replay_execution_enabled
    ):
        valid(CHAIN_LINK_REPLAY_SAFETY, "replay safety references are preserved without replay execution", packet.provenance.replay_reference_ids)
    else:
        gap(CHAIN_LINK_REPLAY_SAFETY, CHAIN_REPLAY_SAFETY_GAP, "replay safety references are missing or execution is enabled", (packet.identifier.packet_id,))


def _audit_rollback_safety(packet, valid, gap) -> None:
    if packet.provenance.rollback_reference_ids and not packet.mutation_behavior_enabled and not packet.persistent_write_enabled:
        valid(CHAIN_LINK_ROLLBACK_SAFETY, "rollback safety references are preserved without mutation or persistent writes", packet.provenance.rollback_reference_ids)
    else:
        gap(CHAIN_LINK_ROLLBACK_SAFETY, CHAIN_ROLLBACK_SAFETY_GAP, "rollback safety references are missing or mutation is enabled", (packet.identifier.packet_id,))


def _source_hashes(source: OrchestrationEvaluationChainAuditInput) -> dict[str, str]:
    return dict(
        sorted(
            {
                "policy_registry": hash_policy_registry(source.policy_registry),
                "compatibility_registry": hash_compatibility_registry(source.compatibility_registry),
                "resolution_registry": hash_resolution_registry(source.resolution_registry),
                "intent_registry": hash_intent_registry(source.intent_registry),
                "mapping_registry": hash_mapping_registry(source.mapping_registry),
                "preflight_registry": hash_preflight_registry(source.preflight_registry),
                "trace_registry": hash_trace_registry(source.trace_registry),
                "replay_registry": hash_replay_registry(source.replay_registry),
                "replay_build": source.replay_build_result.deterministic_replay_build_hash,
                "replay_explainability": source.replay_explainability_result.deterministic_replay_explainability_hash,
                "replay_integrity": source.replay_integrity_result.deterministic_replay_integrity_hash,
            }.items()
        )
    )


def _record_hashes(packet, trace, preflight, mapping, intent, policies, relationships, resolutions) -> dict[str, str]:
    hashes = {"replay_packet": hash_replay_packet(packet)}
    if trace is not None:
        hashes["trace_record"] = hash_trace_record(trace)
    if preflight is not None:
        hashes["preflight_record"] = hash_preflight_record(preflight)
    if mapping is not None:
        hashes["mapping_record"] = hash_mapping_record(mapping)
    if intent is not None:
        hashes["intent_record"] = hash_intent_record(intent)
    for policy in policies:
        hashes[f"policy:{policy.identifier.policy_id}"] = hash_policy_definition(policy)
    for relationship in relationships:
        hashes[f"compatibility:{relationship.identifier.relationship_id}"] = hash_compatibility_relationship(relationship)
    for resolution in resolutions:
        hashes[f"resolution:{resolution.identifier.resolution_id}"] = hash_resolution_record(resolution)
    return dict(sorted(hashes.items()))


def _record(
    chain_id: str,
    packet,
    state: str,
    source_hashes: dict[str, str],
    link_continuity: dict[str, str],
    findings: tuple[OrchestrationEvaluationChainFinding, ...],
    resolutions,
) -> OrchestrationEvaluationChainAuditRecord:
    return OrchestrationEvaluationChainAuditRecord(
        identifier=OrchestrationEvaluationChainIdentifier(
            chain_id=chain_id,
            packet_id=packet.identifier.packet_id,
            trace_id=packet.identifier.trace_id,
            preflight_id=packet.identifier.preflight_id,
            mapping_id=packet.identifier.mapping_id,
            intent_id=packet.identifier.intent_id,
            namespace="v3_6.orchestration_evaluation_chain_integrity",
            version="1",
        ),
        chain_state=state,
        policy_ids=packet.policy_ids,
        compatibility_relationship_ids=packet.provenance.compatibility_relationship_ids,
        resolution_ids=tuple(sorted(resolution.identifier.resolution_id for resolution in resolutions)),
        governance_boundaries=packet.governance_boundaries,
        compatibility_domains=packet.compatibility_domains,
        dependency_domains=packet.dependency_domains,
        blocker_domains=packet.blocker_domains,
        unsupported_domains=packet.unsupported_domains,
        prohibited_domains=packet.prohibited_domains,
        supported_domains=packet.supported_domains,
        source_hashes=source_hashes,
        link_continuity=dict(sorted(link_continuity.items())),
        provenance_evidence=tuple(sorted(evidence.evidence_id for evidence in packet.provenance_evidence)),
        explainability_evidence=tuple(sorted(evidence.evidence_id for evidence in packet.explainability_evidence)),
        integrity_evidence=tuple(sorted(evidence.evidence_id for evidence in packet.integrity_evidence)),
        blocker_visibility=tuple(sorted(evidence.evidence_id for evidence in packet.blocker_evidence)),
        governance_visibility=tuple(sorted(evidence.evidence_id for evidence in packet.governance_evidence)),
        compatibility_visibility=tuple(sorted(evidence.evidence_id for evidence in packet.compatibility_evidence)),
        dependency_visibility=tuple(sorted(evidence.evidence_id for evidence in packet.dependency_evidence)),
        replay_visibility=tuple(sorted(packet.provenance.replay_reference_ids)),
        rollback_visibility=tuple(sorted(packet.provenance.rollback_reference_ids)),
        findings=findings,
        replay_safe=bool(packet.provenance.replay_reference_ids and not packet.replay_execution_enabled),
        rollback_safe=bool(packet.provenance.rollback_reference_ids and not packet.mutation_behavior_enabled),
    )


def _source_hash_findings(
    source: OrchestrationEvaluationChainAuditInput,
    source_hashes: dict[str, str],
) -> tuple[OrchestrationEvaluationChainFinding, ...]:
    expected = source.expected_source_hashes or {}
    return tuple(
        sorted(
            (
                _finding(
                    "v3_6.chain.source",
                    CHAIN_LINK_INTEGRITY,
                    CHAIN_HASH_MISMATCH,
                    f"{key} source hash does not match expected deterministic hash",
                    (source_hashes[key], expected_hash),
                )
                for key, expected_hash in expected.items()
                if source_hashes.get(key) != expected_hash
            ),
            key=_finding_sort_key,
        )
    )


def _visibility(packet) -> tuple[str, ...]:
    return tuple(
        sorted(
            (
                *packet.blocker_domains,
                *packet.unsupported_domains,
                *packet.prohibited_domains,
                *(evidence.evidence_id for evidence in packet.blocker_evidence),
                *(evidence.evidence_id for evidence in packet.unsupported_evidence),
                *(evidence.evidence_id for evidence in packet.prohibited_evidence),
            )
        )
    ) or (packet.identifier.packet_id,)


def _execution_enabled(packet) -> bool:
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


def _continuity_status(records: tuple[OrchestrationEvaluationChainAuditRecord, ...], link_type: str) -> str:
    return (
        CHAIN_CONTINUITY_PRESERVED
        if all(record.link_continuity.get(link_type) == CHAIN_CONTINUITY_PRESERVED for record in records)
        else CHAIN_CONTINUITY_GAP
    )


def _finding(
    chain_id: str,
    link_type: str,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationEvaluationChainFinding:
    return OrchestrationEvaluationChainFinding(
        chain_id=chain_id,
        link_type=link_type,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(str(item) for item in evidence_ids)),
    )


def _summary(status: str, findings: tuple[OrchestrationEvaluationChainFinding, ...]) -> str:
    if status == CHAIN_AUDIT_STABLE:
        return (
            "The deterministic evaluation chain is stable from intent through policy mapping, "
            "compatibility, resolution, preflight, trace, and replay packet evidence."
        )
    failures = tuple(sorted(f"{finding.chain_id}:{finding.link_type}:{finding.classification}" for finding in findings))
    return f"The deterministic evaluation chain has fail-visible continuity findings: {', '.join(failures)}."


def _finding_sort_key(finding: OrchestrationEvaluationChainFinding) -> tuple[str, str, str, str]:
    return (finding.chain_id, finding.link_type, finding.classification, finding.reason)
