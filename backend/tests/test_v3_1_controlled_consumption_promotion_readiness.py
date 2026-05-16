from app.planner_adapters.v3_1.controlled_consumption_promotion_readiness import build_controlled_consumption_promotion_readiness
from scripts.report_v3_1_controlled_consumption_promotion_readiness import build_v3_1_controlled_consumption_promotion_readiness_report


def test_fully_valid_evidence_chain_becomes_ready():
    result = _build()

    record = result["promotion_readiness_records"][0]
    assert record["promotion_readiness_status"] == "ready_for_limited_experimental_runtime_consideration"
    assert result["summary"]["ready_count"] == 1


def test_missing_controlled_consumption_blocks():
    result = _build(consumption=[])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_missing_controlled_consumption"


def test_invalid_output_validation_blocks():
    result = _build(validation=[_validation_record(status="blocked_invalid_consumption_status")])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_invalid_output_validation"


def test_missing_structural_parity_blocks():
    result = _build(structural=[])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_missing_structural_parity"


def test_missing_semantic_parity_blocks():
    result = _build(semantic=[])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_missing_semantic_parity"


def test_invalid_eligibility_blocks():
    result = _build(eligibility=[_eligibility_record(status="blocked_missing_hash")])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_invalid_manifest_eligibility"


def test_invalid_authorization_state_blocks():
    result = _build(consumption=[_consumption_record(authorization_state="production_authoritative")])

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_invalid_authorization_state"


def test_runtime_consumption_enabled_blocks():
    payload = _payload("controlled_consumption_records", [_consumption_record()])
    payload["summary"]["runtime_manifest_consumption_enabled"] = True
    result = build_controlled_consumption_promotion_readiness(
        controlled_test_consumption=payload,
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()]),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()]),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()]),
        manifest_consumption_eligibility=_payload("eligibility_records", [_eligibility_record()]),
    )

    assert result["promotion_readiness_records"][0]["promotion_readiness_status"] == "blocked_runtime_consumption_enabled"


def test_deterministic_ordering():
    first = _build(
        consumption=[_consumption_record("manifest_b", "set_b"), _consumption_record("manifest_a", "set_a")],
        validation=[_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")],
        structural=[_structural_record("manifest_b", "set_b"), _structural_record("manifest_a", "set_a")],
        semantic=[_semantic_record("manifest_b", "set_b"), _semantic_record("manifest_a", "set_a")],
        eligibility=[_eligibility_record("manifest_b", "set_b"), _eligibility_record("manifest_a", "set_a")],
    )
    second = _build(
        consumption=[_consumption_record("manifest_a", "set_a"), _consumption_record("manifest_b", "set_b")],
        validation=[_validation_record("manifest_a", "set_a"), _validation_record("manifest_b", "set_b")],
        structural=[_structural_record("manifest_a", "set_a"), _structural_record("manifest_b", "set_b")],
        semantic=[_semantic_record("manifest_a", "set_a"), _semantic_record("manifest_b", "set_b")],
        eligibility=[_eligibility_record("manifest_a", "set_a"), _eligibility_record("manifest_b", "set_b")],
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["promotion_readiness_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_controlled_consumption_promotion_readiness_report()
    second = build_v3_1_controlled_consumption_promotion_readiness_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["controlled_consumption_promotion_readiness"]["deterministic_hash"] == second["controlled_consumption_promotion_readiness"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _build()
    record = result["promotion_readiness_records"][0]

    assert result["safety_confirmations"]["promotion_readiness_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["promotion_readiness_is_production_approval"] is False
    assert result["safety_confirmations"]["promotion_readiness_enables_runtime_consumption"] is False
    assert record["promotion_readiness_authorizes_production_routing"] is False


def _build(consumption=None, validation=None, structural=None, semantic=None, eligibility=None):
    return build_controlled_consumption_promotion_readiness(
        controlled_test_consumption=_payload("controlled_consumption_records", [_consumption_record()] if consumption is None else consumption),
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()] if validation is None else validation),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()] if structural is None else structural),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()] if semantic is None else semantic),
        manifest_consumption_eligibility=_payload("eligibility_records", [_eligibility_record()] if eligibility is None else eligibility),
    )


def _payload(key, records):
    return {
        "schema_version": f"v3_1.test.{key}.1",
        "deterministic_hash": f"{key}-hash",
        "summary": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "manifest_runtime_consumption_enabled": False,
        },
        "safety_confirmations": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
        },
        key: records,
    }


def _consumption_record(manifest_id="manifest_a", fixture_set_id="set_a", authorization_state="non_production_authoritative"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "controlled_consumption_status": "consumed_in_controlled_test",
        "eligibility_status": "eligible_for_controlled_test_consumption",
        "authorization_state": authorization_state,
        "controlled_consumption_authorizes_production_routing": False,
        "not_production_consumption": True,
        "production_output_affected": False,
    }


def _validation_record(manifest_id="manifest_a", fixture_set_id="set_a", status="valid_controlled_test_output", authorization_state="non_production_authoritative"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "validation_status": status,
        "traceability_summary": {
            "authorization_state": authorization_state,
            "manifest_trace_present": bool(manifest_id),
            "fixture_set_trace_present": bool(fixture_set_id),
        },
        "validation_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _structural_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "parity_status": "parity_confirmed",
        "parity_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _semantic_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "final_semantic_parity_status": "semantic_parity_confirmed",
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _eligibility_record(manifest_id="manifest_a", fixture_set_id="set_a", status="eligible_for_controlled_test_consumption", authorization_state="non_production_authoritative"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "eligibility_status": status,
        "authorization_state": authorization_state,
        "eligibility_authorizes_production_routing": False,
        "production_output_affected": False,
    }
