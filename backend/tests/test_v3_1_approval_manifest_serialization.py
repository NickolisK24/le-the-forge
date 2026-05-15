from copy import deepcopy

from app.planner_adapters.v3_1.approval_manifest_diff_audit import audit_approval_manifest_diffs
from app.planner_adapters.v3_1.approval_manifest_serialization import (
    NON_PRODUCTION_AUTHORIZATION_STATE,
    serialize_approval_manifest_candidates,
)
from scripts.report_v3_1_approval_manifest_serialization import build_v3_1_approval_manifest_serialization_report


def test_deterministic_manifest_serialization():
    first = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_b"), _candidate("set_a")]))
    second = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a"), _candidate("set_b")]))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["serialized_manifests"]] == ["set_a", "set_b"]
    assert first["summary"]["serialized_manifest_count"] == 2


def test_non_ready_candidates_are_excluded():
    result = serialize_approval_manifest_candidates(
        approval_manifest_candidates=_candidate_envelope([_candidate("set_a", candidate_status="excluded_not_ready", reasons=["policy_unsupported"])])
    )

    assert result["summary"]["serialized_manifest_count"] == 0
    assert result["summary"]["excluded_count"] == 1
    assert result["excluded_candidates"][0]["serialization_status"] == "excluded_not_ready"
    assert result["exclusion_reason_counts"]["policy_unsupported"] == 1


def test_manifest_hashes_remain_stable():
    first = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a")]))
    second = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a")]))

    assert first["serialized_manifests"][0]["generated_hash"] == second["serialized_manifests"][0]["generated_hash"]
    assert first["serialized_manifests"][0]["authorization_status"]["authorization_state"] == NON_PRODUCTION_AUTHORIZATION_STATE


def test_diff_audit_detects_added_removed_and_changed_records():
    before = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a"), _candidate("set_b")]))
    after = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_b"), _candidate("set_c")]))
    changed_hash_after = deepcopy(before)
    changed_hash_after["serialized_manifests"][0]["generated_hash"] = "changed"
    changed_metadata_after = deepcopy(before)
    changed_metadata_after["serialized_manifests"][0]["metadata"]["review_note"] = "changed"

    added_removed = audit_approval_manifest_diffs(before=before, after=after)
    changed_hash = audit_approval_manifest_diffs(before=before, after=changed_hash_after)
    changed_metadata = audit_approval_manifest_diffs(before=before, after=changed_metadata_after)

    assert added_removed["classification_counts"]["added"] == 1
    assert added_removed["classification_counts"]["removed"] == 1
    assert changed_hash["classification_counts"]["changed_hash"] == 1
    assert changed_metadata["classification_counts"]["changed_metadata"] == 1


def test_authorization_state_changes_are_high_risk_blocked():
    before = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a")]))
    after = deepcopy(before)
    after["serialized_manifests"][0]["authorization_status"]["authorization_state"] = "production_authoritative"
    result = audit_approval_manifest_diffs(before=before, after=after)

    record = result["diff_records"][0]
    assert record["diff_classification"] == "changed_authorization_state"
    assert record["high_risk"] is True
    assert record["blocked"] is True
    assert result["diff_summary"]["blocked_high_risk_count"] == 1


def test_report_generation_is_stable_and_non_authoritative():
    first = build_v3_1_approval_manifest_serialization_report()
    second = build_v3_1_approval_manifest_serialization_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["approval_manifest_serialization"]["deterministic_hash"] == second["approval_manifest_serialization"]["deterministic_hash"]
    assert first["summary"] == second["summary"]
    assert first["production_default_routing_authorized"] is False


def test_no_production_routing_enablement():
    result = serialize_approval_manifest_candidates(approval_manifest_candidates=_candidate_envelope([_candidate("set_a")]))
    manifest = result["serialized_manifests"][0]

    assert result["safety_confirmations"]["serialized_manifests_authorize_production_routing"] is False
    assert result["safety_confirmations"]["serialized_manifests_are_production_approved"] is False
    assert manifest["authorization_status"]["manifest_authorizes_production_routing"] is False
    assert manifest["authorization_status"]["manifest_is_production_approved"] is False
    assert manifest["non_production_authoritative"] is True


def _candidate_envelope(candidates):
    return {
        "schema_version": "v3_1.approval_manifest_candidates.1",
        "deterministic_hash": "candidate-hash",
        "manifest_candidates": candidates,
    }


def _candidate(set_id, candidate_status="candidate_ready", policy="passes_policy", reasons=None):
    return {
        "manifest_candidate_id": f"candidate_{set_id}",
        "fixture_set_id": set_id,
        "candidate_status": candidate_status,
        "source_summary": {
            "set_key": set_id,
            "associated_fixture_ids": [f"fixture_{set_id}"],
            "input_statuses": {f"fixture_{set_id}": "reviewed"},
        },
        "policy_summary": {
            "policy_outcome": policy,
            "valid_policy_state": policy == "passes_policy",
        },
        "readiness_summary": {
            "readiness_classification": "ready_for_approval_review",
            "block_reason_codes": [],
        },
        "authorization_status": {
            "candidate_is_production_approved": False,
            "candidate_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "trusted_default_routing": False,
        },
        "reason_codes": reasons or ["ready_for_approval_review_policy_passed"],
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }
