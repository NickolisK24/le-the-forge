from app.planner_adapters.v3_2.experimental_runtime_closeout_readiness_audit import (
    DEFAULT_RUNTIME_MANIFEST_CONSUMPTION_STILL_DISABLED,
    PRODUCTION_AUTHORITATIVE_MANIFEST_TREATMENT_STILL_PROHIBITED,
    PRODUCTION_RUNTIME_STILL_PROHIBITED,
    UNRESOLVED_BLOCKERS_PRESENT,
    UNRESOLVED_LIMITATIONS_PRESENT,
    UNRESOLVED_RISKS_PRESENT,
    V3_2_CLOSEOUT_BLOCKED,
    V3_2_CLOSEOUT_SATISFIED,
    V3_2_CONTRACTS_INCOMPATIBLE,
    V3_2_PHASE_COVERAGE_INCOMPLETE,
    V3_3_BLOCKED,
    V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY,
    V3_3_READY_FOR_PLANNING,
    build_experimental_runtime_closeout_readiness_audit,
    classify_v3_2_closeout_state,
    classify_v3_3_readiness_state,
)
from scripts.report_v3_2_experimental_runtime_closeout_readiness_audit import (
    build_v3_2_experimental_runtime_closeout_readiness_audit_report,
)


def test_deterministic_ordering():
    first = _build(
        entrypoints=[_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")],
        kill_switch=[_kill_switch("manifest_b", "set_b"), _kill_switch("manifest_a", "set_a")],
    )
    second = _build(
        entrypoints=[_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")],
        kill_switch=[_kill_switch("manifest_a", "set_a"), _kill_switch("manifest_b", "set_b")],
    )
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["experimental_runtime_closeout_readiness_audits"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_complete_phase_1_through_phase_11_coverage_enforcement():
    record = _record()
    assert record["phase_coverage_state"] == "v3_2_phase_coverage_complete"
    assert record["contract_compatibility_state"] == "v3_2_contracts_compatible"
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_SATISFIED
    assert record["v3_3_readiness_status"] == V3_3_READY_FOR_PLANNING


def test_missing_phase_coverage_fails_visibly():
    result = _build(kill_switch=[])
    record = result["experimental_runtime_closeout_readiness_audits"][0]
    assert record["phase_coverage_state"] == V3_2_PHASE_COVERAGE_INCOMPLETE
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "phase_11_kill_switch_coverage_missing" in record["unresolved_blockers"]


def test_contract_incompatibility_fails_visibly():
    record = _record(isolations=[{**_isolation(), "runtime_isolation_status": "runtime_isolation_blocked"}])
    assert record["contract_compatibility_state"] == V3_2_CONTRACTS_INCOMPATIBLE
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "phase_2_isolation_contract_incompatible" in record["unresolved_blockers"]


def test_production_routing_authorization_fails_closeout():
    record = _record(kill_switch=[{**_kill_switch(), "production_routing_authorized": True}])
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "production_routing_authorization_detected" in record["unresolved_blockers"]


def test_default_runtime_manifest_consumption_enablement_fails_closeout():
    record = _record(kill_switch=[{**_kill_switch(), "runtime_manifest_consumption_enabled": True}])
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "default_runtime_manifest_consumption_enabled" in record["unresolved_blockers"]


def test_production_authoritative_manifest_treatment_fails_closeout():
    record = _record(kill_switch=[{**_kill_switch(), "production_authoritative_manifest_treatment": True}])
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "production_authoritative_manifest_treatment_detected" in record["unresolved_blockers"]


def test_unresolved_blockers_are_reported_explicitly():
    record = _record(context={"unresolved_blockers": ["manual_closeout_review_required"]})
    assert record["unresolved_blocker_state"] == UNRESOLVED_BLOCKERS_PRESENT
    assert record["v3_2_closeout_status"] == V3_2_CLOSEOUT_BLOCKED
    assert "manual_closeout_review_required" in record["unresolved_blockers"]


def test_unresolved_risks_are_reported_explicitly():
    record = _record(context={"unresolved_risks": ["future_runtime_scope_requires_review"]})
    assert record["unresolved_risk_state"] == UNRESOLVED_RISKS_PRESENT
    assert record["v3_3_readiness_status"] == V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY


def test_unresolved_limitations_are_reported_explicitly():
    record = _record()
    assert record["unresolved_limitation_state"] == UNRESOLVED_LIMITATIONS_PRESENT
    assert "production runtime routing remains out of scope" in record["unresolved_limitations"]


def test_v3_3_readiness_classification_is_explicit():
    assert classify_v3_3_readiness_state(closeout_status=V3_2_CLOSEOUT_SATISFIED) == V3_3_READY_FOR_PLANNING
    assert classify_v3_3_readiness_state(closeout_status=V3_2_CLOSEOUT_BLOCKED) == V3_3_BLOCKED
    assert classify_v3_3_readiness_state(closeout_status=V3_2_CLOSEOUT_SATISFIED, unresolved_risks=["risk"]) == V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY
    assert classify_v3_2_closeout_state(phase_coverage_state="v3_2_phase_coverage_complete", contract_compatibility_state="v3_2_contracts_compatible") == V3_2_CLOSEOUT_SATISFIED


def test_v3_3_readiness_does_not_imply_production_enablement():
    record = _record()
    assert record["v3_3_readiness_authorizes_production_enablement"] is False
    assert record["production_routing_authorized"] is False
    assert record["runtime_manifest_consumption_enabled"] is False


def test_no_silent_readiness_approval_or_implicit_production_readiness():
    record = _record()
    assert record["metadata"]["silent_readiness_approval_allowed"] is False
    assert record["metadata"]["implicit_production_readiness_allowed"] is False
    assert record["metadata"]["fallback_closeout_logic_allowed"] is False


def test_no_new_runtime_or_planner_behavior():
    record = _record()
    assert record["new_runtime_behavior_added"] is False
    assert record["new_runtime_consumption_behavior_added"] is False
    assert record["new_planner_behavior_added"] is False


def test_no_production_routing_changes():
    result = _build()
    assert result["safety_confirmations"]["production_planner_routing_changed"] is False
    assert result["summary"]["production_behavior_changed"] is False


def test_production_runtime_remains_prohibited():
    record = _record()
    assert record["production_routing_prohibition_state"] == PRODUCTION_RUNTIME_STILL_PROHIBITED
    assert record["production_runtime_classification"] == "production_runtime_prohibited"


def test_default_runtime_manifest_consumption_remains_disabled():
    record = _record()
    assert record["default_manifest_consumption_disabled_state"] == DEFAULT_RUNTIME_MANIFEST_CONSUMPTION_STILL_DISABLED
    assert record["runtime_manifest_consumption_enabled"] is False


def test_production_authoritative_manifest_treatment_remains_prohibited():
    record = _record()
    assert record["production_authoritative_manifest_prohibition_state"] == PRODUCTION_AUTHORITATIVE_MANIFEST_TREATMENT_STILL_PROHIBITED
    assert record["production_authoritative_manifest_treatment"] is False


def test_stable_report_generation():
    first = build_v3_2_experimental_runtime_closeout_readiness_audit_report()
    second = build_v3_2_experimental_runtime_closeout_readiness_audit_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["experimental_runtime_closeout_readiness_audit"]["deterministic_hash"] == second["experimental_runtime_closeout_readiness_audit"]["deterministic_hash"]


def _record(**overrides):
    return _build(**overrides)["experimental_runtime_closeout_readiness_audits"][0]


def _build(entrypoints=None, isolations=None, sessions=None, safety=None, diffs=None, determinism=None, traceability=None, replayability=None, drift=None, experiment=None, kill_switch=None, context=None):
    return build_experimental_runtime_closeout_readiness_audit(
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
        runtime_kill_switch_contracts={"runtime_kill_switch_contracts": [_kill_switch()] if kill_switch is None else kill_switch, "deterministic_hash": "kill-switch-hash"},
        closeout_context=context,
    )


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_entrypoint_status": "experimental_runtime_eligible", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _safety(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_safety_status": "runtime_safety_satisfied", "runtime_rollback_status": "runtime_rollback_ready", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _diff(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_diff_audit_status": "runtime_diff_audit_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _determinism(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_determinism_status": "runtime_determinism_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _traceability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_traceability_status": "runtime_traceability_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _replayability(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_replayability_status": "runtime_replayability_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _drift(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_drift_detection_status": "runtime_drift_not_detected", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _experiment(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "limited_runtime_experiment_status": "limited_runtime_experiment_eligible", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}


def _kill_switch(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_kill_switch_status": "runtime_kill_switch_satisfied", "production_routing_authorized": False, "runtime_manifest_consumption_enabled": False, "production_authoritative_manifest_treatment": False}
