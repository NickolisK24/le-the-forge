"""Developer-only Phase 6 affix diagnostic consumer.

This module reads generated diagnostic artifacts only. It does not read source
affix exports, bundle data, production loaders, importers, routes, frontend
code, or simulation code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DIAGNOSTICS_DIR = REPO_ROOT.parent / "last-epoch-data" / "docs" / "generated"

PHASE_ARTIFACTS = {
    "phase_1_source_shape": "affix_source_shape_diagnostic_report.json",
    "phase_2_identity_provenance": "affix_identity_provenance_diagnostic_report.json",
    "phase_3_eligibility": "affix_eligibility_diagnostic_report.json",
    "phase_4_tag_category": "affix_tag_category_diagnostic_report.json",
    "phase_5_saved_vs_fresh": "affix_saved_vs_fresh_diagnostic_comparison_report.json",
}

FORBIDDEN_PRODUCTION_USAGE = [
    "Do not use this report to power build math.",
    "Do not use this report for item generation.",
    "Do not use this report for crafting legality.",
    "Do not expose this report through production APIs or frontend behavior.",
    "Do not replace existing Forge affix behavior.",
    "Do not generate or mutate bundle families from this report.",
    "Do not silently deduplicate affix 910.",
    "Do not mark production_safe=true.",
]

OUTPUT_FORBIDDEN_SEGMENTS = (
    ("data", "items"),
    ("exports_json",),
    ("data_bundle",),
)


class AffixDiagnosticConsumerError(RuntimeError):
    """Raised when affix diagnostic artifacts cannot be consumed safely."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def consume_affix_diagnostics(diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR) -> dict[str, Any]:
    """Read generated Phase 1-5 affix diagnostics and build an inspection report."""

    base = Path(diagnostics_dir)
    artifacts = {
        phase: _load_artifact(base / filename)
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    report = build_affix_diagnostic_report(artifacts, diagnostics_dir=base)
    _raise_if_unsafe(report)
    return report


def build_affix_diagnostic_report(
    artifacts: dict[str, dict[str, Any]],
    *,
    diagnostics_dir: str | Path,
) -> dict[str, Any]:
    """Build a serializable Phase 6 report from already loaded diagnostics."""

    phase1 = artifacts["phase_1_source_shape"]
    phase2 = artifacts["phase_2_identity_provenance"]
    phase3 = artifacts["phase_3_eligibility"]
    phase4 = artifacts["phase_4_tag_category"]
    phase5 = artifacts["phase_5_saved_vs_fresh"]

    phase_reports = {
        phase: _phase_status(phase, PHASE_ARTIFACTS[phase], data)
        for phase, data in artifacts.items()
    }
    warning_categories = _remaining_warning_categories(phase1, phase2, phase3, phase4, phase5)
    affix_910 = _find_affix_910_duplicate_evidence(phase3)
    summary = {
        "total_affixes": _summary_value(phase1, "total_affixes"),
        "equipment_affixes": _summary_value(phase1, "equipment_affixes"),
        "idol_affixes": _summary_value(phase1, "idol_affixes"),
        "total_embedded_tiers": _summary_value(phase1, "total_embedded_tiers"),
        "phase5_migration_gate_status": phase5.get("migration_gate_status"),
        "remaining_warning_categories": len(warning_categories),
        "affix_910_duplicate_evidence_present": bool(affix_910),
        "tag_category_warnings_present": bool(
            _summary_value(phase4, "unknown_or_unsupported_tag_category_values")
            or _summary_value(phase4, "ambiguous_tag_category_mappings")
            or (phase4.get("warnings") or [])
        ),
    }
    errors = _safety_errors(phase_reports, phase3, phase4, phase5, affix_910)
    return {
        "diagnostic": "phase_6_affix_diagnostic_consumer",
        "production_safe": False,
        "consumer_scope": "non_production_read_only",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "input_artifacts": phase_reports,
        "phase_validation_statuses": {
            phase: info["validation_status"] for phase, info in phase_reports.items()
        },
        "phase5_migration_gate_status": phase5.get("migration_gate_status"),
        "summary": summary,
        "remaining_warning_categories": warning_categories,
        "affix_910_duplicate_eligibility_evidence": affix_910,
        "tag_category_warning_state": _tag_category_warning_state(phase4, phase3),
        "non_production_inspection_allowed": not errors,
        "errors": errors,
        "warnings": _report_warnings(phase_reports, warning_categories),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE),
        "recommendations": _recommendations(errors),
    }


def render_affix_diagnostic_report(report: dict[str, Any]) -> str:
    """Render a human-readable markdown report."""

    lines = [
        "# Phase 6 Affix Diagnostic Consumer Report",
        "",
        "- diagnostic: phase_6_affix_diagnostic_consumer",
        "- consumer_scope: non_production_read_only",
        "- production_safe: false",
        f"- non_production_inspection_allowed: {str(report['non_production_inspection_allowed']).lower()}",
        f"- phase5_migration_gate_status: {report['phase5_migration_gate_status']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Phase Statuses", ""])
    for phase, info in report["input_artifacts"].items():
        lines.append(
            f"- {phase}: validation_status={info['validation_status']} "
            f"migration_gate_status={info.get('migration_gate_status') or 'n/a'} "
            f"production_safe={str(info['production_safe']).lower()} "
            f"errors={info['error_count']} warnings={info['warning_count']}"
        )

    lines.extend(["", "## Remaining Warning Categories", ""])
    lines.extend(_format_bullets(report["remaining_warning_categories"]))

    lines.extend(["", "## Affix 910 Duplicate Eligibility Evidence", ""])
    evidence = report["affix_910_duplicate_eligibility_evidence"]
    if evidence:
        for key, value in evidence.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- missing")

    lines.extend(["", "## Tag/Category Warning State", ""])
    for key, value in report["tag_category_warning_state"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Errors", ""])
    lines.extend(_format_bullets(report["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_bullets(report["warnings"]))
    lines.extend(["", "## Forbidden Production Usage", ""])
    lines.extend(_format_bullets(report["forbidden_production_usage"]))
    lines.extend(["", "## Recommendations", ""])
    lines.extend(_format_bullets(report["recommendations"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This report consumes generated diagnostic artifacts only.",
            "- It is read-only, non-production, and inspection-only.",
            "- It does not consume production bundle data.",
            "- It does not modify importers, loaders, generated output, APIs, frontend behavior, runtime behavior, crafting, or simulation.",
            "- It does not silently deduplicate affix 910.",
            "- It does not claim production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def affix_diagnostic_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_affix_diagnostic_output_path(path: Path) -> None:
    """Refuse writes into production/generated data directories."""

    resolved = path.resolve()
    roots = [REPO_ROOT.resolve(), REPO_ROOT.parent.resolve()]
    for root in roots:
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        parts = tuple(part.lower() for part in relative.parts)
        for segment in OUTPUT_FORBIDDEN_SEGMENTS:
            if _contains_segment(parts, segment):
                raise ValueError(f"Refusing to write affix diagnostic consumer report into data path: {path}")


def _load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing affix diagnostic artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Affix diagnostic artifact must be a JSON object: {path}")
    return data


def _phase_status(phase: str, filename: str, data: dict[str, Any]) -> dict[str, Any]:
    validation_status = data.get("validation_status") or data.get("migration_gate_status")
    return {
        "phase": phase,
        "filename": filename,
        "diagnostic": data.get("diagnostic"),
        "validation_status": validation_status,
        "migration_gate_status": data.get("migration_gate_status"),
        "production_safe": data.get("production_safe"),
        "error_count": len(data.get("errors") or []),
        "warning_count": len(data.get("warnings") or []),
    }


def _summary_value(data: dict[str, Any], key: str) -> Any:
    summary = data.get("summary") or {}
    return summary.get(key, 0)


def _remaining_warning_categories(
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        ("phase_1_source_shape", "ambiguous_name_collisions", _summary_value(phase1, "ambiguous_name_collisions")),
        ("phase_1_source_shape", "malformed_tier_ranges", _summary_value(phase1, "malformed_tier_ranges")),
        ("phase_1_source_shape", "missing_stat_modifier_references", _summary_value(phase1, "missing_stat_modifier_references")),
        ("phase_1_source_shape", "unsupported_or_unresolved_fields", _summary_value(phase1, "unsupported_or_unresolved_fields")),
        ("phase_2_identity_provenance", "ambiguous_display_name_collisions", _summary_value(phase2, "ambiguous_display_name_collisions")),
        ("phase_3_eligibility", "duplicate_or_ambiguous_eligibility_records", _summary_value(phase3, "duplicate_or_ambiguous_eligibility_records")),
        ("phase_3_eligibility", "unsupported_or_unresolved_eligibility_fields", _summary_value(phase3, "unsupported_or_unresolved_eligibility_fields")),
        ("phase_4_tag_category", "unknown_or_unsupported_tag_category_values", _summary_value(phase4, "unknown_or_unsupported_tag_category_values")),
        ("phase_4_tag_category", "ambiguous_tag_category_mappings", _summary_value(phase4, "ambiguous_tag_category_mappings")),
        ("phase_5_saved_vs_fresh", "phases_with_warning_status", _summary_value(phase5, "phases_with_warning_status")),
    ]
    return [
        {"phase": phase, "category": category, "count": count}
        for phase, category, count in candidates
        if count
    ]


def _find_affix_910_duplicate_evidence(phase3: dict[str, Any]) -> dict[str, Any] | None:
    for warning in phase3.get("warnings") or []:
        if not isinstance(warning, dict):
            continue
        details = warning.get("details") or {}
        if (
            warning.get("record_id") == 910
            and warning.get("code") == "affix_eligibility.duplicate_target"
            and details.get("policy_result") == "warning_only"
        ):
            return {
                "record_id": warning.get("record_id"),
                "section": warning.get("section"),
                "record_path": warning.get("record_path") or details.get("record_path"),
                "raw_canRollOn": details.get("raw_canRollOn"),
                "normalized_canRollOn": details.get("normalized_canRollOn"),
                "raw_duplicate_count": details.get("raw_duplicate_count"),
                "duplicate_positions": details.get("duplicate_positions"),
                "diagnostic_unique_targets": details.get("diagnostic_unique_targets"),
                "diagnostic_unique_targets_label": details.get("diagnostic_unique_targets_label"),
                "policy_result": details.get("policy_result"),
                "origin_assessment": details.get("origin_assessment"),
                "message": warning.get("message"),
            }
    return None


def _tag_category_warning_state(phase4: dict[str, Any], phase3: dict[str, Any]) -> dict[str, Any]:
    return {
        "validation_status": phase4.get("validation_status"),
        "warning_count": len(phase4.get("warnings") or []),
        "unknown_or_unsupported_tag_category_values": _summary_value(phase4, "unknown_or_unsupported_tag_category_values"),
        "ambiguous_tag_category_mappings": _summary_value(phase4, "ambiguous_tag_category_mappings"),
        "duplicate_tag_category_records": _summary_value(phase4, "duplicate_tag_category_records"),
        "name_only_tag_category_records": _summary_value(phase4, "tag_category_records_using_name_only_matching"),
        "subtype_id_only_tag_category_records": _summary_value(phase4, "tag_category_records_using_subtype_id_only_identity"),
        "phase3_eligibility_status_from_phase3_report": phase3.get("validation_status"),
        "phase3_relationship_note": "Phase 4 remains a separate tag/category gate and does not resolve eligibility.",
    }


def _safety_errors(
    phase_reports: dict[str, dict[str, Any]],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    affix_910: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    for phase, info in phase_reports.items():
        if info["production_safe"] is not False:
            errors.append(f"{phase} reports production_safe={info['production_safe']}; expected false.")
        if phase != "phase_5_saved_vs_fresh" and info["validation_status"] == "error":
            errors.append(f"{phase} reports validation_status=error.")
        if info["error_count"]:
            errors.append(f"{phase} contains {info['error_count']} diagnostic errors.")
    if phase5.get("migration_gate_status") == "blocked":
        errors.append("phase_5_saved_vs_fresh reports migration_gate_status=blocked.")
    phase5_summary = phase5.get("summary") or {}
    for key in ("phases_with_count_deltas", "phases_with_warning_deltas", "phases_with_error_deltas"):
        if phase5_summary.get(key, 0) != 0:
            errors.append(f"phase_5_saved_vs_fresh summary {key}={phase5_summary.get(key)}; expected 0.")
    if _summary_value(phase3, "eligibility_records_using_name_only_matching"):
        errors.append("phase_3_eligibility reports name-only eligibility matching.")
    if _summary_value(phase3, "eligibility_records_using_subtype_id_only_identity"):
        errors.append("phase_3_eligibility reports subtype_id-only eligibility identity.")
    if _summary_value(phase4, "tag_category_records_using_name_only_matching"):
        errors.append("phase_4_tag_category reports name-only tag/category matching.")
    if _summary_value(phase4, "tag_category_records_using_subtype_id_only_identity"):
        errors.append("phase_4_tag_category reports subtype_id-only tag/category identity.")
    if not affix_910:
        errors.append("Phase 3 affix 910 warning-only duplicate evidence is missing.")
    return errors


def _report_warnings(
    phase_reports: dict[str, dict[str, Any]],
    warning_categories: list[dict[str, Any]],
) -> list[str]:
    warnings: list[str] = []
    for phase, info in phase_reports.items():
        if info["warning_count"]:
            warnings.append(f"{phase} contains {info['warning_count']} diagnostic warnings.")
        if info["validation_status"] == "warning" or info["migration_gate_status"] == "warning":
            warnings.append(f"{phase} remains warning-level and non-production.")
    if warning_categories:
        warnings.append("Warning categories remain visible; do not treat this consumer as production readiness.")
    return warnings


def _recommendations(errors: list[str]) -> list[str]:
    if errors:
        return [
            "Do not run a non-production affix consumer until blocking diagnostic errors are resolved.",
            "Keep production_safe=false and preserve all warning/error metadata.",
        ]
    return [
        "Phase 6 inspection may remain read-only and non-production.",
        "Keep this consumer limited to generated diagnostic artifacts.",
        "Do not generate affix bundle families or production Forge consumers from this report.",
        "Preserve affix 910 raw duplicate evidence in all downstream diagnostics.",
    ]


def _raise_if_unsafe(report: dict[str, Any]) -> None:
    if report.get("errors"):
        raise AffixDiagnosticConsumerError(
            "Affix diagnostic artifacts are not safe for Phase 6 inspection.",
            report=report,
        )


def _format_bullets(items: list[Any]) -> list[str]:
    if not items:
        return ["- none"]
    lines = []
    for item in items:
        if isinstance(item, dict):
            rendered = ", ".join(f"{key}={value}" for key, value in item.items())
            lines.append(f"- {rendered}")
        else:
            lines.append(f"- {item}")
    return lines


def _contains_segment(parts: tuple[str, ...], segment: tuple[str, ...]) -> bool:
    if len(parts) < len(segment):
        return False
    return any(parts[index : index + len(segment)] == segment for index in range(len(parts) - len(segment) + 1))
