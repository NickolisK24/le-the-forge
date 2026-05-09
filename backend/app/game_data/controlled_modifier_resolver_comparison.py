"""Developer-only saved-vs-fresh comparison for the modifier resolver prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR, REPO_ROOT
from app.game_data.controlled_modifier_resolver_prototype import (
    controlled_modifier_resolver_report_to_json,
    resolve_modifier_diagnostics,
    validate_controlled_modifier_resolver_output_path,
)


DEFAULT_SAVED_MODIFIER_RESOLVER_REPORT = (
    REPO_ROOT / "docs" / "generated" / "controlled_modifier_resolver_prototype_report.json"
)

COUNT_KEYS = (
    "total_modifier_references",
    "resolved_modifier_objects",
    "unresolved_modifier_objects",
    "malformed_modifier_objects",
    "unsupported_modifier_objects",
)


class ControlledModifierResolverComparisonError(RuntimeError):
    """Raised when saved or fresh modifier resolver output cannot be compared."""


def build_controlled_modifier_resolver_comparison(
    saved_report_path: str | Path = DEFAULT_SAVED_MODIFIER_RESOLVER_REPORT,
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    saved = load_controlled_modifier_resolver_report(saved_report_path)
    fresh = resolve_modifier_diagnostics(diagnostics_dir)
    return compare_controlled_modifier_resolver_outputs(
        saved,
        fresh,
        saved_report_path=saved_report_path,
        diagnostics_dir=diagnostics_dir,
    )


def load_controlled_modifier_resolver_report(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Missing saved controlled modifier resolver report: {report_path}")
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Saved controlled modifier resolver report must be a JSON object: {report_path}")
    return data


def compare_controlled_modifier_resolver_outputs(
    saved: dict[str, Any],
    fresh: dict[str, Any],
    *,
    saved_report_path: str | Path | None = None,
    diagnostics_dir: str | Path | None = None,
) -> dict[str, Any]:
    saved_summary = saved.get("summary") or {}
    fresh_summary = fresh.get("summary") or {}
    count_deltas = {
        key: {
            "saved": saved_summary.get(key, 0),
            "fresh": fresh_summary.get(key, 0),
            "delta": fresh_summary.get(key, 0) - saved_summary.get(key, 0),
        }
        for key in COUNT_KEYS
    }
    warning_category_delta = _warning_category_delta(saved, fresh)
    provenance_agreement = _provenance_coverage_agreement(saved, fresh)
    production_safe_agreement = _field_false_agreement(saved, fresh, "production_safe")
    diagnostic_only_agreement = _field_true_agreement(saved, fresh, "diagnostic_only")
    affix_910_agreement = _affix_910_agreement(saved, fresh)
    deterministic_output_agreement = _canonical_json(saved) == _canonical_json(fresh)

    errors = _comparison_errors(
        saved=saved,
        fresh=fresh,
        production_safe_agreement=production_safe_agreement,
        diagnostic_only_agreement=diagnostic_only_agreement,
        provenance_agreement=provenance_agreement,
        affix_910_agreement=affix_910_agreement,
    )
    warnings = _comparison_warnings(
        count_deltas=count_deltas,
        warning_category_delta=warning_category_delta,
        deterministic_output_agreement=deterministic_output_agreement,
        saved=saved,
        fresh=fresh,
    )
    comparison_status = _comparison_status(errors, warnings)

    return {
        "diagnostic": "controlled_modifier_resolver_saved_vs_fresh_comparison",
        "production_safe": False,
        "diagnostic_only": True,
        "comparison_status": comparison_status,
        "saved_report_path": str(saved_report_path) if saved_report_path is not None else None,
        "diagnostics_dir": str(diagnostics_dir) if diagnostics_dir is not None else None,
        "saved_resolver_output_status": _resolver_status(saved),
        "fresh_resolver_output_status": _resolver_status(fresh),
        "count_deltas": count_deltas,
        "warning_category_delta": warning_category_delta,
        "provenance_coverage_agreement": provenance_agreement,
        "deterministic_output_agreement": deterministic_output_agreement,
        "production_safe_agreement": production_safe_agreement,
        "diagnostic_only_agreement": diagnostic_only_agreement,
        "affix_910_duplicate_evidence_agreement": affix_910_agreement,
        "errors": errors,
        "warnings": warnings,
        "recommendations": _recommendations(comparison_status),
    }


def render_controlled_modifier_resolver_comparison(report: dict[str, Any]) -> str:
    lines = [
        "# Controlled Modifier Resolver Prototype Comparison Report",
        "",
        f"- comparison_status: {report['comparison_status']}",
        "- diagnostic_only: true",
        "- production_safe: false",
        f"- saved_resolver_output_status: {report['saved_resolver_output_status']}",
        f"- fresh_resolver_output_status: {report['fresh_resolver_output_status']}",
        f"- deterministic_output_agreement: {str(report['deterministic_output_agreement']).lower()}",
        f"- affix_910_duplicate_evidence_agreement: {str(report['affix_910_duplicate_evidence_agreement']['agrees']).lower()}",
        "",
        "## Count Deltas",
        "",
    ]
    for key in COUNT_KEYS:
        delta = report["count_deltas"][key]
        lines.append(f"- {key}: saved={delta['saved']} fresh={delta['fresh']} delta={delta['delta']}")

    lines.extend(["", "## Warning Category Delta", ""])
    for key, delta in report["warning_category_delta"].items():
        lines.append(f"- {key}: saved={delta['saved']} fresh={delta['fresh']} delta={delta['delta']}")

    lines.extend(["", "## Safety Agreement", ""])
    lines.append(f"- provenance_coverage_agreement: {report['provenance_coverage_agreement']}")
    lines.append(f"- production_safe_agreement: {report['production_safe_agreement']}")
    lines.append(f"- diagnostic_only_agreement: {report['diagnostic_only_agreement']}")

    lines.extend(["", "## Affix 910 Duplicate Evidence", ""])
    evidence = report["affix_910_duplicate_evidence_agreement"]
    lines.append(f"- agrees: {evidence['agrees']}")
    lines.append(f"- saved: {evidence['saved']}")
    lines.append(f"- fresh: {evidence['fresh']}")

    lines.extend(["", "## Errors", ""])
    lines.extend(_format_messages(report["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_messages(report["warnings"]))
    lines.extend(["", "## Recommendations", ""])
    lines.extend(_format_messages(report["recommendations"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This comparison is diagnostic-only and non-production.",
            "- It compares saved modifier resolver output with freshly generated modifier resolver output.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not infer gameplay semantics.",
            "- It does not claim gameplay correctness or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def controlled_modifier_resolver_comparison_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_controlled_modifier_resolver_comparison_output_path(path: Path) -> None:
    validate_controlled_modifier_resolver_output_path(path)


def _resolver_status(report: dict[str, Any]) -> str:
    if report.get("errors"):
        return "error"
    if report.get("warnings"):
        return "warning"
    return "pass"


def _warning_category_delta(saved: dict[str, Any], fresh: dict[str, Any]) -> dict[str, dict[str, Any]]:
    saved_categories = _warning_category_map(saved)
    fresh_categories = _warning_category_map(fresh)
    categories = sorted(set(saved_categories) | set(fresh_categories))
    return {
        category: {
            "saved": saved_categories.get(category, 0),
            "fresh": fresh_categories.get(category, 0),
            "delta": fresh_categories.get(category, 0) - saved_categories.get(category, 0),
        }
        for category in categories
    }


def _warning_category_map(report: dict[str, Any]) -> dict[str, int]:
    categories: dict[str, int] = {}
    for item in report.get("warning_category_summary") or []:
        if not isinstance(item, dict):
            continue
        key = f"{item.get('phase')}::{item.get('category')}"
        categories[key] = int(item.get("count") or 0)
    return categories


def _provenance_coverage_agreement(saved: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    saved_coverage = _provenance_coverage(saved)
    fresh_coverage = _provenance_coverage(fresh)
    return {
        "saved": saved_coverage,
        "fresh": fresh_coverage,
        "agrees": saved_coverage == fresh_coverage and saved_coverage["missing_provenance"] == 0,
    }


def _provenance_coverage(report: dict[str, Any]) -> dict[str, int]:
    records = report.get("modifier_objects") or []
    total = len(records)
    missing = sum(
        1
        for record in records
        if not isinstance(record, dict) or not record.get("source_provenance_path")
    )
    return {
        "total_modifier_objects": total,
        "with_provenance": total - missing,
        "missing_provenance": missing,
    }


def _field_false_agreement(saved: dict[str, Any], fresh: dict[str, Any], field: str) -> dict[str, Any]:
    return {
        "saved": saved.get(field),
        "fresh": fresh.get(field),
        "agrees": saved.get(field) is False and fresh.get(field) is False,
    }


def _field_true_agreement(saved: dict[str, Any], fresh: dict[str, Any], field: str) -> dict[str, Any]:
    return {
        "saved": saved.get(field),
        "fresh": fresh.get(field),
        "agrees": saved.get(field) is True and fresh.get(field) is True,
    }


def _affix_910_agreement(saved: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    saved_evidence = _essential_affix_910_evidence(saved.get("affix_910_duplicate_evidence"))
    fresh_evidence = _essential_affix_910_evidence(fresh.get("affix_910_duplicate_evidence"))
    return {
        "saved": saved_evidence,
        "fresh": fresh_evidence,
        "agrees": saved_evidence == fresh_evidence and bool(saved_evidence),
    }


def _essential_affix_910_evidence(evidence: Any) -> dict[str, Any]:
    if not isinstance(evidence, dict):
        return {}
    return {
        "record_id": evidence.get("record_id"),
        "section": evidence.get("section"),
        "record_path": evidence.get("record_path"),
        "raw_canRollOn": evidence.get("raw_canRollOn"),
        "normalized_canRollOn": evidence.get("normalized_canRollOn"),
        "raw_duplicate_count": evidence.get("raw_duplicate_count"),
        "duplicate_positions": evidence.get("duplicate_positions"),
        "diagnostic_unique_targets": evidence.get("diagnostic_unique_targets"),
        "diagnostic_unique_targets_label": evidence.get("diagnostic_unique_targets_label"),
        "policy_result": evidence.get("policy_result"),
    }


def _comparison_errors(
    *,
    saved: dict[str, Any],
    fresh: dict[str, Any],
    production_safe_agreement: dict[str, Any],
    diagnostic_only_agreement: dict[str, Any],
    provenance_agreement: dict[str, Any],
    affix_910_agreement: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if saved.get("production_safe") is not False:
        errors.append("Saved modifier resolver output does not have production_safe=false.")
    if fresh.get("production_safe") is not False:
        errors.append("Fresh modifier resolver output does not have production_safe=false.")
    if not production_safe_agreement["agrees"]:
        errors.append("Saved/fresh production_safe fields do not agree on false.")
    if saved.get("diagnostic_only") is not True:
        errors.append("Saved modifier resolver output does not have diagnostic_only=true.")
    if fresh.get("diagnostic_only") is not True:
        errors.append("Fresh modifier resolver output does not have diagnostic_only=true.")
    if not diagnostic_only_agreement["agrees"]:
        errors.append("Saved/fresh diagnostic_only fields do not agree on true.")
    if not provenance_agreement["agrees"]:
        errors.append("Saved/fresh provenance coverage does not agree or has missing provenance.")
    if not affix_910_agreement["agrees"]:
        errors.append("Affix 910 duplicate evidence does not agree or is missing.")
    if saved.get("errors"):
        errors.append("Saved modifier resolver output contains errors.")
    if fresh.get("errors"):
        errors.append("Fresh modifier resolver output contains errors.")
    return errors


def _comparison_warnings(
    *,
    count_deltas: dict[str, dict[str, Any]],
    warning_category_delta: dict[str, dict[str, Any]],
    deterministic_output_agreement: bool,
    saved: dict[str, Any],
    fresh: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if any(delta["delta"] != 0 for delta in count_deltas.values()):
        warnings.append("Saved/fresh modifier resolver count deltas are present.")
    if any(delta["delta"] != 0 for delta in warning_category_delta.values()):
        warnings.append("Saved/fresh warning category deltas are present.")
    if not deterministic_output_agreement:
        warnings.append("Saved/fresh modifier resolver JSON output is not byte-for-byte deterministic.")
    if _has_unresolved_malformed_or_unsupported(saved) or _has_unresolved_malformed_or_unsupported(fresh):
        warnings.append("Unresolved, malformed, or unsupported modifier evidence remains visible; comparison is warning-level.")
    if saved.get("warnings") or fresh.get("warnings"):
        warnings.append("Modifier resolver outputs remain warning-level and non-production.")
    return warnings


def _has_unresolved_malformed_or_unsupported(report: dict[str, Any]) -> bool:
    summary = report.get("summary") or {}
    return any(
        summary.get(key, 0)
        for key in (
            "unresolved_modifier_objects",
            "malformed_modifier_objects",
            "unsupported_modifier_objects",
        )
    )


def _comparison_status(errors: list[str], warnings: list[str]) -> str:
    if errors:
        return "error"
    if warnings:
        return "warning"
    return "pass"


def _recommendations(status: str) -> list[str]:
    if status == "error":
        return [
            "Do not expand modifier diagnostics until comparison errors are resolved.",
            "Keep production_safe=false and preserve raw warning/error evidence.",
        ]
    if status == "warning":
        return [
            "Keep the modifier resolver prototype diagnostic-only and non-production.",
            "Review count, warning, or deterministic-output drift before using fresh output as a new baseline.",
            "Do not generate affix bundle families or production consumers from this comparison.",
        ]
    return [
        "Saved and fresh modifier resolver prototype outputs agree diagnostically.",
        "Keep production_safe=false until a separate production readiness review exists.",
    ]


def _canonical_json(report: dict[str, Any]) -> str:
    return controlled_modifier_resolver_report_to_json(report)


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
