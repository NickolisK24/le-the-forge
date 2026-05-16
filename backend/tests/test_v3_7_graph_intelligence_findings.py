from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_findings import (
    count_v3_7_graph_intelligence_findings_by_classification,
    export_v3_7_graph_intelligence_finding_classifications,
    export_v3_7_graph_intelligence_finding_records,
)


def test_aggregated_findings_are_stable_and_fail_visible():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    counts = count_v3_7_graph_intelligence_findings_by_classification(aggregation.findings)

    assert len(aggregation.findings) == 15
    assert all(count == 1 for count in counts.values())
    assert all(finding.fail_visible and not finding.hidden for finding in aggregation.findings)
    assert all(not finding.execution_recommendation for finding in aggregation.findings)
    assert all(not finding.runtime_path_selection for finding in aggregation.findings)


def test_aggregated_finding_exports_are_deterministic():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    first = export_v3_7_graph_intelligence_finding_records(aggregation.findings)
    second = export_v3_7_graph_intelligence_finding_records(tuple(reversed(aggregation.findings)))

    assert first == second
    assert len(export_v3_7_graph_intelligence_finding_classifications()) == 15
    assert first[0]["fail_visible"] is True
