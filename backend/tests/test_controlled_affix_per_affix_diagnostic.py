import json
import shutil
import uuid
from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.controlled_affix_per_affix_diagnostic import (
    ControlledAffixPerAffixDiagnosticError,
    build_per_affix_diagnostic_artifact,
    build_per_affix_diagnostic_artifact_from_resolver,
    per_affix_diagnostic_artifact_to_json,
    render_per_affix_diagnostic_artifact,
    validate_per_affix_diagnostic_artifact,
    validate_per_affix_diagnostic_output_path,
)
from app.game_data.controlled_affix_resolver_prototype import resolve_affix_diagnostics
from tests.test_controlled_affix_resolver_prototype import _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_controlled_affix_per_affix"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_per_affix_record_shape(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    artifact = build_per_affix_diagnostic_artifact(diagnostics_dir)

    assert artifact["production_safe"] is False
    assert artifact["diagnostic_only"] is True
    assert artifact["non_production_inspection_allowed"] is True
    assert artifact["summary"]["total_records"] == 6
    assert artifact["summary"]["equipment_records"] == 4
    assert artifact["summary"]["idol_records"] == 2
    assert artifact["summary"]["embedded_tier_count"] == 12
    assert len(artifact["records"]) == 6

    record = artifact["records"][0]
    assert set(record) == {
        "production_safe",
        "diagnostic_only",
        "affix_identity",
        "display",
        "classification",
        "tier_summary",
        "provenance",
        "eligibility_summary",
        "tag_category_summary",
        "warning_categories",
        "warnings",
        "raw_duplicate_evidence",
        "diagnostic_normalized_views",
    }
    assert record["production_safe"] is False
    assert record["diagnostic_only"] is True
    assert record["affix_identity"]["stable_source_identity"] is True
    assert record["affix_identity"]["name_only"] is False
    assert record["affix_identity"]["subtype_id_only"] is False
    assert record["display"]["label_role"] == "display_only_not_identity"

    parsed = json.loads(per_affix_diagnostic_artifact_to_json(artifact))
    assert parsed["production_safe"] is False
    rendered = render_per_affix_diagnostic_artifact(artifact)
    assert "# Controlled Affix Per-Affix Diagnostic Records" in rendered
    assert "production_safe: false" in rendered


def test_affix_910_duplicate_evidence_is_preserved(scratch_dir):
    artifact = build_per_affix_diagnostic_artifact(_write_diagnostics(scratch_dir))
    affix_910 = _find_record(artifact, "equipment:910")

    assert affix_910["raw_duplicate_evidence"]["raw_duplicate_count"] == 2
    assert affix_910["raw_duplicate_evidence"]["duplicate_positions"] == [0, 1]
    assert affix_910["raw_duplicate_evidence"]["raw_canRollOn"] == ["IDOL_4x1", "IDOL_4x1"]
    assert affix_910["diagnostic_normalized_views"] == [
        {
            "view": "eligibility_unique_targets",
            "values": ["IDOL_4X1"],
            "label": "diagnostic_only_not_source_mutation",
            "source_mutation": False,
        }
    ]
    assert artifact["affix_910_evidence_summary"]["record_contains_raw_duplicate_evidence"] is True
    assert artifact["affix_910_evidence_summary"]["source_mutation"] is False


def test_warning_metadata_is_attached_to_records(scratch_dir):
    artifact = build_per_affix_diagnostic_artifact(_write_diagnostics(scratch_dir))
    affix_910 = _find_record(artifact, "equipment:910")

    assert any(warning["code"] == "affix_eligibility.duplicate_target" for warning in affix_910["warning_categories"])
    assert any(item["category"] == "affix_eligibility.duplicate_target" for item in artifact["warning_category_summary"])


def test_production_safe_true_violation_fails_validation(scratch_dir):
    artifact = build_per_affix_diagnostic_artifact(_write_diagnostics(scratch_dir))
    unsafe = deepcopy(artifact)
    unsafe["records"][0]["production_safe"] = True

    errors = validate_per_affix_diagnostic_artifact(unsafe)

    assert "records[0].production_safe must be false." in errors


def test_top_level_production_safe_true_fails_build_from_resolver(scratch_dir):
    resolver_report = resolve_affix_diagnostics(_write_diagnostics(scratch_dir))
    resolver_report["non_production_inspection_allowed"] = False

    artifact = build_per_affix_diagnostic_artifact_from_resolver(resolver_report, diagnostics_dir=scratch_dir)

    assert "non_production_inspection_allowed must be true for this diagnostic artifact." in artifact["errors"]


def test_output_is_deterministic(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    first = per_affix_diagnostic_artifact_to_json(build_per_affix_diagnostic_artifact(diagnostics_dir))
    second = per_affix_diagnostic_artifact_to_json(build_per_affix_diagnostic_artifact(diagnostics_dir))

    assert first == second


def test_generation_does_not_mutate_source_artifacts(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    before = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}

    build_per_affix_diagnostic_artifact(diagnostics_dir)

    after = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}
    assert after == before


def test_name_only_identity_is_rejected_by_record_validation(scratch_dir):
    artifact = build_per_affix_diagnostic_artifact(_write_diagnostics(scratch_dir))
    unsafe = deepcopy(artifact)
    unsafe["records"][0]["affix_identity"]["name_only"] = True

    assert "records[0] uses name-only identity." in validate_per_affix_diagnostic_artifact(unsafe)


def test_subtype_id_only_identity_is_rejected_by_record_validation(scratch_dir):
    artifact = build_per_affix_diagnostic_artifact(_write_diagnostics(scratch_dir))
    unsafe = deepcopy(artifact)
    unsafe["records"][0]["affix_identity"]["subtype_id_only"] = True

    assert "records[0] uses subtype_id-only identity." in validate_per_affix_diagnostic_artifact(unsafe)


def test_output_path_guard_refuses_production_data_directories():
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError):
        validate_per_affix_diagnostic_output_path(repo_root / "data" / "items" / "per_affix.json")


def _find_record(artifact, source_identity):
    for record in artifact["records"]:
        if record["affix_identity"]["source_identity"] == source_identity:
            return record
    raise AssertionError(f"Missing record {source_identity}")
