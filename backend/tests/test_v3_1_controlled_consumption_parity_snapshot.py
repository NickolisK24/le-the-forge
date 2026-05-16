from app.planner_adapters.v3_1.controlled_consumption_parity_snapshot import build_controlled_consumption_parity_snapshot
from scripts.report_v3_1_controlled_consumption_parity_snapshot import build_v3_1_controlled_consumption_parity_snapshot_report


def test_matching_validated_output_and_baseline_confirms_parity():
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([_baseline()]),
    )

    record = result["parity_records"][0]
    assert record["parity_status"] == "parity_confirmed"
    assert result["summary"]["parity_confirmed_count"] == 1


def test_missing_validated_output_blocks():
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([]),
        planner_snapshot_baselines=_baselines([_baseline()]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_missing_validated_output"


def test_missing_baseline_snapshot_blocks():
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_missing_baseline_snapshot"


def test_identity_mismatch_blocks():
    baseline = _baseline(expected_validation_record_id="different_record")
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([baseline]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_identity_mismatch"


def test_fixture_set_mismatch_blocks():
    baseline = _baseline(expected_fixture_set_id="different_set")
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([baseline]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_fixture_set_mismatch"


def test_manifest_trace_mismatch_blocks():
    baseline = _baseline(expected_manifest_id="different_manifest")
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([baseline]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_manifest_trace_mismatch"


def test_invalid_authorization_state_blocks():
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation(
            [_validation_record("manifest_a", "set_a", authorization_state="production_authoritative")]
        ),
        planner_snapshot_baselines=_baselines([_baseline()]),
    )

    assert result["parity_records"][0]["parity_status"] == "blocked_invalid_authorization_state"


def test_deterministic_ordering():
    records = [_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")]
    first = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation(records),
        planner_snapshot_baselines=_baselines([_baseline(snapshot_id="baseline_b", stable_key="b"), _baseline(snapshot_id="baseline_a", stable_key="a")]),
    )
    second = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation(list(reversed(records))),
        planner_snapshot_baselines=_baselines([_baseline(snapshot_id="baseline_a", stable_key="a"), _baseline(snapshot_id="baseline_b", stable_key="b")]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["parity_records"]] == ["manifest_a", "manifest_b"]
    assert first["baseline_comparison_summary"]["selected_baseline_id"] == "baseline_a"


def test_stable_report_generation():
    first = build_v3_1_controlled_consumption_parity_snapshot_report()
    second = build_v3_1_controlled_consumption_parity_snapshot_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["controlled_consumption_parity_snapshot"]["deterministic_hash"] == second["controlled_consumption_parity_snapshot"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_controlled_consumption_parity_snapshot(
        controlled_consumption_output_validation=_validation([_validation_record("manifest_a", "set_a")]),
        planner_snapshot_baselines=_baselines([_baseline()]),
    )
    record = result["parity_records"][0]

    assert result["safety_confirmations"]["parity_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["parity_is_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["parity_authorizes_production_routing"] is False


def _validation(records):
    return {
        "schema_version": "v3_1.controlled_consumption_output_validation.1",
        "deterministic_hash": "validation-hash",
        "summary": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
        },
        "validation_records": records,
    }


def _validation_record(manifest_id, fixture_set_id, authorization_state="non_production_authoritative", status="valid_controlled_test_output"):
    return {
        "validation_record_id": f"validation_{manifest_id}_{fixture_set_id}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "controlled_consumption_status": "consumed_in_controlled_test",
        "validation_status": status,
        "blockers": [],
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


def _baselines(snapshots):
    return {
        "schema_version": "v3_1.planner_snapshot_baselines.1",
        "deterministic_hash": "baseline-hash",
        "snapshots": snapshots,
    }


def _baseline(
    snapshot_id="baseline_a",
    stable_key="a",
    expected_validation_record_id=None,
    expected_fixture_set_id=None,
    expected_manifest_id=None,
):
    return {
        "snapshot_id": snapshot_id,
        "stable_key": stable_key,
        "baseline_readiness": "baseline_candidate",
        "baseline_candidate": True,
        "comparison_eligible": True,
        "expected_validation_record_id": expected_validation_record_id,
        "expected_fixture_set_id": expected_fixture_set_id,
        "expected_manifest_id": expected_manifest_id,
        "production_output_affected": False,
    }
