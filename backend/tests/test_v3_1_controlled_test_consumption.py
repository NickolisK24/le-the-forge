from app.planner_adapters.v3_1.controlled_test_consumption import build_controlled_test_consumption
from scripts.report_v3_1_controlled_test_consumption import build_v3_1_controlled_test_consumption_report


def test_eligible_non_production_manifest_consumes_in_controlled_test_mode():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a")]),
        controlled_test_mode=True,
    )

    record = result["controlled_consumption_records"][0]
    assert record["controlled_consumption_status"] == "consumed_in_controlled_test"
    assert result["summary"]["controlled_test_consumed_count"] == 1


def test_ineligible_manifest_blocks():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a", status="blocked_missing_hash", blockers=["blocked_missing_hash"])]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a")]),
        controlled_test_mode=True,
    )

    assert result["controlled_consumption_records"][0]["controlled_consumption_status"] == "blocked_not_eligible"


def test_invalid_authorization_state_blocks():
    manifest = _manifest("manifest_a", "set_a")
    manifest["authorization_status"]["authorization_state"] = "production_authoritative"
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([manifest]),
        controlled_test_mode=True,
    )

    assert result["controlled_consumption_records"][0]["controlled_consumption_status"] == "blocked_invalid_authorization_state"


def test_missing_manifest_blocks():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([]),
        controlled_test_mode=True,
    )

    assert result["controlled_consumption_records"][0]["controlled_consumption_status"] == "blocked_missing_manifest"


def test_missing_eligibility_record_blocks():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a")]),
        controlled_test_mode=True,
    )

    assert result["controlled_consumption_records"][0]["controlled_consumption_status"] == "blocked_missing_eligibility_record"


def test_runtime_consumption_disabled_without_explicit_test_mode():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a")]),
        controlled_test_mode=False,
    )

    assert result["controlled_consumption_records"][0]["controlled_consumption_status"] == "blocked_runtime_consumption_disabled"
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False


def test_deterministic_ordering():
    first = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_b", "set_b"), _eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_b", "set_b"), _manifest("manifest_a", "set_a")]),
        controlled_test_mode=True,
    )
    second = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a"), _eligibility_record("manifest_b", "set_b")]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a"), _manifest("manifest_b", "set_b")]),
        controlled_test_mode=True,
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["controlled_consumption_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_controlled_test_consumption_report()
    second = build_v3_1_controlled_test_consumption_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["controlled_test_consumption"]["deterministic_hash"] == second["controlled_test_consumption"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_controlled_test_consumption(
        manifest_consumption_eligibility=_eligibility([_eligibility_record("manifest_a", "set_a")]),
        admission_aware_manifest_serialization=_serialization([_manifest("manifest_a", "set_a")]),
        controlled_test_mode=True,
    )
    record = result["controlled_consumption_records"][0]

    assert result["safety_confirmations"]["controlled_consumption_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["controlled_consumption_is_production_consumption"] is False
    assert result["summary"]["runtime_production_consumption_enabled"] is False
    assert record["not_production_consumption"] is True
    assert record["controlled_consumption_authorizes_production_routing"] is False


def _eligibility(records):
    return {
        "schema_version": "v3_1.manifest_consumption_eligibility.1",
        "deterministic_hash": "eligibility-hash",
        "eligibility_records": records,
    }


def _eligibility_record(manifest_id, set_id, status="eligible_for_controlled_test_consumption", blockers=None):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": set_id,
        "eligibility_status": status,
        "authorization_state": "non_production_authoritative",
        "blockers": blockers or [],
    }


def _serialization(records):
    return {
        "schema_version": "v3_1.admission_aware_manifest_serialization.1",
        "deterministic_hash": "serialization-hash",
        "serialized_manifests": records,
    }


def _manifest(manifest_id, set_id):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": set_id,
        "authorization_status": {
            "authorization_state": "non_production_authoritative",
            "manifest_authorizes_production_routing": False,
            "manifest_is_production_approved": False,
            "manifest_is_production_authoritative": False,
        },
        "non_production_authoritative": True,
    }
