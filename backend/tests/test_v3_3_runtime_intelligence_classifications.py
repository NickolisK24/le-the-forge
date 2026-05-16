import json

from app.runtime_intelligence.classification_contracts import (
    CLASSIFICATION_LABELS,
    build_runtime_intelligence_classification_manifest,
    default_runtime_intelligence_classifications,
    serialize_classification_manifest,
)
from app.runtime_intelligence.classification_hashing import hash_classification_manifest, validate_replay_stability
from app.runtime_intelligence.classification_registry import (
    detect_duplicate_classifications,
    export_classification_registry,
    validate_classification_registry,
)
from scripts.report_v3_3_runtime_intelligence_classifications import (
    build_v3_3_runtime_intelligence_classification_report,
)


def test_deterministic_ordering_stability():
    rows = list(reversed(default_runtime_intelligence_classifications()))
    manifest = build_runtime_intelligence_classification_manifest(rows)
    assert [row["classification_label"] for row in manifest["classifications"]] == list(CLASSIFICATION_LABELS)
    assert [row["deterministic_rank"] for row in manifest["classifications"]] == sorted(row["deterministic_rank"] for row in manifest["classifications"])


def test_stable_hash_repeatability():
    first = build_runtime_intelligence_classification_manifest()
    second = build_runtime_intelligence_classification_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_classification_manifest(first) == hash_classification_manifest(second)


def test_duplicate_classification_rejection():
    rows = default_runtime_intelligence_classifications()
    duplicate = rows + [rows[0]]
    validation = validate_classification_registry(duplicate)
    detection = detect_duplicate_classifications(duplicate)
    assert validation["valid"] is False
    assert "duplicate_classifications_detected" in validation["validation_errors"]
    assert rows[0]["classification_id"] in detection["duplicate_classification_ids"]
    assert rows[0]["classification_label"] in detection["duplicate_classification_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_intelligence_classification_manifest()
    replay = validate_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_classification_serialization_stability():
    manifest = build_runtime_intelligence_classification_manifest()
    first = serialize_classification_manifest(manifest)
    second = serialize_classification_manifest(json.loads(first))
    assert first == second


def test_unsupported_classification_visibility():
    validation = validate_classification_registry(default_runtime_intelligence_classifications())
    assert validation["unsupported_classification_visible"] is True
    unsupported = [row for row in default_runtime_intelligence_classifications() if row["classification_label"] == "unsupported"][0]
    assert unsupported["drift_visible"] is True
    assert unsupported["production_authorized"] is False


def test_provenance_required_validation():
    manifest = build_runtime_intelligence_classification_manifest()
    assert all(row["provenance_required"] for row in manifest["classifications"])
    assert manifest["classifications"][0]["explainability_required"] is True


def test_authorization_prohibited_validation():
    validation = validate_classification_registry(default_runtime_intelligence_classifications())
    assert validation["authorization_prohibited_classification_visible"] is True
    assert validation["production_authorized_classifications"] == []
    auth = [row for row in default_runtime_intelligence_classifications() if row["classification_label"] == "authorization_prohibited"][0]
    assert auth["production_authorized"] is False
    assert "authorization-prohibited states must block runtime enablement" in auth["explicit_risks"]


def test_provenance_incomplete_visibility():
    validation = validate_classification_registry(default_runtime_intelligence_classifications())
    assert validation["provenance_incomplete_classification_visible"] is True


def test_repeat_run_stability():
    first = export_classification_registry()
    second = export_classification_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_intelligence_classification_manifest()
    assert manifest["runtime_intelligence_planning_only"] is True
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["classifications"])
    assert all(row["default_runtime_manifest_consumption_enabled"] is False for row in manifest["classifications"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_intelligence_classification_report()
    second = build_v3_3_runtime_intelligence_classification_report()
    assert first["summary"]["total_classification_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["unsupported_classification_count"] == 1
    assert first["summary"]["production_authorized_classification_count"] == 0
    assert first["classification_manifest"]["deterministic_hash"] == second["classification_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
