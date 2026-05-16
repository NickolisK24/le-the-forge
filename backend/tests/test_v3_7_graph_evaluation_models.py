from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_evaluation_findings import (
    count_v3_7_graph_evaluation_findings_by_classification,
)
from app.runtime_orchestration.v3_7_graph_evaluation_models import (
    V37_EVALUATION_FINDING_CLASSIFICATIONS,
    export_v3_7_graph_evaluation_counts,
    hash_v3_7_graph_evaluation_chain,
    serialize_v3_7_graph_evaluation_chain,
    validate_v3_7_graph_evaluation_hash_stability,
    validate_v3_7_graph_evaluation_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from scripts.report_v3_7_graph_evaluation_reasoning import build_v3_7_graph_evaluation_reasoning_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_evaluation_chain_is_immutable_and_non_executable():
    chain = build_v3_7_graph_evaluation_chain()

    with pytest.raises(FrozenInstanceError):
        chain.routing_enabled = True

    assert chain.evaluation_reasoning_is_non_executable is True
    assert chain.replay_packets_are_not_orchestration_packets is True
    assert chain.evaluation_traces_do_not_imply_traversal is True
    assert chain.evaluation_ordering_does_not_imply_execution_ordering is True
    assert chain.graph_evaluation_does_not_authorize_orchestration is True
    assert chain.graph_execution_enabled is False
    assert chain.traversal_execution_enabled is False
    assert chain.routing_enabled is False
    assert chain.scheduling_enabled is False
    assert chain.dispatch_enabled is False
    assert chain.path_selection_enabled is False


def test_evaluation_serialization_and_hash_are_deterministic():
    chain = build_v3_7_graph_evaluation_chain()
    reordered = replace(
        chain,
        steps=tuple(reversed(chain.steps)),
        traces=tuple(reversed(chain.traces)),
        findings=tuple(reversed(chain.findings)),
        continuity_evidence=tuple(reversed(chain.continuity_evidence)),
    )

    assert serialize_v3_7_graph_evaluation_chain(chain) == serialize_v3_7_graph_evaluation_chain(reordered)
    assert hash_v3_7_graph_evaluation_chain(chain) == hash_v3_7_graph_evaluation_chain(reordered)
    assert validate_v3_7_graph_evaluation_serialization_stability(chain)["stable"] is True
    assert validate_v3_7_graph_evaluation_hash_stability(chain)["stable"] is True
    assert json.loads(serialize_v3_7_graph_evaluation_chain(chain))["dispatch_enabled"] is False


def test_evaluation_counts_and_classifications_are_complete():
    chain = build_v3_7_graph_evaluation_chain()
    counts = count_v3_7_graph_evaluation_findings_by_classification(chain.findings)

    assert export_v3_7_graph_evaluation_counts(chain) == {
        "evaluation_chain_count": 1,
        "evaluation_step_count": 9,
        "evaluation_trace_count": 9,
        "evaluation_finding_count": 9,
        "continuity_evidence_count": 1,
    }
    assert set(counts) == set(V37_EVALUATION_FINDING_CLASSIFICATIONS)
    assert all(value == 1 for value in counts.values())
    assert chain.summary.fail_visible_finding_count == 9


def test_evaluation_report_generation_is_deterministic_and_non_executable():
    first = build_v3_7_graph_evaluation_reasoning_report(REPO_ROOT)
    second = build_v3_7_graph_evaluation_reasoning_report(REPO_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["evaluation_reasoning_is_non_executable"] is True
    assert first["replay_packets_are_not_orchestration_packets"] is True
    assert first["evaluation_traces_do_not_imply_traversal"] is True
    assert first["evaluation_ordering_does_not_imply_execution_ordering"] is True
    assert first["graph_evaluation_does_not_authorize_orchestration"] is True
    assert first["routing_enabled"] is False
    assert first["scheduling_enabled"] is False
    assert first["dispatch_enabled"] is False
    assert first["coverage"]["prohibited_visibility_coverage"] is True
    assert first["coverage"]["unsupported_visibility_coverage"] is True
    assert first["coverage"]["unknown_visibility_coverage"] is True
