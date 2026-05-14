import json
from pathlib import Path

from scripts.validate_v2_trusted_data import (
    FRONTEND_VALIDATION_COMMANDS,
    REQUIRED_GENERATED_REPORTS,
    build_validation_report,
)


def test_v2_validation_report_passes_with_required_json_and_safety_invariants(tmp_path):
    _write_required_reports(tmp_path)

    report = build_validation_report(root=tmp_path)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["missing_generated_report_count"] == 0
    assert report["summary"]["invalid_json_report_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["value_policy_audit_only"] is True
    assert report["summary"]["skill_identity_bridged"] is False
    assert report["summary"]["production_consumed"] is False


def test_v2_validation_report_detects_missing_generated_report(tmp_path):
    _write_required_reports(tmp_path, skip={"v2_affix_bundle.json"})

    report = build_validation_report(root=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["missing_generated_report_count"] == 1
    assert "v2_affix_bundle.json" in report["json_reports"]["missing_reports"]


def test_v2_validation_report_detects_invalid_json(tmp_path):
    _write_required_reports(tmp_path)
    (tmp_path / "docs" / "generated" / "v2_affix_bundle.json").write_text("{", encoding="utf-8")

    report = build_validation_report(root=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["invalid_json_report_count"] == 1
    assert report["json_reports"]["invalid_reports"][0]["path"] == "v2_affix_bundle.json"


def test_v2_validation_report_detects_changed_stable_calculable_count(tmp_path):
    _write_required_reports(tmp_path, stable_calculable_count=1)

    report = build_validation_report(root=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["stable_calculable_count"] == 1
    assert report["safety"]["stable_calculable_status"] == "changed"


def test_v2_validation_report_documents_frontend_caveat_and_focused_commands(tmp_path):
    _write_required_reports(tmp_path)

    report = build_validation_report(root=tmp_path)

    assert "npm --prefix frontend run type-check" in report["commands"]["frontend"]
    assert FRONTEND_VALIDATION_COMMANDS[1] in report["commands"]["frontend"]
    assert report["known_caveats"][0]["status"] == "known_unrelated_failure"
    assert report["frontend_checks"]["full_suite"] == "not_required_for_phase_14_due_known_unrelated_failures"


def _write_required_reports(
    root: Path,
    *,
    skip: set[str] | None = None,
    stable_calculable_count: int = 0,
) -> None:
    skip = skip or set()
    generated_dir = root / "docs" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    for report_name in REQUIRED_GENERATED_REPORTS:
        if report_name in skip:
            continue
        payload = _minimal_payload(report_name, stable_calculable_count=stable_calculable_count)
        (generated_dir / report_name).write_text(json.dumps(payload), encoding="utf-8")


def _minimal_payload(report_name: str, *, stable_calculable_count: int) -> dict:
    if report_name == "v2_modifier_validation_report.json":
        return {
            "summary": {
                "stable_calculable_count": stable_calculable_count,
                "production_consumed": False,
            },
            "metadata": {"production_consumed": False},
        }
    if report_name == "v2_value_normalization_policy_report.json":
        return {
            "summary": {
                "safe_normalization_family_count": 0,
                "stable_calculable_count_changed": False,
            },
            "safe_normalization_families": [],
        }
    if report_name == "v2_skill_identity_alignment_report.json":
        return {
            "summary": {
                "bridge_safe": False,
                "unresolved_reference_count": 2,
                "ambiguous_match_count": 1,
            }
        }
    if report_name == "v2_backend_repository_report.json":
        return {
            "summary": {
                "repository_domain_count": 10,
                "production_consumed": False,
            },
            "metadata": {"production_consumed": False},
        }
    if report_name == "v2_api_contract_report.json":
        return {
            "summary": {
                "route_count": 38,
                "production_consumed": False,
            },
            "metadata": {"production_consumed": False},
        }
    return {}
