from app.planner_adapters.v3_1.controlled_consumption_semantic_parity import build_controlled_consumption_semantic_parity
from scripts.report_v3_1_controlled_consumption_semantic_parity import build_v3_1_controlled_consumption_semantic_parity_report


def test_matching_semantic_fields_confirm_parity():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(semantics={"domain": "affix", "count": 1})]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix", "count": 1})]),
    )

    record = result["semantic_parity_records"][0]
    assert record["semantic_parity_status"] == "semantic_parity_confirmed"
    assert result["summary"]["semantic_parity_confirmed_count"] == 1


def test_missing_optional_semantic_fields_produce_partial():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
        planner_snapshot_baselines=_baselines([_baseline()]),
    )

    record = result["semantic_parity_records"][0]
    assert record["semantic_parity_status"] == "semantic_parity_partial"
    assert record["unavailable_fields"] == ["baseline_semantics"]


def test_missing_required_baseline_semantics_blocks():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record()]),
        planner_snapshot_baselines=_baselines([_baseline(semantic_required=True)]),
    )

    assert result["semantic_parity_records"][0]["semantic_parity_status"] == "blocked_missing_baseline_semantics"


def test_structural_parity_failure_blocks_semantic_parity():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record(status="blocked_missing_baseline_snapshot")]),
        controlled_consumption_output_validation=_validation([_validation_record(semantics={"domain": "affix"})]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix"})]),
    )

    assert result["semantic_parity_records"][0]["semantic_parity_status"] == "blocked_missing_structural_parity"


def test_missing_controlled_output_blocks():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix"})]),
    )

    assert result["semantic_parity_records"][0]["semantic_parity_status"] == "blocked_missing_controlled_output"


def test_semantic_mismatch_blocks():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(semantics={"domain": "item"})]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix"})]),
    )

    record = result["semantic_parity_records"][0]
    assert record["semantic_parity_status"] == "blocked_semantic_mismatch"
    assert record["mismatched_fields"] == ["domain"]


def test_invalid_authorization_state_blocks():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(authorization_state="production_authoritative", semantics={"domain": "affix"})]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix"})]),
    )

    assert result["semantic_parity_records"][0]["semantic_parity_status"] == "blocked_invalid_authorization_state"


def test_deterministic_ordering():
    first = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record("manifest_b", "set_b"), _parity_record("manifest_a", "set_a")]),
        controlled_consumption_output_validation=_validation(
            [
                _validation_record("manifest_b", "set_b", semantics={"domain": "affix"}),
                _validation_record("manifest_a", "set_a", semantics={"domain": "affix"}),
            ]
        ),
        planner_snapshot_baselines=_baselines([_baseline("baseline_a", semantics={"domain": "affix"})]),
    )
    second = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record("manifest_a", "set_a"), _parity_record("manifest_b", "set_b")]),
        controlled_consumption_output_validation=_validation(
            [
                _validation_record("manifest_a", "set_a", semantics={"domain": "affix"}),
                _validation_record("manifest_b", "set_b", semantics={"domain": "affix"}),
            ]
        ),
        planner_snapshot_baselines=_baselines([_baseline("baseline_a", semantics={"domain": "affix"})]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["semantic_parity_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_controlled_consumption_semantic_parity_report()
    second = build_v3_1_controlled_consumption_semantic_parity_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["controlled_consumption_semantic_parity"]["deterministic_hash"] == second["controlled_consumption_semantic_parity"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=_parity([_parity_record()]),
        controlled_consumption_output_validation=_validation([_validation_record(semantics={"domain": "affix"})]),
        planner_snapshot_baselines=_baselines([_baseline(semantics={"domain": "affix"})]),
    )
    record = result["semantic_parity_records"][0]

    assert result["safety_confirmations"]["semantic_parity_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["semantic_parity_is_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["semantic_parity_authorizes_production_routing"] is False


def _parity(records):
    return {
        "schema_version": "v3_1.controlled_consumption_parity_snapshot.1",
        "deterministic_hash": "parity-hash",
        "parity_records": records,
    }


def _parity_record(manifest_id="manifest_a", fixture_set_id="set_a", status="parity_confirmed"):
    return {
        "parity_record_id": f"parity_{manifest_id}_{fixture_set_id}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "baseline_id": "baseline_a",
        "parity_status": status,
        "blockers": [] if status == "parity_confirmed" else [status],
        "parity_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _validation(records):
    return {
        "schema_version": "v3_1.controlled_consumption_output_validation.1",
        "deterministic_hash": "validation-hash",
        "validation_records": records,
    }


def _validation_record(
    manifest_id="manifest_a",
    fixture_set_id="set_a",
    authorization_state="non_production_authoritative",
    semantics=None,
):
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
        "controlled_semantics": semantics or {},
        "validation_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _baselines(snapshots):
    return {
        "schema_version": "v3_1.planner_snapshot_baselines.1",
        "deterministic_hash": "baseline-hash",
        "snapshots": snapshots,
    }


def _baseline(snapshot_id="baseline_a", semantics=None, semantic_required=False):
    baseline = {
        "snapshot_id": snapshot_id,
        "stable_key": "affix",
        "baseline_readiness": "baseline_candidate",
        "baseline_candidate": True,
        "comparison_eligible": True,
        "semantic_required": semantic_required,
        "production_output_affected": False,
    }
    if semantics is not None:
        baseline["semantic_expectations"] = semantics
    return baseline
