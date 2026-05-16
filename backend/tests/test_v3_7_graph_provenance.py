from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_models import (
    V37GraphProvenance,
    default_v3_7_orchestration_planning_graph,
)
from app.runtime_orchestration.v3_7_graph_provenance import (
    V37_PROVENANCE_CONTINUITY_BLOCKED,
    V37_PROVENANCE_CONTINUITY_PRESERVED,
    audit_v3_7_graph_provenance,
    collect_v3_7_graph_provenance,
    hash_v3_7_graph_provenance_result,
    serialize_v3_7_graph_provenance_result,
)


def test_default_graph_provenance_preserves_replay_and_rollback_continuity():
    graph = default_v3_7_orchestration_planning_graph()
    first = audit_v3_7_graph_provenance(graph)
    second = audit_v3_7_graph_provenance(graph)

    assert first.provenance_status == V37_PROVENANCE_CONTINUITY_PRESERVED
    assert first.graph_creation_provenance_preserved is True
    assert first.node_provenance_preserved is True
    assert first.edge_provenance_preserved is True
    assert first.governance_provenance_preserved is True
    assert first.compatibility_provenance_preserved is True
    assert first.explainability_provenance_preserved is True
    assert first.replay_continuity_preserved is True
    assert first.rollback_continuity_preserved is True
    assert first.provenance_record_count == len(collect_v3_7_graph_provenance(graph))
    assert first.deterministic_provenance_hash == second.deterministic_provenance_hash
    assert serialize_v3_7_graph_provenance_result(first) == serialize_v3_7_graph_provenance_result(second)
    assert hash_v3_7_graph_provenance_result(first) == hash_v3_7_graph_provenance_result(second)


def test_missing_node_provenance_is_fail_visible():
    graph = default_v3_7_orchestration_planning_graph()
    broken_provenance = V37GraphProvenance(
        provenance_id="broken-node-provenance",
        source_phase_id="v3_7_graph_foundations",
        source_artifact_id=graph.nodes[0].identity.node_id,
        source_kind="node",
        lineage_references=(),
        replay_lineage_references=(),
        rollback_lineage_references=(),
        governance_references=(),
        compatibility_references=(),
        explainability_references=(),
    )
    broken_node = replace(graph.nodes[0], provenance=broken_provenance)
    result = audit_v3_7_graph_provenance(replace(graph, nodes=(broken_node,) + graph.nodes[1:]))

    assert result.provenance_status == V37_PROVENANCE_CONTINUITY_BLOCKED
    assert result.node_provenance_preserved is False
    assert result.replay_continuity_preserved is False
    assert result.rollback_continuity_preserved is False
    assert result.missing_provenance_subjects == (graph.nodes[0].identity.node_id,)


def test_provenance_records_include_graph_node_edge_governance_compatibility_and_explainability():
    graph = default_v3_7_orchestration_planning_graph()
    records = collect_v3_7_graph_provenance(graph)
    source_kinds = {record.source_kind for record in records}

    assert "graph" in source_kinds
    assert "node" in source_kinds
    assert "edge" in source_kinds
    assert "governance_boundary" in source_kinds
    assert "compatibility_boundary" in source_kinds
    assert "explainability_evidence" in source_kinds
    assert len(records) == 14
