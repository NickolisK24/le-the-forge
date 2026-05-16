from app.planner_adapters.v3_1.baseline_trace_expectation_backfill import build_baseline_trace_expectation_backfill
from scripts.report_v3_1_baseline_trace_expectation_backfill import build_v3_1_baseline_trace_expectation_backfill_report


def test_manifest_and_fixture_traces_backfill_when_sources_exist():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([_expectation()]),
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
        admission_aware_manifest_serialization=_serialization([_manifest_record()]),
    )

    record = result["baseline_trace_backfill_records"][0]
    assert record["trace_backfill_status"] == "trace_expectations_backfilled"
    assert record["manifest_id"] == "manifest_a"
    assert record["fixture_set_id"] == "set_a"
    assert record["remaining_unavailable_fields"] == []


def test_missing_trace_source_remains_partial():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([_expectation()]),
        controlled_consumption_parity_snapshot=_parity([]),
        controlled_consumption_output_validation=_validation([]),
        admission_aware_manifest_serialization=_serialization([]),
    )

    record = result["baseline_trace_backfill_records"][0]
    assert record["trace_backfill_status"] == "trace_expectations_partial"
    assert record["remaining_unavailable_fields"] == ["manifest_trace_fields", "fixture_trace_fields"]


def test_missing_baseline_expectation_blocks():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([]),
        controlled_consumption_parity_snapshot=_parity([]),
        controlled_consumption_output_validation=_validation([]),
        admission_aware_manifest_serialization=_serialization([]),
    )

    assert result["baseline_trace_backfill_records"][0]["trace_backfill_status"] == "blocked_missing_baseline_expectation"


def test_conflicting_trace_sources_block():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([_expectation(expected_manifest_fields={"manifest_id": "different_manifest"})]),
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
        admission_aware_manifest_serialization=_serialization([_manifest_record()]),
    )

    record = result["baseline_trace_backfill_records"][0]
    assert record["trace_backfill_status"] == "blocked_trace_conflict"
    assert record["trace_conflicts"] == ["baseline_manifest_id"]


def test_invalid_authorization_state_blocks():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([_expectation()]),
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(authorization_state="production_authoritative")]),
        admission_aware_manifest_serialization=_serialization([_manifest_record()]),
    )

    assert result["baseline_trace_backfill_records"][0]["trace_backfill_status"] == "blocked_invalid_authorization_state"


def test_deterministic_ordering():
    expectations = [_expectation("baseline_b"), _expectation("baseline_a")]
    parity = [_parity_record("baseline_b", "manifest_b", "set_b"), _parity_record("baseline_a", "manifest_a", "set_a")]
    validations = [_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")]
    manifests = [_manifest_record("manifest_b", "set_b"), _manifest_record("manifest_a", "set_a")]
    first = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations(expectations),
        controlled_consumption_parity_snapshot=_parity(parity),
        controlled_consumption_output_validation=_validation(validations),
        admission_aware_manifest_serialization=_serialization(manifests),
    )
    second = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations(list(reversed(expectations))),
        controlled_consumption_parity_snapshot=_parity(list(reversed(parity))),
        controlled_consumption_output_validation=_validation(list(reversed(validations))),
        admission_aware_manifest_serialization=_serialization(list(reversed(manifests))),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["baseline_id"] for row in first["baseline_trace_backfill_records"]] == ["baseline_a", "baseline_b"]


def test_stable_report_generation():
    first = build_v3_1_baseline_trace_expectation_backfill_report()
    second = build_v3_1_baseline_trace_expectation_backfill_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["baseline_trace_expectation_backfill"]["deterministic_hash"] == second["baseline_trace_expectation_backfill"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=_expectations([_expectation()]),
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
        admission_aware_manifest_serialization=_serialization([_manifest_record()]),
    )
    record = result["baseline_trace_backfill_records"][0]

    assert result["safety_confirmations"]["backfilled_expectations_authorize_production_routing"] is False
    assert result["safety_confirmations"]["backfilled_expectations_are_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["backfilled_expectations_authorize_production_routing"] is False


def _expectations(records):
    return {
        "schema_version": "v3_1.baseline_semantic_expectations.1",
        "deterministic_hash": "expectation-hash",
        "baseline_semantic_expectation_records": records,
    }


def _expectation(baseline_id="baseline_a", expected_manifest_fields=None, expected_fixture_fields=None):
    return {
        "baseline_semantic_expectation_id": f"expectation_{baseline_id}",
        "baseline_id": baseline_id,
        "fixture_set_id": (expected_fixture_fields or {}).get("fixture_set_id"),
        "expected_identity_fields": {"snapshot_id": baseline_id, "stable_key": baseline_id},
        "expected_manifest_trace_fields": expected_manifest_fields or {},
        "expected_fixture_trace_fields": expected_fixture_fields or {},
        "semantic_expectations": {},
        "unavailable_semantic_fields": ["manifest_trace_fields", "fixture_trace_fields"],
        "semantic_expectation_status": "semantic_expectations_partial",
        "blockers": [],
        "semantic_expectations_authorize_production_routing": False,
        "production_output_affected": False,
    }


def _parity(records):
    return {
        "schema_version": "v3_1.controlled_consumption_parity_snapshot.1",
        "deterministic_hash": "parity-hash",
        "parity_records": records,
    }


def _parity_record(baseline_id="baseline_a", manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "parity_record_id": f"parity_{baseline_id}",
        "baseline_id": baseline_id,
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "parity_status": "parity_confirmed",
        "blockers": [],
        "parity_authorizes_production_routing": False,
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


def _serialization(records):
    return {
        "schema_version": "v3_1.admission_aware_manifest_serialization.1",
        "deterministic_hash": "serialization-hash",
        "serialized_manifests": records,
    }


def _manifest_record(manifest_id="manifest_a", fixture_set_id="set_a", authorization_state="non_production_authoritative"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "serialization_status": "serialized_manifest",
        "authorization_status": {
            "authorization_state": authorization_state,
            "manifest_authorizes_production_routing": False,
            "manifest_is_production_approved": False,
            "manifest_is_production_authoritative": False,
        },
        "non_production_authoritative": True,
        "production_output_affected": False,
    }
