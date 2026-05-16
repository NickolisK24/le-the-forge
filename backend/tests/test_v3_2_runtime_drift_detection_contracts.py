from app.planner_adapters.v3_2.runtime_drift_detection_contracts import (
    CURRENT_RUNTIME_EVIDENCE_MISSING,
    RUNTIME_DRIFT_BASELINE_MISSING,
    RUNTIME_DRIFT_DETECTED,
    RUNTIME_DRIFT_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ENTRYPOINT_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_NOT_DETECTED,
    RUNTIME_DRIFT_REPLAYABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_SEVERITY_CRITICAL,
    RUNTIME_DRIFT_SEVERITY_HIGH,
    RUNTIME_DRIFT_SEVERITY_LOW,
    RUNTIME_DRIFT_SEVERITY_MODERATE,
    RUNTIME_DRIFT_SEVERITY_NONE,
    RUNTIME_DRIFT_TRACEABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_EXPECTED_DRIFT_DETECTED,
    RUNTIME_UNEXPECTED_DRIFT_DETECTED,
    RUNTIME_UNREVIEWED_DRIFT_DETECTED,
    build_runtime_drift_detection_contract,
    classify_runtime_drift_severity_state,
    classify_runtime_drift_state,
    evaluate_runtime_drift_detection_contract,
)
from scripts.report_v3_2_runtime_drift_detection_contracts import build_v3_2_runtime_drift_detection_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")], [_determinism("manifest_b", "set_b"), _determinism("manifest_a", "set_a")], [_traceability("manifest_b", "set_b"), _traceability("manifest_a", "set_a")], [_replayability("manifest_b", "set_b"), _replayability("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")], [_determinism("manifest_a", "set_a"), _determinism("manifest_b", "set_b")], [_traceability("manifest_a", "set_a"), _traceability("manifest_b", "set_b")], [_replayability("manifest_a", "set_a"), _replayability("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_drift_detection_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_drift_baseline_enforcement():
    assert _status(_request(runtime_drift_baseline_evidence_state="missing")) == RUNTIME_DRIFT_BASELINE_MISSING


def test_current_runtime_evidence_enforcement():
    assert _status(_request(current_runtime_evidence_state="missing")) == CURRENT_RUNTIME_EVIDENCE_MISSING


def test_deterministic_drift_comparison_and_no_drift_classification():
    record = _build()[ "runtime_drift_detection_contracts"][0]
    assert record["drift_comparison_state"] == "drift_comparison_completed"
    assert record["runtime_drift_detection_status"] == RUNTIME_DRIFT_NOT_DETECTED


def test_expected_drift_classification():
    assert _status(_request(drift_classification_state=RUNTIME_EXPECTED_DRIFT_DETECTED)) == RUNTIME_EXPECTED_DRIFT_DETECTED


def test_generic_drift_classification():
    assert _status(_request(drift_classification_state=RUNTIME_DRIFT_DETECTED)) == RUNTIME_DRIFT_DETECTED


def test_unexpected_drift_classification():
    assert _status(_request(drift_classification_state=RUNTIME_UNEXPECTED_DRIFT_DETECTED)) == RUNTIME_UNEXPECTED_DRIFT_DETECTED


def test_unreviewed_drift_classification():
    assert _status(_request(drift_classification_state=RUNTIME_UNREVIEWED_DRIFT_DETECTED)) == RUNTIME_UNREVIEWED_DRIFT_DETECTED


def test_drift_severity_classifications():
    assert _severity(_request()) == RUNTIME_DRIFT_SEVERITY_NONE
    assert _severity(_request(drift_severity_state=RUNTIME_DRIFT_SEVERITY_LOW)) == RUNTIME_DRIFT_SEVERITY_LOW
    assert _severity(_request(drift_severity_state=RUNTIME_DRIFT_SEVERITY_MODERATE)) == RUNTIME_DRIFT_SEVERITY_MODERATE
    assert _severity(_request(drift_severity_state=RUNTIME_DRIFT_SEVERITY_HIGH)) == RUNTIME_DRIFT_SEVERITY_HIGH
    assert _severity(_request(drift_severity_state=RUNTIME_DRIFT_SEVERITY_CRITICAL)) == RUNTIME_DRIFT_SEVERITY_CRITICAL


def test_compatibility_enforcement():
    request = _request()
    base = dict(entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability(), replayability_contract=_replayability())
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "replayability_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_REPLAYABILITY_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "traceability_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_TRACEABILITY_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "determinism_validation_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_DETERMINISM_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "diff_audit_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_DIFF_AUDIT_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "safety_rollback_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_ROLLBACK_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "session_boundary_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_SESSION_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "isolation_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_ISOLATION_COMPATIBILITY_MISSING
    assert evaluate_runtime_drift_detection_contract(request, **{**base, "entrypoint_contract": None})["runtime_drift_detection_status"] == RUNTIME_DRIFT_ENTRYPOINT_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(runtime_drift_baseline_evidence_state="missing", current_runtime_evidence_state="missing", drift_classification_state=RUNTIME_UNEXPECTED_DRIFT_DETECTED, drift_severity_state=RUNTIME_DRIFT_SEVERITY_HIGH)])["runtime_drift_detection_contracts"][0]
    assert "runtime_drift_baseline_missing" in record["drift_blockers"]
    assert "current_runtime_evidence_missing" in record["drift_blockers"]
    assert "runtime_unexpected_drift_detected" in record["drift_blockers"]
    assert RUNTIME_DRIFT_SEVERITY_HIGH in record["drift_severity_blockers"]


def test_no_silent_drift_failures_or_implicit_approval():
    record = _build()["runtime_drift_detection_contracts"][0]
    assert record["metadata"]["silent_drift_failures_allowed"] is False
    assert record["metadata"]["implicit_drift_approval_allowed"] is False
    assert record["metadata"]["fallback_drift_detection_allowed"] is False


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["runtime_drift_detection_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["runtime_drift_detection_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_drift_state(_request(), blockers=[]) == RUNTIME_DRIFT_NOT_DETECTED
    assert classify_runtime_drift_state(_request(), blockers=["runtime_unexpected_drift_detected"]) == RUNTIME_UNEXPECTED_DRIFT_DETECTED
    assert classify_runtime_drift_severity_state(_request(), blockers=[]) == RUNTIME_DRIFT_SEVERITY_NONE
    assert classify_runtime_drift_severity_state(_request(), blockers=[RUNTIME_DRIFT_SEVERITY_CRITICAL]) == RUNTIME_DRIFT_SEVERITY_CRITICAL


def test_stable_report_generation():
    first = build_v3_2_runtime_drift_detection_contracts_report()
    second = build_v3_2_runtime_drift_detection_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_drift_detection_contracts"]["deterministic_hash"] == second["runtime_drift_detection_contracts"]["deterministic_hash"]


def _status(request):
    return _build([request])["runtime_drift_detection_contracts"][0]["runtime_drift_detection_status"]


def _severity(request):
    return _build([request])["runtime_drift_detection_contracts"][0]["runtime_drift_severity_status"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None, traceability=None, replayability=None):
    return build_runtime_drift_detection_contract(
        {"runtime_drift_detection_requests": [_request()] if requests is None else requests, "deterministic_hash": "drift-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
        runtime_determinism_validation_contracts={"runtime_determinism_validation_contracts": [_determinism()] if determinism is None else determinism, "deterministic_hash": "determinism-hash"},
        runtime_traceability_contracts={"runtime_traceability_contracts": [_traceability()] if traceability is None else traceability, "deterministic_hash": "traceability-hash"},
        runtime_replayability_contracts={"runtime_replayability_contracts": [_replayability()] if replayability is None else replayability, "deterministic_hash": "replayability-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", runtime_drift_baseline_evidence_state="runtime_drift_baseline_present", current_runtime_evidence_state="current_runtime_evidence_present", drift_classification_state=RUNTIME_DRIFT_NOT_DETECTED, drift_severity_state=RUNTIME_DRIFT_SEVERITY_NONE):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_drift_baseline_evidence_state": runtime_drift_baseline_evidence_state, "current_runtime_evidence_state": current_runtime_evidence_state, "drift_comparison_state": "drift_comparison_completed", "drift_classification_state": drift_classification_state, "drift_severity_state": drift_severity_state, "expected_drift_state": "runtime_expected_drift_absent", "unexpected_drift_state": "runtime_unexpected_drift_absent", "unreviewed_drift_state": "runtime_unreviewed_drift_absent"}


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


def _replayability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_replayability_status": "runtime_replayability_satisfied"}
