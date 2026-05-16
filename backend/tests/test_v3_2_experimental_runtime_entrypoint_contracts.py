from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import (
    EXPERIMENTAL_RUNTIME_ELIGIBLE,
    PRODUCTION_RUNTIME_PROHIBITED,
    RUNTIME_DISABLED_BY_AUTHORIZATION,
    RUNTIME_DISABLED_BY_ISOLATION_FAILURE,
    RUNTIME_DISABLED_BY_POLICY,
    RUNTIME_ROLLBACK_REQUIRED,
    build_runtime_entrypoint_contract,
    classify_runtime_entrypoint_state,
    evaluate_runtime_entrypoint_contract,
)
from scripts.report_v3_2_experimental_runtime_entrypoint_contracts import build_v3_2_experimental_runtime_entrypoint_contracts_report


def test_deterministic_ordering():
    first = _build([_request("manifest_b", "set_b"), _request("manifest_a", "set_a")], [_closeout("manifest_b", "set_b"), _closeout("manifest_a", "set_a")])
    second = _build([_request("manifest_a", "set_a"), _request("manifest_b", "set_b")], [_closeout("manifest_a", "set_a"), _closeout("manifest_b", "set_b")])

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["runtime_entrypoint_contracts"]] == ["manifest_a", "manifest_b"]


def test_deterministic_hashes_and_repeat_run_stability():
    first = _build()
    second = _build()

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_production_runtime_prohibition():
    result = _build([_request(runtime_mode="production_runtime")])

    record = result["runtime_entrypoint_contracts"][0]
    assert record["runtime_entrypoint_status"] == PRODUCTION_RUNTIME_PROHIBITED
    assert "production_runtime_requested" in record["blockers"]
    assert record["production_runtime_classification"] == PRODUCTION_RUNTIME_PROHIBITED


def test_runtime_disabled_by_policy_behavior():
    result = _build([_request(runtime_policy_allows_entrypoint=False)])

    assert result["runtime_entrypoint_contracts"][0]["runtime_entrypoint_status"] == RUNTIME_DISABLED_BY_POLICY


def test_runtime_disabled_by_authorization_behavior():
    result = _build([_request(runtime_authorization_state="")])

    record = result["runtime_entrypoint_contracts"][0]
    assert record["runtime_entrypoint_status"] == RUNTIME_DISABLED_BY_AUTHORIZATION
    assert "runtime_authorization_missing" in record["blockers"]


def test_runtime_disabled_by_isolation_failure_behavior():
    result = _build([_request(runtime_isolation_state="shared_runtime")])

    assert result["runtime_entrypoint_contracts"][0]["runtime_entrypoint_status"] == RUNTIME_DISABLED_BY_ISOLATION_FAILURE


def test_blocker_accumulation_behavior():
    result = _build([_request(runtime_policy_allows_entrypoint=False, runtime_authorization_state="", runtime_isolation_state="")])

    blockers = result["runtime_entrypoint_contracts"][0]["blockers"]
    assert "runtime_policy_disabled" in blockers
    assert "runtime_authorization_missing" in blockers
    assert "runtime_isolation_missing" in blockers


def test_rollback_required_behavior():
    result = _build([_request(runtime_rollback_required=True)])

    record = result["runtime_entrypoint_contracts"][0]
    assert record["runtime_entrypoint_status"] == RUNTIME_ROLLBACK_REQUIRED
    assert "rollback_required" in record["blockers"]


def test_explicit_opt_in_enforcement():
    result = _build([_request(explicit_experimental_runtime_opt_in=False)])

    record = result["runtime_entrypoint_contracts"][0]
    assert record["runtime_entrypoint_status"] == RUNTIME_DISABLED_BY_POLICY
    assert "explicit_experimental_opt_in_missing" in record["blockers"]


def test_experimental_runtime_eligible_when_all_contract_states_are_explicit():
    result = _build()

    record = result["runtime_entrypoint_contracts"][0]
    assert record["runtime_entrypoint_status"] == EXPERIMENTAL_RUNTIME_ELIGIBLE
    assert record["runtime_manifest_consumption_enabled"] is False
    assert record["entrypoint_contract_authorizes_runtime_consumption"] is False


def test_no_silent_runtime_activation():
    record = evaluate_runtime_entrypoint_contract(_request(), closeout_record=_closeout())

    assert record["metadata"]["silent_runtime_activation_allowed"] is False
    assert record["metadata"]["fallback_authorization_allowed"] is False
    assert record["runtime_consumption_prohibition_state"] == "runtime_manifest_consumption_disabled"


def test_no_production_routing_changes():
    result = _build()

    assert result["safety_confirmations"]["entrypoint_contract_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["entrypoint_contract_authorizes_production_manifests"] is False
    assert result["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert result["summary"]["production_behavior_changed"] is False


def test_classify_runtime_entrypoint_state_is_explicit():
    assert classify_runtime_entrypoint_state(_request(), blockers=[]) == EXPERIMENTAL_RUNTIME_ELIGIBLE
    assert classify_runtime_entrypoint_state(_request(), blockers=["runtime_authorization_invalid"]) == RUNTIME_DISABLED_BY_AUTHORIZATION


def test_stable_report_generation():
    first = build_v3_2_experimental_runtime_entrypoint_contracts_report()
    second = build_v3_2_experimental_runtime_entrypoint_contracts_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["experimental_runtime_entrypoint_contracts"]["deterministic_hash"] == second["experimental_runtime_entrypoint_contracts"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def _build(requests=None, closeouts=None):
    return build_runtime_entrypoint_contract(
        {"runtime_entry_requests": [_request()] if requests is None else requests, "deterministic_hash": "requests-hash"},
        experimental_runtime_readiness_closeout={"closeout_records": [_closeout()] if closeouts is None else closeouts, "deterministic_hash": "closeout-hash"},
    )


def _request(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    runtime_mode="limited_experimental_runtime",
    runtime_authorization_state="non_production_authoritative",
    runtime_isolation_state="runtime_isolated",
    runtime_policy_allows_entrypoint=True,
    explicit_experimental_runtime_opt_in=True,
    runtime_rollback_eligibility=True,
    runtime_rollback_required=False,
):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_mode": runtime_mode,
        "runtime_authorization_state": runtime_authorization_state,
        "runtime_isolation_state": runtime_isolation_state,
        "runtime_policy_allows_entrypoint": runtime_policy_allows_entrypoint,
        "explicit_experimental_runtime_opt_in": explicit_experimental_runtime_opt_in,
        "runtime_rollback_eligibility": runtime_rollback_eligibility,
        "runtime_rollback_required": runtime_rollback_required,
        "runtime_activation_intent": "contract_evaluation_only",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
    }


def _closeout(manifest_id="manifest_a", fixture_set_id="set_a", status="ready_for_future_limited_experimental_runtime_phase"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "closeout_readiness_status": status,
        "closeout_readiness_authorizes_runtime_routing": False,
        "closeout_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
    }
