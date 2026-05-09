import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.affix_stat_modifier_reference_audit import (
    AffixStatModifierReferenceAuditError,
    affix_stat_modifier_reference_audit_to_json,
    audit_affix_stat_modifier_references,
    build_affix_stat_modifier_reference_audit,
    render_affix_stat_modifier_reference_audit,
    validate_affix_stat_modifier_reference_audit_output_path,
)
from app.game_data.controlled_affix_per_affix_diagnostic import (
    build_per_affix_diagnostic_artifact,
    per_affix_diagnostic_artifact_to_json,
)
from tests.test_controlled_affix_resolver_prototype import _mutate_artifact, _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_affix_stat_modifier_reference_audit"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_resolved_and_unresolved_modifier_references_are_reported(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)

    report = audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert report["production_safe"] is False
    assert report["diagnostic_only"] is True
    assert report["validation_status"] == "warning"
    assert report["summary"]["total_affix_stat_modifier_references"] == 12
    assert report["summary"]["unresolved_references"] == 1
    assert report["summary"]["resolved_references"] == 11
    assert report["summary"]["malformed_modifier_structures"] == 1
    assert report["summary"]["unsupported_modifier_structures"] == 1
    assert report["summary"]["deterministic_inspection_output_stable"] is True
    assert any(finding["code"] == "unresolved_stat_modifier_references" for finding in report["findings"])

    parsed = json.loads(affix_stat_modifier_reference_audit_to_json(report))
    assert parsed["production_safe"] is False
    rendered = render_affix_stat_modifier_reference_audit(report)
    assert "# Affix Stat/Modifier Reference Audit" in rendered
    assert "production_safe: false" in rendered


def test_duplicate_modifier_references_are_reported(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data["summary"].update({"duplicate_stat_modifier_references": 2}),
    )

    report = audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert report["summary"]["duplicate_references"] == 2
    assert any(finding["code"] == "duplicate_stat_modifier_references" for finding in report["findings"])


def test_ambiguous_modifier_references_are_reported(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data["summary"].update({"ambiguous_stat_modifier_references": 3}),
    )

    report = audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert report["summary"]["ambiguous_references"] == 3
    assert any(finding["code"] == "ambiguous_stat_modifier_references" for finding in report["findings"])


def test_malformed_modifier_structures_are_warning_only(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)

    report = audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert report["summary"]["malformed_modifier_structures"] == 1
    assert any(finding["code"] == "malformed_modifier_structures" for finding in report["findings"])
    assert report["errors"] == []


def test_unsafe_identity_assumptions_fail(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_2_identity_provenance"],
        lambda data: data["summary"].update({"affixes_relying_on_name_only_identity": 1}),
    )

    with pytest.raises(AffixStatModifierReferenceAuditError) as exc:
        audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert exc.value.report["validation_status"] == "error"
    assert any(finding["code"] == "unsafe_identity_assumptions" for finding in exc.value.report["findings"])


def test_production_safe_true_fails(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(AffixStatModifierReferenceAuditError) as exc:
        audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert any(finding["code"] == "production_safe_violation" for finding in exc.value.report["findings"])


def test_missing_provenance_is_reported(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    data = json.loads(per_affix_path.read_text(encoding="utf-8"))
    data["records"][0]["provenance"]["source_artifacts"] = []
    per_affix_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    report = audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    assert report["summary"]["missing_provenance_source_references"] == 1
    assert any(finding["code"] == "missing_provenance_source_references" for finding in report["findings"])


def test_audit_output_is_deterministic(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)

    first = affix_stat_modifier_reference_audit_to_json(
        audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)
    )
    second = affix_stat_modifier_reference_audit_to_json(
        audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)
    )

    assert first == second


def test_audit_does_not_mutate_source_artifacts(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    paths = list(diagnostics_dir.iterdir()) + [per_affix_path]
    before = {path: path.read_text(encoding="utf-8") for path in paths}

    audit_affix_stat_modifier_references(diagnostics_dir, per_affix_path)

    after = {path: path.read_text(encoding="utf-8") for path in paths}
    assert after == before


def test_missing_per_affix_artifact_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    with pytest.raises(FileNotFoundError):
        audit_affix_stat_modifier_references(diagnostics_dir, scratch_dir / "missing.json")


def test_build_report_requires_all_phases(scratch_dir):
    diagnostics_dir, per_affix_path = _write_inputs(scratch_dir)
    artifacts = {
        phase: json.loads((diagnostics_dir / filename).read_text(encoding="utf-8"))
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    artifacts.pop("phase_5_saved_vs_fresh")
    per_affix = json.loads(per_affix_path.read_text(encoding="utf-8"))

    with pytest.raises(ValueError):
        build_affix_stat_modifier_reference_audit(
            artifacts,
            per_affix,
            diagnostics_dir=diagnostics_dir,
            per_affix_artifact_path=per_affix_path,
        )


def test_output_path_guard_refuses_production_data_directories():
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError):
        validate_affix_stat_modifier_reference_audit_output_path(
            repo_root / "data" / "items" / "stat_modifier_audit.md"
        )


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    diagnostics_dir = _write_diagnostics(tmp_path)
    per_affix = build_per_affix_diagnostic_artifact(diagnostics_dir)
    per_affix_path = tmp_path / "controlled_affix_per_affix_diagnostic_records.json"
    per_affix_path.write_text(per_affix_diagnostic_artifact_to_json(per_affix), encoding="utf-8")
    return diagnostics_dir, per_affix_path
