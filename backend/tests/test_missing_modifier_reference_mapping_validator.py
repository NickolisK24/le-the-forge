import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.missing_modifier_reference_mapping_validator import (
    MissingModifierReferenceMappingValidatorError,
    missing_modifier_reference_mapping_report_to_json,
    render_missing_modifier_reference_mapping_report,
    validate_missing_modifier_reference_mappings,
)
from tests.test_controlled_affix_resolver_prototype import _mutate_artifact, _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_missing_modifier_reference_mapping"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_raw_reference_evidence_is_preserved(scratch_dir):
    report = validate_missing_modifier_reference_mappings(
        _write_missing_mapping_diagnostics(scratch_dir),
        _write_comparison_report(scratch_dir),
    )

    record = report["records"][0]
    assert record["raw_reference_evidence"]["warning_code"] == "affix_record.idol_stat_modifier_reference_unmodeled"
    assert record["raw_reference_evidence"]["warning_message"] == "Idol affix stat/modifier references are not modeled."
    assert report["summary"]["raw_reference_evidence_preserved"] == 1


def test_affix_identity_provenance_and_warning_metadata_are_preserved(scratch_dir):
    report = validate_missing_modifier_reference_mappings(
        _write_missing_mapping_diagnostics(scratch_dir),
        _write_comparison_report(scratch_dir),
    )
    record = report["records"][0]

    assert record["source_affix_identity"] == "idol:826"
    assert record["provenance"]["source_path"] == "idol[826]"
    assert record["warning_metadata"]["code"] == "affix_record.idol_stat_modifier_reference_unmodeled"
    assert report["summary"]["stable_affix_source_identity_preserved"] == 1
    assert report["summary"]["provenance_preserved"] == 1
    assert report["summary"]["warning_metadata_preserved"] == 1


def test_unresolved_state_is_preserved(scratch_dir):
    report = validate_missing_modifier_reference_mappings(
        _write_missing_mapping_diagnostics(scratch_dir),
        _write_comparison_report(scratch_dir),
    )
    record = report["records"][0]

    assert record["reference_status"] == "unresolved"
    assert record["must_remain_unresolved"] is True
    assert record["resolved_modifier_identity"] is None
    assert record["normalized_inspection_structure"] is None
    assert report["summary"]["records_remaining_unresolved"] == 1


def test_name_only_mapping_inference_is_rejected(scratch_dir):
    diagnostics_dir = _write_missing_mapping_diagnostics(scratch_dir)

    def mutate(data):
        data["warnings"][0]["mapping_source"] = "display_name"

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)

    with pytest.raises(MissingModifierReferenceMappingValidatorError) as exc:
        validate_missing_modifier_reference_mappings(diagnostics_dir, _write_comparison_report(scratch_dir))

    assert "name-only mapping inference" in " ".join(exc.value.report["errors"])


def test_subtype_id_only_mapping_inference_is_rejected(scratch_dir):
    diagnostics_dir = _write_missing_mapping_diagnostics(scratch_dir)

    def mutate(data):
        data["warnings"][0]["mapping_source"] = "subtype_id"

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)

    with pytest.raises(MissingModifierReferenceMappingValidatorError) as exc:
        validate_missing_modifier_reference_mappings(diagnostics_dir, _write_comparison_report(scratch_dir))

    assert "subtype_id-only mapping inference" in " ".join(exc.value.report["errors"])


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_missing_mapping_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(MissingModifierReferenceMappingValidatorError):
        validate_missing_modifier_reference_mappings(diagnostics_dir, _write_comparison_report(scratch_dir))


def test_saved_vs_fresh_missing_is_reported_not_failed(scratch_dir):
    report = validate_missing_modifier_reference_mappings(
        _write_missing_mapping_diagnostics(scratch_dir),
        scratch_dir / "missing_comparison.json",
    )

    assert report["summary"]["saved_vs_fresh_agreement_available"] is False
    assert "not available" in " ".join(report["warnings"])
    assert report["validation_status"] == "warning"


def test_json_and_markdown_shape(scratch_dir):
    report = validate_missing_modifier_reference_mappings(
        _write_missing_mapping_diagnostics(scratch_dir),
        _write_comparison_report(scratch_dir),
    )
    parsed = json.loads(missing_modifier_reference_mapping_report_to_json(report))
    rendered = render_missing_modifier_reference_mapping_report(report)

    assert parsed["production_safe"] is False
    assert parsed["diagnostic_only"] is True
    assert parsed["summary"]["saved_vs_fresh_unresolved_delta"] == 0
    assert "# Missing Modifier Reference Mapping Policy Validation Report" in rendered
    assert "does not add modifier mappings" in rendered


def _write_missing_mapping_diagnostics(tmp_path: Path) -> Path:
    diagnostics_dir = _write_diagnostics(tmp_path)

    def mutate(data):
        data["summary"]["missing_stat_modifier_references"] = 1
        data["warnings"] = [
            {
                "code": "affix_record.idol_stat_modifier_reference_unmodeled",
                "message": "Idol affix stat/modifier references are not modeled.",
                "record_id": 826,
                "section": "idol",
                "severity": "warning",
            }
        ]

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)
    return diagnostics_dir


def _write_comparison_report(tmp_path: Path) -> Path:
    path = tmp_path / "controlled_modifier_resolver_comparison_report.json"
    path.write_text(
        json.dumps(
            {
                "comparison_status": "warning",
                "diagnostic_only": True,
                "production_safe": False,
                "count_deltas": {
                    "unresolved_modifier_objects": {
                        "saved": 1,
                        "fresh": 1,
                        "delta": 0,
                    }
                },
                "warning_category_delta": {
                    "modifier_resolution_policy::unresolved_modifier_references": {
                        "saved": 1,
                        "fresh": 1,
                        "delta": 0,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return path
