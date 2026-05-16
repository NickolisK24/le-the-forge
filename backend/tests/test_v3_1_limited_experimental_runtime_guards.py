from app.planner_adapters.v3_1.limited_experimental_runtime_guards import build_limited_experimental_runtime_guards
from scripts.report_v3_1_limited_experimental_runtime_guards import build_v3_1_limited_experimental_runtime_guards_report


def test_valid_promotion_readiness_evidence_produces_guard_contract_ready():
    result = _build()

    record = result["limited_experimental_runtime_guard_records"][0]
    assert record["guard_contract_status"] == "guard_contract_ready"
    assert result["summary"]["guard_contract_ready_count"] == 1


def test_missing_promotion_readiness_blocks():
    result = _build(readiness=[])

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_missing_promotion_readiness"


def test_invalid_eligibility_blocks():
    result = _build(eligibility=[_eligibility_record(status="blocked_missing_hash")])

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_invalid_manifest_eligibility"


def test_invalid_authorization_state_blocks():
    result = _build(eligibility=[_eligibility_record(authorization_state="production_authoritative")])

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_invalid_authorization_state"


def test_runtime_consumption_enabled_blocks():
    result = _build(assumptions={"runtime_manifest_consumption_enabled": True})

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_runtime_consumption_enabled"


def test_production_routing_authorized_blocks():
    result = _build(assumptions={"production_default_routing_authorized": True})

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_production_routing_authorized"


def test_missing_non_production_manifest_blocks():
    result = _build(manifests=[])

    assert result["limited_experimental_runtime_guard_records"][0]["guard_contract_status"] == "blocked_missing_non_production_manifest"


def test_deterministic_ordering():
    first = _build(
        readiness=[_readiness_record("manifest_b", "set_b"), _readiness_record("manifest_a", "set_a")],
        eligibility=[_eligibility_record("manifest_b", "set_b"), _eligibility_record("manifest_a", "set_a")],
        manifests=[_manifest_record("manifest_b", "set_b"), _manifest_record("manifest_a", "set_a")],
    )
    second = _build(
        readiness=[_readiness_record("manifest_a", "set_a"), _readiness_record("manifest_b", "set_b")],
        eligibility=[_eligibility_record("manifest_a", "set_a"), _eligibility_record("manifest_b", "set_b")],
        manifests=[_manifest_record("manifest_a", "set_a"), _manifest_record("manifest_b", "set_b")],
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["manifest_id"] for row in first["limited_experimental_runtime_guard_records"]] == ["manifest_a", "manifest_b"]


def test_stable_report_generation():
    first = build_v3_1_limited_experimental_runtime_guards_report()
    second = build_v3_1_limited_experimental_runtime_guards_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["limited_experimental_runtime_guards"]["deterministic_hash"] == second["limited_experimental_runtime_guards"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = _build()
    record = result["limited_experimental_runtime_guard_records"][0]

    assert result["safety_confirmations"]["guard_readiness_enables_runtime_behavior"] is False
    assert result["safety_confirmations"]["guard_readiness_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["guard_readiness_is_production_approval"] is False
    assert record["guard_readiness_enables_runtime_behavior"] is False


def _build(readiness=None, eligibility=None, manifests=None, assumptions=None):
    return build_limited_experimental_runtime_guards(
        controlled_consumption_promotion_readiness=_payload("promotion_readiness_records", [_readiness_record()] if readiness is None else readiness),
        manifest_consumption_eligibility=_payload("eligibility_records", [_eligibility_record()] if eligibility is None else eligibility),
        admission_aware_manifest_serialization=_payload("serialized_manifests", [_manifest_record()] if manifests is None else manifests),
        production_non_consumption_assumptions=assumptions
        or {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_default_routing_authorized": False,
        },
    )


def _payload(key, records):
    return {
        "schema_version": f"v3_1.test.{key}.1",
        "deterministic_hash": f"{key}-hash",
        "summary": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_default_routing_authorized": False,
        },
        "safety_confirmations": {
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_planner_routing_changed": False,
        },
        key: records,
    }


def _readiness_record(manifest_id="manifest_a", fixture_set_id="set_a", status="ready_for_limited_experimental_runtime_consideration"):
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "promotion_readiness_status": status,
        "eligibility_status": "eligible_for_controlled_test_consumption",
        "promotion_readiness_authorizes_production_routing": False,
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
