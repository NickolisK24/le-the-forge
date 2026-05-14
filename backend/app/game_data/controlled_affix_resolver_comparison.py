"""Developer-only saved-vs-fresh comparison for the affix resolver prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR, REPO_ROOT
from app.game_data.controlled_affix_resolver_prototype import (
    controlled_affix_resolver_report_to_json,
    resolve_affix_diagnostics,
    validate_controlled_affix_resolver_output_path,
)


DEFAULT_SAVED_RESOLVER_REPORT = (
    REPO_ROOT / "docs" / "generated" / "controlled_affix_resolver_prototype_report.json"
)

COUNT_KEYS = (
    "total_normalized_affixes",
    "equipment_affixes",
    "idol_affixes",
    "total_embedded_tiers",
)


class ControlledAffixResolverComparisonError(RuntimeError):
    """Raised when saved or fresh resolver output cannot be compared."""


def build_controlled_affix_resolver_comparison(
    saved_report_path: str | Path = DEFAULT_SAVED_RESOLVER_REPORT,
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    saved = load_controlled_affix_resolver_report(saved_report_path)
    fresh = resolve_affix_diagnostics(diagnostics_dir)
    return compare_controlled_affix_resolver_outputs(
        saved,
        fresh,
        saved_report_path=saved_report_path,
        diagnostics_dir=diagnostics_dir,
    )


def load_controlled_affix_resolver_report(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Missing saved controlled affix resolver report: {report_path}")
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Saved controlled affix resolver report must be a JSON object: {report_path}")
    return data


def compare_controlled_affix_resolver_outputs(
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
    phase_status_delta = _phase_status_delta(saved, fresh)
    warning_category_delta = _warning_category_delta(saved, fresh)
    affix_910_agreement = _affix_910_agreement(saved, fresh)
    production_safe_agreement = {
        "saved": saved.get("production_safe"),
        "fresh": fresh.get("production_safe"),
        "agrees": saved.get("production_safe") is False and fresh.get("production_safe") is False,
    }
    non_production_inspection_allowed_agreement = {
        "saved": saved.get("non_production_inspection_allowed"),
        "fresh": fresh.get("non_production_inspection_allowed"),
        "agrees": saved.get("non_production_inspection_allowed")
        == fresh.get("non_production_inspection_allowed"),
    }
    deterministic_output_agreement = _canonical_json(saved) == _canonical_json(fresh)
    errors = _comparison_errors(
        saved=saved,
        fresh=fresh,
        production_safe_agreement=production_safe_agreement,
        affix_910_agreement=affix_910_agreement,
    )
    warnings = _comparison_warnings(
        count_deltas=count_deltas,
        phase_status_delta=phase_status_delta,
        warning_category_delta=warning_category_delta,
        deterministic_output_agreement=deterministic_output_agreement,
        non_production_inspection_allowed_agreement=non_production_inspection_allowed_agreement,
        saved=saved,
        fresh=fresh,
    )
    comparison_status = _comparison_status(errors, warnings)
    return {
        "diagnostic": "controlled_affix_resolver_saved_vs_fresh_comparison",
        "production_safe": False,
        "comparison_status": comparison_status,
        "saved_report_path": str(saved_report_path) if saved_report_path is not None else None,
        "diagnostics_dir": str(diagnostics_dir) if diagnostics_dir is not None else None,
        "saved_resolver_status": _resolver_status(saved),
        "fresh_resolver_status": _resolver_status(fresh),
        "count_deltas": count_deltas,
        "phase_status_delta": phase_status_delta,
        "warning_category_delta": warning_category_delta,
        "affix_910_duplicate_evidence_agreement": affix_910_agreement,
        "production_safe_agreement": production_safe_agreement,
        "non_production_inspection_allowed_agreement": non_production_inspection_allowed_agreement,
        "deterministic_output_agreement": deterministic_output_agreement,
        "errors": errors,
        "warnings": warnings,
        "recommendations": _recommendations(comparison_status),
    }


def render_controlled_affix_resolver_comparison(report: dict[str, Any]) -> str:
    lines = [
        "# Controlled Affix Resolver Prototype Comparison Report",
        "",
        f"- comparison_status: {report['comparison_status']}",
        "- production_safe: false",
        f"- saved_resolver_status: {report['saved_resolver_status']}",
        f"- fresh_resolver_status: {report['fresh_resolver_status']}",
        f"- deterministic_output_agreement: {str(report['deterministic_output_agreement']).lower()}",
        f"- affix_910_duplicate_evidence_agreement: {str(report['affix_910_duplicate_evidence_agreement']['agrees']).lower()}",
        "",
        "## Count Deltas",
        "",
    ]
    for key in COUNT_KEYS:
        delta = report["count_deltas"][key]
        lines.append(f"- {key}: saved={delta['saved']} fresh={delta['fresh']} delta={delta['delta']}")

    lines.extend(["", "## Phase Status Delta", ""])
    for phase, delta in report["phase_status_delta"].items():
        lines.append(f"- {phase}: saved={delta['saved']} fresh={delta['fresh']} agrees={delta['agrees']}")

    lines.extend(["", "## Warning Category Delta", ""])
    for key, delta in report["warning_category_delta"].items():
        lines.append(f"- {key}: saved={delta['saved']} fresh={delta['fresh']} delta={delta['delta']}")

    lines.extend(["", "## Affix 910 Duplicate Evidence", ""])
    evidence = report["affix_910_duplicate_evidence_agreement"]
    lines.append(f"- agrees: {evidence['agrees']}")
    lines.append(f"- saved: {evidence['saved']}")
    lines.append(f"- fresh: {evidence['fresh']}")

    lines.extend(["", "## Safety Agreement", ""])
    lines.append(f"- production_safe_agreement: {report['production_safe_agreement']}")
    lines.append(
        f"- non_production_inspection_allowed_agreement: {report['non_production_inspection_allowed_agreement']}"
    )

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
            "- It compares saved resolver output with freshly generated resolver output.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not silently deduplicate affix 910.",
            "- It does not claim production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def controlled_affix_resolver_comparison_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_controlled_affix_resolver_comparison_output_path(path: Path) -> None:
    validate_controlled_affix_resolver_output_path(path)


def _resolver_status(report: dict[str, Any]) -> str:
    if report.get("errors"):
        return "error"
    if report.get("warnings"):
        return "warning"
    return "pass"


def _phase_status_delta(saved: dict[str, Any], fresh: dict[str, Any]) -> dict[str, dict[str, Any]]:
    saved_statuses = saved.get("phase_status_summary") or {}
    fresh_statuses = fresh.get("phase_status_summary") or {}
    phases = sorted(set(saved_statuses) | set(fresh_statuses))
    return {
        phase: {
            "saved": saved_statuses.get(phase),
            "fresh": fresh_statuses.get(phase),
            "agrees": saved_statuses.get(phase) == fresh_statuses.get(phase),
        }
        for phase in phases
    }


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
    for item in report.get("warning_categories") or []:
        if not isinstance(item, dict):
            continue
        key = f"{item.get('phase')}::{item.get('category')}"
        categories[key] = int(item.get("count") or 0)
    return categories


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
    affix_910_agreement: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if saved.get("production_safe") is not False:
        errors.append("Saved resolver output does not have production_safe=false.")
    if fresh.get("production_safe") is not False:
        errors.append("Fresh resolver output does not have production_safe=false.")
    if not production_safe_agreement["agrees"]:
        errors.append("Saved/fresh production_safe fields do not agree on false.")
    if not affix_910_agreement["agrees"]:
        errors.append("Affix 910 duplicate evidence does not agree or is missing.")
    if saved.get("errors"):
        errors.append("Saved resolver output contains errors.")
    if fresh.get("errors"):
        errors.append("Fresh resolver output contains errors.")
    return errors


def _comparison_warnings(
    *,
    count_deltas: dict[str, dict[str, Any]],
    phase_status_delta: dict[str, dict[str, Any]],
    warning_category_delta: dict[str, dict[str, Any]],
    deterministic_output_agreement: bool,
    non_production_inspection_allowed_agreement: dict[str, Any],
    saved: dict[str, Any],
    fresh: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if any(delta["delta"] != 0 for delta in count_deltas.values()):
        warnings.append("Saved/fresh resolver count deltas are present.")
    if any(not delta["agrees"] for delta in phase_status_delta.values()):
        warnings.append("Saved/fresh phase status deltas are present.")
    if any(delta["delta"] != 0 for delta in warning_category_delta.values()):
        warnings.append("Saved/fresh warning category deltas are present.")
    if not deterministic_output_agreement:
        warnings.append("Saved/fresh resolver JSON output is not byte-for-byte deterministic.")
    if not non_production_inspection_allowed_agreement["agrees"]:
        warnings.append("Saved/fresh non_production_inspection_allowed fields differ.")
    if saved.get("warnings") or fresh.get("warnings"):
        warnings.append("Resolver outputs remain warning-level and non-production.")
    return warnings


def _comparison_status(errors: list[str], warnings: list[str]) -> str:
    if errors:
        return "error"
    if warnings:
        return "warning"
    return "pass"


def _recommendations(status: str) -> list[str]:
    if status == "error":
        return [
            "Do not expand affix resolver diagnostics until comparison errors are resolved.",
            "Keep production_safe=false and preserve raw warning/error evidence.",
        ]
    if status == "warning":
        return [
            "Keep the resolver prototype diagnostic-only and non-production.",
            "Review count, warning, or deterministic-output drift before using the fresh output as a baseline.",
            "Do not generate affix bundle families or production consumers from this comparison.",
        ]
    return [
        "Saved and fresh resolver prototype outputs agree diagnostically.",
        "Keep production_safe=false until a separate production readiness review exists.",
    ]


def _canonical_json(report: dict[str, Any]) -> str:
    return controlled_affix_resolver_report_to_json(report)


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
