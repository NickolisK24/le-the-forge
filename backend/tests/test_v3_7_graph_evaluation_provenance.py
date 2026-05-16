from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_evaluation_provenance import (
    V37_GRAPH_EVALUATION_PROVENANCE_BLOCKED,
    V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_evaluation_provenance,
    hash_v3_7_graph_evaluation_provenance_result,
    serialize_v3_7_graph_evaluation_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def test_evaluation_provenance_is_preserved_for_chain_steps_findings_and_replay():
    chain = build_v3_7_graph_evaluation_chain()
    result = audit_v3_7_graph_evaluation_provenance(chain)

    assert result.provenance_status == V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED
    assert result.chain_provenance_preserved is True
    assert result.step_provenance_preserved is True
    assert result.finding_provenance_preserved is True
    assert result.trace_provenance_preserved is True
    assert result.replay_provenance_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_evaluation_provenance_result(result)


def test_evaluation_provenance_serialization_is_deterministic():
    result = audit_v3_7_graph_evaluation_provenance()

    assert serialize_v3_7_graph_evaluation_provenance_result(result) == serialize_v3_7_graph_evaluation_provenance_result(result)


def test_evaluation_provenance_detects_missing_lineage():
    chain = build_v3_7_graph_evaluation_chain()
    broken_provenance = replace(chain.steps[0].provenance, replay_lineage_references=())
    broken_step = replace(chain.steps[0], provenance=broken_provenance)
    result = audit_v3_7_graph_evaluation_provenance(replace(chain, steps=(broken_step,) + chain.steps[1:]))

    assert result.provenance_status == V37_GRAPH_EVALUATION_PROVENANCE_BLOCKED
    assert result.step_provenance_preserved is False
    assert broken_step.step_id in result.missing_provenance_subjects
