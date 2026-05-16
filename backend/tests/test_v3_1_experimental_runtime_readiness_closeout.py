from app.planner_adapters.v3_1.experimental_runtime_readiness_closeout import build_experimental_runtime_readiness_closeout
from scripts.report_v3_1_experimental_runtime_readiness_closeout import build_v3_1_experimental_runtime_readiness_closeout_report


def test_complete_evidence_chain_produces_ready():
    result = _build()

    record = result["closeout_records"][0]
    assert record["closeout_readiness_status"] == "ready_for_future_limited_experimental_runtime_phase"
    assert result["summary"]["ready_count"] == 1


def test_missing_manifest_eligibility_blocks():
    result = _build(eligibility=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_manifest_eligibility"


def test_missing_controlled_consumption_blocks():
    result = _build(consumption=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_controlled_consumption"


def test_missing_output_validation_blocks():
    result = _build(validation=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_output_validation"


def test_missing_structural_parity_blocks():
    result = _build(structural=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_structural_parity"


def test_missing_semantic_parity_blocks():
    result = _build(semantic=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_semantic_parity"


def test_missing_promotion_readiness_blocks():
    result = _build(promotion=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_promotion_readiness"


def test_missing_runtime_guard_blocks():
    result = _build(guard=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_runtime_guard"


def test_missing_dry_run_blocks():
    result = _build(dry_run=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_dry_run"


def test_missing_dry_run_stability_blocks():
    result = _build(stability=[])

    assert result["closeout_records"][0]["closeout_readiness_status"] == "blocked_missing_dry_run_stability"


def test_runtime_consumption_enabled_blocks():
    eligibility = _payload("eligibility_records", [_eligibility_record()])
    eligibility["summary"]["runtime_manifest_consumption_enabled"] = True
    result = _build(eligibility_payload=eligibility)

    assert "blocked_runtime_consumption_enabled" in result["closeout_records"][0]["blockers"]


def test_production_routing_authorized_blocks():
    eligibility = _payload("eligibility_records", [_eligibility_record()])
    eligibility["summary"]["production_routing_authorized"] = True
    result = _build(eligibility_payload=eligibility)

    assert "blocked_production_routing_authorized" in result["closeout_records"][0]["blockers"]


def test_deterministic_ordering():
    first = _build(
        eligibility=[_eligibility_record("manifest_b", "set_b"), _eligibility_record("manifest_a", "set_a")],
        consumption=[_consumption_record("manifest_b", "set_b"), _consumption_record("manifest_a", "set_a")],
        validation=[_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")],
        structural=[_structural_record("manifest_b", "set_b"), _structural_record("manifest_a", "set_a")],
        semantic=[_semantic_record("manifest_b", "set_b"), _semantic_record("manifest_a", "set_a")],
        promotion=[_promotion_record("manifest_b", "set_b"), _promotion_record("manifest_a", "set_a")],
        guard=[_guard_record("manifest_b", "set_b"), _guard_record("manifest_a", "set_a")],
        dry_run=[_dry_run_record("manifest_b", "set_b"), _dry_run_record("manifest_a", "set_a")],
        stability=[_stability_record("manifest_b", "set_b"), _stability_record("manifest_a", "set_a")],
    )
    second = _build(
        eligibility=[_eligibility_record("manifest_a", "set_a"), _eligibility_record("manifest_b", "set_b")],
        consumption=[_consumption_record("manifest_a", "set_a"), _consumption_record("manifest_b", "set_b")],
        validation=[_validation_record("manifest_a", "set_a"), _validation_record("manifest_b", "set_b")],
        structural=[_structural_record("manifest_a", "set_a"), _structural_record("manifest_b", "set_b")],
        semantic=[_semantic_record("manifest_a", "set_a"), _semantic_record("manifest_b", "set_b")],
        promotion=[_promotion_record("manifest_a", "set_a"), _promotion_record("manifest_b", "set_b")],
        guard=[_guard_record("manifest_a", "set_a"), _guard_record("manifest_b", "set_b")],
        dry_run=[_dry_run_record("manifest_a", "set_a"), _dry_run_record("manifest_b", "set_b")],
        stability=[_stability_record("manifest_a", "set_a"), _stability_record("manifest_b", "set_b")],
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["closeout_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_experimental_runtime_readiness_closeout_report()
    second = build_v3_1_experimental_runtime_readiness_closeout_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["experimental_runtime_readiness_closeout"]["deterministic_hash"] == second["experimental_runtime_readiness_closeout"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _build()
    record = result["closeout_records"][0]

    assert result["safety_confirmations"]["closeout_authorizes_runtime_manifest_consumption"] is False
    assert result["safety_confirmations"]["closeout_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["closeout_is_production_approval"] is False
    assert record["closeout_readiness_authorizes_runtime_routing"] is False


def _build(
    *,
    eligibility=None,
    consumption=None,
    validation=None,
    structural=None,
    semantic=None,
    promotion=None,
    guard=None,
    dry_run=None,
    stability=None,
    eligibility_payload=None,
):
    return build_experimental_runtime_readiness_closeout(
        manifest_consumption_eligibility=eligibility_payload or _payload("eligibility_records", [_eligibility_record()] if eligibility is None else eligibility),
        controlled_test_consumption=_payload("controlled_consumption_records", [_consumption_record()] if consumption is None else consumption),
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()] if validation is None else validation),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()] if structural is None else structural),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()] if semantic is None else semantic),
        controlled_consumption_promotion_readiness=_payload("promotion_readiness_records", [_promotion_record()] if promotion is None else promotion),
        limited_experimental_runtime_guards=_payload("limited_experimental_runtime_guard_records", [_guard_record()] if guard is None else guard),
        limited_experimental_runtime_dry_run=_payload("limited_experimental_runtime_dry_run_records", [_dry_run_record()] if dry_run is None else dry_run),
        dry_run_result_stability=_payload("dry_run_result_stability_records", [_stability_record()] if stability is None else stability),
    )


def _payload(key, records):
    return {
        "schema_version": f"v3_1.test.{key}.1",
        "deterministic_hash": f"{key}-hash",
        "summary": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_default_routing_authorized": False,
            "production_routing_authorized": False,
        },
        "safety_confirmations": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_planner_routing_changed": False,
        },
        key: records,
    }


def _eligibility_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "eligibility_status": "eligible_for_controlled_test_consumption"}


def _consumption_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "controlled_consumption_status": "consumed_in_controlled_test"}


def _validation_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "validation_status": "valid_controlled_test_output"}


def _structural_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "parity_status": "parity_confirmed"}


def _semantic_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "final_semantic_parity_status": "semantic_parity_confirmed"}


def _promotion_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "promotion_readiness_status": "ready_for_limited_experimental_runtime_consideration"}


def _guard_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "guard_contract_status": "guard_contract_ready"}


def _dry_run_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "dry_run_status": "dry_run_ready"}


def _stability_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "stability_status": "dry_run_stable"}
