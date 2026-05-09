import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.modifier_unresolved_category_triage import (
    ModifierUnresolvedTriageError,
    build_modifier_unresolved_triage,
    modifier_unresolved_triage_to_json,
    render_modifier_unresolved_triage_report,
)
from tests.test_controlled_affix_resolver_prototype import _mutate_artifact, _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_modifier_unresolved_triage"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_unresolved_reference_classification(scratch_dir):
    report = build_modifier_unresolved_triage(_write_triage_diagnostics(scratch_dir))

    category = report["triage_categories"]["unresolved_references"]
    assert category["count"] == 1
    assert category["likely_issue"] == "missing_reference_mapping"
    assert category["eligible_for_future_diagnostic_policy"] is True
    assert category["must_remain_unresolved"] is True
    assert category["representative_examples"][0]["source_affix_identity"] == "idol:826"
    assert category["representative_examples"][0]["source_provenance_path"] == "idol[826]"


def test_malformed_structure_classification(scratch_dir):
    report = build_modifier_unresolved_triage(_write_triage_diagnostics(scratch_dir))

    category = report["triage_categories"]["malformed_structures"]
    assert category["count"] == 1
    assert category["likely_issue"] == "malformed_tier_value_shape"
    assert category["representative_examples"][0]["source_affix_identity"] == "equipment:74"
    assert category["representative_examples"][0]["source_provenance_path"] == "equipment[74].tiers"


def test_unsupported_structure_classification(scratch_dir):
    report = build_modifier_unresolved_triage(_write_triage_diagnostics(scratch_dir))

    category = report["triage_categories"]["unsupported_structures"]
    assert category["count"] == 1
    assert category["likely_issue"] == "unsupported_special_behavior"
    assert category["representative_examples"][0]["source_affix_identity"] == "equipment:910"
    assert category["representative_examples"][0]["source_provenance_path"] == "equipment[910]._extra"


def test_triage_preserves_provenance_and_affix_910_evidence(scratch_dir):
    report = build_modifier_unresolved_triage(_write_triage_diagnostics(scratch_dir))

    assert report["production_safe"] is False
    assert report["diagnostic_only"] is True
    assert report["summary"]["affix_910_duplicate_evidence_preserved"] is True
    assert report["affix_910_duplicate_evidence"]["duplicate_positions"] == [0, 1]
    for category in report["triage_categories"].values():
        assert category["source_provenance_paths"]
        assert category["representative_examples"]


def test_triage_output_is_deterministic(scratch_dir):
    diagnostics_dir = _write_triage_diagnostics(scratch_dir)

    first = modifier_unresolved_triage_to_json(build_modifier_unresolved_triage(diagnostics_dir))
    second = modifier_unresolved_triage_to_json(build_modifier_unresolved_triage(diagnostics_dir))

    assert first == second


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_triage_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(ModifierUnresolvedTriageError) as exc:
        build_modifier_unresolved_triage(diagnostics_dir)

    assert exc.value.report is not None


def test_json_and_markdown_shape(scratch_dir):
    report = build_modifier_unresolved_triage(_write_triage_diagnostics(scratch_dir))
    parsed = json.loads(modifier_unresolved_triage_to_json(report))
    rendered = render_modifier_unresolved_triage_report(report)

    assert {
        "diagnostic",
        "diagnostic_only",
        "production_safe",
        "summary",
        "triage_categories",
        "affix_910_duplicate_evidence",
    }.issubset(parsed)
    assert "# Modifier Unresolved Category Triage Report" in rendered
    assert "does not resolve gameplay semantics" in rendered


def _write_triage_diagnostics(tmp_path: Path) -> Path:
    diagnostics_dir = _write_diagnostics(tmp_path)

    def mutate(data):
        data["warnings"] = [
            {
                "code": "affix_record.idol_stat_modifier_reference_unmodeled",
                "message": "Idol affix stat/modifier references are not modeled in this source shape validator.",
                "record_id": 826,
                "section": "idol",
                "severity": "warning",
            },
            {
                "code": "affix_tier.inverted_numeric_range",
                "field": "tiers",
                "message": "tiers[3] has minRoll greater than maxRoll.",
                "record_id": 74,
                "section": "equipment",
                "severity": "warning",
            },
            {
                "code": "affix_record.extra_typetree_fields",
                "field": "_extra",
                "message": "Record carries _extra TypeTree fields that are preserved but not modeled.",
                "record_id": 910,
                "section": "equipment",
                "severity": "warning",
            },
        ]

    _mutate_artifact(diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"], mutate)
    return diagnostics_dir
