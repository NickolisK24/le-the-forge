from app.planner_adapters.v3_1.trace_backfilled_semantic_parity import build_trace_backfilled_semantic_parity
from scripts.report_v3_1_trace_backfilled_semantic_parity import build_v3_1_trace_backfilled_semantic_parity_report


def test_matching_backfilled_traces_promote_partial_to_confirmed():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
    )

    record = result["trace_backfilled_semantic_parity_records"][0]
    assert record["final_semantic_parity_status"] == "semantic_parity_confirmed"
    assert record["promoted_from_partial"] is True


def test_unavailable_trace_expectations_remain_partial():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record(status="trace_expectations_partial", remaining=["manifest_trace_fields"])]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
    )

    record = result["trace_backfilled_semantic_parity_records"][0]
    assert record["final_semantic_parity_status"] == "semantic_parity_partial"
    assert record["remaining_unavailable_fields"] == ["manifest_trace_fields"]


def test_trace_mismatch_blocks():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record(manifest_id="different_manifest")]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
    )

    record = result["trace_backfilled_semantic_parity_records"][0]
    assert record["final_semantic_parity_status"] == "blocked_trace_conflict"
    assert record["mismatched_fields"] == ["manifest_id"]


def test_missing_backfill_record_blocks():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
    )

    assert result["trace_backfilled_semantic_parity_records"][0]["final_semantic_parity_status"] == "blocked_missing_backfilled_expectation"


def test_missing_controlled_output_blocks():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record()]),
        controlled_consumption_output_validation=_validation([]),
    )

    assert result["trace_backfilled_semantic_parity_records"][0]["final_semantic_parity_status"] == "blocked_missing_controlled_output"


def test_invalid_authorization_state_blocks():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(authorization_state="production_authoritative")]),
    )

    assert result["trace_backfilled_semantic_parity_records"][0]["final_semantic_parity_status"] == "blocked_invalid_authorization_state"


def test_deterministic_ordering():
    first = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record("baseline_b", "manifest_b", "set_b"), _semantic_record("baseline_a", "manifest_a", "set_a")]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record("baseline_b", "manifest_b", "set_b"), _backfill_record("baseline_a", "manifest_a", "set_a")]),
        controlled_consumption_output_validation=_validation([_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")]),
    )
    second = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record("baseline_a", "manifest_a", "set_a"), _semantic_record("baseline_b", "manifest_b", "set_b")]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record("baseline_a", "manifest_a", "set_a"), _backfill_record("baseline_b", "manifest_b", "set_b")]),
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a"), _validation_record("manifest_b", "set_b")]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["baseline_id"] for row in first["trace_backfilled_semantic_parity_records"]] == ["baseline_a", "baseline_b"]


def test_stable_report_generation():
    first = build_v3_1_trace_backfilled_semantic_parity_report()
    second = build_v3_1_trace_backfilled_semantic_parity_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["trace_backfilled_semantic_parity"]["deterministic_hash"] == second["trace_backfilled_semantic_parity"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_trace_backfilled_semantic_parity(
        controlled_consumption_semantic_parity=_semantic([_semantic_record()]),
        baseline_trace_expectation_backfill=_backfill([_backfill_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
    )
    record = result["trace_backfilled_semantic_parity_records"][0]

    assert result["safety_confirmations"]["semantic_parity_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["semantic_parity_is_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["semantic_parity_authorizes_production_routing"] is False


def _semantic(records):
    return {
        "schema_version": "v3_1.controlled_consumption_semantic_parity.1",
        "deterministic_hash": "semantic-hash",
        "semantic_parity_records": records,
    }


def _semantic_record(baseline_id="baseline_a", manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "semantic_parity_record_id": f"semantic_{baseline_id}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "baseline_id": baseline_id,
        "structural_parity_status": "parity_confirmed",
        "semantic_parity_status": "semantic_parity_partial",
        "compared_fields": [],
        "unavailable_fields": ["baseline_semantics"],
        "mismatched_fields": [],
        "blockers": [],
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _backfill(records):
    return {
        "schema_version": "v3_1.baseline_trace_expectation_backfill.1",
        "deterministic_hash": "backfill-hash",
        "baseline_trace_backfill_records": records,
    }


def _backfill_record(baseline_id="baseline_a", manifest_id="manifest_a", fixture_set_id="set_a", status="trace_expectations_backfilled", remaining=None):
    return {
        "baseline_trace_backfill_id": f"backfill_{baseline_id}",
        "baseline_id": baseline_id,
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "original_semantic_expectation_status": "semantic_expectations_partial",
        "backfilled_manifest_trace_fields": {"manifest_id": manifest_id} if manifest_id else {},
        "backfilled_fixture_trace_fields": {"fixture_set_id": fixture_set_id} if fixture_set_id else {},
        "remaining_unavailable_fields": remaining or [],
        "trace_backfill_status": status,
        "trace_conflicts": [],
        "blockers": [],
        "backfilled_expectations_authorize_production_routing": False,
        "production_output_affected": False,
    }


def _validation(records):
    return {
        "schema_version": "v3_1.controlled_consumption_output_validation.1",
        "deterministic_hash": "validation-hash",
        "validation_records": records,
    }


def _validation_record(manifest_id="manifest_a", fixture_set_id="set_a", authorization_state="non_production_authoritative"):
    return {
        "validation_record_id": f"validation_{manifest_id}_{fixture_set_id}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "validation_status": "valid_controlled_test_output",
        "traceability_summary": {
            "manifest_trace_present": bool(manifest_id),
            "fixture_set_trace_present": bool(fixture_set_id),
            "authorization_state": authorization_state,
            "runtime_consumption_enabled": False,
            "not_production_consumption": True,
        },
        "validation_authorizes_production_routing": False,
        "production_output_affected": False,
    }
