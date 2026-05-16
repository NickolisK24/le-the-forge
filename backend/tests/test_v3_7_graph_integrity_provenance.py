from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from app.runtime_orchestration.v3_7_graph_integrity_provenance import (
    V37_GRAPH_INTEGRITY_PROVENANCE_BLOCKED,
    V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_integrity_provenance,
    hash_v3_7_graph_integrity_provenance_result,
    serialize_v3_7_graph_integrity_provenance_result,
)


def test_integrity_provenance_preserves_all_layers():
    result = audit_v3_7_graph_integrity_provenance()

    assert result.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED
    assert result.enforcement_provenance_preserved is True
    assert result.policy_provenance_preserved is True
    assert result.graph_provenance_preserved is True
    assert result.governance_provenance_preserved is True
    assert result.compatibility_provenance_preserved is True
    assert result.evaluation_provenance_preserved is True
    assert result.session_provenance_preserved is True
    assert result.scenario_provenance_preserved is True
    assert result.aggregation_provenance_preserved is True
    assert result.replay_provenance_preserved is True
    assert result.rollback_provenance_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_integrity_provenance_result(result)
    assert serialize_v3_7_graph_integrity_provenance_result(result) == serialize_v3_7_graph_integrity_provenance_result(result)


def test_integrity_provenance_detects_replay_provenance_gap():
    enforcement = enforce_v3_7_graph_planning_integrity()
    broken_replay = replace(enforcement.replay_evidence[0], provenance_references=())
    result = audit_v3_7_graph_integrity_provenance(replace(enforcement, replay_evidence=(broken_replay,)))

    assert result.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_BLOCKED
    assert result.replay_provenance_preserved is False
