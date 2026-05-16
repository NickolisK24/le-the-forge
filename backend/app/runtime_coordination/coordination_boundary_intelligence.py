"""Deterministic v3.8 coordination boundary intelligence audit logic."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_boundary_models import (
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SUPPORTED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATIONS,
    BOUNDARY_SEVERITY_BLOCKED,
    BOUNDARY_SEVERITY_INFO,
    BOUNDARY_SEVERITY_WARNING,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
    BOUNDARY_VISIBILITY_VISIBLE,
    V3_8_BOUNDARY_AUDIT_BLOCKED,
    V3_8_BOUNDARY_AUDIT_STABLE,
    V38CoordinationBoundaryAudit,
    V38CoordinationBoundaryEvidence,
    V38CoordinationBoundaryFinding,
    V38CoordinationBoundaryIdentity,
    V38CoordinationBoundaryRecord,
    boundary_finding_id,
    export_v3_8_boundary_audit,
    hash_v3_8_boundary_audit,
)
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation


def audit_v3_8_coordination_boundary_intelligence(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationBoundaryAudit:
    source = foundation or default_v3_8_coordination_foundation()
    records = _build_boundary_records(source)
    findings = tuple(_finding_from_record(record) for record in records)
    classification_counts = _count_classifications(records)
    execution_boundary_violation_count = _execution_boundary_violation_count(source, records, findings)
    validation_totals = {
        "boundary_count": len(records),
        "finding_count": len(findings),
        "supported_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_SUPPORTED],
        "unsupported_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_UNSUPPORTED],
        "prohibited_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_PROHIBITED],
        "unknown_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_UNKNOWN],
        "experimental_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_EXPERIMENTAL],
        "planning_only_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_PLANNING_ONLY],
        "non_executable_boundary_count": classification_counts[BOUNDARY_CLASSIFICATION_NON_EXECUTABLE],
        "fail_visible_unsupported_count": _visible_count(records, BOUNDARY_CLASSIFICATION_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(records, BOUNDARY_CLASSIFICATION_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(records, BOUNDARY_CLASSIFICATION_UNKNOWN),
        "supported_hidden_risk_count": sum(
            1 for record in records if record.classification == BOUNDARY_CLASSIFICATION_SUPPORTED and record.supported_risk_hidden
        ),
        "replay_safe_evidence_count": sum(1 for record in records if record.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for record in records if record.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for record in records if record.evidence.provenance_preserved),
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "non_executable_finding_count": sum(1 for finding in findings if finding.non_execution_confirmation),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
        "blocking_finding_count": sum(1 for finding in findings if finding.blocks_boundary_intelligence),
        "valid": execution_boundary_violation_count == 0 and all(finding.fail_visible and not finding.hidden for finding in findings),
    }
    audit = V38CoordinationBoundaryAudit(
        audit_id="v3_8_coordination_boundary_intelligence_audit",
        audit_status=V3_8_BOUNDARY_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_BOUNDARY_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        boundary_records=records,
        findings=findings,
        classification_counts=classification_counts,
        validation_totals=validation_totals,
        non_executable=True,
        coordination_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_enabled=False,
        scheduling_enabled=False,
        dispatch_enabled=False,
        traversal_execution_enabled=False,
        optimization_enabled=False,
        recommendation_enabled=False,
        execution_authorization_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_boundary_hash=hash_v3_8_boundary_audit(audit))


def export_v3_8_coordination_boundary_intelligence_audit(
    audit: V38CoordinationBoundaryAudit,
) -> dict[str, object]:
    return export_v3_8_boundary_audit(audit)


def count_v3_8_boundary_classifications(
    records: tuple[V38CoordinationBoundaryRecord, ...],
) -> dict[str, int]:
    return _count_classifications(records)


def _build_boundary_records(
    foundation: V38CoordinationFoundation,
) -> tuple[V38CoordinationBoundaryRecord, ...]:
    records: list[V38CoordinationBoundaryRecord] = []
    replay_reference = foundation.replay_evidence[0].replay_evidence_id
    rollback_reference = foundation.rollback_evidence[0].rollback_evidence_id
    provenance_reference = foundation.provenance_state.provenance_id
    continuity_reference = foundation.continuity_state.continuity_id
    for boundary in foundation.coordination_boundaries:
        records.append(
            _record(
                boundary_id=boundary.boundary_id,
                source_id=boundary.boundary_id,
                source_type="coordination_boundary",
                classification=BOUNDARY_CLASSIFICATION_SUPPORTED,
                severity=BOUNDARY_SEVERITY_INFO,
                visibility=BOUNDARY_VISIBILITY_VISIBLE,
                explanation=f"coordination boundary {boundary.boundary_id} is supported as deterministic audit evidence",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            )
        )
    for state in foundation.unsupported_states:
        records.append(
            _record(
                boundary_id=state.state_id,
                source_id=state.state_id,
                source_type="unsupported_state",
                classification=BOUNDARY_CLASSIFICATION_UNSUPPORTED,
                severity=BOUNDARY_SEVERITY_WARNING,
                visibility=BOUNDARY_VISIBILITY_FAIL_VISIBLE,
                explanation=f"unsupported coordination state remains fail-visible: {state.reason}",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=state.provenance_reference_ids[0],
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            )
        )
    for state in foundation.prohibited_states:
        records.append(
            _record(
                boundary_id=state.state_id,
                source_id=state.state_id,
                source_type="prohibited_state",
                classification=BOUNDARY_CLASSIFICATION_PROHIBITED,
                severity=BOUNDARY_SEVERITY_BLOCKED,
                visibility=BOUNDARY_VISIBILITY_FAIL_VISIBLE,
                explanation=f"prohibited coordination state is intentionally blocked: {state.reason}",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=state.provenance_reference_ids[0],
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            )
        )
    for state in foundation.unknown_states:
        records.append(
            _record(
                boundary_id=state.state_id,
                source_id=state.state_id,
                source_type="unknown_state",
                classification=BOUNDARY_CLASSIFICATION_UNKNOWN,
                severity=BOUNDARY_SEVERITY_WARNING,
                visibility=BOUNDARY_VISIBILITY_FAIL_VISIBLE,
                explanation=f"unknown coordination state lacks deterministic support evidence: {state.reason}",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=state.provenance_reference_ids[0],
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            )
        )
    records.extend(
        (
            _record(
                boundary_id="v3_8_boundary_experimental_audit_only",
                source_id=foundation.identity.coordination_id,
                source_type="coordination_boundary_intelligence_phase",
                classification=BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
                severity=BOUNDARY_SEVERITY_INFO,
                visibility=BOUNDARY_VISIBILITY_VISIBLE,
                explanation="boundary intelligence is experimental audit evidence only and does not enable runtime capability",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                replay_reference=foundation.replay_evidence[1].replay_evidence_id,
                rollback_reference=foundation.rollback_evidence[1].rollback_evidence_id,
                deterministic_hash_reference="v3_8_boundary_intelligence_hash",
            ),
            _record(
                boundary_id="v3_8_boundary_planning_only_coordination",
                source_id=foundation.identity.coordination_id,
                source_type="coordination_foundation",
                classification=BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
                severity=BOUNDARY_SEVERITY_INFO,
                visibility=BOUNDARY_VISIBILITY_VISIBLE,
                explanation="coordination structures are planning-only evidence and do not select runtime paths",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            ),
            _record(
                boundary_id="v3_8_boundary_non_executable_coordination",
                source_id=foundation.identity.coordination_id,
                source_type="coordination_foundation",
                classification=BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
                severity=BOUNDARY_SEVERITY_INFO,
                visibility=BOUNDARY_VISIBILITY_VISIBLE,
                explanation="coordination boundary intelligence remains non-executable",
                source_reference=foundation.identity.coordination_id,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                replay_reference=replay_reference,
                rollback_reference=rollback_reference,
                deterministic_hash_reference="v3_8_coordination_foundation_hash",
            ),
        )
    )
    return tuple(sorted(records, key=lambda item: (item.classification, item.identity.boundary_id)))


def _record(
    *,
    boundary_id: str,
    source_id: str,
    source_type: str,
    classification: str,
    severity: str,
    visibility: str,
    explanation: str,
    source_reference: str,
    provenance_reference: str,
    continuity_reference: str,
    replay_reference: str,
    rollback_reference: str,
    deterministic_hash_reference: str,
) -> V38CoordinationBoundaryRecord:
    evidence = V38CoordinationBoundaryEvidence(
        evidence_id=f"evidence_{boundary_id}",
        source_coordination_reference=source_reference,
        provenance_reference=provenance_reference,
        continuity_reference=continuity_reference,
        replay_evidence_reference=replay_reference,
        rollback_evidence_reference=rollback_reference,
        deterministic_hash_reference=deterministic_hash_reference,
    )
    return V38CoordinationBoundaryRecord(
        identity=V38CoordinationBoundaryIdentity(
            boundary_id=boundary_id,
            boundary_source_id=source_id,
            boundary_source_type=source_type,
        ),
        classification=classification,
        severity=severity,
        visibility_status=visibility,
        explanation=explanation,
        evidence=evidence,
        provenance_reference_ids=(provenance_reference,),
        continuity_reference_ids=(continuity_reference,),
        replay_reference_ids=(replay_reference,),
        rollback_reference_ids=(rollback_reference,),
        supported_risk_hidden=False,
        fail_visible=True,
        hidden=False,
        non_executable=True,
        execution_capability_enabled=False,
    )


def _finding_from_record(record: V38CoordinationBoundaryRecord) -> V38CoordinationBoundaryFinding:
    blocks = record.execution_capability_enabled or not record.non_executable or record.hidden
    return V38CoordinationBoundaryFinding(
        finding_id=boundary_finding_id(record.classification, record.identity.boundary_id),
        source_coordination_reference=record.evidence.source_coordination_reference,
        boundary_id=record.identity.boundary_id,
        boundary_classification=record.classification,
        severity=record.severity,
        explanation=record.explanation,
        provenance_reference=record.evidence.provenance_reference,
        replay_safe_evidence=(record.evidence.replay_evidence_reference,),
        rollback_safe_evidence=(record.evidence.rollback_evidence_reference,),
        deterministic_visibility_status=record.visibility_status,
        non_execution_confirmation=record.non_executable and not record.execution_capability_enabled,
        fail_visible=record.fail_visible,
        hidden=record.hidden,
        blocks_boundary_intelligence=blocks,
        execution_behavior_detected=record.execution_capability_enabled,
    )


def _count_classifications(records: tuple[V38CoordinationBoundaryRecord, ...]) -> dict[str, int]:
    counts = Counter(record.classification for record in records)
    return {classification: counts.get(classification, 0) for classification in BOUNDARY_CLASSIFICATIONS}


def _visible_count(records: tuple[V38CoordinationBoundaryRecord, ...], classification: str) -> int:
    return sum(
        1
        for record in records
        if record.classification == classification and record.fail_visible and not record.hidden
    )


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    records: tuple[V38CoordinationBoundaryRecord, ...],
    findings: tuple[V38CoordinationBoundaryFinding, ...],
) -> int:
    foundation_flags = (
        foundation.coordination_execution_enabled,
        foundation.orchestration_execution_enabled,
        foundation.execution_authorization_enabled,
        foundation.routing_enabled,
        foundation.scheduling_enabled,
        foundation.dispatch_enabled,
        foundation.traversal_execution_enabled,
        foundation.graph_traversal_execution_enabled,
        foundation.runtime_path_selection_enabled,
        foundation.recommendation_enabled,
        foundation.optimization_enabled,
        foundation.autonomous_orchestration_enabled,
        foundation.callable_execution_flow_enabled,
        foundation.persistent_runtime_mutation_enabled,
        foundation.persistent_runtime_writes_enabled,
        foundation.hidden_state_transition_enabled,
        foundation.silent_fallback_enabled,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for record in records if record.execution_capability_enabled or not record.non_executable)
        + sum(1 for finding in findings if finding.execution_behavior_detected)
    )

