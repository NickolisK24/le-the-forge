from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import (
    build_v3_7_graph_intelligence_identity,
    build_v3_7_graph_planning_intelligence_aggregation,
    graph_intelligence_identities_are_unique,
    graph_intelligence_identity_key,
)


def test_aggregation_identity_is_stable():
    identity = build_v3_7_graph_intelligence_identity("graph-a")

    assert identity.aggregation_id == "v3_7_graph_planning_intelligence_aggregation_default"
    assert identity.phase_id == "v3_7_graph_planning_intelligence_aggregation"
    assert identity.aggregation_version == "v3.7"
    assert identity.stable_identity_key == graph_intelligence_identity_key(identity)
    assert graph_intelligence_identities_are_unique((identity, build_v3_7_graph_intelligence_identity("graph-b"))) is True
    assert graph_intelligence_identities_are_unique((identity, identity)) is False


def test_aggregation_sources_cover_all_required_layers():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    source_types = {source.source_type for source in aggregation.evidence_sources}

    assert source_types == {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
    }
    assert all(source.source_hash for source in aggregation.evidence_sources)
    assert all(source.provenance_references for source in aggregation.evidence_sources)
    assert all(source.explainability_references for source in aggregation.evidence_sources)
    assert all(source.continuity_references for source in aggregation.evidence_sources)


def test_aggregation_totals_summarize_existing_evidence():
    totals = build_v3_7_graph_planning_intelligence_aggregation().totals

    assert totals.governance_finding_total == 4
    assert totals.compatibility_finding_total == 7
    assert totals.evaluation_finding_total == 9
    assert totals.session_finding_total == 6
    assert totals.scenario_finding_total == 14
    assert totals.blocked_visibility_total == 2
    assert totals.prohibited_visibility_total == 9
    assert totals.unsupported_visibility_total == 9
    assert totals.unknown_visibility_total == 7
