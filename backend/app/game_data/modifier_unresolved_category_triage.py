"""Developer-only unresolved modifier category triage.

This module consumes generated diagnostic affix artifacts only. It classifies
unresolved, malformed, and unsupported modifier evidence for future diagnostic
planning. It does not resolve gameplay semantics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import (
    DEFAULT_DIAGNOSTICS_DIR,
    FORBIDDEN_PRODUCTION_USAGE,
    PHASE_ARTIFACTS,
    validate_affix_diagnostic_output_path,
)
from app.game_data.controlled_affix_resolver_prototype import (
    _find_affix_910_duplicate_evidence,
)
from app.game_data.controlled_modifier_resolver_prototype import (
    ControlledModifierResolverError,
    resolve_modifier_diagnostics,
)


DIAGNOSTIC_NAME = "modifier_unresolved_category_triage"

TRIAGE_CODES = {
    "unresolved_references": {
        "warning_code": "affix_record.idol_stat_modifier_reference_unmodeled",
        "likely_issue": "missing_reference_mapping",
        "description": "Idol affix stat/modifier references are present but not modeled by current diagnostic artifacts.",
        "eligible_for_future_diagnostic_policy": True,
        "must_remain_unresolved": True,
    },
    "malformed_structures": {
        "warning_code": "affix_tier.inverted_numeric_range",
        "likely_issue": "malformed_tier_value_shape",
        "description": "Tier min/max ranges are inverted for current semantics and may need signed-value policy.",
        "eligible_for_future_diagnostic_policy": True,
        "must_remain_unresolved": True,
    },
    "unsupported_structures": {
        "warning_code": "affix_record.extra_typetree_fields",
        "likely_issue": "unsupported_special_behavior",
        "description": "Preserved TypeTree fields exist but are not modeled by current diagnostics.",
        "eligible_for_future_diagnostic_policy": True,
        "must_remain_unresolved": True,
    },
}


class ModifierUnresolvedTriageError(RuntimeError):
    """Raised when generated diagnostics are unsafe for modifier triage."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def build_modifier_unresolved_triage(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    """Load generated diagnostics and classify unresolved modifier evidence."""

    base = Path(diagnostics_dir)
    artifacts = {
        phase: _load_json(base / filename)
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    try:
        modifier_report = resolve_modifier_diagnostics(base)
    except ControlledModifierResolverError as exc:
        raise ModifierUnresolvedTriageError(
            "Controlled modifier resolver output is unsafe for unresolved category triage.",
            report=exc.report,
        ) from exc
    report = build_modifier_unresolved_triage_report(
        artifacts,
        modifier_report=modifier_report,
        diagnostics_dir=base,
    )
    if report["errors"]:
        raise ModifierUnresolvedTriageError(
            "Generated diagnostics are unsafe for unresolved modifier triage.",
            report=report,
        )
    return report


def build_modifier_unresolved_triage_report(
    artifacts: dict[str, dict[str, Any]],
    *,
    modifier_report: dict[str, Any],
    diagnostics_dir: str | Path,
) -> dict[str, Any]:
    _require_phases(artifacts)
    phase1 = artifacts["phase_1_source_shape"]
    phase3 = artifacts["phase_3_eligibility"]
    warnings_by_code = _warnings_by_code(phase1)
    categories = {
        category: _triage_category(category, config, warnings_by_code.get(config["warning_code"], []))
        for category, config in TRIAGE_CODES.items()
    }
    affix_910 = _find_affix_910_duplicate_evidence(phase3)
    errors = _safety_errors(artifacts, modifier_report, affix_910)
    warning_categories = _warning_categories(categories)

    summary = {
        "total_unresolved_modifier_evidence": sum(item["count"] for item in categories.values()),
        "unresolved_references": categories["unresolved_references"]["count"],
        "malformed_structures": categories["malformed_structures"]["count"],
        "unsupported_structures": categories["unsupported_structures"]["count"],
        "categories": len(categories),
        "categories_eligible_for_future_diagnostic_policy": sum(
            1 for item in categories.values() if item["eligible_for_future_diagnostic_policy"]
        ),
        "categories_that_must_remain_unresolved": sum(
            1 for item in categories.values() if item["must_remain_unresolved"]
        ),
        "affix_910_duplicate_evidence_preserved": bool(affix_910),
    }
    return {
        "diagnostic": DIAGNOSTIC_NAME,
        "diagnostic_only": True,
        "production_safe": False,
        "scope": "non_production_read_only_cli_report",
        "source": "generated_diagnostic_artifacts",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "modifier_resolver_summary": modifier_report.get("summary") or {},
        "summary": summary,
        "triage_categories": categories,
        "warning_category_summary": warning_categories,
        "affix_910_duplicate_evidence": affix_910,
        "errors": errors,
        "warnings": _report_warnings(categories),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not use this triage as gameplay modifier semantics.",
            "Do not infer behavior for unresolved, malformed, or unsupported modifier evidence.",
            "Do not use this triage to power crafting, simulation, build math, APIs, frontend, or gameplay output.",
        ],
        "recommendations": [
            "Create a diagnostic policy for each triage category before any semantic modifier resolver work.",
            "Keep unresolved, malformed, and unsupported evidence visible until a specific policy resolves or excludes it.",
            "Do not generate affix bundle families or production consumers from this triage.",
        ],
    }


def render_modifier_unresolved_triage_report(report: dict[str, Any]) -> str:
    lines = [
        "# Modifier Unresolved Category Triage Report",
        "",
        "- diagnostic: modifier_unresolved_category_triage",
        "- diagnostic_only: true",
        "- production_safe: false",
        "- scope: non_production_read_only_cli_report",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Triage Categories", ""])
    for name, category in report["triage_categories"].items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"- count: {category['count']}",
                f"- likely_issue: {category['likely_issue']}",
                f"- eligible_for_future_diagnostic_policy: {str(category['eligible_for_future_diagnostic_policy']).lower()}",
                f"- must_remain_unresolved: {str(category['must_remain_unresolved']).lower()}",
                f"- affected_affix_count: {category['affected_affix_count']}",
                "- representative_examples:",
            ]
        )
        for example in category["representative_examples"]:
            lines.append(
                f"  - {example['source_affix_identity']} {example['source_provenance_path']}: {example['message']}"
            )

    lines.extend(["", "## Warning Categories", ""])
    lines.extend(_format_bullets(report["warning_category_summary"]))
    lines.extend(["", "## Affix 910 Duplicate Evidence", ""])
    evidence = report["affix_910_duplicate_evidence"]
    if evidence:
        for key, value in evidence.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- missing")
    lines.extend(["", "## Errors", ""])
    lines.extend(_format_bullets(report["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_bullets(report["warnings"]))
    lines.extend(["", "## Forbidden Production Usage", ""])
    lines.extend(_format_bullets(report["forbidden_production_usage"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This triage is diagnostic-only and non-production.",
            "- It classifies unresolved evidence; it does not resolve gameplay semantics.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not guess unsupported modifier behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def modifier_unresolved_triage_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_modifier_unresolved_triage_output_path(path: Path) -> None:
    validate_affix_diagnostic_output_path(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing affix diagnostic artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Affix diagnostic artifact must be a JSON object: {path}")
    return data


def _require_phases(artifacts: dict[str, dict[str, Any]]) -> None:
    missing = sorted(set(PHASE_ARTIFACTS) - set(artifacts))
    if missing:
        raise ValueError(f"Missing affix diagnostic phases: {', '.join(missing)}")


def _warnings_by_code(phase1: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for warning in phase1.get("warnings") or []:
        if not isinstance(warning, dict):
            continue
        grouped.setdefault(str(warning.get("code")), []).append(warning)
    return grouped


def _triage_category(
    category: str,
    config: dict[str, Any],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    affected = sorted(
        {
            _source_affix_identity(warning)
            for warning in warnings
            if warning.get("record_id") is not None and warning.get("section")
        }
    )
    return {
        "category": category,
        "source_warning_code": config["warning_code"],
        "count": len(warnings),
        "description": config["description"],
        "likely_issue": config["likely_issue"],
        "eligible_for_future_diagnostic_policy": config["eligible_for_future_diagnostic_policy"],
        "must_remain_unresolved": config["must_remain_unresolved"],
        "source_provenance_paths": sorted({_source_provenance_path(warning) for warning in warnings})[:25],
        "affected_affix_identities": affected[:50],
        "affected_affix_count": len(affected),
        "representative_examples": [_example(warning) for warning in warnings[:5]],
    }


def _example(warning: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_affix_identity": _source_affix_identity(warning),
        "source_provenance_path": _source_provenance_path(warning),
        "warning_code": warning.get("code"),
        "field": warning.get("field"),
        "message": warning.get("message"),
        "severity": warning.get("severity", "warning"),
        "diagnostic_only": True,
        "production_safe": False,
    }


def _source_affix_identity(warning: dict[str, Any]) -> str:
    return f"{warning.get('section')}:{warning.get('record_id')}"


def _source_provenance_path(warning: dict[str, Any]) -> str:
    section = warning.get("section")
    record_id = warning.get("record_id")
    field = warning.get("field")
    if section is None or record_id is None:
        return "phase_1_source_shape.warnings"
    if field:
        return f"{section}[{record_id}].{field}"
    return f"{section}[{record_id}]"


def _safety_errors(
    artifacts: dict[str, dict[str, Any]],
    modifier_report: dict[str, Any],
    affix_910: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    for phase, data in artifacts.items():
        if data.get("production_safe") is not False:
            errors.append(f"{phase} reports production_safe={data.get('production_safe')}; expected false.")
    if modifier_report.get("production_safe") is not False:
        errors.append("Controlled modifier resolver report does not have production_safe=false.")
    if modifier_report.get("diagnostic_only") is not True:
        errors.append("Controlled modifier resolver report does not have diagnostic_only=true.")
    if modifier_report.get("errors"):
        errors.append("Controlled modifier resolver report contains errors.")
    if not affix_910:
        errors.append("Affix 910 warning-only duplicate evidence is missing.")
    return errors


def _warning_categories(categories: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "category": name,
            "likely_issue": category["likely_issue"],
            "count": category["count"],
            "must_remain_unresolved": category["must_remain_unresolved"],
        }
        for name, category in categories.items()
        if category["count"]
    ]


def _report_warnings(categories: dict[str, dict[str, Any]]) -> list[str]:
    warnings = []
    for name, category in categories.items():
        if category["count"]:
            warnings.append(
                f"{name} has {category['count']} records and remains unresolved for diagnostic planning."
            )
    warnings.append("This triage classifies evidence only; it does not infer gameplay semantics.")
    return warnings


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
