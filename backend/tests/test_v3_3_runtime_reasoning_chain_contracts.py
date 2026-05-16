import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import (
    REASONING_STAGE_LABELS,
    build_runtime_reasoning_chain_manifest,
    default_runtime_reasoning_chain_contracts,
    serialize_runtime_reasoning_chain_manifest,
)
from app.runtime_intelligence.reasoning_chain_hashing import (
    hash_reasoning_chain_manifest,
    validate_reasoning_chain_replay_stability,
)
from app.runtime_intelligence.reasoning_chain_registry import (
    detect_duplicate_reasoning_stage_contracts,
    export_reasoning_chain_registry,
    validate_reasoning_chain_registry,
)
from scripts.report_v3_3_runtime_reasoning_chain_contracts import build_v3_3_runtime_reasoning_chain_contracts_report


def _deps():
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    return classifications, evidence, provenance


def test_deterministic_ordering_stability():
    classifications, evidence, provenance = _deps()
    rows = list(reversed(default_runtime_reasoning_chain_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance)))
    manifest = build_runtime_reasoning_chain_manifest(rows, classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance)
    assert [row["stage_label"] for row in manifest["reasoning_stage_contracts"]] == list(REASONING_STAGE_LABELS)
    assert [row["deterministic_rank"] for row in manifest["reasoning_stage_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["reasoning_stage_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_reasoning_chain_manifest()
    second = build_runtime_reasoning_chain_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_reasoning_chain_manifest(first) == hash_reasoning_chain_manifest(second)


def test_duplicate_reasoning_stage_contract_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_reasoning_chain_registry(duplicate)
    detection = detect_duplicate_reasoning_stage_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_reasoning_stage_contracts_detected" in validation["validation_errors"]
    assert rows[0]["stage_type_id"] in detection["duplicate_stage_type_ids"]
    assert rows[0]["stage_label"] in detection["duplicate_stage_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_reasoning_chain_manifest()
    replay = validate_reasoning_chain_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_reasoning_chain_serialization_stability():
    manifest = build_runtime_reasoning_chain_manifest()
    first = serialize_runtime_reasoning_chain_manifest(manifest)
    second = serialize_runtime_reasoning_chain_manifest(json.loads(first))
    assert first == second


def test_blocker_risk_limitation_and_decision_boundary_visibility():
    validation = export_reasoning_chain_registry()["registry_validation"]
    assert validation["blocker_capable_stage_visible"] is True
    assert validation["risk_capable_stage_visible"] is True
    assert validation["limitation_capable_stage_visible"] is True
    assert validation["decision_boundary_stage_visible"] is True


def test_reasoning_to_evidence_compatibility():
    registry = export_reasoning_chain_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_evidence_reference_count"] == 0


def test_reasoning_to_provenance_compatibility():
    registry = export_reasoning_chain_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_provenance_reference_count"] == 0


def test_reasoning_to_classification_compatibility():
    registry = export_reasoning_chain_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_required_previous_stage_validation():
    registry = export_reasoning_chain_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_previous_stage_reference_count"] == 0
    assert registry["registry_validation"]["previous_stage_rank_violation_count"] == 0


def test_invalid_evidence_reference_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    rows[0] = {**rows[0], "allowed_evidence_type_ids": ["missing_evidence_type_id"]}
    validation = validate_reasoning_chain_registry(rows)
    assert validation["valid"] is False
    assert "invalid_evidence_references" in validation["validation_errors"]
    assert validation["invalid_evidence_reference_count"] == 1


def test_invalid_provenance_reference_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    rows[0] = {**rows[0], "allowed_provenance_type_ids": ["missing_provenance_type_id"]}
    validation = validate_reasoning_chain_registry(rows)
    assert validation["valid"] is False
    assert "invalid_provenance_references" in validation["validation_errors"]
    assert validation["invalid_provenance_reference_count"] == 1


def test_invalid_classification_reference_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_reasoning_chain_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_invalid_previous_stage_reference_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    rows[1] = {**rows[1], "required_previous_stage_ids": ["missing_stage_id"]}
    validation = validate_reasoning_chain_registry(rows)
    assert validation["valid"] is False
    assert "invalid_previous_stage_references" in validation["validation_errors"]
    assert validation["invalid_previous_stage_reference_count"] == 1


def test_previous_stage_rank_ordering_rejection():
    rows = default_runtime_reasoning_chain_contracts()
    rows[0] = {**rows[0], "required_previous_stage_ids": [rows[-1]["stage_type_id"]]}
    validation = validate_reasoning_chain_registry(rows)
    assert validation["valid"] is False
    assert "previous_stage_rank_ordering_invalid" in validation["validation_errors"]
    assert validation["previous_stage_rank_violation_count"] == 1


def test_repeat_run_stability():
    first = export_reasoning_chain_registry()
    second = export_reasoning_chain_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_reasoning_chain_manifest()
    assert manifest["runtime_reasoning_planning_only"] is True
    assert manifest["runtime_evidence_synthesis_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["reasoning_stage_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_reasoning_chain_contracts_report()
    second = build_v3_3_runtime_reasoning_chain_contracts_report()
    assert first["summary"]["total_reasoning_chain_stage_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["decision_boundary_stage_count"] == 1
    assert first["summary"]["production_authorized_stage_count"] == 0
    assert first["summary"]["invalid_evidence_reference_count"] == 0
    assert first["summary"]["invalid_provenance_reference_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["summary"]["invalid_previous_stage_reference_count"] == 0
    assert first["reasoning_chain_manifest"]["deterministic_hash"] == second["reasoning_chain_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["active_runtime_reasoning_decisions_enabled"] is False
