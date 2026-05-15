from copy import deepcopy

from app.planner_adapters.v3_1.manifest_consumption_eligibility import evaluate_manifest_consumption_eligibility
from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash
from scripts.report_v3_1_manifest_consumption_eligibility import build_v3_1_manifest_consumption_eligibility_report


def test_valid_non_production_manifest_becomes_eligible():
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([_manifest("set_a")]))

    record = result["eligibility_records"][0]
    assert record["eligibility_status"] == "eligible_for_controlled_test_consumption"
    assert record["blockers"] == []
    assert result["summary"]["eligible_count"] == 1


def test_invalid_authorization_state_blocks():
    manifest = _manifest("set_a")
    manifest["authorization_status"]["authorization_state"] = "production_authoritative"
    manifest["generated_hash"] = _hash_manifest(manifest)
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([manifest]))

    assert result["eligibility_records"][0]["eligibility_status"] == "blocked_invalid_authorization_state"
    assert "blocked_invalid_authorization_state" in result["eligibility_records"][0]["blockers"]


def test_missing_required_fields_block():
    manifest = _manifest("set_a")
    manifest.pop("source_summary")
    manifest.pop("policy_summary")
    manifest.pop("readiness_summary")
    manifest.pop("candidate_summary")
    manifest["generated_hash"] = _hash_manifest(manifest)
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([manifest]))

    record = result["eligibility_records"][0]
    assert record["eligibility_status"] == "blocked_missing_source_summary"
    assert "blocked_missing_policy_summary" in record["blockers"]
    assert "blocked_missing_readiness_summary" in record["blockers"]
    assert "blocked_missing_candidate_summary" in record["blockers"]


def test_missing_hash_blocks():
    manifest = _manifest("set_a")
    manifest.pop("generated_hash")
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([manifest]))

    assert result["eligibility_records"][0]["eligibility_status"] == "blocked_missing_hash"


def test_unstable_hash_blocks():
    manifest = _manifest("set_a")
    manifest["generated_hash"] = "unstable"
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([manifest]))

    assert result["eligibility_records"][0]["eligibility_status"] == "blocked_unstable_manifest_hash"


def test_missing_manifest_blocks():
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([]))

    assert result["eligibility_records"][0]["eligibility_status"] == "blocked_missing_manifest"
    assert result["summary"]["blocked_count"] == 1


def test_deterministic_ordering():
    first = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([_manifest("set_b"), _manifest("set_a")]))
    second = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([_manifest("set_a"), _manifest("set_b")]))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["eligibility_records"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_manifest_consumption_eligibility_report()
    second = build_v3_1_manifest_consumption_eligibility_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["manifest_consumption_eligibility"]["deterministic_hash"] == second["manifest_consumption_eligibility"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=_serialization([_manifest("set_a")]))
    record = result["eligibility_records"][0]

    assert result["safety_confirmations"]["eligibility_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["eligibility_enables_runtime_consumption"] is False
    assert result["summary"]["manifest_runtime_consumption_enabled"] is False
    assert record["controlled_test_consumption_only"] is True
    assert record["eligibility_authorizes_production_routing"] is False


def _serialization(manifests):
    return {
        "schema_version": "v3_1.admission_aware_manifest_serialization.1",
        "deterministic_hash": "serialization-hash",
        "serialized_manifests": manifests,
    }


def _manifest(set_id):
    manifest = {
        "manifest_id": f"manifest_{set_id}",
        "manifest_candidate_id": f"candidate_{set_id}",
        "fixture_set_id": set_id,
        "serialization_status": "serialized_manifest",
        "source_summary": {"set_key": set_id, "associated_fixture_ids": [f"fixture_{set_id}"]},
        "policy_summary": {"admission_aware_policy_status": "policy_satisfied_for_review", "valid_policy_state": True},
        "readiness_summary": {"admission_aware_readiness_status": "ready_for_approval_review", "remaining_blockers": []},
        "candidate_summary": {"candidate_status": "candidate_ready", "original_vs_admission_aware": "excluded_not_ready_to_candidate_ready"},
        "authorization_status": {
            "authorization_state": "non_production_authoritative",
            "manifest_authorizes_production_routing": False,
            "manifest_is_production_approved": False,
            "manifest_is_production_authoritative": False,
            "legacy_planner_ownership_preserved": True,
            "trusted_default_routing": False,
        },
        "non_production_authoritative": True,
        "reason_codes": ["admission_aware_candidate_ready_serialized_non_authoritative_manifest"],
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "stable_generation_token": "v3_1_phase_15_admission_aware_manifest_serialization_token",
        },
    }
    manifest["generated_hash"] = _hash_manifest(manifest)
    return manifest


def _hash_manifest(manifest):
    payload = deepcopy(manifest)
    payload.pop("generated_hash", None)
    return deterministic_hash({"admission_aware_serialized_manifest": payload})
