from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_governance_provenance import (
    V37_GOVERNANCE_PROVENANCE_BLOCKED,
    V37_GOVERNANCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_governance_provenance,
    collect_v3_7_graph_governance_provenance,
    hash_v3_7_graph_governance_provenance_result,
    serialize_v3_7_graph_governance_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import build_v3_7_graph_governance_map
from app.runtime_orchestration.v3_7_graph_models import V37GraphProvenance


def test_governance_provenance_preserves_replay_and_rollback_continuity():
    governance_map = build_v3_7_graph_governance_map()
    first = audit_v3_7_graph_governance_provenance(governance_map)
    second = audit_v3_7_graph_governance_provenance(governance_map)

    assert first.provenance_status == V37_GOVERNANCE_PROVENANCE_PRESERVED
    assert first.domain_provenance_preserved is True
    assert first.rule_provenance_preserved is True
    assert first.node_classification_provenance_preserved is True
    assert first.edge_classification_provenance_preserved is True
    assert first.governance_continuity_preserved is True
    assert first.compatibility_continuity_preserved is True
    assert first.explainability_continuity_preserved is True
    assert first.replay_continuity_preserved is True
    assert first.rollback_continuity_preserved is True
    assert first.provenance_record_count == len(collect_v3_7_graph_governance_provenance(governance_map))
    assert first.deterministic_provenance_hash == second.deterministic_provenance_hash
    assert serialize_v3_7_graph_governance_provenance_result(first) == (
        serialize_v3_7_graph_governance_provenance_result(second)
    )
    assert hash_v3_7_graph_governance_provenance_result(first) == (
        hash_v3_7_graph_governance_provenance_result(second)
    )


def test_missing_rule_provenance_is_fail_visible():
    governance_map = build_v3_7_graph_governance_map()
    broken_provenance = V37GraphProvenance(
        provenance_id="broken-rule-provenance",
        source_phase_id="v3_7_graph_governance_boundary_intelligence",
        source_artifact_id=governance_map.rules[0].rule_id,
        source_kind="graph_governance_rule",
        lineage_references=(),
        replay_lineage_references=(),
        rollback_lineage_references=(),
        governance_references=(),
        compatibility_references=(),
        explainability_references=(),
    )
    broken_rule = replace(governance_map.rules[0], provenance=broken_provenance)
    result = audit_v3_7_graph_governance_provenance(
        replace(governance_map, rules=(broken_rule,) + governance_map.rules[1:])
    )

    assert result.provenance_status == V37_GOVERNANCE_PROVENANCE_BLOCKED
    assert result.rule_provenance_preserved is False
    assert result.replay_continuity_preserved is False
    assert result.rollback_continuity_preserved is False
    assert result.missing_provenance_subjects == (governance_map.rules[0].rule_id,)


def test_governance_provenance_records_cover_domains_rules_nodes_and_edges():
    governance_map = build_v3_7_graph_governance_map()
    records = collect_v3_7_graph_governance_provenance(governance_map)
    source_kinds = {record.source_kind for record in records}

    assert "graph_governance_domain" in source_kinds
    assert "graph_governance_rule" in source_kinds
    assert "node_governance_classification" in source_kinds
    assert "edge_governance_classification" in source_kinds
    assert len(records) == 19
