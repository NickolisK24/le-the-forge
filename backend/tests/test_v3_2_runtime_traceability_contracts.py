from app.planner_adapters.v3_2.runtime_traceability_contracts import (
    RUNTIME_DETERMINISM_LINEAGE_MISSING,
    RUNTIME_DIFF_AUDIT_LINEAGE_MISSING,
    RUNTIME_ENTRYPOINT_LINEAGE_MISSING,
    RUNTIME_EVIDENCE_UNEXPLAINABLE,
    RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING,
    RUNTIME_FIXTURE_LINEAGE_MISSING,
    RUNTIME_ISOLATION_LINEAGE_MISSING,
    RUNTIME_LINEAGE_BROKEN,
    RUNTIME_MANIFEST_LINEAGE_MISSING,
    RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING,
    RUNTIME_SESSION_LINEAGE_MISSING,
    RUNTIME_SOURCE_LINEAGE_MISSING,
    RUNTIME_TRACE_IDENTITY_MISSING,
    RUNTIME_TRACEABILITY_SATISFIED,
    build_runtime_traceability_contract,
    classify_runtime_lineage_state,
    classify_runtime_traceability_state,
    evaluate_runtime_traceability_contract,
)
from scripts.report_v3_2_runtime_traceability_contracts import build_v3_2_runtime_traceability_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")], [_determinism("manifest_b", "set_b"), _determinism("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")], [_determinism("manifest_a", "set_a"), _determinism("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_traceability_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_deterministic_trace_identity():
    record = _build()["runtime_traceability_contracts"][0]
    assert record["runtime_trace_id"] == "trace_manifest_a_set_a"
    assert record["runtime_traceability_status"] == RUNTIME_TRACEABILITY_SATISFIED


def test_missing_trace_identity_blocks():
    assert _status(_request(runtime_trace_id=None)) == RUNTIME_TRACE_IDENTITY_MISSING


def test_source_lineage_enforcement():
    assert _status(_request(runtime_source_evidence_lineage="missing")) == RUNTIME_SOURCE_LINEAGE_MISSING


def test_manifest_lineage_enforcement():
    assert _status(_request(runtime_manifest_lineage="missing")) == RUNTIME_MANIFEST_LINEAGE_MISSING


def test_fixture_lineage_enforcement():
    assert _status(_request(runtime_fixture_lineage="missing")) == RUNTIME_FIXTURE_LINEAGE_MISSING


def test_entrypoint_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=None, isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism())
    assert record["runtime_traceability_status"] == RUNTIME_ENTRYPOINT_LINEAGE_MISSING


def test_isolation_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=None, session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism())
    assert record["runtime_traceability_status"] == RUNTIME_ISOLATION_LINEAGE_MISSING


def test_session_boundary_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=None, safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism())
    assert record["runtime_traceability_status"] == RUNTIME_SESSION_LINEAGE_MISSING


def test_safety_rollback_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=None, diff_audit_contract=_diff(), determinism_validation_contract=_determinism())
    assert record["runtime_traceability_status"] == RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING


def test_diff_audit_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=None, determinism_validation_contract=_determinism())
    assert record["runtime_traceability_status"] == RUNTIME_DIFF_AUDIT_LINEAGE_MISSING


def test_determinism_lineage_enforcement():
    record = evaluate_runtime_traceability_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=None)
    assert record["runtime_traceability_status"] == RUNTIME_DETERMINISM_LINEAGE_MISSING


def test_final_classification_lineage_enforcement():
    assert _status(_request(runtime_final_classification_lineage="missing")) == RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING


def test_unexplainable_evidence_blocking():
    assert _status(_request(runtime_trace_explainability_state="runtime_evidence_unexplainable")) == RUNTIME_EVIDENCE_UNEXPLAINABLE


def test_broken_lineage_blocking():
    assert _status(_request(runtime_lineage_integrity_state=RUNTIME_LINEAGE_BROKEN)) == RUNTIME_LINEAGE_BROKEN


def test_blocker_accumulation_behavior():
    record = _build([_request(runtime_source_evidence_lineage="missing", runtime_manifest_lineage="missing", runtime_trace_explainability_state="bad")])["runtime_traceability_contracts"][0]
    assert "runtime_source_lineage_missing" in record["lineage_blockers"]
    assert "runtime_manifest_lineage_missing" in record["lineage_blockers"]
    assert "runtime_evidence_unexplainable" in record["trace_blockers"]


def test_no_silent_traceability_failures_or_implicit_lineage_approval():
    record = _build()["runtime_traceability_contracts"][0]
    assert record["metadata"]["silent_traceability_failures_allowed"] is False
    assert record["metadata"]["implicit_lineage_approval_allowed"] is False
    assert record["metadata"]["fallback_traceability_allowed"] is False


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["runtime_traceability_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["runtime_traceability_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_traceability_state(_request(), blockers=[]) == RUNTIME_TRACEABILITY_SATISFIED
    assert classify_runtime_traceability_state(_request(), blockers=["runtime_trace_identity_missing"]) == RUNTIME_TRACE_IDENTITY_MISSING
    assert classify_runtime_lineage_state(_request(), blockers=[]) == RUNTIME_TRACEABILITY_SATISFIED
    assert classify_runtime_lineage_state(_request(), blockers=["runtime_lineage_broken"]) == RUNTIME_LINEAGE_BROKEN


def test_stable_report_generation():
    first = build_v3_2_runtime_traceability_contracts_report()
    second = build_v3_2_runtime_traceability_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_traceability_contracts"]["deterministic_hash"] == second["runtime_traceability_contracts"]["deterministic_hash"]


def _status(request):
    return _build([request])["runtime_traceability_contracts"][0]["runtime_traceability_status"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None):
    return build_runtime_traceability_contract(
        {"runtime_traceability_requests": [_request()] if requests is None else requests, "deterministic_hash": "traceability-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
        runtime_determinism_validation_contracts={"runtime_determinism_validation_contracts": [_determinism()] if determinism is None else determinism, "deterministic_hash": "determinism-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", runtime_trace_id="trace_manifest_a_set_a", runtime_source_evidence_lineage="source_lineage_present", runtime_manifest_lineage="manifest_lineage_present", runtime_fixture_lineage="fixture_lineage_present", runtime_entrypoint_lineage="entrypoint_lineage_present", runtime_isolation_lineage="isolation_lineage_present", runtime_session_lineage="session_lineage_present", runtime_safety_rollback_lineage="safety_rollback_lineage_present", runtime_diff_audit_lineage="diff_audit_lineage_present", runtime_determinism_lineage="determinism_lineage_present", runtime_final_classification_lineage="final_classification_lineage_present", runtime_trace_explainability_state="runtime_evidence_explainable", runtime_lineage_integrity_state="runtime_lineage_intact"):
    return {
        "runtime_trace_id": runtime_trace_id,
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_trace_identity_state": "runtime_trace_identity_present",
        "runtime_source_evidence_lineage": runtime_source_evidence_lineage,
        "runtime_manifest_lineage": runtime_manifest_lineage,
        "runtime_fixture_lineage": runtime_fixture_lineage,
        "runtime_entrypoint_lineage": runtime_entrypoint_lineage,
        "runtime_isolation_lineage": runtime_isolation_lineage,
        "runtime_session_lineage": runtime_session_lineage,
        "runtime_safety_rollback_lineage": runtime_safety_rollback_lineage,
        "runtime_diff_audit_lineage": runtime_diff_audit_lineage,
        "runtime_determinism_lineage": runtime_determinism_lineage,
        "runtime_final_classification_lineage": runtime_final_classification_lineage,
        "runtime_trace_completeness_state": "runtime_trace_complete",
        "runtime_trace_explainability_state": runtime_trace_explainability_state,
        "runtime_lineage_integrity_state": runtime_lineage_integrity_state,
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
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_determinism_status": "runtime_determinism_satisfied", "runtime_replay_status": "runtime_replay_consistency_satisfied"}
