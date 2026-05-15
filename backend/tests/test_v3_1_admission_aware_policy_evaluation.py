from app.planner_adapters.v3_1.admission_aware_policy_evaluation import build_admission_aware_policy_evaluation
from scripts.report_v3_1_admission_aware_policy_evaluation import build_v3_1_admission_aware_policy_evaluation_report


def test_admitted_source_converts_unsupported_source_blocker_to_satisfied_for_review():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a", "admitted_for_review")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a", status="unsupported")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )

    row = result["admission_aware_policy_records"][0]
    assert row["admission_aware_policy_status"] == "policy_satisfied_for_review"
    assert row["remaining_blockers"] == []
    assert row["source_admission_impact"] == "unsupported_source_reclassified_by_admission"


def test_non_admitted_source_remains_blocked():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a", "blocked_missing_review_evidence")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )

    assert result["admission_aware_policy_records"][0]["admission_aware_policy_status"] == "blocked_source_not_admitted"


def test_missing_admission_record_blocks():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )

    assert result["admission_aware_policy_records"][0]["admission_aware_policy_status"] == "blocked_missing_admission_record"


def test_missing_fixture_input_blocks():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a", "admitted_for_review")]),
        reviewed_fixture_inputs=_inputs([]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )

    assert result["admission_aware_policy_records"][0]["admission_aware_policy_status"] == "blocked_missing_fixture_input"


def test_unrelated_policy_failures_remain_blocked():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a", "admitted_for_review")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "blocked", ["blocked_fixture_set_visible"])]),
    )

    row = result["admission_aware_policy_records"][0]
    assert row["admission_aware_policy_status"] == "blocked_policy_failure"
    assert row["remaining_blockers"] == ["blocked_fixture_set_visible"]


def test_invalid_review_state_blocks():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a", "admitted_for_review")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a", status="malformed")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )

    assert result["admission_aware_policy_records"][0]["admission_aware_policy_status"] == "blocked_invalid_review_state"


def test_deterministic_ordering():
    first = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_b"), _admission_record("source_a")]),
        reviewed_fixture_inputs=_inputs([_input("set_b", "source_b"), _input("set_a", "source_a")]),
        review_policy_evaluation=_policy([
            _policy_record("set_b", "unsupported", ["unsupported_fixture_set_visible"]),
            _policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"]),
        ]),
    )
    second = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a"), _admission_record("source_b")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a"), _input("set_b", "source_b")]),
        review_policy_evaluation=_policy([
            _policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"]),
            _policy_record("set_b", "unsupported", ["unsupported_fixture_set_visible"]),
        ]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["admission_aware_policy_records"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_admission_aware_policy_evaluation_report()
    second = build_v3_1_admission_aware_policy_evaluation_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["admission_aware_policy_evaluation"]["deterministic_hash"] == second["admission_aware_policy_evaluation"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=_admission([_admission_record("source_a")]),
        reviewed_fixture_inputs=_inputs([_input("set_a", "source_a")]),
        review_policy_evaluation=_policy([_policy_record("set_a", "unsupported", ["unsupported_fixture_set_visible"])]),
    )
    row = result["admission_aware_policy_records"][0]

    assert result["safety_confirmations"]["satisfied_for_review_is_production_approval"] is False
    assert result["safety_confirmations"]["admission_aware_policy_authorizes_production_routing"] is False
    assert row["non_production_authorization"]["policy_authorizes_production_routing"] is False
    assert row["production_output_affected"] is False


def _admission(records):
    return {
        "schema_version": "v3_1.fixture_source_admission_policy.1",
        "deterministic_hash": "admission-hash",
        "source_admission_records": records,
    }


def _admission_record(source_id, status="admitted_for_review"):
    return {
        "source_id": source_id,
        "source_type": "persisted_fixture_sets",
        "admission_status": status,
        "block_reasons": ["source_identity_schema_and_evidence_present"] if status == "admitted_for_review" else [status],
    }


def _inputs(records):
    return {
        "schema_version": "v3_1.reviewed_fixture_inputs.1",
        "deterministic_hash": "inputs-hash",
        "normalized_fixture_inputs": records,
    }


def _input(fixture_id, source_id, status="reviewed"):
    return {
        "normalized_fixture_id": fixture_id,
        "source_fixture_id": fixture_id,
        "source_id": source_id,
        "source_type": "persisted_fixture_sets",
        "status": status,
    }


def _policy(records):
    return {
        "schema_version": "v3_1.review_policy_evaluation.1",
        "deterministic_hash": "policy-hash",
        "evaluations": records,
    }


def _policy_record(fixture_set_id, outcome, reasons):
    return {
        "fixture_set_id": fixture_set_id,
        "policy_outcome": outcome,
        "deterministic_reason_codes": reasons,
        "production_output_affected": False,
    }
