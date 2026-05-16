from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_provenance import (
    V37_GRAPH_INTELLIGENCE_PROVENANCE_BLOCKED,
    V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_intelligence_provenance,
    collect_v3_7_graph_intelligence_provenance,
    hash_v3_7_graph_intelligence_provenance_result,
    serialize_v3_7_graph_intelligence_provenance_result,
)


def test_intelligence_provenance_is_preserved_for_all_sources():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    result = audit_v3_7_graph_intelligence_provenance(aggregation)

    assert result.provenance_status == V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED
    assert result.provenance_record_count == 1
    assert result.aggregation_creation_provenance_preserved is True
    assert result.graph_provenance_preserved is True
    assert result.governance_provenance_preserved is True
    assert result.compatibility_provenance_preserved is True
    assert result.evaluation_provenance_preserved is True
    assert result.session_provenance_preserved is True
    assert result.scenario_provenance_preserved is True
    assert result.replay_provenance_preserved is True
    assert result.rollback_provenance_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_intelligence_provenance_result(result)
    assert serialize_v3_7_graph_intelligence_provenance_result(result) == serialize_v3_7_graph_intelligence_provenance_result(result)
    assert len(collect_v3_7_graph_intelligence_provenance(aggregation)) == 1


def test_intelligence_provenance_detects_source_discontinuity():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    broken_source = replace(aggregation.evidence_sources[1], provenance_references=())
    result = audit_v3_7_graph_intelligence_provenance(
        replace(aggregation, evidence_sources=(aggregation.evidence_sources[0], broken_source) + aggregation.evidence_sources[2:])
    )

    assert result.provenance_status == V37_GRAPH_INTELLIGENCE_PROVENANCE_BLOCKED
    assert "governance_provenance" in result.missing_provenance_subjects
