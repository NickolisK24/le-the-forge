from app.planner_adapters.v3_1.admission_aware_readiness_gate import build_admission_aware_readiness_gate
from scripts.report_v3_1_admission_aware_readiness_gate import build_v3_1_admission_aware_readiness_gate_report


def test_policy_satisfied_for_review_unblocks_policy_readiness_failure():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"])]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a", "policy_satisfied_for_review")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )

    row = result["admission_aware_readiness_records"][0]
    assert row["final_admission_aware_readiness_status"] == "ready_for_approval_review"
    assert row["remaining_blockers"] == []
    assert row["readiness_reclassification"] == "policy_blocker_cleared_by_admission_aware_policy"


def test_unrelated_readiness_blockers_remain_blocked():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_insufficient_review", ["workflow_not_review_ready"])]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a", "policy_satisfied_for_review")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )

    row = result["admission_aware_readiness_records"][0]
    assert row["final_admission_aware_readiness_status"] == "blocked_insufficient_review"
    assert row["remaining_blockers"] == ["workflow_not_review_ready"]


def test_missing_admission_aware_policy_blocks():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"])]),
        admission_aware_policy_evaluation=_policy([]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )

    assert result["admission_aware_readiness_records"][0]["final_admission_aware_readiness_status"] == "blocked_missing_admission_aware_policy"


def test_invalid_admission_policy_state_blocks():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"])]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a", "unexpected_state")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )

    row = result["admission_aware_readiness_records"][0]
    assert row["final_admission_aware_readiness_status"] == "blocked_invalid_admission_policy_state"
    assert row["remaining_blockers"] == ["invalid_admission_policy_state_unexpected_state"]


def test_policy_failure_state_remains_blocked():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_blocked"])]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a", "blocked_policy_failure", ["blocked_fixture_set_visible"])]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )

    assert result["admission_aware_readiness_records"][0]["final_admission_aware_readiness_status"] == "blocked_policy_failure"


def test_deterministic_ordering():
    first = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([
            _readiness_record("set_b", "blocked_policy_failure", ["policy_unsupported"], ["fixture_b"]),
            _readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"], ["fixture_a"]),
        ]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_b"), _policy_record("set_a")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_b"), _input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_b", ["fixture_b"]), _set("set_a", ["fixture_a"])]),
    )
    second = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([
            _readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"], ["fixture_a"]),
            _readiness_record("set_b", "blocked_policy_failure", ["policy_unsupported"], ["fixture_b"]),
        ]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a"), _policy_record("set_b")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a"), _input("fixture_b")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"]), _set("set_b", ["fixture_b"])]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["admission_aware_readiness_records"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_admission_aware_readiness_gate_report()
    second = build_v3_1_admission_aware_readiness_gate_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["admission_aware_readiness_gate"]["deterministic_hash"] == second["admission_aware_readiness_gate"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_unsupported"])]),
        admission_aware_policy_evaluation=_policy([_policy_record("set_a")]),
        reviewed_fixture_inputs=_inputs([_input("fixture_a")]),
        persisted_fixture_sets=_sets([_set("set_a", ["fixture_a"])]),
    )
    row = result["admission_aware_readiness_records"][0]

    assert result["safety_confirmations"]["ready_for_approval_review_is_production_approval"] is False
    assert result["safety_confirmations"]["admission_aware_readiness_authorizes_production_routing"] is False
    assert row["non_production_authorization"]["readiness_authorizes_production_routing"] is False
    assert row["production_output_affected"] is False


def _readiness(records):
    return {
        "schema_version": "v3_1.fixture_set_readiness_gate.1",
        "deterministic_hash": "readiness-hash",
        "readiness_records": records,
    }


def _readiness_record(set_id, status, blockers, fixture_ids=None):
    fixture_ids = fixture_ids or ["fixture_a"]
    return {
        "fixture_set_id": set_id,
        "set_key": set_id,
        "readiness_classification": status,
        "associated_fixture_ids": fixture_ids,
        "block_reason_codes": blockers,
        "production_output_affected": False,
    }


def _policy(records):
    return {
        "schema_version": "v3_1.admission_aware_policy_evaluation.1",
        "deterministic_hash": "policy-hash",
        "admission_aware_policy_records": records,
    }


def _policy_record(set_id, status="policy_satisfied_for_review", blockers=None):
    return {
        "fixture_set_id": set_id,
        "admission_aware_policy_status": status,
        "remaining_blockers": blockers or [],
    }


def _inputs(records):
    return {
        "schema_version": "v3_1.reviewed_fixture_inputs.1",
        "deterministic_hash": "inputs-hash",
        "normalized_fixture_inputs": records,
    }


def _input(fixture_id, status="reviewed"):
    return {
        "normalized_fixture_id": fixture_id,
        "source_fixture_id": fixture_id,
        "status": status,
    }


def _sets(records):
    return {
        "schema_version": "v3_1.persisted_fixture_sets.1",
        "deterministic_hash": "sets-hash",
        "fixture_sets": records,
    }


def _set(set_id, fixture_ids):
    return {
        "fixture_set_id": set_id,
        "set_key": set_id,
        "associated_fixture_ids": fixture_ids,
    }
