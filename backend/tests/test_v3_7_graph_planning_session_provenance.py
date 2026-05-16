from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_planning_session_provenance import (
    V37_GRAPH_PLANNING_SESSION_PROVENANCE_BLOCKED,
    V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_planning_session_provenance,
    hash_v3_7_graph_planning_session_provenance_result,
    serialize_v3_7_graph_planning_session_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


def test_session_provenance_preserves_all_required_chains():
    result = audit_v3_7_graph_planning_session_provenance()

    assert result.provenance_status == V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED
    assert result.session_creation_provenance_preserved is True
    assert result.graph_snapshot_provenance_preserved is True
    assert result.evaluation_provenance_preserved is True
    assert result.replay_provenance_preserved is True
    assert result.rollback_provenance_preserved is True
    assert result.audit_provenance_preserved is True
    assert result.explainability_provenance_preserved is True
    assert result.continuity_provenance_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_planning_session_provenance_result(result)


def test_session_provenance_serialization_is_deterministic():
    result = audit_v3_7_graph_planning_session_provenance()

    assert serialize_v3_7_graph_planning_session_provenance_result(result) == serialize_v3_7_graph_planning_session_provenance_result(result)


def test_session_provenance_detects_missing_session_lineage():
    session = build_v3_7_graph_planning_session()
    broken_provenance = replace(session.provenance, replay_lineage_references=())
    result = audit_v3_7_graph_planning_session_provenance(replace(session, provenance=broken_provenance))

    assert result.provenance_status == V37_GRAPH_PLANNING_SESSION_PROVENANCE_BLOCKED
    assert result.session_creation_provenance_preserved is False
    assert session.identity.session_id in result.missing_provenance_subjects
