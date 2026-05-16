import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_contracts import (
    EXPLANATION_LABELS,
    build_runtime_explanation_manifest,
    default_runtime_explanation_contracts,
    serialize_runtime_explanation_manifest,
)
from app.runtime_intelligence.explanation_hashing import (
    hash_explanation_manifest,
    validate_explanation_replay_stability,
)
from app.runtime_intelligence.explanation_registry import (
    detect_duplicate_explanation_contracts,
    export_explanation_registry,
    validate_explanation_registry,
)
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from scripts.report_v3_3_runtime_explanation_contracts import build_v3_3_runtime_explanation_contracts_report


def _deps():
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
    )
    return classifications, evidence, provenance, reasoning


def test_deterministic_ordering_stability():
    classifications, evidence, provenance, reasoning = _deps()
    rows = list(reversed(default_runtime_explanation_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
    )))
    manifest = build_runtime_explanation_manifest(
        rows,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
    )
    assert [row["explanation_label"] for row in manifest["explanation_contracts"]] == list(EXPLANATION_LABELS)
    assert [row["deterministic_rank"] for row in manifest["explanation_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["explanation_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_explanation_manifest()
    second = build_runtime_explanation_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_explanation_manifest(first) == hash_explanation_manifest(second)


def test_duplicate_explanation_contract_rejection():
    rows = default_runtime_explanation_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_explanation_registry(duplicate)
    detection = detect_duplicate_explanation_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_explanation_contracts_detected" in validation["validation_errors"]
    assert rows[0]["explanation_type_id"] in detection["duplicate_explanation_type_ids"]
    assert rows[0]["explanation_label"] in detection["duplicate_explanation_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_explanation_manifest()
    replay = validate_explanation_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_explanation_serialization_stability():
    manifest = build_runtime_explanation_manifest()
    first = serialize_runtime_explanation_manifest(manifest)
    second = serialize_runtime_explanation_manifest(json.loads(first))
    assert first == second


def test_visibility_fields_are_explicit():
    validation = export_explanation_registry()["registry_validation"]
    assert validation["blocker_visible_explanation_visible"] is True
    assert validation["risk_visible_explanation_visible"] is True
    assert validation["limitation_visible_explanation_visible"] is True
    assert validation["confidence_visible_explanation_visible"] is True
    assert validation["unsupported_explanation_visible"] is True
    assert validation["decision_boundary_explanation_visible"] is True


def test_explanation_to_evidence_compatibility():
    registry = export_explanation_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_evidence_reference_count"] == 0


def test_explanation_to_provenance_compatibility():
    registry = export_explanation_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_provenance_reference_count"] == 0


def test_explanation_to_classification_compatibility():
    registry = export_explanation_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_explanation_to_reasoning_compatibility():
    registry = export_explanation_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_reasoning_stage_reference_count"] == 0


def test_required_explanation_section_validation():
    registry = export_explanation_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["required_section_violation_count"] == 0
    rows = default_runtime_explanation_contracts()
    rows[0] = {**rows[0], "required_explanation_sections": []}
    validation = validate_explanation_registry(rows)
    assert validation["valid"] is False
    assert "required_explanation_sections_invalid" in validation["validation_errors"]


def test_invalid_evidence_reference_rejection():
    rows = default_runtime_explanation_contracts()
    rows[0] = {**rows[0], "allowed_evidence_type_ids": ["missing_evidence_type_id"]}
    validation = validate_explanation_registry(rows)
    assert validation["valid"] is False
    assert "invalid_evidence_references" in validation["validation_errors"]
    assert validation["invalid_evidence_reference_count"] == 1


def test_invalid_provenance_reference_rejection():
    rows = default_runtime_explanation_contracts()
    rows[0] = {**rows[0], "allowed_provenance_type_ids": ["missing_provenance_type_id"]}
    validation = validate_explanation_registry(rows)
    assert validation["valid"] is False
    assert "invalid_provenance_references" in validation["validation_errors"]
    assert validation["invalid_provenance_reference_count"] == 1


def test_invalid_classification_reference_rejection():
    rows = default_runtime_explanation_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_explanation_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_invalid_reasoning_stage_reference_rejection():
    rows = default_runtime_explanation_contracts()
    rows[0] = {**rows[0], "allowed_reasoning_stage_ids": ["missing_reasoning_stage_id"]}
    validation = validate_explanation_registry(rows)
    assert validation["valid"] is False
    assert "invalid_reasoning_stage_references" in validation["validation_errors"]
    assert validation["invalid_reasoning_stage_reference_count"] == 1


def test_repeat_run_stability():
    first = export_explanation_registry()
    second = export_explanation_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_explanation_manifest()
    assert manifest["runtime_explanation_planning_only"] is True
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["explanation_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_explanation_contracts_report()
    second = build_v3_3_runtime_explanation_contracts_report()
    assert first["summary"]["total_explanation_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["unsupported_explanation_count"] == 1
    assert first["summary"]["decision_boundary_explanation_count"] == 1
    assert first["summary"]["production_authorized_explanation_count"] == 0
    assert first["summary"]["invalid_evidence_reference_count"] == 0
    assert first["summary"]["invalid_provenance_reference_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["summary"]["invalid_reasoning_stage_reference_count"] == 0
    assert first["summary"]["required_section_violation_count"] == 0
    assert first["explanation_manifest"]["deterministic_hash"] == second["explanation_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["active_runtime_reasoning_decisions_enabled"] is False
    assert first["safety_confirmations"]["recommendation_logic_enabled"] is False
