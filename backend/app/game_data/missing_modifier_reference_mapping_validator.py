"""Developer-only missing modifier reference mapping policy validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import (
    DEFAULT_DIAGNOSTICS_DIR,
    FORBIDDEN_PRODUCTION_USAGE,
    PHASE_ARTIFACTS,
    REPO_ROOT,
    validate_affix_diagnostic_output_path,
)


DIAGNOSTIC_NAME = "missing_modifier_reference_mapping_validator"
MISSING_MAPPING_CODE = "affix_record.idol_stat_modifier_reference_unmodeled"
DEFAULT_COMPARISON_REPORT = REPO_ROOT / "docs" / "generated" / "controlled_modifier_resolver_comparison_report.json"


class MissingModifierReferenceMappingValidatorError(RuntimeError):
    """Raised when missing modifier reference mapping evidence is unsafe."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def validate_missing_modifier_reference_mappings(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
    comparison_report_path: str | Path | None = DEFAULT_COMPARISON_REPORT,
) -> dict[str, Any]:
    """Validate missing-reference evidence without resolving mappings."""

    base = Path(diagnostics_dir)
    phase1 = _load_json(base / PHASE_ARTIFACTS["phase_1_source_shape"])
    comparison = _load_optional_comparison(comparison_report_path)
    report = build_missing_modifier_reference_mapping_report(
        phase1,
        diagnostics_dir=base,
        comparison_report_path=comparison_report_path,
        comparison=comparison,
    )
    if report["errors"]:
        raise MissingModifierReferenceMappingValidatorError(
            "Missing modifier reference mapping evidence failed diagnostic policy validation.",
            report=report,
        )
    return report


def build_missing_modifier_reference_mapping_report(
    phase1: dict[str, Any],
    *,
    diagnostics_dir: str | Path,
    comparison_report_path: str | Path | None,
    comparison: dict[str, Any] | None,
) -> dict[str, Any]:
    warnings = [
        warning
        for warning in phase1.get("warnings") or []
        if isinstance(warning, dict) and warning.get("code") == MISSING_MAPPING_CODE
    ]
    records = [_record_from_warning(warning) for warning in warnings]
    comparison_summary = _comparison_summary(comparison, comparison_report_path)
    errors = _safety_errors(phase1, records, comparison)
    summary = {
        "total_missing_reference_mapping_records": len(records),
        "raw_reference_evidence_preserved": sum(1 for record in records if record["raw_reference_evidence"]["warning_code"] and record["raw_reference_evidence"]["warning_message"]),
        "stable_affix_source_identity_preserved": sum(1 for record in records if record["source_affix_identity"] != "unknown:unknown"),
        "provenance_preserved": sum(1 for record in records if record["provenance"]["source_path"]),
        "warning_metadata_preserved": sum(1 for record in records if record["warning_metadata"]["code"] == MISSING_MAPPING_CODE),
        "records_remaining_unresolved": sum(1 for record in records if record["reference_status"] == "unresolved" and record["must_remain_unresolved"] is True),
        "name_only_mapping_inference_records": sum(1 for record in records if record["classification"]["name_only_mapping_inference"]),
        "subtype_id_only_mapping_inference_records": sum(1 for record in records if record["classification"]["subtype_id_only_mapping_inference"]),
        "saved_vs_fresh_agreement_available": comparison_summary["available"],
        "saved_vs_fresh_unresolved_delta": comparison_summary["unresolved_delta"],
    }
    return {
        "diagnostic": DIAGNOSTIC_NAME,
        "diagnostic_only": True,
        "production_safe": False,
        "scope": "non_production_read_only_cli_report",
        "source": "generated_diagnostic_artifacts",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "comparison_report_path": str(comparison_report_path) if comparison_report_path else None,
        "policy": "docs/migration/MODIFIER_RESOLUTION_POLICY.md#missing-modifier-reference-mapping-policy",
        "validation_status": "error" if errors else "warning",
        "summary": summary,
        "saved_vs_fresh_agreement": comparison_summary,
        "records": records,
        "errors": errors,
        "warnings": _report_warnings(summary, comparison_summary),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not add modifier mappings from this validator.",
            "Do not infer mappings from display names.",
            "Do not infer mappings from subtype_id-only identity.",
            "Do not use missing mapping records for gameplay, crafting, simulation, build math, APIs, or frontend behavior.",
        ],
    }


def render_missing_modifier_reference_mapping_report(report: dict[str, Any]) -> str:
    lines = [
        "# Missing Modifier Reference Mapping Policy Validation Report",
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
    lines.extend(["", "## Saved-vs-Fresh Agreement", ""])
    for key, value in report["saved_vs_fresh_agreement"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Representative Records", ""])
    for record in report["records"][:10]:
        lines.append(
            f"- {record['source_affix_identity']} {record['provenance']['source_path']}: "
            f"status={record['reference_status']} code={record['warning_metadata']['code']}"
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
            "- This validator checks missing reference mapping evidence preservation only.",
            "- It does not implement semantic modifier resolution.",
            "- It does not add modifier mappings.",
            "- It does not infer gameplay semantics or guess unsupported behavior.",
            "- It does not modify source data, generated production output, loaders, importers, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "",
        ]
    )
    return "\n".join(lines)


def missing_modifier_reference_mapping_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_missing_modifier_reference_mapping_output_path(path: Path) -> None:
    validate_affix_diagnostic_output_path(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing affix diagnostic artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Affix diagnostic artifact must be a JSON object: {path}")
    return data


def _load_optional_comparison(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    comparison_path = Path(path)
    if not comparison_path.exists():
        return None
    data = json.loads(comparison_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Modifier comparison artifact must be a JSON object: {comparison_path}")
    return data


def _record_from_warning(warning: dict[str, Any]) -> dict[str, Any]:
    identity = _source_affix_identity(warning)
    return {
        "source_affix_identity": identity,
        "diagnostic_only": True,
        "production_safe": False,
        "reference_status": "unresolved",
        "unresolved_category": "missing_reference_mapping",
        "must_remain_unresolved": True,
        "resolved_modifier_identity": None,
        "normalized_inspection_structure": None,
        "raw_reference_evidence": {
            "warning_code": warning.get("code"),
            "warning_message": warning.get("message"),
            "field": warning.get("field"),
            "section": warning.get("section"),
            "record_id": warning.get("record_id"),
        },
        "classification": {
            "missing_reference_mapping": True,
            "raw_evidence_missing": not bool(warning.get("code") and warning.get("message")),
            "stable_affix_identity_missing": identity == "unknown:unknown",
            "name_only_mapping_inference": _uses_name_only_inference(warning),
            "subtype_id_only_mapping_inference": _uses_subtype_id_only_inference(warning),
            "gameplay_semantics_inferred": False,
        },
        "provenance": {
            "source_phase": "phase_1_source_shape",
            "source_warning_code": warning.get("code"),
            "source_path": _source_provenance_path(warning),
        },
        "warning_metadata": {
            "code": warning.get("code"),
            "field": warning.get("field"),
            "message": warning.get("message"),
            "severity": warning.get("severity", "warning"),
        },
    }


def _source_affix_identity(warning: dict[str, Any]) -> str:
    section = warning.get("section")
    record_id = warning.get("record_id")
    if section is None or record_id is None:
        return "unknown:unknown"
    return f"{section}:{record_id}"


def _source_provenance_path(warning: dict[str, Any]) -> str:
    section = warning.get("section")
    record_id = warning.get("record_id")
    field = warning.get("field")
    if section is None or record_id is None:
        return "phase_1_source_shape.warnings"
    if field:
        return f"{section}[{record_id}].{field}"
    return f"{section}[{record_id}]"


def _uses_name_only_inference(warning: dict[str, Any]) -> bool:
    if warning.get("name_only_mapping") or warning.get("inferred_from_display_name"):
        return True
    if str(warning.get("mapping_source") or "").lower() in {"name", "display_name"}:
        return True
    return bool(warning.get("display_name") and not warning.get("record_id"))


def _uses_subtype_id_only_inference(warning: dict[str, Any]) -> bool:
    if warning.get("subtype_id_only_mapping") or warning.get("subtype_id_only_identity"):
        return True
    if str(warning.get("mapping_source") or "").lower() in {"subtype_id", "subtype"}:
        return True
    has_subtype = warning.get("subtype_id") is not None or warning.get("subTypeID") is not None
    return bool(has_subtype and warning.get("record_id") is None)


def _comparison_summary(
    comparison: dict[str, Any] | None,
    comparison_report_path: str | Path | None,
) -> dict[str, Any]:
    if comparison is None:
        return {
            "available": False,
            "path": str(comparison_report_path) if comparison_report_path else None,
            "production_safe": None,
            "diagnostic_only": None,
            "comparison_status": None,
            "unresolved_delta": None,
            "warning_category_delta": None,
        }
    count_delta = ((comparison.get("count_deltas") or {}).get("unresolved_modifier_objects") or {}).get("delta")
    warning_delta = ((comparison.get("warning_category_delta") or {}).get("modifier_resolution_policy::unresolved_modifier_references") or {}).get("delta")
    return {
        "available": True,
        "path": str(comparison_report_path) if comparison_report_path else None,
        "production_safe": comparison.get("production_safe"),
        "diagnostic_only": comparison.get("diagnostic_only"),
        "comparison_status": comparison.get("comparison_status"),
        "unresolved_delta": count_delta,
        "warning_category_delta": warning_delta,
    }


def _safety_errors(
    phase1: dict[str, Any],
    records: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if phase1.get("production_safe") is not False:
        errors.append(f"phase_1_source_shape reports production_safe={phase1.get('production_safe')}; expected false.")
    if comparison is not None:
        if comparison.get("production_safe") is not False:
            errors.append(f"Modifier comparison report production_safe={comparison.get('production_safe')}; expected false.")
        if comparison.get("diagnostic_only") is not True:
            errors.append(f"Modifier comparison report diagnostic_only={comparison.get('diagnostic_only')}; expected true.")
    for record in records:
        identity = record["source_affix_identity"]
        if record["production_safe"] is not False:
            errors.append(f"{identity} reports production_safe=true.")
        if record["diagnostic_only"] is not True:
            errors.append(f"{identity} is not diagnostic_only=true.")
        if record["classification"]["raw_evidence_missing"]:
            errors.append(f"{identity} is missing raw reference evidence.")
        if record["classification"]["stable_affix_identity_missing"]:
            errors.append(f"{identity} is missing stable affix source identity.")
        if not record["provenance"]["source_path"]:
            errors.append(f"{identity} is missing provenance.")
        if record["warning_metadata"]["code"] != MISSING_MAPPING_CODE:
            errors.append(f"{identity} is missing warning metadata.")
        if record["reference_status"] != "unresolved" or record["must_remain_unresolved"] is not True:
            errors.append(f"{identity} is not preserved as unresolved.")
        if record["resolved_modifier_identity"] is not None or record["normalized_inspection_structure"] is not None:
            errors.append(f"{identity} has resolved mapping data but must remain unresolved.")
        if record["classification"]["name_only_mapping_inference"]:
            errors.append(f"{identity} uses name-only mapping inference.")
        if record["classification"]["subtype_id_only_mapping_inference"]:
            errors.append(f"{identity} uses subtype_id-only mapping inference.")
        if record["classification"]["gameplay_semantics_inferred"]:
            errors.append(f"{identity} inferred gameplay semantics.")
    return errors


def _report_warnings(summary: dict[str, Any], comparison_summary: dict[str, Any]) -> list[str]:
    warnings = [
        f"{summary['total_missing_reference_mapping_records']} missing modifier reference mappings remain unresolved.",
        "Missing mappings are carried as unresolved diagnostic evidence only.",
        "No mappings are inferred from display names or subtype_id-only identity.",
    ]
    if not comparison_summary["available"]:
        warnings.append("Saved-vs-fresh comparison evidence is not available for this validation run.")
    elif comparison_summary["unresolved_delta"] != 0:
        warnings.append(f"Saved-vs-fresh unresolved modifier count delta is {comparison_summary['unresolved_delta']}.")
    return warnings


def _format_bullets(items: list[Any]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]
