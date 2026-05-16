from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from app.runtime_orchestration.v3_7_graph_integrity_findings import (
    count_v3_7_graph_integrity_findings_by_classification,
    export_v3_7_graph_integrity_finding_classifications,
    export_v3_7_graph_integrity_finding_records,
)
from app.runtime_orchestration.v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_BLOCKED,
    V37_INTEGRITY_FINDING_CLASSIFICATIONS,
    V37_INTEGRITY_FINDING_WARNING,
)


def test_integrity_finding_classifications_are_exported_deterministically():
    assert export_v3_7_graph_integrity_finding_classifications() == list(V37_INTEGRITY_FINDING_CLASSIFICATIONS)


def test_integrity_findings_are_fail_visible_and_complete():
    result = enforce_v3_7_graph_planning_integrity()
    counts = count_v3_7_graph_integrity_findings_by_classification(result.findings)

    assert all(count == 1 for count in counts.values())
    assert all(finding.fail_visible and not finding.hidden for finding in result.findings)
    assert any(finding.finding_classification == V37_INTEGRITY_FINDING_BLOCKED for finding in result.findings)
    assert any(finding.finding_classification == V37_INTEGRITY_FINDING_WARNING for finding in result.findings)


def test_integrity_finding_records_are_sorted():
    result = enforce_v3_7_graph_planning_integrity()
    records = export_v3_7_graph_integrity_finding_records(tuple(reversed(result.findings)))

    assert [record["finding_id"] for record in records] == sorted(record["finding_id"] for record in records)
