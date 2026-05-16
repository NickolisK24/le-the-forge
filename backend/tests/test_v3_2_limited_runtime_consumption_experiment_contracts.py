from app.planner_adapters.v3_2.limited_runtime_consumption_experiment_contracts import (
    EXPERIMENT_AUTHORIZATION_MISSING,
    EXPERIMENT_CONSUMPTION_MODE_INVALID,
    EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED,
    EXPERIMENT_DETERMINISM_COMPATIBILITY_MISSING,
    EXPERIMENT_DIFF_AUDIT_COMPATIBILITY_MISSING,
    EXPERIMENT_DRIFT_DETECTION_COMPATIBILITY_MISSING,
    EXPERIMENT_INTENT_MISSING,
    EXPERIMENT_ISOLATION_COMPATIBILITY_MISSING,
    EXPERIMENT_MANIFEST_AUTHORITY_INVALID,
    EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED,
    EXPERIMENT_REPLAYABILITY_COMPATIBILITY_MISSING,
    EXPERIMENT_ROLLBACK_READINESS_MISSING,
    EXPERIMENT_SAFETY_ROLLBACK_COMPATIBILITY_MISSING,
    EXPERIMENT_SCOPE_MISSING,
    EXPERIMENT_SCOPE_UNSAFE,
    EXPERIMENT_SESSION_COMPATIBILITY_MISSING,
    EXPERIMENT_TRACEABILITY_COMPATIBILITY_MISSING,
    LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE,
    build_limited_runtime_consumption_experiment_contract,
    classify_limited_runtime_consumption_experiment_state,
    classify_limited_runtime_consumption_mode_state,
    evaluate_limited_runtime_consumption_experiment_contract,
)
from scripts.report_v3_2_limited_runtime_consumption_experiment_contracts import build_v3_2_limited_runtime_consumption_experiment_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")], [_safety("manifest_b", "set_b"), _safety("manifest_a", "set_a")], [_diff("manifest_b", "set_b"), _diff("manifest_a", "set_a")], [_determinism("manifest_b", "set_b"), _determinism("manifest_a", "set_a")], [_traceability("manifest_b", "set_b"), _traceability("manifest_a", "set_a")], [_replayability("manifest_b", "set_b"), _replayability("manifest_a", "set_a")], [_drift("manifest_b", "set_b"), _drift("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")], [_safety("manifest_a", "set_a"), _safety("manifest_b", "set_b")], [_diff("manifest_a", "set_a"), _diff("manifest_b", "set_b")], [_determinism("manifest_a", "set_a"), _determinism("manifest_b", "set_b")], [_traceability("manifest_a", "set_a"), _traceability("manifest_b", "set_b")], [_replayability("manifest_a", "set_a"), _replayability("manifest_b", "set_b")], [_drift("manifest_a", "set_a"), _drift("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["limited_runtime_experiment_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_explicit_experiment_authorization_enforcement():
    assert _status(_request(experiment_authorization_state="missing")) == EXPERIMENT_AUTHORIZATION_MISSING


def test_explicit_experiment_intent_enforcement():
    assert _status(_request(experiment_intent_state="missing")) == EXPERIMENT_INTENT_MISSING


def test_explicit_experiment_scope_enforcement():
    assert _status(_request(experiment_scope_state="missing")) == EXPERIMENT_SCOPE_MISSING


def test_unsafe_experiment_scope_blocking():
    assert _status(_request(experiment_scope_state="production_scope")) == EXPERIMENT_SCOPE_UNSAFE


def test_invalid_consumption_mode_blocking():
    record = _build([_request(experiment_consumption_mode_state="runtime_default")])["limited_runtime_experiment_contracts"][0]
    assert record["limited_runtime_experiment_status"] == EXPERIMENT_CONSUMPTION_MODE_INVALID
    assert record["limited_runtime_consumption_mode_status"] == EXPERIMENT_CONSUMPTION_MODE_INVALID


def test_invalid_manifest_authority_blocking():
    assert _status(_request(experiment_manifest_authority_state="production_authoritative")) == EXPERIMENT_MANIFEST_AUTHORITY_INVALID


def test_production_routing_prohibition():
    record = _build([_request(production_routing_authorized_by_experiment=True)])["limited_runtime_experiment_contracts"][0]
    assert record["limited_runtime_experiment_status"] == EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED
    assert record["limited_runtime_consumption_mode_status"] == EXPERIMENT_PRODUCTION_ROUTING_PROHIBITED


def test_default_manifest_consumption_prohibition():
    record = _build([_request(runtime_manifest_consumption_enabled_by_default=True)])["limited_runtime_experiment_contracts"][0]
    assert record["limited_runtime_experiment_status"] == EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED
    assert record["limited_runtime_consumption_mode_status"] == EXPERIMENT_DEFAULT_MANIFEST_CONSUMPTION_PROHIBITED


def test_production_authoritative_manifest_treatment_prohibition():
    result = _build()
    record = result["limited_runtime_experiment_contracts"][0]
    assert record["production_authoritative_manifest_treatment"] is False
    assert result["summary"]["production_authoritative_manifest_treatment"] is False


def test_compatibility_enforcement():
    request = _request()
    base = dict(entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session(), safety_rollback_contract=_safety(), diff_audit_contract=_diff(), determinism_validation_contract=_determinism(), traceability_contract=_traceability(), replayability_contract=_replayability(), drift_detection_contract=_drift())
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "entrypoint_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_AUTHORIZATION_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "isolation_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_ISOLATION_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "session_boundary_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_SESSION_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "safety_rollback_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_SAFETY_ROLLBACK_COMPATIBILITY_MISSING
    assert "experiment_rollback_readiness_missing" in evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "safety_rollback_contract": None})["experiment_blockers"]
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "diff_audit_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_DIFF_AUDIT_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "determinism_validation_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_DETERMINISM_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "traceability_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_TRACEABILITY_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "replayability_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_REPLAYABILITY_COMPATIBILITY_MISSING
    assert evaluate_limited_runtime_consumption_experiment_contract(request, **{**base, "drift_detection_contract": None})["limited_runtime_experiment_status"] == EXPERIMENT_DRIFT_DETECTION_COMPATIBILITY_MISSING


def test_rollback_readiness_enforcement():
    safety = _safety()
    safety["runtime_rollback_status"] = "runtime_rollback_blocked"
    assert _build(safety=[safety])["limited_runtime_experiment_contracts"][0]["limited_runtime_experiment_status"] == EXPERIMENT_ROLLBACK_READINESS_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(experiment_authorization_state="missing", experiment_scope_state="unsafe", experiment_consumption_mode_state="bad", runtime_manifest_consumption_enabled_by_default=True)])["limited_runtime_experiment_contracts"][0]
    assert "experiment_authorization_missing" in record["experiment_blockers"]
    assert "experiment_scope_unsafe" in record["experiment_blockers"]
    assert "experiment_consumption_mode_invalid" in record["experiment_blockers"]
    assert "experiment_default_manifest_consumption_prohibited" in record["experiment_blockers"]


def test_no_silent_experiment_eligibility_or_implicit_runtime_consumption():
    record = _build()["limited_runtime_experiment_contracts"][0]
    assert record["metadata"]["silent_experiment_eligibility_allowed"] is False
    assert record["metadata"]["implicit_runtime_consumption_allowed"] is False
    assert record["metadata"]["fallback_experiment_logic_allowed"] is False


def test_no_default_manifest_consumption_activation_or_production_routing_changes():
    result = _build()
    assert result["safety_confirmations"]["limited_runtime_experiment_enables_runtime_manifest_consumption"] is False
    assert result["safety_confirmations"]["limited_runtime_experiment_authorizes_production_routing"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["summary"]["production_behavior_changed"] is False


def test_production_runtime_remains_prohibited():
    result = _build()
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["runtime_disabled_path_verification"]["production_runtime_prohibited"] is True


def test_classifiers_are_explicit():
    assert classify_limited_runtime_consumption_experiment_state(_request(), blockers=[]) == LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE
    assert classify_limited_runtime_consumption_experiment_state(_request(), blockers=["experiment_scope_unsafe"]) == EXPERIMENT_SCOPE_UNSAFE
    assert classify_limited_runtime_consumption_mode_state(_request(), blockers=[]) == LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE
    assert classify_limited_runtime_consumption_mode_state(_request(), blockers=["experiment_consumption_mode_invalid"]) == EXPERIMENT_CONSUMPTION_MODE_INVALID


def test_stable_report_generation():
    first = build_v3_2_limited_runtime_consumption_experiment_contracts_report()
    second = build_v3_2_limited_runtime_consumption_experiment_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["limited_runtime_consumption_experiment_contracts"]["deterministic_hash"] == second["limited_runtime_consumption_experiment_contracts"]["deterministic_hash"]


def _status(request):
    return _build([request])["limited_runtime_experiment_contracts"][0]["limited_runtime_experiment_status"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None, traceability=None, replayability=None, drift=None):
    return build_limited_runtime_consumption_experiment_contract(
        {"limited_runtime_experiment_requests": [_request()] if requests is None else requests, "deterministic_hash": "experiment-request-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
        runtime_safety_rollback_contracts={"runtime_safety_rollback_contracts": [_safety()] if safety is None else safety, "deterministic_hash": "safety-hash"},
        runtime_diff_audit_contracts={"runtime_diff_audit_contracts": [_diff()] if diffs is None else diffs, "deterministic_hash": "diff-hash"},
        runtime_determinism_validation_contracts={"runtime_determinism_validation_contracts": [_determinism()] if determinism is None else determinism, "deterministic_hash": "determinism-hash"},
        runtime_traceability_contracts={"runtime_traceability_contracts": [_traceability()] if traceability is None else traceability, "deterministic_hash": "traceability-hash"},
        runtime_replayability_contracts={"runtime_replayability_contracts": [_replayability()] if replayability is None else replayability, "deterministic_hash": "replayability-hash"},
        runtime_drift_detection_contracts={"runtime_drift_detection_contracts": [_drift()] if drift is None else drift, "deterministic_hash": "drift-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", experiment_authorization_state="experiment_authorized", experiment_intent_state="limited_runtime_consumption_experiment_intent_explicit", experiment_scope_state="non_production_isolated_reversible_limited_scope", experiment_consumption_mode_state="experimental_only_consumption_mode", experiment_manifest_authority_state="non_production_authoritative", runtime_manifest_consumption_enabled_by_default=False, production_routing_authorized_by_experiment=False):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "experiment_authorization_state": experiment_authorization_state, "experiment_intent_state": experiment_intent_state, "experiment_scope_state": experiment_scope_state, "experiment_eligibility_state": "experiment_eligibility_evaluated", "experiment_consumption_mode_state": experiment_consumption_mode_state, "experiment_manifest_authority_state": experiment_manifest_authority_state, "experiment_production_prohibition_state": "production_runtime_prohibited", "runtime_manifest_consumption_enabled_by_default": runtime_manifest_consumption_enabled_by_default, "production_routing_authorized_by_experiment": production_routing_authorized_by_experiment}


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
