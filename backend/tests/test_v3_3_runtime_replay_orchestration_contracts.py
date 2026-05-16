import json

from app.runtime_intelligence.replay_orchestration_contracts import (
    REPLAY_LABELS,
    build_runtime_replay_orchestration_manifest,
    default_runtime_replay_orchestration_contracts,
    serialize_runtime_replay_orchestration_manifest,
)
from app.runtime_intelligence.replay_orchestration_hashing import (
    hash_replay_orchestration_manifest,
    validate_replay_orchestration_replay_stability,
)
from app.runtime_intelligence.replay_orchestration_registry import (
    detect_duplicate_replay_orchestration_contracts,
    export_replay_orchestration_registry,
    validate_replay_orchestration_registry,
)
from scripts.report_v3_3_runtime_replay_orchestration_contracts import build_v3_3_runtime_replay_orchestration_contracts_report


def test_deterministic_ordering_stability():
    rows = list(reversed(default_runtime_replay_orchestration_contracts()))
    manifest = build_runtime_replay_orchestration_manifest(rows)
    assert [row["replay_label"] for row in manifest["replay_contracts"]] == list(REPLAY_LABELS)
    assert [row["deterministic_rank"] for row in manifest["replay_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["replay_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_replay_orchestration_manifest()
    second = build_runtime_replay_orchestration_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_replay_orchestration_manifest(first) == hash_replay_orchestration_manifest(second)


def test_duplicate_replay_orchestration_contract_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_replay_orchestration_registry(duplicate)
    detection = detect_duplicate_replay_orchestration_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_replay_orchestration_contracts_detected" in validation["validation_errors"]
    assert rows[0]["replay_type_id"] in detection["duplicate_replay_type_ids"]
    assert rows[0]["replay_label"] in detection["duplicate_replay_labels"]


def test_deterministic_replay_validation():
    replay = validate_replay_orchestration_replay_stability(build_runtime_replay_orchestration_manifest())
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_replay_orchestration_serialization_stability():
    manifest = build_runtime_replay_orchestration_manifest()
    first = serialize_runtime_replay_orchestration_manifest(manifest)
    second = serialize_runtime_replay_orchestration_manifest(json.loads(first))
    assert first == second


def test_required_previous_replay_and_rank_validation():
    validation = export_replay_orchestration_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_previous_replay_reference_count"] == 0
    assert validation["previous_replay_rank_violation_count"] == 0


def test_invalid_previous_replay_reference_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[1] = {**rows[1], "required_previous_replay_type_ids": ["missing_replay_id"]}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "invalid_previous_replay_references" in validation["validation_errors"]


def test_previous_replay_rank_violation_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[0] = {**rows[0], "required_previous_replay_type_ids": [rows[-1]["replay_type_id"]]}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "previous_replay_rank_ordering_invalid" in validation["validation_errors"]


def test_hash_requirement_validation():
    validation = export_replay_orchestration_registry()["registry_validation"]
    assert validation["hash_requirement_violation_count"] == 0


def test_input_hash_requirement_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[0] = {**rows[0], "requires_input_hash": False}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "hash_requirement_invalid" in validation["validation_errors"]


def test_output_hash_requirement_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[-2] = {**rows[-2], "requires_output_hash": False}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "hash_requirement_invalid" in validation["validation_errors"]


def test_sequence_hash_requirement_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[-2] = {**rows[-2], "requires_sequence_hash": False}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "hash_requirement_invalid" in validation["validation_errors"]


def test_visibility_rule_validation():
    validation = export_replay_orchestration_registry()["registry_validation"]
    assert validation["visibility_rule_violation_count"] == 0


def test_mismatch_visibility_rejection():
    rows = default_runtime_replay_orchestration_contracts()
    rows[-3] = {**rows[-3], "mismatch_visible": False}
    validation = validate_replay_orchestration_registry(rows)
    assert validation["valid"] is False
    assert "visibility_rule_invalid" in validation["validation_errors"]


def test_drift_conflict_blocker_boundary_visibility():
    rows = {row["replay_label"]: row for row in default_runtime_replay_orchestration_contracts()}
    assert rows["replay_synthesis_sequence"]["drift_visible"] is True
    assert rows["replay_synthesis_sequence"]["conflict_visible"] is True
    assert rows["replay_confidence_sequence"]["blocker_visible"] is True
    assert rows["replay_boundary_sequence"]["boundary_visible"] is True
    assert rows["replay_reproducibility_boundary"]["reproducibility_required"] is True


def test_replay_cross_contract_compatibility():
    validation = export_replay_orchestration_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_classification_reference_count"] == 0
    assert validation["invalid_evidence_reference_count"] == 0
    assert validation["invalid_provenance_reference_count"] == 0
    assert validation["invalid_reasoning_stage_reference_count"] == 0
    assert validation["invalid_explanation_reference_count"] == 0
    assert validation["invalid_confidence_reference_count"] == 0
    assert validation["invalid_synthesis_reference_count"] == 0
    assert validation["invalid_boundary_reference_count"] == 0


def _assert_invalid_ref(field: str, error: str, count: str):
    rows = default_runtime_replay_orchestration_contracts()
    rows[0] = {**rows[0], field: ["missing_ref"]}
    validation = validate_replay_orchestration_registry(rows)
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


def test_repeat_run_stability():
    first = export_replay_orchestration_registry()
    second = export_replay_orchestration_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_replay_orchestration_manifest()
    assert manifest["runtime_replay_orchestration_planning_only"] is True
    assert manifest["live_replay_execution_enabled"] is False
    assert manifest["live_synthesis_execution_enabled"] is False
    assert manifest["live_decision_routing_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["replay_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_replay_orchestration_contracts_report()
    second = build_v3_3_runtime_replay_orchestration_contracts_report()
    assert first["summary"]["total_replay_orchestration_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["invalid_previous_replay_reference_count"] == 0
    assert first["summary"]["previous_replay_rank_violation_count"] == 0
    assert first["summary"]["hash_requirement_violation_count"] == 0
    assert first["summary"]["visibility_rule_violation_count"] == 0
    assert first["summary"]["production_authorized_replay_orchestration_count"] == 0
    assert first["replay_orchestration_manifest"]["deterministic_hash"] == second["replay_orchestration_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["live_replay_execution_enabled"] is False
