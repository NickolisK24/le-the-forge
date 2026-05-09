"""Developer-only controlled modifier resolver prototype.

This module consumes generated diagnostic affix artifacts only. It does not
read production bundle data, source exports directly, production loaders,
importers, routes, frontend code, crafting logic, simulation code, build math,
or gameplay output.
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
    _summary_value,
)


DIAGNOSTIC_NAME = "controlled_modifier_resolver_prototype"


class ControlledModifierResolverError(RuntimeError):
    """Raised when diagnostic artifacts are unsafe for modifier inspection."""

    def __init__(self, message: str, report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.report = report


def resolve_modifier_diagnostics(
    diagnostics_dir: str | Path = DEFAULT_DIAGNOSTICS_DIR,
) -> dict[str, Any]:
    """Load generated diagnostic artifacts and build modifier inspection objects."""

    base = Path(diagnostics_dir)
    artifacts = {
        phase: _load_json(base / filename)
        for phase, filename in PHASE_ARTIFACTS.items()
    }
    report = build_controlled_modifier_resolver_report(artifacts, diagnostics_dir=base)
    if report["errors"]:
        raise ControlledModifierResolverError(
            "Affix diagnostic artifacts are not safe for controlled modifier inspection.",
            report=report,
        )
    return report


def build_controlled_modifier_resolver_report(
    artifacts: dict[str, dict[str, Any]],
    *,
    diagnostics_dir: str | Path,
) -> dict[str, Any]:
    """Build a serializable modifier resolver report from generated diagnostics."""

    _require_phases(artifacts)
    phase1 = artifacts["phase_1_source_shape"]
    phase2 = artifacts["phase_2_identity_provenance"]
    phase3 = artifacts["phase_3_eligibility"]
    phase4 = artifacts["phase_4_tag_category"]
    phase5 = artifacts["phase_5_saved_vs_fresh"]

    phase_statuses = _phase_statuses(artifacts)
    counts = _modifier_counts(phase1)
    affix_910 = _find_affix_910_duplicate_evidence(phase3)
    warning_categories = _warning_categories(counts, phase1, phase2, phase3, phase4, phase5)
    errors = _safety_errors(phase_statuses, phase2, phase3, phase4, phase5, affix_910)
    objects = _modifier_objects(counts, affix_910)

    return {
        "resolver": DIAGNOSTIC_NAME,
        "diagnostic_only": True,
        "production_safe": False,
        "scope": "non_production_read_only_cli_report",
        "source": "generated_diagnostic_artifacts",
        "diagnostics_dir": str(Path(diagnostics_dir)),
        "policy": "docs/migration/MODIFIER_RESOLUTION_POLICY.md",
        "input_artifacts": phase_statuses,
        "phase_status_summary": {
            phase: status["validation_status"] for phase, status in phase_statuses.items()
        },
        "phase5_migration_gate_status": phase5.get("migration_gate_status"),
        "non_production_inspection_allowed": not errors,
        "summary": {
            "total_modifier_references": counts["total"],
            "resolved_modifier_objects": counts["resolved"],
            "unresolved_modifier_objects": counts["unresolved"],
            "malformed_modifier_objects": counts["malformed"],
            "unsupported_modifier_objects": counts["unsupported"],
            "warning_categories": len(warning_categories),
            "deterministic_output_status": _deterministic_status(phase5),
            "non_production_inspection_allowed": not errors,
            "affix_910_duplicate_evidence_preserved": bool(affix_910),
        },
        "modifier_objects": objects,
        "warning_category_summary": warning_categories,
        "affix_910_duplicate_evidence": affix_910,
        "errors": errors,
        "warnings": _report_warnings(phase_statuses, warning_categories, counts),
        "forbidden_production_usage": list(FORBIDDEN_PRODUCTION_USAGE)
        + [
            "Do not use this modifier resolver prototype as a gameplay stat model.",
            "Do not infer additive, increased, more, conditional, ailment, minion, skill, class, or stacking semantics.",
            "Do not treat aggregate inspection objects as per-reference gameplay rows.",
        ],
        "notes": [
            "Diagnostic-only: consumes generated diagnostic artifacts only.",
            "Resolved means structurally safe for inspection, not gameplay-correct.",
            "Unresolved, malformed, and unsupported modifier evidence remains visible and excluded from resolved semantics.",
            "Generated artifacts currently expose aggregate modifier warning counts; this prototype emits deterministic aggregate inspection objects rather than invented per-reference mechanics.",
            "Affix 910 raw duplicate eligibility evidence remains visible as upstream warning metadata.",
        ],
    }


def render_controlled_modifier_resolver_report(report: dict[str, Any]) -> str:
    """Render the modifier resolver report as markdown."""

    lines = [
        "# Controlled Modifier Resolver Prototype Report",
        "",
        "- resolver: controlled_modifier_resolver_prototype",
        "- scope: non_production_read_only_cli_report",
        "- source: generated_diagnostic_artifacts",
        "- diagnostic_only: true",
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

    lines.extend(["", "## Modifier Inspection Objects", ""])
    for record in report["modifier_objects"]:
        lines.append(
            f"- {record['stable_modifier_identity']}: state={record['state']} "
            f"references={record['reference_count']} production_safe=false"
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
            "- This resolver is a prototype for inspection-only diagnostics.",
            "- It does not consume production bundle data directly.",
            "- It does not modify source data or generated production output.",
            "- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.",
            "- It does not guess unsupported modifier semantics.",
            "- It does not resolve malformed or unresolved modifier structures.",
            "- It does not claim gameplay correctness or production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def controlled_modifier_resolver_report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def validate_controlled_modifier_resolver_output_path(path: Path) -> None:
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


def _modifier_counts(phase1: dict[str, Any]) -> dict[str, int]:
    total = int(_summary_value(phase1, "total_embedded_tiers") or 0)
    unresolved = int(_summary_value(phase1, "missing_stat_modifier_references") or 0)
    malformed = int(_summary_value(phase1, "malformed_tier_ranges") or 0)
    unsupported = int(_summary_value(phase1, "unsupported_or_unresolved_fields") or 0)
    resolved = max(total - unresolved - malformed - unsupported, 0)
    return {
        "total": total,
        "resolved": resolved,
        "unresolved": unresolved,
        "malformed": malformed,
        "unsupported": unsupported,
    }


def _modifier_objects(
    counts: dict[str, int],
    affix_910: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    objects = [
        _modifier_object(
            identity="modifier_reference_group:resolved_structural",
            state="resolved",
            count=counts["resolved"],
            family="structurally_present",
            warning_categories=[],
            normalized_structure={
                "kind": "aggregate_reference_group",
                "resolution": "inspection_safe_structural_reference",
                "gameplay_semantics": None,
                "source_mutation": False,
            },
            notes=[
                "Resolved only means structurally safe for inspection.",
                "No gameplay formula, stacking, conditional, or crafting semantics are inferred.",
            ],
            affix_910=affix_910,
        ),
        _modifier_object(
            identity="modifier_reference_group:unresolved",
            state="unresolved",
            count=counts["unresolved"],
            family="missing_stat_modifier_reference",
            warning_categories=["missing_stat_modifier_references"],
            normalized_structure=None,
            notes=[
                "Unresolved references are carried as unresolved diagnostic evidence.",
                "They are excluded from resolved modifier semantics.",
            ],
            affix_910=affix_910,
        ),
        _modifier_object(
            identity="modifier_reference_group:malformed",
            state="malformed",
            count=counts["malformed"],
            family="malformed_or_semantically_unresolved_structure",
            warning_categories=["malformed_tier_ranges"],
            normalized_structure=None,
            notes=[
                "Malformed or semantically unresolved structures are not resolved.",
                "A separate semantic policy is required before any normalized value can be emitted.",
            ],
            affix_910=affix_910,
        ),
        _modifier_object(
            identity="modifier_reference_group:unsupported",
            state="unsupported",
            count=counts["unsupported"],
            family="unsupported_or_unresolved_structure",
            warning_categories=["unsupported_or_unresolved_fields"],
            normalized_structure=None,
            notes=[
                "Unsupported structures are not guessed.",
                "They require explicit modeling or explicit exclusion before resolver work can advance.",
            ],
            affix_910=affix_910,
        ),
    ]
    return [record for record in objects if record["reference_count"] > 0]


def _modifier_object(
    *,
    identity: str,
    state: str,
    count: int,
    family: str,
    warning_categories: list[str],
    normalized_structure: dict[str, Any] | None,
    notes: list[str],
    affix_910: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "stable_modifier_identity": identity,
        "source_affix_identity": "aggregate:multiple_affixes",
        "source_affix_identity_scope": "aggregate_generated_diagnostic_counts",
        "source_provenance_path": "phase_1_source_shape.summary.total_embedded_tiers",
        "modifier_family": family,
        "state": state,
        "reference_count": count,
        "normalized_inspection_structure": normalized_structure,
        "warnings": [
            {
                "category": category,
                "message": "Warning category preserved from generated diagnostics.",
                "source": "phase_1_source_shape",
            }
            for category in warning_categories
        ],
        "duplicate_raw_evidence_refs": ["affix_910_duplicate_evidence"] if affix_910 else [],
        "diagnostic_only": True,
        "production_safe": False,
        "notes": notes,
    }


def _deterministic_status(phase5: dict[str, Any]) -> str:
    summary = phase5.get("summary") or {}
    if any(
        summary.get(key, 0)
        for key in ("phases_with_count_deltas", "phases_with_warning_deltas", "phases_with_error_deltas")
    ):
        return "drift_detected"
    return "stable"


def _warning_categories(
    counts: dict[str, int],
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        ("modifier_resolution_policy", "unresolved_modifier_references", counts["unresolved"]),
        ("modifier_resolution_policy", "malformed_modifier_structures", counts["malformed"]),
        ("modifier_resolution_policy", "unsupported_modifier_structures", counts["unsupported"]),
        ("phase_1_source_shape", "ambiguous_name_collisions", _summary_value(phase1, "ambiguous_name_collisions")),
        ("phase_2_identity_provenance", "ambiguous_display_name_collisions", _summary_value(phase2, "ambiguous_display_name_collisions")),
        ("phase_3_eligibility", "duplicate_or_ambiguous_eligibility_records", _summary_value(phase3, "duplicate_or_ambiguous_eligibility_records")),
        ("phase_4_tag_category", "unknown_or_unsupported_tag_category_values", _summary_value(phase4, "unknown_or_unsupported_tag_category_values")),
        ("phase_4_tag_category", "ambiguous_tag_category_mappings", _summary_value(phase4, "ambiguous_tag_category_mappings")),
        ("phase_5_saved_vs_fresh", "phases_with_warning_status", _summary_value(phase5, "phases_with_warning_status")),
    ]
    return [
        {"phase": phase, "category": category, "count": count}
        for phase, category, count in candidates
        if count
    ]


def _safety_errors(
    phase_statuses: dict[str, dict[str, Any]],
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
    if _summary_value(phase2, "affixes_missing_source_identity"):
        errors.append("Phase 2 reports affixes missing source identity.")
    if any(
        _summary_value(data, key)
        for data, key in (
            (phase2, "affixes_relying_on_name_only_identity"),
            (phase3, "eligibility_records_using_name_only_matching"),
            (phase4, "tag_category_records_using_name_only_matching"),
        )
    ):
        errors.append("Name-only identity or matching is present in generated diagnostics.")
    if any(
        _summary_value(data, key)
        for data, key in (
            (phase2, "affixes_relying_on_subtype_id_only_identity"),
            (phase3, "eligibility_records_using_subtype_id_only_identity"),
            (phase4, "tag_category_records_using_subtype_id_only_identity"),
        )
    ):
        errors.append("subtype_id-only identity or matching is present in generated diagnostics.")
    phase5_summary = phase5.get("summary") or {}
    for key in ("phases_with_count_deltas", "phases_with_warning_deltas", "phases_with_error_deltas"):
        if phase5_summary.get(key, 0) != 0:
            errors.append(f"Phase 5 summary {key}={phase5_summary.get(key)}; expected 0.")
    if not affix_910:
        errors.append("Affix 910 warning-only duplicate evidence is missing.")
    return errors


def _report_warnings(
    phase_statuses: dict[str, dict[str, Any]],
    warning_categories: list[dict[str, Any]],
    counts: dict[str, int],
) -> list[str]:
    warnings: list[str] = []
    for phase, status in phase_statuses.items():
        if status["validation_status"] == "warning" or status.get("migration_gate_status") == "warning":
            warnings.append(f"{phase} remains warning-level and non-production.")
        if status["warning_count"]:
            warnings.append(f"{phase} contains {status['warning_count']} diagnostic warnings.")
    if any(counts[key] for key in ("unresolved", "malformed", "unsupported")):
        warnings.append("Unresolved, malformed, and unsupported modifier evidence remains visible and excluded from resolved semantics.")
    if warning_categories:
        warnings.append("Warning categories are preserved; this is not production readiness.")
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
