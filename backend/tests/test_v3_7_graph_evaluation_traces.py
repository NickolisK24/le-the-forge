from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_evaluation_models import (
    V37_EVALUATION_STEP_COMPATIBILITY,
    V37_EVALUATION_STEP_CONTINUITY,
    V37_EVALUATION_STEP_GOVERNANCE,
    V37_EVALUATION_STEP_PROHIBITED,
    V37_EVALUATION_STEP_UNKNOWN,
    V37_EVALUATION_STEP_UNSUPPORTED,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def test_evaluation_ordering_is_deterministic_and_not_execution_ordering():
    chain = build_v3_7_graph_evaluation_chain()

    assert [step.step_order for step in chain.steps] == list(range(1, 10))
    assert [trace.trace_order for trace in chain.traces] == list(range(1, 10))
    assert chain.evaluation_ordering_does_not_imply_execution_ordering is True
    assert all(step.execution_ordering_enabled is False for step in chain.steps)


def test_evaluation_traces_preserve_structural_evidence_without_traversal():
    chain = build_v3_7_graph_evaluation_chain()
    step_ids = {step.step_id for step in chain.steps}

    assert {trace.step_id for trace in chain.traces} == step_ids
    assert all(trace.deterministic_ordering_key for trace in chain.traces)
    assert all(trace.evaluation_evidence_ids for trace in chain.traces)
    assert all(trace.provenance_evidence_ids for trace in chain.traces)
    assert all(trace.trace_implies_traversal is False for trace in chain.traces)
    assert all(trace.trace_authorizes_execution is False for trace in chain.traces)
    assert all(trace.trace_has_side_effects is False for trace in chain.traces)


def test_evaluation_steps_cover_required_structural_step_types():
    chain = build_v3_7_graph_evaluation_chain()
    step_types = {step.step_type for step in chain.steps}

    assert {
        V37_EVALUATION_STEP_COMPATIBILITY,
        V37_EVALUATION_STEP_GOVERNANCE,
        V37_EVALUATION_STEP_PROHIBITED,
        V37_EVALUATION_STEP_UNSUPPORTED,
        V37_EVALUATION_STEP_UNKNOWN,
        V37_EVALUATION_STEP_CONTINUITY,
    }.issubset(step_types)
