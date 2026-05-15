from app.planner_adapters.v3_1.fixture_source_admission_policy import evaluate_fixture_source_admission_policy
from scripts.report_v3_1_fixture_source_admission_policy import build_v3_1_fixture_source_admission_policy_report


def test_supported_source_admitted_for_review():
    result = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows")])

    row = result["source_admission_records"][0]
    assert row["admission_status"] == "admitted_for_review"
    assert row["non_production_authorization"]["source_is_production_approved"] is False
    assert result["summary"]["admitted_for_review_count"] == 1


def test_unknown_source_blocked():
    result = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=[_record("", "baseline_fixture_workflows")])

    assert result["source_admission_records"][0]["admission_status"] == "blocked_unknown_source"
    assert result["block_reason_counts"]["unknown_source_id"] == 1


def test_missing_metadata_blocked():
    result = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows", source_path="")])

    assert result["source_admission_records"][0]["admission_status"] == "blocked_missing_metadata"
    assert result["block_reason_counts"]["missing_source_path"] == 1


def test_missing_review_evidence_blocked():
    result = evaluate_fixture_source_admission_policy(
        reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows", payload_digest=None, reason_codes=[])]
    )

    assert result["source_admission_records"][0]["admission_status"] == "blocked_missing_review_evidence"
    assert result["block_reason_counts"]["missing_review_evidence"] == 1


def test_unstable_identity_blocked():
    result = evaluate_fixture_source_admission_policy(
        reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows", source_fixture_id=None)]
    )

    assert result["source_admission_records"][0]["admission_status"] == "blocked_unstable_identity"
    assert result["block_reason_counts"]["fixture_source_identity_unstable"] == 1


def test_unsupported_schema_blocked():
    result = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=[_record("source_a", "unknown_schema")])

    assert result["source_admission_records"][0]["admission_status"] == "blocked_unsupported_schema"
    assert result["block_reason_counts"]["unsupported_source_type_unknown_schema"] == 1


def test_deterministic_ordering():
    first = evaluate_fixture_source_admission_policy(
        reviewed_fixture_inputs=[_record("source_b", "persisted_fixture_sets"), _record("source_a", "baseline_fixture_workflows")]
    )
    second = evaluate_fixture_source_admission_policy(
        reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows"), _record("source_b", "persisted_fixture_sets")]
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["source_id"] for row in first["source_admission_records"]] == ["source_a", "source_b"]


def test_stable_report_generation():
    first = build_v3_1_fixture_source_admission_policy_report()
    second = build_v3_1_fixture_source_admission_policy_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["fixture_source_admission_policy"]["deterministic_hash"] == second["fixture_source_admission_policy"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=[_record("source_a", "baseline_fixture_workflows")])
    row = result["source_admission_records"][0]

    assert result["safety_confirmations"]["admitted_sources_are_production_approved"] is False
    assert result["safety_confirmations"]["admission_policy_authorizes_production_routing"] is False
    assert row["non_production_authorization"]["source_authorizes_production_routing"] is False
    assert row["production_output_affected"] is False


def _record(
    source_id,
    source_type,
    *,
    source_path="fixture:source",
    normalized_fixture_id="fixture_a",
    source_fixture_id="fixture_a",
    payload_digest="digest",
    reason_codes=None,
):
    return {
        "normalized_fixture_id": normalized_fixture_id,
        "source_fixture_id": source_fixture_id,
        "source_id": source_id,
        "source_type": source_type,
        "source_path": source_path,
        "status": "reviewed",
        "reason_codes": ["approval_state_pending_review"] if reason_codes is None else reason_codes,
        "payload_digest": payload_digest,
        "production_output_affected": False,
        "production_routing_authorized": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }
