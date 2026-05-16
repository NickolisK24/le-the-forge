from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    ENTRYPOINT_COMPATIBILITY_MISSING,
    ISOLATION_COMPATIBILITY_MISSING,
    PRODUCTION_IMPACT_BLOCKED,
    ROLLBACK_REVERSIBILITY_MISSING,
    ROLLBACK_TRIGGER_MISSING,
    RUNTIME_ROLLBACK_BLOCKED,
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
    SESSION_BOUNDARY_COMPATIBILITY_MISSING,
    UNSAFE_SIDE_EFFECT_BLOCKED,
    build_runtime_safety_rollback_contract,
    classify_runtime_rollback_state,
    classify_runtime_safety_state,
    evaluate_runtime_safety_rollback_contract,
)
from scripts.report_v3_2_runtime_safety_rollback_contracts import build_v3_2_runtime_safety_rollback_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")], [_session("manifest_b", "set_b"), _session("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")], [_session("manifest_a", "set_a"), _session("manifest_b", "set_b")])
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_safety_rollback_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_phase_compatibility_summaries():
    result = _build()
    assert result["phase_1_entrypoint_compatibility"]["requires_experimental_runtime_eligible"] is True
    assert result["phase_2_isolation_compatibility"]["requires_runtime_isolation_satisfied"] is True
    assert result["phase_3_session_boundary_compatibility"]["requires_session_boundary_satisfied"] is True


def test_runtime_safety_blocking():
    result = _build([_request(runtime_safety_state="runtime_safety_unknown")])
    assert result["runtime_safety_rollback_contracts"][0]["runtime_safety_status"] != RUNTIME_SAFETY_SATISFIED


def test_rollback_readiness_satisfied_behavior():
    assert _build()["runtime_safety_rollback_contracts"][0]["runtime_rollback_status"] == RUNTIME_ROLLBACK_READY


def test_rollback_readiness_blocked_behavior():
    assert _build([_request(rollback_readiness_state="not_ready")])["runtime_safety_rollback_contracts"][0]["runtime_rollback_status"] == RUNTIME_ROLLBACK_BLOCKED


def test_rollback_trigger_missing_behavior():
    assert _build([_request(rollback_trigger_state="missing")])["runtime_safety_rollback_contracts"][0]["runtime_rollback_status"] == ROLLBACK_TRIGGER_MISSING


def test_rollback_reversibility_missing_behavior():
    assert _build([_request(rollback_reversibility_state="irreversible")])["runtime_safety_rollback_contracts"][0]["runtime_rollback_status"] == ROLLBACK_REVERSIBILITY_MISSING


def test_unsafe_side_effect_blocking():
    assert _build([_request(unsafe_side_effect_detected=True)])["runtime_safety_rollback_contracts"][0]["runtime_safety_status"] == UNSAFE_SIDE_EFFECT_BLOCKED


def test_production_impact_blocking():
    assert _build([_request(production_impact_detected=True)])["runtime_safety_rollback_contracts"][0]["runtime_safety_status"] == PRODUCTION_IMPACT_BLOCKED


def test_missing_entrypoint_compatibility_fails_visibly():
    record = evaluate_runtime_safety_rollback_contract(_request(), entrypoint_contract=None, isolation_contract=_isolation(), session_boundary_contract=_session())
    assert record["runtime_safety_status"] == ENTRYPOINT_COMPATIBILITY_MISSING


def test_missing_isolation_compatibility_fails_visibly():
    record = evaluate_runtime_safety_rollback_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=None, session_boundary_contract=_session())
    assert record["runtime_safety_status"] == ISOLATION_COMPATIBILITY_MISSING


def test_missing_session_boundary_compatibility_fails_visibly():
    record = evaluate_runtime_safety_rollback_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=None)
    assert record["runtime_safety_status"] == SESSION_BOUNDARY_COMPATIBILITY_MISSING


def test_blocker_accumulation_behavior():
    record = _build([_request(unsafe_side_effect_detected=True, production_impact_detected=True, rollback_trigger_state="missing")])["runtime_safety_rollback_contracts"][0]
    assert "unsafe_side_effect" in record["safety_blockers"]
    assert "production_impact" in record["safety_blockers"]
    assert "rollback_trigger_missing" in record["rollback_blockers"]


def test_no_silent_runtime_safety_approval_or_implicit_rollback():
    record = evaluate_runtime_safety_rollback_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation(), session_boundary_contract=_session())
    assert record["metadata"]["silent_runtime_safety_approval_allowed"] is False
    assert record["metadata"]["implicit_rollback_readiness_allowed"] is False


def test_no_irreversible_runtime_side_effects():
    result = _build()
    assert result["safety_confirmations"]["safety_contract_allows_irreversible_side_effects"] is False


def test_no_production_routing_changes_and_runtime_prohibited():
    result = _build()
    assert result["safety_confirmations"]["safety_contract_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["safety_contract_enables_runtime_manifest_consumption"] is False


def test_classifiers_are_explicit():
    assert classify_runtime_safety_state(_request(), blockers=[]) == RUNTIME_SAFETY_SATISFIED
    assert classify_runtime_safety_state(_request(), blockers=["production_impact"]) == PRODUCTION_IMPACT_BLOCKED
    assert classify_runtime_rollback_state(_request(), blockers=[]) == RUNTIME_ROLLBACK_READY
    assert classify_runtime_rollback_state(_request(), blockers=["rollback_trigger_missing"]) == ROLLBACK_TRIGGER_MISSING


def test_stable_report_generation():
    first = build_v3_2_runtime_safety_rollback_contracts_report()
    second = build_v3_2_runtime_safety_rollback_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_safety_rollback_contracts"]["deterministic_hash"] == second["runtime_safety_rollback_contracts"]["deterministic_hash"]


def _build(requests=None, entrypoints=None, isolations=None, sessions=None):
    return build_runtime_safety_rollback_contract(
        {"runtime_safety_requests": [_request()] if requests is None else requests, "deterministic_hash": "safety-requests-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
        runtime_session_boundary_contracts={"runtime_session_boundary_contracts": [_session()] if sessions is None else sessions, "deterministic_hash": "session-hash"},
    )


def _request(manifest_id="manifest_a", fixture_set_id="set_a", runtime_safety_state="runtime_safety_explicitly_satisfied", rollback_readiness_state="rollback_readiness_explicitly_ready", rollback_containment_state="rollback_contained", rollback_trigger_state="rollback_trigger_explicit", rollback_reversibility_state="rollback_reversible", unsafe_side_effect_prohibition_state="unsafe_side_effects_prohibited", production_impact_prohibition_state="production_impact_prohibited", unsafe_side_effect_detected=False, production_impact_detected=False):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_safety_state": runtime_safety_state,
        "rollback_readiness_state": rollback_readiness_state,
        "rollback_containment_state": rollback_containment_state,
        "rollback_trigger_state": rollback_trigger_state,
        "rollback_reversibility_state": rollback_reversibility_state,
        "unsafe_side_effect_prohibition_state": unsafe_side_effect_prohibition_state,
        "production_impact_prohibition_state": production_impact_prohibition_state,
        "session_rollback_compatibility_state": "session_rollback_compatible",
        "isolation_rollback_compatibility_state": "isolation_rollback_compatible",
        "entrypoint_rollback_compatibility_state": "entrypoint_rollback_compatible",
        "unsafe_side_effect_detected": unsafe_side_effect_detected,
        "production_impact_detected": production_impact_detected,
    }


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_entrypoint_status": "experimental_runtime_eligible"}


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_isolation_status": "runtime_isolation_satisfied"}


def _session(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "runtime_session_boundary_status": "runtime_session_boundary_satisfied"}
