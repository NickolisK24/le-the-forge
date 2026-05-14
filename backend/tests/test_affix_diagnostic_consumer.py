import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import (
    PHASE_ARTIFACTS,
    AffixDiagnosticConsumerError,
    affix_diagnostic_report_to_json,
    consume_affix_diagnostics,
    render_affix_diagnostic_report,
    validate_affix_diagnostic_output_path,
)


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_affix_consumer"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_successful_read_only_consumption(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    report = consume_affix_diagnostics(diagnostics_dir)

    assert report["production_safe"] is False
    assert report["consumer_scope"] == "non_production_read_only"
    assert report["non_production_inspection_allowed"] is True
    assert report["summary"]["total_affixes"] == 1227
    assert report["summary"]["equipment_affixes"] == 1112
    assert report["summary"]["idol_affixes"] == 115
    assert report["summary"]["total_embedded_tiers"] == 6959
    assert report["phase_validation_statuses"]["phase_1_source_shape"] == "warning"
    assert report["phase_validation_statuses"]["phase_3_eligibility"] == "warning"
    assert report["phase5_migration_gate_status"] == "warning"
    assert any(category["category"] == "malformed_tier_ranges" for category in report["remaining_warning_categories"])
    assert "Do not use this report to power build math." in report["forbidden_production_usage"]

    parsed = json.loads(affix_diagnostic_report_to_json(report))
    assert parsed["production_safe"] is False
    rendered = render_affix_diagnostic_report(report)
    assert "# Phase 6 Affix Diagnostic Consumer Report" in rendered
    assert "inspection-only" in rendered


def test_missing_diagnostic_artifact_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    (diagnostics_dir / PHASE_ARTIFACTS["phase_2_identity_provenance"]).unlink()

    with pytest.raises(FileNotFoundError):
        consume_affix_diagnostics(diagnostics_dir)


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(AffixDiagnosticConsumerError) as exc:
        consume_affix_diagnostics(diagnostics_dir)

    assert "phase_1_source_shape reports production_safe=True" in exc.value.report["errors"][0]


def test_phase5_blocked_state_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_5_saved_vs_fresh"],
        lambda data: data.update({"migration_gate_status": "blocked"}),
    )

    with pytest.raises(AffixDiagnosticConsumerError) as exc:
        consume_affix_diagnostics(diagnostics_dir)

    assert "migration_gate_status=blocked" in " ".join(exc.value.report["errors"])


def test_affix_910_evidence_is_preserved(scratch_dir):
    report = consume_affix_diagnostics(_write_diagnostics(scratch_dir))
    evidence = report["affix_910_duplicate_eligibility_evidence"]

    assert evidence["record_id"] == 910
    assert evidence["record_path"] == "equipment[910].canRollOn"
    assert evidence["raw_canRollOn"] == ["IDOL_4x1", "IDOL_4x1"]
    assert evidence["raw_duplicate_count"] == 2
    assert evidence["duplicate_positions"] == [0, 1]
    assert evidence["diagnostic_unique_targets_label"] == "diagnostic_only_not_source_mutation"
    assert evidence["policy_result"] == "warning_only"


def test_missing_affix_910_evidence_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_3_eligibility"],
        lambda data: data.update({"warnings": []}),
    )

    with pytest.raises(AffixDiagnosticConsumerError) as exc:
        consume_affix_diagnostics(diagnostics_dir)

    assert "affix 910" in " ".join(exc.value.report["errors"]).lower()


def test_name_only_or_subtype_only_identity_findings_fail(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_3_eligibility"],
        lambda data: data["summary"].update({"eligibility_records_using_name_only_matching": 1}),
    )

    with pytest.raises(AffixDiagnosticConsumerError) as exc:
        consume_affix_diagnostics(diagnostics_dir)

    assert "name-only eligibility" in " ".join(exc.value.report["errors"])


def test_consumer_does_not_mutate_diagnostic_artifacts(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    before = {
        path.name: path.read_text(encoding="utf-8")
        for path in diagnostics_dir.iterdir()
    }

    consume_affix_diagnostics(diagnostics_dir)

    after = {
        path.name: path.read_text(encoding="utf-8")
        for path in diagnostics_dir.iterdir()
    }
    assert after == before


def test_output_path_guard_refuses_production_data_directories():
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError):
        validate_affix_diagnostic_output_path(repo_root / "data" / "items" / "affix_report.md")

    with pytest.raises(ValueError):
        validate_affix_diagnostic_output_path(repo_root.parent / "last-epoch-data" / "data_bundle" / "affix_report.md")


def _write_diagnostics(tmp_path: Path) -> Path:
    diagnostics = {
        "phase_1_source_shape": {
            "diagnostic": "affix_source_shape",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "total_affixes": 1227,
                "equipment_affixes": 1112,
                "idol_affixes": 115,
                "total_embedded_tiers": 6959,
                "ambiguous_name_collisions": 28,
                "malformed_tier_ranges": 136,
                "missing_stat_modifier_references": 115,
                "unsupported_or_unresolved_fields": 1112,
            },
            "errors": [],
            "warnings": ["shape warning"],
        },
        "phase_2_identity_provenance": {
            "diagnostic": "affix_identity_provenance",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "ambiguous_display_name_collisions": 137,
            },
            "errors": [],
            "warnings": ["identity warning"],
        },
        "phase_3_eligibility": {
            "diagnostic": "affix_eligibility",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "duplicate_or_ambiguous_eligibility_records": 1,
                "unsupported_or_unresolved_eligibility_fields": 115,
                "eligibility_records_using_name_only_matching": 0,
                "eligibility_records_using_subtype_id_only_identity": 0,
            },
            "errors": [],
            "warnings": [
                {
                    "code": "affix_eligibility.duplicate_target",
                    "field": "canRollOn",
                    "message": "Eligibility target 'IDOL_4X1' appears 2 times.",
                    "record_id": 910,
                    "record_path": "equipment[910].canRollOn",
                    "section": "equipment",
                    "severity": "warning",
                    "details": {
                        "raw_canRollOn": ["IDOL_4x1", "IDOL_4x1"],
                        "normalized_canRollOn": ["IDOL_4X1", "IDOL_4X1"],
                        "raw_duplicate_count": 2,
                        "duplicate_positions": [0, 1],
                        "diagnostic_unique_targets": ["IDOL_4X1"],
                        "diagnostic_unique_targets_label": "diagnostic_only_not_source_mutation",
                        "policy_result": "warning_only",
                        "origin_assessment": "raw-source duplicate",
                    },
                }
            ],
        },
        "phase_4_tag_category": {
            "diagnostic": "affix_tag_category",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "unknown_or_unsupported_tag_category_values": 148,
                "ambiguous_tag_category_mappings": 110,
                "duplicate_tag_category_records": 0,
                "tag_category_records_using_name_only_matching": 0,
                "tag_category_records_using_subtype_id_only_identity": 0,
            },
            "relationship_to_phase3_eligibility": "unchanged_warning_only",
            "errors": [],
            "warnings": ["tag warning"],
        },
        "phase_5_saved_vs_fresh": {
            "diagnostic": "affix_saved_vs_fresh_diagnostic_comparison",
            "production_safe": False,
            "migration_gate_status": "warning",
            "summary": {
                "phases_compared": 4,
                "phases_with_count_deltas": 0,
                "phases_with_warning_deltas": 0,
                "phases_with_error_deltas": 0,
                "phases_with_warning_status": 4,
            },
            "errors": [],
            "warnings": ["comparison warning"],
        },
    }
    for phase, filename in PHASE_ARTIFACTS.items():
        (tmp_path / filename).write_text(json.dumps(diagnostics[phase], indent=2), encoding="utf-8")
    return tmp_path


def _mutate_artifact(path: Path, mutator) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
