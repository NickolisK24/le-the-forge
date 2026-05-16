from app.planner_adapters.v3_1.controlled_consumption_output_validation import validate_controlled_consumption_output
from scripts.report_v3_1_controlled_consumption_output_validation import build_v3_1_controlled_consumption_output_validation_report


def test_valid_controlled_consumption_output_passes():
    result = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record("manifest_a", "set_a")]))

    record = result["validation_records"][0]
    assert record["validation_status"] == "valid_controlled_test_output"
    assert result["summary"]["valid_count"] == 1


def test_missing_manifest_trace_blocks():
    result = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record(None, "set_a")]))

    assert result["validation_records"][0]["validation_status"] == "blocked_missing_manifest_trace"


def test_missing_fixture_set_trace_blocks():
    result = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record("manifest_a", None)]))

    assert result["validation_records"][0]["validation_status"] == "blocked_missing_fixture_set_trace"


def test_invalid_authorization_state_blocks():
    result = validate_controlled_consumption_output(
        controlled_test_consumption=_consumption([_record("manifest_a", "set_a", authorization_state="production_authoritative")])
    )

    assert result["validation_records"][0]["validation_status"] == "blocked_invalid_authorization_state"


def test_runtime_consumption_enabled_blocks():
    payload = _consumption([_record("manifest_a", "set_a")])
    payload["summary"]["runtime_manifest_consumption_enabled"] = True
    result = validate_controlled_consumption_output(controlled_test_consumption=payload)

    assert result["validation_records"][0]["validation_status"] == "blocked_runtime_consumption_enabled"


def test_invalid_consumption_status_blocks():
    result = validate_controlled_consumption_output(
        controlled_test_consumption=_consumption([_record("manifest_a", "set_a", status="blocked_not_eligible")])
    )

    assert result["validation_records"][0]["validation_status"] == "blocked_invalid_consumption_status"


def test_missing_consumption_record_blocks():
    result = validate_controlled_consumption_output(controlled_test_consumption=_consumption([]))

    assert result["validation_records"][0]["validation_status"] == "blocked_missing_consumption_record"


def test_deterministic_ordering():
    first = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record("manifest_b", "set_b"), _record("manifest_a", "set_a")]))
    second = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record("manifest_a", "set_a"), _record("manifest_b", "set_b")]))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["validation_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_controlled_consumption_output_validation_report()
    second = build_v3_1_controlled_consumption_output_validation_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["controlled_consumption_output_validation"]["deterministic_hash"] == second["controlled_consumption_output_validation"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = validate_controlled_consumption_output(controlled_test_consumption=_consumption([_record("manifest_a", "set_a")]))
    record = result["validation_records"][0]

    assert result["safety_confirmations"]["validation_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["validation_is_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["validation_authorizes_production_routing"] is False


def _consumption(records):
    return {
        "schema_version": "v3_1.controlled_test_consumption.1",
        "deterministic_hash": "consumption-hash",
        "summary": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
        },
        "safety_confirmations": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
        },
        "controlled_consumption_records": records,
    }


def _record(manifest_id, fixture_set_id, authorization_state="non_production_authoritative", status="consumed_in_controlled_test"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "controlled_consumption_status": status,
        "authorization_state": authorization_state,
        "controlled_consumption_authorizes_production_routing": False,
        "not_production_consumption": True,
        "production_output_affected": False,
    }
