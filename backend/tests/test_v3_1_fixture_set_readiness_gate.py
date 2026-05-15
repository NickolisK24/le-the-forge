from app.planner_adapters.v3_1.fixture_set_readiness_gate import build_fixture_set_readiness_gate
from scripts.report_v3_1_fixture_set_readiness_gate import build_v3_1_fixture_set_readiness_gate_report


def test_ready_classification():
    result = _gate(inputs=[_input("fixture_a")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")], workflows=[_workflow("fixture_a")])

    assert result["readiness_records"][0]["readiness_classification"] == "ready_for_approval_review"
    assert result["summary"]["ready_count"] == 1


def test_blocked_missing_inputs_classification():
    result = _gate(inputs=[], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")])

    assert result["readiness_records"][0]["readiness_classification"] == "blocked_missing_inputs"
    assert result["block_reason_counts"]["missing_reviewed_fixture_input"] == 1


def test_blocked_policy_failure_classification():
    result = _gate(inputs=[_input("fixture_a")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "unsupported")])

    assert result["readiness_records"][0]["readiness_classification"] == "blocked_policy_failure"
    assert result["block_reason_counts"]["policy_unsupported"] == 1


def test_blocked_malformed_inputs_classification():
    result = _gate(inputs=[_input("fixture_a", "malformed")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")])

    assert result["readiness_records"][0]["readiness_classification"] == "blocked_malformed_inputs"


def test_blocked_duplicate_inputs_classification():
    result = _gate(inputs=[_input("fixture_a", "duplicate")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")])

    assert result["readiness_records"][0]["readiness_classification"] == "blocked_duplicate_inputs"


def test_blocked_insufficient_review_classification():
    result = _gate(inputs=[_input("fixture_a", "unsupported")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")])

    assert result["readiness_records"][0]["readiness_classification"] == "blocked_insufficient_review"
    assert result["block_reason_counts"]["input_not_reviewed"] == 1


def test_deterministic_ordering():
    inputs = [_input("fixture_b"), _input("fixture_a")]
    sets = [_set("set_b", ["fixture_b"]), _set("set_a", ["fixture_a"])]
    policies = [_policy("set_b", "passes_policy"), _policy("set_a", "passes_policy")]

    first = _gate(inputs=inputs, sets=sets, policies=policies)
    second = _gate(inputs=list(reversed(inputs)), sets=list(reversed(sets)), policies=list(reversed(policies)))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["readiness_records"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_fixture_set_readiness_gate_report()
    second = build_v3_1_fixture_set_readiness_gate_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["fixture_set_readiness_gate"]["deterministic_hash"] == second["fixture_set_readiness_gate"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _gate(inputs=[_input("fixture_a")], sets=[_set("set_a", ["fixture_a"])], policies=[_policy("set_a", "passes_policy")], workflows=[_workflow("fixture_a")])
    record = result["readiness_records"][0]

    assert result["safety_confirmations"]["readiness_authorizes_production_routing"] is False
    assert record["non_production_authorization"]["readiness_authorizes_production_routing"] is False
    assert record["production_output_affected"] is False


def test_compatibility_with_reviewed_inputs_and_policy_layers():
    reviewed_inputs = {"deterministic_hash": "inputs", "normalized_fixture_inputs": [_input("fixture_a")]}
    persisted_sets = {"deterministic_hash": "sets", "fixture_sets": [_set("set_a", ["fixture_a"])]}
    policy = {"deterministic_hash": "policy", "evaluations": [_policy("set_a", "passes_policy")]}

    result = build_fixture_set_readiness_gate(
        reviewed_fixture_inputs=reviewed_inputs,
        persisted_fixture_sets=persisted_sets,
        review_policy_evaluation=policy,
        baseline_fixture_workflows={"deterministic_hash": "workflows", "fixtures": [_workflow("fixture_a")]},
    )

    assert result["input_consumption"]["reviewed_fixture_inputs_hash"] == "inputs"
    assert result["input_consumption"]["persisted_fixture_sets_hash"] == "sets"
    assert result["input_consumption"]["review_policy_evaluation_hash"] == "policy"


def _gate(inputs, sets, policies, workflows=None):
    return build_fixture_set_readiness_gate(
        reviewed_fixture_inputs={"normalized_fixture_inputs": inputs},
        persisted_fixture_sets={"fixture_sets": sets},
        review_policy_evaluation={"evaluations": policies},
        baseline_fixture_workflows={"fixtures": workflows or []},
    )


def _input(fixture_id, status="reviewed"):
    return {"normalized_fixture_id": fixture_id, "status": status, "production_output_affected": False}


def _set(set_id, fixture_ids):
    return {
        "fixture_set_id": set_id,
        "set_key": set_id,
        "associated_fixture_ids": fixture_ids,
        "unsupported": False,
        "blocked": False,
        "production_output_affected": False,
    }


def _policy(set_id, outcome):
    return {"fixture_set_id": set_id, "policy_outcome": outcome, "production_output_affected": False}


def _workflow(fixture_id, state="pending_review"):
    return {"fixture_id": fixture_id, "approval_state": state, "production_output_affected": False}
