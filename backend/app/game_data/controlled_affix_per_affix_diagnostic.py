"""Developer-only per-affix diagnostic artifact from the controlled resolver.

This module reads generated diagnostic artifacts through the controlled affix
resolver prototype. It does not read production bundle data directly, source
exports directly, production loaders, importers, routes, frontend code,
crafting logic, simulation code, build math, or gameplay output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR
from app.game_data.controlled_affix_resolver_prototype import (
    resolve_affix_diagnostics,
    validate_controlled_affix_resolver_output_path,
)


DIAGNOSTIC_NAME = "controlled_affix_per_affix_diagnostic_records"


class ControlledAffixPerAffixDiagnosticError(RuntimeError):
    """Raised when per-affix diagnostic records cannot be generated safely."""

    def __init__(self, message: str, artifact: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.artifact = artifact


def build_per_affix_diagnostic_artifact(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    """Build a validated per-affix diagnostic record artifact."""

    resolver_report = resolve_affix_diagnostics(diagnostics_dir)
    artifact = build_per_affix_diagnostic_artifact_from_resolver(
        resolver_report,
        diagnostics_dir=diagnostics_dir,
    )
    errors = validate_per_affix_diagnostic_artifact(artifact)
    if errors:
        artifact["errors"] = errors
        raise ControlledAffixPerAffixDiagnosticError(
            "Per-affix diagnostic artifact failed validation.",
            artifact=artifact,
        )
    return artifact


def build_per_affix_diagnostic_artifact_from_resolver(
    resolver_report: dict[str, Any],
    *,
    diagnostics_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build the artifact from an already-created controlled resolver report."""

    records = [_per_affix_record(record) for record in resolver_report.get("normalized_affixes") or []]
    warning_summary = _warning_category_summary(records, resolver_report)
    affix_910 = _affix_910_summary(resolver_report, records)
    summary = {
        "total_records": len(records),
        "equipment_records": sum(1 for record in records if record["classification"] == "equipment"),
        "idol_records": sum(1 for record in records if record["classification"] == "idol"),
        "embedded_tier_count": resolver_report.get("summary", {}).get("total_embedded_tiers", 0),
        "warning_category_count": len(warning_summary),
        "records_with_warnings": sum(1 for record in records if record["warning_categories"]),
        "affix_910_duplicate_evidence_preserved": bool(affix_910),
    }
    artifact = {
        "diagnostic": DIAGNOSTIC_NAME,
        "production_safe": False,
        "diagnostic_only": True,
        "scope": "non_production_read_only_per_affix_records",
        "source": "controlled_affix_resolver_prototype",
        "diagnostics_dir": str(Path(diagnostics_dir)) if diagnostics_dir is not None else resolver_report.get("diagnostics_dir"),
        "non_production_inspection_allowed": bool(resolver_report.get("non_production_inspection_allowed")),
        "phase_status_summary": resolver_report.get("phase_status_summary") or {},
        "phase5_migration_gate_status": resolver_report.get("phase5_migration_gate_status"),
        "summary": summary,
        "warning_category_summary": warning_summary,
        "affix_910_evidence_summary": affix_910,
        "records": records,
        "errors": [],
        "warnings": _artifact_warnings(resolver_report, warning_summary),
        "forbidden_production_usage": list(resolver_report.get("forbidden_production_usage") or [])
        + [
            "Do not use this per-affix diagnostic artifact as production affix data.",
            "Do not treat diagnostic normalized views as source mutation.",
        ],
        "notes": [
            "Diagnostic-only: generated from the controlled affix resolver prototype.",
            "Display labels are labels only and are not used as identity.",
            "Name-only identity and subtype_id-only identity are rejected.",
            "Affix 910 raw duplicate evidence is preserved separately from diagnostic-only normalized views.",
        ],
    }
    artifact["errors"] = validate_per_affix_diagnostic_artifact(artifact)
    return artifact


def validate_per_affix_diagnostic_artifact(artifact: dict[str, Any]) -> list[str]:
    """Return validation errors for a per-affix diagnostic artifact."""

    errors: list[str] = []
    if artifact.get("production_safe") is not False:
        errors.append("Top-level production_safe must be false.")
    if artifact.get("diagnostic_only") is not True:
        errors.append("Top-level diagnostic_only must be true.")
    if artifact.get("non_production_inspection_allowed") is not True:
        errors.append("non_production_inspection_allowed must be true for this diagnostic artifact.")
    records = artifact.get("records")
    if not isinstance(records, list):
        return errors + ["records must be a list."]
    summary = artifact.get("summary") or {}
    if summary.get("total_records") != len(records):
        errors.append("summary.total_records does not match record count.")
    if summary.get("equipment_records") != sum(1 for record in records if record.get("classification") == "equipment"):
        errors.append("summary.equipment_records does not match records.")
    if summary.get("idol_records") != sum(1 for record in records if record.get("classification") == "idol"):
        errors.append("summary.idol_records does not match records.")
    for index, record in enumerate(records):
        errors.extend(_record_errors(index, record))
    affix_910 = artifact.get("affix_910_evidence_summary")
    if not isinstance(affix_910, dict) or not affix_910.get("raw_duplicate_evidence"):
        errors.append("Affix 910 raw duplicate evidence is missing.")
    elif affix_910["raw_duplicate_evidence"].get("raw_duplicate_count") != 2:
        errors.append("Affix 910 raw duplicate count is not preserved as 2.")
    return errors


def render_per_affix_diagnostic_artifact(artifact: dict[str, Any]) -> str:
    """Render the per-affix artifact as a markdown summary."""

    lines = [
        "# Controlled Affix Per-Affix Diagnostic Records",
        "",
        f"- diagnostic: {DIAGNOSTIC_NAME}",
        "- scope: non_production_read_only_per_affix_records",
        "- production_safe: false",
        "- diagnostic_only: true",
        f"- non_production_inspection_allowed: {str(artifact['non_production_inspection_allowed']).lower()}",
        f"- phase5_migration_gate_status: {artifact['phase5_migration_gate_status']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in artifact["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Phase Status Summary", ""])
    for phase, status in artifact["phase_status_summary"].items():
        lines.append(f"- {phase}: {status}")

    lines.extend(["", "## Warning Category Summary", ""])
    lines.extend(_format_bullets(artifact["warning_category_summary"]))

    lines.extend(["", "## Affix 910 Evidence Summary", ""])
    evidence = artifact["affix_910_evidence_summary"]
    for key, value in evidence.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Representative Records", ""])
    lines.append("- Full per-affix records are emitted in JSON. Markdown shows representative records only.")
    for record in artifact["records"][:8]:
        lines.append(
            f"- {record['affix_identity']['source_identity']}: classification={record['classification']} "
            f"warnings={len(record['warning_categories'])} production_safe=false diagnostic_only=true"
        )
    if len(artifact["records"]) > 8:
        lines.append(f"- ... {len(artifact['records']) - 8} additional records omitted from markdown.")

    lines.extend(["", "## Errors", ""])
    lines.extend(_format_bullets(artifact["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_bullets(artifact["warnings"]))
    lines.extend(["", "## Forbidden Production Usage", ""])
    lines.extend(_format_bullets(artifact["forbidden_production_usage"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This artifact is diagnostic-only and non-production.",
            "- It is generated from controlled resolver output over approved diagnostic artifacts.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not silently deduplicate affix 910.",
            "- It does not claim production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def per_affix_diagnostic_artifact_to_json(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, sort_keys=True)


def validate_per_affix_diagnostic_output_path(path: Path) -> None:
    validate_controlled_affix_resolver_output_path(path)


def _per_affix_record(record: dict[str, Any]) -> dict[str, Any]:
    identity = record.get("identity") or {}
    affix_family = record.get("affix_family") or {}
    duplicate = record.get("raw_duplicate_evidence")
    normalized_view = record.get("diagnostic_normalized_view")
    warnings = record.get("warnings") or []
    return {
        "production_safe": False,
        "diagnostic_only": True,
        "affix_identity": {
            "stable_source_identity": identity.get("stable_source_identity") is True,
            "source_identity": identity.get("source_identity"),
            "source_section": record.get("source_section"),
            "source_affix_id": record.get("source_affix_id"),
            "name_only": identity.get("name_only") is True,
            "subtype_id_only": identity.get("subtype_id_only") is True,
        },
        "display": {
            "label": (record.get("display") or {}).get("label"),
            "label_role": "display_only_not_identity",
        },
        "classification": affix_family.get("classification"),
        "tier_summary": record.get("tiers") or {},
        "provenance": record.get("provenance") or {},
        "eligibility_summary": record.get("eligibility") or {},
        "tag_category_summary": record.get("tags") or {},
        "warning_categories": _record_warning_categories(warnings),
        "warnings": warnings,
        "raw_duplicate_evidence": duplicate,
        "diagnostic_normalized_views": _normalized_views(normalized_view),
    }


def _record_warning_categories(warnings: list[Any]) -> list[dict[str, Any]]:
    categories = []
    for warning in warnings:
        if not isinstance(warning, dict):
            continue
        categories.append(
            {
                "phase": warning.get("phase"),
                "code": warning.get("code"),
                "severity": warning.get("severity", "warning"),
                "field": warning.get("field"),
            }
        )
    return sorted(categories, key=lambda item: (item.get("phase") or "", item.get("code") or "", item.get("field") or ""))


def _normalized_views(normalized_view: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not normalized_view:
        return []
    return [
        {
            "view": "eligibility_unique_targets",
            "values": normalized_view.get("eligibility_unique_targets"),
            "label": normalized_view.get("label"),
            "source_mutation": normalized_view.get("source_mutation") is True,
        }
    ]


def _warning_category_summary(records: list[dict[str, Any]], resolver_report: dict[str, Any]) -> list[dict[str, Any]]:
    counts: dict[tuple[str | None, str | None], int] = {}
    for record in records:
        for warning in record.get("warning_categories") or []:
            key = (warning.get("phase"), warning.get("code"))
            counts[key] = counts.get(key, 0) + 1
    for warning in resolver_report.get("warning_categories") or []:
        key = (warning.get("phase"), warning.get("category"))
        counts.setdefault(key, int(warning.get("count") or 0))
    return [
        {"phase": phase, "category": category, "count": count}
        for (phase, category), count in sorted(counts.items(), key=lambda item: (item[0][0] or "", item[0][1] or ""))
        if count
    ]


def _affix_910_summary(
    resolver_report: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    record = next(
        (
            item
            for item in records
            if item["affix_identity"].get("source_section") == "equipment"
            and item["affix_identity"].get("source_affix_id") == 910
        ),
        None,
    )
    return {
        "record_identity": "equipment:910",
        "raw_duplicate_evidence": resolver_report.get("affix_910_duplicate_evidence"),
        "record_contains_raw_duplicate_evidence": bool(record and record.get("raw_duplicate_evidence")),
        "diagnostic_normalized_views": record.get("diagnostic_normalized_views") if record else [],
        "source_mutation": False,
    }


def _artifact_warnings(
    resolver_report: dict[str, Any],
    warning_summary: list[dict[str, Any]],
) -> list[str]:
    warnings = list(resolver_report.get("warnings") or [])
    if warning_summary:
        warnings.append("Per-affix warning metadata is attached for inspection only.")
    warnings.append("Per-affix records remain non-production and production_safe=false.")
    return sorted(set(warnings))


def _record_errors(index: int, record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"records[{index}]"
    if record.get("production_safe") is not False:
        errors.append(f"{prefix}.production_safe must be false.")
    if record.get("diagnostic_only") is not True:
        errors.append(f"{prefix}.diagnostic_only must be true.")
    identity = record.get("affix_identity") or {}
    if identity.get("stable_source_identity") is not True:
        errors.append(f"{prefix} missing stable source identity.")
    if not identity.get("source_identity"):
        errors.append(f"{prefix} missing source_identity.")
    if identity.get("name_only"):
        errors.append(f"{prefix} uses name-only identity.")
    if identity.get("subtype_id_only"):
        errors.append(f"{prefix} uses subtype_id-only identity.")
    for view in record.get("diagnostic_normalized_views") or []:
        if view.get("source_mutation") is True:
            errors.append(f"{prefix} diagnostic normalized view claims source mutation.")
    if record.get("classification") not in {"equipment", "idol"}:
        errors.append(f"{prefix} classification must be equipment or idol.")
    return errors


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
