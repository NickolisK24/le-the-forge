from app.planner_adapters.v3_1.baseline_semantic_expectations import build_baseline_semantic_expectations
from scripts.report_v3_1_baseline_semantic_expectations import build_v3_1_baseline_semantic_expectations_report


def test_semantic_expectations_are_produced_when_baseline_fields_exist():
    result = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines(
            [
                _snapshot(
                    expected_manifest_id="manifest_a",
                    expected_fixture_set_id="set_a",
                )
            ]
        )
    )

    record = result["baseline_semantic_expectation_records"][0]
    assert record["semantic_expectation_status"] == "semantic_expectations_available"
    assert record["expected_identity_fields"]["stable_key"] == "affix"
    assert record["expected_manifest_trace_fields"]["manifest_id"] == "manifest_a"
    assert record["expected_fixture_trace_fields"]["fixture_set_id"] == "set_a"


def test_missing_trace_fields_produce_partial_expectations():
    result = build_baseline_semantic_expectations(planner_snapshot_baselines=_baselines([_snapshot()]))

    record = result["baseline_semantic_expectation_records"][0]
    assert record["semantic_expectation_status"] == "semantic_expectations_partial"
    assert record["unavailable_semantic_fields"] == ["manifest_trace_fields", "fixture_trace_fields"]


def test_missing_baseline_blocks():
    result = build_baseline_semantic_expectations(planner_snapshot_baselines=_baselines([]))

    assert result["baseline_semantic_expectation_records"][0]["semantic_expectation_status"] == "blocked_missing_baseline_snapshot"


def test_unstable_identity_blocks():
    result = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines([_snapshot(snapshot_id=None, stable_key=None)])
    )

    assert result["baseline_semantic_expectation_records"][0]["semantic_expectation_status"] == "blocked_unstable_baseline_identity"


def test_missing_required_trace_blocks():
    result = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines([_snapshot(semantic_trace_required=True)])
    )

    assert result["baseline_semantic_expectation_records"][0]["semantic_expectation_status"] == "blocked_missing_required_trace"


def test_deterministic_ordering():
    first = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines([_snapshot(snapshot_id="snapshot_b", stable_key="b"), _snapshot(snapshot_id="snapshot_a", stable_key="a")])
    )
    second = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines([_snapshot(snapshot_id="snapshot_a", stable_key="a"), _snapshot(snapshot_id="snapshot_b", stable_key="b")])
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["baseline_id"] for row in first["baseline_semantic_expectation_records"]] == ["snapshot_a", "snapshot_b"]


def test_stable_report_generation():
    first = build_v3_1_baseline_semantic_expectations_report()
    second = build_v3_1_baseline_semantic_expectations_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["baseline_semantic_expectations"]["deterministic_hash"] == second["baseline_semantic_expectations"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_baseline_semantic_expectations(
        planner_snapshot_baselines=_baselines([_snapshot(expected_manifest_id="manifest_a", expected_fixture_set_id="set_a")])
    )
    record = result["baseline_semantic_expectation_records"][0]

    assert result["safety_confirmations"]["semantic_expectations_authorize_production_routing"] is False
    assert result["safety_confirmations"]["semantic_expectations_are_production_approval"] is False
    assert result["summary"]["runtime_manifest_consumption_enabled"] is False
    assert record["semantic_expectations_authorize_production_routing"] is False


def _baselines(snapshots):
    return {
        "schema_version": "v3_1.planner_snapshot_baselines.1",
        "deterministic_hash": "baseline-hash",
        "snapshots": snapshots,
    }


def _snapshot(
    snapshot_id="snapshot_a",
    stable_key="affix",
    expected_manifest_id=None,
    expected_fixture_set_id=None,
    semantic_trace_required=False,
):
    snapshot = {
        "snapshot_id": snapshot_id,
        "stable_key": stable_key,
        "snapshot_category": "planner_adjacent_summary",
        "baseline_readiness": "baseline_candidate",
        "baseline_candidate": True,
        "comparison_eligible": True,
        "semantic_trace_required": semantic_trace_required,
        "dual_run_comparison_state": {
            "comparison_id": stable_key,
            "legacy_status": "available",
            "trusted_shadow_status": "available",
            "drift_classification": "equivalent",
            "legacy_hash": "legacy-hash",
            "trusted_hash": "trusted-hash",
        },
        "production_output_affected": False,
    }
    if expected_manifest_id is not None:
        snapshot["expected_manifest_id"] = expected_manifest_id
    if expected_fixture_set_id is not None:
        snapshot["expected_fixture_set_id"] = expected_fixture_set_id
    return snapshot
