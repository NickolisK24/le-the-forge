from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_import_context_sidecar_validator import load_sidecar
from app.game_data.le_tools_sidecar_diagnostic_consumer import (
    SidecarDiagnosticConsumerError,
    consume_sidecar_diagnostic,
    consumer_report_to_json,
    render_consumer_report,
)


SAVED_SIDECAR_FIXTURE = (
    Path(__file__).parent / "fixtures" / "le_tools_import_context_sidecar_current.json"
)


def test_valid_saved_sidecar_produces_warning_labeled_report():
    report = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)

    assert report["production_safe"] is False
    assert report["validation_status"] == "warning"
    assert report["errors"] == []
    assert report["summary"] == {
        "total_items": 12,
        "resolved": 8,
        "needs_context": 2,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 1,
    }
    assert len(report["records"]) == 12
    assert len(report["resolved_records"]) == 8
    assert len(report["blocked_records"]) == 4
    assert all(record["production_safe"] is False for record in report["records"])
    assert any(record["bundle_item_type_id"] == "helmet" for record in report["resolved_records"])


def test_report_shape_has_stable_top_level_keys():
    report = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)

    assert {
        "production_safe",
        "sidecar_path",
        "validation_status",
        "errors",
        "warnings",
        "summary",
        "records",
        "blocked_records",
        "resolved_records",
        "records_requiring_base_type_id",
        "manual_review_records",
        "unresolved_records",
        "subtype_only_blocked_records",
        "name_only_blocked_records",
        "recommendations",
    }.issubset(report)

    parsed = json.loads(consumer_report_to_json(report))
    assert parsed["production_safe"] is False
    assert parsed["validation_status"] == "warning"


def test_rendered_report_includes_required_sections():
    content = render_consumer_report(consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE))

    assert "# LE Tools Sidecar Diagnostic Consumer Report" in content
    assert "validation_status: warning" in content
    assert "## Resolved Records" in content
    assert "## Blocked Records" in content
    assert "records_requiring_base_type_id: 2" in content
    assert "production_safe remains false" in content


def test_validation_errors_block_consumer():
    sidecar = load_sidecar(SAVED_SIDECAR_FIXTURE)
    sidecar["production_safe"] = True
    path = SAVED_SIDECAR_FIXTURE.with_name("_tmp_unsafe_sidecar.json")
    try:
        path.write_text(json.dumps(sidecar), encoding="utf-8")

        with pytest.raises(SidecarDiagnosticConsumerError) as exc:
            consume_sidecar_diagnostic(path)

        assert exc.value.validation_result is not None
        assert exc.value.validation_result["status"] == "failed"
    finally:
        path.unlink(missing_ok=True)


def test_missing_sidecar_path_fails():
    with pytest.raises(FileNotFoundError):
        consume_sidecar_diagnostic(Path("missing-sidecar.json"))


def test_report_includes_blocked_record_categories():
    report = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)

    assert len(report["records_requiring_base_type_id"]) == 2
    assert len(report["manual_review_records"]) == 1
    assert len(report["unresolved_records"]) == 1
    assert len(report["subtype_only_blocked_records"]) == 1
    assert len(report["name_only_blocked_records"]) == 1
    assert any(record["raw_item_type"] == "spear" for record in report["manual_review_records"])


def test_consumer_does_not_mutate_sidecar_input():
    before = SAVED_SIDECAR_FIXTURE.read_text(encoding="utf-8")
    original = load_sidecar(SAVED_SIDECAR_FIXTURE)

    consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)

    after = SAVED_SIDECAR_FIXTURE.read_text(encoding="utf-8")
    assert after == before
    assert load_sidecar(SAVED_SIDECAR_FIXTURE) == original


def test_no_production_importer_is_called(monkeypatch):
    from app.routes import import_route

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("production importer mapping should not be called")

    monkeypatch.setattr(import_route, "_map_let_build", fail_if_called)

    report = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)

    assert report["summary"]["resolved"] == 8


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "consumer.md")


def test_mutated_in_memory_copy_can_be_written_and_blocked():
    sidecar = deepcopy(load_sidecar(SAVED_SIDECAR_FIXTURE))
    sidecar["items"][10]["resolver"]["status"] = "resolved"
    sidecar["items"][10]["resolver"]["bundle_item_type_id"] = "two_handed_spear"
    sidecar["summary"]["needs_review"] -= 1
    sidecar["summary"]["resolved"] += 1
    path = SAVED_SIDECAR_FIXTURE.with_name("_tmp_resolved_spear_sidecar.json")
    try:
        path.write_text(json.dumps(sidecar), encoding="utf-8")

        with pytest.raises(SidecarDiagnosticConsumerError):
            consume_sidecar_diagnostic(path)
    finally:
        path.unlink(missing_ok=True)
