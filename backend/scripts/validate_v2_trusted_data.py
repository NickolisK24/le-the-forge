"""Validate the v2 trusted-data checkpoint state for local and CI runs."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REQUIRED_GENERATED_REPORTS = [
    "v2_affix_bundle.json",
    "v2_affix_validation_report.json",
    "v2_api_contract_report.json",
    "v2_backend_repository_report.json",
    "v2_canonical_contract_report.json",
    "v2_class_mastery_bundle.json",
    "v2_class_mastery_validation_report.json",
    "v2_idol_affix_bundle.json",
    "v2_idol_bundle.json",
    "v2_idol_validation_report.json",
    "v2_item_base_bundle.json",
    "v2_item_implicit_bundle.json",
    "v2_item_validation_report.json",
    "v2_modifier_blocked_reasons_report.json",
    "v2_modifier_registry.json",
    "v2_modifier_validation_report.json",
    "v2_planner_adapter_report.json",
    "v2_passive_tree_bundle.json",
    "v2_passive_tree_validation_report.json",
    "v2_passive_unsupported_report.json",
    "v2_set_bundle.json",
    "v2_skill_bundle.json",
    "v2_skill_identity_alignment_report.json",
    "v2_skill_tree_bundle.json",
    "v2_skill_unsupported_report.json",
    "v2_skill_validation_report.json",
    "v2_source_inventory.json",
    "v2_stat_registry.json",
    "v2_unique_bundle.json",
    "v2_unique_set_unsupported_report.json",
    "v2_unique_set_validation_report.json",
    "v2_value_normalization_candidate_families.json",
    "v2_value_normalization_policy_report.json",
]


BACKEND_VALIDATION_COMMANDS = [
    r".\backend\.venv\Scripts\python.exe -m pytest backend\tests\test_v2_* -q",
    r".\backend\.venv\Scripts\python.exe -m pytest backend\tests\test_forge_safe_production_non_consumption.py -q",
    r".\backend\.venv\Scripts\python.exe backend\scripts\report_v2_backend_repository_layer.py",
    r".\backend\.venv\Scripts\python.exe backend\scripts\report_v2_api_contract.py",
    "python -m json.tool docs\\generated\\v2_backend_repository_report.json",
    "python -m json.tool docs\\generated\\v2_api_contract_report.json",
]


FRONTEND_VALIDATION_COMMANDS = [
    "npm --prefix frontend run type-check",
    "npm --prefix frontend test -- v2-api-envelope.test.ts v2-items-debug-page.test.tsx v2-idols-debug-page.test.tsx v2-unique-set-debug-page.test.tsx v2-class-mastery-debug-page.test.tsx v2-passives-debug-page.test.tsx v2-skills-debug-page.test.tsx forge-safe-affixes-debug-page.test.tsx --run",
]


KNOWN_CAVEATS = [
    {
        "id": "frontend_full_suite_navigation_layout_search_assertions",
        "status": "known_unrelated_failure",
        "notes": [
            "The full frontend test suite currently has unrelated navigation/layout search assertion failures.",
            "Focused v2 envelope and debug page tests are the frontend-owned validation target for this checkpoint.",
        ],
    }
]


def build_validation_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    generated_dir = repo_root / "docs" / "generated"
    json_results = _validate_required_json_reports(generated_dir)

    modifier_validation = _load_json(generated_dir / "v2_modifier_validation_report.json")
    value_policy = _load_json(generated_dir / "v2_value_normalization_policy_report.json")
    skill_identity = _load_json(generated_dir / "v2_skill_identity_alignment_report.json")
    backend_repository = _load_json(generated_dir / "v2_backend_repository_report.json")
    api_contract = _load_json(generated_dir / "v2_api_contract_report.json")

    stable_calculable_count = _nested_int(modifier_validation, ["summary", "stable_calculable_count"])
    value_policy_summary = value_policy.get("summary", {}) if isinstance(value_policy, dict) else {}
    safe_normalization_families = value_policy.get("safe_normalization_families", []) if isinstance(value_policy, dict) else []
    skill_summary = skill_identity.get("summary", {}) if isinstance(skill_identity, dict) else {}
    repository_summary = backend_repository.get("summary", {}) if isinstance(backend_repository, dict) else {}
    api_summary = api_contract.get("summary", {}) if isinstance(api_contract, dict) else {}

    production_consumed = any(
        bool(_nested_value(report, ["metadata", "production_consumed"]))
        or bool(_nested_value(report, ["summary", "production_consumed"]))
        for report in [modifier_validation, backend_repository, api_contract]
        if isinstance(report, dict)
    )

    safety = {
        "production_consumed": production_consumed,
        "stable_calculable_count": stable_calculable_count,
        "stable_calculable_status": "intentionally_blocked" if stable_calculable_count == 0 else "changed",
        "value_normalization_policy_status": (
            "audit_only"
            if value_policy_summary.get("safe_normalization_family_count", len(safe_normalization_families)) == 0
            and value_policy_summary.get("stable_calculable_count_changed") is False
            else "changed"
        ),
        "safe_normalization_family_count": value_policy_summary.get(
            "safe_normalization_family_count", len(safe_normalization_families)
        ),
        "skill_identity_bridge_status": (
            "unbridged"
            if skill_summary.get("bridge_safe") is False or skill_summary.get("deterministic_bridge_safe") is False
            else "review_required"
        ),
        "unresolved_skill_reference_count": skill_summary.get("unresolved_reference_count")
        or skill_summary.get("unresolved_references")
        or skill_summary.get("unresolved_count"),
        "ambiguous_skill_reference_count": skill_summary.get("ambiguous_match_count")
        or skill_summary.get("ambiguous_matches")
        or skill_summary.get("ambiguous_count"),
    }

    error_count = (
        json_results["missing_count"]
        + json_results["invalid_count"]
        + (1 if safety["production_consumed"] else 0)
        + (1 if safety["stable_calculable_count"] != 0 else 0)
        + (1 if safety["value_normalization_policy_status"] != "audit_only" else 0)
        + (1 if safety["skill_identity_bridge_status"] != "unbridged" else 0)
    )

    return {
        "summary": {
            "generated_at": datetime.now(UTC).isoformat(),
            "required_generated_report_count": len(REQUIRED_GENERATED_REPORTS),
            "valid_json_report_count": json_results["valid_count"],
            "missing_generated_report_count": json_results["missing_count"],
            "invalid_json_report_count": json_results["invalid_count"],
            "backend_repository_domain_count": repository_summary.get("repository_domain_count"),
            "api_route_count": api_summary.get("route_count"),
            "production_consumed": production_consumed,
            "stable_calculable_count": stable_calculable_count,
            "value_policy_audit_only": safety["value_normalization_policy_status"] == "audit_only",
            "skill_identity_bridged": safety["skill_identity_bridge_status"] != "unbridged",
            "error_count": error_count,
            "status": "pass" if error_count == 0 else "fail",
        },
        "commands": {
            "backend": BACKEND_VALIDATION_COMMANDS,
            "frontend": FRONTEND_VALIDATION_COMMANDS,
        },
        "backend_checks": {
            "generated_report_json": "covered",
            "repository_report_generation": "command_documented",
            "api_contract_report_generation": "command_documented",
            "v2_repository_tests": "command_documented",
            "v2_api_contract_tests": "command_documented",
            "production_non_consumption_guard": "command_documented",
            "missing_invalid_artifact_errors": "covered_by_v2_repository_tests",
        },
        "frontend_checks": {
            "type_check": "command_documented",
            "v2_api_envelope_tests": "command_documented",
            "v2_debug_page_tests": "command_documented",
            "full_suite": "not_required_for_phase_14_due_known_unrelated_failures",
        },
        "json_reports": json_results,
        "safety": safety,
        "known_caveats": KNOWN_CAVEATS,
        "metadata": {
            "source": "v2_validation_ci_hardening",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "production_consumed": False,
            "planner_consumed": False,
            "value_policy_audit_only": True,
            "unresolved_skill_identity_bridged": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_required_json_reports(generated_dir: Path) -> dict[str, Any]:
    valid_reports: list[str] = []
    missing_reports: list[str] = []
    invalid_reports: list[dict[str, str]] = []

    for name in REQUIRED_GENERATED_REPORTS:
        path = generated_dir / name
        if not path.exists():
            missing_reports.append(name)
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            invalid_reports.append({"path": name, "error": str(exc)})
            continue
        valid_reports.append(name)

    return {
        "valid_count": len(valid_reports),
        "missing_count": len(missing_reports),
        "invalid_count": len(invalid_reports),
        "valid_reports": valid_reports,
        "missing_reports": missing_reports,
        "invalid_reports": invalid_reports,
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _nested_int(data: dict[str, Any], keys: list[str]) -> int:
    value = _nested_value(data, keys)
    return value if isinstance(value, int) else 0


def _nested_value(data: dict[str, Any], keys: list[str]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_validation_ci_report.json")
    args = parser.parse_args()

    report = build_validation_report()
    write_report(report, Path(args.output))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    raise SystemExit(0 if report["summary"]["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
