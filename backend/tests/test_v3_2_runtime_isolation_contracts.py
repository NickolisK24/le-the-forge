from app.planner_adapters.v3_2.runtime_isolation_contracts import (
    MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED,
    PLANNER_OWNERSHIP_CROSSOVER_BLOCKED,
    PRODUCTION_ROUTING_CROSSOVER_BLOCKED,
    ROLLBACK_CONTAINMENT_REQUIRED,
    RUNTIME_ISOLATION_SATISFIED,
    RUNTIME_MUTATION_BLOCKED,
    SIDE_EFFECT_BOUNDARY_BLOCKED,
    build_runtime_isolation_contract,
    classify_runtime_isolation_state,
    evaluate_runtime_isolation_contract,
)
from scripts.report_v3_2_runtime_isolation_contracts import build_v3_2_runtime_isolation_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_entrypoint("manifest_b", "set_b"), _entrypoint("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_entrypoint("manifest_a", "set_a"), _entrypoint("manifest_b", "set_b")])

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_isolation_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    first = _build()
    second = _build()

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_phase_1_entrypoint_compatibility():
    result = _build()

    record = result["runtime_isolation_contracts"][0]
    assert record["entrypoint_contract_status"] == "experimental_runtime_eligible"
    assert result["phase_1_entrypoint_compatibility"]["production_runtime_prohibited"] is True


def test_production_routing_crossover_blocking():
    result = _build([_request(production_routing_crossover=True)])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == PRODUCTION_ROUTING_CROSSOVER_BLOCKED


def test_manifest_consumption_crossover_blocking():
    result = _build([_request(manifest_consumption_crossover=True, manifest_consumption_scope="production")])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED


def test_planner_ownership_crossover_blocking():
    result = _build([_request(planner_ownership_mutation_requested=True)])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == PLANNER_OWNERSHIP_CROSSOVER_BLOCKED


def test_runtime_mutation_blocking():
    result = _build([_request(runtime_mutation_requested=True)])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == RUNTIME_MUTATION_BLOCKED


def test_side_effect_boundary_blocking():
    result = _build([_request(runtime_side_effect_prohibition_state="side_effects_external")])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == SIDE_EFFECT_BOUNDARY_BLOCKED


def test_rollback_containment_required_behavior():
    result = _build([_request(rollback_containment_state="rollback_not_contained")])

    assert result["runtime_isolation_contracts"][0]["runtime_isolation_status"] == ROLLBACK_CONTAINMENT_REQUIRED


def test_missing_isolation_inputs_fail_visibly():
    result = _build([])

    record = result["runtime_isolation_contracts"][0]
    assert record["runtime_isolation_status"] != RUNTIME_ISOLATION_SATISFIED
    assert "missing_isolation_inputs" in record["blockers"]


def test_missing_phase_1_authorization_context_fails_visibly():
    record = evaluate_runtime_isolation_contract(_request(), entrypoint_contract=None)

    assert "missing_phase_1_entrypoint_authorization_context" in record["blockers"]


def test_blocker_accumulation_behavior():
    result = _build([_request(production_routing_crossover=True, planner_ownership_mutation_requested=True, runtime_mutation_requested=True)])

    blockers = result["runtime_isolation_contracts"][0]["blockers"]
    assert "production_routing_crossover" in blockers
    assert "planner_ownership_crossover" in blockers
    assert "runtime_mutation_requested" in blockers


def test_no_silent_runtime_activation():
    result = _build()
    record = result["runtime_isolation_contracts"][0]

    assert record["metadata"]["silent_runtime_activation_allowed"] is False
    assert record["metadata"]["fallback_isolation_allowed"] is False
    assert record["isolation_contract_authorizes_runtime_consumption"] is False


def test_no_implicit_manifest_consumption():
    result = _build()
    record = result["runtime_isolation_contracts"][0]

    assert record["metadata"]["implicit_manifest_consumption_allowed"] is False
    assert result["runtime_disabled_path_verification"]["implicit_manifest_consumption_allowed"] is False


def test_no_production_routing_changes_and_runtime_remains_prohibited():
    result = _build()

    assert result["safety_confirmations"]["isolation_contract_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_production_runtime_remains_prohibited():
    result = _build()

    assert result["runtime_isolation_contracts"][0]["production_runtime_classification"] == "production_runtime_prohibited"
    assert result["runtime_disabled_path_verification"]["production_runtime_prohibited"] is True


def test_classify_runtime_isolation_state_is_explicit():
    assert classify_runtime_isolation_state(_request(), blockers=[]) == RUNTIME_ISOLATION_SATISFIED
    assert classify_runtime_isolation_state(_request(), blockers=["manifest_consumption_crossover"]) == MANIFEST_CONSUMPTION_CROSSOVER_BLOCKED


def test_stable_report_generation():
    first = build_v3_2_runtime_isolation_contracts_report()
    second = build_v3_2_runtime_isolation_contracts_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["runtime_isolation_contracts"]["deterministic_hash"] == second["runtime_isolation_contracts"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def _build(requests=None, entrypoints=None):
    return build_runtime_isolation_contract(
        {"runtime_isolation_requests": [_request()] if requests is None else requests, "deterministic_hash": "isolation-requests-hash"},
        experimental_runtime_entrypoint_contracts={"runtime_entrypoint_contracts": [_entrypoint()] if entrypoints is None else entrypoints, "deterministic_hash": "entrypoint-hash"},
    )


def _request(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    runtime_isolation_boundary_state="isolation_boundary_satisfied",
    production_routing_separation_state="production_routing_separated",
    manifest_consumption_separation_state="manifest_consumption_separated",
    manifest_consumption_scope="experimental_only",
    manifest_authorization_state="non_production_authoritative",
    implicit_manifest_consumption=False,
    planner_ownership_separation_state="planner_ownership_separated",
    runtime_mutation_prohibition_state="runtime_mutation_prohibited",
    experimental_only_execution_scope="experimental_only",
    runtime_side_effect_prohibition_state="side_effects_prohibited",
    rollback_containment_state="rollback_contained",
    production_routing_crossover=False,
    manifest_consumption_crossover=False,
    planner_ownership_mutation_requested=False,
    runtime_mutation_requested=False,
):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_isolation_boundary_state": runtime_isolation_boundary_state,
        "production_routing_separation_state": production_routing_separation_state,
        "manifest_consumption_separation_state": manifest_consumption_separation_state,
        "manifest_consumption_scope": manifest_consumption_scope,
        "manifest_authorization_state": manifest_authorization_state,
        "implicit_manifest_consumption": implicit_manifest_consumption,
        "planner_ownership_separation_state": planner_ownership_separation_state,
        "runtime_mutation_prohibition_state": runtime_mutation_prohibition_state,
        "experimental_only_execution_scope": experimental_only_execution_scope,
        "runtime_side_effect_prohibition_state": runtime_side_effect_prohibition_state,
        "rollback_containment_state": rollback_containment_state,
        "production_routing_crossover": production_routing_crossover,
        "manifest_consumption_crossover": manifest_consumption_crossover,
        "planner_ownership_mutation_requested": planner_ownership_mutation_requested,
        "runtime_mutation_requested": runtime_mutation_requested,
    }


def _entrypoint(manifest_id="manifest_a", fixture_set_id="set_a", status="experimental_runtime_eligible"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_entrypoint_status": status,
        "runtime_authorization_state": "non_production_authoritative",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": "production_runtime_prohibited",
        "explicit_experimental_runtime_opt_in": True,
    }
