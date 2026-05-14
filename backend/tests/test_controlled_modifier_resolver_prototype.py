import json
import shutil
import uuid
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.controlled_modifier_resolver_prototype import (
    ControlledModifierResolverError,
    controlled_modifier_resolver_report_to_json,
    render_controlled_modifier_resolver_report,
    resolve_modifier_diagnostics,
    validate_controlled_modifier_resolver_output_path,
)
from tests.test_controlled_affix_resolver_prototype import _mutate_artifact, _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_controlled_modifier_resolver"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_structurally_safe_modifier_resolution(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))

    assert report["diagnostic_only"] is True
    assert report["production_safe"] is False
    assert report["non_production_inspection_allowed"] is True
    assert report["summary"]["total_modifier_references"] == 12
    assert report["summary"]["resolved_modifier_objects"] == 9
    assert report["summary"]["unresolved_modifier_objects"] == 1
    assert report["summary"]["malformed_modifier_objects"] == 1
    assert report["summary"]["unsupported_modifier_objects"] == 1
    assert report["summary"]["deterministic_output_status"] == "stable"
    assert report["affix_910_duplicate_evidence"]["raw_duplicate_count"] == 2

    resolved = _find_object(report, "resolved")
    assert resolved["reference_count"] == 9
    assert resolved["normalized_inspection_structure"]["resolution"] == "inspection_safe_structural_reference"
    assert resolved["normalized_inspection_structure"]["gameplay_semantics"] is None
    assert resolved["source_provenance_path"] == "phase_1_source_shape.summary.total_embedded_tiers"
    assert resolved["diagnostic_only"] is True
    assert resolved["production_safe"] is False

    rendered = render_controlled_modifier_resolver_report(report)
    assert "# Controlled Modifier Resolver Prototype Report" in rendered
    assert "does not guess unsupported modifier semantics" in rendered


def test_unresolved_modifier_references_are_propagated(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))

    unresolved = _find_object(report, "unresolved")
    assert unresolved["reference_count"] == 1
    assert unresolved["normalized_inspection_structure"] is None
    assert unresolved["warnings"][0]["category"] == "missing_stat_modifier_references"
    assert "excluded from resolved modifier semantics" in " ".join(unresolved["notes"])


def test_malformed_modifier_references_are_propagated(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))

    malformed = _find_object(report, "malformed")
    assert malformed["reference_count"] == 1
    assert malformed["normalized_inspection_structure"] is None
    assert malformed["warnings"][0]["category"] == "malformed_tier_ranges"


def test_unsupported_modifier_references_are_propagated(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))

    unsupported = _find_object(report, "unsupported")
    assert unsupported["reference_count"] == 1
    assert unsupported["normalized_inspection_structure"] is None
    assert unsupported["warnings"][0]["category"] == "unsupported_or_unresolved_fields"


def test_modifier_resolver_output_is_deterministic(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)

    first = controlled_modifier_resolver_report_to_json(resolve_modifier_diagnostics(diagnostics_dir))
    second = controlled_modifier_resolver_report_to_json(resolve_modifier_diagnostics(diagnostics_dir))

    assert first == second


def test_modifier_resolver_preserves_warning_metadata_and_provenance(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))

    assert report["warning_category_summary"]
    for record in report["modifier_objects"]:
        assert record["source_affix_identity"] == "aggregate:multiple_affixes"
        assert record["source_affix_identity_scope"] == "aggregate_generated_diagnostic_counts"
        assert record["source_provenance_path"]
        assert record["duplicate_raw_evidence_refs"] == ["affix_910_duplicate_evidence"]


def test_modifier_resolver_does_not_mutate_source_artifacts(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    before = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}

    resolve_modifier_diagnostics(diagnostics_dir)

    after = {path.name: path.read_text(encoding="utf-8") for path in diagnostics_dir.iterdir()}
    assert after == before


def test_production_safe_true_violation_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"],
        lambda data: data.update({"production_safe": True}),
    )

    with pytest.raises(ControlledModifierResolverError) as exc:
        resolve_modifier_diagnostics(diagnostics_dir)

    assert "phase_1_source_shape reports production_safe=True" in " ".join(exc.value.report["errors"])


def test_name_only_identity_rejected(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_2_identity_provenance"],
        lambda data: data["summary"].update({"affixes_relying_on_name_only_identity": 1}),
    )

    with pytest.raises(ControlledModifierResolverError):
        resolve_modifier_diagnostics(diagnostics_dir)


def test_subtype_id_only_identity_rejected(scratch_dir):
    diagnostics_dir = _write_diagnostics(scratch_dir)
    _mutate_artifact(
        diagnostics_dir / PHASE_ARTIFACTS["phase_3_eligibility"],
        lambda data: data["summary"].update({"eligibility_records_using_subtype_id_only_identity": 1}),
    )

    with pytest.raises(ControlledModifierResolverError):
        resolve_modifier_diagnostics(diagnostics_dir)


def test_output_path_guard_refuses_production_data_directories():
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError):
        validate_controlled_modifier_resolver_output_path(repo_root / "data" / "items" / "modifier_resolver.md")

    with pytest.raises(ValueError):
        validate_controlled_modifier_resolver_output_path(
            repo_root.parent / "last-epoch-data" / "data_bundle" / "modifier_resolver.md"
        )


def test_json_shape_has_stable_keys(scratch_dir):
    report = resolve_modifier_diagnostics(_write_diagnostics(scratch_dir))
    parsed = json.loads(controlled_modifier_resolver_report_to_json(report))

    assert {
        "resolver",
        "diagnostic_only",
        "production_safe",
        "summary",
        "modifier_objects",
        "errors",
        "warnings",
    }.issubset(parsed)


def _find_object(report, state):
    for record in report["modifier_objects"]:
        if record["state"] == state:
            return record
    raise AssertionError(f"Missing modifier object state {state}")
