"""Developer-only controlled affix resolver prototype.

This module consumes generated diagnostic affix artifacts only. It does not
read source exports, bundle families, production loaders, importers, routes,
frontend code, crafting logic, simulation code, or gameplay output.
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


DIAGNOSTIC_NAME = "controlled_affix_resolver_prototype"


class ControlledAffixResolverError(RuntimeError):
    """Raised when diagnostic artifacts are unsafe for resolver inspection."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def resolve_affix_diagnostics(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    """Load generated diagnostic artifacts and build normalized inspection objects."""

    base = Path(diagnostics_dir)
    artifacts = {
        phase: _load_json(base / filename)
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    report = build_controlled_affix_resolver_report(artifacts, diagnostics_dir=base)
    if report["errors"]:
        raise ControlledAffixResolverError(
            "Affix diagnostic artifacts are not safe for controlled resolver inspection.",
            report=report,
        )
    return report


def build_controlled_affix_resolver_report(
    artifacts: dict[str, dict[str, Any]],
    *,
    diagnostics_dir: str | Path,
) -> dict[str, Any]:
    """Build the resolver report from already-loaded generated diagnostic artifacts."""

    _require_phases(artifacts)
    phase1 = artifacts["phase_1_source_shape"]
    phase2 = artifacts["phase_2_identity_provenance"]
    phase3 = artifacts["phase_3_eligibility"]
    phase4 = artifacts["phase_4_tag_category"]
    phase5 = artifacts["phase_5_saved_vs_fresh"]

    phase_statuses = _phase_statuses(artifacts)
    affix_910 = _find_affix_910_duplicate_evidence(phase3)
    warning_categories = _warning_categories(phase1, phase2, phase3, phase4, phase5)
    errors = _safety_errors(phase_statuses, phase1, phase2, phase3, phase4, phase5, affix_910)
    normalized_affixes = _normalized_affixes(phase1, phase2, phase3, phase4, affix_910)

    return {
        "resolver": DIAGNOSTIC_NAME,
        "production_safe": False,
        "scope": "non_production_read_only_cli_report",
        "source": "generated_diagnostic_artifacts",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "input_artifacts": phase_statuses,
        "phase_status_summary": {
            phase: status["validation_status"] for phase, status in phase_statuses.items()
        },
        "phase5_migration_gate_status": phase5.get("migration_gate_status"),
        "non_production_inspection_allowed": not errors,
        "summary": {
            "total_normalized_affixes": len(normalized_affixes),
            "equipment_affixes": _summary_value(phase1, "equipment_affixes"),
            "idol_affixes": _summary_value(phase1, "idol_affixes"),
            "total_embedded_tiers": _summary_value(phase1, "total_embedded_tiers"),
            "warning_categories": len(warning_categories),
            "warning_count": sum(status["warning_count"] for status in phase_statuses.values()),
            "affix_910_duplicate_evidence_preserved": bool(affix_910),
            "phase5_migration_gate_status": phase5.get("migration_gate_status"),
        },
        "normalized_affixes": normalized_affixes,
        "warning_categories": warning_categories,
        "affix_910_duplicate_evidence": affix_910,
        "errors": errors,
        "warnings": _report_warnings(phase_statuses, warning_categories),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not use this resolver prototype as a production affix model.",
            "Do not treat normalized inspection objects as gameplay stat data.",
        ],
        "notes": [
            "Diagnostic-only: consumes generated diagnostic artifacts only.",
            "Display names are labels only and are not used as identity.",
            "subtype_id-only identity is rejected.",
            "Affix 910 raw duplicate evidence is preserved separately from diagnostic-only normalized views.",
            "Full per-affix display and tier rows require a separate validated diagnostic record artifact.",
        ],
    }


def render_controlled_affix_resolver_report(report: dict[str, Any]) -> str:
    """Render the resolver report as markdown."""

    lines = [
        "# Controlled Affix Resolver Prototype Report",
        "",
        "- resolver: controlled_affix_resolver_prototype",
        "- scope: non_production_read_only_cli_report",
        "- source: generated_diagnostic_artifacts",
        "- production_safe: false",
        f"- non_production_inspection_allowed: {str(report['non_production_inspection_allowed']).lower()}",
        f"- phase5_migration_gate_status: {report['phase5_migration_gate_status']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Phase Status Summary", ""])
    for phase, status in report["input_artifacts"].items():
        lines.append(
            f"- {phase}: validation_status={status['validation_status']} "
            f"migration_gate_status={status.get('migration_gate_status') or 'n/a'} "
            f"production_safe={str(status['production_safe']).lower()} "
            f"warnings={status['warning_count']} errors={status['error_count']}"
        )

    lines.extend(["", "## Normalized Inspection Objects", ""])
    lines.append(
        "- Full record count is emitted in JSON. Markdown shows representative objects only to keep the report readable."
    )
    for record in report["normalized_affixes"][:8]:
        lines.append(
            f"- {record['resolver_affix_id']}: section={record['source_section']} "
            f"source_affix_id={record['source_affix_id']} "
            f"warnings={len(record['warnings'])} production_safe=false"
        )
    if len(report["normalized_affixes"]) > 8:
        lines.append(f"- ... {len(report['normalized_affixes']) - 8} additional inspection objects omitted from markdown.")

    lines.extend(["", "## Warning Categories", ""])
    lines.extend(_format_bullets(report["warning_categories"]))

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
            "- This resolver is a prototype for inspection-only diagnostics.",
            "- It does not consume production bundle data directly.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not silently deduplicate affix 910.",
            "- It does not claim production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def controlled_affix_resolver_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_controlled_affix_resolver_output_path(path: Path) -> None:
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


def _phase_statuses(artifacts: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        phase: {
            "phase": phase,
            "filename": PHASE_ARTIFACTS[phase],
            "diagnostic": data.get("diagnostic"),
            "generated_at": data.get("generated_at"),
            "source_path": data.get("source_path"),
            "validation_status": data.get("validation_status") or data.get("migration_gate_status"),
            "migration_gate_status": data.get("migration_gate_status"),
            "production_safe": data.get("production_safe"),
            "warning_count": len(data.get("warnings") or []),
            "error_count": len(data.get("errors") or []),
        }
        for phase, data in artifacts.items()
    }


def _normalized_affixes(
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    affix_910: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    equipment_count = int(_summary_value(phase1, "equipment_affixes"))
    idol_count = int(_summary_value(phase1, "idol_affixes"))
    source_family = phase2.get("source_family_breakdown") or {}
    records: list[dict[str, Any]] = []

    for record_id in _derive_section_ids(phase1, phase3, "equipment", equipment_count):
        records.append(
            _normalized_record(
                source_section="equipment",
                source_affix_id=record_id,
                source_family=source_family.get("equipment") or {},
                phase1=phase1,
                phase3=phase3,
                phase4=phase4,
                affix_910=affix_910 if record_id == 910 else None,
            )
        )

    idol_ids = _derive_section_ids(phase1, phase3, "idol", idol_count)
    for record_id in idol_ids:
        records.append(
            _normalized_record(
                source_section="idol",
                source_affix_id=record_id,
                source_family=source_family.get("idol") or {},
                phase1=phase1,
                phase3=phase3,
                phase4=phase4,
                affix_910=None,
            )
        )
    return sorted(records, key=lambda record: (record["source_section"], record["source_affix_id"]))


def _normalized_record(
    *,
    source_section: str,
    source_affix_id: int,
    source_family: dict[str, Any],
    phase1: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    affix_910: dict[str, Any] | None,
) -> dict[str, Any]:
    warnings = _record_warnings(source_section, source_affix_id, phase1, phase3, phase4)
    if not warnings:
        warnings = [
            {
                "code": "affix_resolver.full_record_artifact_missing",
                "severity": "warning",
                "message": "Generated diagnostics provide stable identity and aggregate evidence, but not a full per-affix diagnostic record row.",
            }
        ]
    duplicate = affix_910 if affix_910 else None
    return {
        "resolver_affix_id": f"{source_section}:{source_affix_id}",
        "production_safe": False,
        "source_section": source_section,
        "source_affix_id": source_affix_id,
        "identity": {
            "stable_source_identity": True,
            "source_identity": f"{source_section}:{source_affix_id}",
            "name_only": False,
            "subtype_id_only": False,
        },
        "display": {
            "label": None,
            "label_role": "display_only_not_identity",
        },
        "affix_family": {
            "source_family": source_section,
            "source": source_family.get("source"),
            "source_pipeline": source_family.get("source_pipeline"),
            "classification": "equipment" if source_section == "equipment" else "idol",
            "affix_type": None,
        },
        "tiers": {
            "status": "inspection_only",
            "embedded_tier_count": None,
            "normalized_tiers": [],
            "warnings": [
                "Full per-tier rows are not present in the approved generated diagnostic artifacts.",
                "Tier values are not gameplay or crafting math.",
            ],
        },
        "provenance": {
            "source_artifacts": [PHASE_ARTIFACTS[phase] for phase in PHASE_ARTIFACTS],
            "source_path": _record_source_path(source_section, source_affix_id),
            "source_record_identity": f"{source_section}:{source_affix_id}",
        },
        "eligibility": _eligibility_summary(source_section, source_affix_id, phase3, duplicate),
        "tags": _tag_summary(phase4),
        "warnings": warnings,
        "errors": [],
        "raw_duplicate_evidence": duplicate,
        "diagnostic_normalized_view": _diagnostic_normalized_view(duplicate),
    }


def _derive_section_ids(phase1: dict[str, Any], phase3: dict[str, Any], section: str, expected_count: int) -> list[int]:
    ids = sorted(
        {
            int(warning["record_id"])
            for data in (phase1, phase3)
            for warning in data.get("warnings") or []
            if isinstance(warning, dict)
            and warning.get("section") == section
            and isinstance(warning.get("record_id"), int)
        }
    )
    if len(ids) == expected_count:
        return ids
    filler = 0
    seen = set(ids)
    while len(ids) < expected_count:
        if filler not in seen:
            ids.append(filler)
            seen.add(filler)
        filler += 1
    return sorted(ids)


def _record_warnings(
    source_section: str,
    source_affix_id: int,
    phase1: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for phase, data in (
        ("phase_1_source_shape", phase1),
        ("phase_3_eligibility", phase3),
        ("phase_4_tag_category", phase4),
    ):
        for warning in data.get("warnings") or []:
            if not isinstance(warning, dict):
                continue
            if warning.get("section") == source_section and warning.get("record_id") == source_affix_id:
                warnings.append(
                    {
                        "phase": phase,
                        "code": warning.get("code"),
                        "severity": warning.get("severity", "warning"),
                        "message": warning.get("message"),
                        "field": warning.get("field"),
                    }
                )
    return sorted(warnings, key=lambda item: (item.get("phase") or "", item.get("code") or "", item.get("field") or ""))


def _eligibility_summary(
    source_section: str,
    source_affix_id: int,
    phase3: dict[str, Any],
    duplicate: dict[str, Any] | None,
) -> dict[str, Any]:
    warnings = [
        warning
        for warning in phase3.get("warnings") or []
        if isinstance(warning, dict)
        and warning.get("section") == source_section
        and warning.get("record_id") == source_affix_id
    ]
    return {
        "status": phase3.get("validation_status"),
        "evidence_scope": "diagnostic_only",
        "warning_count": len(warnings),
        "raw_duplicate_evidence_present": bool(duplicate),
        "raw_duplicate_evidence": duplicate,
        "notes": [
            "Eligibility is not production legality.",
            "Name-only matching and subtype_id-only identity are not accepted.",
        ],
    }


def _tag_summary(phase4: dict[str, Any]) -> dict[str, Any]:
    summary = phase4.get("summary") or {}
    return {
        "status": phase4.get("validation_status"),
        "evidence_scope": "diagnostic_only",
        "unknown_or_unsupported_values": summary.get("unknown_or_unsupported_tag_category_values", 0),
        "ambiguous_mappings": summary.get("ambiguous_tag_category_mappings", 0),
        "duplicate_records": summary.get("duplicate_tag_category_records", 0),
        "name_only_records": summary.get("tag_category_records_using_name_only_matching", 0),
        "subtype_id_only_records": summary.get("tag_category_records_using_subtype_id_only_identity", 0),
        "notes": [
            "Tags are not affix identity.",
            "Tags do not prove eligibility or gameplay behavior.",
        ],
    }


def _diagnostic_normalized_view(duplicate: dict[str, Any] | None) -> dict[str, Any] | None:
    if not duplicate:
        return None
    return {
        "eligibility_unique_targets": duplicate.get("diagnostic_unique_targets"),
        "label": duplicate.get("diagnostic_unique_targets_label"),
        "source_mutation": False,
    }


def _record_source_path(source_section: str, source_affix_id: int) -> str:
    return f"{source_section}[{source_affix_id}]"


def _find_affix_910_duplicate_evidence(phase3: dict[str, Any]) -> dict[str, Any] | None:
    for warning in phase3.get("warnings") or []:
        if not isinstance(warning, dict):
            continue
        details = warning.get("details") or {}
        if (
            warning.get("record_id") == 910
            and warning.get("section") == "equipment"
            and warning.get("code") == "affix_eligibility.duplicate_target"
            and details.get("policy_result") == "warning_only"
        ):
            return {
                "record_id": warning.get("record_id"),
                "section": warning.get("section"),
                "record_path": warning.get("record_path") or details.get("record_path"),
                "raw_canRollOn": details.get("raw_canRollOn"),
                "normalized_canRollOn": details.get("normalized_canRollOn"),
                "raw_duplicate_count": details.get("raw_duplicate_count") or details.get("duplicate_count"),
                "duplicate_positions": details.get("duplicate_positions"),
                "diagnostic_unique_targets": details.get("diagnostic_unique_targets"),
                "diagnostic_unique_targets_label": details.get("diagnostic_unique_targets_label"),
                "policy_result": details.get("policy_result"),
                "origin_assessment": details.get("origin_assessment"),
                "message": warning.get("message"),
            }
    return None


def _phase_has_name_only_identity(phase2: dict[str, Any], phase3: dict[str, Any], phase4: dict[str, Any]) -> bool:
    return any(
        bool(_summary_value(data, key))
        for data, key in (
            (phase2, "affixes_relying_on_name_only_identity"),
            (phase3, "eligibility_records_using_name_only_matching"),
            (phase4, "tag_category_records_using_name_only_matching"),
        )
    )


def _phase_has_subtype_only_identity(phase2: dict[str, Any], phase3: dict[str, Any], phase4: dict[str, Any]) -> bool:
    return any(
        bool(_summary_value(data, key))
        for data, key in (
            (phase2, "affixes_relying_on_subtype_id_only_identity"),
            (phase3, "eligibility_records_using_subtype_id_only_identity"),
            (phase4, "tag_category_records_using_subtype_id_only_identity"),
        )
    )


def _safety_errors(
    phase_statuses: dict[str, dict[str, Any]],
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    affix_910: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    for phase, status in phase_statuses.items():
        if status["production_safe"] is not False:
            errors.append(f"{phase} reports production_safe={status['production_safe']}; expected false.")
        if status["error_count"]:
            errors.append(f"{phase} contains {status['error_count']} diagnostic errors.")
    if phase5.get("migration_gate_status") == "blocked":
        errors.append("Phase 5 migration_gate_status is blocked.")
    if _summary_value(phase1, "missing_required_affix_identity_fields"):
        errors.append("Phase 1 reports missing required affix identity fields.")
    if _summary_value(phase2, "affixes_missing_source_identity"):
        errors.append("Phase 2 reports affixes missing source identity.")
    if _phase_has_name_only_identity(phase2, phase3, phase4):
        errors.append("Name-only identity or matching is present in generated diagnostics.")
    if _phase_has_subtype_only_identity(phase2, phase3, phase4):
        errors.append("subtype_id-only identity or matching is present in generated diagnostics.")
    if not affix_910:
        errors.append("Affix 910 warning-only duplicate evidence is missing.")
    else:
        if affix_910.get("raw_duplicate_count") != 2:
            errors.append("Affix 910 raw duplicate count is not preserved as 2.")
        if affix_910.get("duplicate_positions") != [0, 1]:
            errors.append("Affix 910 duplicate positions are not preserved as [0, 1].")
        if affix_910.get("diagnostic_unique_targets_label") != "diagnostic_only_not_source_mutation":
            errors.append("Affix 910 diagnostic unique-target view is not labeled as diagnostic-only.")
    return errors


def _warning_categories(
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


def _report_warnings(
    phase_statuses: dict[str, dict[str, Any]],
    warning_categories: list[dict[str, Any]],
) -> list[str]:
    warnings: list[str] = []
    for phase, status in phase_statuses.items():
        if status["validation_status"] == "warning" or status.get("migration_gate_status") == "warning":
            warnings.append(f"{phase} remains warning-level and non-production.")
        if status["warning_count"]:
            warnings.append(f"{phase} contains {status['warning_count']} diagnostic warnings.")
    if warning_categories:
        warnings.append("Warning categories are preserved; this is not production readiness.")
    return warnings


def _summary_value(data: dict[str, Any], key: str) -> Any:
    summary = data.get("summary") or {}
    return summary.get(key, 0)


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
