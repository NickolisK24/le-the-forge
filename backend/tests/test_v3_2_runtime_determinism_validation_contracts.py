from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import (
    DETERMINISTIC_HASHING_FAILED,
    DETERMINISTIC_ORDERING_FAILED,
    REPEAT_RUN_CONSISTENCY_FAILED,
    RUNTIME_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_DETERMINISM_SATISFIED,
    RUNTIME_INSTABILITY_DETECTED,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED,
    RUNTIME_REPLAY_CONSISTENCY_FAILED,
    RUNTIME_REPLAY_CONSISTENCY_SATISFIED,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_TRANSITION_INSTABILITY_DETECTED,
    build_runtime_determinism_validation_contract,
    classify_runtime_determinism_state,
    classify_runtime_replay_state,
    evaluate_runtime_determinism_validation_contract,
)
from scripts.report_v3_2_runtime_determinism_validation_contracts import build_v3_2_runtime_determinism_validation_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_determinism_validation_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_repeat_run_consistency_validation():
    record = _build([_request(runtime_repeat_run_state="repeat_run_consistency_failed")])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == REPEAT_RUN_CONSISTENCY_FAILED


def test_deterministic_ordering_validation():
    record = _build([_request(runtime_deterministic_ordering_state="deterministic_ordering_failed")])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == DETERMINISTIC_ORDERING_FAILED


def test_deterministic_hashing_validation():
    record = _build([_request(runtime_deterministic_hashing_state="deterministic_hashing_failed")])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == DETERMINISTIC_HASHING_FAILED


def test_unstable_repeat_hashes_fail_hashing_validation():
    record = _build([_request(repeat_run_hashes=["a", "b"])])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == DETERMINISTIC_HASHING_FAILED


def test_replay_consistency_validation():
    record = _build([_request(runtime_replay_consistency_state="runtime_replay_consistency_failed")])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_replay_status"] == RUNTIME_REPLAY_CONSISTENCY_FAILED


def test_runtime_nondeterministic_drift_detection():
    record = _build([_request(runtime_nondeterministic_drift_state=RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED)])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED
    assert "runtime_nondeterministic_drift_detected" in record["instability_blockers"]


def test_runtime_instability_detection():
    record = _build([_request(runtime_instability_classification=RUNTIME_INSTABILITY_DETECTED)])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == RUNTIME_INSTABILITY_DETECTED


def test_runtime_transition_instability_detection():
    record = _build([_request(runtime_transition_consistency_state=RUNTIME_TRANSITION_INSTABILITY_DETECTED)])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_determinism_status"] == RUNTIME_TRANSITION_INSTABILITY_DETECTED


def test_runtime_audit_compatibility_enforcement():
    record = evaluate_runtime_determinism_validation_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=None)
    assert record["runtime_determinism_status"] == RUNTIME_AUDIT_COMPATIBILITY_MISSING
    assert record["runtime_replay_status"] == RUNTIME_AUDIT_COMPATIBILITY_MISSING


def test_runtime_rollback_compatibility_enforcement():
    record = evaluate_runtime_determinism_validation_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=None, diff_audit_contract=_diff())
    assert record["runtime_determinism_status"] == RUNTIME_ROLLBACK_COMPATIBILITY_MISSING


def test_runtime_session_compatibility_enforcement():
    record = evaluate_runtime_determinism_validation_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=None, safety_rollback_contract=_safety(), diff_audit_contract=_diff())
    assert record["runtime_determinism_status"] == RUNTIME_SESSION_COMPATIBILITY_MISSING


def test_runtime_isolation_compatibility_enforcement():
    record = evaluate_runtime_determinism_validation_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=None, session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff())
    assert record["runtime_determinism_status"] == RUNTIME_ISOLATION_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(runtime_repeat_run_state="failed", runtime_deterministic_ordering_state="failed", runtime_instability_classification=RUNTIME_INSTABILITY_DETECTED, runtime_replay_consistency_state="failed")])["runtime_determinism_validation_contracts"][0]
    assert "repeat_run_consistency_failed" in record["determinism_blockers"]
    assert "deterministic_ordering_failed" in record["determinism_blockers"]
    assert "runtime_instability_detected" in record["instability_blockers"]
    assert "runtime_replay_consistency_failed" in record["replay_blockers"]


def test_no_silent_determinism_failures_or_hidden_instability():
    record = _build()["runtime_determinism_validation_contracts"][0]
    assert record["metadata"]["silent_determinism_failures_allowed"] is False
    assert record["metadata"]["hidden_runtime_instability_allowed"] is False
    assert record["metadata"]["implicit_replay_consistency_approval_allowed"] is False


def test_no_implicit_replay_consistency_approval():
    record = _build([_request(runtime_replay_trace_classification="missing")])["runtime_determinism_validation_contracts"][0]
    assert record["runtime_replay_status"] == RUNTIME_REPLAY_CONSISTENCY_FAILED


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["runtime_determinism_validation_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["runtime_determinism_validation_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_determinism_state(_request(), blockers=[]) == RUNTIME_DETERMINISM_SATISFIED
    assert classify_runtime_determinism_state(_request(), blockers=["deterministic_hashing_failed"]) == DETERMINISTIC_HASHING_FAILED
    assert classify_runtime_replay_state(_request(), blockers=[]) == RUNTIME_REPLAY_CONSISTENCY_SATISFIED
    assert classify_runtime_replay_state(_request(), blockers=["runtime_replay_consistency_failed"]) == RUNTIME_REPLAY_CONSISTENCY_FAILED


def test_stable_report_generation():
    first = build_v3_2_runtime_determinism_validation_contracts_report()
    second = build_v3_2_runtime_determinism_validation_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_determinism_validation_contracts"]["deterministic_hash"] == second["runtime_determinism_validation_contracts"]["deterministic_hash"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None):
    return build_runtime_determinism_validation_contract(
        {"runtime_determinism_requests": [_request()] if requests is None else requests, "deterministic_hash": "determinism-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
    )


def _request(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    runtime_repeat_run_state="repeat_run_consistency_satisfied",
    runtime_replay_consistency_state="runtime_replay_consistency_satisfied",
    runtime_deterministic_ordering_state="deterministic_ordering_satisfied",
    runtime_deterministic_hashing_state="deterministic_hashing_satisfied",
    runtime_transition_consistency_state="runtime_transition_consistency_satisfied",
    runtime_nondeterministic_drift_state="runtime_nondeterministic_drift_absent",
    runtime_instability_classification="runtime_instability_absent",
    runtime_replay_trace_classification="runtime_replay_trace_audited",
    repeat_run_hashes=None,
):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_repeat_run_state": runtime_repeat_run_state,
        "runtime_replay_consistency_state": runtime_replay_consistency_state,
        "runtime_deterministic_ordering_state": runtime_deterministic_ordering_state,
        "runtime_deterministic_hashing_state": runtime_deterministic_hashing_state,
        "runtime_transition_consistency_state": runtime_transition_consistency_state,
        "runtime_nondeterministic_drift_state": runtime_nondeterministic_drift_state,
        "runtime_instability_classification": runtime_instability_classification,
        "runtime_replay_trace_classification": runtime_replay_trace_classification,
        "repeat_run_hashes": ["stable", "stable"] if repeat_run_hashes is None else repeat_run_hashes,
    }


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_entrypoint_status": "experimental_runtime_eligible"}


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied"}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied"}


def _safety(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_safety_status": "runtime_safety_satisfied",
        "runtime_rollback_status": "runtime_rollback_ready",
    }


def _diff(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_diff_audit_status": "runtime_diff_audit_satisfied",
        "runtime_drift_status": "runtime_diff_audit_satisfied",
    }
