from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_evaluation_models import (
    V37_EVALUATION_PROHIBITED,
    V37_EVALUATION_UNKNOWN,
    V37_EVALUATION_UNSUPPORTED,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from app.runtime_orchestration.v3_7_graph_evaluation_validation import (
    V37_GRAPH_EVALUATION_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_GRAPH_EVALUATION_BLOCKED_BY_HIDDEN_FINDING,
    V37_GRAPH_EVALUATION_BLOCKED_BY_ORDERING,
    V37_GRAPH_EVALUATION_VALIDATION_BLOCKED,
    V37_GRAPH_EVALUATION_VALIDATION_STABLE,
    validate_v3_7_graph_evaluation,
)


def test_default_evaluation_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_evaluation()

    assert result.validation_status == V37_GRAPH_EVALUATION_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 3
    assert result.prohibited_state_count == 1
    assert result.unsupported_state_count == 1
    assert result.unknown_state_count == 1
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True


def test_validation_detects_invalid_evaluation_ordering():
    chain = build_v3_7_graph_evaluation_chain()
    broken_step = replace(chain.steps[0], step_order=2)
    result = validate_v3_7_graph_evaluation(replace(chain, steps=(broken_step,) + chain.steps[1:]))

    assert result.validation_status == V37_GRAPH_EVALUATION_VALIDATION_BLOCKED
    assert any(finding.status == V37_GRAPH_EVALUATION_BLOCKED_BY_ORDERING for finding in result.findings)


def test_validation_detects_hidden_unsupported_unknown_or_prohibited_findings():
    chain = build_v3_7_graph_evaluation_chain()
    hidden = tuple(
        replace(finding, hidden=True)
        if finding.finding_classification in (V37_EVALUATION_PROHIBITED, V37_EVALUATION_UNSUPPORTED, V37_EVALUATION_UNKNOWN)
        else finding
        for finding in chain.findings
    )
    result = validate_v3_7_graph_evaluation(replace(chain, findings=hidden))

    assert result.validation_status == V37_GRAPH_EVALUATION_VALIDATION_BLOCKED
    assert any(finding.status == V37_GRAPH_EVALUATION_BLOCKED_BY_HIDDEN_FINDING for finding in result.findings)


def test_validation_detects_execution_capability_leak():
    chain = build_v3_7_graph_evaluation_chain()
    result = validate_v3_7_graph_evaluation(replace(chain, dispatch_enabled=True))

    assert result.validation_status == V37_GRAPH_EVALUATION_VALIDATION_BLOCKED
    assert any(finding.status == V37_GRAPH_EVALUATION_BLOCKED_BY_EXECUTION_CAPABILITY for finding in result.findings)
