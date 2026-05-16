from app.planner_adapters.v3_2.runtime_session_boundary_contracts import (
    RUNTIME_SESSION_BOUNDARY_SATISFIED,
    SESSION_AUTHORIZATION_CONTEXT_MISSING,
    SESSION_INITIALIZATION_BLOCKED,
    SESSION_ISOLATION_CONTEXT_MISSING,
    SESSION_LEAKAGE_BLOCKED,
    SESSION_MUTATION_BLOCKED,
    SESSION_OWNERSHIP_CROSSOVER_BLOCKED,
    SESSION_REUSE_BLOCKED,
    SESSION_ROLLBACK_CONTAINMENT_REQUIRED,
    SESSION_TERMINATION_REQUIRED,
    build_runtime_session_boundary_contract,
    classify_runtime_session_boundary_state,
    evaluate_runtime_session_boundary_contract,
)
from scripts.report_v3_2_runtime_session_boundary_contracts import build_v3_2_runtime_session_boundary_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")], [_isolation("manifest_b", "set_b"), _isolation("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")], [_isolation("manifest_a", "set_a"), _isolation("manifest_b", "set_b")])

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_session_boundary_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    assert _build()["deterministic_hash"] == _build()["deterministic_hash"]


def test_phase_1_entrypoint_compatibility():
    result = _build()
    assert result["phase_1_entrypoint_compatibility"]["requires_experimental_runtime_eligible"] is True
    assert result["runtime_session_boundary_contracts"][0]["entrypoint_contract_status"] == "experimental_runtime_eligible"


def test_phase_2_isolation_compatibility():
    result = _build()
    assert result["phase_2_isolation_compatibility"]["requires_runtime_isolation_satisfied"] is True
    assert result["runtime_session_boundary_contracts"][0]["isolation_contract_status"] == "runtime_isolation_satisfied"


def test_session_initialization_blocking():
    assert _build([_request(session_initialization_state="implicit")])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_INITIALIZATION_BLOCKED


def test_missing_authorization_context_fails_visibly():
    record = _build([_request(session_authorization_context="")])["runtime_session_boundary_contracts"][0]
    assert record["runtime_session_boundary_status"] == SESSION_AUTHORIZATION_CONTEXT_MISSING
    assert "session_authorization_context_missing" in record["blockers"]


def test_missing_isolation_context_fails_visibly():
    record = _build([_request(session_isolation_context="")])["runtime_session_boundary_contracts"][0]
    assert record["runtime_session_boundary_status"] == SESSION_ISOLATION_CONTEXT_MISSING
    assert "session_isolation_context_missing" in record["blockers"]


def test_session_ownership_crossover_blocking():
    assert _build([_request(session_ownership_crossover=True)])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_OWNERSHIP_CROSSOVER_BLOCKED


def test_session_mutation_blocking():
    assert _build([_request(session_mutates_production_planner=True)])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_MUTATION_BLOCKED


def test_session_reuse_blocking():
    assert _build([_request(session_reuse_prohibition_state="session_reuse_unscoped")])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_REUSE_BLOCKED


def test_session_leakage_blocking():
    assert _build([_request(session_state_leakage_detected=True)])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_LEAKAGE_BLOCKED


def test_session_termination_required_behavior():
    assert _build([_request(session_termination_requirement_state="termination_not_required")])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_TERMINATION_REQUIRED


def test_rollback_containment_required_behavior():
    assert _build([_request(rollback_containment_state="rollback_not_contained")])["runtime_session_boundary_contracts"][0]["runtime_session_boundary_status"] == SESSION_ROLLBACK_CONTAINMENT_REQUIRED


def test_blocker_accumulation_behavior():
    record = _build([_request(session_ownership_crossover=True, session_mutates_production_planner=True, session_state_leakage_detected=True)])["runtime_session_boundary_contracts"][0]
    assert "session_ownership_crossover" in record["blockers"]
    assert "session_mutation_requested" in record["blockers"]
    assert "session_state_leakage" in record["blockers"]


def test_no_silent_runtime_session_activation():
    record = evaluate_runtime_session_boundary_contract(_request(), entrypoint_contract=_entrypoint(), isolation_contract=_isolation())
    assert record["metadata"]["silent_runtime_session_activation_allowed"] is False
    assert record["session_boundary_authorizes_runtime_consumption"] is False


def test_no_implicit_session_reuse():
    result = _build()
    assert result["runtime_disabled_path_verification"]["implicit_session_reuse_allowed"] is False


def test_no_production_routing_changes():
    result = _build()
    assert result["safety_confirmations"]["session_boundary_authorizes_production_routing"] is False
    assert result["summary"]["production_behavior_changed"] is False


def test_production_runtime_remains_prohibited():
    result = _build()
    assert result["runtime_session_boundary_contracts"][0]["production_runtime_classification"] == "production_runtime_prohibited"
    assert result["runtime_disabled_path_verification"]["production_runtime_prohibited"] is True


def test_default_runtime_manifest_consumption_remains_disabled():
    result = _build()
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert result["safety_confirmations"]["session_boundary_enables_runtime_manifest_consumption"] is False


def test_classify_runtime_session_boundary_state_is_explicit():
    assert classify_runtime_session_boundary_state(_request(), blockers=[]) == RUNTIME_SESSION_BOUNDARY_SATISFIED
    assert classify_runtime_session_boundary_state(_request(), blockers=["session_state_leakage"]) == SESSION_LEAKAGE_BLOCKED


def test_stable_report_generation():
    first = build_v3_2_runtime_session_boundary_contracts_report()
    second = build_v3_2_runtime_session_boundary_contracts_report()
    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_session_boundary_contracts"]["deterministic_hash"] == second["runtime_session_boundary_contracts"]["deterministic_hash"]


def _build(requests=None, entrypoints=None, isolations=None):
    return build_runtime_session_boundary_contract(
        {"runtime_session_requests": [_request()] if requests is None else requests, "deterministic_hash": "session-requests-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
        runtime_isolation_contracts={"runtime_isolation_contracts": [_isolation()] if isolations is None else isolations, "deterministic_hash": "isolation-hash"},
    )


def _request(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    session_initialization_state="session_initialization_explicit",
    explicit_experimental_runtime_opt_in=True,
    session_authorization_context="non_production_authoritative",
    session_isolation_context="runtime_isolated",
    session_lifecycle_state="session_lifecycle_initialized_for_contract_only",
    session_ownership_state="session_ownership_isolated",
    session_mutation_prohibition_state="session_mutation_prohibited",
    session_reuse_prohibition_state="session_reuse_prohibited",
    session_leakage_prohibition_state="session_leakage_prohibited",
    session_termination_requirement_state="session_termination_required_and_explicit",
    rollback_containment_state="rollback_contained",
    session_ownership_crossover=False,
    session_mutates_production_planner=False,
    session_state_leakage_detected=False,
):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "session_initialization_state": session_initialization_state,
        "explicit_experimental_runtime_opt_in": explicit_experimental_runtime_opt_in,
        "session_authorization_context": session_authorization_context,
        "session_isolation_context": session_isolation_context,
        "session_lifecycle_state": session_lifecycle_state,
        "session_ownership_state": session_ownership_state,
        "session_mutation_prohibition_state": session_mutation_prohibition_state,
        "session_reuse_prohibition_state": session_reuse_prohibition_state,
        "session_leakage_prohibition_state": session_leakage_prohibition_state,
        "session_termination_requirement_state": session_termination_requirement_state,
        "rollback_containment_state": rollback_containment_state,
        "session_ownership_crossover": session_ownership_crossover,
        "session_mutates_production_planner": session_mutates_production_planner,
        "session_state_leakage_detected": session_state_leakage_detected,
    }


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_entrypoint_status": "experimental_runtime_eligible",
        "runtime_authorization_state": "non_production_authoritative",
        "runtime_manifest_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": "production_runtime_prohibited",
        "explicit_experimental_runtime_opt_in": True,
    }


def _isolation(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_isolation_status": "runtime_isolation_satisfied",
        "runtime_manifest_consumption_enabled": False,
        "production_routing_authorized": False,
    }
