from app.planner_adapters.v3_1.limited_experimental_runtime_dry_run import build_limited_experimental_runtime_dry_run
from scripts.report_v3_1_limited_experimental_runtime_dry_run import build_v3_1_limited_experimental_runtime_dry_run_report


def test_valid_guard_readiness_manifest_evidence_produces_dry_run_ready():
    result = _build()

    record = result["limited_experimental_runtime_dry_run_records"][0]
    assert record["dry_run_status"] == "dry_run_ready"
    assert result["summary"]["dry_run_ready_count"] == 1


def test_missing_guard_blocks():
    result = _build(guards=[])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_missing_guard_contract"


def test_invalid_guard_status_blocks():
    result = _build(guards=[_guard_record(status="blocked_missing_non_production_manifest")])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_invalid_guard_status"


def test_missing_promotion_readiness_blocks():
    result = _build(readiness=[])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_missing_promotion_readiness"


def test_invalid_authorization_state_blocks():
    result = _build(guards=[_guard_record(authorization_state="production_authoritative")])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_invalid_authorization_state"


def test_runtime_consumption_enabled_blocks():
    guards = _payload("limited_experimental_runtime_guard_records", [_guard_record()])
    guards["summary"]["runtime_manifest_consumption_enabled"] = True
    result = build_limited_experimental_runtime_dry_run(
        limited_experimental_runtime_guards=guards,
        controlled_consumption_promotion_readiness=_payload("promotion_readiness_records", [_readiness_record()]),
        admission_aware_manifest_serialization=_payload("serialized_manifests", [_manifest_record()]),
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()]),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()]),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()]),
    )

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_runtime_consumption_enabled"


def test_production_routing_authorized_blocks():
    guards = _payload("limited_experimental_runtime_guard_records", [_guard_record()])
    guards["summary"]["production_default_routing_authorized"] = True
    result = build_limited_experimental_runtime_dry_run(
        limited_experimental_runtime_guards=guards,
        controlled_consumption_promotion_readiness=_payload("promotion_readiness_records", [_readiness_record()]),
        admission_aware_manifest_serialization=_payload("serialized_manifests", [_manifest_record()]),
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()]),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()]),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()]),
    )

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_production_routing_authorized"


def test_missing_manifest_blocks():
    result = _build(manifests=[])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_missing_manifest"


def test_missing_validated_evidence_blocks():
    result = _build(validations=[])

    assert result["limited_experimental_runtime_dry_run_records"][0]["dry_run_status"] == "blocked_missing_validated_evidence"


def test_deterministic_ordering():
    first = _build(
        guards=[_guard_record("manifest_b", "set_b"), _guard_record("manifest_a", "set_a")],
        readiness=[_readiness_record("manifest_b", "set_b"), _readiness_record("manifest_a", "set_a")],
        manifests=[_manifest_record("manifest_b", "set_b"), _manifest_record("manifest_a", "set_a")],
        validations=[_validation_record("manifest_b", "set_b"), _validation_record("manifest_a", "set_a")],
        structural=[_structural_record("manifest_b", "set_b"), _structural_record("manifest_a", "set_a")],
        semantic=[_semantic_record("manifest_b", "set_b"), _semantic_record("manifest_a", "set_a")],
    )
    second = _build(
        guards=[_guard_record("manifest_a", "set_a"), _guard_record("manifest_b", "set_b")],
        readiness=[_readiness_record("manifest_a", "set_a"), _readiness_record("manifest_b", "set_b")],
        manifests=[_manifest_record("manifest_a", "set_a"), _manifest_record("manifest_b", "set_b")],
        validations=[_validation_record("manifest_a", "set_a"), _validation_record("manifest_b", "set_b")],
        structural=[_structural_record("manifest_a", "set_a"), _structural_record("manifest_b", "set_b")],
        semantic=[_semantic_record("manifest_a", "set_a"), _semantic_record("manifest_b", "set_b")],
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["limited_experimental_runtime_dry_run_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_limited_experimental_runtime_dry_run_report()
    second = build_v3_1_limited_experimental_runtime_dry_run_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["limited_experimental_runtime_dry_run"]["deterministic_hash"] == second["limited_experimental_runtime_dry_run"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _build()
    record = result["limited_experimental_runtime_dry_run_records"][0]

    assert result["safety_confirmations"]["dry_run_enables_runtime_routing"] is False
    assert result["safety_confirmations"]["dry_run_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["dry_run_is_production_approval"] is False
    assert record["dry_run_enables_runtime_routing"] is False


def _build(guards=None, readiness=None, manifests=None, validations=None, structural=None, semantic=None):
    return build_limited_experimental_runtime_dry_run(
        limited_experimental_runtime_guards=_payload("limited_experimental_runtime_guard_records", [_guard_record()] if guards is None else guards),
        controlled_consumption_promotion_readiness=_payload("promotion_readiness_records", [_readiness_record()] if readiness is None else readiness),
        admission_aware_manifest_serialization=_payload("serialized_manifests", [_manifest_record()] if manifests is None else manifests),
        controlled_consumption_output_validation=_payload("validation_records", [_validation_record()] if validations is None else validations),
        controlled_consumption_parity_snapshot=_payload("parity_records", [_structural_record()] if structural is None else structural),
        trace_backfilled_semantic_parity=_payload("trace_backfilled_semantic_parity_records", [_semantic_record()] if semantic is None else semantic),
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


def _guard_record(manifest_id="manifest_a", fixture_set_id="set_a", status="guard_contract_ready", authorization_state="non_production_authoritative"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "guard_contract_status": status,
        "promotion_readiness_status": "ready_for_limited_experimental_runtime_consideration",
        "authorization_state": authorization_state,
        "runtime_consumption_enabled": False,
        "production_routing_authorized": False,
        "guard_readiness_enables_runtime_behavior": False,
        "guard_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
    }


def _readiness_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "promotion_readiness_status": "ready_for_limited_experimental_runtime_consideration",
        "promotion_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
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


def _validation_record(manifest_id="manifest_a", fixture_set_id="set_a"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "validation_status": "valid_controlled_test_output",
        "traceability_summary": {"authorization_state": "non_production_authoritative"},
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
