from app.planner_adapters.v3_2.runtime_kill_switch_contracts import (
    RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_COMPATIBILITY_MISSING,
    RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING,
    RUNTIME_EXPERIMENT_COMPATIBILITY_MISSING,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_KILL_SWITCH_ACTIVE,
    RUNTIME_KILL_SWITCH_POLICY_MISSING,
    RUNTIME_KILL_SWITCH_SATISFIED,
    RUNTIME_KILL_SWITCH_SCOPE_MISSING,
    RUNTIME_KILL_SWITCH_REASON_MISSING,
    RUNTIME_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY,
    RUNTIME_OVERRIDE_NOT_REQUESTED,
    RUNTIME_OVERRIDE_REQUESTED,
    RUNTIME_OVERRIDE_UNAUTHORIZED,
    RUNTIME_OVERRIDE_UNSAFE,
    RUNTIME_REPLAYABILITY_COMPATIBILITY_MISSING,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_SHUTDOWN_COMPLETE,
    RUNTIME_SHUTDOWN_INCOMPLETE,
    RUNTIME_SHUTDOWN_REQUIRED,
    RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING,
    build_runtime_kill_switch_contract,
    classify_runtime_kill_switch_override_state,
    classify_runtime_kill_switch_state,
    classify_runtime_shutdown_state,
    evaluate_runtime_kill_switch_contract,
)
from scripts.report_v3_2_runtime_kill_switch_contracts import build_v3_2_runtime_kill_switch_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")], [_determinism("manifest_b", "set_b"), _determinism("manifest_a", "set_a")], [_traceability("manifest_b", "set_b"), _traceability("manifest_a", "set_a")], [_replayability("manifest_b", "set_b"), _replayability("manifest_a", "set_a")], [_drift("manifest_b", "set_b"), _drift("manifest_a", "set_a")], [_experiment("manifest_b", "set_b"), _experiment("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")], [_determinism("manifest_a", "set_a"), _determinism("manifest_b", "set_b")], [_traceability("manifest_a", "set_a"), _traceability("manifest_b", "set_b")], [_replayability("manifest_a", "set_a"), _replayability("manifest_b", "set_b")], [_drift("manifest_a", "set_a"), _drift("manifest_b", "set_b")], [_experiment("manifest_a", "set_a"), _experiment("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_kill_switch_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_explicit_kill_switch_policy_enforcement():
    assert _status(_request(kill_switch_policy_state="missing")) == RUNTIME_KILL_SWITCH_POLICY_MISSING


def test_explicit_kill_switch_scope_enforcement():
    assert _status(_request(kill_switch_scope_state="missing")) == RUNTIME_KILL_SWITCH_SCOPE_MISSING


def test_active_kill_switch_reason_enforcement():
    assert _status(_request(kill_switch_activation_state="runtime_kill_switch_active", kill_switch_reason_state="missing")) == RUNTIME_KILL_SWITCH_REASON_MISSING


def test_active_kill_switch_blocks_experiment_continuation():
    record = _build([_request(kill_switch_activation_state="runtime_kill_switch_active", kill_switch_reason_state="operator_requested_shutdown", kill_switch_shutdown_state="runtime_shutdown_required")])["runtime_kill_switch_contracts"][0]
    assert record["runtime_kill_switch_status"] == RUNTIME_KILL_SWITCH_ACTIVE
    assert "runtime_kill_switch_active" in record["kill_switch_blockers"]
    assert record["runtime_experiment_continuation_authorized"] is False


def test_shutdown_required_classification():
    assert classify_runtime_shutdown_state(_request(kill_switch_shutdown_state="runtime_shutdown_required"), blockers=["runtime_shutdown_required"]) == RUNTIME_SHUTDOWN_REQUIRED


def test_shutdown_complete_classification():
    assert classify_runtime_shutdown_state(_request()) == RUNTIME_SHUTDOWN_COMPLETE


def test_shutdown_incomplete_blocking():
    record = _build([_request(kill_switch_shutdown_state="runtime_shutdown_incomplete")])["runtime_kill_switch_contracts"][0]
    assert record["runtime_kill_switch_status"] == RUNTIME_SHUTDOWN_INCOMPLETE
    assert record["runtime_shutdown_status"] == RUNTIME_SHUTDOWN_INCOMPLETE


def test_override_not_requested_classification():
    assert classify_runtime_kill_switch_override_state(_request()) == RUNTIME_OVERRIDE_NOT_REQUESTED


def test_override_requested_classification():
    request = _request(kill_switch_override_intent_state="runtime_override_requested")
    assert classify_runtime_kill_switch_override_state(request) == RUNTIME_OVERRIDE_REQUESTED


def test_override_unauthorized_blocking():
    record = _build([_request(kill_switch_override_intent_state="runtime_override_requested", kill_switch_override_authorization_state="override_unauthorized", kill_switch_override_safety_state="override_safe_for_non_production_recovery")])["runtime_kill_switch_contracts"][0]
    assert record["runtime_kill_switch_override_status"] == RUNTIME_OVERRIDE_UNAUTHORIZED
    assert record["runtime_kill_switch_status"] == RUNTIME_OVERRIDE_UNAUTHORIZED


def test_override_unsafe_blocking():
    record = _build([_request(kill_switch_override_intent_state="runtime_override_requested", kill_switch_override_authorization_state="override_authorized_for_non_production_recovery", kill_switch_override_safety_state="override_unsafe")])["runtime_kill_switch_contracts"][0]
    assert record["runtime_kill_switch_override_status"] == RUNTIME_OVERRIDE_UNSAFE
    assert record["runtime_kill_switch_status"] == RUNTIME_OVERRIDE_UNSAFE


def test_override_allowed_only_for_non_production_recovery_behavior():
    record = _build([_request(kill_switch_override_intent_state="runtime_override_requested", kill_switch_override_authorization_state="override_authorized_for_non_production_recovery", kill_switch_override_safety_state="override_safe_for_non_production_recovery")])["runtime_kill_switch_contracts"][0]
    assert record["runtime_kill_switch_override_status"] == RUNTIME_OVERRIDE_ALLOWED_FOR_NON_PRODUCTION_RECOVERY_ONLY
    assert record["metadata"]["override_allowed_only_for_non_production_recovery"] is True
    assert record["runtime_kill_switch_contract_authorizes_production_routing"] is False


def test_compatibility_enforcement():
    request = _request()
    base = dict(entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability(), replayability_contract=_replayability(), drift_detection_contract=_drift(), limited_runtime_experiment_contract=_experiment())
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "entrypoint_contract": None})["runtime_kill_switch_status"] == RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "isolation_contract": None})["runtime_kill_switch_status"] == RUNTIME_ISOLATION_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "session_boundary_contract": None})["runtime_kill_switch_status"] == RUNTIME_SESSION_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "safety_rollback_contract": None})["runtime_kill_switch_status"] == RUNTIME_ROLLBACK_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "diff_audit_contract": None})["runtime_kill_switch_status"] == RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "determinism_validation_contract": None})["runtime_kill_switch_status"] == RUNTIME_DETERMINISM_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "traceability_contract": None})["runtime_kill_switch_status"] == RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "replayability_contract": None})["runtime_kill_switch_status"] == RUNTIME_REPLAYABILITY_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "drift_detection_contract": None})["runtime_kill_switch_status"] == RUNTIME_DRIFT_COMPATIBILITY_MISSING
    assert evaluate_runtime_kill_switch_contract(request, **{**base, "limited_runtime_experiment_contract": None})["runtime_kill_switch_status"] == RUNTIME_EXPERIMENT_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(kill_switch_policy_state="missing", kill_switch_scope_state="missing", kill_switch_override_intent_state="runtime_override_requested", kill_switch_override_authorization_state="override_unauthorized", kill_switch_override_safety_state="override_unsafe")])["runtime_kill_switch_contracts"][0]
    assert "runtime_kill_switch_policy_missing" in record["kill_switch_blockers"]
    assert "runtime_kill_switch_scope_missing" in record["kill_switch_blockers"]
    assert "runtime_override_unauthorized" in record["override_blockers"]
    assert "runtime_override_unsafe" in record["override_blockers"]


def test_no_silent_kill_switch_failures_or_implicit_experiment_continuation():
    record = _build()["runtime_kill_switch_contracts"][0]
    assert record["metadata"]["silent_kill_switch_failures_allowed"] is False
    assert record["metadata"]["implicit_experiment_continuation_allowed"] is False
    assert record["metadata"]["fallback_kill_switch_logic_allowed"] is False


def test_no_default_manifest_consumption_activation_or_production_routing_changes():
    result = _build()
    assert result["safety_confirmations"]["runtime_kill_switch_contract_enables_runtime_manifest_consumption"] is False
    assert result["safety_confirmations"]["runtime_kill_switch_contract_authorizes_production_routing"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["summary"]["production_behavior_changed"] is False


def test_production_runtime_remains_prohibited_and_manifest_authority_prohibited():
    result = _build()
    record = result["runtime_kill_switch_contracts"][0]
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["runtime_disabled_path_verification"]["production_runtime_prohibited"] is True
    assert record["production_authoritative_manifest_treatment"] is False
    assert result["summary"]["production_authoritative_manifest_treatment"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_kill_switch_state(_request(), blockers=[]) == RUNTIME_KILL_SWITCH_SATISFIED
    assert classify_runtime_kill_switch_state(_request(), blockers=["runtime_kill_switch_policy_missing"]) == RUNTIME_KILL_SWITCH_POLICY_MISSING
    assert classify_runtime_kill_switch_override_state(_request(), blockers=["runtime_override_unsafe"]) == RUNTIME_OVERRIDE_UNSAFE


def test_stable_report_generation():
    first = build_v3_2_runtime_kill_switch_contracts_report()
    second = build_v3_2_runtime_kill_switch_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_kill_switch_contracts"]["deterministic_hash"] == second["runtime_kill_switch_contracts"]["deterministic_hash"]


def _status(request):
    return _build([request])["runtime_kill_switch_contracts"][0]["runtime_kill_switch_status"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None, traceability=None, replayability=None, drift=None, experiment=None):
    return build_runtime_kill_switch_contract(
        {"runtime_kill_switch_requests": [_request()] if requests is None else requests, "deterministic_hash": "kill-switch-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
        runtime_determinism_validation_contracts={"runtime_determinism_validation_contracts": [_determinism()] if determinism is None else determinism, "deterministic_hash": "determinism-hash"},
        runtime_traceability_contracts={"runtime_traceability_contracts": [_traceability()] if traceability is None else traceability, "deterministic_hash": "traceability-hash"},
        runtime_replayability_contracts={"runtime_replayability_contracts": [_replayability()] if replayability is None else replayability, "deterministic_hash": "replayability-hash"},
        runtime_drift_detection_contracts={"runtime_drift_detection_contracts": [_drift()] if drift is None else drift, "deterministic_hash": "drift-hash"},
        limited_runtime_experiment_contracts={"limited_runtime_experiment_contracts": [_experiment()] if experiment is None else experiment, "deterministic_hash": "experiment-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", kill_switch_policy_state="kill_switch_policy_present", kill_switch_activation_state="runtime_kill_switch_inactive", kill_switch_scope_state="kill_switch_scope_limited_runtime_experiment", kill_switch_reason_state="kill_switch_reason_not_required", kill_switch_shutdown_state="runtime_shutdown_complete", kill_switch_override_intent_state="runtime_override_not_requested", kill_switch_override_authorization_state="override_authorization_not_required", kill_switch_override_safety_state="override_safety_not_required"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "kill_switch_policy_state": kill_switch_policy_state, "kill_switch_activation_state": kill_switch_activation_state, "kill_switch_scope_state": kill_switch_scope_state, "kill_switch_reason_state": kill_switch_reason_state, "kill_switch_shutdown_state": kill_switch_shutdown_state, "kill_switch_override_intent_state": kill_switch_override_intent_state, "kill_switch_override_authorization_state": kill_switch_override_authorization_state, "kill_switch_override_safety_state": kill_switch_override_safety_state}


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_entrypoint_status": "experimental_runtime_eligible"}


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied"}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied"}


def _safety(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_safety_status": "runtime_safety_satisfied", "runtime_rollback_status": "runtime_rollback_ready"}


def _diff(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_diff_audit_status": "runtime_diff_audit_satisfied"}


def _determinism(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_determinism_status": "runtime_determinism_satisfied"}


def _traceability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_traceability_status": "runtime_traceability_satisfied"}


def _replayability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_replayability_status": "runtime_replayability_satisfied"}


def _drift(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_drift_detection_status": "runtime_drift_not_detected"}


def _experiment(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "limited_runtime_experiment_status": "limited_runtime_experiment_eligible"}
