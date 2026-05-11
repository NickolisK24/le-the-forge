import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.controlled_affix_resolver_prototype import (
    ControlledAffixResolverError,
    build_controlled_affix_resolver_report,
    controlled_affix_resolver_report_to_json,
    render_controlled_affix_resolver_report,
    resolve_affix_diagnostics,
    validate_controlled_affix_resolver_output_path,
)


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_controlled_affix_resolver"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_successful_normalized_inspection_output(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    report = resolve_affix_diagnostics(diagnostics_dir)

    assert report["production_safe"] is False
    assert report["scope"] == "non_production_read_only_cli_report"
    assert report["non_production_inspection_allowed"] is True
    assert report["summary"]["total_normalized_affixes"] == 6
    assert report["summary"]["equipment_affixes"] == 4
    assert report["summary"]["idol_affixes"] == 2
    assert report["summary"]["total_embedded_tiers"] == 12
    assert report["summary"]["affix_910_duplicate_evidence_preserved"] is True
    assert report["phase5_migration_gate_status"] == "warning"
    assert "Do not use this report to power build math." in report["forbidden_production_usage"]

    affix_910 = _find_record(report, "equipment:910")
    assert affix_910["identity"]["stable_source_identity"] is True
    assert affix_910["identity"]["name_only"] is False
    assert affix_910["identity"]["subtype_id_only"] is False
    assert affix_910["display"]["label_role"] == "display_only_not_identity"
    assert affix_910["raw_duplicate_evidence"]["raw_duplicate_count"] == 2
    assert affix_910["diagnostic_normalized_view"]["source_mutation"] is False
    assert affix_910["production_safe"] is False

    parsed = json.loads(controlled_affix_resolver_report_to_json(report))
    assert parsed["production_safe"] is False
    rendered = render_controlled_affix_resolver_report(report)
    assert "# Controlled Affix Resolver Prototype Report" in rendered
    assert "inspection-only" in rendered


def test_missing_diagnostic_artifact_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    (diagnostics_dir / PHASE_ARTIFACTS["phase_4_tag_category"]).unlink()

    with pytest.raises(FileNotFoundError):
        resolve_affix_diagnostics(diagnostics_dir)


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_2_identity_provenance"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(ControlledAffixResolverError) as exc:
        resolve_affix_diagnostics(diagnostics_dir)

    assert "phase_2_identity_provenance reports production_safe=True" in " ".join(exc.value.report["errors"])


def test_affix_910_duplicate_evidence_preserved(scratch_dir):
    report = resolve_affix_diagnostics(_write_diagnostics(scratch_dir))
    evidence = report["affix_910_duplicate_evidence"]

    assert evidence["record_id"] == 910
    assert evidence["record_path"] == "equipment[910].canRollOn"
    assert evidence["raw_canRollOn"] == ["IDOL_4x1", "IDOL_4x1"]
    assert evidence["normalized_canRollOn"] == ["IDOL_4X1", "IDOL_4X1"]
    assert evidence["raw_duplicate_count"] == 2
    assert evidence["duplicate_positions"] == [0, 1]
    assert evidence["diagnostic_unique_targets"] == ["IDOL_4X1"]
    assert evidence["diagnostic_unique_targets_label"] == "diagnostic_only_not_source_mutation"


def test_name_only_identity_rejected(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_2_identity_provenance"],
        lambda data: data["summary"].update({"affixes_relying_on_name_only_identity": 1}),
    )

    with pytest.raises(ControlledAffixResolverError) as exc:
        resolve_affix_diagnostics(diagnostics_dir)

    assert "Name-only identity" in " ".join(exc.value.report["errors"])


def test_subtype_id_only_identity_rejected(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_4_tag_category"],
        lambda data: data["summary"].update({"tag_category_records_using_subtype_id_only_identity": 1}),
    )

    with pytest.raises(ControlledAffixResolverError) as exc:
        resolve_affix_diagnostics(diagnostics_dir)

    assert "subtype_id-only identity" in " ".join(exc.value.report["errors"])


def test_resolver_output_is_deterministic(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    first = controlled_affix_resolver_report_to_json(resolve_affix_diagnostics(diagnostics_dir))
    second = controlled_affix_resolver_report_to_json(resolve_affix_diagnostics(diagnostics_dir))

    assert first == second


def test_resolver_does_not_mutate_source_artifacts(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    before = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}

    resolve_affix_diagnostics(diagnostics_dir)

    after = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}
    assert after == before


def test_build_report_requires_all_phases(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    artifacts = {
        phase: json.loads((diagnostics_dir / filename).read_text(encoding="utf-8"))
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    artifacts.pop("phase_5_saved_vs_fresh")

    with pytest.raises(ValueError):
        build_controlled_affix_resolver_report(artifacts, diagnostics_dir=diagnostics_dir)


def test_output_path_guard_refuses_production_data_directories():
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError):
        validate_controlled_affix_resolver_output_path(repo_root / "data" / "items" / "affix_resolver.md")

    with pytest.raises(ValueError):
        validate_controlled_affix_resolver_output_path(
            repo_root.parent / "last-epoch-data" / "data_bundle" / "affix_resolver.md"
        )


def _find_record(report, resolver_affix_id):
    for record in report["normalized_affixes"]:
        if record["resolver_affix_id"] == resolver_affix_id:
            return record
    raise AssertionError(f"Missing normalized record {resolver_affix_id}")


def _write_diagnostics(tmp_path: Path) -> Path:
    diagnostics = {
        "phase_1_source_shape": {
            "diagnostic": "affix_source_shape_validator",
            "production_safe": False,
            "validation_status": "warning",
            "source_path": "D:\\Forge\\last-epoch-data\\exports_json\\affixes.json",
            "summary": {
                "total_affixes": 6,
                "equipment_affixes": 4,
                "idol_affixes": 2,
                "total_embedded_tiers": 12,
                "missing_required_affix_identity_fields": 0,
                "ambiguous_name_collisions": 1,
                "malformed_tier_ranges": 1,
                "missing_stat_modifier_references": 1,
                "unsupported_or_unresolved_fields": 1,
            },
            "errors": [],
            "warnings": [
                {
                    "code": "affix_record.extra_typetree_fields",
                    "message": "Preserved TypeTree fields are not modeled.",
                    "record_id": 910,
                    "section": "equipment",
                    "severity": "warning",
                }
            ],
        },
        "phase_2_identity_provenance": {
            "diagnostic": "affix_identity_provenance_validator",
            "production_safe": False,
            "validation_status": "warning",
            "source_family_breakdown": {
                "equipment": {
                    "records": 4,
                    "stable_source_identity": 4,
                    "source": "resources.assets (MasterAffixesList, parse_as_dict)",
                    "source_pipeline": "typetree",
                },
                "idol": {
                    "records": 2,
                    "stable_source_identity": 2,
                    "source": "AffixImport.csv (inferred from source section)",
                    "source_pipeline": "typetree",
                },
            },
            "summary": {
                "total_affixes": 6,
                "affixes_missing_source_identity": 0,
                "affixes_relying_on_name_only_identity": 0,
                "affixes_relying_on_subtype_id_only_identity": 0,
                "ambiguous_display_name_collisions": 1,
            },
            "errors": [],
            "warnings": ["identity warning"],
        },
        "phase_3_eligibility": {
            "diagnostic": "affix_eligibility_validator",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "duplicate_or_ambiguous_eligibility_records": 1,
                "unsupported_or_unresolved_eligibility_fields": 2,
                "eligibility_records_using_name_only_matching": 0,
                "eligibility_records_using_subtype_id_only_identity": 0,
            },
            "errors": [],
            "warnings": [
                {
                    "code": "affix_eligibility.idol_context_unresolved",
                    "message": "Idol shape context is not precise.",
                    "record_id": 826,
                    "section": "idol",
                    "severity": "warning",
                },
                {
                    "code": "affix_eligibility.idol_context_unresolved",
                    "message": "Idol shape context is not precise.",
                    "record_id": 827,
                    "section": "idol",
                    "severity": "warning",
                },
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
                        "origin_assessment": "unresolved/unknown before exports_json/affixes.json",
                    },
                },
            ],
        },
        "phase_4_tag_category": {
            "diagnostic": "affix_tag_category_validator",
            "production_safe": False,
            "validation_status": "warning",
            "summary": {
                "unknown_or_unsupported_tag_category_values": 1,
                "ambiguous_tag_category_mappings": 1,
                "duplicate_tag_category_records": 0,
                "tag_category_records_using_name_only_matching": 0,
                "tag_category_records_using_subtype_id_only_identity": 0,
            },
            "errors": [],
            "warnings": ["tag warning"],
        },
        "phase_5_saved_vs_fresh": {
            "diagnostic": "affix_saved_vs_fresh_diagnostic_comparison",
            "production_safe": False,
            "migration_gate_status": "warning",
            "summary": {
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
