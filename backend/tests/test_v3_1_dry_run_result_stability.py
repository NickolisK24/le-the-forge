from app.planner_adapters.v3_1.dry_run_result_stability import audit_dry_run_result_stability
from scripts.report_v3_1_dry_run_result_stability import build_v3_1_dry_run_result_stability_report


def test_repeated_identical_dry_run_snapshots_are_stable():
    result = _audit([[_dry_run_record()], [_dry_run_record()]])

    record = result["dry_run_result_stability_records"][0]
    assert record["stability_status"] == "dry_run_stable"
    assert record["compared_snapshot_count"] == 2
    assert result["summary"]["stable_count"] == 1


def test_insufficient_snapshots_block():
    result = _audit([[_dry_run_record()]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_snapshot_count_insufficient"


def test_missing_dry_run_record_blocks():
    result = _audit([[_dry_run_record()], []])

    record = result["dry_run_result_stability_records"][0]
    assert record["stability_status"] == "blocked_missing_dry_run_record"
    assert "blocked_missing_dry_run_record" in record["blockers"]


def test_manifest_identity_drift_blocks():
    first = _dry_run_record(record_id="dry_run_shared", manifest_id="manifest_a")
    second = _dry_run_record(record_id="dry_run_shared", manifest_id="manifest_b")
    result = audit_dry_run_result_stability([[first], [second]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_manifest_identity_drift"


def test_fixture_set_identity_drift_blocks():
    record = _dry_run_record(record_id="dry_run_shared", fixture_set_id="set_a")
    drifted = _dry_run_record(record_id="dry_run_shared", fixture_set_id="set_b")
    result = audit_dry_run_result_stability([[record], [drifted]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_fixture_set_identity_drift"


def test_guard_status_drift_blocks():
    result = _audit([[_dry_run_record()], [_dry_run_record(guard_status="blocked_invalid_manifest_eligibility")]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_guard_status_drift"


def test_readiness_status_drift_blocks():
    result = _audit([[_dry_run_record()], [_dry_run_record(promotion_readiness_status="blocked_missing_semantic_parity")]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_readiness_status_drift"


def test_authorization_state_drift_blocks():
    result = _audit([[_dry_run_record()], [_dry_run_record(authorization_state="production_authoritative")]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_authorization_state_drift"


def test_dry_run_status_drift_blocks():
    result = _audit([[_dry_run_record()], [_dry_run_record(dry_run_status="blocked_invalid_guard_status")]])

    assert result["dry_run_result_stability_records"][0]["stability_status"] == "blocked_dry_run_status_drift"


def test_deterministic_ordering():
    first = _audit(
        [
            [_dry_run_record(manifest_id="manifest_b", fixture_set_id="set_b"), _dry_run_record(manifest_id="manifest_a", fixture_set_id="set_a")],
            [_dry_run_record(manifest_id="manifest_b", fixture_set_id="set_b"), _dry_run_record(manifest_id="manifest_a", fixture_set_id="set_a")],
        ]
    )
    second = _audit(
        [
            [_dry_run_record(manifest_id="manifest_a", fixture_set_id="set_a"), _dry_run_record(manifest_id="manifest_b", fixture_set_id="set_b")],
            [_dry_run_record(manifest_id="manifest_a", fixture_set_id="set_a"), _dry_run_record(manifest_id="manifest_b", fixture_set_id="set_b")],
        ]
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["dry_run_result_stability_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_dry_run_result_stability_report()
    second = build_v3_1_dry_run_result_stability_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["dry_run_result_stability"]["deterministic_hash"] == second["dry_run_result_stability"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _audit([[_dry_run_record()], [_dry_run_record()]])

    assert result["safety_confirmations"]["stability_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["stability_enables_runtime_manifest_consumption"] is False
    assert result["safety_confirmations"]["stability_is_production_approval"] is False
    assert result["summary"]["production_behavior_changed"] is False


def _audit(snapshots):
    return audit_dry_run_result_stability(snapshots)


def _dry_run_record(
    record_id=None,
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    guard_status="guard_contract_ready",
    promotion_readiness_status="ready_for_limited_experimental_runtime_consideration",
    authorization_state="non_production_authoritative",
    dry_run_status="dry_run_ready",
):
    return {
        "limited_runtime_dry_run_id": record_id or f"dry_run_{manifest_id}_{fixture_set_id}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "guard_status": guard_status,
        "promotion_readiness_status": promotion_readiness_status,
        "authorization_state": authorization_state,
        "dry_run_status": dry_run_status,
        "blockers": [] if dry_run_status == "dry_run_ready" else [dry_run_status],
        "dry_run_enables_runtime_routing": False,
        "dry_run_authorizes_production_routing": False,
        "production_output_affected": False,
    }
