from app.planner_adapters.v3_2.runtime_replayability_contracts import (
    RUNTIME_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_REPLAY_DETERMINISM_FAILED,
    RUNTIME_REPLAY_EVIDENCE_INCOMPLETE,
    RUNTIME_REPLAY_HASH_MISMATCH,
    RUNTIME_REPLAY_INPUT_MISSING,
    RUNTIME_REPLAY_LINEAGE_BROKEN,
    RUNTIME_REPLAY_OUTPUT_MISSING,
    RUNTIME_REPLAY_OUTPUT_UNSTABLE,
    RUNTIME_REPLAY_TRACE_MISMATCH,
    RUNTIME_REPLAYABILITY_SATISFIED,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING,
    build_runtime_replayability_contract,
    classify_runtime_replay_mismatch_state,
    classify_runtime_replayability_state,
    evaluate_runtime_replayability_contract,
)
from scripts.report_v3_2_runtime_replayability_contracts import build_v3_2_runtime_replayability_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")], [_determinism("manifest_b", "set_b"), _determinism("manifest_a", "set_a")], [_traceability("manifest_b", "set_b"), _traceability("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")], [_determinism("manifest_a", "set_a"), _determinism("manifest_b", "set_b")], [_traceability("manifest_a", "set_a"), _traceability("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_replayability_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_replay_input_enforcement():
    assert _status(_request(runtime_replay_input_state="missing")) == RUNTIME_REPLAY_INPUT_MISSING


def test_replay_output_enforcement():
    assert _status(_request(runtime_replay_output_state="missing")) == RUNTIME_REPLAY_OUTPUT_MISSING


def test_replay_hash_mismatch_detection():
    record = _build([_request(runtime_replay_hash_state="mismatch")])["runtime_replayability_contracts"][0]
    assert record["runtime_replayability_status"] == RUNTIME_REPLAY_HASH_MISMATCH
    assert record["runtime_replay_mismatch_status"] == RUNTIME_REPLAY_HASH_MISMATCH


def test_replay_trace_mismatch_detection():
    assert _status(_request(runtime_replay_trace_state="mismatch")) == RUNTIME_REPLAY_TRACE_MISMATCH


def test_replay_lineage_broken_detection():
    assert _status(_request(runtime_replay_lineage_preservation_state="broken")) == RUNTIME_REPLAY_LINEAGE_BROKEN


def test_replay_determinism_failure_detection():
    assert _status(_request(runtime_replay_determinism_state="failed")) == RUNTIME_REPLAY_DETERMINISM_FAILED


def test_replay_evidence_incomplete_behavior():
    assert _status(_request(runtime_replay_evidence_completeness_state="incomplete")) == RUNTIME_REPLAY_EVIDENCE_INCOMPLETE


def test_replay_output_instability_detection():
    assert _status(_request(runtime_replay_output_stability_state="unstable")) == RUNTIME_REPLAY_OUTPUT_UNSTABLE


def test_traceability_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=None)
    assert record["runtime_replayability_status"] == RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING


def test_determinism_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=None, traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_DETERMINISM_COMPATIBILITY_MISSING


def test_diff_audit_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=None, determinism_validation_contract=_determinism(), traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING


def test_rollback_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=None, diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_ROLLBACK_COMPATIBILITY_MISSING


def test_session_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=None, safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_SESSION_COMPATIBILITY_MISSING


def test_isolation_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=None, session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_ISOLATION_COMPATIBILITY_MISSING


def test_entrypoint_compatibility_enforcement():
    record = evaluate_runtime_replayability_contract(_request(), entrypoint_contract=None, isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability())
    assert record["runtime_replayability_status"] == RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(runtime_replay_input_state="missing", runtime_replay_hash_state="mismatch", runtime_replay_output_stability_state="unstable")])["runtime_replayability_contracts"][0]
    assert "runtime_replay_input_missing" in record["replay_blockers"]
    assert "runtime_replay_hash_mismatch" in record["replay_instability_blockers"]
    assert "runtime_replay_output_unstable" in record["replay_instability_blockers"]


def test_no_silent_replay_failures_or_implicit_replay_approval():
    record = _build()["runtime_replayability_contracts"][0]
    assert record["metadata"]["silent_replay_failures_allowed"] is False
    assert record["metadata"]["implicit_replay_approval_allowed"] is False
    assert record["metadata"]["fallback_replayability_allowed"] is False


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["runtime_replayability_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["runtime_replayability_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_replayability_state(_request(), blockers=[]) == RUNTIME_REPLAYABILITY_SATISFIED
    assert classify_runtime_replayability_state(_request(), blockers=["runtime_replay_input_missing"]) == RUNTIME_REPLAY_INPUT_MISSING
    assert classify_runtime_replay_mismatch_state(_request(), blockers=[]) == RUNTIME_REPLAYABILITY_SATISFIED
    assert classify_runtime_replay_mismatch_state(_request(), blockers=["runtime_replay_hash_mismatch"]) == RUNTIME_REPLAY_HASH_MISMATCH


def test_stable_report_generation():
    first = build_v3_2_runtime_replayability_contracts_report()
    second = build_v3_2_runtime_replayability_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_replayability_contracts"]["deterministic_hash"] == second["runtime_replayability_contracts"]["deterministic_hash"]


def _status(request):
    return _build([request])["runtime_replayability_contracts"][0]["runtime_replayability_status"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None, traceability=None):
    return build_runtime_replayability_contract(
        {"runtime_replayability_requests": [_request()] if requests is None else requests, "deterministic_hash": "replayability-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
        runtime_determinism_validation_contracts={"runtime_determinism_validation_contracts": [_determinism()] if determinism is None else determinism, "deterministic_hash": "determinism-hash"},
        runtime_traceability_contracts={"runtime_traceability_contracts": [_traceability()] if traceability is None else traceability, "deterministic_hash": "traceability-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", runtime_replay_input_state="runtime_replay_input_present", runtime_replay_output_state="runtime_replay_output_present", runtime_replay_hash_state="runtime_replay_hash_consistent", runtime_replay_trace_state="runtime_replay_trace_consistent", runtime_replay_lineage_preservation_state="runtime_replay_lineage_preserved", runtime_replay_determinism_state="runtime_replay_determinism_satisfied", runtime_replay_mismatch_state="runtime_replay_mismatch_absent", runtime_replay_evidence_completeness_state="runtime_replay_evidence_complete", runtime_replay_output_stability_state="runtime_replay_output_stable"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_replay_input_state": runtime_replay_input_state,
        "runtime_replay_output_state": runtime_replay_output_state,
        "runtime_replay_hash_state": runtime_replay_hash_state,
        "runtime_replay_trace_state": runtime_replay_trace_state,
        "runtime_replay_lineage_preservation_state": runtime_replay_lineage_preservation_state,
        "runtime_replay_determinism_state": runtime_replay_determinism_state,
        "runtime_replay_mismatch_state": runtime_replay_mismatch_state,
        "runtime_replay_evidence_completeness_state": runtime_replay_evidence_completeness_state,
        "runtime_replay_output_stability_state": runtime_replay_output_stability_state,
    }


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_entrypoint_status": "experimental_runtime_eligible"}


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied"}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied"}


def _safety(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_safety_status": "runtime_safety_satisfied", "runtime_rollback_status": "runtime_rollback_ready"}


def _diff(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_diff_audit_status": "runtime_diff_audit_satisfied", "runtime_drift_status": "runtime_diff_audit_satisfied"}


def _determinism(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_determinism_status": "runtime_determinism_satisfied"}


def _traceability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_traceability_status": "runtime_traceability_satisfied"}
