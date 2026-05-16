import json

from app.runtime_intelligence.drift_audit_contracts import (
    DRIFT_LABELS,
    build_runtime_drift_audit_manifest,
    default_runtime_drift_audit_contracts,
    serialize_runtime_drift_audit_manifest,
)
from app.runtime_intelligence.drift_audit_hashing import (
    hash_drift_audit_manifest,
    validate_drift_audit_replay_stability,
)
from app.runtime_intelligence.drift_audit_registry import (
    detect_duplicate_drift_audit_contracts,
    export_drift_audit_registry,
    validate_drift_audit_registry,
)
from scripts.report_v3_3_runtime_drift_audit_contracts import build_v3_3_runtime_drift_audit_contracts_report


def test_deterministic_ordering_stability():
    rows = list(reversed(default_runtime_drift_audit_contracts()))
    manifest = build_runtime_drift_audit_manifest(rows)
    assert [row["drift_label"] for row in manifest["drift_contracts"]] == list(DRIFT_LABELS)
    assert [row["deterministic_rank"] for row in manifest["drift_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["drift_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_drift_audit_manifest()
    second = build_runtime_drift_audit_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_drift_audit_manifest(first) == hash_drift_audit_manifest(second)


def test_duplicate_drift_audit_contract_rejection():
    rows = default_runtime_drift_audit_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_drift_audit_registry(duplicate)
    detection = detect_duplicate_drift_audit_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_drift_audit_contracts_detected" in validation["validation_errors"]
    assert rows[0]["drift_type_id"] in detection["duplicate_drift_type_ids"]


def test_deterministic_replay_validation():
    replay = validate_drift_audit_replay_stability(build_runtime_drift_audit_manifest())
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_drift_audit_serialization_stability():
    manifest = build_runtime_drift_audit_manifest()
    first = serialize_runtime_drift_audit_manifest(manifest)
    second = serialize_runtime_drift_audit_manifest(json.loads(first))
    assert first == second


def test_drift_category_and_action_validation():
    validation = export_drift_audit_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_drift_category_count"] == 0
    assert validation["invalid_drift_action_count"] == 0


def test_invalid_drift_category_rejection():
    rows = default_runtime_drift_audit_contracts()
    rows[0] = {**rows[0], "drift_category": "silent"}
    validation = validate_drift_audit_registry(rows)
    assert validation["valid"] is False
    assert "invalid_drift_categories" in validation["validation_errors"]


def test_invalid_drift_action_rejection():
    rows = default_runtime_drift_audit_contracts()
    rows[0] = {**rows[0], "drift_action": "silent_pass"}
    validation = validate_drift_audit_registry(rows)
    assert validation["valid"] is False
    assert "invalid_drift_actions" in validation["validation_errors"]


def test_required_behavior_validation():
    validation = export_drift_audit_registry()["registry_validation"]
    assert validation["behavior_rule_violation_count"] == 0


def test_required_behavior_rejection():
    rows = default_runtime_drift_audit_contracts()
    for index, row in enumerate(rows):
        if row["drift_label"] == "hash_manifest_drift":
            rows[index] = {**row, "requires_baseline_hash": False}
            break
    validation = validate_drift_audit_registry(rows)
    assert validation["valid"] is False
    assert "drift_behavior_rule_invalid" in validation["validation_errors"]


def test_explicit_drift_behaviors_visible():
    rows = {row["drift_label"]: row for row in default_runtime_drift_audit_contracts()}
    assert rows["confidence_boundary_drift"]["blocks_confidence_upgrade"] is True
    assert rows["production_authorization_drift"]["blocks_production_authorization"] is True
    assert rows["unsupported_state_drift"]["preserves_unsupported"] is True
    assert rows["replay_sequence_drift"]["requires_replay_validation"] is True
    assert rows["replay_sequence_drift"]["replay_mismatch_visible"] is True
    assert rows["decision_boundary_drift"]["boundary_visible"] is True
    assert rows["patch_version_drift"]["requires_diff_summary"] is True
    assert rows["provenance_lineage_drift"]["requires_manual_review"] is True


def test_drift_cross_contract_compatibility():
    validation = export_drift_audit_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_classification_reference_count"] == 0
    assert validation["invalid_evidence_reference_count"] == 0
    assert validation["invalid_provenance_reference_count"] == 0
    assert validation["invalid_reasoning_stage_reference_count"] == 0
    assert validation["invalid_explanation_reference_count"] == 0
    assert validation["invalid_confidence_reference_count"] == 0
    assert validation["invalid_synthesis_reference_count"] == 0
    assert validation["invalid_boundary_reference_count"] == 0
    assert validation["invalid_replay_reference_count"] == 0


def _assert_invalid_ref(field: str, error: str, count: str):
    rows = default_runtime_drift_audit_contracts()
    rows[0] = {**rows[0], field: ["missing_ref"]}
    validation = validate_drift_audit_registry(rows)
    assert validation["valid"] is False
    assert error in validation["validation_errors"]
    assert validation[count] == 1


def test_invalid_classification_reference_rejection():
    _assert_invalid_ref("allowed_classification_ids", "invalid_classification_references", "invalid_classification_reference_count")


def test_invalid_evidence_reference_rejection():
    _assert_invalid_ref("allowed_evidence_type_ids", "invalid_evidence_references", "invalid_evidence_reference_count")


def test_invalid_provenance_reference_rejection():
    _assert_invalid_ref("allowed_provenance_type_ids", "invalid_provenance_references", "invalid_provenance_reference_count")


def test_invalid_reasoning_stage_reference_rejection():
    _assert_invalid_ref("allowed_reasoning_stage_ids", "invalid_reasoning_stage_references", "invalid_reasoning_stage_reference_count")


def test_invalid_explanation_reference_rejection():
    _assert_invalid_ref("allowed_explanation_type_ids", "invalid_explanation_references", "invalid_explanation_reference_count")


def test_invalid_confidence_reference_rejection():
    _assert_invalid_ref("allowed_confidence_type_ids", "invalid_confidence_references", "invalid_confidence_reference_count")


def test_invalid_synthesis_reference_rejection():
    _assert_invalid_ref("allowed_synthesis_type_ids", "invalid_synthesis_references", "invalid_synthesis_reference_count")


def test_invalid_boundary_reference_rejection():
    _assert_invalid_ref("allowed_boundary_type_ids", "invalid_boundary_references", "invalid_boundary_reference_count")


def test_invalid_replay_reference_rejection():
    _assert_invalid_ref("allowed_replay_type_ids", "invalid_replay_references", "invalid_replay_reference_count")


def test_repeat_run_stability():
    first = export_drift_audit_registry()
    second = export_drift_audit_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_drift_audit_manifest()
    assert manifest["runtime_drift_audit_planning_only"] is True
    assert manifest["live_drift_detection_enabled"] is False
    assert manifest["live_replay_execution_enabled"] is False
    assert manifest["live_synthesis_execution_enabled"] is False
    assert manifest["live_decision_routing_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["drift_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_drift_audit_contracts_report()
    second = build_v3_3_runtime_drift_audit_contracts_report()
    assert first["summary"]["total_drift_audit_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["invalid_drift_category_count"] == 0
    assert first["summary"]["invalid_drift_action_count"] == 0
    assert first["summary"]["behavior_rule_violation_count"] == 0
    assert first["summary"]["production_authorized_drift_audit_count"] == 0
    assert first["drift_audit_manifest"]["deterministic_hash"] == second["drift_audit_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["live_drift_detection_enabled"] is False
