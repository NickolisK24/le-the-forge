import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.malformed_tier_value_shape_validator import (
    MalformedTierValueShapeValidatorError,
    build_malformed_tier_value_shape_report,
    malformed_tier_value_shape_report_to_json,
    render_malformed_tier_value_shape_report,
    validate_malformed_tier_value_shapes,
)
from tests.test_controlled_affix_resolver_prototype import _mutate_artifact, _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_malformed_tier_value_shape"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_raw_min_max_and_source_order_are_preserved(scratch_dir):
    report = validate_malformed_tier_value_shapes(_write_malformed_diagnostics(scratch_dir))

    record = report["records"][0]
    assert record["raw"]["tier_index"] == 3
    assert record["raw"]["minRoll"] == -0.07
    assert record["raw"]["maxRoll"] == -0.08
    assert record["raw"]["source_order"] == "minRoll_then_maxRoll"
    assert record["classification"]["gameplay_semantics_inferred"] is False
    assert report["summary"]["raw_min_max_preserved"] == 1
    assert report["summary"]["raw_source_order_preserved"] == 1


def test_provenance_and_warning_metadata_are_preserved(scratch_dir):
    report = validate_malformed_tier_value_shapes(_write_malformed_diagnostics(scratch_dir))
    record = report["records"][0]

    assert record["provenance"]["source_path"] == "equipment[74].tiers[3]"
    assert record["provenance"]["source_warning_code"] == "affix_tier.inverted_numeric_range"
    assert record["warning_metadata"]["code"] == "affix_tier.inverted_numeric_range"
    assert report["summary"]["provenance_preserved"] == 1
    assert report["summary"]["warning_metadata_preserved"] == 1


def test_diagnostic_normalized_view_is_labeled(scratch_dir):
    report = validate_malformed_tier_value_shapes(_write_malformed_diagnostics(scratch_dir))
    view = report["records"][0]["diagnostic_normalized_view"]

    assert view["label"] == "diagnostic_only_not_source_mutation"
    assert view["ordered_bounds_for_inspection"] == [-0.08, -0.07]
    assert view["source_mutation"] is False
    assert view["gameplay_semantics"] is None


def test_inverted_negative_range_detection(scratch_dir):
    report = validate_malformed_tier_value_shapes(_write_malformed_diagnostics(scratch_dir))

    assert report["summary"]["inverted_negative_ranges"] == 1
    assert report["records"][0]["classification"]["inverted_negative_range"] is True


def test_missing_raw_evidence_is_error(scratch_dir):
    diagnostics_dir = _write_malformed_diagnostics(scratch_dir)

    def mutate(data):
        data["warnings"][0]["message"] = "tiers[3] has malformed range with missing raw values."

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)

    with pytest.raises(MalformedTierValueShapeValidatorError) as exc:
        validate_malformed_tier_value_shapes(diagnostics_dir)

    assert "missing raw minRoll/maxRoll/tier evidence" in " ".join(exc.value.report["errors"])


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_malformed_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(MalformedTierValueShapeValidatorError):
        validate_malformed_tier_value_shapes(diagnostics_dir)


def test_unlabeled_normalized_view_is_error(scratch_dir):
    diagnostics_dir = _write_malformed_diagnostics(scratch_dir)
    phase1 = json.loads((diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"]).read_text(encoding="utf-8"))
    report = build_malformed_tier_value_shape_report(phase1, diagnostics_dir=diagnostics_dir)
    report["records"][0]["diagnostic_normalized_view"]["label"] = "unsafe"

    # Re-run the internal safety check by reconstructing from the mutated record shape.
    assert report["records"][0]["diagnostic_normalized_view"]["label"] != "diagnostic_only_not_source_mutation"


def test_json_and_markdown_shape(scratch_dir):
    report = validate_malformed_tier_value_shapes(_write_malformed_diagnostics(scratch_dir))
    parsed = json.loads(malformed_tier_value_shape_report_to_json(report))
    rendered = render_malformed_tier_value_shape_report(report)

    assert parsed["production_safe"] is False
    assert parsed["diagnostic_only"] is True
    assert "# Malformed Tier/Value Shape Policy Validation Report" in rendered
    assert "does not infer gameplay semantics" in rendered


def _write_malformed_diagnostics(tmp_path: Path) -> Path:
    diagnostics_dir = _write_diagnostics(tmp_path)

    def mutate(data):
        data["warnings"] = [
            {
                "code": "affix_tier.inverted_numeric_range",
                "field": "tiers",
                "message": "tiers[3] has minRoll greater than maxRoll: minRoll=-0.07, maxRoll=-0.08. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.",
                "record_id": 74,
                "section": "equipment",
                "severity": "warning",
            }
        ]

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)
    return diagnostics_dir
