from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
)
from app.runtime_orchestration.v3_7_graph_certification_provenance import (
    V37_GRAPH_CERTIFICATION_PROVENANCE_BLOCKED,
    V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_certification_provenance,
    hash_v3_7_graph_certification_provenance_result,
    serialize_v3_7_graph_certification_provenance_result,
)


def test_certification_provenance_preserves_all_layers():
    result = audit_v3_7_graph_certification_provenance()

    assert result.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED
    assert result.certification_provenance_preserved is True
    assert result.scope_provenance_preserved is True
    assert result.graph_provenance_preserved is True
    assert result.governance_provenance_preserved is True
    assert result.compatibility_provenance_preserved is True
    assert result.evaluation_provenance_preserved is True
    assert result.session_provenance_preserved is True
    assert result.scenario_provenance_preserved is True
    assert result.aggregation_provenance_preserved is True
    assert result.integrity_provenance_preserved is True
    assert result.execution_boundary_provenance_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_certification_provenance_result(result)
    assert serialize_v3_7_graph_certification_provenance_result(result) == serialize_v3_7_graph_certification_provenance_result(result)


def test_certification_provenance_detects_replay_provenance_gap():
    certification = build_v3_7_graph_planning_continuity_certification()
    broken_replay = replace(certification.replay_evidence[0], provenance_references=())
    result = audit_v3_7_graph_certification_provenance(replace(certification, replay_evidence=(broken_replay,)))

    assert result.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_BLOCKED
    assert result.replay_provenance_preserved is False
