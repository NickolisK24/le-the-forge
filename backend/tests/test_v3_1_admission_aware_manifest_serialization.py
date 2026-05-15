from app.planner_adapters.v3_1.admission_aware_manifest_serialization import serialize_admission_aware_manifest_candidates
from scripts.report_v3_1_admission_aware_manifest_serialization import build_v3_1_admission_aware_manifest_serialization_report


def test_candidate_ready_records_serialize():
    result = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a")]))

    assert result["summary"]["serialized_manifest_count"] == 1
    manifest = result["serialized_manifests"][0]
    assert manifest["fixture_set_id"] == "set_a"
    assert manifest["non_production_authoritative"] is True
    assert manifest["candidate_summary"]["original_vs_admission_aware"] == "excluded_not_ready_to_candidate_ready"


def test_non_ready_records_are_excluded():
    result = serialize_admission_aware_manifest_candidates(
        admission_aware_manifest_candidates=_candidates([_candidate("set_a", status="excluded_not_ready", reasons=["still_blocked"])])
    )

    assert result["summary"]["serialized_manifest_count"] == 0
    assert result["summary"]["excluded_count"] == 1
    assert result["excluded_candidates"][0]["serialization_status"] == "excluded_not_ready"
    assert result["exclusion_reason_counts"]["still_blocked"] == 1


def test_manifest_hashes_remain_stable():
    first = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a")]))
    second = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a")]))

    assert first["serialized_manifests"][0]["generated_hash"] == second["serialized_manifests"][0]["generated_hash"]
    assert first["deterministic_hash"] == second["deterministic_hash"]


def test_deterministic_ordering():
    first = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_b"), _candidate("set_a")]))
    second = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a"), _candidate("set_b")]))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["serialized_manifests"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_admission_aware_manifest_serialization_report()
    second = build_v3_1_admission_aware_manifest_serialization_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["admission_aware_manifest_serialization"]["deterministic_hash"] == second["admission_aware_manifest_serialization"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_all_manifests_remain_non_production_authoritative():
    result = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a")]))
    manifest = result["serialized_manifests"][0]

    assert result["safety_confirmations"]["all_manifests_non_production_authoritative"] is True
    assert manifest["authorization_status"]["authorization_state"] == "non_production_authoritative"
    assert manifest["authorization_status"]["manifest_is_production_authoritative"] is False
    assert manifest["non_production_authoritative"] is True


def test_no_production_routing_enablement():
    result = serialize_admission_aware_manifest_candidates(admission_aware_manifest_candidates=_candidates([_candidate("set_a")]))
    manifest = result["serialized_manifests"][0]

    assert result["safety_confirmations"]["admission_aware_manifests_authorize_production_routing"] is False
    assert result["safety_confirmations"]["serialized_manifests_are_production_approval"] is False
    assert manifest["authorization_status"]["manifest_authorizes_production_routing"] is False
    assert manifest["authorization_status"]["manifest_is_production_approved"] is False


def _candidates(records):
    return {
        "schema_version": "v3_1.admission_aware_manifest_candidates.1",
        "deterministic_hash": "candidate-hash",
        "manifest_candidates": records,
    }


def _candidate(set_id, status="candidate_ready", reasons=None):
    return {
        "manifest_candidate_id": f"candidate_{set_id}",
        "fixture_set_id": set_id,
        "candidate_status": status,
        "original_candidate_status": "excluded_not_ready",
        "candidate_refresh_status": "promoted_to_candidate_ready_for_review",
        "original_vs_admission_aware": "excluded_not_ready_to_candidate_ready",
        "readiness_reclassification": "policy_blocker_cleared_by_admission_aware_policy",
        "source_summary": {
            "set_key": set_id,
            "associated_fixture_ids": [f"fixture_{set_id}"],
        },
        "policy_summary": {
            "admission_aware_policy_status": "policy_satisfied_for_review",
            "valid_policy_state": True,
        },
        "readiness_summary": {
            "admission_aware_readiness_status": "ready_for_approval_review",
            "remaining_blockers": [],
        },
        "non_production_authoritative": True,
        "reason_codes": reasons or ["admission_aware_ready_for_approval_review"],
        "production_output_affected": False,
    }
