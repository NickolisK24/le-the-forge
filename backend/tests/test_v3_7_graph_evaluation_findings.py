from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_evaluation_findings import (
    build_v3_7_graph_evaluation_findings,
    count_v3_7_graph_evaluation_findings_by_classification,
    export_v3_7_graph_evaluation_finding_classifications,
)
from app.runtime_orchestration.v3_7_graph_evaluation_models import V37_EVALUATION_FINDING_CLASSIFICATIONS


def test_evaluation_findings_cover_all_required_classifications():
    findings = build_v3_7_graph_evaluation_findings()
    counts = count_v3_7_graph_evaluation_findings_by_classification(findings)

    assert export_v3_7_graph_evaluation_finding_classifications() == list(V37_EVALUATION_FINDING_CLASSIFICATIONS)
    assert set(counts) == set(V37_EVALUATION_FINDING_CLASSIFICATIONS)
    assert all(count == 1 for count in counts.values())


def test_prohibited_unsupported_and_unknown_findings_remain_fail_visible():
    findings = build_v3_7_graph_evaluation_findings()
    by_classification = {finding.finding_classification: finding for finding in findings}

    for classification in ("prohibited", "unsupported", "unknown"):
        finding = by_classification[classification]
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.reason
        assert finding.evidence_ids


def test_governance_and_compatibility_findings_preserve_evidence():
    findings = build_v3_7_graph_evaluation_findings()
    governance = next(finding for finding in findings if finding.finding_classification == "governance_restricted")
    compatibility = next(finding for finding in findings if finding.finding_classification == "compatibility_restricted")

    assert governance.governance_reference_ids
    assert governance.compatibility_reference_ids
    assert compatibility.compatibility_reference_ids
    assert compatibility.provenance.replay_lineage_references
    assert compatibility.provenance.rollback_lineage_references
