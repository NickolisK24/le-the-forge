from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import (
    ISOLATION_AUDIT_COMPATIBILITY_MISSING,
    ROLLBACK_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_DIFF_AUDIT_SATISFIED,
    RUNTIME_DRIFT_BLOCKED,
    RUNTIME_DRIFT_DETECTED,
    RUNTIME_MUTATION_DETECTED,
    RUNTIME_MUTATION_PROHIBITED,
    RUNTIME_SNAPSHOT_MISSING,
    RUNTIME_TRANSITION_UNAUDITED,
    SESSION_AUDIT_COMPATIBILITY_MISSING,
    build_runtime_diff_audit_contract,
    classify_runtime_diff_state,
    classify_runtime_drift_state,
    evaluate_runtime_diff_audit_contract,
)
from scripts.report_v3_2_runtime_diff_auditing_contracts import build_v3_2_runtime_diff_auditing_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_diff_audit_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_runtime_mutation_detection():
    record = _build([_request(runtime_mutation_classification=RUNTIME_MUTATION_DETECTED)])["runtime_diff_audit_contracts"][0]
    assert record["runtime_diff_audit_status"] == RUNTIME_MUTATION_DETECTED
    assert "runtime_mutation_detected" in record["mutation_blockers"]


def test_runtime_mutation_prohibition():
    record = _build([_request(runtime_mutation_classification=RUNTIME_MUTATION_PROHIBITED)])["runtime_diff_audit_contracts"][0]
    assert record["runtime_diff_audit_status"] == RUNTIME_MUTATION_PROHIBITED


def test_runtime_drift_detection():
    record = _build([_request(post_state={"state": "changed"})])["runtime_diff_audit_contracts"][0]
    assert record["runtime_drift_status"] == RUNTIME_DRIFT_DETECTED
    assert "runtime_drift_detected" in record["drift_blockers"]


def test_runtime_drift_blocking():
    record = _build([_request(runtime_drift_classification=RUNTIME_DRIFT_BLOCKED)])["runtime_diff_audit_contracts"][0]
    assert record["runtime_drift_status"] == RUNTIME_DRIFT_BLOCKED


def test_runtime_transition_unaudited_behavior():
    record = _build([_request(runtime_transition_trace="runtime_transition_unaudited")])["runtime_diff_audit_contracts"][0]
    assert record["runtime_diff_audit_status"] == RUNTIME_TRANSITION_UNAUDITED
    assert record["runtime_drift_status"] == RUNTIME_TRANSITION_UNAUDITED


def test_runtime_snapshot_missing_behavior():
    record = _build([_request(pre_state=None)])["runtime_diff_audit_contracts"][0]
    assert record["runtime_diff_audit_status"] == RUNTIME_SNAPSHOT_MISSING
    assert record["runtime_drift_status"] == RUNTIME_SNAPSHOT_MISSING


def test_rollback_audit_compatibility_enforcement():
    record = evaluate_runtime_diff_audit_contract(_request(), safety_rollback_contract=None, isolation_contract=_isolation(), session_boundary_contract=_session())
    assert record["runtime_diff_audit_status"] == ROLLBACK_AUDIT_COMPATIBILITY_MISSING


def test_isolation_audit_compatibility_enforcement():
    record = evaluate_runtime_diff_audit_contract(_request(), safety_rollback_contract=_safety(), isolation_contract=None, session_boundary_contract=_session())
    assert record["runtime_diff_audit_status"] == ISOLATION_AUDIT_COMPATIBILITY_MISSING


def test_session_audit_compatibility_enforcement():
    record = evaluate_runtime_diff_audit_contract(_request(), safety_rollback_contract=_safety(), isolation_contract=_isolation(), session_boundary_contract=None)
    assert record["runtime_diff_audit_status"] == SESSION_AUDIT_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(runtime_mutation_classification=RUNTIME_MUTATION_DETECTED, runtime_transition_trace="missing", runtime_drift_classification=RUNTIME_DRIFT_BLOCKED)])["runtime_diff_audit_contracts"][0]
    assert "runtime_mutation_detected" in record["mutation_blockers"]
    assert "runtime_transition_unaudited" in record["mutation_blockers"]
    assert "runtime_drift_blocked" in record["drift_blockers"]


def test_no_silent_runtime_mutations_or_hidden_transitions():
    record = _build()["runtime_diff_audit_contracts"][0]
    assert record["metadata"]["silent_runtime_mutations_allowed"] is False
    assert record["metadata"]["hidden_runtime_transitions_allowed"] is False
    assert record["metadata"]["implicit_runtime_transition_approval_allowed"] is False


def test_no_implicit_runtime_transition_approval():
    record = _build([_request(runtime_diff_visibility_state="hidden")])["runtime_diff_audit_contracts"][0]
    assert record["runtime_diff_audit_status"] == RUNTIME_TRANSITION_UNAUDITED


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["runtime_diff_audit_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["runtime_diff_audit_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_diff_state(_request(), blockers=[]) == RUNTIME_DIFF_AUDIT_SATISFIED
    assert classify_runtime_diff_state(_request(), blockers=["runtime_mutation_detected"]) == RUNTIME_MUTATION_DETECTED
    assert classify_runtime_drift_state(_request(), blockers=[]) == RUNTIME_DIFF_AUDIT_SATISFIED
    assert classify_runtime_drift_state(_request(), blockers=["runtime_drift_detected"]) == RUNTIME_DRIFT_DETECTED


def test_stable_report_generation():
    first = build_v3_2_runtime_diff_auditing_contracts_report()
    second = build_v3_2_runtime_diff_auditing_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_diff_auditing_contracts"]["deterministic_hash"] == second["runtime_diff_auditing_contracts"]["deterministic_hash"]


def _build(requests=None, safety=None, isolations=None, sessions=None):
    return build_runtime_diff_audit_contract(
        {"runtime_diff_requests": [_request()] if requests is None else requests, "deterministic_hash": "diff-requests-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
    )


def _request(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    pre_state="default",
    post_state="default",
    runtime_mutation_classification="runtime_mutation_absent",
    runtime_drift_classification="runtime_drift_absent",
    runtime_transition_trace="runtime_transition_audited",
    runtime_diff_visibility_state="runtime_diff_visible",
):
    pre = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "state": "stable"} if pre_state == "default" else pre_state
    post = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "state": "stable"} if post_state == "default" else post_state
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_pre_state_snapshot": pre,
        "runtime_post_state_snapshot": post,
        "runtime_mutation_classification": runtime_mutation_classification,
        "runtime_drift_classification": runtime_drift_classification,
        "runtime_transition_trace": runtime_transition_trace,
        "runtime_diff_visibility_state": runtime_diff_visibility_state,
        "runtime_auditability_state": "runtime_auditable",
        "runtime_rollback_audit_compatibility_state": "rollback_audit_compatible",
        "runtime_isolation_audit_compatibility_state": "isolation_audit_compatible",
        "runtime_session_audit_compatibility_state": "session_audit_compatible",
    }


def _safety(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_safety_status": "runtime_safety_satisfied",
        "runtime_rollback_status": "runtime_rollback_ready",
    }


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied"}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied"}
