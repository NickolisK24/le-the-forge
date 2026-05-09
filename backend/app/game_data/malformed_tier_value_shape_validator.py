"""Developer-only malformed tier/value shape policy validator."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import (
    DEFAULT_DIAGNOSTICS_DIR,
    FORBIDDEN_PRODUCTION_USAGE,
    PHASE_ARTIFACTS,
    validate_affix_diagnostic_output_path,
)


DIAGNOSTIC_NAME = "malformed_tier_value_shape_validator"
MALFORMED_CODE = "affix_tier.inverted_numeric_range"
RANGE_RE = re.compile(
    r"(?P<tier_field>tiers\d*)\[(?P<tier_index>\d+)\].*?minRoll=(?P<min_roll>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?), "
    r"maxRoll=(?P<max_roll>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"
)


class MalformedTierValueShapeValidatorError(RuntimeError):
    """Raised when malformed tier/value shape evidence is unsafe."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def validate_malformed_tier_value_shapes(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    base = Path(diagnostics_dir)
    phase1 = _load_json(base / PHASE_ARTIFACTS["phase_1_source_shape"])
    report = build_malformed_tier_value_shape_report(phase1, diagnostics_dir=base)
    if report["errors"]:
        raise MalformedTierValueShapeValidatorError(
            "Malformed tier/value shape evidence failed diagnostic policy validation.",
            report=report,
        )
    return report


def build_malformed_tier_value_shape_report(
    phase1: dict[str, Any],
    *,
    diagnostics_dir: str | Path,
) -> dict[str, Any]:
    warnings = [
        warning
        for warning in phase1.get("warnings") or []
        if isinstance(warning, dict) and warning.get("code") == MALFORMED_CODE
    ]
    records = [_record_from_warning(warning) for warning in warnings]
    errors = _safety_errors(phase1, records)
    summary = {
        "total_malformed_tier_value_shape_records": len(records),
        "raw_min_max_preserved": sum(1 for record in records if record["raw"]["minRoll"] is not None and record["raw"]["maxRoll"] is not None),
        "raw_source_order_preserved": sum(1 for record in records if record["raw"]["source_order"] == "minRoll_then_maxRoll"),
        "provenance_preserved": sum(1 for record in records if record["provenance"]["source_path"]),
        "warning_metadata_preserved": sum(1 for record in records if record["warning_metadata"]["code"] == MALFORMED_CODE),
        "diagnostic_normalized_views": sum(1 for record in records if record["diagnostic_normalized_view"] is not None),
        "inverted_numeric_ranges": sum(1 for record in records if record["classification"]["inverted_numeric_range"]),
        "inverted_negative_ranges": sum(1 for record in records if record["classification"]["inverted_negative_range"]),
        "records_missing_raw_evidence": sum(1 for record in records if record["classification"]["missing_raw_evidence"]),
        "records_with_unlabeled_normalized_view": sum(1 for record in records if record["classification"]["unlabeled_normalized_view"]),
    }
    return {
        "diagnostic": DIAGNOSTIC_NAME,
        "diagnostic_only": True,
        "production_safe": False,
        "scope": "non_production_read_only_cli_report",
        "source": "generated_diagnostic_artifacts",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "policy": "docs/migration/MODIFIER_RESOLUTION_POLICY.md#malformed-tiervalue-shape-policy",
        "validation_status": "error" if errors else "warning",
        "summary": summary,
        "records": records,
        "errors": errors,
        "warnings": _report_warnings(summary),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not treat normalized range order as gameplay truth.",
            "Do not infer whether negative ranges are beneficial, harmful, additive, increased, more, conditional, or scoped.",
            "Do not use this report to power gameplay, crafting, simulation, build math, APIs, or frontend behavior.",
        ],
    }


def render_malformed_tier_value_shape_report(report: dict[str, Any]) -> str:
    lines = [
        "# Malformed Tier/Value Shape Policy Validation Report",
        "",
        f"- validation_status: {report['validation_status']}",
        "- diagnostic_only: true",
        "- production_safe: false",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Representative Records", ""])
    for record in report["records"][:10]:
        lines.append(
            f"- {record['source_affix_identity']} {record['provenance']['source_path']}: "
            f"minRoll={record['raw']['minRoll']} maxRoll={record['raw']['maxRoll']} "
            f"inverted_negative={str(record['classification']['inverted_negative_range']).lower()}"
        )
    if len(report["records"]) > 10:
        lines.append(f"- ... {len(report['records']) - 10} additional records omitted from markdown.")
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
            "- This validator checks diagnostic evidence preservation only.",
            "- It does not implement semantic modifier resolution.",
            "- It does not infer gameplay semantics or guess unsupported behavior.",
            "- It does not modify source data, generated production output, loaders, importers, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "",
        ]
    )
    return "\n".join(lines)


def malformed_tier_value_shape_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_malformed_tier_value_shape_output_path(path: Path) -> None:
    validate_affix_diagnostic_output_path(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing affix diagnostic artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Affix diagnostic artifact must be a JSON object: {path}")
    return data


def _record_from_warning(warning: dict[str, Any]) -> dict[str, Any]:
    match = RANGE_RE.search(str(warning.get("message") or ""))
    tier_index = int(match.group("tier_index")) if match else None
    tier_field = match.group("tier_field") if match else warning.get("field")
    min_roll = float(match.group("min_roll")) if match else None
    max_roll = float(match.group("max_roll")) if match else None
    normalized_view = _normalized_view(min_roll, max_roll)
    return {
        "source_affix_identity": f"{warning.get('section')}:{warning.get('record_id')}",
        "diagnostic_only": True,
        "production_safe": False,
        "raw": {
            "tier_index": tier_index,
            "tier_field": tier_field,
            "minRoll": min_roll,
            "maxRoll": max_roll,
            "source_order": "minRoll_then_maxRoll" if match else None,
            "message": warning.get("message"),
        },
        "diagnostic_normalized_view": normalized_view,
        "classification": {
            "malformed_tier_value_shape": True,
            "inverted_numeric_range": bool(min_roll is not None and max_roll is not None and min_roll > max_roll),
            "inverted_negative_range": bool(min_roll is not None and max_roll is not None and min_roll > max_roll and min_roll < 0 and max_roll < 0),
            "missing_raw_evidence": min_roll is None or max_roll is None or tier_index is None,
            "unlabeled_normalized_view": bool(normalized_view and normalized_view.get("label") != "diagnostic_only_not_source_mutation"),
            "gameplay_semantics_inferred": False,
            "must_remain_unresolved": True,
        },
        "provenance": {
            "source_phase": "phase_1_source_shape",
            "source_warning_code": warning.get("code"),
            "source_path": _source_path(warning, tier_index, tier_field),
        },
        "warning_metadata": {
            "code": warning.get("code"),
            "field": warning.get("field"),
            "message": warning.get("message"),
            "severity": warning.get("severity", "warning"),
        },
    }


def _normalized_view(min_roll: float | None, max_roll: float | None) -> dict[str, Any] | None:
    if min_roll is None or max_roll is None:
        return None
    return {
        "label": "diagnostic_only_not_source_mutation",
        "ordered_bounds_for_inspection": sorted([min_roll, max_roll]),
        "source_mutation": False,
        "gameplay_semantics": None,
    }


def _source_path(warning: dict[str, Any], tier_index: int | None, tier_field: Any) -> str:
    section = warning.get("section")
    record_id = warning.get("record_id")
    if section is None or record_id is None:
        return "phase_1_source_shape.warnings"
    field = tier_field or warning.get("field") or "tiers"
    if tier_index is None:
        return f"{section}[{record_id}].{field}"
    return f"{section}[{record_id}].{field}[{tier_index}]"


def _safety_errors(phase1: dict[str, Any], records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if phase1.get("production_safe") is not False:
        errors.append(f"phase_1_source_shape reports production_safe={phase1.get('production_safe')}; expected false.")
    for record in records:
        if record["production_safe"] is not False:
            errors.append(f"{record['source_affix_identity']} reports production_safe=true.")
        if not record["provenance"]["source_path"]:
            errors.append(f"{record['source_affix_identity']} is missing provenance.")
        if record["classification"]["missing_raw_evidence"]:
            errors.append(f"{record['source_affix_identity']} is missing raw minRoll/maxRoll/tier evidence.")
        if record["classification"]["unlabeled_normalized_view"]:
            errors.append(f"{record['source_affix_identity']} has an unlabeled diagnostic normalized view.")
        if record["classification"]["gameplay_semantics_inferred"]:
            errors.append(f"{record['source_affix_identity']} inferred gameplay semantics.")
    return errors


def _report_warnings(summary: dict[str, Any]) -> list[str]:
    return [
        f"{summary['total_malformed_tier_value_shape_records']} malformed tier/value shape records remain unresolved for semantic resolver purposes.",
        "Diagnostic-only normalized views are inspection aids only and are not source mutation.",
        "Inverted negative ranges may be valid game data, but no gameplay meaning is inferred.",
    ]


def _format_bullets(items: list[Any]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]
