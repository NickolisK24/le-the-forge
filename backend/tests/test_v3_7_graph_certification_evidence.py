from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
    count_v3_7_graph_certification_findings_by_classification,
    export_v3_7_graph_certification_finding_records,
)
from app.runtime_orchestration.v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_CLASSIFICATIONS,
    V37_CERTIFICATION_OUTCOME_CERTIFIED,
)


def test_certification_evidence_preserves_all_reference_classes():
    certification = build_v3_7_graph_planning_continuity_certification()
    evidence = certification.evidence

    assert certification.certification_outcome == V37_CERTIFICATION_OUTCOME_CERTIFIED
    assert evidence.graph_evidence_references
    assert evidence.governance_evidence_references
    assert evidence.compatibility_evidence_references
    assert evidence.evaluation_evidence_references
    assert evidence.session_evidence_references
    assert evidence.scenario_evidence_references
    assert evidence.aggregation_evidence_references
    assert evidence.integrity_evidence_references
    assert evidence.continuity_hashes
    assert evidence.provenance_references
    assert evidence.explainability_references
    assert evidence.replay_references
    assert evidence.rollback_references
    assert evidence.execution_boundary_references
    assert evidence.non_executable_evidence is True
    assert evidence.execution_authorization is False
    assert evidence.runtime_readiness_certification is False


def test_certification_findings_are_fail_visible_and_complete():
    certification = build_v3_7_graph_planning_continuity_certification()
    counts = count_v3_7_graph_certification_findings_by_classification(certification.findings)

    assert tuple(counts.keys()) == V37_CERTIFICATION_FINDING_CLASSIFICATIONS
    assert all(count == 1 for count in counts.values())
    assert all(finding.fail_visible and not finding.hidden for finding in certification.findings)
    assert all(not finding.execution_authorization for finding in certification.findings)
    assert all(not finding.runtime_readiness_certification for finding in certification.findings)


def test_certification_finding_records_are_sorted():
    certification = build_v3_7_graph_planning_continuity_certification()
    records = export_v3_7_graph_certification_finding_records(tuple(reversed(certification.findings)))

    assert [record["finding_id"] for record in records] == sorted(record["finding_id"] for record in records)
